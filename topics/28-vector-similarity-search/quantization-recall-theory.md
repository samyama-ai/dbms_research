# Quantization error vs. recall theory

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/quantization-recall-theory` · **Status:** open

## 1. Problem Statement
Vector compression — scalar quantization (SQ), product quantization (PQ), optimized PQ (OPQ), additive/residual quantization (AQ/RQ), and recent RaBitQ-style schemes — reduces each vector from $32d$ bits to $b$ bits, trading **distance-estimation error** for memory and bandwidth. The open problem: build a **predictive theory** that, given a quantizer at bit-rate $b$, a dataset $P$, and a query distribution, predicts the **top-$k$ recall loss** $\Delta\text{recall}@k(b)$ — ideally a closed-form or tightly-bounded relationship between bit-rate, distortion, and ranking accuracy.

- **(Quantitative/predictive)** Characterize $\text{recall}@k$ as a function of bit-rate $b$ and a small set of data statistics (variance spectrum, near-neighbor gap distribution).
- **(Decision)** Given target recall $\rho$, what minimum bit-rate $b^\*(\rho, P)$ suffices?
- **(Optimization)** Allocate bits across subspaces/codebooks to maximize recall at fixed total $b$ (a rate-allocation problem).

This is distinct from classical rate–distortion: we care not about reconstruction MSE but about **preservation of the top-$k$ ranking** under approximate distances.

## 2. Mathematical Foundations
Classical **rate–distortion theory** (Shannon; Cover–Thomas) gives the minimal expected distortion $D(R)$ achievable at rate $R$ bits/vector; for a Gaussian source the rate-distortion function is $R(D)=\tfrac12\log(\sigma^2/D)$ per dimension, and high-resolution quantization theory (Gersho–Gray) gives the $\sim 2^{-2b/d}$ MSE scaling. PQ (Jégou–Douze–Schmid) decomposes $\mathbb{R}^d$ into $m$ subspaces, quantizes each with a $2^{b/m}$-entry codebook, and estimates $\|q-x\|^2$ via the sum of per-subspace asymmetric distances; the estimator is **unbiased** under suitable assumptions with variance set by per-subspace distortion. OPQ rotates to balance subspace variances (minimizing distortion subject to a rotation), connecting to **PCA/Karhunen–Loève** and the eigenvalue spectrum of $\text{Cov}(P)$.

The missing link is from distortion to *ranking*: top-$k$ recall depends on whether the distance-estimation noise $\hat D - D$ can flip the order of the $k$-th true neighbor and the $(k{+}1)$-th. This is governed by the **distribution of near-neighbor gaps** $\gamma = D_{(k+1)} - D_{(k)}$ vs. the estimator's noise standard deviation $\sigma_{\hat D}(b)$. Concentration (Bernstein/sub-Gaussian) bounds on the PQ estimator yield $\Pr[\text{flip}] \le \exp(-\gamma^2/2\sigma_{\hat D}^2)$, but turning this into tight aggregate recall requires the joint gap distribution — which is dataset-specific and largely uncharacterized. RaBitQ recently provides *provable* per-query error bounds for binary quantization, a notable step toward such a theory.

## 3. State of the Art (SOTA)
**Systems-SOTA.** PQ/OPQ (FAISS) and IVF-PQ are the production standard; RaBitQ (Gao–Long, SIGMOD 2024) gives a 1-bit-per-dimension quantizer with **provable, sharp distance-error bounds** and strong empirical recall, and extended RaBitQ generalizes to multiple bits. Additive/residual quantization (AQ, LSQ, Babenko–Lempitsky) pushes accuracy at higher build cost. Scalar 8-/4-bit quantization with re-ranking is ubiquitous.

**Theory-SOTA.** Rate–distortion and high-resolution quantization theory are mature for MSE, and RaBitQ supplies the first widely-used quantizer with rigorous *distance*-error guarantees. But a general predictive **recall** theory across quantizer families and datasets does not exist — recall is still measured empirically per dataset/bit-rate.

## 4. Upper Bound
Best positive results are per-scheme distance-error bounds, not a unified recall law. **RaBitQ** (Gao–Long 2024) proves that its 1-bit estimator's relative distance error is $O(1/\sqrt{d})$ with high probability, yielding an *upper bound* on the probability of a top-$k$ flip and hence a lower bound on recall, given the gap distribution. For PQ, unbiased-estimator variance bounds give $\sigma_{\hat D}^2 = \sum_m \text{(subspace distortion)}$, and optimal bit-allocation across subspaces follows the classic **reverse-water-filling** solution from rate–distortion (allocate more bits to higher-variance subspaces), maximizing a distortion-proxy. Converting these into a tight, distribution-aware recall@$k$ upper bound is open.

## 5. Lower Bound
Information-theoretic lower bounds come from rate–distortion: at rate $b$, expected distortion is at least $D(b)$ (Shannon lower bound), so distance-estimation noise cannot be driven below a floor — implying a **recall ceiling** $\text{recall}@k \le 1 - g(b, \text{gap dist})$ for any quantizer at bit-rate $b$. For datasets with a heavy mass of small near-neighbor gaps $\gamma$, this ceiling is strictly below 1 at any fixed sub-linear bit-rate, an *unconditional* impossibility. Communication-complexity / sketching lower bounds for distance estimation (e.g. for $\ell_2$ via the JL lower bound of Larsen–Nelson — $\Omega(\epsilon^{-2}\log n)$ dimensions) lower-bound the bits needed for a given multiplicative distance accuracy, hence for a given recall.

## 6. The Gap
Genuinely open. We have (a) mature MSE rate–distortion theory, (b) per-scheme distance-error bounds (RaBitQ being the rigorous frontier), and (c) abundant empirical recall curves — but **no predictive bridge** from bit-rate to top-$k$ recall that holds across quantizer families and is parameterized by clean dataset statistics. The crux is characterizing the **near-neighbor gap distribution** and composing it with estimator-noise concentration into a tight two-sided recall bound. Closing it would let practitioners compute $b^\*(\rho)$ a priori instead of sweeping bit-rates, and would unify SQ/PQ/AQ/RaBitQ under one rate–recall function with matching lower bounds.

## 7. Current Research (as of June 2026)
Directions: (i) provable quantizers — RaBitQ and its multi-bit extensions, pushing rigorous distance-error guarantees *(frontier — verify)*; (ii) characterizing gap/margin distributions of real embeddings and tying them to recall; (iii) learned/end-to-end quantization (DiffPQ-style, catalyst/distillation) with generalization analysis; (iv) bit-allocation as constrained rate-distortion across subspaces and across the index hierarchy (coarse IVF + fine PQ). Groups/people: Jianyang Gao and Cheng Long (RaBitQ, NTU), Hervé Jégou / Matthijs Douze (FAISS, PQ/OPQ lineage), Artem Babenko (additive quantization), and information-theory researchers connecting sketching lower bounds to ANN. *(frontier — verify)* Several 2025 papers report rate–recall curves with theoretical fits on standard embedding benchmarks.

## 8. Future Work
- A closed-form (or tightly bounded) rate–recall function parameterized by the gap distribution.
- Per-dataset estimators of the gap/margin distribution to predict $b^\*(\rho)$ cheaply.
- Optimal joint bit-allocation across IVF coarse + PQ fine levels with recall guarantees.
- Extending provable distance-error bounds (RaBitQ-style) to additive/residual quantizers.

## 9. Key References
- **[Foundational]** A. Gersho, R. M. Gray. *Vector Quantization and Signal Compression.* Kluwer, 1992.
- **[Foundational]** H. Jégou, M. Douze, C. Schmid. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011.
- **[SOTA]** T. Ge, K. He, Q. Ke, J. Sun. *Optimized Product Quantization.* IEEE TPAMI, 2014.
- **[SOTA]** J. Gao, C. Long. *RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search.* SIGMOD, 2024.
- **[Foundational]** K. G. Larsen, J. Nelson. *Optimality of the Johnson-Lindenstrauss Lemma.* FOCS, 2017.
- **[Foundational]** T. M. Cover, J. A. Thomas. *Elements of Information Theory.* Wiley, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
