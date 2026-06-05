# Concurrent Resizable Hash Tables

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/concurrent-resizable-hashing` · **Status:** partially-solved

## 1. Problem Statement
Hash indexes are the workhorse of main-memory databases for point lookups, joins, and aggregation. Under high core counts, the table must support concurrent `lookup`, `insert`, `delete` with minimal synchronization. The hard part is **resizing**: when the load factor crosses a threshold, the table must grow (or shrink) by rehashing, which classically requires a global rebuild that **stalls** all readers and writers. We want a **lock-free (or wait-free)** concurrent hash table that **resizes without stalling** any reader or writer, with **bounded amortized cost** per operation and progress guarantees, while remaining cache-efficient.

Variants:
- **Progress class:** wait-free (per-op bound) vs. lock-free (system-wide progress) vs. obstruction-free.
- **Resize policy:** grow-only, grow-and-shrink, incremental vs. atomic.
- **Consistency:** linearizable point operations; optionally consistent iteration/scan during resize.
- **Cost metric:** worst-case vs. amortized per-operation, and the *re-distribution* cost charged at resize.

## 2. Mathematical Foundations
A hash table maps keys via $h: \mathcal{U} \to [m]$ into $m$ buckets; load factor $\alpha = n/m$. With *linear/Robin-Hood/cuckoo* probing, expected probe length is bounded for $\alpha$ below a threshold, motivating resize. The cost model uses **amortized analysis** (potential method): a resize that touches $\Theta(m)$ slots is amortized over the $\Theta(m)$ insertions that triggered it, giving $O(1)$ amortized insert *in the sequential model*. The concurrency model is **linearizability** with progress guarantees defined over schedules; lock-freedom requires that some thread always makes progress, wait-freedom that *every* thread completes in a bounded number of its own steps.

**Split-ordered lists** (Shalev–Shavit) give the canonical lock-free resizable design: keys are stored in a single lock-free linked list ordered by *bit-reversed* hash, and the bucket array is an index of pointers into the list; growing the table only *adds* bucket pointers and *splits* no nodes — resizing is incremental and never blocks. **Extendible/dynamic hashing** (Fagin et al.) underlies directory-doubling designs. Cuckoo hashing gives worst-case $O(1)$ lookups but concurrent resize is delicate (cuckoo paths cross buckets).

## 3. State of the Art (SOTA)
- **Theory/algorithms-SOTA.** **Split-ordered lists** (Shalev, Shavit, *Split-Ordered Lists: Lock-Free Extensible Hash Tables*, JACM 2006) — lock-free, incrementally resizable, the foundation of `java.util.concurrent` extensible hashing and many libraries. **Liu, Zhang, Spear, *Dynamic-Sized Nonblocking Hash Tables*** (PODC 2014) — resizable nonblocking with freezing.
- **Systems-SOTA.** **libcuckoo** (Li, Andersen, Kaminsky, Freedman, EuroSys 2014) — high-throughput concurrent cuckoo with fine-grained locking and optimistic resize. **Folly's `ConcurrentHashMap`**, **Intel TBB `concurrent_hash_map`**, and **CLHT** (Cache-Line Hash Table, David, Guerraoui, Tudor, ASPLOS 2015) — cache-line-bounded concurrent hashing. DB engines: **Hekaton's** Bw-tree/hash, **HyPer/Umbra** vectorized hash tables, and morsel-driven build hash tables for joins.
- **Persistent variants.** CLEVEL/Dash for persistent-memory concurrent resizable hashing (frontier).

Status: **partially solved** — lock-free incremental resize exists (split-ordered) and high-throughput systems exist, but no single design is simultaneously wait-free, cache-optimal, shrinkable, and worst-case (not just amortized) bounded.

## 4. Upper Bound
Split-ordered lists give **lock-free** operations with **$O(1)$ expected** lookup/insert and *incremental, non-blocking* growth — resize adds buckets lazily, charging $O(1)$ amortized per operation, never stalling readers/writers. libcuckoo gives worst-case $O(1)$ lookups (two probes) with concurrent resize under fine-grained locks (not lock-free). CLHT achieves at most one cache-line access per lookup. Dynamic-sized nonblocking tables (Liu–Zhang–Spear) achieve resize with bounded freezing. The best *combined* upper bound is lock-free, $O(1)$ expected, $O(1)$ amortized incremental resize (split-ordered).

## 5. Lower Bound
Fundamental impossibility: **Fich–Hendler–Shavit** ("Linear lower bounds on real-world implementations of concurrent objects," FOCS 2005 / JACM) prove that a class of lock-free objects requires $\Omega(\#\text{threads})$ stalls or memory operations in the worst case — implying inherent contention cost. For *wait-free* operations, the consensus hierarchy (Herlihy) shows requirements on synchronization primitives (CAS suffices for wait-free hashing but at a cost). Amortized $O(1)$ insert is optimal sequentially (you must at least write the element), but *worst-case* $O(1)$ insert is impossible for any resizable table without either lazy/incremental rehash or pre-allocation — a single resize must touch $\Omega(m)$ slots, so some operation pays $\Omega(m)$ unless the cost is spread (which split-ordered does, but only amortized). Cell-probe lower bounds for dynamic dictionaries (e.g., $\Omega(\log n / \log\log n)$ for some deterministic dynamic problems) bound non-hashed variants.

## 6. The Gap
The upper bound (lock-free, $O(1)$ amortized, incremental resize) is excellent, but gaps remain: (1) **worst-case** per-operation bounds during resize (split-ordered is amortized; a single op can still observe a long split chain); (2) **wait-free** resizable hashing with practical constants is largely unrealized; (3) **shrinking** without stalls is harder than growing and less studied; (4) cache-/NUMA-optimality combined with non-blocking resize is empirical, not proven. Whether a *wait-free, worst-case $O(1)$, cache-optimal, grow-and-shrink* hash table exists with practical constants is **open** — the problem is partially solved in that strong lock-free designs exist, but the strongest combination of guarantees is not achieved.

## 7. Current Research (as of June 2026)
Directions: persistent-memory concurrent resizable hashing (Dash, CLEVEL, and successors) handling crash-consistency plus resize; learned hashing combined with concurrency; RDMA/disaggregated-memory hash tables where resize must coordinate across nodes; and wait-free constructions via hardware transactional memory or RDMA-CAS. Groups: CMU (Andersen/Kaminsky — cuckoo, Pavlo — persistent hashing), EPFL (Guerraoui — CLHT, concurrency theory), Lehigh (Spear), and the persistent-memory community. RDMA-disaggregated resizable hashing with non-blocking resize is an active 2025-2026 frontier *(frontier — verify)*.

## 8. Future Work
- Practical wait-free resizable hashing with worst-case per-op bounds.
- Non-blocking *shrink* with bounded amortized cost.
- Provably cache-/NUMA-optimal lock-free resize.
- Crash-consistent resizable hashing on PMEM/CXL with the same guarantees as volatile designs.

## 9. Key References
- **[Foundational]** Shalev, Shavit. *Split-Ordered Lists: Lock-Free Extensible Hash Tables.* JACM, 2006. — [DOI](https://dl.acm.org/doi/10.1145/1147954.1147958)
- **[SOTA]** Li, Andersen, Kaminsky, Freedman. *Algorithmic Improvements for Fast Concurrent Cuckoo Hashing (libcuckoo).* EuroSys, 2014. — [DOI](https://dl.acm.org/doi/10.1145/2592798.2592820)
- **[SOTA]** David, Guerraoui, Tudor. *Asynchronized Concurrency: The Secret to Scaling Concurrent Search Data Structures (CLHT).* ASPLOS, 2015. — [DOI](https://dl.acm.org/doi/10.1145/2786763.2694359)
- **[Foundational]** Fich, Hendler, Shavit. *On the Inherent Weakness of Conditional Synchronization Primitives / Linear Lower Bounds on Real-World Implementations of Concurrent Objects.* FOCS, 2005. — [IEEE](https://ieeexplore.ieee.org/document/1530711/)
- **[SOTA]** Liu, Zhang, Spear. *Dynamic-Sized Nonblocking Hash Tables.* PODC, 2014. — [DOI](https://dl.acm.org/doi/10.1145/2611462.2611495)
- **[Foundational]** Fagin, Nievergelt, Pippenger, Strong. *Extendible Hashing — A Fast Access Method for Dynamic Files.* ACM TODS, 1979. — [DOI](https://doi.org/10.1145/320083.320092)

## 10. Worked Example

Split-ordered list with $m=2$ buckets, keys $\{1,3,2\}$ inserted. Hash = key itself; bucket = $h \bmod m$. The single underlying lock-free list is sorted by the **bit-reversed** 3-bit key:

| key | binary | reversed | sort value |
|-----|--------|----------|-----------|
| 1 | 001 | 100 | 4 |
| 3 | 011 | 110 | 6 |
| 2 | 010 | 010 | 2 |

List order (ascending reversed value): $2 \to 1 \to 3$. Bucket 0 (even keys) points at node 2; bucket 1 (odd keys) points at node 1.

Now load factor crosses threshold, so grow to $m=4$. We do **not** rebuild: we lazily add bucket pointers 2 and 3. Bucket 2 ($h \bmod 4 = 2$) just needs a pointer into the existing list at the first reversed-key $\ge$ reverse(2) — it lands on node 2 already there. No node moves, no reader stalls; the new bucket is initialized with one CAS. This is the $O(1)$-amortized, non-blocking resize: growth costs only pointer insertion, charged across the inserts that triggered it.

---
*Part of the [DBMS Research catalog](../../README.md).*
