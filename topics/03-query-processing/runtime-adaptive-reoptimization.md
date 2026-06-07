---
id: 03-query-processing/runtime-adaptive-reoptimization
title: "Robust runtime adaptivity (eddies redux)"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Robust runtime adaptivity (eddies redux)

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/runtime-adaptive-reoptimization` · **Status:** empirically-open

## 1. Problem Statement

Static cost-based optimization commits to one plan before execution; when cardinality estimates are wrong (the common case for multi-join, correlated predicates), the plan can be catastrophically bad. **Eddies** (Avnur–Hellerstein, 2000) replaced the fixed plan with a tuple-router that adaptively re-orders operators *during* execution. The enduring problem: *design a mid-query re-routing / re-optimization mechanism that adapts to observed data statistics and provably never performs (much) worse than the best static plan — and ideally approaches the best plan in hindsight — while keeping routing/bookkeeping overhead low.*

Variants: (a) **decision** — detect that the current plan is sub-optimal and worth switching; (b) **optimization/regret** — minimize total work relative to the best static plan (competitive ratio) or the best plan in hindsight (online-learning regret); (c) **no-regression guarantee** — the strict requirement that adaptivity never makes a query slower than its static plan beyond a bounded factor; (d) **stateful operators** — re-routing around pipeline breakers (hash builds, sorts) where switching strands intermediate state. The "redux" framing asks for the robustness guarantees eddies lacked.

## 2. Mathematical Foundations

Model execution as routing each tuple through a permutation of selection/join operators; the *eddy* learns a routing policy online. This is naturally an **online learning / multi-armed bandit / experts** problem: each candidate operator order is an "expert," costs are revealed as tuples flow, and one seeks **sublinear regret** $R_T = \sum_t c_t(\pi_t) - \min_{\pi^\star}\sum_t c_t(\pi^\star)$ against the best fixed routing $\pi^\star$. **Competitive analysis** frames the no-regression goal as a competitive ratio $\le \rho$ versus the offline-optimal static plan. The selectivity/cost surface relates to the **AGM bound** and submodular coverage of join predicates. A key obstacle is that switching plans wastes *sunk* intermediate state (built hash tables, partial sorts), so the online problem has **switching/movement costs**, linking to **metrical task systems** and **online algorithms with reconfiguration cost**. Lottery scheduling / ticket-based routing gives the original eddy its policy.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Online-learning regret bounds exist for adaptive *selection ordering* (filters) — the "pipelined filter ordering" problem has near-optimal competitive and regret results (Babu et al.; Condon et al.; Kaplan–Kushilevitz–Mansour) — but **adaptive join** re-ordering with stateful operators lacks comparable provable guarantees. **Systems-SOTA:** Eddies + SteMs (Raman et al.); **mid-query re-optimization** (Kabra–DeWitt, 1998; Markl et al. POP/progressive optimization, 2004); **Adaptive Query Execution (AQE)** in Spark (re-plans stage boundaries from runtime stats); look-ahead information passing and runtime cardinality feedback in SQL Server / Oracle adaptive plans; DB2 LEO learning optimizer. Modern engines re-optimize at *materialization points* (stage/breaker boundaries), which sidesteps mid-pipeline state loss but limits adaptivity granularity.

## 4. Upper Bound

For **selection (filter) ordering**, online algorithms achieve $O(1)$-competitive or $\sqrt{T}$-style regret against the best static order under stochastic/adversarial selectivities (RAM model, per-tuple routing). **Re-optimization at materialization boundaries** trivially guarantees no-regression *for the remaining sub-plan* because committed work is sunk and the new sub-plan is re-costed with exact intermediate cardinalities — Spark AQE and POP exploit this. For full adaptive joins, the best known *guaranteed* result is the boundary-restricted one; no general mid-pipeline algorithm with a proven competitive ratio against the best static *join* plan is known. Empirically, AQE and POP avoid the worst static blowups on skewed/correlated workloads.

## 5. Lower Bound

Online filter ordering has matching competitive lower bounds (the $O(1)$-competitive results are tight up to constants). For adaptive join re-routing with **switching/state costs**, lower bounds from **metrical task systems** imply that any algorithm paying reconfiguration cost suffers $\Omega(k)$ competitive overhead in the number of operators $k$ in adversarial sequences — so *strict* no-regression with full mid-pipeline freedom is provably impossible without bounding switch cost. Cardinality estimation itself is information-theoretically hard (can require seeing $\Omega(n)$ tuples to distinguish skew), bounding how early any adaptive scheme can react. These are online-competitive and information-theoretic barriers, not NP-hardness.

## 6. The Gap

Filters: essentially **closed** (tight regret/competitive bounds). Joins: **empirically-open** — production systems (Spark AQE, POP, adaptive plans) demonstrably reduce catastrophic regressions, but there is *no proof* that mid-query join re-optimization never regresses below the static plan beyond a bounded factor, and the metrical-task-system lower bound says unrestricted mid-pipeline switching *cannot* be strictly no-regret. The gap is between strong empirical robustness at coarse (materialization-boundary) granularity and the absence of a fine-grained mechanism with a provable competitive ratio that accounts for sunk hash/sort state.

## 7. Current Research (as of June 2026)

(1) **Adaptive Query Execution** maturing in Spark/Photon/Databricks and cloud warehouses, expanding re-optimization triggers beyond shuffle boundaries. (2) **Learned & robust optimization** — Bao, Balsa, LEO-style feedback, and "robust plan" selection that bounds worst-case regret over an uncertainty set rather than reacting online. (3) **Bandit/RL formulations** of operator routing with regret analysis (revisiting eddies with modern online-learning theory). (4) **Parametric / robust cost models** that pre-compute switch-safe plan families. Groups: Hellerstein (Berkeley) lineage, the Spark/Databricks AQE team, Marcus/Kraska (MIT) on learned/robust optimization, Markl (TU Berlin). *(frontier — verify)* 2025–2026 work claims regret-bounded adaptive join routing for restricted (acyclic, bounded-width) queries; general no-regression remains unproven.

## 8. Future Work

- A mid-query join re-optimization algorithm with a *proven* competitive ratio vs. the best static plan, charging for sunk operator state.
- Robust-optimization formulations bounding worst-case regret over a cardinality-uncertainty set (provable no-catastrophe).
- Finer re-optimization granularity than stage boundaries without losing built state (incremental hash-table migration).
- Tight characterization of which query classes admit strict no-regression adaptivity.
- Unified theory linking eddies, AQE, and online learning with switching costs.

## 9. Key References

- **[Foundational]** Avnur, Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD 2000. — [DOI](https://doi.org/10.1145/342009.335420)
- **[Foundational]** Kabra, DeWitt. *Efficient Mid-Query Re-Optimization of Sub-Optimal Query Execution Plans.* SIGMOD 1998. — [DOI](https://doi.org/10.1145/276304.276315)
- **[SOTA]** Markl, Raman, Simmen, Lohman, Pirahesh. *Robust Query Processing through Progressive Optimization.* SIGMOD 2004. — [DOI](https://doi.org/10.1145/1007568.1007642)
- **[SOTA]** Babu, Motwani, Munagala, Nishizawa, Widom. *Adaptive Ordering of Pipelined Stream Filters.* SIGMOD 2004. — [DOI](https://doi.org/10.1145/1007568.1007615)
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Learning to Steer Query Optimizers.* SIGMOD 2021. — [arXiv](https://arxiv.org/abs/2004.03814) — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** Armbrust et al. *Spark SQL / Adaptive Query Execution.* SIGMOD 2015 + Databricks AQE writeups. — [DOI](https://doi.org/10.1145/2723372.2742797)
- **[Survey]** Deshpande, Ives, Raman. *Adaptive Query Processing.* Foundations and Trends in Databases, 2007. — [DOI](https://doi.org/10.1561/1900000001)

## 10. Worked Example

**Adaptive filter ordering.** A stream passes through two commutative filters $\sigma_1$ (cost $c_1=1$, selectivity $s_1$) and $\sigma_2$ (cost $c_2=1$, selectivity $s_2$). The optimal static order puts the more selective filter first. Suppose the optimizer assumed $s_1=0.1, s_2=0.9$ and chose order $\sigma_1\!\to\!\sigma_2$, expected cost per tuple $= c_1 + s_1 c_2 = 1 + 0.1 = 1.1$.

At runtime the data is correlated and true selectivities are reversed: $s_1=0.9, s_2=0.1$. The committed static order now costs $1 + 0.9 = 1.9$ per tuple, whereas $\sigma_2\!\to\!\sigma_1$ would cost $1 + 0.1 = 1.1$. An eddy observing the first few hundred tuples flips the routing, recovering near $1.1$.

For **filters this is closed** — online algorithms achieve $O(1)$-competitive cost. For **joins**, flipping build/probe sides mid-pipeline strands a built hash table (sunk cost); a metrical-task-system lower bound shows strict no-regression is then impossible, which is the open gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
