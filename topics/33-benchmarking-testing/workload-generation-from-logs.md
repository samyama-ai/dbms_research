---
id: 33-benchmarking-testing/workload-generation-from-logs
title: "Realistic Workload Generation from Logs"
topic: 33-benchmarking-testing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Realistic Workload Generation from Logs

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/workload-generation-from-logs` · **Status:** empirically-open

## 1. Problem Statement

Given an anonymized production query/transaction log $L$ (arrival times, query templates, parameter values, transaction structure), synthesize a benchmark workload $\hat{L}$ — and possibly a synthetic database — that **statistically matches** $L$, including parameter **skew**, inter-query/column **correlations**, temporal **burstiness**, and transaction mix, while satisfying a **privacy** constraint (the log is anonymized; synthesis must not leak sensitive values).

Variants:
- **Workload-only:** reproduce the query/transaction stream against an existing schema/data.
- **Joint data+workload:** also synthesize data whose distribution makes query selectivities/plans match production.
- **Private variant:** generate under differential privacy or a formal anonymization guarantee.

## 2. Mathematical Foundations

Treat the log as samples from a joint distribution $\mathcal{D}$ over (template $t$, parameters $\theta$, arrival time $\tau$, txn shape). The goal is a generator $G$ whose output distribution $\hat{\mathcal{D}}$ minimizes a divergence
$$ \min_G\ d\big(\mathcal{D},\hat{\mathcal{D}}\big),\qquad d\in\{\text{KL},\ \text{Wasserstein},\ \text{MMD}\}, $$
subject to a **fidelity-on-metrics** constraint: induced selectivities, plan-shape mix, latency/throughput, and lock-contention should match. Correlations across parameters require modeling the *joint* (copulas, graphical models, autoregressive/transformer density models) rather than per-column marginals. Temporal structure is a marked point process (Hawkes / non-homogeneous Poisson) for burstiness.

Privacy is formalized via **$(\varepsilon,\delta)$-differential privacy**: $G$ trained on $L$ vs. $L'$ differing in one log entry must satisfy $\Pr[G\in O]\le e^{\varepsilon}\Pr[G'\in O]+\delta$. There is a **fidelity-privacy tradeoff**: tighter $\varepsilon$ provably bounds how well correlations/skew can be reproduced (lower bounds from DP estimation). Matching *plan behavior* also depends on the synthetic data, so workload and data generation are **coupled** through selectivity functions.

## 3. State of the Art (SOTA)

- **Benchmark synthesis:** **MyBenchmark / "generating realistic database benchmarks"** lineage and **OLTP-Bench / BenchBase** (Difallah et al., VLDB 2013) provide configurable mixes but draw distributions from templates, not learned from logs.
- **Data generation matching constraints:** **QAGen** (Binnig et al., SIGMOD 2007) and **MyBenchmark** generate data so queries hit target cardinalities; **DataSynth/Touchstone** (Li et al., 2018) scale this to schema-wide cardinality constraints.
- **Learned generative models:** transformer/autoregressive and GAN/copula models for relational data (e.g., CTGAN lineage) capture skew and correlation; learned **cardinality-estimation** density models (Naru/DeepDB) double as data/workload synthesizers.
- **Private synthesis:** DP synthetic-data systems (PrivBayes, and DP-SGD generative models) provide $(\varepsilon,\delta)$ guarantees but with fidelity loss on tail correlations.
- No single system jointly matches correlation+skew+temporal structure from a real log *with* privacy — hence empirically-open.

## 4. Upper Bound

Density estimation of $\mathcal{D}$ from $n$ log entries achieves error decreasing as $O(n^{-1/2})$ for parametric models and $O(n^{-1/(2+\dim)})$ nonparametric (curse of dimensionality), so correlation fidelity needs sample sizes exponential in the number of correlated columns in the worst case. Touchstone-style cardinality matching solves the data-generation subproblem in polynomial time for conjunctive constraints. Under DP, utility upper bounds degrade by factors $\sim 1/\varepsilon$ on each statistic released.

## 5. Lower Bound

- **Privacy lower bounds:** any $(\varepsilon,\delta)$-DP mechanism incurs additive error $\Omega(\sqrt{d}/\varepsilon)$ (or worse) to release $d$ correlated statistics (fingerprinting / tracing-attack lower bounds, Bun-Ullman-Vadhan, Dwork et al.) — fundamentally bounding correlation fidelity under privacy.
- **Statistical:** estimating a high-order joint to fixed accuracy needs sample size exponential in the order of interactions (information-theoretic).
- **Hardness of matching plan behavior:** choosing data/parameters so a generated query attains a target plan/selectivity is at least **NP-hard** (encodes constraint satisfaction over selectivity equations; cf. QAGen).
- *Empirically-open* because the field measures success by fidelity metrics on real logs, with no agreed optimum or matching bound.

## 6. The Gap

The gap is between (a) systems that reproduce *marginal* skew or single-column cardinalities well and (b) the goal of reproducing *joint* correlations, temporal burstiness, and transaction structure **simultaneously, privately**. DP lower bounds prove some correlation fidelity is unrecoverable at small $\varepsilon$; outside privacy, the practical gap is the lack of a generator that provably matches a chosen fidelity metric on real production logs. No clean theoretical optimum is known, so progress is empirical.

## 7. Current Research (as of June 2026)

- **Transformer/diffusion generative models** for joint query+parameter+timing synthesis from logs *(frontier — verify)*.
- **DP workload synthesis** trading $\varepsilon$ against correlation fidelity with explicit error reporting *(frontier — verify)*.
- Coupled data+workload generation so synthetic plans match production plan mix.
- Groups: Andy Pavlo / CMU (BenchBase/OLTP-Bench), Carsten Binnig (TU Darmstadt, QAGen lineage), learned-DB groups (Kraska et al.), DP-synthetic-data community (Ullman, Vadhan, McKenna).

## 8. Future Work

- Standard fidelity metrics for "workload realism" (beyond throughput): correlation, skew, burstiness, contention.
- Generators with *certified* fidelity or DP guarantees on stated statistics.
- Drift-aware synthesis tracking non-stationary production workloads.
- Joint optimization of synthetic schema, data, and workload for plan-level realism.

## 9. Key References

- **[Foundational]** C. Binnig, D. Kossmann, E. Lo, M. T. Özsu. *QAGen: Generating Query-Aware Test Databases.* SIGMOD, 2007. — [DOI](https://doi.org/10.1145/1247480.1247520)
- **[SOTA]** D. E. Difallah, A. Pavlo, C. Curino, P. Cudré-Mauroux. *OLTP-Bench: An Extensible Testbed for Benchmarking Relational Databases.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2732240.2732246)
- **[SOTA]** Y. Li, R. Zhang, X. Yang, Z. Zhang, A. Zhou. *Touchstone: Generating Enormous Query-Aware Test Databases.* USENIX ATC, 2018. — [DBLP](https://dblp.org/rec/conf/usenix/LiZYZZ18.html)
- **[Foundational]** C. Dwork, A. Roth. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in TCS, 2014. — [DOI](https://doi.org/10.1561/0400000042)
- **[Foundational]** J. Zhang, G. Cormode, C. M. Procopiuc, D. Srivastava, X. Xiao. *PrivBayes: Private Data Release via Bayesian Networks.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588573)
- **[SOTA]** Z. Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019. — [DOI](https://doi.org/10.14778/3368289.3368294)

## 10. Worked Example

**Why marginals are not enough — and the DP cost.** A log has two parameter columns, `country` and `currency`, with the joint over 4 entries: $(\text{US},\text{USD})\times 40$, $(\text{EU},\text{EUR})\times 40$, $(\text{US},\text{EUR})\times 1$, $(\text{EU},\text{USD})\times 1$, total $n=82$.

The **marginals** are nearly uniform: $P(\text{US})\approx P(\text{EU})\approx 0.5$, $P(\text{USD})\approx P(\text{EUR})\approx 0.5$. A per-column generator samples them independently, producing $\approx 25\%$ mass on each cell — so it emits the rare $(\text{US},\text{EUR})$ pair $\sim20$ instead of $\sim1$ times, badly mismatching selectivities (a query `WHERE country='US' AND currency='EUR'` hits $\sim20\times$ too many rows). Capturing the true $\rho\approx 0.95$ correlation requires modeling the **joint** (e.g. a 2-way marginal / copula).

Now add **$(\varepsilon,\delta)$-DP** at $\varepsilon=1$: releasing the $2\times2$ contingency table adds Laplace noise of scale $1/\varepsilon = 1$ per cell. The two rare cells (true count $1$) are swamped — noise std $\approx\sqrt{2}\approx1.4 > 1$ — so the sign of the correlation is no longer recoverable. This is the fingerprinting lower bound in miniature: additive error $\Omega(\sqrt{d}/\varepsilon)$ over $d$ correlated statistics fundamentally limits joint-fidelity under privacy.

---
*Part of the [DBMS Research catalog](../../README.md).*
