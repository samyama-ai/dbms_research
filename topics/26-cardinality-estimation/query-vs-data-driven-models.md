---
id: 26-cardinality-estimation/query-vs-data-driven-models
title: "Query-Driven vs Data-Driven Estimator Synthesis"
topic: 26-cardinality-estimation
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Query-Driven vs Data-Driven Estimator Synthesis

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/query-vs-data-driven-models` · **Status:** empirically-open

## 1. Problem Statement

Two paradigms dominate learned cardinality estimation. **Data-driven** models learn the joint data distribution $\Pr[A_1,\dots,A_k]$ and answer any predicate by integrating it; **query-driven** models learn a direct map (featurized query) $\mapsto$ cardinality from observed/executed queries. The problem: **decide, for a given schema, workload, and resource budget, which paradigm to synthesize — or how to combine them — to minimize downstream optimization error.**

Variants:

- **Selection (decision):** given $(D, W, \text{budget})$, predict which paradigm yields lower expected/tail q-error.
- **Synthesis (optimization):** construct a single estimator that provably dominates either pure paradigm, e.g. a hybrid that uses the workload to *correct* a data model where queries concentrate.
- **Sample/label complexity:** how many executed queries (labels) vs how much data access does each paradigm need to reach a target accuracy?

This matters because the paradigms have complementary failure modes: data-driven models are workload-agnostic but pay to model regions no query ever touches and struggle with joins/updates; query-driven models are cheap and join-aware but blind to unseen templates.

## 2. Mathematical Foundations

Let $P_D$ be the data joint and $P_W$ the query distribution over predicates $q$. A data-driven model $\hat P_D$ answers $\hat c(q)=n\!\int_{R_q}\hat P_D$; its error is governed by the **density-estimation risk** $\mathrm{KL}(P_D\Vert\hat P_D)$, which scales with the *full* support and suffers the curse of dimensionality ($O(\epsilon^{-k})$ samples for $k$ columns at accuracy $\epsilon$, nonparametrically).

A query-driven model $\hat f$ minimizes empirical risk $\frac1m\sum_i \ell(\hat f(q_i),c_i)$ over $q_i\sim P_W$; its generalization is controlled by Rademacher complexity $\hat R_m(\mathcal F)$ and degrades off the workload support (domain-shift bound $\epsilon_T\le\epsilon_S+\tfrac12 d_{\mathcal H\Delta\mathcal H}(P_W,P_{test})+\lambda$, Ben-David et al.).

The key information-theoretic distinction: data-driven learning is **distribution learning** (sample complexity set by $P_D$'s complexity); query-driven learning is **function approximation weighted by $P_W$** (effort concentrates where queries are). A hybrid corresponds to importance-weighting the density loss by $P_W$, or to a control-variate decomposition $c(q)=\underbrace{\hat c_{D}(q)}_{\text{data model}}+\underbrace{r(q)}_{\text{query-learned residual}}$.

## 3. State of the Art (SOTA)

- **Data-driven SOTA:** Naru/NeuroCard (Yang et al., VLDB 2019/2021, autoregressive joints + progressive sampling); DeepDB (Hilprecht et al., VLDB 2020, relational sum-product networks); BayesCard.
- **Query-driven SOTA:** MSCN (Kipf et al., CIDR 2019, multi-set CNN over tables/joins/predicates); LW-XGB/LW-NN lightweight regressors (Dutt et al., VLDB 2019).
- **Hybrid / comparative SOTA:** the **"Are We Ready for Learned CE?"** unified study (Wang et al., VLDB 2021) and the **"Cardinality Estimation Benchmark"** (Han et al., VLDB 2022 / STATS-CEB) empirically map when each wins; **FactorJoin** (Wu et al., SIGMOD 2023) and **DeepDB**-style factorizations blend learned per-table distributions with combinatorial join reasoning. *(frontier — verify)* recent residual-hybrid designs learn a query-driven correction on top of a data model.

## 4. Upper Bound

- **Data-driven:** with a model class realizing the true joint, range-predicate error is bounded by a function of $\mathrm{KL}(P_D\Vert\hat P_D)$ and predicate volume; achievable accuracy is limited by density-estimation sample complexity, exponential in column count for fully general correlations.
- **Query-driven:** standard ERM gives $O(\sqrt{\mathrm{VC}(\mathcal F)/m})$ excess risk *on the workload distribution*; no bound off-support.
- **Hybrid:** a control-variate/residual estimator's variance is $\le$ that of either component when the residual is well-correlated — but no general dominance theorem is known; this is the open core.

## 5. Lower Bound

- **Data-driven:** nonparametric density estimation needs $\Omega(\epsilon^{-k})$ samples for $k$ correlated columns (information-theoretic), and join-distribution modeling inherits AGM-style blow-up.
- **Query-driven:** off-workload error is unbounded (OOD impossibility); distinguishing workloads that require different models reduces to two-sample testing with dimension-dependent sample lower bounds.
- **No paradigm dominates:** one can construct $(D,W)$ pairs where each paradigm is arbitrarily better than the other (concentrated workload over complex data favors query-driven; broad workload over simple data favors data-driven), proving no universal winner exists — the choice is genuinely instance-dependent.

## 6. The Gap

The decision problem is **empirically characterized but theoretically open**: benchmarks show *which* wins on known datasets, but there is no predictive, computable criterion $\Phi(D,W,\text{budget})\to\{\text{data},\text{query},\text{hybrid}\}$ with guarantees, nor a hybrid with proven dominance. Closing it needs (a) a complexity measure capturing how "workload-aligned" $P_D$ is, and (b) a synthesis algorithm whose error provably matches the better paradigm up to constants.

## 7. Current Research (as of June 2026)

- Residual/control-variate hybrids: data model as prior, query log as correction signal *(frontier — verify)*.
- Workload-aware density learning: importance-weighting autoregressive/SPN losses toward $P_W$ to spend capacity where queries are.
- AutoML-style estimator selection / portfolio CE that picks per-query among several models.
- Active groups: Berkeley (Stoica, Yang/NeuroCard line), TUM (Kemper/Neumann), UW (Suciu/Balazinska), Microsoft Research (Chaudhuri/Narasayya, Dutt), and the CEB/STATS-CEB benchmark authors (Han et al.).

## 8. Future Work

- A predictive selector with error guarantees, validated across schemas and workloads.
- Provably dominant hybrids; clean sample/label-complexity separations between paradigms.
- Update-robust hybrids (data drift vs workload drift handled by different components).
- Cost-aware synthesis that accounts for training, storage, and inference latency, not just accuracy.

## 9. Key References

- **[SOTA]** Yang, Liang, Kamsetty, Wu, et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019; *NeuroCard.* VLDB, 2021. — [arXiv](https://arxiv.org/abs/1905.04278) — [DOI](https://doi.org/10.14778/3368289.3368294)
- **[SOTA]** Hilprecht, Schmidt, Kulessa, Molina, Kersting, Binnig. *DeepDB: Learn from Data, not from Queries!* VLDB, 2020. — [arXiv](https://arxiv.org/abs/1909.00607) — [DOI](https://doi.org/10.14778/3384345.3384349)
- **[SOTA]** Kipf, Kipf, Radke, Leis, Boncz, Kemper. *Learned Cardinalities (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677) — [PDF](https://www.cidrdb.org/cidr2019/papers/p101-kipf-cidr19.pdf)
- **[SOTA]** Dutt, Wang, Nazi, Kandula, Narasayya, Chaudhuri. *Selectivity Estimation for Range Predicates using Lightweight Models.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3329772.3329780) — [PDF](https://www.vldb.org/pvldb/vol12/p1044-dutt.pdf)
- **[Survey/SOTA]** Wang, Qu, Li, Cui, et al. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2012.06743) — [DOI](https://doi.org/10.14778/3461535.3461552)
- **[Survey/SOTA]** Han, Wu, Wang, et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation (STATS-CEB).* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2109.05877) — [DOI](https://doi.org/10.14778/3503585.3503586)

## 10. Worked Example

Table $D$ with two binary columns $(A,B)$, $n=1000$ rows, perfectly correlated: $A=B$ always. So $500$ rows have $(0,0)$ and $500$ have $(1,1)$; none have $(0,1)$ or $(1,0)$.

Consider the predicate $q:\ A=0\ \wedge\ B=1$. True cardinality $=0$.

**Data-driven** must learn the joint $P_D$. If it captures the correlation it returns $n\cdot\hat P_D(0,1)\approx0$. But a model assuming independence (a common shortcut) estimates $n\cdot P(A{=}0)P(B{=}1)=1000\cdot0.5\cdot0.5=250$ — a 250-row error from mis-modeling correlation it spent capacity trying to learn.

**Query-driven** simply needs $q$ (or a near neighbor) in its training log. If the workload $P_W$ has executed $A{=}0\wedge B{=}1$ before, it has the label $c=0$ and returns $\approx0$ directly — no joint modeling needed.

Now flip it: a *new* template $A=1\wedge B=1$ never seen in $P_W$. The query-driven model extrapolates blindly (could output anything), while the data-driven model integrates its learned joint and returns $\approx500$. This single $(D,W)$ pair shows each paradigm winning on different predicates — concretely why no universal winner exists and a $P_W$-weighted hybrid is attractive.

---
*Part of the [DBMS Research catalog](../../README.md).*
