# Provenance & Lineage

Data provenance records why, how, and where each query answer was derived, and the algebraic
theory of provenance semirings unifies these notions into a single annotation-propagation
framework that also captures probabilistic, security, trust, and cost interpretations. This topic
spans the theory (semiring expressiveness, the complexity of explanation and minimal-witness
problems, reverse data management and deletion propagation as constraint-satisfaction) and the
systems (capturing, compressing, storing, and querying provenance at scale inside real engines, on
streams, in ML/data-science pipelines, and across federated and differentially-private settings).
The problems below are the hard, open, or empirically-unsettled questions that the
PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT communities continue to study.

| Problem | Status | Scope |
|---|---|---|
| [Semiring Expressiveness Hierarchy](./semiring-expressiveness-hierarchy.md) | open | Characterizing exactly which provenance questions each commutative semiring (and its homomorphisms) can and cannot answer relative to the free provenance polynomial semiring. |
| [Provenance for Full Relational Algebra](./provenance-difference-negation.md) | partially-solved | Extending semiring provenance soundly to difference, negation, and aggregation where the monotone semiring model breaks down. |
| [Aggregate-Query Provenance Semantics](./aggregate-query-provenance.md) | partially-solved | A compositional algebraic model of provenance for queries mixing grouping, aggregation, and relational operators that supports incremental recomputation. |
| [Recursive-Datalog Provenance Convergence](./recursive-datalog-provenance.md) | partially-solved | Well-defined, finitely representable provenance for recursive Datalog over semirings where the naive fixpoint of polynomials may not converge. |
| [Provenance Polynomial Compression Bounds](./provenance-polynomial-compression.md) | open | Tight bounds on the smallest circuit/factorized representation of a query's provenance polynomial and when polynomial-size representations exist. |
| [Minimal Why-Provenance Complexity](./minimal-why-provenance-complexity.md) | partially-solved | The complexity of computing minimal witness bases and minimum-cardinality witnesses for an answer under conjunctive and richer queries. |
| [Where-Provenance Formal Characterization](./where-provenance-characterization.md) | open | An invariant, query-rewrite-stable definition of where-provenance (which input cells a value is copied from) and its decidable equivalence. |
| [Smallest-Explanation Query Answers](./smallest-explanation-query-answers.md) | open | Finding minimum-size human-readable explanations (subsets of tuples/rules) that justify a query answer under a fixed explanation model. |
| [Counterfactual Explanation Complexity](./counterfactual-explanation-complexity.md) | partially-solved | Complexity and approximability of responsibility/causality (counterfactual cause) for a tuple's contribution to a query answer. |
| [Deletion Propagation Approximability](./deletion-propagation-approximability.md) | partially-solved | Tight approximation thresholds for side-effect-minimal source deletions that remove a target answer (view-side-effect and source-side-effect variants). |
| [Why-Not Provenance Minimality](./why-not-provenance-minimality.md) | open | Computing minimal-cost source/query modifications that make a missing tuple appear, with provable optimality and tractable subclasses. |
| [Reverse Data Management Tractability](./reverse-data-management-tractability.md) | open | A dichotomy mapping how-to / what-if update problems to PTIME vs. intractable, generalizing deletion propagation to arbitrary objectives. |
| [Provenance-Aware View Update](./provenance-aware-view-update.md) | partially-solved | Using fine-grained provenance to determine unambiguous, side-effect-free translations of view updates back to base relations. |
| [Provenance Storage Overhead Bounds](./provenance-storage-overhead.md) | open | Worst-case and instance-optimal bounds on the space needed to store recomputation-complete provenance versus deduplicated/factorized encodings. |
| [Lazy vs. Eager Provenance Capture](./lazy-vs-eager-capture.md) | empirically-open | When on-demand provenance recomputation beats eager annotation propagation across workloads, and how to choose adaptively. |
| [Low-Overhead Runtime Provenance Capture](./low-overhead-runtime-capture.md) | empirically-open | Instrumenting production query engines to capture row/cell lineage with bounded, predictable latency and throughput overhead. |
| [Streaming and Windowed Provenance](./streaming-windowed-provenance.md) | open | Bounded-memory provenance for continuous queries over windows where naive lineage grows without bound as the stream advances. |
| [Provenance for Dataflow & ML Pipelines](./dataflow-ml-pipeline-provenance.md) | partially-solved | Capturing fine-grained, queryable lineage across UDFs, dataframes, and ML operators that are opaque to relational provenance. |
| [Coarse-to-Fine Provenance Refinement](./coarse-to-fine-provenance.md) | open | Starting from cheap coarse lineage and refining to record/cell granularity only where queries demand it, with cost guarantees. |
| [Provenance Compression and Summarization](./provenance-compression-summarization.md) | partially-solved | Lossy and lossless summarization of large provenance graphs that preserves answerability of a stated class of provenance queries. |
| [Provenance Query Language Expressiveness](./provenance-query-language.md) | open | A declarative language and algebra for querying provenance graphs with characterized expressiveness and evaluation complexity. |
| [Provenance Under Schema Evolution](./provenance-schema-evolution.md) | open | Maintaining and reinterpreting lineage when schemas, queries, and transformations change over time. |
| [Cross-System Federated Provenance](./federated-provenance-integration.md) | open | Reconciling and composing provenance captured by heterogeneous engines into a single coherent, queryable lineage. |
| [Probabilistic-DB Provenance Hardness](./probabilistic-db-provenance.md) | partially-solved | The exact-vs-approximate computation boundary for query reliability via provenance-formula model counting (the dichotomy and its lifting). |
| [Provenance for Differential Privacy](./provenance-differential-privacy.md) | open | Releasing useful lineage/explanations of query answers without violating differential-privacy guarantees on the underlying data. |
| [Provenance-Based Access Control](./provenance-access-control.md) | open | Enforcing and verifying fine-grained, provenance-derived access and disclosure policies with sound information-flow guarantees. |
| [Tamper-Evident Verifiable Provenance](./verifiable-tamper-evident-provenance.md) | partially-solved | Cryptographically authenticated lineage that lets a verifier check that recorded provenance was neither forged nor truncated. |
| [Incremental Provenance Maintenance](./incremental-provenance-maintenance.md) | open | Updating stored provenance under base-data changes without full recomputation, with bounded incremental cost. |
| [Provenance-Guided Data Repair](./provenance-guided-repair.md) | open | Using lineage and causality to localize and minimally repair the source errors responsible for incorrect or inconsistent answers. |
| [How-Provenance for Graph/Path Queries](./graph-path-query-provenance.md) | open | Finitely representable, semiring-correct provenance for regular-path and recursive graph queries where path sets can be infinite. |
| [Provenance-Driven Query Optimization](./provenance-driven-optimization.md) | empirically-open | Exploiting provenance/annotation structure to prune, memoize, or rewrite queries and to optimize provenance-capture plans themselves. |

---
[← Back to taxonomy](../../TAXONOMY.md)
