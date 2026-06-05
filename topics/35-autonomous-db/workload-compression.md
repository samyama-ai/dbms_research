# Workload Compression & Representativeness

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/workload-compression` · **Status:** partially-solved

## 1. Problem Statement
A production trace contains millions of queries; a physical-design advisor that calls the optimizer once per candidate per query cannot scale to it. **Workload compression** reduces a trace $W$ of $n$ (weighted) queries to a small surrogate $W'$ of size $k\ll n$ such that the *design decision* induced by $W'$ is provably close to the decision induced by $W$. The key word is **representativeness**: $W'$ must be representative *for the downstream task* (index/MV/partition selection, configuration tuning), not merely a uniform sample.

Variants:
- **Decision variant (the right one):** find $W'$ minimizing $|F_W(D^\star_{W'}) - F_W(D^\star_W)|$ — the *task regret* of designing on the surrogate.
- **Coverage/optimization variant:** select a $k$-subset (with weights) minimizing a coverage loss over the candidate-structure benefit space.
- **Counting/clustering variant:** how few representatives suffice — i.e. the *intrinsic dimension* of a workload for a given design task.

## 2. Mathematical Foundations
Each query $q$ contributes a *benefit profile* $b_q\in\mathbb R^{|C|}_{\ge0}$ over candidate structures $C$. Total benefit of design $D$ is $F_W(D)=\sum_q w_q\max\dots$ — in canonical formulations the index-benefit objective is **monotone submodular**, so the design subproblem is a $(1-1/e)$-approximable cardinality/knapsack-constrained submodular maximization (Nemhauser–Wolsey–Fisher).

Compression then has two clean mathematical handles:
1. **Coreset theory.** A weighted subset $W'$ is an $\varepsilon$-coreset for the design objective if $\forall D:\ |F_{W'}(D)-F_W(D)|\le \varepsilon\,F_W(D)$. Coreset size bounds depend on the **VC / pseudo-dimension** of the family $\{q\mapsto b_q(D): D\in\mathcal D\}$; importance (sensitivity) sampling gives coresets of size $\tilde O(\dim/\varepsilon^2)$.
2. **Submodular surrogate.** Since the objective is submodular, *representative subset selection* is itself a submodular-coverage problem, again $(1-1/e)$-approximable.

The earliest DB formalization (Chaudhuri, Gupta, Narasayya, SIGMOD 2002) casts compression as a **distance-based k-medoid / set-cover** problem under a query-distance function with a coverage guarantee on retained query cost.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Chaudhuri–Gupta–Narasayya (SIGMOD 2002) gave the canonical cost-distance compression used inside Microsoft's tuning tools. Modern advisors (DTA, and the open-source suite in Kossmann et al.'s benchmark, PVLDB 2020) template-cluster queries and weight clusters. Learned approaches embed queries (plan/feature vectors) and cluster in embedding space; query2vec-style representations feed forecasting and compression alike.

**Theory-SOTA.** Sensitivity-based **coresets** for the relevant loss families (clustering, monotone-submodular coverage) give $\tilde O(\dim/\varepsilon^2)$-size $\varepsilon$-coresets independent of $n$ — the strongest representativeness guarantee available, though the *DB-specific* benefit family's dimension is rarely characterized tightly.

## 4. Upper Bound
For coverage-style compression: importance/sensitivity sampling yields an $\varepsilon$-coreset of size $\tilde O(d/\varepsilon^2)$ where $d$ is the pseudo-dimension of the benefit family, giving $(1\pm\varepsilon)$ preservation of $F_W(D)$ for **all** designs simultaneously (RAM / streaming model). Composed with greedy submodular design, the end-to-end design regret is $O(\varepsilon\cdot F^\star)$. The classic k-medoid cost-distance formulation admits the standard $2$-approximation / set-cover $\ln n$ guarantees.

## 5. Lower Bound
Computing the *minimum* representative set with a hard coverage guarantee is **NP-hard** by reduction from **Set Cover** (Chaudhuri et al.), and Set Cover is inapproximable below $(1-o(1))\ln n$ unless $\mathsf{P}=\mathsf{NP}$ (Dinur–Steurer) — so the $\ln n$ factor for the coverage variant is essentially tight. Information-theoretically, *any* compression to size $k$ incurs decision regret $\Omega$ of the benefit mass it discards: if the optimal design's benefit is concentrated on $> k$ near-orthogonal query profiles, no size-$k$ surrogate preserves the decision (a counting/dimension lower bound).

## 6. The Gap
The status is **partially-solved**: for the *coverage* objective, upper ($\ln n$ / $\varepsilon$-coreset) and lower (Set-Cover $\ln n$) bounds essentially match. The genuinely open part is the **decision variant**: tight bounds on *task regret* (how design quality degrades) as a function of $k$, and a characterization of the *intrinsic representativeness dimension* of real workloads for joint physical design. Closing it requires pseudo-dimension bounds for the actual DB benefit family and decision-regret (not coverage) sampling guarantees.

## 7. Current Research (as of June 2026)
Active directions: learned query embeddings for clustering/compression that respect plan structure; coreset constructions specialized to submodular index-benefit objectives; "decision-faithful" compression that bounds end-to-end advisor regret rather than per-query cost error *(frontier — verify)*; and compression integrated with forecasting so the surrogate reflects the *future* mix (Microsoft GSL; CMU self-driving group; Schlosser/Kossmann at HPI on index-selection benchmarking). The connection between coreset pseudo-dimension and real-workload structure remains largely empirical *(frontier — verify)*.

## 8. Future Work
- Decision-regret coreset bounds for joint index/MV/partition design.
- Characterizing the intrinsic representativeness dimension of production traces.
- Drift-aware compression (surrogate tracks the forecasted future workload).
- Streaming/online compression with bounded memory and provable coverage.

## 9. Key References
- **[Foundational]** Chaudhuri, S., Gupta, A. K., Narasayya, V. *Compressing SQL Workloads.* SIGMOD, 2002.
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions—I.* Mathematical Programming, 1978.
- **[SOTA]** Feldman, D., Langberg, M. *A Unified Framework for Approximating and Clustering Data (sensitivity coresets).* STOC, 2011.
- **[SOTA]** Kossmann, J., Halfpap, S., Jankrift, M., Schlosser, R. *Magic mirror in my hand... An Experimental Evaluation of Index Selection Algorithms.* PVLDB, 2020.
- **[Foundational]** Dinur, I., Steurer, D. *Analytical Approach to Parallel Repetition (tight Set Cover hardness).* STOC, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
