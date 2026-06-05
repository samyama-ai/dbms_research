# Cardinality-Estimator Accuracy Benchmarking

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/cardinality-estimator-benchmarking` · **Status:** partially-solved

## 1. Problem Statement
A cardinality estimator maps a query (predicate + join graph) to a predicted output size $\hat{c}$; the optimizer consumes $\hat{c}$ to choose plans. The benchmarking problem is to construct workloads, datasets, and a ground-truth methodology that **fairly and reproducibly** compare estimators across *correlation regimes* (independent, functionally dependent, skewed, anti-correlated) without overfitting to one benchmark's idiosyncrasies.

Three sub-problems must be distinguished:
- **Measurement (counting/decision):** compute exact ground-truth cardinalities $c$ for every (sub)query — itself a counting problem (`COUNT(*)` over joins) that is expensive at scale.
- **Metric design (optimization):** choose an error functional $\mathcal{L}(\hat{c}, c)$ that correlates with *end-to-end plan quality*, not just with prediction error.
- **Coverage:** guarantee the workload exercises the correlation structures and intermediate-result explosions where estimators actually fail.

A "solution" is a benchmark + protocol such that an estimator's score predicts its production plan-regression rate.

## 2. Mathematical Foundations
Let $Q$ be a conjunctive query over relations $R_1,\dots,R_n$. The true cardinality is $c(Q)=|Q(\mathbf{D})|$. Worst-case output size is bounded by the **AGM bound**: for a fractional edge cover $\mathbf{x}$ of the hypergraph of $Q$,
$$|Q(\mathbf{D})| \le \prod_{i} |R_i|^{x_i}.$$
Independence-based estimators implicitly assume $c \approx |R_1|\cdots|R_n|\cdot\prod_p \text{sel}(p)$, which fails precisely when attribute correlations break the product form.

Error metrics in common use:
- **q-error** $\max(\hat{c}/c,\, c/\hat{c})$ — multiplicative, symmetric, and the quantity Selinger-style plan-cost monotonicity arguments bound. Moerkotte et al. show q-error of $q$ bounds plan-cost suboptimality by a factor polynomial in $q$ for certain cost models.
- relative error, log-error, and **P-error** (plan-induced error: cost gap of the plan chosen under $\hat{c}$ vs. optimal).

Coverage can be framed via the **VC dimension** of the predicate class and via the *correlation entropy* $H(\text{attrs}) - \sum_i H(\text{attr}_i)$ (mutual-information mass) of the data, giving a principled axis along which to stratify workloads.

## 3. State of the Art (SOTA)
- **Systems-SOTA benchmarks:** **JOB** (Join Order Benchmark, Leis et al., VLDB 2015) over IMDb — the de facto correlated real-data workload. **STATS-CEB** (Han et al., VLDB 2021) adds true sub-query cardinalities and a P-error-style evaluation. **CEB** (Cardinality Estimation Benchmark) and **DSB** (Decision Support Benchmark, derived from TPC-DS with skew/correlation injection, Ding et al. 2021).
- **Methodology-SOTA:** Han et al.'s end-to-end protocol that *replaces* the optimizer's estimates with each method's and measures actual runtime — the strongest "fairness" advance, isolating estimator quality from cost-model/plan-search noise.
- **Estimator families benchmarked:** sampling (WJ, IBJS), classic histograms/sketches, learned data-driven (Naru/DeepDB/FLAT) and query-driven (MSCN, LW-NN) models.

## 4. Upper Bound
Exact ground-truth counting of all sub-queries is the cost driver. With join sampling, an $(\varepsilon,\delta)$ estimate of $c$ is obtainable in $\tilde{O}(\text{AGM}/c \cdot \varepsilon^{-2}\log\delta^{-1})$ work via **worst-case-optimal join sampling** (Chen–Yi; Deng et al.), giving a tractable approximate ground truth where exact `COUNT` is infeasible. For metric monotonicity, q-error gives the best-known *plan-quality* upper bound: bounded q-error $\Rightarrow$ bounded cost ratio under monotone cost functions (Moerkotte et al., VLDB 2009).

## 5. Lower Bound
Exact counting of conjunctive-query answers is **#P-hard** in general (Provan–Ball; counting variants of join evaluation), so exact ground truth cannot scale to arbitrary workloads — this is the formal reason approximate ground truth is needed. On the metric side, an **impossibility-flavored** result: *no single scalar error metric is faithful*. One can construct two estimators with identical q-error distributions but arbitrarily different P-error, because plan choice depends on *relative* errors across competing sub-plans, not marginal per-query error — a separation argued empirically in Han et al. (2021) and formalizable via adversarial estimator pairs.

## 6. The Gap
"Partially solved": ground-truth measurement and end-to-end protocols are mature, but **metric faithfulness and coverage guarantees are open**. We lack (a) a metric provably monotone in production regression rate under realistic (non-monotone, parallel) cost models, and (b) a generative procedure that certifies a workload covers a target region of correlation-entropy / predicate-VC space. Closing it requires either a faithful composite metric with proven plan-quality bounds, or acceptance that benchmarking must be *plan-centric and cost-model-specific* rather than estimator-centric.

## 7. Current Research (as of June 2026)
- Plan-centric, cost-model-aware metrics (P-error successors) and **robustness benchmarking** under distribution shift for learned estimators *(frontier — verify)*.
- "Stress benchmarks" that *generate* correlated data to target estimator blind spots (overlaps with adversarial-workload work; CMU/TUM/Alibaba groups).
- Reproducibility infrastructure shipping true sub-query cardinalities and Docker-pinned optimizers; LLM/embedding-based estimators being added to STATS-CEB-style harnesses *(frontier — verify)*.
- Active groups: Leis (TUM/LMU), the DeepDB/learned-CE line (Binnig, TU Darmstadt), Han/Li (StatsCEB), and the WCOJ-sampling theory community (Yi, HKUST).

## 8. Future Work
- A *certified-coverage* generator parameterized by mutual-information targets.
- Composite metric with a proven bound to expected runtime regret under cost-model uncertainty.
- Drift/robustness tracks: benchmark estimators under data updates and schema/skew shift, not just static snapshots.
- Hardware- and parallelism-aware ground truth so the "cost" the metric tracks matches modern engines.

## 9. Key References
- **[Foundational]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB 2015.
- **[Foundational]** Moerkotte, Neumann, Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB 2009.
- **[SOTA]** Han, Wu, Wang, et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation (STATS-CEB).* VLDB 2021.
- **[SOTA]** Ding, Chaudhuri, et al. *DSB: A Decision Support Benchmark for Workload-Driven and Traditional Database Systems.* VLDB 2021.
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Comput., 2013.
- **[Survey]** Yang, Kandula, et al. *Are We Ready for Learned Cardinality Estimation?* VLDB 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
