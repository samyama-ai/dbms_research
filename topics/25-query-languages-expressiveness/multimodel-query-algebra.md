# Unified Algebra for Multi-Model and Polystore Queries

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/multimodel-query-algebra` · **Status:** empirically-open

## 1. Problem Statement
Modern data lives across **multiple models**—relational tables, JSON/XML documents, property/RDF graphs, key–value, wide-column, and dense **tensor/array** data—served by heterogeneous stores (a **polystore**). The problem is to design a single **compositional algebra** $\mathcal{A}$ with a well-defined semantics and an **expressiveness theory** that (a) subsumes relational algebra, document/path algebras, graph pattern matching, and linear/tensor algebra; (b) supports cross-model operators (join a graph traversal to a table to a tensor) with cost-based optimization; and (c) admits formal results on relative expressive power and closure.

Variants:
- **Design:** a closed algebra with a typed data model unifying these structures.
- **Expressiveness/separation:** characterize the algebra against FO, fixpoint logic (graph reachability/recursion), and linear algebra over a semiring (matrix algebra is *not* FO-expressible in general).
- **Optimization/decision:** equivalence, containment, and cost-based rewriting across models; pushdown decidability into heterogeneous engines.

## 2. Mathematical Foundations
Each model has a native algebra: **relational algebra** (FO-complete for the set fragment), **regular path queries / graph pattern matching** (needs transitive closure — beyond FO, captured by fixpoint logics / nested regular expressions; standardized in **GQL** and SQL/PGQ, 2024), **document/path** algebras (XPath/JSONPath, tree/forest algebra), and **linear/tensor algebra (LA)** over a semiring (matrix multiply, einsum), whose expressiveness vs. relational algebra is itself a research subject (LARA, MATLANG).

Unifying foundations:
- **Semiring / $K$-relations** (Green–Tannen): a common annotation framework letting one algebra carry set, bag, probabilistic, and provenance semantics; many models are functors over a semiring.
- **MATLANG / LARA** (Brijder et al.; Hutchison–Howe–Suciu): a matrix/linear-algebra query language and **Lara** as an associative-table algebra bridging relational and linear algebra; results pin the expressive power of LA relative to FO with aggregation.
- **Monad / comprehension calculi** (Buneman–Naqvi–Tannen–Wong; **monoid comprehension calculus**, Fegaras–Maier) provide a *nested-collection* algebra (bags/lists/sets/trees as monads) that already unifies several models compositionally — a strong starting point.
- **Category theory / functorial integration** (Spivak–Wisnesky) for cross-model schema mappings.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The **monoid/monad comprehension calculus** and nested relational algebra give a principled compositional core for collections and documents. **MATLANG/Lara** results characterize linear algebra's expressiveness (e.g., MATLANG = FO with aggregation under restrictions; matrix inverse/eigen ops add power). Semiring provenance unifies annotations across models. Standards **SQL/PGQ + GQL (ISO, 2024)** formalize graph patterns alongside SQL.
- **Systems-SOTA:** **BigDAWG** (MIT, polystore with "islands" of query languages, VLDB 2015–17), **Myria**, **Apache Calcite** (unified relational IR + adapters), **AsterixDB / SQL++** (Ong–Papakonstantinou: a superset semantics over JSON+relational), **DuckDB/Velox/Substrait** (a cross-engine algebra IR), **TensorFlow/Relational** hybrids, and graph+SQL engines (Neo4j, TigerGraph, DuckPGQ). None offers a *proven* unified expressiveness theory across all four models.

## 4. Upper Bound
**SQL++ / the nested-relational + comprehension core** is closed and evaluable in PTIME data complexity for the non-recursive fragment, and provides a *constructive* upper bound: any query expressible in the monoid comprehension calculus has a compositional translation to nested-loop/algebraic plans. **Substrait/Calcite** demonstrate a practical relational-plus IR that compiles to multiple back-ends. For linear-algebra fragments, MATLANG queries reduce to a bounded number of FO-with-aggregation passes (PTIME), and worst-case-optimal join + tensor methods give optimal data-movement bounds for cross-model joins. Graph reachability adds **stratified fixpoint** (PTIME-complete) on top.

## 5. Lower Bound
There is a fundamental **expressiveness barrier**: transitive closure / reachability is **not FO-expressible** (Ehrenfeucht–Fraïssé / locality), so any purely relational-algebra core *cannot* subsume graph queries — recursion (fixpoint) is provably required, and evaluating recursive path queries is **PTIME-complete** (or NP-hard for simple-path semantics). **Matrix inversion / determinant** is not expressible in FO-with-aggregation (counting), giving a separation forcing genuine linear-algebra primitives. Cross-model **join optimization is NP-hard** (general join ordering), and polystore query equivalence inherits **undecidability** from relational calculus equivalence. Communication/IO lower bounds (the **AGM bound** and its tensor generalizations) bound cross-model join cost from below.

## 6. The Gap
No existing algebra is **proven** to (i) be closed and compositional across relational + document + graph + tensor *and* (ii) have a matching **expressiveness characterization** with separation theorems. Systems unify *engineering-wise* (Calcite, SQL++, Substrait) but lack a Codd-style completeness/expressiveness theorem spanning all models; theory results exist per-pair (relational↔LA, relational↔graph) but not for the full union. This is why the status is *empirically open*: workable systems exist, but the unifying theory and optimal cross-model optimization remain unresolved.

## 7. Current Research (as of June 2026)
- **Substrait** as a cross-engine algebraic IR and **Velox/DataFusion** convergence; pushing a community-standard plan algebra *(frontier — standardization in flux; verify coverage of graph/tensor)*.
- Expressiveness of **graph + relational** under the new **GQL/SQL-PGQ** standard; complexity of GQL pattern matching and its place in the FO/fixpoint hierarchy.
- **Tensor-relational** unification for ML pipelines (LARA successors, "in-database ML" algebras) and worst-case-optimal cross-model joins; semiring-based polystore optimization.

## 8. Future Work
- A proven compositional algebra with separation theorems across all four models and a clear recursion/linear-algebra boundary.
- Decidable optimization (equivalence/containment, pushdown) for useful multi-model fragments.
- Cost models with AGM-style optimality for genuinely cross-model joins and a unified provenance/semiring semantics.

## 9. Key References
- **[Foundational]** P. Buneman, L. Libkin, D. Suciu, V. Tannen, L. Wong. *Comprehension Syntax / Principles of Programming with Complex Objects and Collection Types.* (and Fegaras–Maier, *Optimizing Object Queries Using an Effective Calculus*, ACM TODS, 2000).
- **[Foundational]** E. F. Codd. *A Relational Model of Data for Large Shared Data Banks.* CACM, 1970.
- **[SOTA]** K. W. Ong, Y. Papakonstantinou, R. Vernoux. *The SQL++ Query Language: Configurable, Unifying and Semi-Structured.* arXiv:1405.3631, 2014 (AsterixDB).
- **[SOTA]** J. Duggan et al. *The BigDAWG Polystore System.* SIGMOD Record / VLDB, 2015.
- **[SOTA]** R. Brijder, F. Geerts, J. Van den Bussche, T. Weerwag. *On the Expressive Power of Query Languages for Matrices (MATLANG).* ACM TODS / ICDT, 2019.
- **[Foundational]** T. Green, V. Tannen. *The Semiring Framework for Database Provenance.* PODS, 2017 (and Green–Karvounarakis–Tannen, PODS 2007).
- **[SOTA]** A. Deutsch et al. *Graph Pattern Matching in GQL and SQL/PGQ.* SIGMOD, 2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
