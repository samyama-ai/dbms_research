# Optimal storage-compute disaggregation boundary

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/disaggregation-boundary` · **Status:** open

## 1. Problem Statement

In a disaggregated architecture, the compute tier (query engine) and storage tier (durable bytes) are separated by a network. Every operator in a physical plan can run on either side: a filter or aggregation may be *pushed down* to storage to reduce bytes transferred, or *pulled up* to compute where CPU and memory are richer. The **disaggregation-boundary problem** asks: given a query plan, a cost model for remote access (latency, bandwidth, IOPS pricing), and capability/resource limits of the storage tier, assign each operator (or sub-operator function) to a tier so as to minimize total data movement (or end-to-end cost/latency).

Variants: (a) **decision** — does an assignment exist with movement $\le B$? (b) **optimization** — minimize total bytes-on-wire or dollar cost; (c) **online/adaptive** — re-decide per partition as selectivities are observed at runtime.

## 2. Mathematical Foundations

Model the plan as a rooted operator tree (or DAG with shared subplans) $G=(V,E)$. Each node $v$ has a tier label $\ell(v)\in\{S,C\}$. An edge $(u,v)$ carries data volume $d(u,v)$; crossing the boundary (i.e., $\ell(u)\ne\ell(v)$) incurs cost $\beta\cdot d(u,v) + \tau$ for per-byte cost $\beta$ and fixed latency $\tau$. Storage-side capacity constraints (CPU, allowed operator classes) restrict feasible labels.

For a *tree* with edge-crossing costs and per-node feasibility, the minimum-cost cut is solvable by dynamic programming in $O(|V|)$ (each node memoizes best cost given its own tier). With shared subexpressions (a DAG) and side-capacity budgets, the problem generalizes to **multiway graph partitioning under a knapsack constraint**, related to min-cut with node capacities. The objective is essentially a *placement* problem; without capacity it reduces to a generalized $s$–$t$ cut (compute=source, storage=sink) and is polynomial via max-flow/min-cut. Capacity and operator-class constraints push it toward **submodular minimization** or integer programming.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Amazon Aurora (Verbitski et al., SIGMOD 2017–2018) pushes redo-log application and some reads into storage. Snowflake (SIGMOD 2016) and AWS Redshift's *Advanced Query Accelerator (AQUA)* push scans/filters to the storage layer. PolarDB / PolarDB Serverless (VLDB 2021) and Microsoft Socrates (SIGMOD 2019) disaggregate log, page, and compute tiers. *FlexPushdownDB* (Yang et al., VLDB 2021) studies caching-vs-pushdown trade-offs explicitly.
- **Theory-SOTA:** operator-placement is treated as cost-based plan enumeration; the boundary decision is folded into the optimizer's search (Cascades-style). No clean optimal-placement theory dominates.

## 4. Upper Bound

For tree-shaped plans with linear crossing costs and no storage-capacity limit: **exact optimum in $O(|V|)$** via bottom-up DP, or equivalently via min-cut in $O(|V|^2|E|)$. For DAGs with shared subplans the $s$–$t$ min-cut formulation gives polynomial-time optimal placement when costs are submodular in the cut. Approximation guarantees for the capacitated (knapsack-constrained) variant follow from generalized assignment: a $(1+\epsilon)$ PTAS-style bound exists when the storage tier has a single scalar capacity.

## 5. Lower Bound

Adding multiple storage-side resource constraints (CPU *and* IOPS *and* allowed-operator classes) makes the placement problem NP-hard by reduction from **multidimensional knapsack / generalized assignment**. The online variant has an information-theoretic lower bound: with unknown selectivities, no deterministic placement policy can be better than $\Omega(\sqrt{n})$-competitive against the offline optimum in adversarial-selectivity instances (a balance argument analogous to ski-rental / online cut problems).

## 6. The Gap

The unconstrained tree case is *closed* (polynomial, optimal). The genuinely open part is the **realistic** case: shared subplans, multi-resource storage limits, runtime-adaptive selectivities, and dollar-priced heterogeneous resources jointly. No system provably minimizes data movement here; production systems use heuristics. Closing the gap requires either a tight approximation algorithm for the capacitated DAG placement or a matching hardness-of-approximation result.

## 7. Current Research (as of June 2026)

Active threads: computational-storage / SmartSSD pushdown (CIDR, VLDB), "near-data" processing for lakehouse engines, and learned pushdown decisions. Groups at CMU (Andy Pavlo's group), MIT (DSAIL), Wisconsin, and cloud-vendor labs (AWS, Microsoft GSL, Alibaba) are active. *(frontier — verify)* Several 2025–2026 papers explore RDMA/CXL-based memory disaggregation shifting the boundary toward *memory* rather than storage, which reframes the cost model around far-memory latency.

## 8. Future Work

- A unified cost model spanning latency, bandwidth, and per-request pricing for the boundary decision.
- Provable competitive ratios for online, partition-adaptive pushdown.
- Co-design with caching (FlexPushdownDB-style) so placement and cache admission are jointly optimized.
- CXL/far-memory variants where the "boundary" is a memory tier, not durable storage.

## 9. Key References

- **[Foundational]** Verbitski, Gupta, et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017.
- **[SOTA]** Antonopoulos, Kossmann, et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019.
- **[SOTA]** Yang, Wu, et al. *FlexPushdownDB: Hybrid Pushdown and Caching in a Cloud DBMS.* VLDB, 2021.
- **[SOTA]** Cao, Liu, et al. *PolarDB Serverless: A Cloud Native Database for Disaggregated Data Centers.* SIGMOD, 2021.
- **[Survey]** Dageville, Cruanes, et al. *The Snowflake Elastic Data Warehouse.* SIGMOD, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
