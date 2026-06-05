# Persistent-memory logging and recovery

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/pmem-logging-recovery` · **Status:** partially-solved

## 1. Problem Statement

Persistent memory (PMEM) exposes *byte-addressable*, *load/store-accessible* durable storage on or near the memory bus. The classical write-ahead logging (WAL) discipline — force-log-then-write, group commit, ARIES-style redo/undo — was designed for the block-I/O, two-tier (volatile RAM + durable disk) world. The problem is to redesign **durability, atomicity, and recovery** to exploit byte-addressability while bounding three competing costs:

- **Commit latency / logging overhead** (cache-line flushes `CLWB`/`CLFLUSHOPT` + `SFENCE`, memory fences, ordering barriers);
- **Write amplification / write traffic** to the (wear-limited, asymmetric-bandwidth) media;
- **Recovery time** after crash (bounded, ideally near-instant / O(active transactions) rather than O(log length)).

Variants: (a) *decision* — given a workload and a target recovery bound, does a durability scheme exist meeting commit-latency budget $L$ and write-amplification budget $W$? (b) *optimization* — minimize expected commit latency subject to a recovery-time SLO; (c) *correctness* — prove crash-consistency (durable linearizability / strict serializability across power failure) under a given persistence memory model.

## 2. Mathematical Foundations

The substrate is a **persistency model**: an ordering relation over stores and explicit persist barriers, formalized as *strict / epoch / buffered persistency* (Pelley–Chen–Wenisch). Let $\le_{po}$ be program order, $\le_{pers}$ the *persist order*; correctness requires that the persistent state at any crash point is reachable by some prefix of $\le_{pers}$ consistent with $\le_{po}$ at barriers.

**Durable linearizability** (Izraelevitz–Mendes–Scott) extends linearizability: every operation that returns before a crash, and every operation it depends on, survives the crash. A weaker, cheaper target is **buffered durable linearizability**, which only guarantees a consistent prefix.

Cost model: a commit issues $f$ flushes and $b$ fences; with per-flush cost $c_f$ and fence cost $c_b$, commit latency $\approx f c_f + b c_b$. PMEM asymmetry gives read bandwidth $B_r \gg B_w$ and a media write-amplification factor from the device's internal block size (the Optane 256 B XPLine), so logical writes of size $s$ cost $\lceil s/256\rceil$ media writes. Recovery time is governed by the length of the **dirty epoch** that must be replayed; bounding it is a renewal-theoretic checkpoint-interval optimization (Young/Daly-style optimal checkpoint spacing).

## 3. State of the Art (SOTA)

**Systems-SOTA.** Single-tier PMEM-resident engines and hybrids dominate. Notable: *FOEDUS* (Kimura, SIGMOD 2015) with master-tree + dual page snapshots; *SOFORT* (Oukid et al., DaMoN 2014) one-tier engine eliminating the persistent log; *Write-Behind Logging* (Arulraj–Pavlo–Malladi, VLDB 2016) inverting WAL to leverage PMEM; *NV-Logging* / passive group commit; *Zen* and *FAST&FAIR* (Hwang et al., FAST 2018) for failure-atomic B+-trees; *RECIPE* (Lee et al., SOSP 2019) converting concurrent indexes to crash-consistent ones. PMEM-aware allocators: *PMDK*'s `libpmemobj`, *Makalu*.

**Theory-SOTA.** *Log-free / link-and-persist* techniques, *durable linearizable* index transforms (RECIPE conditions: readable→durable conversion rules), and the *Montage* buffered-durable framework (Wen et al., PPoPP 2021) giving generic constructions with proved buffered durable linearizability.

A major caveat: Intel discontinued Optane PMEM (2022), shifting the practical frontier toward CXL-attached memory; the algorithmic results remain valid for any byte-addressable durable tier.

## 4. Upper Bound

For a single durable update, **link-and-persist** achieves atomic durable publication with $O(1)$ flushes and one fence per logical update; failure-atomic 8-byte stores are free (hardware-atomic) under x86 persistency. Write-Behind Logging reduces log volume to $O(\#\text{committed tuples})$ rather than $O(\#\text{updates})$, eliminating redo. Montage gives generic durable structures at amortized $O(1)$ persist barriers per operation with recovery time $O(|\text{epoch}|)$. Optimal checkpoint interval (Daly) bounds expected recovery + checkpoint overhead at $\Theta(\sqrt{2 M \delta})$ for MTBF $M$ and checkpoint cost $\delta$.

## 5. Lower Bound

Any durable-linearizable object whose operations modify shared state must incur at least one persist fence on the commit path in the worst case — captured by the **persistence cost lower bounds** of Cohen–Friedman–Kaplan-style analyses and the *flush/fence necessity* arguments: with $p$ concurrent persisters there exist histories requiring $\Omega(p)$ explicit flushes to maintain durable linearizability for certain objects (e.g., durable queues), shown via covering/indistinguishability arguments. Information-theoretically, recovery must read at least the undurable suffix, so recovery is $\Omega(|\text{unflushed dirty set}|)$. These mirror RDCSS/CAS persistence overhead lower bounds; tight constant-factor bounds remain object-specific.

## 6. The Gap

For *single-word* and *link-and-persist* publications the gap is essentially closed: matching $O(1)$ upper bounds and the one-fence lower bound. The genuinely open region is **multi-object failure-atomic transactions**: minimizing the number of fences/flushes for a $k$-object commit while preserving strict serializability across crashes. Upper bounds need $\Theta(k)$ flushes naively; whether sub-linear (batched, group-persist) commit is achievable without sacrificing durable linearizability is open, and the lower bounds are not tight in $k$. Recovery-time vs. write-traffic Pareto frontiers are characterized only empirically.

## 7. Current Research (as of June 2026)

Active threads: (i) porting PMEM durability results to **CXL Type-3 / CXL.mem** byte-addressable tiers now that Optane is EOL *(frontier — verify)*; (ii) *hardware-software co-design of persist barriers* — eADR (extended ADR makes the CPU cache power-fail-protected), which on eADR platforms removes most `CLWB`s, changing the cost model fundamentally *(frontier — verify)*; (iii) verified crash-consistency (Perennial/GoJournal-style separation logic, Chajed et al.) applied to PMEM indexes; (iv) learned/adaptive checkpoint scheduling. Groups: Wisconsin (Wenisch lineage), CMU-DB (Pavlo, Arulraj→Georgia Tech), Rochester (Scott/Montage), MIT (Chajed/Kaashoek verification), Intel/PMDK alumni.

## 8. Future Work

- Tight $k$-object commit fence lower bounds and matching group-persist algorithms.
- Recasting all PMEM results for **eADR** (where the durability point moves to the cache) and for CXL pooled memory with weak coherence.
- End-to-end *machine-checked* durable-serializability proofs for production engines.
- Co-optimizing wear-leveling / write-amplification with recovery SLOs under media asymmetry.

## 9. Key References

- **[Foundational]** Mohan, C. et al. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992.
- **[Foundational]** Izraelevitz, J., Mendes, H., Scott, M. L. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016.
- **[SOTA]** Arulraj, J., Pavlo, A., Malladi, S. R. *Bridging the Archipelago between Row-Stores and Column-Stores for Hybrid Workloads (Write-Behind Logging).* VLDB, 2016.
- **[SOTA]** Lee, S. K. et al. *RECIPE: Converting Concurrent DRAM Indexes to Persistent-Memory Indexes.* SOSP, 2019.
- **[SOTA]** Wen, H. et al. *Montage: A General System for Buffered Durably Linearizable Data Structures.* PPoPP, 2021.
- **[Survey]** Pelley, S., Chen, P. M., Wenisch, T. F. *Memory Persistency.* ISCA, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
