# Lower Bounds on Lock-Manager Throughput

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/lock-manager-scalability-bounds` · **Status:** empirically-open

## 1. Problem Statement

A centralized **lock manager** mediates acquire/release of locks, traditionally via a shared hash table of lock-request queues guarded by latches. On many-core hardware this central structure becomes a scalability bottleneck: latch contention, cache-line ping-pong, and remote-memory traffic cap throughput well below linear in core count. The problem: **establish fundamental lower bounds on the throughput / per-operation cost of a centralized lock manager** as a function of core count $p$, and identify which costs are intrinsic (irreducible by clever engineering) versus implementation artifacts.

- **Optimization framing:** maximize lock-ops/sec; minimize per-op latency and cache traffic.
- **Lower-bound framing:** what is the minimum unavoidable synchronization cost (cache misses, RMW operations, memory stalls) per lock operation on a shared-memory machine with $p$ cores?

This is an *empirically-open* problem: practice repeatedly bumps into a ceiling, but matching theoretical lower bounds are sparse.

## 2. Mathematical Foundations

Model the machine as an **asynchronous shared-memory** system with $p$ processes, atomic read/write and read-modify-write (CAS/FAA) primitives, and a cache-coherent memory whose cost metric counts **remote cache-line accesses** (cache-coherence steps) and **stalls** (concurrent accesses to one location serialize). Two relevant lower-bound regimes:

- **Contended hot lock:** if $c$ transactions contend a single lock, any mutual-exclusion or RMW-based protocol incurs $\Omega(c)$ serialized coherence operations on the shared line — a *stall complexity* bound; the line becomes a sequential bottleneck with throughput $O(1/\text{coherence-latency})$ regardless of $p$.
- **Aggregate:** distributing locks reduces per-line contention, but a *centralized* manager still funnels metadata (allocation, deadlock detection, queue maintenance) through shared state. The relevant theory is the **cache-coherence / RMW lower-bound** literature (Dwork–Herlihy–Waarts stall complexity; Attiya–Hendler–Woelfel RMW lower bounds), which gives $\Omega(\log p)$ or $\Omega(p)$ bounds depending on the operation and contention model.

$$\text{throughput} \le \frac{p}{1 + \beta\cdot(\text{shared-line coherence steps per op})}.$$

## 3. State of the Art (SOTA)

**Systems-SOTA:** the dominant finding is that *centralized lock managers do not scale*, motivating designs that **co-locate lock state with the tuple** and avoid a central table: **very lightweight locking (VLL)** (Ren, Thomson, Abadi, VLDB 2013), per-tuple latch/version words in main-memory engines (Silo, Tu et al., SOSP 2013, which avoids a shared lock manager entirely via OCC), Hekaton's lock-free MVCC, and **MOCC/Foedus** for many-core. Studies by **Yu, Bezerra, Pavlo, Devadas, Stonebraker (VLDB 2014)** evaluated CC schemes on 1000 cores in simulation and pinpointed the centralized-structure and cache-coherence walls. **Theory-SOTA:** shared-memory lower bounds (stall complexity, RMW complexity, the MCS/queue-lock optimality results) supply the relevant impossibility scaffolding but are rarely connected directly to DBMS lock-manager throughput.

## 4. Upper Bound

Decentralized designs largely *sidestep* the bound: per-tuple latching and OCC make the common-path cost $O(1)$ cache-local operations, scaling near-linearly until data hot-spots reappear. Queue locks (MCS/CLH) give $O(1)$ remote accesses per acquisition under contention — the known optimal for spin locks. For a genuinely *centralized* manager, the best engineering (sharded latches, lock-free queues) reduces but cannot remove funneling through shared allocation/deadlock state, so its throughput plateaus.

## 5. Lower Bound

On a hot lock contended by $c$ cores, any protocol incurs $\Omega(c)$ serialized coherence operations — a stall-complexity bound implying the line caps at coherence-latency-bounded throughput independent of $p$ (Dwork–Herlihy–Waarts). For mutual exclusion, the RMW/remote-access lower bounds (Attiya–Hendler–Woelfel; Anderson–Kim) give $\Omega(\log p / \log\log p)$-type bounds per passage in some models. These are **shared-memory model** results: they bound the *primitive* a lock manager builds on, but a tight, DBMS-specific lower bound on end-to-end lock-manager throughput (folding in deadlock detection, allocation, and queue maintenance) is **not established**.

## 6. The Gap

**Empirically-open.** Experiments (1000-core studies) consistently show centralized lock managers stalling, and theory gives clean lower bounds on the *underlying synchronization primitives*. The gap: no theorem ties these primitive-level bounds into a tight lower bound on *aggregate lock-manager throughput* for realistic workloads, nor proves that decentralized per-tuple schemes are optimal up to constants. Closing it requires a cost model spanning coherence traffic, deadlock detection, and memory allocation, plus matching upper-bound constructions.

## 7. Current Research (as of June 2026)

Active directions: scaling CC to hundreds/thousands of cores and to **disaggregated / RDMA** memory where the "lock manager" spans nodes and the coherence model changes *(frontier — verify)*; NUMA- and cache-aware lock placement; and learned/adaptive switching between centralized locking and OCC by contention. The MIT (Devadas/Madden), CMU (Pavlo), and TUM (Leis/Neumann) groups remain central; shared-memory theory groups continue refining RMW and stall lower bounds relevant to the primitive layer.

## 8. Future Work

- A tight, DBMS-specific lower bound on centralized lock-manager throughput vs. core count.
- Provable optimality (or separation) of per-tuple/decentralized locking against any centralized design.
- Cost models and bounds for RDMA/disaggregated and NUMA lock management.
- Adaptive managers with proven worst-case guarantees across contention regimes.

## 9. Key References

- **[SOTA]** Yu, X.; Bezerra, G.; Pavlo, A.; Devadas, S.; Stonebraker, M. *Staring into the Abyss: An Evaluation of Concurrency Control with One Thousand Cores.* PVLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735511)
- **[SOTA]** Ren, K.; Thomson, A.; Abadi, D. J. *Lightweight Locking for Main Memory Database Systems (VLL).* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2535568.2448947)
- **[SOTA]** Tu, S.; Zheng, W.; Kohler, E.; Liskov, B.; Madden, S. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[Foundational]** Dwork, C.; Herlihy, M.; Waarts, O. *Contention in Shared Memory Algorithms.* JACM, 1997. — [DOI](https://doi.org/10.1145/268999.269000)
- **[Foundational]** Mellor-Crummey, J. M.; Scott, M. L. *Algorithms for Scalable Synchronization on Shared-Memory Multiprocessors.* ACM TOCS, 1991. — [DOI](https://doi.org/10.1145/103727.103729)
- **[Foundational]** Attiya, H.; Hendler, D.; Woelfel, P. *Tight RMR Lower Bounds for Mutual Exclusion and Other Problems.* STOC, 2008. — [DOI](https://doi.org/10.1145/1374376.1374410)

## 10. Worked Example

Suppose $c=8$ cores all try to lock the same hot tuple (e.g., a counter row) via a centralized manager whose queue head sits on one cache line. Each acquire is a CAS on that line. Cache coherence serializes the 8 CAS attempts: the line must migrate (Modified state) to each core in turn, and each migration costs one coherence round-trip of latency $L \approx 100$ ns.

By the stall-complexity bound, the line incurs $\Omega(c)$ serialized coherence operations, so draining all 8 acquirers takes $\ge 8L = 800$ ns, giving throughput $\le c/(cL) = 1/L \approx 10^7$ lock-ops/s on that line — **independent of total core count $p$**. Adding cores past 8 does not help; they just lengthen the queue.

Contrast a per-tuple latch (Silo/OCC style): if the 8 cores touch 8 *distinct* tuples, each CAS hits a private line, all proceed in parallel in $\approx L$, giving $8/L \approx 8\times10^7$ ops/s — near-linear. The bound bites only when the access set collapses to one line; this is exactly why decentralized schemes "sidestep" rather than break the lower bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
