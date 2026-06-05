# Main-Memory Databases

Main-memory (in-memory) database systems keep the primary copy of data in RAM,
eliminating the buffer-manager indirection and disk-I/O bottlenecks that dominate
classic disk-based engines. This shifts the performance frontier onto cache behavior,
memory bandwidth, NUMA topology, concurrency-control overhead, lock-free/latch-free
data-structure design, and the question of how to provide durability and fast recovery
when the canonical state lives in volatile memory. The problems below span both the
theory (complexity and lower bounds for concurrent/persistent structures) and the
systems engineering (index design, NUMA placement, checkpointing, NVM/CXL durability)
studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT.

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal Cache-Conscious In-Memory Index](./cache-conscious-index-optimality.md) | open | Whether a single in-memory ordered-index design can be simultaneously optimal for point, range, and update workloads across cache hierarchies. |
| [Lower Bounds for Lock-Free Ordered Maps](./lock-free-ordered-map-lower-bounds.md) | open | Tight time/space lower bounds for linearizable lock-free ordered maps supporting range scans. |
| [Wait-Free Range Scans on Concurrent Trees](./wait-free-range-scans.md) | open | Whether consistent range scans over a concurrently-updated in-memory tree can be made wait-free with bounded overhead. |
| [NUMA-Optimal Data Placement](./numa-optimal-data-placement.md) | open | Computing data and thread placement that minimizes remote-memory traffic for a given workload on a NUMA machine. |
| [Adaptive Radix Tree Worst-Case Bounds](./adaptive-radix-tree-bounds.md) | partially-solved | Characterizing worst-case space and probe complexity of adaptive-node-fanout radix tries under adversarial keys. |
| [Instant Recovery for IMDBs](./instant-recovery-imdb.md) | partially-solved | Recovering an in-memory database to a transactionally-consistent, queryable state in time independent of database size. |
| [Low-Overhead Consistent Checkpointing](./consistent-checkpointing-overhead.md) | partially-solved | Taking transaction-consistent checkpoints of a multi-GB in-memory store with negligible foreground latency impact. |
| [Persistent Memory Lock-Free Indexes](./persistent-memory-lock-free-index.md) | empirically-open | Designing crash-consistent, lock-free indexes on byte-addressable NVM with provable recovery and low flush overhead. |
| [Optimal Memory Reclamation Scheme](./safe-memory-reclamation.md) | open | A memory reclamation method that is simultaneously lock-free, bounded-garbage, and low-overhead for concurrent indexes. |
| [Hybrid Row/Column In-Memory Layout](./hybrid-row-column-layout.md) | open | Choosing and adapting per-fragment physical layout in an HTAP in-memory store to serve mixed OLTP/OLAP optimally. |
| [Concurrency Control Without Central Bottleneck](./scalable-concurrency-control.md) | partially-solved | A concurrency-control protocol whose throughput scales linearly to hundreds of cores without a global serialization point. |
| [Timestamp Allocation at Scale](./scalable-timestamp-allocation.md) | partially-solved | Allocating monotonic transaction timestamps to many-core MVCC engines without a shared-counter scalability wall. |
| [In-Memory MVCC Version Storage](./mvcc-version-storage.md) | open | Version-chain organization and garbage collection that bounds long-running-reader memory blowup without scan-time penalties. |
| [Latch-Free B-tree With Range Locks](./latch-free-btree-range-locks.md) | partially-solved | Combining latch-free B-tree traversal with phantom-preventing range locking at in-memory speed. |
| [Hardware Transactional Memory for Indexes](./htm-for-in-memory-indexes.md) | empirically-open | Whether HTM can deliver robust, abort-resilient synchronization for concurrent in-memory indexes in practice. |
| [Group Commit vs Latency Tradeoff](./group-commit-latency-tradeoff.md) | partially-solved | Optimal batching of log flushes to maximize throughput while bounding tail commit latency in an IMDB. |
| [Compression for In-Memory Indexes](./in-memory-index-compression.md) | open | Compressing in-memory index structures while preserving O(log n) random access and update performance. |
| [Memory-Bandwidth-Optimal Scans](./bandwidth-optimal-scans.md) | open | Scan and predicate-evaluation kernels that provably saturate memory bandwidth across NUMA nodes. |
| [Cardinality-Aware Index Adaptation](./adaptive-index-structure.md) | empirically-open | Online morphing of index structure (cracking/learned/tree) as workload and data distribution shift. |
| [Durability for Non-Volatile-Free IMDBs](./durability-volatile-only.md) | partially-solved | Providing ACID durability using only volatile memory plus remote replicas, with bounded data-loss windows. |
| [Tail-Latency Bounds Under Compaction](./tail-latency-compaction.md) | empirically-open | Bounding tail latency of in-memory stores during background reorganization, GC, and checkpointing. |
| [Cache-Coherence-Aware Synchronization](./cache-coherence-aware-sync.md) | open | Synchronization primitives that minimize coherence-protocol traffic for write-heavy concurrent structures. |
| [CXL-Disaggregated In-Memory Database](./cxl-disaggregated-imdb.md) | empirically-open | Index and transaction design for memory-semantic disaggregated (CXL) memory with non-uniform far-memory latency. |
| [Provably-Correct Recovery Verification](./recovery-correctness-verification.md) | open | Formally verifying that an IMDB's logging+checkpoint+replay recovers an externally-consistent state. |
| [Optimal Log Record Granularity](./log-granularity-optimality.md) | open | Choosing logical/physiological/command logging granularity to minimize log volume and replay time jointly. |
| [Skew-Resilient Partitioned IMDB](./skew-resilient-partitioning.md) | partially-solved | Partitioned single-threaded-per-core execution that remains performant under dynamic data and access skew. |
| [In-Memory Index for Variable-Length Keys](./variable-length-key-index.md) | open | An in-memory ordered index with worst-case guarantees for arbitrary-length string keys and prefix queries. |
| [Energy-Proportional In-Memory Storage](./energy-proportional-imdb.md) | open | Keeping a large in-memory database both DRAM-refresh-energy-efficient and instantly available. |
| [Concurrent Resizable Hash Tables](./concurrent-resizable-hashing.md) | partially-solved | Lock-free hash tables that resize without stalling readers/writers and with bounded amortized cost. |
| [Snapshot Isolation Without Version Explosion](./snapshot-isolation-version-bound.md) | open | Providing serializable snapshot isolation in memory with provably bounded version-store growth. |

---
*Back to [Taxonomy](../../TAXONOMY.md).*
