---
id: 16-data-cleaning-quality/duplicate-similarity-learning
title: "Approximate-Duplicate Similarity Learning"
topic: 16-data-cleaning-quality
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Approximate-Duplicate Similarity Learning

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/duplicate-similarity-learning` · **Status:** empirically-open

## 1. Problem Statement

Entity resolution (ER) / deduplication decides whether two records refer to the same real-world entity. The hard sub-problem here is **learning the similarity/matching function** $f(r_i, r_j) \to \{0,1\}$ (or a score in $[0,1]$) that **generalizes across domains with few labels**. A function tuned on, say, product catalogs should transfer to publications or addresses with minimal new supervision.

Variants:
- **Pairwise matching (decision):** classify each candidate pair as match/non-match.
- **Clustering (optimization):** partition records into entities maximizing intra-cluster agreement — i.e., **correlation clustering** on the predicted-match graph.
- **Blocking/indexing:** generate a candidate set $C \subseteq R\times R$ with high recall and $|C| \ll |R|^2$.
- **Few-shot / transfer:** minimize labeled pairs needed to reach target F1 on a new domain.

## 2. Mathematical Foundations

Records live in attribute space; a similarity model maps a pair to features (edit distance, Jaccard/TF-IDF cosine, embedding cosine) then to a label. Learning-theoretic backbone: the matcher is a hypothesis $h\in\mathcal H$; generalization is governed by **VC dimension / Rademacher complexity**, with sample complexity $m = O\!\big(\tfrac{1}{\epsilon^2}(\text{VC}(\mathcal H) + \log\tfrac1\delta)\big)$ for $\epsilon$-accurate matching. **Transfer/domain adaptation** bounds (Ben-David et al.) give
$$\epsilon_T(h) \le \epsilon_S(h) + \tfrac12 d_{\mathcal H\Delta\mathcal H}(\mathcal D_S,\mathcal D_T) + \lambda,$$
where the $\mathcal H\Delta\mathcal H$-divergence between source and target distributions controls cross-domain generalization — formalizing *why* few-label transfer is hard.

The clustering step is **correlation clustering**: minimize disagreements (matched pairs split + non-matched pairs joined), an APX-hard objective with constant-factor approximations (Bansal–Blum–Chawla; Ailon–Charikar–Newman pivot algorithm gives 3-approx in expectation, LP gives $\approx 2.06$). Blocking relates to **LSH** and metric/embedding indexing (sublinear candidate generation).

## 3. State of the Art (SOTA)

- **Deep ER:** **DeepMatcher** (Mudgal et al., SIGMOD 2018) established neural matching; **Ditto** (Li, Li, Suhara, Doan, Tan; VLDB 2021) fine-tunes pre-trained transformers (BERT/RoBERTa) and is the systems-SOTA on the Magellan/DeepMatcher benchmarks.
- **Foundation-model / LLM ER:** zero- and few-shot matching with LLMs (Narayan et al., *Can Foundation Models Wrangle Your Data?*, VLDB 2022; subsequent 2023–2025 LLM-ER work) is the current frontier for low-label transfer.
- **Blocking:** **DeepBlocker** (Thirumuruganathan et al., VLDB 2021) and embedding-based blockers.
- **Magellan** (Konda et al., VLDB 2016) — end-to-end ER framework and benchmark suite.

## 4. Upper Bound

For the matching classifier, PAC bounds give the sample complexity above; with transformer features the empirical labeled-pair requirement on benchmark tasks is hundreds to low thousands for high F1, and LLMs push some tasks to *zero* in-domain labels (empirical, not a worst-case guarantee). For the clustering stage, **pivot / LP-rounding** gives a constant-factor approximation to min-disagreement correlation clustering ($\approx 2.06$ via Chawla–Makarychev–Schramm–Yaroslavtsev; 3 via Ailon–Charikar–Newman). Blocking via LSH gives sublinear candidate generation $O(n^{1+\rho})$ with $\rho<1$ depending on the similarity threshold.

## 5. Lower Bound

Correlation clustering (min disagreements) is **APX-hard** — NP-hard to approximate within some constant (Charikar–Guruswami–Wirth); thus no PTAS unless $\mathsf P=\mathsf{NP}$. The information-theoretic transfer lower bound is the $d_{\mathcal H\Delta\mathcal H}$ term: if source and target distributions diverge, *no* algorithm transfers without target labels (the bound is tight in the agnostic setting). For blocking, achieving high recall with a small candidate set runs into LSH lower bounds (O'Donnell–Wu–Zhou) on the exponent $\rho$ for $(r,cr)$-near-neighbor. ER as a whole is unsupervised-unidentifiable without assumptions: distinguishing duplicates from genuinely-similar distinct entities is information-theoretically impossible at the boundary.

## 6. The Gap

Status is **empirically-open**: there is no closed gap because the central question is *statistical generalization*, not a single complexity bound. Systems achieve high F1 in-domain, but **cross-domain few-label transfer** has no theory matching practice — the $\mathcal H\Delta\mathcal H$ bound is loose and uncomputable, LLM transfer lacks sample-complexity guarantees, and benchmark F1 saturates while *robustness* (distribution shift, adversarial near-duplicates) degrades. Closing it requires either tighter, computable transfer bounds for transformer/LLM matchers or new representations provably invariant across domains.

## 7. Current Research (as of June 2026)

- LLM-based matching with in-context examples, chain-of-thought, and self-verification; cost-aware cascades (cheap blocker → LLM only on hard pairs) *(frontier — verify)*.
- Contrastive / self-supervised pretraining of record embeddings for label-free transfer (e.g., **Sudowoodo**-style, 2023).
- Active learning and weak supervision to minimize human labels; **uncertainty-aware** sampling.
- Groups: Doan/Tan/Li (UW–Madison, Megagon Labs, Georgia Tech), Naumann (HPI), Stonebraker/Tamr lineage (MIT), Christen (ANU) on PPRL-adjacent linkage. Benchmark realism and shift-robustness are active threads *(frontier — verify)*.

## 8. Future Work

- Computable, tight domain-transfer bounds for neural/LLM matchers.
- Provably domain-invariant record representations.
- Joint blocking+matching+clustering with end-to-end recall/precision guarantees.
- Standardized few-shot transfer benchmarks across heterogeneous domains.

## 9. Key References

- **[Foundational]** Fellegi, Sunter. *A Theory for Record Linkage.* JASA, 1969. — [DOI](https://doi.org/10.1080/01621459.1969.10501049)
- **[Foundational]** Bansal, Blum, Chawla. *Correlation Clustering.* Machine Learning / FOCS, 2004. — [DOI](https://doi.org/10.1023/B:MACH.0000033116.57574.95)
- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[SOTA]** Mudgal et al. *Deep Learning for Entity Matching.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196926)
- **[SOTA]** Li, Li, Suhara, Doan, Tan. *Ditto: Deep Entity Matching with Pre-Trained Language Models.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3421424.3421431)
- **[SOTA]** Narayan, Chami, Orr, Ré. *Can Foundation Models Wrangle Your Data?* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2205.09911)
- **[Survey]** Christophides, Efthymiou, Palpanas, Papadakis, Stefanidis. *An Overview of End-to-End Entity Resolution for Big Data.* ACM Computing Surveys, 2021. — [DOI](https://doi.org/10.1145/3418896)

## 10. Worked Example

Four product records, with the matcher's pairwise scores (a $+$ edge means predicted match, weight $> 0.5$):

| pair | text sim | decision |
|------|----------|----------|
| $(a,b)$ | 0.92 | $+$ |
| $(b,c)$ | 0.88 | $+$ |
| $(a,c)$ | 0.30 | $-$ |
| $(c,d)$ | 0.10 | $-$ |

The match graph has $+$ edges $a{-}b$, $b{-}c$ and a $-$ edge $a{-}c$. This triangle is **inconsistent**: $a{-}b{-}c$ says all three match, but $a{-}c$ says they do not. Correlation clustering must break exactly one edge. Putting $\{a,b,c\}$ in one cluster pays $1$ disagreement (the $-$ edge $a{-}c$ violated); splitting $c$ off pays $1$ (the $+$ edge $b{-}c$). Both cost $1$, so the min-disagreement optimum is $1$ and $d$ is a singleton.

Transfer view: if this matcher were trained on publications (where token overlap of 0.30 often *is* a match), the threshold mis-fires here. The $d_{\mathcal H\Delta\mathcal H}$ divergence between the two domains is exactly what the $0.30$ edge exposes — the same feature value carries opposite labels across domains, so cross-domain transfer needs new target labels.

---
*Part of the [DBMS Research catalog](../../README.md).*
