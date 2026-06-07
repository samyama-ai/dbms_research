---
id: 34-schema-design-normalization/materialized-view-index-codesign
title: "Materialized View and Index Co-Selection"
topic: 34-schema-design-normalization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Materialized View and Index Co-Selection

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/materialized-view-index-codesign` · **Status:** partially-solved

## 1. Problem Statement
Given a database schema, a workload $W$ of queries (with frequencies/weights), and a **storage budget** $B$, jointly select a set of **materialized views** $V$, **indexes** $I$ (including indexes built *on* the chosen views), and optionally **partitions**, that minimizes total expected query cost while satisfying $\sum \text{size}(\cdot)\le B$ and update-maintenance constraints. The objective must account for **interactions**: an index can be useful only given a view; two views can subsume each other; building one structure changes the optimizer's plan (and thus the marginal benefit) of another.

- **Decision variant:** Does a configuration of total size $\le B$ achieve workload cost $\le \tau$?
- **Optimization variant:** maximize benefit (cost reduction) under the budget — a budgeted combinatorial selection.

## 2. Mathematical Foundations
Let $S$ be the universe of candidate structures (views, indexes, partitions). For configuration $X\subseteq S$, the workload benefit is $g(X)=C(\emptyset)-C(X)$ where $C(X)=\sum_{q}f_q\,\min_{\text{plans}}\text{cost}(q,X)$. The problem is **budgeted maximization** of $g$ subject to $\sum_{s\in X}c_s\le B$.

A central structural property: in many cost models $g$ is **monotone** but only **approximately submodular** — the "min over plans" introduces *negative* interactions (substitutes) and the index-on-view dependency introduces *complementarities*, both violating pure submodularity. When $g$ is submodular, the greedy algorithm gives a $(1-1/e)$ approximation for the budgeted/knapsack-constrained case (Sviridenko). Deviations are quantified via **submodularity ratio** and **curvature**, yielding degraded but still bounded greedy guarantees. The candidate generation step relies on the optimizer's "**what-if**" interface and on syntactic view/index derivation from query structure (the AND-OR / view-matching lattice).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** $(1-1/e)$-approximation for submodular budgeted selection (Nemhauser–Wolsey–Fisher; Sviridenko 2004 for knapsack); approximate-submodular extensions bound greedy by the submodularity ratio.
- **Systems-SOTA:** Microsoft **AutoAdmin / Database Tuning Advisor** (Chaudhuri & Narasayya) pioneered integrated index+view+partition selection with what-if analysis; **DB2 Design Advisor** (Zilio et al., VLDB 2004) co-selects indexes, MQTs (views), partitioning, and MDC. Modern cloud advisors (Azure SQL Database automatic tuning, Amazon Redshift Advisor, Oracle SQL Tuning/Access Advisor) ship co-selection in production. Recent **learned/Bandit** approaches (e.g., DBA bandits, budget-aware RL tuners) treat selection as online learning.

This is "partially-solved": robust systems and provable approximations exist for the submodular regime, but interaction-aware optimality with views-on-indexes complementarities and update costs remains heuristic.

## 4. Upper Bound
For monotone submodular benefit with a knapsack (storage) constraint, **greedy / partial-enumeration greedy** gives a $(1-1/e)$-approximation in polynomial time (Sviridenko 2004), and lazy-greedy (Minoux) makes it scalable. For the approximately-submodular real objective, greedy retains a $(1-e^{-\gamma})$-type guarantee where $\gamma$ is the submodularity ratio. Systems achieve strong empirical results via candidate pruning + what-if cost calls; the dominant cost is the number of optimizer invocations, mitigated by INUM-style plan caching and configuration enumeration.

## 5. Lower Bound
The selection problem is **NP-hard** (it generalizes the index-selection problem, which is NP-hard, and embeds **maximum coverage / budgeted maximum coverage**, NP-hard and inapproximable beyond $(1-1/e)$ unless P=NP — Feige's threshold). Thus no polynomial algorithm beats $1-1/e$ for the submodular case under standard assumptions. With non-submodular interactions (complementary structures), the problem can be as hard as general budgeted maximization, for which no constant-factor guarantee is known. View matching/answering-queries-using-views adds further hardness (containment of conjunctive queries is NP-complete).

## 6. The Gap
For the **submodular** regime the gap is essentially **closed**: $1-1/e$ achievable and $1-1/e$ inapproximability matches. The genuinely open part is the **interaction-aware** regime — complementarities (index-on-view), update/maintenance costs, and optimizer plan-flip non-monotonicities break submodularity, and no tight approximation is known there. Closing it requires either structural conditions under which the real benefit stays (approximately) submodular, or new algorithms with guarantees for the complementary case.

## 7. Current Research (as of June 2026)
- Learned cost models replacing what-if calls to make co-selection cheaper and interaction-aware *(frontier — verify)*.
- RL / contextual-bandit tuners that co-select indexes and views online with safety constraints *(frontier — verify)*.
- Interaction-aware (non-submodular) optimization with curvature/submodularity-ratio guarantees applied to MV+index design *(frontier — verify)*.
- Groups: Chaudhuri & Narasayya (Microsoft Research), Pavlo (CMU, self-driving), Kraska (MIT, learned components), Binnig (TU Darmstadt).

## 8. Future Work
- Tight approximations for complementary (non-submodular) structure selection.
- Update-cost-aware budgeted co-design with maintenance under churn.
- Online co-selection with regret bounds and rollback safety.
- Co-design extended to compression, sort orders, and storage tiers.

## 9. Key References
- **[Foundational]** S. Chaudhuri, V. Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN97.html)
- **[SOTA]** D. Zilio et al. *DB2 Design Advisor: Integrated Automatic Physical Database Design.* VLDB, 2004. — [ACM](https://dl.acm.org/doi/10.5555/1316689.1316783)
- **[Foundational]** G. Nemhauser, L. Wolsey, M. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions—I.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[Foundational]** M. Sviridenko. *A Note on Maximizing a Submodular Set Function Subject to a Knapsack Constraint.* Operations Research Letters, 2004. — [DOI](https://doi.org/10.1016/S0167-6377(03)00062-2)
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)
- **[SOTA]** S. Agrawal, S. Chaudhuri, V. Narasayya. *Automated Selection of Materialized Views and Indexes for SQL Databases.* VLDB, 2000. — [DBLP](https://dblp.org/rec/conf/vldb/AgrawalCN00.html)

## 10. Worked Example

Budget $B=10$. Candidates with (size, standalone benefit): index $a=(4,40)$, index $b=(5,50)$, view $c=(6,72)$. Greedy under the knapsack uses benefit/cost density: $a:10$, $b:10$, $c:12$. Pick $c$ first (density 12, uses 6, leaves 4). Next, among $\{a,b\}$ only $a$ fits the remaining 4. Final greedy set $\{c,a\}$: size $10$, benefit $72+40=112$.

Compare the optimum: $\{b,a\}$ has size $9\le10$ and benefit $90$; $\{c,a\}=112$; $\{c\}$ alone $=72$. So OPT $=112=$ greedy here. The Sviridenko guarantee says greedy-with-enumeration is $\ge(1-1/e)\cdot\text{OPT}\approx0.632\cdot112\approx71$, comfortably met.

Now add a *complementarity*: an index $d=(2,5)$ that, built *on view* $c$, raises $c$'s benefit by $30$ (worthless without $c$). The benefit function is no longer submodular — the marginal gain of $d$ rises after $c$ is chosen, violating diminishing returns. Greedy, evaluating $d$ early when $c$ is absent, sees marginal $5$ at density $2.5$ and skips it, missing the $+30$ synergy. This is exactly the interaction-aware regime where the $(1-1/e)$ bound no longer applies.

---
*Part of the [DBMS Research catalog](../../README.md).*
