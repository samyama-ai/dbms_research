# Cardinality Estimation Benchmarks & Metrics

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/ce-benchmarks-and-metrics` · **Status:** empirically-open

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

- **[Foundational]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really? (Join Order Benchmark).* VLDB, 2015.
- **[Foundational]** Moerkotte, Neumann, Steinbrunn. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009.
- **[SOTA]** Negi, Marcus, Kipf, Mao, Tatbul, Kraska, Alizadeh. *Flow-Loss: Learning Cardinality Estimates that Matter.* VLDB, 2021.
- **[Survey/SOTA]** Han, Wu, Wang, et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation (STATS-CEB).* VLDB, 2022.
- **[Survey/SOTA]** Wang, Qu, Li, Cui, et al. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021.
- **[SOTA]** Negi, Marcus, Mao, Tatbul, Kraska, Alizadeh. *Cardinality Estimation Benchmark (CEB).* (artifact/workload), 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
