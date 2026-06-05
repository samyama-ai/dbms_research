# Approximate Query Processing

Approximate query processing (AQP) trades a bounded, quantified loss of accuracy for orders-of-magnitude
gains in latency, memory, and cost by answering queries over samples, sketches, histograms, and other
synopses rather than the full data. This topic spans the theory (sublinear-space lower bounds, unbiased
estimators, confidence-interval validity, the expressiveness of mergeable synopses) and the systems
(sample/sketch selection, online aggregation engines, interactive-latency dashboards, AQP over joins
and streams). The problems below are the hard, open, or empirically-unsettled questions that
PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT communities continue to study.

| Problem | Status | Scope |
|---|---|---|
| [Unbiased Sampling Over Joins](./sampling-over-joins.md) | partially-solved | Producing provably unbiased, low-variance samples of multi-way join results without materializing the join. |
| [Confidence Intervals for Complex Queries](./valid-confidence-intervals.md) | open | Computing statistically valid error bounds for nested, correlated, multi-aggregate AQP queries rather than single SUM/AVG. |
| [Optimal Stratified Sample Design](./stratified-sample-design.md) | open | Choosing strata and per-stratum allocation that minimize error across an unknown future query workload under a space budget. |
| [Sample Selection for Ad-Hoc Workloads](./sample-selection-adhoc.md) | open | Selecting which (offline) samples to materialize when the query and predicate distribution is unknown or drifting. |
| [Error Guarantees for Group-By Queries](./groupby-error-guarantees.md) | partially-solved | Bounding per-group error and missing-group probability for high-cardinality, skewed group-by aggregates over samples. |
| [Rare Subpopulation and Outlier Queries](./rare-subpopulation-queries.md) | open | Accurately answering aggregates over tiny, highly selective subpopulations that uniform samples systematically miss. |
| [Sketch Composability and Algebra](./sketch-algebra-composability.md) | partially-solved | A principled algebra for combining CM/HLL/AKMV/quantile sketches under union, intersection, difference, and joins. |
| [Mergeable Summaries Lower Bounds](./mergeable-summaries-bounds.md) | partially-solved | Tight space lower bounds for fully mergeable synopses supporting quantiles, heavy hitters, and distinct counts. |
| [Distinct-Count Sketches Beyond HLL](./distinct-count-sketch-frontier.md) | empirically-open | Cardinality sketches that improve HLL's accuracy/space frontier and support set operations and predicates. |
| [Set-Intersection Cardinality Estimation](./set-intersection-cardinality.md) | partially-solved | Estimating intersection/join-key overlap sizes from per-set sketches with provable relative-error bounds. |
| [Sketch Selection and Sizing](./sketch-selection-sizing.md) | open | Automatically choosing which sketch type and parameters to build per column/query under a memory and accuracy budget. |
| [Optimal Multidimensional Histograms](./multidim-histogram-optimality.md) | partially-solved | Constructing v-optimal multi-attribute histograms whose error is provably near-optimal for range and point queries. |
| [Histograms Under Attribute Correlation](./correlated-attribute-histograms.md) | open | Synopses that capture joint distributions and dependencies without exponential blow-up in dimensionality. |
| [Online Aggregation Convergence Rates](./online-aggregation-convergence.md) | partially-solved | Sampling/scan orders and estimators that provably tighten running confidence intervals as fast as possible. |
| [Ripple-Join and Online Join Estimation](./online-join-estimation.md) | partially-solved | Online-aggregation estimators for multi-way joins with valid running bounds and non-blocking, memory-bounded execution. |
| [Wander-Join and Random-Walk Sampling](./random-walk-join-sampling.md) | partially-solved | Index-assisted random-walk sampling of join paths with variance control and support for cyclic/many-way joins. |
| [Approximate Median and Quantile Queries](./approximate-quantiles.md) | partially-solved | Streaming/mergeable quantile structures with optimal space for relative- and rank-error guarantees. |
| [AQP for Nested and Window Queries](./aqp-nested-window-queries.md) | open | Error-bounded approximation of correlated subqueries, window functions, and analytic frames. |
| [Bias Correction for Predicate Pushdown](./predicate-pushdown-bias.md) | open | Correcting selection bias when highly selective predicates interact with non-uniform or stratified samples. |
| [Sample Maintenance Under Updates](./sample-maintenance-updates.md) | partially-solved | Keeping samples uniform/representative under inserts, updates, and deletes without full rescans. |
| [Approximate Top-K and Heavy Hitters](./approximate-topk-heavy-hitters.md) | partially-solved | Identifying top-k/heavy hitters with bounded false-positive/negative rates and rank error in one pass. |
| [Learned Synopses with Guarantees](./learned-synopses-guarantees.md) | empirically-open | Reconciling ML-based density/answer models (deep AQP) with the worst-case error guarantees of classical synopses. |
| [Error-Bounded AQP Under DP Noise](./aqp-differential-privacy.md) | open | Joint optimization of sampling/sketch error and differential-privacy noise so total error is minimized and bounded. |
| [AQP Cost-Accuracy Plan Optimization](./aqp-plan-optimization.md) | open | A query optimizer that chooses among samples/sketches/exact plans to meet an error SLO at minimum cost. |
| [Sublinear-Time Aggregation Lower Bounds](./sublinear-aggregation-bounds.md) | partially-solved | Characterizing which aggregates admit sublinear-time (1+epsilon)-approximation and at what query/sample complexity. |
| [Negative and Self-Join Sketch Estimation](./self-join-sketch-estimation.md) | open | Sketch-based estimation for self-joins, set difference, and queries with negation under provable error. |
| [Interactive Latency-Accuracy Scheduling](./interactive-latency-scheduling.md) | empirically-open | Scheduling progressive computation across many dashboard queries to meet sub-second latency with useful bounds. |
| [AQP Over Streaming and Sliding Windows](./streaming-window-aqp.md) | partially-solved | Time-decayed/sliding-window synopses giving fresh, error-bounded answers under bounded memory and high ingest. |
| [Verifiable and Trustworthy Approximations](./verifiable-aqp.md) | open | Letting users validate or certify that returned error bounds actually hold, including against adversarial data. |
| [Multi-Query Synopsis Sharing](./multi-query-synopsis-sharing.md) | open | Designing a shared set of samples/sketches that jointly minimizes error across an entire query workload under one budget. |

---
[← Back to taxonomy](../../TAXONOMY.md)
