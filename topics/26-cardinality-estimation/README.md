# Cardinality Estimation & Statistics

Cardinality estimation (CE) is the task of predicting the size of intermediate and final query results so a query optimizer can choose good plans. The field spans selectivity estimation for single and multiple predicates, capturing multi-attribute and join-induced correlations, compact synopses (histograms, sketches, samples), learned and information-theoretic estimators, and the question of how estimation error compounds through a plan. It sits at the intersection of deep theory (worst-case bounds, information theory, complexity of consistency) and hard systems engineering (drift, maintenance cost, robustness, and integration into real optimizers).

| Problem | Status | Scope |
|---|---|---|
| [Tight Bounds for Conjunctive Query Cardinality](./agm-bound-tightness.md) | partially-solved | How tight are AGM/polymatroid bounds for real cardinalities and which statistics close the gap. |
| [Multi-Attribute Correlation Without Independence](./multi-attribute-correlation.md) | open | Compactly modeling joint distributions over many correlated attributes for selectivity. |
| [Join-Crossing Correlation Estimation](./join-crossing-correlation.md) | open | Estimating selectivity when predicate correlations span the join graph, not just one table. |
| [Error Propagation Through Query Plans](./error-propagation-plans.md) | open | Characterizing and bounding how per-operator estimation errors compound across a plan tree. |
| [Worst-Case-Optimal Bounds with Degree Constraints](./degree-constrained-bounds.md) | partially-solved | Cardinality bounds from functional dependencies and degree/frequency constraints beyond AGM. |
| [Sketches for Join Cardinality](./sketches-for-join-cardinality.md) | partially-solved | Mergeable sketches that estimate multi-way join sizes with provable error. |
| [Distinct-Value (NDV) Estimation Across Joins](./ndv-estimation-joins.md) | open | Estimating number of distinct values in join outputs and grouped aggregates. |
| [Learned Estimator Generalization & Drift](./learned-estimator-drift.md) | empirically-open | Why learned CE models degrade off-distribution and how to detect/bound the failure. |
| [Confidence Intervals for Cardinality Estimates](./cardinality-confidence-intervals.md) | open | Producing calibrated, query-specific uncertainty intervals usable by an optimizer. |
| [Robust Optimization Under Estimation Uncertainty](./robust-plans-under-uncertainty.md) | partially-solved | Choosing plans that are good across the plausible range of true cardinalities. |
| [Sample-Based Estimation for Selective Joins](./sampling-selective-joins.md) | partially-solved | Avoiding empty samples and high variance when joins or predicates are highly selective. |
| [Statistics for String & Pattern Predicates](./string-predicate-selectivity.md) | open | Selectivity of LIKE, regex, prefix, and substring predicates over text columns. |
| [Range-Predicate Selectivity in High Dimensions](./multidim-range-selectivity.md) | open | Compact synopses for multidimensional range selectivity without exponential blowup. |
| [Cardinality Estimation for Cyclic Joins](./cyclic-join-estimation.md) | open | Estimating output size of cyclic join queries where tree-based assumptions fail. |
| [Self-Tuning / Feedback-Driven Statistics](./feedback-driven-statistics.md) | partially-solved | Correcting estimates and synopses from observed execution cardinalities. |
| [Statistics Maintenance Under Updates](./incremental-statistics-maintenance.md) | partially-solved | Keeping synopses accurate and cheap under high-velocity inserts/updates/deletes. |
| [Subset/Superset Consistency of Estimates](./estimate-consistency-monotonicity.md) | open | Enforcing logical monotonicity and additivity across related subquery estimates. |
| [Negative & Anti-Join Selectivity](./anti-join-selectivity.md) | open | Estimating cardinality of NOT EXISTS, anti-joins, and set-difference operations. |
| [Group-By / Aggregation Result Cardinality](./groupby-result-cardinality.md) | open | Predicting the number of output groups under correlated grouping keys and filters. |
| [User-Defined Function Selectivity](./udf-selectivity-estimation.md) | open | Estimating selectivity of opaque UDF and black-box predicates. |
| [Information-Theoretic Limits of CE Synopses](./synopsis-information-limits.md) | partially-solved | Space lower bounds for any synopsis achieving a target estimation error. |
| [Correlated Predicates Across Subqueries](./correlated-subquery-estimation.md) | open | Estimating selectivity of correlated and nested subquery predicates. |
| [Skew- and Outlier-Robust Histograms](./skew-robust-histograms.md) | partially-solved | Histograms that bound error under heavy-tailed and clustered data distributions. |
| [Cardinality Estimation for Recursive / Graph Queries](./recursive-query-estimation.md) | open | Estimating result sizes for transitive closure, path, and recursive CTE queries. |
| [Worst-Case Error Guarantees for Learned CE](./learned-ce-error-guarantees.md) | open | Provable accuracy or robustness certificates for ML-based estimators. |
| [Query-Driven vs Data-Driven Estimator Synthesis](./query-vs-data-driven-models.md) | empirically-open | When to learn from the workload vs the data, and how to combine both. |
| [End-to-End Plan-Cost Sensitivity to CE Error](./plan-cost-sensitivity.md) | empirically-open | Identifying which estimation errors actually change the chosen plan and matter. |
| [Cardinality Estimation Benchmarks & Metrics](./ce-benchmarks-and-metrics.md) | empirically-open | Defining workloads and error metrics that predict downstream optimization quality. |
| [Cross-Engine Transfer of Statistics](./cross-engine-statistics-transfer.md) | open | Reusing/transferring statistics and learned models across schemas and engines. |
| [Online / Adaptive Re-Estimation During Execution](./adaptive-mid-query-estimation.md) | partially-solved | Refining cardinalities mid-query and re-optimizing from runtime feedback. |

---
[Back to taxonomy](../../TAXONOMY.md)
