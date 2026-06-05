# Polymorphic and Schema-Independent Query Languages

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/schema-independent-queries` · **Status:** open

## 1. Problem Statement
A query should arguably express a property of the *data* itself, not of the accidental way it is laid out in a schema. **Schema-independent (a.k.a. polymorphic, representation-independent, or "genericity-respecting") query languages** are those whose queries return the same logical answer when the database is re-encoded by a *meaning-preserving* schema transformation — e.g., relational $\leftrightarrow$ key/value, horizontal/vertical partitioning, EAV (entity–attribute–value) pivoting, normalization/denormalization, RDF triple-folding, or column-to-row reshaping.

Variants:
- **Design:** Construct a language $L$ and an equivalence $\equiv$ on databases (a schema-transformation group/groupoid $G$) such that every $q \in L$ is **$G$-invariant**: $D_1 \equiv_G D_2 \Rightarrow q(D_1)$ and $q(D_2)$ are corresponding under the induced transformation.
- **Characterization:** Which classical query properties are exactly the $G$-invariant ones? (A "genericity theorem" for schema transformations, analogous to genericity under domain permutations.)
- **Decision problems:** Given $q$, decide whether $q$ is schema-independent w.r.t. a class of transformations; decide equivalence of two queries up to $G$.

## 2. Mathematical Foundations
Classical **genericity** (Aho–Ullman; Chandra–Harel): a query $q$ is generic if it commutes with every permutation $\pi$ of the data domain, $q(\pi D) = \pi q(D)$ (C-genericity allows fixing constants $C$). FO and the relational-complete languages are generic; this is the canonical invariance property of relational query languages.

Schema-independence generalizes the acting group from *domain* permutations to *structural* transformations. Formalisms:
- **Information capacity & schema mappings:** Hull's information-capacity preorders; **GLAV/st-tgd schema mappings** and the chase (Fagin–Kolaitis–Miller–Popa) formalize when one schema can faithfully represent another, with **inverses** and **quasi-inverses** (Fagin et al.) capturing reversibility.
- **Bidirectional transformations / lenses** (Foster et al.): well-behaved lenses give round-tripping laws (GetPut, PutGet) — an algebraic model of representation-independent access.
- **Category theory / functorial data migration** (Spivak; Schultz–Wisnesky): schemas as categories, instances as functors $C \to \mathbf{Set}$, migrations as $\Delta, \Sigma, \Pi$ functors; a query is schema-independent if it is **natural** w.r.t. these functors.
- **Topological / continuous queries** (Gottlob et al.): queries invariant under representation refinement.

Notation: let $T: \mathsf{Inst}(S_1) \to \mathsf{Inst}(S_2)$ be an invertible mapping with inverse $T^{-1}$; $q$ is $T$-independent iff $q_{S_2}\circ T = T_q \circ q_{S_1}$ for the induced answer translation $T_q$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** *Genericity* and **BP-completeness** results (Chandra–Harel, Bancilhon–Paredaens) characterize relational-complete generic queries. **Functorial data migration** and **CQL** (Categorical Query Language, Schultz–Wisnesky, SIGMOD/PODS 2010s–2020s) give a working language where migrations are first-class and certain queries are migration-invariant by construction.
- **Systems-SOTA:** Multi-model and **virtual/federated** systems (e.g., schema-agnostic JSON querying, SQL/JSON, GraphQL resolvers, RDF/SPARQL over relational via R2RML) approximate schema independence operationally; **lens-based** bidirectional tools (Boomerang) realize round-tripping. No mainstream system offers a provable schema-independence guarantee.

## 4. Upper Bound
For restricted transformation classes (pivot/unpivot, normalization given a fixed FD set), checking schema-independence of a **conjunctive query** reduces to query-equivalence-under-constraints and is **NP-complete** (via the chase + homomorphism test) when the constraints form a terminating (weakly acyclic) set. Functorial migrations $\Delta,\Sigma,\Pi$ give a *constructive* upper bound: any query expressed purely in these functors is automatically migration-invariant, evaluable in PTIME data complexity for the conjunctive fragment.

## 5. Lower Bound
Deciding invariance under an *arbitrary* class of schema mappings is **undecidable**: equivalence of GLAV mappings and of queries under tuple-generating dependencies is undecidable in general (the chase need not terminate; implication of TGDs is undecidable, Beeri–Vardi). Even invertibility of a schema mapping (does an exact/quasi-inverse exist?) is co-NP-hard / undecidable depending on the class (Fagin et al.). Thus the general design problem inherits the undecidability of dependency implication.

## 6. The Gap
We have (a) a clean genericity theory for *domain* permutations and (b) a constructive but partial categorical account, but **no genericity theorem for the full lattice of practical schema transformations** (EAV, denormalization, graph/triple foldings) — i.e., no exact characterization "query $q$ is schema-independent iff $q$ is expressible in fragment $F$." The gap between the decidable conjunctive/weakly-acyclic island and the undecidable general case is genuinely open, and no language is known to be *complete* for the schema-independent queries.

## 7. Current Research (as of June 2026)
- **Categorical / functorial query languages** (Wisnesky, Spivak, Brown): pushing CQL toward practical multi-model migration with invariance guarantees *(frontier — verify maturity of invariance-by-construction claims)*.
- **Schema-agnostic and self-describing data** querying (Polystore/ tensor-relational), and LLM-mediated schema matching where representation-independence is a correctness target.
- Revived interest in **information-capacity preservation** for lakehouse "open table format" migrations (Iceberg/Delta schema evolution) with formal invariance.

## 8. Future Work
- A genericity theorem covering EAV/pivot/graph foldings with an exact language characterization.
- Decidable, expressive transformation classes with a usable invariance-checking algorithm.
- Integrating bidirectional lenses with query optimization so plans are provably representation-stable.

## 9. Key References
- **[Foundational]** A. Chandra, D. Harel. *Computable Queries for Relational Data Bases.* JCSS, 1980. — [DOI](https://doi.org/10.1016/0022-0000(80)90032-X)
- **[Foundational]** F. Bancilhon. *On the Completeness of Query Languages for Relational Data Bases.* MFCS, 1978; J. Paredaens, *On the Expressive Power of the Relational Algebra*, IPL, 1978. — [DOI](https://doi.org/10.1016/0020-0190(78)90055-8)
- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Quasi-Inverses of Schema Mappings.* ACM TODS, 2008. — [DBLP](https://dblp.org/rec/journals/tods/FaginKPT08.html)
- **[SOTA]** P. Schultz, R. Wisnesky. *Algebraic Data Integration.* J. Functional Programming, 2017 (Categorical Query Language / CQL). — [arXiv](https://arxiv.org/abs/1503.03571)
- **[SOTA]** D. Spivak, R. Wisnesky. *Relational Foundations for Functorial Data Migration.* DBPL, 2015. — [arXiv](https://arxiv.org/abs/1212.5303)
- **[Foundational]** J. N. Foster et al. *Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.* ACM TOPLAS, 2007. — [DOI](https://doi.org/10.1145/1232420.1232424)

## 10. Worked Example

Take an **EAV pivot**, the canonical schema transformation. Encoding $S_1$ stores a wide relation $\mathsf{Emp}(\underline{id}, name, dept)$:

| id | name | dept |
|----|------|------|
| 1 | Ann | Sales |
| 2 | Bob | Eng |

Encoding $S_2$ stores the same information as triples $\mathsf{EAV}(\underline{id, attr}, val)$:

| id | attr | val |
|----|------|-----|
| 1 | name | Ann |
| 1 | dept | Sales |
| 2 | name | Bob |
| 2 | dept | Eng |

The transformation $T$ is invertible: unpivot recovers $\mathsf{EAV}$, and a pivot (group by $id$, spread $attr\!\to\!val$) recovers $\mathsf{Emp}$, so $D_1 \equiv_G D_2$.

Now the query "*ids in dept Sales*". Over $S_1$: $\sigma_{dept=\text{Sales}}\,\mathsf{Emp}$ projected to $id$ gives $\{1\}$. Over $S_2$ the *same* logical query must be phrased $\pi_{id}\,\sigma_{attr=\text{dept}\,\wedge\,val=\text{Sales}}\,\mathsf{EAV}$, again $\{1\}$ — answers correspond under $T_q=\mathrm{id}$, so the query is **schema-independent** here.

But "*return the whole tuple*" is **not**: $S_1$ yields one 3-arity row, $S_2$ yields two 3-arity triples — different shapes, no answer-translation $T_q$ makes them correspond. This shows genericity is property-by-property, motivating the search for a fragment $F$ capturing *exactly* the $G$-invariant queries.

---
*Part of the [DBMS Research catalog](../../README.md).*
