# XML/JSON path query minimization

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/path-query-minimization` · **Status:** partially-solved

## 1. Problem Statement
A *tree-pattern query* (TPQ) / path query (XPath core, JSONPath, JSONiq navigation) selects nodes from semistructured trees by matching a pattern with child (`/`), descendant (`//`), branching, and wildcard (`*`) edges. **Minimization** asks: given a query $p$, find an equivalent query $p'$ with the fewest nodes (or smallest size) — equivalent meaning same answers on all trees, optionally restricted to trees satisfying schema/integrity constraints.

- **Decision variant:** is $p$ minimal? Equivalently, decide TPQ *containment* $p \sqsubseteq q$.
- **Optimization variant:** output a minimum-size equivalent $p'$.
- **Constraint-aware variant:** minimize under a DTD/XSD or under keys/FDs/inclusion dependencies, which can make more nodes redundant.

## 2. Mathematical Foundations
TPQs are characterized by **homomorphisms**: containment $p\sqsubseteq q$ holds *iff* there is a homomorphism from $q$ to $p$ — but, unlike CQs, this exact characterization holds only for fragments. For the fragment with `/`, `//`, `[]` (no `*`), containment is decided by homomorphism and is in **PTIME**; minimization reduces to computing a minimal homomorphic core. Adding wildcard `*` or disjunction breaks the homomorphism property and pushes containment to **coNP-complete** (Miklau–Suciu). Under constraints, reasoning uses the **chase** for tree constraints and DTD automata; constraints are encoded so that redundancy = simulation/homomorphism modulo the constraint closure. Connections: tree automata, conjunctive queries over trees, and the simulation preorder.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Miklau & Suciu, *Containment and Equivalence for a Fragment of XPath* (JACM 2004) — the definitive map: PTIME for `{/,//,[]}`, coNP-complete with `*`. Amer-Yahia, Cho, Lakshmanan, Srivastava — *Tree Pattern Query Minimization* (VLDB Journal 2002) gave the foundational minimization algorithms and the constraint-aware (CD/IC) extensions. Wood, Neven, Schwentick — XPath containment under DTDs (often EXPTIME / undecidable for richer fragments).
- **Systems-SOTA:** XPath/XQuery optimizers (Saxon, BaseX, eXist-db) apply core-computation and constraint pushdown; JSON engines (PostgreSQL `jsonpath`, MongoDB aggregation, AsterixDB) implement only partial path simplification, mostly redundant-step elimination, not full minimization.

## 4. Upper Bound
- Constraint-free fragment $\{/,//,[]\}$: minimization in **PTIME** via core computation (Amer-Yahia et al.; Flesca–Furfaro–Masciari).
- With required/forbidden constraints, keys, and backward axes, equivalence is still decidable; minimization is in **coNP** (guess the smaller pattern, verify equivalence with a coNP containment check).
- Under non-recursive DTDs, containment is in **EXPTIME** (tree-automata product), so minimization is EXPTIME-bounded.

## 5. Lower Bound
- Containment/minimization for $\{/,//,[],*\}$ is **coNP-complete** (Miklau–Suciu).
- Under disjunction + DTDs, XPath containment is **EXPTIME-complete** or **undecidable** depending on axis set (Neven–Schwentick; Benedikt–Fan–Geerts).
- With data-value joins (full XPath 2.0 / equality between nodes), containment becomes **undecidable** (reduction from FO over trees).

## 6. The Gap
The "partially solved" status is precise: minimization is **completely characterized and tractable** for the practically dominant child/descendant/branch fragment, and tightly classified (coNP) once wildcards or simple constraints enter. The remaining open territory is *minimization under rich integrity constraints over JSON* (optional/repeated structure, inclusion dependencies, recursive schemas) and *data-value-aware* minimization, where decidability boundaries are sharp and some cases remain open. Closing it means mapping the exact constraint classes that keep minimization in coNP versus those that explode to EXPTIME/undecidable.

## 7. Current Research (as of June 2026)
JSON-specific path minimization is being re-derived from the XPath theory because JSONPath/SQL/JSON path lacks a settled semantics; standardization (IETF JSONPath RFC 9535, 2024) is enabling formal containment results. *(frontier — verify: recent claims of PTIME JSONPath minimization under JSON Schema constraints.)* Groups around Benedikt (Oxford), Bojańczyk, and the AsterixDB/SQL++ community work on tree-pattern reasoning and schema-aware simplification.

## 8. Future Work
- A complete dichotomy of JSONPath minimization complexity under JSON Schema.
- Minimization exploiting inferred keys/FDs/INDs (see *semistructured-constraints*).
- Cost-based (not just size-based) minimization tied to physical layout.
- Incremental re-minimization as schema drifts.

## 9. Key References
- **[Foundational]** G. Miklau, D. Suciu. *Containment and Equivalence for a Fragment of XPath.* JACM, 2004.
- **[Foundational]** S. Amer-Yahia, S. Cho, L. Lakshmanan, D. Srivastava. *Tree Pattern Query Minimization.* The VLDB Journal, 2002.
- **[Foundational]** F. Neven, T. Schwentick. *XPath Containment in the Presence of Disjunction, DTDs, and Variables.* ICDT, 2003.
- **[SOTA]** M. Benedikt, W. Fan, F. Geerts. *XPath Satisfiability in the Presence of DTDs.* JACM, 2008.
- **[Foundational]** A. Chandra, P. Merlin. *Optimal Implementation of Conjunctive Queries.* STOC, 1977.
- **[Survey]** S. Gottlob, C. Koch, R. Pichler. *Efficient Algorithms for Processing XPath Queries.* ACM TODS, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
