---
id: 07-storage-buffer/caching-with-predictions
title: "Caching with Predictions: Robustness vs Consistency"
topic: 07-storage-buffer
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Caching with Predictions: Robustness vs Consistency

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/caching-with-predictions` · **Status:** partially-solved

## 1. Problem Statement

A buffer-pool replacement policy may be handed **predictions** from an ML oracle — most usefully, a predicted *next-access time* (or reuse distance) for each page, mimicking Belady's clairvoyant optimum. The oracle can be excellent (then we want to nearly match the offline optimum) or arbitrarily wrong (then we must not do worse than a robust classical policy like LRU/marking). This is the **algorithms-with-predictions** (a.k.a. *learning-augmented*) paradigm applied to caching.

Two formal desiderata, due to Lykouris–Vassilvitskii, govern the design:

- **Consistency:** competitive ratio when predictions are perfect — ideally close to $1$ (Belady-optimal).
- **Robustness:** worst-case competitive ratio when predictions are adversarially wrong — should stay $O(\log k)$ (the randomized paging optimum) or $k$ (deterministic), never unbounded.

**Decision/optimization variant:** given a prediction error budget $\eta$ (e.g., $\ell_1$ error of predicted vs true next-access times), design a policy whose competitive ratio degrades *gracefully and smoothly* in $\eta$ — interpolating between the consistency and robustness endpoints. The research target is the **Pareto frontier**: the achievable region of (consistency $c$, robustness $r$) pairs, and the optimal *error-dependent* ratio $\text{CR}(\eta)$.

## 2. Mathematical Foundations

The setting is online **paging**: cache size $k$, request sequence $\sigma$; cost = number of misses; benchmark = offline optimum $\text{OPT}$ (Belady's furthest-in-future is optimal offline). A policy is $\rho$-competitive if $\text{cost} \le \rho\cdot\text{OPT} + O(1)$.

Predictions are per-request *next-arrival times* $\hat{h}_i$ vs truth $h_i$; the natural error measure is $\eta = \sum_i |\hat{h}_i - h_i|$ (or an $\ell_1$ over predicted reuse distances). A learning-augmented policy seeks

$$\text{CR}(\eta) \;\le\; \min\Bigl\{\, r,\; c + O\!\bigl(g(\eta/\text{OPT})\bigr)\Bigr\},$$

with $c\to 1$ as $\eta\to 0$ (consistency) and a hard cap $r$ (robustness). Key foundations: **Belady (1966)** for the offline optimum; **Sleator–Tarjan (1985)** for $k$-competitiveness and the marking framework; **Fiat et al.** $H_k=\Theta(\log k)$ randomized lower bound; and the **PredictiveMarking / robustify-via-combiner** technique that runs a prediction-following policy *and* a marking policy and switches/combines to inherit both endpoints (a deterministic-to-randomized "combiner" gives provable robustness with $O(1)$ loss). Lower bounds use the same adversary as classical paging plus a budget on how much error the adversary may inject.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Lykouris–Vassilvitskii (ICML'18; JACM'21) introduced caching-with-predictions and the consistency/robustness framing. Rohatgi (SODA'20) and Wei (APPROX'20) sharpened the **error-dependent** ratio to roughly $O(1 + \min\{\eta/\text{OPT},\,\log k\})$ and gave near-tight bounds; Antoniadis–Coester–Eliáš–Polak–Simon and Bansal et al. extended to weighted/metric caching and improved the Pareto tradeoffs. The general **robustification combiner** (Antoniadis et al.) yields $(1+\epsilon)$-consistency with $O(\log k / \epsilon)$-style robustness. **Systems-SOTA:** **LRB** (Learning Relaxed Belady, NSDI'20) for CDN caches; **Parrot / imitation-learning of Belady** (DeepMind, ICML'20) for CPU caches; **CACHEUS** (FAST'21) adaptively combines experts; production CDN admission (Akamai/Meta) uses learned size/popularity signals. These rarely carry the theoretical robustness guarantee end-to-end.

## 4. Upper Bound

The best-known learning-augmented upper bound for unweighted paging is an **error-dependent competitive ratio** of $O\!\left(1 + \min\{\eta/\text{OPT},\ \log k\}\right)$ (randomized; Rohatgi SODA'20, Wei APPROX'20), simultaneously **$1$-consistent** (up to lower-order terms) and **$O(\log k)$-robust** — i.e., it matches Belady when predictions are perfect and the randomized paging optimum when they are useless, degrading smoothly between. Combiner constructions achieve any target $(1+\epsilon)$-consistency at the cost of robustness $O(\log k/\epsilon)$, tracing the upper Pareto curve. For **weighted/metric** caching the upper bounds are weaker (polylog-in-$k$ robustness via the metrical-task-systems machinery) and not yet matching.

## 5. Lower Bound

Classical paging lower bounds are inherited as the **robustness floor**: no policy can beat $k$ (deterministic) or $H_k=\Theta(\log k)$ (randomized) when predictions are adversarial — these are the unavoidable endpoints (Sleator–Tarjan; Fiat et al.). The **consistency–robustness tradeoff** itself has a lower bound: you *cannot* be simultaneously $1$-consistent and $o(\log k)$-robust — any policy with near-optimal behavior under perfect predictions must pay $\Omega(\log k)$ robustness, and more generally the achievable $(c,r)$ Pareto region is bounded away from the ideal corner (Wei–Zhang and follow-ups). The **error-dependence** is also tight up to constants: $\Omega(\min\{\eta/\text{OPT}, \log k\})$ is forced, so the SODA'20-era bound is essentially optimal for unweighted paging. These are competitive-analysis / online lower bounds (no NP-hardness needed).

## 6. The Gap

For **unweighted paging** the gap is **essentially closed**: matching upper/lower error-dependent bounds and a characterized consistency/robustness Pareto frontier — hence the *partially-solved* status. What remains open: (1) **weighted and metric caching** with predictions, where robustness upper bounds are polylog and not tight; (2) the right **error measure** — $\ell_1$ on next-access times is analytically convenient but may not match what real learned predictors get wrong (popularity vs timing errors); (3) **multiple/feature predictions** (predicting reuse *distribution*, not a point) and how their error composes; (4) the **theory–systems gap**: LRB/Parrot-style systems lack the proven robustness cap, and the provably robust algorithms have not been shown to match them empirically at CDN/buffer-pool scale.

## 7. Current Research (as of June 2026)

- **Beyond worst-case error models:** distributional / smoothed prediction error and per-request confidence, so the policy trusts the oracle adaptively *(frontier — verify)*.
- **Weighted & metric learning-augmented caching** closing the robustness gap (Coester, Antoniadis, Polak and collaborators).
- **Learned-Belady at scale** in real buffer pools and CDNs with built-in fallbacks (Meta/Akamai; Stanford/MIT systems groups) *(frontier — verify)*.
- **Multi-prediction and untrusted-oracle composition** — combining several imperfect predictors with provable guarantees.
- Predictions for **write-back / admission** (not just eviction), extending the paradigm across the buffer manager.

## 8. Future Work

- Tight bounds for weighted/metric/file caching with predictions.
- Robustness under realistic ML-error structure (timing vs popularity), not adversarial $\ell_1$.
- End-to-end systems that ship the consistency/robustness guarantee, validated against LRB/CACHEUS.
- Joint prediction of eviction *and* prefetch/admission with a unified competitive analysis.
- Sample-complexity: how much workload data is needed to train an oracle good enough to beat LRU robustly.

## 9. Key References

- **[Foundational]** László A. Bélády. *A Study of Replacement Algorithms for a Virtual-Storage Computer.* IBM Systems Journal, 1966. — [DOI](https://doi.org/10.1147/sj.52.0078)
- **[Foundational]** Daniel Sleator, Robert Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** Thodoris Lykouris, Sergei Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML 2018 / JACM, 2021. — [DOI](https://doi.org/10.1145/3447579)
- **[SOTA]** Dhruv Rohatgi. *Near-Optimal Bounds for Online Caching with Machine Learned Advice.* SODA, 2020. — [arXiv](https://arxiv.org/abs/1910.12172)
- **[SOTA]** Alexander Wei. *Better and Simpler Learning-Augmented Online Caching.* APPROX, 2020. — [arXiv](https://arxiv.org/abs/2005.13716)
- **[SOTA]** Zhenyu Song, Daniel S. Berger, Kai Li, Wyatt Lloyd. *Learning Relaxed Belady for Content Distribution Network Caching.* NSDI, 2020. — [USENIX](https://www.usenix.org/conference/nsdi20/presentation/song)
- **[Survey]** Michael Mitzenmacher, Sergei Vassilvitskii. *Algorithms with Predictions.* CACM, 2022. — [DOI](https://doi.org/10.1145/3528087)

## 10. Worked Example

Cache size $k = 2$, request sequence $\sigma = A\,B\,C\,A\,C\,B$. At each request the oracle gives a predicted next-arrival time $\hat h_i$.

Belady (offline, ground truth): start $\{A,B\}$. Request $C$ (miss): next uses are $A$ at position 4, $B$ at position 6 — evict $B$ (farther). Cache $\{A,C\}$. Then $A$ hit, $C$ hit, $B$ miss (evict $A$, no future use). **Total misses after warm-up: 2.**

A prediction-following policy that *trusts* $\hat h$: if predictions are perfect it reproduces Belady's choice (evict $B$ at the $C$ miss) → 2 misses, so **consistency $\to 1$**.

Now make the oracle adversarial: it predicts $A$ is used soonest, so the policy evicts $A$ instead of $B$ at the $C$ miss → cache $\{B,C\}$, then $A$ at position 4 is a miss too → 3+ misses. A robustifying combiner caps this by also running a marking policy and never trailing it by more than a factor, guaranteeing $O(\log k)$ robustness. With $k=2$ that bound is $H_2 = 1 + \tfrac12 = 1.5$, so the worst case stays bounded — the consistency/robustness interpolation $\mathrm{CR}(\eta) \le \min\{r,\, c + O(\eta/\mathrm{OPT})\}$ in action.

---
*Part of the [DBMS Research catalog](../../README.md).*
