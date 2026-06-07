---
id: 15-data-integration/nested-data-exchange
title: "Nested/Hierarchical Data Exchange"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Nested/Hierarchical Data Exchange

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/nested-data-exchange` · **Status:** open

## 1. Problem Statement

Classical data exchange is defined over **flat relational** schemas. Modern integration targets **nested/hierarchical** data — JSON documents, XML, nested-relational and semi-structured schemas with **set/list constructors**, **referential constraints** (keys/keyrefs, foreign keys across nesting levels) and, for lists, **order constraints**. The problem: define and compute **certain answers** and a canonical **core universal solution** for data exchange where (i) the mapping language ranges over nested tuple-generating dependencies (nested TGDs / tree patterns), (ii) target dependencies include **nested keys, keyrefs, and order/position constraints**, and (iii) queries are nested-relational / XPath-XQuery / JSONPath-style with navigation, grouping, and (un)nesting.

Variants: **decision** (certain answer to a Boolean nested query); **materialization** (compute a minimal/core nested universal solution — the analog of the relational core); **counting/enumeration** of certain answers; and the **order-sensitive** variant where the target list order is partially constrained, making "certainty" a property over admissible orderings.

## 2. Mathematical Foundations

The flat baseline: solutions, universal solutions, and the **core** (Fagin–Kolaitis–Miller–Popa 2005; Fagin–Kolaitis–Popa 2005). Nesting is modeled by the **nested relational calculus/algebra (NRC)** and complex-value/tree data models (Abiteboul–Hull–Vianu; Buneman–Naqvi–Tannen–Wong for NRC). Mappings become **nested st-tgds** that mix existential quantification with **set/grouping** — Skolemized functions create nested structure (the **Clio** nested-mapping generation algorithm, Popa et al., VLDB 2002; Fuxman et al. on nested mappings, SIGMOD 2006).

Hard ingredients: (1) **set semantics + grouping** mean the "universal solution" must be canonical up to *deep* homomorphism and grouping equivalence, which is not a simple labeled-null structure; (2) **keys/keyrefs across levels** are EGD-like but scoped by nesting, so the chase must propagate equalities through tree contexts; (3) **order** turns the target into a *list*, so solutions form a set of admissible orderings and certain answers quantify over them — connecting to **order-preserving tree transductions** and to query answering over partially ordered XML (Arenas–Libkin's XML data exchange, PODS 2005).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** **XML data exchange** (Arenas, Libkin, ACM TODS 2008) settles certain answers for DTD-typed XML with tree-pattern mappings: certain answers for tree-pattern queries are decidable, with data complexity ranging from PTime to **coNP**-complete depending on the DTD class and presence of relative constraints. Nested relational mappings have a chase-and-core theory only partially developed.
- **Systems-SOTA.** **Clio** (IBM) and **++Spicy** generate and execute nested mappings to XML/nested targets; **Llunatic** handles EGDs; modern JSON integration uses **Morph-RDB**/**RML** and lakehouse JSON-flattening pipelines, but without certain-answer guarantees.

## 4. Upper Bound

For XML data exchange with **fully-specified** (non-recursive) DTDs and tree-pattern mappings without value joins, certain answers for tree-pattern queries are in **PTime data complexity** via a canonical solution; with relative/keyref constraints and value comparisons the upper bound rises to **coNP** data complexity (Arenas–Libkin). For nested-relational mappings expressible by nested st-tgds with terminating nested chase, certain answers for NRC unions of conjunctive queries are in **PTime data complexity** when the nested core exists. Model: standard RAM/Turing, data complexity.

## 5. Lower Bound

Certain-answer computation for XML data exchange with tree patterns plus **inequalities or non-trivial DTD recursion** is **coNP-complete in data complexity** (Arenas–Libkin), inheriting the relational $\neq$ hardness and adding tree-structural sources of intractability. Consistency of nested target keyref constraints can make **solution existence** itself NP-hard. For order-constrained targets, deciding certainty over admissible orderings is at least **coNP-hard** and conjectured higher (no matching upper bound is known). Model: NP/coNP data-complexity reductions.

## 6. The Gap

This is **genuinely open**. Three gaps stand out: (1) **no canonical core** theory for nested mappings with set+grouping comparable to the relational core — minimality up to deep/grouping homomorphism lacks a polynomial computation result; (2) the **order dimension** has essentially no tight complexity classification — certainty-over-orderings sits between coNP and $\Pi_2^p$ with no matching bounds; (3) **cross-level keyrefs + grouping** interact in ways that can make solution existence and certainty jump in complexity, and the dichotomy boundary is unmapped. Closing requires a nested chase with provable termination/core guarantees and new lower-bound gadgets exploiting tree+order structure.

## 7. Current Research (as of June 2026)

Active work: **JSON/semi-structured integration with formal guarantees**, lifting XML-data-exchange results to JSON Schema and to lakehouse nested types. *(frontier — verify)* **SHACL/RDF-star and property-graph "shape" mappings** as a nested-constraint analog, with certain-answer semantics over graph schemas. *(frontier — verify)* Order-aware exchange motivated by event/log integration and by vector+JSON hybrid stores. Groups: Libkin (Edinburgh/RelationalAI), Arenas (PUC Chile), Barceló (PUC Chile), Pieris (Edinburgh); systems angle from the Clio/Spicy lineage (Mecca, Papotti).

## 8. Future Work

- A **nested core** theorem: polynomial minimal universal solution for set+grouping mappings.
- Tight complexity for **order-constrained** certain answers.
- Decidable, terminating **nested chase** with keyrefs across levels.
- Practical certain-answer engines for **JSON Schema / property-graph** integration.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* Theoretical Computer Science, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** M. Arenas, L. Libkin. *XML data exchange: Consistency and query answering.* Journal of the ACM / ACM TODS, 2008. — [DOI](https://doi.org/10.1145/1346330.1346332)
- **[Foundational]** L. Popa, Y. Velegrakis, R. Miller, M. Hernández, R. Fagin. *Translating web data (Clio).* VLDB, 2002. — [PDF](https://www.cs.uic.edu/~advis/readings/paperhtml/41.html)
- **[SOTA]** A. Fuxman, M. Hernández, H. Ho, R. Miller, P. Papotti, L. Popa. *Nested mappings: Schema mapping reloaded.* VLDB, 2006. — [PDF](https://www.vldb.org/conf/2006/p67-fuxman.pdf)
- **[Foundational]** P. Buneman, S. Naqvi, V. Tannen, L. Wong. *Principles of programming with complex objects and collection types.* Theoretical Computer Science, 1995. — [DOI](https://doi.org/10.1016/0304-3975(95)00024-Q)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. (Complex values, nested model.) — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

Source (flat): `Enroll(student, course)` = $\{(\text{Ann}, \text{DB}), (\text{Ann}, \text{OS}), (\text{Bob}, \text{DB})\}$.

Target is **nested**: `Student(name, {Course})` — each student holds a *set* of courses. The nested st-tgd groups by student:
$$\text{Enroll}(s,c) \;\to\; \exists G\; \text{Student}(s, G) \wedge c \in G.$$

The canonical (core) universal solution groups all of Ann's courses into one set rather than two singletons:
$$\{\;\text{Student}(\text{Ann}, \{\text{DB}, \text{OS}\}),\; \text{Student}(\text{Bob}, \{\text{DB}\})\;\}.$$

Why nesting matters: a *naive* per-tuple chase would emit `Student(Ann,{DB})` and `Student(Ann,{OS})` — two facts deep-homomorphic to neither each other nor the core. The query "students taking both DB and OS" is **certain** for Ann only under the grouped (core) solution, since certain answers quantify up to *deep/grouping* homomorphism. This is exactly the canonicity gap (Section 6): no PTIME core algorithm is known once grouping plus cross-level keyrefs interact.

---
*Part of the [DBMS Research catalog](../../README.md).*
