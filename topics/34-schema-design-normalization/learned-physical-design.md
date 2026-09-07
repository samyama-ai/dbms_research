---
id: 34-schema-design-normalization/learned-physical-design
title: "Learned and ML-Driven Physical Schema Design"
topic: 34-schema-design-normalization
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Learned and ML-Driven Physical Schema Design

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/learned-physical-design` · **Status:** empirically-open

## 1. Problem Statement
Replace (or augment) the hand-engineered cost models and search heuristics of physical design — index, view, partition, and layout selection — with **learned components**: learned cost/latency estimators and **reinforcement-learning (RL)** agents that propose configurations. The central scientific problem is not only to lower average workload cost but to do so **with guarantees against catastrophic regressions** — i.e., the learned designer must never (or provably rarely) produce a configuration substantially worse than a known-good baseline, despite the learned cost model being approximate and the action space combinatorial.

- **Optimization variant:** learn a policy $\pi$ mapping (schema, workload, current config) to design actions minimizing expected cost.
- **Safety variant (the hard part):** bound the probability/magnitude of regression: $\Pr[\,\text{cost}(\pi) > (1+\delta)\,\text{cost}(\text{baseline})\,]\le \rho$.

## 2. Mathematical Foundations
Frame design as a **Markov Decision Process** (MDP): states = configurations, actions = add/drop structures, reward = negative workload cost change. Learned cost models are function approximators $\hat{C}_\theta$ trained on executed plans; their **generalization** is governed by statistical learning theory (sample complexity, **VC dimension** / Rademacher complexity of the hypothesis class) and is fragile under **distribution shift** when the workload drifts off the training distribution.

Safety connects to **conservative / safe RL** and **offline RL** with pessimism: maximize a lower confidence bound on benefit so the policy is provably no worse than baseline with high probability. The estimation error $|\hat C_\theta - C|$ propagates into regret; **bandit** formulations give $\tilde O(\sqrt{T})$ regret bounds under suitable assumptions, but the combinatorial action space (exponential configurations) and non-stationarity break standard guarantees. Calibration / conformal prediction can wrap $\hat C_\theta$ to produce valid uncertainty for safe action gating.

## 3. State of the Art (SOTA)
- **Learned cost/cardinality models:** **MSCN** (Kipf et al., CIDR 2019), **Neo** (Marcus et al., VLDB 2019), **Bao** (Marcus et al., SIGMOD 2021) for learned/steered query optimization; learned cardinality estimators (deep autoregressive, e.g., Naru/DeepDB).
- **Learned physical design:** RL-based index selection — **DRLinda**, **SmartIX**, and **DBA bandits** (Perera et al.); learned view/partition advisors; **OtterTune** (Van Aken et al., SIGMOD 2017) for knob+design tuning. Bao popularized the **safety-via-bounded-action-set + bandit** recipe that limits catastrophic regressions in production.

This is "empirically-open": strong empirical wins exist, but formal, workload-shift-robust regression guarantees are not generally available.

## 4. Upper Bound
With a **conservative bandit / safe-RL** wrapper over a finite, vetted candidate action set, one can guarantee (with high probability) performance **no worse than the baseline** and sublinear regret $\tilde O(\sqrt{T})$ relative to the best fixed configuration in the candidate set — the design philosophy behind Bao. This is the best-known *provable* upper bound, and it holds only over a restricted action set and stationary (or slowly-varying) workload. There is no known algorithm achieving optimal physical design with guarantees over the full combinatorial space using learned costs.

## 5. Lower Bound
Even with a *perfect* cost oracle, the underlying selection problems are **NP-hard** (index/view selection embeds budgeted max-coverage; see sibling problems), so learned designers cannot escape that combinatorial hardness. With *approximate* learned costs, **no-free-lunch** and distribution-shift arguments imply that without a baseline-safety mechanism, an adversarial workload shift can drive arbitrarily bad regret — an information-theoretic obstacle: bounded training data cannot certify behavior on out-of-distribution workloads. Lower bounds on bandit regret ($\Omega(\sqrt{T})$ in general) cap achievable adaptation speed.

## 6. The Gap
The gap is between (a) empirical RL/learned-cost designers that win on average but can regress under shift, and (b) the desired **provable anti-regression guarantee over the full action space and under drift**. It is **genuinely open**: current guarantees hold only for restricted action sets and near-stationary workloads. Closing it requires drift-robust safe RL with verifiable bounds, calibrated uncertainty integrated into the search, and possibly hybrid analytic+learned cost models with provable error envelopes.

## 7. Current Research (as of June 2026)
- Conformal / calibrated uncertainty around learned cost models to gate unsafe actions *(frontier — verify)*.
- Offline + pessimistic RL for physical design with provable baseline-safety *(frontier — verify)*.
- LLM-assisted design proposal + learned-cost verification loops *(frontier — verify)*.
- Benchmarks for robustness under workload drift (extensions of JOB, DSB) *(frontier — verify)*.
- Groups: Kraska/Marcus (MIT/Intel→), Pavlo (CMU), Chaudhuri/Narasayya (MSR), Aboulnaga (Waterloo/Apple), Binnig (TU Darmstadt).

## 8. Future Work
- Verifiable anti-regression guarantees under non-stationary workloads.
- Sample-efficient learned costs with valid uncertainty quantification.
- Safe exploration that bounds cost during the learning phase itself.
- Transfer across schemas/engines to reduce per-instance training cost.

## 9. Key References
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** R. Marcus et al. *Neo: A Learned Query Optimizer.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1904.03711)
- **[SOTA]** A. Kipf et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** D. Van Aken, A. Pavlo, G. Gordon, B. Zhang. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[SOTA]** R. M. Perera et al. *DBA Bandits: Self-Driving Index Tuning under Ad-hoc, Analytical Workloads with Safety Guarantees.* ICDE, 2021. — [arXiv](https://arxiv.org/abs/2010.09208)
- **[Survey]** Z. Zhou, et al. / X. Zhou et al. *Database Meets Artificial Intelligence: A Survey.* IEEE TKDE, 2022. — [DOI](https://doi.org/10.1109/TKDE.2020.2994641)

## 10. Worked Example

Workload: 3 queries, each run with frequency $f=1$. Candidate structures: index $I_1$ (size 2), index $I_2$ (size 3), view $V$ (size 5). Storage budget $B=5$. True costs (from execution) for the best baseline-or-learned config:

| Config | Workload cost |
|--------|---------------|
| baseline (none) | 100 |
| $\{I_1\}$ | 70 |
| $\{I_2\}$ | 60 |
| $\{V\}$  | 30 |

A learned cost model $\hat C_\theta$ mis-estimates, predicting $\hat C(\{V\})=20$ but $\hat C(\{I_2\})=80$ — it *overrates* $V$ and *underrates* $I_2$. An unguarded RL agent picks $V$; here that's fine (true cost 30 < 100). But suppose on a *shifted* workload $V$ actually costs 130 (a regression) while the model still predicts 20. The Bao-style safety wrapper executes the chosen config but compares against the baseline: with bandit feedback it observes $130>100$, charges regret $130-30_{\text{best}}=100$ this round, and Thompson sampling down-weights $V$. Over $T$ rounds, regret grows as $\tilde O(\sqrt{T})$, and crucially the wrapper's vetted action set always includes "baseline," bounding any single-round loss. Without the wrapper, the model's confident wrong estimate yields unbounded regret under shift — illustrating the gap between average-case wins and provable anti-regression.

---
*Part of the [DBMS Research catalog](../../README.md).*
