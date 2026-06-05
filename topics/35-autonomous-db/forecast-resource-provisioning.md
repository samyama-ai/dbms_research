# Forecast-Driven Resource Provisioning

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/forecast-resource-provisioning` · **Status:** empirically-open

## 1. Problem Statement
An autonomous DBMS must scale compute, memory, buffer pool, connections, and storage *ahead* of demand, using a workload forecast, so that resources are present when load arrives despite non-zero provisioning latency (VM spin-up, cache warm-up, replica catch-up). The **forecast-driven provisioning problem**: given a predicted demand trajectory $\hat{d}_{t:t+H}$ with uncertainty, choose a provisioning trajectory $r_{t:t+H}$ minimizing cost subject to bounded under-provisioning (SLA violation) and bounded over-provisioning (waste).

Variants:
- **Optimization:** minimize $\sum_t \big(c\,r_t + p\,(\hat d_t - r_t)_+\big)$ over feasible $r$ obeying ramp limits.
- **Decision:** is there a schedule meeting an SLA-violation budget $\le \beta$ at cost $\le B$?
- **Online/competitive:** decide $r_t$ without future knowledge, bounding competitive ratio vs. the offline optimum.

## 2. Mathematical Foundations
Demand $d_t$ is a stochastic process; the forecaster outputs $\hat d_{t:t+H}$ plus prediction intervals. Provisioning is constrained by ramp/lead time $L$: $r_{t}$ takes effect at $t+L$. This is a **lot-sizing / capacity-with-switching-cost** problem; the convex-cost online version is the **Convex Body Chasing / Smoothed Online Convex Optimization (SOCO)** problem.

Per-step cost $f_t(r_t)=c\,r_t + p\,(d_t-r_t)_+ + s\,|r_t-r_{t-1}|$, where $s$ is a switching (scaling-action) cost. SOCO with movement cost admits competitive online algorithms; in $1$-D, **Lazy Capacity Provisioning** (Lin et al.) is $3$-competitive against the offline optimum. The newsvendor structure sets the optimal service level: the cost-optimal quantile is $q^\* = p/(p+c)$ of the predictive distribution of $d$, so calibrated *quantile* forecasts (not point forecasts) are what provisioning needs. Robustness uses chance constraints $\Pr[r_t<d_t]\le\beta$ or distributionally-robust (Wasserstein-ball) reformulations.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** QB5000 / the Peloton-NoisePage forecaster (Ma et al., SIGMOD 2018) clusters query arrival patterns and forecasts per-cluster volume to drive provisioning/index actions. Snowflake and Amazon Aurora Serverless / Redshift autoscaling perform reactive + predictive scaling in production. PerfGuard / cloud-DB autoscalers combine forecasts with control loops.
- **Forecasting:** ARIMA/Prophet baselines; deep models (DeepAR, N-BEATS, Temporal Fusion Transformer, PatchTST) give probabilistic multi-horizon forecasts now used for capacity.
- **Theory-SOTA:** SOCO / convex body chasing competitive algorithms (Lin et al. 2013; Sellke 2020 for nested convex body chasing) provide the provisioning-control guarantees.

## 4. Upper Bound
For $1$-D capacity provisioning with switching cost, **Lazy Capacity Provisioning is $3$-competitive** (online, against offline optimum; Lin, Wierman, Andrew, Thereska, 2013). General convex body chasing in $\mathbb{R}^n$ is $O(\sqrt{n})$-competitive (Argue et al. / Sellke 2020). With a calibrated probabilistic forecast, the newsvendor quantile $q^\*=p/(p+c)$ is cost-optimal in expectation; conformal prediction can wrap any forecaster to give finite-sample coverage $1-\beta$, bounding under-provisioning probability without distributional assumptions.

## 5. Lower Bound
Online provisioning faces a competitive-ratio floor: convex body chasing in $n$ dimensions has an $\Omega(\sqrt{n})$ lower bound (Friedman & Linial; Bubeck et al.), so no online algorithm matches the offline optimum without lookahead. Without bounded-error forecasts, *any* lookahead-free policy can be forced into either unbounded SLA violation or unbounded waste by an adversarial demand sequence (info-theoretic). Multi-resource provisioning with discrete instance types is a bin-packing/integer-program generalization and is NP-hard.

## 6. The Gap
Theory gives clean competitive ratios for $1$-D smoothed provisioning, but real systems are *multi-resource, lead-time-coupled, and forecast-driven with miscalibrated intervals*. The empirical gap: end-to-end SLA-violation vs. cost is dominated by **forecast-interval calibration and warm-up latency modeling**, not by the controller's competitive ratio. There is no tight bound combining forecast error, lead time $L$, and switching cost into a single provisioning-regret guarantee. Status is empirically-open: methods work well on traces but lack worst-case + average-case guarantees jointly.

## 7. Current Research (as of June 2026)
- Conformal / calibrated probabilistic forecasting feeding newsvendor-style provisioning with coverage guarantees *(frontier — verify)*.
- Serverless DB autoscaling (Aurora Serverless v2, Neon, cloud Spanner) tightening predictive scale-up to cut cold-start *(frontier — verify)*.
- Learning-augmented online algorithms: provisioning with untrusted ML predictions retaining worst-case competitiveness (consistency/robustness trade-off).
- Groups: CMU NoisePage line (Pavlo, Ma), Microsoft Research (Gemini/database autoscaling), and the learning-augmented-algorithms community (Mitzenmacher, Vassilvitskii, Lykouris).

## 8. Future Work
- Unified regret bounds folding forecast error, lead time, and switching cost.
- Multi-resource, multi-tenant provisioning with fairness and burst SLAs.
- Tight integration of cache/replica warm-up dynamics into the provisioning model.
- Online recalibration of forecast intervals under workload drift.

## 9. Key References
- **[Foundational]** M. Lin, A. Wierman, L. Andrew, E. Thereska. *Dynamic Right-Sizing for Power-Proportional Data Centers.* IEEE/ACM Transactions on Networking, 2013.
- **[SOTA]** L. Ma, D. Van Aken, A. Hefny, G. Mealy, A. Pavlo, et al. *Query-based Workload Forecasting for Self-Driving Database Management Systems.* SIGMOD, 2018.
- **[SOTA]** M. Sellke. *Chasing Nested Convex Bodies Nearly Optimally.* SODA, 2020.
- **[SOTA]** D. Salinas, V. Flunkert, J. Gasthaus. *DeepAR: Probabilistic Forecasting with Autoregressive Recurrent Networks.* International Journal of Forecasting, 2020.
- **[Survey]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
