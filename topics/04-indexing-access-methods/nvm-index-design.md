---
id: 04-indexing-access-methods/nvm-index-design
title: "Index design for NVM/persistent memory"
topic: 04-indexing-access-methods
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Index design for NVM/persistent memory

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/nvm-index-design` · **Status:** empirically-open

## 1. Problem Statement
Byte-addressable **non-volatile / persistent memory** (NVM/PMEM, e.g. Intel Optane DCPMM) sits between DRAM and SSD: load/store-addressable, persistent across power loss, but with **read/write asymmetry**, higher latency than DRAM, limited write endurance, and persistence only at cache-line granularity after explicit flush+fence. The problem: design **crash-consistent** access methods (B-trees, hash tables, tries, LSM components) that (a) recover to a consistent state after any crash, (b) minimize expensive `clwb`/`sfence` ordering operations ("fences"), and (c) exploit the read-cheap/write-expensive asymmetry.

- **Design (optimization) variant:** minimize persist barriers (fences) and write amplification per operation subject to a crash-consistency invariant.
- **Correctness variant:** prove durable linearizability / buffered durable linearizability under the persistency model.

## 2. Mathematical Foundations
Correctness rests on a **persistency model** specifying when stores become durable relative to program order. The standard cache-line atomic store (8 bytes on x86) is the only guaranteed-atomic persistent write; larger updates need logging or copy-on-write to stay crash-consistent. Formal targets:
- **Durable linearizability** and **buffered durable linearizability** (Izraelevitz, Mendes, Scott; DISC 2016) — the accepted correctness conditions; the latter allows a bounded recovery window for higher throughput.
- A cost model counts **persist fences** ($f$) and **cache-line flushes** as the dominant terms, since each `sfence` serializes the pipeline. A B-tree split that previously cost $O(1)$ writes now costs $O(f)$ fences; minimizing $f$ per insert is the core objective.
- **Failure-atomicity** is reasoned about with happens-before / persist-order partial orders; recovery must restore an invariant from a log or from self-describing node layouts.

## 3. State of the Art (SOTA)
- **NV-Tree / wB+-Tree** (early) — selectively persistent / unsorted leaf nodes to cut ordering writes.
- **FAST & FAIR** (Hwang, Kim, Won; FAST 2018) — B+-tree using only store/`mfence` ordering, exploiting that shifts during sorted-insert leave the tree transiently readable but always recoverable; near fence-free.
- **BzTree** (Arulraj et al.; VLDB 2018) — lock-free, PMwCAS-based, persistence-agnostic.
- **RECIPE** (Lee et al.; SOSP 2019) — a *principled conversion* turning concurrent DRAM indexes into crash-consistent PMEM indexes.
- **Dash / DPTree / LB+-Tree / utree / Viper** — hashing and B+-tree designs tuned for Optane's access granularity. Systems-SOTA also includes **PMDK**-based engines and PMEM-aware RocksDB variants.

## 4. Upper Bound
Best constructions achieve **O(1) persist fences per insert in the common (non-split) case** (FAST&FAIR-style), with logarithmic-depth search reading DRAM-cached upper levels. Hash designs (Dash) achieve near-1 cache-line write + 1 fence per insert amortized. These are empirical/engineering bounds in the x86 persistency model, not proven optimal; no clean asymptotic separation establishes the *minimum* fences per operation across the design space.

## 5. Lower Bound
There is **no tight, accepted lower bound** on persist fences for crash-consistent dictionaries. Known results are model-level impossibilities: any failure-atomic update spanning $>1$ atomic-store width requires *at least one* ordering barrier between the data write and the visibility/commit write (else a crash exposes a torn update) — a trivial $\Omega(1)$. Lower bounds on the *number* of fences as a function of structural change (e.g. node splits, rebalancing) and on the inherent write amplification under asymmetry are open; the persistency model itself is still being formalized (the hardware moved with CXL-attached memory replacing discontinued Optane).

## 6. The Gap
We have many empirically excellent designs but **no theory pinning the optimal fence/write-amplification cost** per operation, and no agreement on the canonical hardware/persistency model — especially after Optane's discontinuation (2022) shifted the substrate toward **CXL-attached memory** and battery-backed DRAM, changing the asymmetry constants. The gap is empirical-vs-formal: closing it needs a settled persistency cost model plus matching lower bounds.

## 7. Current Research (as of June 2026)
With DCPMM discontinued, the frontier has moved to **CXL memory pools / CXL-attached persistent or far memory**, re-asking the same crash-consistency questions on new latency/asymmetry profiles *(frontier — verify)*. Active: principled DRAM→PM index conversion (RECIPE lineage), tiered DRAM+PM+SSD indexes, and verified crash consistency (model checking persist orderings). Groups: Vijay Chidambaram (UT Austin), Michael Scott (Rochester), Steven Swanson (UCSD NVSL), Wook-Hee Kim / Beomseok Nam, and DB groups adapting LSM/B+-trees to CXL. *(frontier — verify)* claims about CXL-native index designs should be checked against 2025–2026 venues.

## 8. Future Work
- A settled persistency cost model and matching fence/write-amplification lower bounds.
- Index designs portable across Optane-style PM and CXL-attached memory without redesign.
- Machine-checked proofs of durable linearizability for concurrent PM indexes.

## 9. Key References
- **[Foundational]** Joseph Izraelevitz, Hammurabi Mendes, Michael L. Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23)
- **[SOTA]** Deukyeon Hwang, Wook-Hee Kim, Youjip Won, Beomseok Nam. *Endurable Transient Inconsistency in Byte-Addressable Persistent B+-Tree (FAST & FAIR).* USENIX FAST, 2018. — [USENIX](https://www.usenix.org/conference/fast18/presentation/hwang)
- **[SOTA]** Se Kwon Lee, Jayashree Mohan, Sanidhya Kashyap, Taesoo Kim, Vijay Chidambaram. *RECIPE: Converting Concurrent DRAM Indexes to Persistent-Memory Indexes.* SOSP, 2019. — [DOI](https://doi.org/10.1145/3341301.3359635)
- **[SOTA]** Joy Arulraj, Justin Levandoski, Umar Farooq Minhas, Per-Åke Larson. *BzTree: A High-Performance Latch-Free Range Index for Non-Volatile Memory.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3164135.3164147)
- **[Survey]** Steven Swanson et al. (NVSL). *An Empirical Guide to the Behavior and Use of Scalable Persistent Memory.* USENIX FAST, 2020. — [USENIX](https://www.usenix.org/conference/fast20/presentation/yang)

## 10. Worked Example

Insert key $30$ into a sorted PM leaf node holding $[10,20,40,50]$ (8-byte slots; only an 8-byte aligned store is failure-atomic on x86). We must end with $[10,20,30,40,50]$.

**Naive copy-on-write:** write a fresh node, `clwb` its cache lines, `sfence`, then atomically flip the parent pointer with one more `clwb`+`sfence`. Cost: 2 fences plus a full node copy (write amplification $\approx$ node size).

**FAST&FAIR shift:** shift $40,50$ right one slot, then write $30$ — each store is individually atomic. A crash mid-shift can transiently leave a *duplicate* (e.g. $[10,20,40,40,50]$), but readers tolerate it (a duplicated key is still searchable) and recovery is well-defined, so **no ordering fence is needed between the shifts** in the common case: amortized $\approx O(1)$ fence per insert.

The contrast — $2$ fences + COW vs. near-fence-free in-place shift — is the whole optimization. The open question is the provable *minimum* fences per insert as a function of structural change; only a trivial $\Omega(1)$ is known.

---
*Part of the [DBMS Research catalog](../../README.md).*
