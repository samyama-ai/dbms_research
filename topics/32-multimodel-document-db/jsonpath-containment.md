# Containment and equivalence of JSON path queries

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/jsonpath-containment` · **Status:** open

## 1. Problem Statement
Given two JSON path queries $p$ and $q$ (over the navigational JSON path algebra: child, recursive descent `..`, array indexing, filters with comparisons and arithmetic), decide:
- **Containment:** $p \sqsubseteq q$, i.e., for every JSON document $J$, $p(J) \subseteq q(J)$ (as node/value sets, respecting the chosen multiset/order semantics);
- **Equivalence:** $p \equiv q$ iff $p \sqsubseteq q$ and $q \sqsubseteq p$;
- **Satisfiability:** $\exists J.\ p(J) \neq \varnothing$ (a special case driving the others).

These are the static-analysis primitives behind query optimization, rewriting using views, index applicability, and access-control rewriting. The hard, open setting is the **full feature set simultaneously**: filters (existential subqueries) + recursion (`..`) + value arithmetic/comparisons + the dialect's duplicate/order semantics. Decision variants differ sharply in complexity from satisfiability to containment to equivalence.

## 2. Mathematical Foundations
JSON path containment is the analog of **XPath containment**, which sits on:
- **Tree-pattern containment / homomorphism:** for the conjunctive (positive, recursion-free) fragment, containment reduces to existence of a homomorphism between tree patterns — but unlike relational CQs, XPath/tree-pattern containment is **not** characterized by homomorphism alone once `//` (descendant), wildcard, and branching all co-occur (Miklau–Suciu).
- **Logic over trees:** filters with negation/arithmetic push the language toward FO over ordered trees; satisfiability of FO over trees is decidable but non-elementary, and adding linear/integer arithmetic invokes Presburger/quantifier-elimination machinery.
- **Automata:** containment can be reduced to language inclusion of (alternating/two-way) tree automata, giving EXPTIME upper bounds for navigational fragments.

The decisive boundary results: tree-pattern containment with `{/, //, [], *}` is **coNP-complete** (Miklau–Suciu, *JACM* 2004); satisfiability of XPath fragments ranges from PTIME to undecidable depending on arithmetic, negation, and data-value (joins via key equality) features (Benedikt–Fan–Geerts).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** the XPath static-analysis program (Miklau–Suciu; Neven–Schwentick; Benedikt–Fan–Geerts; Schwentick's survey) gives a near-complete map for XPath; JSON path inherits these but the *arrays + index arithmetic + JSON's filter-comparison* combination has only partial transfer. Recent SQL/JSON-path semantics (Bourhis–Reutter–Suciu–Vrgoč) supply the formal substrate, but containment is not fully classified.
- **Systems-SOTA:** no production engine decides JSON-path containment; optimizers use only conservative syntactic rewrite rules. There is essentially **no** complete containment checker shipped.

## 4. Upper Bound
- **Navigational core (positive tree patterns, $\{$child, descendant, wildcard, branching$\}$):** containment in **coNP**; satisfiability in PTIME (Miklau–Suciu).
- **With recursion + filters as alternating two-way tree automata:** containment in **EXPTIME** via automata inclusion.
- **With data-value joins and arithmetic comparisons:** decidability survives for fragments mapping into Presburger-decidable constraints, but bounds rise to **EXPSPACE / non-elementary**; some combinations are conjectured/known undecidable.

## 5. Lower Bound
- **coNP-hardness** for the positive `{/, //, *}` tree-pattern fragment (Miklau–Suciu).
- **EXPTIME-hardness** for fragments rich enough to encode alternating tree-automaton inclusion.
- **Undecidability:** XPath/regular-path containment becomes **undecidable** once unrestricted data-value comparisons (equality joins on values) combine with recursion (results of Benedikt–Fan–Geerts and the register-automata/data-tree line, Bojańczyk et al.) — directly relevant because JSON filters compare data values and array indices arithmetically.

## 6. The Gap
**Genuinely open.** Even satisfiability — the easy case — is unclassified for the full JSON path with array-index arithmetic plus recursive descent plus value comparisons. Between the coNP navigational core and the undecidable data-value+recursion frontier lies a large grey zone (filters with bounded arithmetic, `..` with index ranges) whose exact decidability/complexity is unknown. Closing the gap means (i) pinpointing the decidability frontier as features are added, and (ii) tight complexity for the decidable side, plus a practical (incomplete-but-sound) containment procedure usable in optimizers.

## 7. Current Research (as of June 2026)
- Transfer of the XPath static-analysis toolkit to RFC 9535 / SQL-JSON path, isolating where **array index arithmetic** and **`length()`/`count()` functions** break decidability *(frontier — verify; few published containment results target arrays specifically)*.
- Data-tree and register/data automata methods (Bojańczyk, Figueira, Segoufin lineage) applied to JSON filters with value joins.
- SMT-backed *bounded* containment checkers (encode "is there a witness document of depth $\le k$ distinguishing $p,q$?") as a pragmatic incomplete tool.

## 8. Future Work
- A decidability map parameterized by (recursion, arithmetic on indices, value joins, negation).
- Containment **modulo a schema** (using inferred JSON Schema to constrain documents), which often lowers complexity.
- Sound incomplete procedures with completeness guarantees on practical fragments, wired into real optimizers.

## 9. Key References
- **[Foundational]** G. Miklau, D. Suciu. *Containment and Equivalence for a Fragment of XPath.* JACM, 2004.
- **[Foundational]** M. Benedikt, W. Fan, F. Geerts. *XPath Satisfiability in the Presence of DTDs.* JACM, 2008.
- **[SOTA]** P. Bourhis, J. Reutter, F. Suciu, D. Vrgoč. *JSON: Data model, query languages and schema specification.* PODS, 2017.
- **[Survey]** T. Schwentick. *XPath Query Containment.* SIGMOD Record, 2004.
- **[Foundational]** M. Bojańczyk, C. David, A. Muscholl, T. Schwentick, L. Segoufin. *Two-Variable Logic on Data Trees and XML Reasoning.* PODS/JACM, 2009.

---
*Part of the [DBMS Research catalog](../../README.md).*
