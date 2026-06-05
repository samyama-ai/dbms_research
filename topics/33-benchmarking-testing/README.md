# Benchmarking, Testing & Verification

Methods for measuring, stress-testing, and proving correctness of database systems: realistic
and adversarial workload generation, query fuzzing, metamorphic and differential testing,
formal verification of optimizers/storage/concurrency code, and the central *oracle problem* of
deciding whether a DBMS returned the right answer. This topic spans deep theory (decidability of
equivalence used as a test oracle, complexity of bug-minimization, statistical guarantees for
benchmarks) and gritty systems work (building fuzzers that find real CVEs, generating workloads
that match production, verifying transactional histories at scale). It sits at the intersection of
the PODS tradition and the practical reliability concerns driving modern SIGMOD/VLDB/CIDR research.

| Problem | Status | Scope |
|---|---|---|
| [The Test Oracle Problem for SQL](./sql-test-oracle-problem.md) | open | Construct a sound, general oracle that decides whether a DBMS answer to an arbitrary SQL query is correct without a trusted reference engine. |
| [Metamorphic Relations for Query Engines](./metamorphic-relations-queries.md) | partially-solved | Systematically discover and prove sound metamorphic relations covering the full SQL surface, not just hand-picked ones. |
| [Differential Testing Across Heterogeneous DBMSs](./differential-testing-heterogeneous.md) | partially-solved | Make differential testing robust to legitimate cross-engine semantic divergences (NULLs, collation, types) so disagreements imply real bugs. |
| [Grammar-Aware SQL Fuzzing Coverage](./grammar-aware-sql-fuzzing.md) | empirically-open | Generate syntactically/semantically valid SQL that maximizes deep optimizer/executor code coverage rather than getting rejected at parse time. |
| [Bug-Inducing Query Minimization](./bug-query-minimization.md) | partially-solved | Minimize a failing query+schema+data triple to a smallest reproducer with provable or near-provable minimality guarantees. |
| [Realistic Workload Generation from Logs](./workload-generation-from-logs.md) | empirically-open | Synthesize benchmark workloads that statistically match an anonymized production query/transaction log including correlations and skew. |
| [Privacy-Preserving Benchmark Data Synthesis](./privacy-preserving-data-synthesis.md) | partially-solved | Generate synthetic benchmark databases that preserve query-plan-relevant statistics while giving formal privacy guarantees over the original data. |
| [Schema-and-Data Co-Generation for Stress Tests](./schema-data-co-generation.md) | open | Jointly generate schemas, constraints, and data instances that provably trigger targeted optimizer/executor corner cases. |
| [Verifying Query Optimizer Transformation Rules](./verify-optimizer-rules.md) | partially-solved | Formally prove that each rewrite rule in a real optimizer preserves query semantics under bag/SQL three-valued logic. |
| [Mechanized Proof of a Cost-Based Optimizer](./verified-cost-based-optimizer.md) | open | Build an end-to-end machine-checked proof that a cost-based optimizer's output is equivalent to its input plan. |
| [Formal Verification of Concurrency Control](./verify-concurrency-control.md) | partially-solved | Mechanically verify that a concurrency-control protocol implementation guarantees its claimed isolation level under all interleavings. |
| [Checking Isolation-Level Conformance Empirically](./isolation-level-conformance.md) | partially-solved | Decide from observed client histories which isolation/anomaly guarantees a black-box DBMS actually provides. |
| [Scalable Serializability Checking](./scalable-serializability-checking.md) | partially-solved | Verify serializability of large observed transaction histories despite the NP-hardness of the general problem. |
| [Crash-Consistency Testing of Storage Engines](./crash-consistency-testing.md) | empirically-open | Systematically explore power-fail/crash points to find durability and recovery bugs in storage engines. |
| [Bounded-Equivalence Oracle via SMT](./bounded-equivalence-smt.md) | partially-solved | Use SMT/decision procedures to decide equivalence of two query plans on bounded instances as a strong test oracle. |
| [Coverage Metrics for DBMS Testing](./dbms-coverage-metrics.md) | open | Define a meaningful, automatable adequacy/coverage criterion for SQL semantics beyond code-line coverage. |
| [Reproducible Performance Benchmarking](./reproducible-performance-benchmarking.md) | empirically-open | Obtain statistically sound, reproducible throughput/latency comparisons despite noise, warmup, and configuration sensitivity. |
| [Benchmark Gaming and Specification Robustness](./benchmark-gaming-robustness.md) | open | Design benchmark specifications that resist over-tuning and special-casing while remaining representative. |
| [Cardinality-Estimator Accuracy Benchmarking](./cardinality-estimator-benchmarking.md) | partially-solved | Build workloads and ground-truth methodology that fairly stress and compare cardinality estimators across correlation regimes. |
| [Testing Learned Database Components](./testing-learned-components.md) | open | Develop oracles and adversarial workloads that expose correctness/robustness failures in learned indexes, estimators, and optimizers. |
| [Fault Injection for Distributed Databases](./distributed-fault-injection.md) | empirically-open | Systematically inject network/partition/clock faults to expose consistency and liveness bugs in distributed DBMSs. |
| [Verifying Distributed Commit Protocols](./verify-commit-protocols.md) | partially-solved | Produce machine-checked safety/liveness proofs of 2PC/3PC/consensus-based commit as implemented, not as idealized. |
| [Generating Adversarial Cardinality Workloads](./adversarial-cardinality-workloads.md) | open | Automatically construct queries/data that maximally mislead an optimizer's estimates to expose plan-regression risk. |
| [Oracle for Floating-Point and Decimal Semantics](./numeric-semantics-oracle.md) | open | Decide correctness of aggregates/arithmetic across engines given differing rounding, overflow, and precision semantics. |
| [Time-Travel and Temporal Query Testing](./temporal-query-testing.md) | open | Generate oracles and workloads that validate as-of/versioned/bitemporal query results against a verifiable reference. |
| [Mutation Testing for SQL and Schemas](./mutation-testing-sql.md) | partially-solved | Define meaningful mutation operators for queries/schemas/constraints and assess test-suite quality with tractable equivalent-mutant detection. |
| [Property-Based Testing of Transaction APIs](./property-based-transaction-testing.md) | partially-solved | Express and check rich transactional/consistency properties via generators that explore meaningful concurrent histories. |
| [Continuous Benchmarking for Regression Detection](./continuous-benchmarking-regression.md) | empirically-open | Detect statistically significant performance regressions in CI from noisy, high-dimensional benchmark signals. |
| [Verified Reference Implementation of SQL Semantics](./verified-sql-semantics.md) | partially-solved | Formalize full SQL (NULLs, bag semantics, aggregation, subqueries) in a proof assistant to serve as a trusted oracle. |
| [Cost-Model Validation and Calibration](./cost-model-validation.md) | open | Empirically validate and falsify an optimizer's cost model against measured execution across hardware and data regimes. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
