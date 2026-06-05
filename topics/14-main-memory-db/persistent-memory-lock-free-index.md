# Persistent Memory Lock-Free Indexes

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/persistent-memory-lock-free-index` · **Status:** empirically-open

## 1. Problem Statement

Design an ordered (or hash) index over byte-addressable **non-volatile memory (NVM)** —
e.g., Intel Optane DCPMM, or CXL-attached persistent memory — that is simultaneously:

1. **Lock-free** (or at least non-blocking): some operation completes in a bounded number
   of steps regardless of thread delays;
2. **Crash-consistent / durably linearizable:** after a power loss, recovery yields a
   state consistent with a linearization of all operations whose effects were
   *persisted*, with no torn or lost structural invariants;
3. **Low flush overhead:** minimize the number of expensive cacheline flushes
   (`clwb`/`clflushopt`) and store fences (`sfence`) on the critical path, since these,
   not DRAM-style stores, dominate cost.

- **Decision variant:** does a given index design satisfy durable linearizability under
  the persistency model $M$?
- **Optimization variant:** minimize persist-ordering operations (flushes+fences) per
  insert/lookup while preserving (1)–(2).

"Solving" empirically means matching a DRAM lock-free index's throughput within a small
constant while guaranteeing recovery; the problem is *empirically-open* because no design
dominates across read-heavy, write-heavy, skewed, and range-scan workloads.

## 2. Mathematical Foundations

**Persistency model.** Memory has a volatile cache and persistent domain. A store becomes
durable only after an explicit flush + fence; otherwise caches may evict in arbitrary
order. Formally this is **strict/epoch persistency** (Pelley et al.) over a relaxed memory
model. The correctness target is **durable linearizability** (Izraelevitz, Mendes,
Scott, DISC 2016): every operation that returns before the crash is linearized, and the
recovered history is a linearization of persisted operations; the stronger **buffered
durable linearizability** allows a bounded suffix to be lost.

**Cost model.** Let an operation issue $p$ persist barriers (flush+fence). The relevant
complexity measure is *persist-instruction count* $p$ and *persist-critical-path length*,
analogous to work/depth. Lower-bound arguments use the observation that any visible
durable update to object $x$ depending on $y$ needs a persist ordering $y \prec x$,
forcing at least one fence — a *persistence happens-before* constraint.

**Recovery correctness.** An index is recoverable iff there exists a recovery function
$R$ such that for every reachable crash state $c$, $R(c)$ is a valid index whose abstract
contents equal the set of durably-completed operations. This is typically argued via a
*persistent invariant*: the structure is always recoverable from any single interrupted
operation (helping/log-free) or via a small per-operation redo descriptor.

## 3. State of the Art (SOTA)

**Systems SOTA.** **BzTree** (Arulraj, Levandoski, Minhas, Larson, VLDB 2018) is a
lock-free persistent B-tree built on a persistent multi-word CAS (PMwCAS). **FAST&FAIR**
(Hwang et al., FAST 2018) gives a failure-atomic B+-tree using ordered shifts that
tolerate transient inconsistency without logging. **DASH** and **CCEH** (Nam et al., FAST
2019) are crash-consistent extendible hash tables minimizing flushes. **RECIPE**
(Lee et al., SOSP 2019) is a *construction*: convert a DRAM concurrent index into a
crash-consistent NVM one when it satisfies certain isolation conditions. **PACTree**,
**ROART**, and **APEX** push range-scan and learned-index variants.

**Theory SOTA.** Durable linearizability and its log-free / detectable variants
(Friedman, Herlihy, Marathe, Petrank, PPoPP 2018 — *detectable* objects) give the
correctness framework and generic but costly transforms.

## 4. Upper Bound

Generic transforms (Izraelevitz et al.; RECIPE) make a DRAM lock-free index durably
linearizable with $O(1)$ extra flushes per linearization point under stated conditions.
Hand-tuned structures (FAST&FAIR, BzTree) achieve $O(\log n)$ traversal with a *small
constant* number of persist barriers per update — often 1–3 fences for an insert — and
$O(1)$ for lookups (no persistence on read). Recovery is $O(n)$ worst case but can be
$O(\text{in-flight ops})$ with detectable descriptors.

## 5. Lower Bound

There is a *persistence cost* lower bound: any durably-linearizable implementation of an
object whose updates have real dependencies must issue $\Omega(1)$ persist fences per
update in the worst case — you cannot make a dependent durable update visible without
ordering its predecessor (a consequence of the persistence happens-before order). For
some objects the *amortized* fence count is provably $\ge 1$ per update. Cell-probe and
classical lock-free lower bounds (e.g., $\Omega(n)$ space for certain wait-free objects,
CAS contention bounds) carry over and compound with persistence. No general tight bound
on minimal fences-per-operation as a function of the data structure is known.

## 6. The Gap

Empirically, the best NVM indexes still trail their DRAM counterparts (Optane's
asymmetric read/write latency and limited write bandwidth amplify each flush), and no
single design wins across workloads. The theory gap: we lack a tight per-structure lower
bound on persist barriers, so we cannot certify any index as flush-optimal. The retreat
of Optane (discontinued) and shift to CXL persistent memory has changed the cost
constants, reopening which trade-offs matter. Closing the gap needs (a) matched
fence-count lower/upper bounds for ordered maps, and (b) a hardware-stable cost model.

## 7. Current Research (as of June 2026)

Active directions: porting persistent-index ideas to **CXL-attached memory** with very
different latency/bandwidth and cache-coherence semantics *(frontier — verify)*;
**detectable / recoverable** lock-free objects with provable recovery and minimal
helping (Petrank, Friedman); learned and hybrid NVM indexes (APEX successors);
log-free failure-atomic primitives. Groups: Technion (Petrank), UT Austin (Vijaykumar/
Witchel lineage, RECIPE/PACTree authors), CMU, Wisconsin. Post-Optane work re-validates
results on emulated/CXL persistent memory.

## 8. Future Work

- Tight lower bounds on persist barriers per operation for ordered maps and hash tables.
- A workload-robust design dominating across read/write/scan/skew.
- CXL-persistency models and indexes co-designed with hardware persist domains.
- Verified recovery: machine-checked proofs of durable linearizability for real indexes.

## 9. Key References

- **[Foundational]** J. Izraelevitz, H. Mendes, M. L. Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23)
- **[SOTA]** J. Arulraj, J. Levandoski, U. F. Minhas, P.-A. Larson. *BzTree: A High-Performance Latch-free Range Index for Non-Volatile Memory.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3164135.3164147)
- **[SOTA]** S. K. Lee, J. Mohan, S. Kashyap, T. Kim, V. Chidambaram. *RECIPE: Converting Concurrent DRAM Indexes to Persistent-Memory Indexes.* SOSP, 2019. — [arXiv](https://arxiv.org/abs/1909.13670)
- **[SOTA]** D. Hwang, W. Kim, Y. Won, B. Nam. *Endurable Transient Inconsistency in Byte-Addressable Persistent B+-Tree (FAST&FAIR).* FAST, 2018. — [USENIX](https://www.usenix.org/conference/fast18/presentation/hwang)
- **[Foundational]** M. Friedman, M. Herlihy, V. Marathe, E. Petrank. *A Persistent Lock-Free Queue for Non-Volatile Memory.* PPoPP, 2018. — [DOI](https://doi.org/10.1145/3178487.3178490)

## 10. Worked Example

Consider inserting key $42$ into a persistent linked list $H \to n_5 \to \text{NULL}$,
where the new node $n_{42}$ must point to $n_5$ and $H$ must then point to $n_{42}$.
Naively: (1) allocate $n_{42}$, set $n_{42}.\text{next} = n_5$; (2) CAS $H.\text{next}$ from
$n_5$ to $n_{42}$. For *durability*, persistence-happens-before forces $n_{42}$'s contents
to reach NVM **before** $H$'s updated pointer does. So the trace is:

1. write $n_{42}.\text{key}=42$, $n_{42}.\text{next}=n_5$;
2. `clwb(n_42)` + `sfence` — persist the node ($1$ barrier);
3. CAS $H.\text{next} \to n_{42}$;
4. `clwb(&H.next)` + `sfence` — persist the link ($1$ barrier).

If a crash strikes between steps 3 and 4, recovery sees $H$ still pointing at $n_5$:
$n_{42}$ is unreachable garbage but the list invariant holds — durably linearizable, with
the insert simply not having taken effect. Total cost: $p=2$ persist barriers, matching
the $\Omega(1)$ lower bound for a dependent durable update. Reordering steps 2 and 3 would
risk persisting a dangling $H.\text{next}$ pointing to non-durable memory.

---
*Part of the [DBMS Research catalog](../../README.md).*
