---
id: 14-main-memory-db/htm-for-in-memory-indexes
title: "Hardware Transactional Memory for Indexes"
topic: 14-main-memory-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Hardware Transactional Memory for Indexes

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/htm-for-in-memory-indexes` · **Status:** empirically-open

## 1. Problem Statement
Hardware Transactional Memory (HTM) — e.g., Intel TSX (RTM/HLE), IBM POWER8 TM — lets a thread execute a region speculatively: reads and writes are buffered in cache, and the region either **commits atomically** or **aborts**, rolling back transparently. The promise for IMDB indexes is enormous: replace hand-crafted latch-free protocols with simple coarse-grained critical sections that *behave* fine-grained, getting concurrency "for free."

**The question is empirical, not existential:** *Can HTM deliver robust, abort-resilient synchronization for concurrent in-memory indexes in practice?* HTM is **best-effort** — transactions can abort for reasons unrelated to data conflicts (capacity overflow of the L1 read/write set, interrupts, page faults, system calls, false sharing), and a fallback path is always mandatory. The problem is to determine whether, and under what index designs and workloads, HTM yields *robust* throughput rather than collapsing into fallback-lock serialization.

Variants: *(throughput)* maximize committed ops/s under bounded abort rate; *(design)* index/node layout that keeps read-write sets within hardware capacity; *(robustness)* worst-case behavior under adversarial conflict and capacity pressure.

## 2. Mathematical Foundations
Model an HTM region as a speculative read set $R$ and write set $W$ tracked at cache-line granularity in a structure of capacity $C$ (L1 lines, with associativity $a$). A transaction commits iff (i) $|R\cup W|$ fits (no capacity/associativity eviction) and (ii) no concurrent committer's write set intersects $R\cup W$ (conflict, detected by the cache-coherence protocol, typically MESI extended). Abort probability decomposes as
$$P_{\text{abort}} = 1-(1-p_{\text{cap}})(1-p_{\text{conf}})(1-p_{\text{other}}),$$
where $p_{\text{cap}}$ rises sharply once $|R\cup W|$ approaches $C$, and $p_{\text{conf}}$ scales with contention and region length. Expected throughput with a global fallback lock follows a **lemming-effect** model: once one thread takes the fallback lock, all concurrent HTM transactions that read the lock abort, so the steady state can degenerate to serial. The design objective is to keep $\mathbb{E}[|R\cup W|]$ small (favoring B-trees over tries, narrow nodes) and region length short, since both $p_{\text{cap}}$ and $p_{\text{conf}}$ are monotone in them.

## 3. State of the Art (SOTA)
- **HTM-based B-tree / DBX** (Wang, Qian, Li, Chen — *Using Restricted Transactional Memory to Build a Scalable In-Memory Database*, EuroSys 2014): HTM for both index and transaction execution; shows real speedups with careful read-set sizing.
- **Leis, Kemper, Neumann** (*Exploiting Hardware Transactional Memory in Main-Memory Databases*, ICDE 2014): timestamp-based fallback + transaction chopping to keep HTM regions within capacity; foundational systems study.
- **Makreshanski, Levandoski, Stutsman** (*To Lock, Swap, or Elide: On the Interplay of HTM and Lock-Free Indexing*, VLDB 2015): directly compares HTM-elision vs. lock-free Bw-tree — finds HTM competitive but capacity- and design-sensitive, the canonical "it depends" result.
- Hardware reality: Intel TSX disabled/deprecated on many client SKUs after errata (TAA side-channel mitigations); availability is now a moving target.

## 4. Upper Bound
Where read-write sets stay within L1 capacity and contention is low-to-moderate, HTM lock elision matches or beats fine-grained latching with far simpler code: traversal + single-node update fits in one short transaction, committing in $O(\log n)$ with near-zero synchronization overhead and full multicore scaling (DBX, Leis et al.). Best-case: coarse critical sections delivering fine-grained throughput, with provably no extra cache-line writes beyond the data path.

## 5. Lower Bound
HTM offers **no progress guarantee**: it is best-effort, so there is no wait-free or even lock-free bound — a transaction may abort indefinitely (livelock) and *must* have a non-HTM fallback (Herlihy-Moss original TM, and every real ISA). Capacity is a hard physical floor: any region whose footprint exceeds L1 ($|R\cup W|>C$) aborts *deterministically*, independent of contention — a structural lower bound on what HTM can protect (large-node tries, long range scans). Under contention, the lemming/lock-convoy effect caps throughput at the fallback-lock's serial rate. Thus worst-case HTM throughput is provably no better than a global lock.

## 6. The Gap
Because the lower bound is "no guarantee" and the upper bound is "great when it fits," the gap is **fundamentally empirical and hardware-coupled** — hence *empirically-open*. There is no algorithm that converts HTM's best-effort nature into a worst-case guarantee without a fallback, and no clean theory predicts the commit/abort frontier for a given index + workload + microarchitecture. Closing it means either (a) hardware with stronger capacity/progress guarantees, or (b) a robust software discipline (adaptive region sizing, fallback that avoids the lemming effect) with proven contention-bounded throughput.

## 7. Current Research (as of June 2026)
- HTM availability is the gating issue: TSX deprecation pushes attention toward AMD/ARM TME-like and research RTM, and toward persistent-memory + HTM for crash-atomic index updates *(frontier — verify)*.
- Adaptive elision controllers (predict abort, switch to lock-free path per operation) and HTM for *persistent* B+-trees / range indexes on CXL memory *(frontier — verify)*.
- Groups: TUM (Leis/Neumann), Microsoft Research (Levandoski/Lomet), SJTU IPADS (Chen — DBX lineage), Utah (Stutsman).

## 8. Future Work
- Co-designed index node layouts guaranteed to fit hardware read/write-set capacity.
- Fallback protocols that provably avoid the lemming effect while preserving serializability.
- A predictive model mapping (index, workload, microarchitecture) to commit probability validated across vendors.
- Reassessing HTM viability on post-TSX hardware and persistent memory.

## 9. Key References
- **[Foundational]** M. Herlihy, J. E. B. Moss. *Transactional Memory: Architectural Support for Lock-Free Data Structures.* ISCA, 1993. — [DOI](https://doi.org/10.1145/165123.165164)
- **[SOTA]** D. Makreshanski, J. Levandoski, R. Stutsman. *To Lock, Swap, or Elide: On the Interplay of Hardware Transactional Memory and Lock-Free Indexing.* VLDB, 2015. — [PVLDB](http://www.vldb.org/pvldb/vol8/p1298-makreshanski.pdf)
- **[SOTA]** V. Leis, A. Kemper, T. Neumann. *Exploiting Hardware Transactional Memory in Main-Memory Databases.* ICDE, 2014. — [DBLP](https://dblp.org/rec/conf/icde/LeisK014.html)
- **[SOTA]** Z. Wang, H. Qian, J. Li, H. Chen. *Using Restricted Transactional Memory to Build a Scalable In-Memory Database (DBX).* EuroSys, 2014. — [DBLP](https://dblp.org/rec/conf/eurosys/WangQLC14.html)
- **[Survey]** T. Harris, J. Larus, R. Rajwar. *Transactional Memory (2nd ed.).* Morgan & Claypool, 2010. — [DOI](https://doi.org/10.1007/978-3-031-01728-5)

## 10. Worked Example

Consider an HTM lock-elision update on a B+-tree leaf vs. a radix-trie node, with an L1 read/write-set capacity of $C = 512$ cache lines (a typical 32 KB L1 at 64 B/line).

**B+-tree path:** an insert traverses 4 levels, touching one 256 B node per level (4 cache lines each) plus a single leaf write (4 lines): $|R\cup W| \approx 5\times 4 = 20$ lines $\ll C$. The region fits, so $p_{\text{cap}}\approx 0$; with low contention the transaction commits in one RTM region.

**Wide-trie node:** a single 4096-entry trie node spans $4096\times 8\,\text{B} = 32\,\text{KB} = 512$ lines $= C$ exactly. Reading it for a scan *deterministically* overflows the read set (associativity evicts before completion), so $p_{\text{cap}}\to 1$ — the region **always aborts** to the fallback lock, regardless of contention.

Plugging into $P_{\text{abort}} = 1-(1-p_{\text{cap}})(1-p_{\text{conf}})(1-p_{\text{other}})$: the B+-tree leaf gives $P_{\text{abort}}\approx p_{\text{other}}$ (near 0), while the wide trie gives $P_{\text{abort}}\approx 1$. This is the structural lower bound in action: footprint, not just contention, decides whether HTM helps.

---
*Part of the [DBMS Research catalog](../../README.md).*
