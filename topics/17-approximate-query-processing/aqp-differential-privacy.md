# Error-Bounded AQP Under DP Noise

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/aqp-differential-privacy` · **Status:** open
> **Verification note:** In the Section 10 sampling-variance line the intermediate "$\tfrac{1}{q^2}\,nq\,p(1-p)$" should read $\tfrac{N}{q}\,p(1-p)=\tfrac{10^6}{0.01}\cdot0.16$; the stated result $1.6\times10^7$ (RMSE $\approx4000$) is correct, only the substituted intermediate is mis-stated.

## 1. Problem Statement

Approximate query processing trades exactness for speed by introducing **sampling/sketch error**; differential privacy (DP) trades exactness for privacy by introducing **calibrated noise**. When both are required — fast *and* private aggregates — the two error sources compound. The problem is to **jointly optimize** the sampling/sketch design and the DP mechanism so that the *total* expected error (sampling variance + privacy noise variance, plus any bias) is **minimized and provably bounded**, subject to a privacy budget $(\varepsilon_{DP}, \delta_{DP})$ and a resource/latency budget.

Variants:
- **Estimation:** minimize total MSE of $\hat A$ at fixed $(\varepsilon_{DP},\delta_{DP})$ and sample size $n$.
- **Optimization (frontier):** trace the Pareto frontier of (privacy, accuracy, cost) and pick the point meeting an error SLO at minimum cost.
- **Decision:** given an error SLO and a privacy budget, does *any* (sample size, mechanism) pair satisfy both?
- **Composition:** allocate a privacy budget across a *workload* of approximate queries.

## 2. Mathematical Foundations

A randomized mechanism $M$ is **$(\varepsilon,\delta)$-DP** if for neighboring databases $D \sim D'$ and all events $E$, $\Pr[M(D)\in E] \le e^{\varepsilon}\Pr[M(D')\in E] + \delta$. The **Laplace mechanism** adds $\mathrm{Lap}(\Delta_1/\varepsilon)$ (sensitivity $\Delta_1$), the **Gaussian mechanism** adds $\mathcal N(0,\sigma^2)$ with $\sigma \propto \Delta_2\sqrt{2\ln(1.25/\delta)}/\varepsilon$.

For an aggregate over a uniform sample of size $n$ from $N$ rows, the estimator MSE decomposes (under independence) as

$$\mathrm{MSE}(\hat A) \;=\; \underbrace{\frac{N^2\sigma_v^2}{n}\Big(1-\tfrac{n}{N}\Big)}_{\text{sampling}} \;+\; \underbrace{\frac{2\Delta^2}{\varepsilon_{DP}^2}}_{\text{DP noise}} \;+\; (\text{bias})^2 .$$

A crucial interaction: **sampling amplifies privacy** — running an $\varepsilon$-DP mechanism on a $q$-fraction Poisson sample yields roughly $\log(1+q(e^\varepsilon-1))$-DP (the *privacy amplification by subsampling* theorem). So sampling is *not just* a cost source; it *buys* privacy, letting one spend less noise. The joint optimum therefore couples $n$ and $\varepsilon_{DP}$ non-trivially. Tight accounting uses **Rényi DP** / the **moments accountant** / **f-DP (Gaussian DP)** for composition across a workload.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** privacy amplification by subsampling (Balle–Barthe–Gaboardi, NeurIPS 2018, tight bounds; Kasiviswanathan et al.), and the **matrix mechanism** (Li–Hay–Rastogi–Miklau–McGregor, PODS 2010) for optimal linear-query workloads under DP. **Rényi DP** (Mironov, 2017) and **Gaussian DP** (Dong–Roth–Su, JRSS-B 2022) give the tightest composition.
- **Systems-SOTA:** **APEx** (Ge, He, Ilyas, Machanavajjhala, SIGMOD 2019) is an accuracy-aware private query engine that *chooses mechanisms to meet an accuracy bound* — the closest deployed system to this problem. **PrivateSQL** (Kotsogiannis et al., VLDB 2019) and **Chorus** (Johnson–Near, VLDB 2018/2020) push DP into relational engines. Google/Apple/Microsoft production DP-SQL stacks combine sampling and DP but optimize the two budgets largely *separately*.

## 4. Upper Bound

For a single counting/sum query, combining a size-$n$ sample with subsampled Gaussian noise gives total RMSE $O\!\big(\sigma_v\sqrt{N^2/n} + \Delta/\varepsilon_{DP}^{\mathrm{eff}}\big)$ where $\varepsilon_{DP}^{\mathrm{eff}}$ is the *amplified* budget — strictly better than either source alone for a range of $n$. For linear-query workloads, the matrix mechanism is *optimal among data-independent linear mechanisms*, achieving error within a known factor of the workload's $\gamma_2$/factorization norm. APEx guarantees the *output* meets a user accuracy bound while minimizing privacy spend, via a search over mechanism configurations.

## 5. Lower Bound

DP imposes hard information-theoretic floors independent of compute: answering $k$ counting queries to error $o(\sqrt{k})$ under $(\varepsilon,\delta)$-DP is impossible (the **fingerprinting / tracing-attack** lower bounds, Bun–Ullman–Vadhan, STOC 2014; Dwork et al.). For a single query, error $\Omega(\Delta/\varepsilon_{DP})$ is unavoidable. Sampling adds its own $\Omega(\sigma_v\sqrt{N^2/n})$ Cramér–Rao floor. Crucially, the **joint** lower bound is *not simply additive*: amplification means the privacy term can shrink with $n$, so the true Pareto frontier is **not characterized** in closed form — the central open difficulty.

## 6. The Gap

The single-query, single-source bounds are each tight, but the **joint** sample-size $\times$ privacy-budget optimization is **open**: there is no closed-form (or tight algorithmic) characterization of the (privacy, accuracy, cost) Pareto frontier that *fully exploits* subsampling amplification, especially for non-linear aggregates (quantiles, AVG with private denominators), joins (sensitivity explosion), and **workloads** under composition. Systems like APEx optimize accuracy-vs-privacy but treat sampling cost as exogenous rather than co-optimizing it. Closing the gap requires a unified estimator-design theory where $n$ and $\varepsilon_{DP}$ are chosen *together* against an SLO.

## 7. Current Research (as of June 2026)

Active: tight **subsampling amplification under f-DP / Gaussian DP** and its use to co-tune sample size and noise *(frontier — verify)*; private **sketches** (DP Count-Min / DP quantiles, e.g. private KLL) so the synopsis itself is the privacy boundary; **private AQP for joins** under bounded-degree / Lipschitz-extension sensitivity control. Workload-level budget allocation via the matrix/factorization mechanism with sampling. Groups: Miklau/Machanavajjhala/He (UMass/Duke, APEx/PrivateSQL lineage), Near (Vermont, Chorus), Ullman (Northeastern, lower bounds), Dwork/Roth (foundations), Smith (BU). The explicit "minimize sampling+DP error jointly under an SLO" formulation is being articulated but lacks a tight solution *(frontier — verify)*.

## 8. Future Work

- A characterized (privacy, accuracy, cost) Pareto frontier exploiting subsampling amplification.
- Joint design for non-linear aggregates and joins under DP.
- Private, mergeable, delete-aware sketches with tight composition.
- Optimizer integration: an SLO-driven planner that allocates both compute and privacy budget (links to AQP plan optimization).

## 9. Key References

- **[Foundational]** C. Dwork, F. McSherry, K. Nissim, A. Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** C. Dwork, A. Roth. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in TCS, 2014. — [DOI](https://doi.org/10.1561/0400000042)
- **[SOTA]** C. Ge, X. He, I. F. Ilyas, A. Machanavajjhala. *APEx: Accuracy-Aware Differentially Private Data Exploration.* SIGMOD, 2019. — [arXiv](https://arxiv.org/abs/1712.10266)
- **[SOTA]** B. Balle, G. Barthe, M. Gaboardi. *Privacy Amplification by Subsampling: Tight Analyses via Couplings and Divergences.* NeurIPS, 2018. — [arXiv](https://arxiv.org/abs/1807.01647)
- **[SOTA]** C. Li, M. Hay, V. Rastogi, G. Miklau, A. McGregor. *Optimizing Linear Counting Queries under Differential Privacy (The Matrix Mechanism).* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807104)
- **[SOTA]** J. Dong, A. Roth, W. J. Su. *Gaussian Differential Privacy.* JRSS-B, 2022. — [arXiv](https://arxiv.org/abs/1905.02383)
- **[Foundational]** M. Bun, J. Ullman, S. Vadhan. *Fingerprinting Codes and the Price of Approximate Differential Privacy.* STOC, 2014. — [DOI](https://doi.org/10.1145/2591796.2591877)

## 10. Worked Example

A table has $N=1{,}000{,}000$ rows; we want a private `COUNT(*) WHERE region='X'`, true count $A=200{,}000$. A counting query has sensitivity $\Delta_1=1$.

**Pure DP, no sampling.** Laplace mechanism at $\varepsilon_{DP}=0.5$ adds $\mathrm{Lap}(1/0.5)=\mathrm{Lap}(2)$, variance $2\cdot 2^2=8$, so DP-RMSE $=\sqrt8\approx 2.83$. Tiny relative to $A$ — but assumes a full scan.

**Sample + amplified DP.** Take a Poisson sample of rate $q=0.01$ ($n\approx10{,}000$). Sampling variance for the scaled estimate $\hat A=\tfrac{1}{q}\cdot(\text{sample count})$: with $p=0.2$, $\mathrm{Var}=\tfrac{1}{q^2}\,nq\,p(1-p)\approx\tfrac{1}{0.01}\cdot 10000\cdot0.16=1.6\times10^7$, sampling-RMSE $\approx 4000$.

Amplification: running $\varepsilon=0.5$ on a $q=0.01$ sample yields effective $\varepsilon' \approx \ln(1+0.01(e^{0.5}-1))\approx \ln(1.0065)\approx 0.0065$ — a $\sim77\times$ privacy gain, so the *same* noise buys far more privacy. The lesson: here sampling error ($4000$) dwarfs DP noise ($2.83$), so the joint optimum spends the privacy budget cheaply and instead enlarges $n$ — exactly the coupling section 6 calls unsolved in closed form.

---
*Part of the [DBMS Research catalog](../../README.md).*
