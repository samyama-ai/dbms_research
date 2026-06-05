# Optimal Memory Reclamation Scheme

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/safe-memory-reclamation` · **Status:** open

## 1. Problem Statement

In a concurrent in-memory index, a node unlinked by one thread may still be referenced by
another thread that read a pointer to it before the unlink. **Safe memory reclamation
(SMR)** is the problem of deciding *when* a removed object can be freed/reused so that no
thread dereferences a dangling pointer (no use-after-free, no ABA). We seek a reclamation
scheme that is simultaneously:

1. **Lock-free / non-blocking:** a stalled or crashed thread cannot prevent other threads
   from making progress *and* cannot prevent reclamation indefinitely (no unbounded
   reclamation blocking);
2. **Bounded garbage:** the number of unreclaimed-but-retired objects is bounded by a
   function of the number of active threads/reservations — $O(T \cdot k)$, not unbounded;
3. **Low overhead:** $O(1)$ amortized, ideally with few memory fences per protected access
   on the read path.

The triple goal "lock-free **and** bounded-garbage **and** low-overhead" is the open
question — known schemes achieve at most two.

- **Decision variant:** does scheme $X$ guarantee bounded garbage under thread crashes?
- **Optimization variant:** minimize per-access fences / bound garbage given $T$ threads.

## 2. Mathematical Foundations

Model: a set of threads performing operations on a shared structure; each operation has a
set of **hazardous accesses** to nodes. A reclamation scheme provides *protect/retire*
primitives. Correctness: an object retired at time $t$ may be freed only after no thread
holds a *reservation* that could dereference it — formally, after all *grace periods*
covering reads that observed it have elapsed.

Key impossibility-style result (Alistarh, Leiserson, Matveev, Shavit; and Singh, Lorenz,
Petrank): there is a tension between **robustness** (bounded garbage under arbitrary
thread delays) and **lock-freedom with $O(1)$ overhead**. Epoch-based reclamation (EBR)
is fast and $O(1)$ but **not robust**: one stalled thread pins an epoch and lets garbage
grow unboundedly. Hazard pointers (HP, Michael) are robust (garbage $\le 2T \cdot$ max
hazards) but pay a fence and a per-access store on the read path. The design space is a
Pareto frontier in $(\text{robustness}, \text{read-path fences}, \text{garbage bound})$.

A formalization uses **interval-linearizability / reservation intervals**: each access
reserves a logical interval $[a,b]$; an object retired at $r$ is reclaimable when no
reservation interval contains $r$. Schemes differ in how cheaply they track intervals.

## 3. State of the Art (SOTA)

- **Hazard Pointers** (M. Michael, IEEE TPDS 2004): robust, bounded garbage, but a store
  + fence per protected pointer.
- **Epoch-Based Reclamation / RCU** (Fraser 2004; McKenney): minimal read overhead, not
  robust.
- **Interval-Based Reclamation (IBR)** and **Hazard Eras (HE)** (Ramalhete & Correia 2017;
  Nikolaev & Ravindran 2018): bound garbage with era stamps, fewer fences than HP.
- **Hyaline** (Nikolaev & Ravindran, DISC 2019 / PODC): lock-free, robust, with low
  overhead via reference-counted retirement batches — among the closest to the triple
  goal.
- **WFE / Crystalline** and **VBR (Version-Based Reclamation)** (Sheffer & Petrank 2023)
  push toward wait-free and near-zero read overhead.

Database engines often sidestep with **quiescent-state / epoch GC** (e.g., Silo, Masstree,
PostgreSQL-style) accepting EBR's non-robustness.

## 4. Upper Bound

Hazard pointers give garbage $\le R \cdot T \cdot H$ (retire batch $R$, threads $T$, max
hazards $H$) with $O(1)$ amortized per-retire and one fence per protected access. Hyaline
and Crystalline achieve robustness with $O(1)$ expected overhead and bounded garbage
proportional to active reservations, with read-path fences reduced versus HP. VBR
approaches near-zero read overhead by reusing version stamps. So an upper bound exists for
*each pair* of properties; the contested claim is achieving all three with truly $O(1)$
read-path cost and worst-case (not expected) bounds.

## 5. Lower Bound

Lower bounds are partial. There is a known trade-off result: any reclamation scheme that
is **robust** (bounded garbage under arbitrary delays) must, on the read path, perform
synchronization that prevents the pure "epoch-announce only" $O(1)$-no-fence behavior —
intuitively a thread must publish enough to protect what it reads, costing $\Omega(1)$
fences/stores per hazardous access in the worst case. No fully general matching lower
bound (e.g., "any robust lock-free SMR needs $\ge f(T)$ fences") is established; the
question of whether robustness, lock-freedom, and zero-extra-fence reads are mutually
exclusive remains formally open.

## 6. The Gap

The gap is the *triple*: lock-free **+** bounded-garbage-under-crashes **+** truly
low (ideally fence-free) read overhead, with **worst-case** guarantees. Hyaline/Crystalline/
VBR get close but rely on expected bounds, reference counting overhead, or special
allocators. We lack (a) a proof that the triple is impossible, or (b) a scheme provably
achieving it. Closing it requires either an impossibility theorem in an agreed model or a
new primitive (possibly hardware-assisted, e.g., load-link/store-conditional or
transactional reads) that breaks the trade-off.

## 7. Current Research (as of June 2026)

Active: **wait-free** reclamation with bounded garbage (Petrank's group, Technion —
VBR/Crystalline lineage) *(frontier — verify)*; hardware-assisted SMR using HTM or
specialized load instructions; integrating SMR with allocator design to bound true memory
footprint, not just retired-object count; reclamation for **persistent**-memory indexes
where "freed" must also be crash-consistent. Groups: Technion (Petrank), Virginia Tech
(Ravindran/Nikolaev), MIT/Brown (Scott lineage), DB engine teams (CMU-DB, TUM) adopting
fast EBR variants.

## 8. Future Work

- An impossibility theorem or a matching scheme for the lock-free/bounded/low-overhead triple.
- Worst-case (not expected) bounds for Hyaline-class schemes.
- Crash-consistent reclamation for NVM/CXL indexes.
- Hardware primitives (LL/SC, HTM, tagged pointers) that make robust reads fence-free.

## 9. Key References

- **[Foundational]** M. Michael. *Hazard Pointers: Safe Memory Reclamation for Lock-Free Objects.* IEEE TPDS, 2004.
- **[Foundational]** K. Fraser. *Practical Lock-Freedom.* PhD thesis / RCU lineage (McKenney), 2004.
- **[SOTA]** R. Nikolaev, B. Ravindran. *Hyaline: Fast and Transparent Lock-Free Memory Reclamation.* PODC / DISC, 2019.
- **[SOTA]** G. Sheffer, E. Petrank. *Wait-Free / Version-Based Reclamation (VBR, Crystalline).* PPoPP, 2021–2023.
- **[Survey]** P. Singh, T. A. Brown, et al. *A Survey of Concurrent Memory Reclamation Techniques.* (comparative study), 2020s.

---
*Part of the [DBMS Research catalog](../../README.md).*
