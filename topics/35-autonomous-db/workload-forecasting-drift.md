# Workload Forecasting Under Drift

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/workload-forecasting-drift` · **Status:** open

## 1. Problem Statement
A self-driving database must act *ahead* of demand: build an index before the query that needs it arrives, scale storage before ingest spikes. This requires **forecasting the future workload** — arrival rate, query *mix* (which templates/clusters), and query *shape* (parameters, predicate ranges, data touched) — far enough into the future to amortize the action's build cost, while the underlying process **drifts** (gradual trend, seasonality, and abrupt *regime change*).

Variants:
- **Point-forecast variant:** predict $\hat\lambda_{t+h}$ and mix vector $\hat p_{t+h}$ at horizon $h$, minimizing forecast loss.
- **Calibrated-uncertainty variant:** produce prediction *intervals/sets* with valid coverage **under drift**, so the planner can act on risk, not just the mean.
- **Change-detection variant:** decide *when* a regime change has occurred (so as to re-plan), trading detection delay against false alarms.

The decision-relevant object is not the raw forecast but a *calibrated predictive distribution* whose tails the downstream planner can trust under non-stationarity.

## 2. Mathematical Foundations
Model the workload as a marked point process: events $(t_i, m_i)$ with arrival times $t_i$ and marks $m_i\in M$ (query template + parameters). Arrival intensity $\lambda(t)$ and mark distribution $p_t(m)$ are time-varying. **Drift** is formalized as non-stationarity of the joint law $P_t$; *regime change* is a change point $\tau$ with $P_{t<\tau}\neq P_{t\ge\tau}$.

Forecasting quality under drift is bounded by **online learning regret**. For prediction with expert/forecaster advice, *dynamic regret* against a comparator sequence $u_1,\dots,u_T$ with path length $P_T=\sum_t\|u_t-u_{t-1}\|$ scales as $O(\sqrt{T(1+P_T)})$ — fundamental: no learner beats $\Omega(\sqrt{T P_T})$ when the environment can drift with budget $P_T$. Calibration under drift rests on **adaptive conformal prediction**: maintaining coverage $\Pr(y_{t}\in \hat C_t)\approx 1-\alpha$ via online quantile updates $\theta_{t+1}=\theta_t+\eta(\alpha-\mathbb 1[y_t\notin\hat C_t])$ (Gibbs & Candès). Change detection rests on the **CUSUM / GLR** framework with the information-theoretic delay–false-alarm tradeoff (Lorden's bound): minimum detection delay $\sim \log(1/\text{ARL}^{-1})/D_{KL}$ in the KL divergence between regimes.

## 3. State of the Art (SOTA)
**Systems-SOTA.** QueryBot 5000 (Ma et al., SIGMOD 2018) clusters query templates and forecasts each cluster's arrival with linear + LSTM ensembles, explicitly for self-driving DBMS planning. Microsoft's workload forecasting for autoscaling (Seagull / resource-prediction line) forecasts at the tenant level. DBMS autoscalers in cloud (Azure SQL, Amazon Aurora Serverless) use proprietary short-horizon predictors.

**Theory-SOTA.** Adaptive conformal inference (ACI, Gibbs & Candès 2021) and its strongly-adaptive successors give *distribution-free* coverage guarantees that survive arbitrary drift; dynamic-regret optimal online learners (Zhang et al.) give the matching $\sqrt{TP_T}$ rates. These are general, not DB-specific.

## 4. Upper Bound
For the calibrated-uncertainty variant, ACI guarantees long-run coverage $|\tfrac1T\sum_t \mathbb 1[y_t\in\hat C_t] - (1-\alpha)| = O(1/T)$ **with no distributional assumptions whatsoever** (online adversarial model) — the strongest available positive result. For point forecasting under bounded drift budget $P_T$, online-learning algorithms achieve dynamic regret $O(\sqrt{T(1+P_T)})$ (online convex optimization model).

## 5. Lower Bound
**Information-theoretic / online-adversarial.** No forecaster can have dynamic regret $o(\sqrt{TP_T})$ against drift budget $P_T$ (minimax lower bound, OCO model). For change detection, **Lorden's bound** is a worst-case lower bound on detection delay given a false-alarm constraint — you *cannot* detect an abrupt mix change faster than $\sim \log(\text{ARL})/D_{KL}$ samples. And point forecasting of an adversarial regime change is impossible *before* it manifests (the future is not a function of the past at a true change point) — a hard impossibility for the point-forecast variant.

## 6. The Gap
For *coverage* the gap is essentially **closed** (ACI matches the adversarial optimum). For *actionable* forecasting it is **open**: tight calibrated intervals are achievable, but their *width* under regime change can blow up to vacuous, and the planner needs narrow-yet-valid intervals. The open question is achieving small-width calibrated forecasts that also minimize *downstream decision regret*, not just coverage. Closing it requires coupling the forecaster's loss to the planner's action cost.

## 7. Current Research (as of June 2026)
Active threads: decision-aware / "end-to-end" forecasting where the loss is the planner's regret rather than forecast MSE; conformal methods specialized to point-process arrivals; foundation-model time-series forecasters (e.g. TimesFM-style) applied to DB telemetry with conformal wrappers for coverage *(frontier — verify)*; and drift-triggered re-planning that couples CUSUM detection to the action loop (CMU self-driving DB group under Pavlo; Microsoft GSL; uncertainty-quantification groups around Candès/Tibshirani). Whether large pretrained time-series models improve *DB-workload* forecasting over per-tenant models remains empirically unsettled *(frontier — verify)*.

## 8. Future Work
- Decision-regret-optimal forecasting tied to build/rollback costs.
- Calibrated *interval-width* guarantees, not just coverage, under bounded drift.
- Joint forecast + change-detection with provable combined delay/coverage bounds.
- Forecasting query *shape* (parameter distributions), not just arrival/mix.

## 9. Key References
- **[Foundational]** Ma, L., Van Aken, D., Hefny, A., Mezerhane, G., Pavlo, A., Gordon, G. *Query-based Workload Forecasting for Self-Driving Database Management Systems.* SIGMOD, 2018.
- **[Foundational]** Gibbs, I., Candès, E. *Adaptive Conformal Inference Under Distribution Shift.* NeurIPS, 2021.
- **[SOTA]** Zhang, L., Lu, S., Zhou, Z.-H. *Adaptive Online Learning in Dynamic Environments.* NeurIPS, 2018.
- **[Foundational]** Lorden, G. *Procedures for Reacting to a Change in Distribution.* Annals of Mathematical Statistics, 1971.
- **[SOTA]** Poppe, O., et al. *Seagull / Resource forecasting for cloud databases.* (Microsoft) PVLDB, 2020–2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
