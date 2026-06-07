---
id: 31-time-series-db/subsequence-distance-indexing
title: "Indexing for distance-based subsequence queries"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Indexing for distance-based subsequence queries

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/subsequence-distance-indexing` · **Status:** partially-solved

## 1. Problem Statement

Build an index over a (very long or massive collection of) time series so that, given a query $Q$ of length $m$ and threshold $\epsilon$ (or $k$), the engine returns:
- **$\epsilon$-range:** all subsequences $T_{i:i+m}$ with $\mathrm{dist}(Q,T_{i:i+m}) \le \epsilon$, or
- **kNN:** the $k$ closest subsequences,

under **elastic** distances (constrained DTW, ERP, EDR, LCSS) or $L_p$, faster than full scan, ideally with bounded false dismissals (exact via lower-bounding) or quantified recall (approximate).

Variants: fixed-length vs. **variable-length** queries; in-memory vs. **on-disk** (I/O-bound); single series (sliding window) vs. catalog of $N$ series; exact (no false dismissals) vs. $(1+\delta)$-approximate. The hard core is the conflict between **arbitrary query length** and a precomputed index granularity.

## 2. Mathematical Foundations

A length-$m$ window is a point $T_{i:i+m}\in\mathbb{R}^m$. After **z-normalization** $\hat{x} = (x-\mu)/\sigma$, Euclidean distance relates to Pearson correlation, so windows live on a sphere. The classic pipeline (Faloutsos–Ranganathan–Manolopoulos, **GEMINI**, SIGMOD 1994) requires a **lower-bounding** feature map $f$ with the *contractive* property
$$\|f(Q)-f(S)\| \le \mathrm{dist}(Q,S),$$
guaranteeing **no false dismissals**: index $f(\cdot)$ in a spatial structure (R-tree, M-tree, iSAX trie) and post-filter. DTW lower bounds use the **envelope** $U_i=\max_{|j-i|\le w} q_j$, $L_i=\min$, with $LB\_Keogh(Q,S)=\sum_i (s_i-U_i)^2_{+} + (L_i-s_i)^2_{+}$.

Dimensionality reduction maps: **PAA** (piecewise aggregate approx, contractive under scaling), **SAX/iSAX** (symbolic, multi-resolution prefixes), DFT/DWT coefficients (Parseval ⇒ contractive on a coefficient prefix). Indexability is bounded by the **curse of dimensionality**: for high intrinsic dimension, metric/spatial indices degrade to scan (Weber–Schek–Blott VA-file argument; Beyer et al. on NN meaningfulness).

## 3. State of the Art (SOTA)

- **iSAX family (Palpanas group):** iSAX (Shieh–Keogh, KDD 2008), **iSAX2.0** (bulk loading), **ADS+** (adaptive, query-driven index building), **Coconut** (sortable, contiguous), **ULISSE** (single index for *variable-length* queries), **DPiSAX** (distributed), **MESSI/SING/Hercules** (in-memory, SIMD, GPU). This is the dominant exact data-series indexing line.
- **Tree/metric indices:** TS-tree, M-tree variants, and **KV-match / UCR-style** lower-bound cascades for range queries.
- **Approximate:** mapping fixed windows to vectors and using **HNSW** (Malkov–Yashunin) or quantization for high-recall kNN.

## 4. Upper Bound

- **Euclidean range/kNN with PAA/SAX + spatial index:** sublinear *expected* I/O with no false dismissals; worst case degrades to $O(n)$ scan under high intrinsic dimension.
- **Variable-length exact (ULISSE):** a single index answering any $m$ in a range with one structure, near-linear build, sub-scan query in practice.
- **Approximate kNN:** $O(n^{\rho})$-style query for vectorized fixed-length windows (LSH/graph), recall tunable; no elastic-distance analogue with proven bound.

## 5. Lower Bound

- **Intrinsic-dimension / VA-file bound:** for windows of high effective dimension, any feature-based index must examine $\Omega(N)$ candidates in the worst case (Weber–Schek–Blott, VLDB 1998); contractive lower bounds cannot prune incompressible data.
- **Elastic-distance exactness:** because DTW/Edit lack a metric and exact pairwise eval is **SETH-hard** to subquadratic (Bringmann–Künnemann, FOCS 2015), an exact index cannot push hardness below the pairwise floor for adversarial inputs.
- **Cell-probe ANN:** space–time lower bounds for $(c,r)$-NN (Andoni–Laarhoven–Razenshteyn–Waingarten) bound any vectorized-window approach.

## 6. The Gap

For low-intrinsic-dimension Euclidean data the gap is small: iSAX-family indices give strong empirical sublinearity with exactness. The open gap is **(a)** an index with *provable* sublinear query for elastic distances with bounded recall, and **(b)** a unified structure handling **arbitrary query length** without rebuild and with worst-case guarantees. No index simultaneously beats the VA-file lower bound on high-dimension data and supports DTW exactly.

## 7. Current Research (as of June 2026)

- **Learned indices for series** (replacing SAX symbolic boundaries with learned partitions) and GPU/SIMD iSAX (Hercules, MESSI line; Palpanas, LIPADE Paris) *(frontier — verify)*.
- Progressive / approximate-with-guarantees query answering (return answers with shrinking error bars as scan proceeds).
- Lower-bound design for DTW with learned envelopes; benchmarking via the **dsbench / data-series** suites.

## 8. Future Work

- Provable-recall elastic-distance indices; tight VA-file-style lower bounds for kNN under DTW.
- Single-index variable-length kNN with worst-case bounds.
- Update-friendly (streaming insert/delete) data-series indices with maintained guarantees.

## 9. Key References

- **[Foundational]** C. Faloutsos, M. Ranganathan, Y. Manolopoulos. *Fast Subsequence Matching in Time-Series Databases (GEMINI).* SIGMOD, 1994. — [DOI](https://doi.org/10.1145/191839.191925)
- **[Foundational]** J. Shieh, E. Keogh. *iSAX: Indexing and Mining Terabyte Sized Time Series.* KDD, 2008. — [DOI](https://doi.org/10.1145/1401890.1401966)
- **[SOTA]** K. Zoumpatianos, S. Idreos, T. Palpanas. *ADS: the Adaptive Data Series Index.* VLDB Journal, 2016. — [DOI](https://doi.org/10.1007/s00778-016-0442-5)
- **[SOTA]** M. Linardi, T. Palpanas. *ULISSE: ULtra Compact Index for Variable-Length Similarity Search.* ICDE, 2018 / VLDBJ. — [IEEE](https://ieeexplore.ieee.org/document/8509370) — [DOI](https://doi.org/10.1109/ICDE.2018.00164)
- **[Foundational]** R. Weber, H.-J. Schek, S. Blott. *A Quantitative Analysis and Performance Study for Similarity-Search Methods in High-Dimensional Spaces.* VLDB, 1998. — [DBLP](https://dblp.org/rec/conf/vldb/WeberSB98.html)
- **[Survey]** T. Palpanas, V. Beckmann. *Report on Data Series Management.* SIGMOD Record, 2019. — [DBLP search](https://dblp.org/search?q=Palpanas+Beckmann+data+series+management+2019)

## 10. Worked Example

Query $Q=[1,2,4,3]$ ($m=4$), threshold $\epsilon=1.5$ (Euclidean). Use **PAA** with 2 segments: average consecutive pairs, $f(Q)=[\tfrac{1+2}{2},\tfrac{4+3}{2}]=[1.5,3.5]$.

Candidate window $S_1=[1,2,3,4]$: $f(S_1)=[1.5,3.5]$. The PAA lower bound (scaled by $\sqrt{m/\text{segs}}=\sqrt 2$) is
$$LB=\sqrt 2\,\|f(Q)-f(S_1)\| = \sqrt 2\cdot 0 = 0 \le \epsilon,$$
so $S_1$ is **not pruned** — compute the true distance $\|Q-S_1\| = \sqrt{0+0+1+1}=\sqrt2\approx1.41\le1.5$: a **hit**.

Candidate $S_2=[5,6,5,6]$: $f(S_2)=[5.5,5.5]$, $LB=\sqrt2\,\sqrt{4^2+2^2}=\sqrt2\cdot\sqrt{20}\approx6.32 > 1.5$. Because PAA is **contractive** ($LB\le$ true distance), $S_2$ can be **safely discarded without** computing its full distance — no false dismissal. The index scans only the un-pruned candidates, here cutting the exact-distance evaluations in half on this tiny set, the GEMINI filter-and-refine principle in action.

---
*Part of the [DBMS Research catalog](../../README.md).*
