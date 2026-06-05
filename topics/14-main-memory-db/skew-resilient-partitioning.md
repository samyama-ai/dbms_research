# Skew-Resilient Partitioned IMDB

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/skew-resilient-partitioning` · **Status:** partially-solved

## 1. Problem Statement
Partitioned, shared-nothing main-memory OLTP systems (H-Store/VoltDB style) eliminate latching and locking overhead by assigning each partition to a single thread/core that executes transactions serially. This is optimal when every transaction touches exactly one partition and load is balanced. It collapses under **skew**: (a) *data skew* — partitions hold uneven amounts of hot data; (b) *access skew* — a few keys (or partitions) receive a disproportionate share of requests (Zipfian); and (c) *multi-partition transactions* — which require coordination and stall single-threaded cores.

**Problem:** design a partitioning + execution scheme for a single-threaded-per-core IMDB that retains the latch-free fast path while remaining performant under *dynamic, a priori unknown, time-varying* skew. Variants:
- **Optimization (static):** Given a workload graph, find a partitioning minimizing multi-partition transactions and balancing load — the **min-cut balanced graph partitioning** problem.
- **Online/dynamic:** Continuously repartition/migrate to track shifting hot spots while bounding migration cost and never violating consistency.
- **Decision:** Does a balanced $k$-partition with $\le c$ cut edges (cross-partition transactions) exist?

## 2. Mathematical Foundations
Represent the workload as a hypergraph $H=(V,E)$: vertices $V$ are tuples (or keys), and each transaction induces a hyperedge over the tuples it accesses, weighted by frequency. A partition is a map $\pi: V \to \{1,\dots,k\}$. Define **cut** $\mathrm{cut}(\pi) = \sum_{e \in E} w(e)\,\mathbf{1}[\pi \text{ splits } e]$ (proportional to distributed-transaction rate) and **imbalance** $\max_j \mathrm{load}(j) / \overline{\mathrm{load}}$. We want
$$\min_{\pi}\; \mathrm{cut}(\pi) \quad \text{s.t.}\quad \mathrm{load}(j) \le (1+\varepsilon)\tfrac{\mathrm{load}(V)}{k}\ \forall j.$$
Under Zipfian access with skew parameter $s$, the $i$-th hottest key has probability $\propto i^{-s}$; balancing load then requires *fewer hot keys per partition*, conflicting with cut minimization. The dynamic case is an online problem measured by competitive ratio against an optimal offline repartitioning, with a *migration cost* term penalizing moved tuples (metrical-task-system / online balanced-partitioning flavor).

## 3. State of the Art (SOTA)
- **Systems-SOTA.** **Schism** (Curino, Jones, Zhang, Madden, VLDB 2010) builds the workload graph and applies METIS-style balanced min-cut + decision-tree range extraction. **E-Store** (Taft et al., VLDB 2014) adds *two-tier* elastic, online re-partitioning that detects hot tuples and migrates them to relieve skew. **Clay** (Serafini et al., VLDB 2016) does incremental "clump" migration tracking load, with strong results under shifting skew. **Squall** (Elmore et al., SIGMOD 2015) provides live reconfiguration mechanics. **Morsel-driven** (Leis et al., SIGMOD 2014) is the analytics counterpart: NUMA-aware work-stealing instead of static partitioning.
- **Theory-SOTA.** Balanced graph partitioning admits no constant approximation in general; best known is $O(\sqrt{\log n \log k})$ (Krauthgamer–Naor–Schwartz) for balanced separators.

The problem is *partially solved*: Clay/E-Store handle moderate dynamic skew well in practice but lack worst-case guarantees and degrade under adversarial or extremely high multi-partition rates.

## 4. Upper Bound
For static balanced partitioning, the best provable approximation for minimum balanced cut is $O(\sqrt{\log n \log k})$ via semidefinite/spectral relaxation. Practical solvers (METIS, KaHIP) give no approximation guarantee but run in near-linear time. For the *online* hot-tuple variant, Clay-style greedy clump migration is a heuristic with empirically bounded migration but no proven competitive ratio. Single-partition execution itself is $O(1)$ latch-free per transaction — the entire upper-bound difficulty is in the partitioning subproblem.

## 5. Lower Bound
Balanced graph/hypergraph partitioning is **NP-hard** (Min-Bisection is NP-hard; balanced separator is hard to approximate within any constant under standard assumptions; Unique-Games-hardness results rule out a PTAS for balanced cut). Thus no efficient exact static optimum exists unless P=NP. For the **online** dynamic case, lower bounds from online balanced graph partitioning (Avin, Bienkowski, Loukas, et al.) show any online algorithm has competitive ratio $\Omega(k)$ against migration cost in the worst case — establishing that fully skew-resilient repartitioning with bounded migration is impossible in the adversarial model. Coordination for multi-partition transactions inflicts an inherent serialization stall lower-bounded by the cross-partition critical path.

## 6. The Gap
Static partitioning is "solved" up to NP-hardness (good heuristics, hardness floor). The real gap is **online**: practical systems (Clay) work well on realistic, slowly-shifting skew, but the $\Omega(k)$ adversarial competitive lower bound means there is *no algorithm that is provably good under arbitrary dynamic skew*. The open question is whether *learning-augmented* or *beyond-worst-case* (smoothed / stochastically-shifting) models admit policies with provable bounded migration and bounded distributed-transaction rate — closing the gap between strong empirical behavior and bleak worst-case theory.

## 7. Current Research (as of June 2026)
Directions: learned cost models predicting hot-key drift; reinforcement-learning repartitioning; beyond-worst-case competitive analysis for online balanced partitioning with predictions; and hardware-assisted approaches that tolerate skew without repartitioning (lock-free hot-key handling, delegation). Groups: MIT (Madden), CMU (Pavlo — self-driving DB lineage), EPFL/TU Munich (Leis, Neumann morsel-driven analytics), and the online-algorithms community on dynamic balanced partitioning. Learning-augmented partitioning with provable robustness/consistency tradeoffs is an active 2025-2026 frontier *(frontier — verify)*.

## 8. Future Work
- Competitive online repartitioning under stochastic skew models with bounded migration.
- Tight robustness/consistency bounds for learning-augmented partitioners.
- Eliminating multi-partition stalls via deterministic ordering (Calvin) blended with partitioned execution.
- Skew handling that avoids data movement entirely (request delegation, key replication with reconciliation).

## 9. Key References
- **[SOTA]** Curino, Jones, Zhang, Madden. *Schism: a Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)
- **[SOTA]** Taft, Mansour, Serafini, Duggan, Elmore, Aboulnaga, Pavlo, Stonebraker. *E-Store: Fine-Grained Elastic Partitioning for Distributed Transaction Processing Systems.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735514)
- **[SOTA]** Serafini, Taft, Elmore, Pavlo, Aboulnaga, Stonebraker. *Clay: Fine-Grained Adaptive Partitioning for General Database Schemas.* VLDB, 2016. — [DOI](https://doi.org/10.14778/3025111.3025125)
- **[SOTA]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[Foundational]** Krauthgamer, Naor, Schwartz. *Partitioning Graphs into Balanced Components.* SODA, 2009. — [DOI](https://doi.org/10.1137/1.9781611973068.102)
- **[Foundational]** Kallman et al., Stonebraker. *H-Store: A High-Performance, Distributed Main Memory Transaction Processing System.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1454159.1454211)

## 10. Worked Example

Consider 6 keys $\{a,b,c,d,e,f\}$ and $k=2$ cores. Transactions (with frequencies) form a workload graph: $T_1=\{a,b\}\times 50$, $T_2=\{b,c\}\times 40$, $T_3=\{d,e\}\times 30$, $T_4=\{e,f\}\times 20$, plus a hot cross link $T_5=\{c,d\}\times 5$.

Try partition $P_1=\{a,b,c\}$, $P_2=\{d,e,f\}$. Only $T_5$ is split, so $\mathrm{cut}=5$ (5 distributed txns/sec). Loads: $P_1$ touched by $50+40=90$ accesses, $P_2$ by $30+20=50$ — imbalance $\frac{90}{70}\approx1.29$, i.e. $\varepsilon=0.29$.

Now inject Zipfian access skew: key $b$ alone gets $90\%$ of traffic. Single-threaded $P_1$ now saturates while $P_2$ idles. No min-cut helps — splitting $b$'s transactions across cores would raise $\mathrm{cut}$ from 5 toward 90. This is the static-vs-dynamic tension: Clay would migrate a "clump" around $b$ (e.g. replicate the hot key), trading $O(1)$ cut increase for restored balance.

---
*Part of the [DBMS Research catalog](../../README.md).*
