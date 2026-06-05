# Compaction-Triggered Cache Invalidation

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/compaction-cache-invalidation` · **Status:** empirically-open

## 1. Problem Statement
LSM-tree key-value stores (RocksDB, Cassandra, HBase, LevelDB) serve reads from in-memory **block caches** (cached SSTable blocks) and **row/point caches** (cached key→value entries). **Compaction** periodically rewrites SSTables — merging, dropping tombstones, reorganizing — which changes physical block boundaries and file identities, so cached blocks keyed by `(file, offset)` become **stale or unaddressable**. The common implementation simply lets the old file's cached blocks age out (or evicts them en masse), causing a post-compaction **cache-miss storm** and latency spikes, even though the *logical* data is largely unchanged.

The problem: keep block and row caches valid across compaction rewrites **without flushing the whole cache**, i.e., preserve the *useful* cached content for keys whose values did not change, repopulating only the genuinely changed entries.

- **Optimization variant:** minimize post-compaction miss rate (or tail-latency degradation) subject to bookkeeping memory/CPU overhead.
- **Decision variant:** given a compaction job's input/output SSTables, identify the maximal set of cache entries provably still valid and remappable to the new layout in $o(\text{cache size})$ work.

## 2. Mathematical Foundations
Compaction is a **k-way merge** of sorted runs producing new sorted runs; the LSM read/write/space amplification trade-off is governed by the size ratio $T$ and level count $L = O(\log_T(N/B))$ (the RUM-conjecture / Dostoevsky framework, Dayan–Idreos). A read costs $O(L)$ run probes mitigated by Bloom filters (false-positive budget allocation, Monkey). Cache effectiveness follows from the **working-set / stack-distance** model: hit rate is a function of reuse-distance distribution; an eviction-induced reset moves the system off its steady-state Che-approximation operating point, with recovery time $\approx$ working-set-size / fill-rate.

The core invalidation question is a **delta-identification** problem: given old block set $\mathcal{B}_{old}$ and new $\mathcal{B}_{new}$ produced by merging the same key-value content, find a remapping $\phi$ of unchanged byte ranges. Because compaction re-sorts and re-blocks, byte-identical blocks rarely survive; validity must be reasoned at the **key granularity** (a key's value is unchanged $\Rightarrow$ its row-cache entry is valid) rather than block granularity. Tombstone garbage collection and merge of multiple versions complicate this: a key present in cache may have been deleted or superseded during compaction (a *coherence* hazard).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** RocksDB supports a **partitioned block cache** and options to *warm* the cache during compaction (`cache_index_and_filter_blocks`, and inserting newly written blocks into the cache as compaction outputs them — "compaction output cache prepopulation") to reduce the post-compaction cliff. Index/filter blocks are pinned to avoid re-reads. HBase has block-cache eviction tied to HFile lifecycle; Cassandra maintains a key cache and row cache with explicit invalidation on flush/compaction. These are **heuristics**, not optimality-guaranteed.
- **Research-SOTA:** Work on LSM read-cache co-design — e.g., Leaper (Alibaba, VLDB 2020) uses machine-learning prefetching to predict and pre-warm hot records *that will be invalidated by compaction*, directly targeting this miss storm; and various "cache-conscious compaction" proposals. No closed-form optimal invalidation policy exists; results are empirical.

## 4. Upper Bound
Best practical guarantee: **row-level remapping** — maintain a key→value cache (not block-keyed) so that compaction need only invalidate keys it actually changed (the merge frontier), giving invalidation work $O(|\text{changed keys}|)$ rather than $O(|\text{cache}|)$. Combined with **output prepopulation**, the hot working set is reinserted during the rewrite, bounding the post-compaction miss surge by the genuinely-changed fraction. Leaper-style learned prefetch empirically cuts the post-compaction miss spike substantially (reported large reductions in hot-record miss rate). These are upper bounds *in practice*; no proven competitive ratio against an offline-optimal cache manager is established.

## 5. Lower Bound
There is no published tight lower bound. Relevant impossibilities: online caching has the classic **competitive-ratio lower bound of $k$** (deterministic) / $H_k$ (randomized) against optimal offline eviction (Sleator–Tarjan; Fiat et al.), so any online cache-warming policy facing adversarial access cannot beat these without future knowledge — which is exactly why learned/predictive prefetch is used. Reasoning about per-key validity requires touching metadata for changed keys; identifying the changed set is $\Omega(|\text{changed keys}|)$, and detecting *whether* a cached key changed without per-key version tracking forces a re-probe, an information lower bound. Establishing a meaningful conditional or competitive lower bound for the *compaction-coupled* setting is itself open.

## 6. The Gap
**Empirically open.** The mechanisms (row-keyed caching, output prepopulation, learned prefetch) demonstrably reduce the miss storm, but there is **no model** that (a) formalizes the optimal post-compaction cache state, (b) proves a competitive ratio for any online warming policy under realistic compaction+workload distributions, or (c) quantifies the metadata cost needed to identify the valid-cache subset exactly. The gap is between strong empirical engineering results and the absence of an analytical optimality characterization — the status is *empirically open* rather than *open* precisely because good-enough solutions exist but lack proven bounds.

## 7. Current Research (as of June 2026)
Directions: **learned cache admission/prefetch coupled to compaction scheduling** extending Leaper to multi-level and tiered (compaction-style) layouts *(frontier — verify)*; **compaction-aware cache key design** (logical row keys + version stamps enabling surgical invalidation); **disaggregated/remote block caches** (e.g., over RDMA or in cloud-native LSM like Rockset/CloudJump) where re-warming cost is amplified and invalidation precision matters more. Groups/people: Stratos Idreos and the data-systems-design community (RUM/Dostoevsky/Monkey), the RocksDB team at Meta, Alibaba's PolarDB/X-Engine group (Leaper, X-Engine compaction), and Niv Dayan (Pliops / LSM tuning).

## 8. Future Work
- A formal optimal-cache-state definition across a compaction boundary and a competitive-analysis framework for warming policies.
- Cheap exact valid-subset identification via per-key version stamps with bounded metadata overhead.
- Joint optimization of compaction scheduling and cache warming (when to compact to minimize cache disruption).
- Evaluation protocols/benchmarks isolating the post-compaction tail-latency cliff.

## 9. Key References
- **[Foundational]** O'Neil, Cheng, Gawlick, O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[Foundational]** Sleator, Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[SOTA]** Dayan, Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Yang et al. *Leaper: A Learned Prefetcher for Cache Invalidation in LSM-tree based Storage Engines.* PVLDB, 2020. — [DBLP](https://dblp.org/rec/journals/pvldb/YangWZCLZWCWH20.html)
- **[SOTA]** Dayan, Athanassoulis, Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DBLP](https://dblp.org/rec/conf/sigmod/DayanAI17.html)
- **[Survey]** Luo, Carey. *LSM-based Storage Techniques: A Survey.* The VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)

## 10. Worked Example

Suppose a block cache holds 4 SSTable blocks, keyed by `(file, offset)`:
`(f7, 0)→[a,b]`, `(f7, 1)→[c,d]`, `(f9, 0)→[e,f]`, `(f9, 1)→[g,h]` (8 keys, all hot).

A compaction merges `f7` and `f9` into `f12`, re-sorting and re-blocking into
`(f12,0)→[a,b,c]`, `(f12,1)→[d,e,f]`, `(f12,2)→[g,h]`. Note: only key `c`'s value was actually updated during the merge.

**Block-keyed invalidation (naive):** all 4 old entries reference dead file ids `f7,f9`, so the whole cache is evicted — $4/4 = 100\%$ miss storm even though 7 of 8 keys are unchanged.

**Row-keyed invalidation (the upper-bound idea):** cache by logical key with a version stamp. Compaction reports only its merge frontier — here the single changed key $c$. Invalidation work is $O(|\text{changed keys}|) = O(1)$, and 7 cached values stay valid. With **output prepopulation**, the rewritten blocks of `f12` are inserted as they are produced, so post-compaction miss rate $\approx 1/8 = 12.5\%$ instead of $100\%$.

---
*Part of the [DBMS Research catalog](../../README.md).*
