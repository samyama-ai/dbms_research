# Multi-way stream join ordering at runtime

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/multiway-stream-join-ordering` · **Status:** empirically-open

## 1. Problem Statement
Given a multi-way join $R_1 \bowtie R_2 \bowtie \cdots \bowtie R_n$ over streams whose arrival rates, value distributions, and pairwise selectivities **drift over time**, continuously choose the join *order* (for a binary-tree pipeline) or the *probe sequence / variable order* (for a worst-case-optimal multi-way operator) that minimizes intermediate-state size and per-tuple processing cost. Because the optimal plan changes as statistics shift, the problem is not "pick a plan once" but **online re-optimization**: when to switch plans, how to migrate intermediate state across plans without losing or duplicating results, and how to bound the regret against a clairvoyant optimizer.

Decision variant: does there exist a switching schedule whose total cost is within factor $\rho$ of the best fixed-per-interval plan? Optimization variant: minimize cumulative state·time (or latency) over the run. The "empirically-open" status reflects that strong heuristics exist and work well in practice, but no system provably tracks the optimal order under adversarial drift.

## 2. Mathematical Foundations
For a fixed instant, the **AGM bound** gives the worst-case output size of a multi-way join via the fractional edge cover number $\rho^*$ of the query hypergraph: $|J| \le \prod_e |R_e|^{x_e}$ for an optimal fractional cover $\{x_e\}$. **Worst-case-optimal join (WCOJ)** algorithms (NPRR / Leapfrog Triejoin / Generic-Join) run in $\tilde O(\mathrm{AGM})$ time, avoiding the polynomially-larger intermediate results that binary plans can produce — relevant because a streaming multi-way join must control intermediate *state*, not just final size.

Runtime re-ordering is an **online algorithm / metrical task system** problem: the planner is in a "state" (current order); switching incurs a migration cost $d(\pi,\pi')$ (a metric over plans), and at each step pays the chosen plan's instantaneous cost. This is the **MTS / online plan-switching** model, where competitiveness is bounded below by the diameter of the plan metric. Adaptive operators (Eddies) instead route each tuple by an online policy, replacing global ordering with per-tuple **bandit-style routing**.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** WCOJ algorithms (Ngo–Porat–Ré–Rudra 2012; Leapfrog Triejoin, Veldhuizen 2014) bound multi-way join cost; their streaming/incremental versions (e.g. dynamic Yannakakis, **DBToaster**, and recent IVM-for-WCOJ work) give state-aware maintenance.
- **Systems-SOTA:** **Eddies** (Avnur & Hellerstein, SIGMOD 2000) — continuous per-tuple routing, the canonical adaptive multi-way operator. **CACQ / TelegraphCQ** extended Eddies to shared continuous queries. Flink/Spark currently lack runtime join re-ordering; research prototypes and **AJU (adaptive join)** schemes plus learned-cardinality-driven re-optimization fill the gap.

## 4. Upper Bound
A WCOJ multi-way operator processes a window in $\tilde O(\mathrm{AGM})$ time with state bounded by the live relations rather than intermediate products (RAM model), strictly dominating worst-case binary plans. For online switching, an MTS-style policy is $O(\mathrm{poly}(n))$-competitive against the best fixed plan when migration cost is metric; Eddies give no worst-case guarantee but empirically track shifting selectivities with negligible per-tuple overhead. Lottery/learning-based routing converges to the best fixed route under stationarity.

## 5. Lower Bound
Even the *static* optimal join-order problem is **NP-hard** for general (bushy, cross-product-allowed) plans (reduction via optimal-order = hard combinatorial selection). Online plan switching inherits an $\Omega(\mathrm{diam})$ competitive lower bound from metrical task systems: no online re-optimizer can beat the plan-metric diameter against an adversary that flips the optimal order. Binary-plan operators provably incur $\Omega(\mathrm{AGM}^{?})$ blow-up relative to WCOJ on cyclic queries — a separation, not just a constant.

## 6. The Gap
The static and worst-case-size questions are **closed** (NP-hard offline; AGM/WCOJ tight). The open, *empirical* gap is the dynamic one: there is no policy that provably **tracks** the time-varying optimal order with bounded regret while paying realistic migration costs, and no consensus on when WCOJ vs. binary pipelines win under streaming state pressure. Closing it needs (a) tight regret bounds for online plan switching with state-migration cost, and (b) accurate, cheap online selectivity/rate estimation to drive switches.

## 7. Current Research (as of June 2026)
Threads: learned and reinforcement-learning query re-optimization adapted to streaming (continuous Bandit/Eddy routing) *(frontier — verify)*; incremental WCOJ and dynamic Yannakakis maintenance for cyclic streaming joins; cardinality/rate estimators feeding runtime re-ordering. Groups: Oxford (Olteanu — factorized/IVM, dynamic Yannakakis), Washington/RelationalAI (WCOJ, IVM), Berkeley (Eddies lineage), TU Munich (adaptive optimization).

## 8. Future Work
- Provable regret bounds for online join re-ordering with metric migration cost.
- Unified cost model deciding WCOJ vs. binary plans under streaming state budgets.
- Cheap, drift-robust online selectivity estimation driving switch decisions.
- Correct, low-latency state hand-off between plans (links to elastic state migration).

## 9. Key References
- **[Foundational]** R. Avnur, J. M. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335420)
- **[Foundational]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 (JACM, 2018). — [arXiv](https://arxiv.org/abs/1203.1952)
- **[SOTA]** T. L. Veldhuizen. *Triejoin: A Simple, Worst-Case Optimal Join Algorithm (Leapfrog Triejoin).* ICDT, 2014. — [arXiv](https://arxiv.org/abs/1210.0481)
- **[SOTA]** M. Idris, M. Ugarte, S. Vansummeren. *The Dynamic Yannakakis Algorithm: Compact and Efficient Query Processing under Updates.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064027)
- **[Foundational]** S. Babu, P. Bizarro, D. DeWitt. *Proactive Re-optimization.* SIGMOD, 2005. — [DOI](https://doi.org/10.1145/1066157.1066171)

## 10. Worked Example

Consider the triangle join $R(a,b) \bowtie S(b,c) \bowtie T(a,c)$ with $|R|=|S|=|T|=N$.

**Binary plan blow-up.** Any binary order, say $(R \bowtie S) \bowtie T$, materializes $R \bowtie S$ first. With every $b$ value shared, $|R \bowtie S|$ can reach $N^2$ intermediate tuples — even though the final triangle output is at most $N^{3/2}$. In a stream, that $N^2$ intermediate state is the live buffer the operator must hold, which is the killer.

**AGM / WCOJ.** The fractional edge cover of the triangle gives $x_e = 1/2$ on each of the 3 edges, so the AGM bound is $\prod_e |R_e|^{1/2} = N^{1/2}\cdot N^{1/2}\cdot N^{1/2} = N^{3/2}$. A worst-case-optimal join (Leapfrog Triejoin / Generic-Join) runs in $\tilde O(N^{3/2})$ with state bounded by the base relations — no $N^2$ intermediate.

**Why runtime re-ordering.** Now suppose $S$'s arrival rate spikes so its live window grows to $10N$ while $R,T$ stay at $N$. The cheapest probe variable order shifts (start from the now-largest relation last). Switching the variable order mid-run incurs a migration cost $d(\pi,\pi')$ to rebuild the trie index; the online question is whether the saved per-tuple cost over the spike's duration exceeds that one-time $d$ — exactly the metrical-task-system tradeoff with diameter-bounded competitiveness.

---
*Part of the [DBMS Research catalog](../../README.md).*
