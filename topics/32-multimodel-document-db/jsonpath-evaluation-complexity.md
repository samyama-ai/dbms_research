# Complexity of JSONPath query evaluation

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/jsonpath-evaluation-complexity` · **Status:** partially-solved

## 1. Problem Statement
Given a JSON document $J$ and a JSONPath expression $p$ (in one of the many dialects: the Goessner de-facto syntax, the IETF RFC 9535 standard, or the SQL/JSON path language of SQL:2016/2023), determine the precise computational complexity of producing the result of $p$ on $J$. We distinguish:
- **Evaluation (function problem):** materialize the (multi-)set of nodes/values selected by $p$.
- **Membership (decision):** given a node $n$, is $n \in p(J)$?
- **Non-emptiness (decision):** is $p(J) \neq \varnothing$? (the natural Boolean variant used inside filters and SQL `JSON_EXISTS`).
- **Combined vs. data complexity:** complexity as a function of $|p|+|J|$ vs. $|J|$ with $p$ fixed.

The open part concerns the *full* feature set: recursive descent (`..`), filter selectors with arithmetic and comparisons, function extensions (`length()`, `count()`, `match()`/`search()` regular expressions), and the interaction of duplicate-elimination/ordering semantics across dialects.

## 2. Mathematical Foundations
A JSON value is a tree (with object and array nodes) or, semantically, a finite structure over the signature of *child*, *descendant*, key labels, and array indices. The navigational core of JSONPath is essentially a unary tree-pattern / XPath-like fragment, so it inherits machinery from:
- **Tree automata and XPath complexity** (Gottlob–Koch–Pichler): core XPath evaluation is PTIME-complete (combined) and in LOGSPACE/linear in data complexity for navigational fragments.
- **Conjunctive-query / first-order logic over trees:** filters with existential subqueries map to positive existential FO; with arithmetic comparisons, evaluation lifts toward FO over an ordered/arithmetic structure.
- **RFC 9535 semantics** define a *nodelist* (order-preserving, with well-specified duplicate behavior under `..`), which makes evaluation a deterministic transducer rather than a relation.

Formally, for the navigational core, membership reduces to model-checking a positive-existential formula $\varphi_p(x)$ over the document structure, giving data complexity in $\mathrm{AC}^0/\mathrm{LOGSPACE}$ and combined complexity in PTIME; with negation/full filters and value arithmetic the relevant class rises (PTIME-complete, and PSPACE-flavored only if backreferencing regex functions are admitted).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The recent formalization line on RFC 9535 (and earlier SQL/JSON path semantics by Bourhis–Reutter–Suciu–Vrgoč) gives a clean autom-theoretic semantics and tight bounds for the navigational + filter fragment: data complexity in non-uniform $\mathrm{AC}^0$ / $\mathrm{LOGSPACE}$, combined complexity PTIME, with PTIME-completeness for fragments with sufficiently rich filters.
- **Systems-SOTA:** PostgreSQL (`jsonb_path_query`), Oracle, SQL Server, MySQL, and MongoDB's `$jsonSchema`/aggregation paths all implement single-pass or automaton-based evaluators that are effectively linear in $|J|$ per path for the common (non-recursive, non-regex) case.

## 4. Upper Bound
For the **navigational + Boolean-filter fragment** (no regex backreferences): combined complexity is in **PTIME** and data complexity in **LOGSPACE** (indeed $\mathrm{AC}^0$ for fixed-depth, recursion-free queries), via the FO/automata reduction. Evaluation is achievable in $O(|p|\cdot|J|)$ time for recursion-free paths and $O(|p|\cdot|J|)$ to $O(|p|\cdot|J|^2)$ with recursive descent under naive node-set materialization, mirroring core-XPath bottom-up algorithms (Gottlob–Koch–Pichler, *JACM* 2005).

## 5. Lower Bound
- **PTIME-hardness** (combined) for fragments expressing the standard core-XPath PTIME-complete features (Boolean filters with descendant), inherited from the XPath lower bounds of Gottlob–Koch–Pichler.
- For SQL/JSON path with **arithmetic and regular-expression functions**, non-emptiness becomes at least as hard as evaluating those functions; with full PCRE-style backreferences (as some engines allow) matching is NP-hard, pushing filter satisfaction outside PTIME.
- No super-linear *unconditional* data-complexity lower bound is known for the recursion-free fragment; the LOGSPACE membership bound is essentially tight against $\mathrm{AC}^0$ separations.

## 6. The Gap
The navigational core is essentially **closed** (matches XPath bounds). The genuinely open territory is the *standardized full language*: nobody has a single, dialect-agnostic complexity classification covering (i) RFC 9535's exact nodelist/dedup semantics, (ii) SQL/JSON's `lax`/`strict` modes, and (iii) the function extension set including regex. The gap is largely *definitional and feature-coverage* rather than an exponential separation: closing it means a complete theorem stating, per feature combination, the exact class (and matching hardness) — particularly isolating where regex/arithmetic tips evaluation from PTIME into NP/PSPACE.

## 7. Current Research (as of June 2026)
- Formal semantics and complexity of **RFC 9535** (published 2024) is an active line; work building on Vrgoč, Reutter, Bourhis, and Suciu's SQL/JSON results extends to the IETF dialect *(frontier — verify exact published bounds for the function-extension set)*.
- Cross-dialect equivalence/"which-features-cost-what" maps, and streaming/single-pass evaluators with worst-case guarantees, are being pursued in the PODS/ICDT community.
- Engine-side, vectorized/SIMD JSON parsing (simdjson) is being coupled to path evaluators, shifting practical bottlenecks from path complexity to parsing throughput.

## 8. Future Work
- A unified complexity taxonomy parameterized by dialect features (recursion, arithmetic, regex flavor, dedup mode).
- Parameterized/fine-grained bounds (e.g., complexity in document depth or path nesting) and lower bounds for recursive descent.
- Provenance- and order-aware evaluation complexity (RFC 9535 insists on output order).

## 9. Key References
- **[Foundational]** G. Gottlob, C. Koch, R. Pichler. *Efficient Algorithms for Processing XPath Queries.* ACM TODS / JACM, 2005.
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995.
- **[SOTA]** P. Bourhis, J. Reutter, F. Suciu, D. Vrgoč. *JSON: Data model, query languages and schema specification.* PODS, 2017.
- **[SOTA]** S. Gorman, G. Normington, et al. (IETF). *RFC 9535: JSONPath: Query Expressions for JSON.* IETF, 2024.
- **[Survey]** P. Bourhis, J. Reutter, D. Vrgoč. *Querying JSON with the SQL/JSON path language and beyond.* (survey-style treatments in ICDT/PODS proceedings), 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
