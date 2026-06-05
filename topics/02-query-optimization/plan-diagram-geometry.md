# Plan diagram smoothness and selectivity geometry

> **Topic:** Query Optimization · **ID:** `02-query-optimization/plan-diagram-geometry` · **Status:** empirically-open
> **Verification note:** The Plan Bouquet author is Anshuman **Dutt** (not "Dutta"); the SIGMOD 2014 paper guarantees worst-case cost within a factor of $4$ of an oracle.

## 1. Problem Statement
Fix a parametric query template with $d$ varying selectivity (or parameter) dimensions, e.g. predicate selectivities $s_1,\dots,s_d \in [0,1]$. For each point in this **selectivity space**, the optimizer chooses an optimal plan. The **plan diagram** colors each point by the plan the optimizer picks; it partitions the space into **optimality regions**. Empirically these diagrams are often startlingly complex: dozens to hundreds of distinct plans, jagged non-convex boundaries, tiny "speckle" regions, and non-monotone transitions.

The problem: **explain and control the geometry** of these regions.
- *Descriptive:* characterize the shape (convexity, connectivity, number of regions, boundary smoothness) of optimality regions as a function of the cost model.
- *Prescriptive:* **reduce** a plan diagram to few plans while bounding the cost penalty (anorexic reduction), and design optimizers whose diagrams are *robust* — small selectivity error causes small cost regret.
- *Predictive:* given a cost model, bound the number of optimal-plan regions over the parameter space.

## 2. Mathematical Foundations
Let $\mathcal{P}$ be the (finite) set of candidate plans for the template. Each plan $p$ has a cost function $c_p:[0,1]^d \to \mathbb{R}_{\ge 0}$. The optimal-plan map is
$$ p^\star(\mathbf{s}) = \arg\min_{p\in\mathcal P} c_p(\mathbf{s}). $$
The optimality region of $p$ is $R_p = \{\mathbf s : c_p(\mathbf s) \le c_{p'}(\mathbf s)\ \forall p'\}$, a **lower-envelope cell** of the arrangement of cost surfaces.

- If every $c_p$ were **linear** (or more generally if the family were such that pairwise differences are sign-stable), $R_p$ would be a convex polytope and the diagram a polyhedral subdivision — the **lower envelope** of $|\mathcal P|$ functions, with complexity governed by **Davenport–Schinzel** bounds: for $d=1$, the lower envelope of $n$ well-behaved curves has near-linear complexity $\lambda_s(n)$.
- Real cost functions are **non-linear and non-convex** (multiplicative selectivities, $\min$/case splits across join methods, memory-threshold discontinuities), so $R_p$ can be non-convex and disconnected, and the number of cells can be large.
- **Plan Bouquet** (Dutta–Haritsa) replaces single-point estimation with a *cost-budgeted isosurface* traversal, yielding a **provable worst-case multiplicative regret bound** of $4$ (and $4\cdot \rho$-style guarantees) relative to an oracle, independent of selectivity error — a geometric, not statistical, robustness guarantee.

## 3. State of the Art (SOTA)
- **Picasso** (Reddy–Haritsa, VLDB 2005) is the tool that empirically produced plan/cost/reduced diagrams across commercial optimizers, documenting their complexity.
- **Anorexic reduction** (Harish, Darera, Haritsa, VLDB 2007/2008): a plan diagram can usually be reduced to a *small* number of plans (often ≤ 10) within a bounded cost increase (e.g. $\lambda = 20\%$), and this reduction is **NP-hard** but greedily near-optimal in practice.
- **Plan Bouquet** (SIGMOD 2014) and **SpillBound / FrugalSpillBound** give selectivity-estimation-free execution with bounded sub-optimality, the SOTA on *robust* geometry exploitation.
- Systems SOTA for robustness also includes parametric/PQO and adaptive (mid-query re-optimization) approaches.

## 4. Upper Bound
- **Anorexic reduction:** under the *plan-cost-domination* assumption, a diagram is reducible to a near-minimal set within penalty factor $(1+\lambda)$; greedy achieves the standard set-cover-style $\ln n$ factor on the hitting-set formulation.
- **Plan Bouquet:** guarantees worst-case performance within a factor of **$4\cdot\rho$** of the oracle for the 1-D case ($\rho$ = number of bouquet plans-ish geometric factor), generalizing with structured bounds in higher dimensions — the best-known *worst-case-regret* upper bound that is independent of estimation accuracy.
- Region-count upper bounds derive from **lower-envelope / Davenport–Schinzel** theory when cost surfaces are restricted to algebraic families of bounded degree.

## 5. Lower Bound
- **Anorexic plan reduction is NP-hard** (reduction from set cover / minimum hitting set) — exact minimization is intractable, and the set-cover inapproximability $\Omega(\ln n)$ applies.
- For estimation-free execution, an **information-theoretic / adversarial lower bound** shows any algorithm ignorant of true selectivities suffers worst-case multiplicative regret bounded below by a constant (the Plan Bouquet analysis exhibits an adversary forcing near-its-guarantee), so constant-factor regret is essentially unavoidable.
- The **geometric** question — a tight bound on the number/complexity of optimality regions for realistic (multiplicative, piecewise) cost models — has **no proven tight bound**; this is the empirically-open core.

## 6. The Gap
The gap is genuinely open and partly *empirical*: we lack a predictive theory linking cost-model structure to plan-diagram geometry (region count, boundary smoothness, speckle). We can *reduce* and *robustly exploit* diagrams with guarantees (Plan Bouquet), but we cannot, from first principles, predict or upper-bound a diagram's complexity for a given optimizer, nor design cost models guaranteed to yield smooth diagrams. Closing it needs either arrangement/Davenport–Schinzel-style bounds specialized to DB cost algebra, or smoothness-by-construction cost models.

## 7. Current Research (as of June 2026)
- **Robust query processing** integrating Plan Bouquet ideas with learned cardinality estimators and bounded-regret guarantees. *(frontier — verify)*
- Studying plan-diagram geometry of **learned optimizers** — do learned plan-selection policies yield smoother or wilder diagrams than cost-based ones? *(frontier — verify)*
- Smoothness via **regularized / monotone cost models** that provably avoid speckle and discontinuities.
- Groups: Haritsa (IISc, Picasso/Plan Bouquet lineage); robust-query-processing community; computational-geometry crossover (lower envelopes, arrangements).

## 8. Future Work
- Provable region-complexity bounds for multiplicative-selectivity cost families.
- Cost models designed for Lipschitz/monotone optimal-plan maps (bounded regret to estimation error by construction).
- Higher-dimensional anorexic reduction with approximation guarantees and tractable construction.

## 9. Key References
- **[Foundational]** Reddy, Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/ReddyH05.html)
- **[SOTA]** Harish, Darera, Haritsa. *On the Production of Anorexic Plan Diagrams.* VLDB, 2007. — [DBLP search](https://dblp.org/search?q=On%20the%20Production%20of%20Anorexic%20Plan%20Diagrams)
- **[SOTA]** Dutt, Haritsa. *Plan Bouquets: Query Processing without Selectivity Estimation.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588566)
- **[Foundational]** Sharir, Agarwal. *Davenport–Schinzel Sequences and Their Geometric Applications.* Cambridge Univ. Press, 1995. — [Cambridge](https://www.cambridge.org/9780521470254)
- **[Survey]** Haritsa. *Robust Query Processing: Mission Possible* (tutorials/keynotes), VLDB/ICDE, 2010s. — [DOI](https://doi.org/10.14778/3415478.3415561)

## 10. Worked Example

**Plan Bouquet on a 1-D selectivity axis.** The true selectivity $s$ is unknown in $[0,1]$; the oracle optimal cost $C^*(s)$ grows monotonically. Lay down cost *isosurfaces* at geometrically spaced budgets $1,2,4,8,16$. Each isosurface is crossed by one bouquet plan optimal there; say plans $p_1,\dots,p_5$ cover the cost bands.

Execution discovery: run $p_1$ with budget $1$. If it finishes, done. Else run $p_2$ with budget $2$, then $p_3$ with budget $4$, and so on, *aborting* each partial run at its budget. Suppose the true optimum cost is $C^*=10$, so plan $p_4$ (budget $8$) fails but $p_5$ (budget $16$) succeeds.

Total work paid: $1+2+4+8+16 = 31$. Oracle would pay $10$. Ratio $31/10 = 3.1 < 4$.

In the worst case the geometric series $\sum_{i=0}^{k} 2^i = 2^{k+1}-1$ against an oracle just above $2^{k-1}$ gives the tight bound: $\frac{2^{k+1}-1}{2^{k-1}} \to 4$. This factor-$4$ regret holds with **no selectivity estimate at all** — a geometric guarantee, not a statistical one.

---
*Part of the [DBMS Research catalog](../../README.md).*
