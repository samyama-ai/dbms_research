# Temporal Databases

Temporal databases manage data whose values change over time, tracking *when* facts
hold in reality (valid time) and *when* they were recorded (transaction time), often
both at once (bitemporal). The field spans formal data models and query-language
semantics, complexity and expressiveness results for temporal operators (joins,
aggregation, coalescing), and the systems engineering of versioning, time-travel,
period indexing, and storage for ever-growing histories. Despite SQL:2011 standardizing
period predicates and system-versioned tables, deep gaps remain between elegant theory
and what engines can execute efficiently at scale.

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal Temporal Coalescing Algorithms](./temporal-coalescing-optimal.md) | partially-solved | Tight bounds for merging value-equivalent adjacent/overlapping periods into a canonical minimal representation. |
| [Bitemporal Conceptual Data Model Foundations](./bitemporal-model-foundations.md) | open | A fully agreed-upon, closed algebra and semantics for the two-dimensional valid/transaction-time space. |
| [Worst-Case-Optimal Temporal Joins](./temporal-join-wcoj.md) | open | Join algorithms over interval-overlap predicates meeting AGM-style worst-case-optimal output bounds. |
| [Period Indexing for Overlap Queries](./period-index-overlap.md) | partially-solved | Index structures with provably good bounds for stabbing and overlap queries over large interval collections. |
| [Temporal Aggregation Complexity](./temporal-aggregation-complexity.md) | partially-solved | Lower/upper bounds for instantaneous, moving-window, and span aggregation over time-varying relations. |
| [Time-Travel Query Cost Models](./time-travel-cost-models.md) | empirically-open | Accurate cost/cardinality models for AS-OF and version-range queries over versioned storage. |
| [Temporal Functional Dependency Theory](./temporal-fd-theory.md) | open | Sound/complete axiomatization and normalization for dependencies that hold over time. |
| [Bitemporal Normal Forms](./bitemporal-normal-forms.md) | open | Normal forms and decomposition theory eliminating temporal redundancy without losing history. |
| [Allen-Relation Query Optimization](./allen-relation-optimization.md) | open | Algebraic rewriting and selectivity for the 13 Allen interval relations in query plans. |
| [Temporal Selectivity Estimation](./temporal-selectivity-estimation.md) | empirically-open | Cardinality estimation for interval-overlap and as-of predicates under correlated time skew. |
| [Versioned Storage Space-Time Tradeoff](./versioned-storage-tradeoff.md) | partially-solved | Optimal delta/snapshot mixing for reconstructing arbitrary historical versions. |
| [Temporal Snapshot Reducibility Limits](./snapshot-reducibility-limits.md) | open | Which temporal queries are/aren't expressible as snapshot-by-snapshot non-temporal evaluation. |
| [Now-Relative & Indeterminate Time](./now-relative-indeterminate.md) | open | Semantics and indexing for variables like NOW and probabilistic/indeterminate timestamps. |
| [Temporal Query Language Expressiveness](./temporal-language-expressiveness.md) | open | Expressive-power hierarchy of temporal SQL, TSQL2, and first-order temporal logic. |
| [Incremental Maintenance of Temporal Views](./temporal-view-maintenance.md) | partially-solved | Efficient incremental update of materialized views over bitemporal base tables. |
| [Temporal Coalescing in Distributed Engines](./distributed-coalescing.md) | empirically-open | Coalescing partitioned interval data with minimal shuffle and bounded skew. |
| [Long-Lived Interval Index Maintenance](./interval-index-maintenance.md) | partially-solved | Update-efficient interval indexes for high-velocity insert/expire workloads. |
| [Temporal Multidimensional Histograms](./temporal-histograms.md) | empirically-open | Histograms capturing joint distribution of period endpoints for accurate estimation. |
| [Point-vs-Interval Semantics Reconciliation](./point-interval-semantics.md) | open | Unifying point-based and interval-based temporal data models without anomalies. |
| [Temporal Outer & Anti Joins](./temporal-outer-anti-joins.md) | partially-solved | Correct, efficient interval-aware semantics for outer, anti, and difference joins. |
| [Versioning Garbage Collection Policy](./versioning-gc-policy.md) | empirically-open | Provably safe and cost-effective reclamation of obsolete versions under time-travel SLAs. |
| [Temporal Integrity Constraint Checking](./temporal-constraint-checking.md) | open | Efficient enforcement of sequenced primary keys and referential integrity over periods. |
| [Bitemporal Indexing in Two Dimensions](./bitemporal-2d-indexing.md) | partially-solved | Index structures supporting combined valid-time and transaction-time range queries. |
| [Temporal Window Join Streaming Bounds](./temporal-window-join-streaming.md) | open | Space/competitive lower bounds for interval joins under out-of-order streaming arrival. |
| [Schema Evolution over Temporal Data](./temporal-schema-evolution.md) | open | Querying consistently across schema versions that themselves change over time. |
| [Temporal Provenance & Lineage](./temporal-provenance.md) | open | Provenance semantics tracking how temporal facts derive across time-varying inputs. |
| [Probabilistic Temporal Databases](./probabilistic-temporal-db.md) | open | Tractable query evaluation when both values and time intervals are uncertain. |
| [Compression of Bitemporal Histories](./bitemporal-compression.md) | empirically-open | Encoding schemes exploiting temporal locality while preserving random version access. |
| [Temporal Aggregation Sketches](./temporal-aggregation-sketches.md) | partially-solved | Mergeable summaries answering approximate aggregates over arbitrary time ranges. |
| [Sequenced Semantics Query Rewriting](./sequenced-semantics-rewriting.md) | partially-solved | Automatic, correct rewriting of non-temporal queries into sequenced temporal form. |
| [Temporal Data Model Concurrency](./temporal-concurrency-control.md) | open | Isolation and concurrency control specialized to append-mostly versioned histories. |

---
*Back to [TAXONOMY.md](../../TAXONOMY.md).*
