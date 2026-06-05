# Cross-modal and metric-learning ANN

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/cross-modal-ann` · **Status:** empirically-open

## 1. Problem Statement
Production retrieval increasingly uses *learned* similarities: cross-modal embeddings (CLIP-style text↔image), dot-product/cosine scores from two-tower recommenders, and explicitly *non-metric* learned scores (e.g., asymmetric relevance, Mahalanobis with a learned PSD matrix, or a small MLP scoring head). Graph-based ANN indexes (HNSW, Vamana) implicitly assume the score behaves like a metric — in particular that *greedy descent on a proximity graph monotonically approaches the answer*, which relies on triangle-inequality-like structure. The problem: **index and query under a learned similarity $s(q,x)$ that may be asymmetric, violate the triangle inequality, or be a non-metric inner product**, while retaining sublinear query time and high recall.

Variants:
- **Decision:** Given query $q$ and threshold $\tau$, decide whether $\exists x$ with $s(q,x)\ge\tau$ using a sublinear number of score evaluations.
- **Optimization (top-$k$):** Return the $k$ items maximizing $s(q,\cdot)$ at minimum cost.
- **Cross-modal:** $q$ and $x$ live in different raw spaces; only the *joint* learned score is defined, so no within-corpus metric exists to build a graph on.

## 2. Mathematical Foundations
Let queries lie in $Q$, items in $X\subset\mathbb{R}^d$, with score $s:Q\times X\to\mathbb{R}$. Maximum inner product search (MIPS) is the canonical hard case: $s(q,x)=\langle q,x\rangle$ is **not** a metric — there is no self-similarity bound and the "nearest" point depends on $\|x\|$, so graph monotonicity fails.

Key scaffolding:
- **MIPS↔NN reductions.** Shrivastava–Li (NeurIPS 2014) give an asymmetric LSH (ALSH) mapping MIPS to $\ell_2$-NN via norm-augmenting transforms $P(x),Q(q)$, restoring a metric at the cost of a dimension lift and distortion. Neyshabur–Srebro (ICML 2015) give a simpler symmetric transform with provable guarantees on the unit ball.
- **Bregman / non-metric divergences.** For Bregman divergences $D_\phi$, Cayton (2008) defines Bregman ball trees; these handle a structured class of non-metric scores but not arbitrary learned MLP heads.
- **Order vs. geometry.** Graph ANN only needs the score to induce a *navigable* order, not a metric. The open formal question is which learned $s$ admit a bounded-degree graph on $X$ that is *monotonic* w.r.t. $s$ for all $q$ — a property strictly weaker than $s$ being a metric.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** ip-HNSW / FAISS with inner-product metric works well empirically despite no monotonicity guarantee; ScaNN (Guo et al., ICML 2020) optimizes anisotropic quantization *for MIPS specifically*, beating metric-agnostic PQ. Two-tower retrieval stacks (Google, Meta) deploy MIPS-tuned ANN at scale.
- **Cross-modal-SOTA:** Systems index the shared embedding space directly when both modalities are projected into one $\mathbb{R}^d$ (CLIP). The hard residual case — a learned *late-interaction* or MLP score with no shared metric space (e.g., ColBERT MaxSim) — is handled by candidate-generation + rerank, not by a single ANN index.
- **Theory-SOTA:** ALSH/symmetric-LSH give provable sublinear MIPS on bounded-norm data; for general non-metric learned scores there is no provable index.

## 4. Upper Bound
For MIPS with bounded norms, ALSH (Shrivastava–Li) and Neyshabur–Srebro transforms yield $O(n^{\rho})$ query time with $\rho<1$ depending on the approximation factor and norm ratio — a provable upper bound in the LSH/RAM model. ScaNN's anisotropic quantization improves *constants and recall* but carries no sublinear proof. For Bregman divergences of bounded "$\mu$-similarity," Bregman ball trees give pruning bounds but degrade toward linear in high dimension.

## 5. Lower Bound
- **Cell-probe / data-structure:** approximate NN lower bounds (Andoni–Indyk–Pătrașcu, FOCS 2006) transfer to MIPS via the reductions, implying space/time tradeoffs with $n^{\Omega(1/c^2)}$-type barriers for approximation factor $c$.
- **Fine-grained:** exact MIPS / bichromatic max-inner-product is SETH-hard to solve in strongly subquadratic time for $d=\omega(\log n)$ (Rubinstein, STOC 2018, via closest-pair). For *arbitrary* learned $s$ with no exploitable structure, an adversary can force $\Omega(n)$ score evaluations (information-theoretic: the score table is incompressible).

## 6. The Gap
For MIPS the theory is reasonably mature (transforms + LSH bounds), but a gap persists between *transform-based provable* methods and *direct* ip-graph methods that win in practice without guarantees. For genuinely non-metric / asymmetric learned scores the gap is wide open: no characterization of which learned similarities admit a navigable graph, and no lower bound separating "indexable" from "must-scan" learned scores. Closing it needs a structural property of $s$ (a learned analogue of doubling dimension or monotonicity) that is both checkable and sufficient for sublinear search.

## 7. Current Research (as of June 2026)
Active directions: anisotropic / score-aware quantization beyond ScaNN; learning embeddings *jointly with the index* so the learned space is provably navigable (index-aware representation learning) *(frontier — verify)*; late-interaction retrieval (ColBERT/PLAID lineage, Khattab, Zaharia) pushing MaxSim into approximate single-stage indexes; and graph-ANN under asymmetric scores with separate out-/in-neighborhoods *(frontier — verify)*. Groups around FAISS/Meta, Google ScaNN, and academic IR/DB labs are the main contributors.

## 8. Future Work
- Define a "navigability dimension" for learned, possibly non-metric scores and prove graph-search bounds in terms of it.
- Provable single-stage indexes for late-interaction (set-of-vectors) scores.
- Co-train embedding geometry with index constraints so triangle-inequality-style guarantees hold by construction.
- Robust handling of norm/temperature drift in cross-modal scores over time.

## 9. Key References
- **[Foundational]** A. Shrivastava, P. Li. *Asymmetric LSH (ALSH) for Sublinear Time Maximum Inner Product Search.* NeurIPS, 2014.
- **[Foundational]** B. Neyshabur, N. Srebro. *On Symmetric and Asymmetric LSHs for Inner Product Search.* ICML, 2015.
- **[SOTA]** R. Guo, P. Sun, E. Lindgren, et al. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization (ScaNN).* ICML, 2020.
- **[Foundational]** L. Cayton. *Fast Nearest Neighbor Retrieval for Bregman Divergences.* ICML, 2008.
- **[SOTA]** O. Khattab, M. Zaharia. *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT.* SIGIR, 2020.
- **[Foundational]** A. Andoni, P. Indyk, M. Pătrașcu. *On the Optimality of the Dimensionality Reduction Method.* FOCS, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
