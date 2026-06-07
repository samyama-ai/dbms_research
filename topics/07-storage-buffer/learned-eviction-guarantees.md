---
id: 07-storage-buffer/learned-eviction-guarantees
title: "Learned Buffer Eviction with Worst-Case Guarantees"
topic: 07-storage-buffer
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Learned Buffer Eviction with Worst-Case Guarantees

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/learned-eviction-guarantees` · **Status:** open

## 1. Problem Statement
A learned eviction policy uses a predictor (ML model, heuristic, or oracle) that, for each resident page, estimates its **next-reuse time** (or a reuse probability), and evicts greedily by predicted Belady. When predictions are accurate this approaches the offline optimum; when they are adversarially wrong, naive trust can be unboundedly bad.

The problem: design a buffer-eviction algorithm that is simultaneously
- **consistent:** if predictions are perfect, it is $(1+o(1))$-competitive (matches Belady), and degrades gracefully with prediction error $\eta$;
- **robust:** regardless of prediction quality, it never exceeds the classical worst-case guarantee — $O(\log k)$ randomized (or $k$ deterministic) competitive.

Formally, we want an algorithm $\text{ALG}$ with $\text{ALG}(\sigma)\le \min\{\,(1+\epsilon)\,g(\eta)\cdot\text{OPT},\; c_{\text{wc}}\cdot\text{OPT}\,\}$ where $g$ is a smooth error function and $c_{\text{wc}}$ is the prediction-free optimum. Variants: deterministic vs. randomized; prediction of *next access time* vs. *next-access-among-resident* vs. binary "reused-soon"; and the **Pareto frontier** question — what robustness–consistency tradeoffs are achievable?

## 2. Mathematical Foundations
This is the *algorithms-with-predictions* (learning-augmented) framework.

**Prediction error.** With per-request predicted next-use $h(p)$ vs. true $\tau(p)$, define $\eta = \sum_t |h_t - \tau_t|$ (an $\ell_1$ error) or a classification error count.

**Belady with predictions.** Lykouris–Vassilvitskii (ICML 2018; JACM 2021) gave the first learning-augmented caching result: a *Predictive Marking* algorithm with competitive ratio
$$O\!\Big(\min\Big\{\,1+\tfrac{\eta}{\text{OPT}},\ \log k\,\Big\}\Big),$$
combining a marking skeleton (for robustness) with predictions inside each phase (for consistency).

**Consistency/robustness.** An algorithm is $\beta$-consistent if $\le \beta\cdot\text{OPT}$ when predictions are perfect, and $\gamma$-robust if $\le \gamma\cdot\text{OPT}$ always. There is a **provable tradeoff frontier**: you cannot have $\beta=1$ and $\gamma=O(1)$ simultaneously for online caching; Pareto-optimal $(\beta,\gamma)$ curves have been characterized for paging.

**Lower-bound machinery.** Yao's principle and the $H_k$ randomized paging lower bound bound the robust side; adversarial-prediction constructions bound the consistent side.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Lykouris–Vassilvitskii (JACM 2021) established the $O(\min\{1+\eta/\text{OPT},\log k\})$ result; Rohatgi (SODA 2020) and Wei (APPROX 2020) improved the error dependence to $O(1+\min\{\frac{\eta}{k\cdot\text{OPT}}\log k,\log k\})$-type bounds; Antoniadis et al. and follow-ups gave Pareto-optimal consistency–robustness tradeoffs and handled weighted/general caching with predictions (ICML/NeurIPS 2020–2023).

**Systems-SOTA:** Hawkeye (Jain–Lin, ISCA 2016) and Glider learn Belady's decisions for CPU caches; LRB (Song et al., NSDI 2020) learns reuse for CDN caching; Parrot and learned-index-adjacent eviction in DB buffer pools. These show large practical gains but **no worst-case guarantee** — exactly the gap this problem targets.

## 4. Upper Bound
Randomized, fault/unit-cost model: $O(\min\{1+\eta/\text{OPT},\ \log k\})$ (Lykouris–Vassilvitskii), improved to error-per-page-scaled bounds (Rohatgi; Wei). Pareto-optimal $(1+\epsilon)$-consistent / $O(\frac{\log(1/\epsilon)}{\epsilon})$-robust tradeoffs are achievable. For weighted/general caching with predictions, $O(1)$-consistent and $O(\log k)$-robust algorithms exist.

## 5. Lower Bound
Robustness inherits the randomized paging lower bound $\Omega(\log k)$ (Fiat et al. 1991) and deterministic $k$. On the tradeoff: any $1$-consistent online algorithm must have $\gamma=\Omega(\log k)$ robustness (no free lunch); more generally a Pareto lower bound shows the consistency–robustness curve cannot be beaten (Wei–Zhang; Antoniadis et al.). Predictions cannot circumvent the information-theoretic randomized barrier in the worst case.

## 6. The Gap
For unit-cost paging the consistency–robustness Pareto frontier is essentially **closed**. It remains **open** to (a) obtain the tight error function for *general/weighted caching with variable size* (ties to `weighted-caching-variable-size`), (b) handle *noisy probabilistic* predictions with matching bounds, and (c) close the gap between theory and the deployed learned systems (LRB, Hawkeye) which lack any robustness fallback. A practical, low-overhead policy that provably interpolates with the *measured* error of a real reuse predictor is missing.

## 7. Current Research (as of June 2026)
- **Algorithms-with-predictions** for caching: tighter error models, multiple/portfolio predictors, and *distributionally robust* variants (Antoniadis, Coester, Lindermayr, Megow; ICML/NeurIPS 2023–2025) *(frontier — verify)*.
- Marrying learned reuse predictors (LRB-style) with marking/primal-dual fallbacks for deployable guarantees *(frontier — verify)*.
- Predictions for **write-back and multi-tier** eviction, connecting to cost-aware caching.

## 8. Future Work
Guarantees under realistic (probabilistic, drifting) predictors; sample-complexity/learning-theoretic bounds for *learning* the predictor itself; integration with online drift tracking; weighted/variable-size tight bounds; hardware-cache vs. DB-buffer-pool transfer of these results.

## 9. Key References
- **[Foundational]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML 2018 / JACM 2021. — [arXiv](https://arxiv.org/abs/1802.05399)
- **[SOTA]** D. Rohatgi. *Near-Optimal Bounds for Online Caching with Machine Learned Advice.* SODA 2020. — [arXiv](https://arxiv.org/abs/1910.12172)
- **[SOTA]** A. Wei. *Better and Simpler Learning-Augmented Online Caching.* APPROX 2020. — [arXiv](https://arxiv.org/abs/2005.13716)
- **[SOTA]** A. Antoniadis, C. Coester, M. Elias, et al. *Online Metric Algorithms with Untrusted Predictions.* ICML 2020. — [PMLR](https://proceedings.mlr.press/v119/antoniadis20a.html)
- **[SOTA]** Z. Song, D. Berger, K. Li, et al. *Learning Relaxed Belady for Content Distribution Network Caching (LRB).* USENIX NSDI 2020. — [USENIX](https://www.usenix.org/conference/nsdi20/presentation/song)
- **[Foundational]** A. Jain, C. Lin. *Back to the Future: Leveraging Belady's Algorithm for Improved Cache Replacement (Hawkeye).* ISCA 2016. — [DOI](https://doi.org/10.1109/ISCA.2016.17)
- **[Survey]** M. Mitzenmacher, S. Vassilvitskii. *Algorithms with Predictions.* CACM 2022. — [DOI](https://doi.org/10.1145/3528087)

## 10. Worked Example

Cache size $k=2$, request sequence $\sigma = a,b,c,a,c,b,a$.

**Belady (OPT, perfect predictions).** On the miss for $c$ (cache $\{a,b\}$), evict the page used farthest in future: $a$ next at position 4, $b$ next at position 6, so evict $b$. Resulting misses: $a,b,c$ (cold), then $b$ at position 6 — total **4 misses**.

**Trusting a bad predictor.** Suppose the predictor wrongly claims $a$ is never reused. On the $c$-miss it evicts $a$; then $a$ at position 4 misses, must evict $c$ or $b$, cascading — **6 misses**, $1.5\times$ OPT.

**Predictive Marking (robust).** The marking skeleton marks $a,b$ when hit; a phase evicts only unmarked pages. Even following the bad prediction inside a phase, the marking invariant caps the competitive ratio at $O(\log k)=O(\log 2)$, so it cannot blow past the prediction-free bound. With error $\eta = \sum_t|h_t-\tau_t|$, the guarantee is
$$\text{ALG}\le O\!\big(\min\{1+\tfrac{\eta}{\text{OPT}},\ \log k\}\big)\cdot\text{OPT},$$
interpolating between Belady (small $\eta$) and classical paging (large $\eta$).

---
*Part of the [DBMS Research catalog](../../README.md).*
