# In-DB anomaly detection with false-alarm guarantees

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/anomaly-detection-fdr-control` · **Status:** open

## 1. Problem Statement
TSDBs run streaming anomaly detectors over millions of series to drive alerting. The problem is **statistical**: emit alerts so that the **false-alarm rate is provably controlled** — either the per-series false-positive rate (type-I), the **false discovery rate** $\mathrm{FDR}=\mathbb{E}[V/\max(R,1)]$ (expected fraction of false alarms among all alarms), or family-wise error — *in a streaming, online, massively-multiple-testing* setting, while retaining power (detecting true anomalies promptly). Naive per-series thresholds produce a flood of false alarms: with $m=10^6$ series each tested every minute, even a $10^{-4}$ per-test false rate yields $\sim$hundreds of false alarms per minute.

Variants: **online FDR control** (control FDR over a never-ending stream of tests); **point vs. collective** anomalies (single spike vs. anomalous window); **detection-delay-constrained** control (bound false alarms *and* expected delay). The hard, distinctive requirement is *provable error-rate control under online multiplicity at scale*, not merely a good detector.

## 2. Mathematical Foundations
Each test produces a $p$-value (or e-value/anomaly score calibrated to one). Classical **Benjamini–Hochberg** (1995) controls FDR $\le \alpha$ for a *batch* of $m$ tests under independence/PRDS. Streaming requires **online FDR**: LORD and SAFFRON (Javanmard–Montanari 2018; Ramdas–Zrnic–Wainwright–Jordan 2018) maintain an "alpha-wealth" budget, spending significance level $\alpha_t$ at each test so that $\mathrm{FDR}(t)\le\alpha$ for all $t$, via
$$ \sum_t \alpha_t \le \alpha\cdot(\text{wealth earned from past rejections}). $$
**E-values** and *e-LOND/e-SAFFRON* (Wang–Ramdas 2022) give validity under arbitrary dependence — crucial because nearby series and timestamps are correlated. Per-series detection theory rests on **sequential change-point** methods (CUSUM, GLR) with the **average-run-length-to-false-alarm** (ARL) as the false-alarm metric (Lorden's optimality). Calibrating scores to valid $p$/e-values uses **conformal anomaly detection** (exchangeability → finite-sample valid). Multiplicity across the *time × series* grid is the core difficulty.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Twitter AnomalyDetection (S-H-ESD), Facebook Prophet residual thresholds, Netflix RAD, Microsoft/Azure Anomaly Detector (SR-CNN, KDD 2019), Datadog/Grafana watchdog. These tune thresholds and sensitivity but **do not provide FDR/false-alarm guarantees** across the population of series *(frontier — verify)*. Numenta HTM and Matrix-Profile/STUMPY give unsupervised detectors without error-rate control. **Theory-SOTA:** online FDR (LORD++, SAFFRON, ADDIS — Tian–Ramdas 2019), e-value online testing (Wang–Ramdas 2022), and conformal anomaly detection (Laxhammar–Falkman; Bates et al. 2023 "testing for outliers with conformal p-values"). The two communities — practical TS detectors and online-FDR theory — are only beginning to merge.

## 4. Upper Bound
**FDR control:** SAFFRON/LORD provide $\mathrm{FDR}(t)\le\alpha$ for *all* $t$ on a stream under independence/PRDS, with $O(1)$ amortized update per test and $O(\text{active rejections})$ memory; ADDIS improves power under conservative nulls. **Arbitrary dependence** (correlated series/time): e-LOND and online-BY-style corrections still control FDR at the cost of a $\log m$-type power penalty. Per-series, CUSUM is **optimal** (Lorden/Moustakides) — it minimizes worst-case expected detection delay for a fixed ARL-to-false-alarm. Conformal calibration yields finite-sample valid $p$-values with one calibration pass under exchangeability.

## 5. Lower Bound
There is a fundamental **power vs. error-rate** trade-off: controlling FDR at $\alpha$ caps achievable true-detection rate (info-theoretic, via the testing risk lower bounds). Under **arbitrary dependence**, any FDR-controlling online procedure must pay a multiplicity penalty — controlling FDR with valid p-values under unknown dependence forces a $\Theta(\log m)$ effective-threshold inflation (Benjamini–Yekutieli factor), provably reducing power. For detection, the **ARL–delay** lower bound (Lorden) makes *zero false alarms with bounded delay* impossible: expected delay $\gtrsim \log(\mathrm{ARL})/\mathrm{KL}(\text{post}\|\text{pre})$. Thus arbitrarily-low false-alarm and arbitrarily-fast detection are jointly unattainable.

## 6. The Gap
Online FDR is solved *abstractly* (LORD/SAFFRON/e-values) and per-series change detection is *tight* (CUSUM optimality). The **gap is integration at scale**: there is no method that simultaneously (a) controls FDR over the full *time × millions-of-series* grid under realistic spatial/temporal dependence, (b) bounds detection delay, and (c) runs in TSDB-budget streaming compute — with matching power lower bounds. This is **genuinely open**: the joint "FDR + delay + dependence + scale" guarantee has not been achieved or proven impossible.

## 7. Current Research (as of June 2026)
Active: **e-value online testing under dependence** for correlated series (Ramdas/CMU, Wang) *(frontier — verify)*; conformal anomaly detection with online recalibration (Bates/Candès lineage); structure-aware multiplicity that exploits the series-correlation graph to *recover* power lost to dependence corrections *(frontier — verify)*; and systems work embedding online-FDR alpha-wealth bookkeeping into streaming engines (Flink/Materialize) for alerting pipelines. Links to drift (`online-model-drift.md`) — anomaly scores must stay calibrated under drift — and to multivariate detection (`multivariate-correlation-anomaly.md`).

## 8. Future Work
- An online procedure controlling FDR over the time × series grid with explicit detection-delay bounds.
- Dependence-aware multiplicity that exploits known series-correlation structure to regain power.
- Calibrated anomaly scores robust to concept drift (drift-conformal).
- Standardized labeled benchmarks at realistic cardinality and dependence (beyond NAB/Yahoo S5).

## 9. Key References
- **[Foundational]** Y. Benjamini, Y. Hochberg. *Controlling the False Discovery Rate.* JRSS-B, 1995. — [DOI](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)
- **[Foundational]** G. Lorden. *Procedures for Reacting to a Change in Distribution.* Annals of Mathematical Statistics, 1971. — [DOI](https://doi.org/10.1214/aoms/1177693055)
- **[SOTA]** A. Ramdas, T. Zrnic, M. Wainwright, M. Jordan. *SAFFRON: An Adaptive Algorithm for Online Control of the False Discovery Rate.* ICML, 2018. — [arXiv](https://arxiv.org/abs/1802.09098)
- **[SOTA]** A. Javanmard, A. Montanari. *Online Rules for Control of False Discovery Rate (LORD).* Annals of Statistics, 2018. — [DOI](https://doi.org/10.1214/17-AOS1559)
- **[SOTA]** R. Wang, A. Ramdas. *False Discovery Rate Control with E-values.* JRSS-B, 2022. — [DOI](https://doi.org/10.1111/rssb.12489)
- **[SOTA]** S. Bates, E. Candès, L. Lei, Y. Romano, M. Sesia. *Testing for Outliers with Conformal p-values.* Annals of Statistics, 2023. — [DOI](https://doi.org/10.1214/22-AOS2244)

## 10. Worked Example

Suppose a 5-minute monitoring window produced $m=10$ anomaly $p$-values, one per series, sorted:

$$0.001,\ 0.008,\ 0.012,\ 0.021,\ 0.030,\ 0.18,\ 0.25,\ 0.41,\ 0.63,\ 0.90.$$

Apply **Benjamini–Hochberg** at $\alpha=0.05$ (batch view). Find the largest $k$ with $p_{(k)}\le \frac{k}{m}\alpha=\frac{k}{10}(0.05)=0.005k$:

| $k$ | $p_{(k)}$ | $0.005k$ | $p_{(k)}\le$? |
|----|-----------|----------|----|
| 1 | 0.001 | 0.005 | yes |
| 2 | 0.008 | 0.010 | yes |
| 3 | 0.012 | 0.015 | yes |
| 4 | 0.021 | 0.020 | no |
| 5 | 0.030 | 0.025 | no |

Largest passing $k=3$, so BH rejects the 3 smallest — alert on those series. A naive per-series cut at $0.05$ would have fired on 5 series (through $p=0.030$), inflating false alarms.

Now stream it: at test $t$ an **online** rule (LORD/SAFFRON) cannot peek ahead, so it spends a wealth-budgeted level $\alpha_t$ — e.g. starting wealth $0.025$, paying $\alpha_1=0.005$ on the first test and *earning back* budget only when a rejection occurs, keeping $\mathrm{FDR}(t)\le0.05$ for every $t$ on the never-ending series $\times$ time grid.

---
*Part of the [DBMS Research catalog](../../README.md).*
