# Query Optimization

Query optimization transforms a declarative query into an efficient physical execution plan by
searching a combinatorially large space of join orders, access paths, and operators guided by a
cost model and cardinality estimates. The field spans deep theory — the NP-hardness of join
ordering, the complexity of plan enumeration, parametric and robust optimization — and hard
systems engineering — extensible rule-based optimizers, adaptive re-optimization, learned cost
models, and multi-query sharing. This index catalogs 30 open and hard problems at the frontier of
both the theory and the systems of query optimization.

| Problem | Status | Scope |
|---|---|---|
| [Optimal join ordering complexity for general query graphs](./join-ordering-complexity.md) | open | Settling the exact tractability boundary of optimal bushy join ordering across query-graph classes and cost functions. |
| [Optimal join ordering under cross products](./join-order-cross-products.md) | open | Characterizing when admitting cross products is needed for optimality and the complexity it induces. |
| [Worst-case-optimal join order vs. binary plans](./wcoj-vs-binary-plans.md) | partially-solved | Bridging multiway worst-case-optimal joins with classical binary-join cost-based ordering in one optimizer. |
| [Provably good cost-model-robust join orders](./robust-join-orders.md) | open | Finding join orders that are near-optimal across an uncertainty set of cost/cardinality inputs. |
| [Cardinality estimation error propagation through plans](./cardinality-error-propagation.md) | open | Bounding how per-operator estimation error amplifies into end-to-end plan cost error. |
| [Cost models that predict real runtime](./cost-model-runtime-fidelity.md) | empirically-open | Building cost models whose ordering of plans matches measured wall-clock time on modern hardware. |
| [Plan enumeration without cardinality oracle](./enumeration-without-oracle.md) | open | Optimizing when reliable cardinalities are unavailable, replacing point estimates with bounds or distributions. |
| [Optimal dynamic-programming join enumeration scaling](./dp-enumeration-scaling.md) | partially-solved | Pushing exact DP join enumeration to dozens of relations within practical time and memory. |
| [Top-down vs. bottom-up search space coverage](./search-strategy-coverage.md) | partially-solved | Characterizing which plans each search paradigm can reach and unifying their guarantees. |
| [Transformation-rule completeness and confluence](./transformation-rule-completeness.md) | open | Determining whether a rule set generates the full logical equivalence class and terminates deterministically. |
| [Cascades-style rule scheduling and pruning](./cascades-rule-scheduling.md) | empirically-open | Principled ordering and branch-and-bound pruning of transformation-rule firings in extensible optimizers. |
| [Parametric query optimization plan-space size](./parametric-plan-space.md) | partially-solved | Bounding the number of optimal plans over a parameter space and computing the parametric decomposition. |
| [Adaptive mid-query re-optimization](./adaptive-reoptimization.md) | empirically-open | Deciding when and how to change a running plan as actual cardinalities are observed. |
| [Robust plans minimizing worst-case suboptimality](./robust-plan-selection.md) | open | Selecting a single plan that minimizes maximum cost regret over a parameter/uncertainty region. |
| [Multi-query optimization shared-subexpression search](./multi-query-optimization.md) | open | Optimally identifying and scheduling shared subexpressions across a batch of queries. |
| [Optimizing queries with user-defined functions](./udf-optimization.md) | partially-solved | Costing, reordering, and inlining opaque UDFs and procedural code inside declarative plans. |
| [Subquery decorrelation and unnesting completeness](./subquery-decorrelation.md) | partially-solved | A complete, cost-aware rewrite framework for arbitrarily nested correlated subqueries. |
| [Optimizing recursive and fixpoint queries](./recursive-query-optimization.md) | open | Cost-based ordering and termination-aware planning for recursive CTEs and Datalog. |
| [Order optimization and interesting orders](./order-optimization.md) | partially-solved | Propagating and exploiting sort/grouping properties across operators in plan enumeration. |
| [Optimizing under materialized views and rewriting](./view-selection-rewriting.md) | open | Jointly choosing views to materialize and rewriting queries to use them optimally. |
| [Plan diagram smoothness and selectivity geometry](./plan-diagram-geometry.md) | empirically-open | Explaining and controlling the geometry of optimal-plan regions over the selectivity space. |
| [Learned cost models with reliability guarantees](./learned-cost-models.md) | empirically-open | Cost models from ML that generalize to unseen queries with calibrated uncertainty. |
| [Learned/RL join-order optimizers vs. classical](./learned-join-optimizers.md) | empirically-open | When learned plan-search policies beat cost-based search and with what guarantees. |
| [Optimizing across the memory hierarchy and parallelism](./parallel-aware-optimization.md) | open | Cost-based planning that jointly accounts for intra-query parallelism, NUMA, and caches. |
| [Distributed and cloud-aware plan optimization](./distributed-plan-optimization.md) | open | Planning with network, shuffle, data placement, and disaggregated-storage cost terms. |
| [Optimizing queries with expensive predicates](./expensive-predicate-ordering.md) | partially-solved | Ordering and placing selective but costly predicates jointly with joins. |
| [Cross-engine and polystore query optimization](./polystore-optimization.md) | open | Cost-based planning across heterogeneous engines with incompatible cost models. |
| [Optimizing AQP and bounded-error plans](./approximate-plan-optimization.md) | open | Selecting plans that meet accuracy targets under sampling and sketching operators. |
| [Optimizing under integrity constraints and semantics](./semantic-query-optimization.md) | partially-solved | Using keys, FDs, and check constraints to prune and rewrite plans soundly. |
| [Reproducible benchmarking of optimizer quality](./optimizer-benchmarking.md) | empirically-open | Methodology to compare optimizers fairly and isolate planning from estimation errors. |
| [Explainability and debuggability of plan choices](./plan-explainability.md) | open | Producing faithful, actionable explanations of why an optimizer chose a given plan. |

---
*Back to [TAXONOMY.md](../../TAXONOMY.md).*
