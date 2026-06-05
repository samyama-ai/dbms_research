# Cascades-style rule scheduling and pruning

> **Topic:** Query Optimization · **ID:** `02-query-optimization/cascades-rule-scheduling` · **Status:** empirically-open

## 1. Problem Statement

In a Cascades/Volcano optimizer the memo grows by **firing transformation and implementation rules** on expression groups, driven by a task/promise queue and bounded by branch-and-bound cost limits. The *order* in which rules fire and the *pruning* applied determine how fast a good plan is found and how much of the (possibly exponential) space is materialized. The problem: **what is a principled, ideally optimal, policy for (i) ordering rule firings and (ii) pruning groups/expressions, that minimizes optimization work while preserving the optimum (or a bounded-suboptimality guarantee)?**

- **Scheduling (optimization) variant:** Choose a firing order minimizing total rules fired (or wall-clock) subject to returning the global optimum over the reachable space.
- **Pruning (decision) variant:** Given lower/upper cost bounds, decide which groups can be skipped (lower bound $\ge$ current upper bound) without losing optimality — branch-and-bound correctness.
- **Anytime variant:** Produce a sequence of monotonically improving plans with a provable gap to optimal at each step (for time-budgeted optimization).

It is **empirically-open**: deployed heuristics (rule "promises," guidance, timeouts) work well but lack guarantees, and no policy is known to be optimal or near-optimal with proof.

## 2. Mathematical Foundations

The search is exploration of an **AND/OR memo graph**; optimization is a sequence of *tasks* (`OptimizeGroup`, `OptimizeExpr`, `ApplyRule`, `OptimizeInputs`) on a stack/priority queue. **Branch-and-bound** correctness rests on an **admissible lower bound** $LB(g)\le \mathrm{best}(g)$ for each group $g$: if $LB(g)\ge UB$ (the best full-plan cost found so far through that context), $g$ need not be optimized — this is sound exactly when $LB$ never overestimates (cf. A* admissibility). Rule **ordering** is a sequencing problem: each firing has a *promise/benefit* (expected cost reduction) and a *cost* (work). Optimal scheduling under uncertainty maps to a **stochastic scheduling / Markov decision process**, and to the **Pandora's-box / optimal-search** family (Weitzman): when exploration is costly and rewards uncertain, an index policy can be optimal. Anytime guarantees relate to **online/competitive** analysis: a policy is $c$-competitive if its plan-at-time-$t$ cost is within $c\times$ the offline optimum reachable in $t$. The key structural fact: pruning soundness requires the optimality principle and admissible bounds; scheduling affects only *efficiency*, not the final optimum, **provided** the search runs to fixpoint — but under a time budget, scheduling determines the *returned* plan.

## 3. State of the Art (SOTA)

- **Systems SOTA:** Cascades (Graefe 1995) introduced rule **promise** and guidance; **Columbia** (Xu, 1998) formalized the task structure and group/expression pruning, demonstrating large search-space reductions. Greenplum **Orca** (SIGMOD 2014), Microsoft SQL Server, CockroachDB, and Calcite's Volcano planner implement branch-and-bound with rule-application heuristics, rule-set partitioning into phases, and timeouts.
- **Theory SOTA:** Branch-and-bound *correctness* (sound pruning with admissible bounds) is established; **optimal scheduling** is not. Lower-bound (group) computation techniques (e.g., cheapest-possible per-group cost) sharpen pruning. No published policy is proven optimal/near-optimal for the firing order. Learned guidance is emerging (below).

## 4. Upper Bound

With sound branch-and-bound and admissible lower bounds, the optimizer is guaranteed to return the **global optimum over the reachable space** at termination; worst-case work is the full memo closure, i.e. $O(\#\text{ground expressions})$, which is exponential for dense graphs (RAM model). Pruning can reduce realized work by orders of magnitude but gives **no worst-case asymptotic improvement** (adversarial flat-cost inputs defeat the bound — same phenomenon as in *search-strategy-coverage*). For the anytime variant, no non-trivial competitive ratio is proven for general rule sets; only the trivial "optimum at fixpoint" guarantee holds.

## 5. Lower Bound

Because the reachable space can be exponential and optimal join ordering is NP-hard, no scheduling/pruning policy can avoid worst-case exponential work in the exact-optimization model unless P=NP. Optimal *scheduling* of uncertain-reward explorations is, in general settings, at least as hard as stochastic scheduling problems that are NP-hard; the Pandora's-box optimal index policy applies only under independence assumptions that real rule interactions violate, so optimal ordering under dependencies is not known to be polynomial. No matching lower bound is known for the *anytime/competitive* variant — its hardness is itself open.

## 6. The Gap

The status is **empirically-open**: pruning *correctness* is closed (admissible bounds give sound branch-and-bound), but there is **no theory of optimal or near-optimal rule scheduling**, and **no competitive guarantee for time-budgeted (anytime) optimization**. The gap is between (a) heuristics that perform well on benchmarks but can be arbitrarily bad adversarially, and (b) the absence of either a provably good policy or a hardness result explaining why one cannot exist. Closing it requires formalizing rule firing as a search/scheduling MDP with realistic dependence structure, then either deriving an index/competitive policy with guarantees or proving inapproximability. Tighter, cheaply-computable admissible lower bounds would also directly strengthen pruning.

## 7. Current Research (as of June 2026)

- **Learned guidance for Cascades** — ML/RL policies that prioritize rule firings and group expansion (lineage of learned optimizers; *Bao*, *Balsa*, and Cascades-specific guidance work). *(frontier — verify)*
- **Tighter group lower bounds** for sharper branch-and-bound (e.g., cardinality-bound-derived $LB$, links to *enumeration-without-oracle*). *(frontier — verify)*
- **Anytime / budget-aware optimization** with monotone-improvement guarantees, framed via online search. *(frontier — verify)*
- Formal **operational semantics of Cascades** enabling reasoning about scheduling effects on the returned plan (connects to *transformation-rule-completeness*).
- Rule-set **phasing/partitioning** strategies to bound interaction blowup (Orca, Calcite practice).

## 8. Future Work

- A provably optimal or constant-competitive rule-scheduling policy under realistic dependence, or an inapproximability result.
- Cheap, tight admissible group lower bounds (esp. from cardinality bounds) to make pruning bite in the worst case.
- Competitive analysis for time-budgeted/anytime optimization with verified gap-to-optimal.
- Guarantees (not just benchmarks) for learned guidance policies.

## 9. Key References

- **[Foundational]** Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bulletin, 1995.
- **[Foundational]** Xu (Bilgin). *Efficiency in the Columbia Database Query Optimizer.* MS Thesis, Portland State University, 1998.
- **[SOTA]** Soliman et al. *Orca: A Modular Query Optimizer Architecture for Big Data.* SIGMOD, 2014.
- **[SOTA]** Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[Foundational]** Weitzman. *Optimal Search for the Best Alternative.* Econometrica, 1979. (Pandora's box / optimal search)
- **[Survey]** Chaudhuri. *An Overview of Query Optimization in Relational Systems.* PODS, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
