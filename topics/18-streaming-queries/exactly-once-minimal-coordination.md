---
id: 18-streaming-queries/exactly-once-minimal-coordination
title: "Exactly-once semantics at minimal coordination cost"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Exactly-once semantics at minimal coordination cost

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/exactly-once-minimal-coordination` · **Status:** partially-solved

## 1. Problem Statement

A streaming dataflow processes records through a DAG of stateful operators terminating in external **sinks** (databases, message queues, files). *Exactly-once* means each input record affects operator state and externally visible output **as if processed precisely once**, despite failures, retries, and reprocessing. Achieving this requires coordination — snapshots/checkpoints, transactional commits, deduplication — which costs latency and throughput.

The problem: **provide end-to-end exactly-once output while minimizing coordination overhead** (snapshot frequency/cost, commit rounds, barrier alignment stalls, sink transaction cost).

Important distinctions:
- **Effectively-once state** (internal state consistency via checkpoint+rollback) vs. **exactly-once output** (the *external* sink sees each effect once). The latter is strictly harder.
- **Idempotent sinks** (writes can be replayed safely) vs. **non-idempotent sinks** (require transactions / 2PC).
- **Optimization variant:** minimize coordination cost (overhead per record, or recovery time) subject to the exactly-once guarantee.
- **Decision variant:** given a topology + sink capabilities, is exactly-once achievable *without* distributed transactions?

## 2. Mathematical Foundations

Model the job as a dataflow graph $G=(V,E)$ with operator states $s_v$. A **consistent cut / global snapshot** (Chandy–Lamport, 1985) is a set of local states + in-flight messages forming a state the system *could* have been in; recovery rolls back all operators to the latest snapshot and replays sources from recorded offsets. Correctness requires that replayed output not duplicate already-committed external effects — a **commit/visibility protocol** at the sink.

Exactly-once output reduces to **atomic commitment** of (state snapshot ⊕ source offsets ⊕ sink writes). With non-idempotent sinks this is **two-phase commit (2PC)**: pre-commit on snapshot, commit on snapshot-complete; it inherits 2PC's blocking under coordinator failure and the **FLP impossibility** (no deterministic asynchronous consensus with one crash) — hence reliance on timeouts/leader election.

Idempotency lets us replace 2PC with **deduplication keys** $(\text{partition}, \text{offset})$ and upsert/transactional-id sinks (e.g., Kafka transactional producer with epoch fencing), reducing coordination to a single fenced commit. The minimal-coordination question is: *what is the least synchronization (barrier alignment frequency $T$, number of commit rounds) such that every external effect is committed atomically with the snapshot that produced it?*

## 3. State of the Art (SOTA)

- **Chandy–Lamport** (1985): asynchronous global snapshots — the theoretical basis.
- **Asynchronous Barrier Snapshotting (ABS)** / Flink checkpoints (Carbone et al., 2015–2017): inject barriers at sources; operators snapshot on barrier alignment without stopping the pipeline. **Unaligned checkpoints** (Flink 1.11+) cut alignment stalls under backpressure by snapshotting in-flight data.
- **Two-phase-commit sink** (`TwoPhaseCommitSinkFunction`) + Kafka transactions: end-to-end exactly-once for transactional sinks.
- **Spark Structured Streaming** (Armbrust et al., SIGMOD 2018): exactly-once via write-ahead log + idempotent sinks (offset log + commit log).
- **Google Dataflow / MillWheel** (Akidau et al., VLDB 2013): exactly-once via per-record deterministic IDs, strong-productions, and persistent state with deduplication — minimal-coordination through idempotent record IDs rather than global snapshots.
- **Clonos / rollback-recovery with causal logging** (academic, VLDB 2021): local recovery to avoid global rollback.

## 4. Upper Bound

- With **idempotent or transactional-ID sinks**, exactly-once output costs *amortized* $O(1)$ extra per record (dedup-key check) plus one fenced commit per epoch — MillWheel/Kafka-transaction model. Coordination is **per-epoch, not per-record**, and barriers cost $O(|E|)$ marker messages per checkpoint.
- **ABS** achieves consistent snapshots with **no global pause** for acyclic graphs (cyclic graphs need in-flight logging on back-edges); unaligned checkpointing bounds checkpoint latency independent of backpressure.
- Snapshot cost is amortized by choosing interval $T$ to balance recovery time vs. overhead; **incremental + asynchronous** state snapshots (RocksDB-backed) make per-checkpoint cost proportional to the *delta*, not full state.

## 5. Lower Bound

- **FLP (1985):** no deterministic protocol solves consensus in an asynchronous system with even one crash failure — so any exactly-once commit that requires agreement cannot be both safe and live without partial synchrony/timeouts. Exactly-once output with non-idempotent sinks therefore inherits a fundamental liveness limitation.
- **2PC blocking:** classic result that 2PC blocks on coordinator failure; non-blocking atomic commit (3PC / Paxos-Commit) requires extra rounds — a strict coordination-cost lower bound for non-idempotent sinks.
- **CAP (Gilbert–Lynch, 2002):** under network partition, a sink cannot be both consistent (exactly-once visible) and available — committing must stall.
- **Coordination-avoidance (CALM theorem, Hellerstein–Ameloot et al.):** a query/dataflow can be computed coordination-free **iff** it is *monotone*; exactly-once over non-monotone aggregation/sinks therefore *provably requires* coordination — you cannot get truly zero-coordination exactly-once for general queries.

## 6. The Gap

**Partially solved.** For idempotent/transactional sinks, modern systems get exactly-once at near-minimal (per-epoch) coordination, and CALM tells us *when* coordination is unavoidable. The open gap: **minimizing coordination for the non-monotone / non-idempotent case** — current designs use heavyweight 2PC with epoch-granularity barriers. We lack (a) tight lower bounds on *barrier/commit frequency* as a function of topology and recovery-time objective, and (b) protocols that localize recovery (avoid global rollback) with provable minimal extra logging. Whether per-operator *local* exactly-once recovery can match global-snapshot guarantees at strictly lower coordination cost is open.

## 7. Current Research (as of June 2026)

- **Coordination-free / CALM-guided pipelines:** pushing monotone fragments to need no checkpoints, isolating coordination to non-monotone sinks *(frontier — verify)*.
- **Local recovery & causal logging** (Clonos-style) to avoid global rollback in large stateful jobs; productionization is ongoing *(frontier — verify)*.
- **Unaligned + generic log-based checkpoints** (Flink's changelog state backend) to decouple checkpoint latency from state size.
- **Exactly-once across heterogeneous sinks / lakehouse tables** (Iceberg/Delta transactional commits as the sink atomic-commit substrate) *(frontier — verify)*.
- Active groups: TU Berlin/Flink lineage (Carbone, Markl), Google streaming team (Akidau et al.), Berkeley (Hellerstein, coordination-avoidance), ETH/Systems.

## 8. Future Work

- Tight lower bounds on checkpoint/commit frequency vs. recovery-time objective.
- Provably minimal-coordination exactly-once for non-monotone sinks (beyond 2PC).
- Fine-grained, per-key local recovery with formal guarantees.
- Exactly-once spanning streaming + transactional lakehouse storage with one atomic commit layer.
- Adaptive checkpoint intervals with regret bounds against an optimal fixed schedule.

## 9. Key References

- **[Foundational]** Chandy, Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)
- **[Foundational]** Fischer, Lynch, Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** Carbone, Ewen, Fóra, Haridi, Richter, Tzoumas. *State Management in Apache Flink: Consistent Stateful Distributed Stream Processing.* PVLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137777)
- **[SOTA]** Akidau et al. *MillWheel: Fault-Tolerant Stream Processing at Internet Scale.* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2536222.2536229)
- **[SOTA]** Armbrust et al. *Structured Streaming: A Declarative API for Real-Time Applications in Apache Spark.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3190664)
- **[Foundational]** Hellerstein, Alvaro. *Keeping CALM: When Distributed Consistency Is Easy.* CACM, 2020. — [DOI](https://doi.org/10.1145/3369736)
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)

## 10. Worked Example

A job reads from Kafka topic `clicks` (partition 0), counts events per minute, and writes counts to an external table.

**Idempotent path (minimal coordination).** Tag each output row with the dedup key $(\text{partition}, \text{offset})=(0, 42)$ and `UPSERT`. Suppose offsets 40–42 are processed, the count emitted, then the worker crashes before checkpoint. On recovery the source rewinds to offset 40 and replays 40, 41, 42. The upserts for $(0,40),(0,41),(0,42)$ overwrite identical rows — net effect once. Coordination cost: $O(1)$ dedup check per record, **no commit round**, barriers only $O(|E|)$ markers per checkpoint epoch.

**Non-idempotent path (2PC).** If the sink is a plain SQL table without dedup keys, exactly-once needs a transaction: on barrier the sink *pre-commits* the buffered writes; when the checkpoint completes the coordinator *commits*. A coordinator crash between pre-commit and commit leaves the transaction in-doubt (2PC blocking), and by FLP no asynchronous protocol resolves this without a timeout/leader.

**CALM check.** The count aggregate is non-monotone (a retraction can lower it), so by the CALM theorem this pipeline *provably requires* coordination — the per-epoch barrier+commit is not removable, only minimized.

---
*Part of the [DBMS Research catalog](../../README.md).*
