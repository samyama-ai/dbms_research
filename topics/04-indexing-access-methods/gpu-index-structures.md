# GPU-resident index structures

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/gpu-index-structures` · **Status:** empirically-open

## 1. Problem Statement
Design index structures whose layout and algorithms exploit the GPU memory hierarchy (global HBM, L2, shared memory/scratchpad, registers) and SIMT execution to answer point lookups, predecessor/successor, and range queries at high throughput. Concretely: given $n$ keys, support a batch $Q$ of $q$ queries and minimize wall-clock time on a GPU subject to (i) coalesced global-memory access, (ii) minimal warp divergence, (iii) bounded shared-memory footprint, and (iv) host↔device transfer cost. Variants: **static** (build once, query many — the throughput-optimization variant), **dynamic** (concurrent insert/delete/query — a concurrency variant), and the **build-cost** variant (amortize construction against query volume). The open question is whether a single design dominates across selectivity regimes (point-heavy vs. range-heavy) and key distributions, and how close practice can get to memory-bandwidth-bound ideal performance.

## 2. Mathematical Foundations
Model GPU execution via the parallel external-memory / PEM and the more faithful **(P)RAM-with-coalescing** abstractions. Let $B$ be the cache-line / coalescing width (e.g., a 128-byte transaction = 32 4-byte keys), $M$ shared-memory size, $p$ the number of concurrent threads. A search touching $t$ distinct memory transactions costs $\Theta(t)$ in the parallel-EM model; a B-tree-like index of fanout $f=\Theta(B)$ has height $\Theta(\log_B n)$, giving query cost $\Theta(\log_B n)$ transactions. Throughput is bounded by aggregate bandwidth $\beta$: if each of $q$ queries needs $D$ bytes of *distinct* traffic, total time $\geq qD/\beta$ (the bandwidth lower bound). Warp divergence is captured by counting *active mask* utilization: a warp executing a branch with selectivity $s$ wastes a factor up to $1/\max(s,1-s)$. Sorting-network and radix primitives underpin batch builds; the work-span model ($T_1$ work, $T_\infty$ span) governs build scalability.

## 3. State of the Art (SOTA)
- **Systems-SOTA (static):** *Harmonia* (Yan et al., PPoPP 2019) — a B-tree reorganized so sibling pointers live contiguously, reducing divergence; reports billions of lookups/s. *GPU B+-tree* and *RadixSpline*-style learned variants push range throughput.
- **Dynamic:** *GpuBTree* / *Warp-cooperative B-tree* (Awad et al., PPoPP 2019) supports concurrent updates via a warp-cooperative work-sharing strategy and a slab-allocator. *SlabHash* (Ashkiani et al., 2018) is the SOTA GPU hash table for point lookups.
- **Learned/GPU hybrids:** GPU-accelerated RMI and *RadixSpline* (Kipf et al., aiDM 2020) port learned indexes; *(frontier — verify)* recent work fuses learned models with GPU LSM/B-trees.
- **LSM on GPU:** Awad et al.'s GPU LSM and follow-ups handle high insert rates.

## 4. Upper Bound
For point queries, sorted-array + GPU binary/k-ary search gives $O(\log_f n)$ transactions per query with $f=\Theta(B)$; Harmonia/GpuBTree realize this with near-optimal coalescing. For batches, sort the query set and co-traverse to maximize locality, giving aggregate cost $O(q\log_B n)$ work that is bandwidth-bound in practice. Build is $O(n\log n)$ work via GPU radix sort with $O(\log n)$ span. Hash tables (SlabHash) achieve $O(1)$ expected transactions per lookup. These bounds hold in the parallel-EM / coalesced-RAM model; none is proven optimal against the bandwidth floor with tight constants.

## 5. Lower Bound
Any comparison/predecessor index on the GPU inherits cell-probe predecessor lower bounds: in the cell-probe model with word size $w$ and space $n^{1+o(1)}$, predecessor search needs $\Omega(\log_w n / \log\log n)$ probes (Pătrașcu–Thorup, STOC 2006), which lower-bounds transaction count per query. The bandwidth bound $qD/\beta$ is an unconditional info-theoretic floor for distinct traffic. No GPU-specific super-constant separation between learned and comparison indices is known; lower bounds for warp-divergence cost are essentially folklore and not tight.

## 6. The Gap
Theory gives per-query probe optimality (Pătrașcu–Thorup) and a bandwidth floor, but **no model jointly captures coalescing, divergence, occupancy, and transfer cost**, so we cannot say which measured design is asymptotically optimal. Empirically, designs differ by 2–5× across workloads with no dominating structure; the gap is between *what bandwidth permits* and *what current layouts achieve*, plus the absence of a predictive model. This is genuinely open: closing it needs both a faithful cost model (see `access-method-cost-model`) and designs provably matching it.

## 7. Current Research (as of June 2026)
Active threads: warp-cooperative dynamic trees and hash tables (Owens group, UC Davis); learned-index/GPU fusion and *RadixSpline* lineage (Kraska, Kipf, MIT/TUM); GPU LSM and key-value stores for analytics; and integration into GPU DBMSs (HeavyDB/OmniSci lineage, *Crystal* primitives, Boncz/Neumann-adjacent vectorized-to-GPU work). *(frontier — verify)* 2025–2026 work targets multi-GPU and CXL/unified-memory indexes and disaggregated HBM. Benchmarks increasingly report energy-per-query alongside throughput.

## 8. Future Work
- A unified GPU cost model linking coalescing, divergence, and occupancy to predicted query latency.
- Provably bandwidth-optimal range indexes; tight constants for k-ary vs. learned search.
- Concurrent dynamic indexes with linearizable semantics and graceful resizing on-device.
- Cross-tier (CPU-GPU-CXL-HBM) cooperative indexing with automatic placement.
- Energy-aware index design and multi-GPU sharding with NVLink-aware traversal.

## 9. Key References
- **[SOTA]** S. Ashkiani, M. Farach-Colton, J. D. Owens. *A Dynamic Hash Table for the GPU (SlabHash).* IPDPS, 2018.
- **[SOTA]** M. A. Awad, S. Ashkiani, R. Johnson, M. Farach-Colton, J. D. Owens. *Engineering a High-Performance GPU B-Tree.* PPoPP, 2019.
- **[SOTA]** Z. Yan, Y. Lin, L. Peng, W. Zhang. *Harmonia: A High Throughput B+tree for GPUs.* PPoPP, 2019.
- **[SOTA]** A. Kipf, R. Marcus, A. van Renen, M. Stoian, A. Kemper, T. Kraska, T. Neumann. *RadixSpline: A Single-Pass Learned Index.* aiDM @ SIGMOD, 2020.
- **[Foundational]** M. Pătrașcu, M. Thorup. *Time–Space Trade-Offs for Predecessor Search.* STOC, 2006.
- **[SOTA]** T. Kraska, A. Beutel, E. H. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
