---
id: 28-vector-similarity-search/gpu-billion-scale-ann
title: "GPU-resident billion-scale ANN"
topic: 28-vector-similarity-search
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# GPU-resident billion-scale ANN

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/gpu-billion-scale-ann` · **Status:** empirically-open

## 1. Problem Statement
A billion 128-d float32 vectors occupy ~512 GB — far beyond a single GPU's 40–192 GB HBM. The problem: design **index layouts and traversal algorithms that exploit the GPU memory hierarchy** (registers, shared memory, L2, HBM, then host/NVLink/PCIe) to answer high-recall ANN over $\sim 10^9$ vectors **within device-memory limits**, maximizing throughput (QPS) and minimizing latency.

- **(Systems/optimization)** Maximize QPS at recall $\ge\rho$ subject to: device memory $\le M_{\text{HBM}}$, with graph/IVF traversal mapped to warps/blocks and memory accesses **coalesced**.
- **(Layout)** Choose compression (PQ/RaBitQ) bit-rate, sharding, and on-device vs. host placement so the working set fits HBM while preserving recall.
- **(Algorithmic)** Restructure inherently irregular, pointer-chasing graph search (HNSW/Vamana) into SIMT-friendly, batched, branch-divergence-minimized traversal.

"Empirically-open": strong systems exist (CAGRA, GGNN, SONG, FAISS-GPU), but there is no clean theory of the optimal layout/traversal under the GPU memory-hierarchy cost model, and billion-scale within a single device's HBM still relies on aggressive compression + host offload with empirically-tuned tradeoffs.

## 2. Mathematical Foundations
The cost model is a **multi-level external-memory / parallel hierarchy**: each level $i$ has capacity $C_i$ and transfer cost; the relevant abstractions are the **Parallel External Memory (PEM)** model and the GPU's **SIMT** execution where a warp of 32 threads must take the same path or pay **branch divergence**, and where memory throughput depends on **coalesced** access (contiguous addresses per warp). Graph search is irregular pointer-chasing — adversarial for both. Reformulations exploit: (i) **batched** queries to amortize divergence (process many queries per block so warps stay full); (ii) **fixed-degree** graphs (CAGRA) so adjacency lists are aligned and coalesced; (iii) compression (PQ/RaBitQ, §quantization) so the resident set shrinks by $32\times$ to fit HBM, with distance tables in shared memory.

Throughput is bounded by the **roofline** model: either compute-bound (distance evaluations, well-suited to GPU FMA throughput) or memory-bandwidth-bound (HBM at ~1–8 TB/s). Billion-scale forces the working set across the HBM/host boundary, making the **PCIe/NVLink bandwidth** and the cut between resident and offloaded shards the binding constraint — a partitioning/caching problem analogous to the disk-ANN I/O question but with a faster, parallel hierarchy.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **CAGRA** (Ootomo et al., NVIDIA / RAPIDS cuVS, ICDE 2024) is a GPU-native fixed-degree graph index with parallel traversal, outperforming HNSW on GPU at high QPS. **GGNN** (Groh et al., IEEE TBD 2022) builds and searches graph indices on GPU. **SONG** (Zhao et al., ICDE 2020) restructures graph ANN for GPU. **FAISS-GPU** (Johnson–Douze–Jégou, IEEE TBD 2019) provides GPU IVF-PQ and brute force, the long-standing baseline. For billion-scale within HBM, IVF-PQ with byte/4-bit codes plus on-GPU re-rank, or RaBitQ codes, are used; multi-GPU sharding (cuVS, RAFT) scales out. *(frontier — verify)* Recent GPU+CXL/host-offload designs target billion-scale on a single GPU by streaming shards.

**Theory-SOTA.** No matching lower/upper bound in a GPU-hierarchy model; analysis is empirical (roofline, profiling).

## 4. Upper Bound
Empirical upper bounds dominate. CAGRA reports order-of-magnitude QPS gains over CPU HNSW at comparable recall, and FAISS-GPU brute force achieves billions of distance evaluations/sec exploiting tensor/FMA throughput. With PQ at ~16–32 bytes/vector, a billion vectors compress to ~16–32 GB, **fitting a single high-end GPU's HBM**, enabling fully-resident search with re-rank from a host copy; this is the practical "upper bound" route to billion-scale on one device. In the PEM/parallel-hierarchy model, batched graph traversal achieves $O(L)$ hierarchy-aware steps with $P$-way parallelism, giving amortized per-query cost $O(L/P + \text{divergence overhead})$, but constants — set by coalescing and divergence — dominate and are only characterized empirically.

## 5. Lower Bound
Rigorous lower bounds are scarce. The general ANN cell-probe / LSH lower bounds (Andoni–Razenshteyn) apply to the *work* regardless of hardware, lower-bounding total distance computations. In the parallel-hierarchy setting, **bandwidth lower bounds** follow from the roofline: any algorithm touching $W$ bytes of resident data per query batch needs $\ge W / \text{HBM-bandwidth}$ time, and any algorithm whose working set exceeds HBM must move $\ge (W - C_{\text{HBM}})$ bytes across PCIe/NVLink, an unconditional transfer lower bound. **Branch-divergence** imposes a model-specific penalty: irregular traversal can force a $\Theta(\text{warp-width})$ slowdown in adversarial graphs. None of these are tight against the systems-SOTA.

## 6. The Gap
The gap is between strong empirical systems and the absence of a predictive theory. We lack: (a) a clean GPU-memory-hierarchy cost model under which an index layout is provably optimal (or constant-competitive); (b) a principled answer to the resident-vs-offload partition for billion-scale on a single device, with bandwidth-aware guarantees; (c) analysis tying graph degree/structure to divergence and coalescing efficiency. Practice picks fixed-degree graphs and PQ bit-rates by sweeping; theory cannot yet say these are near-optimal. Closing it needs a PEM/SIMT-aware analysis of graph traversal with matching bandwidth and divergence lower bounds.

## 7. Current Research (as of June 2026)
Directions: (i) GPU-native graph indices minimizing divergence and maximizing coalescing (CAGRA, cuVS — NVIDIA); (ii) compression co-designed with GPU layout (RaBitQ codes in shared memory, tensor-core distance kernels) *(frontier — verify)*; (iii) out-of-core / host-offload streaming to break the HBM limit at billion-scale, including CXL and GPUDirect-Storage paths; (iv) multi-GPU sharding and disaggregation. People/groups: NVIDIA RAPIDS/cuVS team (Ootomo, Corey Nolet), the FAISS team (Douze, Jégou), the GGNN/SONG academic authors, and BigANN GPU-track participants. *(frontier — verify)* 2025 entries report single-GPU billion-scale at high recall via streamed RaBitQ shards.

## 8. Future Work
- A GPU-hierarchy cost model with provably (near-)optimal index layouts.
- Bandwidth-aware resident/offload partitioning for billion-scale on one device with guarantees.
- Divergence-minimizing graph structures with formal coalescing analysis.
- Co-designed quantization + GPU kernels (tensor-core distance tables) and their rate–recall–throughput frontier.

## 9. Key References
- **[SOTA]** H. Ootomo, A. Naruse, C. Nolet, R. Wang, T. Feher, Y. Wang. *CAGRA: Highly Parallel Graph Construction and Approximate Nearest Neighbor Search for GPUs.* ICDE, 2024. — [arXiv](https://arxiv.org/abs/2308.15136) · [DOI](https://doi.org/10.1109/ICDE60146.2024.00323)
- **[SOTA]** J. Johnson, M. Douze, H. Jégou. *Billion-scale Similarity Search with GPUs.* IEEE Transactions on Big Data, 2019. — [arXiv](https://arxiv.org/abs/1702.08734) · [DOI](https://doi.org/10.1109/TBDATA.2019.2921572)
- **[SOTA]** F. Groh, L. Wieschollek, H. P. A. Lensch et al. *GGNN: Graph-based GPU Nearest Neighbor Search.* IEEE Transactions on Big Data, 2022. — [arXiv](https://arxiv.org/abs/1912.01059) · [DOI](https://doi.org/10.1109/TBDATA.2022.3161156)
- **[SOTA]** W. Zhao, S. Tan, P. Li. *SONG: Approximate Nearest Neighbor Search on GPU.* ICDE, 2020. — [DOI](https://doi.org/10.1109/ICDE48307.2020.00094)
- **[Foundational]** L. Arge, M. T. Goodrich, M. Nelson, N. Sitchinava. *Fundamental Parallel Algorithms for Private-Cache Chip Multiprocessors (PEM model).* SPAA, 2008. — [DBLP search](https://dblp.org/search?q=Fundamental+Parallel+Algorithms+for+Private-Cache+Chip+Multiprocessors)
- **[SOTA]** J. Gao, C. Long. *RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound.* SIGMOD, 2024. — [DOI](https://doi.org/10.1145/3654970) · [arXiv](https://arxiv.org/abs/2405.12497)

## 10. Worked Example

**Why compression is the key to fitting one GPU.** Take $n = 10^9$ vectors, $d = 128$, float32 (4 bytes).

- Raw footprint: $10^9 \times 128 \times 4 = 5.12 \times 10^{11}$ bytes $= 512$ GB. No single GPU's HBM (40–192 GB) holds this — host offload required.
- **PQ at 16 bytes/vector** (each 128-d vector split into 16 subspaces, one byte codebook index each, a $32\times$ reduction): $10^9 \times 16 = 1.6\times10^{10}$ bytes $= 16$ GB. This **fits** an 80 GB A100/H100 fully resident, leaving room for the codebook distance tables in shared memory and a re-rank buffer.

**Roofline check.** Suppose HBM bandwidth is $2$ TB/s and a query batch scans $W = 16$ GB of resident PQ codes (one full IVF list sweep, worst case). Lower bound on time: $W / \text{bandwidth} = 1.6\times10^{10} / 2\times10^{12} = 8$ ms per batch from bandwidth alone — so to hit sub-millisecond latency you must *not* scan all codes: IVF restricts to $n_{\text{probe}}$ lists, cutting $W$ by $\sim 100\times$ to $\sim 0.08$ ms, now compute-bound on FMA throughput. This is exactly the §5 unconditional bandwidth bound dictating that high QPS requires both compression (shrink $W$) and partitioning (touch less of it).

---
*Part of the [DBMS Research catalog](../../README.md).*
