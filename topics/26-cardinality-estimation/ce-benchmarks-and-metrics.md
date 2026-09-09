---
id: 26-cardinality-estimation/ce-benchmarks-and-metrics
title: "Cardinality Estimation Benchmarks & Metrics"
topic: 26-cardinality-estimation
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-07
last_substantive_update: 2026-07
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cardinality Estimation Benchmarks & Metrics

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/ce-benchmarks-and-metrics` · **Status:** empirically-open
> **Verification note:** The q-error paper's third author is Gabriele Steidl, not "Steinbrunn" (Moerkotte, Neumann, Steidl, VLDB 2009); the §9 citation has been corrected accordingly.

## 1. Problem Statement

How we *measure* a cardinality estimator determines what we optimize for. The problem: **define benchmark workloads and error metrics whose values reliably predict downstream optimization quality** — so that "better on the benchmark" implies "better plans in production."

Variants:

- **Metric design (decision):** find an error metric $M(\hat c, c)$ such that lower $M$ provably/empirically implies lower plan regret across optimizers.
- **Workload design (coverage):** construct query sets that exercise the failure modes that matter (correlated multi-column predicates, many-way and cyclic joins, skew, updates, OOD shift) without overfitting to one schema.
- **Evaluation protocol:** train/test splits, update/drift scenarios, and reporting (median vs tail) that prevent misleading single-number claims.

This matters because median q-error — the field's default — hides the tail errors that actually break plans, and per-table single-join benchmarks miss the join-crossing correlations where estimators fail worst.

## 2. Mathematical Foundations

For estimate $\hat c$ and truth $c$, candidate metrics: **q-error** $\max(\hat c/c, c/\hat c)$ (multiplicative, scale-free, plan-cost relevant — Moerkotte et al.); relative/absolute error; **log-error** $|\log\hat c-\log c|$; and aggregate statistics over a workload (mean, percentiles, max). A metric is *plan-faithful* if $M_1(\hat c)\le M_2(\hat c')\Rightarrow \mathbb E[\rho_1]\le\mathbb E[\rho_2]$ where $\rho$ is plan regret — a stochastic-dominance condition that q-error satisfies only loosely.

Foundations:

- **q-error → plan-cost bound** (VLDB 2009): bounding *max* q-error bounds suboptimality; this privileges the **tail** ($L_\infty$), not the median, so median-based reporting is theoretically unjustified for plan quality.
- **Benchmark validity** is a measurement-theory question: a benchmark must have **construct validity** (measures plan-relevant accuracy) and **external validity** (transfers to unseen schemas) — properties one can test via correlation between benchmark metric and measured end-to-end runtime regret.
- **Workload complexity** can be characterized by join-graph structure (acyclic vs cyclic, treewidth), predicate correlation strength, and distribution-shift distance between train/test splits.

## 3. State of the Art (SOTA)

- **Workload-SOTA:** **Join Order Benchmark (JOB)** over IMDb (Leis et al., VLDB 2015) — realistic correlations, the de-facto plan-quality benchmark; **STATS-CEB / the CE benchmark** (Han et al., VLDB 2022) — diverse multi-join queries with true cardinalities and update scenarios; **CEB** (Negi et al.) — large generated workloads with labels; **job-light** for quick learned-CE tests.
- **Metric-SOTA:** q-error is standard; **Flow-Loss** (Negi et al., VLDB 2021) optimizes a differentiable surrogate of plan cost instead of q-error, explicitly targeting plan-faithfulness; runtime/plan-regret reporting in the "Are We Ready…" study (Wang et al., VLDB 2021).
- *(frontier — verify)* recent benchmarks add drift/update axes and tail-q-error and regret as first-class reported metrics.
- **Regret-regime metrics (2026):** framing metric-faithfulness as error propagation through the plan-selection argmin yields *ACS* (average-case sub-optimality) — a cardinality-free closed form that empirically predicts large-error query regret on STATS-CEB (Spearman $\rho\approx0.54$) and on *real* PostgreSQL runtime ($\rho\approx0.42$) where q-error does not ($\rho\approx0.05$ / $-0.16$); it positions q-error, ACS, and worst-case MSO (Haritsa plan diagrams) as small-/large-/worst-case regret regimes. Modest delta over Wolf's per-plan robustness (VLDB 2018) and Moerkotte's $q^4$ bound, both credited (Samyama, arXiv:2606.15600).

## 4. Upper Bound

This is a methodological problem, so "bounds" are about metric guarantees:

- **q-error provides a one-directional guarantee:** bounded max q-error upper-bounds plan suboptimality (Moerkotte et al.) — so $L_\infty$ q-error is a *valid* (if loose) proxy.
- **Flow-Loss** is a computable differentiable surrogate that empirically tracks plan cost more tightly than q-error; it gives no worst-case guarantee but better correlation.
- A benchmark's predictive validity is upper-bounded by how well its metric correlates with measured regret — directly estimable, not a closed-form bound.

## 5. Lower Bound

- **No single scalar suffices:** because plan regret is a step function of the full estimate vector (see plan-cost-sensitivity), no per-query scalar metric can be perfectly plan-faithful across all optimizers/cost models — a metric good for one cost model can mis-rank for another (impossibility by construction).
- **Median is provably misleading:** instances exist where estimator A has lower median q-error but higher max q-error and strictly worse plans than B — so median-based ranking has no soundness.
- **Coverage hardness:** generating workloads that provably exercise all hard cases reduces to enumerating worst-case join structures, which is combinatorially large (exponential families of cyclic/treewidth-bounded queries).

## 6. The Gap

We have good *workloads* (JOB, STATS-CEB) but no *metric* that is both cheap and provably plan-faithful, and no consensus protocol for drift/updates and tail reporting. The gap is **empirically open**: Flow-Loss and runtime-based evaluation point the right way but lack guarantees and broad adoption. Closing it needs a metric with stochastic-dominance guarantees over a stated optimizer class, plus standardized OOD/update splits.

## 7. Current Research (as of June 2026)

- Plan-cost-aware surrogates (Flow-Loss and successors) and end-to-end runtime-regret leaderboards *(frontier — verify)*.
- Drift/update benchmarks (STATS-CEB with insertions; dynamic-workload suites).
- Tail-focused reporting (p99/p99.9 q-error) replacing median; per-subplan error attribution.
- Active groups: TUM (Leis/Neumann/Kemper, JOB), MIT (Negi, Kraska, Flow-Loss/CEB), and STATS-CEB authors (Han et al.); reproducibility efforts in the VLDB/SIGMOD communities.

## 8. Future Work

- A standardized, plan-faithful metric with guarantees and broad agreement.
- Multi-schema benchmarks testing external validity (not just IMDb).
- Mandatory drift/update and tail reporting in CE papers.
- Cost-model-agnostic regret metrics so rankings transfer across engines (ties to cross-engine transfer).

## 9. Key References

- **[Foundational]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really? (Join Order Benchmark).* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594), [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)
- **[Foundational]** Moerkotte, Neumann, Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009. — [DOI](https://doi.org/10.14778/1687627.1687738), [DBLP](https://dblp.org/rec/journals/pvldb/MoerkotteNS09.html)
- **[SOTA]** Negi, Marcus, Kipf, Mao, Tatbul, Kraska, Alizadeh. *Flow-Loss: Learning Cardinality Estimates that Matter.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3476249.3476259), [arXiv](https://arxiv.org/abs/2101.04964)
- **[Survey/SOTA]** Han, Wu, Wu, et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation (STATS-CEB).* VLDB, 2022. — [DOI](https://doi.org/10.14778/3503585.3503586), [arXiv](https://arxiv.org/abs/2109.05877)
- **[Survey/SOTA]** Wang, Qu, Wu, Wang, Zhou. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021. — [DOI](https://doi.org/10.14778/3461535.3461552), [DBLP](https://dblp.org/rec/journals/pvldb/WangQWWZ21.html)
- **[Artifact]** Negi, Marcus, Mao, Tatbul, Kraska, Alizadeh. *Cardinality Estimation Benchmark (CEB).* (artifact/workload), 2021. — [GitHub](https://github.com/learnedsystems/CEB)
- **[SOTA]** Samyama Research. *When Does q-error Predict Plan Regret? Three Regimes of Cardinality-Estimation Error.* arXiv:2606.15600 (cs.DB), 2026. — [arXiv](https://arxiv.org/abs/2606.15600) · [code](https://github.com/samyama-ai/ce-metric-eval)

## 10. Worked Example

Why median q-error misleads. Two estimators run on a 5-query workload (true cardinalities $c$, estimates $\hat c$); q-error is $\max(\hat c/c,\ c/\hat c)$.

| query | $c$ | $\hat c_A$ | q-err A | $\hat c_B$ | q-err B |
|---|---|---|---|---|---|
| $q_1$ | 100 | 130 | 1.3 | 50  | 2.0 |
| $q_2$ | 100 | 70  | 1.43 | 60 | 1.67 |
| $q_3$ | 100 | 120 | 1.2 | 55  | 1.82 |
| $q_4$ | 100 | 80  | 1.25 | 65  | 1.54 |
| $q_5$ | $10^6$ | $10^3$ | **1000** | $4\times10^5$ | 2.5 |

**Median q-error:** A = 1.3, B = 1.82 — A "wins." **Max q-error:** A = 1000, B = 2.5 — B wins by a wide margin. Estimator A's catastrophic $1000\times$ under-estimate on $q_5$ (the large join) is exactly the tail error that drives the optimizer into an unbounded nested-loop, yet it is invisible to the median. Moerkotte et al.'s bound is on **max** q-error: if $\max$ q-error $\le \sqrt{2}$ over a plan's subexpressions, the chosen plan is provably within a bounded factor of optimal — so the $L_\infty$ statistic, not the median, is the plan-faithful one. Ranking by median here gives the wrong winner.

---
*Part of the [DBMS Research catalog](../../README.md).*
