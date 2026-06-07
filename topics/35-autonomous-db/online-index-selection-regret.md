---
id: 35-autonomous-db/online-index-selection-regret
title: "Online Index Selection with Regret Bounds"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Online Index Selection with Regret Bounds

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/online-index-selection-regret` · **Status:** open

## 1. Problem Statement
Queries arrive in a stream $q_1, q_2, \dots, q_T$ drawn from a possibly **non-stationary** distribution. Before each query (or in epochs), the tuner chooses a configuration $S_t \subseteq \mathcal{I}$ of indexes to keep materialized, paying:
- **execution cost** $c_{S_t}(q_t)$,
- **transition (build/drop) cost** $\delta(S_{t-1}, S_t)$ — building an index is expensive and amortizes only over future queries,
- **storage cost** for holding $S_t$ subject to budget $B$.

The objective is to minimize total cost over the horizon. The performance metric is **regret** against a benchmark:
- *Static regret:* $R_T = \sum_t \text{cost}_t(S_t) - \min_{S^\*}\sum_t \text{cost}_t(S^\*)$ vs. the best fixed budget-feasible configuration.
- *Dynamic regret:* vs. the best *sequence* $S_1^\*,\dots,S_T^\*$ with a path-length / switching budget.

Variants: full-information (cost of all configs observable via what-if) vs. **bandit** (only the chosen config's realized cost is seen); decision (achieve $o(T)$ regret) vs. optimization (minimize the constant).

## 2. Mathematical Foundations
This is **online convex/combinatorial optimization with switching costs** — a *Metrical Task System* (MTS) / convex body chasing instance, since indexes form a metric over configurations with movement cost $\delta$.

Key machinery:
- **Online learning:** Hedge/Multiplicative-Weights gives $O(\sqrt{T \log N})$ static regret over $N$ experts; with $N = 2^{|\mathcal{I}|}$ configurations this is exponential, so structure (submodularity, matroid) must be exploited — cf. online submodular maximization (Streeter–Golovin), achieving $(1-1/e)$-regret.
- **Switching cost:** MTS lower bounds give competitive ratio $\Omega(\log n / \log\log n)$ on an $n$-point metric (Bartal–Bollobás–Mendel); the *Work Function Algorithm* is $O(\log n)$-competitive on HSTs.
- **Caching analogy:** keeping/evicting indexes under a size budget generalizes weighted caching / $k$-server, hence $\Omega(k)$ deterministic and $O(\log^2 k)$ randomized competitiveness bounds (Bansal–Buchbinder–Naor) are inherited templates.
- **Drift:** for dynamic regret, bounds scale with **path length** $P_T = \sum_t \lVert S_t^\* \ominus S_{t-1}^\*\rVert$ or number of distribution shifts.

No single existing result simultaneously handles submodular benefit, knapsack storage, *and* asymmetric build/drop switching costs — that combination is the open problem.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Online submodular maximization with bounded switching (Streeter–Golovin 2008; follow-ups on "online with budget") yields $(1-1/e)$-competitive against the best fixed set, but ignores asymmetric, amortizable build cost. Convex-body-chasing / smoothed online learning gives competitive guarantees only for relaxed (fractional) index configurations.

**Systems-SOTA:** Online/continuous physical tuning is heuristic — Bruno–Chaudhuri's *online physical design* (VLDB 2007), the COLT continuous tuner, and modern RL/bandit advisors (e.g., contextual-bandit and DDPG-based index tuners, ~2018–2024). These show empirical adaptivity but offer **no regret bound** that accounts for build cost. *(frontier — verify)*

## 4. Upper Bound
Best provable: a $(1 - 1/e)$-competitive guarantee against the best *fixed* feasible configuration in the full-information, switching-cost-bounded regime via online greedy/Hedge over a submodular benefit oracle, with additive $O(\sqrt{T})$ regret terms when costs are bounded. For the fractional relaxation, $O(\log T)$-type dynamic-regret bounds follow from online-mirror-descent with movement penalties. Integral configurations with realistic asymmetric build/drop costs have **no published sublinear dynamic-regret bound**.

## 5. Lower Bound
- **Switching alone** forces an MTS lower bound: $\Omega(\log |\mathcal{I}|)$ (randomized) / linear (deterministic) competitive ratio on the configuration metric.
- **Bandit feedback** imposes $\Omega(\sqrt{T \cdot |\mathcal{I}|})$ regret (adversarial multi-armed bandit lower bound) since only the realized configuration's cost is observed.
- **Non-stationarity** without a drift budget makes *dynamic* regret linear ($\Omega(T)$): no algorithm beats an adversary that flips the best configuration every step.

## 6. The Gap
**Open.** Upper bounds exist only for (a) the fixed-comparator/submodular case ignoring amortized build cost, or (b) fractional relaxations. Lower bounds (MTS, bandit, drift) are general but not matched by any integral, build-cost-aware algorithm. The crux: build cost is *asymmetric and amortizable*, unlike symmetric MTS movement, so neither caching nor MTS bounds apply tightly. Closing the gap needs an algorithm whose regret is parameterized jointly by storage budget $B$, drift $P_T$, and build/run cost ratio.

## 7. Current Research (as of June 2026)
- Bandit and contextual-bandit index advisors with workload-shift detection; combining change-point detection with regret analysis. *(frontier — verify)*
- Reinforcement-learning tuners (e.g., DDPG/PPO index agents) being retrofitted with safety/regret guarantees and rollback. *(frontier — verify)*
- Cross-pollination from *smoothed online learning* and *online convex optimization with memory* (Anava, Hazan) toward DB tuning. Groups: Microsoft GSL, TU Darmstadt, Hasso Plattner Institute, and the learned-systems community at MIT/CMU. *(frontier — verify)*

## 8. Future Work
- A regret bound parameterized by $(B, P_T, \text{build/run ratio})$ for *integral* configurations.
- Bandit-to-full-information reduction using cheap what-if estimates as side information.
- Robustness/consistency tradeoffs (learning-augmented online algorithms with optimizer predictions).
- Joint online selection of indexes *and* views (couples with *joint-physical-design*).

## 9. Key References
- **[Foundational]** N. Bruno, S. Chaudhuri. *An Online Approach to Physical Design Tuning.* ICDE, 2007. — [DBLP](https://dblp.org/rec/conf/icde/BrunoC07.html)
- **[Foundational]** M. Streeter, D. Golovin. *An Online Algorithm for Maximizing Submodular Functions.* NeurIPS, 2008. — [NeurIPS](https://proceedings.neurips.cc/paper/2008/hash/5751ec3e9a4feab575962e78e006250d-Abstract.html)
- **[Foundational]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge University Press, 1998. — [DBLP](https://dblp.org/rec/books/daglib/0097598.html)
- **[SOTA]** N. Bansal, N. Buchbinder, J. Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[SOTA]** A. Sharma, et al. *Reinforcement Learning for Index Tuning (NoDBA / DRLinda lineage).* ~2018–2021. — [DBLP search](https://dblp.org/search?q=NoDBA%20reinforcement%20learning%20index)
- **[Survey]** E. Hazan. *Introduction to Online Convex Optimization.* now Publishers / MIT Press, 2nd ed., 2022. — [MIT Press](https://mitpress.mit.edu/9780262046985/introduction-to-online-convex-optimization/)

## 10. Worked Example

Consider one candidate index $I$, build cost $\delta = 100$ (paid once when we go from $\emptyset$ to $\{I\}$), and a stream of $T=10$ queries. Each query costs $10$ without the index and $2$ with it (benefit $8$/query). Storage budget admits $I$.

The best *fixed* configuration in hindsight: building $I$ at $t=1$ costs $100 + 10\cdot 2 = 120$; never building costs $10\cdot 10 = 100$. So the offline optimum is **never build** at cost $100$ — because $\delta=100$ is not amortized over only $10$ queries ($8\cdot 10 = 80 < 100$).

Now suppose the stream is non-stationary: $I$ helps only the first $5$ queries, then the workload shifts and $I$ becomes useless (cost $10$ with or without it). A naive "build once benefit looks positive" tuner that builds at $t=1$ pays $100 + (2\!\cdot\!5) + (10\!\cdot\!5) = 160$, versus optimum $100$ — incurring **regret $60$**, almost all of it the unamortized build cost.

The lesson the algorithm must encode: defer building until the *expected future benefit* $\sum 8 > \delta = 100$, i.e. at least $13$ remaining helped queries. This break-even threshold is exactly the asymmetric, amortizable build-cost term that standard symmetric-MTS switching bounds fail to capture.

---
*Part of the [DBMS Research catalog](../../README.md).*
