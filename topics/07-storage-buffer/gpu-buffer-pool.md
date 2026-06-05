# GPU/Heterogeneous-Memory Buffer Pools

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/gpu-buffer-pool` · **Status:** open
> **Verification note:** The "Mordred" VLDB 2022 paper is actually titled *Orchestrating Data Placement and Query Execution in Heterogeneous CPU-GPU DBMS* by Yogatama, Gong, and Yu; the §9 title/author list has been corrected.

## 1. Problem Statement
GPU-accelerated query engines must feed data to massively parallel kernels from **small, high-bandwidth GPU memory** (HBM, typically 16–96 GB) while the working set lives in much larger host DRAM (and below that, NVMe). The buffer-management problem: decide which pages/columns/partitions to stage into GPU memory, when to evict them, and how to overlap PCIe/NVLink/CXL transfers with computation, so that the GPU stays compute-bound rather than transfer-bound. Unlike a CPU buffer pool, the cost model is dominated by **interconnect bandwidth asymmetry** (HBM ≫ NVLink/CXL ≫ PCIe) and by the fact that a page's value depends on the *query plan's parallel access pattern*, not just recency.

Variants:
- **Decision:** Given a plan and HBM budget $k$, can all kernels be served with transfer time hidden under compute? (Feasibility of overlap scheduling.)
- **Optimization:** Minimize total data movement (or maximize achieved GPU throughput) over a query/workload.
- **Online:** Admit/evict GPU-resident pages without knowing future operators.

## 2. Mathematical Foundations
Treat GPU memory as a cache of size $k$ over a universe of pages, but with a **two-resource** cost: transfer bytes over a link of bandwidth $\beta$ and compute time $\tau$ on the GPU. The achievable runtime is bounded below by the *roofline*: $\text{time} \ge \max(\,\text{bytes}/\beta,\ \text{flops}/P\,)$ where $P$ is peak GPU throughput; the operational intensity $I=\text{flops}/\text{bytes}$ determines which term binds. Staging decisions trade movement against recompute/recompression.

The replacement core is again weighted caching (LRU $k$-competitive, randomized $O(\log k)$), but with **non-uniform fetch costs** (different links) and **batch/coalesced fetches** (a kernel needs many pages simultaneously, so the relevant object is a *set*, making this closer to *generalized caching / set-cover-flavored* admission). Overlap scheduling is a **two-machine flow-shop-like** problem (transfer engine ∥ compute engine), where hiding latency is a pipelining/scheduling question; minimizing makespan with precedence (data must arrive before kernel) is NP-hard in general (multiprocessor scheduling with communication delays).

## 3. State of the Art (SOTA)
- **Systems:** *Crystal* (Shanbhag, Madden, Yu, SIGMOD 2020) — tile-based GPU operators assuming data fits in HBM. *HeavyDB/OmniSci*, *BlazingSQL*, *RAPIDS cuDF* — production GPU engines with explicit host↔device staging. *Mordred* (Yogatama, Gong, Yu, VLDB 2022) — a heterogeneous CPU-GPU buffer manager with a semantic-aware caching policy that decides column placement. *G-PICS*, *HippogriffDB* (out-of-core GPU). *Sirius* (frontier, GPU-accelerated engine integrated with a buffer pool) *(frontier — verify)*.
- **Theory:** Roofline model (Williams, Waterman, Patterson, CACM 2009); generalized caching upper bounds (Bansal–Buchbinder–Naor).
- Trend: NVLink/NVLink-C2C and **CXL** reduce (not eliminate) the transfer wall, shifting the optimal staging granularity.

## 4. Upper Bound
For a single GPU-memory cache tier with uniform fetch cost, randomized $O(\log k)$-competitive caching applies. With $d$ distinct link costs, generalized (weighted) caching gives $O(\log k)$ via primal–dual but constants scale with the cost ratio. For the **offline overlap-scheduling** subproblem with a single transfer engine and single compute engine, optimal pipelining is poly-time (Johnson's rule for 2-machine flow shop when no precedence branching); with general DAG precedence it is solved only by ILP/list-scheduling heuristics with a $2-1/m$ approximation for makespan. Systems-SOTA (Mordred) achieves near-DRAM-bandwidth throughput empirically via semantic caching but without a competitive guarantee.

## 5. Lower Bound
Online deterministic caching of GPU pages is $\Omega(k)$-competitive; randomized $\Omega(\log k)$. Makespan minimization with communication delays / precedence is **NP-hard** and even hard to approximate within better than $4/3$ for general DAGs (multiprocessor scheduling lower bounds). Information-theoretically, if operational intensity $I < P/\beta$ the workload is **provably transfer-bound** regardless of caching policy — no buffer manager can beat the bytes/$\beta$ roofline floor; this is a hard physical lower bound on achievable speedup.

## 6. The Gap
The gap is wide and genuinely open. We have (a) tight caching bounds for the idealized single-tier cache, and (b) roofline floors, but **no unified competitive model** that couples set-structured batch fetches, multiple link bandwidths, and transfer/compute overlap. Empirically, semantic policies (Mordred) beat recency/frequency heuristics, yet there is no theory characterizing how far they sit from the movement-optimal schedule. Closing it needs an online model where the "cache miss" cost is a *scheduling* cost (delayed kernel), not a fixed fetch cost.

## 7. Current Research (as of June 2026)
- **CXL-attached GPU memory pooling** and unified virtual memory making page placement implicit but cost-asymmetric *(frontier — verify)*.
- Learned/cost-model-driven column placement extending Mordred's semantic caching *(frontier — verify)*.
- GPU-resident compressed formats so HBM holds more (couples to recompression scheduling).
- Multi-GPU NVLink topologies where placement becomes a graph-partitioning problem across devices.
- Groups: MIT DSAIL (Madden, Shanbhag), NAU/UC (Gowanlock), TUM (Heimel/Leis lineage), NVIDIA RAPIDS, CMU.

## 8. Future Work
- A competitive theory for batch/overlap-aware GPU caching.
- Joint optimization of plan, placement, and on-GPU compression under an HBM budget.
- Buffer pools that span CPU-DRAM, HBM, and CXL memory with a single cost-aware policy.
- Spilling semantics for GPU operators when intermediate results exceed HBM (links to memory-pressure spilling).

## 9. Key References
- **[Foundational]** Williams, Waterman, Patterson. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)
- **[SOTA]** Shanbhag, Madden, Yu. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics (Crystal).* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380595)
- **[SOTA]** Yogatama, Gong, Yu. *Orchestrating Data Placement and Query Execution in Heterogeneous CPU-GPU DBMS (Mordred).* VLDB, 2022. — [DOI](https://doi.org/10.14778/3551793.3551809)
- **[SOTA]** Bansal, Buchbinder, Naor. *Randomized Competitive Algorithms for Generalized Caching.* STOC/SICOMP, 2008/2012. — [DOI](https://doi.org/10.1137/090779000)
- **[Survey]** Breß, Heimel, Siegmund, Bellatreche, Saake. *GPU-Accelerated Database Systems: Survey and Open Challenges.* TLDKS, 2014. — [DOI](https://doi.org/10.1007/978-3-662-45761-0_1)

## 10. Worked Example

A GPU kernel scans a column of $4$ GB. PCIe link bandwidth $\beta = 16$ GB/s; GPU peak $P = 10$ Tflop/s. The scan does $2$ flops/byte, so total flops $= 2 \times 4\times10^9 = 8\times10^9$.

Roofline floor:
$$\text{time} \ge \max\!\Big(\tfrac{\text{bytes}}{\beta},\ \tfrac{\text{flops}}{P}\Big) = \max\!\Big(\tfrac{4}{16}\text{ s},\ \tfrac{8\times10^9}{10\times10^{12}}\text{ s}\Big) = \max(0.25,\ 0.0008) = 0.25 \text{ s}.$$

Operational intensity $I = 2$ flop/byte versus the machine balance $P/\beta = 10000/16 = 625$ flop/byte. Since $I \ll P/\beta$, the workload is **provably transfer-bound**: no buffer/caching policy can beat $0.25$ s while the data must cross PCIe each run.

The buffer manager's leverage is *reuse*. If this column is staged once into HBM ($\beta_{\text{HBM}} \approx 2000$ GB/s) and reused across $5$ queries, four of those runs pay $4/2000 = 0.002$ s instead of $0.25$ s — a $\sim 100\times$ drop. This is exactly why GPU caching value depends on the plan's access pattern, not just recency.

---
*Part of the [DBMS Research catalog](../../README.md).*
