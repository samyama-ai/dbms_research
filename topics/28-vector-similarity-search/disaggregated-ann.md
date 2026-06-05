# ANN over disaggregated storage

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/disaggregated-ann` · **Status:** empirically-open

## 1. Problem Statement

In disaggregated (compute/storage-separated) architectures — cloud object stores (S3, GCS), remote SSD pools, CXL memory, or NVMe-over-Fabrics — the index data lives behind a high-latency, paginated, byte-range-addressable remote interface. We must answer ANN queries where **random access is expensive**: each remote read has latency $L$ (often 1–100 ms for object stores) and a minimum granularity $B$ (e.g., 4–64 KB pages, or whole shards). The graph-walk or posting-list scan that is cheap on local NVMe becomes I/O-bound.

- **Optimization variant.** Minimize end-to-end query latency (or \$ cost) = $\sum (\text{remote reads}) \cdot L + \text{transfer} / \text{bandwidth}$, subject to a recall floor $R@k$, given the data layout is fixed.
- **Layout/co-design variant.** Jointly choose the index structure (graph degree, quantization codebook, page packing) *and* the data layout to minimize expected remote round-trips per query.
- **Decision variant.** Given a latency budget $T$ and recall $R$, decide feasibility for a given $(L, B, \text{bandwidth})$.

The central difficulty: graph traversal is inherently *pointer-chasing* with data-dependent, hard-to-prefetch access; quantization indexes scan large contiguous posting lists, trading more bytes for fewer round-trips.

## 2. Mathematical Foundations

Model the remote tier in the **external-memory (I/O) model** of Aggarwal–Vitter with block size $B$ and an additional per-I/O latency penalty $L$ (a "latency-augmented EM model"). Query cost $= \alpha \cdot (\#I/Os) \cdot L + \beta \cdot (\text{bytes read})$. A greedy graph walk visits $h = O(\log n)$ nodes; naively each node is one dependent I/O, so latency $\approx h \cdot L$ — dominated by $L$, not bandwidth.

Two levers reduce $h\cdot L$:

1. **Locality of the walk.** Pack graph nodes so that neighbors co-reside in a page; this is a graph-partitioning / minimum-linear-arrangement problem (NP-hard) approximated by recursive bisection or space-filling-curve orders. Quality is captured by the expected *page faults per hop*.
2. **Batching / speculation.** Read $w$ candidates per round-trip (beam width), reducing rounds to $O(h/w)$ at the cost of bandwidth — a classic latency/bandwidth tradeoff, formalized via the **parallel-disk** or **bulk-synchronous** cost.

Quantization side: with codebook of $m$ subspaces and $2^b$ centroids, a posting list of length $\ell$ costs one (or few) sequential reads of $\ell \cdot m \cdot b/8$ bytes — bandwidth-bound, latency-amortized. Recall vs. bytes is governed by the rate–distortion of PQ: distortion $\propto 2^{-2b/D}$ (high-rate quantization theory).

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *DiskANN/Vamana* (Subramanya et al., NeurIPS 2019) pioneered SSD-resident graph search with PQ in RAM as a navigational filter and full vectors on disk, minimizing SSD reads per query. *SPANN* (Chen et al., NeurIPS 2021) is a memory–disk hybrid inverted index optimized for posting-list locality. *Starling* (SIGMOD 2024) re-lays out DiskANN graphs (block shuffling + in-block search) to cut SSD I/O. Cloud-native: *AnalyticDB-V*, Turbopuffer, Lance/LanceDB (columnar on object storage), and S3-backed vector indexes.
- **Theory-SOTA.** I/O-efficient nearest-neighbor under the EM model is sparse; LSH variants admit EM analyses but with weak constants in high dimension.

## 4. Upper Bound

DiskANN-style indexes empirically achieve high recall with a small constant number of SSD reads per query (often 4–8 page reads) by keeping a PQ-compressed graph in memory and fetching full vectors only for re-ranking; this gives query I/O $O(1)$ pages amortized in practice, not provably. In the latency-augmented EM model, a beam-width-$w$ walk gives $O((h/w)\cdot L + h\cdot B/\text{bw})$ — tunable but without a closed recall guarantee. PQ posting-list scan is $O(\ell\cdot m\cdot b/(8\cdot \text{bw}) + L)$ per probed cell.

## 5. Lower Bound

No round-optimal lower bound is established for *approximate* NN over object storage. Relevant impossibilities: in the EM model, exact NN inherits the high-dimensional cell-probe barrier (Andoni–Indyk–Pătraşcu), so polylog I/O with linear space is impossible for exact search. Communication-complexity lower bounds for set-disjointness imply that any index distinguishing near vs. far at distance gap $c$ must read $\Omega(\cdot)$ bits in the worst case for hard instances. A clean *round-complexity* lower bound matching beam search is open.

## 6. The Gap

Practitioners hit a layout/round-trip wall that theory does not characterize: we lack (a) a lower bound on remote rounds for $R@k$ recall, and (b) a layout that provably bounds page-faults-per-hop for navigable graphs. The gap is **genuinely open and empirical** — current wins come from engineering (block packing, PQ navigation, async prefetch) rather than from a matched bound.

## 7. Current Research (as of June 2026)

- Graph layout co-optimization (Starling, block-aware Vamana) and learned page-packing.
- Tiered designs: in-memory compressed graph + remote re-rank; CXL-attached far memory for the cold tier *(frontier — verify)*.
- Columnar/object-store-native formats (Lance, Vortex) with predicate pushdown and ANN fused with analytical scans.
- Serverless / "zero-disk" vector search on S3 (Turbopuffer, MyScale, Pinecone serverless) trading latency for elastic cost *(frontier — verify)*.
- Groups: Microsoft Research (DiskANN/SPANN), Zilliz/Milvus, LanceDB, and cloud-warehouse vendors.

## 8. Future Work

- A latency-augmented EM cost model with provable round/recall tradeoffs.
- Prefetch-friendly graph orders and speculative multi-hop fetch.
- Quantization tuned for *bandwidth-bound* remote scans (large contiguous codes) vs. *latency-bound* graph walks — choosing per-workload.
- Integration with disaggregated transactional storage so vector and row data share a buffer/cache layer.

## 9. Key References

- **[SOTA]** Suhas Jayaram Subramanya, Devvrit, Rohan Kadekodi, Ravishankar Krishnaswamy, Harsha Vardhan Simhadri. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [PDF](https://suhasjs.github.io/files/diskann_neurips19.pdf)
- **[SOTA]** Qi Chen et al. *SPANN: Highly-efficient Billion-scale Approximate Nearest Neighbor Search.* NeurIPS, 2021. — [arXiv](https://arxiv.org/abs/2111.08566)
- **[SOTA]** Mengzhao Wang et al. *Starling: An I/O-Efficient Disk-Resident Graph Index Framework for High-Dimensional Vector Similarity Search on Data Segment.* SIGMOD, 2024. — [arXiv](https://arxiv.org/abs/2401.02116) · [DOI](https://doi.org/10.1145/3639269)
- **[Foundational]** Alok Aggarwal, Jeffrey Scott Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** Alexandr Andoni, Piotr Indyk, Mihai Pătraşcu. *On the Optimality of the Dimensionality Reduction Method.* FOCS, 2006. — [PDF](https://www.mit.edu/~andoni/papers/eps2n.pdf) · [DBLP search](https://dblp.org/search?q=On+the+Optimality+of+the+Dimensionality+Reduction+Method)

## 10. Worked Example

Latency vs. bandwidth on object storage. Suppose a greedy graph walk visits $h=12$ hops, each hop a dependent random read from S3 with latency $L=20$ ms and bandwidth $\text{bw}=200$ MB/s; an adjacency+vector page is $B=8$ KB.

Naive serial walk (beam width $w=1$): each hop is one round-trip, so latency $\approx h\cdot L + h\cdot B/\text{bw} = 12\times 20 + 12\times(8\text{KB}/200\text{MB/s})$. The transfer term is $12\times 0.04\ \text{ms}\approx 0.5$ ms — negligible. Total $\approx 240$ ms, entirely latency-bound.

Batched/beam walk ($w=4$): fetch 4 candidate pages per round, cutting rounds to $\lceil h/w\rceil = 3$. Latency $\approx 3\times 20 + 48\times B/\text{bw} = 60 + 48\times0.04 \approx 62$ ms — a $3.9\times$ speedup, paying $4\times$ the bytes (still cheap here because we are far from the bandwidth ceiling).

Contrast a quantization-index posting scan: one sequential read of $\ell=10^5$ PQ codes at $m=16$ subspaces, $b=8$ bits $=1.6$ MB, costing $L + 1.6\text{MB}/200\text{MB/s} = 20 + 8 = 28$ ms — *one* round-trip, bandwidth-amortized. This is exactly the latency-vs-bandwidth lever the layout/co-design variant must choose between per workload.

---
*Part of the [DBMS Research catalog](../../README.md).*
