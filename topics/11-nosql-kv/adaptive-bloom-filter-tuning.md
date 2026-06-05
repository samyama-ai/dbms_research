# Workload-Adaptive Bloom Filter Tuning

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/adaptive-bloom-filter-tuning` · **Status:** empirically-open

## 1. Problem Statement
An LSM-tree (or any layered store) attaches an approximate membership filter (Bloom, cuckoo, ribbon, quotient) to each SSTable to avoid disk probes on negative lookups. Given a fixed *total* memory budget $M$ bits, how should bits be allocated **per level and per key-range** to minimize the *total expected read cost* (false-positive-induced I/Os) for a given, possibly skewed and time-varying, query workload?

Variants:
- **Optimization (static):** minimize $\sum_i a_i \cdot \text{FPR}(m_i)$ over filters $i$ subject to $\sum_i m_i \le M$, where $a_i$ is access frequency and $m_i$ bits for filter $i$.
- **Optimization (adaptive/online):** track drifting workloads, re-allocate bits with bounded reconstruction cost; competitive against the offline optimum.
- **Counting:** distribution of negative queries across ranges (the load $a_i$ must be estimated from a sketch).

Empirically open: closed-form static allocation exists, but the *per-key-range*, *workload-adaptive* allocation that wins in practice has no clean optimal characterization and is dominated by engineering tradeoffs.

## 2. Mathematical Foundations
A Bloom filter with $m$ bits over $k$ keys has false-positive rate $p \approx (1-e^{-(\ln 2) m/k})^{(\ln 2) m/k}$, minimized at $\approx 0.6185^{m/k}$, i.e. $\log_2(1/p) \approx 0.48\,(m/k)$ — needing $\ge \log_2 e \approx 1.44$× the information-theoretic floor of $k\log_2(1/p)$ bits. The allocation problem is the *Monkey* convex program: minimize total expected cost
$$\min_{\{m_i\}} \sum_i a_i \cdot p_i(m_i) \quad \text{s.t.} \sum_i m_i = M,$$
with $p_i$ convex decreasing; Lagrangian/KKT conditions give $\frac{a_i\, dp_i}{dm_i} = \lambda$ (equal marginal benefit), yielding **non-uniform** allocation — fewer bits to deep levels (rarely the answer source, larger) and more to hot, frequently-negative-probed ranges. Per-key-range refinement makes $a_i$ depend on the workload's negative-access histogram, estimable via a Count-Min / frequency sketch. **Adaptive filters** (Bender et al.) that learn from observed false positives and **ribbon/cuckoo** filters that beat Bloom's $1.44\times$ constant change the per-filter cost curve. Optimal *online* re-tuning is an experts/regret problem; submodularity of coverage can be invoked for greedy allocation guarantees.

## 3. State of the Art (SOTA)
**Theory-SOTA.** *Monkey* (Dayan et al., SIGMOD 2017) solves the static per-level allocation optimally and shows uniform per-level bits is suboptimal; *Dostoevsky*/*Wacky* extend it. *Optimal Bloom Filters and Adaptive Merging* and the **adaptive cuckoo filter** (Mitzenmacher, Pontarelli, Reviriego, 2018) and **broom/telescoping adaptive filters** (Bender et al., 2018–21) fix false positives after the fact. *ElasticBF* (Li et al., ATC/TKDE) does hotness-aware bit reallocation. **Rosetta** and **SuRF** add range capability. **Ribbon filters** (Dillinger & Walzer, 2021) approach the space-optimality bound.
**Systems-SOTA.** RocksDB partitioned/prefix Bloom filters and dynamic per-level FPR; ScyllaDB, Cassandra tunable bloom_filter_fp_chance. *ElasticBF* and *bLSM* deploy access-frequency-driven allocation.

## 4. Upper Bound
Static optimum: the Monkey KKT allocation achieves total expected read cost within the $1.44\times$ Bloom constant of the information-theoretic optimum, and *exactly* optimal among Bloom-based schemes for known $\{a_i\}$. Using ribbon/cuckoo filters tightens the constant toward $1.0\times$ (ribbon within $\sim$1–3% of the entropy bound). For *online* adaptation, no-regret allocation gives total cost $\le (1+o(1))$ times the best fixed allocation in hindsight, at $O(\log)$ reconstruction overhead — but this is for the *allocation*, not the full per-range adaptivity, where bounds are partial.

## 5. Lower Bound
Information-theoretic: any approximate-membership filter with FPR $\varepsilon$ on $k$ keys needs $\ge k\log_2(1/\varepsilon)$ bits (Carter–Floyd–Gill–Wegman / Bloom's bound); no allocation can beat the per-filter entropy floor, so the *total*-cost optimum is bounded below by the corresponding convex program's value with $p_i = 2^{-m_i/k_i}$. **Adaptive** filters that guarantee bounded false positives over a *sequence* of queries face a stronger lower bound: maintaining adaptivity against an adversary requires $\Omega(k\log(1/\varepsilon) + k)$ extra bits or external state (Bender et al. — adaptivity is *not free*). Estimating per-range access frequencies from a stream has the Count-Min/heavy-hitters space lower bounds.

## 6. The Gap
**Empirically open.** The static convex optimum is solved; what remains genuinely open in practice: (1) the workload signal $a_i$ (per-range negative-access frequency) is *non-stationary* and must be estimated online — the joint problem of *estimation + allocation + reconstruction-cost* has no closed-form optimal policy; (2) per-key-range allocation interacts with compaction, which destroys and rebuilds filters, so the effective objective is a coupled control problem; (3) which filter *type* per region (Bloom vs ribbon vs cuckoo vs adaptive) is best is workload-dependent and decided empirically. The theory gives the bits-per-FPR floor; the *systems* question of total memory at fixed effective FPR under drift is settled only by benchmarks, not bounds.

## 7. Current Research (as of June 2026)
Active: learned filters (Kraska et al.'s *learned Bloom filters* and *sandwiched* variants) that exploit key structure to beat the entropy bound when keys are learnable; ribbon-filter deployment in RocksDB; reinforcement-learning / bandit bit-allocators that adapt to drift; range-capable adaptive filters merging SuRF/Rosetta with hotness awareness *(frontier — verify)*. Groups: DASlab (Idreos), Stony Brook/CMU (Bender, Farach-Colton, Pandey on quotient/adaptive filters), Mitzenmacher/Reviriego on adaptive cuckoo, Meta RocksDB team. Frontier: provable regret bounds for online per-range allocation under compaction-induced rebuilds *(frontier — verify)*.

## 8. Future Work
- A unified online allocator with regret bounds that accounts for compaction-driven filter rebuild costs.
- Per-region filter-type selection with theoretical guarantees (mixed Bloom/ribbon/learned).
- Robust frequency estimation feeding allocation under adversarial/drifting negative-query streams.
- Extending optimal allocation to *range* filters (ties to *Range Query Filters for LSM*).

## 9. Key References
- **[Foundational]** B. H. Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970.
- **[SOTA]** N. Dayan, M. Athanassoulis, S. Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017.
- **[SOTA]** P. C. Dillinger, S. Walzer. *Ribbon Filter: Practically Smaller than Bloom and Xor.* arXiv:2103.02515 / SEA, 2021.
- **[SOTA]** M. A. Bender, M. Farach-Colton, M. Goswami, R. Johnson, S. McCauley, S. Singh. *Bloom Filters, Adaptivity, and the Dictionary Problem.* FOCS, 2018.
- **[SOTA]** Y. Li, C. Tian, F. Guo, C. Li, Y. Xu. *ElasticBF: Elastic Bloom Filter with Hotness Awareness for Boosting Read Performance.* USENIX ATC, 2019.
- **[Foundational]** T. Kraska, A. Beutel, E. H. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
