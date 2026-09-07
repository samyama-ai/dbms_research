---
id: 02-query-optimization/robust-plan-selection
title: "Robust plans minimizing worst-case suboptimality"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Robust plans minimizing worst-case suboptimality

> **Topic:** Query Optimization · **ID:** `02-query-optimization/robust-plan-selection` · **Status:** open

## 1. Problem Statement

Cardinality and selectivity estimates are uncertain; a plan optimal at the *point estimate* can be catastrophically bad if the true selectivities differ. **Robust plan selection** asks: given an uncertainty region $R$ in selectivity/parameter space, choose a single physical plan $P^\*$ that minimizes its *worst-case sub-optimality* over $R$, rather than its cost at a single point.

Formally, let $\text{cost}(P, s)$ be the cost of plan $P$ at selectivity vector $s \in R$, and let $\text{opt}(s)=\min_{P} \text{cost}(P,s)$. The **sub-optimality (regret)** of $P$ at $s$ is the ratio $\text{SubOpt}(P,s)=\text{cost}(P,s)/\text{opt}(s)$. We seek

$$P^\* = \arg\min_{P}\ \max_{s \in R}\ \frac{\text{cost}(P,s)}{\text{opt}(s)}.$$

Variants: **(a)** additive regret $\text{cost}(P,s)-\text{opt}(s)$ vs. multiplicative ratio; **(b)** single static plan vs. a small *set* of plans switched at runtime (links to Plan Bouquets); **(c)** decision variant — does a plan with worst-case ratio $\le \alpha$ exist over $R$? — vs. the optimization of $\alpha$.

## 2. Mathematical Foundations

The **POSP** (parametric optimal set of plans) partitions $R$ into regions, each owning the plan optimal there; the optimal-cost surface $\text{opt}(s)$ is the lower envelope of the per-plan cost hyperplanes/curves. For typical cost models, $\text{cost}(P,\cdot)$ is monotone and often *multilinear* in selectivities; on a single join's selectivity axis it is monotone, giving the **anorexic reduction** result: the POSP can be reduced to a small set of plans while keeping sub-optimality bounded by a small constant (e.g. $\lambda = 20\%$ inflation suffices to cut plan count drastically).

The min-max objective is a **robust optimization** / Chebyshev-center-style problem over a non-convex plan space (plans are discrete). Because $\text{opt}(s)$ is the *lower envelope* of an exponential set of plan-cost functions, evaluating worst-case ratio requires reasoning about *all* competing plans, not just $P$. Geometric duality and the structure of the **cost-doubling contours** (Dutt–Haritsa) provide the handle: a plan covering a cost contour band of multiplicative width $r$ guarantees worst-case ratio $\le r$ over that band.

Key theoretical objects: selectivity-space monotonicity (PCM — *plan cost monotonicity*), the **isocost contours** $IC_k=\{s:\text{opt}(s)=2^k\}$, and the bound $\text{MSO}\le 4\rho$ where $\rho$ is the maximal number of plans intersecting any contour.

## 3. State of the Art (SOTA)

**Theory-SOTA.** *Plan Bouquets* and its successors (Dutt, Haritsa; Karthik, Haritsa; *SpillBound*, *FrugalSpillBound*) give the strongest worst-case guarantees, achieving bounded MSO **without selectivity estimation** by executing a sequence of plans along cost-doubling contours. SpillBound delivers a structure-independent MSO bound of $D^2+3D$ for $D$ error-prone predicates and proves near-optimality of this approach within the estimation-free model.

**Systems-SOTA.** *Robust cardinality estimation* via uncertainty propagation (Babcock–Chaudhuri, SIGMOD 2005 — *least-expected-cost* plans), and least-expected-cost optimization in research prototypes. Commercial optimizers use *plan stability/baselines* (Oracle SQL Plan Management) and *hints* to avoid regressions — a pragmatic robustness surrogate, not min-max optimal.

## 4. Upper Bound

For the estimation-free, runtime-switching relaxation, **SpillBound** achieves worst-case MSO $\le D^2 + 3D$ where $D$ is the number of error-prone selectivity dimensions, *independent of query/data structure* — the best general upper bound. For a **single static plan** (no switching), the best general upper bound is the trivial one: the min-max-optimal plan can be found by enumerating POSP plans and evaluating each over $R$, giving an exact but exponential-time procedure; the achievable ratio is data/query dependent and can be unboundedly large in adversarial selectivity spaces. *Anorexic reduction* yields a constant-factor ($1+\lambda$) bounded plan set covering $R$, but the per-point single-plan ratio remains query-dependent.

## 5. Lower Bound

Within the estimation-free model, Dutt–Haritsa prove a matching $\Omega(\rho)$ lower bound on MSO for any deterministic scheme, and SpillBound's $\Theta(D^2)$ is shown near-optimal for structure-independent guarantees. For the **single static robust plan** problem, choosing the min-max plan is **NP-hard**: it embeds join-order optimization (already NP-hard, Ibaraki–Kameda for the general / cyclic case), and the worst-case ratio for any single plan can be forced arbitrarily large over a sufficiently rich $R$, an information-theoretic impossibility for static plans — motivating runtime switching.

## 6. The Gap

For the **runtime-switching** formulation the gap is essentially *closed*: SpillBound's $\Theta(D^2)$ matches the lower bound up to constants within the estimation-free model. For the **single static plan** min-max problem the gap is wide open: no polynomial approximation algorithm with a guaranteed ratio on the achievable worst-case sub-optimality is known, and there is no tight characterization of which uncertainty regions $R$ admit a low-regret static plan. Closing it requires either a hardness-of-approximation result or a structure-exploiting approximation for multilinear cost functions over polytope $R$.

## 7. Current Research (as of June 2026)

Active work: (i) **learned + robust hybrids** that shrink $R$ using calibrated ML estimators, then optimize within the smaller region (TUM, Microsoft, CMU); (ii) extensions of the bouquet/SpillBound line to higher dimensions and to compiled engines (Haritsa group, IISc); (iii) **distributionally-robust** formulations replacing the box $R$ with an ambiguity set (Wasserstein balls) and minimizing expected-worst-case cost *(frontier — verify)*; (iv) robustness as a learning objective in Bao-style steering, penalizing tail regressions. Connections to conformal prediction for selectivity intervals are emerging *(frontier — verify)*.

## 8. Future Work

- Approximation algorithms (or hardness) for the single-static-plan min-max regret problem over polytope uncertainty.
- Distributionally-robust optimizers with provable tail guarantees, not just worst-case box bounds.
- Dimension reduction of $R$ via learned, calibrated uncertainty with end-to-end regret guarantees.
- Robustness under joint cardinality + cost-model (hardware) uncertainty.
- Practical integration of bouquet-style guarantees into production engines with acceptable overhead.

## 9. Key References

- **[Foundational]** B. Babcock, S. Chaudhuri. *Towards a Robust Query Optimizer: A Principled and Practical Approach.* SIGMOD, 2005. — [DOI](https://doi.org/10.1145/1066157.1066172)
- **[SOTA]** A. Dutt, J. R. Haritsa. *Plan Bouquets: Query Processing without Selectivity Estimation.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588566)
- **[SOTA]** S. Karthik, J. R. Haritsa, S. Kenkre, V. Pandit. *Platform-Independent Robust Query Processing.* ICDE, 2016 / TKDE (SpillBound). — [DOI](https://doi.org/10.1109/ICDE.2016.7498251)
- **[Foundational]** Harish D., P. N. Darera, J. R. Haritsa. *On the Production of Anorexic Plan Diagrams.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/DDH07.html)
- **[Foundational]** T. Ibaraki, T. Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1270.1498)
- **[Survey]** J. R. Haritsa. *The Picasso Database Query Optimizer Visualizer.* PVLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1921027)

## 10. Worked Example

A 1-D selectivity axis $s\in[0,1]$ with three POSP plans whose costs cross:

- $P_a$ optimal for small $s$, $P_b$ mid-range, $P_c$ large $s$.

**Static-plan regret.** Suppose at $s^\star$ the true optimum is $\text{opt}(s^\star)=100$ but a single fixed plan $P_a$ costs $700$ there: $\text{SubOpt}=700/100=7$. Pick $P_b$ instead and it costs $1000$ at some other $s'$ where $\text{opt}=100$ — ratio $10$. No single static plan beats a small constant everywhere; the worst-case ratio is data-dependent and can be forced large.

**Bouquet execution.** Lay down cost-doubling contours $IC_k=\{s:\text{opt}(s)=2^k\}$, say at costs $1,2,4,8,16$. Execute plans contour-by-contour with a budget cap at each level; when a plan exhausts its $2^k$ budget without finishing, the true selectivity must lie beyond that contour, so advance. The geometric sum $1+2+4+\dots+2^k \le 2\cdot 2^k$ bounds total work at $\le 2\times$ the optimal-for-that-contour cost per error-prone dimension. With $D$ such dimensions, SpillBound's analysis yields the structure-independent bound $\text{MSO}\le D^2+3D$ — e.g. $D=2 \Rightarrow \text{MSO}\le 10$, independent of where the true $s$ actually lies.

---
*Part of the [DBMS Research catalog](../../README.md).*
