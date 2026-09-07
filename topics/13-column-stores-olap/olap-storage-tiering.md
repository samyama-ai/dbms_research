---
id: 13-column-stores-olap/olap-storage-tiering
title: "Workload-Aware Storage Tiering for OLAP"
topic: 13-column-stores-olap
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Workload-Aware Storage Tiering for OLAP

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/olap-storage-tiering` · **Status:** open

## 1. Problem Statement
Modern OLAP runs over a **storage hierarchy** with sharply different cost/latency/bandwidth: local DRAM cache, local NVMe SSD, and remote object storage (S3/GCS), sometimes with intermediate caching tiers. Data also comes in multiple **physical forms** — base columns, **materialized cuboids/aggregates** (OLAP cube), and alternative **encodings/compression** of the same column. The problem: decide **what to place where** — which columns, which precomputed cuboids, in which encoding, on which tier — to **minimize total cost** (storage \$ + I/O \$ + compute) subject to **latency SLOs** on a (drifting) query workload.

Variants:
- **Optimization (focus):** choose a placement $\pi:$ artifacts $\to$ tiers minimizing $\$$ subject to per-query latency $\le$ SLO. This generalizes **view/cuboid selection** and **caching/admission**.
- **Decision:** is there a placement meeting all SLOs within budget $B$? (NP-complete.)
- **Online:** workload is revealed over time; tiering must adapt (competitive analysis).

## 2. Mathematical Foundations
Cuboid selection is the **data-cube materialized-view selection** problem (Harinarayan–Rajaraman–Ullman, SIGMOD 1996): the cube lattice is a partial order; choosing $k$ cuboids to materialize to minimize query cost is **NP-hard**, but the benefit function is **monotone submodular**, so the greedy algorithm achieves the $(1-1/e)$ approximation (Nemhauser–Wolsey–Fisher). Tiered placement under a budget is a **knapsack / generalized assignment** problem (NP-hard), often with multiple knapsack constraints (capacity per tier). Caching/admission across tiers is **weighted caching / $k$-server**-flavored: optimal offline is an LP; online competitive ratio is $\Theta(\log k)$ (randomized) for weighted caching. SLO constraints turn it into **constrained optimization**; with stochastic workloads it becomes a **Markov decision process**. Cost model: expected latency $=\sum_q f_q\cdot \mathrm{cost}(q\mid\pi)$ where $\mathrm{cost}$ depends on which tier serves each accessed artifact (bandwidth/latency of that tier).

## 3. State of the Art (SOTA)
- **Cuboid/view selection:** Harinarayan, Rajaraman, Ullman (SIGMOD 1996) greedy submodular selection — still the theoretical backbone; extended by Gupta, Mumick for view selection under maintenance cost.
- **Industrial tiering:** Snowflake (DRAM/SSD local cache over S3 micro-partitions, automatic), Amazon Redshift **RA3 + AQUA** (managed storage with SSD cache, automatic data tiering), Databricks **Delta caching / Photon**, ClickHouse **storage policies / TTL-to-tier** moves, Apache Iceberg/Hudi with object-store tiers.
- **Encoding selection:** systems pick per-column encodings by sampling (Parquet/ORC, Procella/Capacitor, BtrBlocks — Kuschewski et al., SIGMOD 2023 — learned encoding selection).
- **Caching:** semantic/result caching, LRU/LFU + cost-aware admission; **Cachew/Autoscaling** and learned cache admission.
- **Auto-tuning advisors:** Microsoft AutoAdmin / Database Tuning Advisor lineage for index/MV selection.

## 4. Upper Bound
For cuboid selection, greedy gives a **$(1-1/e)\approx0.63$**-approximation to the optimal cost reduction under a cardinality (or, with curvature analysis, budget) constraint — the best possible for monotone submodular maximization unless P=NP. Multi-tier placement under one budget is a knapsack admitting an **FPTAS**; under multiple per-tier capacities it admits constant-factor approximations (generalized assignment, $\approx 2$-approx via LP rounding). Online cross-tier caching achieves $O(\log k)$-competitiveness (randomized weighted caching), and $k$-competitive deterministically.

## 5. Lower Bound
The decision form ("placement within budget meeting all SLOs") is **NP-complete** (knapsack/GAP reductions; view selection is NP-hard). Submodular maximization is hard to approximate beyond $(1-1/e)$ in the value-oracle model (Feige; Nemhauser–Wolsey) — so greedy is **optimal** among poly-time algorithms. Online weighted caching has a deterministic lower bound of $k$ and randomized $\Omega(\log k)$ (Fiat et al., Bansal–Buchbinder–Naor) — no online tiering policy can beat $\Omega(\log k)$ competitively. With drifting workloads, metrical-task-system lower bounds compound this.

## 6. The Gap
The **static, single-objective** subproblems are essentially closed (greedy is optimal for submodular cuboid selection; knapsack has an FPTAS; weighted caching has matching online bounds). The genuinely **open** problem is the *joint* one: simultaneously selecting **cuboids + encodings + tier placement** under **multiple SLO constraints** and a **drifting workload** is multi-objective, online, and constrained — no algorithm is known to be competitive against the joint offline optimum. Practical systems use decoupled heuristics (cache + TTL + advisor) with no end-to-end guarantee, and SLO-constrained submodular tiering with maintenance-cost coupling lacks tight approximation results.

## 7. Current Research (as of June 2026)
- **Learned / RL tiering and admission** that predict access frequency and place artifacts to meet SLOs at minimal \$ *(frontier — verify)*.
- **Learned encoding selection** (BtrBlocks, 2023; follow-ups) co-optimized with tier placement.
- **Serverless / disaggregated** OLAP economics: optimizing cache size vs. object-store reads vs. compute spin-up (Snowflake, Databricks, Redshift Serverless, DuckDB-over-S3 / MotherDuck) *(frontier — verify)*.
- **SLO-aware autoscaling** of cache tiers.
- Groups: TUM (Neumann — BtrBlocks/Umbra), CMU-DB self-driving (Pavlo), Microsoft Research auto-tuning lineage (Chaudhuri/Narasayya), Snowflake/Databricks/AWS engineering, CWI/DuckDB on cloud-storage execution.

## 8. Future Work
- A unified, SLO-constrained, online algorithm jointly over cuboids/encodings/tiers with provable competitiveness.
- Submodular tiering with maintenance/refresh cost and multiple SLO classes.
- Workload-drift-robust placement (distribution-shift guarantees).
- Cost models capturing real object-store pricing (request cost, egress, cold-start).

## 9. Key References
- **[Foundational]** Harinarayan, Rajaraman, Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996. — [DOI](https://doi.org/10.1145/235968.233333)
- **[Foundational]** Nemhauser, Wolsey, Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[SOTA]** Gupta, Mumick. *Selection of Views to Materialize Under a Maintenance Cost Constraint.* ICDT, 1999. — [DOI](https://doi.org/10.1007/3-540-49257-7_28)
- **[SOTA]** Vuppalapati et al. *Building an Elastic Query Engine on Disaggregated Storage (Snowflake).* NSDI, 2020. — [USENIX](https://www.usenix.org/conference/nsdi20/presentation/vuppalapati)
- **[Foundational]** Bansal, Buchbinder, Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[Survey]** Chaudhuri, Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN07.html)

## 10. Worked Example

Suppose four cuboids could be cached on a hot SSD tier holding **2 slots**; everything else lives on S3. Per-query latencies: an SSD hit costs $1$ unit, an S3 read $20$ units. Cuboid access frequencies (queries/hour): $c_1{=}50,\ c_2{=}30,\ c_3{=}10,\ c_4{=}5$.

Greedy submodular placement picks slots by marginal latency saved $= f_i\cdot(20-1)=19 f_i$:
- Round 1: $c_1$ saves $19\cdot50=950$. Pick $c_1$.
- Round 2: $c_2$ saves $19\cdot30=570$. Pick $c_2$.

Greedy stops at budget 2 with total hourly saving $950+570=1520$ units. The optimal 2-subset is also $\{c_1,c_2\}$, so greedy is exact here; in general it guarantees $\ge(1-1/e)\approx0.63$ of optimum (Nemhauser–Wolsey–Fisher).

Add an SLO: every query must finish $\le5$ units. Then any cuboid served from S3 ($20>5$) violates it, so the *decision* form ("place all within budget meeting SLOs") is infeasible at budget 2 — illustrating how SLO constraints turn the tractable submodular pick into an NP-complete feasibility question.

---
*Part of the [DBMS Research catalog](../../README.md).*
