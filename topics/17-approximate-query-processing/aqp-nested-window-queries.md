---
id: 17-approximate-query-processing/aqp-nested-window-queries
title: "AQP for Nested and Window Queries"
topic: 17-approximate-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# AQP for Nested and Window Queries

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/aqp-nested-window-queries` · **Status:** open

## 1. Problem Statement
Approximate query processing (AQP) is well understood for flat `SELECT–FROM–WHERE–GROUP BY` aggregates over samples/sketches, but it largely breaks down for **nested** and **window/analytic** queries. The open problem: produce **error-bounded** approximate answers — with *valid confidence intervals* — for

- **correlated subqueries** (e.g., `WHERE x > (SELECT AVG(y) FROM ... WHERE outer.k = inner.k)`), where the inner result depends on each outer tuple;
- **window functions** (`RANK`, `ROW_NUMBER`, `LAG`, moving averages, `SUM() OVER (PARTITION BY ... ORDER BY ... ROWS BETWEEN ...)`), which compute per-row results over ordered analytic frames;
- **nested aggregation** (aggregates of aggregates, `HAVING` on subquery results).

Variants:
- **Estimation variant:** return per-row or per-group approximate analytic values with bounded error.
- **Top-k / ranking variant:** approximate `RANK`/`ORDER BY ... LIMIT k` over windows with bounded rank error.
- **Composition variant:** propagate and bound error through *multiple* stacked operators (sample → window → outer aggregate).

The hard part is **error propagation through non-linear, order-dependent, per-row operators**: a sampling error in the inner query or in a frame's input does not compose linearly into the outer answer, and ranking/`LAG` are sensitive to *missing neighbors* that sampling inevitably creates.

## 2. Mathematical Foundations
Flat AQP rests on the linearity of sample-based estimators: $\widehat{\mathrm{SUM}}=\frac{N}{n}\sum_{i\in S} x_i$ is unbiased with variance $O(\sigma^2 N^2/n)$, and CIs follow from the **CLT**/finite-population theory. Nesting and windows break this:

- **Correlated subquery** = a function $g(\hat\theta_k)$ of a *per-group* estimate $\hat\theta_k$; error propagates by the **delta method**, $\mathrm{Var}(g(\hat\theta))\approx g'(\theta)^2\mathrm{Var}(\hat\theta)$, but small per-group samples make $\mathrm{Var}(\hat\theta_k)$ large and the linearization unreliable.
- **Window frames** require *order statistics* and *neighborhood* information; sampling deletes neighbors, so `LAG`/moving frames over a sample estimate a *different* (re-scaled) series — bias must be modeled explicitly.
- **Ranking** maps to **approximate quantile / rank-error** guarantees (see *approximate-quantiles*): a sample gives rank within $\pm\varepsilon n$ only via order-statistic concentration.
- Relevant theory: relational-algebra **decorrelation/unnesting** (Kim; Dayal; Seshadri et al.) to flatten subqueries; **delta method** and **bootstrap** for non-linear error; concentration of order statistics for ranking; **mergeable summaries** for partitioned windows.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BlinkDB** (Agarwal et al., EuroSys 2013) and **Quickr** (Kandula et al., SIGMOD 2016) inject samplers into plans but target *flat* aggregates; **VerdictDB** (Park et al., SIGMOD 2018) provides "variational subsampling" / analytical bootstrap for fairly general SQL and is the closest thing to AQP that *attempts* nested/complex queries, yet its guarantees weaken for correlated subqueries and ranking windows. **DBEst / DeepDB** (model-based AQP) can answer some nested patterns by querying a learned density but without rigorous CIs for windows.
- **Theory-SOTA:** the **analytical bootstrap method** (Zeng, Gao, Mozafari, SIGMOD 2014) gives a closed-form way to compute the bootstrap distribution of relational aggregates, partially extensible to nesting; rank-error quantile theory covers `RANK`-style windows.

## 4. Upper Bound
- Flat aggregates over uniform samples: unbiased, half-width $O(\sigma N n^{-1/2})$ (CLT), the baseline these methods inherit.
- Correlated subqueries after **decorrelation** into a join+`GROUP BY`: error bounded by the *worst per-group* sample variance — i.e., $O(\sigma_k n_k^{-1/2})$ per group $k$, dominated by the smallest-sample group.
- Ranking/percentile windows: rank error $\pm\varepsilon n$ achievable with $O(\frac1\varepsilon)$-style quantile sketches per partition (KLL), mergeable across `PARTITION BY`.
- General nested SQL: the **analytical/variational bootstrap** (VerdictDB) gives empirically valid CIs but **no worst-case guarantee** for arbitrary nesting or order-dependent frames.

## 5. Lower Bound
- **Per-group sample starvation (information-theoretic):** with a global sample of size $n$ spread over $g$ groups, some group gets $O(n/g)$ tuples, so correlated-subquery error there is $\Omega(\sigma\sqrt{g/n})$ — no estimator beats this without group-aware (stratified) sampling.
- **Order-dependence / `LAG`:** estimating an exact predecessor value from a sample is information-theoretically impossible without storing neighbors; any sample of rate $p$ misses a neighbor with probability $1-p$, forcing $\Omega(1)$ bias for point-wise `LAG`/`ROW_NUMBER`.
- **Ranking:** distinguishing adjacent ranks needs $\Omega(1/\varepsilon^2)$ samples (order-statistic concentration / quantile lower bound).
- Composition makes errors **multiply**, so stacked operators inherit the product of these floors.

## 6. The Gap
This is **genuinely open**. Flat AQP is closed; nested/window AQP is not even at parity: there is **no general framework with provable CIs** for correlated subqueries with non-linear outer predicates, for order-sensitive window frames, or for `RANK`/`LAG` over samples. The gap is both *theoretical* (no matching upper/lower bounds for composed operators; error propagation through non-linear, order-dependent operators is unsolved in general) and *systems* (bootstrap-based tools give heuristic, not certified, intervals). Closing it requires (a) **stratified/group-aware** sampling that bounds per-group variance, (b) **frame-aware** estimators that model the bias from missing neighbors, and (c) a compositional **error-propagation calculus** across operators.

## 7. Current Research (as of June 2026)
Active directions: (1) **compositional error bounds** — a calculus that propagates and certifies CIs through stacked sample/window/aggregate operators *(frontier — verify)*; (2) learned + sampling hybrids (DeepDB/DBEst descendants) answering nested patterns from densities with calibrated uncertainty; (3) **stratified and outlier-indexed** sampling so correlated subqueries and rare partitions retain accuracy; (4) approximate ranking/top-k windows via per-partition quantile sketches. Groups: Mozafari (Michigan; VerdictDB, analytical bootstrap), Kandula/Chaudhuri (Microsoft; Quickr), the BlinkDB/Berkeley lineage, and the learned-AQP community (Binnig, Kraska, density-model groups).

## 8. Future Work
- A general, certified error-propagation framework for nested/window SQL.
- Stratified/adaptive sampling tuned for correlated-subquery and rare-partition accuracy.
- Frame-aware estimators that correct missing-neighbor bias in `LAG`/moving windows.
- Approximate `RANK`/`ROW_NUMBER`/top-k with tight rank-error guarantees, mergeable across partitions.
- Benchmarks and ground-truth error metrics for nested/analytic AQP.

## 9. Key References
- **[Foundational]** W. Kim. *On Optimizing an SQL-like Nested Query (subquery decorrelation).* ACM TODS, 1982. — [DOI](https://doi.org/10.1145/319732.319745)
- **[Foundational]** U. Dayal. *Of Nests and Trees: A Unified Approach to Processing Queries That Contain Nested Subqueries, Aggregates, and Quantifiers.* VLDB, 1987. — [DBLP](https://dblp.org/rec/conf/vldb/Dayal87)
- **[SOTA]** Y. Park, B. Mozafari, J. Sorenson, J. Wang. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[SOTA]** K. Zeng, S. Gao, B. Mozafari, C. Zaniolo. *The Analytical Bootstrap: A New Method for Fast Error Estimation in Approximate Query Processing.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588579)
- **[SOTA]** S. Kandula et al. *Quickr: Lazily Approximating Complex Ad-Hoc Queries in Big Data Clusters.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2882940)
- **[Foundational]** S. Agarwal et al. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[Survey]** S. Chaudhuri, B. Ding, S. Kandula. *Approximate Query Processing: No Silver Bullet.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056097)

## 10. Worked Example

**Per-group sample starvation.** A `Sales(region, amount)` table has $N=1{,}000{,}000$ rows split over $g=10{,}000$ regions (100 rows each). The query is a correlated subquery: for each region, flag it if its average sale exceeds the global average.

AQP draws a uniform $1\%$ sample, $n=10{,}000$ rows. Spread over 10,000 regions, the *expected* sample per region is $n/g = 1$ row — many regions get 0 or 1 sampled tuple.

For a region with $n_k=1$ sampled row, the estimate $\hat\theta_k$ of its mean is a single observation: standard error $\sigma_k/\sqrt{n_k}=\sigma_k$. With per-region $\sigma_k=200$, the half-width of a 95% CI is about $1.96\times 200 \approx \pm392$ — useless for deciding whether the region's true mean (say 510) beats the global average (500).

The lower bound from section 5 says error in the starved group is $\Omega(\sigma\sqrt{g/n}) = 200\sqrt{10000/10000}=200$ — no uniform-sampling estimator does better. Only **stratified sampling** (guaranteeing, e.g., $n_k\ge 30$ per region) shrinks this; that requires $g\times 30 = 300{,}000$ rows, $30\times$ the uniform budget. This is exactly why correlated subqueries break flat AQP.

---
*Part of the [DBMS Research catalog](../../README.md).*
