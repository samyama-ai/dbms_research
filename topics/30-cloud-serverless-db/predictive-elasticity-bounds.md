---
id: 30-cloud-serverless-db/predictive-elasticity-bounds
title: "Predictive vs. reactive elasticity bounds"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Predictive vs. reactive elasticity bounds

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/predictive-elasticity-bounds` · **Status:** open

## 1. Problem Statement

An elastic database service scales a resource (nodes, function concurrency, warehouse size) up/down to track a time-varying load $\lambda(t)$. **Reactive** scaling responds only to observed signals (queue length, utilization) *after* load changes; **predictive** scaling acts on a forecast $\hat\lambda(t+\delta)$ to provision *ahead* of demand. Because provisioning has **lag** (cold starts, node boot, rebalancing) and **cost** (over-provisioning wastes money; under-provisioning causes SLO violations / latency spikes), the question is the **competitive-ratio gap**: how much better, in the worst case and in expectation, can a predictive policy do than the best reactive policy — *especially for bursty, heavy-tailed workloads* where bursts are large and forecasts are hard.

Variants:
- **Decision:** given a forecast oracle of accuracy $\eta$ and provisioning lag $L$, is competitive ratio $\le \rho$ achievable?
- **Optimization:** minimize total cost = (resource-seconds) + (penalty $\times$ SLO violations) over a horizon, online.
- **Counting/structural:** characterize the *value of prediction* — the ratio between optimal-with-forecast and optimal-reactive — as a function of burstiness and forecast error.

## 2. Mathematical Foundations

This is an **online optimization with switching costs** problem. The canonical model is **convex body chasing / smoothed online convex optimization (SOCO)**: at each step pay a *service* cost (under/over-provision penalty, convex in the gap) plus a *switching* cost (scaling/migration). The capacity-tracking special case is the **ski-rental / rent-or-buy** and **dynamic right-sizing** problem (Lin–Wierman–Andrew–Thereska), where deterministic $3$-competitive and randomized $2$-competitive online algorithms are known for $1$-D, and **AFHC/RHC (receding-horizon control)** quantifies how *lookahead* (prediction window $w$) shrinks the ratio toward $1$.

Predictive policies are analyzed via **online algorithms with (machine-learned / untrusted) predictions**: a policy is **$\alpha$-consistent** (ratio $\alpha$ when predictions are perfect) and **$\beta$-robust** (ratio $\le\beta$ regardless), with a provable **consistency–robustness tradeoff frontier** (Lykouris–Vassilvitskii; Purohit–Svitkina–Kumar). Burstiness is modeled with **heavy-tailed** arrivals (Pareto/regularly-varying tails, possibly self-similar / long-range-dependent traffic), where the tail index controls how unbounded a single burst can be and thus the achievable worst-case ratio.

## 3. State of the Art (SOTA)

**Theory-SOTA.** Dynamic right-sizing: Lin et al. (INFOCOM 2011 / IEEE-ACM ToN) give a $3$-competitive deterministic and $2$-competitive randomized algorithm for energy-proportional capacity. With lookahead $w$, **AFHC** (Averaging Fixed Horizon Control, Lin–Liu–Wierman) gives competitive ratio $\to 1$ as $w$ grows relative to switching cost. The **learning-augmented** line (Purohit et al., NeurIPS 2018; Lykouris–Vassilvitskii, JACM 2021) gives the consistency/robustness frontier directly applicable to predictive autoscaling. Convex-body-chasing breakthroughs (Bubeck et al.; Argue–Gupta–Guruganesh) give $O(\sqrt{d})$-competitive nested CBC, bounding multi-resource scaling.

**Systems-SOTA.** Predictive autoscalers: **AWS Predictive Scaling** and **Autopilot** (Rzadca et al., EuroSys 2020 — Google's vertical/horizontal autoscaler using historical load), Microsoft **Resource Central** (SOSP 2017 — VM workload prediction), and serverless cold-start mitigation via provisioned concurrency / pre-warming. Snowflake/Redshift Serverless and BigQuery auto-scale slots reactively with some predictive elements.

## 4. Upper Bound

For $1$-D dynamic right-sizing the upper bound is competitive ratio **2 (randomized) / 3 (deterministic)** with *no* prediction (Lin–Wierman et al.), in the online-with-switching-cost model. With a *trusted* forecast over window $w$, RHC/AFHC drive the ratio toward $1$, with the gap shrinking geometrically in $w$/switching-cost ratio. With an *untrusted* ML forecast of error $\eta$, learning-augmented algorithms achieve consistency $\approx 1+O(\eta)$ while preserving robustness $O(1)$, on the proven consistency–robustness Pareto frontier. For $d$-resource scaling, nested convex body chasing gives $O(\sqrt d)$-competitive. These hold in the SOCO / metrical-task-system model.

## 5. Lower Bound

In the pure-online model, **no deterministic algorithm beats ratio 3** (and no randomized beats $2$) for the canonical $1$-D right-sizing problem — a tight lower bound. For metrical task systems / $k$-server-style abstractions the lower bounds are $\Omega(\text{poly})$ in dimension; convex body chasing has an $\Omega(\sqrt d)$ lower bound, matching the upper bound up to constants. The learning-augmented frontier is provably **tight**: you cannot simultaneously have consistency $<1+c$ and robustness $<$ a paired threshold (any improvement in best-case forces worst-case degradation). For heavy-tailed bursts, an information-theoretic limit applies: if the burst tail is *unbounded* (infinite-variance Pareto), *no* online or predictive policy can bound the worst-case SLO-violation cost without unbounded provisioning — prediction cannot beat fundamental tail unpredictability.

## 6. The Gap

The competitive-ratio gap for the *clean* models (1-D right-sizing, CBC) is essentially **closed** (matching $2$/$3$ and $\Theta(\sqrt d)$). What is genuinely **open** is the *value of prediction under realistic burstiness*: a tight characterization of the predictive-vs-reactive ratio as a joint function of (forecast error $\eta$, provisioning lag $L$, tail index $\alpha$, switching cost). In particular, for heavy-tailed/self-similar DB workloads, there is no tight bound on *how much* a forecast helps before tail unpredictability dominates, nor on the *minimal* forecast accuracy that yields a target competitive ratio. The systems literature reports empirical wins for predictive scaling but lacks worst-case guarantees tied to the workload's tail.

## 7. Current Research (as of June 2026)

Active: **learning-augmented online algorithms** specialized to autoscaling with lag-aware, multi-resource, and *tail-aware* models; **cold-start-aware** predictive provisioning for serverless DBs (keep-warm pools sized by forecast) *(frontier — verify)*; and robust/distributionally-robust scaling against adversarial bursts. Groups/people: Wierman and Andrew and Liu (Caltech — online algorithms for energy/right-sizing), Vassilvitskii and collaborators (learning-augmented algorithms), Gupta and Guruganesh (convex body chasing), and the Google **Autopilot**/Microsoft **Resource Central** systems teams. Frontier claim: *tail-aware learning-augmented autoscalers can give SLO guarantees for moderately heavy-tailed (finite-variance) workloads, but infinite-variance regimes remain provably out of reach* *(frontier — verify)*.

## 8. Future Work

- Tight competitive bounds parameterized jointly by forecast error, provisioning lag, and tail index.
- Tail-aware learning-augmented policies with certified SLO guarantees under regularly-varying load.
- Coupling elasticity bounds with right-sizing of individual workers (see function-right-sizing) and live repartitioning lag (see elastic-oltp-repartition).
- Distributionally-robust autoscaling with finite-sample forecast guarantees.

## 9. Key References

- **[Foundational]** M. Lin, A. Wierman, L. L. H. Andrew, E. Thereska. *Dynamic Right-Sizing for Power-Proportional Data Centers.* INFOCOM 2011 / IEEE-ACM ToN, 2013. — [DOI](https://doi.org/10.1109/TNET.2012.2226216) · [DBLP](https://dblp.org/rec/journals/ton/LinWAT13.html)
- **[SOTA]** M. Lin, Z. Liu, A. Wierman, L. L. H. Andrew. *Online Algorithms for Geographical Load Balancing / Averaging Fixed Horizon Control.* IGCC, 2012. — [DOI](https://doi.org/10.1109/IGCC.2012.6322266) · [DBLP](https://dblp.org/rec/conf/green/LinLWA12.html)
- **[SOTA]** M. Purohit, Z. Svitkina, R. Kumar. *Improving Online Algorithms via ML Predictions.* NeurIPS, 2018. — [NeurIPS](https://proceedings.neurips.cc/paper/2018/hash/73a427badebe0e32caa2e1fc7530b7f3-Abstract.html)
- **[SOTA]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML 2018 / JACM, 2021. — [DOI](https://doi.org/10.1145/3447579) · [arXiv](https://arxiv.org/abs/1802.05399)
- **[SOTA]** C. J. Argue, A. Gupta, G. Guruganesh, Z. Tang. *Chasing Convex Bodies with Linear Competitive Ratio.* SODA, 2020. — [arXiv](https://arxiv.org/abs/1905.11877) · [DBLP](https://dblp.org/rec/journals/jacm/ArgueGTG21.html)
- **[SOTA]** K. Rzadca et al. *Autopilot: Workload Autoscaling at Google.* EuroSys, 2020. — [DOI](https://doi.org/10.1145/3342195.3387524) · [DBLP](https://dblp.org/rec/conf/eurosys/RzadcaFSZBKNSWH20.html)
- **[SOTA]** E. Cortez et al. *Resource Central: Understanding and Predicting Workloads for Improved Resource Management in Large Cloud Platforms.* SOSP, 2017. — [DOI](https://doi.org/10.1145/3132747.3132772) · [DBLP](https://dblp.org/rec/conf/sosp/CortezBMRFB17.html)

## 10. Worked Example

Model right-sizing as ski-rental with switching cost. Keeping one warm DB worker idle costs $1$/min; a cold start (spin up + warm cache) costs a one-time $B = 10$ min-equivalents. Load drops to zero for an unknown gap of $G$ minutes, then returns.

- **Reactive (pure online):** the deterministic break-even rule keeps the worker warm for $B=10$ min, then releases it. Worst case (load returns at $t=10^+$): pay $10$ idle + $10$ cold restart $= 20$, versus the offline optimum of $\min(G, B)$. At $G=10$ the optimum is $10$, giving competitive ratio $20/10 = 2$ here; the canonical bound is $\le 2$ randomized, $\le 3$ deterministic — and no online policy beats these (section 5 lower bound).
- **Predictive:** a forecast says the gap is $G = 3$ min ($< B$). The policy keeps the worker warm through the gap (cost $3$) instead of paying the $10$ restart. If the forecast is right, ratio $= 1$; the learning-augmented guarantee is consistency $\approx 1+O(\eta)$ with robustness still $O(1)$, so even a wrong forecast cannot exceed the $\sim 2$–$3$ reactive bound.

If bursts are infinite-variance Pareto, no finite warm pool bounds worst-case SLO cost — prediction cannot beat tail unpredictability.

---
*Part of the [DBMS Research catalog](../../README.md).*
