---
id: 02-query-optimization/learned-join-optimizers
title: "Learned/RL join-order optimizers vs. classical"
topic: 02-query-optimization
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

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
- **[Foundational]** Moerkotte, Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm for the Generation of Optimal Bushy Join Trees (DPccp).* VLDB, 2006. — [DBLP](https://dblp.org/rec/conf/vldb/MoerkotteN06.html)
- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1904.03711)
- **[SOTA]** Yang, Chiang, Luan, et al. *Balsa: Learning a Query Optimizer Without Expert Demonstrations.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2201.01441)
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Survey]** C. Lehmann, P. Behr, et al. *Is Your Learned Query Optimizer Behaving As You Expect? A Machine Learning Perspective.* PVLDB, 2024. — [DOI](https://doi.org/10.14778/3654621.3654625)

## 10. Worked Example

**Search space vs. DP for $n=4$.** Number of bushy join trees (with cross products) is $\frac{(2(n-1))!}{(n-1)!}=\frac{6!}{3!}=\frac{720}{6}=120$; left-deep trees number $n!/2 = 12$. Naive enumeration scales super-exponentially.

**RL framing of the DP recursion.** The classical DP fills a table $V$ over subsets $S\subseteq\{R_1,R_2,R_3,R_4\}$: $V(S)=\min_{S'\subset S}\,[\,V(S')+V(S\setminus S')+\text{cost}(S'\!\bowtie\!S\setminus S')\,]$, exactly Bellman optimality over the MDP whose state is the joined subset. For $n=4$ there are $2^4-1=15$ non-empty subsets; DP is exact but its table is exponential in $n$.

**Approximation-error compounding.** A learned $\hat V$ with $\|V^\star-\hat V\|_\infty=\epsilon$ and discount $\gamma=0.9$ inflates the chosen-plan suboptimality by up to $\frac{2\gamma\epsilon}{(1-\gamma)^2}=\frac{1.8\epsilon}{0.01}=180\epsilon$. So a tiny per-step value error $\epsilon=0.5$ admits a worst-case plan-cost gap of $90$ — quantifying why learned policies, lacking DP's cost-model-relative optimality, can regress on tail queries.

---
*Part of the [DBMS Research catalog](../../README.md).*
