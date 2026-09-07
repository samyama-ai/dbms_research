---
id: 35-autonomous-db/drift-detection-triggers
title: "Concept Drift Detection for Triggers"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Concept Drift Detection for Triggers

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/drift-detection-triggers` · **Status:** open

## 1. Problem Statement
A self-driving DBMS relies on learned models (forecasters, cost models, tuning policies) that silently degrade as the workload distribution shifts (**concept drift**). The **drift-detection-for-triggers problem**: decide *when* a model has degraded enough that the controller should re-plan / retrain, balancing detection delay (acting on a stale model) against false triggers (needless, disruptive re-plans), ideally with formal bounds on staleness and false-alarm rate.

Variants:
- **Decision (change detection):** has the data/error distribution changed at time $t$? (sequential hypothesis test.)
- **Optimization:** choose a trigger policy minimizing $\mathbb{E}[\text{staleness cost}] + \lambda\,\mathbb{E}[\text{re-plan cost}]$.
- **Quickest detection:** minimize detection delay subject to a mean-time-between-false-alarms floor.

## 2. Mathematical Foundations
Drift is a change point: pre-change observations (model errors, or workload features) are i.i.d. $\sim F_0$; after an unknown $\tau$ they are $\sim F_1$. The **quickest change detection (QCD)** framework gives the optimal trade-off. Two canonical formulations:

- **Bayesian (Shiryaev):** minimizes expected detection delay subject to a false-alarm probability bound; the Shiryaev statistic is optimal.
- **Minimax (Lorden/Pollak):** **CUSUM** minimizes worst-case expected delay subject to a mean-time-to-false-alarm constraint $\ge\gamma$. Lorden's bound: CUSUM detection delay $\approx \log\gamma / D(F_1\Vert F_0)$, where $D$ is the KL divergence between post- and pre-change distributions — formalizing *staleness vs. false-trigger* as a KL-driven trade-off.

When $F_1$ is unknown (drift magnitude not known a priori), one uses GLR-CUSUM or nonparametric two-sample tests (MMD, Kolmogorov–Smirnov) over sliding windows; **ADWIN** (Bifet–Gavaldà) maintains a variable window and flags drift with Hoeffding-bounded false-positive rate. Detecting drift on the *model's loss* (performance drift) is more directly tied to the trigger objective than detecting raw covariate drift, which may be benign.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Self-driving DB frameworks (Peloton/NoisePage, Pavlo et al., CIDR 2017) include forecast-monitoring to re-plan; QB5000 (Ma et al., SIGMOD 2018) re-forecasts as patterns shift. Production learned-component systems (Bao, learned cardinality estimators) discuss retraining triggers when estimation error spikes. Cloud autoscalers use error-threshold or scheduled retraining.
- **Drift-detection-SOTA:** ADWIN (Bifet–Gavaldà, SDM 2007), DDM/EDDM, and Page–Hinkley / CUSUM remain the workhorses; MMD-based and kernel change detection for high-dim features.
- **Theory-SOTA:** Optimality of CUSUM (Lorden 1971; Moustakides 1986) and Shiryaev's Bayesian QCD.

## 4. Upper Bound
CUSUM is asymptotically minimax-optimal: for a false-alarm constraint MTBFA $\ge\gamma$, expected detection delay is $\sim \log\gamma / D(F_1\Vert F_0)$ (Lorden 1971; Moustakides 1986) — a tight upper bound on staleness given a false-trigger floor. Shiryaev's procedure is exactly Bayes-optimal for the geometric-prior change-point model. ADWIN guarantees a false-positive rate $\le\delta$ and a bounded detection delay via Hoeffding bounds, with $O(\log W)$ memory for window $W$. These give *certified* staleness/false-trigger bounds for the detection sub-problem.

## 5. Lower Bound
The QCD trade-off is information-theoretically tight: **no detector** can achieve mean delay below $\sim\log\gamma / D(F_1\Vert F_0)$ while keeping MTBFA $\ge\gamma$ (Lorden's lower bound matches CUSUM's upper bound). As $D(F_1\Vert F_0)\to 0$ (subtle drift), required delay $\to\infty$ — small drifts are provably slow to detect. For unknown post-change distribution, GLR detectors pay an unavoidable $\log$-factor penalty. Detecting *adversarial* drift crafted to stay below the KL threshold is impossible within any fixed delay (info-theoretic).

## 6. The Gap
The detection sub-problem (is there a change in a known error stream?) has matching upper/lower bounds. The **open gap** is the *trigger-decision* problem on top: classical QCD bounds the delay to detect a distributional change, but the controller cares about a *task-relevant* threshold — drift that actually degrades decisions, not every statistical change. There is no tight theory mapping QCD delay/false-alarm to *end-to-end control regret and re-plan cost*, especially when re-planning itself perturbs the system (the action changes the distribution). Coupling QCD with the value-of-re-planning under non-stationarity is open.

## 7. Current Research (as of June 2026)
- Performance/loss-drift detection (monitoring model error, not just covariates) tied to retraining triggers *(frontier — verify)*.
- Cost-aware trigger policies trading re-plan disruption against staleness via bandit/RL meta-controllers *(frontier — verify)*.
- Conformal-prediction-based drift signals giving distribution-free trigger thresholds.
- Groups: CMU NoisePage line, the data-streams / concept-drift community (Bifet, Gama), and QCD theory (Veeravalli, Tartakovsky).

## 8. Future Work
- Trigger theory that bounds end-to-end control regret, not just detection delay.
- Joint modeling of re-plan cost and action-induced distribution shift (closed-loop QCD).
- Multi-model fleets: coordinated triggers avoiding correlated retraining storms.
- Distribution-free, task-aware drift signals with provable false-trigger budgets.

## 9. Key References
- **[Foundational]** G. Lorden. *Procedures for Reacting to a Change in Distribution.* Annals of Mathematical Statistics, 1971. — [DOI](https://doi.org/10.1214/aoms/1177693055)
- **[Foundational]** G. V. Moustakides. *Optimal Stopping Times for Detecting Changes in Distributions.* Annals of Statistics, 1986. — [DOI](https://doi.org/10.1214/aos/1176350164)
- **[Foundational]** A. Shiryaev. *On Optimum Methods in Quickest Detection Problems.* Theory of Probability & Its Applications, 1963. — [DOI](https://doi.org/10.1137/1108002)
- **[SOTA]** A. Bifet, R. Gavaldà. *Learning from Time-Changing Data with Adaptive Windowing (ADWIN).* SDM, 2007. — [DOI](https://doi.org/10.1137/1.9781611972771.42)
- **[SOTA]** L. Ma et al. *Query-based Workload Forecasting for Self-Driving Database Management Systems.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196908)
- **[Survey]** V. Veeravalli, T. Banerjee. *Quickest Change Detection.* Academic Press Library in Signal Processing, 2014. — [arXiv](https://arxiv.org/abs/1210.5552)

## 10. Worked Example

A cost model's prediction error is monitored to trigger retraining. Pre-drift, per-query absolute error is Gaussian $F_0=\mathcal N(\mu_0{=}1.0,\sigma{=}0.2)$; after an undetected schema shift at time $\tau$ it jumps to $F_1=\mathcal N(\mu_1{=}1.4,\sigma{=}0.2)$. We want a CUSUM trigger with mean-time-between-false-alarms $\gamma=10^4$ samples.

**KL divergence** between the two normals (same variance): $D(F_1\Vert F_0)=\dfrac{(\mu_1-\mu_0)^2}{2\sigma^2}=\dfrac{0.4^2}{2(0.2)^2}=\dfrac{0.16}{0.08}=2.0$ nats.

**Expected detection delay** (Lorden/Moustakides asymptotics): $\mathbb E[\text{delay}]\approx\dfrac{\log\gamma}{D(F_1\Vert F_0)}=\dfrac{\ln 10^4}{2.0}=\dfrac{9.21}{2.0}\approx 4.6$ samples.

So with a false alarm only every $10{,}000$ queries, the controller detects this drift within $\sim 5$ queries — fast, because the shift is large ($D=2$). Halve the shift to $\mu_1=1.2$ and $D$ drops to $0.5$, pushing delay to $\approx 18$ samples; a subtle shift with $D=0.05$ needs $\approx 184$ — illustrating the lower bound $\text{delay}\to\infty$ as $D\to 0$: small drifts are provably slow to detect at any fixed false-alarm budget.

---
*Part of the [DBMS Research catalog](../../README.md).*
