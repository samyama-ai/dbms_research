---
id: 31-time-series-db/gap-filling-semantics
title: "Gap-filling and interpolation semantics"
topic: 31-time-series-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Gap-filling and interpolation semantics

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/gap-filling-semantics` · **Status:** open

## 1. Problem Statement

Time-series data is sampled irregularly, with gaps, dropped points, and per-series misalignment. Queries that bucket time (`time_bucket`/`GROUP BY` over windows) or join series must decide **what value, if any, exists at instants where no sample was recorded**. The problem: define **principled, query-visible, composable semantics for missing points and interpolation** so that the meaning of a query is unambiguous, referentially transparent, and analytically sound.

Sub-questions:
- **Semantic (definitional):** what does a window aggregate *mean* when the window contains zero, one, or sparse samples? When is a value `NULL`, carried-forward (LOCF), linearly interpolated, or "undefined"?
- **Algebraic:** do gap-fill operators compose? Is `aggregate(gapfill(X))` $=$ `gapfill(aggregate(X))`? Are they associative/idempotent across nesting?
- **Inference (optimization/statistical):** which interpolation minimizes a stated loss given a generative model, and how is that uncertainty surfaced to the query?
- **Decision:** given a query and gap-fill policy, is the result well-defined / deterministic?

Marked **open**: SQL has no agreed standard; vendor semantics (LOCF, `interpolate`, `fill(none/null/previous/linear)`) differ and don't compose predictably.

## 2. Mathematical Foundations

Model a series as a partial function $x: \mathcal{T} \rightharpoonup \mathbb{R}$ over a time domain $\mathcal{T}$ with observed support $\mathrm{dom}(x)=\{t_1,\dots\}$. Gap-filling chooses a **total** extension $\tilde x:\mathcal{T}\to\mathbb{R}\cup\{\bot\}$. Candidate operators:
- **LOCF:** $\tilde x(t) = x(\max\{t_i \le t\})$ (a càdlàg step function; the natural choice for *state* signals).
- **Linear:** $\tilde x(t)$ interpolates the bracketing samples (natural for *rate/continuous* signals).
- **NULL/none:** $\tilde x(t)=\bot$ outside support — preserves three-valued logic but breaks downstream arithmetic.

The semantic issue is that **aggregation and extension do not commute** and depend on whether the signal is interpreted as **instantaneous samples** vs. a **piecewise-constant** vs. **band-limited continuous** process. Statistically, optimal interpolation under a Gaussian-process prior with kernel $K$ is **kriging**: $\hat x(t) = k(t)^\top K^{-1} x$, with posterior variance $K(t,t) - k(t)^\top K^{-1} k(t)$ giving a *principled uncertainty* the query could expose. Connections: SQL **NULL** three-valued logic (Codd), interval/temporal databases (Allen's interval algebra), and the **point vs. interval** timestamp semantics from temporal SQL (SQL:2011 system/application time).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** TimescaleDB `time_bucket_gapfill` + `locf()` / `interpolate()`; InfluxDB `fill(previous|linear|none|<value>)`; Prometheus **range-vector** semantics with `rate()`/`increase()` and **staleness markers** (a notable principled stab at "no value here"); kdb+/q temporal joins (`aj` as-of join). Grafana/PromQL define lookback windows operationally.
- **Theory-SOTA:** temporal-database semantics (Snodgrass, Date–Darwen on temporal data and the relational model), Gaussian-process / state-space imputation (Kalman smoothing) as the statistical gold standard.
- No DBMS adopts a *composable, model-grounded* gap-fill algebra; this is the open frontier.

## 4. Upper Bound

There is no single complexity bound; rather, **constructions**: LOCF/linear gap-fill is computable in $O(n)$ streaming with $O(1)$ state. GP/Kalman imputation costs $O(n)$ (state-space) to $O(n^3)$ (naïve dense kernel) per series, with $O(n\log n)$ structured-kernel methods. The open "upper bound" is a *semantic* one: a denotational definition under which nesting/composition is sound — partial proposals exist but none is canonical.

## 5. Lower Bound

This is primarily a **definitional/impossibility** problem, not a complexity one:
- **No-free-lunch for interpolation:** without a prior/model, no extension is "correct"; any choice is adversarially wrong on some signal — an information-theoretic impossibility of model-free imputation.
- **Non-composability:** one can show families of queries where $\text{agg}\circ\text{gapfill} \ne \text{gapfill}\circ\text{agg}$, so **no gap-fill operator is simultaneously NULL-preserving, aggregate-commuting, and idempotent** — a small algebraic impossibility result that bounds what semantics can offer.
- Three-valued-logic anomalies (Codd-style NULL pathologies) transfer directly.

## 6. The Gap

The gap is **conceptual, not algorithmic**: we can compute any interpolation cheaply, but lack an agreed *meaning* that is composable, model-aware, and exposes uncertainty. Closing it requires a denotational semantics (likely typing series as *sample* / *state* / *cumulative* and fixing per-type fill rules) plus a query algebra in which gap-fill, windowing, and joins have provable rewrite/commutation laws — and ideally first-class uncertainty.

## 7. Current Research (as of June 2026)

- **Typed-signal semantics** distinguishing gauges/counters/states with fill rules derived from the type (OpenTelemetry / Prometheus staleness lineage) *(frontier — verify)*.
- Probabilistic/GP-backed databases surfacing imputation **uncertainty intervals** in query results; differentiable/learned imputation (SAITS, BRITS, diffusion imputers) feeding TSDB query layers.
- Standardization discussions around SQL window/temporal extensions for gap-fill.

## 8. Future Work

- A composable gap-fill algebra with proven commutation laws and a denotational semantics.
- First-class **uncertainty propagation** through aggregates and joins.
- Type systems for time series (sample vs. state vs. cumulative) that auto-select fill semantics.

## 9. Key References

- **[Foundational]** E. F. Codd. *Extending the Database Relational Model to Capture More Meaning (NULLs / missing information).* ACM TODS, 1979. — [DOI](https://doi.org/10.1145/320107.320109)
- **[Foundational]** R. T. Snodgrass. *Developing Time-Oriented Database Applications in SQL.* Morgan Kaufmann, 2000. — [DBLP search](https://dblp.org/search?q=Developing%20Time-Oriented%20Database%20Applications%20in%20SQL)
- **[Foundational]** J. F. Allen. *Maintaining Knowledge about Temporal Intervals.* CACM, 1983. — [DOI](https://doi.org/10.1145/182.358434)
- **[Foundational]** C. E. Rasmussen, C. K. I. Williams. *Gaussian Processes for Machine Learning.* MIT Press, 2006. — [book site](https://gaussianprocess.org/gpml/)
- **[SOTA]** W. Cao et al. *BRITS: Bidirectional Recurrent Imputation for Time Series.* NeurIPS, 2018. — [arXiv](https://arxiv.org/abs/1805.10572)
- **[Survey]** R. T. Snodgrass et al. *The TSQL2 Temporal Query Language.* Kluwer, 1995. — [DBLP search](https://dblp.org/search?q=The%20TSQL2%20Temporal%20Query%20Language)

## 10. Worked Example

A sensor reports at $t=\{0,2,5\}$ with values $\{4,\;?,\;10\}$ — we want the value at $t=2$ and a 5-minute bucket average over $[0,5)$.

| policy | $\tilde x(2)$ | meaning |
|---|---|---|
| NULL/none | $\bot$ | "no reading recorded" |
| LOCF | $4$ | carry last (state signal) |
| linear | $4 + \tfrac{2-0}{5-0}(10-4)=6.4$ | interpolate (rate signal) |

Now the **non-commutativity** bite. Average the *raw* samples in $[0,5)$ (only $t{=}0$): $\mathrm{avg}=4$. But gap-fill first onto grid $\{0,1,2,3,4\}$ with LOCF (all $=4$) then average: still $4$; with linear fill the grid is $\{4,5.2,6.4,7.6,8.8\}$, average $=6.4$. So $\mathrm{avg}\circ\mathrm{gapfill}_{\text{lin}} = 6.4 \ne 4 = \mathrm{avg}\circ\mathrm{gapfill}_{\text{none}}$ — the *same query text* yields different numbers purely from the fill choice, and neither equals $\mathrm{gapfill}\circ\mathrm{avg}$. This is exactly the composability gap: without typing the series as sample / state / rate, the query's meaning is underdetermined. A GP prior with kernel $K$ would instead return $\hat x(2)$ *plus* a posterior variance, surfacing that the $t{=}2$ value is an estimate, not a fact.

---
*Part of the [DBMS Research catalog](../../README.md).*
