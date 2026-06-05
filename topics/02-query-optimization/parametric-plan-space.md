# Parametric query optimization plan-space size

> **Topic:** Query Optimization · **ID:** `02-query-optimization/parametric-plan-space` · **Status:** partially-solved

## 1. Problem Statement

In **parametric query optimization (PQO)**, query cost depends on parameters unknown at compile time — selectivities, predicate constants, memory budget — modeled as a point $\theta$ in a parameter space $\Theta\subseteq\mathbb{R}^d$. Each plan $p$ has a cost function $c_p(\theta)$; the **optimal plan** at $\theta$ is $p^*(\theta)=\arg\min_p c_p(\theta)$. PQO precomputes a decomposition of $\Theta$ into regions, each labeled with the plan optimal throughout it, so that at runtime one looks up $\theta$ instead of re-optimizing. Core questions:

- **Counting variant (the headline):** How many distinct plans can be optimal over $\Theta$ — i.e., the size of the **parametric optimal set** (POSP, parametric optimal set of plans)? Bound it as a function of $d$, the number of plans, and the cost-function class.
- **Decomposition (optimization) variant:** Compute the partition of $\Theta$ into optimality regions and their plan labels efficiently.
- **Decision variant:** Given $\theta$, return $p^*(\theta)$ (lookup), and: is plan $p$ optimal anywhere in $\Theta$?

"Solving" means tight bounds on the POSP size and an algorithm whose work scales with that size, not with a brute-force grid.

## 2. Mathematical Foundations

Each plan's cost $c_p(\theta)$ is a function over $\Theta$; the optimal-cost function is the **lower envelope** $C^*(\theta)=\min_p c_p(\theta)$, and the optimality regions are the projections of the envelope's pieces — exactly the cells of an arrangement. If costs are **linear** in $\theta$ (a common model: cost linear in selectivities), the lower envelope is the boundary of a convex polytope and the regions form a **convex polyhedral subdivision**; the number of pieces of the lower envelope of $m$ hyperplanes in $\mathbb{R}^d$ is $O(m^{\lfloor d/2\rfloor})$ by the **Upper Bound Theorem** for arrangements. For **piecewise-linear or low-degree algebraic** costs, the complexity of the lower envelope is governed by **Davenport–Schinzel sequences**: in 2D, $n$ partially-defined continuous cost curves pairwise crossing $\le s$ times have a lower envelope of complexity $\lambda_{s+2}(n)$, which is near-linear $n\cdot 2^{O(\alpha(n))}$ ($\alpha$ = inverse Ackermann). Thus POSP-size bounds reduce to **computational-geometry envelope complexity**. A crucial subtlety: a single plan may be optimal in *several disconnected* regions, so "number of optimal plans" $\le$ "number of optimality regions."

## 3. State of the Art (SOTA)

- **Theory SOTA:** Reductions to lower-envelope/arrangement complexity give the $O(m^{\lfloor d/2\rfloor})$ (linear costs) and Davenport–Schinzel (low-degree, low-$d$) bounds. Ganguly (PODS 1998) gave foundational analysis of PQO structure and plan-space bounds for linear/affine cost models.
- **Systems SOTA:** Hulgeri & Sudarshan's **PPQO / AniPQO** (VLDB 2002–2003) compute approximate parametric decompositions by adaptive sampling of $\Theta$ with bounded suboptimality. Reddy & Haritsa's **plan diagrams / Picasso** (VLDB 2005) empirically characterize optimality-region geometry for commercial optimizers and motivated **plan-diagram reduction** (anorexic reduction, Harish–Darera–Haritsa, VLDB 2007) that shrinks the effective POSP with bounded cost increase.

## 4. Upper Bound

For **linear** cost functions over $d$ parameters and $m$ candidate plans, the number of optimality regions — hence POSP size — is $O(m^{\lfloor d/2\rfloor})$ (Upper Bound Theorem; real-RAM/arrangement model), and the decomposition is computable in time near the output size. For **low-degree algebraic costs in $d=2$**, the lower-envelope complexity is $\lambda_{s+2}(m)=m\cdot 2^{O(\alpha(m))}$ (near-linear). **Anorexic reduction** shows that allowing a $\lambda$-bounded cost increase reduces the *retained* plan set to a small constant (empirically $\le 10$) for typical 2–3D selectivity spaces — a practical upper bound on the *useful* POSP.

## 5. Lower Bound

The arrangement bounds are **tight**: there exist configurations of $m$ linear cost functions in $\mathbb{R}^d$ whose lower envelope has $\Omega(m^{\lfloor d/2\rfloor})$ pieces, so the POSP can be that large — exponential in dimension $d$. Davenport–Schinzel sequences are likewise tight, giving super-linear (though sub-quadratic) envelope complexity for $s\ge2$. Hence computing the *full* exact decomposition cannot beat output-size, and the output itself is super-polynomial as $d$ grows: PQO suffers a **curse of dimensionality** in the number of parameters. (The underlying single-point optimization remaining NP-hard further bounds exact PQO.)

## 6. The Gap

For **fixed low dimension and structured (linear / low-degree) cost models**, upper and lower bounds essentially **match** (arrangement / Davenport–Schinzel theory) — this slice is *closed*, which is why the status is *partially-solved*. The open gap is: (1) **realistic cost models** are neither linear nor low-degree (they involve min/max, step functions from buffer effects, non-convexity), and no tight POSP bound is known for them; (2) **high $d$** makes exact decomposition intractable, so the practical frontier is *approximate* decompositions with provable suboptimality — but the tradeoff between region count and guaranteed cost increase is not tightly characterized beyond the empirical anorexic-reduction results; (3) connecting POSP size to **robust plan selection** (choosing one plan minimizing regret across $\Theta$, see *robust-plan-selection*) lacks tight bounds. Closing the gap needs POSP complexity results for non-convex/min-cost-model classes and a provable region-count vs. suboptimality frontier.

## 7. Current Research (as of June 2026)

- **Learned / amortized PQO**: models that predict $p^*(\theta)$ directly, avoiding explicit decomposition, with calibrated error (links to *learned-join-optimizers*). *(frontier — verify)*
- Tight **region-count vs. suboptimality** tradeoff theory generalizing anorexic reduction beyond 2–3D plan diagrams (Haritsa group lineage, IISc). *(frontier — verify)*
- PQO integrated with **adaptive re-optimization** so the parametric decomposition guides mid-query plan switching (links to *adaptive-reoptimization* and *plan-diagram-geometry*).
- POSP bounds for **non-linear / piecewise cost models** via realistic algebraic-geometry envelope analysis. *(frontier — verify)*

## 8. Future Work

- Tight POSP-size bounds for non-convex, min/step cost-function classes.
- A provable Pareto frontier between number of retained plans and worst-case suboptimality in arbitrary $d$.
- Scalable approximate decomposition algorithms for high-dimensional parameter spaces with guarantees.
- Unification of PQO decomposition with robust single-plan selection and runtime re-optimization.

## 9. Key References

- **[Foundational]** Ganguly. *Design and Analysis of Parametric Query Optimization Algorithms.* VLDB, 1998.
- **[SOTA]** Hulgeri, Sudarshan. *AniPQO: Almost Non-intrusive Parametric Query Optimization for Nonlinear Cost Functions.* VLDB, 2003.
- **[SOTA]** Reddy, Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005.
- **[SOTA]** Harish, Darera, Haritsa. *On the Production of Anorexic Plan Diagrams.* VLDB, 2007.
- **[Foundational]** Sharir, Agarwal. *Davenport–Schinzel Sequences and Their Geometric Applications.* Cambridge University Press, 1995.
- **[Survey]** Dey, Bhaumik, Haritsa, et al. *Efficiently Approximating Query Optimizer Plan Diagrams.* PVLDB, 2008.

---
*Part of the [DBMS Research catalog](../../README.md).*
