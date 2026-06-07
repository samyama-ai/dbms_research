---
id: 02-query-optimization/parallel-aware-optimization
title: "Optimizing across the memory hierarchy and parallelism"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimizing across the memory hierarchy and parallelism

> **Topic:** Query Optimization · **ID:** `02-query-optimization/parallel-aware-optimization` · **Status:** open

## 1. Problem Statement
Classical cost-based optimization assumes a roughly uniform-cost memory and a single execution context. Modern hardware violates both: **multi-core / multi-socket NUMA** (non-uniform memory access latencies and bandwidths), deep **cache hierarchies** (L1/L2/LLC, TLBs, prefetchers), **SIMD**, and elastic **intra-query parallelism**. The problem is to do **cost-based planning that jointly accounts for**:
- **intra-query parallelism** — degree of parallelism (DOP), pipeline/morsel scheduling, exchange/repartition placement;
- **NUMA** — where operators and data live across sockets, and cross-socket traffic;
- **caches/memory hierarchy** — locality, working-set fit, cache-conscious operator and data-layout choices.

These choices interact (more parallelism can blow caches and add NUMA traffic), so optimizing them independently is suboptimal. Variants: static (compile-time) plan + DOP selection; **adaptive** runtime scheduling (morsel-driven); and the **joint decision** version (plan + DOP + placement) which is the open target.

## 2. Mathematical Foundations
The classical cost model $c(p)=\sum_{\text{op}} (w_{\text{cpu}}\,\text{cpu} + w_{\text{io}}\,\text{io})$ must be replaced by a **resource-and-topology-aware** model. A useful abstraction is a **DAG-scheduling problem on heterogeneous, capacity-constrained resources**:
- The plan is a DAG of pipelines; each operator has a work vector (CPU, memory bandwidth, cache footprint).
- Hardware is a graph of cores/sockets with link bandwidths and memory latencies (a NUMA topology).
- A schedule assigns work to resources over time; cost = makespan / total resource-time under contention.

This is closely related to **malleable / moldable task scheduling** and **DAG scheduling on related machines**, which are **NP-hard**, with classical approximation results (e.g. list scheduling's $2-1/m$ bound for makespan; LP-based moldable-task schedulers achieving constant factors). Cache effects bring in the **external-memory / cache-oblivious model** (Aggarwal–Vitter $\Theta(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/O bound for sorting; Frigo et al. cache-oblivious algorithms) and the **roofline model** (operational intensity vs. bandwidth) for predicting whether an operator is compute- or bandwidth-bound. NUMA adds a non-uniform-cost overlay; bandwidth contention makes per-operator costs **non-separable**, breaking the additivity that DP optimization relies on.

## 3. State of the Art (SOTA)
- **Morsel-driven parallelism** (Leis, Boncz, Kemper, Neumann, SIGMOD 2014) — NUMA-aware, work-stealing, runtime-adaptive intra-query parallelism in HyPer/Umbra; the systems SOTA, deferring much of "optimization" to a smart *scheduler* rather than the cost-based planner.
- **Cache-conscious / hardware-conscious operators:** radix-partitioned hash joins (Manegold–Boncz–Kersten; Balkesen et al.), vectorized (MonetDB/X100, Vectorwise) and data-centric compiled (HyPer) execution.
- **Exchange/parallel planning:** Volcano exchange operator (Graefe) and MPP optimizers (Orca/Greenplum, Spark Catalyst) that plan partitioning/shuffles cost-based — but treat DOP and NUMA coarsely.
- Cost-based **DOP selection** exists in commercial systems (SQL Server, Oracle) but is largely heuristic and decoupled from join-order choice.

## 4. Upper Bound
There is **no optimizer with provable optimality** for the joint (plan + DOP + NUMA + cache) problem. Component upper bounds:
- **DAG/moldable scheduling:** constant-factor approximations for makespan (list scheduling $2-1/m$; LP-rounded moldable schedulers $\approx (2+\epsilon)$ or better) — but these assume known, separable task costs, which contention violates.
- **Cache complexity:** cache-oblivious sorting/joins meet the optimal Aggarwal–Vitter I/O bound *automatically*, an algorithmic upper bound independent of cache parameters.
- **Practice:** morsel-driven scheduling achieves near-linear speedup empirically on many workloads, but with no worst-case guarantee on plan quality.

## 5. Lower Bound
- **Optimal parallel scheduling of the plan DAG is NP-hard** (precedence-constrained / moldable scheduling on multiple machines is strongly NP-hard), and join-order choice already makes the planning problem NP-hard; the joint problem is at least as hard.
- **Memory-hierarchy lower bounds:** the **Aggarwal–Vitter** $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/O lower bound for sorting/permutation, and **red-blue pebble / memory-bandwidth** lower bounds (Hong–Kung) bound the achievable data movement for join/aggregation kernels — unavoidable traffic that any plan must pay.
- **Contention non-separability** means no additive cost model is exact; this is a structural (not merely complexity) barrier to clean DP optimization.

## 6. The Gap
Wide open. We have (a) strong *execution-side* engineering (morsel-driven, cache-conscious operators) that adaptively reacts to hardware, and (b) classical cost-based *planning* that is largely hardware-oblivious — but **no principled cost-based optimizer that jointly plans join order, DOP, placement, and layout** with respect to NUMA/cache/contention, and certainly none with approximation guarantees. The gap is both modeling (a tractable, contention-aware, composable cost model) and algorithmic (optimizing over it). Whether to *plan* these jointly or *schedule* them adaptively at runtime is itself unsettled.

## 7. Current Research (as of June 2026)
- **Learned scheduling/DOP** and resource-aware optimizers that predict contention and pick DOP/placement jointly with the plan. *(frontier — verify)*
- **Hardware-aware cost models** incorporating roofline/bandwidth and NUMA topology into the optimizer's cost function. *(frontier — verify)*
- Optimization for **heterogeneous hardware** (GPU/CPU co-processing, CXL-attached and disaggregated memory, persistent memory) where the hierarchy is even less uniform. *(frontier — verify)*
- Groups: Neumann/Kemper/Leis (TUM/TU Munich, morsel/Umbra), Boncz (CWI), Kersten lineage, MPP-optimizer teams (Databricks/Photon, cloud warehouses).

## 8. Future Work
- A composable, contention-aware cost algebra that restores enough additivity for tractable optimization.
- Approximation algorithms for joint plan + DOP + placement with provable guarantees.
- Co-design of optimizer and morsel-style scheduler: which decisions belong at compile vs. runtime.
- Optimization for disaggregated / CXL memory and heterogeneous accelerators.

## 9. Key References
- **[SOTA]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[Foundational]** Graefe. *Encapsulation of Parallelism in the Volcano Query Processing System.* SIGMOD, 1990. — [DOI](https://doi.org/10.1145/93597.98720)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** Manegold, Boncz, Kersten. *Optimizing Database Architecture for the New Bottleneck: Memory Access.* VLDB Journal, 2000. — [DOI](https://doi.org/10.1007/s007780000031)
- **[Foundational]** Frigo, Leiserson, Prokop, Ramachandran. *Cache-Oblivious Algorithms.* FOCS, 1999. — [DBLP](https://dblp.org/rec/conf/focs/FrigoLPR99.html)
- **[Survey]** Williams, Waterman, Patterson. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)

## 10. Worked Example

A hash join builds on relation $R$ ($16$ GB) and probes with $S$. Run on a 2-socket NUMA box: socket-local memory bandwidth $\approx 60$ GB/s, cross-socket $\approx 20$ GB/s.

Plan A — DOP 16, all threads on socket 0, hash table on socket 0: every probe is NUMA-local, but 16 threads share one socket's $60$ GB/s, so per-thread bandwidth is $\approx 3.75$ GB/s.

Plan B — DOP 32, 16 threads per socket, hash table partitioned NUMA-locally (morsel-driven): each socket serves its own partition at $60$ GB/s; aggregate $\approx 120$ GB/s, roughly $2\times$ Plan A.

Plan C — DOP 32 but table all on socket 0: socket-1 threads pay cross-socket cost; their $16$ probes contend on the $20$ GB/s link ($\approx 1.25$ GB/s each), dragging the slowest thread and the makespan below Plan A.

This shows non-separability: doubling DOP helps (B) or hurts (C) entirely depending on placement, so cost is not additive per operator — the core modeling barrier in Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
