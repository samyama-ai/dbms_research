# Energy- and carbon-aware cloud query scheduling

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/carbon-aware-scheduling` · **Status:** empirically-open

## 1. Problem Statement
Elastic database work (analytic queries, ETL, index/compaction maintenance, model training over data) can often be **shifted in time and space**: deferred to greener hours, migrated to regions with lower-carbon electricity, or run at lower power. **Carbon-/energy-aware scheduling** decides *when, where, and at what power level* to execute each unit of work to minimize energy cost or operational **carbon emissions** while honoring per-query/per-tenant latency SLOs and data-residency constraints.

Variants:
- **Decision:** does a feasible schedule exist meeting all deadlines + residency under a carbon budget?
- **Optimization (offline):** minimize total $\sum_t \text{power}(t)\cdot \text{CI}_{r}(t)$ (carbon intensity by region $r$, time $t$) subject to deadlines, residency, capacity.
- **Online:** carbon intensity and arrivals revealed over time; schedule without the future.
- **Stochastic:** CI and demand are forecasts with error.

Difficulty: carbon intensity is **time- and region-varying and uncertain**, data has **gravity** (egress cost, residency law), and SLOs forbid arbitrary deferral; the objective couples scheduling, placement, and DVFS/power scaling.

## 2. Mathematical Foundations
Let jobs $j$ have work $w_j$, release $r_j$, deadline $d_j$, region-allowable set $\mathcal{R}_j$. A schedule assigns each job a region $r$, start time, and speed $s$ (machines run at speed $s$ with power $P(s)=\beta + \alpha s^{\kappa}$, the standard **convex speed–power** law, $\kappa\approx 2$–$3$). Carbon cost:
$$\min \sum_{j}\int \text{CI}_{r(j)}(t)\, P(s_j(t))\, dt \quad \text{s.t. completion}(j)\le d_j,\ r(j)\in\mathcal{R}_j.$$

Without deadlines/regions this is **speed scaling for energy** (Yao–Demers–Shenker), solvable optimally offline in poly time; adding deadlines + discrete regions makes it a **generalized assignment / scheduling-with-eligibility** problem, NP-hard. Spatial migration adds an **uncapacitated-facility / transportation** structure (data-egress = transport cost). The online version with revealed CI is an **online convex/scheduling** problem analyzed by **competitive ratio**; deadline-feasible online speed scaling has the classic **AVR / Optimal Available** algorithms with competitive ratio $\le \kappa^\kappa$ (and BKP $\le 2(\kappa/(\kappa-1))^\kappa e^\kappa$). Carbon-as-a-time-varying-price generalizes energy to a **price-weighted** objective, linking to **one-way trading / online search** lower bounds when deferring under uncertain future price.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Google's **carbon-intelligent computing** (temporal demand shifting of flexible compute) and follow-ups adding **spatial** shifting; Microsoft's carbon-aware Windows/Azure scheduling and the **Carbon Aware SDK**; academic schedulers **Wait Awhile** (Wiesner et al.), **CarbonScaler / GAIA / Ecovisor**, and carbon-aware Spark/SQL batch placement. WattTime / ElectricityMaps marginal-CI signals are the standard input. Database-specific: carbon-aware compaction/ETL deferral *(frontier — verify)*.
- **Theory-SOTA:** Yao–Demers–Shenker speed scaling; Albers's surveys on energy-efficient scheduling; competitive online speed-scaling (BKP). One-way-trading bounds (El-Yaniv et al.) for deferral under uncertain price.

## 4. Upper Bound
- **Offline energy-optimal** speed scaling (single resource, deadlines, one region): poly-time optimal (YDS).
- **Online deadline speed scaling:** competitive ratio $\le \alpha^\alpha$ (Optimal Available) and improved BKP bounds for power $P(s)=s^\alpha$.
- **Carbon-aware deferral** modeled as online search/one-way trading admits a $\Theta(\log(\Phi))$-competitive (or $\sqrt{\Phi}$ for threshold) algorithm where $\Phi$ = max/min carbon-intensity ratio; with accurate forecasts (learning-augmented) this improves toward $1+\epsilon$.
- **Spatial+temporal** with regions: constant-factor approximations via LP-rounding for the offline generalized-assignment relaxation under capacity slack.

## 5. Lower Bound
- Deadline-constrained scheduling with **machine/region eligibility** is **NP-hard** (reduction from 3-partition / generalized assignment), so optimal carbon scheduling is NP-hard.
- **Online deferral lower bound:** with carbon-intensity range ratio $\Phi$ and no forecast, any online algorithm is $\Omega(\log \Phi)$-competitive (one-way-trading lower bound); thresholding cannot beat $\sqrt{\Phi}$ deterministically.
- Speed-scaling online has matching $\Omega(\alpha^\alpha)$-type lower bounds for the energy objective.
- Information-theoretic: with forecast error $\delta$, no scheduler can guarantee carbon within $o(\delta)$ of optimal — error propagates linearly.

## 6. The Gap
Theory cleanly bounds the *stylized* pieces (energy speed-scaling, one-way trading) but the **integrated** database problem — time + region + DVFS + data-gravity + tail-latency SLOs + forecast uncertainty — has **no algorithm with end-to-end provable carbon-competitive guarantees**. Empirically, schedulers report 10–40% carbon savings, but results are workload/region/signal-dependent and lack worst-case bounds or agreed benchmarks; marginal-vs-average CI accounting is contested. Hence **empirically-open**: practical wins are real, but the optimization is not characterized and the measurement methodology is unsettled.

## 7. Current Research (as of June 2026)
- **Learning-augmented carbon scheduling**: forecast-driven deferral with robustness fallback (consistency/robustness trade-off) *(frontier — verify)*.
- **Spatiotemporal shifting for stateful DB work** accounting for data egress/residency (groups at UMass, MIT, Microsoft Research, Google).
- **Carbon-aware autoscaling/compaction** in LSM and lakehouse engines.
- Standardization of **marginal carbon accounting** and reproducible carbon benchmarks; debate on average vs. consequential/marginal CI.
- Joint **carbon + cost + SLO** Pareto schedulers; embodied vs. operational carbon trade-offs.

## 8. Future Work
- A unified model with provable carbon-competitive bounds under forecast error and SLO constraints.
- Truthful carbon-cost attribution across tenants (links to verifiable billing).
- Handling **embodied carbon** (hardware manufacturing) alongside operational.
- Carbon-aware *transaction* (not just batch) scheduling without violating latency.

## 9. Key References
- **[Foundational]** Frances Yao, Alan Demers, Scott Shenker. *A Scheduling Model for Reduced CPU Energy.* FOCS, 1995.
- **[Foundational]** Nikhil Bansal, Tracy Kimbrel, Kirk Pruhs. *Speed Scaling to Manage Energy and Temperature.* JACM, 2007.
- **[SOTA]** Ana Radovanović, et al. *Carbon-Aware Computing for Datacenters.* IEEE Transactions on Power Systems, 2023 (Google carbon-intelligent computing).
- **[SOTA]** Philipp Wiesner, et al. *Let's Wait Awhile: How Temporal Workload Shifting Can Reduce Carbon Emissions in the Cloud.* Middleware, 2021.
- **[SOTA]** Walid Hanafy, et al. *CarbonScaler: Leveraging Cloud Workload Elasticity for Optimizing Carbon-Efficiency.* SIGMETRICS, 2024.
- **[Survey]** Susanne Albers. *Energy-Efficient Algorithms.* Communications of the ACM, 2010.

---
*Part of the [DBMS Research catalog](../../README.md).*
