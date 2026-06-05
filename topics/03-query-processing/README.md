# Query Processing & Execution

Query processing turns a logical plan into actual computation: how joins, aggregations,
sorts, top-k, and set operations are evaluated over relations, multisets, and streams.
This topic spans the **theory** frontier — worst-case-optimal join algorithms, the AGM
bound and its refinements, fine-grained lower bounds for joins and similarity operators,
the complexity of aggregation and enumeration — and the **systems** frontier — vectorized
vs. compiled execution, cache- and SIMD-conscious operators, parallel/NUMA-aware
scheduling, spilling, and pushdown. The unifying question is how close real engines can
get to information-theoretic and fine-grained limits while remaining robust, parallel,
and adaptive on real hardware.

| Problem | Status | Scope |
|---------|--------|-------|
| [Practical worst-case-optimal join engines](./wcoj-practical-engine.md) | partially-solved | Making WCOJ algorithms competitive with binary-join engines across real workloads, not just adversarial ones. |
| [Beyond-AGM bounds with functional dependencies](./beyond-agm-degree-bounds.md) | partially-solved | Tight output-size bounds and matching algorithms when degree constraints and FDs are present (the entropy/polymatroid frontier). |
| [Optimal hybrid binary/WCOJ plans](./hybrid-binary-wcoj-optimization.md) | open | Choosing per-subquery between binary joins, WCOJ, and tree decompositions to minimize true running time. |
| [Instance-optimal join evaluation](./instance-optimal-joins.md) | open | Algorithms whose cost matches the best possible on each specific instance, not just worst case (certificate complexity). |
| [Faster-than-AGM joins via fast matrix multiplication](./join-matrix-multiplication.md) | solved-but-impractical | When and how subcubic matrix multiplication beats combinatorial joins, and whether it can be made practical. |
| [Worst-case-optimal enumeration with delay guarantees](./wco-enumeration-delay.md) | partially-solved | Constant/polylog-delay enumeration of join results after near-linear preprocessing for general queries. |
| [Compiled vs. vectorized execution unification](./compiled-vs-vectorized.md) | empirically-open | A principled framework (and engine) that gets the best of data-centric compilation and vectorized interpretation. |
| [Optimal vector batch / morsel sizing](./vector-batch-sizing.md) | empirically-open | Choosing batch and morsel granularity to balance cache residency, SIMD utilization, and instruction overhead. |
| [Robust adaptive hash vs. sort decisions](./adaptive-hash-vs-sort.md) | open | Online, robust selection between hashing and sorting for joins/aggregation under unknown data properties. |
| [Cache- and SIMD-optimal hash joins](./cache-simd-hash-join.md) | empirically-open | Hash-join layouts and probing that minimize cache misses and maximize SIMD/gather throughput across architectures. |
| [Skew-resilient parallel join scheduling](./skew-resilient-parallel-join.md) | partially-solved | Load-balanced parallel joins under heavy value skew without prior statistics or excessive repartitioning. |
| [NUMA-aware operator placement](./numa-aware-execution.md) | empirically-open | Data and thread placement that minimizes cross-socket traffic for joins/aggregation on many-core NUMA machines. |
| [Optimal external-memory / spilling joins](./external-memory-spilling-joins.md) | partially-solved | I/O-optimal join and aggregation execution under bounded memory with graceful, predictable spilling. |
| [Worst-case-optimal grouped aggregation](./wco-grouped-aggregation.md) | open | Aggregation over join results without fully materializing the join (FAQ / functional aggregate queries). |
| [Holistic and distinct aggregate evaluation](./holistic-distinct-aggregates.md) | partially-solved | Efficient exact evaluation of MEDIAN, COUNT-DISTINCT, and other holistic aggregates inside execution engines. |
| [Optimal top-k operator algorithms](./optimal-topk-operators.md) | partially-solved | Instance-optimal threshold-style top-k over joins and expensive predicates beyond the classic TA/NRA model. |
| [Top-k with expensive / ML predicates](./topk-expensive-predicates.md) | open | Ordering and short-circuiting top-k when scoring functions are costly UDFs or model inferences. |
| [Cache-oblivious in-memory sorting](./cache-oblivious-sorting.md) | partially-solved | Sorting that is simultaneously cache-, SIMD-, and branch-efficient without architecture-specific tuning. |
| [Massively parallel sorting lower bounds](./parallel-sorting-lower-bounds.md) | open | Tight round/communication bounds for sorting and order-by in the MPC / shuffle model. |
| [Set operations and multiset semantics complexity](./set-operation-complexity.md) | partially-solved | Optimal algorithms and bounds for intersection/union/difference with bag semantics and duplicate handling. |
| [Pipeline breaker minimization](./pipeline-breaker-scheduling.md) | open | Scheduling and plan shaping that minimizes materialization at pipeline breakers (sorts, builds, aggregations). |
| [Robust runtime adaptivity (eddies redux)](./runtime-adaptive-reoptimization.md) | empirically-open | Mid-query re-routing and re-optimization that provably never regresses below the static plan. |
| [Sideways information passing at execution](./sideways-information-passing.md) | partially-solved | Runtime filter (semijoin/Bloom) generation and placement to provably prune work across operators. |
| [Optimal learned/adaptive Bloom-filter pushdown](./adaptive-bloom-pushdown.md) | empirically-open | When to build, size, and push runtime filters to maximize pruning minus overhead, adaptively. |
| [GPU-resident join and aggregation execution](./gpu-query-execution.md) | empirically-open | End-to-end query execution on GPUs with PCIe/HBM bottlenecks, irregular memory access, and spilling. |
| [Query execution over compressed data](./execution-on-compressed-data.md) | partially-solved | Joining, aggregating, and sorting directly on encoded/compressed columns without full decompression. |
| [Provenance-aware / semiring execution cost](./semiring-aware-execution.md) | open | Executing aggregation and joins over general semirings (provenance, probabilities) with minimal overhead. |
| [Recursive and fixpoint query execution](./recursive-fixpoint-execution.md) | open | Efficient set-at-a-time evaluation of recursive/Datalog and WITH RECURSIVE with semi-naive and beyond. |
| [Multi-query / shared execution scheduling](./shared-execution-scheduling.md) | partially-solved | Sharing scans, joins, and computation across concurrent queries to minimize total work (work-sharing). |
| [Energy-optimal query execution](./energy-optimal-execution.md) | empirically-open | Minimizing energy (not just time) for execution plans across heterogeneous cores and accelerators. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
