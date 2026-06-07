---
id: 33-benchmarking-testing/cost-model-validation
title: "Cost-Model Validation and Calibration"
topic: 33-benchmarking-testing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cost-Model Validation and Calibration

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/cost-model-validation` · **Status:** open

## 1. Problem Statement

A query optimizer chooses plans by a **cost model** — a function $C(p)$ estimating the runtime of plan $p$ from cardinality estimates and per-operator cost constants (CPU tuple cost, I/O page cost, random-vs-sequential ratios). The model is rarely validated against reality. The problem: **empirically validate, falsify, and calibrate** a cost model against *measured* execution across hardware (disk/SSD/NVMe, cache sizes, cores) and data regimes (size, skew, correlation).

Variants:
- **Validation (decision) variant:** does $C$ rank plans consistently with measured runtime? (Ordering correctness matters more than absolute accuracy.)
- **Calibration (optimization) variant:** fit cost constants $\theta$ to minimize a loss over measured plans — and detect when *no* parameterization suffices (a structural model defect).
- **Falsification variant:** construct query/data instances where the model's plan choice is provably suboptimal vs. measurement.
- **Counting/diagnosis variant:** quantify what fraction of regret is due to *cardinality* error vs. *cost-constant* error vs. *model-form* error.

## 2. Mathematical Foundations

Let true runtime be $T(p)$ and the model $C_\theta(p)$. Two distinct goals: **ordering accuracy** — for the chosen plan $\hat p = \arg\min_p C_\theta(p)$, the **regret** is $T(\hat p) - \min_p T(p)$; and **estimation accuracy** $|C_\theta(p) - T(p)|$. Ordering accuracy is what governs plan quality; a model can be numerically wrong yet *order-preserving* (a monotone transform of truth) and still optimal. The right validation metric is therefore rank correlation (Kendall's $\tau$, Spearman) and worst-case regret, not RMSE.

Calibration fits $\theta$ by regression: if $C_\theta(p)=\theta^\top \phi(p)$ is **linear** in cost features $\phi(p)$ (page reads, tuples processed, comparisons), least squares gives $\hat\theta=(\Phi^\top\Phi)^{-1}\Phi^\top T$, and **identifiability** requires $\Phi$ to have full column rank — degeneracies arise when features are collinear across the available plan corpus. A central decomposition (Leis et al.) separates error sources: plan regret $\approx$ f(**cardinality estimation error**) $\times$ f(**cost-model error**). Empirically, cardinality error dominates; with *true* cardinalities injected, even a simple cost model often suffices — a key falsifiability experiment ("plan diagrams" / Picasso, Haritsa).

## 3. State of the Art (SOTA)

- **"How Good Are Query Optimizers, Really?"** (Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann; VLDB 2015) — the canonical validation study; introduced the **Join Order Benchmark (JOB)**, isolated cardinality vs. cost error, and showed cardinality estimation is the dominant culprit. Still the systems-SOTA methodology.
- **Picasso / Plan Diagrams** (Reddy & Haritsa; VLDB 2005) — visualizing optimizer plan choices over a selectivity space to expose cost-model anomalies and non-robustness.
- **Learned cost models:** **MSCN** (Kipf et al., CIDR 2019) for cardinality; **Neo / Bao** (Marcus et al., VLDB 2019 / SIGMOD 2021) learn plan-level cost/steering; **End-to-End Learned Cost Models** (Sun & Li, VLDB 2019). These largely *replace* the analytic model rather than validate it.
- **Calibration tooling:** PostgreSQL's `*_cost` GUCs are tuned by hand/heuristics; academic auto-calibration via micro-benchmarking per-operator constants on the target hardware.

## 4. Upper Bound

Linear-in-features cost calibration is solved exactly by least squares in $O(d^3 + nd^2)$ for $n$ measured plans and $d$ features, with confidence intervals on each constant. Validation by rank correlation over a plan corpus is $O(m\log m)$ per query. Constructing *the* optimal plan to measure regret is the optimizer's own job (join ordering is NP-hard, but DP solves it for moderate relation counts; **IK-KBZ** is polynomial for acyclic/linear cost). So the *measurement and fitting* side is tractable; the binding limitation is sampling — you cannot execute the combinatorially many plans, so validation rests on a sampled corpus and gives only *empirical* coverage of the cost surface.

## 5. Lower Bound

The obstacles are statistical/empirical, not a single complexity theorem. (1) **Cardinality estimation** — on which any cost model depends — has worst-case error that is provably unbounded: estimators built from limited statistics can be off by factors growing with join depth (multiplicative error compounds), and lower bounds on synopsis size (sketches, sampling) force a space/accuracy tradeoff (information-theoretic). (2) **Join-order optimization** with arbitrary cost functions is **NP-hard** (Ibaraki–Kameda), so exhaustively *finding* the optimum to measure regret is intractable at scale — regret is estimated, not certified. (3) There is no ground-truth cost function to test against except measurement, which is itself noisy (see continuous-benchmarking), so absolute falsification of a model form requires a regime-spanning experimental design with irreducible variance.

## 6. The Gap

Open. The validation *methodology* exists (Leis et al., Picasso) and shows the dominant error is cardinality, not the cost constants — yet there is **no standard, falsifiable validation suite** that (a) spans hardware regimes (NVMe vs. spinning, cache hierarchy, parallelism), (b) separates the three error sources quantitatively, and (c) yields *actionable* recalibration. Learned models improve average accuracy but are not interpretable as validations of the analytic model and have their own robustness/falsifiability problems. Closing the gap means a reproducible cross-hardware benchmark + an identifiable calibration procedure that flags *model-form* defects (where no $\theta$ fits), not just refits constants.

## 7. Current Research (as of June 2026)

- Robust/learned cost models with uncertainty quantification and out-of-distribution detection (Bao/Neo lineage; Marcus, Kraska groups) *(frontier — verify)*.
- Hardware-aware calibration auto-tuning per-operator constants via micro-benchmarks on the deployment machine *(frontier — verify)*.
- Disentangling cardinality vs. cost error with counterfactual "true-cardinality" execution at scale, extending the Leis methodology to cloud and columnar/vectorized engines.
- Cost-model validation for vectorized/JIT engines (DuckDB, Velox) where classic page-based assumptions break down *(frontier — verify)*.

## 8. Future Work

- A public cross-hardware, cross-data-regime cost-model validation benchmark with ground-truth measurements.
- Identifiability theory: when is a cost model's parameter vector recoverable from a feasible plan corpus?
- Falsification tests that pinpoint structural model defects (vectorization, NUMA, prefetching) rather than refitting constants.
- Hybrid analytic+learned models that remain interpretable and validatable.

## 9. Key References

- **[SOTA]** V. Leis, A. Gubichev, A. Mirchev, P. Boncz, A. Kemper, T. Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594) · [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)
- **[Foundational]** P. G. Selinger, M. Astrahan, D. Chamberlin, R. Lorie, T. Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** N. Reddy, J. R. Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/ReddyH05.html)
- **[Foundational]** T. Ibaraki, T. Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1270.1498)
- **[SOTA]** R. Marcus, P. Negi, H. Mao, N. Tatbul, M. Alizadeh, T. Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677) · [DBLP](https://dblp.org/rec/conf/cidr/KipfKRLBK19.html)

## 10. Worked Example

Consider a 3-table join with two candidate plans for $R\bowtie S\bowtie T$. The optimizer's cost model $C$ and the *measured* runtimes $T$ (ms):

| Plan | feature: page reads $\phi_1$ | feature: tuples $\phi_2$ | $C_\theta$ (with $\theta=(0.5,\,0.002)$) | measured $T$ |
|------|------|------|------|------|
| $A$: $(R\bowtie S)\bowtie T$ | 1000 | 50000 | $500+100=600$ | 540 |
| $B$: $R\bowtie(S\bowtie T)$ | 4000 | 80000 | $2000+160=2160$ | 410 |

The model picks $\hat p=A$ (lower $C$), but measurement shows $B$ is faster. **Regret** $=T(A)-\min(T)=540-410=130$ ms. Crucially, ordering is *inverted* even though both cost numbers are internally plausible — so RMSE on $C$ would not reveal the failure; **Kendall's $\tau$** between $(C_A,C_B)$ and $(T_A,T_B)$ is $-1$ (perfectly anti-correlated on this pair). Diagnosis: plan $B$'s inner join $S\bowtie T$ was badly *under-estimated* in cardinality (the 80000 feature was actually ~20000 at runtime, fitting in cache), so the error is **cardinality-driven**, not a cost-constant defect — refitting $\theta$ won't fix it, matching the Leis et al. finding that cardinality dominates.

---
*Part of the [DBMS Research catalog](../../README.md).*
