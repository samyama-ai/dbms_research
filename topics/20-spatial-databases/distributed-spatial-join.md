# Scalable distributed spatial join

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/distributed-spatial-join` · **Status:** empirically-open

## 1. Problem Statement
Given two large spatial datasets $R$, $S$ partitioned across $p$ machines, compute the spatial join $R\bowtie_{\cap} S$ (all intersecting object pairs) minimizing **wall-clock makespan** under three coupled constraints:
1. **No replication blowup:** an object straddling partition boundaries must be sent to multiple workers; total communication should stay $O((|R|+|S|+k)/\text{const})$ rather than blowing up with boundary objects on skewed data.
2. **No stragglers / load balance:** every worker should receive $\approx (\text{work})/p$ of the *true* cost, where cost is dominated by candidate pairs, not raw input — hard because spatial density (and thus pairwise work) is extremely skewed (cities vs. oceans).
3. **Correctness:** each true pair reported **exactly once** (duplicate avoidance for objects replicated to overlapping cells).

This is an **optimization** problem (minimize makespan / communication) layered on the reporting join; the decision core is the centralized output-sensitive join.

## 2. Mathematical Foundations
The standard frame is the **Massively Parallel Computation (MPC)** model: $p$ machines, each with memory $M$, rounds of local computation + all-to-all shuffle; cost measured in **rounds** and **load** (max bits per machine per round). For relational joins, the **AGM bound** and the **Hypercube / Shares** algorithm (Beame–Koutris–Suciu, PODS 2014) give load $L = O(\mathrm{IN}/p^{1/\rho^*})$ where $\rho^*$ is the fractional edge cover number; a binary spatial join is a 2-relation join with $\rho^*=1$, so the relational ideal is $L=O(\mathrm{IN}/p)$ — but **skew** breaks this because spatial proximity is not a uniform hash.

Spatial partitioning uses space-decomposition structures — **uniform grid**, **quadtree**, **k-d tree**, **STR (Sort-Tile-Recursive)** packing, and **R-tree**-derived global partitioners — to assign objects to cells. An object intersecting $t$ cells is replicated $t$ times; the **replication factor** $\sum_r t_r / |R|$ is the key quantity to bound. Load balancing reduces to a **partition-cost estimation** problem: estimate per-cell pairwise cost $\approx |R_c|\cdot|S_c|$ and pack cells into $p$ bins (a bin-packing / multiprocessor-scheduling instance, NP-hard, approximated greedily).

Duplicate avoidance uses the **reference-point / tile-anchor** rule: a pair is emitted only by the cell containing a canonical reference point (e.g., top-left of the intersection of the two MBRs), guaranteeing exactly-once without cross-worker communication.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Apache Sedona** (formerly GeoSpark, Yu–Sarwat 2015) and **Beast / Spatial Hadoop** (Eldawy–Mokbel) implement grid/quadtree/STR partitioning with reference-point duplicate avoidance on Spark/Hadoop. **SpatialSpark**, **Simba** (Xie et al. SIGMOD 2016, with cost-based partitioning and indexed local joins), **LocationSpark**, and **STARK** are notable. Cloud-native engines (BigQuery GIS, Snowflake, Databricks H3-based joins) push grid/cell-id joins via SQL.
- **Theory-SOTA:** MPC join algorithms with **skew-resilient** load bounds — Hu–Yi–Koutris worst-case optimal MPC joins, and **output-sensitive MPC** results bounding load by $\mathrm{IN}/p + \mathrm{OUT}/p$. Geometric specializations remain thinner than relational ones.

## 4. Upper Bound
- **MPC (relational view):** $O(1)$ rounds with load $\tilde O(\mathrm{IN}/p + (k/p)^{?})$ for binary joins via Hypercube; skew-handling variants add a round to detect heavy hitters.
- **Practical:** STR/quadtree partitioning achieves replication factor near $1{+}\epsilon$ on real GIS data and near-linear scaling to thousands of cores in Sedona/Beast benchmarks — but **no worst-case guarantee** on makespan under adversarial skew; balance is heuristic (sample-based cost estimation).

## 5. Lower Bound
- **Communication:** any MPC join must incur load $\Omega(\mathrm{IN}/p)$ trivially, and $\Omega(\mathrm{OUT}/p)$ to ship/produce output; for skewed instances a single "heavy" cell forces $\Omega(\sqrt{\mathrm{OUT}})$ on one machine unless that cell is itself parallelized.
- **Scheduling:** optimal load balancing of pre-estimated cell costs is **NP-hard** (reduces to multiprocessor scheduling / bin packing), with the classic $4/3$ and PTAS approximation landscape.
- No CAP/FLP-style impossibility applies (this is batch, not consensus), but the **replication-vs-balance tension** behaves like an unavoidable tradeoff frontier rather than a single optimum.

## 6. The Gap
The relational MPC theory gives clean load bounds, but **does not capture spatial replication**: real cost is governed by geometric overlap and density skew, not by a uniform hash with bounded fan-out. Systems achieve excellent average-case scaling yet have **no provable makespan guarantee** under adversarial or heavy-tailed spatial skew, and replication factor is bounded only empirically. The gap is therefore between strong empirical performance and the **absence of a worst-case-optimal, skew-and-replication-aware** distributed algorithm — hence *empirically-open*.

## 7. Current Research (as of June 2026)
- **Cost-model-driven repartitioning:** learned/sampled density models to predict per-cell join cost and rebalance (Eldawy's group at UC Riverside; Sarwat/ASU Sedona team).
- **H3 / S2 discrete global grids** as the partition substrate for cloud SQL engines, trading exactness of cells for hash-like uniformity *(frontier — verify the worst-case replication bounds claimed by vendors)*.
- **Output-sensitive MPC** geometric joins importing Hu–Yi–Koutris techniques to the spatial setting.
- **Straggler mitigation** via work-stealing and speculative re-execution specialized to heavy spatial cells.

## 8. Future Work
- A distributed spatial join with **provable** load $\tilde O((\mathrm{IN}+\mathrm{OUT})/p)$ and replication factor $1+o(1)$ under bounded skew assumptions.
- Adaptive, online repartitioning that reacts to discovered skew within a single job.
- Tight lower bounds separating spatial joins from relational ones in MPC.
- Integration with moving-object / streaming data (continuous distributed joins).

## 9. Key References
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication steps for parallel query processing.* PODS, 2013/2014.
- **[SOTA]** J. Yu, J. Wu, M. Sarwat. *GeoSpark: A cluster computing framework for processing large-scale spatial data.* SIGSPATIAL, 2015 (Apache Sedona).
- **[SOTA]** A. Eldawy, M. F. Mokbel. *SpatialHadoop: A MapReduce framework for spatial data.* ICDE, 2015.
- **[SOTA]** D. Xie, F. Li, B. Yao, G. Li, L. Zhou, M. Guo. *Simba: Efficient in-memory spatial analytics.* SIGMOD, 2016.
- **[SOTA]** X. Hu, K. Yi. *Output-optimal massively parallel algorithms for similarity joins.* ACM TODS, 2019.
- **[Survey]** A. Eldawy, M. F. Mokbel. *The era of big spatial data.* PVLDB tutorial / survey, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
