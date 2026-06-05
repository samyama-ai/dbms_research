# Database Security & Access Control

Database security spans the formal models that decide who may see or change what (access-control logics, RBAC/ABAC, view-based authorization, row/column-level security), the harder problem of stopping what authorized queries *leak* (inference, aggregation, and statistical-disclosure control), the systems fight against injection and authorization bugs, and the cryptographic/hardware machinery that hides access patterns themselves (ORAM, oblivious indexes, enclave-backed engines). The problems below sit at the intersection of deep theory — undecidability of safety, complexity of inference detection, information-theoretic ORAM bounds — and brutal systems engineering — provably side-channel-free query execution, auditable policy at cloud scale, and injection defenses that survive real ORMs. Each is genuinely open or unresolved across the cost dimensions that matter at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT.

| Problem | Status | Scope |
|---------|--------|-------|
| [Safety of Propagating Access Rights](./hru-safety-decidability.md) | open | Identifying expressive yet decidable protection-state models between the undecidable HRU matrix and trivially weak monotonic systems. |
| [Inference Detection Complexity](./inference-detection-complexity.md) | open | Pinning the exact complexity of deciding whether a set of authorized views/queries lets a user infer a protected fact. |
| [Provably Secure View-Based Authorization](./view-authorization-security.md) | partially-solved | Deciding when a set of authorized views is information-theoretically safe rather than merely syntactically restrictive. |
| [Query Rewriting for Fine-Grained Access](./fine-grained-rewriting.md) | partially-solved | Sound and complete rewriting of arbitrary SQL under row/column/cell-level policies without leaking via filtered errors or cardinalities. |
| [Aggregation Control Lower Bounds](./aggregation-control-bounds.md) | open | Tight bounds on how many aggregate queries can be answered before a tracker attack reconstructs protected individual values. |
| [ORAM Bandwidth Lower Bounds](./oram-bandwidth-lower-bounds.md) | partially-solved | Closing the gap between the log-n Goldreich-Ostrovsky/Larsen-Nielsen lower bound and practical ORAM overhead for database workloads. |
| [Oblivious Range and Index Queries](./oblivious-range-index.md) | open | Sublinear oblivious B-tree/range access that hides the access pattern without per-query polylog blowup over large tables. |
| [Access-Pattern Leakage Quantification](./access-pattern-leakage.md) | partially-solved | A general measure of how much an encrypted/oblivious scheme's residual leakage enables reconstruction across query distributions. |
| [SQL Injection Soundness Guarantees](./sql-injection-soundness.md) | partially-solved | Static or runtime defenses that provably eliminate injection across stored procedures, dynamic SQL, and ORM-generated queries. |
| [Second-Order and Stored Injection](./second-order-injection.md) | open | Detecting injection where the payload is persisted and triggered by a later, separately-trusted query path. |
| [Policy Conflict Detection at Scale](./policy-conflict-detection.md) | partially-solved | Efficiently detecting redundancy, conflict, and unreachable rules in large ABAC/RBAC policy sets with hierarchies and constraints. |
| [Expressiveness of ABAC vs RBAC](./abac-rbac-expressiveness.md) | partially-solved | Formal separation results characterizing exactly which policies ABAC can express that role-based models cannot, and at what cost. |
| [Dynamic Separation of Duty Enforcement](./dynamic-sod-enforcement.md) | open | Enforcing history-dependent separation-of-duty constraints under concurrent transactions without serializing all access. |
| [Provable Tamper-Evident Audit Logs](./tamper-evident-audit.md) | partially-solved | Audit logs that are cryptographically tamper-evident and efficiently verifiable even against a compromised database administrator. |
| [Query-Level Misuse Detection](./query-misuse-detection.md) | empirically-open | Detecting malicious-yet-authorized query behavior (exfiltration, recon) without unacceptable false-positive rates on real workloads. |
| [Information Flow Control in DBMS](./information-flow-control.md) | open | Tracking and enforcing end-to-end declassification policies through query operators, triggers, and application stored logic. |
| [Statistical Database Tracker Resistance](./tracker-resistance.md) | open | Query restriction that provably blocks tracker/linear-system attacks while preserving acceptable analytic utility. |
| [Side-Channel-Free Query Execution](./side-channel-free-execution.md) | open | Query operators whose timing, memory, and cache behavior provably do not leak data values across co-tenants or enclaves. |
| [Enclave-Backed Oblivious Operators](./enclave-oblivious-operators.md) | empirically-open | Joins/aggregations inside TEEs that are data-oblivious yet competitive with non-oblivious plans on real hardware. |
| [Searchable Encryption Leakage Abuse](./searchable-encryption-leakage.md) | partially-solved | Characterizing and defeating leakage-abuse/reconstruction attacks on searchable-encrypted indexes under query and update leakage. |
| [Authorization-Aware Query Optimization](./authorization-aware-optimization.md) | open | Optimizing plans so that pushing down security predicates never opens an inference channel via timing or partial results. |
| [Negative and Default-Deny Authorization](./negative-authorization-semantics.md) | partially-solved | Well-defined, conflict-free semantics for combining positive/negative grants with propagation, overriding, and revocation. |
| [Revocation Cascade Complexity](./revocation-cascade-complexity.md) | partially-solved | The cost and correctness of cascading grant/revoke under the GRANT-option graph at scale and under concurrency. |
| [Differential Privacy under Foreign Keys](./dp-relational-joins.md) | open | Calibrating differentially private noise for queries over joined relations where one tuple influences unboundedly many outputs. |
| [Purpose-Based and Usage Control](./purpose-usage-control.md) | open | Enforcing purpose limitation and obligation-bearing usage policies that constrain data *after* it leaves a query. |
| [Verified Reference Monitors for DBMS](./verified-reference-monitor.md) | partially-solved | Machine-checked proof that a production authorization layer fully mediates and matches its policy specification. |
| [Multi-Tenant Isolation Guarantees](./multi-tenant-isolation.md) | empirically-open | Provable data and side-channel isolation between tenants sharing buffers, indexes, and query engines in cloud databases. |
| [Polyinstantiation Consistency](./polyinstantiation-consistency.md) | open | Reconciling multilevel-secure polyinstantiation with serializability and integrity constraints without covert channels. |
| [Covert Channel Bandwidth Bounds](./covert-channel-bounds.md) | open | Bounding and closing storage/timing covert channels arising from shared locks, sequences, and optimizer statistics. |
| [Access Control for Provenance Queries](./provenance-access-control.md) | open | Policies that release lineage/explanations without leaking the very tuples the base-data policy is meant to hide. |

---
[← Back to taxonomy](../../TAXONOMY.md)
