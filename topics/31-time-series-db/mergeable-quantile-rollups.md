# Mergeable sketches for rollup percentiles

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/mergeable-quantile-rollups` · **Status:** partially-solved

## 1. Problem Statement
A time-series store ingests points per series and wants to answer percentile (`p50`,`p99`), rank, and heavy-hitter queries over arbitrary time spans and arbitrary *sets* of series, using precomputed per-bucket summaries rather than raw data. The summary $S$ stored for each (series, time-bucket) cell must support:

1. **Mergeability across time:** $S_{[a,b)} = S_{[a,m)} \oplus S_{[m,b)}$, with the same error guarantee as a single sketch built directly on $[a,b)$ — *no error accumulation under repeated merges*.
2. **Mergeability across series:** combine cells from many series into one summary for a tag-selected fleet.
3. **Tight, composable error bounds:** an $\varepsilon$-approximate rank or relative-value guarantee that is preserved (not merely additive) under both axes of merging.

- **Decision variant:** does an $(\varepsilon,\delta)$-mergeable summary of size $g(\varepsilon,\delta)$ independent of $n$ and merge count exist for the target query class?
- **Optimization variant:** minimize sketch size (words/bucket) for a target $\varepsilon$, $\delta$ over a fixed merge depth.
- The companion *nonlinear-rollup-semantics* problem motivates why this is required; here the focus is the sketch and its bounds.

## 2. Mathematical Foundations
Let $D$ be a multiset of $n$ reals. The **rank** of $x$ is $R(x)=|\{y\in D: y\le x\}|$. An **$\varepsilon$-approximate quantile summary** answers any rank query with additive error $\le \varepsilon n$ (uniform error) or a **relative-error** sketch guarantees error $\le \varepsilon\cdot R(x)$ (DDSketch/UDDSketch — crucial for tail latencies where p99.9 matters).

A summary is **mergeable** (Agarwal et al.) if a single $\oplus$ produces a summary with the *same* $\varepsilon$ as one built on the union — i.e. the bound is governed by the final $n$, not by the number of merges. This is the key contrast with sampling-without-mergeability, where errors compound.

- **GK (Greenwald–Khanna):** deterministic, $O(\frac{1}{\varepsilon}\log(\varepsilon n))$ space, fully mergeable.
- **KLL (Karnin–Lang–Liberty):** randomized, $O(\frac{1}{\varepsilon}\log\log\frac{1}{\delta})$ space, optimal up to that factor, fully mergeable; the systems workhorse.
- **t-digest (Dunning):** heuristic, excellent tail accuracy, mergeable but *no worst-case rank bound* — accuracy can degrade adversarially.
- **DDSketch/UDDSketch (Masson et al.):** **relative**-error, mergeable, exact-rank-preserving for the relative guarantee; ideal for latency tails.
- **Heavy hitters:** Misra–Gries and Count-Min/Count-Sketch are mergeable, giving $\varepsilon$-frequency top-$k$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** KLL is space-optimal for uniform $\varepsilon$-quantiles among mergeable summaries up to a $\log\log\frac1\delta$ term; Cormode–Veselý proved the matching comparison lower bound for the deterministic case.
- **Systems-SOTA:** Apache DataSketches ships production KLL/REQ/quantiles and Theta/HLL for distinct counts, all mergeable, used in Druid and Pinot. TimescaleDB hyperfunctions ship `uddsketch` and `tdigest`. Datadog open-sourced DDSketch and uses it fleet-wide. Prometheus *native histograms* (sparse, exponential-bucket) provide mergeable relative-error quantiles at ingest.

## 4. Upper Bound
- **Uniform quantiles:** KLL, $O(\frac{1}{\varepsilon}\log\log\frac{1}{\delta})$ words, merge in time linear in summary size, error $\varepsilon n$ preserved under arbitrary merge trees.
- **Deterministic:** GK / Agarwal–Cormode mergeable variant, $O(\frac{1}{\varepsilon}\log^{1.5}\frac{1}{\varepsilon})$ words (the known fully-mergeable deterministic bound).
- **Relative error:** DDSketch, $O(\frac{1}{\gamma}\log(\max/\min))$ buckets for relative accuracy $\gamma$, exactly mergeable.
- **Heavy hitters:** Misra–Gries with $O(1/\varepsilon)$ counters, mergeable, $\varepsilon n$ frequency error.

## 5. Lower Bound
**Comparison-based deterministic** quantile summaries require $\Omega(\frac{1}{\varepsilon}\log\frac{1}{\varepsilon})$ space (Cormode–Veselý, PODS 2020) — proving GK essentially tight and ruling out an $O(1/\varepsilon)$ deterministic mergeable summary. For **randomized** comparison-based summaries the bound is $\Omega(\frac{1}{\varepsilon}\sqrt{\log\frac1\delta})$-type (KLL near-optimality). Exact quantiles need $\Omega(n)$ (info-theoretic), forcing approximation. Relative-error sketches inherit an $\Omega(\frac{1}{\gamma}\log(\text{range}))$ dependence on the value range.

## 6. The Gap
For uniform-error quantiles the gap is **nearly closed**: KLL matches the lower bound up to $\log\log\frac1\delta$, and whether that factor is removable is the residual open question. The deterministic side is closed to within the $\log\frac1\varepsilon$ exponent. The genuinely **open** practical gaps are: (1) t-digest's lack of a worst-case bound vs. its empirical dominance on real tails; (2) jointly optimal sketches for *correlated* multi-series rollups where the same value range must serve heterogeneous series; (3) sketches that are simultaneously rank-optimal *and* relative-error-optimal.

## 7. Current Research (as of June 2026)
Prometheus **native histograms** are maturing toward GA, making mergeable relative-error quantiles a first-class ingest-time primitive *(frontier — verify exact GA status)*. Work on **ReqSketch** (relative-error KLL variant) and on SIMD/GPU-vectorized merge of DataSketches is active. Research on differentially private mergeable quantiles (combining Dwork-style DP with KLL) and on learned/optimized bucket boundaries continues. Groups: Apache DataSketches (Lee Rhodes), Liberty/Karnin (KLL), Masson/Rim/Ye (DDSketch, Datadog), Cormode's group (mergeable summaries, lower bounds).

## 8. Future Work
- Remove the $\log\log\frac1\delta$ gap in mergeable randomized quantiles.
- Worst-case-bounded sketch matching t-digest's empirical tail accuracy.
- Unified rank-and-relative-error mergeable summary.
- DP-mergeable summaries with tight composition across both time and series axes.
- Hardware-accelerated merge as the bottleneck shifts to query-time fan-in over millions of cells.

## 9. Key References
- **[Foundational]** Greenwald, Khanna. *Space-Efficient Online Computation of Quantile Summaries.* SIGMOD, 2001. — [DOI](https://doi.org/10.1145/375663.375670) — [DBLP](https://dblp.org/rec/conf/sigmod/GreenwaldK01.html)
- **[Foundational]** Agarwal, Cormode, Huang, Phillips, Wei, Yi. *Mergeable Summaries.* ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2500128) — [DBLP](https://dblp.org/rec/journals/tods/AgarwalCHPWY13.html)
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [DOI](https://doi.org/10.1109/FOCS.2016.17) — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** Masson, Rim, Lee. *DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3352063.3352135) — [arXiv](https://arxiv.org/abs/1908.10693)
- **[SOTA]** Cormode, Veselý. *A Tight Lower Bound for Comparison-Based Quantile Summaries.* PODS, 2020. — [DOI](https://doi.org/10.1145/3375395.3387650) — [arXiv](https://arxiv.org/abs/1905.03838)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Consider per-minute latency buckets for one service. **DDSketch** with relative accuracy $\gamma = 0.02$ uses log-scaled bucket boundaries $b_k = (1+\gamma)^k / (1) $, i.e. bucket index $k(v) = \lceil \log_{1+\gamma} v \rceil$. A value $v$ lands in bucket $k$, and any reported quantile $\hat q$ satisfies $|\hat q - q| \le \gamma\, q$ — a *relative* guarantee, ideal for tails.

Minute A sees latencies (ms) $\{100, 105, 980, 1000\}$; minute B sees $\{102, 990, 1010, 1020\}$. With $\gamma = 0.02$, $\log_{1.02} \approx \ln/0.0198$, so $100$ and $105$ share a bucket region near index $\lceil \ln 100 / 0.0198\rceil = 233$, while $\sim 1000$ ms values cluster near index $349$. Each sketch is just a map {bucket index → count}.

**Merge across time** $S_{A\cup B} = S_A \oplus S_B$ is element-wise count addition over the shared bucket grid — no realignment, and the $\gamma = 0.02$ relative bound is preserved on the union of all 8 points (governed by final $n=8$, *not* by the fact we merged twice). Querying p99 returns a value within $2\%$ of the true p99. Contrast a non-mergeable sample: merging two independent samples would compound sampling error, exactly what mergeability (§2) avoids.

---
*Part of the [DBMS Research catalog](../../README.md).*
