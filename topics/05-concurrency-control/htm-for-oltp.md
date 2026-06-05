# Hardware Transactional Memory for OLTP

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/htm-for-oltp` · **Status:** empirically-open

## 1. Problem Statement
Hardware Transactional Memory (HTM) — e.g. Intel TSX/RTM, IBM POWER8+, ARM TME — lets a CPU execute a region atomically, aborting on conflict via cache-coherence-tracked read/write sets. HTM promises lock-free, fine-grained concurrency control for in-memory OLTP. But HTM is **bounded** (read/write set must fit in cache, typically L1; transactions abort on capacity overflow, interrupts, system calls, page faults, and false sharing) and gives **no progress guarantee**. The problem:

> **Exploit bounded best-effort HTM to implement database concurrency control that is correct (serializable) and faster than software CC, despite capacity limits, spurious aborts, and lack of forward-progress guarantees.**

Variants:
- **Decision/feasibility:** For a given workload, will transactions fit in HTM capacity often enough to win?
- **Optimization:** Partition/decompose database transactions into HTM-sized pieces minimizing software-fallback cost while preserving serializability.
- **Empirical:** Characterize the contention/footprint regime where HTM-based CC beats OCC/2PL.

## 2. Mathematical Foundations
HTM provides an *atomic region* with read set $R$ and write set $W$ tracked at cache-line granularity; the region commits iff no concurrent transaction wrote a line in $R \cup W$ between start and commit (a conflict-serializable certification at hardware speed). Abort probability rises with $|R \cup W|$ (capacity) and with conflict density. A database transaction generally exceeds HTM capacity, so it is **decomposed** into HTM regions glued by a software protocol; correctness requires the composition to be serializable, modeled again by acyclicity of the conflict graph over the *mixed* hardware/software schedule.

A useful model: HTM gives a primitive that atomically validates-and-installs a bounded read/write set with success probability $p(|R \cup W|, \text{contention})$; expected cost is $\frac{c_{HTM}}{p} + (1-p)\,c_{fallback}$. Optimizing CC means choosing region boundaries and a fallback (lock elision, OCC validation) to minimize this, subject to the **lemming effect** (one fallback acquiring a global lock serializes everyone). The classic *lock elision* correctness argument (Rajwar–Goodman, MICRO 2001) underlies safe fallback.

## 3. State of the Art (SOTA)
- **Theory/Systems-SOTA:** Leis, Kemper, Neumann (*Exploiting Hardware Transactional Memory in Main-Memory Databases*, ICDE 2014) showed HTM works for OLTP only when transactions are **chopped** into small static pieces and combined with timestamp ordering — the seminal feasibility result. Wang et al. and the *DBX* system (Wang, Qian, Chen, Tang et al., EuroSys 2014) built an HTM-based in-memory DB combining RTM with optimistic reads. Yoo et al. (SC 2013) characterized TSX performance/aborts. Hybrid transactional memory and HTM-assisted indexing (e.g. on Masstree/B-trees) are explored. ARM TME and persistent-memory HTM extend the design space.
- HTM is also used narrowly to make *latch-free* index operations and short critical sections cheaper rather than wrapping whole transactions.

## 4. Upper Bound
No asymptotic upper bound; HTM is a constant-factor accelerator. The practical upper bound (Leis et al.): with **transaction chopping + timestamp ordering**, HTM-based CC achieves near-linear scalability on small-footprint OLTP (e.g. TPC-C new-order) and beats software OCC/2PL at low–moderate contention. Throughput is bounded by abort rate $\approx 1-p(|R\cup W|,\text{contention})$; once read/write sets exceed L1 capacity (~tens of KB) or contention drives conflicts, fallback dominates and the advantage vanishes. Best results combine HTM with software OCC as fallback to dodge the lemming effect.

## 5. Lower Bound
Fundamental limits are *physical/architectural*, not complexity-theoretic: best-effort HTM offers **no forward-progress guarantee** (a transaction can abort forever), so any HTM CC *must* have a non-HTM fallback — an unconditional impossibility for HTM-only progress. Capacity is bounded by cache associativity/size, so transactions with $|R \cup W|$ exceeding the L1 footprint *cannot* run as a single HTM region (hard lower bound on what fits). These hardware impossibilities, not SETH/NP-style bounds, set the floor.

## 6. The Gap
Empirically open. We know HTM helps *small, low-contention* transactions and needs chopping + fallback elsewhere, but there is no general, workload-portable method to (a) decompose arbitrary transactions into capacity-fitting HTM regions automatically while preserving serializability, and (b) predict when HTM wins. The gap is between hand-tuned demonstrations and a principled, automatic HTM CC framework. Closing it needs automatic transaction chopping with capacity/abort models and robust fallback that avoids the lemming effect — plus newer hardware (larger HTM capacity, ARM TME, PM-backed HTM) re-opening the design space.

## 7. Current Research (as of June 2026)
Directions: HTM on ARM TME and on persistent memory; HTM-assisted latch-free indexes and learned-index concurrency; combining HTM with epoch-based OCC. *(frontier — verify)* Given Intel's deprecation/disabling of TSX on many client parts, 2025–2026 work appears to be shifting toward ARM TME and toward GPU/CXL-coherence-based transactional primitives, with renewed interest in HTM for short index critical sections rather than whole-transaction wrapping; treat specific 2025–2026 system claims as unverified.

## 8. Future Work
- Automatic, serializability-preserving transaction chopping for HTM capacity.
- Abort/capacity cost models to predict HTM viability online (links to the OCC/2PL crossover problem).
- HTM CC for persistent memory and ARM/CXL coherence domains.

## 9. Key References
- **[Foundational]** Herlihy, Moss. *Transactional Memory: Architectural Support for Lock-Free Data Structures.* ISCA, 1993.
- **[Foundational]** Rajwar, Goodman. *Speculative Lock Elision: Enabling Highly Concurrent Multithreaded Execution.* MICRO, 2001.
- **[SOTA]** Leis, Kemper, Neumann. *Exploiting Hardware Transactional Memory in Main-Memory Databases.* ICDE, 2014.
- **[SOTA]** Wang, Qian, Chen, Tang, et al. *Using Restricted Transactional Memory to Build a Scalable In-Memory Database (DBX).* EuroSys, 2014.
- **[SOTA]** Yoo, Hughes, Lai, Rajwar. *Performance Evaluation of Intel Transactional Synchronization Extensions for High-Performance Computing.* SC, 2013.
- **[Survey]** Harris, Larus, Rajwar. *Transactional Memory (2nd ed.).* Morgan & Claypool, 2010.

---
*Part of the [DBMS Research catalog](../../README.md).*
