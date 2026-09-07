---
id: 14-main-memory-db/latch-free-btree-range-locks
title: "Latch-Free B-tree With Range Locks"
topic: 14-main-memory-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

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
- **[Foundational]** J. Levandoski, D. Lomet, S. Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)
- **[Foundational]** Y. Mao, E. Kohler, R. Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012. — [DOI](https://doi.org/10.1145/2168836.2168855)
- **[SOTA]** V. Leis, M. Haubenschild, T. Neumann. *Optimistic Lock Coupling: A Scalable and Practical Synchronization Paradigm.* IEEE Data Eng. Bull. / DaMoN, 2019. — [DBLP](https://dblp.org/rec/journals/debu/LeisH019.html)
- **[Foundational]** K. P. Eswaran, J. Gray, R. Lorie, I. Traiger. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[Foundational]** M. Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[Foundational]** C. Mohan. *ARIES/KVL: A Key-Value Locking Method for Concurrency Control of Multiaction Transactions.* VLDB, 1990. — [DBLP](https://dblp.org/rec/conf/vldb/Mohan90.html)

## 10. Worked Example

Leaf holds keys $\{10, 20, 40\}$. Transaction $T_1$ runs `SELECT COUNT(*) WHERE k BETWEEN 25 AND 35`, scanning the predicate $P=[25,35]$ and finding $0$ matches.

Concurrently $T_2$ inserts $k=30$ (a phantom for $P$).

**Pessimistic next-key locking:** $T_1$'s scan lands between $20$ and $40$, so it takes a *gap lock* on the next key $40$ covering the open interval $(20,40)$. $T_2$'s insert of $30$ must acquire a conflicting lock on the same gap and *blocks* until $T_1$ commits. No phantom; serializable.

**Optimistic validation (latch-free path):** $T_1$ traverses with version counters, records the scanned leaf's version $v=7$, reads $0$ rows, finishes. At commit, $T_1$ re-checks the leaf: $T_2$'s CAS-insert bumped the version to $v=8$, and $30\in[25,35]$. Validation detects the predicate conflict and *aborts* $T_1$.

Both give a serializable outcome; the trade is one blocked insert ($O(1)$ wait) versus one wasted scan (abort + retry) — exactly the contention-dependent cost of §4–§6.

---
*Part of the [DBMS Research catalog](../../README.md).*
