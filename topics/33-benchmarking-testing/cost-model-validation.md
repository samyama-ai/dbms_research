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

- **[SOTA]** V. Leis, A. Gubichev, A. Mirchev, P. Boncz, A. Kemper, T. Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015.
- **[Foundational]** P. G. Selinger, M. Astrahan, D. Chamberlin, R. Lorie, T. Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** N. Reddy, J. R. Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005.
- **[Foundational]** T. Ibaraki, T. Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984.
- **[SOTA]** R. Marcus, P. Negi, H. Mao, N. Tatbul, M. Alizadeh, T. Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
