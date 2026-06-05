# Multi-Model & Document Databases

Multi-model and document databases store semistructured data (JSON, XML, key-value, graph, and relational) under one engine, embracing schema-on-read and path-based query languages instead of a fixed relational schema. The central tensions are giving heterogeneous, irregular data a tractable theory (typing, containment, cost models), optimizing queries that cross data models and storage layouts, and federating multiple specialized stores (polystores) without sacrificing correctness or performance.

This catalog collects 30 research-grade open problems at the intersection of theory (complexity, bounds, expressiveness) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [Complexity of JSONPath query evaluation](./jsonpath-evaluation-complexity.md) | partially-solved | Pinning down combined/data complexity and expressive power of JSONPath/SQL-JSON path dialects under their full feature set. |
| [Static schema inference from document collections](./schema-inference-documents.md) | open | Inferring a concise, sound, and useful schema (JSON Schema) from a heterogeneous document corpus with provable quality guarantees. |
| [Containment and equivalence of JSON path queries](./jsonpath-containment.md) | open | Deciding containment/equivalence for navigational JSON path queries with filters, recursion, and arithmetic. |
| [Cost model for schemaless document scans](./schemaless-cost-model.md) | empirically-open | Building a cardinality and cost model when records lack a fixed schema and field presence is data-dependent. |
| [Multi-model query optimization across models](./multimodel-query-optimization.md) | open | Joint plan enumeration and cost-based optimization for queries spanning relational, document, and graph operators. |
| [Polystore query planning over heterogeneous engines](./polystore-query-planning.md) | partially-solved | Planning and decomposing a single query across autonomous stores with incomparable capabilities and cost models. |
| [Physical layout selection for semistructured data](./physical-layout-selection.md) | empirically-open | Automatically choosing row/column/shredded/native layouts per field for irregular nested data. |
| [Worst-case-optimal joins over nested data](./wco-joins-nested.md) | open | Extending worst-case-optimal join theory and AGM-style bounds to nested/document and array-valued attributes. |
| [Path indexing for deeply nested documents](./nested-path-indexing.md) | partially-solved | Index structures answering arbitrary path/predicate queries over deep, irregular nesting with bounded space. |
| [Expressiveness of multi-model query languages](./multimodel-language-expressiveness.md) | open | Characterizing the relative expressive power of unified languages (SQL/JSON, GQL, AQL, MongoDB) across data models. |
| [Type systems for schema-on-read access](./schema-on-read-typing.md) | open | A sound, gradual type discipline that catches errors on schema-on-read queries without imposing schema-on-write. |
| [Schema evolution without migration](./schema-evolution-no-migration.md) | empirically-open | Supporting in-place schema changes over billions of documents with mixed versions and no global rewrite. |
| [Document store cardinality estimation](./document-cardinality-estimation.md) | empirically-open | Estimating selectivity of path/array/existence predicates over schemaless collections with skewed, sparse fields. |
| [Cross-model join algorithms and bounds](./cross-model-join-algorithms.md) | open | Join algorithms and lower bounds when join keys span graph edges, document fields, and relational columns. |
| [Federated cost-model reconciliation](./federated-cost-reconciliation.md) | open | Reconciling incompatible, opaque cost estimates from autonomous stores into one comparable optimizer currency. |
| [Consistent transactions across polystores](./polystore-transactions.md) | partially-solved | Providing serializable or snapshot-isolated transactions spanning stores with different concurrency models. |
| [Provenance across multi-model transformations](./multimodel-provenance.md) | open | Tracking why/how/where provenance through queries that shred, nest, and cross data-model boundaries. |
| [Compression of heterogeneous JSON columns](./json-columnar-compression.md) | empirically-open | Encoding sparse, deeply nested, type-heterogeneous JSON into columnar formats with good scan and compression. |
| [Adaptive shredding of nested data](./adaptive-shredding.md) | empirically-open | Deciding online which nested substructures to materialize as relational columns based on workload drift. |
| [Query rewriting between document and relational](./document-relational-rewriting.md) | partially-solved | Provably correct bidirectional rewriting of queries across normalized relational and embedded document designs. |
| [XML/JSON path query minimization](./path-query-minimization.md) | partially-solved | Minimizing tree-pattern/path queries under structural and integrity constraints over semistructured trees. |
| [Statistics maintenance for evolving schemas](./evolving-schema-statistics.md) | empirically-open | Incrementally maintaining accurate statistics as the implicit schema and field distributions drift over time. |
| [Integrity constraints over semistructured data](./semistructured-constraints.md) | open | Defining, checking, and exploiting keys/FDs/inclusion dependencies over nested, optional, repeated structure. |
| [Vectorized execution over nested arrays](./vectorized-nested-execution.md) | empirically-open | Achieving columnar-style vectorized execution for unnesting, lateral joins, and array operators on nested data. |
| [Pushdown capability negotiation in federation](./pushdown-capability-negotiation.md) | partially-solved | Formalizing and exploiting partial, asymmetric predicate/operator pushdown capabilities of federated sources. |
| [Benchmarks and theory for schema flexibility](./schema-flexibility-benchmarks.md) | open | A principled metric and benchmark quantifying the cost/benefit tradeoff of schema-on-read vs schema-on-write. |
| [Auto-tuning storage for mixed workloads](./multimodel-auto-tuning.md) | empirically-open | Self-tuning indexes, layouts, and materializations for HTAP workloads mixing document, graph, and relational access. |
| [Approximate path queries with error bounds](./approximate-path-queries.md) | open | Sampling/sketching for path and array-aggregation queries over documents with provable error guarantees. |
| [Semantic equivalence of model encodings](./model-encoding-equivalence.md) | open | Deciding when two encodings of the same data in different models are information-preserving and query-equivalent. |
| [Optimal data placement across polystore tiers](./polystore-data-placement.md) | open | Assigning datasets/fragments to specialized stores to minimize total query cost under capability constraints. |

[← Back to taxonomy](../../TAXONOMY.md)
