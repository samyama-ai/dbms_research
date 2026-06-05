# Spatiotemporal index for trajectory archives

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatiotemporal-archive-index` · **Status:** empirically-open

## 1. Problem Statement
Given a massive, append-mostly **archive** of historical trajectories — $m$ moving objects, each a time-ordered polyline of $(x,y,t)$ samples, totaling $n$ points ($n$ in the trillions for fleet/AIS/mobile-network data) — design an index that is simultaneously **read-, write-, and space-efficient** for a *mixed* analytical workload over the full history:
- **window / range:** objects (or sub-trajectories) inside a spatiotemporal box $[x_1,x_2]\times[y_1,y_2]\times[t_1,t_2]$;
- **$k$NN / nearest-neighbor-in-time:** who was closest to $p$ at time $t$;
- **trajectory retrieval / similarity:** fetch a whole trajectory or all trajectories similar to a query curve;
- **aggregate / OLAP:** count distinct objects, total dwell, flow between regions over a time span.

Variants: **decision/reporting** (window membership), **counting/aggregation** (distinct-object and flow counts), **optimization** (minimize bytes touched, or jointly minimize space *and* query I/O). The hard core is the *three-way tension*: the layout that minimizes query I/O (heavy spatiotemporal clustering + replication) inflates space and slows ingest, while compact append-friendly logs cripple selective reads.

## 2. Mathematical Foundations
The data is a set of points in $\mathbb{R}^2 \times \mathbb{R}$ (3-D) with the temporal axis monotone per object, so trajectories are *1-D manifolds* embedded in 3-space — not arbitrary point clouds, a structure indexes should exploit. Window queries are **3-D orthogonal range reporting**; the canonical RAM bounds are $O(\log n + K)$ query with $O(n\log n)$ space (range trees) or $O(n)$ space with $\mathrm{polylog}$ slowdown. In the **external-memory $(M,B)$ model**, 3-sided/3-D range reporting costs $\Omega(\log_B n + K/B)$ I/Os, met by R-tree-family and kd-tree-derived structures only heuristically; provably optimal EM 3-D range search needs $O(n(\log n/\log\log_B n))$-type space.

Compression rests on **trajectory entropy**: successive samples are spatially autocorrelated, so delta + SFC (Hilbert/Z-order over $(x,y,t)$) coding approaches the coordinate entropy $H$. The **space–time tradeoff** is governed by indexing-with-compression lower bounds: a *succinct* index must use $H + o(H)$ bits yet still answer range/$k$NN in $\mathrm{polylog}$ — the same wall faced by compressed text indices (FM-index, wavelet trees), here lifted to 3-D geometry. Aggregate queries reduce to **range-counting / distinct-counting**, where exactness needs $\Omega(n)$ space in the worst case but sketches (HyperLogLog, Count-Min) give $(\varepsilon,\delta)$ guarantees in $\mathrm{polylog}$ space. The write side is an **LSM / merge** problem: amortized ingest cost vs. read amplification follows the classic LSM tradeoff curve.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **MobilityDB** (PostgreSQL/PostGIS temporal types, Zimányi et al.) for SQL trajectory analytics; **TrajStore**, **SharkDB**, **UlTraMan**, and **TrajMesa** (HBase/GeoMesa-backed) for archive-scale storage; **GeoMesa / GeoWave** layering SFC (Z/Hilbert) keys over Accumulo/HBase/Cassandra; **Apache IoTDB** and time-series stores for the temporal axis. Cloud columnar stores (BigQuery, Databricks + H3) handle window/flow via cell-id + time partition.
- **Theory-SOTA:** EM range-search structures (the **Arge–Vitter** lineage; **kd-B**, **O-tree**, **PR-tree** with provably optimal worst-case window queries, Arge–de Berg–Haverkort–Yi, SIGMOD 2004) and compressed/succinct geometric indexing. These are rarely combined with archive-scale compression and LSM ingest in one analyzed structure.

## 4. Upper Bound
- **PR-tree (EM):** worst-case-optimal $O((n/B)^{1-1/d} + K/B)$ I/Os for $d$-D window reporting with linear space — the strongest *provable* archive-relevant bound.
- **SFC + LSM (systems):** ingest $O((1/B)\log_{M/B}(n/B))$ amortized I/Os; window queries answered by SFC-range decomposition, with replication of boundary-straddling sub-trajectories; near-linear scaling empirically but *no joint* read/write/space optimality proof.
- **Aggregates:** distinct-object and flow counts in $\mathrm{polylog}$ space with $(\varepsilon,\delta)$ error via HLL/Count-Min over time-bucketed sketches.

## 5. Lower Bound
- **Cell-probe / EM:** $d$-D orthogonal range reporting requires $\Omega(\log_B n + K/B)$ I/Os; for *space-$O(n)$* structures there is a proven query penalty (no linear-space, $O(\log_B n + K/B)$ structure for $d\ge 2$ in the comparison/EM model in general).
- **Succinct barrier:** an index over data of entropy $H$ that also supports fast range search cannot use $o(H)$ bits — compression and queryability fight, mirroring compressed-text-index lower bounds.
- **Distinct counting:** exact distinct-object counting over a window needs $\Omega(n)$ bits (info-theoretic), forcing approximation for the OLAP variant.

## 6. The Gap
Each axis is individually well understood — PR-trees nail worst-case window I/O, FM-index/wavelet trees nail succinct compressed search, LSM nails ingest — but **no single analyzed structure is simultaneously read-, write-, and space-optimal** for the mixed trajectory workload, and none provably exploits the *manifold* (per-object monotone) structure of trajectories to beat generic 3-D point bounds. The problem is empirically open: production systems pick a corner of the tradeoff (e.g. GeoMesa favors ingest+space, PR-tree favors reads) and tune heuristically. Closing it needs a structure with proven simultaneous bounds, or a proven impossibility (a three-way tradeoff lower bound) showing the corners cannot be unified.

## 7. Current Research (as of June 2026)
- **Learned + SFC hybrids:** learned partitioning of the spatiotemporal key space to flatten skew and shrink the index, building on RMI/PGM ideas for trajectory keys *(frontier — verify)*.
- **Compression-native indexing:** querying trajectories directly over compressed/segmented representations (semantic + Douglas–Peucker hierarchies) without full decode, joining the *spatial-join-on-compressed* thread.
- **Tiered / cloud-object-store archives:** indexes designed for S3-style high-latency, immutable storage with aggressive prefetch and sketch-based pre-aggregation.
- Active groups: Zimányi/Sakr (MobilityDB), Eldawy (UC Riverside, big spatial), the GeoMesa/GeoWave community, Jensen/Yang (Aalborg, trajectory data management) *(frontier — verify specific 2025–2026 results)*.

## 8. Future Work
- A trajectory archive index with **provably** simultaneous near-optimal read/write/space bounds, or a matching three-way lower bound.
- Manifold-aware structures exploiting per-object temporal monotonicity to beat generic 3-D range bounds.
- Workload-adaptive layouts that re-tier hot vs. cold history online.
- Privacy-preserving archive indexing (queries over anonymized/aggregated trajectory history).

## 9. Key References
- **[Foundational]** Pfoser, Jensen, Theodoridis. *Novel Approaches to the Indexing of Moving Object Trajectories (TB-tree / STR-tree).* VLDB, 2000. — [DBLP](https://dblp.org/rec/conf/vldb/PfoserJT00.html)
- **[Foundational]** Arge, de Berg, Haverkort, Yi. *The Priority R-tree: A Practically Efficient and Worst-Case Optimal R-tree.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007608)
- **[SOTA]** Zimányi, Sakr, Lesuisse. *MobilityDB: A Mobility Database Based on PostgreSQL and PostGIS.* ACM TODS, 2020. — [DOI](https://doi.org/10.1145/3406534)
- **[SOTA]** Hughes et al. *GeoMesa: A Distributed Architecture for Spatio-Temporal Fusion.* SPIE / GeoMesa, 2015. — [DOI](https://doi.org/10.1117/12.2177233)
- **[SOTA]** Cudre-Mauroux, Wu, Madden. *TrajStore: An Adaptive Storage System for Very Large Trajectory Data Sets.* ICDE, 2010. — [DOI](https://doi.org/10.1109/ICDE.2010.5447829)
- **[Survey]** Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016. — [DOI](https://doi.org/10.1017/CBO9781316588284)

## 10. Worked Example

Encode a trajectory point $(x,y,t)$ with a Z-order (Morton) space-filling-curve key, the layout used by GeoMesa. Quantize each coordinate to 2 bits: a point in cell $(x{=}2, y{=}1, t{=}3)$ has binary $(10, 01, 11)$. Interleaving bits as $z = x_1 t_1 y_1 \dots$ — using order $(t,x,y)$ per level — gives the 1-D key; adjacent points in space-time land in nearby keys, so a window query becomes a few contiguous key ranges.

**Why ranges, not a point.** A window $[t_2,t_3]\times[x_1,x_2]\times[y_1,y_2]$ does *not* map to one contiguous Z-interval — the curve re-enters and leaves the box, producing several disjoint ranges (the "Z-order jump"). For a $2\times2\times2$ window the decomposition typically yields $2$–$4$ ranges.

**The three-way tension (Section 1).** With block size $B$, the PR-tree answers this $d{=}3$ window in $O((n/B)^{2/3}+K/B)$ I/Os worst-case. The SFC+LSM layout instead ingests at $O((1/B)\log_{M/B}(n/B))$ amortized but pays boundary replication for sub-trajectories straddling a range edge — trading read optimality for cheap appends.

---
*Part of the [DBMS Research catalog](../../README.md).*
