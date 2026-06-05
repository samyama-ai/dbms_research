# Trajectory similarity join at scale

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/trajectory-similarity-join` · **Status:** empirically-open

## 1. Problem Statement
Given a set $\mathcal{T} = \{T_1,\dots,T_n\}$ of trajectories, each a polyline with up to $m$ sample points in $\mathbb{R}^2$ (or $\mathbb{R}^2 \times \mathbb{R}_{\ge 0}$ with time), and a trajectory distance $d(\cdot,\cdot)$ (discrete/continuous **Fréchet**, **DTW**, **EDR**, **LCSS**, or **ERP**), compute a **similarity join**.

Variants:
- **Threshold (range) join:** report all pairs $\{(T_i,T_j) : d(T_i,T_j)\le \tau\}$.
- **Top-$k$ / kNN join:** for each $T_i$ return its $k$ nearest trajectories under $d$.
- **Decision form:** does any pair satisfy $d(T_i,T_j)\le\tau$ (closest-pair).

The hard core is doing this **without the $\Theta(n^2)$ candidate pairs** and **without the $\Theta(n^2 m^2)$ aggregate alignment cost**, while preserving the metric/semantic guarantees of the chosen distance. Many of these distances are non-metric (DTW, EDR, LCSS violate the triangle inequality), defeating metric-index pruning.

## 2. Mathematical Foundations
The (continuous) **Fréchet distance** between curves $P,Q$ is $\delta_F(P,Q)=\inf_{\alpha,\beta}\max_t \lVert P(\alpha(t))-Q(\beta(t))\rVert$ over reparameterizations. Single-pair Fréchet is computable in $O(m^2\log m)$ (Alt–Godau) and **DTW** in $O(m^2)$ by dynamic programming over the warping-path lattice.

Fine-grained complexity governs the per-pair core: under **SETH**, neither Fréchet nor DTW nor edit-distance admits a strongly subquadratic $O(m^{2-\varepsilon})$ algorithm (Bringmann 2014; Bringmann–Künnemann; Abboud–Backurs–Williams). Thus $n$ pairs over length-$m$ curves give a conditional $\Omega(n^2 m^{2-o(1)})$ wall for exact all-pairs.

For the **join** structure, metric-space indexing requires the triangle inequality, which holds for Fréchet and ERP but fails for DTW/EDR/LCSS, so pruning must instead rely on cheap **lower-bounding** filters ($\mathrm{LB\_Keogh}$, $\mathrm{LB\_Improved}$, envelope and bounding-box bounds) that satisfy $\mathrm{LB}(T_i,T_j)\le d(T_i,T_j)$, enabling filter-and-refine without false dismissals. The inherent quadratic candidate space frames the scalability limit.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Fréchet range/closest-pair via approximate near-neighbor and curve LSH (Indyk; Driemel–Silvestri locality-sensitive hashing for Fréchet; Driemel–Psarros) gives subquadratic *approximate* joins. Approximate DTW near-neighbor structures exist but with weak guarantees due to non-metricity.
- **Systems-SOTA:** distributed/parallel filter-and-refine engines — **DITA** (SIGMOD 2018, trie-based distributed in-memory join), **DISON/REPOSE**, **TrajMesa/JUST**, **Dragoon**, and GPU-accelerated DTW kernels. These scale to billions of points empirically using grid/quadtree partitioning, pivot/reference-point filtering, and bounding-box envelopes, but offer no worst-case guarantee.

## 4. Upper Bound
Exact threshold join: $O(n^2 \cdot C(m))$ where $C(m)=O(m^2\log m)$ (Fréchet) or $O(m^2)$ (DTW), reducible in practice by filters but not in the worst case. For **$(1+\varepsilon)$-approximate** Fréchet near-neighbor, LSH/curve-hashing yields query and join cost subquadratic in $n$ — e.g. $n^{1+\rho}$ candidate work with $\rho<1$ depending on $\varepsilon$ and curve complexity — in the **real-RAM / word-RAM model**. No exact join beats the SETH-conditional quadratic-in-$n$-and-$m$ product.

## 5. Lower Bound
**SETH-conditional:** no $O((nm)^{2-\varepsilon})$ exact algorithm for Fréchet/DTW/edit-distance joins, inherited from single-pair hardness (Bringmann 2014; Backurs–Indyk for edit distance; Abboud–Backurs–Williams). **OV/3SUM**-based hardness applies to closest-pair-style variants. For approximate near-neighbor under Fréchet, cell-probe / LSH lower bounds bound the achievable $\rho$. These are conditional (SETH/OV/3SUM), except the unconditional info-theoretic output-size floor when many pairs qualify.

## 6. The Gap
For **exact** joins the per-pair barrier is essentially tight (SETH); the open question is whether the *join*, amortized over $n^2$ pairs, admits genuine subquadratic-in-$n$ exact pruning beyond worst-case-pathological inputs — currently only heuristic. For **approximate** joins under non-metric DTW/EDR there is a real gap: no algorithm matches the Fréchet LSH guarantees, because triangle-inequality-free distances lack a clean ANN theory. Closing it needs either a provable sketch/embedding for DTW-class distances or a fine-grained lower bound ruling one out.

## 7. Current Research (as of June 2026)
Active directions: learned trajectory embeddings (t2vec, TrajCL, contrastive/self-supervised encoders) mapping curves to $\mathbb{R}^k$ so that Euclidean ANN approximates DTW/Fréchet — strong empirically, **no error bound** *(frontier — verify)*; GPU/FPGA warping kernels and distributed in-memory joins (DITA-lineage systems) pushing to billion-point scale; and tighter cascaded lower-bound filters. Groups: Driemel, Bringmann, Künnemann (theory of Fréchet/DTW); Aref, Mokbel, Zheng/Shang, Jensen (trajectory systems); Indyk/Andoni lineage (curve LSH). Learned-embedding joins with conformal recall guarantees are an emerging thread *(frontier — verify)*.

## 8. Future Work
- Provable sketches/embeddings for DTW/EDR/LCSS despite non-metricity.
- Output-sensitive exact join algorithms with $\tilde O(n\,\mathrm{polylog} + \mathrm{OUT})$ pair work under realistic-input models.
- Recall-certified learned-embedding joins (conformal / PAC guarantees).
- Unified GPU + distributed cost models for filter-and-refine pipelines.

## 9. Key References
- **[Foundational]** Alt, Godau. *Computing the Fréchet Distance Between Two Polygonal Curves.* IJCG, 1995.
- **[Foundational]** Bringmann. *Why Walking the Dog Takes Time: Fréchet Distance Has No Strongly Subquadratic Algorithms Unless SETH Fails.* FOCS, 2014.
- **[Foundational]** Abboud, Backurs, Williams. *Tight Hardness Results for LCS and Other Sequence Similarity Measures.* FOCS, 2015.
- **[SOTA]** Driemel, Silvestri. *Locality-Sensitive Hashing of Curves.* SoCG, 2017.
- **[SOTA]** Shang, Chen, Wei, Jensen, et al. *DITA: Distributed In-Memory Trajectory Analytics.* SIGMOD, 2018.
- **[Survey]** Su, Liu, Zheng, et al. *A Survey of Trajectory Distance Measures and Performance Evaluation.* VLDB Journal, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
