# NewSQL & Distributed SQL

NewSQL and distributed-SQL systems pursue the holy grail of strong (often serializable)
ACID semantics over horizontally partitioned, geo-replicated data while retaining SQL and
elastic scale-out. This topic catalogs open problems spanning the theory and engineering of
distributed atomic commit, deterministic execution, physical/logical clocks (TrueTime/HLC),
distributed snapshot isolation, and the consistency–latency tradeoffs of geo-distribution.

| Problem | Status | Scope |
|---|---|---|
| [Optimal latency for distributed strict serializability](./latency-lower-bound-strict-serializability.md) | open | Tight lower bounds on commit latency for strict serializability under geo-distributed replication and failures. |
| [Atomic commit without blocking under partitions](./nonblocking-atomic-commit-partitions.md) | partially-solved | Non-blocking distributed commit that tolerates network partitions without a single coordinator failure stall. |
| [Clock-uncertainty-free external consistency](./external-consistency-without-clock-bounds.md) | open | Achieving Spanner-style external consistency without bounded-error physical clocks like TrueTime. |
| [Tightening HLC drift bounds](./hlc-drift-bounds.md) | partially-solved | Provable freshness/staleness bounds for hybrid logical clocks under adversarial drift. |
| [Deterministic execution with dynamic read/write sets](./deterministic-dynamic-rwsets.md) | open | Deterministic databases when transaction access sets are not known a priori. |
| [One-shot vs interactive deterministic transactions](./deterministic-interactive-transactions.md) | partially-solved | Supporting interactive (multi-round) transactions in deterministic systems without losing replica determinism. |
| [Distributed snapshot isolation anomaly characterization](./distributed-si-anomalies.md) | partially-solved | Complete characterization of write-skew-class anomalies under distributed/partitioned SI. |
| [Minimizing coordination for serializability](./minimal-coordination-serializability.md) | partially-solved | Determining the coordination-free fragment of workloads that still guarantees serializability. |
| [Geo-distributed transaction routing under SLAs](./geo-transaction-routing-slas.md) | empirically-open | Placement and routing of transactions across regions to meet latency SLAs at minimum cost. |
| [Read-only transaction latency lower bounds](./readonly-transaction-latency-bounds.md) | open | Whether wait-free, single-round, strongly consistent read-only transactions are achievable. |
| [Adaptive isolation level selection](./adaptive-isolation-selection.md) | empirically-open | Automatically choosing the weakest isolation level that preserves application correctness. |
| [Dynamic resharding of live transactional data](./live-resharding-transactional.md) | partially-solved | Online repartitioning of a transactional keyspace with zero downtime and preserved isolation. |
| [Commit protocol for heterogeneous replica clocks](./commit-heterogeneous-clocks.md) | open | Correct timestamp ordering when replicas have clocks of differing accuracy/uncertainty. |
| [Bounding staleness in follower reads](./follower-read-staleness.md) | partially-solved | Tight, workload-aware bounds on staleness for serving reads from non-leader replicas. |
| [Distributed deadlock detection at scale](./distributed-deadlock-detection.md) | partially-solved | Low-overhead, false-positive-free deadlock detection across thousands of shards. |
| [Determinism vs. throughput tradeoff](./determinism-throughput-tradeoff.md) | open | Fundamental limits on throughput imposed by deterministic ordering versus opportunistic concurrency. |
| [Cross-shard secondary index consistency](./cross-shard-secondary-index.md) | partially-solved | Maintaining strongly consistent global secondary indexes over a sharded primary without 2PC per write. |
| [Failure-free fast-path commit conditions](./fast-path-commit-conditions.md) | partially-solved | Characterizing when one-round-trip (fast-path) commit is safe versus requiring full consensus. |
| [Geo-replicated SI with bounded abort rate](./geo-si-bounded-aborts.md) | open | Snapshot isolation across regions with provable bounds on cross-region write-conflict aborts. |
| [Clock synchronization failure semantics](./clock-failure-semantics.md) | empirically-open | Safety and liveness of TrueTime/HLC systems when clock sync degrades or fails silently. |
| [Elastic scaling without transaction stalls](./elastic-scaling-no-stalls.md) | empirically-open | Adding/removing nodes mid-flight without aborting or pausing in-flight distributed transactions. |
| [Deterministic recovery and replay determinism](./deterministic-recovery-replay.md) | partially-solved | Guaranteeing bit-identical state across replicas after crash recovery and log replay. |
| [Multi-region write conflict minimization](./multiregion-write-conflict-minimization.md) | open | Data placement and partitioning to provably minimize cross-region conflicting writes. |
| [Verifying distributed isolation in production](./verifying-isolation-production.md) | empirically-open | Black-box runtime checking that a deployed system actually delivers its claimed isolation level. |
| [Transactional throughput under skewed hot keys](./hot-key-transactional-throughput.md) | empirically-open | Sustaining serializable throughput when a few keys absorb most contention across shards. |
| [Composable cross-database distributed transactions](./cross-database-transactions.md) | open | ACID transactions spanning independent autonomous distributed-SQL systems. |
| [Bounded-staleness query optimization](./bounded-staleness-optimization.md) | partially-solved | Query planner that exploits a staleness budget to route reads for minimal latency. |
| [Watermark/safe-time computation cost](./safe-time-watermark-cost.md) | partially-solved | Efficient computation of the global safe-timestamp/resolved-watermark for consistent reads. |
| [Serializability certification overhead bounds](./serializability-certification-overhead.md) | open | Lower bounds on the validation/certification cost of optimistic distributed serializability. |
| [Mixed deterministic/nondeterministic execution](./hybrid-deterministic-execution.md) | open | Combining deterministic and traditional concurrency control in one engine without anomalies. |

---
*Back to [TAXONOMY.md](../../TAXONOMY.md).*
