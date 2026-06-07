---
id: 21-graph-databases/adaptive-graph-reoptimization
title: "Adaptive runtime reoptimization for graph queries"
topic: 21-graph-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Adaptive runtime reoptimization for graph queries

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/adaptive-graph-reoptimization` · **Status:** open

## 1. Problem Statement
During evaluation of a graph pattern / path query, **cardinality estimates are frequently wrong** (graph data is skewed and correlated, and intermediate result sizes for cyclic patterns and RPQs are hard to predict). The problem: monitor actual intermediate cardinalities at runtime and **re-route** the remaining evaluation — change join order, switch between binary-join and worst-case-optimal (WCOJ) execution, repartition, or change a path-search frontier strategy — to recover from estimation errors, **without ever regressing below the cost of the best static plan** (a no-regret / competitive guarantee), and ideally approaching the cost achievable with perfect foresight.

Variants:
- **Optimization variant:** minimize total work; goal = competitive ratio vs the optimal static (or optimal dynamic) plan.
- **Decision/trigger variant:** decide *when* a re-plan is worth its overhead (a switching-cost / online-decision problem).
- **Plan-space variant:** what re-routing moves are sound mid-flight (order changes, operator switches, materialization) without recomputation or wrong results.
Status: **open** — adaptive techniques exist relationally, but principled, regret-bounded mid-query reoptimization for graph pattern/path queries is unsolved.

## 2. Mathematical Foundations
The estimation problem is grounded in **AGM** (intermediate-size bounds), degree/skew statistics, and the observation that q-error in early operators compounds multiplicatively downstream. The adaptivity problem is an **online algorithm**: choosing actions under revealed information, evaluated by **competitive ratio** $\sup_I \mathrm{ALG}(I)/\mathrm{OPT}(I)$, and is naturally cast as **regret minimization** / online learning (experts, bandits — choosing among join orders/operators as arms) or as **ski-rental–style switching** with switching cost $c$ (when to pay to re-plan). Eddies (Avnur–Hellerstein, SIGMOD 2000) model per-tuple routing as a learning problem with lottery/back-pressure scheduling.

For graph-specific structure, WCOJ's guarantee ($\tilde O(\mathrm{AGM})$ regardless of order) provides a **safety net** — switching to a generic-join over the remaining attributes bounds the worst case — which is the key lever for a no-regret design: the static-plan-floor can be enforced by falling back to a WCO sub-plan. Path-query adaptivity additionally draws on bidirectional / $A^*$ search frontier balancing.

## 3. State of the Art (SOTA)
- **Relational adaptive-SOTA:** Eddies and STAIRs (Avnur–Hellerstein 2000; Deshpande et al.); **mid-query reoptimization** (Kabra–DeWitt, SIGMOD 1998); **POP / re-optimization** (Markl et al., VLDB 2004); **Plan Bouquets / robust plans** (Dutt–Haritsa, SIGMOD 2014) that bound the *maximum sub-optimality* across the selectivity space; **SkinnerDB** (Trummer et al., SIGMOD 2019) — *regret-bounded* join ordering via reinforcement learning (UCT/Monte-Carlo tree search) with a proven bound vs the optimal join order in hindsight.
- **Graph-SOTA:** Graphflow/Kùzu adaptively mix binary joins and WCOJ ("hybrid" plans) chosen partly at runtime; **adaptive worst-case-optimal join** and factorized-execution work (Salihoglu, Olteanu groups); RPQ engines with adaptive bidirectional search. Learned cardinality estimators (e.g., GNN/Flow-based) feed re-planning. No widely adopted *regret-bounded* graph-specific reoptimizer yet.

## 4. Upper Bound
- SkinnerDB-style learning gives a **regret bound**: total time $\le$ (optimal-in-hindsight join-order time) $+ O(\cdot)$ exploration overhead, i.e., constant-competitive against the best static order up to learning regret (Trummer et al. 2019), in the tuple-routing/learning model.
- WCOJ fallback gives an *unconditional* $\tilde O(\mathrm{AGM}(Q))$ ceiling for the remaining sub-query, so a hybrid scheme can guarantee never exceeding AGM by more than the work already done — a worst-case safety bound.
- Plan-bouquet bounds the worst-case sub-optimality to the bouquet's geometric cover factor over the selectivity space (Dutt–Haritsa 2014).

## 5. Lower Bound
- Online lower bounds: any deterministic switching scheme with re-plan cost $c$ has competitive ratio $\ge 2$ in the worst case (ski-rental lower bound); bandit/expert regret is $\Omega(\sqrt{T\log K})$ for $K$ candidate plans over $T$ steps (information-theoretic).
- The underlying join-ordering problem is **NP-hard** (Ibaraki–Kameda; cross-products make even left-deep ordering hard), so optimal static planning — the baseline OPT — is itself intractable to compute, complicating "no-regret-vs-OPT" claims.
- Cardinality estimation cannot be made accurate in general: known **lower bounds on sketch/sample size** for join-size estimation, and the impossibility of bounded q-error from bounded-size synopses for adversarial correlated data.

## 6. The Gap
Relationally, regret-bounded reordering (SkinnerDB) and robust plans (bouquets) exist, but for **graph pattern + path queries** the gap is open: (a) no reoptimizer that is simultaneously regret-bounded *and* exploits WCOJ/factorization safety nets for cyclic patterns; (b) **path/RPQ** reoptimization (frontier re-routing, automaton-product reorder) has no competitive theory; (c) the **switching-cost model** for graph operators (cost of re-materializing partial traversals) is unquantified; (d) integrating *learned* estimators with provable no-regret guarantees rather than heuristic triggers. Closing it needs an online-algorithms treatment with the graph cost model and AGM-aware floors.

## 7. Current Research (as of June 2026)
Active directions: extending SkinnerDB-style regret-bounded execution to *graph* WCOJ plans and to factorized representations *(frontier — verify)*; reinforcement-learning and contextual-bandit query optimizers specialized to graph workloads (Trummer at Cornell; Salihoglu/Olteanu on hybrid WCOJ); adaptive RPQ/path evaluation with runtime frontier balancing in MillenniumDB/Kùzu *(frontier — verify)*; learned, *uncertainty-aware* cardinality estimators that emit confidence intervals to trigger principled re-plans *(frontier — verify)*. Robust-plan / plan-bouquet ideas are being revisited for the high-skew graph setting (Haritsa, IISc).

## 8. Future Work
- A competitive-ratio theory for mid-query graph reoptimization with explicit switching costs.
- Regret-bounded hybrid binary/WCOJ/factorized execution for cyclic patterns.
- Adaptive path/RPQ evaluation with provable guarantees.
- Tight integration of uncertainty-aware learned estimators as *triggers* with formal no-regret bounds.
- Reoptimization that is also provenance/incremental-maintenance friendly under updates.

## 9. Key References
- **[Foundational]** Avnur, Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335420)
- **[Foundational]** Kabra, DeWitt. *Efficient Mid-Query Re-Optimization of Sub-Optimal Query Execution Plans.* SIGMOD, 1998. — [DOI](https://doi.org/10.1145/276304.276315)
- **[SOTA]** Trummer, Wang, Maram, Moseley, Jo, Antonakakis. *SkinnerDB: Regret-Bounded Query Evaluation via Reinforcement Learning.* SIGMOD, 2019 (ACM TODS, 2021). — [arXiv](https://arxiv.org/abs/1901.05152)
- **[SOTA]** Dutt, Haritsa. *Plan Bouquets: Query Performance Robustness via Cost-Greedy Plan Selection.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588566) *(published as "Plan Bouquets: Query Processing without Selectivity Estimation")*
- **[SOTA]** Mhedhbi, Salihoglu. *Optimizing Subgraph Queries by Combining Binary and Worst-Case Optimal Joins.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1903.02076)
- **[Foundational]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

Consider the triangle query $T(a,b,c) \leftarrow E(a,b), E(b,c), E(a,c)$ on a graph where vertex $u$ is a hub with degree $10^6$ but most vertices have degree $\approx 10$. The optimizer, trusting a uniform-degree estimate, picks the left-deep binary-join order $E(a,b) \bowtie E(b,c)$ first, estimating the intermediate $|E\bowtie E|\approx |E|\cdot 10 = 10^7$.

At runtime the eddy/monitor observes that after binding $a=u$, the partial join has already produced $10^6 \cdot 10 = 10^7$ tuples from a *single* source binding — q-error blows up because $u$'s true degree was mis-estimated by $10^5\times$. A regret-bounded reoptimizer reacts: the remaining work is re-routed to a **worst-case-optimal** generic join over $\{a,b,c\}$, whose AGM ceiling is $|E|^{3/2}$. With $|E|\approx 10^6$, AGM $=10^9$, versus the binary plan's runaway $\gg 10^{10}$ on the skewed instance.

The switching decision is ski-rental: pay re-plan cost $c$ only once the observed surplus exceeds $c$, guaranteeing competitive ratio $\le 2$ against having switched optimally in hindsight, while the WCOJ fallback caps the worst case at $\tilde{O}(\mathrm{AGM})$.

---
*Part of the [DBMS Research catalog](../../README.md).*
