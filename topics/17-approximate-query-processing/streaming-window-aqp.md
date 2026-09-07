---
id: 17-approximate-query-processing/streaming-window-aqp
title: "AQP Over Streaming and Sliding Windows"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# AQP Over Streaming and Sliding Windows

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/streaming-window-aqp` · **Status:** partially-solved

## 1. Problem Statement
A high-velocity stream of tuples arrives, and queries ask for aggregates (`COUNT`, `SUM`, quantiles, distinct count, heavy hitters, $F_2$) over a *recent* portion of the stream: a **sliding window** of the last $W$ items (or last $\Delta$ time units), or an **exponentially time-decayed** view that weights recent data more. The goal is a synopsis that, using memory $\ll W$ (ideally $\mathrm{poly}(\tfrac1\varepsilon,\log W)$), answers with $(1\pm\varepsilon)$ error, stays **fresh** under continuous ingest and expiry, and supports per-tuple update in $O(\mathrm{polylog})$ time.

The defining tension is *expiry*: unlike append-only streams, sliding windows must "forget" old tuples, which breaks the linearity many sketches rely on (you cannot subtract an item you no longer stored). Variants: **fixed-size** ($W$ items) vs. **time-based** windows; **count-based decay** vs. continuous **time-decay** ($\lambda$-exponential, polynomial); the **decision** variant (is a windowed aggregate above threshold?) and the **monitoring** variant (continuous, anytime answers). It is partially-solved: smooth-histogram and exponential-histogram frameworks give tight bounds for a broad class, but several functionals (distinct count, $L_2$, quantiles) have residual gaps and the time-decay setting is less complete than the count-based one.

## 2. Mathematical Foundations
Let the stream be $a_1,a_2,\dots$ and the window be the last $W$ elements. The **Exponential Histogram** (Datar–Gionis–Indyk–Motwani, SODA 2002) maintains $O(\tfrac1\varepsilon\log W)$ buckets of geometrically growing size, giving $(1\pm\varepsilon)$ for `COUNT`/`SUM` over sliding windows with $O(\tfrac1\varepsilon\log^2 W)$ bits. The **Smooth Histogram** (Braverman–Ostrovsky, FOCS 2007) generalizes this to all *$(\alpha,\beta)$-smooth* functions $f$ — those where once two suffixes' values get $\beta$-close they stay $\alpha$-close — covering $L_p$ norms, frequency moments, longest-increasing-subsequence-type measures, and more, at $O(\tfrac1\varepsilon\log W)\cdot(\text{sketch size})$ space.

Time-decay uses weights $w(t)=e^{-\lambda(t_{\text{now}}-t)}$; the **decayed aggregate** $\sum_i w(t_i) a_i$ admits mergeable forward-decay sketches (Cormode–Shkapenyuk–Srivastava–Xu) by factoring decay into a landmark, avoiding rescaling. Quantiles over windows use mergeable summaries (GK, KLL) with windowing wrappers. Lower bounds use **communication complexity** over the window contents: the deterministic-counting lower bound forces $\Omega(\tfrac1\varepsilon\log^2(\varepsilon W))$ bits for $(1\pm\varepsilon)$ basic counting, matching DGIM.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** DGIM exponential histograms (basic counting, $L_1$); smooth histograms (general smooth functions, $L_p$, $p\le 2$); randomized window sketches for $F_2$ and distinct-count (Gibbons–Tirthapura "distinct elements in windows"). KLL/GK give mergeable windowed quantiles.
- **Systems-SOTA:** `Apache Flink`/`Spark Structured Streaming` ship sliding-window aggregations with `DataSketches` (HLL, KLL, Theta) for approximate distinct/quantile/heavy-hitters; `Druid` and `Apache DataSketches` support time-windowed mergeable sketches at scale; `Snowflake`/`BigQuery` streaming `APPROX_*` functions on micro-batches.

## 4. Upper Bound
Sliding-window `COUNT`/`SUM`: $O(\tfrac1\varepsilon\log^2(\varepsilon W))$ bits, $O(1)$ amortized update (DGIM). Any smooth function $f$ with base sketch of size $s$: $O(\tfrac1\varepsilon \log W\cdot s)$ space (smooth histogram). Windowed distinct count: $O(\tfrac1{\varepsilon^2}\log W\log\tfrac1\delta)$ (Gibbons–Tirthapura). Windowed quantiles: $O(\tfrac1\varepsilon\log\tfrac1\varepsilon\log W)$. All in the **streaming model** with bounded memory and high ingest, per-update polylog.

## 5. Lower Bound
Basic windowed counting needs $\Omega(\tfrac1\varepsilon\log^2(\varepsilon W))$ bits — a **deterministic communication-complexity** lower bound (DGIM), matched by their upper bound, so `COUNT` is *closed*. For windowed $F_0$/distinct and $F_2$, randomization is essential: $\Omega(\tfrac1{\varepsilon^2})$ from the streaming $F_p$ lower bounds plus a $\log W$ window penalty. Exactness over a window of size $W$ requires $\Omega(W)$ space (you must remember the expiring element) — information-theoretic. These hold in the streaming/communication model unconditionally.

## 6. The Gap
For `COUNT`/`SUM` and the broad smooth-function class the bounds are **tight (closed)**. Open gaps remain for: (i) the exact $\varepsilon$-dependence of *non-smooth* windowed functionals (e.g. entropy, certain quantile regimes) where smooth-histogram does not apply; (ii) tight bounds for **time-decayed** (continuous, non-window) aggregates, which are less fully characterized than count-based windows; and (iii) per-update worst-case (not amortized) time matching the space optima under adversarial ingest order.

## 7. Current Research (as of June 2026)
Active directions: robust/adversarial streaming so windowed sketches survive input chosen adaptively against the synopsis; unifying time-decay and sliding-window theory under one framework; hardware-conscious (SIMD/GPU) sliding-sketch implementations for million-events-per-second ingest; learned windowed synopses. *(frontier — verify)* Recent 2025 work on adversarially-robust sliding-window sketches tightens the overhead factor for windowed distinct-count, but a fully tight robust bound across all $F_p$ in windows is not settled.

## 8. Future Work
- Tight bounds for time-decayed aggregates matching the count-based window theory.
- Adversarially-robust windowed sketches with minimal space/time overhead.
- Smooth-histogram-style general frameworks for non-smooth functionals (entropy, holistic aggregates).

## 9. Key References
- **[Foundational]** Datar, M., Gionis, A., Indyk, P., Motwani, R. *Maintaining Stream Statistics over Sliding Windows.* SODA, 2002 / SIAM J. Computing. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[Foundational]** Braverman, V., Ostrovsky, R. *Smooth Histograms for Sliding Windows.* FOCS, 2007. — [DOI](https://doi.org/10.1109/FOCS.2007.55)
- **[Foundational]** Gibbons, P., Tirthapura, S. *Distributed Streams Algorithms for Sliding Windows.* SPAA, 2002. — [DOI](https://doi.org/10.1145/564870.564880)
- **[SOTA]** Cormode, G., Shkapenyuk, V., Srivastava, D., Xu, B. *Forward Decay: A Practical Time Decay Model for Streaming Systems.* ICDE, 2009. — [DOI](https://doi.org/10.1109/ICDE.2009.65)
- **[SOTA]** Karnin, Z., Lang, K., Liberty, E. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[Survey]** Cormode, G., Garofalakis, M., Haas, P., Jermaine, C. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

**DGIM exponential histogram** for `COUNT` of 1-bits in a sliding window of $W=16$ over a bit stream, with relative error $\varepsilon = 1/2$ (so at most $1$ bucket per size class). Stream (most recent on the right), timestamps mod $2W$:

```
... 1 0 1 1 0 1 1 1   (last 8 bits shown, current time t=40)
```

DGIM keeps buckets of 1-counts that are powers of two, each tagged with the timestamp of its most recent 1. Suppose buckets (size @ end-timestamp) are: $4@33,\; 2@37,\; 2@39,\; 1@40$. Query "how many 1s in last $W=16$"? The window covers timestamps $25..40$. All four buckets' end-times lie inside, so we sum them fully *except* the oldest, which may straddle the window edge — DGIM counts **half** of it: $\hat C = 1 + 2 + 2 + \tfrac{4}{2} = 7$.

The true count might be $5$ to $9$; the half-bucket rule guarantees $|\hat C - C| \le \tfrac12 \cdot(\text{oldest bucket size}) = 2 \le \varepsilon C$. Memory: $O(\tfrac1\varepsilon \log W) = O(2 \cdot 4) = 8$ buckets, each $O(\log W)=4$ bits for its timestamp — i.e. $O(\tfrac1\varepsilon\log^2 W)$ bits total, matching the bound in section 4 rather than the $\Omega(W)=16$ bits exact counting would need.

---
*Part of the [DBMS Research catalog](../../README.md).*
