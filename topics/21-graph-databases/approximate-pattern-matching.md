# Approximate and sampled pattern matching

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/approximate-pattern-matching` · **Status:** open
> **Verification note:** Wander Join (SIGMOD 2016) authors are Li, Wu, Yi, Zhao (corrected in §9 from a mis-cited "Li, Wu, Das, Haritsa").

## 1. Problem Statement
Given a massive graph $G=(V,E)$ (billions of edges, often not fitting in memory) and a small connected pattern $H$ (e.g., triangle, 4-clique, $k$-path, labeled motif), estimate the number of (homomorphic or subgraph) **embeddings** $\mathrm{hom}(H,G)$ / $\mathrm{sub}(H,G)$, or an aggregate over them (e.g., $\sum_{\text{matches}} f(\text{attributes})$), to within relative error $\varepsilon$ with confidence $1-\delta$, using as few edge reads / passes / samples as possible.

Variants:
- **Counting variant:** estimate $\\#$ embeddings (the canonical case).
- **Aggregate variant:** estimate $\mathrm{SUM/AVG/COUNT-DISTINCT}$ of an attribute function over matches (graph-OLAP).
- **Existence/decision variant:** does at least one match exist? (subsumed but easier).
- **Streaming / sublinear variant:** one or few passes, or sublinear-time query access (degree, neighbor, edge-sample oracles).
The challenge is **variance control**: embedding counts are heavy-tailed, so naive uniform sampling has variance that can be exponentially larger than the mean.

## 2. Mathematical Foundations
The estimator backbone is **Horvitz–Thompson**: if each candidate match $m$ is sampled with probability $p_m$, then $\hat{X}=\sum_{m\in S} f(m)/p_m$ is unbiased. Variance is governed by second-moment / clustering structure; concentration follows from Chebyshev (bounded variance) or Bernstein/Chernoff (bounded summands).

Two pillars give *provable* guarantees:
- **Color coding** (Alon–Yuster–Zwick 1995): randomly color $V$ with $k=|V(H)|$ colors; count *colorful* copies (no two vertices share a color) via DP in $O(2^k \cdot \mathrm{poly})$; a colorful copy appears with probability $k!/k^k\approx e^{-k}$, yielding an unbiased estimator after rescaling. Modern sampling-from-the-DP-table variants give $\varepsilon,\delta$ approximations.
- **Adaptive / WanderJoin-style random walks** with Horvitz–Thompson weighting along a join order; variance tied to the AGM/degree structure.

Lower-bound machinery: communication complexity (set-disjointness) for streaming space; the conjectured hardness of detecting $k$-cliques; and **VC dimension / discrepancy** to bound sample size for *uniform* relative-error guarantees over a query class. For triangles, the seminal result: $\tilde{O}(m^{3/2}/t)$ queries suffice (and are necessary) to $\varepsilon$-estimate the triangle count $t$ in the query-access model (Eden–Levi–Ron–Seshadhri, FOCS 2015).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** sublinear-time estimators for triangles (Eden et al. FOCS 2015), arbitrary $k$-cliques and general subgraphs (Eden–Ron–Seshadhri; Assadi–Kapralov–Khanna ITCS 2019 "arboricity" framework) achieving query complexity parameterized by edges, arboricity, and the target count.
- **Systems-SOTA:** WanderJoin (Li–Wu–Yi–Zhao, SIGMOD 2016) for online aggregation joins; Arya/EmptyHeaded-style worst-case-optimal exact counting for moderate graphs; sampling subgraph counters such as **MOTIVO** (Bressan–Leucci–Panconesi, color-coding + succinct sampling, KDD/VLDB 2019) and the GPU/streaming triangle/butterfly counters; **graphlet** estimators (PGD, ESCAPE — Pinar–Seshadhri–Vishal, WWW 2017, exact via orbit equations up to 5-vertex). For aggregates, sampling-based AQP engines extended to property graphs.

## 4. Upper Bound
- Triangles: $\tilde{O}\!\left(\frac{n}{t^{1/3}}+\frac{m^{3/2}}{t}\right)$ queries for an $(\varepsilon,\delta)$-estimate (Eden–Levi–Ron–Seshadhri 2015), in the adjacency-list query model.
- General $k$-subgraphs: color-coding gives $2^{O(k)}\cdot \mathrm{poly}(n)$ time for an FPTRAS in the count parameter; MOTIVO scales to $k\le 8{-}9$ on billion-edge graphs.
- Streaming: triangle count in $\tilde{O}(m/\sqrt{t})$ space (one pass, with guarantees) — Pavan–Tangwongsan–Tirthapura–Wu, and McGregor et al.

## 5. Lower Bound
- $\\#$-counting subgraph homomorphisms is **$\\#W[1]$-hard** parameterized by $|H|$ in general, and $\\#P$-complete for many fixed $H$ (e.g., counting $k$-paths/cycles).
- Query/sample complexity lower bounds: $\Omega(m^{3/2}/t)$ for triangle estimation (matching, FOCS 2015); $\Omega(n^2)$-type bounds without a good lower estimate of $t$.
- Streaming space: $\Omega(m)$ for exact triangle detection (set-disjointness reduction); $k$-clique detection conditioned on the *triangle/clique-detection* fine-grained hypotheses.
- Hardness of **fixed-parameter tractability** is tied to the *vertex-cover number* of $H$ (Curticapean–Marx; Curticapean–Dell–Marx STOC 2017 "homomorphism basis"): counting $H$ is hard exactly when treewidth/vc grows.

## 6. The Gap
For triangles the query-complexity bound is **closed** (tight up to logs). The open gaps: (a) tight sample complexity for general $H$ as a function of arboricity *and* the homomorphism-basis structure; (b) **variance-optimal** practical estimators for $k\ge 6$ that match information-theoretic limits; (c) guaranteed-error estimators for *attribute aggregates* (not just counts) and for *labeled/typed* patterns; (d) closing the gap between worst-case-optimal exact counting and sampling for skewed real graphs.

## 7. Current Research (as of June 2026)
Color-coding + succinct sampling continues to be pushed past 8-node motifs and onto GPUs/distributed settings *(frontier — verify)*. The homomorphism-basis view (Curticapean, Dell, Marx; Seshadhri) is being turned into *practical* estimators that decompose any pattern count into easier basis counts. Active groups: Seshadhri (UCSC), Bressan/Panconesi (Sapienza), Eden (UT Austin/Boston), Assadi (Waterloo) on sublinear/streaming; Haritsa (IISc) and Re (Stanford) bridging to query optimizers. Differentially-private subgraph counting and learned cardinality estimators that emit *calibrated* error bars are an emerging frontier *(frontier — verify)*.

## 8. Future Work
- Unified sample-complexity theory parameterized jointly by arboricity, degeneracy, and homomorphism basis.
- Worst-case-optimal *sampling* (matching AGM) with formal $\varepsilon$-guarantees.
- Guaranteed-error aggregate (SUM/quantile) estimators over matches; distinct-counting of matches.
- Anytime estimators with shrinking, certified confidence intervals usable inside an optimizer's cardinality module.

## 9. Key References
- **[Foundational]** Alon, Yuster, Zwick. *Color-Coding.* J. ACM, 1995. — [DOI](https://doi.org/10.1145/210332.210337)
- **[Foundational]** Eden, Levi, Ron, Seshadhri. *Approximately Counting Triangles in Sublinear Time.* FOCS, 2015. — [arXiv](https://arxiv.org/abs/1504.00954)
- **[SOTA]** Bressan, Leucci, Panconesi. *Motivo: Fast Motif Counting via Succinct Color Coding and Adaptive Sampling.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1906.01599)
- **[SOTA]** Curticapean, Dell, Marx. *Homomorphisms Are a Good Basis for Counting Small Subgraphs.* STOC, 2017. — [arXiv](https://arxiv.org/abs/1705.01595)
- **[SOTA]** Li, Wu, Yi, Zhao. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[Survey]** Seshadhri, Tirthapura. *Scalable Subgraph Counting: The Methods Behind the Madness.* WWW Tutorial / Foundations, 2019. — [DOI](https://doi.org/10.1145/3308560.3320092)

## 10. Worked Example

**Color-coding for a 3-path.** Suppose we want $\mathrm{hom}(P_3,G)$, the number of homomorphic 3-vertex paths $u\!-\!v\!-\!w$, in a small graph $G$ with $V=\{1,2,3,4\}$ and edges $\{(1,2),(2,3),(3,4),(2,4)\}$.

Color each vertex uniformly with one of $k=3$ colors. A path is *colorful* iff its three vertices get distinct colors; this happens with probability $p = k!/k^k = 6/27 = 2/9 \approx 0.22$. Count colorful 3-paths by a DP over color subsets: for each vertex, track the set of colors usable on a path ending there. Say one trial finds $X=5$ colorful paths. The Horvitz–Thompson estimator rescales:
$$\hat{N} = X / p = 5 / (2/9) = 22.5.$$

To hit relative error $\varepsilon=0.1$ with confidence $1-\delta$, average over $R = O(e^k \log(1/\delta)/\varepsilon^2)$ independent colorings — the $e^k$ factor ($\approx 20$ for $k=3$) is the price of demanding *colorful* witnesses, and is exactly what MOTIVO's biased coloring and adaptive sampling attack so the method scales to $k\le 8$–$9$ on billion-edge graphs. Naive uniform path sampling, by contrast, would have variance dominated by the high-degree hub vertex $2$.

---
*Part of the [DBMS Research catalog](../../README.md).*
