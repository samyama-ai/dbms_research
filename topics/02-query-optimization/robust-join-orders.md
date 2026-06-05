# Provably good cost-model-robust join orders

> **Topic:** Query Optimization · **ID:** `02-query-optimization/robust-join-orders` · **Status:** open

## 1. Problem Statement

Cost-based optimizers pick the plan minimizing cost under a **single** point estimate of
cardinalities and cost parameters. But those estimates are uncertain, and the chosen plan can be
catastrophically suboptimal when the truth differs. The **robust join ordering** problem: given an
**uncertainty set** $\mathcal{U}$ of possible cost/cardinality inputs (a box, an ellipsoid, a
distribution, or a set of point scenarios), find a join order that is provably near-optimal across
all of $\mathcal{U}$.

Formal objectives:

- **Minimax cost:** $\min_T \max_{u \in \mathcal{U}} C_u(T)$.
- **Minimax regret:** $\min_T \max_{u \in \mathcal{U}} \big(C_u(T) - \min_{T'} C_u(T')\big)$.
- **Distributional:** $\min_T \ \mathbb{E}_{u}\,[C_u(T)]$ or a CVaR/quantile objective.

Decision, optimization, and "is plan $T$ within factor $\alpha$ of robust-optimal" variants apply.

## 2. Mathematical Foundations

Each scenario $u \in \mathcal{U}$ induces selectivities and base sizes, hence a cost $C_u(T)$ for
join tree $T$. **Regret** $\rho(T)=\max_u (C_u(T)-\mathrm{OPT}(u))$ measures worst-case suboptimality.
Robust optimization layers a max over $\mathcal{U}$ on top of the already-NP-hard inner ordering
problem, so robust ordering is at least as hard as nominal ordering.

Related theory: **parametric query optimization (PQO)** partitions the parameter space into regions,
each with one optimal plan; the **plan diagram** is this decomposition. The number of optimal plans
("plan-space size") bounds robustness structure. Connections exist to **min-regret** combinatorial
optimization (NP-hard even for shortest paths/spanning trees) and to **distributionally robust
optimization (DRO)** with ambiguity sets.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Chu, Halpern, Seshadri (PODS 1999) formalized **least-expected-cost** optimization
  under cost distributions. Babcock & Chaudhuri (SIGMOD 2005) gave robust query optimization trading
  expected cost for predictability. Min-regret plan selection (Dey/Harish/Haritsa, "PlanBouquet"
  line) bounds worst-case suboptimality.
- **Systems-SOTA:** **PlanBouquet / SpillBound** (Haritsa group, IISc) give the first *guaranteed*
  worst-case performance bounds (sub-optimality factor independent of selectivity values) by
  anorexic plan-diagram reduction and bouquet execution. Commercial systems use plan hints,
  parametric plan caching, and adaptive re-optimization instead of provable robustness.

## 4. Upper Bound

- **SpillBound / PlanBouquet** achieve a worst-case performance guarantee bounded by a small constant
  related to the number of cost "contours" (e.g. a factor that is $O(\rho^2)$ in 2D selectivity
  space), independent of the actual selectivity location — a genuine provable competitive bound in
  the bouquet execution model.
- For point-scenario minimax over $m$ scenarios, exact robust ordering is solvable by DP over
  $(\text{subset}, \text{scenario-vector})$ but costs $O(3^n \cdot m)$ in the RAM model.

## 5. Lower Bound

- Nominal join ordering is **NP-hard** (Cluet–Moerkotte), so robust ordering inherits NP-hardness.
- **Min-max-regret** versions of even polynomially-solvable base problems (shortest path, MST) are
  **NP-hard / often inapproximable** (Aissi–Bazgan–Vanderpooten), implying min-regret join ordering
  is hard even when the nominal problem is easy.
- The PlanBouquet guarantee comes with a matching **lower bound** showing its sub-optimality factor is
  essentially optimal for the contour-based execution model (Haritsa et al.).

## 6. The Gap

We have provable guarantees only in restricted execution models (bouquet/contour, low-dimensional
selectivity spaces) and only for *execution-time* robustness, not for *static plan choice* over
high-dimensional uncertainty sets. Open: polynomial or FPT robust ordering for structured
$\mathcal{U}$, approximation algorithms for minimax-regret ordering, and guarantees that scale beyond
2–3 uncertain selectivity dimensions.

## 7. Current Research (as of June 2026)

- Scaling PlanBouquet/SpillBound guarantees to higher-dimensional selectivity spaces and to learned
  estimators' uncertainty. *(frontier — verify)*
- Distributionally-robust and learned-uncertainty plans (MIT, TUM, IISc) combining cardinality-error
  models with DRO. *(frontier — verify)*
- Robustness as a first-class objective in learned optimizers (Balsa, Bao) with worst-case guards.

## 8. Future Work

- Approximation algorithms with provable ratios for minimax-regret join ordering.
- Tractable robust ordering for natural ambiguity sets (boxes, ellipsoids).
- Unifying static robust plan choice with adaptive re-optimization under one guarantee.

## 9. Key References

- **[Foundational]** Chu, Halpern, Seshadri. *Least Expected Cost Query Optimization: An Exercise in Utility.* PODS, 1999.
- **[Foundational]** Babcock, Chaudhuri. *Towards a Robust Query Optimizer: A Principled and Practical Approach.* SIGMOD, 2005.
- **[SOTA]** Dutt, Haritsa. *Plan Bouquets: Query Processing without Selectivity Estimation.* SIGMOD, 2014.
- **[SOTA]** Karthik, Haritsa, et al. *Platform-independent Robust Query Processing (SpillBound).* ICDE, 2016 / TKDE.
- **[Survey]** Aissi, Bazgan, Vanderpooten. *Min-max and Min-max Regret Versions of Combinatorial Optimization Problems: A Survey.* EJOR, 2009.

---
*Part of the [DBMS Research catalog](../../README.md).*
