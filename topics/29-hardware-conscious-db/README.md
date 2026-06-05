# Hardware-Conscious Databases

Hardware-conscious database research co-designs data structures, algorithms, and query engines with the underlying silicon: GPUs and FPGAs, wide SIMD lanes, deep cache and NUMA hierarchies, byte-addressable persistent memory, RDMA fabrics, and near-data/computational storage. The recurring tension is that raw device throughput keeps outrunning the ability of query engines to feed it — bounded by memory bandwidth, interconnect transfers, synchronization, and the difficulty of expressing relational operators in models that fit massively parallel or heterogeneous hardware.

This catalog collects 30 research-grade open problems at the intersection of theory (complexity, parallel cost models, bounds, expressiveness) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [PCIe/interconnect transfer lower bounds for GPU joins](./gpu-join-transfer-bounds.md) | open | Tight bounds on host-device data movement required to evaluate joins when working sets exceed GPU memory. |
| [Heterogeneous CPU-GPU query plan optimization](./cpu-gpu-plan-optimization.md) | empirically-open | Cost-based placement of operators across CPU and GPU under transfer, memory, and concurrency constraints. |
| [Provably work-efficient parallel hash joins](./parallel-hash-join-work-efficiency.md) | partially-solved | Hash-join algorithms that are simultaneously work-optimal and depth-optimal on the PRAM/MPC-style GPU model. |
| [SIMD-vectorizable query compilation](./simd-query-compilation.md) | empirically-open | Automatically generating fully vectorized operator code with control-flow divergence handled across data types. |
| [Cache-oblivious vs cache-conscious join tradeoff](./cache-oblivious-join-tradeoff.md) | partially-solved | Whether cache-oblivious joins can match hand-tuned cache-conscious partitioning across diverse cache hierarchies. |
| [Optimal radix partitioning fan-out](./radix-partition-fanout.md) | partially-solved | Choosing partitioning passes and fan-out to minimize TLB/cache misses given hardware parameters and data skew. |
| [NUMA-aware operator scheduling](./numa-aware-scheduling.md) | empirically-open | Placement and migration of data and threads to minimize remote-socket traffic for analytical operators. |
| [Crash-consistent persistent-memory indexes](./pmem-crash-consistent-index.md) | partially-solved | Tree/hash indexes on byte-addressable NVM that are durable, lock-free, and minimize flush/fence overhead. |
| [Persistent-memory write-amplification bounds](./pmem-write-amplification-bounds.md) | open | Lower bounds on cache-line flushes and media writes needed for durable updates to ordered structures. |
| [RDMA-optimal distributed join algorithms](./rdma-optimal-joins.md) | partially-solved | Joins over RDMA that minimize round trips and bytes given one-sided verbs and limited registered memory. |
| [One-sided RDMA data structures with consistency](./rdma-one-sided-structures.md) | empirically-open | Remotely accessible indexes updated via one-sided verbs while preserving lock-freedom and correctness. |
| [FPGA query operator synthesis from SQL](./fpga-operator-synthesis.md) | empirically-open | Compiling relational operators to pipelined FPGA dataflow without per-query bitstream reconfiguration cost. |
| [Partial reconfiguration for query acceleration](./fpga-partial-reconfiguration.md) | open | Scheduling FPGA partial-reconfiguration regions to amortize bitstream loading across changing workloads. |
| [Near-data processing operator pushdown](./near-data-pushdown.md) | empirically-open | Deciding which operators to push into computational storage given limited in-storage compute and bandwidth gain. |
| [Computational-storage cost model and bounds](./computational-storage-cost-model.md) | open | A predictive model for when in-storage filtering/aggregation beats host execution under interface limits. |
| [Memory-bandwidth-bound scan optimization](./bandwidth-bound-scan.md) | empirically-open | Turning compressed columnar scans into bandwidth-saturating kernels rather than compute- or latency-bound ones. |
| [SIMD-friendly compression codecs](./simd-compression-codecs.md) | partially-solved | Codecs decodable with vector instructions at memory bandwidth while retaining strong compression ratios. |
| [Lock-free synchronization for many-core engines](./manycore-lockfree-sync.md) | empirically-open | Concurrency primitives that scale to hundreds of cores without contention collapse on relational structures. |
| [GPU group-by and aggregation under skew](./gpu-aggregation-skew.md) | empirically-open | Atomics-free, skew-resilient grouped aggregation that keeps GPU lanes utilized under heavy key skew. |
| [Worst-case-optimal joins on parallel hardware](./wcoj-parallel-hardware.md) | open | Realizing worst-case-optimal join bounds on SIMD/GPU models without losing the theoretical guarantee. |
| [Heterogeneous-memory data placement (HBM/DRAM/NVM)](./tiered-memory-placement.md) | empirically-open | Placing hot/cold data across HBM, DRAM, and persistent tiers to optimize a cost-per-access objective. |
| [Energy-efficient query execution models](./energy-aware-execution.md) | open | Cost models and plans that optimize joules-per-query, not just latency, across heterogeneous accelerators. |
| [GPU memory management for spilling queries](./gpu-memory-spilling.md) | empirically-open | Managing device memory and host spill for queries whose intermediates exceed GPU capacity without thrashing. |
| [Vectorized vs compiled execution unification](./vectorized-vs-compiled.md) | partially-solved | A principled model predicting when vectorized interpretation beats data-centric compilation on given hardware. |
| [Persistent-memory logging and recovery](./pmem-logging-recovery.md) | partially-solved | Exploiting byte-addressable durability to cut logging overhead while bounding recovery time and write traffic. |
| [Smart-NIC / DPU offload of DB operators](./smartnic-dpu-offload.md) | empirically-open | Offloading filtering, partitioning, or coordination to programmable NICs/DPUs with a clear cost-benefit boundary. |
| [Cache-conscious tree layout lower bounds](./cache-conscious-tree-bounds.md) | partially-solved | Bounds on cache misses for search-tree layouts across unknown or varying cache-line and hierarchy parameters. |
| [Accelerator-aware cardinality and cost estimation](./accelerator-cost-estimation.md) | open | Estimating operator cost on GPUs/FPGAs where runtime depends nonlinearly on occupancy, divergence, and transfers. |
| [Coherence-free CXL-shared-memory databases](./cxl-shared-memory-db.md) | empirically-open | Data structures and transactions over CXL-attached pooled/shared memory with weak or no hardware coherence. |
| [Portable performance across accelerator generations](./portable-accelerator-performance.md) | open | Operator code and tuning that retain near-peak performance across GPU/FPGA generations without manual rewrites. |

---
[Back to taxonomy](../../TAXONOMY.md)
