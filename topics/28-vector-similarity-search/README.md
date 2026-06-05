# Vector Databases & Similarity Search

Vector databases index high-dimensional embeddings to answer approximate nearest neighbor (ANN) queries, trading recall against latency and memory. The central tensions are the curse of dimensionality, the lack of worst-case guarantees for graph indexes like HNSW, and the systems challenges of filtered/hybrid search, updates, disk-resident and disaggregated deployments, and integrating ANN into relational query engines.

This catalog collects 30 research-grade open problems at the intersection of theory (complexity, bounds, expressiveness) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [Provable guarantees for HNSW graph search](./hnsw-provable-guarantees.md) | open | Whether greedy search on Hierarchical Navigable Small World graphs admits worst-case recall and query-time bounds beyond empirical observation. |
| [Recall-latency-memory Pareto lower bound](./recall-latency-memory-lower-bound.md) | open | A three-way information-theoretic lower bound relating achievable recall, query time, and index memory for ANN. |
| [Optimal product quantization codebooks](./optimal-product-quantization.md) | partially-solved | Whether PQ/OPQ codebook learning can provably minimize expected distance distortion under a fixed bit budget. |
| [Filtered ANN with predicate selectivity guarantees](./filtered-ann-selectivity.md) | empirically-open | Index structures that maintain recall and latency across the full range of attribute-predicate selectivities. |
| [Curse of dimensionality threshold for ANN](./dimensionality-threshold.md) | open | Characterizing the intrinsic-dimension regime where any sublinear ANN method must degrade to near-linear scan. |
| [Updatable graph indexes under churn](./updatable-graph-index.md) | empirically-open | Maintaining HNSW/DiskANN navigability and recall under high-rate inserts and deletes without periodic rebuilds. |
| [Disk-resident ANN I/O lower bounds](./disk-ann-io-bounds.md) | partially-solved | Tight bounds on the number of random page reads required for high-recall ANN over out-of-core vector sets. |
| [Hybrid dense-sparse retrieval fusion](./hybrid-dense-sparse-fusion.md) | empirically-open | Principled, index-aware fusion of dense-vector and sparse-lexical scores with bounded top-k error. |
| [Instance-optimal ANN index selection](./instance-optimal-ann.md) | open | Whether an index can provably match the best graph/quantization configuration for a given dataset and query distribution. |
| [LSH beyond worst-case data distributions](./lsh-beyond-worst-case.md) | partially-solved | Data-dependent locality-sensitive hashing that provably beats data-oblivious LSH on benign distributions. |
| [Quantization error vs. recall theory](./quantization-recall-theory.md) | open | A predictive theory linking compression bit-rate to top-k recall loss for scalar/product/additive quantizers. |
| [GPU-resident billion-scale ANN](./gpu-billion-scale-ann.md) | empirically-open | Index layouts and traversal exploiting GPU memory hierarchy for billion-vector ANN within device-memory limits. |
| [Streaming ANN with bounded staleness](./streaming-ann-staleness.md) | empirically-open | Serving fresh nearest neighbors over continuously arriving vectors with quantified recall-vs-staleness tradeoff. |
| [ANN over disaggregated storage](./disaggregated-ann.md) | empirically-open | Graph and quantization indexes tuned for compute/storage separation with high-latency paginated remote reads. |
| [Cost model for ANN query planning](./ann-cost-model.md) | open | A predictive cost model for ANN operators enabling a relational optimizer to choose plans and tuning parameters. |
| [Optimal IVF partitioning and probing](./ivf-partition-probing.md) | partially-solved | Provably balanced inverted-file partitioning with adaptive n-probe selection minimizing scanned vectors at target recall. |
| [Multi-vector and late-interaction search](./multi-vector-late-interaction.md) | empirically-open | Efficient top-k over documents represented by many vectors (e.g., ColBERT) without materializing all interactions. |
| [Distribution shift in learned embeddings](./embedding-distribution-shift.md) | empirically-open | Keeping ANN recall stable as the embedding model or data distribution drifts away from index-build assumptions. |
| [Provable diversity-aware nearest neighbors](./diverse-nearest-neighbors.md) | open | Sublinear retrieval that returns relevant yet result-set-diverse neighbors with approximation guarantees. |
| [Range and threshold similarity search](./range-similarity-search.md) | partially-solved | Indexes answering all-points-within-radius queries with bounds independent of unbounded result-set size. |
| [Memory-bandwidth-bound ANN on CPUs](./memory-bandwidth-ann.md) | empirically-open | Traversal and layout that turn ANN from latency-bound pointer chasing into bandwidth-saturating scans. |
| [Authenticated/verifiable ANN results](./verifiable-ann.md) | open | Succinct proofs that returned neighbors are the true approximate top-k, for untrusted vector-search services. |
| [Privacy-preserving similarity search](./private-similarity-search.md) | partially-solved | ANN over encrypted/secret-shared vectors with quantified leakage and practical query latency. |
| [Compression-aware distance estimation](./compression-aware-distance.md) | partially-solved | Asymmetric distance computation that provably tightens recall when only the database side is quantized. |
| [Cross-modal and metric-learning ANN](./cross-modal-ann.md) | empirically-open | Indexing under learned, possibly non-metric similarities that violate triangle-inequality assumptions of graph search. |
| [Adversarial robustness of ANN indexes](./adversarial-robustness-ann.md) | open | Query/insert sequences that force graph indexes into worst-case recall or build cost, and defenses against them. |
| [Tail-latency control for ANN serving](./ann-tail-latency.md) | empirically-open | Bounding p99 ANN query latency under concurrency and skew without sacrificing mean recall. |
| [Joint compression and graph co-design](./compression-graph-codesign.md) | open | Jointly optimizing quantization and graph topology rather than treating them as independent layers. |
| [Top-k ANN joins over two vector sets](./vector-similarity-joins.md) | partially-solved | Scalable all-pairs / k-NN similarity joins between large vector collections with subquadratic guarantees. |
| [Right-sizing index parameters automatically](./auto-tuning-ann-params.md) | empirically-open | Automatically selecting M, efConstruction, n-probe, and bit budgets to hit a recall target at minimum cost. |

---
[Back to taxonomy](../../TAXONOMY.md)
