# Concurrency Control

Concurrency control governs how a database admits interleaved transactions while preserving a chosen correctness criterion (serializability and its weaker isolation cousins). The field spans deep theory — the complexity of testing serializability, the expressive limits of conflict graphs, the characterization of anomalies under weak isolation — and hard systems engineering — scalable lock managers, multi-version garbage collection, deterministic execution, and contention-aware scheduling on modern hardware. The problems below mix open complexity questions with empirically open engineering challenges that recur at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT.

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal Schedule Recognition Complexity](./view-serializability-complexity.md) | open | Pinning the exact complexity landscape of testing view-serializability and related recognition problems beyond the classic NP-completeness result. |
| [Robustness Against Snapshot Isolation Anomalies](./si-robustness-characterization.md) | partially-solved | Deciding which workloads are guaranteed serializable when run under snapshot isolation, with tight syntactic and graph-theoretic criteria. |
| [MVCC Garbage Collection Theory](./mvcc-version-gc.md) | empirically-open | Bounding version-chain length and reclaiming dead tuple versions optimally without scanning under long-running readers. |
| [Deterministic Execution Without Pre-Declared Reads/Writes](./deterministic-unknown-rwset.md) | open | Achieving deterministic concurrency control when transaction read/write sets are not known a priori. |
| [Contention-Aware Scheduling Optimality](./contention-aware-scheduling.md) | open | Computing schedules that minimize lock conflicts / abort rate under contention as a combinatorial optimization problem. |
| [Lower Bounds on Lock-Manager Throughput](./lock-manager-scalability-bounds.md) | empirically-open | Establishing fundamental scalability limits of centralized lock managers on many-core hardware. |
| [Isolation-Level Anomaly Completeness](./isolation-anomaly-taxonomy.md) | partially-solved | A complete, formally verified lattice of anomalies distinguishing all commercial isolation levels. |
| [Serializable MVCC With One Version Read](./serializable-mvcc-single-read.md) | open | Whether serializability is achievable under MVCC while each read touches at most one version with no extra validation cost. |
| [Optimistic vs Pessimistic Crossover Prediction](./occ-2pl-crossover.md) | empirically-open | Predicting, per workload, the contention point at which OCC beats 2PL and vice versa, online. |
| [Phantom Prevention Without Predicate Locks](./phantom-prevention-cost.md) | partially-solved | Minimizing the cost of preventing phantoms without full predicate locking or index gap locks. |
| [Conflict-Graph Cycle Detection at Scale](./dependency-cycle-detection.md) | empirically-open | Detecting dangerous dependency-graph cycles online with bounded overhead in serializable SI. |
| [Hardware Transactional Memory for OLTP](./htm-for-oltp.md) | empirically-open | Exploiting bounded HTM for database concurrency control despite capacity/abort limits. |
| [Distributed Deadlock Detection Optimality](./distributed-deadlock-detection.md) | open | Minimizing message and latency cost of detecting distributed deadlocks with no false positives. |
| [Adaptive Isolation Level Selection](./adaptive-isolation-selection.md) | open | Automatically choosing the weakest isolation level per transaction that preserves application invariants. |
| [Time-Stamp Allocation Without Global Clocks](./timestamp-allocation-scalable.md) | empirically-open | Scalable monotonic timestamp generation for MVCC without a centralized counter bottleneck. |
| [Provably Correct Weak-Isolation Programming](./weak-isolation-verification.md) | partially-solved | Verifying that application code remains correct under a given weak isolation level. |
| [Abort-Free Concurrency Control Limits](./abort-free-cc-limits.md) | open | Characterizing workload classes admitting wait/abort-free serializable execution. |
| [Range-Conflict Serializability Theory](./range-conflict-serializability.md) | open | Extending serializability theory to predicate/range operations with tight recognition complexity. |
| [Multi-Version Conflict Minimization](./multiversion-conflict-minimization.md) | open | Choosing version read points to minimize conflicts (MVSR) — known NP-hard, seeking practical structure. |
| [Epoch-Based Concurrency Control Tradeoffs](./epoch-based-cc.md) | empirically-open | Quantifying latency/throughput tradeoffs of batching commits into epochs for serializability. |
| [Long-Running Read-Only Transaction Isolation](./long-read-only-isolation.md) | empirically-open | Serving consistent long analytical reads over a hot OLTP store without blocking or version bloat. |
| [Lock-Free Index Concurrency Correctness](./lock-free-index-correctness.md) | partially-solved | Proving linearizability of lock-free B-tree/skip-list indexes integrated with transactional isolation. |
| [Contention-Aware Data Partitioning](./contention-aware-partitioning.md) | open | Partitioning data/transactions to minimize cross-partition coordination given a contention model. |
| [Commutativity-Based Concurrency Exploitation](./commutativity-concurrency.md) | partially-solved | Automatically inferring and exploiting operation commutativity to raise concurrency safely. |
| [Hybrid OLTP/OLAP Snapshot Consistency](./htap-snapshot-consistency.md) | empirically-open | Providing consistent fresh snapshots to analytics colocated with transactional updates. |
| [Write-Skew Detection and Repair](./write-skew-detection.md) | partially-solved | Statically/dynamically detecting and preventing write-skew anomalies with minimal added serialization. |
| [Deterministic DB Throughput Under Skew](./deterministic-db-skew.md) | empirically-open | Sustaining throughput in deterministic databases when key access is highly skewed. |
| [Real-Time Concurrency Control Guarantees](./real-time-cc-deadlines.md) | open | Concurrency control with provable deadline-miss bounds for real-time transactions. |
| [Coordination Avoidance Boundaries](./coordination-avoidance.md) | partially-solved | Precisely characterizing which invariants permit coordination-free (invariant-confluent) execution. |
| [Energy-Optimal Concurrency Control](./energy-aware-cc.md) | open | Minimizing energy per committed transaction as a first-class concurrency-control objective. |

---
*Back to [TAXONOMY.md](../../TAXONOMY.md).*
