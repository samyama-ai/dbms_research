---
id: 02-query-optimization/optimizer-benchmarking
title: "Reproducible benchmarking of optimizer quality"
topic: 02-query-optimization
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Reproducible benchmarking of optimizer quality

> **Topic:** Query Optimization · **ID:** `02-query-optimization/optimizer-benchmarking` · **Status:** empirically-open

## 1. Problem Statement

How do we **fairly and reproducibly measure the quality of a query optimizer** — and, critically, *isolate the planning component from the cardinality-estimation component*? A reported end-to-end runtime conflates four error sources: (1) cardinality/selectivity estimation, (2) the cost model, (3) the plan search/enumeration, and (4) the execution engine. The benchmarking problem is to design a **methodology and metrics** that attribute observed sub-optimality to the right stage and that are robust across systems, hardware, and workloads.

- **Measurement variant:** define metrics (e.g., *plan sub-optimality ratio* vs. an oracle-cardinality optimum, *P-error*, *Q-error* of estimates) that are comparable across optimizers.
- **Methodology variant:** a protocol (workloads, statistics injection, hardware controls, repetition) that is reproducible and that *holds estimation fixed* to test planning alone.
- **Why "empirically-open":** there is no theorem to prove; the open question is which empirical methodology is *sound and standard*.

## 2. Mathematical Foundations

The key analytical separation is the **two-stage decomposition** of an optimizer: estimation $\hat{c}=\textsf{est}(Q,\text{stats})$ then search $\textsf{plan}=\arg\min_{P}\text{cost}(P\mid \hat{c})$. To isolate search, one *replaces $\hat{c}$ with true cardinalities* (an **oracle**) obtained by executing subplans, then measures
$$ \text{SubOpt}(Q) = \frac{T(\textsf{plan chosen})}{T(\textsf{plan}^* \text{ under true cardinalities})}. $$
Estimation error is quantified by **Q-error** $\;Q\text{-err} = \max\big(\tfrac{\hat{n}}{n},\tfrac{n}{\hat{n}}\big)$ (Moerkotte–Neumann–Steidl), which has the theoretical virtue that bounded Q-error bounds plan cost sub-optimality. **P-error** (plan-based error; Han et al.) measures the cost gap a misestimate induces *in the optimizer's own cost space*, decoupling estimation accuracy from cost-model artifacts. The **plan space** is enormous (Catalan-number many join trees), so exhaustive oracle baselines require careful sampling or DP with materialized true cardinalities.

## 3. State of the Art (SOTA)

- **Workloads/benchmarks:** **TPC-H** and **TPC-DS** (decision support); the **Join Order Benchmark (JOB)** over IMDb (Leis et al., "How Good Are Query Optimizers, Really?") which deliberately stresses *real, skewed, correlated* data where estimation fails; **STATS-CEB** and **JOB-light** for cardinality-estimation benchmarking; **DSB** (extending TPC-DS with skew); **CEB** for learned estimators.
- **Methodology SOTA:** Leis et al. (VLDB 2015) established the now-standard recipe — inject *true* cardinalities to separate estimation from cost model and search; Han et al. (VLDB 2021) "Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation" standardized estimator comparison and introduced P-error. **OptMark** and *plan-quality* tooling, plus **OB-tuner / sniffing** harnesses, support repeatable runs.

## 4. Upper Bound

Not a complexity-bounded problem, but the *best available* methodology gives an attributable upper bound on measured sub-optimality: with oracle (true) cardinalities injected, the residual runtime gap upper-bounds the contribution of **cost model + search**; the remaining gap (real vs. oracle estimates) upper-bounds the **estimation** contribution. Q-error provides a *provable* link: a multiplicative Q-error bound $\theta$ implies a bounded factor on plan cost under a monotone cost model (Moerkotte et al.), giving a quantitative ceiling on how much estimation error can hurt planning.

## 5. Lower Bound

The fundamental obstacle is **non-identifiability / confounding**: end-to-end latency alone cannot uniquely attribute error to estimation vs. cost-model vs. search vs. engine — different fault combinations produce identical runtimes, an *information-theoretic* indistinguishability without controlled interventions (cardinality injection, fixed engine). There is also a **reproducibility lower bound** in practice: hidden state (caches, adaptive runtime, hardware variance, statistics drift) means a single number is not reproducible without specifying the full environment — analogous to the broader empirical-CS reproducibility crisis documented by SIGMOD's reproducibility program.

## 6. The Gap

The gap is **empirical, not mathematical**: there is broad agreement that *true-cardinality injection* is the right lever to isolate planning, but no community-standard, system-agnostic harness that (a) injects oracle statistics portably across PostgreSQL/commercial engines, (b) controls for adaptive runtime and hardware, and (c) reports a metric (P-error / SubOpt) that is comparable across optimizers. Closing it requires an agreed protocol + shared artifact, not a theorem. The Join Order Benchmark plus P-error are the closest to a standard but coverage of cloud/distributed and learned optimizers is incomplete.

## 7. Current Research (as of June 2026)

- **Benchmarks for learned optimizers** (Bao, Balsa, Neo, LEON) emphasizing *regression-safety* and generalization, not just mean speedup; calls for standardized train/test splits to avoid leakage. *(frontier — verify)*
- **Cardinality-estimation benchmarks** (STATS-CEB, CEB) with end-to-end *and* estimator-only metrics; debate over whether lower Q-error reliably yields better plans (P-error as the better proxy). *(frontier — verify)*
- SIGMOD/VLDB **reproducibility (artifact evaluation)** initiatives pushing containerized, re-runnable optimizer experiments.
- Methodology for **distributed/cloud** optimizer benchmarking where \$-cost and elasticity confound latency. *(frontier — verify)*

## 8. Future Work

- A portable, cross-engine true-cardinality injection and oracle-plan harness.
- Standard metrics that decompose error into estimation / cost-model / search.
- Regression-safety and worst-case (tail) metrics for learned optimizers.
- Cloud-cost-aware and distributed optimizer benchmarks with controlled variance.

## 9. Key References

- **[Foundational]** V. Leis, A. Gubichev, A. Mirchev, P. Boncz, A. Kemper, T. Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015 (Join Order Benchmark). — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[Foundational]** G. Moerkotte, T. Neumann, G. Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009 (Q-error). — [DOI](https://doi.org/10.14778/1687627.1687738)
- **[SOTA]** Y. Han et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation.* VLDB, 2021 (P-error, STATS-CEB). — [arXiv](https://arxiv.org/abs/2109.05877)
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** B. Ding et al. *DSB: A Decision Support Benchmark for Workload-Driven and Traditional Database Systems.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3484224.3484234)
- **[Survey]** TPC. *TPC-H and TPC-DS Benchmark Specifications.* Transaction Processing Performance Council. — [TPC](https://www.tpc.org/tpch/)

## 10. Worked Example

**Isolating search from estimation.** A 3-table query runs in $T=900$ ms. Inject *true* cardinalities and re-plan: the oracle-cardinality optimum runs in $T^\star=300$ ms. Then
$$\text{SubOpt} = \frac{T}{T^\star} = \frac{900}{300} = 3.0,$$
so the optimizer's plan is $3\times$ slower than the best plan achievable *if estimation were perfect*. Because true cardinalities were used to find $T^\star$, this gap is attributed to **estimation error**, not the cost model or search.

**Q-error bound in action.** Suppose the join $R\bowtie S$ has true size $n=10{,}000$ but the estimator predicts $\hat n=40{,}000$. Then $Q\text{-err}=\max(\tfrac{40000}{10000},\tfrac{10000}{40000})=4$. The Moerkotte–Neumann–Steidl theorem says plan cost under a monotone cost model degrades by at most a factor $Q^4 = 4^4 = 256$ in the worst case — a provable ceiling linking estimation accuracy to plan quality, and the reason low Q-error (or P-error) is the right knob to standardize.

---
*Part of the [DBMS Research catalog](../../README.md).*
