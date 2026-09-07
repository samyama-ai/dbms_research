---
id: 28-vector-similarity-search/range-similarity-search
title: "Range and threshold similarity search"
topic: 28-vector-similarity-search
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Range and threshold similarity search

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/range-similarity-search` · **Status:** partially-solved

## 1. Problem Statement

Given $P \subseteq \mathbb{R}^d$, a query $q$, a metric $\rho$, and a radius $r$, **range similarity search** returns *all* points within the ball $B(q,r) = \{p \in P : \rho(q,p) \le r\}$. Variants: the **reporting variant** enumerates the answer set; the **counting variant** returns $|B(q,r)|$ without listing it; the **threshold/emptiness variant** decides whether any point lies within $r$; the **approximate** $(r,c)$-variant must report all points within $r$ and may also report points within $cr$, but none beyond. The defining difficulty versus top-$k$ NN is that the **output size $|B(q,r)|$ is unbounded and query-dependent** — it can range from $0$ to $n$. The goal is an index with query cost that is *output-sensitive*, ideally $\tilde O(n^{\rho} + |\mathrm{out}|)$, with bounds on the search overhead **independent of the result-set size**.

## 2. Mathematical Foundations

The core tool is **Locality-Sensitive Hashing**: a family $\mathcal H$ is $(r, cr, p_1, p_2)$-sensitive if $\Pr[h(q)=h(p)] \ge p_1$ when $\rho(q,p)\le r$ and $\le p_2$ when $\rho(q,p) \ge cr$, with $p_1 > p_2$. The exponent $\rho = \frac{\log 1/p_1}{\log 1/p_2}$ governs query time $\tilde O(n^\rho)$ and space $\tilde O(n^{1+\rho})$. For Euclidean/angular metrics, data-independent LSH achieves $\rho = 1/c^2$ (Andoni–Indyk) and data-dependent LSH achieves $\rho = 1/(2c^2-1)$ (Andoni–Razenshteyn 2015), which is optimal among LSH-type schemes. Range search additionally needs **all** in-ball points, so the analysis must control both false negatives (recall on the in-ball set) and the cost of enumerating colliding points — a coupon-collector / output-sensitivity argument over hash buckets. In bounded **doubling dimension**, navigating nets and cover trees give $\rho$-independent $2^{O(\dim)}\log n + |\mathrm{out}|$ reporting.

## 3. State of the Art (SOTA)

- **Theory:** Data-dependent LSH (Andoni–Razenshteyn, STOC 2015) with the LSH-Forest / multi-probe machinery gives near-optimal approximate ball reporting.
- **Systems:** **FAISS** `range_search`, **Milvus**, and **pgvector** expose radius queries; in practice they rely on IVF (inverted file / coarse quantizer) scanning the probed cells, or on graph traversal (HNSW) with a radius stop condition. Graph indices were designed for top-$k$ and are weaker for range queries because the greedy-search termination is recall-tuned for fixed $k$, not for an unbounded ball.
- **Metric-space classics:** VP-trees, M-trees, and cover trees give exact range reporting that is efficient in low intrinsic dimension but degrade to scans in high $d$.

## 4. Upper Bound

For $(r,c)$-approximate ball reporting in $\ell_2$: query time $\tilde O(d\,n^{\rho} + |\mathrm{out}|)$, space $\tilde O(n^{1+\rho})$ with $\rho = 1/(2c^2-1)$ (data-dependent LSH). For counting, $(1\pm\varepsilon)$-approximate ball-size estimation is achievable in $\tilde O(n^\rho/\varepsilon^2)$ via sampling over LSH buckets without materializing the output. In doubling dimension $\lambda$, cover trees give exact reporting in $2^{O(\lambda)}\log n + |\mathrm{out}|$.

## 5. Lower Bound

For exact range reporting in high dimension, the **curse of dimensionality** bites: any structure with $\mathrm{poly}(n,d)$ space requires near-linear query time for exact NN/range under SETH-style and dimensionality reductions (Rubinstein, STOC 2018, for $(1+\varepsilon)$-ANN). For the **counting** variant, conditional hardness from **Hopcroft's problem / Online Matrix-Vector** and from $\\#$-hardness of high-dimensional ball-counting precludes exact $\tilde O(n^{2-\delta})$ batch counting. Cell-probe lower bounds for approximate near-neighbor (Panigrahy–Talwar–Wieder; Andoni–Indyk–Patrascu) lower-bound space-query tradeoffs and transfer to the ball-emptiness variant.

## 6. The Gap

**Approximate** range reporting is essentially solved up to the LSH-optimal $\rho$ — this is why the status is *partially-solved*. The open gaps: (i) **exact** high-dimensional range search has no subquadratic batch algorithm and matching unconditional lower bounds are absent; (ii) reporting cost truly **independent of result-set size** is impossible for reporting (must pay $|\mathrm{out}|$) but the *search overhead* additive term's optimal dependence on $\rho$ and dimension is not tightly pinned; (iii) graph-index range search lacks recall guarantees — an empirical/theoretical gap.

## 7. Current Research (as of June 2026)

Directions: (i) graph indices with provable range-recall via radius-adaptive beam widths *(frontier — verify)*; (ii) GPU-resident range search saturating bandwidth on IVF-PQ cells; (iii) range-filtered ANN combining radius predicates with attribute filters (the "filtered ANN" line, e.g. ACORN, 2024). Pagh's group (Copenhagen) and Razenshteyn's lineage continue LSH-optimality work; the FAISS team (Meta) and Milvus/Zilliz drive systems-side radius search.

## 8. Future Work

- Output-sensitive exact range search beating the curse for structured (low-intrinsic-dimension) data.
- Provable recall for graph-based radius queries.
- Unified cost model jointly covering top-$k$, range, and filtered predicates.
- Streaming / dynamic ball-counting with worst-case update bounds.

## 9. Key References

- **[Foundational]** Indyk, P., Motwani, R. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC, 1998. — [DOI](https://doi.org/10.1145/276698.276876)
- **[SOTA]** Andoni, A., Razenshteyn, I. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[Foundational]** Beygelzimer, A., Kakade, S., Langford, J. *Cover Trees for Nearest Neighbor.* ICML, 2006. — [DOI](https://doi.org/10.1145/1143844.1143857)
- **[Lower bound]** Rubinstein, A. *Hardness of Approximate Nearest Neighbor Search.* STOC, 2018. — [arXiv](https://arxiv.org/abs/1803.00904)
- **[SOTA]** Johnson, J., Douze, M., Jégou, H. *Billion-Scale Similarity Search with GPUs (FAISS).* IEEE Trans. Big Data, 2021. — [arXiv](https://arxiv.org/abs/1702.08734)

## 10. Worked Example

Take $n=6$ points on the line (so $d=1$, $\rho=\ell_2$): $P=\{0.5, 1.0, 2.2, 3.0, 3.1, 7.0\}$, query $q=3.0$, radius $r=0.5$. The ball $B(q,0.5)$ asks for all $p$ with $|p-3.0|\le 0.5$, i.e. $p\in[2.5,3.5]$.

- **Reporting:** scan/probe yields $\{3.0, 3.1\}$ — output size $|\mathrm{out}|=2$.
- **Counting:** return $2$ without listing.
- **Emptiness:** "yes, non-empty" (since $3.0$ itself qualifies).

Now contrast output-sensitivity. Enlarge to $r=2.0$: $B(q,2.0)=[1.0,5.0]$ captures $\{1.0,2.2,3.0,3.1\}$, so $|\mathrm{out}|=4$ — the answer size grew with $r$, unbounded up to $n$. An LSH index aims for query cost $\tilde O(n^{\rho}+|\mathrm{out}|)$: the $n^{\rho}$ term (with $\rho=1/(2c^2-1)$, e.g. $\rho\approx 0.33$ at approximation $c=\sqrt 2$) is the *search overhead* to locate the right buckets, and the additive $|\mathrm{out}|$ is the unavoidable cost of enumerating the answer. For the $(r,c)$-approximate variant with $c=2$, the index must report everything within $r=0.5$ and may also report points up to $cr=1.0$ away (e.g. $2.2$), but never beyond $1.0$.

---
*Part of the [DBMS Research catalog](../../README.md).*
