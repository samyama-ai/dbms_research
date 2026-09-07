---
id: 15-data-integration/blocking-recall-guarantees
title: "Blocking With Recall Guarantees at Scale"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Blocking With Recall Guarantees at Scale

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/blocking-recall-guarantees` · **Status:** open

## 1. Problem Statement

Entity resolution (ER) over $n$ records would compare all $\binom{n}{2}$ pairs — infeasible at $n = 10^9$. **Blocking** (a.k.a. filtering / indexing) generates a *candidate set* $C \subseteq \binom{R}{2}$ of pairs that are then scored by an expensive matcher. The goal: make $|C|$ small while ensuring (almost) all true matches survive.

- **Optimization variant:** Minimize candidate-set size $|C|$ (equivalently maximize the **reduction ratio** $1 - |C|/\binom{n}{2}$) subject to a **recall** constraint $\mathrm{recall} = |C \cap M| / |M| \ge 1 - \delta$, where $M$ is the (unknown) true match set.
- **Decision variant:** Given a blocking scheme, certify $\Pr[\text{a true match is dropped}] \le \delta$.
- **Sublinear-generation variant:** Produce $C$ in **sublinear-per-record** time, i.e. total $\tilde O(n)$ or $n^{1+o(1)}$, not $O(n^2)$ — using LSH/sketching rather than enumerating pairs.

"Solving" means a blocking method with a **provable recall guarantee** $1-\delta$ and **sublinear candidate generation**, simultaneously — currently unattained without distributional assumptions; practice relies on heuristic blocking keys with only *measured* recall.

## 2. Mathematical Foundations

Records are points in a metric/embedding space; a true match is a pair within similarity threshold $\tau$. **Locality-Sensitive Hashing (LSH)** (Indyk–Motwani, STOC 1998) gives, for a $(\,r_1, r_2, p_1, p_2)$-sensitive family, an algorithm solving $(c,r)$-approximate near-neighbor in $O(n^{1+\rho})$ time/space with $\rho = \frac{\log 1/p_1}{\log 1/p_2}$; for Hamming/Jaccard, $\rho \approx 1/c$. With $L$ AND/OR-amplified bands, the **collision (recall) probability** for a true match at similarity $s$ is $1 - (1 - s^k)^L$, giving a *tunable, provable* per-pair retention probability — the basis of any recall guarantee. The recall constraint is a coverage condition over $M$; the trade-off curve (recall vs. reduction ratio) is governed by the **gap** between $p_1$ (matches) and $p_2$ (non-matches). For exact (not approximate) recall one needs either covering-code constructions or **multi-probe / data-dependent LSH** (Andoni–Razenshteyn, STOC 2015) achieving the optimal $\rho = \frac{1}{2c^2-1}$ for Euclidean ANN.

## 3. State of the Art (SOTA)

**Theory SOTA.** LSH and its data-dependent optimum (Andoni–Razenshteyn 2015; Andoni–Indyk–Laarhoven–Razenshteyn–Schmidt 2015) give the best-known ANN exponents and *probabilistic* recall per pair. **Systems SOTA.** Token/sorted-neighborhood/canopy blocking and **meta-blocking** (Papadakis et al., TKDE 2014; the **JedAI** toolkit) dominate practice; **DeepBlocker** (Thirumuruganathan et al., VLDB 2021) and embedding+ANN blocking (FAISS/HNSW — Malkov–Yashunin, TPAMI 2020 graph indexes) are the learned SOTA, with **empirically high but unguaranteed** recall *(frontier — verify)*. Surveys: Papadakis et al., *Blocking and Filtering Techniques for ER*, ACM Computing Surveys 2020; Christophides et al., *End-to-End ER*, CSUR 2021.

## 4. Upper Bound

Embedding + **HNSW**/IVF-PQ ANN indexes generate candidates in **$\tilde O(n)$** total time empirically and $O(n \log n)$ in idealized graph-index analyses, with per-pair recall set by the LSH band design: choosing $k, L$ so that $1-(1-\tau^k)^L \ge 1-\delta$ gives candidate recall $\ge 1-\delta$ *under the assumption that all true matches have similarity $\ge \tau$*. Data-dependent LSH attains query exponent $\rho = \frac{1}{2c^2-1}$ (Andoni–Razenshteyn 2015). So sublinear generation *with* a per-pair probabilistic recall bound is achievable **given a fixed similarity threshold** for matches. Model: approximate near-neighbor (RAM + randomization); guarantee is per-pair probabilistic, not adversarial.

## 5. Lower Bound

ANN has **cell-probe / space lower bounds**: any data structure answering approximate near-neighbor with constant probes needs near-$n^{1+\Omega(1/c^2)}$ space (Andoni–Indyk–Pătrașcu; Panigrahy–Talwar–Wieder, FOCS), and the LSH exponent $\rho \ge \frac{1}{2c^2-1}$ is **optimal** for data-dependent hashing (Andoni–Razenshteyn 2015) — a conditional lower bound in the LSH/cell-probe model. From the fine-grained side, exact "all pairs within distance $\tau$" is subject to **OVH/SETH** hardness: no $n^{2-\epsilon}$ algorithm for many high-dimensional similarity-join problems unless SETH fails (Rubinstein, STOC 2018; Williams). Recall under an **adversarial / arbitrary** match distribution is information-theoretically unguaranteeable in sublinear work — you cannot certify you didn't miss a match without inspecting $\Omega(n^2)$ pairs in the worst case. Model: cell-probe, fine-grained (SETH/OVH), information-theoretic.

## 6. The Gap

The genuine open gap: existing recall guarantees are **per-pair and distributional** (true matches lie within a known $\tau$, similarities behave like the LSH model), whereas real ER matches are heterogeneous (typos, missing fields, schema noise) so the *aggregate* recall over $M$ has **no worst-case guarantee** while keeping generation sublinear. SETH/cell-probe results say *exact* sublinear recall is impossible in the worst case, so the question is the best achievable $(\delta, \text{reduction ratio})$ frontier under realistic, learnable match distributions — and whether learned blockers can be made to *certify* their recall (e.g. via conformal prediction). That certification-at-scale problem is open.

## 7. Current Research (as of June 2026)

Directions: (1) **learned blocking** with self-supervised embeddings + ANN (DeepBlocker lineage) and LLM-assisted blocking-key synthesis *(frontier — verify)*; (2) **conformal / PAC recall certificates** for blockers — distribution-free guarantees that measured recall transfers to deployment *(frontier — verify)*; (3) data-dependent and learned LSH closing the gap to optimal $\rho$; (4) GPU/graph-index ANN (FAISS, HNSW, DiskANN) for billion-scale generation; (5) progressive/anytime blocking with recall-bound budgets. Groups: Papadakis–Palpanas, Doan–Govind (Magellan), Stonebraker/Tamr lineage, Andoni–Razenshteyn (ANN theory).

## 8. Future Work

Distribution-free recall certificates (conformal) that hold under deployment drift; tight $(\delta,\text{reduction})$ frontiers under realistic noise models; provably near-optimal learned LSH; blocking that jointly optimizes downstream *clustering* recall (not just pairwise); and integrating blocking guarantees end-to-end with the matcher and resolution stages so a global recall bound is certifiable.

## 9. Key References

- **[Foundational]** Indyk, Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC 1998. — [DOI](https://doi.org/10.1145/276698.276876)
- **[SOTA]** Andoni, Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[SOTA]** Malkov, Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using HNSW.* IEEE TPAMI, 2020. — [arXiv](https://arxiv.org/abs/1603.09320)
- **[SOTA]** Thirumuruganathan, Li, Tang, et al. *Deep Learning for Blocking in Entity Matching (DeepBlocker).* VLDB 2021. — [DOI](https://doi.org/10.14778/3476249.3476294)
- **[Survey]** Papadakis, Skoutas, Thanos, Palpanas. *Blocking and Filtering Techniques for Entity Resolution: A Survey.* ACM Computing Surveys, 2020. — [DOI](https://doi.org/10.1145/3377455)
- **[Foundational]** Rubinstein. *Hardness of Approximate Nearest Neighbor Search (under SETH).* STOC 2018. — [arXiv](https://arxiv.org/abs/1803.00904)

## 10. Worked Example

Suppose true matches have Jaccard similarity $s \ge \tau = 0.8$ on their MinHash signatures, and we band with $k$ rows per band and $L$ bands. The per-pair retention (collision) probability is $P(s) = 1 - (1 - s^k)^L$.

Pick $k=5,\ L=20$. For a true match at $s=0.8$:
$$s^k = 0.8^5 = 0.3277,\quad P = 1 - (1 - 0.3277)^{20} = 1 - 0.6723^{20} \approx 1 - 0.00040 = 0.99960.$$
So the per-pair miss (drop) probability is $\delta \approx 4\times 10^{-4}$ — well under a 1% recall-loss budget.

Now check a non-match at $s=0.3$: $s^k = 0.3^5 = 0.00243$, so $P = 1 - (1-0.00243)^{20} \approx 1 - 0.9526 = 0.0474$. Only about 4.7% of dissimilar pairs collide, so the candidate set stays small and reduction ratio stays high.

This is the $p_1$-vs-$p_2$ gap in action: the steep S-curve of $P(s)$ keeps matches ($s\ge0.8$) almost surely while discarding most non-matches — but the guarantee is *conditional* on every true match truly having $s \ge \tau$, which adversarial noise can violate.

---
*Part of the [DBMS Research catalog](../../README.md).*
