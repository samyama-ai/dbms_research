# Spatial data partitioning for skew

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatial-partitioning-skew` · **Status:** empirically-open

## 1. Problem Statement
Given a set $S$ of $n$ spatial objects (points or extended objects with bounding boxes) in $\mathbb{R}^d$, partition the space into $p$ cells and assign objects to cells so as to **simultaneously minimize**:

1. **Load imbalance** — the maximum partition size $\max_i |P_i|$ (or its variance), which governs straggler-bound query/join runtime; and
2. **Boundary replication / duplication** — extended objects (or the replicate side of a join) that straddle cell boundaries and must be copied into multiple cells, plus the duplicate results they generate.

These objectives **conflict**: finer cuts in dense regions reduce imbalance but increase boundary crossings; coarser cuts reduce replication but worsen imbalance under skew. The data is **heavily skewed** (urban GPS, points-of-interest), so uniform grids are pathological.

Variants: (a) *decision* — does a partition with imbalance $\le L$ and replication $\le R$ exist? (b) *optimization* — minimize $\alpha\cdot\text{imbalance} + \beta\cdot\text{replication}$; (c) *streaming/online* — build the partition in one pass under bounded memory.

## 2. Mathematical Foundations
Model a partition as disjoint cells $\{C_i\}$ covering the domain. The **load** of $C_i$ is $|S\cap C_i|$; for extended objects with footprints $f(o)$, an object replicates into every cell its footprint intersects, so total work is $\sum_i |\{o: f(o)\cap C_i\neq\emptyset\}|$ and **replication** $=\sum_o(|\{i:f(o)\cap C_i\neq\emptyset\}|-1)$.

Balanced point partitioning relates to **$k$-d / median-split** geometry and **discrepancy theory**: a partition into $r$ equal-count cells with small boundary measure is a low-**stabbing-number** decomposition. **Matoušek's partition theorem** guarantees $r$ cells each holding $\le n/r$ points with any halfplane crossing $O(\sqrt r)$ cells, and $O(\sqrt r)$ is optimal for halfspaces. Boundary replication for line/rectangle queries is then bounded by the arrangement's **stabbing number**. Balancing under skew with capacity constraints is akin to **capacitated facility location / minimum bisection** and is generally **NP-hard**.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** SpatialHadoop (Eldawy–Mokbel, ICDE 2015) and **GeoSpark/Apache Sedona** offer Grid, Quadtree, KDB, STR-R-tree, Hilbert-curve, and sampling-based partitioners; Simba, LocationSpark, and Beast extend these. Partitioner selection is largely heuristic/cost-based.
- **Sampling-based bulk partitioning:** STR (Sort-Tile-Recursive) packing and Hilbert sort over a sample to derive balanced boundaries — the de-facto Sedona default.
- **Theory-SOTA:** Matoušek partition trees and the BBD-tree (Arya–Mount) give provable balance/crossing trade-offs but are not what big-data systems ship.

## 4. Upper Bound
For $n$ points in $\mathbb{R}^2$, a partition into $p$ cells with **perfect count balance** $\lceil n/p\rceil$ and crossing number $O(\sqrt p)$ per line is achievable in $O(n\log n)$ (simplicial/partition trees; RAM model). For axis-parallel range workloads, STR/Hilbert partitioning empirically yields near-balanced loads with $O(\sqrt p)$ replication per straddling query, but **no system delivers a proven joint $(\alpha,\beta)$-approximation** for the combined objective.

## 5. Lower Bound
The joint balanced-partition-with-minimum-replication problem is **NP-hard** by reduction from minimum bisection / balanced hypergraph partitioning (hard to approximate within any constant under standard assumptions). Geometrically, any partition achieving load imbalance below threshold on adversarial skew forces $\Omega(\sqrt p)$ crossings per line — a **discrepancy / stabbing-number** lower bound matching the upper bound asymptotically. The number of duplicate results is lower-bounded by the arrangement's boundary measure (information-theoretic on the output).

## 6. The Gap
Asymptotically, balance vs. crossing is **tight ($\Theta(\sqrt p)$)** for point data and line crossings. The genuine gap is **empirical and multi-objective**: (i) for *extended* objects (polygons) no partitioner provably co-optimizes imbalance and replication; (ii) the right Pareto operating point is workload- and skew-dependent and chosen by heuristics; (iii) one-pass/streaming construction with guarantees is open. Hence *empirically-open*: idealized point/line bounds exist, but the deployed multi-objective skew problem lacks both a sharp characterization and a robust auto-tuner.

## 7. Current Research (as of June 2026)
- **Learned / cost-model-driven partitioners** predicting the imbalance–replication trade-off from a sample to minimize end-to-end join cost *(frontier — verify)*.
- Adaptive re-partitioning for evolving/streaming workloads; partitioning co-designed with the join operator.
- Groups/people: Ahmed Eldawy & Mohamed Mokbel (SpatialHadoop/Beast), Jia Yu & Mohamed Sarwat (Sedona), the Simba/LocationSpark lines.

## 8. Future Work
Provable bi-criteria approximation for polygon partitioning; streaming one-pass balanced partitioners with replication guarantees; partitioners co-optimized with multi-way join order; theory linking stabbing number to end-to-end distributed-join cost.

## 9. Key References
- **[Foundational]** Matoušek. *Efficient Partition Trees.* Discrete & Computational Geometry, 1992.
- **[Foundational]** Leutenegger, Lopez, Edgington. *STR: A Simple and Efficient Algorithm for R-Tree Packing.* ICDE, 1997.
- **[SOTA]** Eldawy, Mokbel. *SpatialHadoop: A MapReduce Framework for Spatial Data.* ICDE, 2015.
- **[SOTA]** Yu, Zhang, Sarwat. *Spatial Data Management in Apache Spark: The GeoSpark Perspective.* GeoInformatica, 2019.
- **[Survey]** Pandey, Kipf, Neumann, Kemper. *How Good Are Modern Spatial Analytics Systems?* PVLDB, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
