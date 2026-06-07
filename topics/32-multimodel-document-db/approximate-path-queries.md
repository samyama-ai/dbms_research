---
id: 32-multimodel-document-db/approximate-path-queries
title: "Approximate path queries with error bounds"
topic: 32-multimodel-document-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Approximate path queries with error bounds

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/approximate-path-queries` · **Status:** open

## 1. Problem Statement
Given a large corpus of JSON/BSON documents and a **path or array-aggregation query** — e.g., `SUM`/`AVG`/`COUNT`/quantile over values selected by a JSONPath like `$.orders[*].items[*].price`, or `COUNT` of documents matching a recursive-descent predicate — return an answer that is *approximate but comes with a provable error guarantee* (an $(\varepsilon,\delta)$ bound), using **sampling and sketching** at a fraction of the cost of full evaluation.

Variants:
- **Aggregation estimation:** estimate $\sum / \mathrm{avg} / \mathrm{quantile}$ of the multiset $p(D) = \bigcup_{d\in D} p(d)$ with relative error $\varepsilon$ and confidence $1-\delta$.
- **Counting/non-emptiness:** estimate the number of documents (or path-matches) satisfying $p$; distinct-count of values under a path.
- **Array/nesting subtlety:** a single document can contribute a *variable-size, skewed* multiset to $p(D)$ (one document may have $10^6$ array elements), so naive document-level sampling has unbounded variance — the open part is unbiased estimators with bounded variance under **nested, variable-arity** selection and **recursive descent** (`..`).

## 2. Mathematical Foundations
The problem fuses **approximate query processing (AQP)** with the structure of document paths:
- **Hoeffding/Bernstein concentration** gives sample sizes for bounded aggregates: for value range $[a,b]$, $n = O\!\big(\frac{(b-a)^2}{\varepsilon^2}\log\frac1\delta\big)$ samples suffice for additive error; relative-error needs variance-aware (Bernstein) or stratified sampling.
- **Unequal-probability / Horvitz–Thompson estimators** handle the variable-arity issue: if document $d$ contributes $m_d$ values and is sampled with probability $\pi_d$, the HT estimator $\sum_{d\in \text{sample}} \frac{1}{\pi_d}\sum_{v\in p(d)} v$ is unbiased; the open work is choosing $\pi_d \propto$ document "mass" without scanning every document.
- **Sketches:** `COUNT(DISTINCT)` under a path → **HyperLogLog**; frequency/heavy paths → **Count-Min** (Cormode–Muthukrishnan); quantiles → **KLL / t-digest / GK** summaries; set membership of paths → Bloom/quotient filters; *array-join* size estimation → AGM-style bounds and *bottom-$k$/MinHash* for set overlap.
- **Online aggregation** (Hellerstein–Haas–Wang) frames running confidence intervals that tighten as more documents are read, the natural UX for path AQP.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** sketch theory (Cormode et al.; KLL quantiles, Karnin–Lang–Liberty 2016; HyperLogLog, Flajolet et al. 2007) and AQP sampling theory (BlinkDB's error-bounded sampling, Agarwal et al. 2013) are mature for *flat relational* aggregates; **mergeable summaries** (Agarwal–Cormode et al.) give the algebra needed to aggregate per-shard summaries.
- **Systems-SOTA:** BlinkDB, **Snowflake/Spark `APPROX_COUNT_DISTINCT`/`APPROX_PERCENTILE`** (HLL/t-digest), DuckDB and Presto approximate aggregates, and Druid's sketch modules implement these — but over *columnarized* data. Document engines (MongoDB `$sample`, Elasticsearch cardinality/percentile aggregations) expose sketches **without rigorous error bounds for nested/recursive path selection**. There is no system giving $(\varepsilon,\delta)$ guarantees for general JSONPath array-aggregation with recursive descent.

## 4. Upper Bound
For a path that selects a **bounded-arity, non-recursive** multiset, drawing $n = O\!\big(\varepsilon^{-2}\log\delta^{-1}\big)$ documents and applying a Horvitz–Thompson/stratified estimator yields an $(\varepsilon,\delta)$ additive guarantee (relative under bounded coefficient-of-variation) in the **streaming/sampling model**; distinct-count under a path is $(\varepsilon,\delta)$-estimable in $O(\varepsilon^{-2}\log\delta^{-1})$ words via HLL/KMV (space-optimal up to the $\log$, Kane–Nelson–Woodruff). Quantiles need $O(\varepsilon^{-1}\log(\varepsilon n))$ space (GK) or $O(\varepsilon^{-1}\log\log\delta^{-1})$ (KLL). These are the relevant upper bounds; the *document-arity* skew is absorbed into the variance term.

## 5. Lower Bound
- **Distinct elements** requires $\Omega(\varepsilon^{-2} + \log n)$ bits in the streaming model (Indyk–Woodruff; Kane–Nelson–Woodruff), so path distinct-count sketches are near-optimal.
- **Quantile summaries** require $\Omega(\varepsilon^{-1})$ space (comparison model lower bounds), matched by KLL up to $\log\log$ factors.
- **Heavy variance / adversarial arity:** if document contribution sizes are arbitrarily skewed and unknown a priori, any single-pass *uniform* document sampler needs $\Omega(\text{mass}/\varepsilon^2)$ samples — a **communication/streaming** lower bound showing recursive-descent aggregation cannot be done with document-uniform sampling alone; some metadata (mass) or a second pass is information-theoretically required.
- **Join/array-product size** estimation inherits AGM/worst-case-optimal lower bounds: subquadratic estimation of certain self-join sizes is hard under fine-grained assumptions.

## 6. The Gap
For *flat* aggregates and distinct/quantile sketches, bounds are **essentially closed**. The open gap is specifically the **document structure**: (1) error-bounded estimators for **recursive descent (`..`)** and **deeply nested array products** where one document's contribution is itself a query result of unknown size; (2) AQP that *composes* across a path's selection, filtering, and aggregation stages while propagating $(\varepsilon,\delta)$ correctly; and (3) doing this in a *single pass* without precomputed per-document mass. Closing it requires either provably-good mass-proportional sampling built into the document store, or new sketches that are mergeable across nesting levels with tight variance for skewed arity.

## 7. Current Research (as of June 2026)
- Sketch-augmented document/lakehouse engines (Apache DataSketches integration into Spark/Druid/Pinot, DuckDB approximate aggregates) are extending toward semi-structured data *(frontier — verify rigorous nested-path error bounds in any shipping system)*.
- AQP-over-JSON with online-aggregation-style confidence intervals and stratified sampling on inferred shapes is an emerging direction.
- Worst-case-optimal-join ideas applied to array/`UNNEST` size estimation for cost-based path optimization.

## 8. Future Work
- Mergeable summaries indexed by document *shape*/path that give per-path $(\varepsilon,\delta)$ guarantees for recursive descent.
- Mass-proportional (Horvitz–Thompson) document sampling primitives built into storage so $\pi_d$ is known cheaply.
- Compositional error propagation through select–filter–unnest–aggregate path pipelines.
- Differentially private variants of path-aggregation sketches.

## 9. Key References
- **[Foundational]** J. M. Hellerstein, P. J. Haas, H. J. Wang. *Online Aggregation.* SIGMOD, 1997. — [DOI](https://doi.org/10.1145/253260.253291)
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog.* AofA, 2007. — [DBLP](https://dblp.org/rec/journals/dmtcs/FlajoletFGM07.html)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** S. Agarwal, B. Mozafari, A. Panda, H. Milner, S. Madden, I. Stoica. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[Foundational]** D. M. Kane, J. Nelson, D. P. Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[Survey]** G. Cormode, M. Garofalakis, P. J. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

A collection of $N = 5$ order documents; query `AVG($.items[*].price)`. The path selects a *variable-arity* multiset, one document is a whale:

| doc | prices in `items[*]` |
|---|---|
| $d_1$ | $\{10\}$ |
| $d_2$ | $\{20, 30\}$ |
| $d_3$ | $\{15\}$ |
| $d_4$ | $\{40,40,40,40\}$ (bulk) |
| $d_5$ | $\{25\}$ |

True flattened multiset has $9$ values summing to $260$, so true $\mathrm{AVG} = 260/9 \approx 28.9$.

**Naive document-uniform sampling** (pick 2 of 5 docs, average their per-doc means) is biased: if we draw $\{d_1, d_3\}$ we estimate $\tfrac{10+15}{2}=12.5$, far off, because it ignores that $d_4$ contributes 4 values. This is the variable-arity variance blow-up of section 1.

**Horvitz–Thompson fix:** sample documents with probability $\pi_d \propto m_d$ (its array length). Total mass $= 9$. Draw with $\pi_d = m_d/9$; the unbiased estimator of the *sum* is $\hat S = \sum_{d \in \text{sample}} \frac{1}{\pi_d}\sum_{v \in p(d)} v$. For a single draw of $d_4$ ($\pi=4/9$): $\hat S = \tfrac{9}{4}\cdot 160 = 360$, and dividing by the separately HT-estimated count recovers $\approx 28.9$ in expectation. Hoeffding then sizes the sample: for additive error $\varepsilon$ over price range $[10,40]$, $n = O\!\big(\tfrac{(40-10)^2}{\varepsilon^2}\log\tfrac1\delta\big)$ documents.

---
*Part of the [DBMS Research catalog](../../README.md).*
