# Conjunctive regular path query optimization

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/crpq-optimization` · **Status:** open

## 1. Problem Statement

A **conjunctive regular path query (CRPQ)** is a conjunction of RPQ atoms

$$Q(\bar z) \leftarrow \bigwedge_{i=1}^{n} r_i(x_i, y_i),$$

where each $r_i$ is a (2)RPQ and $\bar z$ are the output (distinguished) variables. **UC2RPQs** add unions and inverses. CRPQs are the navigational backbone of SPARQL (property paths inside BGPs), Cypher, and the GQL standard.

**Optimization problem:** choose a *join order and decomposition* over the RPQ atoms — and within each atom a navigation strategy — that minimizes total intermediate-result size and runtime. Unlike pure relational CQ optimization, each "relation" $r_i(x_i,y_i)$ is **virtual**: its extension (the pair set) is produced *on the fly* by automaton-driven path navigation and can be huge or expensive. The open challenge is a unified optimizer that interleaves **path navigation** with **worst-case-optimal multiway joins** so that neither the materialized path relations nor the conjunction's intermediate joins blow up.

## 2. Mathematical Foundations

Each RPQ atom $r_i$ defines a binary relation $\llbracket r_i \rrbracket_G \subseteq V\times V$. Evaluating the conjunction is a CQ over these binary relations, so the **AGM bound** and **fractional hypertree width** $\mathsf{fhw}$ / **submodular width** $\mathsf{subw}$ govern worst-case output and intermediate sizes:

$$|Q(G)| \le \prod_i |\llbracket r_i\rrbracket_G|^{x_i}, \quad \mathbf{x} \text{ a fractional edge cover.}$$

But $|\llbracket r_i\rrbracket_G|$ is itself only bounded by $|V|^2$ and is expensive to materialize, so the relevant cost model must account for *navigation cost* (product-automaton BFS, $O(|E|\cdot|A_{r_i}|)$ per source) *plus* join cost. Tree-decomposition / $\mathsf{fhw}$ methods and PANDA's $\mathsf{subw}$ apply once atoms are treated as relations; the novelty is doing this **without fully materializing** each atom — i.e. *factorized* or *lazy* path relations.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Worst-case-optimal evaluation of CRPQs by treating path atoms as relations and applying generic-join/PANDA; results on *bounded-treewidth* CRPQ tractability (Barceló, Romero, Vardi). Yannakakis-style acyclic CRPQ evaluation when the atom hypergraph is acyclic.
- **Systems-SOTA:** *MillenniumDB* (Vrgoč et al., 2023) with worst-case-optimal joins integrated with path queries; *Kùzu* factorized + WCOJ processing; SPARQL engines (Virtuoso, GraphDB) optimizing property-path-in-BGP via cost heuristics; *AvantGraph* (TU Eindhoven) applying WCOJ and automaton-aware planning to RPQ conjunctions. No system gives provable optimality for the *interleaved* navigate-and-join problem.

## 4. Upper Bound

If each atom is materialized, the conjunction evaluates in $\tilde{O}(N^{\mathsf{subw}} + |\mathrm{out}|)$ via PANDA where $N = \sum_i |\llbracket r_i\rrbracket_G|$, plus navigation cost $\sum_i O(|E|\cdot|A_{r_i}|)$ to build atoms. For acyclic atom-hypergraphs, **Yannakakis** gives $O(N \cdot |\mathrm{out}|)$ (linear in input + output). Lazy/factorized navigation can avoid materializing full $\llbracket r_i\rrbracket$, replacing $N$ by per-binding on-demand reachability — the best practical upper bound, but without a clean closed form. These hold in word-RAM with automaton product structures.

## 5. Lower Bound

CRPQ **evaluation/containment** combined complexity is high: Boolean CRPQ evaluation is **NP-hard** (inherits CQ NP-hardness via the conjunction) and **EXPSPACE/PSPACE** for containment (see RPQ-containment page). For the *join-ordering optimization* itself, choosing the minimum-intermediate-size order is **NP-hard** (inherits from CQ optimal join ordering, Cluet–Moerkotte). Fine-grained: any CRPQ subsuming a hard CQ (e.g. triangle via three $a$-atoms) is **BMM/Hyperclique-hard**, so $O(n^{3-\epsilon})$ combinatorial evaluation is ruled out. Under *simple-path* semantics each atom is already NP-hard (Mendelzon–Wood), pushing the whole problem beyond PTIME data complexity.

## 6. The Gap

**Open.** Worst-case-optimal evaluation exists *if* atoms are materialized, but materialization is exactly what kills performance on real graphs; conversely lazy navigation has no worst-case-optimality guarantee. There is no optimizer with a provable competitive ratio that *interleaves* navigation and joins, and no tight characterization of when factorized path relations beat materialize-then-WCOJ. Closing the gap requires (a) a cost model unifying navigation and join costs, (b) a planner with provable bounds against the optimal interleaving, and (c) handling inverses (2RPQ) and unions (UC2RPQ) within the same framework.

## 7. Current Research (as of June 2026)

- *(frontier — verify)* AvantGraph and MillenniumDB integrating automaton-aware WCOJ planning; pushing path navigation into the join's set-intersection inner loop rather than materializing atoms first.
- *(frontier — verify)* factorized representations of path relations (Olteanu lineage) applied to CRPQ atoms to compress intermediate results.
- GQL/SQL-PGQ standardization (2024) driving renewed optimizer work on path-pattern + join queries (groups: Eindhoven, Chile/IMFD, Edinburgh, Oxford).

## 8. Future Work

- A unified navigate-and-join cost model with provable competitiveness.
- Cardinality estimation for *path* atoms feeding the CRPQ optimizer (cross-link to subgraph/path estimation).
- Worst-case-optimal handling of UC2RPQs (unions, inverses, two-way) with delay guarantees.
- Adaptive / runtime re-optimization as path navigation reveals true selectivities.

## 9. Key References

- **[Foundational]** Consens, Mendelzon. *GraphLog / Expressing structural queries.* and Florescu, Levy, Suciu. *Query Containment for Conjunctive Queries with Regular Expressions.* PODS 1998.
- **[Foundational]** Barceló, Libkin, Reutter (and Romero, Vardi). *Querying Graphs with Data / CRPQ tractability.* — Barceló. *Querying Graph Databases.* PODS 2013 (tutorial/survey).
- **[Foundational]** Abo Khamis, Ngo, Rudra. *PANDA: submodular-width joins.* PODS 2016 (applied to CRPQ atoms).
- **[SOTA]** Vrgoč, Rojas, Angles, Arenas, et al. *MillenniumDB.* 2023.
- **[SOTA]** Wang, Yakovets, et al. / AvantGraph team. *Worst-Case Optimal Joins for Regular Path Query Evaluation.* (TU Eindhoven), 2022–2023.
- **[Survey]** Angles, Arenas, Barceló, Hogan, Reutter, Vrgoč. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
