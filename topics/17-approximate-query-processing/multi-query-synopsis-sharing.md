---
id: 17-approximate-query-processing/multi-query-synopsis-sharing
title: "Multi-Query Synopsis Sharing"
topic: 17-approximate-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Multi-Query Synopsis Sharing

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/multi-query-synopsis-sharing` · **Status:** open

## 1. Problem Statement
Given a workload $\mathcal{W}=\{Q_1,\dots,Q_m\}$ of approximate queries (filters, group-bys, aggregates over various columns and join paths) and a total **space budget** $B$, design a *shared* collection of synopses — samples (uniform, stratified, measure-biased), sketches (CM/HLL/Theta), and histograms/wavelets — that jointly **minimizes aggregate error** across the workload, rather than optimizing each query in isolation. The same stratified sample can serve many group-bys; one Theta sketch can answer several distinct-count and set queries; but strata and sketch parameters tuned for one query hurt another. The problem is to allocate $B$ across synopsis *types, columns, and strata* so total (or worst-case) workload error is minimized.

Formal variants: the **optimization** variant minimizes $\sum_i \text{err}(Q_i\mid \mathcal{S})$ (or $\max_i$) subject to $\text{size}(\mathcal{S})\le B$; the **decision** variant asks if some $\mathcal{S}$ of size $\le B$ meets per-query error SLAs; and an **online/workload-drift** variant adapts $\mathcal{S}$ as the query distribution shifts. The catch is that errors *interact*: shrinking a stratum to fund another sketch changes many queries' errors simultaneously, so the allocation is a coupled combinatorial optimization, not $m$ independent ones. It is open: production systems pick synopses greedily/heuristically with no approximation guarantee on workload-wide error.

## 2. Mathematical Foundations
Let synopsis configuration $\mathcal{S}$ have per-query error $e_i(\mathcal{S})$. For sample-based answers, $e_i\propto 1/\sqrt{n_i}$ where $n_i$ is the *effective* sample count covering $Q_i$'s predicate/group; stratified allocation across $g$ groups under budget $n$ is the classic **Neyman allocation** $n_j\propto N_j\sigma_j$ minimizing variance — and extends to workloads where each group's *query frequency* $w_j$ weights its error. The multi-query objective $\sum_i w_i e_i$ is typically a **monotone, submodular** function of "synopsis elements selected," so the budgeted maximization of *error reduction* admits a $(1-1/e)$ greedy guarantee — when the reduction is genuinely submodular.

The hardness: choosing which strata/columns/sketch-cells to fund is a **budgeted maximum coverage / facility-location**-flavored problem (NP-hard), and cross-query coupling can violate strict submodularity (negative interactions when a shared sample is re-stratified). Information-theoretically, a single synopsis of size $B$ cannot simultaneously give low error on $m$ "orthogonal" queries whose answers require disjoint information — a *pigeonhole* limit linking $B$, $m$, and achievable per-query $\varepsilon$. Optimal sample design also connects to **D-/A-optimal experimental design** and to coresets (a weighted subset approximating all queries in a class).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Neyman/optimal stratified allocation for a known query distribution; coreset constructions giving $(1\pm\varepsilon)$ for whole *families* of queries with size independent of $n$; submodular greedy with $(1-1/e)$ for budgeted synopsis selection when reductions are submodular.
- **Systems-SOTA:** `BlinkDB` (EuroSys 2013) optimizes a *family* of stratified samples for a column-set workload under storage/latency budgets via a mixed-integer formulation; `STRAT`/`SciBORQ`/`AQUA` build workload-aware synopses; `VerdictDB` (SIGMOD 2018) and `DeepDB`/data-driven models share learned models across queries; commercial warehouses keep per-column `APPROX_*` sketches but do **not** jointly optimize a shared budget across the workload.

## 4. Upper Bound
For a fixed known workload distribution, Neyman allocation is the **optimal** variance-minimizing stratified sample (closed form). Budgeted synopsis selection with submodular error-reduction: greedy yields a $(1-1/e)$-approximation to the optimal workload error reduction in $O(mB)$ evaluations (Nemhauser–Wolsey–Fisher). Coresets give $(1\pm\varepsilon)$ guarantees for an entire query class with size $\mathrm{poly}(\tfrac1\varepsilon,\dim)$, independent of $n$. These hold in the RAM/sample-oracle model assuming the workload distribution is known or well-estimated.

## 5. Lower Bound
Optimal multi-synopsis selection is **NP-hard**: it captures budgeted maximum coverage / weighted set-cover, for which no polynomial algorithm beats $(1-1/e)$ unless P=NP (Feige's tightness for max-coverage). Information-theoretically, serving $m$ queries demanding disjoint information forces $B=\Omega(\sum_i \text{info}(Q_i))$ — a single shared synopsis cannot evade this *pigeonhole* lower bound, so worst-case workloads admit no small shared synopsis. When error reductions are *not* submodular (negative cross-query interaction), the $(1-1/e)$ guarantee provably fails, and no constant-factor approximation is known. These are NP-hardness and information-theoretic bounds.

## 6. The Gap
The closed cases (single known group-by → Neyman; submodular selection → $(1-1/e)$) do not cover real workloads, which mix synopsis *types* with non-submodular cross-query coupling, uncertain/shifting query distributions, and join paths. The open gap: **no approximation algorithm with a workload-wide error guarantee for the full heterogeneous, coupled problem**, and no tight characterization of when sharing is provably beneficial vs. when per-query synopses are forced. Closing it needs either a structural condition restoring submodularity or a new approximation framework for the coupled, multi-type budget allocation.

## 7. Current Research (as of June 2026)
Active directions: learned/data-driven models (`DeepDB`, sum-product networks) as *shared* synopses amortizing across a workload; workload-adaptive sample re-stratification under drift; coreset and sensitivity-sampling methods unifying multiple aggregate families; treating synopsis selection as online learning with regret bounds. *(frontier — verify)* Several 2025 systems claim joint optimization of mixed sketches+samples under one budget using learned cost models, but report empirical workload error rather than provable approximation ratios for the coupled objective.

## 8. Future Work
- Approximation algorithms with provable workload-error guarantees for heterogeneous, coupled synopsis sets.
- Structural conditions (when is multi-query error reduction submodular?) characterizing beneficial sharing.
- Online, drift-aware shared-synopsis maintenance with regret bounds against the best fixed allocation.

## 9. Key References
- **[Foundational]** Acharya, S., Gibbons, P., Poosala, V. *Congressional Samples for Approximate Answering of Group-By Queries.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335450)
- **[SOTA]** Agarwal, S., Mozafari, B., Panda, A., Milner, H., Madden, S., Stoica, I. *BlinkDB: Queries with Bounded Errors and Bounded Response Times.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[SOTA]** Hilprecht, B., Schmidt, A., Kulessa, M., Molina, A., Kersting, K., Binnig, C. *DeepDB: Learn from Data, Not from Queries!* VLDB, 2020. — [DOI](https://doi.org/10.14778/3384345.3384349) · [arXiv](https://arxiv.org/abs/1909.00607)
- **[Survey]** Chaudhuri, S., Ding, B., Kandula, S. *Approximate Query Processing: No Silver Bullet.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056097)

## 10. Worked Example

**Neyman vs. uniform allocation for a group-by workload.** A table has $g=2$ groups: group 1 with $N_1=900$ rows, std dev $\sigma_1=1$; group 2 with $N_2=100$ rows, $\sigma_2=9$. Workload weights are equal ($w_1=w_2$). Total sample budget $n=100$.

**Uniform/proportional split** by size: $n_1=90,\,n_2=10$. The per-group mean's variance is $\sigma_j^2/n_j$: group 1 gives $1/90\approx 0.011$, group 2 gives $81/10=8.1$ — the rare, high-variance group dominates total error $\approx 8.11$.

**Neyman allocation** sets $n_j\propto N_j\sigma_j$. Compute $N_1\sigma_1=900$, $N_2\sigma_2=900$ — equal, so $n_1=n_2=50$. Now variances are $1/50=0.02$ and $81/50=1.62$, total $\approx 1.64$ — a $\approx 5\times$ reduction over proportional, by funding the noisy small group. This is the closed-form optimum of Section 4.

The multi-query twist: a *second* query grouping by a different column needs its own stratification of the same sample. Re-stratifying for query 2 perturbs $n_1,n_2$ above — the coupling that breaks per-query optimality and makes the joint allocation NP-hard (Section 5).

---
*Part of the [DBMS Research catalog](../../README.md).*
