# Temporal Aggregation Complexity

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-aggregation-complexity` · **Status:** partially-solved

## 1. Problem Statement
Given a temporal relation where each tuple has a value and a time period, compute aggregates (`COUNT`, `SUM`, `MIN`, `MAX`, `AVG`, etc.) as functions of time. Three flavors:
- **Instantaneous (constant-interval) aggregation:** produce, for every maximal time interval over which the aggregate is constant, the aggregate value — i.e. an aggregate that changes only at tuple endpoints.
- **Moving-window aggregation:** at each point/granule, aggregate over a sliding window of width $w$ (e.g. "count of active sessions in the last hour").
- **Span / cumulative aggregation:** aggregate over an entire query period or a user-specified grouping of time spans.

We want tight **upper and lower bounds** for each, in batch, streaming, and incremental-maintenance settings, distinguishing reporting (emit the whole time-varying aggregate) from point queries (aggregate at one instant) and from counting.

## 2. Mathematical Foundations
Instantaneous aggregation is fundamentally an **endpoint-sweep**: the aggregate can change only at the $2n$ interval endpoints, so the output has at most $2n-1$ constant segments. A balanced-tree / sweepline computes all of them in $O(n \log n)$. For decomposable aggregates the per-segment update is $O(1)$ (a delta at each endpoint), but **holistic** aggregates (`MEDIAN`, `MIN`/`MAX` under deletion) require a priority structure, costing $O(\log n)$ per event.

Formally, with start-events $+v$ and end-events $-v$, $\textsf{SUM}(t) = \sum_{e \le t} \Delta_e$ is a prefix sum over sorted events; `MIN`/`MAX` need a sliding-window deque or interval/segment tree. The **Aggregation Tree (SB-tree)** and **Balanced Tree (Kline–Snodgrass)** materialize this. Window aggregation connects to **sliding-window streaming** lower bounds (Datar–Gionis–Indyk–Motwani exponential histograms) and to *monoid* structure: aggregates form a monoid, and window aggregation cost depends on whether the monoid is invertible (groups, $O(1)$ amortized) or only a semigroup (FIFO-window, $\Theta(1)$ amortized via two-stack / DABA, but $\Omega(\log w)$ for some out-of-order variants).

## 3. State of the Art (SOTA)
**Theory-SOTA:** Instantaneous aggregation in $O(n \log n)$ via balanced sweep is the classic optimum (Kline & Snodgrass, ICDE 1995; Moon, Lopez, Immanuel — *aggregation over long-duration intervals*, TKDE 2003, with the **SB-tree** giving $O(\log n)$ amortized updates and queries). Streaming window aggregation: **two-stacks**, **FlatFAT** (Tangwongsan et al., VLDB 2015), and **DABA / DABA Lite** achieve $O(1)$ worst-case per element for general associative aggregates.

**Systems-SOTA:** Stream processors (Flink, Spark Structured Streaming, Trill) implement sliding/tumbling windows with incremental, often invertible-aggregate paths; columnar/temporal engines push instantaneous aggregation into vectorized endpoint sweeps. SAP HANA's Timeline Index supports efficient temporal aggregation over versions.

## 4. Upper Bound
- **Instantaneous:** $O(n \log n)$ time, $O(n)$ space (sort endpoints + sweep); $O(n)$ if endpoints pre-sorted; SB-tree gives $O(\log n)$ amortized per insert and per range-aggregate query, $O(n)$ space — model: comparison/RAM.
- **Moving-window (FIFO, associative monoid):** $O(1)$ amortized/worst-case per element, $O(w)$ space (DABA, two-stacks, FlatFAT) — streaming model.
- **Span aggregation:** $O(\log n)$ per span query with a precomputed aggregate tree; $O(n)$ total for a partition of time.

## 5. Lower Bound
- Instantaneous aggregation is $\Omega(n \log n)$ in the comparison model (endpoint sorting reduction; the $2n$ change points must be ordered).
- **Sliding-window streaming:** for non-invertible aggregates and approximate counts, Datar–Gionis–Indyk–Motwani prove $\Omega(\frac{1}{\epsilon}\log^2 N)$ space lower bounds for $\epsilon$-approximate window sums/counts; exact `MIN`/`MAX` over arbitrary windows needs $\Omega(w)$ space.
- General associative window aggregation has an $\Omega(1)$ trivial bound matched by DABA, but **out-of-order** / multi-query window settings inherit higher bounds; some variants connect to **(min,+)** / APSP-style hardness for repeated range-min over updates *(frontier — verify)*.

## 6. The Gap
**Closed** for batch instantaneous aggregation ($\Theta(n \log n)$) and for in-order FIFO associative window aggregation ($\Theta(1)$ per element, matched by DABA). **Open / partially solved:** (i) out-of-order and *multi-window / multi-resolution* aggregation with tight per-update bounds; (ii) holistic aggregates (median, distinct-count) over moving windows with optimal space–accuracy tradeoffs; (iii) bitemporal aggregation (aggregating over both time axes) where the 2D structure may force super-linearithmic cost; (iv) parallel/distributed temporal aggregation lower bounds. These keep the topic partially-solved.

## 7. Current Research (as of June 2026)
- Sliding-window aggregation theory (Tangwongsan, Hirzel, Schneider): general-monoid, out-of-order, and shared multi-window algorithms; *(frontier — verify)* recent work on coarse-grained / multi-resolution window sharing with worst-case guarantees.
- Approximate holistic temporal aggregation (distinct counting, quantiles over windows) building on sketches (HyperLogLog, KLL, DDSketch) with temporal decay.
- Bitemporal and interval-grouped aggregation in columnar/vectorized engines; GPU temporal aggregation.
- Aggregation pushdown in versioned lakehouse formats over `validfrom/validto` ranges.

## 8. Future Work
- Tight bounds for **out-of-order** and multi-window streaming aggregation.
- Optimal space–accuracy tradeoffs for holistic aggregates over moving windows.
- Lower bounds for **bitemporal** aggregation; is super-linearithmic unavoidable?
- Distributed/parallel temporal aggregation with communication-optimal guarantees.

## 9. Key References
- **[Foundational]** Kline, N., Snodgrass, R. T. *Computing Temporal Aggregates.* ICDE, 1995.
- **[Foundational]** Moon, B., Lopez, I. F. V., Immanuel, V. *Efficient Algorithms for Large-Scale Temporal Aggregation.* IEEE TKDE, 2003. (SB-tree)
- **[SOTA]** Tangwongsan, K., Hirzel, M., Schneider, S., Wu, K.-L. *General Incremental Sliding-Window Aggregation.* VLDB, 2015. (FlatFAT)
- **[SOTA]** Tangwongsan, K., Hirzel, M., Schneider, S. *Low-Latency Sliding-Window Aggregation in Worst-Case Constant Time.* DEBS, 2017. (DABA)
- **[Foundational]** Datar, M., Gionis, A., Indyk, P., Motwani, R. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Computing, 2002.
- **[Survey]** Böhlen, M., Gamper, J., Jensen, C. S. *Multi-Dimensional Aggregation for Temporal Data.* EDBT, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
