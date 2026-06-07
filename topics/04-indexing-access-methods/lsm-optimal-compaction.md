---
id: 04-indexing-access-methods/lsm-optimal-compaction
title: "Optimal LSM-tree compaction policy"
topic: 04-indexing-access-methods
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal LSM-tree compaction policy

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/lsm-optimal-compaction` · **Status:** partially-solved

## 1. Problem Statement
A **log-structured merge (LSM) tree** buffers writes in memory, flushes sorted runs to disk, and periodically **compacts** (merges) runs to bound read cost and reclaim space. The *compaction policy* decides **when** to merge, **which** runs, and **how many per level**. It governs the three-way tradeoff among write amplification $W$, read cost (point/range/scan), and space amplification.

The problem: **find the Pareto-optimal compaction policy and its tuning** across the full design space — given a workload (read/write/range mix, distribution, point-query selectivity, deletes), a memory budget, and a hardware cost model, output policy parameters minimizing one cost subject to bounds on the others.

- **Optimization variant:** minimize expected total cost $= c_r \cdot R + c_w \cdot W$ subject to space bound $M \le M^\*$.
- **Decision variant:** does a policy achieving $(R^\*, W^\*, M^\*)$ exist for the given workload?

This is *partially solved*: the leveling/tiering frontier and Bloom-filter allocation are characterized; full workload-adaptive optimality is not.

## 2. Mathematical Foundations
Let $T$ = size ratio between levels, $L = \Theta(\log_T \tfrac{N}{B})$ levels, $B$ = buffer entries, $N$ = data size, $P$ = buffer pages. Classical results (Bigtable/LevelDB analysis; O'Neil et al. 1996):

- **Leveling:** write amp $W = O(T \cdot L)$, point lookup $O(L)$ run probes.
- **Tiering:** $W = O(L)$, lookup $O(T \cdot L)$.

**Bloom-filter modeling:** with $M_{\text{filt}}$ total filter bits, per-level false-positive rates $p_i$ minimize $\sum p_i$ under $\sum$-bit constraint; **Monkey** (Dayan–Athanassoulis–Idreos, SIGMOD 2017) shows optimal allocation gives *unequal* $p_i$ across levels, reducing worst-case lookup from $O(L)$ to $O(1)$ expected I/O. **Dostoevsky** introduces *lazy leveling* (a hybrid) and the **Fluid LSM** continuum parameterized by per-level merge greediness $(K, Z)$, proving Pareto-dominance over pure leveling/tiering.

## 3. State of the Art (SOTA)
- **Theory/modeling:** Monkey (2017), Dostoevsky (SIGMOD 2018), **Fluid LSM** / Wacky continuum, and **Cosine** (auto cost-model navigation) give closed-form cost models and provably Pareto-optimal points within their parameterized families.
- **Systems:** RocksDB (leveled + universal), Cassandra (tiered + LCS), ScyllaDB; **SILK/SILK+** (I/O scheduling to bound tail latency), **Lethe** (delete-aware compaction, SIGMOD 2020), **Spooky**, **Endure** (robust tuning under workload uncertainty, VLDB 2022).

## 4. Upper Bound
Within the Fluid LSM family, the achievable frontier is $W = O(\tfrac{T}{K}\cdot L \;+\; Z\cdot L)$ with tunable point/range/space costs; Monkey gives expected $O(e^{-M_{\text{filt}}/N})$ point-lookup I/O. These are **optimal within the parameterized policy class** (cost-model SOTA), not over *all* conceivable compaction strategies.

## 5. Lower Bound
No tight unconditional lower bound over *all* compaction policies. Known constraints: sort-merge external dictionaries require $W = \Omega(\log_{M/B} N/B)$-type amplification (Aggarwal–Vitter sorting bound) for fully-merged reads; the RUM conjecture frames the three-way obstruction informally. The hardness lies in **non-stationary, adaptive** workloads: choosing a policy online competitive against the best fixed policy is essentially a metrical-task / online-optimization problem with no proven competitive ratio for the full space.

## 6. The Gap
Closed-form optimality exists **within** $(T, K, Z, \text{filter bits})$ families; **open** is (a) optimality *across all* policies including partial/range-partitioned and key-skew-aware compaction, and (b) **online/adaptive** optimality under drifting workloads with provable regret. Closing it needs either a matching lower bound proving the Fluid family is universal, or new policies (e.g., learned, per-key-range) that escape it.

## 7. Current Research (as of June 2026)
- **Learned/RL compaction schedulers** that predict hot ranges and trigger merges adaptively *(frontier — verify)*.
- **Robust tuning** beyond Endure — distributionally-robust and bandit formulations of $(T,K,Z)$ selection *(frontier — verify)*.
- Delete- and TTL-aware compaction (Lethe lineage); disaggregated/NVM and key-value-separation (WiscKey, BlobDB) reshaping the cost model.
- Groups: Harvard DASlab, BU (Athanassoulis), Wisconsin (WiscKey lineage), industrial RocksDB/Speedb teams.

## 8. Future Work
- Prove an online competitive ratio for adaptive compaction vs. best fixed policy.
- Unify key-value separation, filters, and merge greediness into one cost model with a single optimality theorem.
- Workload-drift detection with bounded re-tuning cost.

## 9. Key References
- **[Foundational]** P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[SOTA]** N. Dayan, M. Athanassoulis, S. Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** N. Dayan, S. Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree-Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** S. Sarkar, et al. *Lethe: A Tunable Delete-Aware LSM Engine.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389757)
- **[SOTA]** A. Huynh, et al. *Endure: A Robust Tuning Paradigm for LSM Trees Under Workload Uncertainty.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2110.13801)
- **[Survey]** C. Luo, M. Carey. *LSM-based Storage Techniques: A Survey.* VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)

## 10. Worked Example

Take size ratio $T=4$, buffer $B=2$ entries, data $N=32$ entries, so $L=\log_T(N/B)=\log_4 16=2$ levels below the buffer.

**Leveling** keeps one run per level: write amp $W=O(T\cdot L)=4\cdot 2=8$ (each entry is re-merged up to $T$ times per level). A point lookup probes $L=2$ runs, but every run's Bloom filter is checked — worst case $O(L)$ I/O.

**Tiering** keeps up to $T$ runs per level before merging: write amp drops to $W=O(L)=2$, but a lookup now probes $T\cdot L=8$ runs.

**Monkey's twist:** with a fixed filter budget, set per-level false-positive rates $p_i$ proportional to level size rather than uniform. With uniform $p=0.01$ across $L=2$ levels, expected wasted probes $\approx \sum p_i = 0.02$. Reallocating bits to make deeper (larger) levels have *lower* $p_i$ minimizes $\sum p_i$ subject to total bits — driving expected lookup I/O toward $O(1)$. The Fluid LSM continuum then tunes the merge greediness $(K,Z)$ to slide along the $W$-vs-lookup Pareto frontier between these two extremes.

---
*Part of the [DBMS Research catalog](../../README.md).*
