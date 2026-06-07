---
id: 24-privacy-encrypted-db/instance-optimal-local-sensitivity
title: "Instance-Optimal Local Sensitivity Release"
topic: 24-privacy-encrypted-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Instance-Optimal Local Sensitivity Release

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/instance-optimal-local-sensitivity` · **Status:** open

## 1. Problem Statement
Given a database instance $x \in \mathcal{D}^n$ and a real-valued query $f$, we wish to release an answer $\hat f(x)$ under $\varepsilon$- (or $(\varepsilon,\delta)$-) differential privacy whose error tracks the *local sensitivity* $\mathrm{LS}_f(x)$ — how much $f$ can change at *this* instance — rather than the worst-case *global sensitivity* $\mathrm{GS}_f = \max_x \mathrm{LS}_f(x)$. The catch: $\mathrm{LS}_f(x)$ is itself a function of the private data, so calibrating noise directly to it leaks information. The problem is to design mechanisms that are **instance-optimal** — within a small factor of the best error achievable by any private mechanism on each instance — *without* the calibration itself becoming a side channel.

Variants: (i) the **single-query** release (a join size, a regression coefficient); (ii) the **counting/aggregation** variant over relational queries with predicates; (iii) the **decision** variant (is $f(x)$ above a threshold?), where propose-test-release is natural. A self-contained statement requires fixing a benchmark: e.g., the *down-local-sensitivity* or *inverse-sensitivity* error profile.

## 2. Mathematical Foundations
Local sensitivity at distance $k$ is $\mathrm{LS}_f^{(k)}(x) = \max_{y: d(x,y)\le k}\mathrm{LS}_f(y)$, and the **smooth sensitivity** of Nissim–Raskhodnikova–Smith is
$$S^*_{f,\beta}(x) = \max_{k\ge 0} e^{-\beta k}\, \mathrm{LS}_f^{(k)}(x),$$
which yields a smooth upper bound that can be calibrated to safely. Adding noise from an admissible distribution (Cauchy, Laplace-Logistic, Student-$t$) scaled to $S^*/\varepsilon$ gives $(\varepsilon,\delta)$-DP. Alternatives include **Propose-Test-Release** (PTR), the **inverse-sensitivity mechanism** of Asi–Duchi (instance-optimal for a precise per-instance benchmark via the exponential mechanism over the *inverse-sensitivity* loss), and the **shifted-inverse**/quantile mechanisms for monotone functions. The relevant optimality notion is per-instance: a mechanism is instance-optimal if its error competes with $\min$ over mechanisms of error on each neighborhood, formalized through the **local minimax** risk and the inverse-sensitivity profile $\mathrm{len}_f(x,t)$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The **inverse-sensitivity mechanism** (Asi & Duchi, NeurIPS 2020) is instance-optimal up to constants for a large class of functions against the local-minimax benchmark. Smooth sensitivity (NRS, STOC 2007) remains the workhorse for medians, MSTs, and triangle/subgraph counts.
- For graph/relational counting, **Lipschitz extensions** and the **down-sensitivity** framework (Raskhodnikova–Smith; Kasiviswanathan et al.) give near-optimal degree-bounded subgraph counts.
- **Systems-SOTA:** Database query engines mostly avoid local sensitivity; PINQ/Flex (Johnson, Near, Song, VLDB 2018) uses **elastic sensitivity** (a tractable, smooth-ish upper bound on local sensitivity for SQL joins) shipped in production-style settings; **Chorus** and **GoogleDP/PipelineDP** rely on clipping + global sensitivity for scalability.

## 4. Upper Bound
For $1$-dimensional queries the inverse-sensitivity / shifted-inverse mechanisms achieve expected error $O\!\big(\mathrm{len}_f(x,\tilde O(1/\varepsilon))\big)$, instance-optimal to within constant factors against any $\varepsilon$-DP mechanism (pure-DP, central model). Smooth sensitivity attains error $O(S^*_{f,\beta}(x)/\varepsilon)$ with $\beta \approx \varepsilon$, holding in the central model under $(\varepsilon,\delta)$-DP. For elastic sensitivity (Flex), error is $O(\mathrm{ES}_f(x)/\varepsilon)$ with $\mathrm{ES}_f \ge \mathrm{LS}_f$, polynomially computable for SPJA SQL — an upper bound on cost, not an optimality guarantee.

## 5. Lower Bound
Per-instance lower bounds come from **local minimax**: no $\varepsilon$-DP mechanism can beat $\Omega(\mathrm{len}_f(x, c/\varepsilon))$ on instance $x$ (packing / coupling arguments). For median and quantiles these match the inverse-sensitivity upper bound. **Reconstruction / fingerprinting** lower bounds (Bun–Ullman–Vadhan; Dwork–Smith–Steinke–Ullman) bound how many low-sensitivity queries are answerable per dataset, capping budget reuse. For join-size queries, multiplicative-error lower bounds tie to the **AGM bound** structure: error cannot be below the contribution of the heaviest witness without violating DP.

## 6. The Gap
For univariate, monotone, and quantile queries the gap is essentially **closed** (constant-factor instance optimality). The genuinely **open** territory: (i) high-dimensional / multi-query release where smooth sensitivity is loose and inverse-sensitivity is computationally intractable; (ii) **relational join queries**, where elastic sensitivity is provably loose versus true local sensitivity and no instance-optimal, polynomial-time mechanism is known; (iii) reconciling instance optimality with **composition** across an optimizer's many sub-queries. Closing it requires either tractable approximations of $\mathrm{LS}^{(k)}$ for joins or a new benchmark that is both achievable and meaningful.

## 7. Current Research (as of June 2026)
Active threads: tighter **per-instance optimality for SQL** beyond elastic sensitivity, including residual-sensitivity and **sensitivity via the "boxed" / fractional-cover** view of joins (Dong, Yi, et al.) *(frontier — verify)*; instance-optimal **mean estimation** and the broader Asi–Duchi program (Stanford); **friendly-core / propose-test-release** advances (Tsfadia, Cohen, Nissim) for robust private statistics; and unifying instance optimality with the **shifted-inverse** mechanism for set-function/relational aggregates (Fang, Dong, Yi, SIGMOD 2022–2024 line). Groups: Duchi (Stanford), Smith/Steinke (BU/Google), Yi & Dong (HKUST), Near/Johnson (Vermont). A 2025–2026 frontier claim is near-instance-optimal private join-size estimation with polynomial-time sensitivity bounds for acyclic queries *(frontier — verify)*.

## 8. Future Work
- Polynomial-time, provably instance-optimal mechanisms for cyclic/relational join queries.
- High-dimensional inverse-sensitivity without exponential-time exponential-mechanism sampling.
- Side-channel-free calibration: prove the *budget cost of learning $\mathrm{LS}$* and fold it into the accounting.
- Instance optimality under **continual release** and under **local/shuffle** models.
- Practical libraries exposing smooth/elastic sensitivity to optimizers with composition-aware accounting.

## 9. Key References
- **[Foundational]** Nissim, Raskhodnikova, Smith. *Smooth Sensitivity and Sampling in Private Data Analysis.* STOC, 2007. — [DOI](https://doi.org/10.1145/1250790.1250803)
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[SOTA]** Asi, Duchi. *Instance-Optimality in Differential Privacy via Approximate Inverse Sensitivity Mechanisms.* NeurIPS, 2020. — [NeurIPS](https://proceedings.neurips.cc/paper/2020/hash/a267f936e54d7c10a2bb70dbe6ad7a89-Abstract.html)
- **[SOTA]** Johnson, Near, Song. *Towards Practical Differential Privacy for SQL Queries (Elastic Sensitivity / Flex).* PVLDB, 2018. — [DOI](https://doi.org/10.1145/3187009.3177733) · [arXiv](https://arxiv.org/abs/1706.09479)
- **[SOTA]** Fang, Dong, Yi. *Shifted Inverse: A General Mechanism for Monotonic Functions under User Differential Privacy.* SIGMOD/CCS line, 2022–2023. — [DBLP search](https://dblp.org/search?q=Shifted+Inverse+A+General+Mechanism+for+Monotonic+Functions+under+User+Differential+Privacy)
- **[Survey]** Vadhan. *The Complexity of Differential Privacy.* In *Tutorials on the Foundations of Cryptography*, 2017. — [DOI](https://doi.org/10.1007/978-3-319-57048-8_7)

## 10. Worked Example

Release the **median** of a salary dataset under $\varepsilon$-DP. Take $n=7$ sorted values (in $\$$k):
$$x = (40,\ 42,\ 45,\ 50,\ 51,\ 52,\ 300).$$
The median is $x_{(4)} = 50$. Global sensitivity is huge: a single record can be any value in $[0,\infty)$, so $\mathrm{GS}_{\text{med}}$ is unbounded (or the full range) — naive Laplace noise is useless.

**Local sensitivity** only looks at *this* instance: changing one point moves the median at most to a neighboring order statistic, so $\mathrm{LS}(x)=\max(x_{(4)}-x_{(3)},\,x_{(5)}-x_{(4)})=\max(50-45,\,51-50)=5$. Far smaller than global.

But $\mathrm{LS}$ itself is private, so we use **smooth sensitivity** $S^*_{\beta}(x)=\max_{k\ge0} e^{-\beta k}\mathrm{LS}^{(k)}(x)$. At distance $k$, $\mathrm{LS}^{(k)}$ can grow (e.g., $\mathrm{LS}^{(1)}$ uses $x_{(3)},x_{(6)}$ giving $\max(50-45,52-50)=5$; larger $k$ eventually reaches the $300$ gap). With $\beta=\varepsilon/2$ and $\varepsilon=1$ the geometric decay caps the smoothed value near $S^*\approx 5$–$8$. We then add Cauchy noise scaled to $S^*/\varepsilon$, giving error $\approx \$6$k — versus unbounded error from global sensitivity. The instance-optimal benchmark $\mathrm{len}_{\text{med}}(x,1/\varepsilon)$ matches this up to constants.

---
*Part of the [DBMS Research catalog](../../README.md).*
