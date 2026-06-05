# Logging for disaggregated storage

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/disaggregated-storage-logging` · **Status:** empirically-open

## 1. Problem Statement

In **disaggregated** architectures, compute nodes and storage nodes are separated by a network (RDMA fabric, NVMe-oF, or a cloud storage service), and the two sides constitute **independent failure domains**: a compute node can crash with in-flight log records the storage side never received, or storage can be reachable while compute is partitioned. The problem: **design the write-ahead log and recovery protocol so durability, recoverability, and consistency hold when WAL travels over an unreliable network between independently-failing tiers.**

Sub-questions: where is the *durable point* (when may compute acknowledge commit)? How does recovery proceed when the recovering node is *not* the node that generated the log? How are torn/partial network writes, reordering, and duplicate delivery handled? How is the log truncated/checkpointed across the boundary?

Variants: (a) *decision* — does a protocol preserve the committed prefix under all crash/partition combinations? (b) *optimization* — minimize commit round trips and recovery time over the network; (c) *availability* — bound recovery/failover time after a compute failure.

## 2. Mathematical Foundations

Model two state machines: compute $C$ (volatile state $V_C$, lost on crash) and storage $S$ (durable state $P_S$), connected by an asynchronous, lossy, reordering channel. A commit is *durable* only once its log records are in $P_S$ (or a quorum of storage replicas), **not** when they leave $C$ — so the protocol needs an acknowledgment round trip. This is the **shared-log / log-is-the-database** model (Aurora's "the log is the database").

Recoverability requires that $P_S$ always reflects a **consistent prefix** of the commit order. Because the channel can reorder, log records carry a total order (LSN) and storage must apply them prefix-consistently (gap-free), echoing **state-machine replication**: storage replicas agree on a log prefix. Cross-domain failure invokes the **FLP impossibility** (no deterministic consensus with one crash in a fully asynchronous network) and **CAP**: under a compute/storage partition, you cannot have both availability and linearizable durability. Practical systems sidestep FLP with partial synchrony + a consensus core (Paxos/Raft) for the log.

Key invariant (Aurora-style): storage nodes accept log records, gossip to fill gaps, and advance a **Volume Complete LSN** (VCL) — the highest LSN below which the log is gap-free and durable; commit visibility is gated on VCL, giving the formal "durable prefix."

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **Amazon Aurora** (Verbitski et al., SIGMOD 2017; 2018 follow-up on quorums/durability) ships redo log to a 6-way (3-AZ) quorum, commits on a 4/6 write quorum, and recovers by having storage nodes reconstruct pages from log — the canonical disaggregated WAL. **Microsoft Socrates** (SIGMOD 2019) splits a log service (XLOG landing zone) from page servers. **PolarDB** (shared storage), **Taurus** (Huawei, VLDB 2020), **Neon** (WAL safekeepers using Paxos + page servers replaying from object storage) realize variants *(frontier — verify)*. RDMA-based designs (**FaRM**, **Tell**) push log over one-sided RDMA.
- **Theory-SOTA:** Grounded in state-machine replication and shared-log abstractions (**CORFU**, Balakrishnan et al., NSDI 2012; **Delos/virtual consensus**). No closed theory specific to the compute/storage failure-domain split.

## 4. Upper Bound

Constructive results: **commit in one network round trip to a write quorum** (Aurora: 4-of-6, sub-millisecond on RDMA-class fabrics), with recovery that is **near-instant for the compute side** (a fresh compute node attaches to durable storage; no redo on the compute critical path — storage applies log lazily/on-demand). For the log/consensus core, **one round trip per commit** to a quorum is achievable, amortizable via batching to $O(1/k)$ per commit. Recovery time is bounded by re-establishing the durable prefix (VCL) and on-demand page reconstruction, decoupled from total log size.

## 5. Lower Bound

- **Round-trip floor:** with independent failure domains, compute cannot acknowledge a commit before storage durably holds it — $\ge 1$ network round trip on the commit path (the "no premature ack" durability floor, now paying network latency).
- **Consensus / FLP:** advancing a durable, gap-free prefix across replicated storage under crashes is a consensus problem; FLP forbids a deterministic asynchronous solution, so liveness needs partial synchrony or randomization.
- **CAP:** under a compute–storage partition, no protocol provides both availability and linearizable durable commits.
- **Quorum intersection:** to tolerate $f$ storage failures with read/write quorums, $|W| + |R| > N$ and $|W| > f$ (Lamport/quorum bounds), lower-bounding replication cost.
- No tight problem-specific fine-grained lower bound exists; this is "empirically-open" — bounds are borrowed, the engineering trade space is explored mainly by measurement.

## 6. The Gap

Empirically open: production systems demonstrate one-round-trip commit and fast failover, but there is **no unifying model** quantifying the achievable frontier of {commit latency, recovery/failover time, replication cost, availability under partition} as a function of network synchrony and failure-domain independence. The gap is between borrowed worst-case theory (FLP/CAP/quorums) and the rich, measured behavior of real disaggregated stacks; closing it needs a model that captures the compute/storage split as first-class and yields matching bounds for, e.g., the minimum failover time given an SLO on commit latency.

## 7. Current Research (as of June 2026)

Active threads: WAL over CXL-attached / fabric-attached memory shortening the durable-point round trip *(frontier — verify)*; "log-as-a-service" disaggregation (Neon, Aurora, Socrates) and serverless databases where cold-start recovery dominates; virtual consensus / reconfigurable shared logs (Delos) for the storage log core; RDMA and NVMe-oF logging research (TUM, MIT, Microsoft Research, AWS). Open empirical question: optimal placement of the consensus core relative to storage replicas.

## 8. Future Work

- A first-class compute/storage failure-domain model with matching latency/recovery lower bounds.
- Minimizing commit round trips via fabric-attached persistent memory as the durable landing zone.
- Failover-time-optimal designs under explicit availability SLOs.
- Formal verification of cross-domain recovery (gap-free prefix, exactly-once application under reordering/duplication).

## 9. Key References

- **[SOTA]** Alexandre Verbitski, Anurag Gupta, Debanjan Saha, Murali Brahmadesam, Kamal Gupta, et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017.
- **[SOTA]** Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019.
- **[Foundational]** Mahesh Balakrishnan, Dahlia Malkhi, Vijayan Prabhakaran, et al. *CORFU: A Shared Log Design for Flash Clusters.* NSDI, 2012.
- **[Foundational]** Michael Fischer, Nancy Lynch, Michael Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[Foundational]** Seth Gilbert, Nancy Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002.

---
*Part of the [DBMS Research catalog](../../README.md).*
