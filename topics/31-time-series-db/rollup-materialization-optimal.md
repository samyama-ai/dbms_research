# Optimal rollup hierarchy materialization

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/rollup-materialization-optimal` · **Status:** open

## 1. Problem Statement

Time-series systems pre-aggregate ("roll up" / "downsample") raw data into coarser resolutions (1s → 1m → 1h → 1d → …) to accelerate queries over long ranges. Materializing every resolution costs storage and continuous-aggregate maintenance; materializing none forces expensive raw scans. The problem: **given a query workload and retention/cost constraints, choose which resolutions (and which aggregate functions) to precompute** to minimize total cost.

Variants:
- **Optimization (cost):** minimize (query cost + maintenance cost + storage) over the choice of materialized set $S \subseteq$ candidate resolutions.
- **Decision:** under storage budget $B$, does a materialization achieving query cost $\le T$ exist?
- **Online/adaptive:** workload shifts over time; choose/evict rollups online.

This is the **time-series specialization of view/cuboid selection** in OLAP, with the lattice being the resolution hierarchy and answerability rules set by aggregate decomposability.

## 2. Mathematical Foundations

Model resolutions as a lattice/DAG $L$: a query at resolution $r$ can be answered from any materialized finer resolution $r' \preceq r$ whose aggregate **decomposes** into $r$ (e.g., SUM, COUNT, MIN, MAX are decomposable; AVG via SUM+COUNT; quantiles/DISTINCT are *not* exactly, needing mergeable sketches).

Let cost$(q, S)$ be the cost of answering query $q$ from the best ancestor in $S$. Total benefit of materializing a node is the query cost it saves minus its maintenance/storage. This is exactly **Harinarayan–Rajaraman–Ullman (HRU) view selection in the data cube** specialized to a chain/lattice:

$$\max_{|S|\le k} \; \text{Benefit}(S), \quad \text{Benefit monotone + submodular.}$$

The benefit function is **monotone submodular**, so the greedy algorithm gives a $(1 - 1/e)$ approximation (HRU's classic result). For a **total-order chain** of resolutions, the problem is even easier and admits exact DP. With **maintenance cost** and **continuous aggregates** (incremental refresh), the objective gains an update term, and the choice becomes a knapsack-flavored submodular optimization.

Decomposability is the algebraic side: an aggregate is materializable across the lattice iff it is an **algebraic/distributive** function (Gray et al. data-cube taxonomy); **holistic** aggregates (exact median, COUNT DISTINCT) require sketches with bounded merge error, linking to the lossy-guarantee problem.

## 3. State of the Art (SOTA)

- **Foundational:** **Harinarayan, Rajaraman, Ullman**, *Implementing Data Cubes Efficiently* (SIGMOD 1996) — greedy view selection, $(1-1/e)$ guarantee; **Gray et al.**, *Data Cube* (1997) aggregate taxonomy.
- **Systems-SOTA:** **TimescaleDB continuous aggregates** (hierarchical, incrementally maintained); **InfluxDB** downsampling tasks / retention policies; **Druid** rollup at ingest + segment granularities; **Prometheus/Thanos/Cortex** recording rules and downsampling; **Apache Pinot** star-tree index (a materialization lattice with budget). Selection of *which* rollups is mostly manual / rule-of-thumb, not optimized — hence "open" as a principled, automated, guaranteed problem.

## 4. Upper Bound

- **Greedy submodular** selection gives $(1-1/e)\approx 0.63$ of optimal benefit under a cardinality budget (HRU); under a knapsack (storage-byte) budget, the cost-benefit greedy / continuous-greedy gives $(1-1/e)$ as well.
- For a **chain lattice** (pure resolution hierarchy, no branching), **exact DP** in polynomial time selects the optimal subset under a budget, by interval/segment optimization over the chain.
- Online/workload-shifting variants admit **competitive caching**-style bounds (treat rollups as a weighted cache).

## 5. Lower Bound

- The general **view/cuboid selection** problem (arbitrary lattice, budget) is **NP-hard** (reduction from set cover / knapsack), and inapproximable beyond $(1-1/e)$ for the cardinality-budget benefit-maximization (matching the submodular-maximization hardness of Feige). So greedy is **optimal among poly-time algorithms** for the general lattice.
- For the special **chain** structure the hardness vanishes (DP-exact), so the lower bound is structure-dependent.
- With maintenance + dynamic workload, online lower bounds inherit from weighted caching/$k$-server.

## 6. The Gap

Genuinely open as an *automated, guaranteed, time-series-specific* problem, despite the OLAP theory being mature. Gaps: (1) integrating **continuous-aggregate maintenance cost** and **retention/TTL** into the objective with tight bounds; (2) **holistic aggregates** (quantiles, distinct) via mergeable sketches that change the answerability lattice and inject approximation error — coupling rollup choice to error budgets; (3) **adaptive online** rollup selection under drifting workloads with competitive guarantees. No deployed TSDB picks rollups with a stated approximation/competitive ratio.

## 7. Current Research (as of June 2026)

- Workload-driven automatic rollup/continuous-aggregate recommendation in TSDBs (Timescale, Druid star-tree auto-tuning) *(frontier — verify)*.
- Sketch-backed approximate rollups (mergeable quantile/distinct) integrated with resolution lattices.
- Learned/online materialization under drift, reusing competitive-caching theory.
- Cross-pollination with cloud "materialized view advisor" work (Snowflake/BigQuery) applied to temporal lattices.

## 8. Future Work

- Unified objective coupling query, maintenance, storage, and retention with tight approximation.
- Rollup lattices for holistic aggregates with end-to-end error budgets.
- Online adaptive rollup selection with provable competitive ratios.
- Joint optimization of rollup choice and compression/encoding per resolution.

## 9. Key References

- **[Foundational]** V. Harinarayan, A. Rajaraman, J. Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996.
- **[Foundational]** J. Gray, S. Chaudhuri, A. Bosworth, et al. *Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals.* Data Mining and Knowledge Discovery, 1997.
- **[Foundational]** G. Nemhauser, L. Wolsey, M. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978.
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* Journal of the ACM, 1998.
- **[SOTA]** F. Yang, E. Tschetter, X. Léauté, et al. *Druid: A Real-time Analytical Data Store.* SIGMOD, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
