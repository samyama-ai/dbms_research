---
id: 17-approximate-query-processing/verifiable-aqp
title: "Verifiable and Trustworthy Approximations"
topic: 17-approximate-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Verifiable and Trustworthy Approximations

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/verifiable-aqp` · **Status:** open

## 1. Problem Statement
An AQP system returns an estimate $\hat{Q}$ together with an error guarantee — a confidence interval $[\hat{Q}-\varepsilon,\hat{Q}+\varepsilon]$ at level $1-\delta$, or a claimed relative-error bound. The trustworthiness problem asks: **can the user (or an auditor, or a downstream system) verify that the stated bound actually holds**, ideally without recomputing the exact answer? This splits into (i) *statistical validity* — does the CI have its nominal coverage, given finite samples, skew, and the chosen estimator? — and (ii) *cryptographic/protocol verifiability* — when the data or computation is outsourced (untrusted cloud, possibly adversarial data provider), can the system **prove** that the returned approximate answer and its bound are honestly derived from the committed data?

Variants: the **certification** variant produces a proof/certificate of the bound; the **decision** variant asks "does this returned interval cover the true answer with probability $\ge 1-\delta$?"; the **adversarial** variant assumes the data (or a malicious server) is chosen to *defeat* the guarantee — e.g. heavy-tailed values that break a CLT-based CI, or a server that biases samples. It is open: today's AQP bounds are largely *trust-me* CLT intervals with known failure modes, and no system gives end-to-end verifiable, adversary-robust error certificates.

## 2. Mathematical Foundations
Statistical validity rests on concentration. A sample-mean CI of half-width $z_{1-\delta/2}\,s/\sqrt{m}$ has nominal coverage *only asymptotically*; for skewed or heavy-tailed values the CLT under-covers, and the true coverage can be far below $1-\delta$ (the well-known "AQP CI under-coverage under skew"). **Distribution-free** alternatives — Hoeffding/Bernstein/empirical-Bernstein bounds, the bootstrap, and **conformal prediction** (which gives finite-sample, distribution-free coverage under exchangeability) — trade width for honesty. Self-normalized and Catoni/median-of-means estimators give robust CIs under only finite-variance assumptions, defending against heavy tails.

Cryptographic verifiability uses **authenticated data structures** and **verifiable computation**: the data owner commits to $R$ via a Merkle tree / vector commitment; the server returns $\hat{Q}$ plus a succinct proof (SNARK / IOP) that a sample of claimed size was drawn by a *committed, unbiased* procedure (verifiable randomness, e.g. a VRF, prevents the server from cherry-picking the sample) and that the estimator was applied correctly. Verification cost should be $o(n)$ — polylog with SNARKs — versus $O(n)$ for recomputation. The adversarial-sampling threat is exactly the *robust/adversarial streaming* model: the input may adapt to the synopsis's randomness, breaking guarantees that assumed oblivious data.

## 3. State of the Art (SOTA)
- **Statistical-SOTA:** Bootstrap-based CIs in `BlinkDB`/`VerdictDB`; diagnostic tests that *detect* when bootstrap/CLT CIs are unreliable (`Kleiner et al.` "Bag of Little Bootstraps", and AQP CI-validation diagnostics by Agarwal–Mozafari et al.). Empirical-Bernstein and conformal methods provide finite-sample coverage but are under-deployed in DBMS engines.
- **Systems/crypto-SOTA:** Authenticated query processing (`IntegriDB`, `vSQL`, verifiable SQL via SNARKs) certifies *exact* query results over committed data; extending this to *approximate* answers with certified error is largely unaddressed. Robust-streaming sketches (`Ben-Eliezer et al.`, PODS 2020) give adversary-resilient synopses but not user-facing certificates.

## 4. Upper Bound
Finite-sample, distribution-free CIs are achievable: empirical-Bernstein gives valid coverage in $O(m)$ time with width $O(\sigma\sqrt{\tfrac{\log(1/\delta)}{m}}+\tfrac{\log(1/\delta)}{m})$; conformal prediction gives exact $1-\delta$ coverage under exchangeability. Median-of-means yields sub-Gaussian-tail CIs under only finite variance. For verifiable computation, SNARK-based proofs verify the estimator + committed-sample provenance in **polylog($n$)** verifier time with $O(1)$ proof size (in the SNARK/IOP model), versus $O(n)$ recomputation — *modulo* an honest, unbiased committed sampling procedure enforced by verifiable randomness.

## 5. Lower Bound
There are hard limits. **Distribution-free relative-error** certification is impossible without assumptions: a single unseen large value can invalidate any sampling-based bound (information-theoretic; ties to the `MAX`/rare-event lower bounds). Against an **adaptive adversary**, oblivious sketches provably fail — robust streaming requires a $\sqrt{\text{flip-number}}$ / $\tilde\Omega$ space overhead (Ben-Eliezer et al.). Cryptographically, verifying an answer cannot be sound under standard assumptions if the sampling randomness is server-controlled — without verifiable randomness, the server can always produce a biased-but-"valid-looking" sample, so soundness reduces to the unforgeability of the commitment/VRF (computational assumption). Achieving $o(n)$ verification with information-theoretic (not computational) soundness is impossible in general.

## 6. The Gap
The pieces exist in isolation — robust CIs (statistics), authenticated exact queries (crypto), robust sketches (streaming) — but there is **no unified, deployable framework** delivering an approximate answer with a *certificate* that is simultaneously (a) finite-sample and distribution-aware, (b) sound against an adversarial data provider/server, and (c) verifiable in sublinear time. Whether such an end-to-end certificate is even efficiently attainable for general aggregates (vs. only sample-friendly ones) is genuinely open.

## 7. Current Research (as of June 2026)
Threads: conformal-prediction and betting-martingale CIs imported into AQP for distribution-free coverage; adversarially-robust sketches with user-exposed guarantees; SNARK/commitment-based verifiable analytics extended from exact to approximate answers; sampling with verifiable randomness (VRF-seeded) to block sample cherry-picking. *(frontier — verify)* A few 2025 prototypes combine robust streaming with verifiable computation to certify sketch outputs, but no peer-reviewed system gives end-to-end adversary-robust *and* sublinear-verifiable AQP error bounds.

## 8. Future Work
- A unified certificate format: statistically valid + cryptographically verifiable + adversary-robust error bounds.
- Distribution-aware coverage diagnostics built into query engines, surfaced to users.
- Verifiable, unbiased committed sampling protocols for outsourced/cloud AQP.

## 9. Key References
- **[Foundational]** Kleiner, A., Talwalkar, A., Sarkar, P., Jordan, M. *A Scalable Bootstrap for Massive Data (Bag of Little Bootstraps).* JRSS-B, 2014. — [DOI](https://doi.org/10.1111/rssb.12050)
- **[SOTA]** Ben-Eliezer, O., Jayaram, R., Woodruff, D., Yogev, E. *A Framework for Adversarially Robust Streaming Algorithms.* PODS, 2020. — [arXiv](https://arxiv.org/abs/2003.14265)
- **[SOTA]** Agarwal, S., Milner, H., Kleiner, A., Talwalkar, A., Jordan, M., Madden, S., Mozafari, B., Stoica, I. *Knowing When You're Wrong: Building Fast and Reliable Approximate Query Processing Systems.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2593667)
- **[Foundational]** Vovk, V., Gammerman, A., Shafer, G. *Algorithmic Learning in a Random World (Conformal Prediction).* Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)
- **[SOTA]** Zhang, Y., Genkin, D., Katz, J., Papadopoulos, D., Papamanthou, C. *vSQL: Verifying Arbitrary SQL Queries over Dynamic Outsourced Databases.* IEEE S&P, 2017. — [DOI](https://doi.org/10.1109/SP.2017.43)

## 10. Worked Example

**CLT CI under-covers; conformal does not.** Suppose true per-row values are heavy-tailed: $999$ rows $=1$ and $1$ row $=1000$, so $\mu = 1.999$. We sample $m=100$ rows and form the textbook $95\%$ CI $\bar x \pm 1.96\, s/\sqrt{m}$. With probability $(1-1/1000)^{100}\approx 0.905$ the sample contains **no** spike, giving $\bar x = 1$, $s = 0$, hence the interval $[1,1]$ — width zero, and it *misses* $\mu=1.999$. So actual coverage $\le 1 - 0.905 = 0.095 \ll 0.95$: gross under-coverage, the section-2 failure mode.

**Conformal alternative (split conformal).** Reserve a calibration set of $n_c = 200$ rows; compute nonconformity scores (here, residuals $|x_i - \bar x_{\text{train}}|$). Sort them; the prediction band uses the $\lceil (n_c+1)(1-\delta)\rceil = \lceil 201\cdot0.95\rceil = 191$st smallest score $q$. By exchangeability, $\Pr[\,|x_{\text{new}}-\bar x| \le q\,] \ge 1-\delta = 0.95$ for *any* distribution — finite-sample, distribution-free. The price is width: $q$ is driven up by the calibration spike, so the band is honestly wide rather than falsely tight. This is the width-for-honesty trade of section 4 — and it still cannot certify a *relative*-error `MAX` bound (section 5), since one unseen larger value remains unbounded.

---
*Part of the [DBMS Research catalog](../../README.md).*
