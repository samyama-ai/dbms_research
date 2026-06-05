# Confidence Intervals for Complex Queries

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/valid-confidence-intervals` · **Status:** open

## 1. Problem Statement
Given a sample-based answer to a **complex** SQL query — nested subqueries, multiple correlated aggregates, joins, group-by, `HAVING`, and user-defined functions — compute **statistically valid** error bounds: a confidence interval (CI) $[\hat\theta - \epsilon, \hat\theta + \epsilon]$ such that $\Pr[\theta \in \text{CI}] \ge 1-\delta$ over the sampling randomness. Classical theory covers a single `SUM`/`AVG`/`COUNT` over an i.i.d. sample. The open problem is the **compositional** case: errors propagate non-linearly through nesting and correlation, and standard normal-approximation CLT bounds become unreliable for (i) **non-smooth** estimators (`MIN`/`MAX`, quantiles), (ii) heavily **correlated** sub-aggregates, (iii) **selective predicates** leaving few sample rows, and (iv) **derived ratios** (e.g. `SUM(x)/SUM(y)`). Decision variant: certify whether a `HAVING`/threshold predicate's truth value is determined by the sample at confidence $1-\delta$.

## 2. Mathematical Foundations
For a smooth functional $\theta=g(\mu_1,\dots,\mu_m)$ of population means, the **delta method** gives asymptotic normality: $\sqrt{n}(\hat\theta-\theta)\to\mathcal N(0,\nabla g^\top \Sigma \nabla g)$, where $\Sigma$ is the covariance of the per-tuple estimators — capturing correlation among sub-aggregates but requiring smoothness and large $n$. Distribution-free alternatives: the **bootstrap** (resample $B$ times, recompute the whole query, take empirical quantiles) handles arbitrary functionals at $B\times$ query cost; **Bernstein/Bennett** inequalities give finite-sample bounds with bounded variance; **Hoeffding** for bounded ranges. For non-smooth estimators the CLT fails and **subsampling** or the **$m$-out-of-$n$ bootstrap** is required. Validity across **simultaneous** CIs needs union/Bonferroni or **FDR** control. Key pathology — **diagnosability**: there exist queries (extreme-value, empty-stratum group-by) where *no* sample-only procedure yields a valid CI, formalized via **bootstrap inconsistency**.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BlinkDB** (Agarwal et al., EuroSys 2013) — closed-form CLT CIs over stratified samples for a restricted query class. **VerdictDB** (Park, Mozafari et al., SIGMOD 2018) — *variational subsampling* giving CIs for unmodified engines. **ABS / analytical bootstrap** (Zeng, Mozafari et al., SIGMOD 2014) — symbolic execution computing the bootstrap distribution analytically, avoiding the $B\times$ cost.
- **Theory-SOTA:** Bootstrap-consistency theory (Bickel–Freedman; Politis–Romano subsampling) imported into DB; **error-diagnostic** procedures (Agarwal–Mozafari et al., SIGMOD 2014) that *detect* when CIs are invalid.

## 4. Upper Bound
With the analytical bootstrap (ABS), valid CIs for relational-algebra-plus-aggregation queries are computed in time polynomial in query and sample size, *without* the $B$-fold blowup, for queries whose bootstrap distribution is symbolically tractable. Variational subsampling (VerdictDB) adds $O(1)$ passes and is provably valid as $n\to\infty$ for smooth functionals. Delta-method CIs cost $O(m^2)$ in the number of aggregates per group (covariance matrix).

## 5. Lower Bound
**Information-theoretic impossibility:** for extreme-value queries (`MAX`, rare-group existence) no sample-only estimator yields a valid finite-width CI — the bootstrap is provably *inconsistent* (Bickel–Götze–van Zwet). For selective predicates leaving $k$ rows, any CI half-width is $\Omega(1/\sqrt k)$ regardless of total sample size (Cramér–Rao / effective-Fisher-information bound). These are unconditional, not complexity-conditional.

## 6. The Gap
Smooth, well-sampled aggregates are **solved** (CLT/delta/bootstrap give tight valid CIs). Open for: non-smooth estimators, heavy cross-level correlation, and the small-effective-sample regime. No procedure simultaneously (a) is provably valid for arbitrary nested queries, (b) avoids the $B\times$ bootstrap cost, and (c) self-diagnoses its own invalidity. Closing it likely needs query-class-specific consistency theorems plus a sound "cannot certify" fallback.

## 7. Current Research (as of June 2026)
Directions: conformal-prediction AQP CIs (distribution-free finite-sample coverage); selective-inference corrections when the query is chosen after seeing the sample; betting/e-value **confidence sequences** for *anytime-valid* online aggregation. Groups: Barzan Mozafari (Michigan/Keebo), Yongjoo Park (UIUC), Surajit Chaudhuri / Bolin Ding (MSR/Alibaba). *(frontier — verify)* conformal AQP claiming guaranteed coverage for arbitrary group-by-having pipelines.

## 8. Future Work
Anytime-valid confidence sequences inside online aggregation; automatic detection/reporting of non-diagnosable queries; CIs that compose operator-by-operator across an AQP plan; joint CIs over sampling noise plus differential-privacy noise.

## 9. Key References
- **[Foundational]** Hellerstein, Haas, Wang. *Online Aggregation.* SIGMOD 1997. — [DOI](https://doi.org/10.1145/253262.253291)
- **[SOTA]** Agarwal, Mozafari, Panda, Milner, Madden, Stoica. *BlinkDB: Queries with Bounded Errors and Bounded Response Times.* EuroSys 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[SOTA]** Zeng, Gao, Mozafari, Zaniolo. *The Analytical Bootstrap: A New Method for Fast Error Estimation in AQP.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2588579)
- **[SOTA]** Agarwal, Milner, Kleiner, Talwalkar, Jordan, Madden, Mozafari, Stoica. *Knowing When You're Wrong: Building Fast and Reliable AQP Systems.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2593667)
- **[SOTA]** Park, Mozafari, Sorenson, Wang. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[Foundational]** Politis, Romano, Wolf. *Subsampling.* Springer, 1999. — [DOI](https://doi.org/10.1007/978-1-4612-1554-7)

## 10. Worked Example

**Delta method for a ratio.** Query: `SELECT SUM(revenue)/SUM(cost) FROM sales` — a derived ratio $\theta = \mu_x/\mu_y$. From a sample of $n = 400$ rows we get per-row means $\hat\mu_x = 50$, $\hat\mu_y = 20$, so $\hat\theta = 2.5$. Sample (co)variances per row: $s_x^2 = 900$, $s_y^2 = 100$, $s_{xy} = 150$.

The delta method linearizes $g(\mu_x,\mu_y)=\mu_x/\mu_y$ with gradient $\nabla g = (1/\mu_y,\ -\mu_x/\mu_y^2) = (0.05,\ -0.125)$. The variance of $\hat\theta$ is

$$\widehat{\mathrm{Var}}(\hat\theta) = \tfrac1n\,\nabla g^\top \Sigma\, \nabla g = \tfrac1{400}\big(0.05^2\cdot 900 + (-0.125)^2\cdot 100 + 2(0.05)(-0.125)\cdot 150\big).$$

Compute: $0.0025\cdot900 = 2.25$; $0.015625\cdot100 = 1.5625$; cross term $2(-0.00625)(150) = -1.875$. Sum $= 1.9375$, divided by $400$ gives $0.00484$, so $\mathrm{SE} = 0.0696$. The $95\%$ CI is $2.5 \pm 1.96(0.0696) = [2.36,\ 2.64]$.

Note the negative cross term ($s_{xy}>0$): positively correlated numerator and denominator **shrink** the interval — ignoring $\Sigma$'s off-diagonal (treating the two `SUM`s as independent) would overstate the width to $\sqrt{(2.25+1.5625)/400}=0.0977$. This is exactly the correlation-among-sub-aggregates effect of section 2; it also fails for non-smooth $g$ (e.g. `MIN/MAX`), motivating the open cases in section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
