---
id: 27-learned-db-components/multidimensional-learned-indexes
title: "Multidimensional Learned Indexes"
topic: 27-learned-db-components
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Multidimensional Learned Indexes

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/multidimensional-learned-indexes` · **Status:** empirically-open
> **Verification note:** the specific Morton codes and "4 disjoint runs" in §10 do not match a standard bit-interleaved Z-order (which yields codes {6,7,12,13,14,15} = 2 runs for this rectangle); the qualitative fragmentation point still holds but the exact numbers should be recomputed.

## 1. Problem Statement
One-dimensional learned indexes exploit a clean monotone CDF; in $d > 1$ dimensions there is no canonical total order, so the problem is harder. The goal: **a learned multidimensional index that beats R-trees, k-d-trees, and space-filling-curve (Z-order/Hilbert) layouts for range and k-NN queries — with *provable* block-skipping / I/O bounds**, not merely empirical wins on benchmark workloads.

- **Static/optimization variant:** given a dataset of $n$ points in $\mathbb{R}^d$ and a query workload, build a layout + model minimizing expected blocks scanned per query under a space budget.
- **Decision variant:** does a learned layout exist with worst-case range-query I/O within a constant of the output-sensitive optimum $O(n^{1-1/d} + k)$?
- **k-NN variant:** bound distance computations with provable pruning guarantees.

Status is *empirically-open*: systems (Flood, Tsunami, LISA, RSMI) beat classical baselines on many workloads, but provable worst-case skipping bounds are missing.

## 2. Mathematical Foundations
Classical worst-case range reporting in $d$ dimensions costs $\Omega(n^{1-1/d} + k)$ I/Os for $k$ outputs (the **Kanellakis–Ramaswamy–Vengroff–Vitter** lower bound for the external-memory model), matched by kd-B-trees up to constants. Learned approaches reduce dimensionality:
- **Space-filling curves** map $\mathbb{R}^d \to \mathbb{R}$ preserving locality approximately (Hilbert distortion $\Theta(\sqrt{d})$-bounded clustering), then apply a 1-D learned index — but range queries become *unions of curve intervals*, and the number of intervals is the cost driver.
- **Grid/flattening** methods (Flood, Tsunami) learn a per-dimension partitioning minimizing expected scanned cells, optimizing the layout to the *query workload* — a combinatorial layout-optimization with no closed-form optimum.
- k-NN pruning relates to learned **bounding** of point sets; without metric guarantees, pruning is heuristic.

## 3. State of the Art (SOTA)
- **Systems/empirical:** Flood (Nathan et al., SIGMOD 2020) — workload-adaptive learned grid, beats optimized R-trees/octrees on range queries. Tsunami (Ding et al., VLDB 2020) — handles correlated columns and skewed workloads via learned partitioning. LISA (Li et al., SIGMOD 2020) — disk-based learned spatial index. RSMI (Qi et al., VLDB 2020) — recursive spatial model index with rank-space transformation. ML-enhanced Z-order/Hilbert layouts.
- **Theory:** mostly absent — these are empirical; provable skipping/I-O bounds for the learned variants are not established.

## 4. Upper Bound
Empirically, Flood/Tsunami achieve large constant-factor reductions in cells/blocks scanned versus tuned classical indexes by aligning partition granularity to query and data distributions. No method has a *proven* worst-case I/O bound better than (or even matching) the classical $O(n^{1-1/d}+k)$; their guarantees are average-case over the trained workload. RSMI's rank-space mapping improves monotonicity but without a worst-case range-query proof.

## 5. Lower Bound
The external-memory range-reporting lower bound $\Omega(n^{1-1/d} + k)$ (KRVV) and the **pointer-machine** lower bounds of Chazelle for orthogonal range search apply to *any* layout, learned or not — so learned multidimensional indexes cannot asymptotically beat classical structures on worst-case range queries. For k-NN, curse-of-dimensionality lower bounds (e.g., for exact nearest neighbor) similarly bind. Thus, as in 1-D, learned gains must be *distributional/workload* constants, not asymptotic — but a *matching* learned upper bound proving these constants is the missing piece.

## 6. The Gap
Empirically open. Lower bounds are inherited from classical range-search theory; the gap is the **absence of any provable upper bound** for learned layouts that (a) certifies the empirical block-skipping wins and (b) characterizes which data/workload distributions admit them. Closing it needs a formal model of learned-layout cost and a two-sided (workload-parameterized) bound — currently only experiments exist.

## 7. Current Research (as of June 2026)
- **Workload-adaptive layout learning** with optimization-theoretic guarantees on expected blocks scanned *(frontier — verify)*.
- Learned **space-filling curves** that minimize range-query interval fragmentation provably *(frontier — verify)*.
- Updatable multidimensional learned indexes and k-NN with pruning bounds.
- Groups: MIT DSAIL (Flood/Tsunami, Nathan, Ding, Kraska); RMIT/UQ (RSMI, LISA, spatial learned indexing); ongoing spatial-DB integration.

## 8. Future Work
- Provable block-skipping bounds parameterized by data/query distribution.
- Robustness to workload drift and updates in $d$ dimensions.
- Learned indexes for high-dimensional / vector k-NN with pruning guarantees.

## 9. Key References
- **[Foundational]** T. Kraska, et al. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** V. Nathan, J. Ding, M. Alizadeh, T. Kraska. *Learning Multi-Dimensional Indexes (Flood).* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/1912.01668)
- **[SOTA]** J. Ding, et al. *Tsunami: A Learned Multi-dimensional Index for Correlated Data and Skewed Workloads.* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2006.13282)
- **[SOTA]** P. Li, et al. *LISA: A Learned Index Structure for Spatial Data.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389703)
- **[Foundational]** P. Kanellakis, S. Ramaswamy, D. Vengroff, J. Vitter. *Indexing for Data Models with Constraints and Classes.* PODS, 1993 (external-memory range-search bounds). — [DOI](https://doi.org/10.1145/153850.153884)

## 10. Worked Example

Take $n=16$ points in $d=2$ on a $4\times4$ grid (one point per cell), block = one grid cell, and a range query covering the rectangle $x\in[2,3],\,y\in[1,3]$.

- **Z-order curve.** Indexing cells by Morton code, the query rectangle is *not* a contiguous Z-interval: cells $(2,1),(3,1),(2,2),(3,2),(2,3),(3,3)$ have Morton codes $7,13,6,12,3,9$ — splitting into intervals $\{3\},\{6,7\},\{9\},\{12,13\}$ = **4 disjoint runs**. A 1-D learned index over Morton codes must issue 4 separate range scans; fragmentation is the cost driver.
- **Flood-style learned grid.** A workload-adaptive grid that simply partitions on $x$ then $y$ scans exactly the $2\times3=6$ target cells as one rectangular block sweep — **0 wasted cells**, no interval fragmentation.

So here Flood touches 6 cells vs Z-order's 6 cells across 4 fragmented runs (extra seeks). Asymptotically neither beats the KRVV floor $\Omega(n^{1-1/d}+k)=\Omega(\sqrt{16}+6)=\Omega(10)$; the learned win is the *constant* — eliminating curve-fragmentation seeks — exactly the empirical-but-unproven gain section 6 flags.

---
*Part of the [DBMS Research catalog](../../README.md).*
