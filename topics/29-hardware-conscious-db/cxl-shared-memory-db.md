---
id: 29-hardware-conscious-db/cxl-shared-memory-db
title: "Coherence-free CXL-shared-memory databases"
topic: 29-hardware-conscious-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-09
last_substantive_update: 2026-09
stale_since: ""
provenance: synthesized
---

# Coherence-free CXL-shared-memory databases

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/cxl-shared-memory-db` · **Status:** empirically-open

## 1. Problem Statement

Compute Express Link (CXL) lets multiple hosts attach to **pooled / shared byte-addressable memory** (CXL Type-3 devices; multi-headed devices and CXL 3.0 fabrics support shared regions across hosts). Crucially, hardware cache **coherence across hosts is weak or absent**: CXL.cache provides device↔host coherence, but *host-to-host* coherence over a shared region is not generally guaranteed — software must manage visibility. The problem is to design **data structures, indexes, and transaction protocols** that are correct and efficient over such shared memory **without relying on hardware coherence**, while exploiting load/store access (no message round-trips) and the ability to share state at memory speed.

Concretely: given $h$ hosts mapping a shared CXL region, with intra-host coherence but only **explicit software coherence** (flush/invalidate, fences, or message-passing for visibility) across hosts, build a concurrent ordered index and a transaction manager guaranteeing **(strict) serializability / linearizability** while minimizing (i) cross-host coherence traffic (flushes/invalidations/RPCs), (ii) latency (CXL adds load latency vs. local DRAM), and (iii) synchronization. Decision variant: does a protocol meet a throughput target within a coherence-traffic budget? This sits between shared-memory and shared-nothing/RDMA models — it is *partitioned global address space (PGAS) with byte access but manual coherence*.

## 2. Mathematical Foundations

The substrate is a **weak / release-consistency memory model** without inter-host cache coherence — closer to a distributed shared memory (DSM) or a relaxed-consistency model than to x86-TSO. Correctness targets: **linearizability** (Herlihy–Wing) for objects and **strict serializability** for transactions, both of which require establishing a real-time order over operations whose visibility is software-controlled. Without hardware coherence, a write becomes visible to another host only after an explicit *publish* (flush + fence on writer, invalidate/acquire on reader), so synchronization cost is measured in **coherence messages**, analyzable in the **CONGEST / message-passing model** and via **cache-coherence lower bounds**: maintaining a shared mutable cell read by $r$ hosts and written by one costs $\Omega(r)$ invalidations per write epoch. **CAP / consistency-availability** tensions reappear because failure of a host or the shared device partitions visibility. Lock-free progress is governed by consensus number theory (Herlihy): atomic primitives the CXL device exposes (e.g. CXL-native atomics / far-atomics, if any) set the consensus number and hence which wait-free objects are buildable.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Early CXL-DB systems treat CXL memory mostly as a **tier** (capacity expansion) rather than truly shared: *TPP* (Maruf et al., ASPLOS 2023) for tiered placement, *Pond* (Li et al., ASPLOS 2023, Microsoft Azure) for memory pooling. Genuinely *shared* CXL DB work is emerging: disaggregated indexes and buffer pools over shared CXL (*CXL-SHM*, *Sherman*-style disaggregated B+-trees adapted from RDMA). RDMA-era disaggregated-memory designs are the closest mature analogues: *FaRM* (Dragojević et al., NSDI 2014) — coherence-free RDMA transactions with one-sided ops; *Sherman* (Wang et al., SIGMOD 2022) — disaggregated B+-tree; *Clover*, *FORD*, *DrTM* — RDMA transactions. These inform but do not directly solve the CXL byte-addressable-without-coherence case.

**Theory-SOTA.** Disaggregated/PGAS data-structure design and DSM consistency theory; *Practical, lock-free, software-coherent* structures via explicit publish protocols. No settled theory specific to CXL host-to-host non-coherent shared memory yet.

## 4. Upper Bound

From the RDMA/disaggregated lineage, one-sided read-optimized B+-trees (Sherman) achieve $O(\log n)$ remote reads per lookup with combining/locking to bound write contention; FaRM-style optimistic concurrency achieves transactions with a constant number of one-sided ops per record plus a validation phase. Translating to CXL: lookups cost $O(\log_B n)$ CXL loads (no RPC), with explicit acquire on cross-host shared nodes; the publish cost per update is $O(1)$ flush+fence plus $O(r)$ reader invalidations in the worst sharing case. These are practical upper bounds; no provably optimal coherence-traffic protocol is established.

## 5. Lower Bound

**Coherence-traffic lower bound:** maintaining a value read by $r$ hosts under a writer forces $\Omega(r)$ invalidations/publishes per write in the worst case (covering argument; mirrors cache-coherence and the $\Omega(p)$ persistence flush bounds). **Consensus / FLP:** any host-to-host agreement (e.g. distributed commit over the shared region) is subject to **FLP impossibility** under asynchrony with a single failure, and **CAP** forbids simultaneous linearizability and availability under partition — a partitioned or failed shared CXL device is exactly such a partition. **Communication-complexity** bounds (set-disjointness $\Omega(n)$) lower-bound coordination for certain distributed joins/aggregations even with shared memory if visibility requires explicit transfer. Herlihy's hierarchy lower-bounds wait-free constructions by the available atomics' consensus number.

## 6. The Gap

**Empirically-open.** Real multi-host shared CXL 3.0 hardware is scarce, so the design space is explored mostly in emulation/simulation; there is no consensus on the right programming model (manual flush/invalidate vs. message-passing overlay vs. limited hardware-assisted coherence) nor a validated cost model for cross-host visibility. The gap is between (a) mature RDMA-disaggregation results that *assume* message-passing visibility and (b) the CXL promise of *load/store* sharing whose true coherence-traffic and latency costs are not yet measured at scale. Whether coherence-free protocols can beat RDMA-style ones, and by how much, is an open empirical and modeling question; matching coherence-traffic lower bounds with optimal publish protocols is open theory.

## 7. Current Research (as of June 2026)

- **Shared (not just tiered) CXL DB engines**: buffer pools and indexes mapped into a host-shared CXL region with software coherence; CXL 3.0 fabric + multi-headed devices enabling true sharing *(frontier — verify hardware availability)*.
- **Hardware-assisted partial coherence / back-invalidation** semantics and how DB protocols should use them *(frontier — verify)*.
- Porting **PMEM durability** and **RDMA disaggregation** results onto CXL's byte-addressable-shared model (overlaps with the PMEM logging problem).
- Memory-pool **transaction managers** minimizing publish/invalidate traffic.
- Groups: Microsoft Research (Pond), Meta (TPP), CMU-DB, UW Madison, ETH Zürich, MIT, Korea (KAIST/Samsung CXL ecosystem), Intel.

## 8. Future Work

- A canonical programming/consistency model for host-shared CXL and matching cost model validated on real CXL 3.0 hardware.
- Coherence-traffic-optimal concurrent indexes and commit protocols with proven bounds.
- Fault-tolerant transactions over a shared device that can itself fail/partition (CAP-aware design).
- Co-design with CXL-native atomics to raise constructible consensus number.

## 9. Key References

- **[Foundational]** Herlihy, M. P., Wing, J. M. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** Herlihy, M. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[SOTA]** Dragojević, A., Narayanan, D., Castro, M., Hodson, O. *FaRM: Fast Remote Memory.* NSDI, 2014. — [USENIX](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-dragojevic.pdf)
- **[SOTA]** Wang, Q. et al. *Sherman: A Write-Optimized Distributed B+Tree Index on Disaggregated Memory.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2112.07320)
- **[SOTA]** Li, H. et al. *Pond: CXL-Based Memory Pooling Systems for Cloud Platforms.* ASPLOS, 2023. — [arXiv](https://arxiv.org/abs/2203.00241)
- **[SOTA]** Maruf, H. A. et al. *TPP: Transparent Page Placement for CXL-Enabled Tiered Memory.* ASPLOS, 2023. — [arXiv](https://arxiv.org/abs/2206.02878)
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)

## 10. Worked Example

Consider $h = 4$ hosts mapping a shared CXL region holding one counter cell $c$ (initial value $0$). Hosts $H_2, H_3, H_4$ are readers that have cached $c=0$ in their local caches; $H_1$ is the writer. With **no host-to-host hardware coherence**, when $H_1$ does $c \leftarrow 1$, that store lands in $H_1$'s cache/the device but the readers' caches still hold the stale $0$.

To make the write visible, $H_1$ must **publish**: flush $c$ to the device (1 cache-line flush) and issue a store fence. Each reader must then **acquire**: invalidate its cached copy and reload from the device. With $r = 3$ readers, that is $\Omega(r) = 3$ explicit invalidations per write epoch — matching the coherence-traffic lower bound. A hardware-coherent system would do this in the background; here it is software-visible cost.

Concretely, if a CXL load is $300$ ns and a flush+fence is $\sim 100$ ns, one published increment seen by all readers costs $\approx 100 + 3\times(100 + 300) \approx 1300$ ns — versus a few ns on a coherent single host. This is exactly why a coherence-free index must batch publishes and minimize the reader fan-out $r$ on hot cells.

---
*Part of the [DBMS Research catalog](../../README.md).*
