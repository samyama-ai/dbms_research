# Confidence Intervals for Cardinality Estimates

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/cardinality-confidence-intervals` · **Status:** open

## 1. Problem Statement

Instead of (or in addition to) a point estimate $\hat c(q)$, produce a **query-specific interval** $[\ell(q), u(q)]$ that is *calibrated*: the true cardinality $c(q)$ lies in it with a stated probability $1-\alpha$ (or is a guaranteed deterministic bound), and the interval is usable by a query optimizer.

Variants:

- **Statistical CI:** $\Pr[c(q)\in[\ell,u]]\ge 1-\alpha$ over the randomness of sampling/sketching.
- **Deterministic bound:** $\ell\le c(q)\le u$ always (e.g. via AGM / degree bounds) — a guarantee, not a probability.
- **Optimizer-usable:** the interval must be (i) cheap, (ii) propagable through plan operators, and (iii) actionable — e.g. drive robust plan choice or runtime re-optimization.

The hard part is *calibration under composition*: marginal per-predicate intervals must combine into a valid interval for a multi-join query without blowing up to vacuous width.

## 2. Mathematical Foundations

For a uniform sample $S\subseteq R$ of size $r$ answering a predicate $\theta$ with sample count $X=\sum_{i\in S}\mathbf 1[\theta]$, the estimate is $\hat c=(n/r)X$. Since $X\sim \mathrm{Binomial}(r,s)$ (or hypergeometric without replacement), **Hoeffding/Chernoff** give $\Pr[|\hat s - s|>\varepsilon]\le 2e^{-2r\varepsilon^2}$, and exact **Clopper–Pearson** intervals are available. The catch: for selective predicates ($s$ small) the *relative* half-width scales as $\sqrt{(1-s)/(rs)}$, exploding as $s\to 0$.

For joins, a deterministic worst-case upper bound is the **AGM bound**: for a join hypergraph $H$ with fractional edge cover $\mathbf x$, $|{\bowtie}|\le \prod_e |R_e|^{x_e}$ (Atserias–Grohe–Marx, 2008), tightened by **degree-bounds / polymatroid (entropic) bounds** (Abo Khamis–Ngo–Suciu, PODS 2017) which give the tightest known *guaranteed* upper interval from cardinality + functional-dependency + degree statistics. A natural lower bound for a non-empty result is $\max_e$ over projections.

Calibration is formalized via **coverage**: an interval procedure has coverage $1-\alpha$ if $\Pr[c\in I]\ge 1-\alpha$. **Conformal prediction** gives finite-sample, distribution-free coverage for learned estimators by calibrating residual quantiles on a held-out set (exchangeability assumption).

## 3. State of the Art (SOTA)

- **Sampling CIs:** online aggregation (Hellerstein–Haas–Wang, SIGMOD 1997) pioneered running CIs; ripple joins and "wander joins" (Li et al., SIGMOD 2016) give unbiased join estimates with CLT-based CIs for AQP.
- **Deterministic optimizer bounds:** **pessimistic cardinality estimation** (Cai, Balazinska, Suciu, SIGMOD 2019) uses degree/AGM bounds as a certified upper interval to avoid catastrophic plans; extended by "Safe-Bound" and bound-sketch work.
- **Learned + uncertainty:** Bayesian/ensemble and *conformalized* cardinality estimators emit predictive intervals; *(frontier — verify)* conformal CE wrappers with optimizer integration are an active 2024-2026 thread.
- **Systems:** few production optimizers expose true CIs; most use single point estimates plus heuristic "fudge factors."

## 4. Upper Bound

- **Single predicate from a sample:** an exact $1-\alpha$ Clopper–Pearson interval with relative half-width $\varepsilon$ needs $r=\Theta(\varepsilon^{-2}s^{-1}\log\alpha^{-1})$ samples — achievable and (for the multiplicative target) order-optimal.
- **Deterministic join upper bound:** the polymatroid/entropic bound is computable as an LP over the join's statistics and is the tightest known guaranteed upper interval given the available statistics (Abo Khamis–Ngo–Suciu 2017).
- **Distribution-free predictive coverage:** split conformal achieves exactly $1-\alpha$ marginal coverage with $O(\alpha^{-1})$ calibration points, regardless of the base estimator.

## 5. Lower Bound

- **Selective predicates:** the $\Omega(\sqrt{n/r})$ NDV/selectivity sampling bound (Charikar et al. 2000) implies any sampling CI for rare predicates is provably wide unless $r\to n$.
- **Tightness of AGM:** the AGM bound is tight (achieved by some instance) but can be exponentially loose for a *specific* instance — no per-query guaranteed interval narrower than AGM is possible using only the cardinality statistics it consumes (information-theoretic).
- **Conformal limits:** distribution-free *conditional* coverage $\Pr[c\in I\mid q]$ is impossible in finite samples (Vovk; Barber et al., "limits of distribution-free conditional coverage") — only marginal coverage is attainable, which is weaker than what optimizers ideally want per query.

## 6. The Gap

**Open.** Two regimes: (1) deterministic bounds are *valid* but often loose (AGM/entropic gap to true value can be huge); (2) statistical/conformal intervals are *tight on average* but only marginally calibrated and may be invalid under drift or for the rare predicates that matter most. No method gives *per-query, tight, valid* intervals that also *propagate through joins* with controlled width. Closing it needs either entropic-bound tightening with measured higher-order statistics, or conditionally-valid conformal procedures specialized to cardinality.

## 7. Current Research (as of June 2026)

- Tightening guaranteed bounds with degree sequences, functional dependencies, and sampled join-degree information ("LP/entropic" bounds; Suciu, Ngo, Abo Khamis).
- Conformalized and Bayesian-ensemble CE producing calibrated intervals consumed directly by cost models *(frontier — verify)*.
- Risk-aware optimizers that take $[\ell,u]$ rather than a point (links to the robust-plans problem in this topic).
- Combining a learned point estimate with a certified pessimistic ceiling so the interval is both tight and safe.

## 8. Future Work

- Interval *propagation algebra* through full plans with non-vacuous width.
- Conditional (per-query) coverage guarantees, even approximate.
- Online tightening of intervals during execution (re-optimization triggers).
- Standard benchmarks scoring calibration + width, not just point q-error.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 / SICOMP, 2013.
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS, 2017.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019.
- **[Foundational]** Hellerstein, Haas, Wang. *Online Aggregation.* SIGMOD, 1997.
- **[SOTA]** Li, Wu, Yi, Zhao. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016.
- **[Foundational]** Vovk, Gammerman, Shafer. *Algorithmic Learning in a Random World (Conformal Prediction).* Springer, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
