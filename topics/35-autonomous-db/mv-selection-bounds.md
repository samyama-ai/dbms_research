# Materialized View Selection Bounds

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/mv-selection-bounds` · **Status:** partially-solved

## 1. Problem Statement
Given a workload of queries (often OLAP aggregations), a lattice or DAG of candidate **materialized views (MVs)** $\mathcal{V}$ with view sizes (space) and **maintenance costs** under updates, select $M \subseteq \mathcal{V}$ to materialize so as to minimize total **query-evaluation cost** subject to:
- a **space budget** $\sum_{v \in M} \mathrm{size}(v) \le B$, and/or
- a **maintenance-cost budget** $\sum_{v\in M} \mathrm{maint}(v) \le U$.

Variants:
- **Decision:** Does some $M$ within budget achieve total query cost $\le t$?
- **Optimization:** Min query cost / max benefit under space (the classic data-cube version) or under *both* space and maintenance.
- **Counting:** Number of view subsets closed under the "answerable-from" relation.

The view-selection benefit, like index benefit, can be modeled as coverage of query subexpressions, but **maintenance cost** couples views to the *update* stream, making the dual-budget version qualitatively harder.

## 2. Mathematical Foundations
Classic setting: the **data cube lattice** $L$ (Harinarayan–Rajaraman–Ullman). A view $u$ can answer query $v$ iff $v \preceq u$ in the dependency lattice; the cost to answer $v$ from the nearest materialized ancestor is its size. The **benefit** of adding $u$ given current set $M$,
$$ B(u, M) = \sum_{w \preceq u} \big( \mathrm{cost}(w \mid M) - \mathrm{size}(u) \big)_+ ,$$
is **monotone and submodular** in $M$ for the pure space-constrained cube — the structural fact enabling guarantees.

Maintenance changes the picture: maintenance cost is a function of *update frequencies* and view *derivation*, and minimizing query cost subject to a maintenance budget is a **knapsack-with-submodular-objective** when sizes/maint are linear, but becomes non-submodular when **shared subexpressions / common MV reuse** make maintenance of one view cheaper given another (the MV equivalent of index interaction). The general AND-OR DAG formulation (Gupta–Mumick) is the maximal model.

## 3. State of the Art (SOTA)
**Theory-SOTA:** For the data-cube under cardinality $k$, the **HRU greedy** achieves benefit $\ge (1-1/e)\,\mathrm{OPT}$ (it is the canonical submodular-greedy result). Extensions: $(1-1/e)$ under a space (knapsack) budget via Sviridenko-style greedy; bicriteria results for the dual space+maintenance budget that violate one budget by a logarithmic factor.

**Systems-SOTA:** Microsoft DTA and DB2/Oracle advisors select MVs jointly with indexes using cost-based greedy + merging; data-warehouse and modern lakehouse engines (e.g., automatic MV recommendation in cloud warehouses) use workload-driven heuristics and learned recommenders without ratio guarantees. *(frontier — verify)*

## 4. Upper Bound
- **Cardinality $k$, data cube:** greedy gives $(1 - 1/e)\,\mathrm{OPT}$ benefit (HRU 1996), $O(k|\mathcal{V}|)$ time.
- **Single space (knapsack) budget, submodular benefit:** $(1-1/e)$ via budgeted greedy / partial enumeration.
- **Space + maintenance (two linear budgets):** $(1 - 1/e - \varepsilon)$ via continuous greedy + swap rounding for the submodular core; or bicriteria $(1-1/e,\, O(\log))$ when one budget is soft.

## 5. Lower Bound
- View selection is **NP-hard** (HRU show the data-cube selection generalizes problems hard to optimize; the general DAG version reduces from Set Cover / Knapsack).
- The submodular-coverage core inherits **Feige's $(1 - 1/e + \varepsilon)$ inapproximability** under $\mathrm{P}\ne\mathrm{NP}$ — so the $(1-1/e)$ greedy is **optimal** for that core.
- With **maintenance interactions** (shared subexpressions making the objective non-submodular), the problem captures DkS-style instances with no known constant-factor approximation.

## 6. The Gap
**Partially solved.** For the *space-only, submodular* cube the gap is **closed**: $(1-1/e)$ matches Feige. The open gap is the **maintenance-constrained, interaction-rich** version — between bicriteria/parameterized upper bounds and the (suspected super-constant) hardness when shared-subexpression maintenance breaks submodularity. Closing it requires either proving real maintenance cost is "nearly submodular" or a hardness reduction for the AND-OR DAG model.

## 7. Current Research (as of June 2026)
- Learned MV recommenders in cloud warehouses, and **automatic MV maintenance / incremental view maintenance (IVM)** scheduling co-optimized with selection. *(frontier — verify)*
- Submodular-with-deletions and dynamic MV selection under drifting workloads.
- Theory groups continue tightening dual-budget submodular maximization (Vondrák, Feldman); systems groups (Microsoft GSL, cloud-DW teams, HPI) study workload-driven and LLM-assisted view recommendation. *(frontier — verify)*

## 8. Future Work
- Tight bounds for joint space+maintenance budgets with shared-subexpression maintenance.
- View selection integrated with IVM cost models and freshness SLAs.
- Beyond-worst-case guarantees exploiting lattice structure of real OLAP cubes.
- Joint MV + index + partition selection (see *joint-physical-design*).

## 9. Key References
- **[Foundational]** V. Harinarayan, A. Rajaraman, J. D. Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996.
- **[Foundational]** H. Gupta, I. S. Mumick. *Selection of Views to Materialize Under a Maintenance Cost Constraint.* ICDT, 1999.
- **[Foundational]** G. L. Nemhauser, L. A. Wolsey, M. L. Fisher. *An analysis of approximations for maximizing submodular set functions—I.* Math. Programming, 1978.
- **[SOTA]** S. Agrawal, S. Chaudhuri, V. Narasayya. *Automated Selection of Materialized Views and Indexes for SQL Databases.* VLDB, 2000.
- **[SOTA]** M. Sviridenko. *A note on maximizing a submodular set function subject to a knapsack constraint.* OR Letters, 2004.
- **[Survey]** R. Chirkova, J. Yang. *Materialized Views.* Foundations and Trends in Databases, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
