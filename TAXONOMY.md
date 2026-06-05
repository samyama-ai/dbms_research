# Taxonomy — DBMS Research Problems

35 topics, ~30 problems each (~1050 problems total). Each topic directory contains a
`README.md` index and one `.md` file per problem.

| # | Topic | Directory | Scope |
|---|-------|-----------|-------|
| 01 | Relational Model & Dependency Theory | [`01-relational-theory`](./topics/01-relational-theory/) | Relational algebra/calculus, FDs/MVDs/JDs, the chase, normalization theory, query equivalence/containment |
| 02 | Query Optimization | [`02-query-optimization`](./topics/02-query-optimization/) | Join ordering, cost models, plan enumeration, transformation rules, adaptive & robust optimization |
| 03 | Query Processing & Execution | [`03-query-processing`](./topics/03-query-processing/) | Join algorithms, worst-case-optimal joins, vectorized/compiled execution, aggregation, top-k |
| 04 | Indexing & Access Methods | [`04-indexing-access-methods`](./topics/04-indexing-access-methods/) | B-trees, LSM-trees, hashing, bitmap/inverted, multidimensional, write/read/space tradeoffs |
| 05 | Concurrency Control | [`05-concurrency-control`](./topics/05-concurrency-control/) | Serializability theory, 2PL, OCC, MVCC, isolation levels, deterministic execution |
| 06 | Recovery, Logging & Durability | [`06-recovery-logging`](./topics/06-recovery-logging/) | ARIES, WAL, checkpointing, NVM logging, group commit, instant recovery |
| 07 | Storage & Buffer Management | [`07-storage-buffer`](./topics/07-storage-buffer/) | Buffer replacement, caching theory, page layout, compression, tiering |
| 08 | Distributed Query Processing | [`08-distributed-databases`](./topics/08-distributed-databases/) | Partitioning, distributed joins, semijoin reduction, shuffle, straggler mitigation |
| 09 | Replication & Consistency | [`09-replication-consistency`](./topics/09-replication-consistency/) | Consistency models, CRDTs, causal/eventual consistency, anti-entropy, CAP/PACELC |
| 10 | Consensus & Coordination | [`10-consensus-coordination`](./topics/10-consensus-coordination/) | Paxos/Raft, atomic commit, FLP, Byzantine agreement, leases, membership |
| 11 | NoSQL & Key-Value Stores | [`11-nosql-kv`](./topics/11-nosql-kv/) | KV data models, sharding, compaction, secondary indexing, tunable consistency |
| 12 | NewSQL & Distributed SQL | [`12-newsql-distributed-sql`](./topics/12-newsql-distributed-sql/) | Distributed transactions, deterministic DBs, global clocks, distributed snapshot isolation |
| 13 | Column Stores & OLAP | [`13-column-stores-olap`](./topics/13-column-stores-olap/) | Columnar layout, encoding, late materialization, cube/rollup, vectorization |
| 14 | Main-Memory Databases | [`14-main-memory-db`](./topics/14-main-memory-db/) | In-memory indexing, lock-free structures, NUMA, durability for IMDBs |
| 15 | Data Integration & Schema Mapping | [`15-data-integration`](./topics/15-data-integration/) | Schema matching/mapping, data exchange, certain answers, entity resolution at scale |
| 16 | Data Cleaning & Quality | [`16-data-cleaning-quality`](./topics/16-data-cleaning-quality/) | Constraint repair, error detection, deduplication, missing values, data fusion |
| 17 | Approximate Query Processing | [`17-approximate-query-processing`](./topics/17-approximate-query-processing/) | Sampling, sketches, histograms, error guarantees, online aggregation |
| 18 | Streaming & Continuous Queries | [`18-streaming-queries`](./topics/18-streaming-queries/) | Windowing, punctuation, load shedding, out-of-order, exactly-once, sketches |
| 19 | Temporal Databases | [`19-temporal-databases`](./topics/19-temporal-databases/) | Bitemporal models, temporal joins/aggregation, versioning, time-travel queries |
| 20 | Spatial & Spatiotemporal | [`20-spatial-databases`](./topics/20-spatial-databases/) | R-trees, space-filling curves, kNN, spatial joins, trajectories, GIS |
| 21 | Graph Databases & Processing | [`21-graph-databases`](./topics/21-graph-databases/) | Subgraph matching, path queries, RPQs, property graphs, graph analytics engines |
| 22 | Provenance & Lineage | [`22-provenance-lineage`](./topics/22-provenance-lineage/) | Why/how/where provenance, semirings, explanations, reverse data management |
| 23 | Database Security & Access Control | [`23-database-security`](./topics/23-database-security/) | Access control models, inference control, SQL injection, auditing, oblivious access |
| 24 | Privacy & Encrypted Databases | [`24-privacy-encrypted-db`](./topics/24-privacy-encrypted-db/) | Differential privacy for queries, encrypted/searchable DBs, leakage, secure MPC |
| 25 | Query Languages & Expressiveness | [`25-query-languages-expressiveness`](./topics/25-query-languages-expressiveness/) | Datalog, recursion, FO/SQL expressiveness, descriptive complexity, query rewriting |
| 26 | Cardinality Estimation & Statistics | [`26-cardinality-estimation`](./topics/26-cardinality-estimation/) | Selectivity, multi-attribute correlation, sketches, learned estimators, error bounds |
| 27 | Learned Database Components | [`27-learned-db-components`](./topics/27-learned-db-components/) | Learned indexes, learned CE, learned optimizers, instance-optimality, ML for tuning |
| 28 | Vector Databases & Similarity Search | [`28-vector-similarity-search`](./topics/28-vector-similarity-search/) | ANN, HNSW/IVF/PQ, recall-latency tradeoffs, filtered search, high-dim hardness |
| 29 | Hardware-Conscious Databases | [`29-hardware-conscious-db`](./topics/29-hardware-conscious-db/) | GPU/FPGA, SIMD, NVM, RDMA, cache-conscious algorithms, near-data processing |
| 30 | Cloud & Serverless Databases | [`30-cloud-serverless-db`](./topics/30-cloud-serverless-db/) | Storage/compute disaggregation, elasticity, multi-tenancy, serverless OLAP/OLTP |
| 31 | Time-Series Databases | [`31-time-series-db`](./topics/31-time-series-db/) | Time-series compression, downsampling, gorilla encoding, anomaly/forecast in-DB |
| 32 | Multi-Model & Document Databases | [`32-multimodel-document-db`](./topics/32-multimodel-document-db/) | JSON/document stores, schema-on-read, XML/JSON path queries, polystores |
| 33 | Benchmarking, Testing & Verification | [`33-benchmarking-testing`](./topics/33-benchmarking-testing/) | Workload generation, fuzzing, metamorphic testing, formal verification of DB code |
| 34 | Schema Design & Normalization | [`34-schema-design-normalization`](./topics/34-schema-design-normalization/) | Normal forms, dependency discovery, schema evolution, denormalization tradeoffs |
| 35 | Self-Driving / Autonomous Databases | [`35-autonomous-db`](./topics/35-autonomous-db/) | Auto-tuning, index/partition advisors, workload forecasting, self-driving control loops |

> The flat list of every problem is generated into [`INDEX.md`](./INDEX.md).
