---
id: 19-temporal-databases/temporal-aggregation-sketches
title: "Temporal Aggregation Sketches"
topic: 19-temporal-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Temporal Aggregation Sketches

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-aggregation-sketches` · **Status:** partially-solved

## 1. Problem Statement
Given a temporal relation where each tuple carries a value and a time period (or timestamp), support **approximate aggregate queries over an arbitrary time range** $[a,b)$ — `COUNT`, `SUM`, `AVG`, distinct-count, quantiles, heavy hitters, `MIN/MAX` — using a **small, mergeable summary** rather than the full data. "Mergeable" means the summary of $[a,c)$ can be obtained by combining the summaries of $[a,b)$ and $[b,c)$ with no loss beyond the per-summary error, enabling distributed/parallel construction and hierarchical range answering.

Variants:
- **Range-aggregate (decision/optimization):** answer $\text{AGG}(R, [a,b))$ within $(\epsilon,\delta)$ using space sublinear in the number of tuples / time points.
- **Sliding window:** maintain the aggregate over the last $W$ time units under a stream.
- **Instantaneous / cumulative temporal aggregation:** report the aggregate as a *function of time* (a step function over the timeline), the classic temporal-DB operator.
- **Sequenced grouping:** aggregates partitioned by value groups, each over time.

Difficulty: tuples have *intervals*, so a single tuple contributes to a whole time range; range queries can start/end anywhere; and the summary must be both *mergeable* and *decomposable* over arbitrary, not just suffix, ranges.

## 2. Mathematical Foundations
The backbone is the theory of **mergeable summaries** (Agarwal–Cormode–Huang–Phillips–Wei–Yi, PODS/TODS 2012): a summary class is mergeable if merging two summaries of size $s$ yields a summary of size $s$ with the same error guarantee. Key instances:
- **Count/sum:** linear sketches (Count-Min, AMS) are trivially mergeable (additive); $\ell_p$-norm via $p$-stable sketches.
- **Distinct count:** **HyperLogLog** (Flajolet et al.) and KMV sketches — mergeable via register-max / min-union, error $O(1/\sqrt{m})$.
- **Quantiles:** **GK (Greenwald–Khanna)**, $\epsilon$-approximate; the **KLL sketch** (Karnin–Lang–Liberty, FOCS 2016) is optimal at $O(\tfrac1\epsilon \log\log\tfrac1\delta)$ space and mergeable.
- **Heavy hitters:** SpaceSaving/Misra–Gries, mergeable.

Temporal range answering layers these over an interval/segment structure. The canonical tool is **dyadic decomposition**: a range $[a,b)$ splits into $O(\log T)$ dyadic intervals, each holding a precomputed sketch, so any range aggregate is the merge of $O(\log T)$ summaries — extending **Exponential Histograms** (Datar–Gionis–Indyk–Motwani, SODA 2002) for sliding windows. Error composes additively/by union bound; space is $O(s \cdot T/g)$ for granularity $g$, or $O(s\log T)$ with a dyadic/segment-tree layout. For interval tuples, a tuple spanning $[t_s,t_e)$ updates all covering dyadic nodes (a *range update*), handled by lazy/segment-tree propagation.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Mergeable summaries (Agarwal et al. 2012) unify count/quantile/distinct under merge-closure; **KLL** gives optimal mergeable quantiles; HyperLogLog(++) is the practical distinct-count standard. Sliding-window: **Exponential Histograms** and **Smooth Histograms** (Braverman–Ostrovsky, FOCS 2007) extend a broad class of functions to windows with relative error. Dyadic-interval composition gives arbitrary-range answers from window/prefix sketches.

**Systems-SOTA:** Apache **DataSketches** (Yahoo/Apache, KLL/HLL/Theta/Frequent-items, all mergeable) is the de-facto library, used in Druid, Pinot, and Hive for time-range approximate analytics. **Druid** and **ClickHouse** keep per-time-chunk sketches (HLL, quantile, t-digest) and merge them across the queried time range; **t-digest** (Dunning) is widely deployed for mergeable quantiles though without worst-case guarantees. Postgres/Timescale `tdigest`/`hyperloglog` extensions follow the same per-bucket-merge pattern.

## 4. Upper Bound
For count/sum range aggregates over $T$ time buckets: $O(\log T)$ merges per query with a dyadic/segment-tree of additive sketches; space $O(T)$ exact prefix sums or $O((\log T)/\epsilon)$ for sketched. **Distinct count:** HyperLogLog answers any range as a union of $O(\log T)$ register-max merges, $O(2^{-k})$ registers giving standard error $\approx 1.04/\sqrt{m}$, space $O(m\log T)$. **Quantiles:** KLL per bucket, $O(\tfrac1\epsilon)$ space each, $O(\log T)$ merges per arbitrary range, total additive $\epsilon$ error — all in the streaming / merge model. Sliding window of size $W$: Exponential Histograms give $(1+\epsilon)$ count in $O(\tfrac1\epsilon \log^2 W)$ bits.

## 5. Lower Bound
Quantile sketches need $\Omega(\tfrac1\epsilon \log\log\tfrac1\delta)$ space (KLL is tight, matching the comparison-based lower bound). Distinct-count requires $\Omega(\epsilon^{-2} + \log n)$ bits (Indyk–Woodruff; Kane–Nelson–Woodruff). For **arbitrary-range** distinct count there is a multiplicative $\Omega(\log T)$ price over a single sketch (the dyadic factor) shown via communication-complexity / direct-sum arguments. Frequency-moment and $\ell_p$ lower bounds (AMS; Bar-Yossef et al.) bound linear-sketch size. These are information-theoretic / communication-complexity bounds in the streaming model.

## 6. The Gap
Why **partially-solved**: for *decomposable, additive* aggregates (count, sum, distinct, quantiles, heavy hitters) mergeable summaries plus dyadic decomposition essentially match the lower bounds — the per-query $O(\log T)$ factor is provably near-tight. The **remaining gap** is for (i) **non-decomposable / holistic** aggregates and correlated statistics over interval-valued tuples where a single tuple updates many ranges, (ii) **error that does not blow up under $O(\log T)$ merges** for relative-error quantiles, and (iii) optimal joint space across many simultaneously-maintained time granularities. These are open in constants and in handling interval (vs. point) data exactly.

## 7. Current Research (as of June 2026)
Active: (i) **DataSketches** ecosystem growth and standardization of mergeable sketch formats across engines; (ii) **differentially private** temporal range sketches (the dyadic-decomposition "binary mechanism" of Chan–Shi–Song / Dwork et al. for continual observation); (iii) **learned / workload-aware** sketch sizing per time bucket. *(frontier — verify)* Recent work targets *relative-error* quantiles over arbitrary time ranges with provably bounded merge-error and GPU/SIMD-accelerated sketch merging in vectorized engines, plus sketches robust to out-of-order and late-arriving temporal events. Groups: Cormode (Warwick/Meta), Yi (HKUST), Liberty/Karnin (sketching), Druid/Pinot/DataSketches communities.

## 8. Future Work
- Optimal mergeable summaries for **holistic** aggregates over interval-valued tuples.
- **Relative-error** arbitrary-range quantiles with provably bounded merge degradation.
- Joint-optimal multi-granularity sketch hierarchies (space across all resolutions).
- Private, out-of-order-robust temporal sketches with continual-observation guarantees.

## 9. Key References
- **[Foundational]** Agarwal, P., Cormode, G., Huang, Z., Phillips, J., Wei, Z., Yi, K. *Mergeable Summaries.* ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2500128)
- **[SOTA]** Karnin, Z., Lang, K., Liberty, E. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[Foundational]** Flajolet, P., Fusy, É., Gandouet, O., Meunier, F. *HyperLogLog.* AofA, 2007. — [HAL](https://hal.science/hal-00406166)
- **[Foundational]** Datar, M., Gionis, A., Indyk, P., Motwani, R. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Computing / SODA, 2002. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[Foundational]** Cormode, G., Muthukrishnan, S. *An Improved Data Stream Summary: the Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[SOTA]** Chan, T.-H. H., Shi, E., Song, D. *Private and Continual Release of Statistics.* ACM TISSEC, 2011. (dyadic binary mechanism) — [DOI](https://doi.org/10.1145/2043621.2043626)

## 10. Worked Example

**Dyadic decomposition for a range-`SUM`.** Suppose $T=8$ time buckets $[0,8)$, each holding a precomputed (mergeable) summary of that bucket's events. Build the dyadic / segment-tree layout:

```
level 0:  [0,8)
level 1:  [0,4)        [4,8)
level 2:  [0,2) [2,4)  [4,6) [6,8)
level 3:  0 1 2 3 4 5 6 7   (singletons)
```

Query range $[1,7)$. Greedy maximal-dyadic cover decomposes it into the *fewest* aligned nodes:

$$[1,7) = \underbrace{[1,2)}_{\text{leaf}} \;\cup\; \underbrace{[2,4)}_{\text{lvl 2}} \;\cup\; \underbrace{[4,6)}_{\text{lvl 2}} \;\cup\; \underbrace{[6,7)}_{\text{leaf}}.$$

The answer merges $4$ precomputed sketches. In general any range needs $\le 2\log_2 T = 6$ nodes here, so the per-query cost is $O(\log T)$ merges. With additive `COUNT/SUM` the merges are exact; with a distinct-count sketch (HyperLogLog) each merge is a register-wise max and the union error stays $\approx 1.04/\sqrt{m}$, paying the multiplicative $O(\log T)$ dyadic factor over a single sketch. An interval tuple spanning, say, $[2,6)$ is a *range update* covered exactly by nodes $[2,4)$ and $[4,6)$ — two lazy node updates instead of touching every leaf.

---
*Part of the [DBMS Research catalog](../../README.md).*
