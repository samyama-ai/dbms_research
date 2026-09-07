---
id: 26-cardinality-estimation/robust-plans-under-uncertainty
title: "Robust Optimization Under Estimation Uncertainty"
topic: 26-cardinality-estimation
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Robust Optimization Under Estimation Uncertainty

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/robust-plans-under-uncertainty` · **Status:** partially-solved

## 1. Problem Statement

A query optimizer chooses a plan to minimize cost, but cost depends on cardinalities that are only *estimated* and may be wrong by orders of magnitude. **Robust optimization** chooses a plan that is good not just at the point estimate but across the *plausible range* of true cardinalities.

Variants:

- **Min-max (worst-case):** pick plan $p$ minimizing $\max_{\mathbf c\in U} \mathrm{cost}(p,\mathbf c)$ over an uncertainty set $U$ of cardinality vectors.
- **Min-max regret:** minimize $\max_{\mathbf c\in U}\big[\mathrm{cost}(p,\mathbf c)-\mathrm{cost}(p^*_{\mathbf c},\mathbf c)\big]$, i.e. the gap to the best plan had we known $\mathbf c$.
- **Adaptive / runtime:** defer choices and re-optimize using observations gathered during execution (parametric / adaptive query processing).
- **Risk-aware:** minimize a risk functional (e.g. CVaR / expected cost) over a probability distribution on $\mathbf c$.

## 2. Mathematical Foundations

Let $\mathbf c=(c_1,\dots,c_k)$ be the unknown true cardinalities of plan sub-expressions, and $\mathrm{cost}(p,\mathbf c)$ a cost model. Given an uncertainty set $U\subseteq\mathbb R_{\ge0}^k$ (a box from per-node intervals, or an ellipsoid, or a finite scenario set), robust objectives are:

$$p_{\text{rob}}=\arg\min_{p\in\mathcal P}\ \max_{\mathbf c\in U}\ \mathrm{cost}(p,\mathbf c), \qquad p_{\text{regret}}=\arg\min_{p}\ \max_{\mathbf c\in U}\ \big[\mathrm{cost}(p,\mathbf c)-\mathrm{OPT}(\mathbf c)\big].$$

**Parametric query optimization (PQO)** partitions the parameter space into *plan-optimality regions* where one plan is optimal; the number of distinct optimal plans over a $d$-dimensional selectivity space can be exponential, but is often small in practice. Geometrically, with a linear cost model each plan is a hyperplane over selectivity space and the optimal-plan map is the lower envelope of an arrangement. **Plan diagrams** (Picasso, Reddy–Haritsa VLDB 2005) visualize this and motivate *plan-reduction*: swallow small regions into a neighbor at bounded cost inflation $\lambda$ (anorexic reduction), trading optimality for robustness/stability.

The plan search space itself is the System R / dynamic-programming lattice (Selinger et al., SIGMOD 1979); robustness layers a worst-case/regret objective over it.

## 3. State of the Art (SOTA)

- **Plan-region theory:** plan diagrams + anorexic reduction (Reddy–Haritsa 2005; Harish–Darera–Haritsa, VLDB 2007/2008) show a few plans cover most of selectivity space within 20% cost.
- **Least-expected-cost & robust plans:** Chu–Halpern–Seshadri (ICDE 1999) on least-expected-cost optimization; **Babcock–Chaudhuri (SIGMOD 2005)** robust query processing trading mean cost for predictability.
- **Adaptive query processing:** Eddies (Avnur–Hellerstein, SIGMOD 2000), mid-query re-optimization (Kabra–DeWitt, SIGMOD 1998; Markl et al. POP, VLDB 2004), and **smooth scan / g-join** robust operators.
- **Bounding-driven robustness:** pessimistic CE (Cai et al. 2019) makes the optimizer prefer plans safe under upper-bounded cardinalities — effectively a tractable robust surrogate.
- **Systems:** SQL Server "Adaptive Query Processing" (interleaved execution, adaptive joins), Oracle adaptive plans — production-grade partial solutions.

## 4. Upper Bound

- **PQO structure:** with a piecewise-linear cost model, optimal-plan regions are convex polytopes; the robust min-max problem over a *box* $U$ reduces to evaluating each candidate at the box corner that maximizes its cost — polynomial *per candidate plan*, but the candidate set is exponential, so overall it stays in the System-R DP regime.
- **Anorexic reduction:** plan-set reduction to a robust subset with $\le \lambda$ cost inflation is computable greedily; empirically $\lambda\approx 1.2$ suffices.
- **Adaptive bound:** re-optimization with $O(\log)$ checkpoints gives provable competitive bounds for some operator classes (e.g. competitive ripple/adaptive join orders) but no general guarantee.

## 5. Lower Bound

- **Hardness of join order:** even the *non-robust* optimal join-order problem is NP-hard for general (cyclic/cross-product) query graphs (Ibaraki–Kameda 1984; Cluet–Moerkotte), so robust variants are at least as hard.
- **Min-max regret:** robust/regret discrete optimization is typically NP-hard even when the nominal problem is easy (Kouvelis–Yu); for join ordering the regret-robust version inherits this.
- **Adaptivity limits:** online plan selection without lookahead has competitive-ratio lower bounds; no online algorithm can match the offline optimum given adversarial cardinality revelation (information-theoretic).

## 6. The Gap

**Partially solved.** Practically effective heuristics exist (plan reduction, adaptive joins, pessimistic bounds) and ship in real systems. What's missing: (1) a *principled* uncertainty set $U$ derived from calibrated CIs (links to the CI problem in this topic) rather than ad-hoc; (2) tractable regret-optimal join ordering with guarantees; (3) a unified theory connecting estimation-error magnitude to plan-cost robustness. The gap between "works empirically" and "provably robust within a stated uncertainty model" is the open core.

## 7. Current Research (as of June 2026)

- Uncertainty-aware optimizers consuming intervals/distributions from conformal or pessimistic CE and optimizing CVaR/worst-case cost *(frontier — verify)*.
- Learned-yet-safe optimizers (Bao, Balsa, Lero) that hedge model risk with bandit/RL exploration and guardrails; groups at MIT (Kraska, Marcus), TUM (Neumann, Kemper), IISc (Haritsa).
- Robust operator design (adaptive hash/merge selection, smooth scan) and re-optimization triggers driven by runtime cardinality feedback (DB2 LEO-style learning optimizers).
- Theory of plan-diagram complexity and provable anorexic-reduction bounds.

## 8. Future Work

- Tight coupling of calibrated uncertainty sets to regret-bounded plan choice.
- Tractable approximation algorithms for min-max-regret join ordering with ratio guarantees.
- End-to-end benchmarks scoring tail latency / worst-case regret, not mean runtime.
- Provably-safe learned optimizers that never regress below the classical plan.

## 9. Key References

- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099) — [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[SOTA]** Babcock, Chaudhuri. *Towards a Robust Query Optimizer: A Principled and Practical Approach.* SIGMOD, 2005. — [DOI](https://doi.org/10.1145/1066157.1066172) — [DBLP](https://dblp.org/rec/conf/sigmod/BabcockC05.html)
- **[SOTA]** Reddy, Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005; Harish, Darera, Haritsa. *On the Production of Anorexic Plan Diagrams.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ReddyH05.html)
- **[Foundational]** Avnur, Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335420) — [PDF](https://dsf.berkeley.edu/cs286/papers/eddies-sigmod2000.pdf)
- **[Foundational]** Kabra, DeWitt. *Efficient Mid-Query Re-Optimization of Sub-Optimal Query Execution Plans.* SIGMOD, 1998. — [DOI](https://doi.org/10.1145/276304.276315)
- **[SOTA]** Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838) — [DBLP](https://dblp.org/rec/conf/sigmod/MarcusNMTAK21.html)
- **[Survey]** Kouvelis, Yu. *Robust Discrete Optimization and Its Applications.* Springer, 1997. — [DOI](https://doi.org/10.1007/978-1-4757-2620-6)

## 10. Worked Example

One uncertain cardinality $c$ (true value unknown, uncertainty set $U=[100, 10{,}000]$) and two candidate plans:

- $p_1$ (hash join): $\mathrm{cost}(p_1,c)=5000$, flat in $c$ (build side fixed).
- $p_2$ (index nested-loop): $\mathrm{cost}(p_2,c)=2c$, linear in $c$.

The point estimate is $\hat c=500$, giving $\mathrm{cost}(p_2)=1000<5000$, so the nominal optimizer picks $p_2$.

**Min-max (worst-case)** over $U$: $\max_{c\in U}\mathrm{cost}(p_1)=5000$; $\max_{c\in U}\mathrm{cost}(p_2)=2\cdot10{,}000=20{,}000$. So $p_\text{rob}=p_1$ — the robust choice abandons the nominally cheaper $p_2$ because it is catastrophic if $c$ is large.

**Min-max regret:** the plans tie at $2c=5000\Rightarrow c=2500$ (the decision boundary). For $c<2500$, $p_2$ is optimal; for $c>2500$, $p_1$ is. Regret of $p_1$: worst at $c=100$, $5000-200=4800$. Regret of $p_2$: worst at $c=10{,}000$, $20{,}000-5000=15{,}000$. So $p_\text{regret}=p_1$ (regret $4800$).

This single boundary at $c=2500$ is exactly a plan-diagram cell wall; anorexic reduction would keep just one of these plans if the other's region inflates cost by $\le\lambda\approx1.2$.

---
*Part of the [DBMS Research catalog](../../README.md).*
