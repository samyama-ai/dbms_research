# Learned Database Components

Learned database components replace hand-engineered structures and policies — index lookups,
cardinality estimators, query optimizers, and configuration knobs — with models fitted to data and
workload, trading worst-case guarantees for empirical speed and, sometimes, provable instance
optimality. This topic spans the theory (when learning beats classical structures, what bounds and
expressiveness limits apply, what instance-optimality means formally) and the systems (training and
serving cost, drift under updates, robustness, integration into real engines, and safe deployment).
The problems below are the hard, open, or empirically-unsettled questions that
PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT communities continue to study.

| Problem | Status | Scope |
|---|---|---|
| [Learned Index Lower Bounds](./learned-index-lower-bounds.md) | partially-solved | Establishing cell-probe / information-theoretic limits on how much a learned index can beat a comparison-based or implicit static index. |
| [Learned Indexes Under Updates](./learned-index-updates.md) | open | Maintaining a learned index's accuracy and lookup bound under insertions, deletions, and distribution shift without full retraining. |
| [Distribution-Free Learned Index Guarantees](./distribution-free-index-guarantees.md) | open | Worst-case lookup-time bounds for learned indexes that hold for any key distribution, not just smooth or piecewise-linear ones. |
| [Optimal Model Complexity vs. Lookup Cost](./model-complexity-lookup-tradeoff.md) | partially-solved | Choosing model size/segmentation to minimize the combined model-evaluation plus last-mile-search cost for a given key set. |
| [Multidimensional Learned Indexes](./multidimensional-learned-indexes.md) | empirically-open | Learned structures that beat R-trees / space-filling curves for range and kNN queries with provable skipping bounds. |
| [Learned String / Variable-Length Key Indexes](./learned-string-key-indexes.md) | open | Learned indexing over non-numeric, variable-length, high-entropy keys where monotone model fitting breaks down. |
| [PAC Bounds for Learned Cardinality Estimation](./learned-ce-pac-bounds.md) | open | Sample-complexity and generalization bounds for learned selectivity estimators over unseen predicates and joins. |
| [Worst-Case Error Guarantees for Learned CE](./learned-ce-error-guarantees.md) | open | Learned cardinality estimators that provide bounded q-error in the worst case rather than only good average accuracy. |
| [Learned CE Under Joins and Correlation](./learned-ce-joins-correlation.md) | empirically-open | Models that capture multi-table join-key correlation and conditional dependence without exponential blow-up. |
| [Drift Detection and Retraining Triggers](./ce-drift-retraining-triggers.md) | open | Detecting when a learned estimator/index has degraded enough to warrant retraining, with formal staleness bounds. |
| [Instance-Optimal Indexing Formalization](./instance-optimal-indexing.md) | partially-solved | A robust definition and achievability theory of instance optimality for index/access-method selection over a workload. |
| [Instance-Optimal Query Plans](./instance-optimal-query-plans.md) | open | Plan-selection procedures provably competitive with the best plan for the actual data instance, not the estimated one. |
| [Learned Query Optimizer Convergence](./learned-optimizer-convergence.md) | empirically-open | Whether RL/learned plan-search optimizers converge to good plans and how many queries of exploration that costs. |
| [Safe Exploration in Learned Optimizers](./safe-exploration-optimizers.md) | open | Bounding the regret/latency damage of an online learned optimizer's bad plan choices during exploration. |
| [Learned Plan Cost Model Calibration](./learned-cost-model-calibration.md) | partially-solved | Cost models learned from execution feedback that stay calibrated across hardware, data growth, and concurrency. |
| [Generalization to Unseen Queries](./optimizer-unseen-query-generalization.md) | open | Learned optimizers that generalize to query shapes, predicates, and schemas absent from training. |
| [Plan Featurization Expressiveness](./plan-featurization-expressiveness.md) | open | What classes of plan/data interactions a given query/plan encoding (tree-LSTM, GNN, set) can and cannot represent. |
| [Robustness to Adversarial / Tail Workloads](./learned-component-robustness.md) | open | Worst-case behavior and graceful fallback of learned components on out-of-distribution and adversarial inputs. |
| [Guaranteed Fallback and Hybrid Designs](./hybrid-fallback-guarantees.md) | partially-solved | Architectures that combine a learned fast path with a classical structure so worst-case bounds are preserved. |
| [Sample Complexity of Knob Tuning](./knob-tuning-sample-complexity.md) | open | How many workload executions are needed to find a near-optimal configuration in a high-dimensional knob space. |
| [Transferable Knob-Tuning Models](./transferable-knob-tuning.md) | empirically-open | ML tuners whose learned policies transfer across workloads, hardware, and DBMS versions without retuning from scratch. |
| [Safe Online Configuration Tuning](./safe-online-knob-tuning.md) | open | Online knob tuners with bounded performance-regression risk and rollback guarantees on production systems. |
| [Black-Box vs. White-Box Tuning Limits](./blackbox-whitebox-tuning-limits.md) | open | Whether structural knowledge of the engine provably reduces the search/sample cost of configuration tuning. |
| [Joint Multi-Component Co-Learning](./multi-component-co-learning.md) | open | Jointly learning index, CE, optimizer, and knobs whose decisions interact, avoiding feedback-loop instability. |
| [Training and Serving Cost Amortization](./training-serving-cost-amortization.md) | empirically-open | When the offline training plus inference overhead of a learned component is actually repaid by query speedups. |
| [Inference Latency Inside the Critical Path](./inference-latency-critical-path.md) | open | Keeping model inference cheap enough to sit on the per-tuple / per-query hot path without erasing its benefit. |
| [Explainability and Debuggability of Learned Decisions](./learned-decision-explainability.md) | open | Explaining, auditing, and debugging why a learned optimizer/index/tuner made a specific costly choice. |
| [Benchmarks and Reproducibility for Learned DB](./learned-db-benchmarking.md) | empirically-open | Workloads, metrics, and protocols that fairly compare learned components against strong classical baselines. |
| [Theory of When Learning Helps](./when-learning-helps-theory.md) | open | Characterizing the data/workload regularities under which a learned component can provably beat the best classical one. |
| [Lifelong / Continual Learning for DB Components](./continual-learning-db-components.md) | open | Components that adapt continually to evolving data and workloads without catastrophic forgetting of past regimes. |

---
[← Back to taxonomy](../../TAXONOMY.md)
