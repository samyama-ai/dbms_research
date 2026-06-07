---
id: 28-vector-similarity-search/compression-graph-codesign
title: "Joint compression and graph co-design"
topic: 28-vector-similarity-search
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Joint compression and graph co-design

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/compression-graph-codesign` · **Status:** open

## 1. Problem Statement
Billion-scale ANN stacks layer two mechanisms: a **proximity graph** (HNSW/Vamana) that decides *which* candidates to visit, and a **quantizer** (PQ/OPQ/RaBitQ/scalar) that compresses vectors so distances are *cheap/approximate*. These are almost always designed *independently* — build the graph on full-precision vectors, then quantize for storage/scoring, or quantize first and build the graph on codes. But the two interact: quantization error perturbs the very distances that determine graph edges and greedy navigation, so an edge set optimal for exact distances can be suboptimal under quantized scoring, and vice versa. The problem: **jointly optimize the quantization codebook and the graph topology to maximize recall at a fixed total bit/compute budget**, rather than treating them as independent layers.

Variants:
- **Optimization:** minimize expected query cost (or maximize recall) over (codebook $\mathcal{C}$, graph $G$) subject to a bit budget $B$ per vector and degree budget $M$.
- **Construction:** build $G$ whose *greedy navigability holds under the quantized distance* $\hat d$, not the true $d$.
- **Routing/rerank split:** decide which bits/precision to spend on *navigation* (graph traversal scoring) vs. *ranking* (final rerank), jointly with topology.

## 2. Mathematical Foundations
Let true distance be $d$ and quantized estimate $\hat d=d+\eta$ with error $\eta$ depending on codebook $\mathcal C$. Greedy search correctness depends on the *ordering* induced by $\hat d$ along graph paths.

Key scaffolding:
- **Quantization theory.** Product Quantization (Jégou–Douze–Schmid, TPAMI 2011) splits $\mathbb{R}^d$ into $m$ subspaces with $k$-means codebooks; OPQ (Ge et al., 2013) learns a rotation minimizing quantization distortion. RaBitQ (Gao–Long, SIGMOD 2024) gives *unbiased* distance estimators with concentration bounds — error bars that a co-design can propagate into edge selection.
- **Rate–distortion.** A bit budget $B$ caps achievable distortion $D(B)$ (Shannon rate–distortion); the open question is the *task-rate–distortion* tradeoff — bits-per-vector vs. *recall*, not vs. MSE.
- **Monotonicity under noise.** Graph search is exact on a monotonic search network; under $\hat d$, monotonicity requires edges robust to the *ordering* perturbations $\eta$ induces. This couples codebook variance to admissible topology — an explicitly *joint* constraint.
- **Submodular/combinatorial edge selection.** Choosing $M$ neighbors to preserve navigability under noisy distances is a coverage-like problem; greedy heuristics (RNG pruning) lack joint-with-quantization guarantees.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** DiskANN/Vamana stores PQ codes in RAM for navigation and full vectors on SSD for rerank — a hand-tuned *two-precision* design, not a joint optimum. ScaNN co-tunes anisotropic quantization toward the MIPS *score*, a partial step toward task-aware compression. RaBitQ + graph (e.g., in modern vector DBs) tightens estimator quality but still treats the graph as fixed.
- **Theory-SOTA:** quantizer-side bounds (RaBitQ concentration) and graph-side analyses (Prokhorenkova–Shekhovtsov) exist *separately*; no theory couples them. Learned/end-to-end indexes that train codebook and selection jointly are emerging but lack guarantees.

## 4. Upper Bound
No bound is known for the *joint* objective. Component bounds: OPQ/PQ achieve distortion within a constant of the per-subspace optimum given the rotation; RaBitQ gives distance estimates with error $O(1/\sqrt{B})$-type concentration for bit budget $B$, so navigation errors can be bounded *given* a fixed graph. Composing these into a recall guarantee for *co-designed* $(\mathcal C,G)$ is open; the best available is empirical Pareto fronts on benchmarks.

## 5. Lower Bound
- **Rate–distortion:** Shannon gives an information-theoretic floor $D(B)$ on achievable distortion at $B$ bits/vector; below it, *some* query orderings must be wrong, lower-bounding recall loss as a function of the bit budget independent of graph cleverness.
- **Fine-grained:** the underlying ANN problem retains its SETH/cell-probe hardness; compression cannot evade the worst-case space/time tradeoffs (Andoni–Razenshteyn optimal-LSH lower bounds). Jointly optimal $(\mathcal C,G)$ selection is at least as hard as graph construction for navigability, for which no efficient exact algorithm with guarantees is known.

## 6. The Gap
Genuinely open. Practice shows large gains from *co-tuning* precision and topology (two-precision DiskANN, anisotropic ScaNN), but there is no theory of the joint optimum, no task-rate–distortion characterization (bits ↔ recall), and no algorithm with a guarantee for selecting codebook and edges together. Closing it needs (i) a recall-oriented rate–distortion bound, and (ii) a joint construction whose navigability under quantized distances is provable.

## 7. Current Research (as of June 2026)
Active directions: unbiased/quantization-with-error-bars estimators (RaBitQ and successors) feeding *error-aware* graph pruning *(frontier — verify)*; learned end-to-end indexes that backprop a retrieval objective into both codebook and edge scores *(frontier — verify)*; multi-precision navigation (cheap codes to traverse, finer codes to rerank) being formalized as a budget-allocation problem; and GPU-native designs (CAGRA + compression) that change the compute/bit tradeoff. Contributors: FAISS/Meta, ScaNN/Google, the RaBitQ authors (NTU/academic DB), and vector-DB vendors.

## 8. Future Work
- A task-rate–distortion theory: minimum bits/vector to reach recall $\rho$ on a given graph.
- Provably navigable graph construction under a quantized distance with known error bars.
- Joint, differentiable codebook+topology optimization with guarantees.
- Principled precision split between navigation and reranking under a single budget.

## 9. Key References
- **[Foundational]** H. Jégou, M. Douze, C. Schmid. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011. — [DOI](https://doi.org/10.1109/TPAMI.2010.57)
- **[Foundational]** T. Ge, K. He, Q. Ke, J. Sun. *Optimized Product Quantization (OPQ).* IEEE TPAMI / CVPR, 2013. — [DOI](https://doi.org/10.1109/TPAMI.2013.240)
- **[SOTA]** J. Gao, C. Long. *RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search.* SIGMOD, 2024. — [arXiv](https://arxiv.org/abs/2405.12497) · [DOI](https://doi.org/10.1145/3654970)
- **[SOTA]** R. Guo, et al. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization (ScaNN).* ICML, 2020. — [arXiv](https://arxiv.org/abs/1908.10396)
- **[SOTA]** S. J. Subramanya, et al. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [PDF](https://suhasjs.github.io/files/diskann_neurips19.pdf)
- **[Survey]** L. Prokhorenkova, A. Shekhovtsov. *Graph-based Nearest Neighbor Search: From Practice to Theory.* ICML, 2020. — [arXiv](https://arxiv.org/abs/1907.00845)

## 10. Worked Example

Three 1-D points $x_1=0,\ x_2=1,\ x_3=3$, query $q=0.9$. True distances: $d(q,x_1)=0.9,\ d(q,x_2)=0.1,\ d(q,x_3)=2.1$, so the true NN is $x_2$.

Build a tiny graph independently of quantization: edges $x_1\!-\!x_2$ and $x_2\!-\!x_3$ (a path). Greedy search from $x_1$ moves to a neighbor only if it is *closer* under the scoring distance.

Now quantize to 1 bit by rounding to centroids $\{0,2\}$: $x_1\to 0,\ x_2\to 0,\ x_3\to 2$. Quantized distances become $\hat d(q,x_1)=\hat d(q,x_2)=0.9$ (both code to $0$). Greedy from $x_1$ sees neighbor $x_2$ as *no closer* ($0.9 \not< 0.9$) and stops — returning $x_1$, recall@1 $=0$.

The fix a co-design would make: spend the same bit differently, e.g. centroids $\{0.5,3\}$ so $x_1\to0.5,\ x_2\to0.5$ still ties — quantization alone cannot separate $x_1,x_2$. So the *graph* must instead add a shortcut letting navigation rerank the tied pair with full precision. This is exactly the joint $(\mathcal C, G)$ coupling: a bit budget that loses the $x_1$ vs. $x_2$ ordering forces a topology that reranks, illustrating why optimizing codebook and graph separately is suboptimal.

---
*Part of the [DBMS Research catalog](../../README.md).*
