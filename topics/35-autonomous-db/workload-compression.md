---
id: 35-autonomous-db/workload-compression
title: "Workload Compression & Representativeness"
topic: 35-autonomous-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

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
- **[Foundational]** Chaudhuri, S., Gupta, A. K., Narasayya, V. *Compressing SQL Workloads.* SIGMOD, 2002. — [PDF](https://15799.courses.cs.cmu.edu/spring2022/papers/12-workload2/chaudhuri-sigmod2002.pdf)
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions—I.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[SOTA]** Feldman, D., Langberg, M. *A Unified Framework for Approximating and Clustering Data (sensitivity coresets).* STOC, 2011. — [arXiv](https://arxiv.org/abs/1106.1379)
- **[SOTA]** Kossmann, J., Halfpap, S., Jankrift, M., Schlosser, R. *Magic mirror in my hand... An Experimental Evaluation of Index Selection Algorithms.* PVLDB, 2020. — [PDF](https://www.vldb.org/pvldb/vol13/p2382-kossmann.pdf)
- **[Foundational]** Dinur, I., Steurer, D. *Analytical Approach to Parallel Repetition (tight Set Cover hardness).* STOC, 2014. — [arXiv](https://arxiv.org/abs/1305.1979)

## 10. Worked Example

A trace of $n=5$ queries, each with a benefit profile $b_q$ over 3 candidate indexes $\{x_1,x_2,x_3\}$ (benefit = cost saved if the index exists), weight $w_q=1$:

| $q$ | $x_1$ | $x_2$ | $x_3$ |
|----|----|----|----|
| $q_1$ | 90 | 0 | 0 |
| $q_2$ | 85 | 0 | 0 |
| $q_3$ | 0 | 80 | 0 |
| $q_4$ | 0 | 0 | 5 |
| $q_5$ | 0 | 0 | 4 |

Budget: pick $k=1$ index. True best on full $W$: $x_1$ saves $90+85=175$, $x_2$ saves $80$, $x_3$ saves $9$. So $D^\star_W=\{x_1\}$, $F_W=175$.

Compress to $W'$ of size 2 by **uniform** sampling and we might draw $\{q_3,q_4\}$: now $x_2$ looks best (80 vs. $x_1$'s 0), so $D^\star_{W'}=\{x_2\}$ giving real benefit $F_W(\{x_2\})=80$ — task regret $175-80=95$.

**Sensitivity sampling** instead weights each query by its importance (its max contribution to any design); $q_1,q_2$ have high sensitivity and are retained with up-weighting, so $x_1$ is correctly chosen — an $\varepsilon$-coreset preserves $F_W(D)$ for *all* $D$. This contrasts coverage (provably $(1\pm\varepsilon)$ via $\tilde O(d/\varepsilon^2)$ samples) against the still-open *decision-regret* characterization of section 6: the near-orthogonal profiles of $q_1,q_3$ are exactly the dimension lower bound that forbids tiny surrogates.

---
*Part of the [DBMS Research catalog](../../README.md).*
