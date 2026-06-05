# Zone Maps and Min/Max Skipping Bounds

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/zone-map-skipping-bounds` · **Status:** partially-solved
> **Verification note:** The "Fine-grained Partitioning for Aggressive Data Skipping" (SIGMOD 2014) authors are Sun, Franklin, Krishnan, and Xin (not "Kandula"); §3's inline attribution misnames a co-author.

## 1. Problem Statement

A *zone map* (a.k.a. min/max index, small-materialized aggregate, or block-range index) stores, for each physical block (zone) of a column, summary statistics — typically the minimum and maximum value — so that a scan can *skip* a block whenever its $[\min,\max]$ interval is provably disjoint from a query predicate's selection range. The central problem has two coupled variants:

- **Effectiveness (analysis) variant:** Given a data layout (an assignment of rows to blocks) and a query workload, bound the *fraction of blocks that must still be scanned* — the **scan amplification** — relative to the ideal of touching only blocks that contain a qualifying row.
- **Layout (optimization) variant:** Given a workload (or a distribution over predicates) and a row count $n$ with block size $B$, choose a row-to-block assignment — equivalently a *sort/clustering order*, possibly multi-dimensional — that minimizes expected scan amplification subject to maintaining at most $O(1)$ orders (one physical order) or a small number of replicated orderings.

The decision version ("does a layout exist achieving amplification $\le \alpha$?") and the optimization version are both of interest; the counting variant ("how many blocks survive predicate $P$?") underlies cost-based query optimization.

## 2. Mathematical Foundations

Let a column be a multiset $X = \{x_1,\dots,x_n\}$ partitioned into $m = \lceil n/B\rceil$ zones $Z_1,\dots,Z_m$. Each zone has interval $I_j = [\min Z_j, \max Z_j]$. A range predicate $[a,b]$ scans $Z_j$ iff $I_j \cap [a,b] \neq \emptyset$. Define **survivability**
$$ S(a,b) = \\#\{ j : I_j \cap [a,b] \neq \emptyset \}, $$
and the *false-survival* (over-scan) count $S(a,b) - S^*(a,b)$ where $S^*$ counts only zones containing a true match. For a *fully sorted* column, intervals are nested/contiguous, so $S^* \le S \le S^* + 2$: at most two boundary zones are wasted, giving optimal one-dimensional skipping. The difficulty is **multi-dimensional**: with $d$ independent range attributes and a single physical order, no order is simultaneously locality-preserving for all $d$ dimensions.

Key tools: the layout problem reduces to a **clustering / space-filling-curve** problem. Z-order (Morton) and Hilbert curves bound the *dilation* of locality; for a $d$-dimensional grid the number of curve segments intersecting an axis-aligned query box of side $s$ scales like $\Theta(s^{d-1})$, which controls surviving-block counts. Information-theoretically, with one ordering the achievable skipping across $d$ uncorrelated dimensions is constrained by a *Kolmogorov–Smirnov*-style spread argument: total "ordering budget" $\log n!$ must be shared across dimensions.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Zone maps are ubiquitous — Netezza (zone maps, 2003), PostgreSQL BRIN, Snowflake micro-partitions with pruning, Apache Parquet/ORC page+stripe statistics, ClickHouse sparse primary indexes, Amazon Redshift zone maps. *Multi-dimensional clustering*: Snowflake clustering keys, Databricks Delta **Z-Ordering** and the newer **Liquid Clustering** *(frontier — verify)*, Amazon Redshift interleaved sort keys (Z-order based).
- **Theory-SOTA:** The clustering-for-skipping problem was formalized by Sun, Franklin, et al. as **workload-driven partitioning** ("Fine-grained partitioning for aggressive data skipping", SIGMOD 2014) using a feature-based partitioning that provably reduces scanned blocks for a given workload via a reduction to balanced graph/cluster partitioning.

## 4. Upper Bound

For 1-D range predicates on a sorted column, optimal: $S \le S^* + 2$, i.e., additive-2 over-scan, $O(\log m)$ time to identify the surviving contiguous run via binary search over zone boundaries, $O(m)$ space for the zone map (two values per block). For $d$-D with a Z-order/Hilbert clustering, the surviving-block upper bound is $O(s^{d-1})$ per box query (grid of side $s$), and Sun et al.'s feature-partitioning achieves a constant-factor approximation to the *workload-optimal* skipping objective under their cost model.

## 5. Lower Bound

With a **single** physical ordering and $d \ge 2$ independent uniform range dimensions, any layout incurs expected survival $\Omega(m^{1-1/d})$ for a constant-selectivity box — a consequence of space-filling-curve lower bounds (no bijection $[1,n]\to[1,n']^d$ has dilation $o(n^{1/d})$). The general workload-optimal partitioning problem is **NP-hard** (reduction from balanced graph partitioning / hypergraph min-cut), so exact layout optimization is intractable; only approximations are achievable. Min/max summaries alone are *information-theoretically* weak against non-contiguous predicates (e.g. equality on a high-cardinality unsorted column), where $S$ can be $\Theta(m)$ with $S^*$ small.

## 6. The Gap

For 1-D the gap is **closed** (additive-2 optimal). For multi-D the gap is **genuinely open**: the $\Omega(m^{1-1/d})$ single-order lower bound is matched only up to constants by Z/Hilbert curves for uniform data, but for *skewed/correlated real workloads* the achievable–vs–optimal gap (and how many replicated orderings buy how much skipping) is not tightly characterized. Closing it requires either (a) tight bounds on replicated-ordering skipping, or (b) workload-aware lower bounds beyond uniform assumptions.

## 7. Current Research (as of June 2026)

- Learned and workload-adaptive layouts: Qd-tree (Yang et al., SIGMOD 2020) uses RL to cut data into skip-friendly blocks; follow-ons extend to streaming/ingest. *(frontier — verify)*
- Databricks **Liquid Clustering** as an incremental, ingest-time alternative to static Z-order, with internal claims of better pruning under drift *(frontier — verify)*.
- Richer per-zone summaries (histograms, Bloom/range filters, "column sketches" by Hentschel et al., SIGMOD 2018) to attack equality and non-contiguous predicates.

## 8. Future Work

- Tight multi-dimensional skipping bounds for replicated orderings ($k$ orders $\Rightarrow$ what amplification?).
- Predicate-distribution-aware layouts with provable competitive ratios against an adaptive workload.
- Unifying zone maps with secondary lightweight filters under a single I/O cost model.

## 9. Key References

- **[Foundational]** G. Moerkotte. *Small Materialized Aggregates: A Light Weight Index Structure for Data Warehousing.* VLDB, 1998. — [PDF](https://www.vldb.org/conf/1998/p476.pdf)
- **[SOTA]** L. Sun, M. J. Franklin, S. Krishnan, R. S. Xin. *Fine-grained Partitioning for Aggressive Data Skipping.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610515)
- **[SOTA]** Z. Yang et al. *Qd-tree: Learning Data Layouts for Big Data Analytics.* SIGMOD, 2020. — [DBLP](https://dblp.org/rec/conf/sigmod/YangCWGLMLKA20.html)
- **[SOTA]** B. Hentschel, M. S. Kester, S. Idreos. *Column Sketches: A Scan Accelerator for Rapid and Robust Predicate Evaluation.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196911)
- **[Survey]** D. Abadi, P. Boncz, S. Harizopoulos, S. Idreos, S. Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Column of $n=12$ values stored **sorted**, block size $B=4$, so $m=3$ zones:

- $Z_1=[2,5,7,9]\Rightarrow I_1=[2,9]$
- $Z_2=[11,14,16,18]\Rightarrow I_2=[11,18]$
- $Z_3=[20,22,25,30]\Rightarrow I_3=[20,30]$

Query predicate $[13,21]$. Test each interval: $I_1=[2,9]$ disjoint → **skip**; $I_2=[11,18]$ overlaps → scan; $I_3=[20,30]$ overlaps → scan. So $S=2$ zones survive. True matches are $14,16,18$ (in $Z_2$) and $20$ (in $Z_3$), so $S^*=2$. Over-scan $=S-S^*=0$ here — the additive-2 bound ($S\le S^*+2$) holds comfortably, and binary search locates the surviving contiguous run $Z_2..Z_3$ in $O(\log m)$.

**Why multi-D breaks:** add a second sorted attribute. With one physical order you can co-sort on attribute A *or* B but not both. For $d=2$ uniform dimensions and a constant-selectivity box, the single-order lower bound forces $\Omega(m^{1-1/d})=\Omega(\sqrt{m})$ surviving zones — here $\Omega(\sqrt{3})\approx 2$ even for a tiny box, versus the 1-D additive-2 optimum. This is the gap a Z-order/Hilbert clustering can only match up to constants.

---
*Part of the [DBMS Research catalog](../../README.md).*
