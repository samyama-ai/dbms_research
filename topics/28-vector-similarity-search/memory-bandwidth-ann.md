# Memory-bandwidth-bound ANN on CPUs

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/memory-bandwidth-ann` · **Status:** empirically-open

## 1. Problem Statement

Graph-based approximate nearest neighbor (ANN) indices — HNSW, NSG, DiskANN — achieve state-of-the-art recall/latency, but their search is **pointer chasing**: each step reads a node's neighbor list and a set of vectors at addresses determined by the data, producing irregular, dependent memory accesses. On modern CPUs this makes single-query ANN **latency-bound** (stalled on cache/TLB misses) rather than **bandwidth-bound**, so it utilizes a small fraction of available DRAM bandwidth. The problem: design **traversal strategies and memory layouts** that convert ANN into (near-)sequential, prefetchable, bandwidth-saturating scans while preserving recall and sublinear comparison count. Concretely, minimize wall-clock latency at fixed recall by maximizing **effective bandwidth utilization** and **memory-level parallelism (MLP)**, subject to the graph's combinatorial search semantics. This is an *empirical/systems* problem: there is no clean asymptotic statement, but a measurable, reproducible gap between achieved and roofline-bound throughput.

## 2. Mathematical Foundations

The relevant model is the **external-memory / cache-oblivious** model (Aggarwal–Vitter): cost counted in block transfers of size $B$ between memory levels, with the **roofline** bound $T \ge \max(\text{FLOPs}/\pi,\ \text{Bytes}/\beta)$ where $\pi$ is peak compute and $\beta$ peak bandwidth. Graph search visits $O(\mathrm{ef}\cdot \deg)$ candidate vectors; with vector dimension $d$ and scalar bytes $b$, the byte traffic per query is $\Theta(\text{visited}\cdot d\, b)$, and the achievable latency is bounded below by traffic$/\beta$ *only if* MLP is high enough to hide latency $L$: by **Little's Law**, sustaining bandwidth $\beta$ requires $\approx \beta \cdot L / (\text{request size})$ outstanding misses. Pointer-chasing serializes dependent loads, collapsing MLP to $\approx 1$, so achieved throughput is $\approx (\text{line size})/L \ll \beta$. The design problem is to restructure the dependency graph of memory accesses to raise MLP toward the line-fill-buffer limit.

## 3. State of the Art (SOTA)

- **Systems:** **HNSW** (Malkov–Yashunin, TPAMI 2018/2020) is the dominant in-memory baseline. **DiskANN/Vamana** (Subramanya et al., NeurIPS 2019) targets SSD, reorganizing for sequential block reads and using **product-quantized** in-memory vectors to cut traffic. **SVS / scann-style** layouts (Intel SVS, Google ScaNN) use SIMD-friendly quantized layouts and **LVQ** (locally-adaptive vector quantization) to make distance kernels bandwidth-friendlier. **Glass**, **hnswlib** prefetch optimizations, and **ParlayANN** (CMU, 2024) explore parallel, cache-conscious construction and search.
- **Techniques in production:** software prefetching of neighbor vectors one hop ahead, structure-of-arrays vector storage, reordering nodes by graph locality (graph reordering / GOrder-style), and batching queries to amortize MLP.

## 4. Upper Bound

No tight asymptotic upper bound exists. The practical "upper bound" is the **roofline**: a query that must touch $V$ vectors of $d\,b$ bytes cannot beat $V d b/\beta$ latency, and quantization (PQ, SQ, LVQ) reduces $b$ (e.g. $4\times$–$32\times$), proportionally lowering the bound. DiskANN-style designs approach the SSD sequential-bandwidth roofline; in-memory, SVS-LVQ and prefetched HNSW report large fractions of DRAM bandwidth on batched workloads *(frontier — verify exact utilization figures)*. Batched/SIMD distance kernels are compute-roofline-bound and effectively solved.

## 5. Lower Bound

There is **no nontrivial unconditional lower bound** isolating the bandwidth gap; this is what makes the problem empirically open rather than theoretically closed. The information-theoretic floor is the roofline traffic bound above. From the algorithmic side, graph-ANN must perform $\Omega(\text{polylog or }n^{o(1)})$ dependent hops for good recall on adversarial data, and each hop's target is data-dependent, so a *worst-case* argument suggests MLP cannot be raised to the roofline without speculative over-reading (reading vectors that may not be needed), which trades bandwidth for latency. Cell-probe lower bounds for ANN bound *probe count*, not *bandwidth utilization*, and do not directly apply.

## 6. The Gap

The gap is between achieved single-query latency (latency-bound, low MLP) and the roofline bandwidth bound. It is **closed for batched/throughput** workloads (SIMD + many concurrent queries saturate bandwidth) but **open for low-latency single-query** search, where dependent hops serialize. Closing it requires either (i) layouts that co-locate likely-visited neighbors so a hop is one sequential read, (ii) speculative multi-hop prefetch with provably bounded waste, or (iii) algorithm redesign (e.g. partition-then-scan hybrids) that are bandwidth-bound by construction.

## 7. Current Research (as of June 2026)

- Speculative/beam-parallel traversal raising MLP per query *(frontier — verify)*.
- Quantization-aware layouts (LVQ, RaBitQ, 2024) that shrink per-hop traffic while keeping asymmetric distance accuracy.
- Graph reordering and degree-bounded layouts for cache locality (ParlayANN, CMU — Blelloch, Dhulipala, Gu).
- Hybrid IVF-then-graph designs that turn the first phase into a bandwidth-bound scan.
- CXL / tiered-memory ANN where bandwidth modeling becomes first-order.

## 8. Future Work

- A predictive cost model mapping graph topology + layout to achieved MLP/bandwidth.
- Provably bounded-waste speculative prefetch for graph search.
- Single-query designs that hit a constant fraction of DRAM roofline at fixed recall.
- Co-design of quantizer, layout, and traversal as one optimization.

## 9. Key References

- **[Foundational]** Malkov, Yu. A., Yashunin, D. A. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs (HNSW).* IEEE TPAMI, 2020. — [arXiv](https://arxiv.org/abs/1603.09320) · [DOI](https://doi.org/10.1109/TPAMI.2018.2889473)
- **[SOTA]** Subramanya, S. J., Devvrit, Kadekodi, R., Krishnaswamy, R., Simhadri, H. V. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [NeurIPS](https://proceedings.neurips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html)
- **[Foundational]** Aggarwal, A., Vitter, J. S. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Aguerrebere, C., Bhati, I., Hildebrand, M., Tepper, M., Willke, T. *Similarity Search in the Blink of an Eye with Compressed Indices (SVS/LVQ).* VLDB, 2023. — [arXiv](https://arxiv.org/abs/2304.04759) · [DOI](https://doi.org/10.14778/3611479.3611537)
- **[SOTA]** Manohar, M. D., Shen, Z., Blelloch, G., Dhulipala, L., Gu, Y., Simhadri, H. V., Sun, Y. *ParlayANN: Scalable and Deterministic Parallel Graph-Based ANN.* PPoPP, 2024. — [arXiv](https://arxiv.org/abs/2305.04359) · [DOI](https://doi.org/10.1145/3627535.3638475)

## 10. Worked Example

One HNSW query visits $V=200$ vectors, each $d=768$ dims at $b=4$ bytes (fp32), so byte traffic $\approx Vdb = 200\cdot768\cdot4 \approx 0.61$ MB. On a DRAM channel with bandwidth $\beta=20$ GB/s the **roofline latency** is $0.61\text{MB}/20\text{GB/s}\approx 31\ \mu s$.

But the 200 vectors are read along $\approx 50$ *dependent* hops (beam search, $\mathrm{ef}$ small). Each hop stalls on a cache miss of latency $L\approx 100$ ns before the next address is known, so wall-clock $\gtrsim 50\cdot 100\text{ns}=5\ \mu s$ of pure stall — and with MLP $\approx 1$, the effective bandwidth is only $(64\text{ B line})/100\text{ns}=0.64$ GB/s, i.e. **3% of the 20 GB/s roofline**.

**Little's Law check:** to saturate $\beta$ you need $\beta L/\text{(line)} = (20\text{GB/s}\cdot 100\text{ns})/64\text{B}\approx 31$ outstanding misses; pointer-chasing supplies $\approx 1$. **Quantization** (LVQ to $b=1$ byte) cuts traffic $4\times$ to $\approx 0.15$ MB, dropping the roofline to $\approx 8\ \mu s$ and shrinking per-hop reads so more fit in flight — illustrating why shrinking $b$ and raising MLP are the two levers in the open gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
