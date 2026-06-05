# Graph Databases & Graph Query Processing

Graph databases manage data whose primary structure is connectivity: property graphs and
RDF, navigated by pattern matching, paths, and analytics. This topic spans the **theory**
frontier — the complexity and expressiveness of subgraph isomorphism, regular and conjunctive
path queries, worst-case-optimal graph joins, and the descriptive power of emerging standards
like GQL/SQL-PGQ — and the **systems** frontier — matching engines, RPQ evaluation, graph
storage and partitioning, incremental maintenance, and large-scale analytics runtimes. The
unifying question is how to evaluate richly structured, recursive, navigational queries over
skewed billion-edge graphs while approaching information-theoretic limits and staying robust,
distributed, and dynamic.

| Problem | Status | Scope |
|---------|--------|-------|
| [Practical worst-case-optimal subgraph matching](./wco-subgraph-matching.md) | partially-solved | Closing the gap between WCOJ theory and engines that beat join-at-a-time matching on real skewed graphs. |
| [Optimal subgraph isomorphism matching order](./matching-order-selection.md) | open | Choosing a vertex/edge matching order that provably minimizes intermediate enumeration on a given graph and pattern. |
| [Cardinality estimation for subgraph patterns](./subgraph-cardinality-estimation.md) | open | Estimating the number of embeddings of a pattern under heavy degree correlation and label skew with error bounds. |
| [Tight bounds for regular path query evaluation](./rpq-complexity-bounds.md) | partially-solved | Fine-grained upper/lower bounds for evaluating and enumerating RPQ answers beyond the BFS/product-automaton baseline. |
| [Conjunctive regular path query optimization](./crpq-optimization.md) | open | Join ordering and decomposition for CRPQs/UC2RPQs that combines path navigation with worst-case-optimal joins. |
| [RPQ containment and equivalence decidability](./rpq-containment.md) | partially-solved | Practical decision procedures and tight complexity for containment of (C)RPQs and their unions with inverses. |
| [Enumerating paths with bag and trail semantics](./path-enumeration-semantics.md) | partially-solved | Polynomial-delay enumeration of shortest/arbitrary/trail paths reconciling GQL/SQL-PGQ semantics with #P-hardness of simple paths. |
| [Expressiveness and gaps in GQL/SQL-PGQ](./gql-expressiveness.md) | open | Pinning down the exact expressive power, limits, and missing primitives of the new ISO graph query standards. |
| [Incremental maintenance of graph pattern views](./incremental-pattern-maintenance.md) | open | Maintaining subgraph-match and path-query answers under edge insert/delete with bounded per-update work. |
| [Continuous subgraph matching on streaming graphs](./streaming-subgraph-matching.md) | partially-solved | Detecting pattern (dis)appearances in high-velocity edge streams with bounded state and low latency. |
| [Distributed worst-case-optimal graph joins](./distributed-wcoj.md) | open | Communication-optimal multiway pattern matching in the MPC/shuffle model under skew, beyond Shares/HyperCube. |
| [Graph partitioning for query locality](./graph-partitioning-locality.md) | empirically-open | Partitioning property graphs to minimize cross-partition traversal for unknown, evolving navigational workloads. |
| [Native graph storage vs. relational backing](./native-vs-relational-storage.md) | empirically-open | Whether index-free-adjacency native storage genuinely beats a tuned relational/columnar layout for graph workloads. |
| [Adjacency and reachability index tradeoffs](./reachability-index-tradeoffs.md) | partially-solved | Index structures answering reachability/distance with sublinear space and query time on billion-edge dynamic graphs. |
| [Label-constrained and approximate shortest paths](./constrained-shortest-paths.md) | partially-solved | Indexing for label/predicate-constrained distance and path queries with provable accuracy/space tradeoffs. |
| [Property-graph schema and constraint theory](./property-graph-schema-theory.md) | open | A principled schema, key, and integrity-constraint theory for property graphs with validation and inference. |
| [Keys, normalization and dependencies for graphs](./graph-dependencies-normalization.md) | open | Defining graph functional/entity dependencies and normal forms that guide design without a fixed schema. |
| [Multiway join plans mixing paths and patterns](./hybrid-path-pattern-plans.md) | open | A cost-based optimizer that interleaves WCOJ pattern matching, path navigation, and binary joins optimally. |
| [Subgraph counting and homomorphism complexity](./subgraph-counting-complexity.md) | partially-solved | Practical exact/approximate counting of motifs exploiting treewidth/homomorphism structure at scale. |
| [Temporal and time-respecting path queries](./temporal-path-queries.md) | open | Models, indexes, and complexity for time-respecting reachability and pattern matching over temporal graphs. |
| [Graph analytics vs. query engine unification](./analytics-query-unification.md) | empirically-open | One engine and abstraction spanning pattern/path queries and iterative analytics (PageRank, components) efficiently. |
| [Out-of-core and GPU graph analytics scheduling](./out-of-core-gpu-analytics.md) | empirically-open | Scheduling iterative analytics over graphs exceeding GPU/RAM with irregular access and minimal I/O stalls. |
| [Distributed iterative analytics communication bounds](./distributed-analytics-bounds.md) | partially-solved | Tight round/communication lower bounds for PageRank, connectivity, and matching in vertex-centric/MPC models. |
| [Dynamic graph analytics with bounded recomputation](./dynamic-analytics-maintenance.md) | open | Maintaining centrality, components, and core decomposition under edge updates without full recomputation. |
| [Provenance and explanation for graph queries](./graph-provenance-explanation.md) | open | Why-provenance, witnesses, and minimal explanations for path/pattern answers over annotated property graphs. |
| [Approximate and sampled pattern matching](./approximate-pattern-matching.md) | open | Sampling estimators with error guarantees for embedding counts and aggregate pattern queries on huge graphs. |
| [Worst-case-optimal RDF/SPARQL evaluation](./sparql-wco-evaluation.md) | partially-solved | Bringing WCOJ and tree-decomposition optimality to SPARQL basic graph patterns with property paths at scale. |
| [Vector-augmented graph query processing](./vector-graph-queries.md) | empirically-open | Integrating ANN similarity predicates into graph pattern/path queries with a joint cost model and index. |
| [Benchmarking and workload generation for graphs](./graph-benchmarking.md) | empirically-open | Realistic, parameterizable graph and query generators and metrics that expose true engine weaknesses. |
| [Adaptive runtime reoptimization for graph queries](./adaptive-graph-reoptimization.md) | open | Mid-query re-routing of pattern/path evaluation under wrong estimates without regressing below the static plan. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
