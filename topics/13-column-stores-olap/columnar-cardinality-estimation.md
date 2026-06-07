---
id: 13-column-stores-olap/columnar-cardinality-estimation
title: "Cardinality Estimation for Columnar Plans"
topic: 13-column-stores-olap
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cardinality Estimation for Columnar Plans

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/columnar-cardinality-estimation` · **Status:** open

## 1. Problem Statement
Given a columnar relation $R$ over attributes $A_1,\dots,A_m$ stored with per-block encodings (dictionary, RLE, frame-of-reference, bit-packing), a sort/clustering order, and per-block synopses (zone maps / min-max, bloom filters, sketches), estimate the **selectivity** $\sigma$ and **output cardinality** of a query plan node — filters, joins, and group-by — so the optimizer can choose join order, build/probe sides, and aggregation strategy.

Variants:
- **Decision:** does predicate $p$ on column $A_i$ qualify any tuple in block $b$ (the zone-map pruning question)?
- **Optimization (the focus):** minimize the **q-error** $\max(\hat{n}/n,\, n/\hat{n})$ of the estimate $\hat{n}$, which bounds plan-cost suboptimality.
- **Counting:** exactly or approximately count distinct values (NDV) per column and per group, including after multi-column correlated filters.

The columnar twist: estimation must exploit **physical layout** — encoding (a dictionary makes equality cheap and exact-NDV easy; RLE collapses runs), **sort order** (clustering induces zone-map locality and inter-column correlation), and **zone-map correlation** (min/max ranges across blocks are not independent across columns when co-sorted).

## 2. Mathematical Foundations
Classic independence/uniformity assumptions give $\hat{\sigma}(p_1\wedge p_2)=\sigma(p_1)\,\sigma(p_2)$, with error growing multiplicatively under correlation. The information-theoretic optimum is captured by the **maximum-entropy** consistent distribution given a set of marginal/conditional constraints $C$:
$$\hat{P}=\arg\max_{P:\,P\models C} H(P),\qquad H(P)=-\sum_x P(x)\log P(x).$$
Distinct-value estimation rests on streaming sketches: **HyperLogLog** gives NDV with relative error $\approx 1.04/\sqrt{m}$ using $m$ registers; **KMV/$\theta$-sketches** support set operations. Join-output bounds use the **AGM bound**: for a join $Q$ with hypergraph $\mathcal{H}$ and fractional edge cover $\mathbf{x}$, $|Q|\le \prod_{e} |R_e|^{x_e}$, tight in the worst case. Sort order matters via **clustering factor** and the dependence structure: zone-map prunability of block $b$ for range $[l,u]$ is exactly $[\min_b,\max_b]\cap[l,u]\neq\emptyset$, and the *expected* surviving blocks depend on the value-to-block assignment induced by the sort permutation.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Histogram + per-column NDV is standard (Postgres, DuckDB, ClickHouse). Learned estimators — **MSCN** (multi-set CNN, Kipf et al., 2019), **DeepDB** (RSPNs / sum-product networks, Hilprecht et al., VLDB 2020), **NeuroCard** (single-model deep autoregressive, Yang et al., VLDB 2021), and **Naru/UAE** (autoregressive density) — model joint distributions and beat independence assumptions on correlated benchmarks.
- **Pessimistic / bound-based:** AGM-style and **degree-bounded** pessimistic estimators (Cai et al., SIGMOD 2019) give *guaranteed upper bounds*, attractive because over-estimation is safer than under-estimation for join ordering.
- **Columnar-aware:** Zone-map / min-max pruning combined with **data-induced predicates** (Perf. on co-sorted columns) is used in Amazon Redshift, Snowflake micro-partitions, and Apache Parquet/ORC stats. Sketch-based exact-distinct via dictionary metadata is exploited in DuckDB/ClickHouse.

## 4. Upper Bound
For approximate NDV, HyperLogLog achieves standard error $1.04/\sqrt{m}$ in $O(m)$ space, $O(1)$ per element — near information-theoretically optimal for distinct counting (Indyk–Woodruff lower bounds). For join cardinality, the **AGM bound** is computable in time polynomial in the query size and is worst-case tight, giving an over-estimate with bounded looseness equal to the gap between fractional cover and actual data skew. Learned models give low *empirical* q-error (often <2 median) but carry **no worst-case guarantee**.

## 5. Lower Bound
Exact cardinality estimation is as hard as evaluation (counting query answers is **#P-hard** in general). Approximate distinct counting in one pass requires $\Omega(\varepsilon^{-2}+\log n)$ bits (Indyk–Woodruff; Kane–Nelson–Woodruff tight $\Theta(\varepsilon^{-2}+\log n)$). For correlated multi-column selectivity, any estimator using only single-column synopses inherits an unbounded q-error under adversarial correlation — an information-theoretic limit: the synopsis simply does not contain the joint distribution. No general poly-space synopsis yields bounded q-error for arbitrary conjunctive predicates.

## 6. The Gap
NDV estimation is essentially closed (matching $\Theta(\varepsilon^{-2}+\log n)$ bounds). The open gap is **multi-column, layout-aware selectivity**: learned models are accurate but lack guarantees and are costly to train/maintain under updates; pessimistic bounds have guarantees but can be loose by orders of magnitude. No estimator simultaneously (a) exploits encoding + sort order + zone-map correlation, (b) gives bounded q-error, and (c) updates cheaply. Closing it requires either a synopsis class with provable q-error under a stated correlation model, or learned models with certified bounds.

## 7. Current Research (as of June 2026)
Active threads: **bounded-error learned estimators** that combine pessimistic AGM guards with neural correction *(frontier — verify)*; **update-robust** learned cardinality (incremental retraining, drift detection); **layout-coupled** estimators that read encoding/zone-map metadata directly rather than re-sampling. Groups: the DeepDB/Naru lineage (TU Darmstadt — Binnig; Berkeley — Stoica/Yang), MIT (Kraska, learned DB components), CWI/DuckDB (Mühleisen/Raasveldt) on cheap exact stats from dictionaries. Benchmarks: **CardBench / JOB-light / STATS-CEB** driving comparisons. Robustness-vs-accuracy and "when does CE error actually change plans" (Leis et al.'s "How Good Are Query Optimizers, Really?") remain central.

## 8. Future Work
- A synopsis with **provable q-error** under a declared correlation budget.
- **Incrementally maintainable** joint models tied to LSM/delta updates in column stores.
- Optimizer integration that is **CE-error-aware** (robust plans rather than point estimates).
- Exploiting **sort-order-induced** functional/soft dependencies for free.

## 9. Key References
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational DBMS.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 (AGM bound). — [arXiv](https://arxiv.org/abs/1711.03860)
- **[SOTA]** Hilprecht et al. *DeepDB: Learn from Data, not from Queries.* PVLDB, 2020. — [arXiv](https://arxiv.org/abs/1909.00607)
- **[SOTA]** Yang et al. *NeuroCard: One Cardinality Estimator for All Tables.* PVLDB, 2021. — [arXiv](https://arxiv.org/abs/2006.08109)
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[Survey]** Leis et al. *How Good Are Query Optimizers, Really?* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[Foundational]** Flajolet et al. *HyperLogLog.* AofA, 2007. — [HAL](https://inria.hal.science/hal-00406166v1)

## 10. Worked Example

A table has $N=10{,}000$ rows. Two columns: `city` ($\sigma_{\text{city=NYC}}=0.10$) and `weather` ($\sigma_{\text{rain}}=0.20$). A query filters `city='NYC' AND weather='rain'`.

**Independence estimate:** $\hat\sigma = 0.10 \times 0.20 = 0.02$, so $\hat n = 200$.

But suppose NYC is rainy and these columns are correlated: the *true* conditional is $P(\text{rain}\mid\text{NYC})=0.5$, giving true $n = 10{,}000 \times 0.10 \times 0.5 = 500$.

**q-error:** $\max(\hat n/n,\, n/\hat n) = \max(200/500,\,500/200) = 2.5$. A plan tuned for $200$ rows may pick the wrong build side or under-size a hash table.

**AGM-style upper bound** for the join's worst case is computable and *guaranteed* not to under-estimate, but here would over-shoot. The columnar fix: if the table is *sorted by* `city`, all NYC rows cluster in a contiguous block, and a zone-map can store the joint min/max — exposing the correlation directly. This illustrates the open gap: single-column synopses (two marginals) lose the joint $P(\text{NYC},\text{rain})$, yielding unbounded q-error under adversarial correlation, while layout-aware joint stats recover it.

---
*Part of the [DBMS Research catalog](../../README.md).*
