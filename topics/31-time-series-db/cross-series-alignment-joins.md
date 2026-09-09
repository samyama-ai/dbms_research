---
id: 31-time-series-db/cross-series-alignment-joins
title: "Cross-series alignment and join semantics"
topic: 31-time-series-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cross-series alignment and join semantics

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/cross-series-alignment-joins` · **Status:** open

## 1. Problem Statement
Given two (or many) series $A=\{(a_i, x_i)\}$ and $B=\{(b_j, y_j)\}$ recorded on **different timestamp grids and resolutions**, produce an aligned relation enabling binary operations $f(x,y)$ (ratios, differences, correlations). Because timestamps rarely coincide, a join must *define* what value of $B$ pairs with each point of $A$:

- **As-of / temporal join:** pair $a_i$ with the most recent $b_j \le a_i$ (LOCF), within tolerance $\tau$;
- **Interpolated alignment:** resample both onto a common grid (linear/LOCF/sum) before joining;
- **Windowed / band join:** pair within $|a_i - b_j| \le \tau$ (may be many-to-many).

Variants: **decision** — is there an alignment within tolerance $\tau$ covering fraction $\ge \rho$ of points? **computation** — produce the aligned stream efficiently and incrementally; **counting** — output size of a band/as-of join (needed for cost estimation, see `tsdb-cost-based-optimization`).

Soundness pitfalls: tolerance-based as-of joins are **not transitive** (lookback joins break associativity/commutativity), resampling order changes results, and naive grid resampling can fabricate values across gaps.

## 2. Mathematical Foundations
As-of join is a **temporal/interval semijoin**; formally for time-varying relations it is the *temporal natural join* of Snodgrass's temporal algebra restricted to the "most-recent-predecessor" matching. LOCF alignment treats each series as a step function (a coalesced interval relation), so the as-of join equals an **interval-overlap join** over $[b_j, b_{j+1})$ vs. point $a_i$.

Cost-wise, an as-of/merge join over sorted timestamps is a **merge** in $O(|A|+|B|)$. A band join (tolerance $\tau$, many-to-many) has output size governed by an **AGM-style bound**: with sortedness it is $O(|A|+|B|+\mathrm{OUT})$ via a sweep; general inequality/band joins are subject to the inequality-join worst case $O(n^2)$ output. Multi-series alignment onto a master grid is an instance of *worst-case-optimal* multiway join where the join graph is a path/star over time; the AGM bound $\mathrm{OUT}\le \prod |R_e|^{x_e}$ (fractional edge cover) bounds intermediate sizes, and Leapfrog-Triejoin-style sweeps achieve it.

Interpolated alignment is a sampling operation: linear resampling is a linear operator $R$, and correlation/ratio over $R_g(A)$ vs $R_g(B)$ on grid $g$ introduces resampling bias bounded by the local Lipschitz constant times grid spacing.

## 3. State of the Art (SOTA)
**Systems-SOTA.** kdb+/q `aj` (as-of join) is the canonical high-performance temporal join; pandas `merge_asof` and Polars `join_asof` (with `tolerance`/`by`) are the de-facto analytics implementations. Apache Flink/ksqlDB **interval joins** and Spark Structured Streaming **stream-stream time-bounded joins** handle band semantics with watermarks. PromQL vector matching (`on`/`ignoring`/`group_left`) aligns by *label sets at the same instant* after per-series resampling to the eval step — a different, instant-grid model. QuestDB and TimescaleDB provide `ASOF`/`LATERAL` time joins; ClickHouse has `ASOF JOIN`.

**Theory-SOTA.** Snodgrass/Jensen temporal-database algebra (TSQL2, 1995) gives sound interval-join semantics; worst-case-optimal join theory (Ngo–Porat–Ré–Rudra, PODS 2012; Leapfrog Triejoin, Veldhuizen, ICDT 2014) bounds multiway temporal alignment.

## 4. Upper Bound
Sorted as-of/merge join: $O(|A|+|B|)$ time, $O(1)$ extra state streaming (with bounded lookback buffer). Band join over sorted inputs: $O(|A|+|B|+\mathrm{OUT})$ via sweepline. Multiway grid alignment of $k$ series: worst-case-optimal $O(\prod |R_e|^{x_e})$ output via Leapfrog Triejoin, optimal for the AGM bound. Incremental (streaming) interval joins are $O(1)$ amortized per arrival within a watermark-bounded buffer of size proportional to max out-of-orderness $\times$ rate.

## 5. Lower Bound
Band/inequality joins inherit a **fine-grained barrier**: detecting whether any pair aligns within tolerance reduces from set-disjointness; and computing all aligned pairs is output-sensitive but the *Boolean* "do any two series correlate above $\theta$ over aligned points" relates to **APSP/3SUM-hard** correlation-detection (Williams, *On the difference between closest, furthest, and orthogonal pairs*; and 3SUM-hardness of geometric tolerance matching). For exact multiway alignment, AGM gives a matching $\Omega(\prod|R_e|^{x_e})$ output lower bound. Out-of-order streaming joins face an unbounded-buffer impossibility absent watermarks (a CAP-flavored latency/completeness tradeoff).

## 6. The Gap
For two sorted series the gap is **closed** ($\Theta(n)$ merge). It is **open** for: (i) the *semantics* — no agreed-upon standard for tolerance, interpolation contract, and many-to-many resolution, so engines silently disagree; (ii) *many-series* alignment where AGM-optimality is known but practical, cache-aware, tier-aware implementations over compressed/out-of-order TSDB storage are lacking; (iii) *streaming* alignment where the latency/completeness frontier under bounded memory is not characterized for irregular high-cardinality telemetry. Closing it needs a formal alignment algebra plus worst-case-optimal physical operators integrated with TSDB storage.

## 7. Current Research (as of June 2026)
Directions: native worst-case-optimal temporal joins in columnar engines (DataFusion/DuckDB `ASOF` work) *(frontier — verify)*; principled streaming interval-join semantics with provable watermark bounds in Flink/Arroyo *(frontier — verify)*; PromQL vector-matching formalization and cross-resolution rollup alignment in Mimir/Thanos. Groups: temporal-DB lineage (Snodgrass, Jensen/Aalborg), worst-case-optimal-join community (Ré at Stanford, Ngo at RelationalAI), and streaming-systems groups (TU Berlin/Flink, CMU).

## 8. Future Work
- A standardized, testable as-of/band-join semantics with explicit interpolation and tolerance contracts.
- Worst-case-optimal multi-series alignment operators pushed into compressed/tiered storage.
- Characterizing the streaming latency-vs-completeness frontier for irregular telemetry joins.
- Cost/cardinality estimation for band joins feeding the TSDB optimizer.

## 9. Key References
- **[Foundational]** Snodgrass et al. *The TSQL2 Temporal Query Language.* Kluwer, 1995. — [DBLP search](https://dblp.org/search?q=The%20TSQL2%20Temporal%20Query%20Language)
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 (JACM 2018). — [arXiv](https://arxiv.org/abs/1203.1952)
- **[SOTA]** Veldhuizen. *Leapfrog Triejoin: A Simple, Worst-Case Optimal Join Algorithm.* ICDT, 2014. — [arXiv](https://arxiv.org/abs/1210.0481)
- **[Foundational]** Atallah, Tsotras et al.; and DeWitt, Naughton, Schneider. *An Evaluation of Non-Equijoin (Band Join) Algorithms.* VLDB, 1991. — [VLDB PDF](https://www.vldb.org/conf/1991/P443.PDF)
- **[Docs]** Whitehouse (kdb+/q). *As-of Joins (`aj`).* Kx documentation. (canonical systems reference) — [Kx docs](https://code.kx.com/q/ref/aj/)
- **[Survey]** Jensen, Snodgrass. *Temporal Database Management.* (entry in Encyclopedia of Database Systems), 2009. — [DBLP search](https://dblp.org/search?q=Jensen%20Snodgrass%20Temporal%20Database%20Encyclopedia)

## 10. Worked Example

Series $A$ (a price probe) and $B$ (a slower index) on different grids:

| $A$: time | $x$ | | $B$: time | $y$ |
|---|---|---|---|---|
| 10 | 100 | | 8 | 50 |
| 14 | 102 | | 13 | 52 |
| 21 | 99 | | 19 | 55 |

**As-of join** (pair each $a_i$ with most recent $b_j \le a_i$, tolerance $\tau=6$):
- $a=10$: latest $b\le10$ is $t{=}8\ (y{=}50)$, gap $2\le6$ → $(100,50)$.
- $a=14$: latest is $t{=}13\ (y{=}52)$, gap $1$ → $(102,52)$.
- $a=21$: latest is $t{=}19\ (y{=}55)$, gap $2$ → $(99,55)$.

A single forward merge over the two sorted timestamp lists touches each row once: $O(|A|+|B|)=O(6)$ comparisons, $O(1)$ lookback state. Now contrast a **band join** with the same $\tau=6$ but *all* pairs within tolerance: $a{=}10$ matches $b{\in}\{8,13\}$, $a{=}14$ matches $\{8,13,19\}$, $a{=}21$ matches $\{19\}$ — output size $6 > |A|+|B|$ already, illustrating why band-join cost is $O(|A|+|B|+\mathrm{OUT})$ and why the as-of variant's single-match rule is the cheap special case.

---
*Part of the [DBMS Research catalog](../../README.md).*
