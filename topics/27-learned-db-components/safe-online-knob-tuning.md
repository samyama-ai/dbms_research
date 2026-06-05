# Safe Online Configuration Tuning

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/safe-online-knob-tuning` · **Status:** open

## 1. Problem Statement
Offline tuning evaluates configurations on a replica; **online** tuning changes knobs $\theta_t$ on a *live production* system while serving real traffic. Each change risks a **performance regression** that directly harms users. The safe-online problem: design a sequential tuner that explores $\Theta$ to improve a metric $g$ while guaranteeing that, at every step $t$, performance stays above a safety threshold:
$$g(\theta_t) \ge (1-\alpha)\, g(\theta_{\mathrm{base}}) \quad \text{for all } t, \text{ w.h.p.},$$
and that any violation is **detected and rolled back** within a bounded number of steps with bounded cumulative damage.

Variants: **decision** (is there a safe improving move from the current safe set?), **optimization** (minimize regret subject to the per-step safety constraint), and the **rollback/recovery** variant (bound the time-to-detect and the integral of the regression during detection). Non-stationarity (workload drift) makes the safe set itself time-varying.

## 2. Mathematical Foundations
This is **safe sequential decision-making under uncertainty**, formalized as a constrained bandit/BO problem.
- **Safe Bayesian optimization (SafeOpt):** model $g$ as a GP; maintain a high-probability **safe set**
$$S_t = \{\theta : l_t(\theta) \ge (1-\alpha)g_{\mathrm{base}}\},$$
where $l_t$ is a GP lower-confidence bound, and only evaluate inside $S_t$, expanding it cautiously (Sui et al., Berkenkamp et al.). Safety holds w.p. $\ge 1-\delta$ given correct GP calibration.
- **Constrained / conservative bandits:** regret bounds with an anytime budget constraint $\sum_t (g_{\mathrm{base}} - g(\theta_t))_+ \le B$ (Wu et al., "Conservative Bandits").
- **Change-point detection:** rollback relies on detecting regressions; CUSUM / sequential-likelihood tests give expected detection delay vs. false-alarm-rate trade-offs (information-theoretic, Lorden's bound).
- **Statistical validity online:** **always-valid p-values / e-values** and confidence sequences (Howard–Ramdas) enable continuous safety monitoring without peeking bias.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **OnlineTune** (Zhang et al., SIGMOD 2022) applies contextual safe exploration to live DBMSs with safety constraints and a safe-region expansion strategy — the leading production-oriented safe online tuner. Cloud autopilots (e.g., Azure/Amazon auto-tuning) add guardrails and canarying. **CGPTuner** handles online context shift but with weaker formal safety.
- **Theory-SOTA:** **SafeOpt** (Sui–Gotovos–Burdick–Krause, ICML 2015) and **StageOpt** / **Berkenkamp et al.** provide the safe-set machinery with sublinear regret *and* high-probability safety, plus reachability characterizations of which optima are safely attainable.

## 4. Upper Bound
SafeOpt-class algorithms guarantee, under a correctly specified GP with RKHS norm bound and noise sub-Gaussianity, that **all evaluated configs are safe w.p. $\ge 1-\delta$**, while achieving sublinear cumulative regret $O^*(\sqrt{T\gamma_T})$ over the *reachable* safe set. Conservative-bandit analyses bound the safety-budget violation by a constant independent of $T$. Thus per-step safety + sublinear regret is *simultaneously achievable* in the GP model — the best known positive result.

## 5. Lower Bound
There are intrinsic **reachability limits**: SafeOpt provably cannot reach optima separated from the initial safe seed by an "unsafe valley" — the achievable optimum is the *safely reachable* set $R_\epsilon(S_0)$, which can be strictly suboptimal; this is a structural impossibility, not an algorithmic weakness. If GP calibration is wrong (misspecified kernel / heavy-tailed noise), **no safety guarantee can hold** — an instance of the impossibility of safe exploration without realizability assumptions. Online change-point detection has an information-theoretic delay–false-alarm trade-off (Lorden / Lai), lower-bounding rollback latency.

## 6. The Gap
Genuinely **open**. Positive results require GP realizability and stationarity that production DBMS surfaces routinely violate (integer knobs, sharp cliffs, drift). No method guarantees safety under *misspecification* or *adversarial workload shift*, which is exactly the production regime. The reachability gap (safely reachable vs. global optimum) is unquantified for real engines. Closing it needs (a) distribution-free / misspecification-robust safe exploration, (b) provable bounded-damage rollback under drift, and (c) reachability analysis tied to DBMS response-surface structure.

## 7. Current Research (as of June 2026)
Directions: (a) misspecification-robust safe BO using confidence sequences / e-values instead of fragile GP bounds *(frontier — verify)*; (b) staged canary + automatic-rollback pipelines with formal damage bounds, integrating change-point detection; (c) safe RL formulations (CMDP, Lagrangian shielding) for online tuning; (d) human-in-the-loop guardrails with provable escalation. Groups: Krause/Berkenkamp (ETH, safe BO); Zhang/Li (Tsinghua/PKU, OnlineTune); Ramdas (CMU, anytime-valid inference). Cloud vendors actively deploy guardrailed auto-tuners but publish few formal guarantees.

## 8. Future Work
- Distribution-free per-step safety guarantees.
- Provable rollback-time and cumulative-damage bounds under non-stationarity.
- Reachability characterization for real DBMS knob surfaces.
- Composition of safety guarantees when multiple components tune online simultaneously (links to co-learning).

## 9. Key References
- **[Foundational]** Y. Sui, A. Gotovos, J. Burdick, A. Krause. *Safe Exploration for Optimization with Gaussian Processes (SafeOpt).* ICML, 2015.
- **[SOTA]** X. Zhang et al. *Towards Dynamic and Safe Configuration Tuning for Cloud Databases (OnlineTune).* SIGMOD, 2022.
- **[Foundational]** F. Berkenkamp, A. Krause, A. P. Schoellig. *Bayesian Optimization with Safety Constraints: Safe and Automatic Parameter Tuning in Robotics.* Machine Learning, 2021.
- **[Foundational]** S. Howard, A. Ramdas, J. McAuliffe, J. Sekhon. *Time-uniform, Nonparametric, Nonasymptotic Confidence Sequences.* Annals of Statistics, 2021.
- **[Foundational]** Y. Wu, R. Shariff, T. Lattimore, C. Szepesvári. *Conservative Bandits.* ICML, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
