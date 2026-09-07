---
id: 32-multimodel-document-db/schemaless-cost-model
title: "Cost model for schemaless document scans"
topic: 32-multimodel-document-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cost model for schemaless document scans

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/schemaless-cost-model` · **Status:** empirically-open

## 1. Problem Statement
Build a **cardinality- and cost-estimation model** for scanning and filtering schemaless document collections, where records have no fixed schema: fields may be present or absent per document, types of the same field may vary, and physical size per record is data-dependent. Concretely, for a predicate $\phi$ over paths (e.g., `WHERE a.b > 5 AND EXISTS(c.d)`), estimate:
- **selectivity** $\sigma(\phi)$ — fraction of documents satisfying $\phi$, accounting for *field-presence probability* (a field may be absent, which is distinct from NULL and distinct from "present but failing the predicate");
- **per-document I/O / CPU cost**, which depends on document size, parse cost, and which paths must be touched;
- **result and intermediate cardinalities** for downstream operators (unwind/$\$$unwind, joins, projections).

This is the optimizer's foundational statistics problem, but the classic relational assumption "every tuple has every attribute" fails. Variants: point-predicate selectivity, conjunction/disjunction of presence+value predicates, and cardinality of array-unnest operators (one document → variable number of rows).

## 2. Mathematical Foundations
- **Selectivity as joint probability:** a path predicate factors as $P(\text{field present}) \cdot P(\text{value satisfies}\mid \text{present})$. Presence and value are correlated; the independence assumption (AVI) is even less safe than in relational systems.
- **Sketches and synopses:** count-distinct via **HyperLogLog**, frequency/quantiles via **Count-Min**, **t-digest/KLL** quantile sketches, and **AGM/worst-case bounds** for join cardinality bound the estimates with provable error (Cormode–Muthukrishnan; Karnin–Lang–Liberty KLL).
- **Schema as a distribution over tree shapes:** documents are samples from a distribution over labeled trees; estimating presence probabilities is parameter estimation with concentration bounds (Hoeffding/Chernoff) on a sampled sub-corpus.
- **Cost = f(touched bytes, parse model):** for row/columnar-shredded JSON, cost depends on *path materialization* — a column store (e.g., shredded variant/Parquet) makes presence cheap to count; row stores must parse.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** MongoDB's query planner uses index multikey bounds and sampled plan-cache "works" estimates rather than a true cost model; PostgreSQL maintains MCV/histogram statistics on `jsonb` *expressions* (functional-index statistics) but not on arbitrary paths; Couchbase, SQL Server JSON, and Snowflake's VARIANT/columnar shredding collect per-path presence and value stats. Snowflake/Databricks variant shredding is the most principled production approach: it materializes frequent sub-paths into typed columns and keeps per-column statistics.
- **Theory-SOTA:** no published, validated cost model captures field-presence + type-polymorphism jointly with error guarantees; the closest is the rich literature on *sampling-based* and *sketch-based* selectivity estimation (and recent learned cardinality estimators) adapted ad hoc to documents.

## 4. Upper Bound
With per-path synopses, presence selectivity and distinct counts are estimable with **$(\varepsilon,\delta)$ guarantees** in sublinear space: HyperLogLog gives distinct counts with relative error $\approx 1.04/\sqrt{m}$ using $O(m)$ registers; KLL quantiles achieve additive $\varepsilon$ error in $O((1/\varepsilon)\log\log(1/\delta))$ space. Sampling $s$ documents bounds presence-probability error by $O(1/\sqrt{s})$ (Hoeffding). These give provable *single-path* estimation; the model is buildable in one pass.

## 5. Lower Bound
- **Multi-path / join correlation is the hard part:** distinct-element and frequency estimation have **communication-complexity lower bounds** forcing $\Omega(1/\varepsilon^2)$-type space (Indyk–Woodruff and the data-stream lower-bound program); exact distinct counting needs linear space.
- **Conjunctive selectivity under arbitrary correlation** is not estimable to small relative error without (near-)linear space or assumptions — an information-theoretic barrier inherited from relational cardinality estimation, where capturing $k$-way correlations is exponentially hard in $k$.
- Worst-case join output is bounded by the **AGM bound**, but tight *expected* cardinality under presence-correlation has no closed form.

## 6. The Gap
The status is **empirically-open**: the building blocks (sketches, sampling, AGM) are theoretically solid for single paths, but there is **no validated end-to-end model** that (a) handles field-presence and type-polymorphism jointly, (b) models per-document variable cost under different physical layouts, and (c) has been benchmarked to show robust accuracy across real document workloads. The gap is less an upper/lower bound separation than the absence of a model that is simultaneously sound, learnable from one pass, and empirically accurate — and a benchmark to falsify it. Closing it requires both a principled correlation-aware presence/value model and a standardized accuracy evaluation.

## 7. Current Research (as of June 2026)
- **Learned cardinality estimation** (deep/auto-regressive density models à la Naru/MSCN) extended to semi-structured presence patterns *(frontier — verify; document-specific learned estimators are nascent)*.
- **Variant shredding cost models** in lakehouse engines (Spark/Delta Variant, DuckDB JSON, ClickHouse JSON type) that learn which sub-paths to materialize and cost scans accordingly.
- Robust/worst-case-guarantee optimizers (pessimistic cardinality estimation, Cai–Balazinska lineage) applied to path predicates.

## 8. Future Work
- Joint presence+value+type synopsis with provable conjunction error bounds.
- Layout-aware cost (row vs. shredded-columnar vs. hybrid) and adaptive re-optimization.
- A public benchmark for document-store cardinality/cost-model accuracy (analogous to the relational JOB benchmark).

## 9. Key References
- **[Foundational]** P. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099) · [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166v2) · [DOI](https://doi.org/10.46298/dmtcs.3545)
- **[SOTA]** Z. Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1905.04278) · [DOI](https://doi.org/10.14778/3368289.3368294)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Computing, 2013. — [DOI](https://doi.org/10.1137/110859440) · [arXiv](https://arxiv.org/abs/1711.03860)
- **[Survey]** V. Leis et al. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594) · [PDF](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)

## 10. Worked Example

A collection of $N = 1000$ documents. The field path `a.b` is **present** in only 600 of them; among those present, 150 satisfy `a.b > 5`. Estimate the selectivity of `WHERE a.b > 5`.

The naive relational view ("every tuple has `a.b`") with the AVI independence assumption would compute $\sigma = P(\texttt{a.b}>5) \approx 150/1000 = 0.15$. The document-aware factorization separates presence from value:

$$\sigma(\phi) = P(\text{present}) \cdot P(\text{value}>5 \mid \text{present}) = \frac{600}{1000}\cdot\frac{150}{600} = 0.6 \times 0.25 = 0.15.$$

Here the numbers coincide, but the *structure* matters: change the predicate to `EXISTS(a.b) AND a.b > 5` over a corpus where presence is correlated with large values, and the factors no longer multiply naively. Suppose we sample only $s = 100$ documents to estimate $P(\text{present})$. By Hoeffding, the additive error is $\approx 1/\sqrt{s} = 0.1$ at fixed confidence — so a single-path estimate is cheap and provably bounded, while the *joint* presence+value correlation (the hard case of Section 5) is what resists small-space guarantees.

---
*Part of the [DBMS Research catalog](../../README.md).*
