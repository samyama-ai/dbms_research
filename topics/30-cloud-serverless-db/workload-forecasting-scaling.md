# Workload-forecasting for scale-to-zero

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/workload-forecasting-scaling` · **Status:** empirically-open

## 1. Problem Statement
A serverless database (e.g., Aurora Serverless v2, Neon, Cosmos DB serverless) can **scale to zero** — fully pausing compute during idle periods to stop billing — and resume on the next request. Pausing is profitable only if idle intervals are long enough to amortize the **cold-start cost** of resume; resuming late forces the first request to wait, violating a tail-latency SLO. The problem: **forecast idle and burst intervals accurately enough that the pause/resume policy maximizes cost savings subject to a bound on SLO violations.**

- **Decision variant:** Given a forecast and a cold-start cost $c$, decide at each idle moment whether to pause, such that the fraction of requests hitting a cold start with latency $> \ell$ stays $\le \epsilon$.
- **Optimization (online) variant:** Minimize total cost = idle compute paid + (penalty $\times$ cold-start delays), with no knowledge of future arrivals — this is exactly the **ski-rental / rent-or-buy** problem.
- **Counting variant:** Estimate the distribution of inter-arrival gaps to set the pause threshold.

## 2. Mathematical Foundations
The core is the **ski-rental problem**: keeping a paused-able resource warm costs $1$ per time unit; resuming (the "buy") costs $B$ (the cold-start penalty). The classic deterministic break-even strategy — pay-as-you-go until accumulated idle cost equals $B$, then pause — is **2-competitive**, and the randomized strategy achieves competitive ratio $\frac{e}{e-1}\approx 1.58$, both optimal in the online (no-forecast) model.

Forecasting tightens this beyond worst case. With a predictor giving idle-gap length $\hat{g}$ vs. true $g$, **learning-augmented (algorithms-with-predictions)** ski-rental achieves competitive ratio $\min\!\big(1+\eta,\ \tfrac{e}{e-1}\big)$-style bounds that interpolate between $1$ (perfect prediction, *consistency*) and the worst-case $\frac{e}{e-1}$ (*robustness*), where $\eta$ is prediction error. This is the Purohit–Svirschoo–Kumar (NeurIPS 2018) framework.

Tail-SLO control adds a constraint: if request arrivals are modeled as a (possibly non-stationary) point process with intensity $\lambda(t)$, the probability the next arrival lands within cold-start window after a pause is $1-e^{-\int \lambda}$. Forecast quality is measured by the predictability of $\lambda(t)$; VC/Rademacher or time-series-generalization bounds govern how much history is needed to estimate burst onsets.

$$
\min_{\text{policy}}\ \mathbb{E}\Big[\underbrace{\textstyle\int \mathbb{1}[\text{warm}]\,dt}_{\text{idle cost}} + B\cdot N_{\text{cold}}\Big]\quad \text{s.t.}\quad \Pr[\text{first-req latency} > \ell] \le \epsilon .
$$

## 3. State of the Art (SOTA)
**Systems-SOTA.** **Aurora Serverless v2** scales ACUs continuously and can pause; **Neon** scale-to-zero (Postgres compute suspends, storage persists) with sub-second-to-few-second resume is the cleanest public scale-to-zero DB. **Azure Cosmos DB serverless** and **PlanetScale**/Vitess autoscaling. FaaS-side: **AWS Lambda SnapStart** and Firecracker snapshotting cut cold starts via memory-image restore — directly applicable to DB resume.

**Theory-SOTA.** Ski-rental and its learning-augmented variants (Purohit et al. 2018; Lykouris–Vassilvitskii on caching-with-predictions, ICML 2018) are the governing theory. Workload forecasting uses standard time-series/ML (ARIMA, Prophet, LSTMs, and now transformers for arrival-rate prediction).

## 4. Upper Bound
Online, no prediction: **$\frac{e}{e-1}\approx 1.58$-competitive** (randomized ski-rental), or 2-competitive deterministic. With predictions of error $\eta$: consistency $\to 1$ as $\eta\to 0$ while retaining robustness $\le \frac{e}{e-1}$. These are the best provable cost guarantees and they *are* achieved by threshold policies.

## 5. Lower Bound
Ski-rental's competitive ratio is **tight**: no randomized online algorithm beats $\frac{e}{e-1}$, and no deterministic one beats $2$ — an unconditional online lower bound. For forecasting itself, the limit is **statistical/information-theoretic**: bursty, heavy-tailed, or adversarially-timed arrivals are *unpredictable* in principle (no estimator generalizes when the arrival process has unbounded change), so the tail-SLO constraint cannot be met for arbitrary workloads — only for those with bounded predictability. There is no closed-form characterization of which real DB workloads are "predictable enough," which is why the problem is **empirically open**.

## 6. The Gap
The *online cost* side is closed (tight competitive ratios). The genuinely open, **empirical** gap is: real workloads are neither worst-case adversarial nor cleanly stationary, so the achievable consistency depends on how predictable production traffic actually is — and we lack both (a) a benchmark characterization of DB-workload predictability and (b) provable joint guarantees on cost *and* tail-SLO under realistic non-stationary arrivals. Closing it needs empirical predictability studies plus learning-augmented policies that respect a hard SLO constraint (most theory bounds expected cost, not tail violations).

## 7. Current Research (as of June 2026)
- Snapshot-based fast resume (Firecracker/SnapStart-style memory images) to shrink $B$ so pausing pays off for shorter idle gaps. *(frontier — verify)*
- Transformer/foundation-model time-series forecasters applied to per-tenant DB arrival rates. *(frontier — verify)*
- Learning-augmented autoscaling with SLO-as-constraint (not penalty), an active algorithms-with-predictions direction.
- Groups: Neon and Aurora Serverless teams; algorithms-with-predictions community (Vassilvitskii, Mitzenmacher, Indyk-adjacent); systems-for-ML autoscaling at Berkeley Sky.

## 8. Future Work
- Predictability benchmarks for real serverless-DB traces.
- Online policies with hard tail-latency guarantees, not just expected cost.
- Co-optimizing forecast horizon, snapshot cost, and multi-tenant resume contention.

## 9. Key References
- **[Foundational]** Karlin, A., Manasse, M., McGeoch, L., Owicki, S. *Competitive Randomized Algorithms for Nonuniform Problems (ski-rental).* Algorithmica, 1994.
- **[SOTA]** Purohit, M., Svitkina, Z., Kumar, R. *Improving Online Algorithms via ML Predictions.* NeurIPS, 2018.
- **[SOTA]** Lykouris, T., Vassilvitskii, S. *Competitive Caching with Machine Learned Advice.* ICML, 2018.
- **[Systems]** Agache, A. et al. *Firecracker: Lightweight Virtualization for Serverless Applications.* NSDI, 2020.
- **[Survey]** Mitzenmacher, M., Vassilvitskii, S. *Algorithms with Predictions.* CACM / Beyond the Worst-Case Analysis of Algorithms, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
