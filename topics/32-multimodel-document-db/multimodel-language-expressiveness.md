# Expressiveness of multi-model query languages

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/multimodel-language-expressiveness` · **Status:** open

## 1. Problem Statement
Characterize the *relative expressive power* of the query languages used to interrogate multi-model data: SQL/JSON (the ISO `json_table`/`JSON_QUERY` family), GQL/Cypher (property graphs), AQL (ArangoDB), and the MongoDB aggregation pipeline. The goal is a formal map: which queries are expressible in each language, which separations are strict, and what a *unified core* would need to subsume all of them.

- **Containment/separation variant:** is language $L_1 \subseteq L_2$ (every $L_1$-query has an equivalent $L_2$-query)? Is the inclusion strict?
- **Capability variant:** which classic features — recursion/transitive closure, aggregation, grouping, nesting/unnesting, path navigation, ordering — does each support, and at what data-complexity?
- **Equivalence/decision variant:** given two queries (possibly cross-language), are they equivalent? (Generally undecidable for rich fragments.)

The challenge is that these languages live over *different data models* (relations-with-JSON, property graphs, document trees), so expressiveness must be compared via a common semantic domain and faithful encodings.

## 2. Mathematical Foundations
The yardstick is descriptive complexity and logic:
- **Relational core:** SQL ≈ relational algebra ≈ first-order logic $\mathrm{FO}$; with grouping/aggregation, $\mathrm{FO}(\mathrm{Count})$; recursive SQL / Datalog ≈ least-fixpoint logic $\mathrm{FO+LFP}$ ≈ PTIME on ordered structures (Immerman–Vardi).
- **Graph languages:** Cypher/GQL pattern matching corresponds to (unions of) conjunctive *regular path queries* (C2RPQ/UCRPQ); reachability needs **transitive closure**, expressible in $\mathrm{FO+TC}$ but *not* in pure $\mathrm{FO}$ (a classic inexpressibility result via locality/Ehrenfeucht–Fraïssé games). GQL formalization (Francis et al., PODS 2023) gives a denotational semantics.
- **Nested/document:** the right model is the **nested relational algebra / calculus (NRC)** and *monad comprehensions*; the conservativity theorem (Wong) shows NRC over flat I/O is no more expressive than flat relational algebra, but intermediate nesting matters for succinctness. MongoDB's pipeline is a fragment of NRC plus aggregation.
- Tools: Ehrenfeucht–Fraïssé games, locality (Gaifman/Hanf) for inexpressibility, and structural induction over operator semantics for inclusions.

## 3. State of the Art (SOTA)
- **GQL/Cypher:** formal semantics by Francis et al. (the "Cypher: An Evolving Query Language" SIGMOD 2018 paper) and the GQL/SQL-PGQ standard analyses (Francis, Green, Libkin, et al., PODS/SIGMOD 2023) pin graph-pattern expressiveness to C(2)RPQ-like classes.
- **SQL/JSON:** standardized in SQL:2016/2023; its expressiveness over JSON has partial formal treatment but no complete comparative map. *(There is a clean theory for JSONiq/JSONPath and for the W3C SPARQL/XQuery lineage.)*
- **Comparative multi-model:** survey-level treatments (Holubová, Svoboda et al.) catalog features; a *rigorous* expressiveness lattice across SQL/JSON, GQL, AQL, and MongoDB is **not** established. AQL and MongoDB's pipeline lack published formal semantics in the peer-reviewed literature.

## 4. Upper Bound
Known *containments*: the navigational core of GQL ⊆ $\mathrm{FO+TC}$ (≤ NLOGSPACE data complexity for RPQ reachability); SQL/JSON's non-recursive core ⊆ NRC ⊆ (by conservativity) relational algebra on flat I/O, hence within $\mathrm{FO}$ data complexity; MongoDB aggregation (no `$graphLookup` recursion) ⊆ $\mathrm{FO(Count)}$; with `$graphLookup`, it gains bounded transitive closure. These place upper bounds on what each language can compute but do not prove tightness against one another.

## 5. Lower Bound
Strict separations are *inexpressibility* results: reachability/transitive closure is **not** in $\mathrm{FO}$ (so non-recursive SQL/JSON and recursion-free pipelines cannot express graph connectivity), proven by locality / EF-games. Query *equivalence* and *containment* are **undecidable** for languages with arithmetic/aggregation (reduction from Diophantine/Datalog containment), and even C2RPQ containment is EXPSPACE-complete. These give hardness of the decision variant; full cross-language separation lower bounds (e.g., AQL vs. MongoDB pipeline) are largely unproven.

## 6. The Gap
We have a solid theory for the graph fragment (GQL ↔ C2RPQ ↔ $\mathrm{FO+TC}$) and for the relational/nested fragment (NRC, conservativity), but **no unified expressiveness lattice** that places SQL/JSON, GQL, AQL, and MongoDB on one semantic domain with proven strict separations. Closing it requires: (i) published formal semantics for AQL and the MongoDB pipeline, (ii) a common multi-model algebra, and (iii) separation proofs (which features are genuinely added by each). This is genuinely open.

## 7. Current Research (as of June 2026)
GQL/SQL-PGQ standardization and its formal analysis (Libkin, Francis, Green, Martens, Vrgoč) is the most active strand. *(frontier — verify)* Several groups are formalizing multi-model algebras and "one query language to rule them all" cores (e.g., work around MongoDB's semantics, ArangoDB's AQL, and unified document-graph calculi) in 2025–2026; results on expressiveness of `json_table`/SQL/JSON recursion and on schema-flexible NRC are emerging but not yet consolidated into a comparative theorem.

## 8. Future Work
A peer-reviewed denotational semantics for AQL and the MongoDB pipeline; a unified multi-model algebra with conservativity results; strict-separation proofs across the four languages; complexity classification of cross-model equivalence; a principled "minimal complete core" for multi-model querying.

## 9. Key References
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995.
- **[Foundational]** Libkin. *Elements of Finite Model Theory.* Springer, 2004 (locality, EF-games, inexpressibility).
- **[SOTA]** Francis, Green, Guagliardo, Libkin, Lindaaker, Marsault, Plantikow, Rydberg, Selmer, Taylor. *Cypher: An Evolving Query Language for Property Graphs.* SIGMOD, 2018.
- **[SOTA]** Francis, Gheerbrant, Guagliardo, Libkin, Marsault, Martens, Murlak, Peterfreund, Rogova, Vrgoč. *A Researcher's Digest of GQL.* ICDT, 2023.
- **[Foundational]** Buneman, Naqvi, Tannen, Wong. *Principles of Programming with Complex Objects and Collection Types (NRC).* Theoretical Computer Science, 1995.
- **[Survey]** Holubová, Svoboda, Lu. *Multi-Model Databases: A Survey.* (ACM Computing Surveys / DEXA tutorials), 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
