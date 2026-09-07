---
id: 11-nosql-kv/range-query-lsm-filters
title: "Range Query Filters for LSM"
topic: 11-nosql-kv
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Range Query Filters for LSM

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/range-query-lsm-filters` · **Status:** open

## 1. Problem Statement
Bloom filters prune SSTables for **point** lookups, but a *range* query `[lo, hi]` cannot use them — a Bloom filter answers only "is key $x$ present?". The problem: design a compact, **mergeable** per-SSTable filter that, given an arbitrary range predicate, answers *"does this SSTable contain any key in $[lo,hi]$?"* (range emptiness) with bounded false-positive rate, so that empty SSTables are skipped without a disk probe. "Mergeable" is essential: LSM compaction merges runs, so two filters must combine into the filter of the union *without rebuilding from raw keys*.

Variants:
- **Decision (range emptiness):** report `empty`/`maybe-nonempty` for $[lo,hi]$ with FPR $\le \varepsilon$.
- **Optimization:** minimize filter bits per key at fixed range-FPR over a target query-length distribution.
- **Counting/approx:** estimate the number of keys (or the min/next key) in the range for cost-based scan planning.

The difficulty: range-FPR depends on *query length* and the *gap structure* of keys; short ranges behave like point queries (solvable), but arbitrary-length ranges defeat hashing-based filters because hashing destroys order.

## 2. Mathematical Foundations
Order must be preserved, so range filters are built on **succinct ordered structures**, not hashing. **SuRF** (Zhang et al., SIGMOD 2018) uses a *Fast Succinct Trie* (FST) — a LOUDS-encoded trie storing truncated key prefixes; it answers range-emptiness with FPR growing with range length and shrinking with suffix bits, at $\approx 10$ bits/key. **Rosetta** (Luo et al., SIGMOD 2020) decomposes a range into $O(\log R)$ dyadic prefix intervals and stores a hierarchy of Bloom filters (a *segment-tree of Bloom filters*), giving FPR controllable per query length; it excels at short ranges. **REMIX**, **bloomRF** (Mößner et al.), and **Proteus** (learned, adaptive) interpolate the design space. Information-theoretically, a structure that distinguishes the $\binom{U}{n}$ possible $n$-subsets of universe $U$ to support exact range-emptiness needs $\Omega(n\log\frac{U}{n})$ bits (full ordered set); approximate range-emptiness with FPR $\varepsilon$ admits savings but the *order-preserving* requirement raises the floor above the point-query Bloom bound $n\log_2(1/\varepsilon)$. Mergeability requires the encoding to be a *monoid* under set union — tries and dyadic Bloom hierarchies merge; arbitrary minimal perfect hashes do not.

## 3. State of the Art (SOTA)
**Systems/theory-SOTA.** **SuRF** (succinct range filter, SIGMOD 2018) — first practical range filter, deployed in RocksDB experiments; **Rosetta** (SIGMOD 2020) — Robust Space-Time Optimized Range Filter, better for short/medium ranges; **Proteus** (Knorr, Spector, et al., SIGMOD 2022) — a *learned*, workload-adaptive range filter that mixes prefix Bloom and trie segments and tunes to the query distribution; **bloomRF** (EDBT 2023) — prefix/dyadic Bloom variant with monotone hashing; **Grafite** (Costa et al., SIGMOD 2024) — gives *worst-case robust* range-emptiness guarantees independent of data/query correlation *(frontier — verify)*. **SNARF** (learned) estimates membership via a learned CDF. RocksDB integrates prefix Bloom and (experimentally) SuRF.

## 4. Upper Bound
Grafite gives a range filter with a **clean, data-independent** FPR bound $\varepsilon \le \frac{L}{2^{B-2}}$ for range length $L$ and $B$ bits/key (worst-case, no correlation assumption), at $O(1)$ query time — the strongest current guarantee *(frontier — verify)*. SuRF: empirically $\sim$few-percent FPR at 10 bits/key, with FPR rising with range length. Rosetta: for a range of length $\le R$, decomposes into $O(\log R)$ probes with tunable per-level FPR, optimal for short ranges. All are **mergeable** (trie or dyadic-Bloom union). Space is $O(B)$ bits/key with $B$ a tunable budget; query time $O(\log R)$ to $O(|\text{key}|)$ depending on structure.

## 5. Lower Bound
Approximate range-emptiness has an information-theoretic floor strictly above point membership: distinguishing range-occupancy at FPR $\varepsilon$ for all ranges effectively requires encoding the order statistics, giving $\Omega(n\log(1/\varepsilon) + n)$ bits with the constant degrading as the supported range-length grows (the filter must resolve more "gaps"). For *exact* range-emptiness, $\Omega(n\log\frac{U}{n})$ bits (succinct ordered set lower bound, Pătraşcu). Cell-probe lower bounds for predecessor/range search (Pătraşcu–Thorup) imply that a filter answering range-emptiness in $o(\log\log U)$ probes cannot also be near-space-optimal in general. Adversarial (correlated) queries provably defeat data-dependent filters like SuRF/Rosetta — motivating Grafite's correlation-free guarantee.

## 6. The Gap
**Open.** Unlike point filters (Bloom is within $1.44\times$ of optimal — essentially closed), range filters have **no tight matching bound**: (1) the optimal bits/key vs. range-FPR vs. supported-range-length surface is not characterized; (2) existing practical filters are either data-dependent (fail under adversarial/correlated workloads) or robust-but-loose; the gap between Grafite-style worst-case bounds and best-case learned filters (Proteus) is large and workload-dependent; (3) *mergeability* under compaction with bounded space blow-up is achieved empirically but lacks a clean optimality theory; (4) supporting *both* point and range probes in one near-optimal filter is unresolved. Closing it needs a lower bound parameterized by range-length distribution plus a matching construction.

## 7. Current Research (as of June 2026)
Active: worst-case-robust range filters (Grafite and successors) decoupling guarantees from data correlation; learned/adaptive range filters (Proteus, SNARF) tuning to query-length distributions; integration of range filters with cost models for LSM range-read planning (ties to *Compaction-Aware Read Bounds*); GPU/SIMD-friendly succinct tries. Groups: CMU/Wisconsin (Pavlo, Andersen — SuRF lineage), Harvard DASlab (Idreos — Rosetta, Proteus), and the succinct-data-structures community (Costa et al. — Grafite). Frontier: a unified point+range near-optimal mergeable filter with proven bounds *(frontier — verify)*; range filters for non-lexicographic / composite keys *(frontier — verify)*.

## 8. Future Work
- Matching upper/lower bounds parameterized by range-length distribution.
- A single mergeable filter optimal for both point and range predicates.
- Provably correlation-robust learned range filters (closing Grafite ↔ Proteus gap).
- Range filters for multi-dimensional / composite secondary-index keys.

## 9. Key References
- **[SOTA]** H. Zhang, H. Lim, V. Leis, D. G. Andersen, M. Kaminsky, K. Keeton, A. Pavlo. *SuRF: Practical Range Query Filtering with Fast Succinct Tries.* SIGMOD, 2018. — [DBLP](https://dblp.org/rec/conf/sigmod/ZhangLLAKKP18.html)
- **[SOTA]** S. Luo, S. Chatterjee, R. Ketsetsidis, N. Dayan, W. Qin, S. Idreos. *Rosetta: A Robust Space-Time Optimized Range Filter for Key-Value Stores.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389731)
- **[SOTA]** E. Knorr, B. Spector, M. Kester, et al. *Proteus: A Self-Designing Range Filter.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526167)
- **[SOTA]** M. Costa, P. Ferragina, G. Vinciguerra. *Grafite: Taming Adversarial Queries with Optimal Range Filters.* SIGMOD, 2024. — [DOI](https://doi.org/10.1145/3639258)
- **[Foundational]** M. Pătraşcu, M. Thorup. *Time-Space Trade-offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043)
- **[Foundational]** B. H. Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970. — [DOI](https://doi.org/10.1145/362686.362692)

## 10. Worked Example

An SSTable stores 4 keys over an 8-bit universe $U=256$: $\{12, 13, 80, 200\}$. A range query asks "any key in $[40,60]$?" — the true answer is **empty** (nothing between 13 and 80).

*Point Bloom fails:* you would have to probe every one of the 21 candidate keys $40,41,\dots,60$, and a Bloom filter cannot rule out the gap.

*Grafite-style bound:* with budget $B=8$ bits/key, the worst-case false-positive probability for a range of length $\ell$ is $\le \ell/2^{B-2}$. Here $\ell=21$, so $\text{FPR} \le 21/2^{6} = 21/64 \approx 0.33$ — and crucially this holds *regardless* of whether the query is adversarially correlated with the keys. Doubling the budget to $B=16$ drops it to $21/2^{14}\approx 0.0013$.

*Mergeability:* during compaction this SSTable merges with one holding $\{50\}$. The union filter must now report $[40,60]$ as **maybe-nonempty** (50 is present) — a trie or dyadic-Bloom encoding combines the two filters directly, without re-reading the raw keys.

---
*Part of the [DBMS Research catalog](../../README.md).*
