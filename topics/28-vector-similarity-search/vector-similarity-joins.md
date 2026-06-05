# Top-k ANN joins over two vector sets

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/vector-similarity-joins` · **Status:** partially-solved

## 1. Problem Statement
Beyond single-query ANN, many DB workloads need a **similarity join**: given two vector collections $R$ and $S$, compute, for *every* $r\in R$, its top-$k$ nearest neighbors in $S$ (a $k$-NN join), or all pairs within a radius (a range/similarity join). Use cases: entity resolution, near-duplicate detection, embedding-based blocking, recommendation candidate generation, and building a $k$-NN graph ($R=S$). The naive algorithm is $\Theta(|R|\,|S|\,d)$ — quadratic and prohibitive at scale. The problem: **scalable, approximate top-$k$ / radius similarity joins with subquadratic cost and quality guarantees.**

Variants:
- **$k$-NN join (optimization):** $\forall r\in R$ return $\mathrm{top}\text{-}k_{s\in S} \, \mathrm{sim}(r,s)$.
- **Radius/similarity join (counting/enumeration):** output all $(r,s)$ with $\mathrm{dist}(r,s)\le\tau$.
- **Self-join / $k$-NN graph construction:** $R=S$, the building block for graph indexes and clustering.
- **Decision:** does any pair have similarity $\ge\tau$ (closest-pair / threshold existence)?

## 2. Mathematical Foundations
Let $R,S\subset\mathbb{R}^d$, $n=\max(|R|,|S|)$. Distinguish *output-sensitive* (radius join, output size $\mathrm{OUT}$) from *fixed-size* ($k$-NN join, output $k|R|$) regimes.

Key scaffolding:
- **LSH joins.** Locality-sensitive hashing (Indyk–Motwani, STOC 1998; Datar et al. SoCG 2004) buckets points so colliding pairs are likely near; a similarity join scans buckets, costing $\tilde{O}(n^{1+\rho}+\mathrm{OUT})$ for an LSH exponent $\rho<1$ that depends on the approximation factor $c$ — *subquadratic* with provable recall.
- **Set-similarity prefix filtering.** For sparse/set data, prefix/length/positional filters (Xiao et al., WWW 2008; Bayardo et al.) prune candidate pairs exactly and underpin classic similarity-join theory; the dense-vector analogue is LSH/graph-based.
- **Closest pair hardness.** Bichromatic closest pair is the decision core; in high $d$ it is SETH-hard to solve exactly in strongly subquadratic time (Alman–Williams; Rubinstein STOC 2018) — so exact joins are quadratic-hard, justifying approximation.
- **Graph-based joins.** NN-Descent (Dong et al., WWW 2011) builds an approximate $k$-NN graph in empirically $O(n^{1.14})$-ish time by iterative neighbor-of-neighbor refinement — fast but without worst-case guarantees.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** LSH-based similarity joins give $\tilde{O}(n^{1+\rho})$ with $\rho=\rho(c)$ provably $<1$ for approximation factor $c>1$; for the *radius* join, output-sensitive bounds $\tilde{O}(n^{1+\rho}+\mathrm{OUT})$. These are the cleanest provable subquadratic results — hence "partially-solved": approximate joins have guarantees, exact dense joins do not.
- **Systems-SOTA:** GPU brute-force $k$-NN join (FAISS) is the throughput baseline at moderate scale; NN-Descent / EFANNA and DiskANN-style construction build approximate $k$-NN graphs at billion scale; distributed similarity joins on Spark/MapReduce (e.g., partition-and-replicate with LSH) handle out-of-core $R,S$. Vector DBs increasingly expose batch/"join" search APIs.

## 4. Upper Bound
LSH similarity join: $\tilde{O}\!\big(n^{1+\rho}+\mathrm{OUT}\big)$ time, $\tilde{O}(n^{1+\rho})$ space, for $c$-approximate radius join in the LSH/RAM model, with $\rho=1/c^2$ for Euclidean (Andoni–Indyk) and the data-dependent improvement to $\rho=1/(2c^2-1)$ (Andoni–Razenshteyn, STOC 2015). For the $k$-NN join, running each query through a shared index gives $\tilde{O}(n^{1+\rho})$. Graph-based NN-Descent is faster in practice ($\approx n^{1.1}$) but has no proven worst-case bound.

## 5. Lower Bound
- **Fine-grained / SETH:** exact bichromatic closest pair (hence exact $k$-NN join) requires $n^{2-o(1)}$ time for $d=\omega(\log n)$ unless SETH fails (Rubinstein, STOC 2018; Alman–Williams). This rules out strongly subquadratic *exact* dense joins.
- **LSH-side optimality:** the data-dependent LSH exponent $\rho=1/(2c^2-1)$ is *optimal* among LSH schemes (Andoni–Razenshteyn lower bound), pinning the approximate-join upper bound to the LSH barrier.
- **Output sensitivity:** any algorithm must pay $\Omega(\mathrm{OUT})$ to enumerate a radius join — a trivial but binding lower bound when the result is dense.

## 6. The Gap
Partially closed. For *approximate* joins, LSH upper bounds meet LSH lower bounds (gap closed *within the LSH model*); whether a non-LSH method beats $\rho=1/(2c^2-1)$ for joins is open, mirroring single-query ANN. For *exact* dense joins, SETH makes subquadratic impossible — gap closed negatively. The live gap is between *provable* LSH-join exponents and the much faster *empirical* graph-based joins (NN-Descent), which lack guarantees: can one prove NN-Descent-class running times under an intrinsic-dimension model?

## 7. Current Research (as of June 2026)
Active directions: GPU- and disk-resident batch $k$-NN-graph construction at billion scale (DiskANN/CAGRA build pipelines) *(frontier — verify)*; distributed/streaming similarity joins integrated into vector DBs and lakehouse engines; output-sensitive approximate joins with tighter recall–cost tradeoffs; and analyses aiming to give NN-Descent worst-case or distributional guarantees *(frontier — verify)*. Contributors: theory groups around Andoni/Razenshteyn-lineage LSH joins, the NN-Descent/graph-build community, and FAISS/cuVS engineering teams.

## 8. Future Work
- Provable running-time bounds for graph-based ($k$-NN-graph) joins under realistic data models.
- Output-sensitive approximate radius joins matching $\Omega(\mathrm{OUT})$ with small additive overhead.
- I/O- and communication-optimal distributed similarity joins (massively-parallel / MPC model).
- Joins under learned / non-metric similarities (ties to cross-modal ANN).

## 9. Key References
- **[Foundational]** P. Indyk, R. Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC, 1998. — [DOI](https://doi.org/10.1145/276698.276876)
- **[Foundational]** W. Dong, M. Charikar, K. Li. *Efficient k-Nearest Neighbor Graph Construction for Generic Similarity Measures (NN-Descent).* WWW, 2011. — [DOI](https://doi.org/10.1145/1963405.1963487)
- **[SOTA]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[Foundational]** A. Rubinstein. *Hardness of Approximate Nearest Neighbor Search.* STOC, 2018. — [arXiv](https://arxiv.org/abs/1803.00904)
- **[Foundational]** C. Xiao, W. Wang, X. Lin, J. X. Yu. *Efficient Similarity Joins for Near Duplicate Detection.* WWW, 2008. — [DOI](https://doi.org/10.1145/1367497.1367516)
- **[SOTA]** J. Johnson, M. Douze, H. Jégou. *Billion-scale Similarity Search with GPUs (FAISS).* IEEE Transactions on Big Data, 2021. — [arXiv](https://arxiv.org/abs/1702.08734)

## 10. Worked Example

Top-1 NN join of $R$ into $S$, both in $\mathbb{R}^2$:

$R = \{r_1{=}(0,0),\ r_2{=}(5,5)\}$, $S = \{s_1{=}(1,0),\ s_2{=}(0,2),\ s_3{=}(6,5)\}$.

**Brute force** ($k$-NN join) costs $|R|\,|S| = 2\times3 = 6$ distance evaluations:
- $r_1$: $\|r_1{-}s_1\|{=}1,\ \|r_1{-}s_2\|{=}2,\ \|r_1{-}s_3\|{\approx}7.8 \Rightarrow$ NN $= s_1$.
- $r_2$: $\|r_2{-}s_1\|{\approx}6.4,\ \|r_2{-}s_2\|{\approx}5.8,\ \|r_2{-}s_3\|{=}1 \Rightarrow$ NN $= s_3$.

**LSH-join** instead hashes all five points with a random projection (bucket width $w$). With a grid of width $w=3$, $s_1,s_2,r_1$ fall in cell $(0,0)$ and $s_3,r_2$ in cell $(1,1)$; each $r$ is only compared within its bucket, giving $2 + 1 = 3$ evaluations — half the brute-force work, and it still recovers both true neighbors here.

**Scaling:** at $n = |R| = |S| = 10^6$ and $c = 2$ (Euclidean, $\rho = 1/c^2 = 0.25$), brute force is $n^2 = 10^{12}$ ops, while the LSH join is $\tilde O(n^{1+\rho}) = 10^{7.5} \approx 3.2\times10^7$ — a $\sim 30{,}000\times$ reduction, the subquadratic win the problem targets. Exact dense joins, by Rubinstein/SETH, cannot beat $n^{2-o(1)}$.

---
*Part of the [DBMS Research catalog](../../README.md).*
