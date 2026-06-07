---
id: 28-vector-similarity-search/embedding-distribution-shift
title: "Distribution shift in learned embeddings"
topic: 28-vector-similarity-search
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Distribution shift in learned embeddings

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/embedding-distribution-shift` · **Status:** empirically-open

## 1. Problem Statement

An ANN index is built under assumptions about the embedding distribution: centroids (IVF), codebooks (PQ), graph topology (HNSW/Vamana), and even the metric calibration all encode the data distribution $p_0$ at build time. Two kinds of drift degrade recall:

- **Data drift.** New vectors are drawn from $p_t \ne p_0$ (topic/seasonal shift, new domains), so centroids become unbalanced, codebooks distort, and graph navigability degrades in newly dense regions.
- **Model drift.** The embedding model itself is upgraded/fine-tuned, producing $\phi_t$ instead of $\phi_0$. Old vectors $\phi_0(x)$ and new vectors $\phi_t(x)$ live in *incompatible* spaces, so a query embedded by $\phi_t$ cannot be meaningfully compared to an index of $\phi_0$ vectors without re-embedding everything.

The problem: **keep $R@k$ stable (within tolerance $\epsilon$) under bounded drift, minimizing the cost of re-embedding / re-indexing.** Decision variant: given a drift magnitude, decide whether the current index still meets the recall SLA. Optimization variant: schedule partial re-embedding/re-training to hold recall at minimal compute.

## 2. Mathematical Foundations

Let drift be measured by a divergence $\mathrm{Div}(p_0, p_t)$ (KL, Wasserstein-$W_2$, or MMD). For quantization, expected distortion increase is bounded by the codebook's mismatch: if centroids are optimal for $p_0$, excess distortion under $p_t$ scales with $W_2(p_0,p_t)^2$ (Lloyd optimality is local; perturbation bounds follow from $k$-means sensitivity analysis). For graph indexes, navigability depends on the relative-neighborhood structure; drift that creates new dense clusters far from build-time hubs can break the small-world property, raising hop counts.

Model drift is sharper: $\phi_0$ and $\phi_t$ are generally **not aligned** — even similar models differ by an arbitrary rotation/scaling plus nonlinear warping. Comparing across them requires a learned alignment map $A:\mathbb{R}^{D_0}\to\mathbb{R}^{D_t}$ (Procrustes/orthogonal alignment minimizing $\|A\phi_0(X)-\phi_t(X)\|$) or **backward-compatible training** that constrains $\phi_t$ to be comparable to $\phi_0$ (the BCT objective). This connects to representation-stability theory and to *concept drift* detection in streaming ML. Recall under drift can be monitored via the distribution of margins (distance to the $k$-th neighbor); shift in this statistic is an early-warning signal.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Production practice = periodic full re-embed + rebuild (Vespa, Milvus, Pinecone), gated by offline recall regression tests; tombstone + compaction handles data drift incrementally. *Backward-Compatible Training (BCT)* (Shen et al., CVPR 2020) and follow-ups (FCT, BT$^2$, $L^2$/alignment methods) let a new model serve queries against an old gallery without re-indexing the gallery. **Matryoshka Representation Learning** (Kusupati et al., NeurIPS 2022) yields nested embeddings robust to truncation, easing some re-index churn.
- **Theory-SOTA.** Domain-adaptation generalization bounds ($\mathcal{H}\Delta\mathcal{H}$-divergence, Ben-David et al.) and quantization perturbation bounds; no recall-specific guarantee under embedding shift.

## 4. Upper Bound

With backward-compatible or aligned embeddings, the new model can query the old index with recall loss bounded by the alignment residual $\|A\phi_0 - \phi_t\|$; empirically BCT recovers most of the recall with **zero gallery re-embedding**. For data drift, periodic re-clustering bounds excess PQ distortion to $O(W_2(p_0,p_t)^2)$; adaptive centroid splitting/merging keeps balance. Drift *detection* via two-sample tests (MMD, kernel tests) flags when rebuild is needed, bounding the window of degraded recall by the detection delay. None of these is a closed-form recall guarantee — they are bounds on the *proxies* (distortion, alignment error).

## 5. Lower Bound

Domain-adaptation lower bounds (Ben-David–Blitzer–Crammer–Pereira) show that without assumptions relating source and target, no algorithm can guarantee target performance — i.e., **unbounded drift makes recall preservation impossible without re-embedding** (information-theoretic). For model drift, comparing vectors from independently trained $\phi_0,\phi_t$ is impossible without shared anchors: there exist model pairs achieving identical downstream accuracy yet with embeddings related by an adversarial nonlinear map, so no fixed alignment recovers cross-model neighbors (an identifiability/impossibility result). This forces either re-embedding or a compatibility constraint baked into training.

## 6. The Gap

The gap is between **proxy metrics** (distortion, alignment residual, drift divergence) that we can bound and the **actual recall** we care about — no theory tightly links drift magnitude to recall loss for real indexes, and no principled, cheap *trigger* tells you exactly when to re-index. It is **empirically open**: practice relies on conservative periodic rebuilds and regression tests. Closing it needs (a) recall-predictive drift statistics and (b) incremental index repair with recall guarantees under bounded shift.

## 7. Current Research (as of June 2026)

- Backward-compatible and cross-model alignment so model upgrades avoid full re-embedding (BCT/FCT successors) *(frontier — verify)*.
- Drift-aware monitoring: margin-distribution and MMD-based triggers wired into vector DBs *(frontier — verify)*.
- Out-of-distribution-robust index construction (OOD-DiskANN, RobustVamana) handling query/base distribution mismatch.
- Matryoshka and adaptive-dimension embeddings to reduce re-index cost on model change.
- Groups: Microsoft (OOD-DiskANN), Google/Meta (BCT line, Matryoshka), and the big-ann OOD track community.

## 8. Future Work

- Recall-predictive drift metrics with confidence bounds.
- Incremental codebook/graph repair under bounded $W_2$ drift with provable recall retention.
- Standardized compatibility contracts for embedding-model versioning in vector DBs.
- Joint scheduling of re-embedding vs. partial re-indexing minimizing compute under a recall SLA (links to streaming-ANN and cost-model problems).

## 9. Key References

- **[Foundational]** Shai Ben-David, John Blitzer, Koby Crammer, Alex Kulesza, Fernando Pereira, Jennifer Wortman Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[SOTA]** Yantao Shen, Yuanjun Xiong, Wei Xia, Stefano Soatto. *Towards Backward-Compatible Representation Learning (BCT).* CVPR, 2020. — [arXiv](https://arxiv.org/abs/2003.11942)
- **[SOTA]** Aditya Kusupati et al. *Matryoshka Representation Learning.* NeurIPS, 2022. — [arXiv](https://arxiv.org/abs/2205.13147)
- **[SOTA]** Shikhar Jaiswal, Ravishankar Krishnaswamy, Ankit Garg, Harsha Vardhan Simhadri, Sheshansh Agrawal. *OOD-DiskANN: Efficient and Scalable Graph ANNS for Out-of-Distribution Queries.* arXiv:2211.12850, 2022. — [arXiv](https://arxiv.org/abs/2211.12850)
- **[Survey]** Jie Lu, Anjin Liu, Fan Dong, Feng Gu, João Gama, Guangquan Zhang. *Learning under Concept Drift: A Review.* IEEE TKDE, 2019. — [DOI](https://doi.org/10.1109/TKDE.2018.2876857)

## 10. Worked Example

**Model drift, concretely.** Suppose the old model $\phi_0$ embeds three documents in $\mathbb{R}^2$: $A=(1,0)$, $B=(0,1)$, $C=(-1,0)$. A query $\phi_0(q)=(0.9,0.1)$ retrieves nearest neighbor $A$ (cosine $\approx 0.99$). Now we upgrade to $\phi_t$, which happens to apply a $90°$ rotation plus reflection of the *same* semantic content: $\phi_t(A)=(0,1)$, $\phi_t(B)=(-1,0)$, $\phi_t(C)=(0,-1)$, and the query lands at $\phi_t(q)=(0.1,0.9)$.

If we query the **un-migrated** index (still storing $\phi_0$ vectors) with $\phi_t(q)=(0.1,0.9)$, the nearest stored vector is $B=(0,1)$, not $A$ — recall@1 drops to $0$. The semantic answer didn't change; only the coordinate frame did.

**Fix via Procrustes alignment.** Learn orthogonal $A$ minimizing $\|A\,\phi_0(X)-\phi_t(X)\|$. Here the exact map is the rotation $R=\begin{psmallmatrix}0&-1\\1&0\end{psmallmatrix}$; applying $R$ to stored $\phi_0(A)=(1,0)$ gives $(0,1)=\phi_t(A)$, restoring recall@1 with **zero re-embedding** of the gallery — exactly the upper-bound route of §4, where residual recall loss is bounded by $\|R\phi_0-\phi_t\|$ (here $0$).

---
*Part of the [DBMS Research catalog](../../README.md).*
