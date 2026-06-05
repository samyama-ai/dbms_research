# In-database forecasting with error bounds

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/in-db-forecasting-bounds` · **Status:** open

## 1. Problem Statement
Modern TSDBs expose server-side forecasting (e.g., `forecast(metric, horizon)` SQL functions, Prophet/ARIMA UDFs, ML built-ins). The research problem is to make these forecasts carry **calibrated, query-composable uncertainty**: for any future horizon $h$ and any miscoverage level $\alpha$, return prediction intervals $[\hat L_h, \hat U_h]$ with a *provable* coverage guarantee — and have that uncertainty propagate correctly when the forecast is used inside further SQL (aggregated, joined, thresholded for alerting). Naively, intervals from a fitted model are conditional on the model being correct; we want **distribution-free / finite-sample** guarantees that survive model misspecification and that compose under relational operators.

Variants: **point forecast** (minimize horizon-$h$ loss); **interval/coverage** (guarantee $\Pr[y_{t+h}\in[\hat L_h,\hat U_h]]\ge 1-\alpha$, marginally or conditionally); **composable** (bounds on $\mathrm{SUM}$, percentile, or anomaly-score of forecasts). The hard, distinctive requirement is *validity under arbitrary horizon and SQL composition* at TSDB scale (millions of series).

## 2. Mathematical Foundations
Let a series $y_1,\dots,y_t$ generate horizon-$h$ targets. A forecaster $\hat f$ plus a nonconformity score $S(\cdot)$ yields **conformal prediction** intervals. Under *exchangeability*, split conformal gives finite-sample marginal coverage
$$ \Pr\big[y_{t+h} \in C_\alpha(x)\big] \ge 1-\alpha, $$
with $C_\alpha$ the $\lceil(1-\alpha)(n+1)\rceil$-th quantile of calibration scores (Vovk; Lei et al. 2018). Time series **violate exchangeability**, so the relevant theory is *adaptive/online conformal* — Adaptive Conformal Inference (ACI, Gibbs–Candès 2021) and Conformal PID control (Angelopoulos et al. 2023) — which guarantee *long-run average coverage* $\frac1T\sum_t \mathbf{1}[\text{err}_t]\to\alpha$ under arbitrary, even adversarial, distribution shift, via online gradient updates of the quantile level. Composability draws on **error propagation** and union bounds: a guarantee on $k$ forecasts combined by an $L$-Lipschitz aggregate yields an inflated interval; sum of intervals is straightforward, percentiles need order-statistic conformal. Underlying point models range from classical ARIMA/ETS (state-space, $O(1)$ online update) to gradient-boosted and deep global models (N-BEATS, TFT, TimesFM).

## 3. State of the Art (SOTA)
**Systems-SOTA:** TimescaleDB + Prophet/`hyperfunctions`, InfluxDB Kapacitor/Flux Holt-Winters, ClickHouse `seriesDecompose`/ML, BigQuery `ML.FORECAST` (ARIMA_PLUS with prediction intervals), Azure Data Explorer `series_decompose_forecast`, Amazon Timestream/Forecast. These emit intervals from *model assumptions* (Gaussian residuals), **not** distribution-free coverage. **Theory-SOTA:** online/adaptive conformal — ACI (Gibbs–Candès, NeurIPS 2021), Conformal PID and *Conformal Prediction for Time Series* (Angelopoulos, Bates, Candès et al. 2023–2024); EnbPI (Xu–Xie, ICML 2021) for bootstrap-conformal under temporal dependence. Foundation TS models (TimesFM, Chronos, Moirai, 2024) give strong zero-shot point forecasts but ship heuristic, not guaranteed, intervals.

## 4. Upper Bound
**Marginal/long-run coverage:** ACI and Conformal-PID achieve $|\frac1T\sum_t\mathbf{1}[\text{miscover}] - \alpha| = O(1/\sqrt{T})$ (or $O(1/T)$ for the running average error of the adaptive level) with $O(1)$ per-step update and $O(\text{window})$ space — fully online, model-agnostic, in the adversarial-shift model. Split conformal gives exact finite-sample $1-\alpha$ marginal coverage under exchangeability with one pass over a calibration window. Composing $k$ such intervals by a sum preserves validity with interval width growing as $O(\sqrt{k})$ for independent-ish errors, $O(k)$ worst case.

## 5. Lower Bound
**Conditional coverage is impossible** distribution-free: Vovk (2012) and Barber–Candès–Ramdas–Tibshirani (2021, "Limits of distribution-free conditional predictive inference") show no finite-width interval can guarantee $\Pr[y\in C \mid x]\ge1-\alpha$ for all distributions — only marginal/approximate-conditional is attainable. Under genuine adversarial drift, any method with *instantaneous* (not long-run) coverage must have unbounded-width intervals; this is an information-theoretic barrier, not an algorithmic one. Thus *per-horizon, per-series exact conditional bounds* are unachievable in general — the achievable target is long-run/marginal coverage.

## 6. The Gap
The gap here is **semantic, not a numeric upper-vs-lower spread**: we *can* get long-run marginal coverage online, but TSDB users want *conditional* (per-series, per-horizon) guarantees, which are provably impossible distribution-free. The open problem is to (a) define a coverage notion that is both *achievable* and *meaningful inside SQL composition*, and (b) make adaptive conformal *scale to millions of series* with shared/global calibration. This is **genuinely open**: no system today offers composable, scalable, drift-robust calibrated forecasts.

## 7. Current Research (as of June 2026)
Active: conformal foundation-model forecasting (wrapping TimesFM/Chronos with adaptive conformal) and *multi-series / hierarchical* conformal that shares calibration across correlated series for tighter intervals *(frontier — verify)*; Candès/Stanford and Ramdas/CMU groups on online conformal under drift; Berkeley (Angelopoulos, Jordan, Malik) on conformal control. Database-side integration — pushing conformal calibration into the query engine so intervals compose through `GROUP BY`/joins — is appearing in research prototypes but not mainstream engines *(frontier — verify)*.

## 8. Future Work
- A relational algebra of prediction intervals: rules for how coverage propagates through selection, aggregation, join, and thresholding.
- Scalable shared-calibration for millions of series with per-series adaptivity (hierarchical/cluster conformal).
- Tight interval widths under known temporal dependence (beyond worst-case union bounds).
- Coupling with drift maintenance (`online-model-drift.md`) and alerting FDR control (`anomaly-detection-fdr-control.md`).

## 9. Key References
- **[Foundational]** V. Vovk, A. Gammerman, G. Shafer. *Algorithmic Learning in a Random World.* Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)
- **[Foundational]** R. F. Barber, E. J. Candès, A. Ramdas, R. J. Tibshirani. *The limits of distribution-free conditional predictive inference.* Information and Inference, 2021. — [DOI](https://doi.org/10.1093/imaiai/iaaa017)
- **[SOTA]** I. Gibbs, E. Candès. *Adaptive Conformal Inference Under Distribution Shift.* NeurIPS, 2021. — [arXiv](https://arxiv.org/abs/2106.00170)
- **[SOTA]** A. Angelopoulos, E. Candès, R. Tibshirani. *Conformal PID Control for Time Series Prediction.* NeurIPS, 2023. — [arXiv](https://arxiv.org/abs/2307.16895)
- **[SOTA]** C. Xu, Y. Xie. *Conformal Prediction Interval for Dynamic Time-Series (EnbPI).* ICML, 2021. — [PMLR](https://proceedings.mlr.press/v139/xu21h.html)
- **[Survey]** A. Angelopoulos, S. Bates. *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification.* Foundations and Trends in ML, 2023. — [arXiv](https://arxiv.org/abs/2107.07511)

## 10. Worked Example

**Split conformal interval for a 1-step forecast.** A model $\hat f$ forecasts a metric; on a calibration window of $n=9$ recent points we record absolute residuals (nonconformity scores) $S_i = |y_i - \hat f(x_i)|$:

$$\{0.2,\;0.5,\;0.9,\;1.1,\;1.3,\;1.6,\;2.0,\;2.4,\;3.0\}.$$

For miscoverage $\alpha = 0.1$, take the $\lceil (1-\alpha)(n+1)\rceil = \lceil 0.9\times 10\rceil = 9$-th smallest score $= 3.0 = q$. If the next point's forecast is $\hat f = 50$, the interval is $[\,50-3.0,\;50+3.0\,] = [47,53]$, with finite-sample marginal coverage $\ge 1-\alpha = 0.9$ **under exchangeability**.

But telemetry is not exchangeable: suppose drift makes the true error jump and the point lands at $54$ — a miss. **ACI** reacts: it updates the effective level $\alpha_t \leftarrow \alpha_t + \gamma(\alpha - \mathbf{1}[\text{miss}])$ with step $\gamma=0.05$, so after the miss $\alpha_t \to 0.1 + 0.05(0.1-1) = 0.055$, *lowering* the target miscoverage and thus *widening* the next quantile/interval. Over $T$ steps this drives $\tfrac1T\sum_t \mathbf{1}[\text{miss}_t]\to 0.1$ — the achievable *long-run* guarantee. The catch (§5): no finite-width rule gives *conditional* coverage at this specific instant.

---
*Part of the [DBMS Research catalog](../../README.md).*
