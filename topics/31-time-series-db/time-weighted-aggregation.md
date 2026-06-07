---
id: 31-time-series-db/time-weighted-aggregation
title: "Time-weighted and rate aggregation correctness"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Time-weighted and rate aggregation correctness

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/time-weighted-aggregation` · **Status:** partially-solved

## 1. Problem Statement
Given an irregularly-sampled series of (timestamp, value) pairs $S = \{(t_i, v_i)\}_{i=1}^n$ over a window $[a,b]$, compute aggregates that respect the *duration* each value was in effect rather than treating samples as equal-weight:

- **Time-weighted average:** $\bar{v}_{tw} = \frac{1}{b-a}\int_a^b \hat{v}(t)\,dt$ for an interpolation $\hat v$.
- **Time-weighted integral** (e.g. area-under-curve, "device-seconds").
- **Counter rate:** $\frac{v(b) - v(a)}{b-a}$ for a value that is the integral of an underlying rate, *corrected for resets* (see `counter-reset-handling`).

Variants: **decision** — is the time-weighted average within tolerance $\epsilon$ of a target? **computation/streaming** — maintain the aggregate incrementally with bounded state under out-of-order arrival; **partial-aggregate / parallel** — produce mergeable partial states for rollups and distributed reduction.

The correctness subtlety: the answer depends on the **interpolation contract** (LOCF/last-observation-carried-forward vs. linear), boundary handling at $a,b$, and gap policy.

## 2. Mathematical Foundations
For a piecewise-constant (LOCF) interpolant the integral telescopes exactly:
$$\int_a^b \hat v\,dt = \sum_{i} v_i \,(t_{i+1} - t_i),$$
and for linear interpolation each segment contributes trapezoid area $\frac{(v_i+v_{i+1})}{2}(t_{i+1}-t_i)$. The estimator is **exact** for the chosen interpolant — there is no statistical error term given the contract; ambiguity is *semantic*, not algorithmic.

Mergeability requires an **associative, commutative monoid** on partial states. A correct time-weighted partial state must retain *boundary points* $(t_{\text{first}}, v_{\text{first}}, t_{\text{last}}, v_{\text{last}})$ plus the accumulated integral, so that adjacent partials can stitch the cross-boundary trapezoid: the naive (integral-only) state is **not** associative across gaps. This is the same algebra as **segment-tree / Fenwick** range aggregation but over real-valued duration weights. Out-of-order arrival breaks the telescoping order, requiring either buffering (watermarks) or a commutative-monoid formulation closed under reordering.

## 3. State of the Art (SOTA)
**Systems-SOTA.** TimescaleDB's `time_weight()` / `time_weighted_average` (Toolkit) implements both LOCF and linear contracts with a *mergeable two-step aggregate* carrying boundary points — the reference correct implementation. Prometheus/PromQL `rate()`, `increase()`, `irate()` compute per-second rates with extrapolation to window edges and reset correction. InfluxDB `integral()` and `MEAN` (the latter *not* time-weighted, a known footgun). Grafana Mimir/Cortex inherit PromQL semantics. M3DB and VictoriaMetrics provide `rollup_*` functions with explicit duration weighting.

**Theory-SOTA.** Streaming sliding-window aggregation under associative monoids: **FlatFIN/Two-Stacks/DABA** (Tangwongsan, Hirzel, Schneider, *General Incremental Sliding-Window Aggregation*, VLDB 2015) give $O(1)$ amortized updates for any monoid, directly applicable to time-weighted states.

## 4. Upper Bound
Computing the exact time-weighted integral over $n$ samples is $\Theta(n)$ time, $O(1)$ streaming state for in-order data (running integral + last point). Sliding-window with eviction: $O(1)$ amortized per update via DABA/Two-Stacks, $O(w)$ space for window size $w$. Parallel/partial aggregation: $O(\log p)$ depth for $p$ partials with the boundary-augmented monoid. These are tight — the problem is linear-scan-bound.

## 5. Lower Bound
Any algorithm must read every sample in the window to be exact: $\Omega(n)$ in the cell-probe/comparison model (a single unread sample can change the integral arbitrarily). For sliding windows requiring exact results, $\Omega(w)$ space is necessary in the streaming model (an adversary can force recall of any evicted value at the boundary). No approximation lower bound applies because, given a fixed interpolation contract, the computation is exact — the open content is *semantic standardization*, not complexity.

## 6. The Gap
Complexity-wise the gap is **closed**: matching $\Theta(n)$ time and $\Theta(w)$ window space. What remains "partially-solved" is **semantic correctness and portability**: engines disagree on interpolation, boundary extrapolation, gap-vs-reset handling, and whether `avg` is time-weighted at all, so identical queries yield different numbers across TSDBs. Closing this requires a *specified, testable contract* (a standard akin to SQL window-frame semantics) and verified mergeable implementations.

## 7. Current Research (as of June 2026)
Directions: formal/property-based specification of rate and time-weighted semantics (PromQL has community-driven "rate() correctness" RFCs) *(frontier — verify)*; native push-down of time-weighted partial aggregates into columnar/continuous-aggregate engines; Arrow-/DataFusion-based mergeable accumulators for distributed rollups. Groups: TimescaleDB Toolkit team, Prometheus/Grafana maintainers, VictoriaMetrics, and the streaming-aggregation lineage (Hirzel/Tangwongsan/Schneider).

## 8. Future Work
- A cross-engine conformance suite pinning down interpolation/boundary/gap semantics.
- Unified algebra covering time-weighted average, integral, and counter-rate as one mergeable monoid.
- Provably-correct out-of-order handling with watermark-bounded latency.
- Integration with downsampling so rollups preserve time-weighting (avoid double-weighting).

## 9. Key References
- **[SOTA]** Tangwongsan, Hirzel, Schneider, Wu. *General Incremental Sliding-Window Aggregation.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752940)
- **[SOTA]** TimescaleDB Toolkit. *Time-Weighted Average / Two-Step Aggregates.* (project documentation), 2021–. *(unverified)*
- **[Foundational]** Prometheus project. *PromQL `rate()`/`increase()` semantics.* Prometheus documentation, 2015–. *(unverified)*
- **[Survey]** Jensen, Pedersen, Thomsen. *Time Series Management Systems: A Survey.* IEEE TKDE, 2017. — [DOI](https://doi.org/10.1109/TKDE.2017.2740932)
- **[Foundational]** Boncz, Zukowski, Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005. (mergeable vectorized aggregation) — [DBLP](https://dblp.uni-trier.de/rec/conf/cidr/BonczZN05.html)

## 10. Worked Example

A thermostat reports temperature irregularly over the window $[0,10]$ (seconds): $(t,v) = (0,20),(2,20),(8,30)$. Compute the average temperature two ways.

**Naive (equal-weight) `avg`:** $\frac{20+20+30}{3}=23.33$ — wrong, because the $30$ reading covers a tiny slice of time but counts as one-third.

**Time-weighted, LOCF interpolation:** each value holds until the next sample, extended to the window end:
$$\int_0^{10}\hat v\,dt = 20\cdot(2-0)+20\cdot(8-2)+30\cdot(10-8)=40+120+60=220,$$
so $\bar v_{tw}=220/10=\mathbf{22.0}$. The $20$ held for 8s, the $30$ for 2s — correctly down-weighting the brief spike.

**Linear interpolation** changes the middle segment $[2,8]$ to a trapezoid $\frac{20+30}{2}\cdot6=150$ instead of $120$, giving $\int=40+150+60=250$, $\bar v_{tw}=25.0$ — a different answer from the *same data*, illustrating why the interpolation contract must be specified.

**Mergeability:** splitting at $t=5$ requires each partial to keep its boundary point $(t_{\text{last}},v_{\text{last}})$ so the cross-boundary segment $[2,8]$ is stitched once, not double-counted — the integral-only state is not associative here.

---
*Part of the [DBMS Research catalog](../../README.md).*
