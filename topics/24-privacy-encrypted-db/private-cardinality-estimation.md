---
id: 24-privacy-encrypted-db/private-cardinality-estimation
title: "Private Cardinality and Selectivity Estimation"
topic: 24-privacy-encrypted-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Private Cardinality and Selectivity Estimation

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/private-cardinality-estimation` · **Status:** open

## 1. Problem Statement
A query optimizer needs **cardinality** (number of rows produced by a sub-plan) and **selectivity** (fraction surviving a predicate) estimates to choose join orders and access paths. We want these estimates under differential privacy so that the *optimizer's behavior and emitted plans* do not leak about individual rows. The hard part: an optimizer issues **many** such estimates per query (one per candidate sub-plan, per predicate, per join order), so naive per-estimate noise exhausts the privacy budget $\varepsilon$ exponentially fast. The problem is to produce a **DP synopsis** (histogram, sketch, or model) once, then answer the optimizer's combinatorial set of cardinality/selectivity questions from it with bounded total budget and bounded *relative* error.

Variants: **counting** (point/range selectivity, distinct counts $F_0$), **optimization** (returning a low-cost plan whose *cost* is near-optimal, not its exact cardinalities), and **decision** (is this sub-plan's cardinality below a pruning threshold?).

## 2. Mathematical Foundations
Selectivity of a conjunctive predicate over a join is bounded above by the **AGM bound** $\prod \text{(relation sizes)}^{x_e}$ from a fractional edge cover $x$ of the query hypergraph (Atserias–Grohe–Marx); private estimators may calibrate noise to these structural bounds. Range/predicate selectivity reduces to **DP histograms / range queries**, governed by the prefix-sum **$\gamma_2$ factorization** error $O(\varepsilon^{-1}\log d)$. Distinct-count selectivity invokes private $F_0$ via **flajolet-martin / HyperLogLog** sketches, where the privacy concern is **sketch composability** under union: a sketch is *DP-mergeable* if its randomized response noise survives `merge`. Budget management uses **advanced composition** ($\sqrt{k\log(1/\delta)}\,\varepsilon$ over $k$ queries) and **post-processing immunity**: once a synopsis is DP, *unbounded* deterministic queries against it are free.

## 3. State of the Art (SOTA)
- **Synopsis route (theory-SOTA):** Build one DP synopsis (private multi-dimensional histogram via hierarchical/MF mechanisms, or a DP marginals model à la **PrivBayes / Private-PGM**, McKenna–Sheldon–Miklau, ICML 2019) and answer all optimizer queries by post-processing — *constant* total budget regardless of query count.
- **DP sketches (systems-SOTA):** Differentially private **HyperLogLog / Bloom-filter cardinality** (Desfontaines, Lochbihler, Basin — "Cardinality Estimators do not Preserve Privacy", PoPETs 2019, with positive DP-HLL constructions; Google's DP sketch work) give DP distinct counts that **merge** across shards — directly usable for join-distinctness.
- **Optimizer-aware:** Learned cardinality estimators trained with **DP-SGD** are emerging but lack the relative-error guarantees optimizers need.

## 4. Upper Bound
Range/selectivity queries from a DP synopsis: additive error $O(\varepsilon^{-1}\log^{1.5} n)$ (hierarchical) or $O(\varepsilon^{-1}\log n)$ (matrix factorization), per query, for *arbitrarily many* queries (central model, post-processing). DP distinct count: multiplicative $(1\pm\eta)$ with additive $O(\varepsilon^{-1})$ slack via DP-HLL, mergeable. For **join cardinality**, no general low-relative-error DP estimator exists; AGM-calibrated estimates give upper bounds but loose relative error on skewed/correlated data.

## 5. Lower Bound
**Reconstruction / fingerprinting** lower bounds (Bun–Ullman–Vadhan; Dinur–Nissim) cap the number of *independent* low-error linear queries answerable on $n$ rows at $\tilde O(n^2)$ under $(\varepsilon,\delta)$-DP — a hard ceiling on synopsis fidelity. For **distinct counts**, any DP estimator has additive error $\Omega(\varepsilon^{-1})$ and **multiplicative** error cannot be made arbitrarily small without large additive slack (info-theoretic). Cardinality-estimator-as-leakage results (Desfontaines et al.) show *non-private* HLL/Bloom sketches **fail** any reasonable DP definition — leakage is inherent without explicit noise.

## 6. The Gap
This is **open** because the missing piece is **relative-error** join cardinality under DP. Synopses give good *additive* error on single tables, but optimizer decisions hinge on *relative* errors of multi-join sub-plans where DP additive noise is overwhelmed by tiny true cardinalities (the "0 vs 1000 rows" problem dominating plan choice). No mechanism is known that (a) bounds total budget across the optimizer's exponential sub-plan space *and* (b) guarantees the *chosen plan* is near-cost-optimal. Closing it likely needs an "optimize the plan, not the estimate" objective with a DP regret bound.

## 7. Current Research (as of June 2026)
Active: **DP-mergeable sketches** with tight privacy/accuracy (Desfontaines, Pagh, Lebeda, Thorup line), and **learned + DP cardinality models** with calibrated uncertainty *(frontier — verify)*; **Private-PGM / AIM** (McKenna, Miklau, Sheldon) graphical-model synopses adapted to optimizer marginals; and an **end-to-end "private query planning"** objective minimizing plan suboptimality rather than estimate error *(frontier — verify)*. Groups: Miklau/McKenna/Sheldon (UMass/DPsynth), Pagh & Lebeda (Copenhagen), Desfontaines (Tumult Labs/independent), Cormode (Warwick) on private sketches. Tumult Analytics and OpenDP increasingly expose private histograms/quantiles that an optimizer could consume.

## 8. Future Work
- A DP cardinality estimator with provable *relative*-error for multi-way joins on skewed data.
- "Plan-regret" DP guarantees: bound suboptimality of the emitted plan, not per-estimate error.
- Budget-free reuse: amortize one synopsis across an entire workload of queries.
- DP-mergeable join-distinctness sketches for distributed/sharded warehouses.
- Integrating private cardinality estimation with private *query execution* (so end-to-end answers and plans share one budget).

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS/SIAM J. Comput., 2008/2013. — [DOI](https://doi.org/10.1137/110859440) — [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[SOTA]** McKenna, Sheldon, Miklau. *Graphical-model based estimation and inference for differential privacy (Private-PGM).* ICML, 2019. — [arXiv](https://arxiv.org/abs/1901.09136)
- **[SOTA]** Desfontaines, Lochbihler, Basin. *Cardinality Estimators do not Preserve Privacy.* PoPETs, 2019. — [arXiv](https://arxiv.org/abs/1808.05879)
- **[SOTA]** Pagh, Stausholm. *Efficient Differentially Private $F_0$ Linear Sketching / Mergeable Sketches.* ICDT/PODS line, 2021–2022. — [arXiv](https://arxiv.org/abs/2001.11932) — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2021.18)
- **[Survey]** Cormode, Jha, Kulkarni, Li, Srivastava, Wang. *Privacy at Scale: Local Differential Privacy in Practice.* SIGMOD tutorial, 2018. — [DOI](https://doi.org/10.1145/3183713.3197390)

## 10. Worked Example

Take a tiny range-count synopsis over the domain $[1,8]$ of an `age_bucket` column with true leaf counts $(3,0,5,2,7,1,4,2)$. An optimizer wants the selectivity of predicate `age_bucket BETWEEN 3 AND 6`, i.e. the sum of leaves $3..6 = 5+2+7+1 = 15$ out of $24$ rows, selectivity $15/24 \approx 0.625$.

Build a binary tree of partial sums and add Laplace noise $\mathrm{Lap}(1/\varepsilon)$ to each node. The range $[3,6]$ is covered by just $2$ dyadic nodes: $[3,4]$ (count $7$) and $[5,6]$ (count $8$). With $\varepsilon=1$, each noised node has stddev $\sqrt2/\varepsilon \approx 1.41$, so the range estimate is $15 \pm \approx 2$ — additive error $O(\varepsilon^{-1}\log n)$ over only $\log_2 8 = 3$ levels, not $O(n)$.

Crucially, once this tree is published DP, the optimizer may ask *unboundedly many* range/selectivity questions ($[1,4]$, $[5,8]$, $[2,7]$, ...) by post-processing — total budget stays $\varepsilon=1$. That is the synopsis route's payoff: combinatorially many estimates, constant budget.

---
*Part of the [DBMS Research catalog](../../README.md).*
