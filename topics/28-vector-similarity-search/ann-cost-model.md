---
id: 28-vector-similarity-search/ann-cost-model
title: "Cost model for ANN query planning"
topic: 28-vector-similarity-search
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cost model for ANN query planning

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/ann-cost-model` · **Status:** open

## 1. Problem Statement

A relational/hybrid query optimizer must treat ANN search as a first-class operator and choose among plans: which index (HNSW vs. IVF-PQ vs. flat scan), what tuning knobs (`ef_search`, `n_probe`, re-rank depth), and how to order it relative to filters, joins, and `ORDER BY ... LIMIT k`. This requires a **predictive cost model**: a function that maps $(\text{query vector}, k, \text{recall target}, \text{index state}, \text{predicate selectivity}) \mapsto (\widehat{\text{latency}}, \widehat{\text{recall}}, \widehat{\text{rows scanned}})$.

- **Estimation variant.** Given a plan and parameters, predict cost and recall accurately enough to rank plans.
- **Optimization variant.** Choose the plan + parameter setting minimizing latency subject to $R@k \ge R_0$ (or maximizing recall under a latency budget).
- **Filtered/hybrid variant.** Model the interaction of a metadata predicate of selectivity $s$ with the ANN operator (pre-filter vs. post-filter vs. inline filtering), since selectivity drastically changes the best plan.

This is the ANN analogue of Selinger-style cost-based optimization, but recall is a *quality* dimension absent from classical relational costing.

## 2. Mathematical Foundations

Classical optimizers (System R, Selinger 1979) cost plans via cardinality estimates and per-operator cost formulas; correctness rests on selectivity estimation and the principle of optimality enabling dynamic programming over join orders. ANN breaks two assumptions: (i) the operator is *approximate*, so output is a function of a tuning knob, and (ii) cost is **data-** and **query-dependent** (a query in a dense region probes fewer cells than one near a Voronoi boundary).

Formally, for IVF with $C$ centroids and balanced cells of size $n/C$, scanning $p$ cells reads $\approx p\,n/C$ vectors; recall is a function $R(p)$ that is concave and increasing, well-approximated empirically by $R(p)\approx 1-e^{-\gamma p}$ for instance-dependent $\gamma$. For graph search, work scales with $\mathrm{ef}$ and the local intrinsic dimension $d_{\mathrm{LID}}$; expected distance computations $\approx \mathrm{ef}\cdot\overline{\deg}\cdot \Theta(\log n)$. A principled model uses **local intrinsic dimensionality** (Houle) and the distance distribution $F(r)=\Pr[d(q,x)\le r]$ to predict both cost and the recall–effort curve. Filtered search composes the predicate selectivity $s$ with the ANN reachability — modeled as a thinned point process, where pre-filtering changes effective $n\to s\,n$.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *pgvector* (Postgres) exposes `ivfflat`/`hnsw` with hand-set knobs but no recall-aware cost model; its planner uses crude row-count heuristics. *AnalyticDB-V* (Wei et al., VLDB 2020) and *Milvus* integrate ANN into a query engine with rule-based operator placement. *VBASE* (OSDI 2023) unifies vector and scalar/relational predicates via a "relaxed monotonicity" traversal, enabling correct filtered top-$k$ without a full cost model. Learned auto-tuners: *VDTuner*, and Bayesian-optimization knob tuners for Milvus/Faiss.
- **Theory-SOTA.** No general predictive recall–cost model with guarantees; analytic IVF cell-occupancy models and LID-based difficulty predictors are the closest.

## 4. Upper Bound

There is no algorithmic "upper bound" in the complexity sense; the achievable target is *estimator accuracy*. Best current practice predicts the recall–latency curve within single-digit-percent error for fixed workloads using offline calibration plus LID/distance-distribution features, and uses Bayesian optimization to find near-optimal knobs in $O(\text{tens})$ trials. Selectivity-aware plan choice (pre- vs. post-filter) is solved heuristically by comparing $s\,n$ against a crossover threshold.

## 5. Lower Bound

The hardness is statistical/learning-theoretic rather than NP-hardness: predicting recall for an *unseen* query is bounded by the difficulty of estimating high-dimensional density (curse of dimensionality in nonparametric estimation, with sample complexity exponential in intrinsic dimension). Worst-case adversarial query distributions can make any fixed cost model arbitrarily wrong (no distribution-free guarantee), echoing impossibility of distribution-free selectivity estimation. Optimizer-error propagation (Ioannidis–Christodoulakis) shows estimation errors compound multiplicatively across operators, bounding any plan-ranking guarantee.

## 6. The Gap

The gap is between hand-tuned, per-workload calibrated models (good in practice) and a **portable, query-adaptive, recall-aware** cost model usable by a general optimizer for arbitrary hybrid queries. It is genuinely **open**: no model robustly predicts recall under distribution shift, varying selectivity, and changing index state. Closing it needs (a) cheap online difficulty estimators per query, and (b) a calculus composing ANN cost/recall with relational operators.

## 7. Current Research (as of June 2026)

- Recall prediction from per-query features (LID, margin to $k$-th neighbor) feeding cost-based planners *(frontier — verify)*.
- Unified relational + vector optimizers extending VBASE-style relaxed monotonicity into Postgres/DuckDB/SingleStore.
- Learned and Bayesian knob auto-tuning (VDTuner-style) with recall SLAs.
- Selectivity-aware filtered ANN: ACORN (SIGMOD 2024) predicate-agnostic graph traversal; cost crossover modeling for pre/post-filter.
- Groups: Zilliz/Milvus, Microsoft (VBASE), Stanford (ACORN/FlexANN line), pgvector community.

## 8. Future Work

- A first-principles recall model from the local distance distribution with confidence intervals.
- Integration into dynamic-programming join enumeration so ANN can be pushed below/above joins correctly.
- Robustness to distribution shift and index aging.
- Multi-objective optimization exposing the recall–latency–cost frontier as a planner-visible Pareto set.

## 9. Key References

- **[Foundational]** Patricia G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Qianxi Zhang et al. *VBASE: Unifying Online Vector Similarity Search and Relational Queries via Relaxed Monotonicity.* OSDI, 2023. — [USENIX](https://www.usenix.org/conference/osdi23/presentation/zhang-qianxi)
- **[SOTA]** Chuangxian Wei et al. *AnalyticDB-V: A Hybrid Analytical Engine Towards Query Fusion for Structured and Unstructured Data.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3415478.3415541)
- **[SOTA]** Liana Patel et al. *ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data.* SIGMOD, 2024. — [arXiv](https://arxiv.org/abs/2403.04871) — [DBLP](https://dblp.org/rec/journals/corr/abs-2403-04871.html)
- **[Foundational]** Michael E. Houle. *Local Intrinsic Dimensionality I: An Extreme-Value-Theoretic Foundation for Similarity Applications.* SISAP, 2017. — [DOI](https://doi.org/10.1007/978-3-319-68474-1_5)
- **[Foundational]** Yannis E. Ioannidis, Stavros Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991. — [DOI](https://doi.org/10.1145/115790.115835)

## 10. Worked Example

**IVF cost/recall and a pre- vs. post-filter crossover.** Index $n{=}1{,}000{,}000$ vectors with $C{=}1000$ IVF cells, balanced cell size $n/C{=}1000$. Empirically the recall curve fits $R(p)\approx 1-e^{-\gamma p}$ with $\gamma{=}0.5$. To hit $R_0{=}0.90$ we need $1-e^{-0.5p}\ge 0.9 \Rightarrow p\ge \ln(10)/0.5 \approx 4.6$, so $p{=}5$ probes, reading $\approx p\cdot n/C = 5000$ vectors per query.

Now add a metadata predicate of selectivity $s{=}0.002$ (2000 matching rows).

- **Post-filter:** run ANN ($5000$ distance evals), then keep only matches. But of the $\approx k$ returned, a fraction $\approx s$ survive — to return top-$k{=}10$ matches you must over-fetch $\sim k/s = 5000$ candidates, blowing up probes.
- **Pre-filter then exact:** scan the $s\,n = 2000$ matching vectors directly: $2000$ distance evals, exact recall.

Crossover: pre-filter wins when $s\,n < $ the probes post-filter needs. Here $2000 < 5000$, so the planner should pre-filter. The crossover threshold is roughly $s^\* n \approx p\,n/C$, i.e. $s^\* \approx p/C = 5/1000 = 0.005$; any $s < 0.005$ favors the exact pre-filter scan.

---
*Part of the [DBMS Research catalog](../../README.md).*
