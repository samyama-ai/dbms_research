# Counterfactual Action Evaluation

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/counterfactual-evaluation` · **Status:** open

## 1. Problem Statement
A self-driving database collects a log of *(state, action, reward)* tuples generated under its *current* deployed policy: configurations it actually built (indexes, knob settings, partitionings) and the latencies/throughputs that resulted. The **counterfactual action evaluation** problem asks: given only this logged, non-randomized production data, estimate the performance the system *would have* achieved under a *different* action that was **not taken** — without paying to actually execute it.

Formally, with contexts $x$ (workload + DB state), a *logging policy* $\mu(a\mid x)$ that produced the data, and a *target action/policy* $\pi$, estimate the value
$$V(\pi) = \mathbb{E}_{x\sim D,\, a\sim\pi(\cdot\mid x)}\big[r(x,a)\big]$$
from samples $\{(x_i, a_i, r_i)\}$ with $a_i\sim\mu(\cdot\mid x_i)$ and $r_i$ observed only for $a_i$.

Variants. **(i) Decision:** is $V(\pi) > V(\mu)$ (should we switch)? **(ii) Estimation:** produce a point estimate plus a confidence interval on $V(\pi)$. **(iii) Selection/optimization:** pick $\arg\max_{\pi\in\Pi} \hat V(\pi)$ over a candidate set of designs. The defining difficulty is that the database **never randomized** its actions, so the log is *confounded*: the logging policy chose actions because of workload features that also drive reward.

## 2. Mathematical Foundations
This is **off-policy evaluation (OPE)** / counterfactual policy estimation under the **potential-outcomes** (Rubin) and contextual-bandit frameworks.
- **Inverse Propensity Scoring (IPS):** $\hat V_{\mathrm{IPS}} = \frac1n\sum_i \frac{\pi(a_i\mid x_i)}{\mu(a_i\mid x_i)} r_i$, unbiased iff **positivity** ($\mu(a\mid x)>0$ wherever $\pi(a\mid x)>0$) and **unconfoundedness** (logged propensities known) hold. Variance scales with the propensity ratio and can explode.
- **Doubly Robust (DR):** combines IPS with a reward model $\hat r$; consistent if *either* the propensity model *or* the reward model is correct. Lower variance than IPS.
- **Concentration:** confidence intervals via empirical Bernstein / self-normalized bounds on the importance-weighted estimator; effective sample size $\propto (\sum w_i)^2/\sum w_i^2$.
- **Identifiability:** under hidden confounding, $V(\pi)$ is only **partially identified** — Manski-style bounds, not a point. Sensitivity models (Rosenbaum $\Gamma$) bound the bias.
- **Cost-model surrogates** play the role of $\hat r$; "what-if" optimizer calls give cheap but biased counterfactual rewards.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Index advisors and "what-if" APIs (Microsoft AutoAdmin / Database Tuning Advisor) estimate the cost of *unbuilt* indexes via the optimizer's hypothetical cost — a model-based counterfactual. RL tuners (CDBTune, QTune, UDO) reuse replay buffers but mostly assume on-policy or simulator access. Bao/Balsa and learned cardinality estimators provide reward surrogates. Off-policy bandit machinery is now appearing in DBMS knob/index tuning to reuse historical trials *(frontier — verify)*.
- **Theory-SOTA:** Doubly-robust and **switch/SWITCH-DR**, **MRDR**, and **CAB** estimators (Dudík, Wang, Agarwal; Su et al.) give the best bias–variance tradeoffs; **DRos** / shrinkage-optimized weights (Su et al., ICML 2020) optimize the IPS clipping threshold.

## 4. Upper Bound
For a finite policy class $\Pi$ under positivity and known propensities, DR achieves estimation error $\tilde O\!\big(\sqrt{V^\star \log|\Pi| / n}\big)$ where $V^\star$ is the (reduced) variance of the DR score, and uniform guarantees over $\Pi$ follow by a union/covering argument — enabling provably near-optimal *policy selection* with $n = \tilde O(\text{Var}\cdot\log|\Pi|/\epsilon^2)$ logged samples. With a $\zeta$-correct reward model, DR's bias is $O(\zeta_\mu\cdot\zeta_r)$ (product of model errors), the best general guarantee.

## 5. Lower Bound
- **Information-theoretic:** any unbiased importance-weighting estimator has variance $\Omega$ scaling with $\sup_x \pi/\mu$; when the logging policy is **near-deterministic** (positivity violated), no estimator can identify $V(\pi)$ — the parameter is unidentified and worst-case error is $\Omega(1)$ regardless of $n$ (Manski partial-identification lower bound).
- **Confounding impossibility:** with unobserved confounders, point identification is impossible; only interval estimates exist (a causal-inference impossibility, analogous in spirit to FLP for the "no free identification" sense).
- The $\sqrt{\log|\Pi|/n}$ rate is minimax-optimal for policy *selection* over finite $\Pi$.

## 6. The Gap
The estimation gap is essentially **closed in the idealized bandit model** (DR is minimax-optimal up to constants). The genuinely **open** part is DBMS-specific: production logs have *unknown* propensities (the database did not record a stochastic policy), near-deterministic logging (severe positivity violations), and **delayed, non-stationary** rewards (a built index changes future workload). Bridging from "off-policy bandit theory" to "estimate the effect of an index/knob change from confounded, deterministic, drifting production logs with valid finite-sample intervals" is unsolved.

## 7. Current Research (as of June 2026)
Active threads: (a) propensity *estimation/imputation* for deterministic logs plus sensitivity analysis to bound residual confounding; (b) combining optimizer "what-if" cost models as the DR control variate with learned-CE error bars *(frontier — verify)*; (c) OPE for the *sequential* (full-RL) setting where actions have downstream effects (marginalized importance sampling, MAGIC, fitted-Q evaluation); (d) safe policy improvement with high-confidence lower bounds before deploying a design change. Groups: Pavlo/CMU (self-driving DB, NoisePage/OtterTune lineage), Trummer/Cornell, Kraska/MIT, and the OPE/causal-ML community (Dudík, Joachims, Thomas, Brunskill, Athey).

## 8. Future Work
- Finite-sample, distribution-free confidence intervals on $V(\pi)$ that remain valid under estimated propensities and drift.
- Principled fusion of *cheap biased* what-if cost models with *expensive unbiased* execution probes (multi-fidelity counterfactuals).
- Sequential OPE that accounts for an action reshaping the future workload (interventional non-stationarity).
- Sensitivity bounds tying Rosenbaum $\Gamma$ to deployable "don't switch unless gain exceeds bias" rules.

## 9. Key References
- **[Foundational]** M. Dudík, J. Langford, L. Li. *Doubly Robust Policy Evaluation and Learning.* ICML, 2011.
- **[Foundational]** C. F. Manski. *Identification for Prediction and Decision.* Harvard University Press, 2007.
- **[SOTA]** Y. Su, M. Dimakopoulou, A. Krishnamurthy, M. Dudík. *Doubly Robust Off-Policy Evaluation with Shrinkage.* ICML, 2020.
- **[SOTA]** P. Thomas, G. Theocharous, M. Ghavamzadeh. *High-Confidence Off-Policy Evaluation.* AAAI, 2015.
- **[Foundational]** S. Chaudhuri, V. Narasayya. *AutoAdmin "What-If" Index Analysis Utility.* SIGMOD, 1998.
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
