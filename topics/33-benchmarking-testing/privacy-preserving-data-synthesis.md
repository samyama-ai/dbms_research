---
id: 33-benchmarking-testing/privacy-preserving-data-synthesis
title: "Privacy-Preserving Benchmark Data Synthesis"
topic: 33-benchmarking-testing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Privacy-Preserving Benchmark Data Synthesis

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/privacy-preserving-data-synthesis` · **Status:** partially-solved

## 1. Problem Statement
Given a sensitive source database $D$ over schema $\mathcal{S}$, produce a synthetic database $\tilde{D}$ that (a) preserves the statistics relevant to query optimization and execution — column cardinalities, value distributions, join-key correlations, multi-column joint frequencies, data skew — so that plans and costs measured on $\tilde{D}$ match those on $D$, while (b) satisfying a *formal* privacy guarantee (typically $(\varepsilon,\delta)$-differential privacy) with respect to any single tuple of $D$.

Variants:
- **Decision:** does there exist $\tilde{D}$ achieving fidelity error $\le \eta$ on a workload $W$ under $\varepsilon$-DP? (Generally infeasible to decide exactly; reduces to error-bounded mechanism existence.)
- **Optimization:** minimize maximum (or expected) plan-cost distortion over $W$ subject to a fixed privacy budget $\varepsilon$.
- **Counting / estimation:** answer the marginal/conditional-frequency queries that optimizers consume, under DP, with minimal error — the workhorse subproblem.

The defining tension: plan-relevant statistics (especially join correlations and tail/heavy-hitter behavior) are exactly the high-sensitivity quantities DP must blur.

## 2. Mathematical Foundations
A randomized mechanism $\mathcal{M}$ is $(\varepsilon,\delta)$-**differentially private** if for neighboring databases $D \sim D'$ (differing in one tuple) and all measurable $S$:
$$\Pr[\mathcal{M}(D)\in S] \le e^{\varepsilon}\Pr[\mathcal{M}(D')\in S] + \delta.$$
The **Laplace/Gaussian mechanisms** add noise scaled to the $\ell_1$/$\ell_2$ **global sensitivity** $\Delta f = \max_{D\sim D'}\lVert f(D)-f(D')\rVert$. Marginals are low-sensitivity ($\Delta=1$), making *low-order marginal* synthesis the natural primitive.

Workload-aware approaches frame synthesis as releasing a set of linear counting queries $W$ via the **matrix mechanism**, with error governed by the query-matrix factorization. The **AGM bound** $|Q(D)| \le \prod_e |R_e|^{x_e}$ (fractional edge cover) explains *why* join-output cardinality — the optimizer's key quantity — depends on multi-relation statistics that single-table DP marginals do not capture, motivating *correlation-preserving* synthesis (e.g., PGM-style graphical models capturing a chosen junction tree of marginals). Composition theorems (basic, advanced, Rényi/zCDP) bound total budget across the marginals selected.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Private marginal-based synthesis. **MWEM** (Hardt–Ligett–McSherry, NeurIPS 2012) and the **matrix mechanism** (Li et al., VLDBJ 2015) give workload-optimal linear-query release. **PrivBayes** (Zhang et al., SIGMOD 2014/TODS 2017) synthesizes via a DP Bayesian network. **Private-PGM** (McKenna–Sheldon–Miklau, ICML 2019) and **AIM** (McKenna et al., VLDB 2022) represent the current marginal-selection frontier and won the NIST DP synthetic-data challenges.
- **Systems-SOTA:** DP relational synthesizers and benchmark-oriented tools (e.g., **PrivLava** for multi-relational/foreign-key data, Cai et al., SIGMOD 2023) and learned generative models (DP-GAN/DP-diffusion) used mainly for single-table fidelity. Production benchmark cloning still leans on non-DP statistics-preserving generators (Microsoft's data-cloning work, dbgen-style scaling) when formal privacy is not required.

## 4. Upper Bound
For releasing a workload of $k$ linear (marginal) queries under $\varepsilon$-DP, the matrix/factorization mechanisms achieve expected per-query error $O(\sqrt{\log k}/\varepsilon)$ via advanced composition, and Private-PGM produces a *consistent* full synthetic table from these noisy marginals in time polynomial in the junction-tree treewidth. PrivLava extends polynomial-time synthesis to bounded-arity foreign-key schemas. These are the strongest known *constructive* guarantees giving usable plan-relevant statistics.

## 5. Lower Bound
Releasing all $d$-way marginals accurately is information-theoretically hard: by **reconstruction/tracing attacks** (Dinur–Nissim 2003; Bun–Ullman–Vadhan, STOC 2014; Steinke–Ullman 2015), answering $\Theta(n)$ low-sensitivity queries with $o(\sqrt n)$ noise enables reconstruction, so per-query error $\Omega(\sqrt{k}/(\varepsilon n))$-type bounds are unavoidable for large query sets. Exact high-order joint distributions (needed for some join-correlation fidelity) require error growing with the number of cells, making *worst-case* full-fidelity synthesis provably impossible under non-trivial $\varepsilon$.

## 6. The Gap
For *low-order* marginals the upper and lower bounds nearly match (up to $\mathrm{polylog}$ factors) — that subproblem is essentially solved. The genuine open gap is **plan-fidelity vs. privacy for multi-relation join correlations and heavy-hitter/tail structure**: there is no tight characterization of how much optimizer-relevant distortion is *forced* by $\varepsilon$-DP across joins. Closing it needs a fidelity metric defined directly in terms of plan/cost divergence rather than marginal error, plus matching mechanisms and lower bounds in that metric.

## 7. Current Research (as of June 2026)
Active directions: (1) workload-conditioned synthesis that takes the *query benchmark* as input and optimizes plan-cost fidelity rather than generic marginals; (2) DP synthesis over foreign-key/multi-relational schemas beyond PrivLava, including approximate-DP relaxations for correlated tables *(frontier — verify)*; (3) DP-finetuned generative/diffusion models for tabular fidelity with tracing-attack auditing. Groups: Miklau/McKenna/Sheldon (UMass, marginal-based DP synthesis), Kifer (Penn State), the Berkeley/CMU DP communities, and NIST's ongoing DP synthetic-data program. An emerging *(frontier — verify)* thread evaluates whether learned cardinality estimators trained on DP-synthetic data transfer to real workloads.

## 8. Future Work
- A plan-divergence fidelity metric with matching mechanism + lower bound.
- Privacy accounting that spends budget preferentially on join-key correlations.
- DP synthesis preserving *physical* properties (sortedness, clustering, page-level skew) for storage/access-method benchmarks.
- Auditing synthetic benchmarks against tracing/membership-inference attacks as a standard release gate.

## 9. Key References
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** Dinur, Nissim. *Revealing Information While Preserving Privacy.* PODS, 2003. — [DOI](https://doi.org/10.1145/773153.773173)
- **[SOTA]** McKenna, Sheldon, Miklau. *Graphical-model based estimation and inference for differential privacy (Private-PGM).* ICML, 2019. — [arXiv](https://arxiv.org/abs/1901.09136)
- **[SOTA]** McKenna, Miklau, Sheldon, et al. *AIM: An Adaptive and Iterative Mechanism for Differentially Private Synthetic Data.* PVLDB, 2022. — [DOI](https://doi.org/10.14778/3551793.3551817)
- **[SOTA]** Cai, Lei, Xiao, et al. *PrivLava: Synthesizing Relational Data under Differential Privacy.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589287)
- **[Foundational]** Zhang, Cormode, Procopiuc, Srivastava, Xiao. *PrivBayes: Private Data Release via Bayesian Networks.* SIGMOD 2014 / TODS 2017. — [DOI](https://doi.org/10.1145/2588555.2588573)
- **[Survey]** Bun, Ullman, Vadhan. *Fingerprinting Codes and the Price of Approximate Differential Privacy.* STOC, 2014. — [DOI](https://doi.org/10.1145/2591796.2591877)

## 10. Worked Example

Source table `Patients(zip, disease)` with $n=4$ tuples; we release the 1-way marginal over `disease` $\in\{\text{flu},\text{cancer}\}$ under $\varepsilon$-DP. True counts: $f = (\text{flu}{=}3,\ \text{cancer}{=}1)$. Adding one tuple changes one count by 1, so global sensitivity $\Delta f = 1$. The **Laplace mechanism** adds $\mathrm{Lap}(\Delta f/\varepsilon) = \mathrm{Lap}(1/\varepsilon)$ to each count. With $\varepsilon = 1$, the noise scale $b = 1$ and standard deviation is $\sqrt 2 b \approx 1.41$.

One draw might give noisy $\tilde f = (3 + 0.4,\ 1 - 0.9) = (3.4,\ 0.1)$. Post-processing clips/rounds and normalizes to a distribution, then samples $\tilde D$. Note the *relative* error on the heavy hitter (flu, $\approx 13\%$) is small, but on the rare cell (cancer) the $\pm 1.4$ noise can flip it to $0$ or $2$ — exactly the **tail/heavy-hitter fidelity** problem in section 6. For a join correlation needing the 2-way marginal over $(\text{zip},\text{disease})$ with, say, $100$ cells, each gets independent $\mathrm{Lap}(1/\varepsilon)$ noise, so per-cell error stays $O(1/\varepsilon)$ but the *count* of noisy cells grows — illustrating why high-order joint fidelity degrades.

---
*Part of the [DBMS Research catalog](../../README.md).*
