# GPU-Accelerated OLAP Operators

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/gpu-olap-operators` · **Status:** empirically-open

## 1. Problem Statement
Given columnar OLAP workloads (scan with predicate, equi-join, group-by aggregation) and a heterogeneous system with a CPU, host RAM, and one or more GPUs connected by an interconnect (PCIe, NVLink, or unified memory), design operators and data-placement strategies that make the GPU a *net* win end-to-end. Variants:

- **Optimization:** minimize total query latency/cost including host↔device transfer, not just kernel time.
- **Placement/decision:** decide which operators (or operator sub-ranges) run on GPU vs. CPU, and which columns to cache in device memory, under a fixed VRAM budget.
- **Throughput vs. latency:** maximize tuples/sec under bandwidth and occupancy constraints.

The crux is the **transfer wall**: a GPU may scan/join at TB/s internally, but feeding it over PCIe (tens of GB/s) can erase the advantage. The open problem is when, and via what designs, GPUs robustly beat a well-tuned vectorized CPU engine on real OLAP.

## 2. Mathematical Foundations
Model the device as compute throughput $C$ (lanes × clock) bounded by **device memory bandwidth** $B_{\text{dev}}$ and gated by the **interconnect bandwidth** $B_{\text{pcie}}$. For an operator touching $D$ bytes with arithmetic intensity $I$ (FLOPs or comparisons per byte), the **roofline** predicts attainable performance $\min(C, I\cdot B_{\text{dev}})$ on resident data, but for transient data the ceiling becomes $I\cdot B_{\text{pcie}}$. Net speedup over CPU requires

$$\frac{D/B_{\text{pcie}} + W/C_{\text{gpu}}}{W/C_{\text{cpu}}} < 1,$$

so high **operational intensity** $W/D$ and **data residency** (amortizing transfer across many queries) are necessary. Joins add the difficulty of *irregular*, data-dependent memory access (hash probes → uncoalesced gathers), which destroys the coalescing that GPU bandwidth depends on. Compression raises effective $B_{\text{pcie}}$ by shrinking $D$, trading decode work on-device.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Crystal (Shanbhag, Madden, Yu — SIGMOD 2020) is a library of tile-based GPU primitives showing GPUs win on Star-Schema Benchmark *when data is device-resident*; HeavyDB/OmniSciDB, BlazingSQL, and RAPIDS cuDF are production GPU columnar engines; Proteus and HetExchange (Karpathiotakis/Ailamaki, CWI/EPFL) do CPU+GPU heterogeneous execution.
- **Algorithmic-SOTA:** GPU radix/partitioned hash joins (He et al.; Sioulas et al., ICDE 2019) and GPU sort/scan from CUB/Thrust; "Triton Join" and partitioned joins exploiting **fast interconnects (NVLink, GPUDirect)** to scale beyond VRAM (Lutz et al., SIGMOD 2020/2022).
- Late-materialization + on-GPU decompression to beat the PCIe wall is standard practice.

## 4. Upper Bound
For **device-resident** columnar data, scan and aggregation are bandwidth-bound: $O(D/B_{\text{dev}})$ time, i.e. near-roofline, often 5–20× a CPU socket because $B_{\text{dev}} \gg B_{\text{cpu-mem}}$. Partitioned hash join achieves $O((|R|+|S|)/B_{\text{dev}})$ once partitions are cache/shared-memory resident. With NVLink/GPUDirect, out-of-core joins approach $O(D/B_{\text{nvlink}})$, lifting the practical transfer ceiling by an order of magnitude over PCIe. These are RAM/roofline-model upper bounds, realized empirically for narrow projections and high-selectivity scans.

## 5. Lower Bound
Any operator must move its input: $\Omega(D/B_{\text{pcie}})$ for non-resident data — an unavoidable communication lower bound that caps speedup regardless of compute. Join lower bounds inherit the **AGM bound** on output size and the communication-complexity floor for distributed/partitioned joins. Irregular access in hash probes forfeits coalescing, so achievable bandwidth is provably a fraction of peak (uncoalesced ≈ $1/k$ of coalesced for $k$-way scatter). No model shows GPUs asymptotically dominate CPUs for transfer-bound, low-intensity OLAP — the limit is the interconnect, not the algorithm.

## 6. The Gap
Asymptotics are clear; the gap is **practical and regime-dependent**. GPUs win when (high intensity) ∧ (data resident or compressible) ∧ (regular access); they lose on transfer-bound, low-selectivity, wide-tuple, or pointer-chasing workloads. There is no robust, workload-agnostic GPU OLAP engine that beats a top CPU engine *across the board including transfer*. Closing the gap needs either ubiquitous fast interconnects (NVLink/CXL) or operators whose intensity and compression hide PCIe — plus a cost model that places work correctly.

## 7. Current Research (as of June 2026)
Active directions: (i) exploiting **NVLink/NVSwitch and CXL-attached memory** to dissolve the PCIe wall and enable out-of-core GPU joins (Lutz/Boncz lineage, CWI); (ii) GPU-resident compressed columnar formats with on-device decode; (iii) heterogeneous query optimizers that assign morsels to CPU vs. GPU by predicted intensity (Ailamaki/EPFL, Heimel/Markl/TU Berlin); (iv) multi-GPU and GPU+SSD (GPUDirect Storage) scan pipelines. Frontier: a *general-purpose GPU columnar engine that dominates CPU engines on full TPC-H/DS including transfer and updates* is not yet demonstrated *(frontier — verify)*; CXL 3.0 memory pooling reshaping the placement calculus is early *(frontier — verify)*.

## 8. Future Work
- Cost models that decide CPU/GPU placement per operator under transfer + VRAM constraints with guarantees.
- Operators co-designed with compression so PCIe carries encoded, not raw, columns.
- Exploiting CXL/NVLink coherent memory to retire host↔device copies entirely.
- GPU-accelerated updates/MVCC for HTAP, not just read-only OLAP.

## 9. Key References
- **[SOTA]** Shanbhag, Madden, Yu. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics.* SIGMOD 2020 (Crystal). — [DOI](https://doi.org/10.1145/3318464.3380595)
- **[SOTA]** Sioulas, Chrysogelos, Karpathiotakis, Appuswamy, Ailamaki. *Hardware-Conscious Hash-Joins on GPUs.* ICDE 2019. — [DBLP](https://dblp.org/rec/conf/icde/SioulasCKAA19.html)
- **[SOTA]** Lutz, Breß, Zeuch, Rabl, Markl. *Pump Up the Volume: Processing Large Data on GPUs with Fast Interconnects.* SIGMOD 2020. — [DOI](https://doi.org/10.1145/3318464.3389705)
- **[SOTA]** Chrysogelos, Karpathiotakis, Appuswamy, Ailamaki. *HetExchange: Encapsulating Heterogeneous CPU-GPU Parallelism in JIT Compiled Engines.* VLDB 2019. — [VLDB PDF](http://www.vldb.org/pvldb/vol12/p544-chrysogelos.pdf)
- **[Survey]** Breß, Heimel, Siegmund, Bellatreche, Saake. *GPU-Accelerated Database Systems: Survey and Open Challenges.* TLDKS, 2014. — [DOI](https://doi.org/10.1007/978-3-662-45761-0_1)

## 10. Worked Example

Scan-and-aggregate a column of $D = 4\text{ GB}$, one-shot (non-resident). Suppose $B_{\text{pcie}} = 16\text{ GB/s}$ (PCIe 4.0 x16), $B_{\text{dev}} = 1000\text{ GB/s}$ (HBM), CPU memory bandwidth $B_{\text{cpu}} = 50\text{ GB/s}$. The aggregation is bandwidth-bound (low intensity), so kernel time $\approx D/B_{\text{dev}} = 4/1000 = 4\text{ ms}$, but transfer time $\approx D/B_{\text{pcie}} = 4/16 = 250\text{ ms}$.

GPU end-to-end: $250 + 4 = 254\text{ ms}$. CPU: $D/B_{\text{cpu}} = 4/50 = 80\text{ ms}$. So the **CPU wins** ($80 < 254$) — the PCIe transfer wall dominates, matching the inequality in section 2.

Now amortize: if the column is **device-resident** (cached from a prior query), the transfer term vanishes and GPU time is $4\text{ ms}$ versus $80\text{ ms}$ — a $20\times$ win. Alternatively, $2{:}1$ compression halves transferred bytes to $2\text{ GB}$ ($125\text{ ms}$ transfer), still losing to the CPU, showing residency matters more than compression for low-intensity scans.

---
*Part of the [DBMS Research catalog](../../README.md).*
