---
id: 30-cloud-serverless-db/slo-admission-control
title: "SLO-aware admission control under bursts"
topic: 30-cloud-serverless-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# SLO-aware admission control under bursts

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/slo-admission-control` · **Status:** empirically-open
> **Verification note:** The "$\approx 3.3$"-competitive figure in §10 should be read as an order-of-magnitude $O(\log R)$ bound (the standard online-knapsack ratio is $\ln R + 1$, $\approx 3.3$ for $R=10$); the constant is model-dependent, not exact.

## 1. Problem Statement
A multi-tenant cloud query service provisions a fixed (or slowly elastic) pool of compute. When aggregate demand transiently exceeds capacity, the system must decide, *online and per query*, whether to **admit, queue, defer, or shed** work so that per-tenant **tail-latency SLOs** (e.g., p99 < 200 ms) are protected for the queries it does admit, while maximizing goodput / revenue and honoring fairness across tenants.

Variants:
- **Decision:** given current backlog and a new arrival with class/SLO $s$, does admitting it keep all active SLOs feasible?
- **Optimization (online):** maximize admitted value (weighted goodput) subject to each admitted query meeting its deadline/percentile, deciding without future knowledge.
- **Stochastic:** demand is a random process (often bursty/heavy-tailed); minimize expected SLO-violation probability or violation cost.

The defining difficulty is **burstiness + tail metrics + elasticity lag**: percentile SLOs are non-additive and sensitive to queueing in the tail, autoscaling has cold-start latency, and admission errors are only observable after the fact.

## 2. Mathematical Foundations
Model the service as a multi-class queueing system. Arrivals of class $i$ form a process with rate $\lambda_i$ (often **Markov-modulated** or self-similar to capture bursts); service demands $S_i$ are general (G), so the system is a $\sum_i M^X/G/c$ or $G/G/c$ network with **deadline/percentile constraints**. The relevant quantities:

$$P(\text{response time } W_i > \text{SLO}_i) \le \epsilon_i.$$

Because tail constraints are not captured by mean-value (Little's law $L=\lambda W$ gives means only), one uses **large-deviations / effective-bandwidth** theory: a class admitted with effective bandwidth $\alpha_i(\theta)$ keeps overflow probability $\approx e^{-\theta B}$ for buffer $B$. Admission becomes a **knapsack-like packing** in effective-bandwidth space:
$$\sum_{i \in \text{admitted}} \alpha_i(\theta^*) \le C.$$

The online structure is a **competitive-ratio** problem: admission control with deadlines generalizes online interval scheduling / the $k$-server and online knapsack families. Worst-case adversarial arrivals make pure online optimal impossible (see §5), motivating stochastic/learning models (MDP with state = backlog + arrival phase; objective = discounted SLO-violation cost; solvable in principle by dynamic programming but state space explodes).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** production schedulers use class-based **weighted fair queueing + token-bucket admission + load shedding** (e.g., Google's prioritized RPC load shedding / adaptive overload control, Amazon Aurora/Redshift WLM queues, Microsoft Azure SQL DB resource governance). Cloud query engines add **autoscaling with predictive warm pools**. Reinforcement-learning and model-based controllers (e.g., learned admission in Snowflake/Databricks-style warehouses) are emerging *(frontier — verify)*.
- **Theory-SOTA:** effective-bandwidth admission control (Kelly), online knapsack/secretary bounds, and the $\Theta(\log(\text{value ratio}))$-competitive online-admission results for deadline scheduling.
- **Overload control:** Welsh–Culler SEDA-style adaptive admission and Google's *Overload Control* (Breakwater, CC) give practical tail protection under bursts.

## 4. Upper Bound
- For **online admission to maximize value under deadlines**, no constant-competitive deterministic algorithm exists for unbounded value ratios; with value-to-size ratio in $[1,R]$, online knapsack admits an $O(\log R)$-competitive algorithm, and threshold policies are $(1-1/e)$-competitive under random-order/stochastic input (secretary/prophet models).
- Under **effective-bandwidth** admission, a simple sum-test is *provably safe* (keeps overflow $\le e^{-\theta B}$) and within a constant factor of optimal admittable load for many traffic classes.
- For tail-SLO with $G/G/c$, **heavy-traffic** diffusion approximations give policies (generalized $c\mu$ / $c\mu/\theta$ rule) that are **asymptotically optimal** for minimizing weighted tail cost.

## 5. Lower Bound
- Online admission with arbitrary values/deadlines has an **$\Omega(\log R)$** (and unbounded for unrestricted values) competitive lower bound — adversary forces any deterministic policy far from optimal (online knapsack hardness).
- Meeting *strict percentile* SLOs under adversarial heavy-tailed bursts is **impossible in the worst case** without overprovisioning: a large-deviations argument shows required headroom grows with burst variability; with bounded capacity and unbounded burst, some violation is unavoidable (an availability/consistency-style tension).
- The exact MDP is **PSPACE-hard** to solve optimally in general queueing-network admission formulations.

## 6. The Gap
Theory gives tight bounds only in stylized regimes (single bottleneck, known traffic class, mean or asymptotic tail). Real systems face **correlated multi-resource bursts, percentile (not mean) SLOs, autoscaling lag, and unknown/non-stationary traffic** — for which there is *no* policy with proven competitive guarantees on p99 latency. The status is **empirically-open**: practical RL/heuristic controllers beat baselines on benchmarks but lack worst-case or even distribution-free tail guarantees. Closing it requires either (a) provable tail-SLO competitive bounds under realistic burst models, or (b) impossibility results delimiting what headroom buys.

## 7. Current Research (as of June 2026)
- **Learning-augmented (ML-advice) admission**: combine an RL/forecast predictor with a worst-case-safe fallback to get *consistency + robustness* bounds for tail-SLO admission *(frontier — verify)*.
- **Predictive autoscaling + admission co-design** to hide cold starts (work at Berkeley, MIT, Microsoft Research, Google).
- **Tail-aware overload control** (Breakwater/CC successors) extended to stateful database workloads.
- SLO-aware **serverless function admission** and credit/burst-bucket accounting in DBaaS.

## 8. Future Work
- Distribution-free or PAC-style tail-latency guarantees for online admission.
- Joint admission + elastic-scaling + carbon-aware deferral (links to carbon-aware scheduling).
- Truthful admission under tenants that strategically classify their queries.
- Benchmarks with realistic, reproducible burst traces for percentile-SLO evaluation.

## 9. Key References
- **[Foundational]** Frank P. Kelly. *Effective Bandwidths at Multi-Class Queues.* Queueing Systems, 1991. — [DOI](https://doi.org/10.1007/BF01158789)
- **[Foundational]** Matthew Welsh, David Culler, Eric Brewer. *SEDA: An Architecture for Well-Conditioned, Scalable Internet Services.* SOSP, 2001. — [DOI](https://doi.org/10.1145/502034.502057)
- **[SOTA]** Inho Cho, Ahmed Saeed, et al. *Overload Control for µs-scale RPCs with Breakwater.* OSDI, 2020. — [DBLP](https://dblp.org/rec/conf/osdi/ChoSFPAB20.html)
- **[Foundational]** Niv Buchbinder, Joseph (Seffi) Naor. *Online Primal-Dual Algorithms for Covering and Packing.* (online knapsack/admission). ESA, 2005 / Math. OR. — [DOI](https://doi.org/10.1007/11561071_61)
- **[Survey]** Mor Harchol-Balter. *Performance Modeling and Design of Computer Systems: Queueing Theory in Action.* Cambridge Univ. Press, 2013. — [DBLP search](https://dblp.org/search?q=Performance+Modeling+and+Design+of+Computer+Systems+Harchol-Balter)
- **[SOTA]** Thodoris Lykouris, Sergei Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML/JACM, 2018/2021 (learning-augmented framework). — [DOI](https://doi.org/10.1145/3447579), [arXiv](https://arxiv.org/abs/1802.05399)

## 10. Worked Example

A warehouse has capacity $C = 100$ "service units." Two tenant classes arrive: class A (interactive, SLO p99 $<200$ ms, effective bandwidth $\alpha_A = 4$ units each) and class B (batch, lax SLO, $\alpha_B = 1$ unit each). The effective-bandwidth admission test admits a set iff

$$\sum_{i\in\text{admitted}} \alpha_i(\theta^\*) \le C.$$

Suppose $20$ class-A and $30$ class-B queries are active: load $=20\times4 + 30\times1 = 110 > 100$ — **infeasible**, the system is overloaded and some p99 SLO will be violated. A new class-A arrival must be **shed or deferred**: admitting it would push load to $114$.

Now apply the **online-knapsack** view: with value-to-size ratios in $[1, R]$ and here $R = 10$ (A is worth 10x B per unit but costs 4 units), the best deterministic online policy is $O(\log R) = O(\log 10) \approx 3.3$-competitive — i.e., worst-case adversarial arrivals can force any online admitter to capture only $\sim 1/3.3$ of the optimal value. A threshold policy admits class A whenever its marginal value density $v/\alpha = 10/4 = 2.5$ exceeds a price threshold $\psi(\text{utilization})$ that rises as load $\to C$; at $110\%$ load $\psi$ exceeds $2.5$, so even class A is rejected — matching the shed decision above. This quantifies why bounded capacity plus bursty load forces unavoidable violation (§5).

---
*Part of the [DBMS Research catalog](../../README.md).*
