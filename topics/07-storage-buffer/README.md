# Storage & Buffer Management

The storage and buffer layer mediates between a DBMS's logical access methods and the
physical memory/storage hierarchy: it decides which pages live in RAM, how data is laid
out and compressed on disk, and how cold data is tiered across DRAM, SSD, and object
storage. Its problems sit at the intersection of online/competitive caching theory and
hard systems engineering, where worst-case bounds, workload-adaptive learning, and
hardware realities (NVMe, persistent memory, NUMA, disaggregation) all collide.

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal Buffer Replacement Under Workload Drift](./adaptive-replacement-drift.md) | open | Designing a replacement policy that provably tracks a non-stationary, drifting reuse distribution without manual tuning. |
| [Tight Competitive Ratio for Weighted Caching with Variable Page Sizes](./weighted-caching-variable-size.md) | partially-solved | Closing the competitive-ratio gap for general caching where pages have both arbitrary sizes and arbitrary fetch costs. |
| [Learned Buffer Eviction with Worst-Case Guarantees](./learned-eviction-guarantees.md) | open | Combining ML-predicted reuse with a fallback that preserves classical competitive bounds. |
| [Buffer Management for Disaggregated Memory](./disaggregated-buffer-pool.md) | empirically-open | Page caching when the buffer pool spans local DRAM and far CXL/RDMA memory with non-uniform latency. |
| [Provably Good Prefetching from Access Sequences](./prefetching-bounds.md) | open | Online prefetching that minimizes stall time with competitive guarantees against an offline optimal. |
| [Cost-Aware Caching Across DRAM/SSD/Object Tiers](./multi-tier-cost-caching.md) | partially-solved | Replacement that jointly optimizes hit rate and dollar/byte-movement cost across a deep storage hierarchy. |
| [Optimal Page Layout for Mixed OLTP/OLAP Access](./hybrid-page-layout.md) | open | Choosing row/column/PAX-style intra-page layout to minimize total I/O under a mixed workload. |
| [Compression-Aware Buffer Accounting](./compression-aware-buffering.md) | empirically-open | Managing a buffer pool whose effective capacity varies with per-page compression ratios. |
| [Hot/Cold Classification with Bounded Misclassification](./hot-cold-classification.md) | open | Online tiering that bounds the cost of mislabeling pages as hot or cold under shifting skew. |
| [Buffer Pool Sizing Under Multi-Tenant Contention](./multitenant-buffer-sizing.md) | partially-solved | Allocating shared buffer capacity across tenants to maximize aggregate utility with fairness. |
| [Self-Tuning Page Size Selection](./adaptive-page-size.md) | empirically-open | Choosing physical page granularity online to balance read amplification, fill factor, and metadata cost. |
| [Competitive Caching with Delayed Hits](./delayed-hits-caching.md) | partially-solved | Replacement theory when concurrent misses to the same page incur aggregate-latency costs, not unit costs. |
| [Buffer Management for Log-Structured / LSM Stores](./lsm-buffer-management.md) | open | Caching and block-cache policy that accounts for compaction-induced churn and write amplification. |
| [Write-Back Scheduling to Minimize Stall and Wear](./writeback-scheduling.md) | open | Ordering dirty-page flushes to jointly minimize foreground stalls and SSD write amplification/wear. |
| [Information-Theoretic Limits of Page Compression](./compression-limits-pages.md) | partially-solved | Lower bounds on random-access-preserving compression of database pages. |
| [Optimal Block-Granularity for Random vs Sequential I/O](./block-granularity-tradeoff.md) | open | Choosing transfer/block size to minimize expected I/O time across an unknown read mix. |
| [Caching with Predictions: Robustness vs Consistency](./caching-with-predictions.md) | partially-solved | Pareto frontier between trusting an ML oracle and degrading gracefully when it errs. |
| [Buffer Replacement for Index vs Heap Pages](./typed-page-replacement.md) | empirically-open | Differentiating eviction value of internal index nodes, leaves, and heap pages within one pool. |
| [NVM-Aware Buffer Management and Page Placement](./nvm-buffer-placement.md) | empirically-open | Exploiting byte-addressable persistent memory as a buffer tier with asymmetric read/write cost. |
| [GPU/Heterogeneous-Memory Buffer Pools](./gpu-buffer-pool.md) | open | Managing pages across host DRAM and limited high-bandwidth GPU memory for accelerated query engines. |
| [Scan-Resistant Replacement with Optimality Bounds](./scan-resistant-replacement.md) | partially-solved | Policies provably immune to sequential-flooding while retaining near-LRU performance on reuse. |
| [Cardinality-Aware Prefetch Depth Control](./prefetch-depth-control.md) | open | Setting prefetch aggressiveness from cardinality/selectivity estimates to avoid cache pollution. |
| [Compressed Page Recompression Scheduling](./recompression-scheduling.md) | open | Deciding when to re-encode pages between light/heavy compression as access patterns evolve. |
| [Buffer Management Under Strict Memory Pressure (Spilling)](./memory-pressure-spilling.md) | empirically-open | Coordinating buffer-pool eviction with operator memory grants and spill-to-disk decisions. |
| [Online Working-Set Estimation for Auto-Sizing](./working-set-estimation.md) | partially-solved | Estimating the resident working set in sublinear space to drive elastic buffer allocation. |
| [Page Clustering / Co-Location for Locality](./page-coclustering.md) | open | Physically clustering correlated tuples/pages to maximize buffer locality under query workloads. |
| [Snapshot/MVCC Version Page Caching](./mvcc-version-caching.md) | open | Replacement that accounts for version chains and snapshot visibility across concurrent transactions. |
| [Cloud Storage Caching with Egress Cost](./cloud-egress-caching.md) | empirically-open | Local-cache admission/eviction that minimizes cloud-storage request and egress billing, not just misses. |
| [Encrypted/Oblivious Buffer Access Patterns](./oblivious-buffer-access.md) | open | Hiding page-access patterns in the buffer pool against side-channel adversaries with low overhead. |
| [End-to-End Learned Storage-Layout Co-Design](./learned-layout-codesign.md) | open | Jointly learning compression, layout, and tiering decisions to minimize total query cost. |

---
*Part of the [DBMS Research catalog](../../TAXONOMY.md).*
