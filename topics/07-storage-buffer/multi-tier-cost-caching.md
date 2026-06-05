# Cost-Aware Caching Across DRAM/SSD/Object Tiers

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/multi-tier-cost-caching` · **Status:** partially-solved

## 1. Problem Statement
Modern data systems span a **deep storage hierarchy**: DRAM (fast, expensive, small), local NVMe **SSD** (medium), and remote **object storage** (S3-class: high latency, per-request and per-byte egress *dollar* cost, effectively unbounded). A cache manager must decide what to keep in each tier to jointly optimize **hit rate** (latency) and **cost** — both the dollar cost of object-store requests/egress and the byte-movement (write-amplification, SSD endurance) cost of promotion/demotion.

This is not classical paging: the objective is multi-criteria. The decision is *where* each object lives, with **asymmetric, monetized** miss costs (an object-store fetch costs real money and milliseconds; an SSD hit costs neither but consumes endurance on writes).

Variants:
- **Optimization:** minimize a weighted sum $\alpha\cdot\text{stall} + \beta\cdot\text{\$} + \gamma\cdot\text{bytes-moved}$.
- **Constrained:** minimize \$ subject to a latency-SLO, or maximize hit rate subject to a \$ budget.
- **Decision:** is a target (hit-rate, \$) Pareto point feasible given tier capacities?

Marked *partially-solved* because the underlying **weighted/general caching** core is well-understood theoretically, but the deep-hierarchy, monetized, write-aware composite objective is only addressed by heuristics with partial guarantees.

## 2. Mathematical Foundations
The single-tier core is **weighted caching** (Cost model: arbitrary fetch cost $c_p$ per object) and **general caching** (also variable object size $w_p$) — see `weighted-caching-variable-size`. The deployed optimum there is **Greedy-Dual-Size(-Frequency)** / **Landlord** (Young 1994; Cao–Irani 1997), which is $k$-competitive deterministically and $O(\log k)$ randomized (Bansal–Buchbinder–Naor).

For multiple tiers, model a **hierarchical caching** instance: tiers $T_0,\dots,T_{L}$ with capacities $k_i$, hit costs $a_0<\dots<a_L$, and promotion/demotion (movement) costs $m_{ij}$. The composite cost makes it an online problem on a metric with **service costs + movement costs** — a **Metrical Task System / weighted $k$-server**-flavored model. The multi-criteria objective lives on a **Pareto frontier** between hit rate and dollars; scalarizing with weights $(\alpha,\beta,\gamma)$ recovers a single weighted-caching instance per weight vector.

Key analytic tools: the covering **LP** for caching and its online primal–dual solution; **submodularity** of coverage/hit-rate (used by some admission heuristics); and the **bit/fault model** distinction for accounting byte-movement vs. per-request cost.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Greedy-Dual-Size-Frequency and TinyLFU/W-TinyLFU admission (Einziger–Friedman) are the production cost/size-aware policies; **S3-FIFO** (Yang et al., SOSP 2023) is a recent simple, scalable eviction competitive with complex policies. Cloud-tier caches: **CacheLib** (Berger et al., OSDI 2020) — Meta's general caching engine with DRAM+SSD tiers and admission policies; **AdaptSize** (Berger et al., NSDI 2017) — size-aware admission with a Markov model. DB-side: tiered buffer pools that cache S3/object data on local NVMe (e.g., Snowflake-/Redshift-style local SSD caches, Neon, RocksDB secondary cache).

**Theory-SOTA:** weighted/general caching is essentially settled ($\Theta(\log k)$ randomized); multi-tier with movement costs has $O(\text{polylog})$ competitive results via $k$-server/MTS but not for the monetized, write-aware composite objective.

## 4. Upper Bound
- Single-tier weighted/general caching: deterministic $k$ (Landlord), randomized $O(\log k)$ (Bansal–Buchbinder–Naor), offline $O(1)$-approximation.
- Multi-tier with movement: $O(\log(\sum_i k_i))$-type online bounds in the symmetric idealized model; $k$-server polylog ratios when cast as a metric.
- Learning-augmented variants give $O(1)$ consistency with $O(\log k)$ robustness when predictions are available.
No single result yields a guarantee for the full $\alpha,\beta,\gamma$ composite with write-amplification.

## 5. Lower Bound
Inherits randomized paging $\Omega(\log k)$ and deterministic $k$. Offline general caching is **NP-hard**; with byte-movement costs the offline tiered-placement problem embeds constrained assignment and remains NP-hard. The multi-criteria version has no single optimum — only a Pareto frontier — so "lower bound" is per-scalarization. No tight bound is known for the write-aware, monetized hierarchy.

## 6. The Gap
The single-tier and idealized multi-tier theory is closed up to constants; the **open part** is a provable policy for the *deep, monetized, write-aware* hierarchy that (a) handles per-request **dollar** costs and byte-movement/endurance jointly, (b) navigates the hit-rate/\$ Pareto frontier online, and (c) matches or beats CacheLib/S3-FIFO-class heuristics with a guarantee. Bridging requires casting the composite objective into a tractable online model (likely weighted general caching with movement) and proving competitive or learning-augmented bounds for it.

## 7. Current Research (as of June 2026)
- **Cost-aware cloud caching:** minimizing object-store egress \$ in lakehouse/DB caches (Snowflake, Databricks, Neon) *(frontier — verify specific results)*.
- **Simple scalable eviction** (S3-FIFO, SIEVE — Zhang et al., NSDI 2024) replacing LRU-class policies, with emerging analysis *(frontier — verify)*.
- **Learning-augmented weighted caching** carried to multi-tier settings; flash-aware admission to limit write amplification (CacheLib line; Berger, Yang, Pavlo groups).
- ML-driven tier controllers optimizing the \$/latency Pareto point.

## 8. Future Work
A competitive theory for monetized multi-tier caching with write-amplification; online Pareto-frontier tracking for hit-rate vs. \$; endurance-aware demotion guarantees; integration with the disaggregated/CXL tier (see `disaggregated-buffer-pool`); benchmark suites with real object-store pricing.

## 9. Key References
- **[Foundational]** N. Young. *On-Line File Caching (Landlord).* SODA 1998 / Algorithmica.
- **[Foundational]** P. Cao, S. Irani. *Cost-Aware WWW Proxy Caching Algorithms (GreedyDual-Size).* USENIX Symp. Internet Tech., 1997.
- **[SOTA]** B. Berger, B. Berg, T. Zhang, et al. *The CacheLib Caching Engine: Design and Experiences at Scale.* USENIX OSDI 2020.
- **[SOTA]** D. Berger, R. Sitaraman, M. Harchol-Balter. *AdaptSize: Orchestrating the Hot Object Memory Cache in a Content Delivery Network.* USENIX NSDI 2017.
- **[SOTA]** J. Yang, Y. Zhang, et al. *FIFO Queues Are All You Need for Cache Eviction (S3-FIFO).* ACM SOSP 2023.
- **[SOTA]** N. Bansal, N. Buchbinder, J. Naor. *Randomized Competitive Algorithms for Generalized Caching.* STOC 2008.
- **[Survey]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge Univ. Press, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
