# Consistent distributed snapshots for stateful operators

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/distributed-snapshots-streaming` · **Status:** partially-solved

## 1. Problem Statement

A long-running streaming job maintains large, continuously evolving **operator state** (windows, aggregates, keyed maps, join hash tables) sharded across many tasks. To recover from failures and to enable reconfiguration/rescaling, the system must periodically take a **consistent distributed snapshot**: a global state from which the job can resume as if no failure occurred. The challenge is doing this with **low overhead and without stopping the pipeline**, even when individual operator states are gigabytes-to-terabytes and changing under high ingest.

Problem: produce a globally consistent snapshot of all operator states + in-flight records + source offsets such that (i) it corresponds to a valid consistent cut, (ii) processing is not blocked ("non-blocking"), (iii) snapshot size/IO is proportional to *change*, not total state, and (iv) snapshots interoperate with rescaling (state redistribution).

Variants:
- **Aligned vs. unaligned** snapshots (whether to wait for barriers from all input channels).
- **Full vs. incremental** state capture.
- **Optimization:** minimize snapshot-induced latency/throughput loss and storage, subject to a bounded recovery-time objective.

## 2. Mathematical Foundations

The bedrock is **Chandy–Lamport (1985)**: a snapshot is a **consistent cut** of the distributed computation's space-time diagram — a downward-closed set under the *happens-before* relation $\to$ (Lamport, 1978). A cut $C$ is consistent iff $e' \in C \wedge e \to e' \Rightarrow e \in C$; recording channel states captures messages "in flight" across the cut. For a dataflow with markers/barriers injected at sources, the set of records *before* the barrier at each operator defines such a cut.

**Asynchronous Barrier Snapshotting (ABS)** specializes this: barriers flow with data; an operator with multiple inputs **aligns** by buffering channels that have passed the barrier until all inputs reach it, then snapshots its state and forwards the barrier. For acyclic graphs ABS needs no channel logging; **cyclic** graphs require logging records on back-edges (the in-flight set). **Unaligned** snapshots instead snapshot immediately and persist in-flight buffers, trading storage for zero alignment stall.

Incremental snapshots exploit an LSM/RocksDB state backend: a snapshot persists only **SSTable deltas** since the last checkpoint, so cost $\approx$ size of changed keys. Rescaling requires **key-group** partitioning so that snapshot fragments can be reassigned to a different parallelism without rewriting; consistency of the reshuffled state follows from key-group disjointness.

## 3. State of the Art (SOTA)

- **Chandy–Lamport** (TOCS 1985) and **Lamport happens-before** (CACM 1978): foundations.
- **Flink ABS** (Carbone, Fóra, Ewen, Haridi, Tzoumas; 2015) and **State Management in Apache Flink** (Carbone et al., PVLDB 2017): the canonical streaming-snapshot system — barriers, key-groups, RocksDB incremental checkpoints, savepoints.
- **Unaligned checkpoints** (Flink 1.11+) and **generic log-based / changelog state backend** (Flink 1.15+): decouple checkpoint duration from state size and backpressure.
- **Naiad / timely dataflow** (Murray et al., SOSP 2013): frontier-based progress underpinning consistent snapshots for iterative dataflows.
- **Spark Structured Streaming** state store + checkpointing (Armbrust et al., SIGMOD 2018).
- **Differential dataflow** maintains versioned state enabling consistent reads at logical times.

## 4. Upper Bound

- For **acyclic** dataflows, ABS produces a consistent snapshot with **no blocking** and marker overhead $O(|E|)$ per checkpoint; alignment cost is bounded by inter-channel skew. **Unaligned** snapshots remove alignment latency entirely at the cost of persisting in-flight buffers.
- **Incremental** state capture costs $O(\Delta)$ IO where $\Delta$ is the changed-state size since last checkpoint (RocksDB delta), independent of total state — the practical state-of-the-art bound.
- Recovery cost is $O(\text{state to reload} + \text{records to replay since snapshot})$; choosing checkpoint interval optimally trades steady-state overhead against expected recovery time (a standard Young/Daly-style optimum, $T^\* \approx \sqrt{2 C \cdot \text{MTBF}}$ for checkpoint cost $C$).

## 5. Lower Bound

- **Consistency requires capturing in-flight messages:** Chandy–Lamport shows channel state must be recorded; for cyclic dataflows there is an unavoidable $\Omega(\text{in-flight back-edge volume})$ logging cost — you cannot get a consistent cut for free on cycles.
- **FLP (1985):** in a fully asynchronous system, coordinating a global snapshot that also requires agreement (e.g., to atomically commit alongside external effects) cannot be both safe and live with a crash — practical systems escape via partial synchrony.
- **Storage lower bound:** any recoverable snapshot must persist enough state to reconstruct results; for non-mergeable, non-compressible state this is $\Omega(\text{live state size})$ — incremental snapshots only reduce *per-checkpoint* IO, not the eventual full footprint.
- **CAP:** during a partition, a snapshot that must be globally agreed cannot complete while remaining available.

## 6. The Gap

**Partially solved.** Non-blocking consistent snapshots (ABS + unaligned + incremental) are well-engineered and close to optimal for *acyclic* graphs: marker overhead, $O(\Delta)$ IO, and Young–Daly interval tuning are essentially tight. Open gaps: (a) **cyclic/iterative** dataflows still pay back-edge logging with no tight characterization of minimal logging; (b) snapshotting **very large state under heavy skew/backpressure** without latency spikes — unaligned checkpoints help but storage and recovery-time tradeoffs lack tight theory; (c) **snapshot + rescaling + exactly-once external commit** as one atomic, minimal-coordination operation; (d) formal bounds linking checkpoint interval, state size, and tail-latency SLOs.

## 7. Current Research (as of June 2026)

- **Log-based / changelog state backends** making checkpoint latency near-constant regardless of state size, and enabling fast rescaling *(frontier — verify)*.
- **Disaggregated state** (state on remote/cloud storage, e.g., tiered or "ForSt"-style backends) so snapshots become metadata operations over shared storage *(frontier — verify)*.
- **Fine-grained / partial & local recovery** to avoid global rollback (causal-logging, Clonos lineage).
- **Snapshot-consistent online rescaling** of multi-TB state without downtime.
- Active groups: TU Berlin / Flink community (Carbone, Markl, Katsifodimos), ETH timely-dataflow lineage, Alibaba/Ververica streaming engineering, Spark/Databricks streaming.

## 8. Future Work

- Tight minimal-logging bounds for consistent snapshots of cyclic/iterative dataflows.
- Disaggregated, copy-on-write state where snapshots are O(metadata).
- Unified atomic operation combining snapshot, rescaling, and exactly-once sink commit at minimal coordination.
- Formal interval-selection theory tying checkpoint cost to tail-latency SLOs and state size.
- Verified consistency of snapshots under online rescaling and key-group migration.

## 9. Key References

- **[Foundational]** Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978.
- **[Foundational]** Chandy, Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985.
- **[SOTA]** Carbone, Fóra, Ewen, Haridi, Tzoumas. *Lightweight Asynchronous Snapshots for Distributed Dataflows.* arXiv:1506.08603, 2015.
- **[SOTA]** Carbone, Ewen, Fóra, Haridi, Richter, Tzoumas. *State Management in Apache Flink.* PVLDB, 2017.
- **[SOTA]** Murray, McSherry, Isaacs, Isard, Barham, Abadi. *Naiad: A Timely Dataflow System.* SOSP, 2013.
- **[Foundational]** Young / Daly. *A Higher Order Estimate of the Optimum Checkpoint Interval for Restart Dumps.* Future Generation Computer Systems, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
