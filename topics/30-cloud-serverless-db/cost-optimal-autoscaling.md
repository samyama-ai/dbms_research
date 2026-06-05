# Cost-optimal autoscaling policies

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/cost-optimal-autoscaling` · **Status:** empirically-open
> **Verification note:** The Christianson–Shen–Wierman robustness–consistency result appeared at AISTATS 2023 (the §9 year is corrected from 2022); its specific setting is learning-augmented metrical task systems.

## 1. Problem Statement

A serverless or elastic database must decide, online, how much compute to provision over time as load varies. Over-provisioning wastes money; under-provisioning violates the latency/throughput SLO. The **cost-optimal autoscaling problem**: design an online policy that, observing load only up to the present, chooses resource levels to **minimize total dollar cost** (compute-seconds + scaling overhead + SLO-violation penalty) while keeping SLO violations within budget — and prove a competitive ratio against the offline optimum.

Variants: (a) **decision/feasibility** — is there a schedule meeting the SLO at cost $\le B$? (b) **online optimization** — minimize cost with no future knowledge; (c) **learning-augmented** — given an (untrusted) load forecast, be near-optimal if it is accurate and bounded-bad if it is wrong.

## 2. Mathematical Foundations

This is **online convex optimization with switching costs**, a.k.a. *Smoothed Online Convex Optimization (SOCO)* / *Convex Body Chasing*. At each time $t$, a hitting cost $f_t(x_t)$ (under-provisioning penalty + per-unit price) and a switching cost $\gamma\,\lVert x_t - x_{t-1}\rVert$ (spin-up/spin-down latency monetized) are incurred. The objective is
$$\min_{\{x_t\}} \sum_t \big[ f_t(x_t) + \gamma\lVert x_t - x_{t-1}\rVert \big].$$
For one-dimensional convex hitting costs, the optimal online algorithm (Bansal et al.) achieves a competitive ratio of **2**; with switching costs the lower bound is also $2$ in 1-D. In $d$ dimensions this becomes nested convex body chasing, with competitive ratio $O(\sqrt{d})$ (Sellke / Argue et al.). Learning-augmented versions give **consistency** (near-1 with a good forecast) and **robustness** (bounded ratio with a bad one).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Aurora Serverless v2 scales *Aurora Capacity Units* sub-second via fine-grained vertical scaling; Snowflake multi-cluster warehouses auto-suspend/resume; Kubernetes HPA/VPA and KEDA drive container-level autoscaling; BigQuery/Redshift Serverless allocate "slots"/RPUs on demand. Most use reactive threshold (utilization-based) controllers plus predictive heuristics.
- **Theory-SOTA:** SOCO with switching costs and convex-body-chasing results provide the rigorous backbone; learning-augmented online scaling (e.g., Christianson, Wierman et al.) gives consistency/robustness trade-off bounds.

## 4. Upper Bound

For 1-D convex hitting + switching cost, an online algorithm is **2-competitive** (optimal). For $d$-dimensional convex body chasing, competitive ratio $O(\sqrt d)$ (and $O(d)$ for general/nested bodies via simpler algorithms). Learning-augmented policies achieve $(1+\epsilon)$-consistency with $O(1/\epsilon)$-robustness, interpolating by a trust parameter. Regret-minimizing (OCO) controllers achieve $O(\sqrt T)$ regret against the best fixed allocation.

## 5. Lower Bound

The 1-D SOCO-with-switching lower bound is **2**, matching the upper bound. For convex body chasing in $d$ dimensions, $\Omega(\sqrt d)$ is a known lower bound. No online policy can be 1-competitive once switching costs are positive and the future is adversarial. For learning-augmented scaling, there is a hard **consistency–robustness trade-off**: improving worst-case robustness necessarily degrades best-case consistency (Pareto lower bound).

## 6. The Gap

In clean 1-D and convex-chasing models the gap is essentially *closed*. The status is **empirically-open** because the *real* problem deviates from the model: discrete/lumpy resource units, non-convex SLO (tail-latency) penalties, multi-resource (CPU+memory+IO) coupling, cold-start switching that is *latency* not just cost, and non-stationary load. No deployed policy is known to be provably cost-optimal under these realistic features; benchmarks, not theorems, currently arbitrate.

## 7. Current Research (as of June 2026)

Active: learning-augmented online algorithms (Wierman/Caltech, Lee/USC), RL-based autoscalers, and forecast-driven predictive scaling. Cloud labs (AWS, Google, Snowflake, Databricks) publish empirical autoscaler studies. *(frontier — verify)* 2025–2026 work couples LLM/transformer load forecasters with competitive-ratio-bounded controllers, aiming for both empirical accuracy and worst-case guarantees; claims of provable dollar-optimality under tail-latency SLOs remain unverified.

## 8. Future Work

- Online policies with provable bounds under **tail-latency** (non-convex) SLOs.
- Multi-resource (CPU/memory/IO/connections) joint scaling with switching-cost coupling.
- Integrating cold-start latency (not just cost) into the switching term.
- Robust learning-augmented scaling with distribution-shift guarantees.

## 9. Key References

- **[Foundational]** Lin, Wierman, Andrew, Thereska. *Dynamic Right-Sizing for Power-Proportional Data Centers.* IEEE/ACM ToN, 2013. — [DOI](https://doi.org/10.1109/TNET.2012.2226216)
- **[Foundational]** Bansal, Gupta, et al. *A 2-competitive algorithm for online convex optimization with switching costs.* APPROX, 2015. — [DOI](https://doi.org/10.4230/LIPIcs.APPROX-RANDOM.2015.96)
- **[SOTA]** Sellke. *Chasing Convex Bodies Optimally.* SODA, 2020. — [arXiv](https://arxiv.org/abs/1905.11968)
- **[SOTA]** Christianson, Shen, Wierman. *Optimal Robustness-Consistency Trade-offs for Learning-Augmented Metrical Task Systems.* AISTATS, 2023. — [PMLR](https://proceedings.mlr.press/v206/christianson23a.html)
- **[Survey]** Lorido-Botran, Miguel-Alonso, Lozano. *A Review of Auto-scaling Techniques for Elastic Applications in Cloud Environments.* J. Grid Computing, 2014. — [DOI](https://doi.org/10.1007/s10723-014-9314-7)

## 10. Worked Example

Consider $1$-D autoscaling over $4$ time steps. The resource level $x_t$ is the number of warehouse units; load implies a target level $\hat{x}_t = [2, 6, 2, 6]$. Hitting cost is $f_t(x) = (x - \hat{x}_t)^2$ (under/over-provisioning penalty); switching cost is $\gamma|x_t - x_{t-1}|$ with $\gamma = 3$, $x_0 = 2$.

**Reactive (chase the target exactly):** $x = [2,6,2,6]$. Hitting cost $=0$; switching cost $= 3(|6-2|+|2-6|+|6-2|) = 3\cdot 12 = 36$. Total $= 36$.

**Smoothed (stay flat at $x=4$):** $x = [4,4,4,4]$. Hitting cost $= (4-2)^2+(4-6)^2+(4-2)^2+(4-6)^2 = 4\cdot 4 = 16$; switching $= 3\cdot|4-2| = 6$. Total $= 22$.

The smoothed policy wins because the load oscillates faster than the switching cost can profitably track — exactly the SOCO-with-switching trade-off. The Bansal et al. online algorithm interpolates toward the move that balances marginal hitting against marginal switching cost and is provably **2-competitive** against the offline optimum in $1$-D; here it lands near the flat plan rather than the costly chase. A learning-augmented variant would chase only when a trusted forecast says the spike persists.

---
*Part of the [DBMS Research catalog](../../README.md).*
