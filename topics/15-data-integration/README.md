# Data Integration & Schema Mapping

Data integration unifies heterogeneous, autonomously designed data sources behind a
common interface, reconciling differences in schema, structure, semantics, and identity.
The field spans deep theory — the semantics of source-to-target dependencies (GAV/LAV/GLAV),
data exchange and certain-answer computation, the chase and its termination, and the
complexity of mapping management operators (composition, inversion, definability) — and
hard systems engineering: schema matching at web scale, entity resolution and blocking over
billions of records, incremental and privacy-preserving integration, and increasingly the
use of learned/LLM components. The problems below are the kind studied at
PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT and remain genuinely open, only partially solved, or
practically unsolved at scale.

| Problem | Status | Scope |
|---------|--------|-------|
| [Certain Answers Under Existential Rules](./certain-answers-existential-rules.md) | open | Tight data/combined-complexity boundaries for certain-answer evaluation of unions of CQs under decidable existential-rule (tuple-generating dependency) mappings. |
| [Chase Termination Decidability Gap](./chase-termination-decidability.md) | open | Closing the gap between known sufficient acyclicity conditions and the exact (semi-)decidability frontier of chase termination for arbitrary instances. |
| [Schema-Mapping Composition Closure](./schema-mapping-composition-closure.md) | partially-solved | Characterizing when the composition of GLAV mappings is expressible in a usable language and bounding its size blow-up. |
| [Schema-Mapping Inversion Semantics](./schema-mapping-inversion.md) | partially-solved | A unified, computable notion of inverse for GLAV mappings that recovers source data with provable information-loss guarantees. |
| [Optimal Core Computation for Data Exchange](./core-universal-solution-cost.md) | solved-but-impractical | Computing the core universal solution (the minimal target instance) efficiently for large instances and expressive mappings. |
| [Certain Answers for Aggregate Queries](./certain-answers-aggregation.md) | open | A coherent semantics and tractable evaluation for COUNT/SUM/AVG certain answers over incomplete exchanged data. |
| [Mapping Discovery From Data Examples](./mapping-discovery-from-examples.md) | partially-solved | Learning a correct GLAV schema mapping from a small set of source-target data examples with characterizability guarantees. |
| [Definability and Loss in LAV Rewriting](./lav-rewriting-definability.md) | partially-solved | Deciding when a target query is exactly answerable (lossless) under LAV views and synthesizing the maximally-contained rewriting. |
| [Probabilistic Schema Mappings Semantics](./probabilistic-schema-mappings.md) | open | Sound semantics and tractable certain/probable-answer computation when the source-to-target mapping itself is uncertain. |
| [Holistic Many-to-Many Schema Matching](./holistic-schema-matching.md) | empirically-open | Matching hundreds of heterogeneous schemas jointly with calibrated confidence rather than pairwise, at web scale. |
| [Schema Matching Quality Lower Bounds](./schema-matching-lower-bounds.md) | open | Information-theoretic limits on automatic schema matching accuracy given only instance and metadata signals. |
| [Blocking With Recall Guarantees at Scale](./blocking-recall-guarantees.md) | open | Blocking/filtering for entity resolution over billions of records with provable recall and sublinear candidate generation. |
| [Progressive Entity Resolution Scheduling](./progressive-entity-resolution.md) | partially-solved | Ordering ER comparisons to maximize resolved-pairs-per-unit-work under a budget with anytime quality bounds. |
| [Incremental Entity Resolution Maintenance](./incremental-entity-resolution.md) | partially-solved | Maintaining a consistent ER clustering under streaming inserts/updates/deletes without full recomputation. |
| [Correlation Clustering for ER at Scale](./correlation-clustering-er.md) | solved-but-impractical | Approximation algorithms for correlation-clustering-based ER that scale to billions of nodes with quality guarantees. |
| [Crowd/Human-in-the-Loop ER Optimization](./crowd-er-question-selection.md) | partially-solved | Choosing the minimum set of human verification questions to certify an ER result under transitivity constraints. |
| [Multi-Source Data Fusion Truth Discovery](./multi-source-truth-discovery.md) | empirically-open | Resolving conflicting values across many unreliable sources with principled, source-trust-aware accuracy guarantees. |
| [Mapping-Aware Consistency Repair](./mapping-aware-consistency.md) | open | Jointly repairing target constraint violations introduced by data exchange while preserving certain answers. |
| [Open-World Certain Answers Semantics](./open-world-certain-answers.md) | partially-solved | A well-behaved, tractable semantics for query answering that distinguishes open- vs closed-world target instances per mapping. |
| [Mapping Evolution Under Schema Change](./mapping-evolution-schema-change.md) | partially-solved | Automatically adapting existing schema mappings when source or target schemas evolve, with minimal-change guarantees. |
| [Nested/Hierarchical Data Exchange](./nested-data-exchange.md) | open | Certain answers and core computation for data exchange over nested/JSON/XML schemas with referential and order constraints. |
| [Entity Resolution Under Differential Privacy](./private-entity-resolution.md) | open | Linking records across parties with formal privacy guarantees while bounding linkage-accuracy loss. |
| [Learned Embedding ER Calibration](./learned-embedding-er-calibration.md) | empirically-open | Calibrated, threshold-free matching decisions from learned record embeddings with controllable precision-recall tradeoffs. |
| [LLM-Based Mapping Reliability](./llm-schema-mapping-reliability.md) | empirically-open | Making LLM-generated schema mappings verifiable, hallucination-bounded, and reproducible against formal mapping semantics. |
| [Source Selection Under Cost and Coverage](./source-selection-coverage.md) | partially-solved | Choosing which sources to integrate to maximize answer coverage/quality under acquisition and integration cost budgets. |
| [Mapping Repair From Constraint Violations](./mapping-repair-from-violations.md) | open | Minimally revising a schema mapping so the exchanged data satisfies target constraints and user feedback. |
| [GLAV Query Answering Complexity Census](./glav-query-answering-complexity.md) | partially-solved | A complete complexity classification of certain-answer evaluation across mapping language and query language combinations. |
| [Blocking Key Discovery Automation](./blocking-key-discovery.md) | empirically-open | Automatically synthesizing blocking schemes (keys/rules) that jointly optimize recall and reduction ratio from data. |
| [Schema Mapping Optimization and Minimality](./schema-mapping-minimization.md) | partially-solved | Deciding equivalence and computing minimal-size GLAV mappings under data-exchange and CQ-answering equivalence. |
| [Federated Query Certain Answers Online](./federated-certain-answers-online.md) | open | Returning certain answers (not just best-effort) over live federated sources under access-pattern and latency limits. |

---
*Back to [Taxonomy](../../TAXONOMY.md).*
