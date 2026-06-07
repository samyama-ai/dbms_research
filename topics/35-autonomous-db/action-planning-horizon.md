---
id: 35-autonomous-db/action-planning-horizon
title: "Action-Planning Horizon & Sequencing"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Action-Planning Horizon & Sequencing

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/action-planning-horizon` · **Status:** open

## 1. Problem Statement
A self-driving database does not just pick a *target* configuration; it must decide the **ordered sequence of design changes** to reach (and continually re-reach) good states over time. Each action — build an index, drop one, repartition, change a knob — has a **build cost** (time, CPU, extra storage, possible exclusive lock) and induces **transient states** in which performance is *worse* than both the start and the destination (e.g., during an index build the table is partly degraded). The problem: **plan a schedule of actions over a horizon $H$ that maximizes cumulative utility net of build/transition cost**, given a forecast of the (drifting) future workload.

Formally, with state $s_t$ (set of physical-design decisions + DB stats), action set $A(s_t)$, transition cost $c(s_t,a)$, transient/online reward $r(s_t,a)$, and workload forecast $\{w_t\}$, find a policy maximizing
$$\sum_{t=1}^{H} \gamma^{t}\,\big[\,u(s_t; w_t) - c(s_{t-1}, a_t)\,\big].$$
Variants. **(i) Decision:** does a horizon-$H$ schedule of total cost $\le B$ achieve utility $\ge U$? **(ii) Optimization:** maximize discounted net utility. **(iii) Online/competitive:** workload revealed incrementally — minimize competitive ratio vs. an offline optimum. The crux is that **myopic** (greedy, per-step) tuning ignores build cost and transient pain, and can thrash (build/drop oscillation) or fail to amortize an expensive index over a long-lived workload.

## 2. Mathematical Foundations
- **Finite-horizon MDP / optimal control:** the natural model; states are physical designs, actions are migrations, with switching/build costs. Bellman optimality over horizon $H$.
- **Metrical Task Systems (MTS) & $k$-server-like structure:** moving between configurations with a movement (build) cost plus a service (workload) cost is exactly an MTS / convex-body-chasing instance — gives competitive-ratio theory for the online variant.
- **Submodularity:** the *static* "pick a set of indexes under a storage budget" subproblem is monotone-submodular-ish, yielding greedy $(1-1/e)$ guarantees — but sequencing breaks pure submodularity because of order-dependent transient cost.
- **Job-scheduling / sequencing complexity:** ordering builds with precedence and resource contention is scheduling-hard.
- **Forecast error** enters as model-predictive control (MPC) with a receding horizon; regret degrades with forecast inaccuracy.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **AutoAdmin/DTA** and modern cloud advisors choose *which* indexes but largely ignore *ordering* and transient cost; they recommend a target set. **Self-Driving Peloton / NoisePage** (Ma et al., SIGMOD 2018; Pavlo CIDR 2017) introduced forecasting workload and *scheduling* actions ahead of demand, explicitly modeling action cost and deployment timing. RL tuners (UDO, Trummer 2021) plan joint index+knob changes; **Microsoft Auto-Indexing** sequences create/drop with regression-gated rollout.
- **Theory-SOTA:** online configuration migration maps to **MTS / convex body chasing**, whose competitive ratios (Bubeck et al.; Sellke) are the relevant theory; finite-horizon MDP planning (value iteration / MCTS) is the algorithmic backbone.

## 4. Upper Bound
For a known finite-horizon MDP with $|S|$ states and $|A|$ actions, the optimal schedule is computable by value iteration in $O(H\,|S|\,|A|)$ — but $|S|$ is exponential in the number of design decisions, so this is only a *conceptual* bound. For the **online** configuration-chasing variant on a metric of $n$ configurations, MTS admits an $O(\log^2 n)$-competitive randomized algorithm (and $O(\log n)$ for special metrics); nested convex body chasing is $O(\sqrt{d\log T})$-competitive in $d$ dimensions (Sellke 2020). The static index-selection subproblem admits a greedy $(1-1/e)$-approximation under a budget.

## 5. Lower Bound
- **NP-hardness:** optimal index/physical-design selection under a storage budget is **NP-hard** (reduces from knapsack/set-cover); adding sequencing with precedence/resource constraints keeps it NP-hard.
- **Online lower bound:** any randomized algorithm for MTS on $n$ points is $\Omega(\log n/\log\log n)$-competitive; deterministic MTS is $\Omega(n)$-competitive on the uniform metric — so *no* online scheduler can be constant-competitive against an offline-optimal plan in general.
- **Planning hardness:** general finite-horizon MDP planning is PSPACE-hard in succinctly-represented (factored) state spaces, which physical-design states are.

## 6. The Gap
**Genuinely open.** Static selection (NP-hard but with good approximations) and abstract online chasing (tight competitive bounds) are each fairly well understood, but the *combined* DBMS problem — sequencing under **build cost + transient degradation + drifting forecast + resource contention** — has no algorithm with end-to-end guarantees. The gap between the $(1-1/e)$ static bound and the $\Omega(\log n)$ online competitive floor is real, and neither captures transient-state cost. Closing it needs a model that unifies switching-cost online optimization with factored-MDP planning and forecast error.

## 7. Current Research (as of June 2026)
Threads: (a) **forecast-driven, look-ahead deployment** (build indexes *before* a predicted demand spike) extending NoisePage-style action scheduling *(frontier — verify)*; (b) RL / Monte-Carlo-tree-search planners over joint design actions amortizing build cost (UDO lineage); (c) **smoothed online learning / convex-body-chasing** applied to elastic resource and configuration changes; (d) transient-aware cost models that price the degradation window of an online index build. Groups: Pavlo/CMU, Trummer/Cornell, Krause/ETH (online convex optimization with switching costs), and competitive-analysis theorists (Bubeck, Sellke).

## 8. Future Work
- Competitive or regret bounds that explicitly charge transient-degradation cost, not just movement cost.
- Factored / hierarchical planners scaling to realistic design-decision dimensionality.
- Robust MPC with provable degradation under bounded forecast error.
- Anti-thrashing guarantees (no pathological build/drop oscillation) as a certified property.

## 9. Key References
- **[Foundational]** A. Borodin, N. Linial, M. Saks. *An Optimal On-Line Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[SOTA]** L. Ma, D. Van Aken, A. Hefny, G. Mezerhane, A. Pavlo, G. Gordon. *Query-based Workload Forecasting for Self-Driving Database Management Systems.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196908)
- **[Foundational]** S. Chaudhuri, V. Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN97.html)
- **[SOTA]** M. Sellke. *Chasing Convex Bodies Optimally.* SODA, 2020. — [arXiv](https://arxiv.org/abs/1905.11968)
- **[SOTA]** J. Wang, I. Trummer, D. Basu. *UDO: Universal Database Optimization using Reinforcement Learning.* PVLDB, 2021. — [arXiv](https://arxiv.org/abs/2104.01744)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)

## 10. Worked Example

A tuner faces a 3-tick horizon. The candidate index $I$ costs a one-time **build** of $c=20$ (units of lost throughput while building, paid the tick it is created) and yields per-tick **utility** $u=15$ once live. The forecast says the query that $I$ helps fires on ticks 2 and 3 only. Use $\gamma=1$.

**Plan A — build now (tick 1):** pay $-20$ at tick 1 (build, index not yet helping), then $+15$ at ticks 2 and 3.
$$V_A = -20 + 15 + 15 = +10.$$

**Plan B — myopic / never build:** $V_B = 0$ (no cost, no benefit).

**Plan C — build at tick 2 (greedy reaction once demand appears):** index is building during tick 2 so it does not help that tick; only tick 3 benefits.
$$V_C = 0 - 20 + 15 = -5.$$

So the optimal schedule is **build ahead at tick 1** ($V_A=10$), beating both the do-nothing baseline and the reactive build. This is the look-ahead-deployment intuition of §3/§7: the transient build window must be paid *before* the demand spike so the index is warm when load arrives. Had demand lasted only one tick, $V_A = -20+15 = -5 < 0$ and *not building* would win — the build cost fails to amortize, which is exactly the horizon/sequencing tradeoff at the core of the problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
