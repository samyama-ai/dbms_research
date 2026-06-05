# Multivariate correlation anomaly at scale

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/multivariate-correlation-anomaly` · **Status:** open

## 1. Problem Statement
Many anomalies are invisible per-series: each metric stays within its normal range, but the **joint/correlation structure** breaks (two metrics that always move together diverge; a usually-uncorrelated pair synchronizes). The problem: detect **structural/correlation anomalies** across a large set of $m$ correlated series in a streaming TSDB while maintaining only **sublinear state** in the number of pairs $\binom{m}{2}$ (and ideally sublinear in $m$), with bounded per-point update cost. Equivalently, monitor a time-varying covariance/precision matrix (or correlation graph) and flag statistically significant structural changes — without materializing the full $m\times m$ matrix at every step.

Variants: **pairwise** (a correlation $\rho_{ij}$ shifts), **subset/clique** (a group decorrelates), **global structural** (the covariance spectrum or precision graph changes), and the **decision** form (is there *any* pair whose correlation changed by $>\delta$ this window?). The scale constraint — $m$ in the thousands-to-millions, so $\binom{m}{2}$ pairs is $10^6$–$10^{12}$ — is the crux: exact all-pairs monitoring is infeasible.

## 2. Mathematical Foundations
Stack series into $x_t\in\mathbb{R}^m$; the object of interest is the (windowed) covariance $\Sigma_t=\mathbb{E}[x_tx_t^\top]$, correlation matrix $C_t$, or precision $\Theta_t=\Sigma_t^{-1}$ (whose zeros encode conditional independence — a Gaussian graphical model). Detecting structural anomalies is **change detection over $\Sigma_t$**. Sublinear state leverages: **sketching / random projection** — Johnson–Lindenstrauss preserves pairwise inner products with $O(\epsilon^{-2}\log m)$-dimensional projections, so correlations are estimable from a compressed state; **count-sketch / AMS** for inner products and second moments; **low-rank + sparse** decompositions ($\Sigma\approx LL^\top + S$) when correlation structure is governed by few latent factors; and **graphical-lasso** / sparse precision estimation ($\ell_1$-penalized) when $\Theta$ is sparse. Detecting a single highly-correlated pair among many connects to **light bulb / closest-pair** problems, solvable in subquadratic time via LSH or Valiant's (2015) tensor/fast-matrix-multiply method in $O(m^{2-c})$. Change significance uses spectral/Frobenius statistics with random-matrix-theory null calibration (Marchenko–Pastur).

## 3. State of the Art (SOTA)
**Systems/ML-SOTA:** deep multivariate detectors — Omni­Anomaly (KDD 2019), MTAD-GAT (ICDM 2020), GDN (graph deviation network, AAAI 2021), and Transformer/diffusion variants (Anomaly Transformer, ICLR 2022) — model joint structure but are *batch/offline*, $O(m^2)$ or denser in state, and lack scale-out streaming guarantees. **Streaming-SOTA:** StreamingPCA / subspace tracking (GROUSE, Frequent-Directions matrix sketch — Ghashami et al. 2016) tracks the top subspace in $O(mk)$ state; online graphical-lasso variants track sparse precision. **Theory-SOTA:** Valiant's subquadratic closest-correlated-pair (2015), Frequent Directions deterministic matrix sketching with tight $\|A^\top A - B^\top B\|$ error (Liberty 2013; Ghashami–Liberty–Phillips–Woodruff 2016), and JL-based correlation sketching. No system unifies sublinear-state streaming with *provable* detection guarantees.

## 4. Upper Bound
**Subspace/spectral change:** Frequent Directions maintains a sketch $B\in\mathbb{R}^{\ell\times m}$ with $\|\Sigma - B^\top B\|_2 \le \|\Sigma\|_F^2/\ell$ using $O(m\ell)$ space and $O(m\ell)$ per update — sublinear in $\binom m2$ — enabling spectral-norm change detection. **Closest correlated pair:** Valiant's algorithm finds an $\rho$-correlated pair (vs. background $\le\rho/2$) in $O(m^{2-\Theta(\log(1/\rho))})$ time via fast matrix multiplication — subquadratic. **JL sketching:** all pairwise correlations approximated to $\pm\epsilon$ from $O(\epsilon^{-2}\log m)$-dim projections, $O(m\epsilon^{-2}\log m)$ state. Under a $k$-factor low-rank model, state drops to $O(mk)$ with detection power for factor-structure breaks.

## 5. Lower Bound
Detecting an arbitrary single shifted pair among $\binom m2$ with no structural assumption requires $\Omega(m^2)$ work in the worst case (you must, information-theoretically, touch each pair) — a **streaming/communication lower bound**: distinguishing "all pairs normal" from "one pair shifted by $\delta$" needs $\Omega(m^2)$ bits in the one-way communication model when correlations are adversarial (reduction from set-disjointness on the pair index). The closest-pair subquadratic results **provably require a correlation gap** ($\rho$ vs. $\rho/2$); without a gap, $\Omega(m^2)$ is conjectured tight (related to OV/3SUM-style fine-grained barriers for closest-pair under general metrics). Thus *sublinear-in-pairs* detection is impossible without structure (low rank, sparsity, or a correlation gap).

## 6. The Gap
The bounds **match only under structural assumptions**: with low-rank/sparse/correlation-gap structure we have sublinear-state algorithms; for *arbitrary* correlation anomalies the $\Omega(m^2)$ barrier stands. The open problem is to (a) characterize the *minimal structural assumption* under which streaming sublinear-state detection with provable power is possible, and (b) give matching upper/lower bounds for *delay + state + power* jointly. **Genuinely open** — current detectors either assume strong structure or pay $O(m^2)$.

## 7. Current Research (as of June 2026)
Threads: graph-based detectors (GDN-style) made **streaming with sketched adjacency** to cut state *(frontier — verify)*; random-matrix-theory null models for calibrating spectral change statistics at scale; sparse online precision-matrix tracking for conditional-independence breaks; and connections to **causal/structural** change detection. Scaling self-supervised multivariate foundation detectors to millions of series under sublinear state is an active and unsettled systems+theory direction *(frontier — verify)*. Ties to FDR control (`anomaly-detection-fdr-control.md`) for the resulting many-pair multiplicity, and to similarity search (`time-series-similarity-search.md`) via LSH for correlated-pair retrieval.

## 8. Future Work
- A taxonomy of structural assumptions (low-rank, sparse-precision, correlation-gap) with tight state/delay/power bounds for each.
- Streaming spectral change detection with RMT-calibrated false-alarm control fused with online FDR.
- Subquadratic *streaming* closest-correlated-pair with bounded memory (beyond batch Valiant).
- Benchmarks with injected structural (vs. point) anomalies at high $m$.

## 9. Key References
- **[Foundational]** E. Liberty. *Simple and Deterministic Matrix Sketching (Frequent Directions).* KDD, 2013.
- **[Foundational]** G. Valiant. *Finding Correlations in Subquadratic Time, with Applications to Learning Parities and the Closest Pair Problem.* JACM, 2015.
- **[Foundational]** M. Ghashami, E. Liberty, J. Phillips, D. Woodruff. *Frequent Directions: Simple and Deterministic Matrix Sketching.* SIAM J. Computing, 2016.
- **[SOTA]** Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, D. Pei. *Robust Anomaly Detection for Multivariate Time Series through Stochastic Recurrent Networks (OmniAnomaly).* KDD, 2019.
- **[SOTA]** A. Deng, B. Hooi. *Graph Neural Network-Based Anomaly Detection in Multivariate Time Series (GDN).* AAAI, 2021.
- **[Survey]** J. Friedman, T. Hastie, R. Tibshirani. *Sparse Inverse Covariance Estimation with the Graphical Lasso.* Biostatistics, 2008.

---
*Part of the [DBMS Research catalog](../../README.md).*
