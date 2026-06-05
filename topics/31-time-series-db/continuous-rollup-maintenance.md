# Continuous-query rollup maintenance

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/continuous-rollup-maintenance` · **Status:** partially-solved

## 1. Problem Statement

TSDBs precompute **rollups** — materialized aggregates over time buckets (1m/1h/1d) and dimensions — to serve dashboards cheaply. Under **high-rate** and **out-of-order / late-arriving** ingest, the problem is to **incrementally maintain** these materialized aggregates correctly and efficiently: when a point arrives (possibly hours late, possibly a correction/retraction), update all affected rollup cells with minimal recomputation and bounded staleness.

Variants:
- **Maintenance (optimization):** minimize work per ingested/retracted point to keep rollups consistent.
- **Decision/consistency:** given a watermark/lateness bound, is a rollup cell *final* (sealed) or still mutable?
- **Counting/aggregate class:** which aggregates admit cheap incremental maintenance — distributive (sum/count/min/max), algebraic (avg, var), or holistic (median, distinct, percentiles)?
- **Out-of-order:** maintain correctness when events arrive non-monotonically in event-time.

Marked **partially-solved**: distributive/algebraic rollups over append-only, near-ordered streams are well-handled; holistic aggregates, retractions, and arbitrary lateness remain hard.

## 2. Mathematical Foundations

A rollup is a view $V = \gamma_{\text{bucket},\text{dims}}(R)$. Incremental view maintenance (IVM) seeks a delta rule $V' = V \oplus \delta$ for an update $\Delta R$. Aggregates classify (Gray et al., **data cube**, 1997) as:
- **Distributive:** $f(A\cup B)=g(f(A),f(B))$ — sum, count, min, max. $O(1)$ incremental update.
- **Algebraic:** computable from a bounded-size tuple (avg $=$ sum/count; variance via $\sum x, \sum x^2$). $O(1)$ state.
- **Holistic:** no bounded summary suffices in general — exact median/quantile/COUNT DISTINCT need $\Omega(n)$ in the worst case; mitigated by **sketches** (Greenwald–Khanna $\epsilon$-approx quantiles in $O(\frac{1}{\epsilon}\log \epsilon n)$ space; HyperLogLog for distinct; t-digest; KLL).

Out-of-order ingest formalizes via **event-time vs. processing-time** and **watermarks** (Dataflow model, Akidau et al., VLDB 2015): a watermark $W(t)$ asserts no event with event-time $\le t$ will arrive later; cells below $W$ may be **sealed**. Retractions need rollups to form a **group** (invertible $\oplus$) or be recomputable. Out-of-order min/max are **not** invertible — a fundamental asymmetry: sum supports retraction, max does not (needs a heap/recompute). Sliding-window maintenance ties to **FlatFAT / DABA / SlickDeque** algorithms achieving $O(1)$ amortized per element for associative operators.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **TimescaleDB continuous aggregates** (real-time + materialized, with refresh policies and out-of-order handling); **Druid** ingestion-time rollup + segment compaction; **ClickHouse** `AggregatingMergeTree` / materialized views with partial aggregate states; **InfluxDB** tasks/downsampling; **M3 / Mimir / VictoriaMetrics** recording rules; **Materialize / Feldera (DBSP)** for general streaming IVM.
- **Theory-SOTA:** **DBSP** (Budiu et al., 2022/2023) — incremental computation of arbitrary relational+aggregate queries with a change-propagation calculus; **Greenwald–Khanna**, **KLL** sketches for streaming holistic aggregates; sliding-window aggregation (Tangwongsan et al. **DABA**, 2017).
- **Out-of-order:** **Google Dataflow / Beam** watermark+trigger model; Flink's event-time + allowed-lateness.

## 4. Upper Bound

- **Distributive/algebraic rollups:** $O(1)$ amortized maintenance per in-order event; $O(\\#\text{affected cells})$ for an out-of-order event hitting already-built buckets.
- **Sliding-window associative aggregates:** $O(1)$ amortized per insert/evict (DABA/FlatFAT), worst-case $O(1)$ (DABA Lite / SlickDeque) in the RAM model.
- **Holistic (approximate):** $\epsilon$-quantiles in $O(\frac{1}{\epsilon}\log(\epsilon n))$ space (Greenwald–Khanna); distinct in $O(\epsilon^{-2})$ (HLL-class); mergeable across buckets.
- **General IVM (DBSP):** maintenance cost proportional to the size of the change, not the database.

## 5. Lower Bound

- **Holistic exactness:** exact median / COUNT DISTINCT over a stream requires $\Omega(n)$ space (and exact distinct elements has the classic $\Omega(n)$ communication lower bound); hence sketches are *necessary*, not just convenient.
- **Non-invertible aggregates:** maintaining a sliding-window **max** under arbitrary eviction has an $\Omega(\log w)$ comparison lower bound per op in comparison models for some variants; out-of-order max with retraction can force recomputation — no $O(1)$ retraction exists.
- **Out-of-order impossibility:** with **unbounded** lateness, no finite-state rollup can both seal cells and remain correct — a watermark (bounded lateness assumption) is *required*; this is an FLP-flavored impossibility (can't decide finality without a timing assumption).

## 6. The Gap

Closed for distributive/algebraic, append-only, bounded-lateness ingest. Open at the intersection of **(holistic aggregate) × (out-of-order/retraction) × (high cardinality dimensions)**: there is no system giving exact holistic rollups under retraction with sub-linear work, and the trade-off curve (accuracy vs. maintenance cost vs. staleness) under adversarial lateness lacks tight bounds. DBSP closes much of the *generality* gap in theory but practical cost for holistic/sketch aggregates and unbounded lateness is unresolved.

## 7. Current Research (as of June 2026)

- **DBSP / Feldera** maturing into production incremental SQL, including windowed/streaming aggregates *(frontier — verify)*.
- Mergeable-sketch rollups as first-class materialized state (ClickHouse AggregateFunction states, Druid sketch columns, Apache DataSketches integration).
- Out-of-order-tolerant continuous aggregates with bounded recomputation (TimescaleDB, Druid compaction; Flink/Beam trigger refinements).

## 8. Future Work

- Tight accuracy–cost–staleness bounds for holistic rollups under out-of-order ingest.
- Retraction-friendly maintenance for non-invertible aggregates without full recompute.
- Adaptive watermarking with provable finality/staleness guarantees.

## 9. Key References

- **[Foundational]** J. Gray et al. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* Data Mining and Knowledge Discovery, 1997. — [DOI](https://doi.org/10.1023/A:1009726021843)
- **[Foundational]** T. Akidau et al. *The Dataflow Model.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824076)
- **[SOTA]** M. Budiu et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3587136.3587137)
- **[SOTA]** K. Tangwongsan, M. Hirzel, S. Schneider. *Low-Latency Sliding-Window Aggregation in Worst-Case Constant Time (DABA).* DEBS, 2017. — [DOI](https://doi.org/10.1145/3093742.3093925)
- **[Foundational]** M. Greenwald, S. Khanna. *Space-Efficient Online Computation of Quantile Summaries.* SIGMOD, 2001. — [DOI](https://doi.org/10.1145/375663.375670)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)

## 10. Worked Example

A 1-minute SUM and MAX rollup over bucket $b=[12{:}00,12{:}01)$ receives in-order points $4, 9, 2$:

$$\text{SUM}=15,\qquad \text{MAX}=9.$$

Now a **late** point with value $7$ and event-time inside $b$ arrives at processing-time 12:05.

- **SUM is distributive and invertible (a group under $+$):** apply the delta rule $V'=V\oplus\delta$ with $\delta=+7$, giving $\text{SUM}=22$ in $O(1)$. A *retraction* of the earlier $9$ is just $\delta=-9$, also $O(1)$.
- **MAX is distributive but not invertible:** the new $7<9$ leaves $\text{MAX}=9$, fine. But retracting the $9$ leaves $\{4,2,7\}$ and there is no $O(1)$ rule to find the new max $7$ — you must keep the full multiset (a heap) or recompute, the fundamental asymmetry.

Watermark/sealing: if the lateness bound is 3 min, then by processing-time 12:04 the watermark $W$ passes 12:01 and bucket $b$ is **sealed** — the 12:05 point would be *dropped* as beyond allowed lateness. With **unbounded** lateness no finite-state rollup can both seal and stay correct (the FLP-flavored impossibility), so a bounded-lateness assumption is required to ever declare a cell final.

---
*Part of the [DBMS Research catalog](../../README.md).*
