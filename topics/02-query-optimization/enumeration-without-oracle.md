---
id: 02-query-optimization/enumeration-without-oracle
title: "Plan enumeration without cardinality oracle"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Plan enumeration without cardinality oracle

> **Topic:** Query Optimization · **ID:** `02-query-optimization/enumeration-without-oracle` · **Status:** open

## 1. Problem Statement

Classical cost-based plan enumeration (Selinger-style) assumes an *oracle* that returns a single point cardinality estimate $\hat{n}_S$ for every intermediate subexpression $S$. In practice these estimates are systematically wrong — error grows multiplicatively with join depth, and the optimizer's plan ranking is dominated by these errors rather than by the cost model. This problem asks: **how do we enumerate and select plans when no reliable point cardinality is available?** Instead of a single number, the optimizer is given, per subexpression, either (a) provable upper/lower **bounds** on output size, or (b) a **distribution** over possible cardinalities.

- **Decision variant:** Given bound functions and a cost budget $B$, does there exist a plan whose cost is $\le B$ under all admissible cardinality assignments?
- **Optimization variant:** Find the plan minimizing worst-case cost, expected cost, or a risk functional (e.g., CVaR) over the admissible cardinality set.
- **Counting/enumeration variant:** Enumerate the set of plans that are optimal for *some* admissible cardinality assignment (the robust analogue of the parametric plan set).

"Solving" means producing a plan with a provable guarantee (worst-case ratio, regret bound, or probabilistic tail bound) relative to the unknown true cardinalities — not merely a heuristic that "works on TPC-H."

## 2. Mathematical Foundations

Let a query be a hypergraph $H=(V,E)$ over relations $V$ with join predicates $E$. For a subset $S\subseteq V$, the AGM bound gives a tight worst-case output size $\mathrm{AGM}(S)=\prod_e R_e^{x_e}$ where $\mathbf{x}$ is an optimal fractional edge cover of the subhypergraph induced by $S$; this is a **provable upper bound** computable without data statistics beyond relation sizes. With degree constraints / functional dependencies, the polymatroid (entropic) bound of Khamis–Ngo–Suciu tightens this. These give the bound oracle of variant (a).

For the distributional variant, model each $|S|$ as a random variable; selectivities compose via assumed (in)dependence, and the optimizer minimizes $\mathbb{E}[\text{cost}]$ or $\inf_t\{t:\Pr[\text{cost}>t]\le\alpha\}$. The robust-optimization formulation seeks
$$\min_{p\in\mathcal{P}}\ \max_{n\in\mathcal{U}}\ \mathrm{cost}(p,n),$$
where $\mathcal{U}$ is an uncertainty set of admissible cardinality vectors and $\mathcal{P}$ the plan space. Minimizing **regret** $\mathrm{cost}(p,n)-\min_{p'}\mathrm{cost}(p',n)$ instead yields the minimax-regret plan. Connections: this is a two-stage robust combinatorial optimization problem, generally harder than its nominal counterpart, and ties to online learning when cardinalities are revealed incrementally during execution.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Pessimistic cardinality estimation — replacing estimates with AGM/polymatroid upper bounds — gives plans with *bounded* intermediate sizes. Cai, Balazinska & Suciu's *pessimistic cardinality estimator* (SIGMOD 2019) and the Khamis–Ngo–Suciu degree-bound framework (PODS 2017) are the canonical bound oracles.
- **Systems SOTA:** *SafeBound* (Deeds et al., SIGMOD 2023) makes pessimistic bounds practical with compressed degree sequences; learned estimators (MSCN, *NeuroCard*, *FactorJoin*) target accuracy but provide no worst-case guarantee. Robust/risk-aware selection appears in *Robust Query Optimization* lineage (Babcock–Chaudhuri SIGMOD 2005) and least-expected-cost plans (Chu, Halpern, Seshadri).

## 4. Upper Bound

Using AGM bounds as the cardinality oracle, a plan can be selected whose every intermediate result is provably at most its AGM size, so cost-model evaluation is exact-on-bounds; enumeration cost is that of standard DP (Section *dp-enumeration-scaling*), i.e. $O(3^n)$ time / $O(2^n)$ space for $n$ relations in the RAM model. The selected plan is worst-case optimal *up to the looseness of the bound*. With minimax-regret and a finite uncertainty set $\mathcal{U}$ of size $m$, the robust plan is computable in $O(m\cdot|\mathcal{P}|)$ — polynomial only when $\mathcal{P}$ is succinctly enumerable.

## 5. Lower Bound

Join ordering is NP-hard for general query graphs even with *exact* cardinalities (Ibaraki–Kameda 1984; Cluet–Moerkotte for cross-products), so the bound-/distribution-based variants inherit NP-hardness. Minimax-regret combinatorial optimization is $\Sigma_2^p$-hard in general (Aissi–Bazgan–Vanderpooten survey), strictly harder than the nominal problem under standard assumptions. Information-theoretically, no estimator reading $o(N)$ bits of a relation can bound multi-join selectivity to within any constant factor in the worst case (adversarial data distributions), making purely-sampling oracles provably unreliable for deep joins.

## 6. The Gap

The gap is twofold. (1) **Tightness:** AGM/polymatroid upper bounds are worst-case-tight but can be orders of magnitude above true cardinality on real data, so a worst-case-optimal-on-bounds plan may be far from runtime-optimal — there is no matching lower bound certifying the chosen plan is good for *the actual* data. (2) **Robust complexity:** between the polynomial nominal optimum and the $\Sigma_2^p$ minimax-regret formulation lies an unmapped landscape; we lack tractable uncertainty-set shapes $\mathcal{U}$ for which robust plan selection is provably polynomial while remaining useful. Closing it likely requires data-dependent bound oracles with calibrated tightness plus a complexity classification of regret minimization over realistic $\mathcal{U}$.

## 7. Current Research (as of June 2026)

Active directions: (i) **learned bounds with guarantees** — combining ML estimators with pessimistic fallbacks so the output is always an upper bound (Suciu, Balazinska groups, UW); (ii) **conformal-prediction cardinality intervals** giving distribution-free coverage, fed into risk-aware selection *(frontier — verify)*; (iii) **bound-aware enumeration** integrating SafeBound-style oracles directly into DP/Cascades pruning (Moerkotte/Neumann lineage); (iv) factorized and entropic bounds for cyclic queries (Khamis, Ngo, Suciu, Olteanu). A recurring frontier theme is replacing the "single number" interface between estimation and search with an interval/distribution interface end-to-end *(frontier — verify)*.

## 8. Future Work

- A complexity dichotomy for robust/minimax-regret join ordering as a function of uncertainty-set geometry.
- Bound oracles that are simultaneously worst-case-sound and average-case-tight, with provable calibration on real workloads.
- End-to-end optimizer architectures where cardinality *distributions* (not points) propagate through enumeration and into adaptive re-optimization.
- Lower bounds certifying that no plan can beat the chosen one for the observed-data class.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. — [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[SOTA]** Deeds, Suciu, Balazinska, et al. *SafeBound: A Practical System for Generating Cardinality Bounds.* SIGMOD, 2023. — [arXiv](https://arxiv.org/abs/2211.09864)
- **[Foundational]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS, 2017. — [arXiv](https://arxiv.org/abs/1612.02503)
- **[Survey]** Aissi, Bazgan, Vanderpooten. *Min–max and min–max regret versions of combinatorial optimization problems: A survey.* EJOR, 2009. — [DOI](https://doi.org/10.1016/j.ejor.2008.09.012)

## 10. Worked Example

Triangle query $R(a,b)\bowtie S(b,c)\bowtie T(c,a)$, each relation of size $N$. The **AGM bound** uses the fractional edge cover: assigning $x_e=\tfrac12$ to all three edges covers every vertex ($\tfrac12+\tfrac12=1$ at $a,b,c$), giving $\mathrm{AGM}=N^{1/2}\cdot N^{1/2}\cdot N^{1/2}=N^{3/2}$. So no plan's final output can exceed $N^{3/2}$ tuples — a guarantee that needs *only the relation sizes*, no statistics.

Now compare the **pairwise** sub-join $R\bowtie S$: an oracle-free upper bound is the product $N\cdot N=N^2$, since the cover of the 2-edge sub-hypergraph puts $x=1$ on each. An optimizer choosing join order to minimize worst-case intermediates therefore prefers any plan whose largest guaranteed intermediate is $N^{3/2}$ over the binary plan with an $N^2$ blow-up — motivating worst-case-optimal multiway joins. If true data has only $N$ triangle results, the $N^{3/2}$ bound is loose by $\sqrt{N}$: the "tightness gap" of Section 6 made concrete.

---
*Part of the [DBMS Research catalog](../../README.md).*
