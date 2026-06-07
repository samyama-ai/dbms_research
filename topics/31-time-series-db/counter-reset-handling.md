---
id: 31-time-series-db/counter-reset-handling
title: "Counter reset and monotonicity handling"
topic: 31-time-series-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Counter reset and monotonicity handling

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/counter-reset-handling` · **Status:** empirically-open

## 1. Problem Statement
A **monotonic counter** is a series $c(t)$ that should be non-decreasing because it accumulates an underlying rate $\lambda(t) \ge 0$, with $c(t) = c(0) + \int_0^t \lambda(s)\,ds$. In practice counters violate monotonicity via:

1. **Resets** — process restart sets the counter back to 0;
2. **Rollovers** — fixed-width counter wraps modulo $2^k$;
3. **Missing samples / gaps** — scrape failures hide whether a reset occurred;
4. **Out-of-order or duplicate samples**.

Goal: recover a correct **delta** $\Delta = c(b)-c(a)$ and **rate** $\hat\lambda = \Delta/(b-a)$ over a window despite these artifacts. Variants: **detection** — did a reset occur in $[t_i,t_{i+1}]$? **estimation** — best estimate of true accumulated increase; **decision** — is the reset-corrected rate $> \theta$ (alerting).

The core difficulty is **identifiability**: a single observed *drop* $c_{i+1} < c_i$ is ambiguous between a reset (true increase $= c_{i+1}$ plus pre-reset tail) and a rollover (true increase $= 2^k - c_i + c_{i+1}$), and *increases* can hide an even number of resets entirely.

## 2. Mathematical Foundations
Standard heuristic: treat any decrease as exactly one reset and add back the pre-drop value, summing per-interval corrected deltas
$$\widehat{\Delta} = \sum_{i: c_{i+1}\ge c_i}(c_{i+1}-c_i) \;+\; \sum_{i: c_{i+1}<c_i} c_{i+1}.$$
This is **provably correct iff** at most one reset occurs per sampling interval and no rollover — i.e. the **Nyquist-style condition** $\Delta t <$ (min reset spacing). With $m$ resets in one interval the heuristic undercounts by the lost pre-reset tails; this is an *information-theoretic* loss — sub-sampling below the reset rate is unrecoverable without side information (counter width, restart events).

Edge extrapolation (PromQL `rate()`) fits the boundary by assuming the rate is locally constant and extrapolating to $[a,b]$, an MLE under a homogeneous-Poisson-rate model $\lambda$ over the window. Rollover correction requires knowing width $k$; then $c_{i+1}-c_i \bmod 2^k$ disambiguates *if* $\lambda\,\Delta t < 2^k$ (no full wrap), again a sampling-rate condition.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Prometheus PromQL `rate()`/`increase()` apply the one-reset-per-interval heuristic plus boundary extrapolation; `resets()` counts detected drops. VictoriaMetrics refines edge extrapolation and staleness handling; InfluxDB `non_negative_derivative`/`difference` and the `NON_NEGATIVE_DIFFERENCE` family clamp negatives. OpenTelemetry's metrics model adds explicit *start-time / cumulative-vs-delta* temporality, sidestepping reset ambiguity by transmitting deltas with start timestamps — the principled fix. M3/Mimir/Thanos inherit and extend PromQL semantics for downsampled blocks.

**Theory-SOTA.** No closed reset-recovery theory; the topic sits in change-point detection and sampling theory. The OpenMetrics/OTel "start timestamp" design is the SOTA *engineering* answer because it removes the identifiability problem at the source.

## 4. Upper Bound
Under the Nyquist condition (≤1 reset/interval, no full rollover), correction is **exact** in $O(n)$ time, $O(1)$ streaming state. With explicit start-timestamps (OTel cumulative temporality), delta recovery is exact and $O(1)$ regardless of reset frequency. Rollover with known width $k$ and bounded per-interval increase: exact in $O(n)$. These are the strongest guarantees available and are tight for a single linear pass.

## 5. Lower Bound
Without side information, reset recovery is **information-theoretically impossible** below the reset/rollover sampling rate: distinct true series with $m\ge 2$ inter-sample resets are observationally indistinguishable, so no estimator achieves bounded error in the worst case (a Shannon/Nyquist aliasing argument). Detection of even a *single* reset from samples alone is impossible when a reset is followed by enough accumulation to exceed the prior value before the next sample. Thus any worst-case-correct algorithm must assume the sampling condition or consume out-of-band restart/width metadata — an unconditional impossibility, not a complexity-conditional one.

## 6. The Gap
The gap is **fundamental, not closable by cleverer algorithms**: the limitation is identifiability, not computation. Closing it operationally means *adding information* — start timestamps (OTel), reset event streams, or counter-width metadata — rather than improving estimators. "Empirically open" reflects that real deployments still ship bare cumulative counters; the open work is migration, robust heuristics for legacy data, and quantifying error under realistic reset distributions.

## 7. Current Research (as of June 2026)
Directions: industry-wide adoption of OpenTelemetry delta/cumulative temporality with explicit start-time to eliminate reset ambiguity *(frontier — verify)*; improved staleness/extrapolation handling in VictoriaMetrics and Prometheus native histograms; probabilistic reset estimators under known restart priors. Groups: Prometheus/Grafana maintainers, OpenTelemetry metrics SIG, VictoriaMetrics, and observability vendors (Datadog, Chronosphere) refining rate semantics over downsampled tiers *(frontier — verify)*.

## 8. Future Work
- Standardized, testable reset semantics across engines and downsampling levels.
- Error bounds for rate estimates as a function of scrape interval vs. reset-rate distribution.
- Loss-free rollups that preserve reset boundaries (avoid double-counting across compaction).
- Bridging legacy cumulative counters to OTel start-time temporality automatically.

## 9. Key References
- **[Foundational]** Prometheus project. *Counter semantics: `rate()`, `increase()`, `resets()`.* Prometheus documentation, 2015–. — [docs](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)
- **[SOTA]** OpenTelemetry. *Metrics Data Model — Cumulative vs. Delta Temporality and Start Time.* OTel specification, 2021–. — [spec](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)
- **[Foundational]** OpenMetrics. *Counter and `_total` Semantics.* OpenMetrics specification / CNCF, 2020. — [spec](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md)
- **[Survey]** Jensen, Pedersen, Thomsen. *Time Series Management Systems: A Survey.* IEEE TKDE, 2017. — [DOI](https://doi.org/10.1109/TKDE.2017.2740932)
- **[Foundational]** Aminikhanghahi, Cook. *A Survey of Methods for Time Series Change Point Detection.* Knowledge and Information Systems, 2017. — [DOI](https://doi.org/10.1007/s10115-016-0987-z)

## 10. Worked Example

A request counter is scraped at samples $c = [10,\ 14,\ 3,\ 9]$ (one process restart between samples 2 and 3 zeroed it). True increase: from 10 it rose to (say) 16 before the reset — contributing $16-10=6$ pre-restart — then $0\to9$ after, total $6+9=15$.

The PromQL one-reset-per-interval heuristic:

$$\widehat{\Delta} = \sum_{i:\,c_{i+1}\ge c_i}(c_{i+1}-c_i) \;+\; \sum_{i:\,c_{i+1}<c_i} c_{i+1}.$$

Interval-by-interval: $14\ge10\Rightarrow+4$; $3<14\Rightarrow$ add $c_{i+1}=3$ (reset, add post-drop value); $9\ge3\Rightarrow+6$. So $\widehat{\Delta}=4+3+6=13$.

The estimate **undercounts by 2** ($13$ vs. true $15$): the heuristic adds back the post-reset value $3$, but the *real* pre-reset tail was $16-14=2$ higher — lost because we never sampled the peak $16$. This is the identifiability loss: it is provably exact **iff** $\le 1$ reset per interval *and* the pre-reset value at drop equals the last observed sample, i.e. the Nyquist-style condition $\Delta t<$ (min reset spacing) with dense enough sampling. OTel cumulative-vs-delta temporality with an explicit start timestamp would transmit the true $+15$ directly, removing the ambiguity at the source.

---
*Part of the [DBMS Research catalog](../../README.md).*
