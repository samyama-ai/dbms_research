# Column Stores & OLAP

Column-oriented storage and analytical query processing turn the read-heavy, scan-and-aggregate
workloads of decision support into a problem of layout, encoding, and vectorized execution rather
than tuple-at-a-time access. This topic spans the theory (optimal compression and materialization
bounds, cube complexity, expressiveness of encoded operators) and the systems (vectorized vs.
compiled engines, late materialization, SIMD/GPU acceleration, cloud-native columnar formats) that
make modern OLAP and data-warehouse engines fast. The problems below are the hard, open, or
empirically-unsettled questions that PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT communities continue to study.

| Problem | Status | Scope |
|---|---|---|
| [Optimal Lightweight Encoding Selection](./optimal-encoding-selection.md) | open | Choosing a per-column (or per-block) encoding cascade that minimizes a combined storage-plus-decode-cost objective over a workload. |
| [Direct Computation on Compressed Columns](./compressed-operator-completeness.md) | partially-solved | Characterizing which relational/aggregate operators can run on encoded data without full decompression and at what asymptotic cost. |
| [Late vs. Early Materialization Optimization](./materialization-strategy-optimization.md) | open | Deciding per-operator materialization timing in a plan to minimize total tuple-reconstruction and intermediate-data cost. |
| [Tuple Reconstruction Cost Lower Bounds](./tuple-reconstruction-lower-bounds.md) | open | Establishing complexity bounds on stitching late-materialized columns back into rows under different position-mapping models. |
| [Compression-Aware Query Optimization](./compression-aware-optimization.md) | open | Cost models and plan enumeration that treat encoding as a first-class physical property affecting operator choice. |
| [Optimal Data Cube Materialization](./cube-view-selection.md) | partially-solved | Selecting a subset of cuboids to precompute under space and maintenance budgets to minimize query cost. |
| [Cube Computation Complexity](./cube-computation-complexity.md) | partially-solved | Tight bounds on time/space to compute full and iceberg cubes over high-dimensional, sparse data. |
| [Incremental Cube Maintenance](./incremental-cube-maintenance.md) | open | Efficiently updating materialized cuboids and rollups under streaming inserts, updates, and deletes. |
| [Vectorized vs. Compiled Execution Frontier](./vectorized-vs-compiled.md) | empirically-open | Determining when (and how to hybridize) interpreted-vectorized and JIT-compiled execution for analytical pipelines. |
| [Optimal SIMD Operator Kernels](./simd-operator-kernels.md) | empirically-open | Designing provably data-parallel kernels for selection, hashing, and aggregation that saturate wide-SIMD/AVX-512 units. |
| [Adaptive Column Layout Reorganization](./adaptive-layout-reorganization.md) | open | Online reorganization of columnar layout, sort order, and partitioning in response to drifting query workloads. |
| [Optimal Sort Order for Columnar Storage](./columnar-sort-order.md) | open | Choosing a global tuple/block sort order that jointly maximizes run-length compression and predicate pushdown. |
| [Zone Maps and Min/Max Skipping Bounds](./zone-map-skipping-bounds.md) | partially-solved | Theory of block-level skipping effectiveness and how to lay out data to maximize provable data-skipping. |
| [Learned Data Skipping Indexes](./learned-data-skipping.md) | empirically-open | Learned, multi-dimensional block-skipping structures with bounded false-positive scan amplification. |
| [Hybrid Row/Column (HTAP) Layout](./htap-hybrid-layout.md) | open | Storage and execution design that serves OLTP and OLAP from one layout without crippling either. |
| [String/Dictionary Encoding at Scale](./dictionary-encoding-scale.md) | partially-solved | Global vs. local dictionary management, order-preserving codes, and dictionary maintenance under updates. |
| [Selection Pushdown into Encoded Scans](./encoded-predicate-pushdown.md) | partially-solved | Evaluating complex predicates directly over bit-packed/RLE/FOR-encoded data with provable speedups. |
| [Columnar Join Algorithm Optimality](./columnar-join-optimality.md) | open | Join algorithms (and their materialization) tuned for columnar inputs, late binding, and vectorized probes. |
| [Group-By Aggregation on Columns](./vectorized-groupby-aggregation.md) | empirically-open | Cache- and SIMD-efficient hash/sort aggregation with skew robustness over columnar inputs. |
| [GPU-Accelerated OLAP Operators](./gpu-olap-operators.md) | empirically-open | Operator and data-transfer designs that make GPUs win for columnar scan/join/aggregation despite PCIe limits. |
| [Cloud-Native Open Columnar Formats](./open-columnar-format-design.md) | open | Next-generation Parquet/ORC/Arrow-class formats co-designed for object storage, wide schemas, and predicate pushdown. |
| [Bitmap Index Compression Tradeoffs](./bitmap-index-compression.md) | partially-solved | Compressed bitmap encodings that are both space-optimal and fast for AND/OR/COUNT under varied cardinality. |
| [Approximate Cube / Rollup Synopses](./approximate-cube-synopses.md) | partially-solved | Sublinear-space synopses answering aggregate cube/rollup queries with provable error bounds. |
| [Result-Cache and Semantic Reuse for OLAP](./olap-result-reuse.md) | open | Detecting and exploiting overlap among analytical queries via subexpression and cached-result reuse. |
| [Cardinality Estimation for Columnar Plans](./columnar-cardinality-estimation.md) | open | Selectivity/cardinality estimation that accounts for encoding, sort order, and zone-map correlations. |
| [Updates and Deletes in Column Stores](./columnar-update-handling.md) | partially-solved | Delta/positional-delta architectures that absorb writes while preserving scan speed and compression. |
| [Wide-Table and Sparse-Column Storage](./wide-sparse-column-storage.md) | open | Storage and access methods for thousands-of-columns, highly sparse analytical tables. |
| [Window-Function Execution on Columns](./columnar-window-functions.md) | open | Efficient partitioning, framing, and incremental evaluation of SQL window functions over columnar data. |
| [Spilling and Memory-Bounded OLAP](./memory-bounded-olap.md) | open | Robust, near-optimal spill strategies for hash joins/aggregations when columnar working sets exceed RAM. |
| [Workload-Aware Storage Tiering for OLAP](./olap-storage-tiering.md) | open | Placing columns/cuboids/encodings across hot-cold tiers to minimize cost under latency SLOs. |

---
[← Back to taxonomy](../../TAXONOMY.md)
