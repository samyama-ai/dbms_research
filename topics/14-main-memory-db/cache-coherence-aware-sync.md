# Cache-Coherence-Aware Synchronization

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/cache-coherence-aware-sync` · **Status:** open

## 1. Problem Statement
On modern multi-socket machines the bottleneck for write-heavy concurrent data structures is not lock contention per se but the **cache-coherence protocol traffic** (MESI/MOESI invalidations, cross-socket interconnect messages) generated when many cores write shared cache lines. A single contended cache line serializes through the coherence directory, and each writer pays a remote-cache-to-cache transfer. The problem: **design synchronization primitives (locks, atomics, version counters, hand-over-hand schemes) that realize a given concurrent-structure semantics while minimizing the number of coherence messages / contended-line transfers per operation, ideally provably matching a coherence-traffic lower bound.**

Variants:
- *Decision:* given an abstract structure and a target traffic bound $t$ per op, does a linearizable implementation using $\le t$ coherence transfers per op exist?
- *Optimization:* minimize expected/worst-case coherence messages per operation (or per committed update).
- *Counting:* count remote line transfers as the cost metric, distinct from instruction count.

## 2. Mathematical Foundations
The right cost model is **not** the flat RAM/PRAM but a coherence-aware variant. Define $T_{\text{coh}}(op)$ = number of cache-line ownership transfers (state transitions M↔S↔I) charged to an operation; on a directory protocol each transfer is $\Omega(1)$ interconnect message, cross-socket ones costing a NUMA factor. This is captured by **distributed-shared-memory / message-passing complexity** rather than work-depth alone.

A foundational result: **MCS / queue locks** (Mellor-Crummey–Scott, TOCS 1991) reduce a contended lock from $\Omega(p)$ coherence traffic per acquisition (test-and-set spinning) to **$O(1)$ remote references per acquisition** — each spinner busy-waits on a *local* flag, so only the handoff touches a remote line. This is the canonical "coherence-traffic-optimal" mutual-exclusion result. The **remote-memory-reference (RMR) complexity** model (Yang–Anderson; Attiya–Hendler–Woelfel) formalizes this: count only references that traverse the interconnect. Lower bounds: Attiya–Hendler–Woelfel (STOC 2008) prove $\Omega(\log p)$ RMR-or-stall worst-case for mutual exclusion in the CC/DSM model. Read–write/read-mostly structures exploit that shared (S) state lets readers replicate a line without traffic; **writes** force invalidation of all sharers — so write-heavy is the hard regime, and the relevant quantity is the *sharer fan-out* invalidated per write.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **MCS** and **CLH** queue locks; **NUMA-aware locks** — **Cohort locks** (Dice–Marathe–Shavit, PPoPP 2012) and **ShflLock**/**CNA** (compact NUMA-aware, Linux kernel) keep the lock line on one socket to cut cross-socket transfers. **Read-mostly:** RCU (McKenney) and **read-optimized lock coupling / optimistic lock coupling (OLC)** (Leis et al., DaMoN 2016) used in ART/Bw-tree avoid reader coherence traffic via version validation. **Sloppy/biased counters**, **per-core sharded counters**, and **delegation/combining** — **Flat Combining** (Hendler–Incze–Shavit–Tzafrir, SPAA 2010) — move all updates to one core to localize the contended line.
- **Theory-SOTA:** RMR-complexity bounds for mutual exclusion (Attiya–Hendler–Woelfel) are the cleanest traffic lower bounds; combining-tree depth bounds for fetch-and-add.

## 4. Upper Bound
For mutual exclusion, MCS/CLH achieve **$O(1)$ RMR per passage** under the CC model — coherence-traffic-optimal for a single lock. For write-heavy counters/aggregates, **flat combining / combining trees** reduce $p$ concurrent updates to $O(\log p)$ or amortized $O(1)$ remote transfers by funneling through a combiner, beating $p$-way contention. Cohort/CNA locks bound cross-socket transfers to $O(1)$ per socket-handoff. Optimistic lock coupling gives readers **zero** coherence writes (validation reads shared lines), with writers paying only along their path.

## 5. Lower Bound
**Attiya–Hendler–Woelfel (STOC 2008):** any mutual-exclusion algorithm in the CC or DSM model has worst-case RMR complexity $\Omega(\log p)$ (a passage incurring that many remote references or stalls) — you cannot make every acquisition $O(1)$ in the worst case. For a single shared write-target, the coherence protocol forces $\Omega(s)$ invalidation messages to evict $s$ sharers per write — an unavoidable fan-out cost intrinsic to invalidation-based coherence. **Cell-probe / information-theoretic** arguments lower-bound any counter that must reflect $p$ contributions, and **Jayanti**-style bounds give $\Omega(\log p)$ for many linearizable objects. These hold in the asynchronous shared-memory model with a coherence cost metric.

## 6. The Gap
Mutual exclusion has nearly matching $\Theta(\log p)$-ish RMR bounds, but for **general write-heavy concurrent structures** (ordered maps, multi-word updates) there is **no tight characterization** of minimum coherence traffic — upper bounds (combining, sharding, NUMA-aware) are constructions without matching per-structure lower bounds, and real protocols (directory vs snoop, MOESI O-state cache-to-cache) are not modeled in the clean RMR cost. The problem is genuinely open: we lack a coherence-traffic complexity theory predicting the optimal primitive for a given structure and workload.

## 7. Current Research (as of June 2026)
Threads: delegation/combining generalized to arbitrary structures; NUMA- and CXL-fabric-aware locks where "remote" now spans pooled memory with non-uniform coherence cost *(frontier — verify)*; hardware-transactional-memory + coherence co-design; modeling MOESI cache-to-cache forwarding in RMR analysis. Groups: Tel Aviv / Oracle Labs (Shavit/Dice/Marathe), MIT (Shun/Kaashoek lineage), EPFL (Falsafi/Guerraoui), TUM (Leis — OLC), Waterloo/Calgary (Woelfel — RMR theory).

## 8. Future Work
- A coherence-traffic complexity model that captures directory vs snoop and O-state forwarding, with matching bounds.
- Provably traffic-optimal primitives for ordered maps and multi-word CAS under write-heavy loads.
- Synchronization tuned to CXL/heterogeneous coherence domains with non-uniform transfer cost.

## 9. Key References
- **[Foundational]** Mellor-Crummey, J., Scott, M. *Algorithms for Scalable Synchronization on Shared-Memory Multiprocessors.* ACM TOCS, 1991. — [DOI](https://doi.org/10.1145/103727.103729)
- **[Foundational]** Attiya, H., Hendler, D., Woelfel, P. *Tight RMR Lower Bounds for Mutual Exclusion and Other Problems.* STOC, 2008. — [PDF](https://hagit.net.technion.ac.il/files/2015/09/AHW-STOC08.pdf)
- **[SOTA]** Hendler, D., Incze, I., Shavit, N., Tzafrir, M. *Flat Combining and the Synchronization-Parallelism Tradeoff.* SPAA, 2010. — [DOI](https://doi.org/10.1145/1810479.1810540)
- **[SOTA]** Dice, D., Marathe, V., Shavit, N. *Lock Cohorting: A General Technique for Designing NUMA Locks.* PPoPP, 2012. — [DOI](https://doi.org/10.1145/2370036.2145848)
- **[SOTA]** Leis, V., Scheibner, F., Kemper, A., Neumann, T. *The ART of Practical Synchronization (Optimistic Lock Coupling).* DaMoN, 2016. — [DBLP](https://dblp.org/rec/conf/damon/LeisSK016.html)
- **[Survey]** Herlihy, M., Shavit, N. *The Art of Multiprocessor Programming.* Morgan Kaufmann, 2nd ed., 2020. — [Publisher](https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming)

## 10. Worked Example

Consider $p = 8$ cores hammering one shared counter. With a naive test-and-set / `lock xadd` on a single cache line, each increment must acquire the line in M state, invalidating the other 7 sharers: per successful update the directory issues $\Omega(p)$ invalidation/transfer messages, so $p$ updates cost $\Theta(p^2) = 64$ coherence transfers — quadratic, the contention collapse.

Now apply **flat combining**: one core becomes the combiner, reads a publication list of the other 7 pending requests (each spinning on its own *local* flag, no remote write), applies all 8 increments locally, and writes back once. The contended line moves $O(1)$ times per combining round, so $p$ updates cost $\Theta(p)$ transfers — here $\approx 8$ instead of 64, an $8\times$ reduction.

For the mutual-exclusion handoff itself, an MCS queue lock makes each waiter spin on a local node, so a passage costs $O(1)$ remote references — but the Attiya–Hendler–Woelfel bound says worst-case RMR is still $\Omega(\log p) = 3$ here, unavoidable.

---
*Part of the [DBMS Research catalog](../../README.md).*
