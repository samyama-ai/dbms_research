# Semantic equivalence of model encodings

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/model-encoding-equivalence` · **Status:** open

## 1. Problem Statement
Multi-model systems represent "the same" data in different models: a relation can be shredded into JSON documents, a JSON document can be stored as adjacency-list graph triples, a graph can be encoded relationally (edge tables) or as nested documents, RDF can be stored as property tables, etc. Given two encodings $E_1: D \to R_1$ and $E_2: D \to R_2$ of source data $D$ into different models, decide when they are **information-preserving** (lossless — $D$ is recoverable) and **query-equivalent** (every query in a target language over one can be faithfully simulated over the other).

Variants:
- **Information preservation (decision):** is there a computable inverse, i.e., is $E$ injective up to the intended identity (an *exact/lossless mapping*)?
- **Query equivalence (decision):** for a query language $\mathcal{L}$, does there exist a translation $\tau$ such that $Q(E_1(D)) \equiv \tau(Q)(E_2(D))$ for all $D$? (A *relative-information-capacity* / dominance question.)
- **Optimization:** among equivalent encodings, choose one minimizing query/storage cost — links to physical design.

This is the formal core under "schema/model mapping," "data exchange," and "ontology-based data access," but cross-*model* (relational↔document↔graph) equivalence with full query languages is open.

## 2. Mathematical Foundations
- **Information capacity / schema dominance** (Hull 1986; Miller–Ioannidis–Ramakrishnan): a schema $S_1$ has greater-or-equal *information capacity* than $S_2$ if there's a total injective "information-preserving" mapping; *equivalence* is mutual dominance. Hull defined a hierarchy (absolute, internal, query, calculous equivalence). These notions give the right yardstick for "information-preserving."
- **Data exchange & the chase** (Fagin–Kolaitis–Miller–Popa 2005): schema mappings as source-to-target tuple-generating dependencies (s-t tgds); a *universal solution* (computed by the chase) certifies that the target carries all and only the source's certain information; *invertibility* of mappings (Fagin's inverse, quasi-inverse) formalizes recoverability.
- **Bisimulation / structural equivalence:** graph and tree encodings are compared up to bisimulation; two graph encodings are query-equivalent for modal/navigational languages iff bisimilar.
- **Relative expressiveness / query simulation:** equivalence of encodings under a language $\mathcal{L}$ reduces to existence of a *language-preserving translation*, i.e., a question of relative expressive power and of *certain-answer* preservation (Abiteboul–Hull–Vianu foundations).
- Decidability typically hinges on the dependency class: equivalence/implication of general embedded dependencies is **undecidable**; weakly-acyclic mappings make the chase terminate and many questions decidable.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** schema-mapping theory (Fagin–Kolaitis–Miller–Popa; Fagin's *inverses of schema mappings*), information-capacity equivalence (Hull, Miller et al.), and the **chase & backchase** give complete machinery for *relational-to-relational* lossless/equivalence decisions in restricted (weakly-acyclic, GLAV) classes. Cross-model treatments exist for relational↔XML (shredding correctness) and relational↔RDF (R2RML, *Ultrawrap*, ontology-based data access with PerfectRef/combined rewriting).
- **Systems-SOTA:** R2RML/RML mappings, Apache Calcite/Drill cross-model views, Cosmos DB's multi-API (same data via SQL/Mongo/Gremlin), AgensGraph and other relational-graph bridges, and JSON-shredding/`json_table` in SQL engines implement specific encodings — but typically *without* a verified equivalence/losslessness certificate across models.

## 4. Upper Bound
For **relational schema mappings in well-behaved classes** (weakly-acyclic GLAV s-t tgds), a universal solution and inverse (when one exists) are computable by the **chase in PTIME (data complexity)**; checking that a candidate mapping is information-preserving / that a query rewriting is equivalent is decidable, with the *equivalence of mappings* in such classes decidable (often in NP/$\Pi_2^p$ for combined complexity). For **navigational/graph encodings**, bisimulation-based equivalence is checkable in near-linear time (Paige–Tarjan). These bounds hold for the restricted classes; the general cross-model, full-language case has no known finite procedure.

## 5. Lower Bound
- **Implication and equivalence of general (embedded) dependencies is undecidable** (Beeri–Vardi); since lossless/equivalent encodings are stated via such dependencies, the unrestricted decision problem is **undecidable**.
- **Query equivalence/containment** is already undecidable for relational calculus (FO) and for Datalog (Shmueli); even containment of conjunctive queries is **NP-complete** (Chandra–Merlin) — so checking query-equivalence of two encodings is at least NP-hard and rises to undecidable as the language grows.
- **Determinacy → rewriting:** whether a query is determined by a set of views (needed to know an encoding suffices to answer a query) is **undecidable** in general (Nash–Segoufin–Vianu), even when a rewriting would exist.

## 6. The Gap
The relational, restricted-dependency-class corner is **closed** (chase-based decision procedures with matching complexity). The genuinely **open** territory is *cross-model* equivalence with *expressive* query languages: there is no general decidable theory stating when a document encoding and a graph encoding of the same data are query-equivalent for, say, full SQL/JSON path versus a regular-path-query graph language. The gap is partly *undecidability* (must be carved into decidable fragments) and partly *missing definitions* — "query-equivalent across models" needs a canonical cross-model query semantics to even state. Closing it means (a) identifying maximal decidable cross-model mapping fragments and (b) tight complexity for equivalence/losslessness within them.

## 7. Current Research (as of June 2026)
- Unified multi-model query semantics and "category-theoretic" data integration (Spivak/Schultz functorial data migration, the CQL tool) aim to make cross-model mappings compositional and their equivalence checkable *(frontier — verify which equivalence questions CQL-style tools decide vs. only execute)*.
- Ontology-based data access and graph-relational rewriting (Calvanese, Xiao et al.) continue to extend decidable lossless-mapping fragments.
- Multi-model formal foundations (Lu–Holubová's multi-model survey lineage) and verified shredding/encodings are active in the PODS/ICDT community.

## 8. Future Work
- A decidable **cross-model equivalence calculus** spanning relational, document (nested), and graph encodings with explicit fragment boundaries.
- Certified, verifiable losslessness for production encoders (shredders, R2RML-like graph mappings) — proof-carrying mappings.
- Cost-aware *choice* among equivalent encodings (tie to physical design / data placement).
- Equivalence up to *certain answers* under incomplete/heterogeneous data.

## 9. Key References
- **[Foundational]** R. Hull. *Relative Information Capacity of Simple Relational Database Schemata.* SIAM J. Computing / PODS, 1986.
- **[Foundational]** R. Fagin, P. Kolaitis, R. J. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* TCS / ICDT, 2005.
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977.
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995.
- **[Foundational]** A. Nash, L. Segoufin, V. Vianu. *Views and Queries: Determinacy and Rewriting.* PODS / TODS, 2010.
- **[SOTA]** R. Fagin. *Inverting Schema Mappings.* PODS / TODS, 2007.
- **[Survey]** J. Lu, I. Holubová. *Multi-model Databases: A New Journey to Handle the Variety of Data.* ACM Computing Surveys, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
