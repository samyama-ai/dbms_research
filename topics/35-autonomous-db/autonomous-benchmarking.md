---
id: 35-autonomous-db/autonomous-benchmarking
title: "Benchmarking & Reproducible Evaluation"
topic: 35-autonomous-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Benchmarking & Reproducible Evaluation

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/autonomous-benchmarking` · **Status:** empirically-open

## 1. Problem Statement
How do we **fairly and reproducibly** compare self-driving database agents against each other and against strong human/heuristic baselines? Unlike a query benchmark with a fixed query set, an autonomous agent is a *closed-loop controller*: its actions change the system state, which changes future inputs. This makes evaluation a problem of comparing **policies under a non-stationary, agent-influenced environment**.

Sub-problems:
- **Workload generation:** produce workloads (and *workload drift*) that are realistic, diverse, and not over-fit to any one agent.
- **Metrics:** define metrics capturing not just steady-state throughput but *adaptation speed*, *regret vs. an oracle/clairvoyant tuner*, *safety* (worst-case regressions), *cost of actions* (rebuild/migration overhead), and *cumulative* cost over a horizon.
- **Protocol:** specify warm-up, seeds, exploration budgets, hardware, and what the agent may observe (what-if access, ground truth) so results are reproducible and the comparison is *apples-to-apples*.
- **Baselines:** strong human-DBA / heuristic-advisor baselines, not strawmen.

This is **empirically-open**: the obstruction is methodological, not a complexity-theoretic barrier.

## 2. Mathematical Foundations
Frame the system as a **Markov / partially-observable decision process** $(\mathcal{S}, \mathcal{A}, P, r, \gamma)$ where state $s$ is DB configuration + recent workload, action $a$ is a tuning/reconfiguration step, reward $r$ aggregates performance minus action cost. An agent is a policy $\pi$; the evaluation target is its **value** $V^\pi$ or its **regret** $\mathrm{Reg}_T(\pi) = \sum_{t\le T}\big(r_t(\pi^\*) - r_t(\pi)\big)$ against a clairvoyant comparator $\pi^\*$.

Key issues with rigorous foundations:
- **Off-policy / counterfactual evaluation:** comparing policies on logged data needs unbiased estimators (importance sampling, doubly-robust); naïvely replaying one agent's trace under-/over-states another's value.
- **Confounded non-stationarity:** since the agent *causes* state transitions, you cannot simply re-use one agent's observed workload for another — a causal-inference framing (do-calculus / potential outcomes) is needed.
- **Statistical power:** runs are expensive and high-variance; you need variance-reduction (common random numbers, paired seeds) and multiple-comparison correction. Report confidence intervals, not single numbers.
- **Generalization gap:** an agent tuned/evaluated on the same workload family exhibits optimistic bias; held-out *distribution shift* (analogous to train/test in ML) must be measured.

## 3. State of the Art (SOTA)
**Systems-SOTA:** TPC-C/TPC-H/TPC-DS and the **Star Schema Benchmark** are workload sources but were not built for closed-loop tuning. **OLTP-Bench / BenchBase** (CMU) provides controllable, mixed, rate-limited workloads and is the de-facto harness for tuning studies. **OtterTune** (VLDB 2017) and follow-ups, **CDBTune** (SIGMOD 2019, RL knob tuning), **QTune**, and index advisors are evaluated on these. The **JOB / Join Order Benchmark** stresses cardinality estimation. Cloud vendors run internal A/B fleets. Most papers, however, use bespoke protocols, making cross-paper comparison unreliable.

**Methodology-SOTA:** community calls for reproducibility (SIGMOD Reproducibility, ACM artifact badging) and dedicated critiques of self-driving evaluation; emerging **agent benchmarks** that script workload drift and report regret-style metrics. *(frontier — verify)*

## 4. Upper Bound
There is no algorithmic "upper bound" here in the complexity sense; the achievable target is an **evaluation protocol with provable statistical guarantees**: e.g., off-policy value estimates with $O(1/\sqrt{n})$ confidence-interval width via doubly-robust estimators, and *unbiased* regret estimates against a computable clairvoyant baseline when the workload trace is fixed and agent actions are simulated in a faithful (what-if) model. Where a faithful simulator exists, regret against the optimal in-hindsight configuration is exactly computable, giving a tight comparator.

## 5. Lower Bound
- **Counterfactual impossibility:** without a faithful simulator or randomized exploration, off-policy comparison of two action-influencing policies is **not identifiable** — different policies induce different state distributions, so any single logged trace cannot estimate both values without coverage/overlap assumptions (positivity). This is an information-theoretic obstruction from causal inference.
- **No-free-lunch / overfitting:** for any finite benchmark suite there exist agents that exploit its idiosyncrasies; ranking on a fixed suite cannot certify generalization (a learning-theoretic limit tied to the evaluator's own VC/Rademacher complexity over the benchmark family).
- **Sample-cost lower bounds:** distinguishing two policies whose value gap is $\Delta$ needs $\Omega(\sigma^2/\Delta^2)$ runs (standard estimation lower bound), which for expensive DB experiments is the practical barrier.

## 6. The Gap
**Empirically open.** We lack (a) a *standard, drift-aware, agent-vs-baseline* benchmark with agreed metrics and reproducibility protocol, and (b) accepted *counterfactual* evaluation methodology so two agents can be compared without re-running each in every environment. The "gap" is sociotechnical: closing it needs a community-adopted suite (workloads + drift scenarios + strong baselines + statistics) plus faithful what-if simulators so regret-against-clairvoyant becomes the common currency.

## 7. Current Research (as of June 2026)
- Extensions of BenchBase toward closed-loop, drift-scripted autonomous-tuning evaluation. *(frontier — verify)*
- Off-policy / counterfactual evaluation imported from RL into DB tuning, with simulators trained on telemetry. *(frontier — verify)*
- Reproducibility pushes: artifact evaluation, shared traces (e.g., cloud snowset-style workload traces, Snowflake/Redshift telemetry releases). Groups: CMU (Pavlo), Microsoft GSL, TU Darmstadt, HPI, MIT/Berkeley learned-systems. *(frontier — verify)*
- Calls to report *safety* and *worst-case regression* alongside mean throughput.

## 8. Future Work
- A canonical "autonomous-DB gym" with versioned workloads, injected drift/anomalies, and adversarial scenarios (couples with adversarial-robustness).
- Standard regret and safety metrics with required confidence intervals and seeds.
- Faithful, openly-validated what-if simulators enabling cheap, unbiased counterfactual comparison.
- Cost-aware metrics that internalize action overhead and (in shared settings) cross-tenant externalities.

## 9. Key References
- **[Foundational]** TPC. *TPC-C / TPC-H / TPC-DS Benchmark Specifications.* Transaction Processing Performance Council. — [TPC](https://www.tpc.org/)
- **[SOTA]** D. Van Aken, A. Pavlo, G. Gordon, B. Zhang. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[SOTA]** J. Zhang et al. *An End-to-End Automatic Cloud Database Tuning System Using Deep Reinforcement Learning (CDBTune).* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3300085)
- **[Foundational]** D. E. Difallah, A. Pavlo, C. Curino, P. Cudré-Mauroux. *OLTP-Bench: An Extensible Testbed for Benchmarking Relational Databases.* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2732240.2732246)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[SOTA]** M. Dudík, J. Langford, L. Li. *Doubly Robust Policy Evaluation and Learning.* ICML, 2011. — [arXiv](https://arxiv.org/abs/1103.4601)

## 10. Worked Example

**Why a replayed trace mis-ranks agents.** Two tuners are compared on a fixed workload trace. Agent $\pi_A$ builds index $I$; agent $\pi_B$ does not. We log $\pi_A$ running, observing mean latency $40$ ms, and want to estimate $\pi_B$'s value by replay.

The catch: under $\pi_A$, the *query optimizer rewrites plans to use $I$*, so the logged query mix and cardinalities differ from what $\pi_B$ would have seen. Naïve replay assigns $\pi_B$ the logged $40$ ms — but $\pi_B$ never built $I$, so its plans would be scans, say $70$ ms. The replay estimate is biased because the two policies induce **different state distributions** (positivity/overlap fails): the log has zero coverage of "no-$I$ plan on this query," so $V^{\pi_B}$ is **not identified** (§5).

**Sample budget.** Suppose the true gap is $\Delta = V^{\pi_A}-V^{\pi_B} = 30$ ms with per-run noise $\sigma = 60$ ms. Distinguishing the two at fixed confidence needs
$$n \;=\; \Omega\!\left(\frac{\sigma^2}{\Delta^2}\right) \;=\; \Omega\!\left(\frac{60^2}{30^2}\right) \;=\; \Omega(4)$$
runs *per agent* under paired common-random-number seeds. Halving the gap to $\Delta=15$ quadruples the requirement to $\Omega(16)$ runs — the $1/\Delta^2$ blow-up that makes expensive DB experiments the practical barrier (§4–§5), and why a faithful what-if simulator (which restores coverage and lets regret-vs-clairvoyant be computed) is the lever in §6.

---
*Part of the [DBMS Research catalog](../../README.md).*
