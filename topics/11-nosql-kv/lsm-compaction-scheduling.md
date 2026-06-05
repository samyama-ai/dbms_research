# Optimal LSM Compaction Scheduling

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/lsm-compaction-scheduling` · **Status:** open

## 1. Problem Statement

Log-Structured Merge (LSM) trees buffer writes in memory, flush them as immutable sorted runs (SSTables), and periodically *compact* (merge-sort) overlapping runs to reclaim space and bound read fan-out. **Compaction scheduling** asks: at each point in time, given the current set of runs across levels, *which* runs to merge and *when*, so as to jointly minimize the three amplification factors:

- **Write amplification (WA):** bytes written to storage per byte of user data.
- **Read amplification (RA):** runs probed per point/range query (driven by Bloom-filter false positives and run count per level).
- **Space amplification (SA):** physical bytes stored per byte of live data (driven by obsolete/dead keys awaiting reclamation).

Variants: the **decision** variant (does a schedule exist meeting WA $\le \alpha$, RA $\le \beta$, SA $\le \gamma$ over a workload window?); the **offline optimization** variant (known future workload, minimize a weighted cost $w_W \cdot WA + w_R \cdot RA + w_S \cdot SA$); and the **online/competitive** variant (workload revealed incrementally, adversarial or stochastic). The realistic regime is online under a *dynamic, skewed, time-varying* workload with bounded CPU/IO budget for background compaction.

## 2. Mathematical Foundations

Let data size be $N$ entries, buffer (memtable) size $B$, and size ratio $T$ between adjacent levels, giving $L = \lceil \log_T (N/B) \rceil$ levels. The Dostoevsky/Monkey line of work formalizes the cost surface. For **leveling** (one run per level), worst-case point-lookup I/O on an empty key is $O(L \cdot e^{-m})$ where $m$ is bits-per-key in Bloom filters; write cost is $O(T \cdot L / B)$. For **tiering** ($T$ runs per level), write cost drops to $O(L/B)$ but lookup rises to $O(T \cdot L \cdot e^{-m})$.

The core insight (Monkey) is that **optimal Bloom-filter memory allocation is non-uniform**: assigning more bits to smaller levels minimizes total false positives under a fixed memory budget $M$, solved via Lagrangian optimization of $\sum_i N_i e^{-m_i}$ subject to $\sum_i N_i m_i = M$. Dostoevsky generalizes to a continuum (*lazy leveling*, *fluid LSM*) parameterized by $(T, K, Z)$ — runs per level, runs at the largest level, merge greediness.

The scheduling decision is a constrained sequential optimization; the offline weighted-cost variant maps to a job-scheduling / merge-tree construction problem, and the three-way Pareto surface $WA \times RA \times SA$ has no single dominating point — RUM-conjecture territory: you cannot simultaneously minimize all three.

$$ \min_{\text{schedule}} \; w_W \cdot WA + w_R \cdot RA + w_S \cdot SA \quad \text{s.t. compaction budget } \rho \text{ per unit time}. $$

## 3. State of the Art (SOTA)

**Systems-SOTA:** RocksDB's leveled and universal compaction with tunable triggers; Cassandra's SizeTieredCompactionStrategy and TimeWindowCompactionStrategy. **Dostoevsky** (Dayan & Idreos, SIGMOD 2018) and **Monkey** (Dayan, Athanassoulis & Idreos, SIGMOD 2017) define the navigable design space. **Wacky/Endure** (Huynh, Chaudhari, Idreos et al., VLDB 2022) adds *robust* tuning under workload uncertainty via robust optimization. Learned and reinforcement-learning schedulers — **Spooky** (Dayan et al. 2022) for partial compaction, and RL-driven compaction picking — are the systems frontier.

**Theory-SOTA:** the closed-form Pareto characterizations of fluid LSM give the best understood *static* configuration; no tight theory exists for the fully online adversarial scheduling problem.

## 4. Upper Bound

Best static configuration: fluid LSM achieves point-lookup $O(e^{-m})$ at the largest level with write cost $O((L/B)\cdot(1 + \text{greediness}))$, provably Pareto-optimal among leveling–tiering interpolations (Dostoevsky). For Bloom allocation, Monkey's allocation is *provably optimal* for minimizing expected false positives under fixed memory (KKT conditions). For online scheduling, only heuristic competitive guarantees exist; no constant-competitive online algorithm against an adaptive adversary is known for the full three-amplification objective.

## 5. Lower Bound

The **RUM conjecture** (Athanassoulis et al., EDBT 2016) posits an inherent trade-off: any access-method cannot simultaneously achieve optimal Read, Update, and Memory overheads — an informal impossibility that bounds the achievable Pareto frontier. Information-theoretically, sorted-run merging inherits comparison/IO lower bounds for external-memory sorting ($\Omega((N/B)\log_{M/B}(N/B))$ I/Os, Aggarwal–Vitter), which lower-bounds cumulative write work to maintain sortedness. No matching unconditional lower bound is known for the *online* weighted-cost objective with a compaction budget.

## 6. The Gap

The static design space is essentially closed (tight Pareto characterizations). The **online dynamic** problem is genuinely open: there is no tight competitive analysis matching a lower bound for adversarial or even stochastic time-varying workloads, and the three-way trade-off lacks a clean impossibility theorem (the RUM conjecture remains a conjecture, not a proof). Closing the gap requires either a constant-competitive online scheduler with a matching lower bound, or a proof that no such constant exists.

## 7. Current Research (as of June 2026)

Active directions: RL/learned compaction policies that adapt to workload drift (Idreos group, Harvard DASlab); robust tuning under uncertainty (*Endure* lineage); disaggregated/cloud-native LSM where compaction cost is offloaded to remote compute (e.g., RocksDB-Cloud, Neon-style separation) *(frontier — verify)*; and key-value separation (WiscKey, BlobDB) which changes the amplification calculus. There is growing interest in *workload-aware partial compaction* that picks sub-key-ranges rather than whole runs. Benchmarking via the *Endure/K-V-bench* harnesses continues.

## 8. Future Work

- A provably constant-competitive online compaction scheduler (or an impossibility proof).
- Turning the RUM conjecture into a theorem with a formal model.
- Joint optimization of compaction *with* Bloom-filter and cache memory under one budget.
- Cost models for compaction on disaggregated storage / NVMe-oF where IO latency and parallelism differ sharply from local SSD.

## 9. Key References

- **[Foundational]** Patrick O'Neil, Edward Cheng, Dieter Gawlick, Elizabeth O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996.
- **[SOTA]** Niv Dayan, Manos Athanassoulis, Stratos Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD 2017.
- **[SOTA]** Niv Dayan, Stratos Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD 2018.
- **[SOTA]** Andy Huynh, Harshal Chaudhari, Evimaria Terzi, Manos Athanassoulis. *Endure: A Robust Tuning Paradigm for LSM Trees under Workload Uncertainty.* VLDB 2022.
- **[Foundational]** Manos Athanassoulis et al. *Designing Access Methods: The RUM Conjecture.* EDBT 2016.
- **[Foundational]** Alok Aggarwal, Jeffrey Scott Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988.

---
*Part of the [DBMS Research catalog](../../README.md).*
