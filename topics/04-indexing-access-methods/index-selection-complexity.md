# Self-tuning index selection complexity

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/index-selection-complexity` · **Status:** open

## 1. Problem Statement
The **index selection problem (ISP)**: given a database, a query workload $W=\{(q_j, f_j)\}$ (queries with frequencies), a set of *candidate* indexes $\mathcal{C}$, a cost function $\mathrm{cost}(q, S)$ giving the optimizer's estimated cost of $q$ under index configuration $S\subseteq\mathcal{C}$, and a **space budget** $B$, choose $S$ minimizing total workload cost $\sum_j f_j \cdot \mathrm{cost}(q_j, S)$ subject to $\sum_{I\in S}\mathrm{size}(I)\le B$.

- **Optimization variant:** minimize workload cost under budget (above).
- **Decision variant:** is there $S$ with $\mathrm{size}(S)\le B$ and total cost $\le K$?
- **Counting/online variants:** count optimal configs; or choose indexes online under shifting workloads with regret guarantees. Includes materialized views, partitioning, and "index interactions" (the benefit of one index depends on which others are present).

## 2. Mathematical Foundations
ISP generalizes classical NP-hard problems. The benefit of adding indexes is often modeled as **set-function maximization under a knapsack/cardinality constraint**. If $\mathrm{benefit}(S) = \mathrm{cost}(W,\emptyset) - \mathrm{cost}(W,S)$ were **monotone submodular**, the greedy algorithm would give a $(1-1/e)$ approximation (Nemhauser–Wolsey–Fisher) and $(1-1/e)$ under a knapsack budget (Sviridenko). But **index interactions** violate submodularity: two indexes can be complementary (index-only plans, merge joins) so benefit is *super*modular in places, breaking the guarantee. Formally ISP embeds **Weighted Set Cover / Maximum Coverage** (each index "covers" the queries it accelerates) and **0/1 Knapsack** (budget), both NP-hard; the cost oracle ($\mathrm{cost}(q,S)$) is itself the optimizer, often non-monotone and only available as a black box ("what-if" calls). Approximability is studied relative to oracle complexity (number of what-if calls).

## 3. State of the Art (SOTA)
- **Foundational systems:** AutoAdmin (Chaudhuri & Narasayya, VLDB 1997) — the index/what-if framework underpinning Microsoft's Database Tuning Advisor; DB2 Index Advisor; Oracle SQL Access Advisor.
- **Theory:** ISP is long known NP-hard; greedy/relaxation heuristics with restricted submodular models give partial guarantees.
- **Modern systems-SOTA:** **Dexter** (Postgres), **DTA/Anytime** algorithms, and **learned / RL-based tuners** — DBA bandits, **SmartIX**, and reinforcement-learning index advisors; cloud auto-indexing in **Azure SQL Database** (automatic tuning) and **AWS**. **DTA "Anytime"** (Chaudhuri–Narasayya) gives a high-quality heuristic with progressive refinement.

## 4. Upper Bound
No constant-factor approximation is known for the general problem because benefit is non-submodular. Under the **restricted assumption** that benefit is monotone submodular (e.g., ignoring index interactions, "atomic" configurations), greedy gives $(1-1/e)$ under cardinality (NWF 1978) and $(1-1/e)$ under the knapsack/space budget (Sviridenko 2004), using $O(|\mathcal{C}|^2)$ oracle calls. In practice DTA/AutoAdmin use bounded what-if enumeration with no worst-case ratio but strong empirical quality. Model: black-box optimizer-cost oracle.

## 5. Lower Bound
ISP is **NP-hard** (and the decision version NP-complete) by reduction from **Weighted Set Cover / Knapsack**; many formulations are also **NP-hard to approximate**: maximum-coverage is hard to approximate better than $1-1/e$ (Feige 1998) unless P=NP, so the greedy submodular ratio is *optimal* for the coverage-style relaxation. With index interactions the benefit function is non-submodular, and general non-monotone / super-modular maximization has no constant-factor approximation; the problem also inherits Set-Cover's $\Theta(\ln n)$ inapproximability in cover formulations. Online variants face worst-case competitive lower bounds (adversarial workloads).

## 6. The Gap
The gap is between (a) NP-hardness + $(1-1/e)$/$\ln n$ inapproximability under *simplified submodular/coverage* models, and (b) the *true* problem with index interactions, a non-monotone non-submodular black-box oracle, and an unbounded candidate space, for which **no approximation guarantee exists at all**. It is open whether any structural restriction matching real optimizers (e.g., bounded interaction degree) admits a provable constant-factor approximation, and what the right oracle-complexity lower bounds are. The problem is genuinely **open** at the level of guarantees, even though heuristics work well empirically.

## 7. Current Research (as of June 2026)
Active directions: **learned/RL and bandit** index tuners with formal regret bounds for the *online* problem; bounding the *interaction degree* of indexes to recover approximation guarantees; **budget-aware** and **HTAP/columnar** index selection; and joint selection of indexes + materialized views + partitioning. Groups/people: Surajit Chaudhuri & Vivek Narasayya (Microsoft Research, AutoAdmin/DTA), Carsten Binnig / Tim Kraska (learned DBA), Andy Pavlo (CMU, self-driving DBs / OtterTune lineage), and cloud auto-tuning teams. *(frontier — verify)* recent claims of provable-regret RL index selection and of approximation algorithms under bounded-interaction assumptions.

## 8. Future Work
- Approximation algorithms under realistic, interaction-aware cost models (bounded interaction degree).
- Tight oracle-complexity (what-if call) lower bounds for budgeted selection.
- Online/streaming index selection with provable regret under workload drift; safe automatic deployment.

## 9. Key References
- **[Foundational]** Surajit Chaudhuri, Vivek Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB, 1997.
- **[Foundational]** George L. Nemhauser, Laurence A. Wolsey, Marshall L. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978.
- **[Foundational]** Uriel Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998.
- **[SOTA]** Maxim Sviridenko. *A Note on Maximizing a Submodular Set Function Subject to a Knapsack Constraint.* Operations Research Letters, 2004.
- **[Survey]** Surajit Chaudhuri, Vivek Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007.
- **[SOTA]** Hai Lan, Zhifeng Bao, Yuwei Peng. *A Survey on Advancing the DBMS Query Optimizer / Learned Index Selection.* (learned index-selection survey), 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
