# Data Cleaning & Quality

Real-world data is dirty: it violates declared constraints, contains duplicate and
conflicting records, carries missing or erroneous values, and fuses sources that
disagree. This topic collects the hard and open problems of making such data usable —
constraint-based repair, error detection, deduplication/entity resolution, missing-value
imputation, data fusion and conflict resolution. The questions span theory (complexity of
minimum-cost repair, expressiveness of repair semantics, learnability of constraints) and
systems (scaling detection and matching to billions of records, human-in-the-loop and
learned cleaning, end-to-end pipelines whose quality can be certified).

| Problem | Status | Scope |
|---|---|---|
| [Minimum-Cost Repair Under Denial Constraints](./min-cost-repair-denial-constraints.md) | open | Compute or approximate a minimum-cost repair for a database violating denial constraints. |
| [Consistent Query Answering Complexity Frontier](./cqa-complexity-frontier.md) | partially-solved | Map the exact tractability frontier of consistent query answering across constraint and query classes. |
| [Optimal Repair Semantics Selection](./repair-semantics-selection.md) | open | Decide which repair semantics (subset/superset/update/cardinality) a given application should use and how they relate. |
| [Update-Based Repairs with Value Imputation](./update-repairs-value-choice.md) | open | Compute optimal cell-value updates that restore consistency while choosing plausible replacement values. |
| [Holistic Multi-Constraint Repair](./holistic-multi-constraint-repair.md) | partially-solved | Repair errors that violate interacting heterogeneous constraints jointly rather than constraint-by-constraint. |
| [Scalable Conditional FD Discovery](./conditional-fd-discovery.md) | partially-solved | Discover conditional functional dependencies from data at scale with statistical reliability. |
| [Denial-Constraint Discovery at Scale](./denial-constraint-discovery.md) | partially-solved | Mine approximate denial constraints from large dirty relations efficiently and with quality guarantees. |
| [Error Detection Without Ground Truth](./error-detection-no-ground-truth.md) | empirically-open | Detect heterogeneous errors with high precision/recall when no labeled clean data is available. |
| [Blocking with Recall Guarantees](./blocking-recall-guarantees.md) | partially-solved | Design blocking/indexing for entity resolution with provable recall and subquadratic cost. |
| [Entity Resolution at Billion-Record Scale](./entity-resolution-billion-scale.md) | empirically-open | Resolve entities across billions of records under tight latency and memory budgets. |
| [Transitive Closure in Matching](./matching-transitivity-clustering.md) | partially-solved | Reconcile pairwise match decisions into globally consistent entity clusters. |
| [Incremental Entity Resolution](./incremental-entity-resolution.md) | open | Maintain entity-resolution results incrementally as records and rules change. |
| [Crowd-Powered Cleaning Cost Optimization](./crowd-cleaning-cost.md) | partially-solved | Minimize human/crowd cost while guaranteeing cleaning quality in human-in-the-loop pipelines. |
| [Truth Discovery From Conflicting Sources](./truth-discovery-conflicts.md) | partially-solved | Infer true values and source reliability jointly from conflicting multi-source data. |
| [Copy Detection in Data Fusion](./copy-detection-fusion.md) | partially-solved | Detect source-to-source copying to avoid double-counting evidence in fusion. |
| [Imputation Under Constraints](./constraint-aware-imputation.md) | open | Impute missing values so results respect integrity constraints and downstream queries. |
| [Statistically Valid Imputation for Analytics](./imputation-statistical-validity.md) | empirically-open | Impute values that preserve joint distributions and yield unbiased downstream estimates. |
| [Repair Quality Certification](./repair-quality-certification.md) | open | Certify that a produced repair is close to the unknown ground truth with formal guarantees. |
| [Learned vs Rule-Based Cleaning Unification](./learned-rule-cleaning-unification.md) | empirically-open | Unify statistical/ML and logical/rule-based cleaning into one principled framework. |
| [Constraint Repair Itself](./constraint-vs-data-repair.md) | partially-solved | Decide when to repair the constraints rather than the data, and trade the two off optimally. |
| [Approximate-Duplicate Similarity Learning](./duplicate-similarity-learning.md) | empirically-open | Learn record-similarity/matching functions that generalize across domains with few labels. |
| [Privacy-Preserving Record Linkage](./privacy-preserving-linkage.md) | partially-solved | Link records across parties without revealing non-matching identities, at scale and accuracy. |
| [Streaming Error Detection and Repair](./streaming-cleaning.md) | open | Detect and repair errors over unbounded streams under bounded memory and latency. |
| [Explainable Repairs](./explainable-repairs.md) | open | Produce human-interpretable explanations for why and how data was repaired. |
| [Cleaning-Aware Query Answering](./cleaning-aware-query-answering.md) | partially-solved | Answer queries directly over dirty data without materializing a full clean instance. |
| [End-to-End Pipeline Quality Propagation](./pipeline-quality-propagation.md) | open | Quantify and propagate data-quality/error metrics through multi-stage cleaning pipelines. |
| [Active Learning for Constraint Acquisition](./active-constraint-acquisition.md) | partially-solved | Acquire cleaning constraints interactively with minimal user effort and convergence guarantees. |
| [Repairing Knowledge Graphs and Linked Data](./knowledge-graph-repair.md) | empirically-open | Detect and repair errors in large, heterogeneous, schema-flexible knowledge graphs. |
| [Fairness-Aware Data Cleaning](./fairness-aware-cleaning.md) | empirically-open | Clean data without introducing or amplifying bias against protected groups. |
| [Benchmarking and Reproducible Evaluation](./cleaning-benchmarking.md) | empirically-open | Build realistic error benchmarks and metrics that predict real deployment quality. |

---

[← Back to Taxonomy](../../TAXONOMY.md)
