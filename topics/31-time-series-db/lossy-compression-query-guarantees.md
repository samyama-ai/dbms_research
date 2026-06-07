---
id: 31-time-series-db/lossy-compression-query-guarantees
title: "Lossy compression with downstream-query guarantees"
topic: 31-time-series-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Lossy compression with downstream-query guarantees

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/lossy-compression-query-guarantees` · **Status:** open

## 1. Problem Statement

Standard lossy time-series compressors bound the **per-point** error (typically $L_\infty$ or $L_2$ on raw samples). But analytics consume **derived** quantities: windowed aggregates (SUM/AVG/MIN/MAX/quantiles), forecasts, correlations, and anomaly scores. The problem: design lossy codecs whose error bound is stated and provably enforced on the **downstream query output**, not (only) on raw points.

Variants:
- **Aggregate-guarantee:** guarantee $|\text{AGG}(\hat{x}) - \text{AGG}(x)| \le \delta$ for a query class (sliding sums, group-by aggregates).
- **Forecast/model-guarantee:** bound the change in a trained forecaster's or anomaly detector's output induced by compression.
- **Optimization:** minimize size subject to the downstream guarantee (vs. the raw-point guarantee).

The core insight: a small per-point $\varepsilon$ may either over-pay (aggregates average out noise → looser raw bound suffices) or under-protect (MAX/quantiles/anomaly thresholds are sensitive to single extremes).

## 2. Mathematical Foundations

Let $x \in \mathbb{R}^n$, $\hat{x}$ the reconstruction, $e = \hat{x} - x$. For a query $Q$, we want $|Q(\hat x) - Q(x)| \le \delta$.

- **Linear aggregates** (SUM over window $W$): $Q(\hat x)-Q(x)=\sum_{i\in W} e_i$. A per-point $L_\infty$ bound gives only $|W|\varepsilon$ (loose); but bounding **cumulative/prefix error** $|\sum_{i\le t} e_i|\le \delta$ directly controls every windowed sum (telescoping). This motivates codecs that bound *integrated* error, not pointwise — connecting to $L_1$/total-variation guarantees rather than $L_\infty$.
- **MIN/MAX/quantiles:** order statistics are 1-Lipschitz in $L_\infty$, so per-point $\varepsilon$ transfers, but quantile *rank* shifts need bounded sorting perturbation.
- **Forecasts:** for a Lipschitz model $f$ with constant $L_f$, $|f(\hat x)-f(x)|\le L_f\|e\|$; for linear AR models this is exact and the relevant norm is determined by the coefficient vector.
- **Anomaly scores** (e.g., z-score, residual magnitude): sensitive to both mean and variance perturbation; guarantees require bounding $\|e\|_2$ and possibly higher moments.

Thus the problem is choosing the **error functional** matched to the query class and building a codec optimal under that functional — a shift from worst-case $L_\infty$ to **query-induced norms**.

## 3. State of the Art (SOTA)

- **Foundational lossy TSDB:** PMC piecewise-constant (Lazaridis-Mehrotra 2003), SwingFilter/SlideFilter (2009), all $L_\infty$ raw-point.
- **Error-bounded scientific compressors:** **SZ** (Di & Cappello, IPDPS 2016) and **ZFP** (Lindstrom, 2014) — bound raw pointwise/relative error; widely used but **agnostic to downstream queries**.
- **Aggregate-aware (closest):** sketch-based summaries (**t-digest** for quantiles; **DDSketch**, Masson et al. 2019 — relative-error quantile guarantee) give downstream guarantees but are query-specific summaries, not general codecs. **Buri / query-aware lossy** lines and **wavelet/ histogram synopses with error guarantees** (Garofalakis-Gibbons, 2002) provide guaranteed-error wavelet thresholding for aggregate queries.
- **Open:** no general lossy time-series codec offers tunable, *proven* guarantees across a broad downstream-query class simultaneously.

## 4. Upper Bound

- **Wavelet/histogram synopses** (Garofalakis-Gibbons) give probabilistic and deterministic maximum-error guarantees for range-sum queries with provable size–error tradeoffs.
- **DDSketch/t-digest** give relative-error quantile guarantees with $O(\log(\text{range}/\alpha))$ or near-constant space per bucket.
- For linear AR forecasts, propagating an $L_2$ raw bound through the (known) coefficient vector yields a tight forecast-error bound. These are the best-known and are query-class-specific, not unified.

## 5. Lower Bound

- **Sketch lower bounds:** quantile/heavy-hitter summaries have known space lower bounds ($\Omega(\frac{1}{\varepsilon}\log\frac{1}{\varepsilon})$ comparison-based quantiles; communication-complexity bounds for distinct/frequency moments). Any codec answering these with guarantee $\delta$ inherits them.
- **Information-theoretic:** rate–distortion theory lower-bounds bits for a target *distortion measure*; choosing the query-induced distortion changes the rate floor but a floor remains.
- No single codec can simultaneously be size-optimal for incompatible query-induced norms (a per-point-MAX query and an averaging query pull in opposite directions) — a Pareto impossibility.

## 6. The Gap

Open and wide. We have query-specific guaranteed synopses (quantiles, range-sums) and raw-point lossy codecs, but **no general framework** that (a) takes a declared downstream-query workload, (b) derives the matched error functional, and (c) produces a size-optimal lossy encoding with proven end-to-end bounds — especially for forecasts and learned anomaly detectors. Closing it needs a rate–distortion theory parameterized by query class plus constructive codecs meeting it.

## 7. Current Research (as of June 2026)

- Query-/workload-aware lossy compression that bounds aggregate and quantile error jointly *(frontier — verify)*.
- Error-bounded ML-inference-preserving compression (bound change in forecaster/detector output) — emerging at the ML-systems / TSDB boundary *(frontier — verify)*.
- Differentially-private-style analysis of compression-induced perturbation on analytics.
- Groups: Argonne (Cappello, SZ line), LLNL (Lindstrom, ZFP), Datadog (DDSketch), and academic TSDB groups (Aalborg ModelarDB, Athens).

## 8. Future Work

- A rate–distortion framework indexed by query class with matching codecs.
- Guarantees for nonlinear/learned forecasters and anomaly detectors.
- Multi-query Pareto-optimal lossy encodings and impossibility characterizations.

## 9. Key References

- **[Foundational]** M. Garofalakis, P. Gibbons. *Wavelet Synopses with Error Guarantees.* SIGMOD, 2002. — [DOI](https://doi.org/10.1145/564691.564746)
- **[SOTA]** S. Di, F. Cappello. *Fast Error-Bounded Lossy HPC Data Compression with SZ.* IPDPS, 2016. — [DOI](https://doi.org/10.1109/IPDPS.2016.11)
- **[Foundational]** P. Lindstrom. *Fixed-Rate Compressed Floating-Point Arrays (ZFP).* IEEE TVCG, 2014. — [DOI](https://doi.org/10.1109/TVCG.2014.2346458)
- **[SOTA]** C. Masson, J. Rim, H. Lee. *DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3352063.3352135) — [arXiv](https://arxiv.org/abs/1908.10693)
- **[Foundational]** T. Berger. *Rate Distortion Theory: A Mathematical Basis for Data Compression.* Prentice-Hall, 1971. — [archive.org](https://archive.org/details/ratedistortionth0000berg)
- **[SOTA]** S. Jensen, T. Pedersen, C. Thomsen. *ModelarDB: Modular Model-Based Time Series Management.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3236187.3236215)

## 10. Worked Example

Let $x = (10, 12, 11, 13, 14)$ and a codec with per-point bound $\varepsilon = 1$ that happens to round every point *up*, giving error $e = (+1, +1, +1, +1, +1)$, so $\hat x = (11,13,12,14,15)$. Each point satisfies $|e_i| \le \varepsilon$.

**Why per-point bounds mislead downstream:** consider the windowed SUM over all 5 points. True SUM $= 60$, approximate SUM $= 65$. The naive transfer bound is $|W|\varepsilon = 5\times 1 = 5$, and indeed the error is exactly $5$ — the biased errors do *not* cancel. A codec that instead bounded **cumulative/prefix error** $|\sum_{i\le t} e_i| \le \delta$ would directly cap every windowed sum at $\delta$, regardless of window length: a tighter, query-matched guarantee.

**Contrast with MAX:** $\max(x)=14$, $\max(\hat x)=15$, error $1 = \varepsilon$ — order statistics are 1-Lipschitz in $L_\infty$, so the per-point bound transfers cleanly here. The lesson of section 2: SUM wants an integrated ($L_1$/prefix) functional while MAX is fine with $L_\infty$, and the two pull in opposite directions, the Pareto impossibility of section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
