---
id: 28-vector-similarity-search/filtered-ann-selectivity
title: "Filtered ANN with predicate selectivity guarantees"
topic: 28-vector-similarity-search
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-07
last_substantive_update: 2026-07
stale_since: ""
provenance: synthesized
---

# Filtered ANN with predicate selectivity guarantees

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/filtered-ann-selectivity` · **Status:** empirically-open

## 1. Problem Statement
Production vector search rarely runs unconstrained: a query asks for the $k$ nearest vectors **among those satisfying an attribute predicate** $P$ (e.g., `category = 'shoes' AND price < 100 AND lang = 'en'`). The predicate's **selectivity** $s = |\{x : P(x)\}|/n$ ranges from near-1 (almost everything passes) to near-0 (a handful pass). The problem: design index structures and query algorithms that maintain target **recall** and **latency simultaneously across the entire selectivity spectrum**, ideally with provable guarantees rather than per-regime heuristics.

Variants:
- **Pre-filter:** compute the eligible set, then ANN within it (great at low $s$, wasteful/incomplete at high $s$).
- **Post-filter:** run ANN, then discard violators (great at high $s$, recall collapses at low $s$ — the candidate list may contain zero eligible points).
- **In-filter (single-stage):** traverse a structure that respects $P$ during search.
- **Decision / optimization:** given $(P, k, \rho)$, can a single index meet recall $\rho$ and latency $T$ for all $s$?

## 2. Mathematical Foundations
Let the index be a graph $G$ (HNSW/Vamana) or partition (IVF). Predicate $P$ induces a subset $X_P$. The difficulty: $G$'s navigability is a global property; restricting to $X_P$ can **disconnect** the induced subgraph, so greedy search may fail to reach the true filtered NN even when it exists.

- **Graph connectivity under deletion.** $X_P$ is a vertex subset; the induced subgraph $G[X_P]$ must remain navigable. For random $s$-fraction subsets, $G[X_P]$ stays connected only if degree $M \gtrsim \log n / s$ (a percolation-style threshold), which fails for small $s$.
- **Selectivity estimation** mirrors classical query optimization (Selinger et al. 1979): the optimizer must estimate $s$ to choose pre/post/in-filter — an integration of cardinality estimation with ANN cost models.
- **Combinatorial structure.** Arbitrary boolean predicates over many attributes are like multi-dimensional range/containment search; building one index per predicate is infeasible, so structures must support *ad hoc* $P$.
- **Specialized graphs.** Filtered-DiskANN augments edges with label sets so that for each label there exists a navigable monotonic sub-path — an attempt at per-label monotonicity.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Filtered-DiskANN** (Gollapudi et al., WWW 2023) and **Stitched/StreamingDiskANN** build label-aware graphs guaranteeing connectivity per label. **ACORN** (Patel et al., SIGMOD 2024) constructs a predicate-agnostic graph supporting arbitrary boolean predicates via denser construction + predicate-aware traversal. Industrial systems (Milvus, Weaviate, Qdrant, pgvector + filters) implement pre/post/in-filter with cost-based selection. **NHQ**, **CAPS**, and partitioned-by-attribute IVF variants target specific selectivity regimes.
- **Theory-SOTA:** essentially none with end-to-end recall/latency guarantees across all $s$. The label-navigability invariant in Filtered-DiskANN is the closest to a structural guarantee, but recall–latency bounds remain empirical.

## 4. Upper Bound
No clean theoretical upper bound spans all selectivities. Practically: ACORN-style predicate-agnostic graphs achieve near-unfiltered QPS at high-to-moderate $s$ by traversing with on-the-fly predicate checks and an expanded neighbor frontier (degree blow-up $\sim 1/s_{\min}$ to preserve connectivity), giving an upper bound of roughly $O(M/s \cdot \log n)$ distance evaluations under their construction. Filtered-DiskANN gives per-label search at cost comparable to unfiltered DiskANN when labels are known at build time. These are empirical/heuristic bounds, not proven worst-case.

## 5. Lower Bound
- **Connectivity barrier (info/structural):** for an index of degree $M$, an adversarial low-selectivity predicate can isolate true neighbors, forcing either $\Omega(1/s)$ degree (memory) or near-linear scan over $X_P$ — a tradeoff lower bound analogous to the recall–memory frontier.
- **Reduction to range search:** supporting arbitrary conjunctive predicates with sublinear guarantees inherits hardness of multidimensional range searching; cell-probe lower bounds for orthogonal range search (e.g., Pătraşcu) suggest no single compact structure answers all predicate+ANN queries in polylog without space blow-up.
- No tight, ANN-specific lower bound coupling selectivity, recall, latency, and memory has been proven — hence **empirically-open**.

## 6. The Gap
Systems handle the *ends* of the selectivity spectrum well (pre-filter at low $s$, post-filter at high $s$) but the **middle regime** and **adversarial low-selectivity correlated predicates** cause recall or latency cliffs. The gap is between (a) heuristics with strong benchmark numbers but no guarantees and (b) the absence of any structure provably uniform across $s$. Closing it needs either a structural index with a proven per-predicate navigability+recall bound, or a lower bound establishing that uniform performance is impossible without $\Omega(1/s)$ resource cost.

## 7. Current Research (as of June 2026)
Active: predicate-agnostic graph construction (ACORN line) and label-aware graphs (Filtered/Streaming-DiskANN, Microsoft Research, Indyk/Gollapudi collaborators); cost-based filter strategy selection inside vector DBs (Milvus, Weaviate engineering). Emerging: range-filter ANN over numeric attributes via segment-tree / hierarchical partition indexes (e.g., "iRangeGraph", SeRF-style window filters) *(frontier — verify)*; benchmarks with controlled selectivity sweeps becoming standard *(frontier — verify)*. Joint learned cardinality estimation + ANN cost models is an open systems direction. A **phase-transition account** of strategy selection frames selectivity as an order parameter (pre/post/in-filter = phases) and shows estimation error causes plan regret only in *critical regions* near phase boundaries: the in-filter connectivity cliff is a site-percolation transition at $s_c\approx0.83/M$ (degree-set, $n$-independent), criticality requires a constrained budget $B<\sqrt{kn}$, and the regret wedge obeys a finite-size-scaling collapse across two decades of $n$ (validated on SIFT1M). Modest-conceptual delta — strategy selection itself is prior art (Gan–Wang; AlloyDB adaptive filtering; Vespa) (Samyama, arXiv:2606.16341) *(frontier — verify)*.

## 8. Future Work
- A single index with provable recall/latency uniform over selectivity.
- Lower bounds quantifying the unavoidable cost of arbitrary boolean predicates.
- Optimal pre/post/in-filter strategy selection with cardinality-estimation error bounds.
- Range-predicate (numeric window) ANN with logarithmic overhead.

## 9. Key References
- **[SOTA]** S. Gollapudi, N. Karia, V. Sivashankar, et al. *Filtered-DiskANN: Graph Algorithms for Approximate Nearest Neighbor Search with Filters.* WWW, 2023. — [DOI](https://doi.org/10.1145/3543507.3583552)
- **[SOTA]** L. Patel, P. Kraft, C. Guestrin, M. Zaharia. *ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data.* SIGMOD, 2024. — [DOI](https://doi.org/10.1145/3654923) · [arXiv](https://arxiv.org/abs/2403.04871)
- **[Foundational]** P. Selinger, M. Astrahan, D. Chamberlin, R. Lorie, T. Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** S. J. Subramanya, et al. *DiskANN.* NeurIPS, 2019. — [DBLP](https://dblp.org/rec/conf/nips/SubramanyaDSKK19.html)
- **[Systems]** J. Wang, et al. *Milvus: A Purpose-Built Vector Data Management System.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3457550)
- **[SOTA]** C. Zuo, M. Qiao, W. Zhou, F. Li, D. Deng. *SeRF: Segment Graph for Range-Filtering Approximate Nearest Neighbor Search.* SIGMOD, 2024. — [DOI](https://doi.org/10.1145/3639324)
- **[SOTA]** Samyama Research. *Filtered ANN as a Phase Transition: When Selectivity-Estimation Error Causes Plan Regret.* arXiv:2606.16341 (cs.DB), 2026. — [arXiv](https://arxiv.org/abs/2606.16341) · [code](https://github.com/samyama-ai/filtered-ann-regret)

## 10. Worked Example

**Post-filter recall collapse at low selectivity.** Index $n=10{,}000$ product vectors. The query's true 10 nearest neighbors by vector distance are *all* `category='shoes'`, but only $s=0.5\%$ of the corpus is shoes (50 items), scattered through the distance ranking.

*Post-filter* runs unfiltered ANN with a candidate list of $K=200$, then drops violators. Suppose shoes occur uniformly at rate $s$. The expected number of eligible items in the top-$K$ is $K\cdot s = 200 \times 0.005 = 1$. So on average the post-filter returns **1** result where $k=10$ were requested — recall@10 $\approx 0.1$, a cliff. To recover recall you'd need $K \gtrsim k/s = 10/0.005 = 2000$ candidates, blowing up latency.

*Pre-filter* instead materializes the 50 shoe vectors and brute-forces them: 50 distance evals, exact, fast. Here pre-filter wins decisively.

Now flip to $s=0.95$ (almost everything passes): pre-filter materializes 9500 vectors (wasteful), while post-filter's top-$K$ already contains $\approx 0.95K$ eligible items, so post-filter wins. The crossover near the percolation threshold $M \gtrsim \log n / s$ (§2) is exactly the **middle regime** where neither strategy is safe and a single uniform index is still open.

---
*Part of the [DBMS Research catalog](../../README.md).*
