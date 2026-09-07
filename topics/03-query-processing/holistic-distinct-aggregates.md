---
id: 03-query-processing/holistic-distinct-aggregates
title: "Holistic and distinct aggregate evaluation"
topic: 03-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Holistic and distinct aggregate evaluation

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/holistic-distinct-aggregates` · **Status:** partially-solved

## 1. Problem Statement

Aggregates split into **distributive** (`SUM`, `MAX`, `COUNT`), **algebraic** (`AVG`, variance — finite-state combinable), and **holistic** (`MEDIAN`, percentiles, `MODE`, `COUNT DISTINCT`, rank) — Gray et al.'s data-cube taxonomy. Holistic aggregates have **no bounded-size partial-aggregate state**: in the worst case you must see the whole group to compute the answer exactly. The problem: **evaluate holistic and distinct aggregates *exactly* and efficiently inside an execution engine** — minimizing memory, passes, and per-tuple cost — especially under `GROUP BY` with many groups, high skew, and parallel/distributed execution where partial states must be merged.

Variants: (a) **exact** vs. **approximate** (sketches); this page targets *exact* but contrasts with sketches. (b) `COUNT(DISTINCT x)` and `SUM(DISTINCT x)` — duplicate elimination per group. (c) **order-statistic** holistics (`MEDIAN`, `PERCENTILE_CONT/DISC`) — selection. (d) **`GROUPING SETS`/cube** with many distinct aggregates simultaneously. (e) **windowed** holistics (running median). Decision/optimization: minimize memory at fixed exactness, or minimize passes/I/O for out-of-core groups.

## 2. Mathematical Foundations

Exact `COUNT DISTINCT` over a group of $n$ elements from a universe of size $u$ requires distinguishing all subsets, giving a **communication / streaming lower bound** of $\Omega(\min(n,u))$ bits in one pass (reduction from set-disjointness): no $o(n)$-space *exact* single-pass algorithm exists. **Order statistics**: exact selection (the $k$-th smallest) is $\Theta(n)$ time in RAM (median-of-medians, Blum–Floyd–Pratt–Rivest–Tarjan), but exact single-pass median in $p$-space is impossible for $p=o(n)$ (Munro–Paterson: $p$-pass selection needs $\Omega(n^{1/p})$ space). Approximate counterparts rest on different math: `COUNT DISTINCT` ≈ via **HyperLogLog** ($O(\varepsilon^{-2}\log\log u)$ bits, Flajolet et al.); quantiles via **GK / KLL sketches** ($O(\varepsilon^{-1}\log\!\frac{1}{\varepsilon})$, mergeable, Greenwald–Khanna, Karnin–Lang–Liberty). Mergeability (Agarwal et al.) formalizes when partial states combine without error growth.

## 3. State of the Art (SOTA)

**Theory-SOTA (exact):** linear-time selection for a single median; for `COUNT DISTINCT`, exact requires sort/hash duplicate elimination, $O(n)$ space per group. Munro–Paterson gives the pass/space tradeoff for exact quantiles. **Systems-SOTA:** Engines compute exact `COUNT(DISTINCT)` by **sort- or hash-based deduplication**, often via a `GROUP BY (g, x)` rewrite then a count — expensive with many distinct aggregates. Multiple distinct aggregates use **grouping-sets expansion** or the "CASE/duplication" rewrite; Spark/BigQuery/Snowflake do exact distinct via shuffle-dedup and approximate via HLL (`APPROX_COUNT_DISTINCT`) and KLL (`APPROX_QUANTILES`). DuckDB/Umbra implement exact distinct with radix-partitioned hash sets and exact quantiles via partial sorting / quickselect. Apache DataSketches (Yahoo) and ClickHouse `uniqExact`/`quantileExact` are the production references.

## 4. Upper Bound

Single-group exact: median/percentile in $O(n)$ time, $O(n)$ space (quickselect / BFPRT) — RAM model. `COUNT DISTINCT` in $O(n)$ expected time via hashing, $O(d)$ space for $d$ distinct values. Out-of-core exact quantiles: $O(\text{sort}(n))$ I/O. For *many* groups, hash-partitioning gives $O(N)$ total with state proportional to total distinct values. With $p$ passes, exact selection needs $O(n^{1/p})$ space (Munro–Paterson upper bound, tight). Approximate (for contrast): $\varepsilon$-quantiles in $O(\varepsilon^{-1}\log(\varepsilon n))$ space (GK), $O(\varepsilon^{-1}\log\log(1/\delta))$ (KLL, optimal), fully mergeable.

## 5. Lower Bound

Exact `COUNT DISTINCT` in one streaming pass needs $\Omega(\min(n,u))$ space — **communication complexity** (set-disjointness reduction; Alon–Matias–Szegedy frame the $F_0$ hardness). Exact single-pass median with $o(n)$ space is impossible (Munro–Paterson); $p$-pass exact selection requires $\Omega(n^{1/p})$ space (matching upper bound). For *approximate* $F_0$, $\Omega(\varepsilon^{-2}+\log u)$ bits is necessary (Indyk–Woodruff, Kane–Nelson–Woodruff), and KLL is space-optimal for quantiles. These are **information-theoretic / communication** lower bounds; they explain why exact holistics cannot be made small-state and force either full materialization or accepting approximation.

## 6. The Gap

For a *single group*, exact holistics are essentially **closed** (linear-time selection, optimal pass/space tradeoffs). The remaining gap is **systems-side and combinatorial**: (1) evaluating **many distinct aggregates and grouping sets together** without quadratic blowup from per-aggregate deduplication — current rewrites duplicate the input per distinct column; (2) **parallel/distributed exact** distinct and median with low shuffle and good skew handling, where exactness forbids the cheap mergeability that approximate sketches enjoy; (3) **windowed holistics** (incremental running median/distinct) lack an exact data structure as clean as the streaming sketches. The exact-vs-approximate boundary is sharp and well understood; the open work is making exact evaluation *cheap in practice*.

## 7. Current Research (as of June 2026)

Directions: efficient **multi-distinct** execution (single-scan, shared hashing across grouping sets); **GPU and SIMD** exact dedup and selection; **mergeable exact** structures for distributed median where feasible; tighter **KLL/ReqSketch** variants and their adoption (Apache DataSketches). *(frontier — verify)* 2025–2026 work reports vectorized engines computing multiple exact distinct aggregates in a single pass via shared partitioned hash tables, and relative-error quantile sketches (ReqSketch) reaching the tails. People/groups: Cormode (Warwick, sketches), Liberty/Karnin (KLL), the Apache DataSketches team, DuckDB/Umbra engine groups (Raasveldt, Neumann), ClickHouse engineering.

## 8. Future Work

- Single-pass shared execution for many distinct aggregates across grouping sets without per-column input duplication.
- Skew-robust distributed exact `COUNT DISTINCT` and median with minimal shuffle.
- Incremental/windowed exact holistics (running median, sliding distinct) with sub-linear update.
- Cost models that let the optimizer choose exact vs. approximate per query under accuracy budgets.
- Hardware-accelerated (GPU/SIMD) exact selection and deduplication operators.

## 9. Key References

- **[Foundational]** Gray, Chaudhuri, Bosworth, Layman, Reichart, Venkatrao, Pellow, Pirahesh. *Data Cube: A Relational Aggregation Operator (distributive/algebraic/holistic).* ICDE/Data Mining and Knowledge Discovery, 1996/1997. — [arXiv](https://arxiv.org/abs/cs/0701155)
- **[Foundational]** Munro, Paterson. *Selection and Sorting with Limited Storage.* Theoretical Computer Science / FOCS, 1980. — [DBLP](https://dblp.org/rec/journals/tcs/MunroP80.html)
- **[Foundational]** Blum, Floyd, Pratt, Rivest, Tarjan. *Time Bounds for Selection.* JCSS, 1973. — [DOI](https://doi.org/10.1016/S0022-0000(73)80033-9)
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: the Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166v1)
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** Agarwal, Cormode, Huang, Phillips, Wei, Yi. *Mergeable Summaries.* PODS / ACM TODS, 2012/2013. — [DOI](https://doi.org/10.1145/2500128)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Consider `SELECT g, COUNT(DISTINCT x), MEDIAN(x) FROM R GROUP BY g` on a 6-row table:

| g | x |
|---|---|
| A | 5 |
| A | 5 |
| A | 8 |
| A | 1 |
| B | 7 |
| B | 7 |

Group **A** has multiset $\{5,5,8,1\}$. `COUNT(DISTINCT x)` needs duplicate elimination: hashing the values gives the set $\{1,5,8\}$, so the answer is $3$. `MEDIAN` needs the full sorted group $1,5,5,8$; with $n=4$ the median is the average of positions 2–3, $(5+5)/2 = 5$. Group **B**: distinct $\{7\}$ so count $=1$, median $=7$.

Why these are *holistic*: had we streamed A with $o(n)$ state, no $O(1)$-size partial summary could have told us whether the next tuple was a new distinct value or a duplicate — the $\Omega(\min(n,u))$ exact-$F_0$ lower bound. Contrast `SUM(x)` for A: the running scalar $5\to10\to18\to19$ is a bounded distributive state. Here exactness forces us to materialize the whole group (sort or hash-set), exactly the cost the engine pays.

---
*Part of the [DBMS Research catalog](../../README.md).*
