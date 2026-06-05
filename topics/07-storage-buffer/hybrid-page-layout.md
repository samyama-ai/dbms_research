# Optimal Page Layout for Mixed OLTP/OLAP Access

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/hybrid-page-layout` · **Status:** open

## 1. Problem Statement

Given a relation $R$ with attributes $A_1,\dots,A_m$, a physical page of fixed size $B$ bytes, and a workload $W$ that mixes point/range lookups touching whole tuples (OLTP) with scans/aggregations touching attribute subsets (OLAP), choose an **intra-page tuple layout** — pure row store (NSM), pure column store (DSM), or a partition-attributes-across (PAX) grouping — that minimizes expected total bytes read (equivalently cache-line / page transfers) over $W$.

Variants:
- **Decision:** Does a layout exist with expected cost $\le k$? (PAX column-grouping is a set-partitioning problem.)
- **Optimization:** Find the minimum-cost layout (column grouping + ordering + per-group compression hint).
- **Counting/enumeration:** Size of the Pareto frontier over (scan-cost, point-cost) — relevant to HTAP systems that keep multiple layouts.

The layout must respect the page boundary (a tuple's attributes must reconstruct within $B$) and a fill-factor constraint.

## 2. Mathematical Foundations

Model the workload as a query–attribute access matrix. Let $f_q$ be the frequency of query $q$ and $S_q \subseteq \{1,\dots,m\}$ the attributes it reads. A layout is a partition $\mathcal{P} = \{G_1,\dots,G_t\}$ of attributes into column groups stored contiguously (NSM = one group; DSM = singletons; PAX = arbitrary partition within a page).

The I/O cost of $q$ under $\mathcal{P}$, ignoring intra-group selectivity, is
$$\mathrm{cost}(q,\mathcal{P}) \;=\; \sum_{G \in \mathcal{P}\,:\,G \cap S_q \neq \emptyset} w(G),$$
where $w(G)$ is the per-tuple width of group $G$. The objective is $\min_{\mathcal{P}} \sum_q f_q\,\mathrm{cost}(q,\mathcal{P})$.

This is exactly the **attribute-clustering / vertical-partitioning** problem. The pairwise "affinity" $a_{ij}=\sum_{q:\,i,j\in S_q} f_q$ gives a weighted graph; grouping co-accessed attributes is a graph-partitioning objective related to **min-uncut / correlation clustering**. With per-group reconstruction penalties (tuple stitching), the objective gains a supermodular join-cost term, so it is neither purely submodular nor modular.

## 3. State of the Art (SOTA)

**Systems-SOTA.** PAX (Ailamaki et al., VLDB 2001) established cache-friendly hybrid layout. HYRISE (Grund et al., VLDB 2010) automated layout selection by clustering the access matrix. Modern HTAP engines — SAP HANA, SQL Server column-store indexes, Oracle Dual-Format, and **Peloton/self-driving** layout adaptation (Pavlo et al., CIDR 2017) — pick or morph layouts per fragment. **BTrim / tile-based** and Apache Arrow + Parquet's row-group/column-chunk model are the de-facto on-disk PAX.

**Theory-SOTA.** The clean abstraction is vertical partitioning; HYRISE's formulation and subsequent ILP/branch-and-bound solvers are the reference. No constant-factor approximation with proof is standard practice; production systems use greedy affinity clustering + cost-model search.

## 4. Upper Bound

The optimization is solvable by ILP (exponential worst case) or by greedy affinity clustering in $O(m^2 + |W|\cdot m)$ to build affinities plus a clustering pass. For the **fixed number of groups $t$** and metric affinities, correlation-clustering style LP rounding yields $O(\log n)$-type approximations; for unconstrained $t$ the problem inherits the best-known correlation-clustering bound (constant-factor for the complete-graph $\pm$ version, **Chawla–Makarychev–Schramm–Yaroslavtsev / Cohen-Addad et al.**). In practice greedy + cost-model search returns near-optimal layouts on real schemas within seconds.

## 5. Lower Bound

Vertical partitioning to minimize access cost is **NP-hard** (reduction from graph partitioning / the affinity-based clustering used since Navathe et al., 1984, has no poly-time exact algorithm unless P=NP). The reconstruction-penalty variant generalizes **correlation clustering**, which is **APX-hard** (MaxSNP-hard) — so a PTAS is ruled out unless P=NP. No fine-grained (SETH/3SUM) separation is known; the hardness is classical NP/APX.

## 6. The Gap

The decision problem's complexity is settled (NP-hard / APX-hard). The genuine gap is **approximation-ratio**: best provable ratios come from correlation clustering, but they ignore the page-boundary packing constraint and the supermodular stitching cost, for which **no approximation guarantee is known**. Equally open: an instance-optimal or learning-augmented layout that provably tracks a drifting workload. Closing it requires either a tight approximation for the boundary-constrained, stitch-penalized objective or a matching hardness showing it is strictly harder than plain correlation clustering.

## 7. Current Research (as of June 2026)

- **Learned / self-driving layout:** RL and cost-model-guided morphing (CMU NoisePage lineage; MIT/Brown HTAP work). *(frontier — verify)* claims of bandit-based online relayout with regret bounds remain mostly empirical.
- **Hardware-shaped layouts:** CXL-attached and NVMe-zoned storage shift the cost model; groups sized to flash read units. *(frontier — verify)*
- **Single-format HTAP:** Tile-based and "fractured mirrors" revisited under modern SIMD; Umbra/DuckDB-style adaptive compression interacts with grouping.

## 8. Future Work

- A provable approximation for vertical partitioning **with** page-packing and tuple-reconstruction penalties.
- Online relayout with worst-case regret vs. the best static layout under bounded workload drift.
- Joint optimization of layout, compression scheme, and buffer admission as one objective.
- Pareto-frontier characterization for true HTAP dual-format storage budgets.

## 9. Key References

- **[Foundational]** Ailamaki, DeWitt, Hill, Skounakis. *Weaving Relations for Cache Performance (PAX).* VLDB, 2001.
- **[Foundational]** Navathe, Ceri, Wiederhold, Dou. *Vertical Partitioning Algorithms for Database Design.* ACM TODS, 1984.
- **[SOTA]** Grund, Krüger, Plattner, Zeier, Cudre-Mauroux, Madden. *HYRISE — A Main Memory Hybrid Storage Engine.* VLDB, 2010.
- **[SOTA]** Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017.
- **[Survey]** Abadi, Boncz, Harizopoulos, Idreos, Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
