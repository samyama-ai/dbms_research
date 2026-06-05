# GPU memory management for spilling queries

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/gpu-memory-spilling` · **Status:** empirically-open

## 1. Problem Statement
GPU device memory is small (tens of GB) relative to working-set sizes of analytic queries. When a query's inputs or **intermediate results** (hash tables, sort runs, materialized join outputs) exceed device capacity $M$, the engine must **spill** to host (CPU) memory or storage across the PCIe/NVLink interconnect. The problem: schedule device-memory allocation and host spill so the query completes **without thrashing** — i.e., without repeatedly evicting and re-fetching data over the slow interconnect such that throughput collapses below CPU-only execution.

- **Optimization variant (primary):** minimize total interconnect traffic (or query time) given device capacity $M$, interconnect bandwidth $B$, and a DAG of operators with intermediate sizes.
- **Decision variant:** given $M$ and a plan, can it execute with at most $k$ bytes of spill traffic (or zero spill)?
- **Online variant:** intermediate sizes are unknown until produced (cardinality misestimation); minimize spill competitively against an offline oracle that knows the sizes.

## 2. Mathematical Foundations
This is **external-memory / I/O-complexity** (Aggarwal–Vitter) with the GPU as "fast memory" of size $M$ and PCIe as the "disk." A computation reading $N$ bytes costs $\Omega(N/B)$ transfers; sorting in this model is $\Theta(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/Os, and hash join is $\Theta(N/B)$ if the build side fits, otherwise it incurs **recursive partitioning** rounds $\lceil \log_{M} (\text{build size}) \rceil$ — the GPU analogue of Grace-hash partitioning.

The eviction subproblem is **paging/caching**: choosing which device buffers to evict is weighted caching, with **Belady's MIN** (evict the buffer reused farthest in the future) optimal offline, and LRU/CLOCK $k$-competitive online. Thrashing is precisely the **working-set-exceeds-capacity** regime of Denning: when the live intermediate set $W$ exceeds $M$, the page-fault (spill) rate jumps discontinuously. Formally, query time $\approx \max(\text{compute}, \text{spill-bytes}/B)$; the goal is to keep spill-bytes such that the interconnect term doesn't dominate.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **NVIDIA RAPIDS cuDF / Dask-cuDF / Spark-RAPIDS** implement out-of-core operators and a **spill manager** (device → pinned host → disk) with LRU-style eviction of cached columns. **HeavyDB** and **BlazingSQL** support larger-than-GPU scans via chunked streaming. **CUDA Unified Memory (UVM)** with oversubscription provides automatic page migration (driver-managed paging) as a baseline, often outperformed by explicit management.
- **Out-of-core join/sort:** partitioned hash joins that size partitions to fit $M$ (Sioulas et al., ICDE 2019 "Hardware-conscious Hash-Joins on GPUs"; Paul et al.), and external GPU sort.
- **Heterogeneous (CPU+GPU) co-processing:** ship overflow to the CPU rather than spilling (HetExchange / Periscope, Chrysogelos et al., VLDB 2019) — co-design that avoids round-trips.

## 4. Upper Bound
In the external-memory model, the spill-optimal hash join completes in $O(N/B)$ transfers when the build side fits in $M$, and $O(\frac{N}{B}\log_{M}(\text{build}))$ with recursive partitioning otherwise; sort-merge spills in $O(\frac{N}{B}\log_{M/B}\frac{N}{B})$ — these are I/O-optimal upper bounds. For eviction, **Belady MIN** is offline-optimal and gives the minimum possible spill traffic for a fixed access sequence; LRU is **$k$-competitive** and resource-augmented LRU with $(1+\varepsilon)$ extra memory is **$O(1/\varepsilon)$-competitive** (Sleator–Tarjan), bounding online spill. With accurate intermediate-size estimates, partition-sizing to exactly fill $M$ attains the lower bound up to constants.

## 5. Lower Bound
The Aggarwal–Vitter bounds are **tight lower bounds** in the I/O model: sorting and permuting $N$ elements require $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ transfers, so no out-of-core GPU sort/sort-based operator can avoid that interconnect traffic. Online, **no deterministic eviction policy beats $k$-competitive** and no randomized policy beats $\Omega(\log k)$ (the caching lower bounds), so thrashing under adversarial reuse is unavoidable without future knowledge. The practical lower bound is **interconnect bandwidth itself**: any plan touching $S$ bytes of spilled data pays $\ge S/B$ time, and on PCIe ($B\sim$ tens of GB/s) this can be orders of magnitude below device-memory bandwidth — the cliff that defines "thrashing."

## 6. The Gap
The I/O-complexity theory is closed (tight bounds), but **systems remain empirically open** because the model assumes intermediate sizes and access sequences are known. In reality: (1) **cardinality misestimation** means partition sizes are wrong, causing partitions to overflow $M$ mid-flight and trigger unplanned recursive spills; (2) UVM's automatic paging thrashes precisely when the working set marginally exceeds $M$ (page-fault storms), while explicit management requires accurate sizing the optimizer can't provide; (3) the choice between **spill-to-host vs offload-to-CPU vs recursive-partition** is plan-dependent and lacks a unified cost model. Closing the gap needs adaptive, **size-oblivious** out-of-core operators with competitive spill guarantees under online cardinality, plus interconnect-aware (NVLink/CXL vs PCIe) cost models.

## 7. Current Research (as of June 2026)
- Adaptive out-of-core operators that re-partition on overflow without a global restart, and spill-aware cardinality feedback loops in Spark-RAPIDS / cuDF *(frontier — verify)*.
- **Grace-Hopper / unified coherent memory (NVLink-C2C, CXL)** changing the spill economics — fast cache-coherent host access narrows the PCIe cliff, prompting re-evaluation of when to spill vs offload *(frontier — verify)*.
- HetExchange-style CPU+GPU co-execution that routes overflow to the CPU pipeline (Chrysogelos, Ailamaki / EPFL DIAS) *(frontier — verify)*.
- Learned spill/eviction policies and Belady-imitation caching for GPU buffer managers *(frontier — verify)*.

## 8. Future Work
- Size-oblivious out-of-core join/sort with proven competitive spill traffic under online cardinality.
- Interconnect-topology-aware cost models (PCIe vs NVLink vs CXL vs unified memory) integrated into the optimizer.
- Cooperative device-buffer management across concurrent queries (multi-tenant GPU memory).
- Belady-imitation / learned eviction with regret bounds for analytic access patterns.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** L. Belady. *A Study of Replacement Algorithms for a Virtual-Storage Computer.* IBM Systems Journal, 1966. (MIN / optimal eviction.) — [DOI](https://doi.org/10.1147/sj.52.0078)
- **[SOTA]** P. Sioulas, P. Chrysogelos, M. Karpathiotakis, R. Appuswamy, A. Ailamaki. *Hardware-conscious Hash-Joins on GPUs.* ICDE, 2019. — [DOI](https://doi.org/10.1109/ICDE.2019.00068)
- **[SOTA]** P. Chrysogelos, M. Karpathiotakis, R. Appuswamy, A. Ailamaki. *HetExchange: Encapsulating Heterogeneous CPU-GPU Parallelism in JIT Compiled Engines.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3303753.3303760)
- **[Foundational]** D. Sleator, R. Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. (Competitive caching / spill.) — [DOI](https://doi.org/10.1145/2786.2793)
- **[Survey]** S. Breß, et al. *GPU-Accelerated Database Systems: Survey and Open Challenges.* TLDKS, 2014. — [DOI](https://doi.org/10.1007/978-3-662-45761-0_1)

## 10. Worked Example

A GPU buffer holds $M = 3$ column chunks; PCIe bandwidth $B$. A query accesses chunks in the sequence
$$1,\,2,\,3,\,4,\,1,\,2,\,5,\,1,\,2,\,3,\,4,\,5.$$

**Belady MIN (offline optimal):** on each miss, evict the resident chunk reused farthest in the future. Trace (cache shown after each access): faults at $1,2,3$ (cold), then $4$ evicts $3$ (next use of $3$ is latest) → $\{1,2,4\}$; $1,2$ hit; $5$ evicts $4$ → $\{1,2,5\}$; $1,2$ hit; $3$ evicts $5$ → $\{1,2,3\}$; $4$ evicts $3$ → $\{1,2,4\}$; $5$ evicts $4$ → $\{1,2,5\}$. Total **8 faults**.

**LRU on the same trace** faults additionally because it evicts the least-recently-used rather than the farthest-future chunk: it gives **10 faults** here.

Each fault re-fetches one chunk across PCIe, so spill time $\approx \text{faults} \times (\text{chunk}/B)$. The ratio $10/8 = 1.25$ is well within LRU's worst-case $k$-competitiveness ($k=M=3$). The lesson: when the live working set ($\{1,2\}$ plus a rotating third) marginally exceeds $M$, every extra fault is a full interconnect round-trip — the thrashing cliff.

---
*Part of the [DBMS Research catalog](../../README.md).*
