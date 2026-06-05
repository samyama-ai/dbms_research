# Provable guarantees for HNSW graph search

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/hnsw-provable-guarantees` · **Status:** open

## 1. Problem Statement
Hierarchical Navigable Small World (HNSW) graphs are the workhorse index for approximate nearest neighbor (ANN) search in production vector databases. Greedy best-first search over the multi-layer proximity graph is observed to return high-recall results in roughly logarithmic time, yet this behavior is almost entirely empirical. The problem: **establish worst-case (or distribution-parametric) guarantees** for greedy/beam search on HNSW that bound (a) the probability of returning the true $k$ nearest neighbors (recall) and (b) the number of distance evaluations (query time), as functions of dataset size $n$, dimension $d$, intrinsic dimension, and the construction parameters $M$ (degree) and $\mathit{ef}$ (beam width).

Variants:
- **Decision:** Given a query $q$ and target $r$, does greedy search find a point within distance $r$ with probability $\ge 1-\delta$?
- **Optimization:** Minimize expected distance computations subject to a recall constraint $\rho$.
- **Construction:** Does the randomized incremental HNSW build produce a graph on which greedy search provably converges?

## 2. Mathematical Foundations
Let $X = \{x_1,\dots,x_n\} \subset \mathbb{R}^d$ with metric $\mathrm{dist}$. HNSW builds a sequence of nested graphs $G_0 \supseteq \cdots \supseteq G_L$; a node enters layer $\ell$ with probability $p^\ell$ (geometric, $p = 1/\ln M$ typical). Greedy search from an entry point follows the locally distance-minimizing edge until no neighbor improves, descending layers.

Key theoretical scaffolding:
- **Navigable small-world / Kleinberg model.** Kleinberg (2000) showed decentralized greedy routing achieves $O(\log^2 n)$ hops only under a precise inverse-$d$-power long-range link distribution. HNSW's layer structure is an empirical analogue, but no Kleinberg-style exponent characterization is proven for learned data graphs.
- **Doubling dimension.** For a metric of doubling dimension $\lambda$, navigating nets (Krauthgamer–Lee 2004) give $2^{O(\lambda)}\log n$ query bounds. HNSW lacks the explicit covering invariants that make navigating nets analyzable.
- **Monotonic search networks (MSNET).** A graph is *monotonic* if from every vertex there is a path to any target along which distance strictly decreases; greedy search is exact on an MSNET. Delaunay graphs are monotonic but have degree $\Theta(n)$ in high $d$.

The crux: HNSW edges (selected by a heuristic pruning rule) only approximate Delaunay/MSNET structure, so the monotonicity that would yield a clean bound is not guaranteed to hold.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** HNSW (Malkov–Yashunin, TPAMI 2018/2020) and its descendants (FAISS-HNSW, hnswlib, NMSLIB) dominate ANN benchmarks (ann-benchmarks.com). DiskANN/Vamana (Subramanya et al., NeurIPS 2019) gives comparable recall with a flat graph and SSD residency.
- **Theory-SOTA:** Analyses exist for *idealized* relatives. Prokhorenkova & Shekhovtsov (ICML 2020) analyze graph-based ANN under a beta/uniform model on the sphere and give convergence rates for greedy search on $\varepsilon$-MSNET-like graphs. Laarhoven (2018) gives provable bounds for LSH-style and graph hybrids on random instances. No analysis directly covers the *actual* HNSW construction heuristic with its pruning rule and layered insertion.

## 4. Upper Bound
For metrics of doubling dimension $\lambda$, *navigating nets* and *cover trees* achieve $2^{O(\lambda)}\log n$ query time with $2^{O(\lambda)} n$ space — a provable upper bound for the *problem* (exact/approx NN), but not for HNSW's specific algorithm. For graph-based search on data uniform on $S^{d-1}$, Prokhorenkova–Shekhovtsov show greedy search on a suitable graph attains recall $\to 1$ with $O(n^{\rho})$ distance computations for an explicit $\rho<1$ depending on the model. Mapping these onto HNSW's heuristic graph remains conjectural.

## 5. Lower Bound
No unconditional lower bound is known specifically for greedy HNSW search. Relevant conditional bounds:
- **Cell-probe / data-structure lower bounds** for approximate NN (e.g., Andoni–Indyk–Patrascu, FOCS 2006; Andoni–Razenshteyn 2015 optimal LSH lower bound) show any $(1+\varepsilon)$-ANN data structure in high $d$ needs space/time tradeoffs implying $n^{\Omega(1/\varepsilon^2)}$-style barriers in the worst case.
- **SETH-conditional** hardness for exact NN / bichromatic closest pair (Williams; Rubinstein STOC 2018) rules out strongly subquadratic exact NN for $d = \omega(\log n)$.
These bound *the problem*, providing evidence that any HNSW guarantee must be distribution-dependent, not worst-case sublinear.

## 6. The Gap
The gap is essentially total: practitioners observe $\sim O(\log n)$ behavior with $>95\%$ recall, while theory offers either (i) bounds for related-but-different idealized graphs or (ii) hardness for the worst case. What would close it: an analysis tying HNSW's pruning heuristic and geometric layer sampling to a covering/monotonicity invariant under a realistic intrinsic-dimension model, yielding recall–time bounds matching the empirical $n^{\rho}$ or $\mathrm{polylog}$ regime.

## 7. Current Research (as of June 2026)
Active threads: graph-ANN theory under intrinsic-dimension models (Prokhorenkova and collaborators); analyses of $\alpha$-RNG / Vamana pruning that DiskANN uses, which is more analyzable than HNSW's heuristic (Indyk, Xu and others). There is growing interest in *relative neighborhood graph (RNG)* sparsification as the bridge between Delaunay monotonicity and bounded degree *(frontier — verify)*. Work on "navigability of learned graphs" and connections to expander/small-world spectral properties is emerging at NeurIPS/ICML/SODA venues *(frontier — verify)*.

## 8. Future Work
- Prove recall–query-time bounds for the exact HNSW build, not a proxy graph.
- Characterize which data distributions make HNSW's heuristic produce a (near-)monotonic graph.
- Connect the layer-sampling exponent to Kleinberg's optimal long-range exponent for general doubling metrics.
- Tighten the dependence on intrinsic vs. ambient dimension.

## 9. Key References
- **[Foundational]** Y. Malkov, D. Yashunin. *Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs.* IEEE TPAMI, 2020 (arXiv:1603.09320).
- **[Foundational]** J. Kleinberg. *The Small-World Phenomenon: An Algorithmic Perspective.* STOC, 2000.
- **[SOTA]** L. Prokhorenkova, A. Shekhovtsov. *Graph-based Nearest Neighbor Search: From Practice to Theory.* ICML, 2020.
- **[Foundational]** R. Krauthgamer, J. R. Lee. *Navigating Nets: Simple Algorithms for Proximity Search.* SODA, 2004.
- **[SOTA]** S. J. Subramanya, F. Devvrit, et al. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019.
- **[Foundational]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
