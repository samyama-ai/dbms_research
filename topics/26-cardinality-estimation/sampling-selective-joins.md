# Sample-Based Estimation for Selective Joins

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/sampling-selective-joins` · **Status:** partially-solved

## 1. Problem Statement

Estimate the cardinality (or an aggregate) of a join — possibly with selective predicates — using samples of the base relations, while avoiding the two classic failure modes: **empty samples** (no sampled tuple survives the predicate/join, giving estimate 0 and no signal) and **high variance** (a few surviving tuples dominate, giving wild estimates).

Variants:

- **Estimation:** estimate $|R\bowtie S|$ (or $\sigma_\theta(R\bowtie S)$) and its variance from samples.
- **Non-empty guarantee:** design a sampling scheme whose estimator is non-zero / bounded-variance with high probability even when selectivity is $\ll 1/r$.
- **Online/AQP:** produce a running estimate with shrinking CI as more samples arrive.

The core difficulty: independent uniform samples of $R$ and $S$ rarely *join* (the "quadratic loss" of sampling joins — a fraction $f$ sample of each yields only $\approx f^2$ of the join), and predicates further thin survivors.

## 2. Mathematical Foundations

For $T=R\bowtie_A S$, independent Bernoulli($f$) samples $R',S'$ give $\mathbb E[|R'\bowtie S'|]=f^2|T|$, but the variance is governed by the join-attribute frequency moments: $\mathrm{Var}\propto \sum_v f_R(v)^2 f_S(v)^2$, dominated by **heavy hitters** (skewed values). This is why naive join sampling fails on skew.

Key techniques and their math:

- **Correlated / index-assisted sampling:** sample $R$, then for each sampled $r$ draw matching $S$-tuples via an index — turns $f^2$ into $f$, recovering an unbiased $\hat{|T|}$ with much lower variance.
- **Random walks (Wander Join):** perform a random walk over join keys; the inverse-probability (Horvitz–Thompson) estimator $\hat{|T|}=\frac1t\sum_{i} 1/p(\text{path}_i)$ is unbiased with CLT-based CIs (Li–Wu–Yi–Zhao, SIGMOD 2016).
- **End-biased / measure-biased sampling:** sample tuples with probability proportional to their join degree (Estan–Naughton; Chen–Yi, "two-level sampling" VLDB 2017) to tame heavy hitters.
- **Sketch–sample hybrids:** Bound-Sketch / pessimistic sketches cap the contribution of heavy keys deterministically while sampling the light tail.

The unavoidable barrier: for a predicate of selectivity $s$, a uniform sample needs $\Omega(1/s)$ tuples merely to see one survivor (coupon/occupancy), and the $\Omega(\sqrt{n/r})$ distinct-value bound (Charikar et al. 2000) applies to the join's value set.

## 3. State of the Art (SOTA)

- **Theory+systems-SOTA:** **Wander Join** (Li et al., SIGMOD 2016) and **XDB** give unbiased online join aggregates with CIs via random walks over indexes — the reference method for AQP joins.
- **Two-level / measure-biased sampling** (Chen, Yi, VLDB 2017) gives provably better variance for join-size estimation under skew.
- **Index-based ripple/correlated sampling** in commercial AQP and the classic **ripple joins** (Haas–Hellerstein, SIGMOD 1999) for online aggregation.
- **Hybrid with bounds:** combining samples with degree/AGM ceilings (pessimistic CE, Cai et al. 2019) to prevent zero/under-estimates on selective joins.
- **Learned correction:** sample-then-correct schemes feeding sample features into a model *(frontier — verify)*.

## 4. Upper Bound

- **Wander Join:** $O(1)$ index lookups per walk; for a chain join of length $\ell$, $O(\ell)$ per sample, unbiased, with variance controlled by path-probability spread; achieves $(\varepsilon,\delta)$ relative error in $\tilde O(\varepsilon^{-2}\cdot\rho)$ walks where $\rho$ depends on degree skew.
- **Two-level sampling:** matches the information-theoretic variance lower bound for join-size estimation up to constants under the available statistics (Chen–Yi 2017).
- **Index-assisted predicate sampling:** converts the $f^2$ join-sampling loss to $f$, an exponential improvement in effective sample yield.

## 5. Lower Bound

- **Selectivity barrier:** $\Omega(1/s)$ samples to observe any tuple of a selectivity-$s$ predicate (occupancy bound) — no estimator beats it without auxiliary structure (indexes/sketches).
- **Skew/variance:** without index access, join-size estimation from independent uniform samples has variance lower-bounded by the heavy-hitter mass; communication/streaming lower bounds for inner-product ($F_2$-style) imply $\Omega(\sqrt{n})$-type space to estimate join sizes within constant factor in the worst case.
- **Distinct-value inheritance:** the $\Omega(\sqrt{n/r})$ NDV bound transfers to join-output distinct counts and grouped selective joins.

## 6. The Gap

**Partially solved.** With *indexes*, Wander-Join-style and measure-biased methods are near-optimal in theory and strong in practice — the index-available case is largely closed. The genuinely open part is the **index-free / streaming** setting and *extreme selectivity* (rare needle joins), where every sampling estimator is provably weak; the practical answer is hybridizing with deterministic bounds, but a tight characterization of the achievable variance-vs-budget frontier across query shapes remains open.

## 7. Current Research (as of June 2026)

- Extending random-walk estimators to cyclic queries, many-way joins, and adaptive walk-budget allocation (Yi, Wu, and collaborators).
- Sample + pessimistic-bound hybrids that guarantee non-zero, upper-bounded estimates on selective joins (Suciu/Balazinska line) *(frontier — verify)*.
- Learned importance/proposal distributions to steer walks toward surviving tuples (variance reduction via learned sampling).
- AQP engines integrating CI-aware sampling directly into optimizer cost models.

## 8. Future Work

- Provably variance-optimal sampling for arbitrary acyclic and bounded-treewidth joins under predicates.
- Index-free schemes with sub-$1/s$ effective cost via learned or sketched needle-finding.
- Unified sample+sketch+bound estimators with a single calibrated CI.
- Robust handling of correlated predicates across multiple joined tables.

## 9. Key References

- **[Foundational]** Haas, Hellerstein. *Ripple Joins for Online Aggregation.* SIGMOD, 1999.
- **[SOTA]** Li, Wu, Yi, Zhao. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016.
- **[SOTA]** Chen, Yi. *Two-Level Sampling for Join Size Estimation.* SIGMOD/VLDB, 2017.
- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimating the Number of Distinct Values of an Attribute.* VLDB, 2000.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation.* SIGMOD, 2019.
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
