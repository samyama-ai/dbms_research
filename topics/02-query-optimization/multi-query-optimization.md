---
id: 02-query-optimization/multi-query-optimization
title: "Multi-query optimization shared-subexpression search"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Multi-query optimization shared-subexpression search

> **Topic:** Query Optimization · **ID:** `02-query-optimization/multi-query-optimization` · **Status:** open

## 1. Problem Statement

Given a *batch* of queries $Q_1,\dots,Q_m$ (or one query with repeated subexpressions), **multi-query optimization (MQO)** seeks a global execution strategy that exploits **common subexpressions** (CSEs) — subqueries computed once and reused — to minimize total cost, instead of optimizing each query independently.

Each query $Q_i$ has multiple alternative plans, each a tree/DAG of operators; some operators across plans compute the *same* logical subexpression (possibly modulo subsumption: a more selective scan can serve a less selective one). The optimizer must jointly choose, for each query, a plan *and* the set of subexpressions to materialize/share.

Variants:
- **Decision variant:** is there a global plan of total cost $\le K$?
- **Optimization variant:** minimize $\sum_i \text{cost}(P_i) + \sum_{e \in M}\text{matCost}(e) - \text{savings}(M)$ over plan choices and materialized set $M$.
- **Scheduling variant:** order shared subexpression evaluation respecting producer→consumer dependencies, possibly under a materialization/memory budget.
- **Counting variant:** number of distinct shareable subexpressions across the AND/OR plan DAG.

## 2. Mathematical Foundations

The search space is the **AND/OR DAG** (a.k.a. *expanded* plan graph): AND-nodes are operators (need all inputs), OR-nodes are equivalence classes (choose one alternative). Sharing turns plan *trees* into *DAGs*. Choosing a minimum-cost sub-DAG that covers all query roots while accounting for shared-node cost-once semantics is a **Directed Steiner / DAG-covering** problem.

The materialization/sharing decision is a **set-cover-like** problem: subexpression $e$ benefits a set of consuming plans; selecting which to materialize under interactions (a materialization changes which plan is cheapest, which changes which subexpressions are needed) makes the objective **non-submodular in general** but often **monotone**; benefit functions are frequently submodular when plan choices are fixed, enabling $(1-1/e)$ greedy bounds in restricted settings.

Subsumption/containment reasoning rests on **query containment** (Chandra–Merlin): conjunctive-query containment is NP-complete, and view-rewriting/answering-queries-using-views underlies sharing modulo predicates. The producer-consumer ordering is a DAG-scheduling problem; under memory budget it becomes a **register-allocation / pebbling** problem (black pebble game), which is **PSPACE-complete** in general.

## 3. State of the Art (SOTA)

**Foundational systems-SOTA.** Sellis (ACM TODS 1988) formalized MQO and gave A*/heuristic search. **Roy–Seshadri–Sudarshan–Bhobe** (SIGMOD 2000) gave the canonical practical algorithm: greedy DAG-based MQO with cost-based sharing on the Volcano/Cascades AND/OR DAG — the most-cited systems result, integrated into Cascades-style optimizers.

**Modern systems-SOTA.** Cloud warehouses do MQO-style work as **materialized-view / result-cache selection** and **computation reuse**: Microsoft *CloudViews* and SCOPE's subexpression reuse (VLDB 2018, 2020), AWS Redshift / Snowflake result reuse, and *recurring-workload* view selection. Apache Calcite exposes shared-subplan spooling. Sketch-/learning-guided CSE selection appears in recent work.

**Theory-SOTA.** Reductions to Directed Steiner Tree give $O(m^\epsilon)$-style approximations inherited from DST; for the view/subexpression-selection subproblem, submodular greedy yields $(1-1/e)$ under independence assumptions.

## 4. Upper Bound

No polynomial exact algorithm is known; the best *exact* method is exhaustive AND/OR DAG search, exponential in the number of subexpressions. For **approximation**: the materialized-view/subexpression *selection* subproblem (plans fixed) is an instance of weighted set cover / submodular maximization, giving a $(1-1/e)$-approximation by greedy, or $\ln n$ set-cover approximation for the covering form. The *joint* plan-plus-sharing problem reduces to **Directed Steiner Tree/Forest**, whose best polynomial approximation is $O(n^\epsilon)$ for any $\epsilon>0$ (Charikar et al.) or quasi-poly $O(\log^2 k)$ — these are the best general upper bounds inherited by joint MQO. Roy et al.'s greedy is the practical SOTA but has no constant-factor guarantee for the joint problem.

## 5. Lower Bound

MQO is **NP-hard**: even the restricted problem of selecting which common subexpressions to materialize to minimize total cost contains **Weighted Set Cover** (Sellis; Roy et al.), which is NP-hard and, under $P\neq NP$, inapproximable below $(1-o(1))\ln n$ (Dinur–Steurer). The joint plan-selection-plus-sharing problem is at least as hard as **Directed Steiner Tree**, for which an $O(\log^{2-\epsilon} k)$ approximation would refute standard assumptions; under the projection games / Label-Cover hardness, DST has no $\Omega(\log^{2-\epsilon}n)$ approximation. Containment-based sharing inherits NP-completeness of conjunctive-query containment (Chandra–Merlin, STOC 1977).

## 6. The Gap

The gap is **genuinely open and wide**. For the selection subproblem, the $(1-1/e)$/$\ln n$ upper bounds match set-cover lower bounds up to constants — essentially closed. But for the **joint** plan-and-sharing problem, the only general upper bounds come from Directed Steiner ($O(n^\epsilon)$ / quasi-poly) while the lower bound is merely $\Omega(\log^{2-\epsilon})$ — a polynomial-vs-polylog chasm. No algorithm with a poly-logarithmic guarantee for joint cost-based MQO is known, and it is open whether the DST hardness is the *real* barrier or an artifact of the reduction. Closing it would require either a polylog joint approximation or a stronger fine-grained lower bound.

## 7. Current Research (as of June 2026)

Active directions: (i) **workload-aware computation reuse** in cloud platforms — CloudViews-style subexpression mining over recurring jobs at Microsoft, AWS, Google *(frontier — verify)*; (ii) **learned subexpression selection** using GNNs over plan DAGs to predict reuse benefit (work from MIT, Microsoft GSL, TUM); (iii) **MQO for ML/feature pipelines and tensor programs**, where shared subexpression elimination resembles common-subexpression elimination in compilers; (iv) semantic caching and **incremental view maintenance** integration so shared results survive across batches (DBToaster/IVM lineage, Koch et al.). Theoretical work on tighter DST-free bounds for the structured plan DAGs arising in practice is sparse and an opportunity.

## 8. Future Work

- A poly-logarithmic approximation (or matching hardness) for joint cost-based MQO on realistic plan DAGs.
- Online/streaming MQO where queries arrive over time and sharing decisions are irrevocable (competitive analysis).
- Tight integration of MQO with adaptive re-optimization and learned cardinality.
- Memory/pebbling-aware scheduling of shared subexpressions with provable space-time tradeoffs.
- Semantic (containment-modulo-predicate) sharing at warehouse scale with bounded reasoning cost.

## 9. Key References

- **[Foundational]** T. K. Sellis. *Multiple-Query Optimization.* ACM TODS, 1988. — [DOI](https://doi.org/10.1145/42201.42203)
- **[Foundational]** P. Roy, S. Seshadri, S. Sudarshan, S. Bhobe. *Efficient and Extensible Algorithms for Multi-Query Optimization.* SIGMOD, 2000. — [arXiv](https://arxiv.org/abs/cs/9910021)
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[SOTA]** A. Jindal, K. Karanasos, S. Rao, H. Patel. *Selecting Subexpressions to Materialize at Datacenter Scale (CloudViews).* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3192965.3192971)
- **[SOTA]** M. Charikar, C. Chekuri, et al. *Approximation Algorithms for Directed Steiner Problems.* Journal of Algorithms, 1999. — [DOI](https://doi.org/10.1006/jagm.1999.1042)
- **[Survey]** G. Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bulletin, 1995. — [PDF](https://15721.courses.cs.cmu.edu/spring2016/papers/graefe-ieee1995.pdf)

## 10. Worked Example

Two queries share a subexpression $E = \sigma_{p}(R)\bowtie S$. Independently: $Q_1$ costs $100$, $Q_2$ costs $90$, and each computes $E$ at internal cost $40$. Materializing $E$ once costs $\text{matCost}(E)=45$ (compute + write), after which each query reuses it for $5$ instead of $40$.

Objective $\sum_i \text{cost}(P_i) + \sum_{e\in M}\text{matCost}(e) - \text{savings}(M)$:

- **No sharing** ($M=\varnothing$): $100 + 90 = 190$.
- **Share $E$** ($M=\{E\}$): each query saves $40-5=35$, so $\text{savings}=2\cdot35=70$; total $=190 + 45 - 70 = 165$.

Sharing wins by $25$. But the decision is non-local: had $\text{matCost}(E)=75$, the math flips to $190+75-70=195 > 190$ — *not* worth sharing. With many candidate subexpressions and interacting plan choices, picking the optimal $M$ is the **weighted set-cover** core that makes MQO NP-hard (section 5); greedy on the benefit-per-cost ratio gives the $(1-1/e)$ guarantee when plans are held fixed.

---
*Part of the [DBMS Research catalog](../../README.md).*
