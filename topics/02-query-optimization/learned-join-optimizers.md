# Learned/RL join-order optimizers vs. classical

> **Topic:** Query Optimization · **ID:** `02-query-optimization/learned-join-optimizers` · **Status:** empirically-open

## 1. Problem Statement
Join-order selection is the combinatorial core of query optimization: given a query over $n$ relations, choose a join tree (and methods) minimizing execution cost. Classical optimizers use **cost-based dynamic programming** (System-R/DPccp) or **transformation search** (Cascades/Volcano) over a cost model. **Learned join optimizers** instead frame plan search as a **sequential decision (reinforcement-learning) problem**: a policy $\pi$ builds the join tree step by step, trained to minimize predicted or measured cost.

The research question is sharp and **comparative**:
- *When* do learned/RL plan-search policies **beat** classical cost-based search (in plan quality, planning latency, robustness to estimation error)?
- *With what guarantees*? Classical DP is provably optimal w.r.t. its cost model; learned search trades that for speed and potential cost-model-independence. What can be guaranteed about a learned policy's regret or worst-case plan quality?

Variants: full plan generation (Neo/Balsa-style) vs. **steering** an existing optimizer (Bao-style hint selection) vs. learned **cardinality only** feeding classical search.

## 2. Mathematical Foundations
**Search-space size.** The number of join trees (with cross products) for $n$ relations is the Catalan-scaled $\frac{(2(n-1))!}{(n-1)!}$ (bushy); even linear trees give $n!/2$. DP collapses overlapping subproblems but is still exponential.

**MDP formulation.** State = set of joined subrelations (a partial plan); action = next join; reward = $-\text{cost}$ (terminal) or shaped per step. The optimal value function $V^\star$ satisfies Bellman optimality; a learned $\hat V$ or policy $\pi_\theta$ (often a tree/graph-NN) approximates it. This is **approximate dynamic programming**: the classical optimizer's DP table *is* exact value iteration over this MDP, so RL is a function-approximation relaxation of the same recursion.

**Guarantees.** Tabular value iteration is exact; with function approximation, error compounds — performance loss is bounded by $\tfrac{2\gamma\,\epsilon}{(1-\gamma)^2}$-style terms in $\|V^\star - \hat V\|_\infty$ (approximation error $\epsilon$). **Imitation learning / Balsa** uses a *safe* expert (a simple optimizer) to bootstrap, bounding worst-case regret early. No learned method provides a *cost-model-relative optimality* guarantee comparable to DP; their advantage must come from a **better implicit cost model** (learned from execution), not from better search.

## 3. State of the Art (SOTA)
- **Classical theory-SOTA:** DPccp (Moerkotte–Neumann, VLDB 2006) enumerates connected subgraph pairs optimally; adaptive/graph-aware DP and Cascades top-down search are the production baselines (PostgreSQL, SQL Server, Umbra, CockroachDB).
- **Learned systems-SOTA:**
  - **DQ / ReJOIN** (Krishnan et al.; Marcus–Papaemmanouil, 2018) — first RL join-order learners.
  - **Neo** (Marcus et al., VLDB 2019) — end-to-end learned optimizer.
  - **Balsa** (Yang et al., SIGMOD 2022) — learns *without* an expert cost model, bootstrapped by a minimal simulator, reaching expert quality safely.
  - **Bao** (SIGMOD 2021) — learned **steering** of the native optimizer; most deployment-friendly, with bandit guarantees.
  - **LOGER / RTOS / Lero** and **"Is Learned Query Optimization Ready?"**-style audits (2023–2024) benchmark these against PostgreSQL.

## 4. Upper Bound
- **Classical:** DPccp finds the cost-model-optimal bushy plan in time/space polynomial in the number of connected subgraph pairs (worst-case exponential, but optimal-by-construction) — an *exact* upper bound w.r.t. the cost model.
- **Learned:** empirical upper bounds — Bao/Balsa/Neo match or beat PostgreSQL/commercial plans on benchmarks (JOB, Stack, TPC) with **lower tail latency** and **much faster planning** at inference for large $n$ (amortized policy rollout vs. exponential DP). Approximate-DP theory bounds their *sub-optimality* by value-function approximation error, but no benchmark-independent worst-case guarantee exists.

## 5. Lower Bound
- **Optimal join ordering is NP-hard** for general query graphs (Ibaraki–Kameda for tree queries with certain cost functions; Cluet–Moerkotte for cross-product cost) — so *neither* classical nor learned search can be both optimal and polynomial in the worst case unless P = NP.
- **Estimation barrier:** any optimizer (learned or not) relying on cardinality estimates inherits worst-case-unbounded plan cost when estimates are adversarially wrong (no estimator achieves bounded multiplicative join-size error from limited statistics — communication/sketch lower bounds).
- **RL learnability:** without assumptions, sample-complexity lower bounds for policy learning are exponential in horizon; learned optimizers have *no* worst-case regret guarantee against the optimal plan.

## 6. The Gap
Genuinely open and **empirical**: learned optimizers *sometimes* beat classical search — chiefly by implicitly learning a better cost model from execution feedback and by amortizing search — but **inconsistently**, with regressions under workload shift, cold start, and rare/tail queries; and **without guarantees**. Classical DP keeps an unbeatable cost-model-relative optimality but is hostage to its cost model. The unresolved question is whether a *hybrid* can keep DP's guarantee while gaining learned robustness, and under what assumptions a learned policy admits a provable regret bound. Reproducibility audits (2023–2025) report mixed, setup-sensitive results — hence empirically-open.

## 7. Current Research (as of June 2026)
- **Hybrid/steering** approaches (Bao, Lero) dominate practical interest: keep classical search, learn to nudge it — better risk profile. *(frontier — verify)*
- **Safe/guaranteed RL** with fallback to classical plans when the policy is uncertain, giving bounded worst-case regret. *(frontier — verify)*
- **Foundation-model / LLM-assisted** plan reasoning and cross-database transfer of learned policies. *(frontier — verify)*
- Rigorous, standardized **benchmarks and audits** (JOB-extended, CEB, "ready?" studies) to settle the comparative question.
- Groups: Kraska/Marcus (MIT), Stoica/Yang (Berkeley, Balsa), Neumann/Moerkotte (TUM, classical), Alibaba/Microsoft learned-optimizer teams.

## 8. Future Work
- Provable regret bounds for learned plan search relative to the cost-model optimum.
- Robustness-first training (worst-case / distributionally-robust objectives) to kill tail regressions.
- Unified evaluation isolating *search* gains from *cost-model* gains.

## 9. Key References
- **[Foundational]** Moerkotte, Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm for the Generation of Optimal Bushy Join Trees (DPccp).* VLDB, 2006.
- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019.
- **[SOTA]** Yang, Chiang, Luan, et al. *Balsa: Learning a Query Optimizer Without Expert Demonstrations.* SIGMOD, 2022.
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[Survey]** Lehmann, Behr, et al. / Han, Wu, et al. *Is Learned Query Optimization Ready / A Comprehensive Benchmark.* VLDB, 2023–2024.

---
*Part of the [DBMS Research catalog](../../README.md).*
