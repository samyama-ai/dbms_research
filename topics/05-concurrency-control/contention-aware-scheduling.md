# Contention-Aware Scheduling Optimality

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/contention-aware-scheduling` · **Status:** open

## 1. Problem Statement

Under high contention, the order in which a scheduler admits and serializes transactions strongly affects lock-wait time, abort rate, and throughput. The **contention-aware scheduling** problem: given a batch (or stream) of transactions with (possibly estimated) read/write footprints, choose an execution order / partition / priority assignment that **minimizes a contention objective** — total abort count, makespan under lock conflicts, or expected lock-wait — subject to producing a serializable schedule.

- **Optimization variant:** minimize aborts/makespan over all serial-equivalent orders.
- **Decision variant:** is there a schedule with abort cost $\le k$?
- **Counting variant:** number of conflict-free orderings (relevant to randomized admission).
- **Online variant:** stream arrivals, commit ordering decisions irrevocably, compete against the offline optimum.

The open question is whether optimal (or constant-factor) contention-aware scheduling is tractable, and where the hardness frontier sits.

## 2. Mathematical Foundations

Model transactions as nodes in a **conflict graph** $G=(V,E)$ where $\{T_i,T_j\}\in E$ if their footprints intersect on a conflicting operation; an edge weight $w_{ij}$ estimates conflict cost. Running conflicting transactions concurrently risks aborts/waits, so a low-contention schedule seeks to *temporally separate* heavy-conflict pairs — closely related to **graph coloring** (each color = a concurrent wave with no internal conflict) and to **scheduling with conflicts / makespan minimization**:

$$\min_{\text{partition } V_1,\dots,V_m} \sum_t \text{cost}(V_t) \quad \text{s.t. each } V_t \text{ is (near) conflict-free}.$$

Batch grouping to maximize intra-batch independence is a **maximum independent set / minimum coloring** problem; minimizing weighted conflict while respecting a serial-equivalence order maps to constrained graph partitioning. Abort-rate prediction additionally needs a stochastic model of footprint overlap (e.g., balls-in-bins / occupancy on hot keys).

## 3. State of the Art (SOTA)

**Systems-SOTA:** **Quro** (Yan & Cheung, VLDB 2016) reorders operations within transactions to shorten contended lock-hold windows. **IC3 / Runtime Pipelining** (Wang et al., SIGMOD 2016) decomposes and pipelines transactions by static conflict analysis. **Bamboo** (Guo, Yu, et al., SIGMOD 2021) enables early lock release on hot keys. Contention-aware *partitioning/batching* appears in **Aria** (deterministic reordering), **Strife** (Prasaad, Cheung, Suciu, SIGMOD 2020) which clusters a batch into conflict-free groups then serially handles residue, and learned admission controllers (Polyjuice, OSDI 2021) that tune CC policy by contention. **Theory-SOTA:** the scheduling problem maps onto classical NP-hard combinatorial problems (coloring, scheduling-with-conflicts), but a *database-specific* optimality theory is underdeveloped.

## 4. Upper Bound

Strife computes conflict-free batches via connected-component / clustering heuristics in near-linear time per batch, with empirical large abort reductions but no approximation guarantee. Coloring-based grouping inherits the $O(\log n)$- and $\Delta+1$-type approximations for chromatic objectives. Greedy conflict-minimizing admission gives an online competitive ratio only under restrictive footprint assumptions. No polynomial algorithm with a constant-factor guarantee on *abort rate* across general workloads is known.

## 5. Lower Bound

The offline optimization is **NP-hard**: minimum conflict-free partitioning generalizes **graph coloring** (NP-hard, and inapproximable within $n^{1-\epsilon}$ unless P=NP), and contention-minimizing scheduling generalizes **scheduling with conflicts** and **min-makespan on conflict graphs**, both NP-hard. The online variant inherits competitive lower bounds from list-scheduling and online coloring (online coloring has no constant competitive ratio). These hardness results hold even with exact footprints; with *estimated* footprints, additional uncertainty lower bounds apply. No fine-grained (SETH) sharpening is established.

## 6. The Gap

**Open.** We have NP-hardness/inapproximability (lower) and effective heuristics with no guarantees (upper), but **no matching approximation theory** for the contention objectives databases actually care about (abort rate, weighted lock-wait, throughput). Closing it requires: a clean problem definition tying the combinatorial objective to realized abort rate, approximation algorithms (or APX-hardness) for that objective, and online algorithms with provable competitive ratios under realistic arrival/footprint models.

## 7. Current Research (as of June 2026)

Active directions: **learned and adaptive CC** (Polyjuice, CormCC-style hybrids) that select policies per-contention-regime; batch clustering (Strife successors) for serializable cloud OLTP; and contention-aware scheduling for deterministic and disaggregated engines *(frontier — verify)*. Theory groups are beginning to connect transaction scheduling to approximation results for scheduling-with-conflicts and to online matching/coloring. Hot-key and skew modeling (Zipfian workloads) is an active empirical thread.

## 8. Future Work

- A canonical objective linking the combinatorial schedule to predicted abort rate, plus approximation/APX-hardness results.
- Online contention-aware admission with provable competitive ratios under stochastic arrivals.
- Robust scheduling under *estimated/learned* footprints with uncertainty guarantees.
- Integration with deterministic and multi-version engines as a unified optimization.

## 9. Key References

- **[SOTA]** Prasaad, G.; Cheung, A.; Suciu, D. *Handling Highly Contended OLTP Workloads Using Fast Dynamic Partitioning (Strife).* SIGMOD, 2020.
- **[SOTA]** Yan, C.; Cheung, A. *Leveraging Lock Contention to Improve OLTP Application Performance (Quro).* PVLDB, 2016.
- **[SOTA]** Wang, Z.; Mu, S.; Cui, Y.; Yi, H.; Chen, H.; Li, J. *Scaling Multicore Databases via Constrained Parallel Execution (IC3).* SIGMOD, 2016.
- **[SOTA]** Wang, J.; Ding, D.; Wang, H.; Christensen, C.; Wang, Z.; Chen, H.; Li, J. *Polyjuice: High-Performance Transactions via Learned Concurrency Control.* OSDI, 2021.
- **[Foundational]** Garey, M. R.; Johnson, D. S. *Computers and Intractability: A Guide to the Theory of NP-Completeness.* W. H. Freeman, 1979.

---
*Part of the [DBMS Research catalog](../../README.md).*
