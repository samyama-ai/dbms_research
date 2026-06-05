# Cardinality explosion from high-dimensional labels

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/label-cardinality-explosion` · **Status:** empirically-open

## 1. Problem Statement
In label/tag-based time-series models (Prometheus, InfluxDB, OpenTSDB), a **series** is uniquely identified by a metric name plus a set of key–value label pairs, e.g. `http_requests{method="GET",path="/u/123",pod="p-7f",region="us"}`. The number of distinct series is the size of the *realized* Cartesian product of label values. When one label has unbounded domain (user id, request id, full URL, container hash), cardinality **explodes combinatorially**, blowing up the index, per-series in-memory state (head chunks, append buffers), and query fan-out.

The problem: **store and index a set of series whose count grows multiplicatively with label dimensions and value domains, while keeping ingest memory, index size, and tag-query latency bounded.**

- **Decision variant:** given a label schema and value-domain bounds, will active series stay under a memory budget $M$?
- **Optimization variant:** minimize index + head-state bytes per active series subject to a query-latency SLO.
- **Counting variant:** accurately *estimate* live distinct series cardinality (and per-label contribution) cheaply, to detect explosions early. This is itself a distinct-count sketching problem.

It is **empirically-open**: there is no clean theory predicting the bound; production systems fight it with limits, sampling, and operational guardrails.

## 2. Mathematical Foundations
Let labels $L_1,\dots,L_d$ have realized value sets of sizes $c_1,\dots,c_d$. Worst-case series count is $\prod_i c_i$, but real data is **sparse**: only a co-occurrence subset $A\subseteq L_1\times\cdots\times L_d$ appears. The **AGM bound** (Atserias–Grohe–Marx) bounds the size of a join/product by the optimal fractional edge cover of the underlying hypergraph — the realized cardinality is governed by functional dependencies and correlations among labels, not the naive product. Where labels are independent and high-domain, the AGM/product bound is tight and explosion is real; where strong FDs exist (`pod ⟶ region`), realized cardinality collapses far below the product.

Live-cardinality estimation is a **distinct-count** problem: HyperLogLog gives $\hat n$ with relative error $\approx 1.04/\sqrt{m}$ using $m$ registers ($O(\log\log n)$ bits each). Per-label "which label drives the explosion" attribution maps to estimating distinct counts of projections — a sketch-union/intersection problem (Theta sketches).

The index is an **inverted index** (label, value) → posting list of series ids; its size is $\sum_i \sum_{v} |\text{postings}(L_i{=}v)| = d\cdot|A|$ in the worst case, so it grows *linearly in realized series count times label dimension*.

## 3. State of the Art (SOTA)
- **Systems:** Prometheus TSDB caps via `sample_limit`, `label_limit`, and relabeling drops; Grafana Mimir/Cortex enforce per-tenant `max_series` limits and ships a *cardinality analysis* API. VictoriaMetrics is engineered specifically for high cardinality (per-day inverted index, streaming aggregation to pre-collapse labels). InfluxDB historically suffered the TSM "cardinality wall"; IOx (Arrow/Parquet, columnar) re-architected to avoid per-series in-memory state. Thanos/M3DB add downsampling + label aggregation. eBPF/OTel pipelines add tail-based sampling and `metric_relabel_configs` to drop high-cardinality labels at the edge.
- **Estimation:** HyperLogLog/Theta sketches used to report live cardinality and top label contributors.

## 4. Upper Bound
There is no sublinear exact bound: the index and head state are inherently $\Theta(|A|)$ in realized active series, $\Theta(d\cdot|A|)$ for the inverted index. Best-known *mitigations* are constant-factor: columnar storage removes per-series object overhead; streaming pre-aggregation reduces $|A|$ by projecting away offending labels *before* indexing. For *estimation*, HyperLogLog answers live cardinality in $O(\log\log n)$ space per stream with $\sim$2% error.

## 5. Lower Bound
Any structure answering arbitrary boolean tag queries over $|A|$ distinct series must store $\Omega(|A|)$ bits (each series is individually addressable) — an information-theoretic floor; you cannot index $N$ distinguishable series in $o(N)$ space. **Exact** distinct-count of live series in one pulse requires $\Omega(n)$ bits (streaming distinct-elements lower bound), forcing approximation. Worst-case realized cardinality meeting the AGM product bound is achievable by adversarial independent labels, so no schema-agnostic sublinear guarantee exists. This is why the problem is empirically-open rather than closed: the lower bounds say "you must pay for what you keep," and the open question is purely *what to keep / drop*.

## 6. The Gap
The theory cleanly says exact indexing is $\Theta(|A|)$ and explosion is unavoidable for independent high-domain labels. The **gap is not a bound gap but a modeling/operational gap**: we lack (a) predictive models that, from a label schema + sample, forecast realized cardinality and flag the culprit label *before* ingest, and (b) principled, automatic policies (which labels to drop, bucket, or hash) that trade query fidelity for bounded cost with a provable error on downstream queries. Closing it means turning today's manual relabeling heuristics into a cost-model-driven, guaranteed scheme.

## 7. Current Research (as of June 2026)
Active directions: **adaptive cardinality limiting** in OTel collectors and Grafana (automatic detection + aggregation of runaway labels) *(frontier — verify)*; VictoriaMetrics streaming aggregation and per-day index design as the systems reference for surviving tens of millions of active series; **exemplars + sampling** to keep high-cardinality detail out of the metric index (move it to traces). Research on learned label-correlation models for cardinality forecasting and on sketch-based per-label attribution dashboards is ongoing. Groups/vendors: VictoriaMetrics, Grafana Labs (Mimir), InfluxData (IOx), the OpenTelemetry metrics SIG.

## 8. Future Work
- Cost models forecasting realized cardinality from schema + FD structure (AGM-grounded).
- Automatic, query-error-bounded label dropping/bucketing/hashing.
- Per-series state amortization so head memory is sublinear in active series.
- Standard live-cardinality and per-label-contribution sketches across systems.
- Separating "detail" (high-cardinality, trace-like) from "metrics" (low-cardinality, indexed) at the data-model level.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* SIAM Journal on Computing, 2013 (AGM bound).
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007.
- **[SOTA]** Rabenstein, Volz. *Prometheus: A Next-Generation Monitoring System.* SoundCloud / SREcon, 2015 (label data model).
- **[SOTA]** VictoriaMetrics. *Engineering Articles on High-Cardinality Time Series Storage and Streaming Aggregation.* 2019–2024 (systems design).
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
