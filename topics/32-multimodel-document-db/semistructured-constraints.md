---
id: 32-multimodel-document-db/semistructured-constraints
title: "Integrity constraints over semistructured data"
topic: 32-multimodel-document-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Integrity constraints over semistructured data

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/semistructured-constraints` · **Status:** open

## 1. Problem Statement
Relational integrity constraints — **keys**, **functional dependencies (FDs)**, **inclusion dependencies (INDs)** — have crisp semantics on flat tables. Over semistructured data (XML trees, JSON with nested **optional** and **repeated** structure), even *defining* these constraints is subtle, and *checking* and *exploiting* them for optimization is largely unsettled.

- **Definitional variant:** give semantics to keys/FDs/INDs over trees with paths, optionality (a field may be absent), and arrays (multi-valued, ordered) — including *relative* keys (unique within a subtree) vs *absolute* keys.
- **Checking variant (validation):** decide whether an instance satisfies a constraint set; decide **consistency/implication** of a constraint set with a schema.
- **Exploitation variant:** use satisfied constraints to minimize queries, choose shredding, and rewrite across designs.

## 2. Mathematical Foundations
The canonical model is **XML keys** (Buneman–Davidson–Fan–Hara–Tan): a key is a triple $(Q,(Q',\{P_1,\dots,P_k\}))$ — a *context path* $Q$, a *target path* $Q'$, and *key paths* $P_i$ — with absolute ($Q=\epsilon$) and relative variants. Satisfaction is defined via node sets reached by path expressions and value-equality. FDs generalize to **XFDs** (path → path); INDs to inclusion between path-defined node sets. Reasoning uses the **chase**, **tree automata**, and **implication** problems. Key tools: axiomatizability (finite vs infinite axiom systems), the distinction between **finite** and **unrestricted** implication, and decidability frontiers analogous to FD+IND implication being **undecidable** in the relational case (Mitchell; Chandra–Vardi). Optionality and arrays add three-valued logic and multiset semantics, breaking clean Armstrong-style axiomatizations.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Buneman–Davidson–Fan–Hara–Tan, *Keys for XML* (WWW 2001 / Computer Networks 2002) and *Reasoning about keys for XML* (Information Systems 2003) — semantics + the implication problem, with PTIME results for important key fragments. Arenas–Libkin, *A Normal Form for XML Documents* (PODS 2002 / TODS 2004) — **XNF**, FDs over XML and normalization. Fan–Siméon, *Integrity constraints for XML* (PODS 2000). JSON-specific work: **JSON Schema** validation semantics (Pezoa et al., WWW 2016) and emerging JSON keys/FD proposals.
- **Systems-SOTA:** XML Schema `key`/`keyref`/`unique`; MongoDB unique indexes (single-document, no cross-document FD/IND enforcement); PostgreSQL `jsonb` + check/exclusion constraints; no mainstream document store enforces general nested FDs or INDs. Constraint *discovery* tools (metanome-style FD/IND mining) exist for relational, nascent for JSON.

## 4. Upper Bound
- **Keys for XML** (Buneman et al.): satisfaction is PTIME; **implication** is decidable and in PTIME for the core fragment (absolute + relative keys without competing wildcards). With DTDs/schemas, validation against keys is polynomial in data, exponential in schema.
- **XFDs / XNF** (Arenas–Libkin): FD implication and normalization to XNF are decidable; lossless decomposition exists for the studied fragment.
- JSON Schema validation is decidable and linear-ish per document (with recursion/`$ref` handled by automata).

## 5. Lower Bound
- Adding **DTDs/regular schemas** to key/FD reasoning pushes implication to **EXPTIME** or **undecidable** depending on the path language (Fan–Libkin; Arenas–Fan–Libkin).
- **FD + IND implication** is already **undecidable** in the relational case (Mitchell 1983; Chandra–Vardi 1985); the semistructured generalization inherits this — combined nested keys + INDs reasoning is undecidable in general.
- Constraints with wildcard/descendant paths and value joins encode FO over trees ⇒ **undecidable** consistency.

## 6. The Gap
This is genuinely **open**. Unlike the relational case, there is no agreed-upon, complete axiomatization of keys+FDs+INDs over JSON with optional + repeated + ordered structure, nor a clean decidability map for their combined implication under JSON Schema. Practical systems enforce essentially nothing across documents. The gap spans three fronts simultaneously: (1) *semantics* (what does an IND mean across arrays with nulls?), (2) *decidability* (which combinations stay decidable?), and (3) *exploitation* (no optimizer systematically uses nested constraints). Closing even the definitional + checking fronts for a useful fragment would be a significant result.

## 7. Current Research (as of June 2026)
Formal JSON Schema semantics (Pezoa, Bourhis, Reutter, Vrgoč, Suciu) underpins new constraint definitions; constraint *discovery/profiling* over JSON (extending Metanome/HyFD to nested data) is active. *(frontier — verify: claims of a complete, decidable axiomatization of JSON keys+FDs+INDs under recursive JSON Schema — likely still partial as of early 2026.)* Groups: Edinburgh/Oxford (Libkin, Benedikt, Bourhis), PUC Chile (Reutter, Vrgoč), and the data-profiling community (Naumann, HPI).

## 8. Future Work
- Decidability dichotomy for nested keys/FDs/INDs under JSON Schema.
- Sound+complete axiom systems for an optionality/array fragment.
- Constraint-aware query minimization (links to *path-query-minimization*) and design rewriting (*document-relational-rewriting*).
- Scalable cross-document constraint enforcement and discovery.

## 9. Key References
- **[Foundational]** P. Buneman, S. Davidson, W. Fan, C. Hara, W.-C. Tan. *Keys for XML.* Computer Networks / WWW, 2002. — [DOI](https://doi.org/10.1145/371920.371984)
- **[Foundational]** M. Arenas, L. Libkin. *A Normal Form for XML Documents.* ACM TODS, 2004. — [DOI](https://doi.org/10.1145/974750.974757)
- **[Foundational]** W. Fan, J. Siméon. *Integrity Constraints for XML.* JCSS / PODS, 2000–2003. — [DOI](https://doi.org/10.1145/335168.335172)
- **[Foundational]** J. C. Mitchell. *The Implication Problem for Functional and Inclusion Dependencies.* Information and Control, 1983. — [DOI](https://doi.org/10.1016/S0019-9958(83)80002-3)
- **[SOTA]** F. Pezoa, J. Reutter, F. Suárez, M. Ugarte, D. Vrgoč. *Foundations of JSON Schema.* WWW, 2016. — [DOI](https://doi.org/10.1145/2872427.2883029) · [DBLP](https://dblp.org/rec/conf/www/PezoaRSUV16.html)
- **[Survey]** W. Fan. *XML Constraints: Specification, Analysis, and Applications.* (survey/tutorial), DEXA/various, 2005. — [DOI](https://doi.org/10.1109/DEXA.2005.204)

## 10. Worked Example

Take a JSON `order` document with a nested array of line items:

```
{ "orderId": "O1",
  "items": [ { "sku": "A", "qty": 2 },
             { "sku": "B", "qty": 1 },
             { "sku": "A", "qty": 5 } ] }
```

Consider a **relative key**: "within one order (context path `/order`), `sku` is a key for `items`" — i.e. $(\,/order,\ (items,\{sku\})\,)$. This order **violates** it: two `items` nodes share `sku = "A"`. Note the key is *relative*, not absolute — the same `sku` "A" may legally reappear in a different order `O2`, so an absolute key `(\epsilon, (//items, \{sku\}))` would be a strictly stronger (and here false) constraint.

Now add optionality: suppose some items omit `qty`. An XFD `sku → qty` (same SKU implies same quantity) then faces the three-valued question of Section 6 — does a *missing* `qty` count as equal to, distinct from, or incomparable with a present `qty`? Under "missing = distinct", `sku → qty` is satisfiable; under "missing matches anything", it may be violated. This ambiguity is exactly why a clean Armstrong-style axiomatization over optional+repeated structure remains open: the satisfaction relation itself is not yet canonical.

---
*Part of the [DBMS Research catalog](../../README.md).*
