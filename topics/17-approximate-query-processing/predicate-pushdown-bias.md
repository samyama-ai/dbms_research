# Bias Correction for Predicate Pushdown

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/predicate-pushdown-bias` · **Status:** open

## 1. Problem Statement

Approximate query processing (AQP) answers aggregate queries from a small sample $S$ of a relation $R$ rather than scanning all of $R$. When a query carries a **highly selective predicate** $\sigma_\theta$, the subset of the sample that survives the predicate, $S_\theta = \{t \in S : \theta(t)\}$, may be tiny or empty — and, worse, *systematically unrepresentative* of $R_\theta = \sigma_\theta(R)$ whenever the sample was built non-uniformly (stratified, measure-biased, congressional, outlier-indexed). The problem is to produce an estimator $\hat{A}$ of an aggregate $A(R_\theta)$ (e.g. `SUM`, `AVG`, quantile) together with a *correct, tight* confidence interval, **after** the predicate is pushed down into the sample, correcting the selection bias introduced by the interaction between $\theta$ and the sampling design.

Variants:
- **Estimation (optimization):** minimize estimator variance / interval width subject to unbiasedness.
- **Decision:** does a valid $1-\delta$ interval of half-width $\le \varepsilon$ exist for this (query, sample) pair, or must we fall back to exact?
- **Counting:** estimate $|R_\theta|$ itself when $\theta$ is rare (the "small-group / empty-group" regime).

## 2. Mathematical Foundations

Let each tuple $t$ be included in $S$ with known inclusion probability $\pi_t > 0$. The **Horvitz–Thompson** estimator for $A = \sum_{t \in R_\theta} v_t$ is

$$\hat{A}_{HT} = \sum_{t \in S_\theta} \frac{v_t}{\pi_t}, \qquad \mathbb{E}[\hat{A}_{HT}] = A,$$

with variance depending on second-order inclusion probabilities $\pi_{tu}$. Pushdown bias arises when $\pi_t$ is *correlated with $\theta$ and with $v_t$*: stratified designs allocate few draws to strata that happen to contain $R_\theta$, inflating $\mathrm{Var}(\hat{A}_{HT})$ and degrading coverage of the normal-approximation interval

$$\hat{A} \pm z_{1-\delta/2}\,\sqrt{\widehat{\mathrm{Var}}(\hat{A})}.$$

The normal approximation fails precisely in the small-$|S_\theta|$ regime; one then needs a **bootstrap** (resample $S_\theta$ with HT weights) or finite-sample concentration (empirical Bernstein, $\mathrm{Var}(\hat A)$-aware). Connections: optimal allocation reduces to **Neyman allocation** $n_h \propto N_h \sigma_h$, which is *predicate-oblivious*; the open difficulty is allocating against an unknown future predicate workload, linking to **online/adaptive stratification** and to the **VC/Rademacher complexity** of the predicate class $\Theta$ (uniform error over all $\theta \in \Theta$ scales with the VC dimension of $\Theta$).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** *BlinkDB* (Agarwal et al., EuroSys 2013) introduced multi-dimensional stratified samples with error/latency bounds but assumes predicate columns are known at sample-build time. *AQP++ / VerdictDB* (Park et al., SIGMOD 2017/2018) layer bias-corrected interval estimation on top of arbitrary engines via "variational subsampling." *DBEst / DeepDB* attach models. *Sample+Seek* (Ding et al., SIGMOD 2016) provably handles selective predicates by combining a measure-biased sample with an index-assisted "seek" for rare groups.
- **Theory-SOTA:** HT/Hájek estimators with Neyman allocation; the *outlier-indexed* sample of Babcock–Chaudhuri–Das (SIGMOD 2003) separates heavy contributors. Empirical-Bernstein and betting-based confidence sequences (Waudby-Smith & Ramdas, 2024) give the tightest known finite-sample intervals usable post-pushdown.

## 4. Upper Bound

For a *known* predicate workload, stratified Neyman allocation achieves variance within a constant factor of optimal and an interval of half-width $O(\sigma/\sqrt{n})$ with $n$ the surviving sample size. *Sample+Seek* gives a distribution-independent guarantee: with a measure-biased sample of size $O(\varepsilon^{-2}\log(1/\delta))$ plus index seeks, relative error $\varepsilon$ on `SUM`/`COUNT` over any conjunctive predicate, time sublinear in $|R|$ for "large-answer" queries. Empirical-Bernstein gives valid intervals of half-width $O\!\big(\sigma\sqrt{\tfrac{\log(1/\delta)}{n}} + \tfrac{\log(1/\delta)}{n}\big)$ with no distributional assumption.

## 5. Lower Bound

No sample of size $o(|R|)$ can give bounded *relative* error for arbitrarily selective predicates whose answer set is small: an adversary hides all mass in a measure-zero group, so any sublinear sampler misses it with constant probability — an information-theoretic Ω-bound (this is why *Sample+Seek* needs index seeks, i.e. non-sample access). For fixed sample size $n$, the central-limit half-width $\Omega(\sigma/\sqrt{n})$ is information-theoretically unimprovable for mean estimation (Cramér–Rao). Worst-case over a predicate class of VC dimension $d$, uniform interval validity requires $n = \Omega(d/\varepsilon^2)$.

## 6. The Gap

The estimation-variance bound is essentially *closed* for a known workload. The genuinely **open** gap is: (i) tight, *adaptive* allocation against an *unknown* future predicate workload (no algorithm matches the offline Neyman optimum without distributional foreknowledge); and (ii) the rare-group regime, where the sample-only lower bound forbids relative-error guarantees — closing it requires a principled theory of *when* to fall back to index/exact access, which today is heuristic. The "decision" variant (does a valid tight interval exist before answering?) has no characterized complexity.

## 7. Current Research (as of June 2026)

Active threads: **confidence sequences / betting estimators** (Ramdas, Waudby-Smith) imported into AQP for always-valid post-pushdown intervals; **learned stratification** that predicts predicate workloads and re-allocates samples online *(frontier — verify)*; integration of AQP intervals with **selectivity/cardinality estimators** so the optimizer can refuse a sample when predicted survivors are too few. Groups: Chaudhuri/Narasayya (Microsoft Research), Mozafari (formerly Michigan / VerdictDB), Ding & collaborators, the Berkeley RISE lineage. Open question being pushed: combining HT estimation with **conformal prediction** for distribution-free coverage under arbitrary pushdown *(frontier — verify)*.

## 8. Future Work

- Workload-adaptive sample allocation with regret guarantees against the offline Neyman optimum.
- A complexity-theoretic characterization of the "fall back to exact" decision under an error SLO.
- Bias correction for *joins* under pushdown, where inclusion probabilities multiply and HT variance explodes (the join-sampling barrier).
- Distribution-free, always-valid intervals that remain tight in the small-$|S_\theta|$ regime.

## 9. Key References

- **[Foundational]** D. G. Horvitz, D. J. Thompson. *A Generalization of Sampling Without Replacement from a Finite Universe.* JASA, 1952. — [DOI](https://doi.org/10.1080/01621459.1952.10483446)
- **[Foundational]** B. Babcock, S. Chaudhuri, G. Das. *Dynamic Sample Selection for Approximate Query Processing.* SIGMOD, 2003. — [DOI](https://doi.org/10.1145/872757.872822)
- **[SOTA]** B. Ding, S. Huang, S. Chaudhuri, K. Chakrabarti, C. Wang. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915249)
- **[SOTA]** S. Agarwal et al. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[SOTA]** Y. Park, B. Mozafari, J. Sorenson, J. Wang. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[SOTA]** I. Waudby-Smith, A. Ramdas. *Estimating Means of Bounded Random Variables by Betting.* JRSS-B, 2024. — [DOI](https://doi.org/10.1093/jrsssb/qkad009)

## 10. Worked Example

A relation $R$ has $N = 10^6$ rows split into two strata: stratum $H$ (90% of rows) and stratum $L$ (10%, the "rare" region). We build a stratified sample of $n = 10{,}000$ rows allocated proportionally — $9{,}000$ from $H$ and $1{,}000$ from $L$ — so inclusion probabilities are uniform, $\pi_t = 10^{-2}$.

Now push down a selective predicate $\theta$ whose answer set $R_\theta$ lives entirely in $L$ and has size $|R_\theta| = 500$ (selectivity $5\times10^{-4}$). The surviving sample is
$$\mathbb{E}[|S_\theta|] = 500 \times \pi_t = 500 \times 10^{-2} = 5 \text{ rows}.$$
With only 5 survivors, the normal-approximation CI $\hat A \pm 1.96\sqrt{\widehat{\mathrm{Var}}}$ badly under-covers (Section 2).

The bias bites if the design were *not* uniform: suppose an analyst had allocated only $200$ samples to $L$ (because $L$ looked unimportant), giving $\pi_t = 200/10^5 = 2\times10^{-3}$ there and $\mathbb{E}[|S_\theta|] = 500\times 2\times10^{-3} = 1$. One survivor cannot yield a valid interval — the HT weight $1/\pi_t = 500$ makes a single tuple swing $\hat A$ wildly, exactly the pushdown-bias pathology.

---
*Part of the [DBMS Research catalog](../../README.md).*
