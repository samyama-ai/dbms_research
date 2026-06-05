# Differentially Private Query Plan Optimization

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/dp-query-plan-optimization` · **Status:** open

## 1. Problem Statement

Classical query optimization (à la Selinger) picks the execution plan minimizing estimated **runtime cost**. Under differential privacy, two logically equivalent plans for the same query can have radically different *privacy-loss-for-accuracy* profiles: where a join/aggregation/truncation is placed, which sub-results are noised, and how the global budget $\varepsilon$ is split across operators all change the final error. The problem is to design a **cost model and optimizer** that, given a query (or workload), a privacy budget, and an accuracy target, chooses the relational plan (operator order, truncation thresholds, noise-injection points, budget allocation) minimizing expected output error — possibly jointly with runtime.

Variants:
- **Single-query plan selection (optimization):** choose plan + budget split minimizing expected $L_1$/$L_2$ error at fixed $(\varepsilon,\delta)$.
- **Mechanism-placement (decision):** decide whether to noise before vs. after each operator (e.g., noise-then-join vs. join-then-noise).
- **Joint cost (multi-objective):** Pareto-optimize (runtime, privacy-loss, error).

## 2. Mathematical Foundations

A plan is a DAG of relational operators $o_1,\dots,o_m$. DP composition (basic, advanced, **Rényi/zCDP**, or PLD/numerical accountant) determines how per-operator budgets $\varepsilon_i$ compose to the global $\varepsilon$: under zCDP, $\rho=\sum_i \rho_i$ and error of a Gaussian mechanism on operator $i$ scales as $\Delta_i/\sqrt{\rho_i}$. The optimizer minimizes total expected error
$$\min_{\{\rho_i\},\,\text{plan}}\ \mathbb{E}\!\left[\,\textstyle\sum_i w_i\,\mathrm{err}(\Delta_i(\text{plan}),\rho_i)\right]\quad \text{s.t. } \sum_i \rho_i \le \rho .$$
For fixed sensitivities, the inner budget-allocation is a convex program (Lagrangian / water-filling, generalizing the *Matrix Mechanism*'s strategy optimization). The outer plan choice changes the $\Delta_i$'s themselves (sensitivity depends on operator order, join keys, truncation $\tau$), making the joint problem combinatorial and non-convex. Sensitivity propagation through a plan is governed by elastic/residual sensitivity (see `dp-multi-join-sensitivity`).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** The **Matrix Mechanism** (Li, Hay, Rastogi, Miklau, Suciu, PODS 2010) optimizes a *strategy* matrix for a linear workload — effectively budget allocation across a fixed query "plan." HDMM (McKenna et al., VLDB 2018) scales this. These optimize *what to measure*, not *how to execute relationally*.
- **Systems-SOTA:** **PrivateSQL** (VLDB 2019) and **Tumult Analytics** compile DP-SQL but use largely fixed strategies. **CHORUS** (Johnson, Near et al., 2018/2020) rewrites SQL into DP plans. **APEx** (Ge, Mohan, He, et al., SIGMOD 2019) is an accuracy-aware DP query engine that *selects mechanisms* to meet an accuracy bound at minimum privacy cost — the closest to a true DP optimizer.

## 4. Upper Bound

For **linear** counting workloads with a fixed measurement plan, the matrix-mechanism strategy-optimization is solvable to (local) optimum; HDMM gives near-optimal error in polynomial time per workload. APEx provides accuracy guarantees with a greedy/translation-based mechanism selector but **no global plan-optimality guarantee**. Budget allocation across a *fixed* operator pipeline is a convex program solvable in poly-time. No algorithm is known to choose the relational *plan shape* optimally in general.

## 5. Lower Bound

Joint plan-selection-plus-budget-allocation is **NP-hard**: it generalizes both join-order optimization (NP-hard, Ibaraki–Kameda) and sensitivity-minimizing truncation (hard for cyclic joins). The matrix-mechanism's optimal strategy problem is conjectured hard in general; even approximating the optimal error for arbitrary linear workloads has no known poly-time constant-factor algorithm. Lower bounds on *error itself* inherit from linear-query DP lower bounds (Hardt–Talwar, the discrepancy/$\sigma$-LP bound, STOC 2010).

## 6. The Gap

There is **no unified DP cost model** that is both (a) predictive of true output error across plan rewrites and (b) optimizable with provable approximation guarantees. The gap is **genuinely open**: current systems either fix the plan and optimize budget (matrix mechanism — near-optimal but narrow) or select per-query mechanisms greedily (APEx/CHORUS — general but no optimality). Closing it needs a sensitivity-aware, composition-aware cost model with a provable approximation ratio for joint plan + budget search.

## 7. Current Research (as of June 2026)

- DP query optimizers integrating numerical PLD accountants into the cost model so budget composition is exact rather than via loose advanced-composition bounds *(frontier — verify)*.
- Learning-based / RL cost models for DP plans, analogous to learned query optimizers (Bao/Neo) but with error-vs-privacy reward *(frontier — verify)*.
- Tumult, OpenDP, and Google PipelineDP teams formalizing operator-level "stability" so plan rewrites are sound by construction.

## 8. Future Work

- A Selinger-style dynamic program with DP-aware pruning and provable bounds.
- Multi-objective (runtime × privacy × error) Pareto optimizers.
- Plan rewrites that exploit FK constraints and pre-aggregation to cut sensitivity.
- Reusing noisy sub-results across a workload (caching under composition).

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Li, Hay, Rastogi, Miklau, McGregor. *Optimizing Linear Counting Queries Under Differential Privacy (Matrix Mechanism).* PODS, 2010.
- **[Foundational]** Hardt, Talwar. *On the Geometry of Differential Privacy.* STOC, 2010.
- **[SOTA]** McKenna, Miklau, Hay, Machanavajjhala. *Optimizing Error of High-Dimensional Statistical Queries Under Differential Privacy (HDMM).* VLDB, 2018.
- **[SOTA]** Ge, Mohan, He, Machanavajjhala, et al. *APEx: Accuracy-Aware Differentially Private Data Exploration.* SIGMOD, 2019.
- **[SOTA]** Johnson, Near, et al. *CHORUS: A Programming Framework for Building Scalable Differential Privacy Mechanisms.* IEEE EuroS&P, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
