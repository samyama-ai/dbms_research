# Recovery, Logging & Durability

This topic covers the algorithms and systems that make a database survive crashes: write-ahead logging (WAL) and ARIES-style undo/redo, checkpointing, durability protocols such as group commit, and the redesign of all of these for persistent memory, fast NVMe, RDMA, disaggregated cloud storage, and multicore main-memory engines. It spans formal questions — lower bounds on logging overhead, the complexity of recovery, correctness of crash-consistency protocols — and deep systems questions about achieving instant/constant-time recovery, scaling logging across cores, and reasoning about durability under realistic failure models.

| Problem | Status | Scope |
|---------|--------|-------|
| [Lower bounds on logging overhead](./logging-overhead-lower-bounds.md) | open | Establish tight theoretical lower bounds on the persistent-write and I/O overhead any crash-recoverable durability protocol must pay. |
| [Scalable multicore log manager](./scalable-multicore-logging.md) | partially-solved | Remove the centralized log buffer/LSN as a scalability bottleneck on hundreds of cores while preserving recoverability. |
| [Provably correct ARIES variants](./aries-formal-verification.md) | partially-solved | Produce a machine-checked proof of correctness for a full-featured ARIES implementation including all optimizations. |
| [Constant-time recovery theory](./constant-time-recovery-bounds.md) | empirically-open | Characterize which workloads and storage models admit recovery in time independent of log/database size. |
| [NVM logging without flush ordering](./nvm-flush-ordering.md) | open | Design durability protocols minimizing or eliminating expensive cache-line flush/fence ordering on persistent memory. |
| [Persistent-memory crash-consistency proofs](./pmem-crash-consistency-proofs.md) | partially-solved | Verify crash consistency of PM data structures under realistic out-of-order persistence and partial-write failure models. |
| [Optimal group-commit policy](./optimal-group-commit-policy.md) | empirically-open | Derive a latency-throughput-optimal adaptive group-commit batching policy under unknown arrival distributions. |
| [Distributed WAL with single-copy durability](./distributed-wal-durability.md) | open | Durability that survives correlated failures without paying full N-way log replication cost. |
| [Logical vs physiological logging tradeoff](./logical-physiological-logging.md) | open | Formalize when logical, physical, or physiological logging minimizes total recovery + runtime cost. |
| [Instant recovery for indexes](./instant-recovery-indexes.md) | partially-solved | On-demand, query-driven recovery of B-tree/LSM indexes serving transactions before full restore completes. |
| [Checkpoint scheduling optimization](./checkpoint-scheduling-optimization.md) | empirically-open | Optimal checkpoint frequency/granularity jointly minimizing runtime overhead and bounded recovery time. |
| [Log compression and reclamation bounds](./log-compression-reclamation.md) | open | Bounds on how compactly a recoverable log can be encoded and how aggressively it can be truncated. |
| [Durable lock-free data structures](./durable-lock-free-structures.md) | partially-solved | Lock-free structures that are both linearizable and durably linearizable on PM with low persistence cost. |
| [Recovery under partial/torn writes](./torn-write-recovery.md) | partially-solved | Guaranteeing recoverability when the storage device can tear or partially apply a write atomically. |
| [Cross-media log tiering](./cross-media-log-tiering.md) | open | Placing log records across PM/SSD/cloud tiers to optimize commit latency and recovery time jointly. |
| [Logging for disaggregated storage](./disaggregated-storage-logging.md) | empirically-open | WAL and recovery when compute and storage are separated by a network with independent failure domains. |
| [Group commit vs early lock release](./group-commit-lock-release.md) | open | Safely overlap commit-durability latency with releasing locks without violating recoverability. |
| [Adaptive logging granularity](./adaptive-logging-granularity.md) | empirically-open | Dynamically switch between row/page/command logging based on workload to minimize log volume. |
| [Recovery correctness under weak memory](./weak-memory-recovery.md) | open | Specify and verify durability protocols against realistic weak persistency memory-consistency models. |
| [Parallel log replay scalability](./parallel-log-replay.md) | partially-solved | Maximally parallelize redo/undo replay while respecting dependency constraints for fast recovery. |
| [Single-pass vs multi-pass recovery](./single-pass-recovery.md) | open | When can ARIES's three-pass recovery be provably reduced to fewer passes without losing generality. |
| [Durability for deterministic databases](./deterministic-db-durability.md) | partially-solved | Replace physical logging with input/command logging in deterministic engines while bounding recovery. |
| [Non-volatile WAL buffer semantics](./nvram-wal-buffer.md) | empirically-open | Exploiting a small NVRAM log tail to eliminate commit-path fsync without losing durability guarantees. |
| [Recovery for compressed/encrypted logs](./compressed-encrypted-log-recovery.md) | open | Recoverability and integrity when log records are compressed and/or encrypted at rest and in flight. |
| [Bounded staleness durability tradeoff](./bounded-staleness-durability.md) | open | Formalize the achievable tradeoff between commit latency, durability lag, and data-loss bounds. |
| [Crash-consistency testing/fuzzing](./crash-consistency-fuzzing.md) | empirically-open | Systematically generating crash schedules that expose durability/recovery bugs in real engines. |
| [Self-tuning recovery parameters](./self-tuning-recovery.md) | empirically-open | Autonomous control of checkpoint/log/commit parameters to meet recovery-time SLAs under shifting load. |
| [Log-structured durability for OLTP](./log-structured-oltp-durability.md) | open | Making the log the database (log-is-database) while keeping point-query and recovery costs bounded. |
| [Epoch-based durability commit](./epoch-based-durability.md) | partially-solved | Coarse epoch-grained persistence (Silo-style) with provable bounds on data loss and recovery latency. |
| [Recovery-time SLO guarantees](./recovery-time-slo.md) | open | Provide provable worst-case recovery-time guarantees as a first-class, schedulable resource. |

> Back to [Taxonomy](../../TAXONOMY.md)
