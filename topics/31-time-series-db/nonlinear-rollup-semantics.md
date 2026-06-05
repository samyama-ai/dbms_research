# Semantically correct non-linear rollups

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/nonlinear-rollup-semantics` · **Status:** partially-solved

## 1. Problem Statement
Time-series systems precompute *rollups* (continuous aggregates, downsampled buckets) so that long-range queries read coarse summaries instead of raw points. A rollup at resolution $\Delta$ stores, per series and per bucket, some state $s_b$. A query over a span $[t_0,t_1)$ wants $f$ applied to the raw points in the span, but must instead compute it from the bucket states. The problem is **composability**: when is there a merge operator $\oplus$ and a finalizer $\phi$ such that $f(\text{raw}) = \phi(s_{b_1}\oplus\cdots\oplus s_{b_k})$ exactly, and what do we do when no exact $\oplus$ exists?

For *decomposable* (algebraic/distributive) aggregates — `sum`, `count`, `min`, `max`, `avg` (as sum+count) — exact composition is trivial. The hard cases are **non-linear / holistic** aggregates: percentiles (`p99`), `count distinct`, top-$k$/heavy hitters, and **rates** (`rate`, `increase`, `irate` over counters with resets). Naively re-aggregating bucket finals (e.g. averaging per-bucket p99s) is *semantically wrong*.

- **Decision variant:** given aggregate $f$ and bucket granularity, does a finite-state exact rollup with associative merge exist?
- **Optimization variant:** minimize stored state size (bits/bucket) subject to an error bound $\varepsilon$ on the finalized result.
- **Counting variant:** for `count distinct` and rates over resettable counters, recover the exact answer from per-bucket summaries.

## 2. Mathematical Foundations
The canonical classification is Gray et al.'s data-cube taxonomy: **distributive** ($F(X\cup Y)=G(F(X),F(Y))$ for some $G$), **algebraic** (finalizer over a fixed-size tuple of distributive sub-aggregates), and **holistic** (no constant-bound intermediate state suffices, e.g. exact median, mode, rank). Holistic aggregates are precisely those with *no* associative, constant-space exact rollup — this is the formal obstruction.

For composability we want a **commutative monoid** $(\mathcal{S},\oplus,e)$ on rollup states with a homomorphism from raw multisets, plus a finalizer $\phi:\mathcal{S}\to\mathbb{R}$. `sum`, `count`, `min`, `max` are monoids; `avg`=algebraic. Percentiles and distinct counts are holistic, so exactness forces $|\mathcal{S}|$ to grow with the data, defeating the rollup. The escape is **approximation**: replace exact $f$ by a $(\varepsilon,\delta)$-mergeable sketch (see companion problem on mergeable quantile rollups), trading an $\varepsilon$ rank/relative error for $O(\text{polylog})$ state.

Rates need a different model: a **counter** is a monotone step function with occasional resets to 0. `increase` over $[t_0,t_1)$ must detect and compensate resets; the correct rollup state per bucket is the tuple (first value, last value, max, reset-adjusted cumulative delta), which *is* algebraic and composable once resets are encoded — Prometheus's PromQL formalizes this with extrapolation at boundaries.

## 3. State of the Art (SOTA)
- **Systems:** TimescaleDB *continuous aggregates* support real-time + materialized rollups; for percentiles it ships the `tdigest` and `uddsketch` hyperfunctions (approximate, mergeable). InfluxDB IOx / Flux downsampling. Druid uses approximate sketches (Theta, quantiles-DoublesSketch from Apache DataSketches) precisely because holistic aggregates can't be exactly rolled up. M3DB / Mimir / Cortex implement PromQL rate semantics over chunked counters.
- **Theory:** Gray et al. data cube (VLDB Journal 1997) gives the decomposability taxonomy; Cohen & Strauss, and Cormode's sketch line, give the mergeable-summary basis for the approximate cases.

## 4. Upper Bound
For distributive/algebraic $f$: exact rollup in $O(1)$ state per bucket, merge in $O(1)$, query over $k$ buckets in $O(k)$ (or $O(\log k)$ with a hierarchical/aggregating tree of pre-merged levels). For holistic $f$ under approximation: $O(\frac{1}{\varepsilon}\log(\varepsilon n))$ space per series-bucket for $\varepsilon$-approximate quantiles (KLL/GK-class), fully mergeable, finalize in $O(\frac{1}{\varepsilon})$. Rates: $O(1)$ state per bucket, exact under the counter-reset model.

## 5. Lower Bound
Exact holistic aggregates admit a **communication / information-theoretic** lower bound: any rollup that answers exact $\phi$-quantiles or exact `count distinct` over an arbitrary span must, in the worst case, retain $\Omega(n)$ bits — exact median is not computable in sublinear merge-able state (a standard reduction from the indexing/streaming exact-selection lower bounds). For approximate quantiles, the comparison-based lower bound is $\Omega(\frac{1}{\varepsilon}\log\frac{1}{\varepsilon\delta})$ words (Cormode–Veselý), matched by KLL up to log factors.

## 6. The Gap
For decomposable and rate aggregates the gap is **closed**: tight $O(1)$ exact rollups exist. For holistic aggregates the gap is **provably unbridgeable exactly** (the $\Omega(n)$ bound), so the open frontier is entirely about the approximate regime: closing the residual $\log\frac{1}{\varepsilon}$ factor between KLL and the comparison lower bound, and extending exactness/mergeability to *correlated* finalizers (e.g. ratios of two holistic aggregates, p99-of-p50) where error compounds non-trivially.

## 7. Current Research (as of June 2026)
Active work targets (a) *error-bounded* continuous aggregates where the planner picks raw-vs-rollup based on the requested error, (b) UDDSketch-style relative-error sketches as first-class rollup state in TimescaleDB and Apache DataSketches, and (c) PromQL semantic-correctness formalization for `rate`/`increase` extrapolation, with proposals to replace heuristic boundary extrapolation by exact reset-tracking *(frontier — verify)*. Groups: Timescale (hyperfunctions team), Apache DataSketches (Yahoo/Verizon lineage, Lee Rhodes), Cormode's group on mergeable summaries.

## 8. Future Work
- A complete algebra of which *compositions* of holistic aggregates remain finalizable with bounded error.
- Cost models that let the query planner choose rollup granularity per requested $\varepsilon$.
- Exact, space-optimal counter-reset encodings robust to out-of-order arrival (see late-arrival problem).
- Standardizing rate semantics across Prometheus/InfluxDB/SQL so rollups are portable.

## 9. Key References
- **[Foundational]** Gray, Chaudhuri, Bosworth, Layman, Reichart, Venkatrao, Pellow, Pirahesh. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* Data Mining and Knowledge Discovery / VLDB Journal, 1997. — [DOI](https://doi.org/10.1023/A:1009726021843)
- **[Foundational]** Agarwal, Cormode, Huang, Phillips, Wei, Yi. *Mergeable Summaries.* ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2500128), [DBLP](https://dblp.org/rec/journals/tods/AgarwalCHPWY13.html)
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** Cormode, Veselý. *A Tight Lower Bound for Comparison-Based Quantile Summaries.* PODS, 2020. — [arXiv](https://arxiv.org/abs/1905.03838), [DOI](https://doi.org/10.1145/3375395.3387650)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Two adjacent 1-minute buckets each hold 5 latency samples:

- Bucket $A$ = $\{10, 20, 30, 40, 50\}$, finalized $p99(A)\approx 50$.
- Bucket $B$ = $\{60, 70, 80, 90, 100\}$, finalized $p99(B)\approx 100$.

A 2-minute query wants $p99$ over all 10 points $\{10,\dots,100\}$. The true answer is $\approx 99$.

**Wrong (re-aggregate finals):** averaging the per-bucket $p99$s gives $(50+100)/2 = 75$ — off by 24. Even taking the max, $100$, only happens to be close here and fails whenever the high bucket is the smaller one. This is the holistic-aggregate trap: $p99$ is *not* distributive, so no associative merge of scalar finals is correct.

**Right (mergeable sketch):** store a KLL/GK sketch per bucket instead of the scalar. Merging the two sketches yields a summary of all 10 values; querying rank $0.99$ returns an item within $\pm\varepsilon n$ of true rank. With $\varepsilon = 0.05$ and $n=10$, the error tolerance is $\pm 0.5$ ranks — the sketch returns $90$ or $100$, both valid $0.99$-quantiles. State per bucket is $O(\tfrac{1}{\varepsilon}\log(\varepsilon n))$ words, and the merge is exact-as-a-monoid, so the rollup composes across arbitrarily many buckets without the averaging error.

---
*Part of the [DBMS Research catalog](../../README.md).*
