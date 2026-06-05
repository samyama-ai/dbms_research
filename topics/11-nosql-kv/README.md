# NoSQL & Key-Value Stores

This topic studies the data models, storage engines, and distribution mechanisms behind NoSQL and key-value systems: how keys map to nodes (hash vs. range partitioning), how data is rebalanced as clusters grow, how LSM-tree compaction is scheduled under read/write/space tradeoffs, how secondary and global indexes stay consistent with primary data, and how applications dial consistency, latency, and availability. The open problems span both theory (complexity and lower bounds for rebalancing, indexing, and consistency) and systems (compaction scheduling, hotspot mitigation, multi-tenant isolation, and verifiable correctness at scale).

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal LSM Compaction Scheduling](./lsm-compaction-scheduling.md) | open | Choosing when and which SSTables to merge to jointly minimize read, write, and space amplification under a dynamic workload. |
| [Provably Minimal-Movement Rebalancing](./minimal-movement-rebalancing.md) | partially-solved | Lower bounds and optimal algorithms for the amount of data moved when a sharded ring adds or removes nodes. |
| [Adaptive Range vs Hash Partitioning](./adaptive-range-hash-partitioning.md) | open | Automatically choosing and switching between range and hash partitioning per key-space region based on workload skew. |
| [Online Hot-Shard Splitting](./online-hot-shard-splitting.md) | empirically-open | Detecting and splitting hot shards online without violating latency SLOs or losing causal ordering. |
| [Tunable Consistency Cost Model](./tunable-consistency-cost-model.md) | open | A principled model that predicts staleness and latency for arbitrary quorum (R,W,N) and consistency-level choices. |
| [Bounded-Staleness Read Guarantees](./bounded-staleness-guarantees.md) | partially-solved | Giving precise, enforceable bounds on read staleness under eventual/tunable consistency with realistic clocks. |
| [Global Secondary Index Consistency](./global-secondary-index-consistency.md) | open | Keeping distributed global secondary indexes consistent with base data without distributed transactions. |
| [Compaction-Aware Read Cost Bounds](./compaction-aware-read-bounds.md) | partially-solved | Tight bounds on worst-case point/range read cost as a function of compaction policy and key distribution. |
| [Hash Ring Load Balance Theory](./hash-ring-load-balance.md) | partially-solved | Closing the gap between consistent-hashing variants and provably optimal load balance with bounded virtual nodes. |
| [Workload-Adaptive Bloom Filter Tuning](./adaptive-bloom-filter-tuning.md) | empirically-open | Per-level, per-key-range allocation of Bloom/filter bits to minimize total memory at fixed false-positive cost. |
| [Range Query Filters for LSM](./range-query-lsm-filters.md) | open | Compact, mergeable filters that prune SSTables for arbitrary range predicates, not just point lookups. |
| [Cross-Shard Secondary Index Joins](./cross-shard-index-joins.md) | open | Efficiently answering queries that join a secondary index to base rows scattered across many shards. |
| [Consistency-Aware Caching](./consistency-aware-caching.md) | partially-solved | Client/edge caches that respect a chosen consistency level without per-request coordination. |
| [Verifiable KV Store Correctness](./verifiable-kv-correctness.md) | partially-solved | Cryptographic and runtime verification that a remote KV store returns fresh, complete, untampered results. |
| [Multi-Tenant Compaction Isolation](./multitenant-compaction-isolation.md) | empirically-open | Scheduling shared compaction/IO so one tenant's writes cannot starve another's reads. |
| [Optimal Tombstone Garbage Collection](./tombstone-garbage-collection.md) | open | Deciding when deletes/tombstones can be safely dropped under tunable consistency and TTLs. |
| [Skew-Resilient Key Distribution](./skew-resilient-key-distribution.md) | open | Partitioning schemes that bound load even under adversarial or heavy-tailed key popularity. |
| [Elastic Rebalancing Under Churn](./elastic-rebalancing-churn.md) | empirically-open | Stable rebalancing when membership changes faster than data movement can complete. |
| [Multi-Key Atomicity Without 2PC](./multikey-atomicity-no-2pc.md) | partially-solved | Atomic multi-key operations across shards at lower cost than two-phase commit while bounding anomalies. |
| [Compaction Write-Stall Theory](./compaction-write-stall-theory.md) | open | Characterizing and provably avoiding write stalls/backpressure cliffs in LSM ingestion. |
| [Tiered-Storage Compaction Placement](./tiered-storage-compaction.md) | empirically-open | Placing SSTable levels across memory/SSD/object storage to minimize cost at a latency target. |
| [Secondary Index Selection for KV](./secondary-index-selection.md) | open | Automatically selecting which secondary indexes to materialize given a KV workload and write budget. |
| [Causal Consistency at Scale](./causal-consistency-at-scale.md) | partially-solved | Tracking and enforcing causality with metadata that does not grow with the number of clients or keys. |
| [Range-Partition Boundary Learning](./range-boundary-learning.md) | empirically-open | Learning and maintaining split points for range partitions that adapt to evolving key distributions. |
| [Hybrid Hash-Range Index Structures](./hybrid-hash-range-index.md) | open | A single access method that serves both point and range queries efficiently under partitioning. |
| [Read-Repair Convergence Bounds](./read-repair-convergence-bounds.md) | partially-solved | Bounding the time and message cost for anti-entropy/read-repair to converge replicas. |
| [Conflict Resolution Expressiveness](./conflict-resolution-expressiveness.md) | open | Characterizing which application semantics are expressible via last-writer-wins, CRDTs, or custom merges. |
| [Compaction-Triggered Cache Invalidation](./compaction-cache-invalidation.md) | empirically-open | Keeping block/row caches valid across rewrites without flushing the entire cache on each compaction. |
| [Cost Bounds for Tunable Reads](./cost-bounds-tunable-reads.md) | open | Lower bounds on coordination messages for a target consistency/staleness under failures. |
| [Schema-on-Read Query Optimization](./schema-on-read-optimization.md) | open | Optimizing queries over schemaless/semi-structured KV values without a fixed catalog. |
| [Adaptive Compaction Policy Switching](./adaptive-compaction-switching.md) | empirically-open | Safely switching compaction strategies (leveled/tiered/hybrid) online as workloads drift. |

---

[Back to taxonomy](../../TAXONOMY.md)
