# Schema Design & Normalization

The engineering and theory of turning a domain into a good relational (or post-relational)
schema: choosing and deciding normal forms (3NF/BCNF/4NF/5NF/DKNF), discovering the
dependencies that justify those decisions from data, evolving and migrating schemas as
applications change, and the physical-design tradeoffs (denormalization, partitioning,
materialization) that trade redundancy for performance. This topic sits between the pure
dependency theory of relational foundations and the systems reality of running databases,
collecting open problems in decomposition complexity, scalable dependency profiling,
zero-downtime migration, and automated/learned physical design at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT.

| Problem | Status | Scope |
|---|---|---|
| [Tractable Synthesis of Dependency-Preserving BCNF](./bcnf-dependency-preserving-synthesis.md) | open | Decide when a relation admits a lossless, dependency-preserving BCNF decomposition and synthesize one efficiently. |
| [Approximate-Optimal 3NF Decomposition](./minimal-3nf-decomposition.md) | partially-solved | Compute 3NF schemas minimizing redundancy/table count given that minimal-cover choices change the result. |
| [Information-Theoretic Normal-Form Decisioning](./information-theoretic-normal-forms.md) | partially-solved | Decide and rank schema designs by an information-theoretic redundancy measure rather than syntactic normal forms. |
| [Exact Functional-Dependency Discovery at Scale](./scalable-fd-discovery.md) | partially-solved | Discover all minimal FDs from large wide relations within practical time/space budgets. |
| [Robust Approximate & Conditional FD Discovery](./approximate-conditional-fd-discovery.md) | partially-solved | Mine approximate/conditional FDs that are statistically meaningful and noise-robust from dirty real data. |
| [Multivalued & Join Dependency Discovery](./mvd-jd-discovery.md) | open | Efficiently discover MVDs/JDs from data to justify 4NF/5NF decompositions without enumerating all decompositions. |
| [Inclusion Dependency & Foreign-Key Discovery](./inclusion-dependency-discovery.md) | partially-solved | Detect n-ary inclusion dependencies and true foreign keys (vs. coincidental overlaps) over many tables. |
| [Denormalization Selection Under Mixed Workloads](./denormalization-workload-aware.md) | open | Choose which normalized relations to merge/pre-join to optimize a workload while bounding update/anomaly cost. |
| [Provably Correct Online Schema Migration](./online-schema-migration-correctness.md) | partially-solved | Perform zero-downtime, lock-light schema changes on live tables with formal correctness and rollback guarantees. |
| [Schema Evolution Operator Completeness](./schema-evolution-operators.md) | partially-solved | Define a complete, composable algebra of evolution operators with co-evolving data and query rewrites. |
| [Backward/Forward Schema Compatibility Verification](./schema-compatibility-verification.md) | open | Statically verify that a schema change keeps existing and future application code and data compatible. |
| [Schema Inference for Semi-Structured Data](./schema-inference-semistructured.md) | partially-solved | Infer compact, useful relational/document schemas from heterogeneous JSON/log collections. |
| [Optimal Normalize-vs-JSON Hybrid Layout](./relational-json-hybrid-design.md) | empirically-open | Decide which attributes to keep relational vs. nest as JSON/document columns for a given workload. |
| [Cost-Optimal Vertical Partitioning](./vertical-partitioning-optimality.md) | partially-solved | Compute workload-optimal attribute-to-partition assignment with realistic cost models at scale. |
| [Automated Horizontal Partitioning & Sharding Design](./horizontal-partitioning-design.md) | open | Pick partition keys and boundaries that balance load and minimize cross-partition joins/distributed transactions. |
| [Materialized View & Index Co-Selection](./materialized-view-index-codesign.md) | partially-solved | Jointly select views, indexes, and partitions under storage budgets with interaction-aware cost models. |
| [Learned/ML-Driven Physical Schema Design](./learned-physical-design.md) | empirically-open | Use learned cost models and RL to design physical schemas with guarantees against catastrophic regressions. |
| [Self-Driving Continuous Schema Tuning](./self-driving-schema-tuning.md) | empirically-open | Continuously adapt physical schema to drifting workloads online without disruptive reorganizations. |
| [Temporal & Bitemporal Normal Forms](./temporal-normal-forms.md) | open | Define and synthesize redundancy-free normal forms for temporal/bitemporal relations and their dependencies. |
| [Normalization Under Probabilistic/Uncertain Data](./probabilistic-schema-normalization.md) | open | Develop normal-form theory and decomposition when dependencies hold only probabilistically. |
| [Denial-Constraint Discovery & Schema Design](./denial-constraint-discovery.md) | partially-solved | Discover denial constraints and incorporate them into schema design beyond classical FDs. |
| [Numeric & Order/Differential Dependency Design](./order-numeric-dependency-design.md) | open | Discover and exploit order/numeric/differential dependencies for schema and physical design. |
| [Embedding Business Rules as Schema Constraints](./business-rules-to-constraints.md) | open | Translate informal business rules into enforceable, non-redundant schema-level constraints automatically. |
| [Schema Design for Graph & Property-Graph Stores](./graph-schema-design.md) | empirically-open | Decide node/edge/property factoring and normalization tradeoffs for property-graph and RDF schemas. |
| [Polystore & Multi-Engine Schema Decomposition](./polystore-schema-decomposition.md) | open | Decompose a logical schema across heterogeneous engines (relational/KV/doc/graph) optimally for a workload. |
| [Cross-Schema Constraint Reconciliation in Integration](./constraint-reconciliation-integration.md) | partially-solved | Reconcile and propagate keys/FDs/normal forms when merging or mapping independently designed schemas. |
| [Privacy/Access-Aware Schema Decomposition](./privacy-aware-decomposition.md) | open | Decompose schemas so that sensitive attribute combinations are separated for privacy/access-control goals. |
| [Redundancy & Anomaly Detection in Legacy Schemas](./legacy-redundancy-detection.md) | partially-solved | Detect normalization violations and update anomalies in large legacy schemas from schema+data jointly. |
| [Human-in-the-Loop Dependency Validation](./human-in-the-loop-dependency-validation.md) | empirically-open | Minimize expert effort to confirm which discovered dependencies are genuine vs. spurious for design use. |
| [Benchmarks & Ground Truth for Schema Design](./schema-design-benchmarks.md) | empirically-open | Build realistic benchmarks with ground-truth dependencies/designs to evaluate discovery and design tools. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
