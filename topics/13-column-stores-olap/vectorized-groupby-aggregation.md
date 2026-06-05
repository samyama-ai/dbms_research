# Group-By Aggregation on Columns

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/vectorized-groupby-aggregation` · **Status:** empirically-open

## 1. Problem Statement
Given a columnar relation $R$ with grouping keys drawn from a domain of $g$ distinct groups and one or more measures, compute $\gamma_{A_1,\dots,A_k; \mathsf{agg}}(R)$ — the grouped aggregate — over $n$ input rows. Variants:

- **Optimization (the practical problem):** minimize wall-clock time on modern CPUs/GPUs, i.e. minimize cache misses, branch mispredictions, and memory traffic, while remaining robust to *skew* (a few heavy groups) and to unknown/large $g$.
- **Decision/threshold:** materialize only groups whose aggregate passes a predicate (iceberg-style `HAVING`).
- **Counting:** estimate or compute $g$ (distinct-group count) to size hash tables, itself a distinct-counting subproblem.

The open question is not asymptotic — it is which physical strategy (hash vs. sort vs. hybrid/partitioned) and which layout (open-addressing, partitioned, SIMD-gather) is *robustly* fastest across the full $(n, g, \text{skew}, \text{key-width})$ space, and whether a single adaptive operator can dominate.

## 2. Mathematical Foundations
Aggregation cost is dominated by the **memory hierarchy**, not arithmetic. Two regimes:

- **Hash aggregation:** expected $O(n)$ probes, but each probe is a random access; throughput collapses once the hash table exceeds cache, governed by the **external/cache-oblivious model** with block size $B$ and cache size $M$. Working-set $\Theta(g)$; cost transitions sharply at $g \approx M/B$.
- **Sort aggregation:** $O(n \log n)$ comparisons / radix passes, sequential access, cost $\Theta\!\big(\frac{n}{B}\log_{M/B}\frac{n}{B}\big)$ I/Os, with $g$-independent locality.

Aggregates are classified (Gray et al.) as **distributive** (SUM, COUNT, MIN/MAX — constant state, mergeable), **algebraic** (AVG, STDDEV — fixed-size sufficient statistics), or **holistic** (MEDIAN, distinct-count — no bounded summary). Distributive/algebraic aggregates are *commutative monoids* $(S,\oplus,e)$, enabling SIMD reduction, partial pre-aggregation, and tree/segmented combination. Skew robustness formalizes as instance-optimality: cost should track the empirical group-size distribution, not the worst case.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** vectorized engines (MonetDB/X100 — Boncz et al., CIDR 2005; DuckDB; ClickHouse; Velox) use partitioned/two-phase hash aggregation with thread-local tables merged at the end. HyPer/Umbra (Neumann) compile aggregation into tight loops; "Morsel-driven parallelism" (Leis et al., SIGMOD 2014) gives NUMA-aware, work-stealing scheduling.
- **Algorithmic-SOTA:** Cagri Balkesen et al. (VLDB 2014) and Müller et al. characterize hash vs. sort crossovers; **SIMD/AVX-512** gather-scatter and partitioning (Polychroniou & Ross, SIGMOD 2015) push hashing throughput near memory bandwidth.
- Adaptive aggregation (spill-to-sort on overflow; switching radix-partitioning fan-out by observed cardinality) is shipping in DuckDB and Umbra.

## 4. Upper Bound
For distributive aggregates, $O(n)$ expected RAM time via hashing, and cache-optimal $O\!\big(\frac{n}{B}\log_{M/B}\frac{g}{B}\big)$ I/Os via partitioned/radix aggregation (the external-memory sorting bound restricted to the $g$ distinct keys). With SIMD width $w$, per-element work drops by up to $w$ for vectorizable monoids, and partitioning makes the hash table cache-resident, giving near-memory-bandwidth throughput in the RAM model with caches.

## 5. Lower Bound
Any aggregation reads all input: $\Omega(n/B)$ I/Os and $\Omega(n)$ time unconditionally. Producing $g$ distinct outputs needs $\Omega(g)$ space and output. In the **comparison/algebraic-decision-tree** model, group-by with output ordering inherits the $\Omega(n \log g)$ sorting bound; hashing escapes this only under the RAM/integer-key assumption. **Exact holistic** aggregates (e.g., exact distinct count) require $\Omega(g)$ space — no sublinear exact summary exists (information-theoretic). No nontrivial fine-grained lower bound separates the *best* hash strategy from the best sort strategy; that crossover is empirical.

## 6. The Gap
Asymptotically the problem is "closed" ($\Theta(n)$ for distributive aggregates). The real gap is **constant-factor and robustness**: no single operator provably dominates across $(g,\text{skew},\text{key-width},\text{hardware})$, and the hash/sort crossover is hardware- and data-dependent. Closing it means either a proven instance-optimal adaptive operator or a tight cost model that picks the winner without trial execution.

## 7. Current Research (as of June 2026)
Directions: (i) *unified adaptive aggregation* that morphs between hashing, radix-partitioning, and sorting based on runtime cardinality/skew samples (DuckDB, Umbra teams); (ii) SIMD/AVX-512 and ARM SVE group-by kernels with conflict-detection for in-register accumulation; (iii) learned cardinality feedback to pre-size tables and choose fan-out; (iv) skew-aware "heavy-hitter offloading" where a few hot groups get dedicated accumulators. Frontier: *near-bandwidth-saturating, fully skew-robust single-operator aggregation across CPU+GPU with no plan-time strategy choice* remains unachieved *(frontier — verify)*. Groups: Neumann (TUM), Boncz/CWI, Ross (Columbia), the DuckDB Labs and Velox communities.

## 8. Future Work
- A provably instance-optimal aggregation operator parameterized by the group-size distribution.
- Cost models accurate enough to retire runtime strategy-switching.
- Holistic-aggregate group-by with embedded sketches (KLL, HyperLogLog) at vectorized speed.
- Co-design with columnar compression so aggregation runs on encoded data (RLE/dictionary) without full decode.

## 9. Key References
- **[Foundational]** Gray, Chaudhuri, Bosworth, Layman, et al. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* ICDE 1996. — [arXiv](https://arxiv.org/abs/cs/0701155)
- **[Foundational]** Boncz, Zukowski, Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR 2005. — [PDF](https://www.cidrdb.org/cidr2005/papers/P19.pdf)
- **[SOTA]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[SOTA]** Polychroniou, Raghavan, Ross. *Rethinking SIMD Vectorization for In-Memory Databases.* SIGMOD 2015. — [DOI](https://doi.org/10.1145/2723372.2747645)
- **[SOTA]** Balkesen, Teubner, Alonso, Özsu. *Main-Memory Hash Joins on Modern Processor Architectures.* IEEE TKDE / VLDB lineage, 2014. — [DBLP](https://dblp.org/rec/journals/tkde/BalkesenTAO15.html)

## 10. Worked Example

Compute `SELECT region, SUM(sales) GROUP BY region` over $n=8$ rows with keys `[N,S,N,E,S,N,W,E]` and measures `[3,5,2,4,1,6,7,2]`, so $g=4$ groups $\{N,S,E,W\}$.

**Hash path:** scan once, probing a 4-slot table. After the scan: $N=3{+}2{+}6=11$, $S=5{+}1=6$, $E=4{+}2=6$, $W=7$. Cost $O(n)$ probes; since $g=4$ fits in cache, every probe is cheap. The crossover warning fires when $g$ grows past $\approx M/B$: with cache $M=256$KB, block $B=64$B, the table stops fitting once $g\gtrsim 4000$ slots, and random probes start missing cache — the sharp throughput cliff.

**Sort/radix path:** radix-partition the 8 keys by their first byte into $\le g$ runs, then a contiguous sequential reduction sums adjacent equal keys. Cost $\Theta(\tfrac{n}{B}\log_{M/B}\tfrac{g}{B})$ I/Os, locality independent of $g$.

For this tiny instance ($g=4 \ll M/B$) hash wins on constants; the value of the sort path only appears once $g$ blows past cache, illustrating why the crossover is empirical, not asymptotic.

---
*Part of the [DBMS Research catalog](../../README.md).*
