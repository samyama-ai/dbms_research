# DP for Streaming and Continuous Queries

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/dp-streaming-continuous` · **Status:** partially-solved

## 1. Problem Statement
A relational stream presents updates $u_1, u_2, \dots, u_T$ (insertions, or insertions+deletions in the *turnstile* model). At every step $t$ we must release an answer $a_t$ to a query — running count, sum, histogram, distinct count, or a SPJA aggregate — under differential privacy of the **entire output transcript** $(a_1,\dots,a_T)$. This is the **continual observation** model: neighboring streams differ in one element/event, and the *whole* sequence of releases must be private simultaneously. The objective is to minimize worst-case (or per-step) error as a function of $T$ (and the number of events), ideally matching information-theoretic lower bounds.

Variants: **event-level** vs **user-level** privacy (one event vs all events of one user); **bounded** vs **unbounded** $T$; **single** continuous query vs a workload; counting (decision/aggregation) vs optimization (selecting top-$k$ over time).

## 2. Mathematical Foundations
The canonical primitive is the **binary tree / dyadic mechanism** (Dwork–Naor–Pitassi–Rothblum; Chan–Shi–Song, 2010) for continual counting: decompose each prefix sum into $O(\log T)$ dyadic ranges, add Laplace noise per node, so each output sums $O(\log T)$ noisy partial sums, giving error $O(\varepsilon^{-1}\log^{1.5} T)$. Privacy follows from **parallel + sequential composition** since each event touches $O(\log T)$ nodes. Formally, with the **factorization mechanism** view, releasing $A x$ for a workload matrix $A$ (here the lower-triangular all-ones prefix-sum matrix $M$) under $\ell_2$ has error governed by the **$\gamma_2$ / factorization norm**: $\mathrm{err} \propto \|L\|_{1\to2}\,\|R\|_{2\to\infty}$ over $M=LR$. The optimal constant for continual counting is the $\gamma_2$-norm of the prefix-sum matrix, $\Theta(\log T)$ squared in MSE.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** **Matrix factorization mechanisms** achieve the optimal leading constant for continual counting. Henzinger, Upadhyay, Upadhyay (SODA 2023) gave a near-optimal *explicit* factorization with error $\approx \frac{1}{\pi}\varepsilon^{-1}(\ln T)\,$ and matching lower-order terms; Fichtenberger, Henzinger, Upadhyay (ICML 2023) and the "smooth/banded" factorizations refine constants.
- **Systems-SOTA:** DP-FTRL / **banded matrix factorization** (Kairouz, McMahan, Choquette-Choo et al., 2021–2023) deploys continual-observation MF in production federated learning (Google), making the binary-tree → MF transition practical at scale. Streaming sketches with DP (private CountMin / Misra–Gries; Lebeda–Tetek) handle heavy hitters and frequencies.

## 4. Upper Bound
Continual counting (event-level, central, $(\varepsilon,\delta)$ or pure-$\varepsilon$): max error over $T$ steps is $O(\varepsilon^{-1}\log^{1.5} T)$ via binary tree; **$O(\varepsilon^{-1}\log T)$ via matrix factorization**, which is tight in the $\gamma_2$ sense. Histograms/CDFs over a domain of size $d$: $O(\varepsilon^{-1}\log T \log d)$. User-level privacy multiplies error by the max per-user contribution (after clipping). Turnstile distinct-count and $F_0$ estimation are far harder — only poly-log multiplicative or large additive guarantees are known.

## 5. Lower Bound
**Information-theoretic:** any continual counting mechanism has worst-case additive error $\Omega(\varepsilon^{-1}\log T)$ (Dwork–Naor–Pitassi–Rothblum 2010; refined to tight constants via $\gamma_2$-norm lower bounds, Henzinger et al.). For **fully dynamic / turnstile distinct counting**, Jain, Kalemaj, Raskhodnikova, Sivakumar, Smith (2023) prove a **polynomial** $\Omega(T^{c})$ lower bound under continual release — separating it sharply from the static setting. **Reconstruction/fingerprinting** bounds cap user-level multi-query release. These hold in the central model; local/pan-private models are strictly harder.

## 6. The Gap
For **continual counting / prefix sums** the gap is essentially **closed**: matching $\Theta(\varepsilon^{-1}\log T)$ upper and lower bounds, even to leading constants. This is why the problem is "partially solved." The **open** part: (i) **turnstile** aggregates with deletions, where distinct-count and quantiles have polynomial gaps; (ii) **rich relational workloads** (joins, group-bys over streams) lacking tight factorization analyses; (iii) **unbounded $T$** without knowing the horizon (online/doubling tricks lose constants); (iv) tight **user-level** continual bounds for general aggregates.

## 7. Current Research (as of June 2026)
Hot directions: optimal/near-optimal **banded and Toeplitz factorizations** for streaming ML and analytics, including continual release with **amplification by sampling/shuffling** *(frontier — verify)*; private **continual histograms and quantiles** with poly-log error (Cohen, Lyu, Nelson, Steinke, Stemmer line); **continual release lower bounds for dynamic graph problems** (edge/triangle counting) extending Jain et al.; and **sketch + MF hybrids** for frequency moments. Groups: Henzinger & Upadhyay (ISTA/Vienna, Apple), McMahan/Choquette-Choo/Kairouz (Google), Smith/Raskhodnikova (BU), Stemmer (Tel Aviv/Google). A 2025–2026 frontier item: near-tight continual release for sliding-window and time-decayed aggregates *(frontier — verify)*.

## 8. Future Work
- Tight bounds for turnstile $F_0$/distinct elements and quantiles under continual release.
- Factorization-optimal mechanisms for relational joins and group-bys over streams.
- Horizon-free (truly unbounded-$T$) mechanisms matching known-$T$ constants.
- User-level continual release with practical clipping and adaptive contribution bounds.
- Continual release in the shuffle/pan-private models with amplification.

## 9. Key References
- **[Foundational]** Dwork, Naor, Pitassi, Rothblum. *Differential Privacy under Continual Observation.* STOC, 2010. — [DOI](https://doi.org/10.1145/1806689.1806787) · [DBLP](https://dblp.org/rec/conf/stoc/DworkNPR10.html)
- **[Foundational]** Chan, Shi, Song. *Private and Continual Release of Statistics.* ICALP/ACM TISSEC, 2010/2011. — [ICALP DOI](https://doi.org/10.1007/978-3-642-14162-1_34) · [DBLP](https://dblp.org/rec/conf/icalp/ChanSS10.html) · [TISSEC DOI](https://doi.org/10.1145/2043621.2043626)
- **[SOTA]** Henzinger, Upadhyay, Upadhyay. *Almost Tight Error Bounds for Differentially Private Continual Counting.* SODA, 2023. — [DOI](https://doi.org/10.1137/1.9781611977554.ch183) · [DBLP search](https://dblp.org/search?q=Almost+Tight+Error+Bounds+Differentially+Private+Continual+Counting)
- **[SOTA]** Fichtenberger, Henzinger, Upadhyay. *Constant Matters: Fine-Grained Error Bound on Differentially Private Continual Observation.* ICML, 2023. — [PMLR](https://proceedings.mlr.press/v202/fichtenberger23a.html) · [arXiv](https://arxiv.org/abs/2202.11205)
- **[SOTA]** Kairouz, McMahan, Song, Thakkar, Thakurta, Xu. *Practical and Private (Deep) Learning without Sampling or Shuffling (DP-FTRL).* ICML, 2021. — [PMLR](https://proceedings.mlr.press/v139/kairouz21b.html) · [arXiv](https://arxiv.org/abs/2103.00039)
- **[SOTA]** Jain, Kalemaj, Raskhodnikova, Sivakumar, Smith. *Counting Distinct Elements in the Turnstile Model with Differential Privacy under Continual Observation.* NeurIPS, 2023. — [arXiv](https://arxiv.org/abs/2306.06723) · [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2023/hash/0ef1afa0daa888d695dcd5e9513bafa3-Abstract-Conference.html)

## 10. Worked Example

**Binary-tree mechanism for continual counting, $T=4$.** A stream of bits arrives: $x_1,x_2,x_3,x_4 = 1,0,1,1$. We must release every prefix sum $S_t=\sum_{i\le t}x_i$ under event-level DP of the whole transcript. Naively adding fresh Laplace noise to each of the four prefix sums is wasteful and adding noise once to each $x_i$ then summing makes error grow as $\sqrt{t}$.

The dyadic mechanism builds a binary tree over the 4 positions and stores a noisy partial sum at each node: leaves $[1,1],[2,2],[3,3],[4,4]$, internal $[1,2],[3,4]$, root $[1,4]$. Each node gets independent noise $\mathrm{Lap}(1/\varepsilon)$. To answer $S_3$, decompose $\{1,2,3\}$ into the dyadic ranges $[1,2]\cup[3,3]$ — just **2** nodes — so $\tilde S_3$ sums only 2 noisy values, not 3.

In general each prefix $[1,t]$ decomposes into at most $\lceil\log_2 T\rceil$ dyadic ranges (here $\le 2$), and each event $x_i$ affects only $\log_2 T$ tree nodes. So the noise per release is a sum of $O(\log T)$ Laplace variables, giving error $O(\varepsilon^{-1}\log^{1.5}T)$ — exponentially better in $T$ than the $\Theta(\sqrt T)$ of independent-per-step noise.

---
*Part of the [DBMS Research catalog](../../README.md).*
