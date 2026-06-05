# Query Languages & Expressiveness

The logical heart of database theory: what queries a language *can* and *cannot* express,
and at what computational cost. This topic spans Datalog and recursion, the expressive
power of first-order logic and SQL, descriptive complexity (the logic-vs-complexity-class
correspondence), query rewriting and answering using views, and the design of new query
languages for graphs, streams, and modern data models. Problems here range from deep open
questions in finite model theory (does a logic capture PTIME?) to concrete systems
challenges (how to compile, optimize, and incrementally maintain recursive queries at
scale) in the PODS/SIGMOD/VLDB tradition.

| Problem | Status | Scope |
|---|---|---|
| [A Logic Capturing PTIME on Unordered Structures](./logic-capturing-ptime.md) | open | Determine whether there is a logic that captures exactly the polynomial-time queries on arbitrary finite structures. |
| [Datalog Boundedness and Predicate Boundedness](./datalog-boundedness.md) | partially-solved | Decide whether a Datalog program is equivalent to a non-recursive (bounded) one, across program classes. |
| [Static Analysis of Datalog with Negation](./datalog-negation-analysis.md) | open | Characterize decidability and semantics (stratified/well-founded/stable) for containment and equivalence of Datalog with negation. |
| [Expressive Power and Limits of SQL Recursion](./sql-recursive-expressiveness.md) | partially-solved | Pin down what recursive SQL (WITH RECURSIVE, linear vs. mutual) can express versus full Datalog and fixpoint logics. |
| [Choice of Fixpoint Operator for Capturing Classes](./fixpoint-logic-capture.md) | partially-solved | Settle which fixpoint/transitive-closure extensions of FO capture which complexity classes on ordered/unordered structures. |
| [Rank Logic and Capturing PTIME via Linear Algebra](./rank-logic-ptime.md) | open | Determine whether FO plus rank operators (or related algebraic operators) captures PTIME. |
| [Containment of Conjunctive Queries with Recursion](./recursive-query-containment.md) | partially-solved | Decide containment between recursive (Datalog/RPQ) queries and characterize the decidability frontier. |
| [Decidable Query Determinacy and View Rewriting](./determinacy-view-rewriting.md) | open | Decide whether views determine a query and whether an equivalent (FO/Datalog) rewriting exists. |
| [Maximally Contained Rewritings Using Views](./maximally-contained-rewriting.md) | partially-solved | Compute maximally contained rewritings under open-world assumptions for recursive and constrained settings. |
| [Regular Path Query Evaluation and Optimization](./rpq-evaluation-optimization.md) | empirically-open | Evaluate and optimize regular/conjunctive regular path queries at scale with provable guarantees. |
| [Expressiveness and Design of Graph Query Languages](./graph-query-language-design.md) | open | Establish the expressive-power hierarchy and a principled core for GQL/Cypher/SPARQL-style languages. |
| [Two-Variable and Guarded Logic Query Power](./guarded-logic-expressiveness.md) | partially-solved | Map the expressiveness/complexity tradeoffs of guarded, two-variable, and unary-negation fragments for querying. |
| [Locality and Lower Bounds for FO Queries](./fo-locality-lower-bounds.md) | partially-solved | Use Hanf/Gaifman locality and games to prove inexpressibility results for practical query fragments. |
| [Aggregation and Arithmetic in Logical Query Languages](./aggregation-logic-semantics.md) | open | Give a clean expressiveness theory and capture results for query languages with grouping, aggregation, and arithmetic. |
| [Provenance Semirings for Recursive and Aggregate Queries](./semiring-provenance-recursion.md) | partially-solved | Extend semiring/absorptive provenance soundly and finitely to recursion and aggregation. |
| [Datalog with Aggregation and Lattice Semantics](./datalog-aggregation-lattices.md) | partially-solved | Define convergent, deterministic semantics for Datalog extended with aggregation/lattice values and program analysis. |
| [Incremental Maintenance of Recursive Views](./incremental-recursive-views.md) | empirically-open | Incrementally maintain recursive/Datalog views under updates with bounded work and correctness guarantees. |
| [Constant-Delay Enumeration for Expressive Queries](./constant-delay-enumeration.md) | partially-solved | Characterize which query/structure classes admit linear-preprocessing constant-delay answer enumeration. |
| [Semantic Query Optimization with Recursion](./semantic-optimization-recursion.md) | open | Exploit integrity constraints to rewrite and prune recursive queries provably and automatically. |
| [Termination and Magic-Sets for Existential Rules](./existential-rules-evaluation.md) | partially-solved | Decide termination and design goal-directed (magic-set/chase) evaluation for existential-rule (TGD) query answering. |
| [Expressive Completeness of Algebraic Query Languages](./algebraic-completeness.md) | partially-solved | Settle expressive-completeness and the operator basis for relational, nested-relational, and tensor algebras. |
| [Nested-Relational and Higher-Order Query Calculi](./nested-relational-calculi.md) | partially-solved | Characterize the expressive power and conservativity of nested/complex-object and comprehension-based languages. |
| [Querying with Counting and Majority Quantifiers](./counting-logic-queries.md) | partially-solved | Determine the expressive power of FO/fixpoint logics extended with counting on practical query problems. |
| [Datalog Optimization and Compilation at Scale](./datalog-compilation-scale.md) | empirically-open | Compile and optimize Datalog (join ordering, semi-naive, demand) to compete with hand-written engines. |
| [Expressiveness of Window and Streaming Query Languages](./streaming-language-expressiveness.md) | open | Formalize and compare the expressive power of windowed/continuous query languages over infinite streams. |
| [Polymorphic and Schema-Independent Query Languages](./schema-independent-queries.md) | open | Design and characterize languages whose queries are invariant under schema/representation changes. |
| [Query Language Power Over Probabilistic Databases](./probabilistic-query-languages.md) | partially-solved | Characterize the dichotomy between tractable and #P-hard query classes over probabilistic data. |
| [Translating Natural Language to Formal Queries](./nl-to-query-semantics.md) | empirically-open | Ground natural-language questions into semantically faithful, executable formal queries with guarantees. |
| [Bag (Multiset) Semantics Expressiveness and Equivalence](./bag-semantics-expressiveness.md) | open | Develop expressiveness theory and decide equivalence/containment for query languages under bag semantics. |
| [Unified Algebra for Multi-Model and Polystore Queries](./multimodel-query-algebra.md) | empirically-open | Design a compositional algebra and expressiveness theory spanning relational, document, graph, and tensor models. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
