# Buffer Management for Log-Structured / LSM Stores

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/lsm-buffer-management` · **Status:** open

## 1. Problem Statement

Log-Structured Merge (LSM) stores partition data into an in-memory mutable buffer (the *memtable*) and a sequence of immutable, sorted on-disk runs organized into levels. Reads may probe several runs; background *compaction* rewrites runs to bound the number of probes and reclaim space. This couples three caches that classical buffer management treats separately: (i) the memtable/write buffer, (ii) the block cache over immutable run blocks, and (iii) auxiliary structures (Bloom/ribbon filters, fence pointers, block indexes).

The decision problem: given a fixed memory budget $M$, a workload of point/range reads and writes, and a compaction policy, **partition $M$ across memtable, filters, and block cache, and choose a block-cache eviction policy, to minimize expected I/O cost (or tail latency).** The complication absent in B-tree buffer pools is *compaction-induced churn*: compaction invalidates cached blocks en masse and rewrites the same logical keys to new physical blocks, so cache hit rate, write amplification (WA), and read amplification (RA) are jointly determined by the same memory split. Variants: the **optimization** variant (minimize a weighted RA+WA+space cost); the **online** variant (policy must react to a non-stationary mix); and a **counting/analysis** variant (predict hit rate of a given split under a given compaction schedule).

## 2. Mathematical Foundations

Let the LSM have $L$ levels with size ratio $T$, so level $i$ holds $\approx T^i$ times the memtable. For uniform-random point lookups with per-level Bloom filters of $b$ bits/key, the false-positive rate at level $i$ is $\approx e^{-b\ln^2 2}$, and expected I/O per negative lookup is $\sum_i \text{FPR}_i$. The **Monkey** result (Dayan–Athanassoulis–Idreos, SIGMOD'17) shows the optimal allocation gives *more* bits to filters at larger levels, yielding $O(L)$ improvement over uniform allocation. Write cost under leveling is $O(L \cdot T)$ I/Os per entry; under tiering $O(L)$; the **Dostoevsky/Wacky** continuum (SIGMOD'18) parameterizes this. The buffer-management subproblem sits atop this: given residual memory after filters, the block cache faces a request stream whose locality is *destroyed periodically* by compaction. Formally, model the cache as serving a stream where a compaction event at time $t$ remaps a working set $W$ to fresh keys; competitive analysis must account for forced misses with rate tied to the compaction frequency $\propto$ write rate $/$ level capacity. Submodularity of hit-rate-vs-memory (concavity of the miss-ratio curve) underlies convex allocation, but compaction breaks stationarity, so the MRC is time-varying.

## 3. State of the Art (SOTA)

**Systems-SOTA:** RocksDB's `LRUCache`/`HyperClockCache` with optional compaction-aware insertion hints; partitioned filters and index blocks cached separately; `cache_index_and_filter_blocks` with high-priority pinning of top levels. Leveled-N and FIFO compaction variants tune churn. **Theory-SOTA:** Monkey (SIGMOD'17) and Dostoevsky (SIGMOD'18) give closed-form optimal filter/memory allocation under a cost model; *Cosine* (VLDB'22) and *Endure* (VLDB'22, robust LSM tuning under workload uncertainty) extend to uncertain/adversarial workloads. *LeaperCache* and learned block-prefetching for LSM (various 2021-2023) target compaction-aware caching.

## 4. Upper Bound

For the **filter/memory allocation** sub-objective, Monkey gives a *provably optimal* allocation under its cost model (Lagrangian over per-level FPR), an exact result, not an approximation. For **online block caching** under compaction churn, the best guarantee inherits paging's $k$-competitiveness (LRU is $k$-competitive, $k$ = cache size in blocks), but with an additive *forced-miss* term equal to compaction-invalidated requests, which is policy-independent. No algorithm achieves better than the offline optimal's forced misses, so the achievable competitive ratio is $k$-competitive *on the reducible (non-forced) portion* of the stream. End-to-end joint optimization of (memtable, filter, cache) split has only heuristic/convex-relaxation upper bounds (Endure's robust optimization).

## 5. Lower Bound

Online paging has a tight $k$-competitive lower bound for deterministic policies and $H_k=\Theta(\log k)$ for randomized (Fiat et al.), and these transfer to the block cache. The *joint* allocation problem is at least as hard as the convex but non-stationary MRC allocation; under adversarial, non-stationary workloads no online policy can match the offline optimum better than the paging bound, and the compaction-induced forced misses are an information-theoretic floor: any policy must re-read remapped blocks at least once, giving a $\Omega(\text{write-rate}/\text{level-capacity})$ miss-rate lower bound independent of cache size. There is no known NP-hardness for the clean cost-model version (Monkey is poly-time solvable); hardness appears only when adding integrality, multi-objective Pareto, or workload-uncertainty constraints (robust variants become min-max programs).

## 6. The Gap

The *filter-allocation* slice is essentially closed (Monkey is optimal in its model). The genuinely **open** gap is the **joint, online** problem: there is no tight competitive analysis that integrates (a) the convex memory split, (b) compaction-driven non-stationarity, and (c) the block-cache eviction decision. Practice uses decoupled heuristics (allocate filters by Monkey, then run LRU/Clock on the remainder), but no proof says this decoupling is within a constant factor of the joint optimum. Closing it requires a model of compaction churn that yields a competitive ratio (or a hardness result showing constant-factor is impossible online).

## 7. Current Research (as of June 2026)

Active directions: (1) **compaction-aware caching** that pins or pre-warms blocks the compactor is about to produce, amortizing the forced-miss floor *(frontier — verify)*; (2) **learned/ML-guided memory split** that adapts the memtable/filter/cache partition online to a drifting MRC (Idreos group at Harvard DASlab; Athanassoulis at BU); (3) **robust tuning** under workload uncertainty (Endure line, BU); (4) **disaggregated/CXL-memory LSM** where the cache spans local DRAM and remote memory, changing the cost model *(frontier — verify)*. RocksDB and SplinterDB teams continue engineering HyperClockCache scalability and secondary-cache (NVM/SSD) tiers.

## 8. Future Work

- A unified competitive model coupling compaction schedule + cache eviction; prove or refute constant-factor optimality of decoupled allocation.
- Tail-latency (not just expected I/O) objectives, since compaction stalls dominate p99.
- Filter alternatives (ribbon/xor filters) change the bits/key tradeoff — re-derive optimal allocation.
- Cross-tier (DRAM/CXL/SSD) buffer management with heterogeneous read/write asymmetry.
- Online MRC estimation robust to compaction-induced non-stationarity.

## 9. Key References

- **[Foundational]** Patrick O'Neil, Edward Cheng, Dieter Gawlick, Elizabeth O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[SOTA]** Niv Dayan, Manos Athanassoulis, Stratos Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** Niv Dayan, Stratos Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Andy Huynh, Harshal A. Chaudhari, Evimaria Terzi, Manos Athanassoulis. *Endure: A Robust Tuning Paradigm for LSM Trees Under Workload Uncertainty.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2110.13801)
- **[Foundational]** Daniel Sleator, Robert Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Survey]** Chen Luo, Michael J. Carey. *LSM-based Storage Techniques: A Survey.* VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)

## 10. Worked Example

A 3-level LSM ($L=3$), size ratio $T=10$, $N=10^6$ keys, memory budget for filters $=10^6$ bits total. Point-lookup I/O on a negative query $\approx \sum_i \text{FPR}_i$, with per-level FPR $\approx e^{-b_i \ln^2 2}$ where $b_i$ is bits/key at level $i$ (which holds $\approx 10^{i}$ fraction of keys).

**Uniform allocation** ($b_i = 1$ bit/key everywhere): each $\text{FPR}_i \approx e^{-0.48}\approx 0.62$, so expected probes $\approx 3\times0.62 = 1.86$ wasted I/Os per negative lookup.

**Monkey allocation.** The Lagrangian optimum gives *more* bits to larger levels (they dominate FPR mass). Shifting bits so $b_3 > b_2 > b_1$ — e.g. $b_1{=}0.3, b_2{=}1, b_3{=}1.7$ at equal total budget — drives the larger levels' FPR down, cutting total expected probes to $\approx 0.6$, roughly an $O(L){=}3\times$ improvement, matching the closed-form result.

**Compaction churn.** If writes trigger a level-2 compaction every $10^4$ ops, each event remaps a working set $W$ to fresh blocks; the block cache must re-read $W$ at least once — a forced-miss floor $\Omega(\text{write-rate}/\text{level-capacity})$ that *no* eviction policy (LRU, Clock) can avoid, independent of cache size $k$.

---
*Part of the [DBMS Research catalog](../../README.md).*