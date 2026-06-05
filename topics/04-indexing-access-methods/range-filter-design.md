# Range filters with provable guarantees

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/range-filter-design` · **Status:** empirically-open

## 1. Problem Statement
A **range filter** is a compact probabilistic structure that answers *range-emptiness* queries: given $[a,b]$, report "empty" (no stored key falls in $[a,b]$) or "maybe non-empty," with no false negatives and a bounded false-positive rate (FPR). It generalizes a Bloom filter (which only answers point/equality emptiness) to intervals, the workhorse query for LSM-tree range scans.

- **Static variant:** build over a fixed key set, minimize bits for target FPR over a query-length distribution.
- **Dynamic variant:** support inserts/deletes with bounded amortized cost while preserving FPR — empirically the hard part.
- **Counting/optimization variant:** minimize expected I/O = $\sum_{[a,b]} \Pr[\text{query}]\cdot \text{FPR}(a,b)$ given a query workload.

The central difficulty: FPR for ranges depends on **query length and key distribution**, unlike point filters whose FPR is workload-independent.

## 2. Mathematical Foundations
Point-filter theory gives $n\log_2(1/\varepsilon)$ bits as the information-theoretic floor for equality membership. For ranges, no such clean universal bound exists because the query class is richer: a range filter must, in effect, distinguish the $\binom{U}{2}$ intervals over a universe $U$ that contain a stored key from those that don't. SuRF builds a **succinct trie** (LOUDS-encoded, $\approx 2$ bits/node) truncated to a few suffix bits, so FPR scales with shared prefixes among keys and the query length; adversarial (e.g., long-common-prefix) key sets blow up FPR. Rosetta recasts range queries as a **dyadic decomposition**: a range $[a,b]$ splits into $O(\log U)$ dyadic intervals, each probed in a hierarchy of segment Bloom filters, giving analyzable FPR $\approx \prod$ over $O(\log(\text{range len}))$ probes but at higher space/CPU. SNARF and Proteus blend learned/segment models with trie-style suffixes.

## 3. State of the Art (SOTA)
- **SuRF** (Zhang, Lim, Andersen, Kaminsky, Keeton, Pavlo; SIGMOD 2018) — succinct range filter; first practical design, but no distribution-free FPR guarantee.
- **Rosetta** (Luo, Dayan, et al.; SIGMOD 2020) — dyadic Bloom hierarchy with tunable, analyzable FPR for short ranges.
- **SNARF** (Vaidya et al.; SIGMOD 2022) — learned model + bit array; strong on real data, no worst-case bound.
- **Proteus** (Knorr, Athanassoulis et al.; SIGMOD 2022) — unifies trie + prefix-Bloom designs and *auto-tunes* to a sampled workload. Systems-SOTA filters ship/experiment in RocksDB-derived engines.

## 4. Upper Bound
Rosetta: for a range of length $\ell$, query cost $O(\log \ell)$ filter probes and FPR bounded by a product of per-level Bloom FPRs — a *distribution-aware* but not distribution-free guarantee, in the RAM model. SuRF/Proteus give space $\approx$ a constant bits/key plus suffix bits, with empirically tuned FPR. No design achieves a *clean closed-form* worst-case bits-vs-FPR tradeoff for arbitrary range length matching the point-filter floor.

## 5. Lower Bound
There is no tight, widely accepted lower bound matching practical designs. Information-theoretically, supporting all ranges with bounded FPR over universe $U$ requires more than the point-filter $n\log_2(1/\varepsilon)$ once query length is unrestricted; adversarial key/query arguments show any fixed-suffix trie design (SuRF-style) has FPR $\to 1$ on worst-case clustered keys. Establishing a matching cell-probe or information-theoretic lower bound for *dynamic, distribution-free* range filters is open.

## 6. The Gap
Empirically strong filters (SuRF, SNARF, Proteus) lack distribution-free guarantees; the one design with cleaner analysis (Rosetta) pays space/CPU and degrades for long ranges. No structure simultaneously offers: distribution-free bounded FPR for arbitrary range length, near-information-theoretic space, **and** efficient updates. The gap is open — closing it needs either a new lower bound proving the tradeoff is fundamental, or a construction achieving all three.

## 7. Current Research (as of June 2026)
Active threads: learned + worst-case hybrid range filters that fall back to a guaranteed structure off-distribution; update-friendly designs avoiding full rebuilds; and memtable/concurrent range filters. Groups: Athanassoulis (BU), Pavlo/Andersen (CMU), Dayan, Idreos (Harvard). *(frontier — verify)* recent attempts at provably distribution-free dynamic range filters and at unifying range-filter allocation with the LSM memory-budget problem.

## 8. Future Work
- A distribution-free, dynamic range filter with a proven bits/FPR/range-length tradeoff.
- Matching lower bounds (cell-probe or information-theoretic) clarifying the inherent cost of ranges over points.
- Workload-adaptive auto-tuning with regret guarantees; integration with the global LSM filter-memory budget.

## 9. Key References
- **[SOTA]** Huanchen Zhang, Hyeontaek Lim, et al. *SuRF: Practical Range Query Filtering with Fast Succinct Tries.* SIGMOD, 2018.
- **[SOTA]** Siqiang Luo, Subarna Chatterjee, Niv Dayan, et al. *Rosetta: A Robust Space-Time Optimized Range Filter for Key-Value Stores.* SIGMOD, 2020.
- **[SOTA]** Kapil Vaidya et al. *SNARF: A Learning-Enhanced Range Filter.* SIGMOD/VLDB, 2022.
- **[SOTA]** Eric R. Knorr, Manos Athanassoulis, et al. *Proteus: A Self-Designing Range Filter.* SIGMOD, 2022.
- **[Foundational]** Burton H. Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970.

---
*Part of the [DBMS Research catalog](../../README.md).*
