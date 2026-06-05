# Learned Embedding ER Calibration

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/learned-embedding-er-calibration` · **Status:** empirically-open

## 1. Problem Statement

Modern entity resolution (ER) encodes records into learned vector **embeddings** $\phi(r) \in \mathbb{R}^d$ (via DeepMatcher, Ditto, transformer/LM encoders) and decides whether $a$ and $b$ co-refer from a similarity $s(a,b) = g(\phi(a), \phi(b))$. In practice a **single global threshold** $\tau$ converts $s$ into a binary match decision. The problem: produce **calibrated, threshold-free** matching decisions whose scores are interpretable as **probabilities of co-reference**, with a **controllable, predictable precision–recall tradeoff** — i.e., choosing an operating point gives the *guaranteed* (or tightly estimated) precision/recall on the deployment distribution, including under **distribution shift** between training and target corpora.

Variants: (1) **calibration** — make $\Pr[\text{match} \mid s]$ well-estimated (low ECE / proper-scoring loss); (2) **risk control** — output a decision set with a **distribution-free** guarantee that precision (or FDR) $\ge 1-\alpha$; (3) **operating-point selection** — pick thresholds (or abstain) to hit a target P/R with finite-sample validity; (4) **transitivity-consistent** decisions — calibrated pairwise scores that survive clustering/transitive closure.

## 2. Mathematical Foundations

ER is binary classification over pairs with a Fellegi–Sunter probabilistic semantics: ideal score $s^\star(a,b) = \Pr[\text{match}\mid a,b]$. **Calibration**: a scorer is calibrated if $\Pr[Y=1 \mid s(X)=p] = p$; measured by **Expected Calibration Error** and proper scoring rules (Brier, log-loss) which decompose into calibration + refinement (DeGroot–Fienberg). Post-hoc methods: **Platt scaling**, **isotonic regression**, **temperature scaling** (Guo et al., ICML 2017 — modern nets are systematically *over*confident).

Distribution-free guarantees come from **conformal prediction / risk control**: **Conformalized risk control** and **Learn-then-Test** (Angelopoulos–Bates et al.) certify, with exchangeability, that a chosen threshold controls a monotone risk (e.g., FDR/precision) at level $\alpha$ with high probability — *finite-sample, model-agnostic*. The transitivity issue is graph-structured: pairwise probabilities must be reconciled with the constraint that co-reference is an **equivalence relation**, linking to **correlation clustering** and probabilistic-soft-logic consistency. The hard, *empirically open* part is **calibration transfer under covariate/label shift** (Tibshirani et al. weighted conformal), since ER deployment corpora rarely match training blocks.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** **Ditto** (Li et al., VLDB 2020) and LM/transformer matchers dominate F1 benchmarks; **DeepMatcher** (Mudgal et al., SIGMOD 2018) set the deep-learning baseline; recent **LLM-based matchers** (in-context / fine-tuned) push zero/few-shot F1. These report F1 but rarely calibration or risk-controlled operating points.
- **Theory/ML-SOTA.** **Temperature scaling** + **conformal risk control** are the principled tools; their application to ER is recent and partial. **Calibrated correlation clustering** for transitivity consistency is nascent.

## 4. Upper Bound

Achievable guarantees (upper bound on what is *provable*): given an **exchangeable** calibration set of size $n$, conformal risk control / Learn-then-Test certifies a threshold with precision $\ge 1-\alpha$ at confidence $1-\delta$ with the finite-sample slack $O(\sqrt{\log(1/\delta)/n})$ — **distribution-free**, model-agnostic. Temperature scaling reduces ECE to near-zero on i.i.d. test data with one parameter. Under **known** likelihood-ratio shift, weighted conformal preserves the guarantee. Model: PAC / exchangeability (statistical), no computational obstruction (post-hoc fitting is convex/poly-time).

## 5. Lower Bound

The barriers are **statistical/information-theoretic**, not computational. (1) **No distribution-free calibration**: without exchangeability (i.e., under unknown distribution shift between training blocks and deployment), no method can guarantee calibrated probabilities — a **no-free-lunch** impossibility (Barber, "limits of distribution-free guarantees"; Gupta–Podkopaev–Ramdas show conditional calibration needs distributional assumptions). (2) **Class imbalance**: ER is extremely imbalanced (matches are $O(n)$ among $O(n^2)$ pairs), so estimating precision to additive $\epsilon$ at fixed recall needs $\Omega(1/(\epsilon^2 \pi))$ labeled positives ($\pi$ = match prevalence) — a sample-complexity floor. (3) Transitivity reconciliation reduces to **correlation clustering**, which is **APX-hard**. Model: information-theoretic sample-complexity, hardness of approximation.

## 6. The Gap

**Empirically open.** On i.i.d. data the tools exist (temperature scaling + conformal risk control close the gap), but ER's defining conditions — **block-induced distribution shift**, **severe imbalance**, and **transitivity** — break the exchangeability assumptions those guarantees rest on. There is no method that *simultaneously* (a) calibrates under realistic ER shift, (b) gives a finite-sample precision/recall guarantee at a chosen operating point, and (c) stays consistent after transitive closure. The gap is between strong i.i.d. guarantees and the absence of any deployment-distribution guarantee; closing it needs shift-robust calibration with mild, ER-realistic assumptions plus imbalance-aware sample-complexity analysis — currently an experimental, benchmark-driven frontier.

## 7. Current Research (as of June 2026)

Active directions: **conformal ER** applying risk control to matcher thresholds with FDR/precision targets; **weighted/robust conformal** for blocking-induced shift. *(frontier — verify)* **LLM-matcher calibration** — confidence extraction and verbalized-probability calibration for in-context ER, plus selective prediction / abstention. *(frontier — verify)* **Calibrated clustering** that propagates pairwise uncertainty through correlation-clustering with guarantees. Groups: Doan/
Govind (Wisconsin, Magellan), Tang/Li (HKUST, Ditto), Angelopoulos–Bates–Jordan (Berkeley, conformal), Ramdas (CMU, calibration limits), Stoyanovich (NYU, responsible ER).

## 8. Future Work

- **Shift-robust calibration** for block-mismatched deployment corpora.
- Finite-sample **precision/recall certificates** at chosen operating points under imbalance.
- **Transitivity-consistent** calibrated clustering with end-to-end guarantees.
- Standard **calibration+risk benchmarks** for ER (beyond F1) and LLM-matcher confidence.

## 9. Key References

- **[Foundational]** C. Guo, G. Pleiss, Y. Sun, K. Weinberger. *On calibration of modern neural networks.* ICML, 2017. — [arXiv](https://arxiv.org/abs/1706.04599)
- **[SOTA]** A. Angelopoulos, S. Bates, et al. *Conformal risk control* / *Learn then Test: Calibrating predictive algorithms to achieve risk control.* 2021–2023. — [arXiv](https://arxiv.org/abs/2110.01052)
- **[SOTA]** Y. Li, J. Li, Y. Suhara, A. Doan, W.-C. Tan. *Deep entity matching with pre-trained language models (Ditto).* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2004.00584)
- **[SOTA]** S. Mudgal et al. *Deep learning for entity matching: A design space exploration (DeepMatcher).* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196926)
- **[Foundational]** R. Tibshirani, R. Foygel Barber, E. Candès, A. Ramdas. *Conformal prediction under covariate shift.* NeurIPS, 2019. — [arXiv](https://arxiv.org/abs/1904.06019)
- **[Survey]** C. Bishop / A. Niculescu-Mizil, R. Caruana. *Predicting good probabilities with supervised learning.* ICML, 2005. — [DOI](https://doi.org/10.1145/1102351.1102430)

## 10. Worked Example

A matcher outputs similarity scores; we bin a calibration set into score buckets and compare predicted confidence to empirical match rate:

| bucket | mean score $\bar p$ | #pairs | #true matches | empirical acc |
|--------|------|--------|---------------|---------------|
| 0.8–1.0 | 0.90 | 100 | 70 | 0.70 |
| 0.6–0.8 | 0.70 | 100 | 50 | 0.50 |
| 0.4–0.6 | 0.50 | 100 | 45 | 0.45 |

**ECE** = $\sum_b \frac{n_b}{N}\,|\,\text{acc}_b - \bar p_b\,| = \tfrac{100}{300}(0.20+0.20+0.05) = 0.15$. The model is **overconfident** (acc $<$ score everywhere) — the Guo et al. signature.

**Conformal risk control for precision.** Target precision $\ge 0.90$, i.e. risk (FDR) $\le \alpha=0.10$. Sweep the threshold $\tau$ upward; on the calibration set pick the smallest $\tau$ whose empirical FDR plus finite-sample slack $O(\sqrt{\log(1/\delta)/n})$ stays $\le 0.10$. Here even the top bucket has FDR $0.30$, so no $\tau$ certifies $0.90$ precision — the matcher must **abstain** or be recalibrated. This is the core tension: high F1 yet no risk-controlled operating point.

---
*Part of the [DBMS Research catalog](../../README.md).*
