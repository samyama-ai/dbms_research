---
id: 14-main-memory-db/cxl-disaggregated-imdb
title: "CXL-Disaggregated In-Memory Database"
topic: 14-main-memory-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# CXL-Disaggregated In-Memory Database

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/cxl-disaggregated-imdb` · **Status:** empirically-open

## 1. Problem Statement
**CXL (Compute Express Link)** exposes pooled/disaggregated memory with *load/store (memory-semantic)* access rather than RDMA message passing, but **far** (CXL-attached or pooled) memory has $3\!-\!10\times$ higher and more variable latency than local DRAM, and bandwidth is asymmetric. The problem: **design index structures and a transaction/concurrency-control layer for a memory hierarchy that is byte-addressable but strongly non-uniform (local DRAM vs near-CXL vs pooled far-CXL), so that hot data and synchronization metadata stay local while capacity lives far, with provable bounds on far-memory accesses per operation.**

Variants:
- *Decision:* given a latency vector $(\ell_0,\ell_1,\ell_2)$ for tiers and a request mix, is there a data layout meeting an average-op latency target?
- *Optimization:* minimize expected far-memory accesses (or weighted latency) per lookup/scan/transaction subject to local-tier capacity $M_0$.
- *Counting:* count tier-crossing cache-line fetches, analogous to I/O complexity but with $\ge 2$ unequal levels.

## 2. Mathematical Foundations
The natural model generalizes external memory to a **non-uniform multi-level byte-addressable hierarchy**: tiers $0,\dots,L$ with capacities $M_i$, line size $B$, and *unequal* per-access latencies $\ell_i$ (unlike the classic $(B,M)$ model where only the boundary matters). The cost of an operation is $\sum_i \ell_i \cdot (\text{tier-}i\text{ line fetches})$. Because access is cache-line granular and hardware-cached, the relevant complexity is closer to **cache-oblivious analysis with a latency-weighted objective** than to block-transfer counting.

Key tension theorems carry over: predecessor/range cell-probe bounds (Pătraşcu–Thorup, STOC 2006) bound the number of probes, but here probes are *weighted by tier*. Optimal placement of a working set of size $> M_0$ across tiers is a **caching/paging problem with non-uniform miss costs** — the *weighted caching* problem, for which the competitive ratio of LRU-style policies degrades and optimal offline is the weighted $k$-server/paging LP. Concurrency control must account for **coherence semantics of CXL.mem/CXL.cache**: hardware coherence over the link makes cross-host atomics possible but expensive, so the synchronization-traffic analysis (see *cache-coherence-aware-sync*) gains a far-tier cost term. Transaction commit over disaggregated memory revisits the **distributed-vs-shared-memory** boundary: is the far tier a shared log, a shared heap, or a replication target?

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **TPP** (Maruf et al., ASPLOS 2023) — transparent OS page placement for CXL tiers; **Pond** (Li et al., ASPLOS 2023, Microsoft Azure) — CXL memory pooling for cloud. DB-specific: studies of **DBMS-on-CXL buffer pools and indexes** showing far-memory-aware B-trees and hot/cold tiering (early DaMoN/SIGMOD/VLDB 2023–2025 work). Disaggregated-memory DBs predating CXL: **FaRM** (RDMA), **Sherman** (Wang et al., SIGMOD 2022) — RDMA-aware B+-tree with offloaded concurrency; **dLSM**, **DINOMO** (NSDI 2022) — disaggregated KV with ownership/caching. These inform CXL designs but assume message-passing rather than load/store.
- **Theory-SOTA:** Non-uniform/multi-level cache-oblivious results (HM/cache-oblivious hierarchies, Bender et al.) and weighted-caching competitive bounds (Young; Bansal–Buchbinder–Naor for weighted paging).

## 4. Upper Bound
Hot/cold tiering with a local cache of size $M_0$ achieves expected far accesses $\propto$ working-set-miss-rate; for B-tree-like indexes, keeping the top $O(\log_B(M_0))$ levels local bounds far-tier fetches per lookup to $O(\log_B N - \log_B M_0)$ — provably few link crossings. Weighted-paging algorithms (e.g. **Landlord/Greedy-Dual**, Young) are $k$-competitive against non-uniform miss costs, giving an online placement upper bound. RDMA-disaggregated trees (Sherman) demonstrate practical $\mu$s-scale far-memory ops with offloaded locking; CXL load/store is expected to lower the constant further (no per-message CPU). Cache-oblivious layouts (van Emde Boas) transfer to CXL since they minimize transfers at *every* boundary simultaneously.

## 5. Lower Bound
Any index over $N$ keys with local capacity $M_0$ must, in the worst case, incur $\Omega(\log_B N - \log_B M_0)$ far-tier probes for predecessor/lookup (cell-probe predecessor bound, latency-weighted). **Weighted caching** has competitive-ratio lower bound $k$ for deterministic and $\Omega(\log k)$ for randomized online policies (Bansal–Buchbinder–Naor) — so no online tiering policy can be universally optimal against the non-uniform miss costs. For cross-host transactions over coherent far memory, the coherence-invalidation fan-out lower bound and the RTT/link-latency floor ($\Omega(\ell_{\text{far}})$ per cross-tier synchronizing access) apply. CAP/FLP still bound multi-host fault-tolerant commit.

## 6. The Gap
There is **no settled cost model** for CXL's non-uniform byte-addressable hierarchy (people borrow the binary $(B,M)$ model or RDMA message models, both imperfect), and consequently no tight upper/lower-bound pair for index lookup or transaction commit *as a function of the tier-latency vector*. Empirically the hardware is new, variable across vendors, and 2.0/3.0 coherent-pooling features are partially deployed — so claims are measurement-driven and not yet theory-matched. Genuinely empirically-open.

## 7. Current Research (as of June 2026)
Threads: CXL-aware buffer managers and tiered B-trees with hardware-cache-conscious far layouts; offloading concurrency control / version validation to keep synchronization local; transactional use of CXL 3.0 **coherent shared memory pools** across hosts *(frontier — verify)*; learned hot/cold classification for placement. Groups: Microsoft Research (Pond/Azure), Meta (TPP), CMU-DB (Pavlo), TUM (Neumann/Leis), UCSD/UW systems, Korea (KAIST/SNU CXL groups).

## 8. Future Work
- A non-uniform multi-tier byte-addressable cost model with matching index lower bounds.
- Concurrency control proven to bound far-tier synchronizing accesses per transaction.
- Online tiering/placement with competitive guarantees against measured CXL latency vectors.

## 9. Key References
- **[Foundational]** Aggarwal, A., Vitter, J. S. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** Frigo, M., Leiserson, C., Prokop, H., Ramachandran, S. *Cache-Oblivious Algorithms.* FOCS, 1999. — [DBLP](https://dblp.org/rec/conf/focs/FrigoLPR99.html)
- **[SOTA]** Li, H., et al. *Pond: CXL-Based Memory Pooling Systems for Cloud Platforms.* ASPLOS, 2023. — [arXiv](https://arxiv.org/abs/2203.00241)
- **[SOTA]** Maruf, H. A., et al. *TPP: Transparent Page Placement for CXL-Enabled Tiered Memory.* ASPLOS, 2023. — [arXiv](https://arxiv.org/abs/2206.02878)
- **[SOTA]** Wang, Q., et al. *Sherman: A Write-Optimized Distributed B+Tree Index on Disaggregated Memory.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2112.07320)
- **[Survey]** Bansal, N., Buchbinder, N., Naor, J. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://dl.acm.org/doi/10.1145/2339123.2339126)

## 10. Worked Example

A B-tree over $N = 10^9$ keys, fanout $B = 100$, so height $\log_B N = \log_{100}10^9 = 4.5 \approx 5$ levels. Two tiers: local DRAM at $\ell_0 = 100$ ns, far CXL-pooled memory at $\ell_2 = 500$ ns ($5\times$).

**Naive (all far).** Each lookup probes one node per level: $5$ far fetches $\Rightarrow 5 \times 500 = 2500$ ns.

**Tiered.** Pin the top of the tree locally. Local capacity $M_0$ holds the root plus level-2, i.e. $1 + 100 = 101$ nodes — comfortably the top $\log_B M_0 = \log_{100}(10^4) = 2$ levels. Far fetches drop to $\log_B N - \log_B M_0 = 5 - 2 = 3$, matching the section-4 bound. Latency:

$$2\,(\text{local}) \times 100 + 3\,(\text{far}) \times 500 = 200 + 1500 = 1700\text{ ns},$$

a $1.47\times$ speedup from pinning only $101$ nodes. Pinning one more level ($M_0 \approx 10^4$ nodes) cuts far fetches to $2$, giving $300 + 1000 = 1300$ ns. The lower bound says we can never beat $\Omega(\log_B N - \log_B M_0)$ far probes, so with this $M_0$, $3$ link crossings is optimal.

---
*Part of the [DBMS Research catalog](../../README.md).*
