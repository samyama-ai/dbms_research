# Persistent-memory crash-consistency proofs

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/pmem-crash-consistency-proofs` · **Status:** partially-solved

## 1. Problem Statement

Persistent-memory (PMEM/NVM, CXL-attached) data structures — indexes, allocators, logs, queues — must survive a crash in a state from which a recovery routine reconstructs a consistent, durable structure. The difficulty is that the failure model is harsh and *realistic*: stores persist **out of order** (governed by a persistency model), a single store may be **torn** (partially persisted at sub-cache-line / non-8-byte granularity), and a crash can interrupt the recovery routine itself. Hand-written PMEM structures are notoriously buggy under exactly these conditions.

**Problem:** **formally verify crash consistency** of PMEM data structures under realistic out-of-order persistence and partial-write failure models — i.e., prove that for every reachable crash state (over all legal persist linearizations and all torn-write splits), the recovery procedure yields a state satisfying the structure's abstract invariant, and that operations are **durably linearizable** (Izraelevitz et al.).

Variants: (a) verify a *single structure* (B+-tree, hash map, allocator); (b) verify *under a specific persistency model* (Px86, ARMv8); (c) verify *compositionally* so verified structures combine; (d) the *model-checking / bug-finding* variant — automatically find crash-consistency bugs (not full proof).

## 2. Mathematical Foundations

The correctness criterion is **durable linearizability**: a history is durably linearizable iff it is linearizable and every operation that completed before a crash is reflected in the recovered state (and persists across further crashes); **buffered durable linearizability** relaxes this to an explicit sync point.

The semantic foundation is a **persistency model** giving a partial persist order $\le_{pm}$ over stores, plus a **crash relation** mapping a pre-crash memory + pending-store set to a post-crash persistent memory. Realistic models add: (i) **out-of-order** — any linearization of $\le_{pm}$ may be the persisted prefix; (ii) **torn writes** — a non-atomic store of width $> 8$ bytes may persist any subset of its bytes (only naturally-aligned 8-byte stores are typically atomic). The verification obligation is an invariant $I$ on persistent state such that:
$$\forall\, s \in \mathrm{Crash}(\text{exec}),\ I(\mathrm{Recover}(s)) \wedge \mathrm{abs}(\mathrm{Recover}(s)) = \text{committed prefix},$$
quantified over all crash states $s$ reachable under $\le_{pm}$ and all torn-write splits. Tools express this in **persistency-aware separation logics** (e.g., Spirea/Perennial-style "crash weakest preconditions" with a *post-crash resource* describing what survives). Idempotent recovery requires $\mathrm{Recover}\circ\mathrm{Recover} = \mathrm{Recover}$ to tolerate crash-during-recovery, proved via a well-founded measure.

## 3. State of the Art (SOTA)

- **Testing/model-checking SOTA (strong):** **Yat** (Lantz et al.), **PMTest** (Liu et al., ASPLOS 2019), **XFDetector** (Liu et al., ASPLOS 2020), **AGAMOTTO** (Neal et al., OSDI 2020, symbolic execution), **Jaaru/Witcher** (Gorjiara et al.; Fu et al., SOSP/OSDI 2021) — automatically find crash-consistency bugs in real PMEM code under out-of-order persistence. Widely used; finds real bugs but gives *no proof of absence*.
- **Proof SOTA (emerging):** **Perennial** crash separation logic extended to persistency; **Spirea** (Vindum & Birkedal) — a higher-order separation logic in Iris/Coq for verifying crash-safe PMEM programs under a release/acquire persistency model; **Pierogi** and PArmv8/Px86 program logics (Raad, Vafeiadis et al., POPL/PLDI 2020–2022). These verify nontrivial structures but full-featured, optimized PMEM indexes with torn-write reasoning remain hard — hence *partially-solved*.

## 4. Upper Bound

Achievable today: **machine-checked durable-linearizability proofs** for moderately complex lock-free PMEM structures (e.g., a persistent queue, Treiber-style stack, a durable map) in Iris/Spirea under a formal persistency model, including idempotent recovery. On the automated side, **bug-finding scales to real systems** (PMDK, NOVA, Redis-pmem) under out-of-order + 8-byte-atomicity models, exploring crash states efficiently via heuristics and persistency-aware pruning rather than full enumeration. Proof effort is high (10–20× code) but tractable for individual structures.

## 5. Lower Bound

The full verification problem is undecidable in general (arbitrary code + unbounded heaps); even *bounded* crash-consistency checking is hard because the crash-state space is **exponential**: $k$ pending stores yield up to $2^k$ persisted subsets under out-of-order persistence, and torn writes multiply this by the per-store split factor. This combinatorial blow-up is the practical "lower bound" — exhaustive model checking is infeasible, forcing heuristics (Witcher/Jaaru) that may miss bugs. There is no NP-hardness *theorem* that is the operative barrier; rather the barrier is (a) undecidability for full proofs and (b) exponential crash-state explosion for automated checking. Information-theoretically, torn-write tolerance again forces redundant validating bits (Section: atomicity floor) — you cannot verify torn-safety of a structure that stores no validating redundancy across non-atomic stores.

## 6. The Gap

The gap is between strong *bug-finding* (scales, but unsound — finds bugs, can't prove their absence) and *full proofs* (sound, but laborious and so far limited to individual, not-fully-optimized structures). Neither yet routinely handles **torn writes + out-of-order persistence + crash-during-recovery + lock-free concurrency** *together* for a production-grade index. Closing it needs: scalable proof automation (or sound-by-construction PMEM programming abstractions whose use *implies* crash consistency), and faithful torn-write models in the logics (many current proofs assume 8-byte atomicity and elide arbitrary tearing).

## 7. Current Research (as of June 2026)

Active: persistency-aware separation logics maturing (Spirea, Pierogi; Birkedal — Aarhus; Vafeiadis/Raad — MPI-SWS) toward richer models and more automation *(frontier — verify)*; combining symbolic execution (AGAMOTTO-style) with sound abstraction; verified PMEM allocators and transactional libraries (PMDK-like) *(frontier — verify)*; crash-consistency semantics for **CXL** persistent/shared memory, which differ from local PMEM *(frontier — verify)*. The bug-finding line (Witcher, Jaaru, Vinter) continues to harden real systems. A 2025–2026 thread targets *sound, near-automatic* verification of single-structure PMEM indexes under torn writes *(frontier — verify)*.

## 8. Future Work

- Faithful torn-write + out-of-order models inside scalable proof logics.
- Sound-by-construction PMEM abstractions (transactions, durable objects) that discharge crash-consistency proofs once for all clients.
- Compositional durable-linearizability so verified components combine.
- Verified crash consistency for CXL-attached and disaggregated persistent memory.

## 9. Key References

- **[Foundational]** Joseph Izraelevitz, Hammurabi Mendes, Michael L. Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23)
- **[SOTA]** Ian Neal, Ben Reeves, Ben Stoler, Andrew Quinn, Youngjin Kwon, Simon Peter, Baris Kasikci. *AGAMOTTO: How Persistent is your Persistent Memory Application?* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/neal) · [DBLP](https://dblp.org/rec/conf/osdi/NealRSQKPK20.html)
- **[SOTA]** Sihang Liu, Korakit Seemakhupt, Yizhou Wei, Thomas Wenisch, Aasheesh Kolli, Samira Khan. *Cross-Failure Bug Detection in Persistent Memory Programs (XFDetector).* ASPLOS, 2020. — [DOI](https://doi.org/10.1145/3373376.3378452)
- **[SOTA]** Simon Friis Vindum, Lars Birkedal. *Spirea: A Mechanized Concurrent Separation Logic for Weak Persistent Memory.* OOPSLA, 2023. — [DOI](https://doi.org/10.1145/3622820)
- **[SOTA]** Azalea Raad, John Wickerson, Gil Neiger, Viktor Vafeiadis. *Persistency Semantics of the Intel-x86 Architecture (Px86).* POPL, 2020. — [DBLP](https://dblp.org/rec/journals/pacmpl/RaadWNV20.html)

## 10. Worked Example

Consider a persistent singly-linked stack push: allocate node $n$, write $n.\text{val}=7$, write $n.\text{next}=\text{head}$, then publish $\text{head}=n$. Recovery invariant $I$: every node reachable from $\text{head}$ has a valid `val` and `next`. Under out-of-order persistence the publishing store of $\text{head}$ may persist *before* $n.\text{next}$ — a crash then leaves $\text{head}\to n$ with $n.\text{next}$ garbage, violating $I$. The fix is a `CLWB(n.next)` + `SFENCE` *before* writing $\text{head}$, ordering the persists.

Now count the crash-state explosion the verifier faces. With $k=4$ pending (un-persisted) stores and out-of-order persistence, the number of persisted subsets is $2^k = 16$. Add torn writes: the 8-byte `head` pointer, if mis-aligned across two cache lines, can persist as either half, multiplying states by a per-store split factor $s\approx 2$, giving $\sim 2^k \cdot s = 32$ states to check. For $k=40$ pending stores this is $>10^{12}$ — the exponential blow-up that forces heuristic checkers (Witcher, Jaaru) over exhaustive enumeration, and motivates *proofs* that quantify over all linearizations symbolically.

---
*Part of the [DBMS Research catalog](../../README.md).*
