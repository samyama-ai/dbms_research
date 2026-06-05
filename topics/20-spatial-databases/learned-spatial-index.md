# Learned spatial indexes with guarantees

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/learned-spatial-index` · **Status:** empirically-open

## 1. Problem Statement
A **learned index** replaces (parts of) a classical index with a model $\hat f$ that predicts the storage position of a key, correcting prediction error by a bounded local search. For **multidimensional / spatial** data the goal is a structure that, given a point set $P\subset\mathbb{R}^d$ (or rectangles), answers **range queries**, **k-NN**, and **point queries** with:
- query time competitive with an R-tree / k-d tree (ideally $O(\log n + |\text{out}|)$), and
- **worst-case** bounds (not just average-case) on query and update cost,

while exploiting learned models to shrink index size and improve constants on **real GIS distributions**. The hard part is that a 1-D learned index relies on a total order; in $d>1$ no order preserves locality, so one must learn a space-filling-curve mapping *and* bound the error/locality loss it induces.

Variants: static (build-once) vs. **updatable**; **counting** (range-count via learned CDF) vs. **reporting**; approximate vs. exact NN.

## 2. Mathematical Foundations
The 1-D learned index (Kraska et al. SIGMOD 2018) models the **empirical CDF**: position $\approx n\cdot F(x)$ where $F$ is the key CDF, learned by a "recursive model index" (RMI). Worst-case query time depends on the **maximum prediction error** $\epsilon=\max_x |n F(x) - \hat f(x)|$; a query costs $O(\log\epsilon)$ local search. **PGM-index** (Ferragina–Vinciguerra, PVLDB 2020) makes $\epsilon$ a *tunable, provable* bound via piecewise-linear $\epsilon$-approximation, yielding $O(\log_{?} n)$ worst-case with optimal space in the **PLA (piecewise-linear approximation)** model.

In $d$ dimensions, two formalisms recur:
1. **Rank-space / space-filling curve (SFC):** map $\mathbb{R}^d\to\mathbb{R}$ via a Z-order/Hilbert curve $h$, then learn $F\circ h$. Locality loss is governed by the curve's **dilation / clustering number** — Hilbert curves give $O(n^{1-1/d})$ expected query "runs" for a range, an unavoidable SFC term.
2. **Learned grid / partition:** learn cell boundaries to equalize occupancy (e.g., Flood, Tsunami), optimizing a cost model over query workload; relates to **histogram / partitioning** theory and, for guarantees, to **VC dimension** of the query class (axis-parallel rectangles have VC-dim $2d$) bounding sample complexity of workload-adaptive layouts.

The central tension: models give good *expected* performance under the assumed distribution, but a **distribution shift** or adversarial query breaks any guarantee that is not enforced by an error bound $\epsilon$ + a fallback structure.

## 3. State of the Art (SOTA)
- **1-D with guarantees:** **PGM-index** (provable $\epsilon$, optimal-space PLA); **RadixSpline**, **ALEX** (updatable, Ding et al. SIGMOD 2020).
- **Spatial / multi-D (systems-SOTA):** **Flood** (Nathan et al. SIGMOD 2020) and **Tsunami** (Ding et al. VLDB 2020) — workload-and-data-adaptive learned grids beating R-trees on in-memory analytic ranges; **LISA** (Li et al. SIGMOD 2020) — learned disk-based spatial index; **RSMI / Recursive Spatial Model Index** (Qi et al. VLDB 2020); **ZM-index** (Z-order + model). **SPRIG**, **RLR-tree** (RL-tuned R-tree). Most report strong empirical wins but rely on average-case behavior.
- **Theory-SOTA:** PGM-style provable bounds exist in 1-D; clean **worst-case multidimensional** learned bounds are essentially absent — this is the open core.

## 4. Upper Bound
- **1-D:** PGM-index gives query $O(\log\frac{n}{\epsilon}+\log\epsilon)$ with space tunable to $O(n/\epsilon)$ segments, provable in the PLA model — competitive with B-trees worst-case.
- **Spatial:** Best provable statements are conditional on a bounded prediction error $\epsilon$ per learned partition plus a classical fallback (so the worst case degrades to the underlying grid/R-tree). No learned multidimensional index is known to **strictly dominate** R-trees in worst case; empirical speedups of 2–60× on real GIS workloads are reported but are average-case.

## 5. Lower Bound
- **Range reporting** in $d\ge2$ has the classical **cell-probe / pointer-machine** lower bound $\Omega((\log n/\log\log n))$ per query for $\tilde O(n)$ space (Chazelle; Pătrașcu lineage); orthogonal range counting has $\Omega(\log n/\log\log n)$ cell-probe bounds — a learned index **cannot beat these** without extra space, so any "sub-logarithmic" claim must rest on distributional assumptions.
- **Distribution dependence:** without a bounded-error guarantee, adversarial inputs force the model's local search to $\Omega(n)$; guarantees therefore *must* import the $\epsilon$ error budget, which costs space.

## 6. The Gap
In 1-D the gap is largely **closed** (PGM matches B-tree worst case with better constants). In $\ge 2$D it is **genuinely open**: there is no learned spatial index with worst-case query/update bounds provably competitive with R-trees that *also* delivers the empirical wins on real data. Closing it requires either (a) a multidimensional analogue of the $\epsilon$-PLA guarantee that survives the SFC locality loss, or (b) a hybrid that provably falls back to R-tree bounds while keeping learned fast paths — with a clean characterization of when learning helps (data "learnability" / smoothness of $F$).

## 7. Current Research (as of June 2026)
- **Updatable learned spatial indexes** combining ALEX-style gapped arrays with learned grids (overlaps the high-churn problem).
- **Distribution-shift-robust** models with online retraining and bounded staleness *(frontier — verify the worst-case guarantees claimed by 2025 systems)*.
- **Theory of learnability** for indexes: characterizing when a smooth CDF yields provable speedups (Vinciguerra–Ferragina; Kraska/MIT DSAIL lineage).
- **GPU/accelerator** learned spatial indexes and integration into DuckDB/PostGIS-style engines.
Groups: MIT DSAIL (Kraska), Pisa (Ferragina–Vinciguerra), TU Munich, RMIT (Qi/Tanin), and the Flood/Tsunami authors.

## 8. Future Work
- A provable worst-case-competitive multidimensional learned index, or a cell-probe lower bound showing learning cannot help beyond constants for adversarial workloads.
- Unified cost model coupling data distribution + query workload + update rate.
- Robustness certificates under distribution shift.
- Secondary/disk-resident learned spatial indexes with I/O-optimal guarantees.

## 9. Key References
- **[Foundational]** T. Kraska, A. Beutel, E. H. Chi, J. Dean, N. Polyzotis. *The case for learned index structures.* SIGMOD, 2018.
- **[Foundational]** P. Ferragina, G. Vinciguerra. *The PGM-index: a fully-dynamic compressed learned index with provable worst-case bounds.* PVLDB, 2020.
- **[SOTA]** V. Nathan, J. Ding, M. Alizadeh, T. Kraska. *Learning multi-dimensional indexes (Flood).* SIGMOD, 2020.
- **[SOTA]** J. Ding et al. *Tsunami: a learned multi-dimensional index for correlated data and skewed workloads.* PVLDB, 2020.
- **[SOTA]** P. Li, H. Lu, Q. Zheng, L. Yang, G. Pan. *LISA: A learned index structure for spatial data.* SIGMOD, 2020.
- **[Survey]** A. Al-Mamun, H. Wu, W. G. Aref. *A tutorial on learned multi-dimensional indexes.* SIGSPATIAL, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
