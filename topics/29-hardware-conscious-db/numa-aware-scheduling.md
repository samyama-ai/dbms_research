# NUMA-aware operator scheduling

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/numa-aware-scheduling` · **Status:** empirically-open

## 1. Problem Statement

Modern analytical servers are non-uniform memory access (NUMA) machines: a multi-socket box exposes several memory controllers, and a core's latency/bandwidth to a memory page depends on whether the page is *local* (same socket) or *remote* (cross-socket interconnect, e.g. UPI/Infinity Fabric). The problem is to place base data and intermediate state, and to schedule operator threads, so that the analytical pipeline (scans, joins, aggregations, sorts) minimizes remote traffic while keeping all sockets load-balanced.

Variants:
- **Optimization (placement):** given a query plan, a data partitioning, and a NUMA topology, choose thread-to-core and data-to-node assignments minimizing total weighted remote bytes (or makespan).
- **Online/decision (migration):** during execution, decide whether to migrate a thread or a memory page given observed access patterns, subject to migration cost; decide if a target latency is achievable.
- **Counting/analysis:** estimate remote access volume of a plan for the optimizer's cost model.

The hard core is that placement and scheduling interact: co-locating a build-side hash table with its probing threads reduces remote reads but may overload one socket's bandwidth.

## 2. Mathematical Foundations

Model the machine as a complete graph $G=(N,E)$ over NUMA nodes with latency/bandwidth weights $c_{ij}$ (cost per byte from node $i$ to $j$, $c_{ii}<c_{ij}$). An operator instance $o$ has thread demand and an access vector $a_o(\cdot)$ over data fragments. Let $x_{o,n}\in\{0,1\}$ assign operator $o$ to node $n$ and $y_{f,n}$ place fragment $f$. Minimize

$$\sum_{o,f} a_o(f)\sum_{n,m} x_{o,n}\,y_{f,m}\,c_{nm}\quad\text{s.t. node capacity }\sum_o x_{o,n}\,d_o \le C_n.$$

This is a **quadratic assignment / generalized assignment** formulation; QAP is NP-hard and hard to approximate. The migration sub-problem is an instance of online **metrical task systems** / $k$-server-style page placement, where competitive ratio bounds apply. Bandwidth contention makes the cost function *non-linear* (load-dependent), connecting to congestion games and the price of anarchy.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** HyPer / Umbra's *morsel-driven parallelism* (Leis et al., SIGMOD 2014) is the dominant practical scheduler: work is broken into cache-sized morsels dispatched by a NUMA-aware dispatcher that prefers local morsels and steals remotely only when idle. SAP HANA, Oracle, and DB2 BLU adopt similar socket-local partitioning. ERIS (Kissinger et al.) explored data-oriented NUMA placement.
- Albutiu et al.'s *MPSM* (massively parallel sort-merge join, VLDB 2012) and Balkesen et al.'s radix/hardware-conscious joins (ICDE/VLDB 2013) gave NUMA-aware join blueprints.
- **Theory-SOTA.** No tight approximation for the joint placement problem; practice relies on heuristics (greedy local-first + work stealing) with strong empirical results but no guarantees.

## 4. Upper Bound

For the static placement QAP, only general QAP approximations apply (e.g. $O(\log n)$-type results for special metrics; no constant factor in general). Morsel-driven scheduling gives, empirically, near-linear speedup to dozens of cores; theoretically, randomized work stealing has the classic Blumofe–Leiserson bound: expected time $T_1/P + O(T_\infty)$ on $P$ workers, but this ignores NUMA cost asymmetry. For online page migration, deterministic algorithms achieve competitive ratio $3$ (Black–Sleator-style) for migrating a single page between two nodes; randomized do better.

## 5. Lower Bound

Joint operator/data placement is NP-hard via reduction from QAP and from minimum-makespan scheduling on unrelated machines (no PTAS unless P=NP for the latter's $3/2$ barrier; Lenstra–Shmoys–Tardos give a $2$-approximation as the best known general result). Online migration has a competitive-ratio lower bound of $3$ for deterministic single-page migration (matching the upper bound) and $\Omega(\log)$ behaviors for general task-system formulations. Bandwidth contention pushes the problem into congestion-game territory where computing optimal load-balanced placement is also NP-hard.

## 6. The Gap

The *theory* gap (no constant-factor approximation for joint NUMA placement) coexists with a *practical* gap: morsel-driven scheduling works extremely well empirically but has no worst-case NUMA-cost guarantee, and its behavior under bandwidth saturation, skew, and heterogeneous interconnects (4+ sockets, CXL-attached memory) is not characterized. The status is **empirically-open**: we have battle-tested heuristics that win benchmarks, but no model that predicts when they fail or a scheduler provably within a factor of optimal remote traffic. Closing it needs either a contention-aware cost model with approximation guarantees, or a lower bound showing heuristics are near-optimal in realistic regimes.

## 7. Current Research (as of June 2026)

- Scheduling for **CXL-attached and tiered memory**, where "remote" is no longer just another socket but a pooled/disaggregated tier with its own latency class *(frontier — verify)*. Groups at TUM (Neumann/Leis, Umbra), CWI (DuckDB lineage), and ETH Zürich (Alonso) are active.
- Learned / cost-model-driven NUMA placement integrated into the optimizer, and reinforcement-learning thread placement *(frontier — verify)*.
- Bandwidth-aware morsel sizing and adaptive stealing thresholds under skew.

## 8. Future Work

- A contention-aware approximation algorithm with provable bounds on remote-byte cost.
- Unified scheduling across NUMA + CXL + GPU memory tiers.
- Robustness to topology heterogeneity (asymmetric interconnects, sub-NUMA clustering).
- Online algorithms that bound migration cost against an adaptive adversary representing query phase changes.

## 9. Key References

- **[Foundational]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD, 2014.
- **[SOTA]** Albutiu, Kemper, Neumann. *Massively Parallel Sort-Merge Joins in Main Memory Multi-Core Database Systems.* VLDB, 2012.
- **[SOTA]** Balkesen, Teubner, Alonso, Özsu. *Main-Memory Hash Joins on Multi-Core CPUs: Tuning to the Underlying Hardware.* ICDE, 2013.
- **[Foundational]** Blumofe, Leiserson. *Scheduling Multithreaded Computations by Work Stealing.* JACM, 1999.
- **[Foundational]** Lenstra, Shmoys, Tardos. *Approximation Algorithms for Scheduling Unrelated Parallel Machines.* Math. Programming, 1990.
- **[Survey]** Psaroudakis et al. *Scaling Up Concurrent Main-Memory Column-Store Scans: Towards Adaptive NUMA-aware Data and Task Placement.* VLDB, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
