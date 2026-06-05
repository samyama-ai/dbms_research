# Optimal Data Cube Materialization

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/cube-view-selection` · **Status:** partially-solved

## 1. Problem Statement

Given a data cube over $d$ dimensions, there are $2^d$ possible **cuboids** (group-by aggregations, the cube lattice). Precomputing all of them is too expensive in space and maintenance; computing none makes queries slow. **Select a subset of cuboids to materialize** under a **space budget** (and/or maintenance/update budget) so as to **minimize total/average query cost** over an expected query workload.

- **Optimization variant (HRU):** Choose $k$ views to materialize to maximize the **benefit** (query-cost reduction), given each query is answered from the smallest materialized ancestor in the lattice.
- **Budgeted variant:** Minimize expected query cost subject to $\sum \text{size}(v) \le S$.
- **Decision variant:** Is there a selection of total size $\le S$ achieving query cost $\le Q$?
- **Maintenance-constrained variant:** add an update-cost budget.

## 2. Mathematical Foundations

The cube forms a **lattice** $L$ ordered by the "can-be-computed-from" (roll-up) relation; a query for cuboid $v$ is answered by scanning the smallest materialized $u \succeq v$. Define the **benefit** of materializing $v$ given an already-chosen set $M$:

$$
B(v \mid M) = \sum_{w \preceq v}\max\big(0,\ \mathrm{cost}_{M}(w) - \mathrm{cost}_{M\cup\{v\}}(w)\big).
$$

The crucial property: this benefit function is **monotone and submodular** in $M$. Hence the greedy "pick max marginal benefit per unit size" achieves the classic **$(1-1/e)$** guarantee (cardinality constraint) — the Harinarayan–Rajaraman–Ullman (HRU) result. With a knapsack (size) budget, cost-benefit greedy gives a constant-factor (roughly $\tfrac12(1-1/e)$) approximation.

Adding **maintenance/update** constraints couples view selection with **incremental-view-maintenance** cost and generally breaks pure submodularity, moving the problem toward constrained submodular / facility-location territory.

## 3. State of the Art (SOTA)

- **Foundational:** Harinarayan, Rajaraman, Ullman, *Implementing Data Cubes Efficiently* (SIGMOD 1996) — the greedy lattice algorithm and submodular benefit analysis. Gray et al., *Data Cube* operator (1997), defines the cube.
- **Theory-SOTA:** Greedy $(1-1/e)$ for cardinality; cost-benefit / lazy-greedy (Minoux) for the budgeted form; the general problem with both space and maintenance budgets is NP-hard with constant-factor approximations under submodular relaxations.
- **Systems-SOTA:** Apache **Kylin**, **Druid**, **ClickHouse** projections/materialized views, and cloud OLAP engines select/auto-recommend cuboids and materialized views, often with workload-driven heuristics and ILP solvers; commercial **automated MV advisors** (e.g., in major warehouses) extend HRU with maintenance and multi-query interactions.

## 4. Upper Bound

- **Cardinality-constrained** ($k$ views): greedy gives $(1-1/e)\approx 0.632$ of optimal benefit, in $O(k \cdot |L|)$ benefit evaluations (lazy greedy much faster in practice).
- **Knapsack/space-budget:** cost-benefit greedy with partial enumeration gives a $(1-1/e)$ approximation (Sviridenko) for monotone submodular maximization under a knapsack constraint, in polynomial time.
- ILP formulations solve small/medium instances optimally; column generation scales the LP relaxation.

## 5. Lower Bound

View selection is **NP-hard** (HRU note hardness via reduction from set cover). As a monotone-submodular maximization problem under a cardinality constraint, it is **hard to approximate beyond $(1-1/e)$** unless P = NP (Feige's set-cover inapproximability transfers via Nemhauser–Wolsey–Fisher tightness). Thus greedy is **optimal among poly-time algorithms** for the cardinality case. The maintenance-constrained and multi-query-interaction variants are at least as hard and lose the clean submodular guarantee.

## 6. The Gap

**Partially solved.** For the canonical space- (or count-) budgeted, submodular-benefit formulation, the gap is **closed**: greedy's $(1-1/e)$ matches the inapproximability lower bound. The **open** part is the realistic setting: simultaneous **space + maintenance budgets**, **update-aware** benefit (incremental maintenance), **non-submodular** interactions among partially overlapping views, and **uncertain/evolving** workloads — here no tight approximation is known.

## 7. Current Research (as of June 2026)

- **Workload-adaptive / online** view and projection selection in cloud warehouses, reacting to drift with bounded re-materialization *(frontier — verify)*.
- **Learned / RL-based** materialized-view advisors that fold in maintenance cost and query interactions *(frontier — verify)*.
- Unifying cuboid selection with **column-store projections** and partial/conditional materialization (only frequent slices).
- Groups: Stanford (Ullman lineage), Microsoft/Amazon/Snowflake auto-tuning teams, academic MV-selection work (e.g., Wisconsin, TU Munich).

## 8. Future Work

- Tight approximation for the joint space + maintenance + interaction problem.
- Robust selection under workload uncertainty (regret bounds).
- Incremental re-selection algorithms with amortized re-materialization guarantees.
- Integration with cube **compression/encoding** so benefit reflects encoded sizes.

## 9. Key References

- **[Foundational]** Harinarayan, Rajaraman, Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996.
- **[Foundational]** Gray, Bosworth, Layman, Pirahesh, et al. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* ICDE, 1996 / Data Mining and Knowledge Discovery, 1997.
- **[Foundational]** Nemhauser, Wolsey, Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978.
- **[SOTA]** Sviridenko. *A Note on Maximizing a Submodular Set Function Subject to a Knapsack Constraint.* Operations Research Letters, 2004.
- **[Survey]** Mami, Bellahsene. *A Survey of View Selection Methods.* SIGMOD Record, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
