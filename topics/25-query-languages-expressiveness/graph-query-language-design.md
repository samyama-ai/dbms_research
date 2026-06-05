# Expressiveness and Design of Graph Query Languages

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/graph-query-language-design` · **Status:** open

## 1. Problem Statement
Establish a principled, well-understood foundation for property-graph and RDF query languages (**GQL**, **Cypher**, **SPARQL**, SQL/PGQ, Gremlin): (i) determine their **exact expressive power** relative to logics and algebras; (ii) place fragments in a clean **hierarchy**; and (iii) design a **principled core** with predictable semantics and complexity. Concretely:

- What can each language express vs. **FO**, **Datalog**, **transitive closure logic (FO+TC)**, **fixpoint logics**, **first-order with counting (FOC)**?
- Which combinations of features (path patterns, path modes, aggregation, list/path values, recursion via `WITH`/views, subqueries) yield decidable static analysis and tractable evaluation?
- Can we factor the languages into an **orthogonal core + extensions** with a clean denotational semantics (the analogue of relational algebra for graphs)?

This is **open**: the standards fix syntax, but a complete, agreed expressiveness theory and a canonical core algebra do not yet exist.

## 2. Mathematical Foundations
The yardsticks are classical: **FO** captures relational algebra; **regular path queries** add navigational recursion (a restricted transitive closure); **CRPQ/UCRPQ** form a robust navigational core; adding path/output features pushes toward **FO+TC**, **monadic second-order (MSO)** over paths, or **Datalog**. **Expressive completeness** results characterize a language as exactly some logic on graph structures.

Key formal devices: **Ehrenfeucht–Fraïssé games** and **locality** (Gaifman/Hanf) for inexpressibility (e.g., transitive closure $\notin$ FO); **bisimulation**-invariance for navigational fragments (graph XPath/PDL-style languages capture the bisimulation-invariant fragment of FO/MSO, akin to van Benthem/Janin–Walukiewicz); and **descriptive complexity** (FO+LFP = PTIME on ordered structures, Immerman–Vardi) to align expressiveness with complexity classes. A graph **relational algebra** must close over path values, lists, and grouping while keeping these characterizations.

## 3. State of the Art (SOTA)
- **Foundations of graph languages** (Angles–Arenas–Barceló–Hogan–Reutter–Vrgoč, CSUR 2017) give the reference expressiveness map for RPQ/CRPQ/UCRPQ and their two-way/regular extensions.
- **Cypher formal semantics** (Francis et al., SIGMOD 2018) provides the first rigorous denotational semantics of a commercial language.
- **GQL & SQL/PGQ** (ISO, 2023–2024; Francis et al. SIGMOD 2023) standardize property-graph pattern matching, path modes, and composition.
- Results placing fragments w.r.t. **FO, FO+TC, Datalog, MSO**, and identifying **navigational cores** (Libkin, Martens, Reutter, Vansummeren) and **bisimulation-invariant** characterizations of XPath-like graph languages.

## 4. Upper Bound
- **Data complexity:** UCRPQ and most navigational cores are evaluable in **NLOGSPACE/PTIME**; the regular-path core sits in NL.
- **Combined complexity:** CRPQ/UCRPQ is **NP-complete** (CQ-like joins) or **PSPACE** with full two-way/regular features.
- Languages restricted to bisimulation-invariant navigation enjoy **PTIME** evaluation and decidable static analysis. A "**GQL core**" that stays within FO+TC retains these favorable bounds; aggregation and arithmetic raise complexity toward that of SQL with recursion.

## 5. Lower Bound
- **Inexpressibility:** transitive closure / reachability is **not FO-definable** (EF-game / locality), justifying built-in path recursion.
- Full GQL/SPARQL with general recursion (`WITH RECURSIVE`, SPARQL 1.1 features) reaches **Turing-completeness** or **Datalog-hard** static analysis; **query containment/equivalence becomes undecidable** for sufficiently rich fragments (cf. Datalog⊑Datalog).
- SPARQL with `OPTIONAL` (well-designed vs. general) has **PSPACE-complete** combined complexity (Pérez–Arenas–Gutierrez 2009); general patterns are PSPACE-hard.

## 6. The Gap
There is **no settled, complete expressiveness hierarchy** for the *full* standardized languages (with path modes, lists, aggregation, composition) and **no canonical core algebra** with the role relational algebra plays for SQL. Open: exact logical characterizations of GQL's **path-mode** semantics (trail/simple/shortest), the expressive cost of **path/list values as first-class data**, and where decidable static analysis ends. Closing the gap needs new logics over *path-valued* structures and matching games/locality tools.

## 7. Current Research (as of June 2026)
Active work formalizes **GQL/SQL/PGQ semantics**, defines **graph algebras** closed over paths and groupings, and maps fragments to FO+TC, Datalog, and counting logics. Strong activity on **composability** (graph-to-graph queries, views) and on **path-mode expressiveness**. *(frontier — verify)* Several 2024–2026 papers give denotational semantics and complexity for GQL's pattern-matching core and study **bag/list semantics** and **regular path with data values**. Groups/people: Libkin, Martens, Vansummeren, Reutter, Barceló, Hogan, Arenas, Francis, Bonifati, and the **LDBC** and ISO/GQL communities.

## 8. Future Work
- A canonical **graph relational algebra** (path-closed) and its expressive-completeness theorem.
- Exact logical characterizations of **path modes** and first-class path/list values.
- Decidability frontier for static analysis (containment/equivalence) of GQL fragments.
- Unifying property-graph and RDF semantics; expressiveness of **schema/SHACL**-aware querying; counting and aggregation extensions with clean complexity.

## 9. Key References
- **[Survey]** R. Angles, M. Arenas, P. Barceló, A. Hogan, J. Reutter, D. Vrgoč. *Foundations of modern query languages for graph databases.* ACM Computing Surveys, 2017. — [DOI](https://doi.org/10.1145/3104031)
- **[Foundational]** N. Francis et al. *Cypher: An evolving query language for property graphs.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3190657)
- **[SOTA]** N. Francis et al. *GQL and SQL/PGQ: The ISO standards for property graph querying.* SIGMOD, 2023. — [DBLP search](https://dblp.org/search?q=GQL+and+SQL%2FPGQ+The+ISO+Standards+for+Property+Graph+Querying)
- **[Foundational]** J. Pérez, M. Arenas, C. Gutierrez. *Semantics and complexity of SPARQL.* ACM TODS, 2009. — [DOI](https://doi.org/10.1145/1567274.1567278)
- **[Foundational]** L. Libkin. *Elements of Finite Model Theory.* Springer, 2004. — [DOI](https://doi.org/10.1007/978-3-662-07003-1)
- **[Survey]** P. Barceló. *Querying graph databases.* PODS, 2013. — [ACM](https://doi.org/10.1145/2463664.2465216)

## 10. Worked Example

**A CRPQ and the path-mode subtlety.** Take a property graph of flights, edges labelled $\mathsf{flight}$:
$$\mathsf{LAX}\xrightarrow{\mathsf{flight}}\mathsf{DEN}\xrightarrow{\mathsf{flight}}\mathsf{ORD}\xrightarrow{\mathsf{flight}}\mathsf{LAX}.$$
The regular-path query "reachable from $\mathsf{LAX}$ by one or more flights" is the RPQ
$$Q(y)\;=\;(\mathsf{LAX})\;\xrightarrow{\;\mathsf{flight}^+\;}\;(y),$$
a transitive closure not expressible in plain FO. Its answer is $\{\mathsf{DEN},\mathsf{ORD},\mathsf{LAX}\}$ — under **arbitrary-walk** semantics $\mathsf{LAX}$ is included via the 3-cycle.

**Path modes change the answer set, and the complexity.** Now ask for *simple paths* (no repeated vertex). The walk $\mathsf{LAX}\to\mathsf{DEN}\to\mathsf{ORD}\to\mathsf{LAX}$ is *not* simple, so under `SIMPLE`/`TRAIL` mode $\mathsf{LAX}$ may drop out of the answer. Crucially, evaluating "is there a *simple* path matching a regular expression?" is **NP-complete** in general (Mendelzon–Wood), whereas the arbitrary-walk RPQ is in **NL**. This jump — same syntax, different path mode — is exactly the kind of semantic cell that GQL/SQL-PGQ standardize but for which a complete expressiveness/complexity map is still open.

---
*Part of the [DBMS Research catalog](../../README.md).*
