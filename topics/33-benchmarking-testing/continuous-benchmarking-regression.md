---
id: 33-benchmarking-testing/continuous-benchmarking-regression
title: "Continuous Benchmarking for Regression Detection"
topic: 33-benchmarking-testing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Continuous Benchmarking for Regression Detection

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/continuous-benchmarking-regression` · **Status:** empirically-open

## 1. Problem Statement

Continuous benchmarking runs performance benchmarks on every commit (or nightly) and must **flag statistically significant regressions** while tolerating noise from microarchitecture, OS scheduling, thermal throttling, cloud-VM neighbors, and nondeterministic query plans. The signal is **high-dimensional** (many benchmarks × metrics: latency, throughput, p99, IPC) and **noisy/non-stationary**.

Variants:
- **Detection (decision) variant:** given a stream of measurements per benchmark, decide whether a *change point* corresponds to a true performance regression vs. noise.
- **Localization variant:** attribute a detected regression to a specific commit (bisection under noise).
- **Optimization variant:** schedule which benchmarks to run, and how many repetitions, to maximize detected-regression-per-CPU-hour under a budget — a sequential experimental-design problem.
- **Multiple-testing control:** bound false discovery rate (FDR) across thousands of benchmark/metric pairs.

## 2. Mathematical Foundations

Model benchmark $i$'s measurement at commit $t$ as $x_{i,t} = \mu_{i,t} + \varepsilon_{i,t}$ with heavy-tailed, possibly heteroscedastic noise $\varepsilon$. A regression is a **change point**: $\mu_{i,t}$ jumps at some $t^*$. Detection is **changepoint analysis**: e.g., **E-Divisive means** (Matteson–James) or **PELT** (Killick et al.) minimizing
$$\sum_{\text{segments}} \mathcal{C}(\text{segment}) + \beta\,(\\#\text{changepoints}),$$
with a penalty $\beta$ trading sensitivity vs. false alarms.

Because thousands of hypotheses are tested, control the **false discovery rate** via Benjamini–Hochberg, or use **e-values / always-valid p-values** (Howard, Ramdas) for *anytime* monitoring of a streaming sequence without inflating type-I error. Robustness to outliers motivates rank-based statistics (Mann–Whitney U) and the **Hodges–Lehmann** shift estimator. The repetition-budget problem is an instance of **best-arm identification / sequential testing**; sample complexity scales as $O(\sigma^2/\Delta^2 \cdot \log(1/\delta))$ to detect an effect size $\Delta$ at confidence $1-\delta$. Dimensionality reduction across correlated benchmarks can exploit low **effective rank** of the metric covariance.

## 3. State of the Art (SOTA)

- **MongoDB's change-point-detection pipeline** (Ingo, Daly et al., *“The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System,”* ICPE 2020) — production E-Divisive-based system; widely cited as systems-SOTA for CI perf.
- **Hunter** (DataStax) and **Fallout** — automated regression detection using E-Divisive over time series.
- **Statistically rigorous microbenchmarking:** Georges, Buytaert, Eeckhout (*“Statistically Rigorous Java Performance Evaluation,”* OOPSLA 2007) — confidence intervals, steady-state detection; foundational for methodology. **Kalibera & Jones** — rigorous benchmarking with hierarchical variance.
- **Academic DB benchmarking:** OLTP-Bench / BenchBase (Difallah et al., VLDB 2013; Cloud-era reboot) standardize workloads; **TPC-C/H/DS** and **YCSB** remain the canonical suites. Cloud variance characterization: Leitner & Cito.

## 4. Upper Bound

PELT computes the optimal segmentation in **$O(n)$ expected** time (vs. $O(n^2)$ for naive optimal partitioning) under a linear-in-changepoints penalty with pruning; E-Divisive is $O(n^2)$ but distribution-free. Always-valid sequential tests (mixture supermartingales / confidence sequences) allow **continuous monitoring** with provable type-I control and detection delay $O(\log(1/\delta)/\Delta^2)$. Best-arm-identification schedulers allocate repetitions near-optimally up to log factors. These are the strongest *guarantees* available; in practice the binding constraint is the unknown, non-stationary noise model, so no method is provably optimal on real CI noise.

## 5. Lower Bound

This is fundamentally **statistical**, so bounds are information-theoretic, not complexity-theoretic. To detect a mean shift of size $\Delta$ against noise variance $\sigma^2$ at error $\delta$ requires $\Omega(\sigma^2/\Delta^2 \cdot \log(1/\delta))$ samples (Le Cam / Fano lower bounds on hypothesis testing) — you *cannot* cheaply detect small regressions in high-variance benchmarks. Under multiple testing, the FDR/power tradeoff is bounded by the **Benjamini–Hochberg** frontier; no procedure beats it without distributional assumptions. There is no "true model" of cloud noise, so any detector has an irreducible false-positive/false-negative floor — making the problem **empirically open** rather than closed by a theorem.

## 6. The Gap

Empirically open. The *statistical machinery* (changepoint detection, anytime-valid inference, FDR control, best-arm budgeting) is mature and near-optimal in its idealized models. The gap is **modeling reality**: CI noise is non-stationary, heavy-tailed, and correlated across benchmarks and over time (warmup, autocorrelation, environment drift). No published method jointly (a) handles non-stationary correlated noise, (b) controls FDR across thousands of metrics, (c) localizes to a commit, and (d) respects a tight compute budget, with validated guarantees on *real* database CI data. Closing it is an empirical/benchmark-construction problem more than a theorem to prove.

## 7. Current Research (as of June 2026)

- Anytime-valid (e-value / confidence-sequence) monitoring applied to CI performance streams, extending Ramdas-group methods to correlated benchmark suites *(frontier — verify)*.
- Learned noise models and variance-reduction via paired/A-B execution on the same hardware slot to cancel environment drift.
- Budget-aware benchmark selection treating CI as sequential experimental design / multi-armed bandits *(frontier — verify)*.
- Cloud-variance-aware methodologies and reproducibility infrastructure (SIGMOD/VLDB reproducibility initiatives) feeding back into detector design.

## 8. Future Work

- Public, labeled corpora of real CI performance time series (with ground-truth regressions) to benchmark detectors.
- Joint models of cross-benchmark correlation enabling shared-strength detection and fewer repetitions.
- Causal localization that combines bisection with changepoint posteriors under a fixed compute budget.
- Standard reporting (effect sizes + confidence sequences) replacing ad-hoc percentage thresholds.

## 9. Key References

- **[Foundational]** A. Georges, D. Buytaert, L. Eeckhout. *Statistically Rigorous Java Performance Evaluation.* OOPSLA, 2007. — [DOI](https://doi.org/10.1145/1297027.1297033)
- **[SOTA]** D. Daly, W. Brown, H. Ingo, J. O'Leary, D. Bradford. *The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System.* ICPE, 2020. — [DOI](https://doi.org/10.1145/3358960.3375791) · [arXiv](https://arxiv.org/abs/2003.00584)
- **[Foundational]** R. Killick, P. Fearnhead, I. A. Eckley. *Optimal Detection of Changepoints with a Linear Computational Cost (PELT).* JASA, 2012. — [DOI](https://doi.org/10.1080/01621459.2012.737745) · [arXiv](https://arxiv.org/abs/1101.1438)
- **[SOTA]** S. R. Howard, A. Ramdas, J. McAuliffe, J. Sekhon. *Time-Uniform, Nonparametric, Nonasymptotic Confidence Sequences.* Annals of Statistics, 2021. — [DOI](https://doi.org/10.1214/20-AOS1991) · [arXiv](https://arxiv.org/abs/1810.08240)
- **[SOTA]** D. E. Difallah, A. Pavlo, C. Curino, P. Cudré-Mauroux. *OLTP-Bench: An Extensible Testbed for Benchmarking Relational Databases.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2732240.2732246)
- **[Foundational]** Y. Benjamini, Y. Hochberg. *Controlling the False Discovery Rate.* JRSS-B, 1995. — [DOI](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)

## 10. Worked Example

Nightly p99 latency (ms) for one benchmark over 12 commits:

$$8.0,\ 8.1,\ 7.9,\ 8.2,\ 8.0,\ 8.1,\ \mathbf{9.4},\ 9.5,\ 9.3,\ 9.6,\ 9.4,\ 9.5$$

A 5%-threshold alarm would fire on the noisy spike at commit 4→5 in many runs and miss the *real* shift. Changepoint detection instead minimizes within-segment cost. Pre-shift mean $\hat\mu_1=8.05$ (commits 1–6), post-shift $\hat\mu_2=9.45$ (commits 7–12); pooled noise $\sigma\approx0.12$. The shift is $\Delta=1.40$, so effect size $\Delta/\sigma\approx11.7$ — huge, detected with very few repetitions.

Sample-complexity check: to confirm a mean shift at confidence $1-\delta=0.99$ ($\log(1/\delta)\approx4.6$), the bound $n\gtrsim \sigma^2/\Delta^2\cdot\log(1/\delta) = 0.0144/1.96 \cdot 4.6 \approx 0.034$ — i.e. a single clean repetition suffices here. Contrast a *small* regression $\Delta=0.1$ at the same $\sigma$: $n\gtrsim 0.0144/0.01\cdot4.6\approx6.6$ repetitions per commit. Detecting small regressions in noisy benchmarks is what burns the compute budget.

---
*Part of the [DBMS Research catalog](../../README.md).*
