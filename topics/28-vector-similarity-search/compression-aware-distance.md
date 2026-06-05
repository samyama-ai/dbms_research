# Compression-aware distance estimation

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/compression-aware-distance` · **Status:** partially-solved

## 1. Problem Statement

To fit billion-scale vector databases in memory, the database vectors $P \subseteq \mathbb{R}^d$ are **quantized** (product quantization, scalar quantization, binary/RaBitQ codes), while the query $q$ arrives uncompressed at search time. **Asymmetric distance computation (ADC)** estimates $\rho(q, p)$ using the *full-precision* query against the *quantized* database point $\hat p$, rather than quantizing both. The problem: design quantizers and estimators that **provably minimize distance-estimation error** — and thereby tighten the **recall** of the downstream top-$k$ — under the constraint that only the database side is compressed. Variants: the **estimation variant** (minimize MSE / produce unbiased, low-variance distance estimates); the **ranking variant** (preserve the *order* of distances, which is what recall depends on); and the **bound variant** (produce a confidence interval $[\ell, u]$ on $\rho(q,p)$ enabling provable pruning/re-ranking). The key claim to establish: asymmetric (query-uncompressed) estimation is *provably* better than symmetric, and by how much.

## 2. Mathematical Foundations

**Product Quantization** (Jégou–Douze–Schmid, 2011) partitions $\mathbb{R}^d$ into $m$ subspaces, each quantized to a codebook of $2^b$ centroids; a vector maps to $m$ codes. The **symmetric** estimator approximates $\|q-p\|^2$ by $\|\hat q - \hat p\|^2$; the **asymmetric** estimator uses $\|q - \hat p\|^2$, precomputing per-subspace lookup tables of $q$ against all centroids. The foundational fact: ADC has **lower expected squared error** because it removes the query-side quantization noise term. If $\hat p = p + \eta_p$ and $\hat q = q + \eta_q$ with independent quantization noise, then symmetric error scales with $\mathrm{Var}(\eta_p)+\mathrm{Var}(\eta_q)$ while asymmetric scales with $\mathrm{Var}(\eta_p)$ alone. **RaBitQ** (Gao–Long, SIGMOD 2024) gives, for the first time, an *unbiased* estimator with an explicit **concentration bound**: the relative error of the estimated inner product concentrates as $O(1/\sqrt{B})$ for $B$ bits via randomized rotation + binary codes, yielding rigorous recall guarantees. The analysis rests on **Johnson–Lindenstrauss**-style random projections, sub-Gaussian concentration, and **rate–distortion** theory bounding achievable distortion at a given bit budget.

## 3. State of the Art (SOTA)

- **Foundational:** PQ + ADC (Jégou et al., TPAMI 2011); **OPQ** (Ge et al., CVPR 2013) optimizes the rotation to minimize quantization distortion.
- **Theory + systems SOTA:** **RaBitQ** (Gao–Long, SIGMOD 2024) and **Extended RaBitQ** (2024–2025) provide unbiased ADC with theoretical error bounds and SIMD-fast kernels, outperforming PQ at equal bits.
- **Systems:** **ScaNN** (Guo et al., ICML 2020) introduces **anisotropic vector quantization** — a score-aware loss weighting parallel error more than orthogonal — directly optimizing for inner-product ranking rather than reconstruction; deployed in Google's vector search. **SVS-LVQ** (Intel, VLDB 2023) uses locally-adaptive scalar quantization with asymmetric kernels.
- All production stacks (FAISS, ScaNN, Milvus) use asymmetric LUT-based distance by default.

## 4. Upper Bound

RaBitQ achieves an **unbiased** distance/inner-product estimator whose relative error concentrates with high probability as $O(1/\sqrt{B})$ for a $B$-bit code, with explicit constants and SIMD-amenable computation — the strongest known *provable* recall-tightening guarantee for database-side-only quantization. Anisotropic quantization (ScaNN) provably minimizes the *score-weighted* loss that governs MIPS ranking, giving better top-$k$ recall than reconstruction-optimal quantizers at equal bitrate. The general upper bound on achievable distortion at $B$ bits is the **rate–distortion** function $D(R)$, which ADC approaches but, for fixed practical codebooks, does not meet.

## 5. Lower Bound

The information-theoretic floor is **rate–distortion**: for a source with given distribution, no $B$-bit quantizer can achieve expected distortion below $D(B)$; thus distance-estimation error is lower-bounded regardless of estimator cleverness. For **ranking/recall**, distinguishing the true top-$k$ requires resolving distance gaps of size $\Delta$; if quantization error exceeds $\Delta$, recall is *information-theoretically* impossible without re-ranking exact vectors — a lower bound forcing the standard two-stage "quantized filter + exact re-rank" pipeline. There is **no matching lower bound** showing current practical quantizers are optimal: the gap between achieved distortion and $D(R)$ for realistic embedding distributions is open. Asymmetry strictly helps (removes one noise term) but the *optimal* asymmetric estimator for a given bit budget is not characterized.

## 6. The Gap

**Partially solved**: RaBitQ closed much of the theory–practice gap by delivering provable, unbiased, recall-tightening ADC, and anisotropic quantization aligned the objective with ranking. Remaining gaps: (i) no quantizer provably meets the rate–distortion bound for real (correlated, heavy-tailed) embedding distributions; (ii) the *optimal asymmetric estimator* under a fixed code is uncharacterized; (iii) data-dependent / learned codebooks lack the clean guarantees of randomized RaBitQ; (iv) tight joint analysis of quantization error and graph-index recall (how estimation error propagates through HNSW traversal) is largely empirical.

## 7. Current Research (as of June 2026)

- Extended/higher-bit RaBitQ and its integration into graph indices (IVF-RaBitQ, HNSW-RaBitQ) with end-to-end recall bounds *(frontier — verify)*.
- Learned, distribution-adaptive quantizers that retain concentration guarantees.
- Asymmetric estimators for cosine/MIPS with tight confidence intervals enabling *provable* early pruning.
- Joint quantizer–index co-design analyzing error propagation through traversal.
- Groups: Gao & Long (RaBitQ, NTU/RMIT lineage), the ScaNN team (Google), Intel SVS team, FAISS (Meta).

## 8. Future Work

- A quantizer provably matching $D(R)$ for realistic embedding sources.
- Characterization of the minimum-variance asymmetric estimator at fixed bitrate.
- End-to-end recall guarantees coupling quantization error with graph-traversal behavior.
- Confidence-interval ADC enabling sound pruning with bounded false-negative rate.

## 9. Key References

- **[Foundational]** Jégou, H., Douze, M., Schmid, C. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011. — [DOI](https://doi.org/10.1109/TPAMI.2010.57)
- **[Foundational]** Ge, T., He, K., Ke, Q., Sun, J. *Optimized Product Quantization (OPQ).* CVPR, 2013. — [DOI](https://doi.org/10.1109/CVPR.2013.379)
- **[SOTA]** Gao, J., Long, C. *RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search.* SIGMOD, 2024. — [arXiv](https://arxiv.org/abs/2405.12497) — [DOI](https://doi.org/10.1145/3654970)
- **[SOTA]** Guo, R., Sun, P., Lindgren, E., Geng, Q., Simcha, D., Chern, F., Kumar, S. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization (ScaNN).* ICML, 2020. — [arXiv](https://arxiv.org/abs/1908.10396) — [DBLP](https://dblp.org/rec/conf/icml/GuoSLGSCK20.html)
- **[Survey]** Cover, T. M., Thomas, J. A. *Elements of Information Theory* (rate–distortion). Wiley, 2006. — [DOI](https://doi.org/10.1002/047174882X)

## 10. Worked Example

**Asymmetric beats symmetric: a 2-D, 1-bit-per-coordinate trace.** Let the quantizer round each coordinate to the nearest of $\{0,1\}$ (one bit). Database point $p=(0.9,0.1)\Rightarrow \hat p=(1,0)$. Query $q=(0.8,0.2)$. True squared distance $\|q-p\|^2=(0.8-0.9)^2+(0.2-0.1)^2=0.01+0.01=0.02$.

- **Symmetric** quantizes the query too: $\hat q=(1,0)$, estimate $\|\hat q-\hat p\|^2=0$. Error $=|0-0.02|=0.02$, and worse, it collapses the gap to a competitor.
- **Asymmetric (ADC)** keeps $q$ full-precision: $\|q-\hat p\|^2=(0.8-1)^2+(0.2-0)^2=0.04+0.04=0.08$. Error $=|0.08-0.02|=0.06$.

In this single draw symmetric looks closer, but bias/variance over the *distribution* tells the real story. With i.i.d. per-coordinate quantization noise of variance $\sigma^2$, symmetric error variance $\propto \mathrm{Var}(\eta_p)+\mathrm{Var}(\eta_q)=2\sigma^2$, asymmetric $\propto \sigma^2$ — half the noise, because the query side carries none. Over many queries ADC's estimator concentrates twice as tightly, which is exactly what preserves the *ranking* between two near-tied neighbors and thus recall — the property RaBitQ formalizes with its $O(1/\sqrt B)$ bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
