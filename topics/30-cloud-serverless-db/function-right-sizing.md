# Right-sizing serverless function memory

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/function-right-sizing` · **Status:** empirically-open

## 1. Problem Statement

Serverless platforms let you pick a single knob per function — a **memory size** $m$ — and CPU/network are allocated *proportionally* to $m$ (AWS Lambda, GCP Functions). Billing is $\text{cost} \propto m \times \text{duration}(m)$. Because more memory means more CPU, the *duration* of a DB operator (scan, hash-join build, sort, aggregation) typically *decreases* with $m$ up to a point, so cost is a non-monotone function of $m$. **Right-sizing** is choosing $m^\*$ (per function, per invocation) to minimize a **cost–latency product** (or cost subject to a latency SLO), for DB operators whose memory/CPU footprint is **data-dependent** — it varies with input size, selectivity, and skew, which are unknown a priori.

Variants:
- **Optimization (per-function):** $\min_m\ \text{cost}(m)\cdot \text{latency}(m)$, or $\min_m \text{cost}(m)$ s.t. $\text{latency}(m)\le \text{SLO}$.
- **Online/data-dependent:** choose $m$ per invocation when the input footprint distribution is learned over a stream of invocations (regret minimization).
- **DAG-level:** jointly size all functions in a query DAG (build/probe/shuffle stages) under an end-to-end SLO.

## 2. Mathematical Foundations

The performance model is a **speedup curve**: $\text{latency}(m)=\text{work}/\min(\,\text{cpu}(m),\,\text{mem-bound}\,) + \text{const}$, where $\text{cpu}(m)\propto m$ until a parallelism/IO ceiling — an **Amdahl's-law**-shaped curve with diminishing returns. Cost $= \kappa\, m\, \text{latency}(m)$ is typically **quasi-convex** in $m$, so a unique cost-minimizer exists and the cost–latency product is amenable to convex/quasi-convex search; but the curve's parameters depend on *data* (footprint $S$, spill behavior once $S>m$ triggers external-memory I/O with cost $\Theta(\frac{S}{B}\log_{M/B}\frac{S}{B})$, Aggarwal–Vitter). Hence right-sizing is **optimization under uncertainty** over a parameterized family.

The online, data-dependent variant is a **bandit / Bayesian-optimization** problem: each invocation is a noisy sample of $f(m)=\text{cost}\times\text{latency}$; minimizing cumulative regret over arms $m$ is a **continuum-armed bandit** with a Lipschitz/unimodal reward, where unimodality yields $\tilde O(\sqrt{T})$ or better regret. DAG-level sizing under an SLO is a constrained nonlinear program; with per-stage convex cost it can be reduced via Lagrangian/critical-path arguments, but data dependence makes parameters latent.

## 3. State of the Art (SOTA)

**Systems-SOTA.** *AWS Lambda Power Tuning* (Casalboni) is the de-facto tool: it sweeps memory settings, measures cost/latency, and reports the Pareto frontier — purely empirical, per-function, offline. Research systems: **COSE** (Akhtar et al., INFOCOM 2020) uses Bayesian optimization to pick memory/config minimizing cost under SLO with few samples; **Sizeless** (Eismann et al., Middleware 2021) *predicts* the optimal memory from a single observed run using ML on resource-consumption metrics; **Aquatope**, **Parrotfish** (adaptive, online parametric regression over the cost curve), and **StepConf** (SLO-aware step configuration for function workflows / DAGs). For serverless **data** systems specifically, Starling/Lambada/Locus (the OLAP-on-functions engines) tune degree-of-parallelism and worker size empirically. Cloud vendors also expose memory recommendations (AWS Compute Optimizer for Lambda).

**Theory-SOTA.** No closed-form optimality result; the relevant theory is unimodal continuum bandits and quasi-convex optimization, plus external-memory spill modeling.

## 4. Upper Bound

For a *known* (or well-estimated) speedup curve, the cost–latency-product minimizer is found in **$O(\log(1/\epsilon))$** evaluations by ternary/golden-section search over the quasi-convex/unimodal $f(m)$ — a clean upper bound when the curve is fixed. Bayesian-optimization methods (COSE) reach near-optimal configs in a *constant, small* number of sampled invocations empirically. For the online data-dependent variant, unimodal/Lipschitz continuum bandits give **$\tilde O(\sqrt T)$** regret (or $O(\log T)$ for strongly unimodal noise-free), bounding the cost of *learning* the footprint distribution. Sizeless-style predictors give one-shot estimates with bounded empirical error. These are upper bounds in the "parametric curve + noisy evaluation" model.

## 5. Lower Bound

Lower bounds are *information-theoretic and complexity-theoretic*, and partial. **(a)** Any online policy must pay $\Omega(\sqrt T)$ regret in the worst case for a Lipschitz continuum-armed bandit (matching the upper bound up to logs), so *learning* the right size from data has an unavoidable cost. **(b)** The footprint $S$ is itself a function of *selectivity/cardinality*, which cannot be predicted better than cardinality estimation allows — worst-case multiplicative error is unbounded (Ioannidis–Christodoulakis; AGM tightness), so for adversarial inputs no policy can pre-size to avoid a spill (a phase change once $S>m$ forces external-memory I/O), giving an information-theoretic barrier to perfect right-sizing. **(c)** DAG-level joint sizing under an SLO with discrete memory steps is a constrained nonlinear/combinatorial program that is NP-hard in general (it generalizes makespan-type allocation). No single tight bound covers the full problem; pieces hold in their sub-models.

## 6. The Gap

**Empirically open.** In practice right-sizing is solved *well enough* by sweeping (Power Tuning) or learning (COSE/Sizeless), and Pareto frontiers are routinely found. But there is no tight theory characterizing the *minimal* cost–latency product as a function of the data-dependent footprint distribution and the platform's $m\!\to\!$CPU mapping, nor a policy with *certified* regret that accounts for the spill phase-change and cardinality-estimation error together. DAG-level joint sizing under end-to-end SLOs lacks both tight approximation guarantees and a clean optimal substructure once data dependence and stragglers are included. Closing the gap needs a model unifying the speedup curve, external-memory spill, footprint uncertainty, and DAG critical path.

## 7. Current Research (as of June 2026)

Active: **adaptive online right-sizing** (Parrotfish-style parametric regression that updates per invocation), **one-shot ML predictors** (Sizeless successors) generalized across functions and inputs, and **footprint-aware** sizing that detects/anticipates spill from cardinality estimates *(frontier — verify)*. DAG-aware SLO-constrained sizing (StepConf line) is being extended to serverless query plans. Newer platform features (Lambda's flexible CPU, larger memory/ephemeral storage, SnapStart cold-start reduction) shift the cost curve and reopen tuning *(frontier — verify)*. Groups/people: Eismann and Kounev (Würzburg — Sizeless, serverless performance), Casalboni (AWS — Power Tuning), the COSE/Parrotfish authors, and the serverless-OLAP engine teams (Alonso/ETH, Madden/MIT). Frontier claim: *per-invocation, footprint-conditioned sizing beats static per-function sizing for skewed DB operators, but lacks regret guarantees in production* *(frontier — verify)*.

## 8. Future Work

- A unified cost model (speedup + spill phase-change + footprint distribution) with a provably optimal sizing policy and tight regret.
- Cardinality-estimate-conditioned sizing with bounds tying estimator error to expected over/under-provisioning cost.
- Tight approximation algorithms for DAG-level SLO-constrained joint sizing including stragglers (links to serverless-shuffle and predictive-elasticity-bounds).
- Cross-platform transfer so a curve learned on one runtime predicts $m^\*$ on another.

## 9. Key References

- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988.
- **[SOTA]** N. Akhtar, A. Raza, V. Ishakian, I. Matta. *COSE: Configuring Serverless Functions using Statistical Learning.* INFOCOM, 2020.
- **[SOTA]** S. Eismann et al. *Sizeless: Predicting the Optimal Size of Serverless Functions.* Middleware, 2021.
- **[SOTA]** A. Casalboni. *AWS Lambda Power Tuning.* Open-source tool / AWS Compute Blog, 2017–.
- **[SOTA]** Z. Wen, Y. Wang, F. Liu. *StepConf: SLO-Aware Dynamic Resource Configuration for Serverless Function Workflows.* INFOCOM, 2022.
- **[Foundational]** R. Kleinberg. *Nearly Tight Bounds for the Continuum-Armed Bandit Problem.* NeurIPS, 2004.
- **[Foundational]** Y. Ioannidis, S. Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991.

---
*Part of the [DBMS Research catalog](../../README.md).*
