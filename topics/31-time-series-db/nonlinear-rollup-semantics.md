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
- **[Foundational]** Gray, Chaudhuri, Bosworth, Layman, Reichart, Venkatrao, Pellow, Pirahesh. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* Data Mining and Knowledge Discovery / VLDB Journal, 1997.
- **[Foundational]** Agarwal, Cormode, Huang, Phillips, Wei, Yi. *Mergeable Summaries.* ACM TODS, 2013.
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016.
- **[SOTA]** Cormode, Veselý. *A Tight Lower Bound for Comparison-Based Quantile Summaries.* PODS, 2020.
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
