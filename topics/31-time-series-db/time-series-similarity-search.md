---
id: 31-time-series-db/time-series-similarity-search
title: "Approximate similarity search over series"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Approximate similarity search over series

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/time-series-similarity-search` · **Status:** partially-solved

## 1. Problem Statement

Given a database of $N$ time series (or one long series of length $n$) and a query series $Q$, return the series (or subsequence) most similar to $Q$ under an elastic or $L_p$ distance, in **sublinear** time after preprocessing, with provable approximation/recall guarantees at TSDB scale.

Variants:
- **Whole-series NN:** over $N$ series of equal length $m$, find $\arg\min_i \mathrm{dist}(Q, S_i)$.
- **Subsequence matching:** over one series of length $n$, find the length-$m$ window $T_{i:i+m}$ minimizing $\mathrm{dist}(Q, T_{i:i+m})$ (the *motif/discord/query* setting).
- **$c$-approximate / $(c,r)$-near-neighbor (decision):** report a series within $cr$ if one within $r$ exists.
- **kNN** and **$\epsilon$-range** counting versions.

The distance is typically **DTW** (Dynamic Time Warping), constrained DTW (Sakoe–Chiba band $w$), or Euclidean/$L_p$ on z-normalized windows.

## 2. Mathematical Foundations

For $Q,S \in \mathbb{R}^m$, Euclidean distance is $\|Q-S\|_2$. DTW is the optimal-alignment cost
$$\mathrm{DTW}(Q,S) = \min_{\pi \in \mathcal{A}} \sum_{(i,j)\in\pi} (q_i - s_j)^2,$$
over monotone alignments $\pi$, computable by DP in $O(m^2)$ (or $O(mw)$ banded). DTW is **not a metric** (violates the triangle inequality), which blocks direct use of metric-tree indices and motivates **lower-bounding**: functions $LB(Q,S) \le \mathrm{DTW}(Q,S)$ (Kim, Yi, **Keogh's $LB\_Keogh$** via envelope $U,L$) that prune candidates exactly.

Fundamental hardness: DTW (and Edit Distance / LCSS) admits no truly subquadratic exact algorithm unless **SETH fails** (Bringmann–Künnemann / Abboud–Backurs–Williams, FOCS 2015). So sublinear *exact* search over arbitrary data is implausible; the field targets **approximation** and **data-dependent** structure. For $L_2$, **LSH** gives $(c,r)$-NN in $O(n^{\rho})$ with $\rho = 1/c^2$ (Indyk–Motwani; Andoni–Razenshteyn near-optimal $\rho = 1/(2c^2-1)$).

## 3. State of the Art (SOTA)

- **Systems-SOTA (subsequence):** the **Matrix Profile / STOMP / SCRIMP / STUMPY** line (Keogh & Mueen, ICDM 2016–) computes all-pairs nearest-neighbor distances; **MASS** does $O(n\log n)$ Euclidean subsequence search via FFT. **UCR Suite** (Rakthanmanon et al., KDD 2012) made cascaded-lower-bound DTW search practical at trillion-point scale.
- **Indexing-SOTA:** **iSAX / iSAX2.0 / ADS+ / DPiSAX / Coconut / ULISSE / MESSI / Hercules** (Palpanas group, Paris) — the dominant family of scalable series indices.
- **Approximate-NN-SOTA:** graph indices **HNSW** (Malkov–Yashunin, 2016) and learned/quantization methods on fixed-length embeddings (PAA/SAX, random projections, or learned encoders) when series are mapped to vectors.

## 4. Upper Bound

- **Euclidean subsequence:** $O(n \log n)$ exact via MASS (FFT-based sliding dot products).
- **$(c,r)$-approximate $L_2$ NN:** $O(n^{\rho})$ query, $O(n^{1+\rho})$ space with $\rho \to 1/(2c^2{-}1)$ (Andoni–Razenshteyn, STOC 2015), in the RAM model with random hashing.
- **DTW search:** no sublinear worst-case bound; practical near-linear *expected* pruning via $LB\_Keogh$ cascades. Approximate DTW embeddings give $O(\log n)$-distortion into $\ell_1$ for some regimes, enabling LSH-style search with logarithmic-factor error.

## 5. Lower Bound

- **Exact DTW/Edit similarity:** no $O(m^{2-\epsilon})$ algorithm for a single pair unless **SETH** is false (Bringmann–Künnemann 2015; Abboud–Backurs–Williams 2015). This forbids fast exact whole-database scan-free guarantees in general.
- **ANN (cell-probe):** for $(c,r)$-NN in $\ell_1/\ell_2$, near-tight space–time lower bounds hold (Andoni–Laarhoven–Razenshteyn–Waingarten; Panigrahy–Talwar–Wieder) — e.g. exponent trade-offs that current LSH/graph methods nearly match.
- **DTW embedding:** any embedding of DTW into $\ell_1$ incurs distortion $\Omega(\cdot)$ (no isometric/low-distortion embedding in general), limiting purely metric-index approaches.

## 6. The Gap

For **Euclidean** the gap is essentially closed (near-optimal ANN; $O(n\log n)$ subsequence). For **DTW** it is genuinely open: we have a strong *exact* lower bound (SETH) and good *heuristic* pruning, but **no approximation algorithm with both a provable distortion guarantee and proven sublinear query time on adversarial data**. Closing it means either a low-distortion DTW sketch with matching lower bounds, or a fine-grained hardness result for *approximate* DTW search.

## 7. Current Research (as of June 2026)

- Provable **DTW approximation** via greedy/quadtree alignment achieving $O(\cdot)$-approximation in near-linear time per pair (Kuszmaul, ITCS/SODA line) and its lifting to search *(frontier — verify)*.
- Learned and embedding-based indices replacing SAX with neural encoders, plus GPU Matrix Profile (Palpanas, Keogh groups).
- Unified ANN benchmarking of series-as-vectors vs. native series indices (ann-benchmarks ecosystem).

## 8. Future Work

- A DTW sketch with provable distortion and sublinear search; matching fine-grained lower bounds for approximate DTW-NN.
- Index structures that respect **z-normalization** and variable query length simultaneously.
- Tight space–time–recall trade-offs for billion-series catalogs.

## 9. Key References

- **[Foundational]** E. Keogh, C. Ratanamahatana. *Exact indexing of dynamic time warping.* KAIS, 2005. — [DOI](https://doi.org/10.1007/s10115-004-0154-9)
- **[SOTA]** T. Rakthanmanon et al. *Searching and Mining Trillions of Time Series Subsequences under DTW.* KDD, 2012. — [DOI](https://doi.org/10.1145/2339530.2339576)
- **[SOTA]** C.-C. M. Yeh et al. *Matrix Profile I.* ICDM, 2016. — [DOI](https://doi.org/10.1109/ICDM.2016.0179)
- **[Foundational]** K. Bringmann, M. Künnemann. *Quadratic Conditional Lower Bounds for String Problems and DTW.* FOCS, 2015. — [arXiv](https://arxiv.org/abs/1502.01063)
- **[SOTA]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[Survey]** T. Palpanas et al. *Data Series Management and Analytics.* (data-series indexing line / surveys), 2019–2023. — [DBLP search](https://dblp.org/search?q=Palpanas+Data+Series+Management+and+Analytics)

## 10. Worked Example

Take query $Q=(0,1,2)$ and candidate $S=(0,0,1,2,2)$ — same shape, stretched in time. Plain Euclidean on the aligned prefix $(0,1,2)$ vs $(0,0,1)$ gives $\sqrt{0^2+1^2+1^2}=\sqrt 2\approx1.41$, falsely large. DTW does better.

Fill the DP grid $D[i,j]=(q_i-s_j)^2+\min(D[i{-}1,j],D[i,j{-}1],D[i{-}1,j{-}1])$ with cost $(q_i-s_j)^2$:

| | s=0 | 0 | 1 | 2 | 2 |
|---|---|---|---|---|---|
| **q=0** | 0 | 0 | 1 | 5 | 9 |
| **q=1** | 1 | 1 | 0 | 1 | 2 |
| **q=2** | 5 | 5 | 1 | 0 | 0 |

The bottom-right cell is $\mathrm{DTW}(Q,S)=0$: the warping path $0{\to}0,0; 1{\to}1; 2{\to}2,2$ aligns perfectly, recovering the true match Euclidean missed.

**Lower-bound pruning:** $LB\_Keogh$ builds an envelope $(U,L)$ around $Q$ with band $w=1$: $U=(1,2,2),L=(0,0,1)$. For a far candidate, $LB\_Keogh=\sum\max(0,(s_i-U_i)^2,(L_i-s_i)^2)$ is computed in $O(m)$ and, if it already exceeds the best-so-far DTW, the $O(m^2)$ DP is skipped — the cascade behind UCR Suite's trillion-point scan.

---
*Part of the [DBMS Research catalog](../../README.md).*
