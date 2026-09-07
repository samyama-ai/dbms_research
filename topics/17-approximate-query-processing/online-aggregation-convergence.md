---
id: 17-approximate-query-processing/online-aggregation-convergence
title: "Online Aggregation Convergence Rates"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Online Aggregation Convergence Rates

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/online-aggregation-convergence` · **Status:** partially-solved

## 1. Problem Statement
**Online aggregation (OLA)** answers an aggregate query (e.g., `AVG`, `SUM`, `COUNT`) progressively: as tuples are sampled/scanned, the system continuously refines a running estimate $\hat\theta_t$ together with a running confidence interval $[\hat\theta_t - \varepsilon_t,\ \hat\theta_t + \varepsilon_t]$ that shrinks until the user is satisfied. The central question is: **how fast can $\varepsilon_t$ provably shrink**, and which *scan/sampling order* and *estimator* achieve the optimal convergence rate?

Variants:
- **Optimization variant:** minimize the number of tuples (or wall-clock time) to reach a target half-width $\varepsilon$ with confidence $1-\delta$.
- **Scheduling variant:** for multiple groups (`GROUP BY`) or multiple queries, choose the sampling order that tightens the *worst* (or aggregate) interval fastest.
- **Estimator-design variant:** construct unbiased, low-variance estimators whose CIs are *valid at every stopping time* (anytime-valid), not only at a fixed sample size.

## 2. Mathematical Foundations
For a population of $N$ values with mean $\mu$ and variance $\sigma^2$, a uniform random sample of size $n$ yields the estimator $\hat\mu_n = \frac1n\sum X_i$ with $\mathrm{Var}(\hat\mu_n)=\frac{\sigma^2}{n}\cdot\frac{N-n}{N-1}$ (finite-population correction). Hence the half-width scales as
$$\varepsilon_n \approx z_{1-\delta/2}\,\frac{\sigma}{\sqrt n}\sqrt{\tfrac{N-n}{N-1}},$$
the canonical **$1/\sqrt n$** convergence — a consequence of the **CLT** and **Hoeffding/Bernstein** concentration. The $1/\sqrt n$ rate is information-theoretically optimal for mean estimation from i.i.d. samples (matching Cramér–Rao). Tightening requires reducing $\sigma$ (stratification, control variates) rather than beating the exponent.

Key tools: **finite-population sampling theory** (Hájek), **martingale/anytime-valid inference** (confidence sequences, Howard et al.), **large-deviation** bounds, and for `GROUP BY`, **multi-armed-bandit** / optimal-allocation (Neyman allocation) theory for distributing samples across strata to equalize/ minimize interval widths.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Neyman-optimal stratified allocation achieves variance $\big(\sum_h W_h\sigma_h\big)^2/n$, strictly below uniform sampling when strata variances differ; anytime-valid confidence sequences (Howard, Ramdas, McAuliffe, Sekhon, 2021) give CIs valid under optional stopping with only a $\sqrt{\log\log}$ penalty over the fixed-$n$ rate.
- **Systems-SOTA:** the original **CONTROL** project (Hellerstein, Haas, Wang, SIGMOD 1997) introduced OLA with running CIs and index striding; **DBO** and **Turbo-DBO** (Jermaine et al.) generalized to multi-table; **Wander Join / XDB** (Li, Wu, Yu, Nakayama, SIGMOD 2016) and **Quickr** / **BlinkDB** (Agarwal et al., EuroSys 2013) deliver progressive answers in modern engines. Cloud OLA appears in research prototypes over Spark/Flink.

## 4. Upper Bound
- Mean/`SUM`/`COUNT`/`AVG`: half-width $O(\sigma n^{-1/2})$ with explicit constants from Bernstein, achievable by simple random sampling; **anytime-valid** CIs achieve $O\!\big(\sigma\sqrt{\tfrac{\log\log n}{n}}\big)$ uniformly over all $n$ (Howard et al. 2021), the optimal sequential rate.
- Stratified/Neyman allocation lowers the leading constant (the $\sigma$ factor) but **cannot improve the $n^{-1/2}$ exponent** for additive aggregates.
- For `GROUP BY` with $g$ groups, round-robin/optimal-allocation reaches target width for all groups in $O(\max_h \sigma_h^2/\varepsilon^2)$ samples per group under proportional allocation.

## 5. Lower Bound
- **Information-theoretic / statistical:** estimating a mean to additive error $\varepsilon$ with confidence $1-\delta$ requires $\Omega(\sigma^2\varepsilon^{-2}\log\delta^{-1})$ samples — the $n^{-1/2}$ rate is *optimal* (Cramér–Rao; minimax lower bounds for sub-Gaussian mean estimation).
- **Sequential penalty:** the law of the iterated logarithm forces a $\sqrt{\log\log n}$ multiplicative penalty for any procedure whose CI is valid at *every* stopping time (Robbins; Darling–Robbins) — so anytime-valid OLA cannot match fixed-$n$ width exactly.
- For low-selectivity predicates, hitting even one qualifying tuple needs $\Omega(1/p)$ samples (coupon/occupancy bound), capping early convergence.

## 6. The Gap
For single additive aggregates the gap is **closed**: upper (Bernstein / anytime-valid) and lower (Cramér–Rao + LIL) bounds match up to the unavoidable $\sqrt{\log\log n}$ sequential factor. The **open** part is *systems-side and structural*: (i) optimal scan/index orders when data is clustered or sorted (non-i.i.d. access), (ii) optimal multi-group/multi-query scheduling, and (iii) convergence for *non-additive* aggregates (quantiles, `DISTINCT`, joins) where the clean $1/\sqrt n$ theory breaks. Hence "partially solved."

## 7. Current Research (as of June 2026)
Active threads: (1) **anytime-valid / e-value inference** for OLA, importing Ramdas-school confidence sequences into databases for safe early stopping *(frontier — verify)*; (2) learned/predictive OLA that uses models to pre-allocate sampling effort across groups; (3) OLA over modern distributed engines (Spark/Flink/lakehouse) with progressive UIs; (4) OLA for joins via Wander-Join descendants. Groups: Hellerstein/Haas lineage (Berkeley), Jermaine (Rice), Wu (Wander-Join), and the sequential-inference community (Ramdas, Howard, Wasserman).

## 8. Future Work
- Optimal sampling order under physical clustering / sortedness (beyond i.i.d.).
- Unified anytime-valid CIs across `GROUP BY`, joins, and nested queries.
- Variance-reduction (control variates, stratification) chosen *online* and adaptively.
- Tight scheduling theory for many concurrent OLA queries sharing a scan.

## 9. Key References
- **[Foundational]** J. M. Hellerstein, P. J. Haas, H. J. Wang. *Online Aggregation.* SIGMOD, 1997. — [DOI](https://doi.org/10.1145/253262.253291)
- **[Foundational]** P. J. Haas, J. M. Hellerstein. *Ripple Joins for Online Aggregation.* SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304182.304208)
- **[SOTA]** S. R. Howard, A. Ramdas, J. McAuliffe, J. Sekhon. *Time-Uniform, Nonparametric, Nonasymptotic Confidence Sequences.* Annals of Statistics, 2021. — [DOI](https://doi.org/10.1214/20-AOS1991), [arXiv](https://arxiv.org/abs/1810.08240)
- **[SOTA]** F. Li, B. Wu, K. Yu, A. Nakayama. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[SOTA]** S. Agarwal et al. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[Foundational]** J. Neyman. *On the Two Different Aspects of the Representative Method (stratified/optimal allocation).* JRSS, 1934. — [DOI](https://doi.org/10.1111/j.2397-2335.1934.tb04184.x)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Consider `SELECT AVG(amount) FROM payments` over $N = 1{,}000{,}000$ rows with true mean $\mu = 50$ and standard deviation $\sigma = 40$. We want a 95% CI of half-width $\varepsilon = 1$ (so $z_{0.975} = 1.96$).

Ignoring the finite-population correction, the required sample size is
$$n \approx \Big(\frac{z\,\sigma}{\varepsilon}\Big)^2 = \Big(\frac{1.96 \times 40}{1}\Big)^2 = (78.4)^2 \approx 6{,}147.$$
After scanning only $\sim 0.6\%$ of the table the interval already reads $[49, 51]$ at 95% confidence.

Watch the $1/\sqrt n$ law: at $n = 1{,}500$ the half-width is $1.96 \cdot 40/\sqrt{1500} \approx 2.02$; quadrupling to $n = 6{,}000$ halves it to $\approx 1.01$. To reach $\varepsilon = 0.5$ we must again quadruple $n$ to $\approx 24{,}600$ — the exponent never improves, confirming Section 5's $\Omega(\sigma^2/\varepsilon^2)$ floor. Stratifying by, say, region (cutting effective $\sigma$ to $30$) lowers the constant, needing only $\approx 3{,}458$ rows, but the $1/\sqrt n$ shape is unchanged.

---
*Part of the [DBMS Research catalog](../../README.md).*
