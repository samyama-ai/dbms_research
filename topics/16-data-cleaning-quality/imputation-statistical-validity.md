# Statistically Valid Imputation for Analytics

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/imputation-statistical-validity` · **Status:** empirically-open

## 1. Problem Statement
Imputing missing values to maximize per-cell accuracy is the wrong objective for analytics: it shrinks variance and distorts correlations, **biasing downstream estimators** (means, regressions, aggregates, ML models). The problem: **impute so the completed data preserves the joint distribution and yields (asymptotically) unbiased, correctly-calibrated downstream estimates** with valid uncertainty.

Variants:
- **Estimation:** Produce $\hat\theta$ (e.g., a regression coefficient, an AVG, a quantile) from imputed data that is unbiased/consistent for the true $\theta$.
- **Inference:** Produce confidence intervals with nominal coverage despite imputation uncertainty.
- **Distribution preservation:** Make the imputed joint $\hat P$ close to true $P$ in a divergence (KL, Wasserstein).

The central tension: best-MSE imputation (conditional mean) is provably *bad* for variance/covariance estimands.

## 2. Mathematical Foundations
Missingness is classified (Rubin 1976) as **MCAR**, **MAR** ($\Pr(\text{missing}\mid X)$ depends only on observed values), or **MNAR**. Under **MAR**, valid inference is achievable; under **MNAR** the missingness mechanism is generally **non-identifiable** without extra assumptions. **Multiple Imputation (MI)** draws $m$ completions from the Bayesian posterior predictive $P(X_{\text{mis}}\mid X_{\text{obs}})$; Rubin's rules combine estimates: $\bar\theta=\frac1m\sum\hat\theta_j$, total variance $T = \bar W + (1+\tfrac1m)B$ with within-variance $\bar W$ and between-variance $B$. This yields **proper** inference (correct coverage) when the imputation model is congenial with the analysis model. Single conditional-mean imputation drives $B\to 0$, **understating variance** and attenuating regression slopes. **Inverse-probability weighting (IPW)** and **doubly-robust / AIPW** estimators give consistency if either the missingness or outcome model is correct, with semiparametric-efficiency bounds (Robins–Rotnitzky–Zhao).

## 3. State of the Art (SOTA)
- **Multiple Imputation by Chained Equations (MICE / `mice`)** (van Buuren & Groothuis-Oudshoorn, JSS 2011): the statistical workhorse for proper multivariate MI.
- **Deep generative imputation: GAIN** (Yoon, Jordon, van der Schaar, ICML 2018), **MIWAE/notMIWAE** (Mattei–Frellsen, ICML 2019), VAE/normalizing-flow and diffusion-based imputers—strong distributional fit empirically.
- **MissForest** (Stekhoven–Bühlmann, 2012): random-forest iterative imputation, robust to nonlinearity.
- **Optimal-transport imputation** (Muzellec et al., ICML 2020): minimizes Sinkhorn divergence between mini-batches to preserve distribution.
- Database-side: **ImputeDB** (Cambronero et al., VLDB 2017) for query-aware imputation cost/accuracy tradeoffs.

Systems-SOTA (DB) optimizes cost+accuracy; statistics-SOTA (MI/AIPW) optimizes *inferential validity*—and the two literatures are only loosely connected.

## 4. Upper Bound
Under correct (congenial) models and MAR, **multiple imputation and AIPW are consistent and asymptotically normal**, with AIPW attaining the **semiparametric efficiency bound** (Robins–Rotnitzky–Zhao 1994); Rubin's combining rules give asymptotically nominal coverage. Deep imputers (GAIN, OT) empirically reduce Wasserstein/feature error but carry **no general bias or coverage guarantees**. So the strongest *provable* upper bound (unbiasedness + valid CIs) holds only for model-based MI/AIPW under MAR with a correctly-specified, congenial model.

## 5. Lower Bound
Under **MNAR**, the estimand is **non-identifiable** in general (Rubin 1976; Manski partial-identification): no imputation can recover $\theta$ without untestable assumptions—an **information-theoretic impossibility**. Even under MAR, **congeniality** (Meng 1994) is necessary: if the imputer's model and analyst's model disagree, MI inference is **invalid** (wrong coverage), and no purely automatic imputer is congenial with all downstream analyses simultaneously. Single (deterministic) imputation **provably** understates variance—a structural lower bound on its inferential validity.

## 6. The Gap
**Empirically open.** Modern deep/OT imputers win on distributional-fit benchmarks but lack the unbiasedness and **coverage guarantees** that classical MI/AIPW provide only under restrictive model assumptions. There is no method that is simultaneously (a) flexible/nonparametric, (b) distribution-preserving, and (c) equipped with valid downstream confidence intervals across arbitrary analyses. The frontier is *empirical*: practitioners observe good point estimates but cannot certify inference. Closing it requires congeniality-aware deep MI with provable (or conformal) coverage.

## 7. Current Research (as of June 2026)
- **Diffusion-model and tabular-foundation-model imputation** (e.g., transformer/TabPFN-style) with attempts at calibrated multiple draws *(frontier — verify)*.
- **Conformal prediction for imputation:** distribution-free coverage on imputed targets/estimands *(frontier — verify)*.
- **Causal/MNAR-robust imputation** using sensitivity analysis and partial identification.
- Groups: Mihaela van der Schaar (Cambridge), Jes Frellsen, Aude Genevay/OT-imputation line, Stef van Buuren (MICE), Robins/Tsiatis semiparametric school.

## 8. Future Work
- Deep MI with congeniality guarantees and valid Rubin-style variance.
- Estimand-targeted imputation: minimize downstream estimator error directly (links to constraint-aware-imputation's query-awareness).
- Principled MNAR handling with reported identification bounds; benchmark suites that score *inference* not just imputation RMSE.

## 9. Key References
- **[Foundational]** D. B. Rubin. *Inference and Missing Data.* Biometrika, 1976. (and *Multiple Imputation for Nonresponse in Surveys*, 1987.)
- **[Foundational]** J. M. Robins, A. Rotnitzky, L. P. Zhao. *Estimation of Regression Coefficients When Some Regressors Are Not Always Observed.* JASA, 1994.
- **[Foundational]** X.-L. Meng. *Multiple-Imputation Inferences with Uncongenial Sources of Input.* Statistical Science, 1994.
- **[SOTA]** S. van Buuren, K. Groothuis-Oudshoorn. *mice: Multivariate Imputation by Chained Equations in R.* JSS, 2011.
- **[SOTA]** J. Yoon, J. Jordon, M. van der Schaar. *GAIN: Missing Data Imputation using Generative Adversarial Nets.* ICML, 2018.
- **[SOTA]** B. Muzellec, J. Josse, C. Boyer, M. Cuturi. *Missing Data Imputation using Optimal Transport.* ICML, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
