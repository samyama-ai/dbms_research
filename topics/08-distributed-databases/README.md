# Distributed Query Processing

Distributed query processing studies how to evaluate relational and analytical
queries across many machines connected by a network, where communication, not just
computation, is the dominant cost. The central tensions are minimizing data movement
(via partitioning, semijoin reduction, and shuffle scheduling), tolerating skew and
stragglers, and reasoning about the communication-complexity lower bounds that govern
what any distributed algorithm can achieve. This topic spans both theory
(massively-parallel-computation rounds/load bounds, communication complexity,
worst-case-optimal distributed joins) and systems (exchange operators, adaptive
repartitioning, skew handling, distributed aggregation at cloud scale).

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal Round Complexity for Distributed Joins](./mpc-round-complexity-joins.md) | open | Pin down the exact number of MPC rounds needed to evaluate arbitrary conjunctive queries under a given per-machine load budget. |
| [Load Balancing for Skewed Multi-way Joins](./skew-optimal-mpc-load.md) | partially-solved | Achieve provably load-balanced one-round evaluation of multi-way joins under arbitrary value-frequency skew. |
| [Worst-Case-Optimal Distributed Joins](./distributed-wcoj.md) | partially-solved | Build a distributed join whose total communication matches the AGM/output-size bound for cyclic queries. |
| [Optimal Semijoin Reduction Programs](./optimal-semijoin-programs.md) | open | Compute the communication-minimal sequence of semijoins that fully reduces a (cyclic) query before final assembly. |
| [Partition Scheme Selection Under Workloads](./workload-aware-partitioning.md) | open | Choose a data-partitioning layout that minimizes expected cross-node traffic over an evolving query workload. |
| [Co-Partitioning for Join Graphs](./co-partitioning-join-graphs.md) | open | Decide whether a database can be partitioned so all queries in a workload join locally, and how close one can get. |
| [Adaptive Repartitioning Mid-Query](./adaptive-repartitioning.md) | empirically-open | Detect at runtime that a chosen partitioning is wrong and re-shuffle with provable amortized cost. |
| [Straggler Mitigation Without Over-Replication](./straggler-mitigation-theory.md) | partially-solved | Bound the redundancy needed to mask the slowest machines in a distributed query stage. |
| [Coded Computing for Relational Operators](./coded-distributed-joins.md) | empirically-open | Apply coded-computation redundancy to joins/aggregations to trade communication for straggler tolerance. |
| [Shuffle Scheduling Lower Bounds](./shuffle-scheduling-bounds.md) | open | Characterize the minimum makespan of an all-to-all shuffle under heterogeneous link bandwidths. |
| [Skew-Resilient Distributed Aggregation](./skew-resilient-aggregation.md) | partially-solved | Compute group-by aggregates when a few groups dominate, without a single hot reducer. |
| [Holistic Aggregates in MPC](./holistic-aggregates-mpc.md) | open | Evaluate non-decomposable aggregates (median, distinct-count, mode) with optimal rounds and load. |
| [Communication-Optimal Top-k Across Nodes](./distributed-topk-communication.md) | partially-solved | Minimize bytes exchanged to retrieve global top-k from horizontally partitioned scored data. |
| [Distributed Theta-Join Partitioning](./theta-join-partitioning.md) | partially-solved | Partition non-equi (theta) joins across reducers with balanced load and minimal duplication. |
| [Multi-Query Shuffle Sharing](./multi-query-shuffle-sharing.md) | open | Share exchange/shuffle work across concurrent queries to cut aggregate network cost. |
| [Distributed Join Order with Network Cost](./network-aware-join-ordering.md) | open | Optimize join order and redistribution strategy jointly under a topology-aware cost model. |
| [Elastic Reshuffle Under Autoscaling](./elastic-reshuffle.md) | empirically-open | Redistribute in-flight query state when the cluster grows or shrinks during execution. |
| [Bandwidth-Tagged Cost Models](./topology-aware-cost-models.md) | open | Build a cost model capturing rack/zone/region bandwidth tiers that yields robust distributed plans. |
| [Distributed Recursive Query Evaluation](./distributed-recursive-queries.md) | partially-solved | Evaluate Datalog/transitive-closure queries across nodes with bounded rounds and communication. |
| [Semijoin Reducers for Cyclic Queries](./cyclic-query-semijoins.md) | open | Extend full-reducer theory beyond acyclic queries via generalized hypertree decompositions. |
| [Provably Fault-Tolerant Query Restart](./fault-tolerant-query-restart.md) | partially-solved | Recover a long distributed query from mid-stage failures without full re-execution, with cost bounds. |
| [Heavy-Hitter-Aware Join Routing](./heavy-hitter-join-routing.md) | partially-solved | Route only frequent join keys specially while keeping the light tail uniformly hashed. |
| [Distributed Cardinality for Repartitioning](./distributed-cardinality-shuffle.md) | empirically-open | Estimate intermediate sizes cheaply across nodes to drive shuffle and broadcast-vs-repartition choices. |
| [Broadcast-vs-Shuffle Decision Bounds](./broadcast-vs-shuffle.md) | partially-solved | Determine when broadcasting the small side beats repartitioning both, under uncertain cardinalities. |
| [Multi-Round Tradeoffs in MPC Joins](./mpc-rounds-vs-load-tradeoff.md) | open | Characterize the Pareto frontier between number of rounds and per-machine load for join queries. |
| [Locality-Aware Shuffle Placement](./locality-aware-shuffle.md) | empirically-open | Place shuffle partitions to exploit data locality and minimize cross-zone egress cost. |
| [Distributed Window-Function Evaluation](./distributed-window-functions.md) | open | Partition and order data for SQL window functions with minimal repartitioning and balanced load. |
| [Skew Detection vs Mitigation Latency](./online-skew-detection.md) | empirically-open | Detect emerging partition skew early enough to react without paying a full extra shuffle. |
| [Communication Complexity of Set Joins](./set-similarity-join-communication.md) | open | Establish tight communication bounds for distributed set-similarity and band joins. |
| [Disaggregated-Storage Shuffle Design](./disaggregated-shuffle.md) | empirically-open | Design a shuffle layer over disaggregated/object storage that decouples compute elasticity from exchange. |

---
*Back to [TAXONOMY.md](../../TAXONOMY.md).*
