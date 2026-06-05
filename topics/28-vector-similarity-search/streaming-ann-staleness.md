# Streaming ANN with bounded staleness

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/streaming-ann-staleness` · **Status:** empirically-open

## 1. Problem Statement

Vectors arrive as an unbounded stream of insertions, deletions, and updates. We must continuously serve approximate $k$-nearest-neighbor (ANN) queries against the *current* dataset while bounding how stale the answer may be. Concretely, fix a similarity metric $d$ (e.g., inner product, Euclidean, cosine) over $\mathbb{R}^D$. At query time $t$ the answer should reflect all points whose ingestion timestamp is $\le t - \tau$ for a staleness bound $\tau$, while preserving a target recall $R$ at $k$.

- **Optimization variant.** Minimize the index maintenance cost (CPU, write amplification, memory) subject to a staleness SLA $\tau$ and recall floor $R@k$.
- **Decision variant.** Given throughput $\lambda$ (vectors/s), query rate $q$, and bounds $(\tau, R)$, decide whether a single-node index can sustain them.
- **Tradeoff characterization.** Quantify the achievable Pareto frontier of (recall, staleness, query latency, ingest throughput).

The core tension: graph-based and quantization indexes amortize build cost over many queries, but high-velocity updates erode graph quality (orphaned nodes, stale neighbor lists) and centroid drift, forcing rebuilds that spike staleness.

## 2. Mathematical Foundations

Let $S_t \subseteq \mathbb{R}^D$ be the live set at time $t$. An index $\mathcal{I}$ answers $\mathrm{ANN}_k(q)$ returning $\hat{N}$ with recall $R = |\hat{N}\cap N_k(q)|/k$ where $N_k(q)$ is the true top-$k$. Define **staleness** $\sigma(t)=\max\{\,t - t_v : v \in S_t \text{ not yet reflected}\}$.

Graph indexes (HNSW, NSG, Vamana) rely on navigability: a greedy walk converges in $O(\log |S|)$ hops when the graph approximates a *monotonic relative-neighborhood graph*. Insertions/deletions perturb the small-world property; deletion of high-degree hubs is the adversarial case. Under the **doubling-dimension** model with intrinsic dimension $\dim_2$, query cost scales as $2^{O(\dim_2)}\log n$, and incremental edge repair must preserve this constant.

Quantization (IVF-PQ, OPQ, RaBitQ) partitions space into Voronoi cells around centroids $\{c_i\}$; drift of the empirical distribution $p_t$ from $p_0$ degrades cell balance, measurable via the KL divergence $D_{\mathrm{KL}}(p_t\|p_0)$ and the resulting quantization distortion $\mathbb{E}\|x-Q(x)\|^2$. Bounded staleness reduces to a **sliding-window / freshness** problem reminiscent of CQ semantics and the streaming model of Henzinger–Raghavan–Rajagopalan.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *FreshDiskANN* (Singh et al., Microsoft, 2021) maintains a long-term Vamana index plus a temporary in-memory delta and a background merge ("StreamingMerge"), bounding staleness to the merge interval. *SPFresh* (SOSP 2023) does in-place, lightweight LIRE rebalancing of SPANN posting lists, achieving low-staleness updates without global rebuild. Production engines: Milvus, Weaviate, Qdrant, Vespa, and *DiskANN*-derived services use tombstone-based deletes plus periodic compaction.
- **Theory-SOTA.** Fully-dynamic ANN with polylog update/query in the cell-probe and LSH models (Andoni–Indyk–Razenshteyn line); dynamic LSH supports updates in $O(n^\rho)$ amortized with $\rho<1$.

## 4. Upper Bound

LSH gives fully-dynamic $c$-approximate NN with query time $O(D n^{\rho})$ and update time $O(D n^{\rho})$, $\rho = 1/c^2$ for Euclidean (Andoni–Indyk 2006; Andoni–Razenshteyn 2015 optimal $\rho=1/(2c^2-1)$ for data-dependent), with staleness $\tau \to 0$ since updates apply in place. Space $O(n^{1+\rho})$. Graph indexes give empirically far better constants but lack a proven dynamic recall guarantee; FreshDiskANN bounds staleness by the merge period $\Delta$ with amortized insert cost $O(\text{degree}\cdot\log n)$.

## 5. Lower Bound

For exact NN, cell-probe lower bounds (Pătraşcu–Thorup; Andoni–Indyk–Pătraşcu) force either $n^{\Omega(1)}$ query time or near-quadratic space in high dimension — the *curse of dimensionality* persists under updates. For dynamic problems, the **dynamic** cell-probe bounds (Larsen 2012) give $\Omega(\log n/\log\log n)$ per operation for problems with the requisite chronogram structure. A genuine staleness–recall **impossibility** at the systems level (you cannot simultaneously have $\tau=0$, full recall, and sublinear maintenance under adversarial high-degree deletions) is folklore but lacks a clean published separation.

## 6. The Gap

The dynamic LSH upper bounds are tight up to the approximation exponent in theory, but they are *not* the bounds practitioners hit: real systems use graph/quantization indexes whose dynamic recall under adversarial churn is unquantified. The open gap is a **predictive model** of the (recall, staleness, throughput) frontier for graph indexes — i.e., proving that incremental repair preserves navigability within a bounded recall loss. This is empirically open: no theorem matches FreshDiskANN/SPFresh behavior.

## 7. Current Research (as of June 2026)

- In-place graph repair and "self-healing" edges to avoid global merges; locality-aware compaction scheduling.
- Freshness-aware query planning that mixes a hot in-memory delta index with a cold base index and merges result sets *(frontier — verify)*.
- Out-of-distribution and drift-aware updates connecting to filtered/streaming ANN (DiskANN, SPANN teams at Microsoft; Milvus/Zilliz; Pinecone; Weaviate research).
- Benchmarks: streaming track of *big-ann-benchmarks* (NeurIPS competition) standardizing recall-under-churn measurement.

## 8. Future Work

- Provable recall bounds for incrementally maintained navigable graphs under adversarial deletion.
- A formal staleness SLA primitive integrated with transactional MVCC semantics so vector freshness composes with row visibility.
- Cost models linking ingest rate, merge cadence, and the achievable recall floor, enabling autoscaling.
- Co-design with embedding refresh (see distribution-shift problem) when the model itself changes mid-stream.

## 9. Key References

- **[SOTA]** Aditi Singh, Suhas Jayaram Subramanya, Ravishankar Krishnaswamy, Harsha Vardhan Simhadri. *FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search.* arXiv:2105.09613, 2021.
- **[SOTA]** Yuming Xu et al. *SPFresh: Incremental In-Place Update for Billion-Scale Vector Search.* SOSP, 2023.
- **[Foundational]** Alexandr Andoni, Piotr Indyk. *Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor in High Dimensions.* FOCS / CACM, 2006/2008.
- **[Foundational]** Yu A. Malkov, D. A. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs.* IEEE TPAMI, 2020.
- **[Foundational]** Kasper Green Larsen. *The Cell Probe Complexity of Dynamic Range Counting.* STOC, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
