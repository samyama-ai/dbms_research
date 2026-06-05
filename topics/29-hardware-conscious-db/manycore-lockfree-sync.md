# Lock-free synchronization for many-core engines

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/manycore-lockfree-sync` · **Status:** empirically-open

## 1. Problem Statement

Modern servers have hundreds of hardware threads across many sockets/chiplets with non-uniform memory and cache-coherence costs. Shared relational structures — hash tables, B-trees, lock tables, the WAL tail, transaction-ID counters, buffer-pool latches — become contention points where a single hot cache line, atomically updated by many cores, causes **contention collapse**: throughput rises then *falls* as cores are added because the coherence traffic to bounce one line dominates. The problem: design **concurrency primitives and data-structure access protocols that scale to hundreds of cores** on relational workloads, avoiding the collapse while preserving correctness (linearizability/serializability) and progress (lock-freedom / wait-freedom where required).

Variants: (i) **structure-specific** — scalable concurrent hash-index, B-tree (OLC/Bw-tree), and counter; (ii) **protocol** — scalable locking (MCS, reader-writer, hierarchical NUMA locks) vs lock-free vs optimistic; (iii) **progress guarantee** — lock-free vs wait-free trade-offs; (iv) **contention-management** — back-off, delegation/combining, and sharding to remove single hot lines.

## 2. Mathematical Foundations

The cost model is **cache-coherence / remote-memory-reference (RMR)** complexity: operations counted by the number of cache-line transfers across cores (not just instructions), because an uncontended CAS is $O(1)$ but a contended hot line costs $\Theta(p)$ serialized coherence transactions for $p$ cores. Foundations: **linearizability** (Herlihy–Wing) as the correctness criterion; the **consensus hierarchy** (Herlihy) — CAS has consensus number $\infty$, so it can build any wait-free object, but at a coherence cost; **wait-free/lock-free progress** definitions; and **mutual-exclusion lower bounds** in the cache-coherent (CC) and distributed-shared-memory (DSM) models (Attiya–Hendler–Woelfel; Fan–Lynch) giving $\Omega(\log p)$ RMR per operation for mutual exclusion. **Combining/flat-combining** turns $p$ concurrent updates into one cache-line owner doing batched work, lowering RMR from $\Theta(p)$ toward $\Theta(\log p)$ or $O(1)$ amortized for commutative operations. **Universal construction** results bound the cost of making any sequential structure concurrent. The "contention collapse" is the regime where measured throughput $\propto p$ until coherence bandwidth saturates, then degrades — captured empirically, not by a single closed form.

## 3. State of the Art (SOTA)

- **Locks:** **MCS / CLH** queue locks (scalable, local-spin), **NUMA-aware / hierarchical locks** (cohort locks, Dice et al.), reader-writer and **biased** locks. **Optimistic Lock Coupling (OLC)** for B-trees (Leis et al., DaMoN 2019) is the practical winner for in-memory indexes.
- **Lock-free structures:** Michael–Scott queue, **split-ordered / lock-free hash tables** (Shalev–Shavit, JACM 2006), **Bw-tree** (Microsoft, ICDE 2013), epoch-based reclamation (EBR) and hazard pointers for safe memory reclamation.
- **DB engines:** **Silo** (MIT, SOSP 2013) avoids a global TID via decentralized commit; **ERMIA, Cicada, FOEDUS** target many-core OLTP; **Masstree** (EuroSys 2012) for scalable trees. Why empirically-open: each structure has a strong design, but *general* primitives that provably avoid collapse at hundreds of cores across all relational structures do not exist — it's tuned per structure.

## 4. Upper Bound

In the CC model, scalable mutual exclusion achieves **$O(\log p)$ RMR per passage** (Yang–Anderson tournament locks; matching the lower bound). Flat-combining and delegation give **$O(1)$ amortized** cache-line ownership for batchable/commutative operations. Lock-free hash tables and queues provide $O(1)$ expected work with lock-free progress. For B-trees, OLC and Bw-tree empirically scale near-linearly to dozens–hundreds of cores on read-mostly workloads. Decentralized-commit OLTP (Silo) scales to many cores by *eliminating* the shared counter rather than synchronizing it faster — the dominant practical "upper bound" technique is **avoidance/sharding**, not faster atomics.

## 5. Lower Bound

The key lower bound is **$\Omega(\log p)$ RMR per operation for mutual exclusion** in both CC and DSM models (Attiya–Hendler–Woelfel, STOC 2008; Fan–Lynch), meaning no lock can be perfectly scalable — some logarithmic coherence cost is unavoidable for exclusion. For **wait-free** implementations, Jayanti's lower bounds show $\Omega(\log p)$ or worse step complexity for many objects (e.g., snapshots, counters), and Herlihy's hierarchy implies registers alone cannot build many objects wait-free. Information-theoretically, a single shared counter updated by $p$ cores requires $\Omega(p)$ coherence transactions per "epoch" if every core must observe a unique value — the root cause of collapse on global TID/sequence counters. These are **model-named** (CC/DSM RMR, consensus hierarchy) and explain why *sharding/avoidance* beats *faster shared updates*.

## 6. The Gap

The mutual-exclusion gap is **closed up to constants**: $\Theta(\log p)$ RMR. The genuinely **open** gap is *practical and workload-dependent*: there is no general design that guarantees no contention collapse for arbitrary relational structures and skewed/hot-key workloads at hundreds of cores — current results are per-structure (B-tree OLC, lock-free hash, decentralized commit) and skew can still concentrate updates onto one line. Closing it needs either (i) general delegation/combining frameworks with proven $O(1)$-amortized coherence under skew, or (ii) impossibility results showing hot-key workloads force collapse, formalizing what "sharding" must give up (e.g., real-time / strict serializability constraints).

## 7. Current Research (as of June 2026)

- Delegation/combining and **shared-nothing partitioning** to remove hot lines under skew *(frontier — verify)*.
- NUMA/chiplet- and CXL-aware lock and index protocols modeling multi-hop coherence cost *(frontier — verify)*.
- Hardware transactional memory (HTM) revival and RDMA/one-sided primitives for disaggregated engines.
- Scalable epoch/EBR and hazard-pointer reclamation at hundreds of cores.
- Groups: TUM (Leis, Neumann — OLC/Umbra), MIT (Liskov/Morris lineage, Silo), Tel Aviv (Shavit/Shalev), Microsoft Research (Bw-tree), Oracle Labs (Dice — cohort locks).

## 8. Future Work

- General-purpose combining frameworks with proven $O(1)$-amortized coherence under adversarial skew.
- Impossibility/lower-bound theory for hot-key relational workloads (when is collapse unavoidable?).
- Coherence-cost models for chiplet/CXL/NUMA hierarchies to guide protocol design.
- Wait-free relational index/log primitives that remain practical at hundreds of cores.

## 9. Key References

- **[Foundational]** Herlihy, M., Wing, J. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990.
- **[Foundational]** Herlihy, M. *Wait-Free Synchronization.* ACM TOPLAS, 1991.
- **[Foundational]** Mellor-Crummey, J. M., Scott, M. L. *Algorithms for Scalable Synchronization on Shared-Memory Multiprocessors (MCS Locks).* ACM TOCS, 1991.
- **[Lower Bound]** Attiya, H., Hendler, D., Woelfel, P. *Tight RMR Lower Bounds for Mutual Exclusion and Other Problems.* STOC, 2008.
- **[SOTA]** Tu, S., Zheng, W., Kohler, E., Liskov, B., Madden, S. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013.
- **[SOTA]** Leis, V., Haubenschild, M., Neumann, T. *Optimistic Lock Coupling: A Scalable and Efficient General-Purpose Synchronization Method.* IEEE Data Eng. Bulletin / DaMoN, 2019.
- **[SOTA]** Shalev, O., Shavit, N. *Split-Ordered Lists: Lock-Free Extensible Hash Tables.* JACM, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
