# Property-graph schema and constraint theory

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/property-graph-schema-theory` · **Status:** open

## 1. Problem Statement
Develop a **principled, complete theory of schemas, keys, and integrity constraints for property graphs** — comparable in maturity to the relational schema/constraint theory — that supports:
- **Schema definition:** node/edge type systems, property typings, cardinalities, and mandatory/optional structure, where data may be *schema-flexible* (open) or *schema-fixed* (closed).
- **Constraint specification:** keys, existence/participation constraints, type constraints, path/topological constraints.
- **Validation (decision):** does graph $G$ satisfy schema/constraint set $\Sigma$?
- **Inference / implication (decision):** does $\Sigma \models \sigma$? Is $\Sigma$ satisfiable/consistent?

The open problem is that property graphs lack a *single, agreed* formal model; SQL/PGQ and GQL standardized *queries* in 2023–24 but constraint theory remains fragmented across PG-Schema, ShEx/SHACL (RDF), and ad-hoc system features.

## 2. Mathematical Foundations
A property graph is $G=(V,E,\rho,\lambda,\sigma)$ where $\rho:E\to V\times V$, $\lambda$ assigns label *sets* to $V\cup E$, and $\sigma$ assigns property–value maps. Unlike relations, graphs are **second-order / semi-structured**: a node's "schema" is its label set plus realized properties, so constraints quantify over heterogeneous objects.

Key theoretical scaffolding:
- **Description Logics / SHACL semantics:** validation as model-checking against a shape language; complexity ranges P → NP → undefined depending on recursion and closure (Corman–Reutter–Savković on **recursive SHACL** undecidability of stratified semantics).
- **The chase and implication:** lifting **tuple- and equality-generating dependencies (tgds/egds)** to graphs; implication via chase termination, generally undecidable for general tgds, decidable for guarded/weakly-acyclic fragments (Fagin–Kolaitis–Miller–Popa; Deutsch–Nash–Remmel).
- **Graph keys:** Fan–Fan–Tian–Bohannon **GKeys** define key by a graph pattern + value equalities; key satisfaction reduces to **subgraph isomorphism**, hence validation is generally **NP-hard** combined complexity.
- **Type systems:** PG-Schema (Angles et al.) gives content/structural types with *open* and *closed* semantics, formalized via formulas over label sets.

## 3. State of the Art (SOTA)
- **PG-Schema** (Angles, Bonifati, Dumbrava, Fletcher, Hidders, … SIGMOD 2023) — the leading academic proposal for property-graph schemas with keys; basis for GQL schema features.
- **PG-Keys** (Angles et al., SIGMOD 2021) — a key-language design space (identifier/exclusive/mandatory keys).
- **GQL (ISO/IEC 39075:2024)** and **SQL/PGQ (SQL:2023)** — standardized graph type/schema constructs, though constraint coverage is partial.
- **SHACL / ShEx** (W3C) — mature *RDF* validation; closest deployed constraint theory, with known recursion/decidability subtleties.
- **GKeys / functional dependencies for graphs** (Fan et al., VLDB 2015–2019) — keys and entity resolution via patterns.

## 4. Upper Bound
- **Validation:** for non-recursive shape/key constraints, validation is in **PTIME data complexity**; with pattern-based keys it is **NP-complete combined** (subgraph iso), PTIME data.
- **Implication:** decidable in coNP/EXPTIME for restricted, well-behaved fragments (guarded tgds, FO-expressible shapes); chase-based decision procedures terminate for weakly-acyclic constraint sets.
- **SHACL (non-recursive):** validation NP-complete combined, PTIME for tractable shape fragments.

## 5. Lower Bound
- **Pattern-based key validation:** NP-hard (subgraph isomorphism) combined complexity.
- **Recursive SHACL / general shapes:** satisfiability and implication are **undecidable** under several natural semantics (Corman, Reutter, Savković, ISWC 2018).
- **General tgd implication on graphs:** **undecidable** (inherits relational undecidability of the implication problem for arbitrary embedded dependencies, Beeri–Vardi).
- **Schema validation with closed types + recursion:** $\Pi$-complete / undecidable depending on quantifier alternation.

## 6. The Gap
There is **no canonical model**, so "the" upper/lower bounds depend on which formalism one adopts — the field has not converged. Relational theory has Codd's normal forms, Armstrong's axioms, and a complete implication theory; property graphs have *competing* partial theories (PG-Schema, SHACL, GKeys) with no unifying axiomatization, no sound-and-complete inference system covering keys + topology + properties jointly, and unsettled open/closed-world semantics. The open problem is **foundational unification**: a single calculus with decidable, well-characterized validation and implication.

## 7. Current Research (as of June 2026)
- Standardizing schema/constraints inside **GQL** (post-2024 amendments) — keys, cardinalities, mandatory properties *(frontier — verify)*.
- Decidable fragments of recursive SHACL and their PG-Schema analogues.
- Combining **PG-Schema + PG-Keys** into one inference system with a chase-style procedure *(frontier — verify)*.
- Groups: LDBC schema working group; Bonifati (Lyon), Hidders/Fletcher (Eindhoven), Reutter/Arenas (IMFD Chile), Martens (Bayreuth), Fan (Edinburgh).

## 8. Future Work
- A sound-and-complete axiomatization (Armstrong-style) for graph keys + dependencies.
- Decidability map for implication across open/closed, recursive/non-recursive shapes.
- Schema inference/extraction from instance graphs with statistical guarantees.
- Reconciling RDF (SHACL) and property-graph constraint theories.

## 9. Key References
- **[Foundational]** Codd, E. F. *Further Normalization of the Data Base Relational Model.* IBM Research Report RJ909, 1971. — [DBLP](https://dblp.org/rec/persons/Codd71a.html)
- **[Foundational]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[SOTA]** Angles, R., Bonifati, A., Dumbrava, S., Fletcher, G., Hidders, J., et al. *PG-Schema: Schemas for Property Graphs.* SIGMOD 2023. — [arXiv](https://arxiv.org/abs/2211.10962) · [DOI](https://doi.org/10.1145/3589778)
- **[SOTA]** Angles, R., et al. *PG-Keys: Keys for Property Graphs.* SIGMOD 2021. — [DOI](https://doi.org/10.1145/3448016.3457561)
- **[SOTA]** Fan, W., Fan, Z., Tian, C., Dong, X. L. *Keys for Graphs.* VLDB 2015. — [DOI](https://doi.org/10.14778/2824032.2824056)
- **[Lower bound]** Corman, J., Reutter, J., Savković, O. *Semantics and Validation of Recursive SHACL.* ISWC 2018. — [DOI](https://doi.org/10.1007/978-3-030-00671-6_19)
- **[Survey]** Bonifati, A., Fletcher, G., Voigt, H., Yakovets, N. *Querying Graphs.* Morgan & Claypool Synthesis Lectures, 2018. — [DBLP](https://dblp.org/rec/series/synthesis/2018Bonifati.html)

## 10. Worked Example

Consider a property graph of a publication DB with node label `Person` (properties `name`, `email`) and `Paper`, plus `AUTHORED` edges. We want a **graph key**: "a `Person` is identified by their `email`."

**Relational-style key** would just be `email` $\to$ tuple. But a *GKey* (Fan et al.) is a graph pattern + value equalities. Take the pattern $K$: a `Person` node $x$ with property `email = e`. Key satisfaction asks: are there two distinct `Person` nodes $v_1 \ne v_2$ that both match $K$ with the same $e$? Checking this requires finding embeddings of $K$ — i.e., **subgraph isomorphism** — so validation is NP-hard in *combined* complexity, though for this fixed, single-node pattern it is PTIME in data complexity (a single grouping scan over `email`).

Now make the key topological: "a `Review` is identified by `(its Paper, its Reviewer)`." The pattern has 3 nodes and 2 edges; validating it scans for two `Review` nodes sharing both neighbors — still subgraph-iso matching, NP-hard combined.

**Implication:** does $\{$email-key on `Person`$\} \models \{$email-key on `Author` (a subtype)$\}$? Under PG-Schema's *closed*-type semantics with subtyping this can be decided via the type lattice; add recursive SHACL-style shapes referencing each other and satisfiability becomes **undecidable** (Corman–Reutter–Savković) — exactly the fragmentation the open problem targets: no single calculus yet covers keys + topology + recursion with decidable implication.

---
*Part of the [DBMS Research catalog](../../README.md).*
