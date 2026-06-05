# Distributed Window-Function Evaluation

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/distributed-window-functions` · **Status:** open

## 1. Problem Statement

SQL window functions (`OVER (PARTITION BY g ORDER BY o [frame])`) compute, for each row, an aggregate over an ordered group ("window partition"). Distributing them requires (1) repartitioning by `PARTITION BY` key so each group is co-located, (2) globally sorting within each group by `ORDER BY`, and (3) a sequential scan applying the frame (ROWS/RANGE/GROUPS, possibly unbounded). The problem: choose the partitioning and ordering plan that minimizes repartitioning/communication and balances per-worker load, especially when (a) a few window-partition keys are heavy (skew), (b) consecutive window clauses have *different* PARTITION/ORDER keys (forcing re-shuffles), and (c) frames are running/unbounded (creating sequential dependencies across workers).

- **Optimization variant:** minimize total bytes shuffled + max worker load for a sequence of window clauses.
- **Decision variant:** can a given window query be evaluated in $r$ shuffles with load $\le L$?
- **Counting/holistic sub-case:** rank/ntile/percentile and `RANGE`-frame holistic aggregates that are non-decomposable.

The endpoints (single window, hash-friendly key) are well solved; multi-window clause ordering and skewed/holistic frames are open.

## 2. Mathematical Foundations

Treat each window clause as requiring a partition function $h_g$ and a total order $\le_o$ within groups. A *single* window clause is a **group-by-then-sort** operation: communication-optimal sorting in MPC needs $\Theta(\log_L N)$ rounds with load $L$ (Goodrich's BSP/MPC sorting bound), and grouping costs one shuffle. For a *sequence* of $k$ clauses with key sets $K_1,\dots,K_k$, the minimal number of shuffles is governed by how many consecutive clauses can *share* a partitioning — an instance of finding a maximum chain of compatible (functionally-dependent or prefix-compatible) keys, related to **interesting-orders** propagation in the Selinger optimizer. Load under skew is bounded by the heaviest group: if group $g$ has size $N_g$, a holistic frame forces $\Omega(N_g)$ on one worker unless the frame is *decomposable* (e.g., running SUM via prefix sums, computable by a parallel scan / segmented prefix-sum in $O(\log p)$ depth). Decomposability is the key algebraic property:

$$ \text{frame agg } F \text{ is parallelizable} \iff F \text{ admits an associative combine } \oplus \text{ with } O(1)\text{-size partial state.} $$

RANK/percentile (holistic) admit no $O(1)$ partial state, forcing different treatment.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Spark, Presto/Trino, Snowflake, DuckDB, and Apache Flink implement *segment-tree* / *running-aggregate* window operators; Spark's window exec shuffles once per distinct partition spec and sorts; Trino pushes partial pre-aggregation. Microsoft SQL Server's batch-mode window aggregate and Umbra/HyPer's morsel-driven window operator are state of the art for single-node parallelism.
- **Theory-SOTA:** MPC sorting/grouping bounds (Goodrich; Beame–Koutris–Suciu) supply the per-clause optimum; *interesting orders* and shared-shuffle reuse (Neumann–Moerkotte) supply clause-sequence optimization, but joint skew+ordering optimality is unproven.

## 4. Upper Bound

A single window clause with a *decomposable* frame: $O(\log_L N)$ rounds, load $\tilde O(N/p)$ for skew-free input, via MPC sort + segmented prefix-sum — in the **MPC model**. For $k$ clauses, greedily reusing compatible partitionings gives at most $k$ shuffles; with interesting-order matching the number drops to the size of a minimum compatible-key cover. Holistic frames over a heavy group $g$ cost $\tilde O(N_g)$ on its owner unless the frame is range-decomposable.

## 5. Lower Bound

Sorting within groups inherits the **MPC sorting lower bound** $\Omega(\log_L N)$ rounds (Goodrich), so no constant-round, low-load algorithm exists for general `ORDER BY` frames. For holistic per-row aggregates (e.g., exact percentile in a RANGE frame) over a single dominant group, a **communication-complexity** argument shows $\Omega(N_g)$ data must funnel through the group's owner, an information-theoretic load lower bound. Multi-clause shuffle minimization (choosing an order of window specs minimizing re-partitions) is **NP-hard** by reduction from minimum-key-cover / shortest common supersequence style arguments.

## 6. The Gap

Single decomposable windows are essentially tight (sorting bound matched). The open gaps: (1) no algorithm provably minimizes shuffles for an arbitrary *sequence* of window clauses with distinct keys — only heuristics; (2) skewed holistic frames lack a load-balanced distributed algorithm better than funneling the heavy group; (3) no tight round/load characterization for `RANGE`/`GROUPS` frames with peer-spanning boundaries. Closing requires a frame-decomposition theory plus an approximation algorithm (or hardness proof) for clause-order shuffle minimization.

## 7. Current Research (as of June 2026)

Morsel-driven and vectorized window operators (Neumann's Umbra group, TU Munich); skew-aware window partitioning in Spark/Photon (Databricks) *(frontier — verify)*; incremental/streaming window evaluation over unbounded frames (Flink, RisingWave) sharing techniques with continuous queries; and theoretical work on parallel prefix decompositions for richer frame functions. Holistic-aggregate-in-MPC results (Yi, Tao) feed directly into RANK/percentile windows.

## 8. Future Work

- Optimal (or approximation-guaranteed) ordering of multi-window-clause shuffles.
- Load-balanced distributed exact percentile/RANK over skewed groups.
- A decomposition calculus classifying which frame functions parallelize at $O(\log p)$ depth.
- Incremental maintenance of distributed window results under updates.

## 9. Key References

- **[Foundational]** M. T. Goodrich. *Communication-Efficient Parallel Sorting.* SIAM J. Computing, 1999 (BSP/MPC sorting bounds).
- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD 1979 (interesting orders).
- **[SOTA]** V. Leis et al. *Morsel-Driven Parallelism.* SIGMOD 2014 (parallel window/operator execution).
- **[SOTA]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* JACM 2017 (grouping/sorting in MPC).
- **[Survey]** G. Moerkotte. *Building Query Compilers* (draft monograph), chapters on window functions and interesting orders.

---
*Part of the [DBMS Research catalog](../../README.md).*
