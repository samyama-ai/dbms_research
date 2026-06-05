# Provable diversity-aware nearest neighbors

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/diverse-nearest-neighbors` · **Status:** open

## 1. Problem Statement

Given a dataset $P \subseteq \mathbb{R}^d$ of $n$ points, a query $q$, a metric $\rho$, and an output size $k$, return a set $S \subseteq P$, $|S| = k$, that is simultaneously *relevant* (points close to $q$) and *diverse* (points spread out from one another). The canonical objective combines a query-relevance term with an inter-point dissimilarity term, e.g. maximize

$$f(S) = \lambda \sum_{p \in S} \mathrm{sim}(q,p) + (1-\lambda)\,\mathrm{div}(S),$$

where $\mathrm{div}(S)$ is the sum of pairwise distances, the minimum pairwise distance (Max-Min Diversification), or a determinantal volume (DPP). The **optimization variant** seeks an approximately optimal $S$; the **decision variant** asks whether $f(S) \ge \tau$ is achievable; the **counting variant** asks how many points lie within radius $r$ that form a diverse cover. The hard constraint is **sublinear** query time (no full scan) *together with* a provable approximation ratio on diversity — most deployed re-ranking heuristics give neither.

## 2. Mathematical Foundations

Diversity objectives split into two regimes. **Submodular monotone** objectives (e.g. facility-location-style coverage, DPP log-likelihood is log-submodular) admit a $(1-1/e)$ greedy guarantee under cardinality constraints (Nemhauser–Wolsey–Fisher). **Dispersion / Max-Min** objectives ($\max_S \min_{p\neq p' \in S}\rho(p,p')$) are NP-hard but admit a $2$-approximation via the Gonzalez farthest-point heuristic. **Determinantal Point Processes** model diversity through $\Pr(S) \propto \det(L_S)$, where $L$ is a PSD kernel; MAP inference is NP-hard but log-submodular, giving constant-factor greedy. The tension is geometric: sublinear NN structures (LSH, graph indices, tree covers) prune by *proximity*, while diversity demands points be *far apart*, so the index must support combined locality-and-dispersion queries — a problem touching $\varepsilon$-nets, coresets, and the doubling dimension $\dim_{\mathrm{KR}}$.

## 3. State of the Art (SOTA)

- **Theory:** Coreset / $\varepsilon$-net constructions for $k$-dispersion give $(2+\varepsilon)$ guarantees but with construction time depending on $n$; not query-time sublinear.
- **Systems:** *MMR* (Maximal Marginal Relevance, Carbonell–Goldstein 1998) is the deployed baseline — greedy, no sublinear guarantee. Diverse retrieval layered on **HNSW**/**DiskANN** via over-fetch-then-rerank (fetch $K \gg k$, run MMR/DPP on $K$) is standard in production RAG stacks (2023–2025) but loses guarantees because diversity is computed only on the retrieved candidate pool.
- **DPP-on-ANN:** Fast greedy MAP (Chen et al., NeurIPS 2018) makes DPP re-ranking practical at $O(K^2 k)$ over the candidate pool.

## 4. Upper Bound

For the candidate-pool model, greedy Max-Min gives a $2$-approximation in $O(Kk)$ time after an ANN over-fetch of $K$ points; DPP-MAP greedy gives $(1-1/e)$ for the log-submodular objective. For the *true* sublinear setting, $\varepsilon$-net diversification yields $(2+\varepsilon)$-approximate $k$-dispersion among the $r$-neighborhood with query time $\tilde O(\rho^{O(d)} + k^2)$ in doubling dimension $d$ — exponential in dimension, so only meaningful for low intrinsic dimension.

## 5. Lower Bound

Max-dispersion (remote-clique) is NP-hard and **inapproximable beyond $2$** in general metrics unless P=NP (Ravi–Rosenkrantz–Tayi); the Max-Min variant matches the Gonzalez $2$-bound tightly. Exact MAP-DPP is NP-hard (Ko–Lee–Queyranne / Çivril–Magdon-Ismail for max-volume subset selection, which is even hard to approximate to $c^k$). For the *sublinear-query* requirement, no nontrivial cell-probe or fine-grained lower bound specific to diversity-constrained NN is known; the relevant barrier is inherited from approximate NN itself (hardness of $c$-ANN under SETH-style reductions for $c$ close to 1, Rubinstein 2018).

## 6. The Gap

Closed in the candidate-pool model (matching $2$ / $(1-1/e)$ bounds). **Genuinely open** in the truly-sublinear model: there is no index that returns diversity-guaranteed top-$k$ in time sublinear in $n$ *and* polynomial in $d$. The over-fetch heuristic has no bound relating pool-diversity to global-diversity — adversarial datasets make any fixed $K$ arbitrarily bad. Closing it requires either a diversity-aware index primitive (proximity-and-dispersion in one structure) or a reduction proving the over-fetch gap is inherent.

## 7. Current Research (as of June 2026)

Active directions: (i) diversity-aware graph indices that bias HNSW edge selection toward angular/spatial spread *(frontier — verify)*; (ii) coreset-based streaming diversification with relevance constraints; (iii) submodular maximization over ANN candidate sets with data-dependent pool-size bounds. Groups at CMU, MIT, and IT University of Copenhagen (Pagh) work on LSH-with-fairness/diversity; the "fair near-neighbor" line (Aumüller, Pagh, Silvestri) is closely related and partially transferable.

## 8. Future Work

- An index supporting $(r, k)$-dispersion queries with $\mathrm{poly}(d)\cdot n^{o(1)}$ query time.
- Instance-optimal over-fetch: provable $K$ as a function of local intrinsic dimension.
- Unifying fairness-constrained and diversity-constrained NN under one combinatorial framework.
- Lower bounds tailored to diversity-constrained ANN (distinct from plain ANN).

## 9. Key References

- **[Foundational]** Carbonell, J., Goldstein, J. *The Use of MMR, Diversity-Based Reranking for Reordering Documents.* SIGIR, 1998.
- **[Foundational]** Ravi, S. S., Rosenkrantz, D. J., Tayi, G. K. *Heuristic and Special Case Algorithms for Dispersion Problems.* Operations Research, 1994.
- **[SOTA]** Chen, L., Zhang, G., Zhou, E. *Fast Greedy MAP Inference for Determinantal Point Process.* NeurIPS, 2018.
- **[SOTA]** Aumüller, M., Pagh, R., Silvestri, F. *Fair Near Neighbor Search via Sampling.* ICDT / SIGMOD Record, 2021–2022.
- **[Survey]** Kulesza, A., Taskar, B. *Determinantal Point Processes for Machine Learning.* Foundations and Trends in ML, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
