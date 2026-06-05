# Latch-Free B-tree With Range Locks

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/latch-free-btree-range-locks` · **Status:** partially-solved

## 1. Problem Statement
A latch-free (lock-free) B-tree variant lets many threads traverse and mutate the index using only atomic primitives (CAS, fetch-and-add) plus epoch-based reclamation, achieving near-linear scalability on multicore IMDBs. **Serializable** transactions, however, must additionally prevent **phantoms**: a predicate read over a key range $[lo,hi)$ must be protected so that no concurrent transaction inserts a key into that range. The classical answer is **range / next-key locking**, which is intrinsically *stateful and pessimistic* — seemingly at odds with the *stateless, optimistic* nature of latch-free traversal.

**The problem:** design an index that simultaneously (a) traverses and updates latch-free at in-memory speed, and (b) supports phantom-preventing range locks (or an equivalent validation) without reintroducing a global lock manager or per-node latches that destroy scalability.

Variants: *(decision)* serializable phantom prevention vs. *(relaxed)* snapshot-isolation phantom *anomalies tolerated*; *(mechanism)* pessimistic range locks vs. optimistic predicate **validation** at commit.

## 2. Mathematical Foundations
Phantoms are formalized via the **multiversion / view-serializability** theory of conflict graphs. Let a predicate read $R_P$ and an insert $W_k$ with $k\in P$ form a **predicate-write conflict**. Serializability requires the conflict graph (including these phantom edges) be acyclic. Range locking realizes this by mapping a predicate $P$ to a *covering set of key-range lock intervals* such that any insert into $P$ must first acquire a conflicting lock — a **gap-locking** discipline over the ordered key domain $\mathcal{K}$.

Latch-freedom is defined by progress conditions: an operation is **lock-free** if some thread always makes progress, **wait-free** if every thread completes in bounded steps. Memory safety under concurrent unlink uses **epoch-based reclamation (EBR)**: a node freed at epoch $e$ is reclaimed only after all threads have advanced past $e$, guaranteeing no dangling reader, formalized by the grace-period invariant $\forall t:\ \text{epoch}(t)>e$.

Key tension: range locks impose a *total order on intervals* (a serialization structure), while lock-free structures rely on *linearizability of single-word CAS*. Bridging them is the technical crux.

## 3. State of the Art (SOTA)
- **Bw-tree** (Levandoski, Lomet, Sengupta, ICDE 2013): latch-free B-tree via a mapping table + delta records + CAS; basis of Microsoft Hekaton's range index. Phantom prevention in Hekaton is handled by the transaction layer (validation), not by the index latches.
- **Masstree** (Mao, Kohler, Morris, EuroSys 2012): cache-craftiness trie-of-B-trees with optimistic concurrency (versioned nodes), the canonical fast in-memory ordered index.
- **OLC / Optimistic Lock Coupling B-tree** (Leis, Haubenschild, Neumann; *The ART of Practical Synchronization*, DaMoN 2016/2019): optimistic version locks give near-latch-free read scaling with simple correctness — widely viewed as the practical winner over fully lock-free designs.
- **Precision/predicate locking & next-key locking**: the classical phantom-prevention contracts (Eswaran et al. 1976; Mohan ARIES/KVL) that serializable indexes still emulate.

## 4. Upper Bound
Reads scale latch-free (or optimistic-lock-coupled) at $O(\log n)$ traversal with **no cache-line writes on the read path** (OLC, Masstree). Phantom prevention via OCC validation costs $O(|\text{read predicates}|)$ at commit. With next-key/gap locking, an insert acquires $O(1)$ amortized interval locks; a range scan of $m$ keys protects them with $O(m)$ gap locks or one validated range. Best known: serializable range queries with **single-word-CAS updates** + epoch reclamation, achieving multicore-linear throughput on partition-free workloads (Hekaton, Silo-style OCC).

## 5. Lower Bound
There is no general lock-free B-tree lower bound, but two hard facts constrain designs: (1) **CAS retry under contention** — Ellen/Fatourou-style results on lock-free search trees show worst-case unbounded retries (only lock-*freedom*, not wait-freedom, is achievable cheaply), so a single hot range serializes. (2) Phantom prevention is *information-theoretically* a predicate-locking problem: to certify "no key in $[lo,hi)$ was inserted," a serializable schedule must communicate every conflicting insert to the reader, a communication-complexity floor that pure optimism cannot beat when contention on the range is high — validation must abort. Universal wait-free range structures are subject to the consensus-number hierarchy (Herlihy), requiring CAS (consensus number $\infty$) but giving no contention-free guarantee.

## 6. The Gap
Read-mostly, low-contention serializable range indexing is effectively *solved* (OLC/Bw-tree + OCC validation, hence "partially-solved"). The genuine remaining gap: **high-contention overlapping range predicates**, where both fully lock-free updates and optimistic validation degrade (livelock / abort storms), and there is no design that is simultaneously wait-free *and* phantom-serializable without falling back to pessimistic gap locks that re-serialize the hot range. Whether a structure can give bounded-step progress under range contention while staying serializable is open.

## 7. Current Research (as of June 2026)
- Hybrid pessimistic/optimistic range locks that escalate to gap locks only on detected contention *(frontier — verify)*.
- Learned indexes (RMI/ALEX/PGM) gaining concurrent, range-lockable variants — combining model-based lookup with phantom-safe inserts *(frontier — verify)*.
- Range locks tailored to persistent-memory and disaggregated indexes, where remote CAS cost reshapes the tradeoff *(frontier — verify)*.
- Groups: TUM (Leis, Neumann), MIT (Kohler/Morris lineage), Microsoft Research (Lomet/Levandoski), CMU DB Group.

## 8. Future Work
- A provably wait-free, phantom-serializable ordered index, or a proof of impossibility.
- Tight competitive analysis of optimistic validation vs. pessimistic gap locking under a contention parameter.
- Formal verification (e.g., in Iris/separation logic) of latch-free B-tree + range-lock protocols.

## 9. Key References
- **[Foundational]** J. Levandoski, D. Lomet, S. Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013.
- **[Foundational]** Y. Mao, E. Kohler, R. Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012.
- **[SOTA]** V. Leis, M. Haubenschild, T. Neumann. *Optimistic Lock Coupling: A Scalable and Practical Synchronization Paradigm.* IEEE Data Eng. Bull. / DaMoN, 2019.
- **[Foundational]** K. P. Eswaran, J. Gray, R. Lorie, I. Traiger. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976.
- **[Foundational]** M. Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991.
- **[Foundational]** C. Mohan. *ARIES/KVL: A Key-Value Locking Method for Concurrency Control of Multiaction Transactions.* VLDB, 1990.

---
*Part of the [DBMS Research catalog](../../README.md).*
