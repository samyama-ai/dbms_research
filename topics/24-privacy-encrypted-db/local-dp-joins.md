---
id: 24-privacy-encrypted-db/local-dp-joins
title: "Local-DP SQL Analytics with Joins"
topic: 24-privacy-encrypted-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Local-DP SQL Analytics with Joins

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/local-dp-joins` · **Status:** open

## 1. Problem Statement

In the **local model** of differential privacy (LDP) there is **no trusted curator**: each user perturbs their own data before it ever leaves their device, and the aggregator sees only randomized reports. LDP is well understood for single-table statistics (frequency estimation, heavy hitters, means). The open question: **can useful join / multi-table SQL analytics be done under LDP?** A join correlates records that may belong to *different users* (or different tables held by different parties), so the join *key* and the *cross-record relationship* — exactly what must be computed — are precisely what each user is trying to hide. The problem is whether non-trivial accuracy for `COUNT(*)`-over-join, multi-table aggregates, and graph/relationship statistics is even *achievable* in LDP, and if so with what error, vs. requiring the **shuffle** or **MPC/secure-aggregation** middle ground.

Variants:
- **Feasibility (decision):** is there *any* LDP mechanism with $o(\text{trivial})$ error for an inner join count?
- **Optimization (counting):** minimal-error LDP estimation of join-size / multi-table aggregates.
- **Model-relaxation:** what does the **shuffle model** or single-message MPC buy over pure LDP for joins?

## 2. Mathematical Foundations

LDP: a randomizer $R$ is $\varepsilon$-LDP if for all inputs $x,x'$ and outputs $y$, $\Pr[R(x)=y]\le e^{\varepsilon}\Pr[R(x')=y]$. Single-table frequency estimation has error $\Theta(\sqrt{n}/\varepsilon)$ (vs. $\Theta(1/\varepsilon)$ central), the canonical **$\sqrt{n}$ gap**. A join involves a **bilinear / correlation functional** $\sum_{i,j}\mathbb{1}[k_i=k_j]$ across users; estimating such second-order/relationship quantities in LDP is governed by lower bounds for **distribution-correlation** and **inner-product** estimation, which are far harder than linear statistics. The **shuffle model** (Erlingsson–Feldman–Mironov–Raghunathan–Talwar–Thakurta "ESA"; Cheu–Smith–Ullman–Zeber–Zhilyaev) amplifies LDP to near-central error for *some* functionals via anonymity, but join keys break anonymity. **Secure aggregation / MPC** can emulate the central curator for specific aggregates. Graph/relationship analytics use **edge-LDP vs. node-LDP** (Qin et al.; Imola–Murakami–Chaudhuri): triangle/subgraph counting under edge-LDP is the closest studied analog of a self-join.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Subgraph counting under **edge-LDP** (Imola, Murakami, Chaudhuri, USENIX Security 2021/2022) gives multi-round LDP triangle/$k$-star estimators — the strongest positive results for join-like relationship statistics, but with large error and extra interaction. Shuffle-model amplification (Feldman–McMillan–Talwar; Balle et al.) gives near-central error for *sums*, not joins.
- **Systems-SOTA:** Industrial LDP (Google RAPPOR, Apple, Microsoft Telemetry) is single-table only. No deployed system does LDP joins; multi-party join analytics in practice uses **MPC/private set intersection** (e.g., private join-and-compute) rather than pure LDP.

## 4. Upper Bound

For single-table aggregates, $\varepsilon$-LDP frequency/mean estimation achieves $O(\sqrt{n}/\varepsilon)$ error (optimal). For **edge-LDP triangle counting**, interactive estimators attain $O(n^{?})$-relative error with two-round protocols (Imola et al.), and the shuffle model can recover near-central error for *decomposable sums* over single tables. For genuine cross-table inner-join *counts* in **pure LDP with one message**, no mechanism beats roughly the trivial $\Theta(n)$-scale error in the worst case — i.e., **no useful general upper bound is known**.

## 5. Lower Bound

LDP imposes a fundamental $\Omega(\sqrt{n})$ penalty even for single-bit means (Beimel–Nissim–Omri; Chan–Shi–Song; Duchi–Jordan–Wainwright via local Fano/Assouad). For **interactive vs. non-interactive** LDP, separations show some tasks *require* many rounds (Joseph–Mao–Neel–Roth). For join/correlation functionals the lower bounds are stronger: estimating pairwise-correlation/inner-product type quantities has error scaling like $\Omega(\sqrt{n}/\varepsilon)$ *per estimated relationship*, and worst-case join-size estimation in single-message LDP is **information-theoretically infeasible** to non-trivial accuracy (a communication/Fano argument: each user's key is hidden, so the cross-user coincidence count is unidentifiable). These results strongly suggest pure LDP joins are impossible in general.

## 6. The Gap

**Genuinely open.** We have (a) strong LDP lower bounds for correlation-type functionals and (b) only narrow positive results (edge-LDP subgraph counting, shuffle-model sums) — but **no general characterization** of which multi-table/join workloads are LDP-feasible, nor tight error bounds for those that are. The gap is between "single-table LDP is solved" and "joins seem impossible but lack a clean impossibility theorem covering all variants." Closing it needs either (i) a general LDP/shuffle join impossibility (info-theoretic), or (ii) a surprising positive protocol (likely interactive or shuffle/MPC-assisted) with provable accuracy.

## 7. Current Research (as of June 2026)

- Shuffle-model and **single-server MPC + DP** hybrids for two-table joins / private-join-and-compute with DP output *(frontier — verify)*.
- Multi-round edge-/node-LDP graph analytics pushing subgraph-counting accuracy (Murakami, Imola, Cormode groups) *(frontier — verify)*.
- Characterizing the *interactivity hierarchy* for LDP relational queries — which joins need how many rounds *(frontier — verify)*.

## 8. Future Work

- A general impossibility/feasibility dichotomy for LDP multi-table workloads.
- Shuffle-model join protocols with central-like error for restricted (e.g., FK, low-degree) joins.
- Combining LDP with PSI/secure-aggregation for practical private join analytics.
- Node-LDP (stronger) relationship statistics with usable accuracy.

## 9. Key References

- **[Foundational]** Kasiviswanathan, Lee, Nissim, Raskhodnikova, Smith. *What Can We Learn Privately? (Local model).* FOCS, 2008. — [DOI](https://doi.org/10.1109/FOCS.2008.27) · [arXiv](https://arxiv.org/abs/0803.0924)
- **[Foundational]** Duchi, Jordan, Wainwright. *Local Privacy and Statistical Minimax Rates.* FOCS, 2013. — [DOI](https://doi.org/10.1109/FOCS.2013.53) · [arXiv](https://arxiv.org/abs/1302.3203)
- **[Foundational]** Erlingsson, Pihur, Korolova. *RAPPOR: Randomized Aggregatable Privacy-Preserving Ordinal Response.* CCS, 2014. — [DOI](https://doi.org/10.1145/2660267.2660348) · [arXiv](https://arxiv.org/abs/1407.6981)
- **[SOTA]** Cheu, Smith, Ullman, Zeber, Zhilyaev. *Distributed Differential Privacy via Shuffling.* EUROCRYPT, 2019. — [DOI](https://doi.org/10.1007/978-3-030-17653-2_13) · [arXiv](https://arxiv.org/abs/1808.01394)
- **[SOTA]** Imola, Murakami, Chaudhuri. *Locally Differentially Private Analysis of Graph Statistics (Triangle/Subgraph Counting).* USENIX Security, 2021. — [USENIX](https://www.usenix.org/conference/usenixsecurity21/presentation/imola)
- **[SOTA]** Joseph, Mao, Neel, Roth. *The Role of Interactivity in Local Differential Privacy.* FOCS, 2019. — [arXiv](https://arxiv.org/abs/1904.03564) · [IEEE](https://ieeexplore.ieee.org/document/8948625/)
- **[Survey]** Cormode, Jha, Kulkarni, Li, Srivastava, Wang. *Privacy at Scale: Local Differential Privacy in Practice.* SIGMOD Tutorial, 2018. — [DOI](https://doi.org/10.1145/3183713.3197390)

## 10. Worked Example

Why an inner-join `COUNT(*)` is hard under LDP. Imagine $n=6$ users, each holding one private key value; the aggregator wants the **self-join size** $J=\sum_{i<j}\mathbb{1}[k_i=k_j]$ (number of matching pairs).

True data (hidden): keys $=(a,a,a,b,b,c)$. Matching pairs: $\binom{3}{2}=3$ among the $a$'s, $\binom{2}{2}=1$ among the $b$'s, $0$ for $c$ → $J=4$.

Each user must run an $\varepsilon$-LDP randomizer on her key *before* sending. With a domain of, say, 4 possible keys and $\varepsilon=1$, a randomized-response report is correct with probability $\frac{e^{\varepsilon}}{e^{\varepsilon}+3}=\frac{2.72}{5.72}\approx 0.48$ and otherwise uniform. The aggregator only sees noisy keys; the *coincidence* it must count is precisely what randomization destroys.

Concretely, estimating $J$ requires estimating the second moment $\sum_v p_v^2$ of the key distribution. LDP frequency estimation gives each $\hat p_v$ with standard error $\Theta(\sqrt{n}/\varepsilon)$; squaring and summing makes the variance of $\hat J$ scale like $\Theta(n)$ — the **same order as $J$ itself in the worst case**. So the signal-to-noise ratio stays $O(1)$: no nontrivial accuracy, matching the $\Omega(\sqrt{n})$ correlation lower bound that makes pure single-message LDP joins essentially infeasible.

---
*Part of the [DBMS Research catalog](../../README.md).*
