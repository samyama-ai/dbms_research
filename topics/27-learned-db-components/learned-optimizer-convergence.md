# Learned Query Optimizer Convergence

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-optimizer-convergence` · **Status:** empirically-open

## 1. Problem Statement

A *learned query optimizer* replaces (parts of) Selinger-style dynamic programming with a policy trained by reinforcement learning (RL) or learned plan search: it observes a query, emits join order / operator / index choices, executes, and uses measured latency as reward. The convergence problem asks: **does such a policy converge to (near-)optimal plans, and what is the sample (query-execution) cost of that convergence?**

Variants:

- **Asymptotic convergence (decision):** does the learned policy $\pi_t$ converge as $t\to\infty$ to a policy whose expected plan cost is within factor $(1+\epsilon)$ of the optimal plan-search policy on the training workload distribution $\mathcal D$?
- **Sample complexity (quantitative):** how many executed queries $T(\epsilon,\delta)$ are needed before $\Pr[\text{cost}(\pi_T)\le(1+\epsilon)\,\text{cost}(\pi^\*)]\ge 1-\delta$?
- **Regret (online):** minimize cumulative excess latency $\sum_{t}\big(\text{cost}(\pi_t(q_t))-\text{cost}(\pi^\*(q_t))\big)$.

This is empirically-open: systems demonstrably converge on benchmark workloads (JOB, TPC-H/DS), but no system gives a workload-independent convergence rate, and convergence is brittle to workload/data drift.

## 2. Mathematical Foundations

Model plan search as a finite-horizon **Markov Decision Process** $\mathcal M=(S,A,P,r,H)$: a state $s$ is a partial plan (set of joined relations + chosen physical operators), an action $a$ extends it, the horizon $H$ is the number of joins, reward $r=-\log(\text{latency})$ at the leaf. The join-ordering MDP has $|A|=O(n^2)$ per step and a state space exponential in $n$; the *optimal substructure* exploited by Selinger DP corresponds to an MDP whose optimal value function factorizes over relation subsets.

Relevant theory: tabular RL gives sample complexity $\tilde O(|S||A|H^2/\epsilon^2)$ for $\epsilon$-optimal policies (PAC-MDP, e.g. UCBVI; Azar–Osband–Munos 2017), but $|S|$ is exponential, so guarantees require **function approximation**. With linear-realizable $Q$ and bounded feature dimension $d$, regret is $\tilde O(\sqrt{d^3 H^3 T})$ (LSVI-UCB; Jin et al. 2020). The catch: optimal value functions over plans are **not** known to be low-rank in any standard plan encoding, so realizability is an assumption, not a theorem. Convergence of policy-gradient/actor-critic methods is only guaranteed to *stationary points*, which may be poor local optima for non-convex deep value nets.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** *Neo* (Marcus et al., VLDB 2019) and *Bao* (Marcus et al., SIGMOD 2021) — Bao narrows the action space to hint sets over an existing optimizer, which empirically converges in hundreds of queries with low regret. *Balsa* (Yang et al., SIGMOD 2022) learns from scratch with a simulation-bootstrapped value net, converging without an expert optimizer. *LOGER*, *LEON*, and *HybridQO* refine plan ranking with learned + cost-model signals.
- **Theory-SOTA:** no convergence-rate theorem specific to plan-search MDPs; the field imports generic PAC-MDP / linear-MDP rates that do not bind the true (exponential, non-realizable) problem.

## 4. Upper Bound

- **Generic:** under a linear-MDP / low-Bellman-rank assumption on the plan encoding, $\tilde O(\sqrt{d^3H^3T})$ regret and $\mathrm{poly}(d,H,1/\epsilon)$ sample complexity (LSVI-UCB; Eluder-dimension bounds, Jin et al. 2020). Holds in the **statistical learning model** only under the realizability assumption.
- **Practical (action-restricted):** Bao-style hint selection reduces the problem to a contextual bandit with $K$ arms, giving $\tilde O(\sqrt{KT})$ regret (LinUCB), which is the only *honest* near-tight upper bound the field can defend — it works because it sidesteps full plan search.

## 5. Lower Bound

- **Exploration hardness:** for general MDPs with $|S|$ states, any algorithm needs $\Omega(|S||A|H/\epsilon^2)$ samples (PAC-MDP lower bound); since reachable plan states are exponential in $n$, worst-case convergence is exponential without structural assumptions.
- **Non-realizability barrier:** if the optimal $Q^\*$ is not in the function class, RL with that class can fail to converge to any near-optimal policy (no agnostic guarantee for general MDPs; Weisz et al. 2021 show exponential lower bounds even under $q^\pi$-realizability with large action sets).
- **Planning NP-hardness:** optimal join ordering with cross products is NP-hard (Ibaraki–Kameda 1984), so even the *target* of convergence is intractable to certify exactly.

## 6. The Gap

Genuinely open and **wide**. Upper bounds either assume a realizability property no one has established for plan encodings, or restrict the action space until the problem becomes a bandit. Lower bounds say worst-case convergence is exponential. Closing the gap needs either (a) a structural theorem that optimal plan value functions are low-rank under a concrete encoding (linking to **plan-featurization-expressiveness**), or (b) a hardness result that learned plan search cannot beat classical DP in samples without such structure.

## 7. Current Research (as of June 2026)

- Action-space restriction (Bao/LEON hint sets) as the pragmatic convergence guarantee; learned components as *re-rankers* over a sound optimizer rather than replacements (MIT Marcus/Kraska; Tianzheng Wang group).
- Offline / off-policy RL and simulation pre-training (Balsa) to cut online exploration cost, with value-net bootstrapping from a learned cost model *(frontier — verify)*.
- Convergence diagnostics and "experience reuse" across workloads to amortize the exploration budget (TUM, CMU) *(frontier — verify)*.

## 8. Future Work

- A plan-encoding-specific sample-complexity theorem (realizability or its impossibility).
- Provably safe warm-starting from the classical optimizer so $t=0$ regret is bounded (links to **safe-exploration-optimizers**).
- Workload-drift-aware convergence: re-convergence rate after distribution shift, not just cold-start rate.

## 9. Key References

- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1904.03711)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** Yang, Chiang, Luan, et al. *Balsa: Learning a Query Optimizer Without Expert Demonstrations.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2201.01441)
- **[Foundational]** Jin, Yang, Wang, Jordan. *Provably Efficient Reinforcement Learning with Linear Function Approximation.* COLT, 2020. — [arXiv](https://arxiv.org/abs/1907.05388)
- **[Foundational]** Azar, Osband, Munos. *Minimax Regret Bounds for Reinforcement Learning.* ICML, 2017. — [arXiv](https://arxiv.org/abs/1703.05449)
- **[Foundational]** Ibaraki, Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1270.1498)

## 10. Worked Example

**The MDP blow-up vs. the bandit shortcut, $n=4$ relations.** Plan search for a 4-way join is an MDP whose states are partial plans. The number of left-deep join orders alone is $4! = 24$; counting bushy plans the reachable state count is $\sum_{k} \binom{4}{k}\cdot(\text{sub-plans})$, already in the hundreds, and it grows super-exponentially in $n$. A tabular PAC-MDP bound $\tilde O(|S||A|H^2/\epsilon^2)$ would demand executing thousands of queries just for $n=4$ — and $|S|$ explodes for realistic $n=10$.

**Bao's shortcut.** Restrict the action to choosing one of $K=5$ hint-sets (e.g. {default, no-nestloop, no-hashjoin, no-mergejoin, no-indexscan}) over the *existing* optimizer. This collapses the MDP to a contextual bandit: each query is a context, each arm a hint-set, reward $=-\text{latency}$. LinUCB gives regret $\tilde O(\sqrt{KT})=\tilde O(\sqrt{5T})$. Concretely, after $T=500$ queries the cumulative excess latency is bounded by $\approx c\sqrt{2500}=50c$ — convergence in *hundreds* of queries, matching the empirical Bao result. The trade: we no longer search the full plan space, so optimality is relative to what the base optimizer's hint-sets can express, sidestepping the unproven realizability assumption that full plan-search RL requires.

---
*Part of the [DBMS Research catalog](../../README.md).*
