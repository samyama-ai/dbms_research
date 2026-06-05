# Approximate spatial query with error bounds

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/approximate-spatial-aqp` · **Status:** partially-solved

## 1. Problem Statement
Given a large spatial relation $R$ (and possibly a second relation $S$), answer **spatial aggregate** queries — `COUNT`/`SUM`/`AVG` over a range or polygon, density, spatial `GROUP BY` cell, and **spatial-join aggregates** (e.g. count pairs within distance $\epsilon$, or sum an attribute over joined pairs) — *approximately*, returning an estimate $\hat\theta$ together with a **provable confidence interval** $[\hat\theta - \Delta,\ \hat\theta + \Delta]$ such that $\Pr[\theta \in [\hat\theta\pm\Delta]] \ge 1-\alpha$, using a summary or sample far smaller than $R$.

Variants:
- **Estimation (counting):** $\hat\theta$ with a CI, the canonical AQP target.
- **Decision/threshold:** decide $\theta \ge \tau$ at confidence $1-\alpha$ with the smallest sample (sequential/online aggregation).
- **Optimization:** minimize sample/sketch size (or query latency) for a target CI width over a query class $\mathcal{Q}$.

It is "partially solved" because for *single-relation* range aggregates the sampling theory and CIs are clean and deployed; the open frontier is **spatial joins** and **arbitrary-polygon / skewed-selectivity** aggregates, where naive sampling gives uselessly wide intervals.

## 2. Mathematical Foundations
A range-`COUNT` is $\theta=\mu(q)$ for query region $q$; a uniform sample of size $s$ gives $\hat\theta$ with CI width $\Delta=O(\sqrt{\theta(1-\theta)/s})$ by Hoeffding/Bernstein, and *uniform-over-a-query-class* error is governed by **VC dimension**: an $\varepsilon$-sample of size $O((\mathrm{VC}/\varepsilon^2)\log(1/\delta))$ makes every $q\in\mathcal{Q}$ accurate simultaneously (axis-boxes $\mathrm{VC}=2d$; halfspaces $d{+}1$; $k$-gons grow with $k$). **Relative**-error CIs need $\Omega(1/(\varepsilon^2\theta))$ samples, blowing up for selective queries.

Spatial **joins** are the hard case: a uniform Bernoulli($p$) sample of a join estimates pair-counts with variance inflated by degree skew, and AGM-style worst-case output makes naive sample-then-join high-variance. **Correlated / index-assisted sampling** (Olken; ripple join; wander-join over the join graph) and **bifocal / end-biased** sampling reduce variance. **Sketches** give a complementary route: count distinct via **HyperLogLog**, frequency/heavy spatial cells via **Count-Min**, and quantiles via **KLL/t-digest**, each with $(\varepsilon,\delta)$ guarantees in $\mathrm{polylog}$ space; **geometric coresets** ($\varepsilon$-approximations, discrepancy-based) give *deterministic* range-aggregate error of size $O(\varepsilon^{-2d/(d+1)})$ for boxes. CIs themselves come from CLT/bootstrap or, for distribution-free guarantees, **conformal prediction**.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BlinkDB** (Agarwal et al., EuroSys 2013) — stratified samples + error-latency profiles, the template AQP engine; **VerdictDB** (Park et al., SIGMOD 2018) — DB-agnostic middleware with CIs; **online aggregation** (Hellerstein–Haas–Wang) and **wander-join / XDB** (Li et al., SIGMOD 2016) for join sampling. Spatial-specific: **Sedona/GeoSpark sampling**, **SnappyData**, and density/heatmap approximation in visualization systems (**VAS**, sampling-for-visualization). H3/S2 pre-aggregated cells back fast approximate `GROUP BY`.
- **Theory-SOTA:** geometric coresets and $\varepsilon$-approximations (Phillips; Matoušek discrepancy), AGM/worst-case-optimal join theory for the join-aggregate variant, and sketch lower/upper bounds (Cormode–Muthukrishnan Count-Min; Flajolet HLL).

## 4. Upper Bound
- **Single-relation range aggregate:** uniform/stratified sample of size $\tilde O(\mathrm{VC}/\varepsilon^2)$ gives additive-$\varepsilon$ CIs over the whole query class (info-theoretically near-tight); deterministic coresets of size $O(\varepsilon^{-2d/(d+1)})$ for boxes in the **real-RAM/comparison** model.
- **Join-aggregate:** index-assisted **wander-join** estimates COUNT/SUM with unbiased estimators and CLT CIs; variance — hence CI width — depends on join-degree skew, so worst-case width is not bounded sublinearly.
- **Distinct/heavy cells:** HLL gives relative error $\approx 1.04/\sqrt{m}$ with $m$ registers; Count-Min gives additive $\varepsilon\|f\|_1$ error.

## 5. Lower Bound
- **Sampling:** additive-$\varepsilon$ over a class needs $\Omega(\mathrm{VC}(\mathcal{Q})/\varepsilon^2)$ samples; relative error at selectivity $\theta$ needs $\Omega(1/(\varepsilon^2\theta))$ — info-theoretic, unconditional.
- **Sketches:** Count-Min/distinct-counting space lower bounds ($\Omega(1/\varepsilon)$, $\Omega(\varepsilon^{-2})$ regimes) from communication complexity (INDEX/GAP-HAMMING reductions).
- **Join aggregates:** estimating join size to relative error inherits set-intersection/communication lower bounds and AGM worst-case output; no sample sublinear in skew gives bounded relative-error CIs on adversarial inputs.

## 6. The Gap
For single-table spatial range aggregates the gap is essentially closed: matching $\Theta(\mathrm{VC}/\varepsilon^2)$ sampling bounds and deployed CI machinery. The **open** part is twofold: (a) **spatial joins** — provably narrow CIs under degree/density skew without scanning the data, where current estimators have unbounded worst-case variance; and (b) **arbitrary-polygon / highly-selective** aggregates, where the $1/\theta$ relative-error blowup makes guarantees impractical exactly where users query. Closing it needs instance-/skew-adaptive estimators with certified intervals, or sketches purpose-built for spatial-join aggregates.

## 7. Current Research (as of June 2026)
- **Conformal / distribution-free CIs** wrapping learned spatial cardinality and aggregate estimators to give *post-hoc* coverage guarantees *(frontier — verify)*.
- **Coreset-backed AQP** that swaps uniform samples for discrepancy coresets to tighten range-aggregate CIs at fixed budget.
- **Skew-aware join sampling** extending wander-join with heavy-hitter handling and learned proposals for spatial joins *(frontier — verify)*.
- **Approximation-for-visualization** (density/heatmap) with perceptual + statistical error bounds. Groups: Cormode (sketches), Phillips (coresets), Park/Mozafari (VerdictDB AQP), Re/Suciu (learned/probabilistic estimation), spatial-viz groups (Wu, Doraiswamy/Freire).

## 8. Future Work
- Spatial-join-aggregate estimators with provable CI width under bounded skew.
- Relative-error guarantees whose cost depends on *intrinsic* dimension / real data skew, not ambient VC.
- Composable error propagation through multi-operator spatial query plans (CIs end-to-end).
- Certified learned AQP: estimators with monotone/Lipschitz structure and proven coverage, robust to drift.

## 9. Key References
- **[Foundational]** Olken, Rotem. *Simple Random Sampling from Relational Databases.* VLDB, 1986. — [DBLP](https://dblp.org/rec/conf/vldb/OlkenR86.html)
- **[Foundational]** Hellerstein, Haas, Wang. *Online Aggregation.* SIGMOD, 1997. — [DBLP](https://dblp.org/rec/conf/sigmod/HellersteinHW97.html)
- **[SOTA]** Agarwal, Mozafari, Panda, Milner, Madden, Stoica. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[SOTA]** Li, Wu, Yi, Zhao. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[SOTA]** Park, Mozafari et al. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[SOTA]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Survey]** Phillips. *Coresets and Sketches.* Handbook of Discrete and Computational Geometry, 3rd ed., 2017. — [arXiv](https://arxiv.org/abs/1601.00617)

## 10. Worked Example

Suppose a table `Pickups` holds $N = 10^7$ taxi pickup points, and we want `COUNT(*)` inside a query rectangle $q$ that covers a downtown block — true selectivity $\theta = 0.002$ (so the true count is $\theta N = 20{,}000$).

Draw a uniform sample of size $s = 100{,}000$. The number of sampled points falling in $q$ is $X \sim \mathrm{Binomial}(s, \theta)$, so the estimate is $\hat\theta = X/s$ and $\hat\theta N$ estimates the count. Expected hits $= s\theta = 200$. The standard error of $\hat\theta$ is
$$\sqrt{\tfrac{\theta(1-\theta)}{s}} = \sqrt{\tfrac{0.002 \cdot 0.998}{10^5}} \approx 1.41\times10^{-4}.$$
A $95\%$ CI ($z=1.96$) on the count is $20{,}000 \pm 1.96 \cdot N \cdot 1.41\times10^{-4} \approx 20{,}000 \pm 2{,}770$, i.e. a relative half-width of about $\pm14\%$.

This shows the $1/\theta$ pain: to halve the interval you must quadruple $s$, and for a $10\times$ more selective query ($\theta=0.0002$) the same sample gives only $\approx 20$ hits and a useless $\pm 44\%$ interval — exactly why selective and join-aggregate queries (Section 6) need stratified or index-assisted sampling rather than plain uniform sampling.

---
*Part of the [DBMS Research catalog](../../README.md).*
