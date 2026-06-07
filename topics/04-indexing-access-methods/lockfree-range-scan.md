---
id: 04-indexing-access-methods/lockfree-range-scan
title: "Concurrent index with non-blocking range scans"
topic: 04-indexing-access-methods
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Concurrent index with non-blocking range scans

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/lockfree-range-scan` · **Status:** partially-solved

## 1. Problem Statement
An **ordered concurrent index** (B-tree / skip list / trie) must support `insert`, `delete`, `lookup`, and **`range(lo, hi)`** under many threads. Point operations have mature lock-free and wait-free solutions; the hard case is the **range scan**, which must return a key set that is **linearizable** — equivalent to some atomic snapshot at a single instant — *without* blocking concurrent writers or being blocked by them.

The problem: **design an ordered index whose range scans are linearizable and non-blocking** (lock-free, ideally wait-free), with scan cost proportional to result size and bounded interference with updates.

- **Decision/feasibility variant:** can a wait-free linearizable range scan coexist with lock-free updates on the same structure?
- **Optimization variant:** minimize scan overhead (extra reads, helping, version retention) subject to linearizability and a progress guarantee.
- Distinguish **linearizable** scans from weaker **consistent-but-not-linearizable** (epoch-serializable) scans, which are cheaper and often sufficient.

*Partially solved:* lock-free linearizable range scans exist (via versioning / RangeScan helping); **wait-free** range scans with point-operation efficiency remain elusive, and lower bounds on unavoidable cost are incomplete.

## 2. Mathematical Foundations
The correctness target is **linearizability** (Herlihy–Wing 1990): every operation appears atomic at a *linearization point* within its interval. Progress conditions: **wait-free** (every thread finishes in finite steps), **lock-free** (some thread progresses), **obstruction-free**. A range scan returns a *set*, so its linearization point must witness a single global snapshot — the core tension, since the scan touches many nodes over time.

Key techniques:
- **Multi-version / snapshot reads:** assign each update a version/timestamp; a scan reads the consistent version $\le t_{\text{scan}}$, reducible to a partial **snapshot object**. Snapshots cost $\Omega(n)$ bookkeeping in worst-case classical models (Afek et al.), motivating *partial* snapshots covering only $[lo,hi]$.
- **Helping & descriptors:** scans publish a descriptor; writers in the range **help** complete or record their effect relative to the scan, preserving linearizability.
- **RCU / epoch-based reclamation:** bounds memory while readers traverse, but plain RCU gives consistency only relative to grace periods, not per-scan linearizability under concurrent updates.

## 3. State of the Art (SOTA)
- **Theory/algorithms:** lock-free linearizable range queries via the **versioned-CAS / RangeScan** framework of Arbel-Raviv & Brown (PPoPP 2018), a general technique adding linearizable scans to many lock-free trees/lists; the **Bundled References** approach (Nelson-Slominski et al., PPoPP 2022) attaches version chains to pointers. **KiWi** (Basin et al., PPoPP 2017) is a wait-free-scan / lock-free-update concurrent ordered map.
- **Systems:** **Masstree** (EuroSys 2012, trie-of-B-trees, optimistic version validation), **Bw-tree** (latch-free, Hekaton / ICDE 2013), **OLFIT** B-trees, and **ART/ROWEX** (optimistic lock coupling) — most provide consistent but practically-snapshotted scans rather than provably wait-free ones.

## 4. Upper Bound
The Arbel-Raviv–Brown technique adds linearizable range queries with **lock-free** progress and scan cost $O(|\text{result}| + c)$ where $c$ counts concurrent overlapping updates helped; updates retain $O(1)$ amortized extra work. KiWi achieves **wait-free scans** with lock-free puts at scan cost $O(\log n + |\text{result}|)$ amortized. These hold in the **asynchronous shared-memory model with CAS** and are algorithmic SOTA; they trade memory (version retention) for non-blocking scans.

## 5. Lower Bound
In asynchronous shared memory, **atomic snapshots** require $\Omega(n)$ space/steps in adversarial single-writer constructions (Jayanti–Tan–Toueg-style bounds), and partial-snapshot lower bounds (Attiya et al.) imply scans cannot be entirely free of writer interaction. No matching tight bound exists for the *combined* object (wait-free scan **and** wait-free update at point-operation efficiency); the conjectured obstruction is that linearizable wait-free range scans force either unbounded version retention or per-update scan-coordination cost. CAP/FLP impossibility does not directly apply (single shared memory), but **helping is provably necessary** for some wait-free objects (Censor-Hillel et al.).

## 6. The Gap
Lock-free linearizable scans are *achieved*; the open frontier is (a) **wait-free** linearizable scans without sacrificing update throughput or memory, and (b) **tight lower bounds** quantifying unavoidable scan/update interference. It is genuinely open whether an index can be wait-free for both range scans and updates at point-operation efficiency. Closing it needs either such a construction or a cell-probe/step-complexity lower bound forbidding it.

## 7. Current Research (as of June 2026)
- **Bundled references and version-pointer GC** bounding multi-version scan memory with provable reclamation latency *(frontier — verify)*.
- **Persistent-memory-aware** lock-free range indexes where scan linearization must survive crashes (durable linearizability) *(frontier — verify)*.
- Hardware-transactional-memory-assisted hybrids narrowing the wait-free gap.
- Groups: Trevor Brown (Waterloo), Erez Petrank / Technion (KiWi lineage), MIT/Harvard concurrency theory, Microsoft Research (Bw-tree/FASTER lineage).

## 8. Future Work
- A wait-free linearizable ordered map with $O(\log n)$ scans and bounded version memory.
- Tight step-complexity lower bounds for combined scan+update objects.
- Formal (model-checked) verification of helping-based range-scan protocols.

## 9. Key References
- **[Foundational]** M. Herlihy, J. Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[SOTA]** M. Arbel-Raviv, T. Brown. *Harnessing Epoch-Based Reclamation for Efficient Range Queries.* PPoPP, 2018. — [DOI](https://doi.org/10.1145/3178487.3178489)
- **[SOTA]** D. Basin, et al. *KiWi: A Key-Value Map for Scalable Real-Time Analytics.* PPoPP, 2017. — [DOI](https://doi.org/10.1145/3018743.3018761)
- **[SOTA]** J. Levandoski, D. Lomet, S. Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)
- **[SOTA]** Y. Mao, E. Kohler, R. Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012. — [DOI](https://doi.org/10.1145/2168836.2168855)

## 10. Worked Example

A sorted linked list holds keys $\{10,20,30,40\}$. Thread $A$ runs `range(15,35)` (should return $\{20,30\}$); thread $B$ concurrently does `insert(25)` and `delete(20)`.

Without coordination, $A$ traverses $20$ (reads it), then $B$ inserts $25$ and deletes $20$, then $A$ reaches $30$ — $A$ might return $\{20,30\}$ while *also* a node $25$ that committed before $A$ saw $30$. Is $\{20,30\}$ linearizable? Only if there is a single instant where the live set restricted to $[15,35]$ equals exactly the returned set. If $B$'s two writes straddle $A$'s reads, no such instant exists — the scan is non-linearizable.

The versioned-CAS fix: stamp the scan with timestamp $t_s$. Each node carries a version; $A$ reports a node iff its insert-version $\le t_s$ and its delete-version $> t_s$. With $t_s$ taken before $B$ commits, $A$ deterministically returns $\{20,30\}$ — the snapshot at $t_s$ — regardless of interleaving, and $B$ never blocks. Cost: $O(|\text{result}| + c)$, with $c$ the overlapping updates helped.

---
*Part of the [DBMS Research catalog](../../README.md).*
