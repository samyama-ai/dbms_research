# Out-of-core and GPU graph analytics scheduling

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/out-of-core-gpu-analytics` · **Status:** empirically-open

## 1. Problem Statement
Run iterative graph analytics (PageRank, BFS/SSSP, connected components, label propagation, GNN aggregation) on graphs whose data structures exceed device memory — GPU HBM and/or host RAM. The host graph and its working state must stream from a deeper tier (host RAM, NVMe SSD, or across PCIe/NVLink) while computation proceeds. The scheduling problem:

> Partition the graph and order the movement and processing of partitions across the memory hierarchy so that iterative, **irregular**, data-dependent access converges with **minimal I/O stalls** and maximal device utilization.

Sub-problems: graph partitioning/ordering for locality; overlap of transfer and compute; selecting active (frontier) subsets to avoid moving cold data; choosing push vs. pull and synchronous vs. asynchronous iteration. It is **empirically open**: many systems push the frontier of GB/s-per-watt and largest-graph-on-one-GPU, but no scheduler is known optimal, and results are sensitive to graph structure.

## 2. Mathematical Foundations
Model the hierarchy as the **external-memory (EM) / DAM model** (Aggarwal–Vitter): $N$ data items, block size $B$, fast memory $M$; cost counts block transfers (I/Os). Lower bounds for permutation/sorting are $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$. Sparse irregular access defeats large $B$ amortization, so the relevant quantity is the **I/O complexity of sparse matrix–vector multiply (SpMV)** repeated for $I$ iterations.

- **Semi-external** model: vertices ($O(|V|)$ state) fit in $M$, edges stream — enables single-pass-per-iteration schedules.
- Partition quality is governed by **edge cut / vertex separators** and bandwidth; balanced $k$-partitioning is NP-hard, so heuristics (METIS, streaming partitioners, Gorder/Rabbit ordering) are used.
- GPU adds **memory-coalescing** and **warp-divergence** terms; the roofline model bounds achievable throughput by min(compute, bandwidth) intensity.

## 3. State of the Art (SOTA)
**Out-of-core (CPU/SSD):** GraphChi (Kyrola, OSDI 2012) introduced the **Parallel Sliding Windows** schedule; X-Stream (edge-centric streaming, SOSP 2013); GridGraph (2D partition, ATC 2015); Mosaic (Hilbert-ordered, EuroSys 2017); semi-external **FlashGraph** (FAST 2015).

**GPU / out-of-GPU-core:** Gunrock (frontier-centric, PPoPP 2016) is the throughput reference in-core; **GraphReduce**, **Subway** (EuroSys 2020, loads only active subgraphs), **EMOGI** (zero-copy UVM, VLDB 2021), **Grus / HALO** unified-memory schedulers, and large-scale **DGL/cuGraph** sampling pipelines for GNNs. No single scheduler dominates across BFS, PageRank, and SSSP on all of the Graphalytics graphs.

## 4. Upper Bound
- Per-iteration I/O: $O(\frac{|E|}{B})$ block transfers in semi-external mode (each edge streamed once); $O(I\cdot\frac{|E|}{B})$ total for $I$ iterations.
- PSW (GraphChi): $O(P^2)$ block reads per iteration for $P$ shards, with sequential access guarantee.
- Subway-style active-subgraph loading: transfers $O(\sum_i |E(\text{frontier}_i)|/B)$, asymptotically better when frontiers are small (BFS/SSSP) but no better worst-case for dense PageRank.
- Throughput upper bound: roofline $\min(\text{FLOP}_{\max}, \text{BW}\cdot\text{intensity})$; PCIe/NVLink bandwidth caps out-of-core GPU speed.

## 5. Lower Bound
- EM lower bound: any algorithm performing the $I$ SpMVs of irregular analytics needs $\Omega(I\cdot\frac{|E|}{B})$ I/Os in the worst case when reuse is absent; sorting/permutation lower bounds $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ apply to the partition/relabel preprocessing.
- Balanced partitioning (to minimize cut and hence cross-tier traffic) is **NP-hard** and hard to approximate within any constant under standard assumptions.
- No nontrivial unconditional lower bound shows a *specific* scheduler is optimal; the empirical openness stems from worst-case I/O bounds being matched up to constants while real performance hinges on instance structure.

## 6. The Gap
Worst-case I/O bounds are essentially matched (streaming each edge once per iteration is both achievable and necessary without reuse). The real gap is **instance-adaptive**: choosing partitioning, ordering, frontier compaction, sync mode, and transfer/compute overlap to exploit locality and skip cold data. There is no scheduler with provable competitive ratio against an offline-optimal across diverse graphs, and no cost model that reliably predicts the best configuration — so the problem stays empirically open.

## 7. Current Research (as of June 2026)
Active groups: Hwu/cuGraph and NVIDIA (UVM/GPUDirect Storage zero-copy); Kim/Eom (Subway, EMOGI lineage); Lin/cuGraph; Pingali/Galois for asynchronous out-of-core. *(frontier — verify)* GPUDirect Storage and CXL-attached memory are reshaping the hierarchy, prompting CXL-aware out-of-core schedulers. *(frontier — verify)* GNN-driven demand — billion-edge neighbor sampling and feature streaming (DGL/GraphLearn, P3, BGL, large-scale mini-batch GNN training) — is now the dominant out-of-core workload, shifting the objective toward feature-fetch I/O rather than topology I/O.

## 8. Future Work
- A scheduler with a provable competitive ratio for out-of-core iterative analytics.
- Cost models predicting optimal partition/order/sync configuration from graph statistics.
- CXL/disaggregated-memory-aware schedulers replacing PCIe-bound designs.
- Unified topology + feature streaming for GNN training at trillion-edge scale.

## 9. Key References
- **[Foundational]** Aggarwal, Vitter. *The input/output complexity of sorting and related problems.* CACM, 1988.
- **[Foundational]** Kyrola, Blelloch, Guestrin. *GraphChi: Large-scale graph computation on just a PC.* OSDI, 2012.
- **[SOTA]** Wang, Davidson et al. *Gunrock: A high-performance graph processing library on the GPU.* PPoPP, 2016.
- **[SOTA]** Sabet, Zhao, Gupta. *Subway: Minimizing data transfer during out-of-GPU-memory graph processing.* EuroSys, 2020.
- **[SOTA]** Min et al. *EMOGI: Efficient memory-access for out-of-memory graph-traversal in GPUs.* PVLDB, 2021.
- **[Survey]** Roy, Mihailovic, Zwaenepoel. *X-Stream: Edge-centric graph processing using streaming partitions.* SOSP, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
