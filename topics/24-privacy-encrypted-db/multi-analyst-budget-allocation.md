# Multi-Analyst Fair Budget Allocation

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/multi-analyst-budget-allocation` · **Status:** open

## 1. Problem Statement

A differentially private data system has a single, finite **global privacy budget** $\varepsilon_{\text{global}}$ (or $\rho_{\text{global}}$ in zCDP) for the dataset's lifetime, because privacy loss *composes across everyone who ever queries it*. When **multiple analysts** (teams, departments, external researchers) share that dataset, they compete for slices of this budget. The problem is to design an **allocation mechanism** that divides the global budget across analysts and their query workloads so as to (a) be **fair** (no analyst is starved; analysts with similar needs get similar accuracy), (b) be **incentive-compatible / truthful** (analysts cannot game their stated accuracy needs to grab more budget), and (c) maximize **overall utility** — all while the total spend never exceeds $\varepsilon_{\text{global}}$.

Variants:
- **Static allocation (optimization):** split a known budget across $k$ analysts with known workloads to maximize a welfare function.
- **Online/dynamic:** analysts arrive over time with unknown future demand; allocate without exhausting the budget prematurely.
- **Mechanism-design (game-theoretic):** elicit private valuations truthfully; charge "prices" in budget; guarantee fairness axioms.

## 2. Mathematical Foundations

Each analyst $i$ has a workload whose error is a decreasing function of allocated budget $\rho_i$, e.g. for Gaussian/zCDP mechanisms $\mathrm{err}_i(\rho_i)=c_i/\sqrt{\rho_i}$, with valuation $v_i(\rho_i)$. Composition gives the hard constraint $\sum_i \rho_i \le \rho_{\text{global}}$ (zCDP composes additively; under $(\varepsilon,\delta)$ use advanced/numerical composition). The allocation problem is then a **constrained welfare optimization**
$$\max_{\rho\ge 0}\ \sum_i w_i\,U_i(\rho_i)\quad\text{s.t.}\ \sum_i\rho_i\le \rho_{\text{global}},$$
which, for concave $U_i$, is a convex program whose KKT conditions yield a **water-filling** solution. Fairness brings in axioms from fair division — **proportionality**, **envy-freeness**, **max-min (egalitarian) / Nash-bargaining** objectives — applied to a *divisible but non-replenishable* resource. Incentives bring in **mechanism design**: budget acts as money, and one seeks truthful (VCG-like) or strategyproof allocations. Key subtlety distinguishing this from ordinary resource allocation: spent privacy is **irreversible** and **externality-laden** (one analyst's queries raise everyone's privacy loss).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **DPella / accuracy-aware budgeting** and the line on *privacy budget as a shared resource* formalize allocation, but a complete truthful-and-fair mechanism is not settled. Fair-division theory (Nash welfare, max-min) and DP composition are individually mature; their combination for privacy budget is recent. Pujol et al. (*Fair Decision Making Using Privacy-Protected Data*, FAT\* 2020) studies fairness *of outcomes* under DP; the *allocation-fairness* angle is newer.
- **Systems-SOTA:** **PrivateSQL** and **Tumult Analytics** track per-query budget against a global cap (an odometer), and the **U.S. Census / TopDown** allocates budget across query tiers (geographic levels, query types) by fixed proportions chosen via policy — effectively a hand-tuned static allocation. **Sage/PrivateKube** (Lécuyer et al., SOSP 2019) treats privacy budget as a **schedulable Kubernetes resource** with admission control — the closest to a systems-grade allocator.

## 4. Upper Bound

For concave per-analyst utilities, the static welfare-optimal allocation is a convex program solvable in polynomial time (water-filling, closed form for $U_i=-c_i/\sqrt{\rho_i}$). PrivateKube gives an online admission-control scheme with formal guarantees that the global budget is never violated while maximizing accepted demand under a "Rényi DP block" abstraction. Nash-welfare-optimal divisions are computable for concave utilities (Eisenberg–Gale convex program), giving a *proportional and envy-free* allocation in poly-time for this special structure.

## 5. Lower Bound

No-free-lunch results in fair division apply: **truthfulness, Pareto-efficiency, and proportionality cannot in general be simultaneously guaranteed** for indivisible or non-quasi-linear settings (Gibbard–Satterthwaite / impossibility for strategyproof efficient mechanisms without money). For *online* arrival with unknown demand, the irreversibility of privacy spend forces a **competitive-ratio lower bound**: any online allocator that commits budget early can be forced into an $\Omega(\log k)$-type loss versus the offline optimum (analogous to online matching/AdWords lower bounds). Welfare maximization with combinatorial workload interactions (shared queries reducing total sensitivity) is NP-hard.

## 6. The Gap

The gap is **genuinely open**. We have (a) clean convex-program allocators for the *cooperative, truthful-valuation* case and (b) admission-control systems (PrivateKube) that respect the cap — but **no mechanism that is simultaneously truthful, fair (envy-free/max-min), and welfare-near-optimal** under strategic analysts and online arrival. Missing pieces: a pricing of irreversible privacy that internalizes the negative externality, and competitive-ratio-optimal online allocators. Closing it likely needs combining DP composition accounting with mechanism design for a non-replenishable, externality-bearing resource.

## 7. Current Research (as of June 2026)

- Treating privacy budget as a **schedulable cloud resource** with SLA-style fairness (PrivateKube lineage), extended to multi-tenant DP warehouses *(frontier — verify)*.
- Mechanism-design for truthful elicitation of accuracy needs, pricing budget to internalize composition externalities *(frontier — verify)*.
- Census Bureau and national statistical offices publishing *budget-allocation rationales* across query tiers as policy artifacts — empirical input to the theory.
- Groups: Lécuyer/Geambasu (systems), Machanavajjhala/He (DP-SQL), and fair-division theorists (Nash welfare) crossing into DP.

## 8. Future Work

- Truthful, envy-free, online budget allocators with proven competitive ratios.
- Pricing privacy loss as a market (externality-aware) rather than fixed quotas.
- Cross-analyst query sharing / caching to reduce total composed spend.
- Fairness *across populations* (group-budget) in addition to across analysts.

## 9. Key References

- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** Rogers, Roth, Ullman, Vadhan. *Privacy Odometers and Filters: Pay-as-you-Go Composition.* NeurIPS, 2016. — [arXiv](https://arxiv.org/abs/1605.08294)
- **[SOTA]** Lécuyer, Spahn, Vodrahalli, Geambasu, Hsu. *Privacy Accounting and Quality Control in the Sage Differentially Private ML Platform / PrivateKube.* SOSP, 2019. — [DOI](https://doi.org/10.1145/3341301.3359639) — [arXiv](https://arxiv.org/abs/1909.01502)
- **[SOTA]** Pujol, McKenna, Kuppam, Hay, Machanavajjhala, Miklau. *Fair Decision Making Using Privacy-Protected Data.* ACM FAT\*, 2020. — [DOI](https://doi.org/10.1145/3351095.3372872) — [arXiv](https://arxiv.org/abs/1905.12744)
- **[Foundational]** Eisenberg, Gale. *Consensus of Subjective Probabilities: The Pari-Mutuel Method (Nash welfare / market equilibrium).* Annals of Mathematical Statistics, 1959. — [DOI](https://doi.org/10.1214/aoms/1177706369)

## 10. Worked Example

A dataset has global zCDP budget $\rho_{\text{global}} = 1.0$. Three analysts share it; analyst $i$'s Gaussian-mechanism error is $\mathrm{err}_i(\rho_i) = c_i/\sqrt{\rho_i}$ with weights/scales $c_1=1,\;c_2=2,\;c_3=4$. We minimize total error $\sum_i c_i/\sqrt{\rho_i}$ subject to $\rho_1+\rho_2+\rho_3 = 1$.

**Water-filling via KKT.** Set the Lagrangian $\sum_i c_i\rho_i^{-1/2} + \lambda(\sum_i\rho_i - 1)$. Stationarity: $-\tfrac12 c_i\rho_i^{-3/2} + \lambda = 0 \Rightarrow \rho_i \propto c_i^{2/3}$.

Compute $c_i^{2/3}$: $1^{2/3}=1,\;2^{2/3}\approx1.587,\;4^{2/3}\approx2.520$; sum $\approx5.107$. Normalize:
$$\rho_1\approx0.196,\quad \rho_2\approx0.311,\quad \rho_3\approx0.493.$$

The analyst with the largest noise scale ($c_3=4$) rightly gets the most budget, but spread is sublinear in $c$ (exponent $2/3$, not $1$) — the convex program tempers, not amplifies, demand. Resulting errors: $1/\sqrt{0.196}\approx2.26$, $2/\sqrt{0.311}\approx3.59$, $4/\sqrt{0.493}\approx5.70$.

**Where it breaks:** if analyst 3 *lies*, overstating $c_3$ to grab more budget, nothing in this cooperative water-filling penalizes the misreport — that is exactly the truthfulness gap (Section 6) that a pricing/mechanism-design layer must close.

---
*Part of the [DBMS Research catalog](../../README.md).*
