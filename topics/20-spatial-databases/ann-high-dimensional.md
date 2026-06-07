---
id: 20-spatial-databases/ann-high-dimensional
title: "Approximate nearest neighbor in high dimensions"
topic: 20-spatial-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Approximate nearest neighbor in high dimensions

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/ann-high-dimensional` · **Status:** partially-solved

## 1. Problem Statement
**$(c,r)$-approximate near neighbor (ANN):** preprocess $N$ points in $(\mathbb{R}^d,\ell_p)$ so that, given query $q$, if some point lies within distance $r$, return a point within $cr$ (for approximation $c>1$). The exact nearest-neighbor problem in high $d$ suffers the **curse of dimensionality** — known structures degrade to near-linear scan. ANN is the practical relaxation.

**Open core:** *close the gap* between (a) the time–accuracy tradeoffs achieved by deployed methods (LSH families and graph indexes such as HNSW/DiskANN) and (b) the **proven cell-probe and data-structure lower bounds**. Concretely: for what $(c,\rho)$ is query time $O(N^\rho)$ with space $O(N^{1+\rho})$ optimal, and do graph-based indexes admit *any* matching worst-case theory? Variants: decision (near-neighbor), reporting (all near neighbors), and the $k$-ANN top-$k$ problem.

## 2. Mathematical Foundations
**Locality-Sensitive Hashing (LSH):** a hash family $\mathcal{H}$ is $(r,cr,p_1,p_2)$-sensitive if $\Pr[h(x)=h(y)]\ge p_1$ when $\|x-y\|\le r$ and $\le p_2$ when $\ge cr$. The exponent
$$\rho=\frac{\log(1/p_1)}{\log(1/p_2)}$$
governs cost: query time $\tilde O(N^\rho)$, space $\tilde O(N^{1+\rho})$. For $\ell_2$, **Andoni–Indyk** achieve $\rho=1/c^2+o(1)$; **data-dependent** hashing (Andoni–Razenshteyn) improves to $\rho=\frac{1}{2c^2-1}+o(1)$. Lower bounds: in the LSH framework $\rho\ge 1/c^2-o(1)$ (data-*independent*), and $\rho\ge \frac{1}{2c^2-1}-o(1)$ for data-dependent (Andoni–Razenshteyn). Cell-probe lower bounds (Panigrahy–Talwar–Wieder; Andoni–Indyk–Pătraşcu) bound the space–query tradeoff. Graph indexes rest on **navigable small-world** / Delaunay-approximation geometry with far weaker theory; their success connects to the **doubling dimension** and intrinsic dimensionality of real data.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Andoni–Razenshteyn **optimal data-dependent LSH** ($\rho=\frac{1}{2c^2-1}$ for $\ell_2$); Andoni–Laarhoven–Razenshteyn–Waingarten time–space tradeoff curve (STOC 2017) — currently the best-known and matching the LSH-family lower bounds.
- **Systems-SOTA:** **HNSW** (Malkov–Yashunin, 2016/2018) and **DiskANN/Vamana** (Subramanya et al., NeurIPS 2019) dominate vector-search benchmarks (ann-benchmarks, BigANN); **ScaNN** (Guo et al., 2020) for anisotropic quantization. These power vector databases (FAISS, Milvus, pgvector, Pinecone, Weaviate).

## 4. Upper Bound
Optimal data-dependent LSH: for $\ell_2$ and approximation $c$, query $\tilde O(N^{\rho_q})$ with space $\tilde O(N^{1+\rho_s})$ where $(\rho_q,\rho_s)$ lie on the Andoni–Laarhoven–Razenshteyn–Waingarten optimal curve, e.g. balanced point $\rho=\frac{1}{2c^2-1}$. Graph indexes (HNSW, Vamana) give empirically *poly-logarithmic* query at high recall but **no worst-case guarantee** — provable bounds exist only under benign assumptions (bounded doubling dimension).

## 5. Lower Bound
Within the LSH framework, $\rho\ge\frac{1}{2c^2-1}-o(1)$ (Andoni–Razenshteyn) — tight against the upper bound, so **LSH is closed**. In the general **cell-probe** model, the picture is weaker: lower bounds (O'Donnell–Wu–Zhou; Andoni–Indyk–Pătraşcu) constrain but do not fully match the space–time tradeoff for *arbitrary* structures, leaving room for non-LSH algorithms (e.g., graph indexes) that could, in principle, beat the LSH barrier. No nontrivial cell-probe lower bound is known to apply to the navigable-graph paradigm.

## 6. The Gap
Two gaps: (1) **theory vs. systems** — graph indexes outperform LSH in practice but lack worst-case theory, while LSH theory is tight but rarely the fastest deployed method; (2) **LSH-optimal vs. cell-probe-optimal** — whether *any* data structure can beat the $\frac{1}{2c^2-1}$ exponent for general inputs is open, since cell-probe lower bounds don't yet forbid it. Closing requires either a graph-index analysis with worst-case guarantees, or a cell-probe lower bound matching LSH for all structures.

## 7. Current Research (as of June 2026)
Heavy activity driven by **vector databases for RAG/embeddings**: theoretical analysis of **graph-based ANN** (when does greedy routing on navigable graphs provably converge in polylog steps?) *(frontier — verify)*; **filtered / hybrid ANN** (predicate + vector); **streaming and fresh-update** indexes (FreshDiskANN); quantization–graph hybrids; and **GPU ANN**. Groups: Andoni, Razenshteyn, Indyk (theory); Microsoft Research / DiskANN, Google ScaNN, Meta FAISS (systems).

## 8. Future Work
- Worst-case (or doubling-dimension-parameterized) guarantees for HNSW/Vamana-style graphs.
- Cell-probe lower bounds matching or separating from the LSH exponent for general structures.
- Provable time–accuracy bounds for *exact-recall-target* ANN, not just $(c,r)$.
- Theory for filtered, multi-vector, and dynamic/streaming ANN.

## 9. Key References
- **[Foundational]** P. Indyk, R. Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC, 1998. — [DBLP](https://dblp.org/rec/conf/stoc/IndykM98.html)
- **[SOTA]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[SOTA]** A. Andoni, T. Laarhoven, I. Razenshteyn, E. Waingarten. *Optimal Hashing-Based Time–Space Trade-offs for Approximate Near Neighbors.* SODA, 2017. — [arXiv](https://arxiv.org/abs/1608.03580)
- **[SOTA]** Y. Malkov, D. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs (HNSW).* IEEE TPAMI, 2018. — [arXiv](https://arxiv.org/abs/1603.09320)
- **[SOTA]** S. J. Subramanya, et al. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [NeurIPS](https://proceedings.neurips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html)
- **[Survey]** A. Andoni, P. Indyk, I. Razenshteyn. *Approximate Nearest Neighbor Search in High Dimensions.* Proc. ICM, 2018. — [arXiv](https://arxiv.org/abs/1806.09823)

## 10. Worked Example

Take $\ell_2$ ANN with approximation $c=2$ and $N=10^6$ points. Compare the two LSH regimes on the **query-time exponent** $\rho$, where cost is $\tilde O(N^\rho)$.

- **Data-independent (Andoni–Indyk):** $\rho = 1/c^2 = 1/4 = 0.25$, so query touches $\approx N^{0.25} = (10^6)^{0.25} = 10^{1.5} \approx 32$ "buckets'" worth of work.
- **Optimal data-dependent (Andoni–Razenshteyn):** $\rho = \frac{1}{2c^2-1} = \frac{1}{2\cdot4-1} = \frac{1}{7} \approx 0.143$, giving $\approx N^{0.143} = (10^6)^{0.143} \approx 10^{0.857} \approx 7.2$.

So at $c=2$ the data-dependent bound cuts the exponent from $0.25$ to $\approx 0.143$ — roughly a $32/7 \approx 4.5\times$ asymptotic speedup, and the lower bound $\rho \ge \frac{1}{2c^2-1}$ says no LSH-family scheme can do better. Meanwhile a graph index (HNSW) on the same set empirically answers in $\approx 50$–$200$ distance comparisons at 95% recall — fast in practice, but with no matching worst-case $\rho$ guarantee, which is exactly the theory-vs-systems gap of Section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
