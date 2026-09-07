---
id: 04-indexing-access-methods/learned-multidim-index
title: "Multidimensional learned indexes"
topic: 04-indexing-access-methods
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Multidimensional learned indexes

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/learned-multidim-index` · **Status:** empirically-open

## 1. Problem Statement
A **learned index** replaces a classical structure (B-tree, R-tree) with a model that predicts the position/region of a key, refined by a small local search. For one dimension this works well (RMI, PGM); the open problem is the **multidimensional / spatial** case: learn a model mapping a $d$-attribute key (or spatial point/rectangle) to storage locations so that **range, k-NN, and point queries** are fast — *with worst-case query and update guarantees*, not just average-case wins on benchmark data.

- **Static variant:** given a fixed dataset and query workload, build a layout + model minimizing expected query cost (data-blocks scanned) subject to a space budget.
- **Dynamic variant:** support inserts/deletes with bounded amortized cost while preserving query bounds — the empirically hard part.
- The crux: classical multidim indexes have provable $O(\log n + k)$-type guarantees; learned ones typically have **only empirical** guarantees that degrade adversarially.

## 2. Mathematical Foundations
1-D learned indexes approximate the **CDF** $F(x)=\Pr[\text{key}\le x]$; predicting position $\approx n\,F(x)$ with bounded error $\epsilon$ gives a local search window of size $O(\epsilon)$. The **PGM-index** (Ferragina & Vinciguerra, VLDB 2020) makes this rigorous via piecewise-linear approximation: optimal number of segments for error $\epsilon$ is computed in linear time, giving worst-case $O(\log n)$ query and provable space. In $d$ dimensions there is **no canonical CDF order**; one must impose a space-filling curve (Z-order, Hilbert) or a learned partitioning. Cost models draw on:
- **Computational geometry** lower bounds for orthogonal range search ($\Omega(\log n + k)$ comparisons; cell-probe bounds of Chazelle on space-time tradeoffs for range reporting).
- **VC dimension / learning theory** to bound how well a model class fits the data distribution, hence the worst-case local-search window.
- **Submodularity** when choosing which dimensions/cuts to learn under a budget.

## 3. State of the Art (SOTA)
- **Flood** (Nathan, Ding, Alizadeh, Kraska; SIGMOD 2020) — workload-aware grid layout, dimensions ordered by query frequency.
- **Tsunami** (Ding et al.; VLDB 2020) — handles correlated data and skewed workloads via augmented grids + trees.
- **LISA** (Li et al.; SIGMOD 2020) — learned spatial index on disk with update support.
- **RSMI / ZM-index / ML-enhanced R-trees** — space-filling-curve + model hybrids.
- **Theory-SOTA for 1-D:** PGM-index and **RadixSpline** give the only *provable* worst-case bounds; multidim designs remain empirical. Systems-SOTA: workload-adaptive learned layouts integrated into columnar/OLAP engines.

## 4. Upper Bound
1-D: PGM achieves worst-case $O(\log n)$ query, $O(n/B)$-style space, optimal segmentation — rigorous, in the comparison/RAM + I/O model. Multidim: Flood/Tsunami give strong *empirical* speedups (often 2–10×) over R-trees/grids on target workloads, but their guarantees are average-case under the trained distribution; worst-case range-query cost can degrade to a full scan when the data/query distribution shifts away from training. No multidim learned index currently matches a *provable* $O(\log n + k)$ worst-case while retaining the learned speedup.

## 5. Lower Bound
The relevant lower bounds are classical **cell-probe / pointer-machine** bounds for orthogonal range reporting: with $O(n\,\mathrm{polylog}\,n)$ space, range reporting needs $\Omega(\log\log n)$-type probe overhead beyond output size (and stronger tradeoffs of Chazelle and Pătraşcu for related problems). These bind *any* index, learned or not — a learned model cannot beat the information-theoretic geometry of range search in the worst case. Learned indexes thus cannot have an asymptotically better worst case; their value is constant-factor/distributional. No lower bound specific to "learned" structures exists; the open question is whether one can *match* classical worst-case bounds *and* the learned average-case gain simultaneously, with updates.

## 6. The Gap
Empirically excellent, theoretically ungrounded. The gap: combining (i) classical worst-case guarantees, (ii) learned-model average-case speedup, and (iii) efficient dynamic updates in $d\ge 2$. It is open whether all three are jointly achievable or whether a formal tradeoff forbids it. Closing it needs either a hybrid with a guaranteed fallback (model + classical backbone with proven bounds) or a lower bound showing learned multidim indexes cannot dominate.

## 7. Current Research (as of June 2026)
Active directions: **updatable** learned multidim indexes with bounded reorganization cost; **distribution-shift-robust** designs with worst-case fallbacks; learned indexes for high-dimensional **vector / ANN** search (overlapping with HNSW/IVF), and benchmarking frameworks (SOSD, and multidim analogues) for honest worst-case evaluation. Groups: Kraska / Tim Kraska's group (MIT, "SageDB" / instance-optimized DBs), Ferragina & Vinciguerra (Pisa, PGM), Stratos Idreos (Harvard). *(frontier — verify)* recent work claiming worst-case-bounded updatable multidim learned indexes and learned indexes that provably interleave with ANN structures.

## 8. Future Work
- A multidim learned index with proven worst-case query/update bounds and learned speedup.
- Robustness to distribution shift via guaranteed fallbacks; online retraining with regret bounds.
- Unification with ANN/vector indexing and with cost-based query optimization (instance-optimized DBs).

## 9. Key References
- **[Foundational]** Tim Kraska, Alex Beutel, Ed H. Chi, Jeffrey Dean, Neoklis Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** Paolo Ferragina, Giorgio Vinciguerra. *The PGM-index: A Fully-Dynamic Compressed Learned Index with Provable Worst-Case Bounds.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[SOTA]** Vikram Nathan, Jialin Ding, Mohammad Alizadeh, Tim Kraska. *Learning Multi-Dimensional Indexes (Flood).* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380579)
- **[SOTA]** Jialin Ding, Vikram Nathan, Mohammad Alizadeh, Tim Kraska. *Tsunami: A Learned Multi-dimensional Index for Correlated Data and Skewed Workloads.* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2006.13282)
- **[Foundational]** Bernard Chazelle. *Lower Bounds for Orthogonal Range Searching.* JACM, 1990. — [DOI](https://doi.org/10.1145/77600.77614)

## 10. Worked Example

Consider 6 points in 2-D, attributes $(x,y)$:
$(1,1),(2,2),(3,1),(8,9),(9,8),(9,9)$, and the range query $x\in[7,10],\,y\in[7,10]$ (expected answer: the last three points).

A **Flood**-style grid orders dimensions by query frequency and splits each into cells. Split $x$ at $\{5\}$ and $y$ at $\{5\}$, giving four cells. The points cluster: cell $(x{>}5,y{>}5)$ holds exactly $(8,9),(9,8),(9,9)$. The query's box overlaps only that one cell, so we scan 3 records and return all 3 — zero false hits. Cost $=$ cells-touched $\times$ records-per-cell $= 1\times3$.

Now shift the workload so queries concentrate on $x\in[8,9]$. The uniform split at $5$ is wasteful — every hot query still pays the full bottom-right cell. A workload-aware refit places a finer $x$-cut at $8.5$, shrinking the scanned cell. But if the data later drifts (new points scatter across the grid), worst-case cost rises toward a full scan of all $6$ — the missing worst-case guarantee. Classical R-trees instead bound this at $O(\log n + k)$ regardless of distribution.

---
*Part of the [DBMS Research catalog](../../README.md).*
