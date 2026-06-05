# Relational Model & Dependency Theory

The mathematical bedrock of relational databases: relational algebra and calculus, the
theory of data dependencies (functional, multivalued, join, and more general embedded
dependencies), the chase procedure, normalization theory, and the equivalence/containment
of conjunctive and more expressive queries. This topic collects the hard and open problems
at the foundation of the field — questions about decidability, complexity, expressiveness,
and the gap between elegant theory and what query engines can actually execute. Problems
here sit squarely in the PODS tradition but increasingly drive systems work on certain
answers, semiring provenance, and constraint-aware optimization.

| Problem | Status | Scope |
|---|---|---|
| [Chase Termination for Arbitrary TGDs](./chase-termination-tgds.md) | open | Decide whether the (standard/oblivious) chase terminates on all instances for a given set of tuple-generating dependencies. |
| [Implication Problem for Embedded Dependencies](./embedded-dependency-implication.md) | partially-solved | Pin down decidable fragments and complexity of logical implication for embedded (multivalued/join/inclusion) dependencies. |
| [Conjunctive Query Containment Under Constraints](./cq-containment-under-constraints.md) | partially-solved | Characterize decidability/complexity of CQ containment in the presence of TGDs and EGDs. |
| [Optimal Bag-Semantics CQ Equivalence](./bag-cq-equivalence.md) | open | Decide equivalence of conjunctive queries under multiset (bag) semantics. |
| [Acyclic Join Dependency Recognition](./acyclic-join-dependencies.md) | partially-solved | Recognize and exploit acyclicity hierarchies of join dependencies for tractable evaluation and design. |
| [Worst-Case-Optimal Joins from Degree Constraints](./wcoj-degree-constraints.md) | partially-solved | Derive tight output-size bounds and matching algorithms from FDs/degree/cardinality constraints beyond AGM. |
| [Certain Answers Over Inconsistent Databases](./certain-answers-inconsistency.md) | partially-solved | Compute consistent/certain answers under constraint violation with tractable data complexity. |
| [Information-Theoretic Normal Forms](./information-theoretic-normalization.md) | partially-solved | Define and decide redundancy-free normal forms via an information-theoretic measure rather than syntactic FDs. |
| [Core Computation for Data Exchange](./core-computation-data-exchange.md) | solved-but-impractical | Compute the core of a universal solution efficiently in schema-mapping/data-exchange settings. |
| [Boundedness of Recursive Dependencies](./boundedness-recursive-dependencies.md) | open | Decide whether a recursive set of dependencies/Datalog program is equivalent to a non-recursive one. |
| [FD-Aware Query Minimization](./fd-aware-query-minimization.md) | partially-solved | Minimize conjunctive queries optimally using available functional dependencies and keys. |
| [Separability and Decidable Guarded TGDs](./guarded-tgd-reasoning.md) | partially-solved | Delineate the decidability frontier and combined complexity of reasoning with guarded/frontier-guarded TGDs. |
| [MVD/JD Inference Without a Complete Axiomatization](./jd-no-axiomatization.md) | open | Resolve the (non-)existence of finite k-ary complete axiomatizations for join dependencies. |
| [Chase Step Complexity and Size Bounds](./chase-size-bounds.md) | partially-solved | Bound the size and number of steps of a terminating chase as a function of dependency structure. |
| [Conditional FD Discovery vs. Implication](./conditional-fd-theory.md) | partially-solved | Formalize implication, axiomatization, and complexity for conditional and approximate FDs. |
| [Query Determinacy and Rewriting Using Views](./query-determinacy-views.md) | open | Decide whether a query is determined by a set of views and whether a (first-order) rewriting exists. |
| [Finite vs. Unrestricted Implication](./finite-vs-unrestricted-implication.md) | partially-solved | Separate finite from unrestricted implication for dependency classes and characterize finite controllability. |
| [Tractable Homomorphism via Treewidth/Submodular Width](./cq-treewidth-submodular-width.md) | partially-solved | Characterize the exact structural parameter governing polynomial-time CQ evaluation. |
| [Disjunctive and Existential Dependency Repair](./disjunctive-dependency-repair.md) | open | Reason about and repair under disjunctive existential rules and denial constraints together. |
| [Open-World Certain Answers Complexity](./open-world-certain-answers.md) | partially-solved | Settle data/combined complexity of certain answers under open-world assumption for query+constraint classes. |
| [Provenance Semirings for Recursive Queries](./provenance-semiring-recursion.md) | partially-solved | Extend semiring provenance soundly and finitely to recursive (Datalog) and aggregate queries. |
| [Relational Algebra Equivalence with Aggregation](./algebra-equivalence-aggregation.md) | open | Decide equivalence of relational-algebra expressions extended with grouping/aggregation. |
| [Tight Chase-Based Containment Algorithms](./chase-containment-algorithms.md) | solved-but-impractical | Make chase-and-backchase containment checking practical at engine scale. |
| [Counting and Enumeration Complexity of CQs](./cq-counting-enumeration.md) | partially-solved | Classify CQs by tractable counting and constant-delay enumeration of answers. |
| [Inclusion Dependencies and Acyclicity Interaction](./inclusion-dependencies-acyclicity.md) | partially-solved | Characterize decidability of implication for inclusion dependencies combined with FDs. |
| [Normalization Beyond Fourth/Fifth Normal Form](./normalization-beyond-4nf-5nf.md) | open | Decide and synthesize schemas in dependency-preserving normal forms beyond 4NF/5NF/DKNF. |
| [Dependency-Driven Schema Synthesis Complexity](./schema-synthesis-complexity.md) | partially-solved | Determine the complexity of synthesizing lossless, dependency-preserving decompositions. |
| [Cardinality Constraints in the Chase](./cardinality-constraints-chase.md) | open | Incorporate numeric cardinality/counting constraints into chase-based reasoning. |
| [Probabilistic Database Dependency Theory](./probabilistic-dependencies.md) | partially-solved | Develop a dependency/implication theory for probabilistic and uncertain relational data. |
| [Order Dependencies and Their Implication](./order-dependencies-implication.md) | partially-solved | Axiomatize and decide implication for order/sequential dependencies and exploit them in optimization. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
