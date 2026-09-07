---
id: 28-vector-similarity-search/optimal-product-quantization
title: "Optimal product quantization codebooks"
topic: 28-vector-similarity-search
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal product quantization codebooks

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/optimal-product-quantization` · **Status:** partially-solved

## 1. Problem Statement
Product Quantization (PQ) compresses a vector $x \in \mathbb{R}^d$ by splitting it into $m$ subvectors and quantizing each with a separate $k$-entry codebook, yielding a compact code of $m\log_2 k$ bits used for fast (asymmetric) distance estimation. The central question: **can PQ/OPQ codebook learning provably minimize expected distance distortion under a fixed bit budget?**

Formally, given a distribution (or sample) over $\mathbb{R}^d$ and budget $B = m\log_2 k$ bits, find subspace decomposition + codebooks minimizing expected quantization error (or, sharper, expected *distance-estimation* error). 

Variants:
- **Optimization (reconstruction):** minimize $\mathbb{E}\|x - \hat{x}\|^2$.
- **Optimization (distance-aware):** minimize $\mathbb{E}[(\|q-x\| - \widehat{\|q-x\|})^2]$ over query/data pairs (the quantity that actually drives recall).
- **Decision:** does there exist a codebook achieving distortion $\le D$ at budget $B$? (NP-hardness of the underlying clustering.)

## 2. Mathematical Foundations
PQ assumes a partition of coordinates into $m$ groups; per group $j$, a codebook $C_j = \{c_{j,1},\dots,c_{j,k}\}$ minimizing within-group $k$-means distortion. The product codebook has $k^m$ effective centers but only $mk$ stored centroids.

- **Lloyd / $k$-means.** Each subquantizer is a $k$-means instance; $k$-means is NP-hard (Aloise et al. 2009; Mahajan–Nimbhorkar–Varadarajan 2009) even in the plane for general $k$, and $\mathsf{APX}$-hard. PTAS exist for fixed $k$ or fixed $d$.
- **Optimized PQ (OPQ).** Ge et al. (CVPR 2013) add a rotation $R \in O(d)$: minimize $\sum \|Rx - \hat{R x}\|^2$, alternating between $R$ (Procrustes / eigen-allocation) and codebooks. The optimum balances variance across subspaces — connected to minimizing the product of subspace variances under a fixed-budget constraint (an entropy/AM–GM argument).
- **Rate–distortion floor.** For a source with covariance $\Sigma$, the Gaussian rate–distortion bound gives a lower envelope $D(B)$; reverse water-filling allocates bits to eigen-directions. PQ with rotation can approach but, due to the product structure, not always meet this floor.
- **Additive/composite quantization.** Generalizes PQ to non-orthogonal codebooks (sum of codewords); strictly more expressive, NP-hard encoding (it becomes a high-order MRF / fully-connected assignment).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** OPQ (Ge et al. 2013) and **ScaNN's anisotropic VQ** (Guo et al., ICML 2020), which reweights the loss to penalize errors along the query direction — directly targeting the distance-aware objective and yielding SOTA recall-at-fixed-bits on benchmarks. LSQ/Composite Quantization (Zhang et al. 2014; Martinez et al. 2018) and residual/additive quantization push reconstruction lower at higher encoding cost.
- **Theory-SOTA:** $k$-means with provable guarantees — $k$-means++ (Arthur–Vassilvitskii 2007) gives $O(\log k)$-competitive seeding; constant-factor approximations (Kanungo et al. 2002; Ahmadian et al. 2017, $\approx 6.357$) exist for the per-subspace problem. There is **no** algorithm provably optimal for the *joint* (rotation + product partition + distance-aware) objective.

## 4. Upper Bound
Per subquantizer, $k$-means++ yields expected distortion $\le 8(\ln k + 2)\,\mathrm{OPT}$; local-search / primal-dual give constant-factor $\mathrm{OPT}$ approximations. Thus **each PQ codebook can be learned with provable constant-factor distortion** — this is why the status is *partially-solved*: the per-subspace reconstruction problem has provable approximation. For fixed $d$ and $k$, a PTAS gives $(1+\varepsilon)$ distortion. The **distance-aware** anisotropic objective is convex in the assignment-relaxed form and ScaNN optimizes it to a stationary point, but without a global approximation ratio.

## 5. Lower Bound
- **NP-hardness / APX-hardness** of $k$-means (Aloise et al. 2009; Awasthi–Charikar–Krishnaswamy–Sinop 2015 show $k$-means is APX-hard, no PTAS for general $d,k$ unless P=NP). Hence exact optimal PQ codebooks are NP-hard.
- **Joint rotation + partition** subsumes the unconstrained problem and is at least as hard; choosing the optimal subspace split is combinatorial.
- **Rate–distortion lower bound** $D(B)$ caps how good *any* $B$-bit quantizer can be; PQ's product constraint generally keeps it strictly above the unconstrained floor (an information-theoretic, model-based bound).

## 6. The Gap
For pure per-subspace **reconstruction**, the gap between upper (constant-factor / PTAS) and lower (APX-hard) is essentially understood. The open gap is the **distance-aware, jointly-optimized** objective: ScaNN's anisotropic loss matches empirical optimality but lacks a global approximation guarantee, and the optimal *bit allocation across subspaces under a recall-relevant loss* has no proven-optimal poly-time algorithm. Closing it requires either a provable approximation for anisotropic/composite quantization or a hardness result specific to the distance-estimation loss.

## 7. Current Research (as of June 2026)
Active: learned/neural quantizers and residual VQ (RVQ/RQ-VAE) for ANN, with analyses borrowing from rate–distortion; theory for anisotropic VQ approximation guarantees *(frontier — verify)*. Groups around Google Research (ScaNN), Meta FAISS, and academic quantization theorists pursue tighter bit-allocation results and connections between composite quantization and MRF inference hardness *(frontier — verify)*. Interest in *quantization-aware* graph indexes (combining PQ codes with HNSW/DiskANN) raises a joint codebook+graph optimization question.

## 8. Future Work
- A provable approximation ratio for the anisotropic / distance-aware objective.
- Optimal bit allocation across subspaces with guarantees (beyond eigen-heuristics).
- Tight characterization of the PQ gap to the rate–distortion floor as a function of covariance structure.
- Joint optimization of quantization codes and graph topology.

## 9. Key References
- **[Foundational]** H. Jégou, M. Douze, C. Schmid. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011. — [DOI](https://doi.org/10.1109/TPAMI.2010.57)
- **[SOTA]** T. Ge, K. He, Q. Ke, J. Sun. *Optimized Product Quantization.* CVPR, 2013 / IEEE TPAMI 2014. — [DOI](https://doi.org/10.1109/TPAMI.2013.240)
- **[SOTA]** R. Guo, P. Sun, E. Lindgren, et al. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization (ScaNN).* ICML, 2020. — [arXiv](https://arxiv.org/abs/1908.10396)
- **[Foundational]** D. Arthur, S. Vassilvitskii. *k-means++: The Advantages of Careful Seeding.* SODA, 2007. — [DBLP](https://dblp.org/rec/conf/soda/ArthurV07.html)
- **[Foundational]** P. Awasthi, M. Charikar, R. Krishnaswamy, A. Sinop. *The Hardness of Approximation of Euclidean k-means.* SoCG, 2015. — [DOI](https://doi.org/10.4230/LIPIcs.SOCG.2015.754)
- **[SOTA]** J. Martinez, S. Zakhmi, H. Hoos, J. Little. *LSQ++: Lower Running Time and Higher Recall in Multi-codebook Quantization.* ECCV, 2018. — [DOI](https://doi.org/10.1007/978-3-030-01270-0_30)

## 10. Worked Example

Take $d=4$, budget $B=4$ bits, split into $m=2$ subspaces of $2$ dims each, so $k=2^{B/m}=2^{2}=4$ centroids per subquantizer. Subspace 1 covers dims $(1,2)$, subspace 2 covers dims $(3,4)$.

Suppose subspace 1 has high variance (centroids spread over $[-3,3]$) while subspace 2 has tiny variance (centroids in $[-0.3,0.3]$). Assigning each subspace its own 4-entry $k$-means codebook gives, say, per-subspace MSE of $0.5$ (sub 1) and $0.005$ (sub 2), total reconstruction error $\approx 0.505$.

OPQ rotates the data so variance is *balanced*: after a rotation $R$, both subspaces carry variance $\sim 1.5$, and reverse-water-filling allocates the same 2 bits each more evenly, dropping total MSE to $\approx 0.30$. The AM–GM intuition: distortion scales with the *product* of per-subspace variances $\prod_j \sigma_j^2$, minimized when variances are equal. The distance estimate $\widehat{\lVert q-x\rVert^2}=\sum_{j} \lVert q^{(j)}-c_{j,\text{idx}}\rVert^2$ then has lower variance, raising recall at the same $4$-bit budget.

---
*Part of the [DBMS Research catalog](../../README.md).*
