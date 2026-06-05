# Spatial & Spatiotemporal Databases

Spatial and spatiotemporal databases index and query data with geometric extent and movement: points, lines, polygons, and trajectories over space and time. The hard problems span theory — optimality of multidimensional access methods, lower bounds for range and nearest-neighbor search, the analysis of space-filling-curve locality — and systems — building R-tree variants that balance read/update/space, scaling spatial joins and kNN to billions of objects, supporting moving objects and trajectories, and serving modern GIS, mapping, and location workloads on parallel/GPU/distributed hardware.

This catalog collects 30 research-grade open problems at the intersection of theory (bounds, expressiveness, instance optimality) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [Worst-case-optimal dynamic R-tree](./rtree-worst-case-optimal.md) | open | Whether a dynamically updatable R-tree variant can guarantee polylogarithmic worst-case range query time with linear space. |
| [Optimal R-tree bulk-loading objective](./rtree-bulk-loading-optimal.md) | partially-solved | Finding a packing that provably minimizes expected node accesses over a query distribution, not just a heuristic cost proxy. |
| [Lower bounds for orthogonal range reporting](./range-reporting-lower-bound.md) | open | Tightening the query-time/space tradeoff for d-dimensional range reporting in the pointer-machine and cell-probe models. |
| [Space-filling-curve locality lower bounds](./sfc-locality-lower-bound.md) | partially-solved | Proving optimal worst-case and average clustering bounds for Hilbert and other curves under range queries. |
| [Approximate nearest neighbor in high dimensions](./ann-high-dimensional.md) | partially-solved | Closing the gap between LSH/graph-index ANN time-accuracy tradeoffs and proven cell-probe lower bounds. |
| [Instance-optimal exact kNN](./knn-instance-optimal.md) | open | An exact kNN access method provably competitive with the best index tuned to the actual data and query distribution. |
| [Spatial join output-sensitive complexity](./spatial-join-output-sensitive.md) | partially-solved | Algorithms for rectangle/polygon join whose cost provably scales with input plus true intersection output size. |
| [Scalable distributed spatial join](./distributed-spatial-join.md) | empirically-open | Partitioning and load-balancing spatial joins on skewed data without replication blowup or stragglers. |
| [Learned spatial indexes with guarantees](./learned-spatial-index.md) | empirically-open | Learned multidimensional models that give worst-case query/update bounds competitive with R-trees on real GIS data. |
| [Updatable spatial index under high churn](./spatial-index-high-churn.md) | empirically-open | Maintaining query quality and bounded reorganization cost under continuous high-rate inserts and deletes. |
| [Concurrent R-tree with optimal contention](./rtree-concurrency.md) | partially-solved | A concurrent/lock-free R-tree whose synchronization cost scales with actual conflict rather than tree size. |
| [Indexing moving objects with predictive queries](./moving-object-index.md) | partially-solved | Index structures answering present and future-time queries on continuously moving points with bounded update cost. |
| [Trajectory similarity join at scale](./trajectory-similarity-join.md) | empirically-open | Scalable joins under Frechet/DTW/EDR similarity without quadratic blowup or loss of metric guarantees. |
| [Trajectory compression with query guarantees](./trajectory-compression.md) | partially-solved | Lossy trajectory simplification that bounds error for downstream range, kNN, and similarity queries. |
| [Map matching at scale with guarantees](./map-matching-scalable.md) | empirically-open | Online and batch map matching with provable accuracy under GPS noise and high-throughput trajectory streams. |
| [Continuous kNN over moving queries](./continuous-knn-moving.md) | partially-solved | Maintaining kNN answers for moving query points and moving objects with minimal recomputation. |
| [Reverse kNN with dynamic updates](./reverse-knn-dynamic.md) | partially-solved | Efficient exact RkNN under high-dimensional and continuously updating spatial datasets. |
| [Spatial query optimization cost models](./spatial-cost-model.md) | empirically-open | Accurate, robust selectivity and cost estimation for spatial range/join/kNN operators across skewed distributions. |
| [Spatial selectivity estimation under skew](./spatial-selectivity-estimation.md) | open | Provable-error multidimensional selectivity estimators for arbitrary polygon and trajectory predicates. |
| [GPU-accelerated spatial indexing](./gpu-spatial-index.md) | empirically-open | Index layouts and traversal that exploit GPU parallelism for range/kNN/join without divergence penalties. |
| [In-database raster-vector unification](./raster-vector-unified.md) | open | A query model and physical design unifying raster and vector spatial data with optimizable algebra. |
| [Spatial joins on compressed/encoded data](./spatial-join-on-compressed.md) | empirically-open | Evaluating spatial predicates directly over compressed geometries without full decompression. |
| [Spatiotemporal index for trajectory archives](./spatiotemporal-archive-index.md) | empirically-open | Read/write/space-optimal indexing of massive historical trajectory archives for mixed analytical queries. |
| [Approximate spatial query with error bounds](./approximate-spatial-aqp.md) | partially-solved | Sampling/sketch methods for spatial aggregates and joins with provable confidence-interval guarantees. |
| [Privacy-preserving spatial queries](./private-spatial-query.md) | partially-solved | kNN/range queries with differential-privacy or oblivious guarantees and acceptable utility/overhead. |
| [Spatial data partitioning for skew](./spatial-partitioning-skew.md) | empirically-open | Partitioning schemes minimizing both load imbalance and boundary-object replication on heavily skewed data. |
| [Density-aware spatial clustering at scale](./density-clustering-scalable.md) | empirically-open | Scalable, index-supported DBSCAN-style clustering with output equivalent to the in-memory exact algorithm. |
| [Polygon containment and overlay complexity](./polygon-overlay-complexity.md) | partially-solved | Robust, output-sensitive algorithms for polygon overlay/containment under floating-point and degeneracy issues. |
| [Multi-way spatial join optimization](./multiway-spatial-join.md) | open | Optimal evaluation order and intermediate-result control for joins over three or more spatial relations. |
| [Spatial data lakes and serverless query](./spatial-data-lake.md) | empirically-open | Indexing and query pushdown for spatial data on object storage with serverless, cold-start-tolerant execution. |

[Back to taxonomy](../../TAXONOMY.md)
