# Compaction-Aware Read Cost Bounds

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/compaction-aware-read-bounds` · **Status:** partially-solved

## 1. Problem Statement
In an LSM-tree, a key may reside in any of several on-disk *runs* (sorted SSTables) plus the in-memory buffer. A point lookup or range scan must, in the worst case, probe one run per level (point) or merge across overlapping runs (range). The cost depends jointly on the **compaction policy** (leveling, tiering, or a hybrid), the size ratio $T$, the number of levels $L$, the filter configuration, and the **key distribution** of both the dataset and the query workload.

Goal: derive **tight worst-case and expected** bounds on read I/O for point and range queries as a function of $(n, T, \text{policy}, \text{filters}, \mathcal{D})$, and identify the policy that is Pareto-optimal on the read/write/space tradeoff.

Variants:
- **Decision:** does configuration $C$ guarantee point-read $\le b$ I/Os at false-positive rate $\le \varepsilon$?
- **Optimization:** minimize expected total I/O over a workload mix subject to a write-amplification budget.
- **Counting:** number of runs that must be merged for a range of selectivity $s$.

## 2. Mathematical Foundations
Standard LSM model (Dayan–Athanassoulis–Idreos *Monkey/Dostoevsky*). With $n$ entries, buffer size $B$ (entries), size ratio $T$, the number of levels is
$$L = \left\lceil \log_T \frac{n}{B} \right\rceil = \Theta\!\left(\frac{\log(n/B)}{\log T}\right).$$
**Leveling:** $\le 1$ run/level, so point lookup probes $O(L)$ runs; with per-level Bloom filters of total false-positive rate $\sum_i p_i$, expected I/O is $1 + \sum_i p_i$. **Tiering:** up to $T-1$ runs/level, point cost $O(T \cdot L)$ runs. Range cost: short ranges behave like point lookups multiplied by output; long ranges are dominated by the merge over $O(L)$ (leveling) or $O(TL)$ (tiering) overlapping runs, i.e. $\Theta(L + s\cdot n/B)$ vs $\Theta(TL + \dots)$. The *Monkey* result minimizes $\sum p_i$ under a fixed total bits budget $M$ by allocating bits unevenly: optimal $p_i \propto T^{i}$, giving total point-read cost $O(e^{-M/n} \cdot L)$ improved to a constant-ish multiplier. Key-distribution effects enter through filter FPR being content-independent but **range** pruning depending on key-density per SSTable (zone maps / min-max).

## 3. State of the Art (SOTA)
**Theory/systems-SOTA.** The *Monkey* (SIGMOD 2017) and *Dostoevsky* (SIGMOD 2018) line by Dayan & Idreos established closed-form read/write/space tradeoffs and the **lazy-leveling** hybrid, plus *Wacky* continuum tuning. *Cosine* / *Endure* (Idreos group; Huynh et al., VLDB 2022) add robust tuning under workload uncertainty. RocksDB's leveled compaction with partitioned filters and *FrModel*-style cost models is the systems baseline; *SlimDB*, *PebblesDB* (fragmented LSM), and *SplinterDB* push the tradeoff. *ElasticBF* and *bLSM* address filter/Bloom dynamics.

## 4. Upper Bound
For point lookups under leveling with Monkey-optimal Bloom allocation: expected I/O $= O\!\left(L \cdot e^{-M/N}\right)$ plus one positive read, and worst case $O(L)$ I/Os. Lazy-leveling gives point cost $O(e^{-M/N})$ (constant in $L$ for the lookup-dominant levels) while bounding write amplification to $O(\log_T(n/B))$. Range queries: short range $O(L \cdot e^{-M/N} + \text{output})$; long range $\Theta(L + \frac{sn}{B})$ I/Os — sort-merge over $O(L)$ runs is optimal for full-overlap ranges. These hold in the **external-memory (DAM) model** with block size $B$.

## 5. Lower Bound
The read/write/space tradeoff is governed by an inherent tension: in the **external-memory model**, any structure supporting inserts in $o$(amortized) and queries must pay a product tradeoff. Brodal–Fagerberg's **comparison-/I-O tradeoff for buffer trees / external dictionaries** gives a lower bound: $\text{query} \cdot \text{insert}$ cannot both be $o(\log)$; specifically insertion at amortized $\frac{\lambda}{B}$ forces lookup $\Omega(\log_{\lambda}(n))$-style cost. For range emptiness/range queries, **cell-probe** and the indexability lower bounds (Hellerstein–Koutsoupias–Papadimitriou; Arge et al.) bound the *redundancy × access* product. Filter memory is bounded information-theoretically: a filter with FPR $\varepsilon$ needs $\ge n \log_2(1/\varepsilon)$ bits (Bloom is within a $\log_2 e \approx 1.44$ factor), so read cost cannot fall below the budget-implied FPR.

## 6. The Gap
**Partially solved.** Point-lookup cost is essentially *closed*: Monkey allocation matches the information-theoretic filter bound up to the $1.44\times$ Bloom slack, and the leveling/tiering frontier is characterized. The genuine gaps: (1) **range queries** have no point-lookup-style optimal filter, so worst-case range bounds are loose and distribution-dependent (see *Range Query Filters for LSM*); (2) bounds are **expected-case under uniform/independent assumptions** — tight *worst-case* bounds under adversarial or skewed key/query distributions, and under *concurrent compaction* changing the run structure mid-query, are open; (3) the joint optimum over read+write+space+memory for *mixed* workloads with correlated keys is not in closed form.

## 7. Current Research (as of June 2026)
Active: learned/ML cost models and *learned compaction* policies that adapt size ratio per-level to observed skew; *Endure*-style robust optimization under workload drift; integrating learned indexes (RMI/PGM) with LSM levels to cut the per-run search term. The Harvard DASlab (Idreos), Boston U (Athanassoulis), and RocksDB/Meta teams remain central. Frontier: tight worst-case range-read bounds with mergeable range filters (SuRF/Rosetta successors) and analysis under concurrent compaction *(frontier — verify)*; reinforcement-learning compaction schedulers with provable competitive ratios *(frontier — verify)*.

## 8. Future Work
- Closed-form *worst-case* range-read bounds parameterized by query selectivity and key skew.
- Compaction policies with proven competitive ratio against an offline optimum.
- Joint filter+zone-map allocation optimal for mixed point/range workloads.
- Analysis accounting for in-progress compaction and read amplification during merges.

## 9. Key References
- **[Foundational]** P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996.
- **[SOTA]** N. Dayan, M. Athanassoulis, S. Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017.
- **[SOTA]** N. Dayan, S. Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores.* SIGMOD, 2018.
- **[SOTA]** A. Huynh, H. Chaudhari, E. Terzi, M. Athanassoulis. *Endure: A Robust Tuning Paradigm for LSM Trees under Workload Uncertainty.* VLDB, 2022.
- **[Foundational]** G. S. Brodal, R. Fagerberg. *Lower Bounds for External Memory Dictionaries.* SODA, 2003.
- **[Foundational]** L. Arge. *The Buffer Tree: A Technique for Designing Batched External Data Structures.* Algorithmica, 2003.

---
*Part of the [DBMS Research catalog](../../README.md).*
