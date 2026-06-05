# Safe Online Action Deployment

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/safe-action-deployment` · **Status:** open

## 1. Problem Statement
A self-driving controller decides *what* to change (build index, drop view, flip a knob); **safe deployment** governs *how* to apply that change to a **live** system serving real traffic, so that a wrong or mis-estimated action cannot cause an unbounded performance regression, and so that any harmful action can be **rolled back** with a guarantee. The problem is the online-control analogue of "first, do no harm."

Variants:
- **Bounded-regression variant:** apply actions so that, at every time $t$, performance is no worse than $(1+\gamma)$ times a safe baseline (the pre-action or human configuration), with high probability.
- **Rollback-guarantee variant:** ensure every applied action has a reachable, bounded-cost inverse that restores a known-good state.
- **Sequential / budgeted-risk variant:** over a horizon, keep cumulative *safety violations* below a budget while still improving (a constrained online-learning / safe-exploration problem).

## 2. Mathematical Foundations
Model deployment as a constrained online decision process. At step $t$ the controller picks action $a_t$; the system yields performance $r_t$ and the *baseline* (do-nothing / human config) yields $r_t^{0}$. Define **safety regression** $g_t = \max(0,\, r^0_t - r_t)$ (cost above baseline). Two formal frameworks:

1. **Constrained / conservative online learning.** Require, for every $T$, the *conservative constraint*
$$\sum_{t=1}^{T} r_t \ \ge\ (1-\alpha)\sum_{t=1}^{T} r^0_t,$$
i.e. never fall more than a fraction $\alpha$ below the baseline (Wu et al., "conservative bandits"). Achievable simultaneously with sublinear regret.
2. **Safe MDP / shielding.** A *shield* (Alshiekh et al.) is a reactive policy filter that provably blocks any action leading outside a verified safe set; combined with reachability analysis it guarantees the controller never enters an unsafe region. Rollback corresponds to requiring the safe set be *controllable back to* a recovery state — a backward-reachability condition.

The rollback guarantee rests on **invertibility/idempotence** of physical-design operations and on transactional **atomic switch** semantics (apply-or-abort), making deployment a state-machine reachability problem.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Production self-driving systems gate actions behind validation and staged rollout: OtterTune (Van Aken et al., SIGMOD 2017) recommends but defers application; CMU's self-driving DBMS (Pavlo et al., CIDR 2017) frames "actions" with cost/benefit and behavior modeling; cloud advisors (Azure SQL automatic tuning) auto-create indexes but **monitor and auto-revert** on regression — the strongest deployed safety pattern. Microsoft's auto-indexing explicitly compares post-deployment performance to a baseline and rolls back.

**Theory-SOTA.** Conservative bandits/RL (Wu et al. 2016; Garcelon et al. 2020) give *sublinear-regret-with-baseline-safety* algorithms; safe RL via shielding and constrained MDPs (CMDP, Altman) give per-step or cumulative constraint guarantees. These are general; DB-specific worst-case-bounded deployment with rollback is not formalized end-to-end.

## 4. Upper Bound
Conservative bandit/linear-bandit algorithms guarantee the baseline constraint holds for **all** $T$ while achieving regret $O(\sqrt{T})$ plus a constant overhead for the safety budget (stochastic bandit / linear-bandit model). With a verified shield, the probability of an unsafe action is **zero** by construction (given a correct safe-set model), and rollback cost is bounded by the inverse-operation cost — the best available positive results.

## 5. Lower Bound
Safety is not free: any algorithm guaranteeing the conservative baseline constraint must incur an **additive regret overhead** that is $\Omega(1)$ (and grows with how tight $\alpha$ is) relative to the unconstrained optimum — a lower bound in the bandit model (Wu et al.). More fundamentally, with **unknown stochastic outcomes** you cannot guarantee zero regression while still exploring: distinguishing a good action from a harmful one requires trying it, and information-theoretically you need $\Omega(1/\Delta^2)$ samples to detect a regression of size $\Delta$ — so *some* exposure to harm is unavoidable without a perfect prior (sample-complexity lower bound). Shielding's zero-violation guarantee is only as sound as the (possibly wrong) safe-set model — an impossibility under model misspecification.

## 6. The Gap
**Open.** Deployed systems achieve safety via *detect-and-revert* (reactive), but lack *proactive* worst-case-bounded-regression guarantees tied to the action's estimated benefit/uncertainty. The gap is between (a) bandit-theoretic conservative guarantees that assume stationary stochastic rewards and (b) real DB dynamics with drift, build latency, and transient states during the change. Closing it requires safe-exploration bounds that hold under non-stationarity *and* account for the cost of the transition itself.

## 7. Current Research (as of June 2026)
Active directions: shielding/CMDP applied to DB knob tuning with verified safe sets; "canary"/staged rollout with statistically-valid stopping (sequential testing) to bound exposure; uncertainty-gated action application that only deploys when benefit dominates a calibrated risk bound *(frontier — verify)*; and verifiable rollback via transactional DDL and shadow structures (CMU, Microsoft GSL, and safe-RL groups bridging to systems). End-to-end formal worst-case-regression guarantees on production engines remain unachieved *(frontier — verify)*.

## 8. Future Work
- Bounded-regression deployment under drift and non-stationary rewards.
- Accounting for transition/build cost and transient-state risk in the safety bound.
- Verified, bounded-cost rollback for joint multi-structure actions.
- Composing per-action safety into horizon-level cumulative-risk budgets.

## 9. Key References
- **[Foundational]** Pavlo, A., et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[SOTA]** Van Aken, D., Pavlo, A., Gordon, G., Zhang, B. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[Foundational]** Wu, Y., Shariff, R., Lattimore, T., Szepesvári, C. *Conservative Bandits.* ICML, 2016. — [arXiv](https://arxiv.org/abs/1602.04282)
- **[SOTA]** Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., Topcu, U. *Safe Reinforcement Learning via Shielding.* AAAI, 2018. — [arXiv](https://arxiv.org/abs/1708.08611)
- **[Foundational]** Altman, E. *Constrained Markov Decision Processes.* Chapman & Hall, 1999. — [DBLP search](https://dblp.org/search?q=Altman%20Constrained%20Markov%20Decision%20Processes)

## 10. Worked Example

A controller deploys a knob change to a live instance. Baseline throughput is $r^0 = 100$ tps each round; the conservative budget is $\alpha = 0.05$, so the constraint of Section 2 demands $\sum_{t\le T} r_t \ge 0.95\sum_{t\le T} r^0_t = 95T$.

Round-by-round, suppose the new config under-performs at first while warming caches:

| round $t$ | $r_t$ | cumulative $\sum r_t$ | floor $95t$ | slack |
|---|---|---|---|---|
| 1 | 80 | 80 | 95 | $-15$ |
| 2 | 90 | 170 | 190 | $-20$ |

After round 2 the cumulative $170$ has already breached the floor $190$: the deployment violated the bounded-regression guarantee. A **conservative** controller instead tracks the running budget *before* committing: entering round 1 it has banked surplus $0$, so a config expected to dip below $95$ may only be applied if banked slack covers the shortfall. Lacking slack, the shield **rolls back** to baseline (cost = inverse-DDL cost, $O(1)$), keeping $r_t = 100$ and the constraint intact.

The Section 5 lower bound bites here: to *know* the new config was bad, the controller had to run it for $\Omega(1/\Delta^2)$ rounds with $\Delta = 20$, so a small, bounded exposure to the $-20$ regression was information-theoretically unavoidable — but the budget caps it and rollback prevents unbounded damage.

---
*Part of the [DBMS Research catalog](../../README.md).*
