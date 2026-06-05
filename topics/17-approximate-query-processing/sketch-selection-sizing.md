# Sketch Selection and Sizing

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sketch-selection-sizing` · **Status:** open

## 1. Problem Statement
Given a relation schema, a (possibly evolving) query workload $Q$, a global memory budget $B$, and per-query accuracy targets, **automatically choose which synopsis to build on which column(s) and at what size**. Each candidate is a (column or column-group, sketch-type, parameter) triple — e.g., HLL with $m$ registers on `user_id`, KLL with parameter $k$ on `latency`, CM with width $w$ on `event_type`, a 2-D histogram on `(lat,lon)`, or a coordinated minhash for a join key.

Formally (optimization variant): choose a set $S$ of synopses with $\sum_{s\in S}\mathrm{size}(s)\le B$ maximizing workload utility (e.g., minimizing expected/worst-case query error), where each query draws on a subset of synopses and its error is a function of their parameters. The decision variant: does a configuration meeting all per-query SLAs within budget $B$ exist? The online variant: adapt $S$ as the workload and data distribution drift.

This is genuinely **open**: the design space is combinatorial, error-vs-size curves differ per sketch family and per data distribution, queries share synopses (utility is non-separable), and the optimum interacts with the query optimizer's plan choices.

## 2. Mathematical Foundations
Cast as a **constrained budget allocation / knapsack-like** problem. Let $u_q(\theta)$ be query $q$'s utility under parameter assignment $\theta$ to its relevant synopses, and $c(\theta)$ the byte cost. Maximize $\sum_q w_q\,u_q(\theta)$ s.t. $\sum c\le B$. When utilities are **submodular** in the chosen synopsis set (diminishing returns from adding redundant synopses), greedy gives a $(1-1/e)$ approximation (Nemhauser–Wolsey–Fisher). But sizing is *continuous* (register counts, sketch widths) and error curves are typically convex-decreasing — e.g., HLL error $\propto 1/\sqrt m$, CM error $\propto 1/w$, KLL rank error $\propto 1/k$ — turning the inner problem into **convex resource allocation** solvable by Lagrangian/water-filling when separable.

The hardness sources: (1) **shared synopses** break separability; (2) **column-group selection** (which multi-attribute synopses to build) resembles index/view selection, which is NP-hard; (3) **distribution dependence** — the optimal sketch type depends on skew (Zipf favors heavy-hitter sketches; uniform favors HLL/histograms), so the objective itself must be learned or sampled.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** No closed-form optimum. The relevant theory is submodular maximization under knapsack constraints and Lagrangian budget allocation; the synopsis-selection objective is not generally submodular, so guarantees are partial.
- **Systems-SOTA:** Self-tuning approaches inherit from **AutoAdmin / index-and-view selection** (Chaudhuri–Narasayya, VLDB 1997–) and self-tuning histograms (**STHoles**, Bruno–Chaudhuri–Gravano, SIGMOD 2001). Modern AQP engines (**VerdictDB**, **BlinkDB**) choose *sample* sizes/stratification under storage and latency budgets given a workload, the closest deployed analog. Apache DataSketches leaves sizing to the user via documented error-vs-size tables.

## 4. Upper Bound
For *separable* utilities with convex error-vs-size curves, Lagrangian/water-filling yields the exact optimal continuous sizing in $O(n\log n)$ over $n$ candidates (KKT conditions). For the discrete *selection* part with submodular coverage utility under a knapsack constraint, greedy achieves $(1-1/e)$ of optimum (Sviridenko 2004 for knapsack-constrained submodular). BlinkDB-style sample selection solves an integer program / multi-armed allocation heuristically with no global optimality guarantee.

## 5. Lower Bound
The **selection** subproblem generalizes index/materialized-view selection, which is NP-hard (reduction from set cover / knapsack), and is **inapproximable beyond $(1-1/e)$** for the underlying max-coverage formulation unless P=NP (Feige 1998). When utilities are non-submodular (shared synopses with super-/sub-additive interactions), no constant-factor approximation is known. Online/adaptive variants face regret lower bounds from the bandit/experts framework.

## 6. The Gap
Both the upper-bound *guarantees* and the lower-bound *characterization* are incomplete: we lack (a) a tractable, accurate model of per-query error as a function of a *heterogeneous* synopsis portfolio, and (b) approximation algorithms with provable bounds for the **joint** type-selection + continuous-sizing problem under shared, distribution-dependent utilities. The gap is wide open — there is no agreed-upon formalization with matching algorithm and hardness result, only heuristics (BlinkDB, self-tuning histograms) and isolated theory pieces (submodular knapsack, convex allocation).

## 7. Current Research (as of June 2026)
Active work: **learned/RL-based synopsis and sample advisors** that observe the workload and pick sketch types/sizes (extending learned-index and learned-CE lines from TUM, MIT, CMU). *(frontier — verify)* Proposals couple sketch sizing with the query optimizer so plan choice and synopsis budget are co-optimized; differentiable surrogates for error-vs-size enable gradient-based budget allocation. Cloud AQP services explore auto-sizing under cost/SLA constraints.

## 8. Future Work
- A unified cost model for heterogeneous synopsis portfolios with shared usage.
- Approximation algorithms with provable bounds for joint type-selection + sizing.
- Online/adaptive re-sizing under data and workload drift with regret guarantees.
- Optimizer-integrated co-design of plans and synopsis budgets.

## 9. Key References
- **[Foundational]** Chaudhuri, S., Narasayya, V. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB 1997.
- **[Foundational]** Bruno, N., Chaudhuri, S., Gravano, L. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD 2001.
- **[SOTA]** Agarwal, S., Mozafari, B., Panda, A., Milner, H., Madden, S., Stoica, I. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys 2013.
- **[SOTA]** Park, Y., Mozafari, B., et al. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD 2018.
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978.

---
*Part of the [DBMS Research catalog](../../README.md).*
