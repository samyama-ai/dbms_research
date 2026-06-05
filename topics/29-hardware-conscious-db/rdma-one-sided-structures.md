# One-sided RDMA data structures with consistency

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/rdma-one-sided-structures` · **Status:** empirically-open

## 1. Problem Statement

A *one-sided* RDMA verb (READ, WRITE, and a small set of atomics — `CMP_AND_SWAP`, `FETCH_AND_ADD` on 8 bytes) lets a client access a server's registered memory **without invoking the server's CPU**. Building a remotely accessible index (hash table, B-tree, skip list) under this model is hard: the remote CPU is bypassed, so the *only* synchronization available across the network is 8-byte RDMA atomics and the read/write verbs themselves. The problem: design indexes mutated via one-sided verbs that remain **correct (linearizable / lock-free)** under concurrent remote readers and writers, while minimizing round trips (each pointer dereference or retry is a network latency hit).

Variants:
- **Decision:** is a one-sided access protocol linearizable given only 8-byte remote atomics?
- **Optimization:** minimize round trips per lookup/insert under concurrency and limited registered memory.
- **Lock-freedom:** guarantee system-wide progress without server-side locks.

## 2. Mathematical Foundations

The base correctness notion is **linearizability** (Herlihy–Wing, TOPLAS 1990); for non-blocking progress, **lock-freedom / wait-freedom** (Herlihy's hierarchy). The available synchronization primitive is single-word `compare-and-swap` (consensus number $\infty$ in the shared-memory model) — but RDMA imposes constraints the classical theory does not: (i) reads are **non-atomic across cache lines** (a remote READ of a multi-word node can observe a torn state mid-write), and (ii) there is no remote read-modify-write beyond 8 bytes. So designers add **versioning/checksums** so a torn read is *detectable* and retried, turning the structure into an *optimistic* concurrency object whose correctness relies on a read-validate loop.

Formally one models the fabric as a shared-memory system where remote operations have **non-atomic multi-word reads** and only 8-byte CAS. Round-trip count is the cost measure; pointer-chasing depth $d$ implies $\Omega(d)$ round trips (a communication-complexity argument). Self-verifying data (CRC/version per cache line) provides the encoding needed to make non-atomic reads safe.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *FaRM* (Dragojević et al., NSDI 2014) pioneered one-sided RDMA reads with version-based consistency and lock-free reads. *Pilaf* (Mitchell, Geng, Li, ATC 2013) introduced self-verifying hash tables (CRC) so clients detect torn one-sided reads. *FaSST* (Kalia, Kaminsky, Andersen, OSDI 2016) argued two-sided/datagram RPC often beats one-sided for complex ops. *Cell* and *eRPC* explore the trade-off. Recent one-sided B-trees: *Sherman* (Wang et al., SIGMOD 2022) — a write-optimized disaggregated B-tree using on-chip RNIC locks + versioning; *FUSEE*, *RACE hashing* (Zuo et al., OSDI 2021) — a fully one-sided, lock-free disaggregated hash index.
- **Theory-SOTA.** General linearizable/lock-free constructions exist for shared memory with CAS, but few results specifically model non-atomic remote multi-word reads with only 8-byte atomics; this is largely a *systems* literature.

## 4. Upper Bound

Achievable: **lock-free, fully one-sided** hash indexes (RACE hashing) with O(1) expected round trips per lookup and bounded retries per insert via 8-byte CAS on slot metadata. Disaggregated B-trees (Sherman) achieve a few round trips per operation with versioned nodes and hierarchical on-chip locking; reads are lock-free with version validation. Self-verifying reads (Pilaf) give O(1)-round consistent lookups with a small checksum overhead. These are strong empirical upper bounds; the worst-case retry count under adversarial contention is generally unbounded (optimistic).

## 5. Lower Bound

Any structure of dereference depth $d$ accessed purely one-sided needs $\Omega(d)$ round trips — a pointer-chasing / communication lower bound. With only 8-byte remote atomics, a multi-word atomic update is impossible in a single round trip, so any node update spanning $>8$ bytes needs either multiple round trips or a versioning scheme with a detect-and-retry loop (no wait-free bounded-round multi-word update). Classical results give that wait-free consensus among unbounded clients needs CAS (which we have), but **bounded retry / wait-freedom over the network under non-atomic reads** has no clean matching lower bound. There is no tight bound on round trips for one-sided lock-free range queries.

## 6. The Gap

Practice has working one-sided lock-free hash indexes and write-optimized B-trees with good empirical round-trip counts and contention behavior — but **no formal model** captures non-atomic multi-word remote reads + 8-byte atomics and yields tight upper/lower bounds on round trips and progress under contention. Linearizability proofs for these systems are mostly hand-argued, not derived in a faithful RDMA consensus model. So the status is **empirically-open**: the systems exist and work, but the theory (correctness conditions, optimal round-trip bounds, wait-freedom feasibility) is unsettled.

## 7. Current Research (as of June 2026)

- **Memory disaggregation** (CXL + RDMA pooled memory) driving fully one-sided lock-free indexes; integrating CXL's cache-coherent far memory with RDMA's non-coherent model *(frontier — verify)*.
- Formal/mechanized linearizability proofs for one-sided RDMA structures *(frontier — verify)*.
- SmartNIC/DPU-assisted designs that reintroduce a *programmable* remote agent, blurring one-sided vs two-sided. Active groups: Tsinghua (Zuo — RACE/FUSEE), CUHK (Sherman lineage), CMU (Kaminsky/Andersen), ETH Zürich (Alonso).

## 8. Future Work

- A consensus/round-trip model for RDMA with non-atomic multi-word reads, with tight bounds.
- Wait-free (not just lock-free) one-sided structures, or a proof of impossibility.
- Lock-free one-sided **range** indexes with bounded round trips.
- Verified correctness toolchains for disaggregated indexes.

## 9. Key References

- **[Foundational]** Herlihy, Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** Dragojević, Narayanan, Castro, Hodson. *FaRM: Fast Remote Memory.* NSDI, 2014. — [USENIX](https://www.usenix.org/conference/nsdi14/technical-sessions/dragojevi%C4%87)
- **[SOTA]** Mitchell, Geng, Li. *Using One-Sided RDMA Reads to Build a Fast, CPU-Efficient Key-Value Store (Pilaf).* USENIX ATC, 2013. — [USENIX](https://www.usenix.org/conference/atc13/technical-sessions/presentation/mitchell)
- **[SOTA]** Zuo, Wang, et al. *One-sided RDMA-Conscious Extendible Hashing for Disaggregated Memory (RACE).* USENIX ATC, 2021. — [USENIX](https://www.usenix.org/conference/atc21/presentation/zuo)
- **[SOTA]** Wang, Qian, et al. *Sherman: A Write-Optimized Distributed B+Tree Index on Disaggregated Memory.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2112.07320)
- **[SOTA]** Kalia, Kaminsky, Andersen. *FaSST: Fast, Scalable and Simple Distributed Transactions with Two-Sided RDMA Datagram RPCs.* OSDI, 2016. — [USENIX](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/kalia)

## 10. Worked Example

A client reads a 24-byte hash-table slot — `{key: 8B, value: 8B, version: 8B}` — laid out across two cache lines via one one-sided RDMA READ. Because the READ is **non-atomic across cache lines**, it can observe a torn state while a writer is mid-update.

*Self-verifying read (Pilaf/RACE style).* The writer updates with a version-and-checksum protocol. Client reads slot, sees `version=7` in the trailer but a checksum over `{key,value}` that does not match `version 7`'s stored CRC → torn read **detected** → retry. After the writer's WRITE completes, a re-READ yields a consistent `version=8` with matching CRC → accepted in **1 extra round trip**.

*Insert via 8-byte CAS.* To claim an empty slot, the client issues `CMP_AND_SWAP(slot.header, EMPTY, my_token)` — exactly 8 bytes, the only remote atomic available. If two clients race, one CAS succeeds, the loser retries elsewhere; this is lock-free (system-wide progress), not wait-free (a single client may retry unboundedly under contention).

*Round-trip lower bound.* Probing a bucket whose overflow chain has dereference depth $d=3$ costs $\ge 3$ round trips (pointer-chasing argument, Section 5): each remote pointer needs its own READ. With latency $\sim 2\,\mu s$, that is $\ge 6\,\mu s$ per lookup before any retries — illustrating why minimizing $d$ dominates one-sided index design.

---
*Part of the [DBMS Research catalog](../../README.md).*
