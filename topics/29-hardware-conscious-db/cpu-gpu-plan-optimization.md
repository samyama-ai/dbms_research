# Heterogeneous CPU-GPU query plan optimization

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/cpu-gpu-plan-optimization` · **Status:** empirically-open

## 1. Problem Statement
Given a query plan (a DAG of relational operators) and a heterogeneous machine with CPU cores and one or more GPUs connected by an interconnect of bandwidth $\beta$, decide **for each operator (and pipeline segment) whether it runs on CPU or GPU**, plus the join order and physical algorithm, so as to minimize end-to-end latency (or maximize throughput) subject to GPU memory $M$, transfer costs, and concurrency limits.

Variants: (a) **decision** — is there a placement with makespan $\le T$? (b) **optimization** — minimum-makespan placement+ordering; (c) **counting/enumeration** is rarely the goal but the search space is what makes optimization hard. The operator-placement subproblem alone, with data-transfer edges, generalizes classic NP-hard scheduling.

## 2. Mathematical Foundations
Placement on a plan DAG with transfer costs on cross-device edges is exactly **task graph scheduling on unrelated/heterogeneous processors with communication delays** — $R\,|\,prec, c_{ij}\,|\,C_{\max}$ in scheduling notation — which is **strongly NP-hard** and inapproximable beyond known factors. Adding join-order selection multiplies this by the System-R join-ordering search space (Cayley-number-many bushy trees). Formally a plan is $P=(V,E)$, operator $v$ has device-dependent cost $w_v^{\mathrm{cpu}}, w_v^{\mathrm{gpu}}$, each cross-device edge $(u,v)$ carries transfer $\frac{\mathrm{data}(u)}{\beta}$; minimize the longest weighted path under the GPU-memory knapsack constraint $\sum_{v\in\mathrm{GPU},\text{coresident}} \mathrm{mem}(v)\le M$. Cost-model accuracy rests on cardinality estimation, whose worst-case error is itself unbounded (AGM gives only an upper envelope).

## 3. State of the Art (SOTA)
**Systems-SOTA:** HeavyDB/OmniSci, MapD, Crystal, and Microsoft's TQP (Tensor Query Processor, VLDB 2022) place whole pipelines; HetExchange (Chrysogelos et al., VLDB 2019, EPFL) introduced router/split operators letting one plan span CPU+GPU with cost-based placement — the canonical academic system. Funke et al. (CIDR/SIGMOD, TUM) studied pipelined heterogeneous execution. He et al.'s earlier "Relational Joins on Graphics Processors" (SIGMOD 2008) seeded GPU operator costing. Most production optimizers still use **rule + greedy cost heuristics**, not provably good placement.

## 4. Upper Bound
No constant-factor approximation is deployed; the practical upper bound is **cost-based dynamic programming over join order (System-R / DPccp) with a per-operator device-cost annotation**, plus list-scheduling for placement. List scheduling (HEFT-style) gives the classic $2-\frac1m$ makespan guarantee only in restricted (related-machine, no-communication) cases; with communication delays and unrelated speeds no better-than-logarithmic general approximation is known to be implemented.

## 5. Lower Bound
The placement problem is **strongly NP-hard** (reduction from scheduling unrelated machines / multiprocessor scheduling with communication delays); even special cases (two processors, precedence + unit communication) are NP-hard (Hoogeveen–Lenstra–Veltman). Approximation hardness: unrelated-machine makespan has no PTAS and is hard to approximate within $<3/2$ (Lenstra–Shmoys–Tardos lower bound). Join ordering adds the well-known difficulty that optimal bushy ordering is NP-hard for general predicates (Ibaraki–Kameda / Cluet–Moerkotte).

## 6. The Gap
The decision/optimization problem is provably NP-hard, so the "gap" is not closed vs. open in the math sense — it is **empirically open**: we lack (i) cost models whose error is bounded enough that an approximation guarantee would be meaningful, and (ii) practical algorithms with *any* worst-case placement guarantee. Real systems win or lose by cardinality estimation and transfer modeling, not by combinatorial optimality. Closing it requires robust cost models + approximation algorithms that respect them.

## 7. Current Research (as of June 2026)
Directions: **learned/adaptive placement** (RL and cost-model learning à la Bao/Neo carried to heterogeneous targets) *(frontier — verify)*; Grace-Hopper / unified-memory machines that shrink transfer edges and shift the optimal toward more GPU offload *(frontier — verify)*; CXL memory pooling changing the $M$ constraint from hard to soft. Groups: EPFL DIAS (Ailamaki), TUM (Neumann/Leis), MIT DSAIL, Microsoft GSL (TQP), and the Heidelberg/TU Berlin GPU-DB communities.

## 8. Future Work
Approximation algorithms for placement under realistic communication models; integrating robust (worst-case/bounded-error) cardinality estimates with device costing; multi-GPU and disaggregated-memory placement; adaptive re-optimization that migrates pipelines mid-flight as observed cardinalities deviate.

## 9. Key References
- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** J. K. Lenstra, D. B. Shmoys, É. Tardos. *Approximation Algorithms for Scheduling Unrelated Parallel Machines.* Math. Programming, 1990.
- **[SOTA]** P. Chrysogelos, M. Karpathiotakis, R. Appuswamy, A. Ailamaki. *HetExchange: Encapsulating Heterogeneous CPU-GPU Parallelism in JIT Compiled Engines.* VLDB, 2019.
- **[SOTA]** D. Justo, A. Floratou et al. *The Tensor Data Platform / TQP: Querying with Tensor Computation Runtimes.* VLDB/CIDR, 2022–2023.
- **[Survey]** S. Breß, H. Funke, J. Teubner. *Robust Query Processing in Co-Processor-accelerated Databases.* SIGMOD, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
