# Indexing & Access Methods

Access methods are the data structures that let a DBMS find tuples without scanning everything: B-trees and their concurrent variants, write-optimized LSM-trees, hash indexes, bitmap and inverted indexes, and multidimensional structures. The central tension is the RUM conjecture — every design trades off read, update, and memory/space overheads — and the hard problems span complexity-theoretic lower bounds (cell-probe, fine-grained) as well as concrete engineering challenges (concurrency, NVM, cloud-native, learned and adaptive structures).

This catalog collects 30 research-grade open problems at the intersection of theory (bounds, expressiveness, instance optimality) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [Closing the RUM tradeoff lower bound](./rum-tradeoff-lower-bound.md) | open | Whether a three-way read/update/memory lower bound can be proven for dynamic ordered dictionaries in the external-memory/cell-probe model. |
| [Optimal LSM-tree compaction policy](./lsm-optimal-compaction.md) | partially-solved | Finding the Pareto-optimal merge policy and tuning across the full read/write/space design space of log-structured merge trees. |
| [Instance-optimal learned indexes](./learned-index-instance-optimal.md) | empirically-open | Whether a learned index can provably match the best static structure for any given key distribution with worst-case guarantees. |
| [Updatable learned indexes under writes](./updatable-learned-index.md) | empirically-open | Maintaining learned-index accuracy and bounded lookup cost under high-throughput insert/delete workloads. |
| [Concurrent B-tree with optimal contention](./concurrent-btree-contention.md) | partially-solved | Designing a B-tree variant whose synchronization cost provably scales with actual conflict, not structure size. |
| [Worst-case-optimal multidimensional index](./multidim-index-lower-bound.md) | open | Whether orthogonal range search can achieve simultaneously optimal query time and linear space in d dimensions. |
| [Adaptive indexing convergence guarantees](./database-cracking-convergence.md) | partially-solved | Provable bounds on how fast database cracking converges to a sorted index under adversarial query sequences. |
| [Cache-oblivious dynamic B-tree optimality](./cache-oblivious-btree.md) | solved-but-impractical | Closing the gap between cache-oblivious search-tree bounds and constants competitive with tuned cache-aware B-trees. |
| [Hashing with optimal RUM under skew](./hash-index-skew-rum.md) | open | Hash table designs that retain O(1) expected probes and bounded memory under heavy-tailed, adversarial key skew. |
| [Succinct dynamic ordered dictionaries](./succinct-dynamic-dictionary.md) | open | Supporting predecessor/range queries and updates in space within o(n) bits of the information-theoretic minimum. |
| [Bitmap index compression vs. query speed](./bitmap-compression-tradeoff.md) | partially-solved | Provably optimal compression schemes that preserve word-aligned boolean-operation speed on bitmap indexes. |
| [Inverted-index compression for conjunctions](./inverted-index-conjunction.md) | empirically-open | Compressed posting-list layouts that accelerate multi-term intersection beyond galloping/SIMD lower bounds. |
| [Optimal Bloom/filter memory allocation](./filter-memory-allocation.md) | partially-solved | Allocating filter bits across LSM levels to minimize false positives under a global memory budget. |
| [Range filters with provable guarantees](./range-filter-design.md) | empirically-open | Compact filters answering range-emptiness queries with bounded false-positive rate and update support. |
| [Write-optimized index lower bounds](./write-optimized-lower-bound.md) | open | Tight bounds on the insert/query tradeoff achievable by buffered/B-epsilon-tree-style structures. |
| [Index design for NVM/persistent memory](./nvm-index-design.md) | empirically-open | Crash-consistent, low-fence access methods that exploit byte-addressable persistent memory's asymmetry. |
| [Multidimensional learned indexes](./learned-multidim-index.md) | empirically-open | Learned models for multi-attribute and spatial data with worst-case query and update guarantees. |
| [Self-tuning index selection complexity](./index-selection-complexity.md) | open | Hardness and approximability of choosing an index configuration to minimize workload cost under a space budget. |
| [Secondary indexing on LSM-trees](./lsm-secondary-indexing.md) | partially-solved | Maintaining consistent, low-amplification secondary indexes over log-structured primary stores. |
| [Concurrent index with non-blocking range scans](./lockfree-range-scan.md) | partially-solved | Lock-free or wait-free ordered indexes that provide linearizable range queries without scan-time blocking. |
| [Optimal index for mixed point/range workloads](./mixed-point-range-index.md) | empirically-open | A single structure provably near-optimal across both point-lookup-heavy and range-scan-heavy workloads. |
| [Compaction scheduling under bursty writes](./compaction-scheduling.md) | empirically-open | Online compaction scheduling that bounds tail read latency while keeping write stalls bounded under bursts. |
| [Predecessor search optimality gaps](./predecessor-search-bounds.md) | partially-solved | Closing remaining gaps in the cell-probe complexity of static and dynamic predecessor search. |
| [Tree indexes on disaggregated storage](./disaggregated-index.md) | empirically-open | Access methods optimized for compute/storage separation with high-latency, paginated remote storage. |
| [GPU-resident index structures](./gpu-index-structures.md) | empirically-open | Index designs that exploit GPU memory hierarchy and massive parallelism for point and range queries. |
| [Verifiable/authenticated index structures](./authenticated-index.md) | partially-solved | Indexes producing succinct membership and range proofs with minimal proof size and update overhead. |
| [Approximate-membership for dynamic sets](./dynamic-amq-structures.md) | open | Filters supporting deletes and resizing while matching the static space lower bound and false-positive rate. |
| [Order-preserving encrypted indexes](./order-preserving-index.md) | open | Indexes supporting range queries over encrypted keys with quantified leakage and access-pattern bounds. |
| [Index maintenance under schema/data drift](./index-under-drift.md) | empirically-open | Keeping learned/adaptive indexes accurate and cheap as data distributions shift over time. |
| [Unified cost model for access-method design](./access-method-cost-model.md) | open | A predictive cost model spanning the access-method design space to enable automated structure synthesis. |

---
[Back to taxonomy](../../TAXONOMY.md)
