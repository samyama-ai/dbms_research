---
id: 27-learned-db-components/instance-optimal-query-plans
title: "Instance-Optimal Query Plans"
topic: 27-learned-db-components
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Instance-Optimal Query Plans

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/instance-optimal-query-plans` · **Status:** open

## 1. Problem Statement

A query optimizer chooses a plan using **estimated** statistics; when estimates are
wrong, the chosen plan can be arbitrarily worse than the best plan for the **actual
data instance**. The problem: design a plan-selection procedure that is provably
**competitive with the best plan for the realized instance** $D$, not the estimated
one — i.e., bounded *suboptimality* (regret) regardless of estimation error.

- **Decision variant:** does a plan with cost $\le\alpha\cdot\mathrm{OPT}(D)$ exist /
  can it be selected within the optimizer's enumeration class?
- **Optimization variant:** minimize competitive ratio
  $\sup_D \mathrm{cost}(\text{chosen},D)/\mathrm{OPT}(D)$, possibly via adaptive
  (run-time) re-optimization.
- **Online/adaptive variant:** route/re-route execution as true cardinalities are
  observed mid-query (eddies, adaptive joins).

"Solving" means a guarantee on the *outcome* (runtime), decoupled from the accuracy of
any single cardinality estimate.

## 2. Mathematical Foundations

- **Worst-case-optimal joins (WCOJ):** algorithms whose runtime is
  $\tilde O(\mathrm{AGM}(q))$ — within a polylog factor of the **AGM bound**
  $\prod_e|R_e|^{x_e}$ — guarantee optimality *with respect to worst-case output size*
  regardless of join order (Ngo–Porat–Ré–Rudra, *Worst-case Optimal Join Algorithms*,
  PODS 2012). This sidesteps cardinality estimation entirely for a single join.
- **Adaptive / instance optimality:** beyond worst case, runtime can be bounded by the
  *certificate complexity* of the instance — minimal proof size of the output
  (instance-optimal set intersection / Minesweeper, Ngo et al.).
- **Robust optimization & parametric query optimization (PQO):** treat selectivities
  as unknown in a region; choose the plan minimizing maximum regret over that region,
  using the *plan diagram* / parametric optimality structure.
- **Competitive analysis:** mid-query re-optimization is online decision-making; bound
  total cost against the offline-optimal plan for the observed instance.

## 3. State of the Art (SOTA)

- **Theory SOTA:** **Worst-case optimal joins** (NPRR, PODS 2012; LeapFrog Triejoin,
  Veldhuizen, ICDT 2014) and **Minesweeper / instance-optimal joins** (Ngo et al.,
  PODS 2014) give the strongest guarantees decoupled from estimates — but only for
  (multiway) joins, not full plans with aggregation/selection ordering.
- **Systems SOTA:** **Adaptive query processing** — eddies (Avnur–Hellerstein, SIGMOD
  2000), mid-query re-optimization (Kabra–DeWitt 1998; **POP** Markl et al., VLDB
  2004), and SkinnerDB (Trummer et al., SIGMOD 2019) which uses **reinforcement
  learning with regret bounds** to choose join orders adaptively and is provably
  near-optimal in its execution model — the closest practical instance-optimal planner.

## 4. Upper Bound

For a single multiway join, WCOJ algorithms run in $\tilde O(\mathrm{AGM}(q))$,
matching the worst-case output-size optimum (**RAM model**); LeapFrog Triejoin
achieves this with a single variable order. SkinnerDB's adaptive join-order learning
attains runtime within a constant factor of the *best fixed* join order in hindsight,
with **regret bounds** from its UCT/regret-minimization execution model. PQO can
precompute a plan set so that, for any selectivity point, a plan within ratio
$1+\varepsilon$ of optimal is available.

## 5. Lower Bound

No estimate-free planner can beat the **AGM bound** for joins in general — it is a
tight information-theoretic limit on output size and hence runtime for any algorithm
that must produce the join. For full plans, choosing the optimal join order is
**NP-hard** (Ibaraki–Kameda; cross-product-free bushy ordering), so polynomial-time
instance-optimality across all plans is unattainable unless P = NP. Adaptive routing
faces **online lower bounds**: any algorithm that commits before observing
cardinalities can be forced to ratio $\Omega(N)$ on adversarial instances.

## 6. The Gap

Genuinely **open** beyond single joins. WCOJ closes the gap for one multiway join
(matching upper/lower bounds), and SkinnerDB gives outcome-level regret guarantees in
a restricted execution model, but there is **no** general theory giving a competitive
ratio for *full* plans (selections + multiway joins + aggregation) against the best
plan for the realized instance. The gap is between estimate-free guarantees that exist
for join sub-problems and the absence of such guarantees for complete query plans.
Closing it likely requires composing WCOJ-style certificates with adaptive re-
optimization and a regret theory over the full plan space.

## 7. Current Research (as of June 2026)

- Learned/adaptive optimizers with safety nets: **Bao** (SIGMOD 2021) and
  **Balsa/LOGER**-style RL planners aiming for bounded regret vs. the native optimizer
  *(frontier — verify)*.
- Bridging worst-case-optimal joins into mainstream cost-based optimizers (free-join /
  hybrid WCOJ, Wang et al.) so guarantees survive in full plans *(frontier — verify)*.
- Robust/parametric optimization revival: choosing plans by minimax regret over an
  uncertainty set derived from learned-CE confidence intervals.

## 8. Future Work

- A competitive-ratio theory for full plans against the instance-optimal plan.
- Re-optimization triggers with provable end-to-end runtime regret bounds.
- Composing certificate/instance-optimal joins with aggregation and grouping.

## 9. Key References

- **[Foundational]** H. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS 2012 / J. ACM 2018. — [arXiv](https://arxiv.org/abs/1203.1952) — [DOI](https://doi.org/10.1145/3180143)
- **[Foundational]** R. Avnur, J. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD 2000. — [DOI](https://doi.org/10.1145/342009.335420) — [DBLP](https://dblp.org/rec/conf/sigmod/AvnurH00.html)
- **[SOTA]** I. Trummer et al. *SkinnerDB: Regret-Bounded Query Evaluation via Reinforcement Learning.* SIGMOD 2019. — [arXiv](https://arxiv.org/abs/1901.05152) — [DOI](https://doi.org/10.1145/3299869.3300088)
- **[SOTA]** H. Ngo, D. Nguyen, C. Ré, A. Rudra. *Beyond Worst-Case Analysis for Joins with Minesweeper.* PODS 2014. — [arXiv](https://arxiv.org/abs/1302.0914) — [DOI](https://doi.org/10.1145/2594538.2594547)
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)

## 10. Worked Example

Consider the triangle query $q = R(a,b) \bowtie S(b,c) \bowtie T(a,c)$ with $|R| = |S| = |T| = N$. The **AGM bound** uses fractional edge cover $\mathbf{x}$ minimizing $\prod_e |R_e|^{x_e}$. Assigning $x_e = \tfrac12$ to each of the three edges is a valid cover (every vertex $a,b,c$ is covered by edges summing to $\ge 1$), giving output bound $N^{1/2}\cdot N^{1/2}\cdot N^{1/2} = N^{3/2}$.

A **binary-join** plan, e.g. $(R \bowtie S) \bowtie T$, can materialize an intermediate $R \bowtie S$ of size up to $N^2$ even when the final answer has only $O(N^{3/2})$ tuples — so for $N = 10^6$ it touches $10^{12}$ rows vs. the $10^9$ truly necessary. A bad cardinality estimate that picks this order is catastrophic.

A **WCOJ** algorithm (LeapFrog Triejoin) runs in $\tilde O(N^{3/2})$ regardless of join order, *independent of any selectivity estimate* — matching the AGM lower bound. This is exactly the estimate-free, instance-decoupled guarantee the problem seeks, but it holds only for the single multiway join; extending it to full plans with aggregation remains open.

---
*Part of the [DBMS Research catalog](../../README.md).*
