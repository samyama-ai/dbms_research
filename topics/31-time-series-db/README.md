# Time-Series Databases

Time-series databases (TSDBs) specialize in append-heavy ingestion of timestamped numeric (and increasingly multivariate/text) streams, lossy and lossless compression of slowly varying signals, multi-resolution rollups and retention, and in-database analytics such as forecasting, anomaly detection, and pattern search. The field sits at the intersection of compression and information theory (Gorilla/delta-of-delta encodings, error-bounded approximation), streaming-systems engineering (LSM ingestion, out-of-order writes, cardinality explosion from labels), and statistical/learning theory (online forecasting, drift, alerting under uncertainty). The hard problems below span provable compression and query bounds, storage and ingest engineering, and the semantics of approximate, model-driven answers.

| Problem | Status | Scope |
|---|---|---|
| [Optimal error-bounded streaming compression](./error-bounded-compression-optimal.md) | open | Online piecewise approximation achieving the minimum segment count under an $L_\infty$ error bound in one pass. |
| [Lower bounds for XOR float compression](./gorilla-xor-lower-bounds.md) | empirically-open | Information-theoretic limits and optimality of Gorilla-style XOR encoding for real-valued float streams. |
| [Adaptive encoding selection per block](./adaptive-encoding-selection.md) | partially-solved | Choosing the best codec (delta, XOR, dictionary, RLE) per chunk online with provable competitive ratio. |
| [Compression-aware query execution](./compressed-domain-query-execution.md) | partially-solved | Evaluating filters, aggregates, and joins directly over compressed time-series without full decoding. |
| [Lossy compression with downstream-query guarantees](./lossy-compression-query-guarantees.md) | open | Lossy codecs that bound error on derived aggregates, forecasts, and anomaly scores, not just raw points. |
| [Optimal rollup hierarchy materialization](./rollup-materialization-optimal.md) | open | Selecting which downsampled resolutions to precompute to minimize cost under a query/retention workload. |
| [Semantically correct non-linear rollups](./nonlinear-rollup-semantics.md) | partially-solved | Composing rollups for non-decomposable aggregates (percentiles, distinct, rates) without re-reading raw data. |
| [Mergeable sketches for rollup percentiles](./mergeable-quantile-rollups.md) | partially-solved | Quantile/heavy-hitter sketches that roll up across time and series with tight, composable error bounds. |
| [Cardinality explosion from high-dimensional labels](./label-cardinality-explosion.md) | empirically-open | Indexing and storing series whose count explodes combinatorially with label/tag dimensions. |
| [Inverted-index design for tag matching](./tag-inverted-index-design.md) | partially-solved | Space/latency-optimal indexes for boolean tag predicates selecting series sets at query time. |
| [High-ingest LSM tuning for time-series](./lsm-ingest-tuning.md) | empirically-open | Compaction/flush policies that sustain peak append rates while bounding read and space amplification. |
| [Out-of-order and late-arrival ingestion](./out-of-order-ingestion.md) | partially-solved | Efficiently absorbing backfilled/late points into time-partitioned, append-optimized storage. |
| [Optimal time-partitioning (chunking) policy](./time-chunking-policy.md) | open | Choosing chunk boundaries/sizes to co-optimize ingest, compression, query pruning, and retention. |
| [Retention and tiering as an optimization problem](./retention-tiering-optimization.md) | open | Provably cost-optimal eviction/downsample/tier decisions under accuracy and budget constraints. |
| [In-database forecasting with error bounds](./in-db-forecasting-bounds.md) | open | Server-side forecasts carrying calibrated, query-composable uncertainty over arbitrary horizons. |
| [Online model maintenance under concept drift](./online-model-drift.md) | empirically-open | Keeping in-DB forecast/detection models current as series distributions shift, with bounded staleness. |
| [In-DB anomaly detection with false-alarm guarantees](./anomaly-detection-fdr-control.md) | open | Streaming detectors with provable false-discovery/alarm-rate control across millions of series. |
| [Multivariate correlation anomaly at scale](./multivariate-correlation-anomaly.md) | open | Detecting joint/structural anomalies across many correlated series under sublinear state. |
| [Approximate similarity search over series](./time-series-similarity-search.md) | partially-solved | Sublinear-time subsequence/whole-series matching under DTW/Lp with quality guarantees at TSDB scale. |
| [Indexing for distance-based subsequence queries](./subsequence-distance-indexing.md) | partially-solved | Index structures supporting fast $\varepsilon$-range and kNN subsequence search under elastic distances. |
| [Gap-filling and interpolation semantics](./gap-filling-semantics.md) | open | Principled, query-visible semantics for missing points, irregular sampling, and interpolation choices. |
| [Irregular and event-driven sampling storage](./irregular-sampling-storage.md) | partially-solved | Compression and query models for non-uniformly sampled and asynchronous-per-series data. |
| [Continuous-query rollup maintenance](./continuous-rollup-maintenance.md) | partially-solved | Incrementally maintaining materialized rollups/aggregates under high-rate, out-of-order ingest. |
| [Range-aggregate query lower bounds](./range-aggregate-lower-bounds.md) | partially-solved | Cell-probe/space-time bounds for time-range aggregates over compressed, multi-resolution stores. |
| [Workload-adaptive physical layout](./workload-adaptive-layout.md) | empirically-open | Online reorganization of chunk/column/tier layout to track shifting scan-vs-point query mixes. |
| [Time-weighted and rate aggregation correctness](./time-weighted-aggregation.md) | partially-solved | Exact time-weighted averages, integrals, and counter-rate computation over irregular, reset-prone series. |
| [Counter reset and monotonicity handling](./counter-reset-handling.md) | empirically-open | Robust rate/delta semantics for monotonic counters under resets, rollovers, and missing samples. |
| [Cross-series alignment and join semantics](./cross-series-alignment-joins.md) | open | Sound, efficient temporal alignment/join of series with differing timestamps and resolutions. |
| [Cost-based optimization for TSDB query plans](./tsdb-cost-based-optimization.md) | open | A cost model and optimizer spanning compression, rollups, indexes, and tiering decisions jointly. |
| [Privacy-preserving release of rollups](./privacy-preserving-rollups.md) | open | Differentially private or aggregated release of downsampled series without leaking fine-grained events. |

---
*Back to [Taxonomy](../../TAXONOMY.md).*
