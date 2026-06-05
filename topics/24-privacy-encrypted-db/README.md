# Privacy & Encrypted Databases

This topic studies how to answer queries over data that must stay confidential — either
from the analyst (via differential privacy and other formal privacy notions for SQL and
relational analytics) or from the server/storage provider (via encrypted, searchable,
and oblivious databases). The central tension is that any useful answer leaks
information, so the research spans formal privacy/leakage definitions and lower bounds
on one side, and the cryptographic systems engineering of practical encrypted, oblivious,
and secure-multiparty query engines on the other. The problems below cover differentially
private query processing, encrypted/searchable databases and their leakage-abuse
surface, access-pattern hiding (ORAM/oblivious operators), and secure multiparty query
processing, as studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT and adjacent security venues.

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal DP Mechanisms for Multi-Join Queries](./dp-multi-join-sensitivity.md) | open | Computing or approximating tight global/local sensitivity and optimal noise for SQL queries with multiple joins and self-joins. |
| [Differentially Private Query Plan Optimization](./dp-query-plan-optimization.md) | open | A cost model and optimizer that chooses execution plans minimizing total privacy-loss-for-accuracy rather than runtime. |
| [End-to-End Privacy Budget Accounting for Workloads](./privacy-budget-accounting-workloads.md) | partially-solved | Tight composition accounting across an evolving, adaptive workload of correlated SQL queries under a fixed global budget. |
| [DP Under Foreign-Key Constraints and Schemas](./dp-with-fk-constraints.md) | open | Defining and achieving neighbor-relations and sensitivity for normalized multi-relation schemas with referential integrity. |
| [Truthful Private Histograms over Hierarchies](./private-hierarchical-histograms.md) | partially-solved | Optimal consistent noisy answers to large hierarchical/range-count workloads under pure and approximate DP. |
| [Local-DP SQL Analytics with Joins](./local-dp-joins.md) | open | Whether useful join and multi-table analytics are achievable under local differential privacy without a trusted curator. |
| [Instance-Optimal Local Sensitivity Release](./instance-optimal-local-sensitivity.md) | open | Releasing query answers calibrated to instance-specific sensitivity without leaking the sensitivity itself. |
| [DP for Streaming and Continuous Queries](./dp-streaming-continuous.md) | partially-solved | Continual observation mechanisms with near-optimal error for unbounded streams of relational aggregates. |
| [Private Cardinality and Selectivity Estimation](./private-cardinality-estimation.md) | open | Differentially private cardinality/selectivity estimates usable inside an optimizer without exhausting the budget. |
| [Leakage-Abuse-Resistant Searchable Encryption](./leakage-abuse-resistant-sse.md) | open | Searchable symmetric encryption schemes provably resisting known volume/access/co-occurrence leakage-abuse attacks. |
| [Encrypted Range Queries Without Order Leakage](./encrypted-range-no-order-leakage.md) | partially-solved | Practical encrypted range query schemes that avoid the order/distribution leakage exploited against OPE/ORE. |
| [Optimal ORAM Bandwidth-Latency Tradeoff](./oram-bandwidth-latency-tradeoff.md) | partially-solved | Closing the gap to the logarithmic ORAM lower bound while achieving low round complexity for database workloads. |
| [Oblivious Relational Operators at Scale](./oblivious-relational-operators.md) | open | Oblivious join/group-by/sort operators with overhead competitive with plaintext on large inputs. |
| [Access-Pattern Leakage Quantification](./access-pattern-leakage-quantification.md) | open | A general framework to quantify and bound what a sequence of access patterns reveals about data and queries. |
| [Volume-Hiding Encrypted Multi-Maps](./volume-hiding-multimaps.md) | partially-solved | Encrypted multi-map and join indexes that hide result/intermediate volumes with sub-quadratic storage. |
| [Forward/Backward Private Dynamic SSE](./forward-backward-private-sse.md) | partially-solved | Dynamic searchable encryption with strong forward/backward privacy and low update/search overhead at scale. |
| [Secure Multiparty Join Processing](./mpc-secure-joins.md) | open | MPC join protocols with communication/round complexity scaling to real OLAP-size relations across distrustful parties. |
| [Communication Lower Bounds for MPC Queries](./mpc-query-communication-lower-bounds.md) | open | Tight communication and round lower bounds for secure evaluation of relational-algebra and aggregation queries. |
| [Practical Private Set Intersection Joins](./psi-equijoin-cardinality.md) | partially-solved | Scalable private-join/PSI-cardinality protocols that compute aggregates without revealing the intersecting rows. |
| [Hybrid TEE + Crypto Query Engines](./tee-crypto-hybrid-engines.md) | empirically-open | Principled splitting of query execution between enclaves and cryptography under side-channel and leakage models. |
| [Side-Channel-Resistant Enclave Query Execution](./enclave-side-channel-resistant.md) | empirically-open | Query operators inside TEEs that provably resist timing, paging, and microarchitectural side channels at acceptable cost. |
| [Homomorphic SQL Aggregation at Practical Cost](./fhe-sql-aggregation.md) | solved-but-impractical | FHE-based SQL aggregation/filtering with overhead low enough for interactive analytic workloads. |
| [Provable Bounds for Snapshot Encrypted DBs](./snapshot-attack-bounds.md) | open | Tight reconstruction bounds for property-preserving encrypted columns under snapshot (single-dump) adversaries. |
| [Query-Recovery Hardness for Encrypted DBs](./query-recovery-hardness.md) | open | Characterizing when query/data reconstruction from leakage is information-theoretically or computationally hard. |
| [DP-Encrypted Co-Design Against Leakage](./dp-encrypted-codesign.md) | open | Combining differential privacy with encryption so access-pattern leakage is itself differentially private. |
| [Privacy-Preserving Query Auditing](./private-query-auditing.md) | open | Deciding online whether answering a query violates a privacy policy, given prior answers, without itself leaking. |
| [Multi-Analyst Fair Budget Allocation](./multi-analyst-budget-allocation.md) | open | Allocating a shared global privacy budget across competing analysts with incentive and fairness guarantees. |
| [Private Synthetic Relational Data with Utility Guarantees](./private-synthetic-relational-data.md) | partially-solved | Generating DP synthetic multi-table data that provably preserves join/aggregate query accuracy. |
| [Encrypted Query Optimization and Planning](./encrypted-query-optimization.md) | open | Cost-based optimization over encrypted operators where statistics themselves are encrypted or leakage-bounded. |
| [Verifiable Private Outsourced Queries](./verifiable-private-outsourced-queries.md) | partially-solved | Proving correctness/completeness of outsourced query answers while preserving data and access-pattern privacy. |

---

[Back to taxonomy](../../TAXONOMY.md)
