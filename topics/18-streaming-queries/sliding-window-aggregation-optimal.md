---
id: 18-streaming-queries/sliding-window-aggregation-optimal
title: "Optimal sliding-window aggregation under arbitrary aggregates"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal sliding-window aggregation under arbitrary aggregates

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/sliding-window-aggregation-optimal` · **Status:** partially-solved

## 1. Problem Statement

A sliding-window aggregation (SWAG) maintains the aggregate of the most recent window of a stream under two operations: `insert` (a new element arrives at the window's right edge) and `evict` (the oldest element leaves the left edge), with `query` returning the aggregate of the current window contents. The aggregation operator $\oplus$ is an **associative** binary operator (a semigroup), but is *not assumed* to be invertible (no subtraction), commutative, or idempotent. Examples that defeat naive tricks include `MAX`, `MIN`, arg-max, Bloom-filter union, sketch merge, geometric-mean, first/last, and collect-into-list.

- **Optimization (in-order) variant.** Given a FIFO sliding window of size $n$, design a data structure whose amortized cost per `insert`/`evict`/`query` is $O(1)$ semigroup operations, with $O(n)$ space. Can $O(1)$ be made *worst-case* per operation rather than amortized?
- **Out-of-order variant.** Elements may arrive/depart at arbitrary positions (data-driven or session windows, retractions). What is the optimal cost per update?
- **Variable-size / multi-window variant.** Window boundaries are determined at query time, or many windows of different sizes share one stream.

## 2. Mathematical Foundations

Let $(S,\oplus)$ be a semigroup. For a window holding $x_1,\dots,x_k$ (left to right), the query result is $x_1\oplus x_2 \oplus \cdots \oplus x_k$. Because $\oplus$ need not be commutative, **order must be preserved**; because it need not be invertible, the "subtract on evict" approach used for `SUM` is unavailable.

The lower-bound model counts **semigroup operations** (the operator is a black box). The classic batch primitive is the *sliding-window minimum* / **monotonic-wedge** technique, generalized by the **two-stacks** algorithm: maintain two stacks `front` and `back`, each storing running suffix/prefix aggregates; `query` is one $\oplus$ of the two stack tops. Amortized analysis gives $O(1)$ ops because each element is pushed once and popped once across the two stacks.

For worst-case bounds the relevant tool is the **functional/incremental aggregation hierarchy** and a connection to the **range-semigroup-sum** problem, where preprocessing a static array for arbitrary subrange aggregates relates to inverse-Ackermann $\alpha(n)$ bounds (Yao; Alon–Schieber) when no inverse exists.

## 3. State of the Art (SOTA)

- **Two-Stacks** (DABA's predecessor; folklore / Tangwongsan et al.): $O(1)$ amortized, but $O(n)$ worst-case per operation.
- **DABA (De-Amortized Banker's Aggregator)** — Tangwongsan, Hirzel, Schneider (DEBS 2017): **$O(1)$ worst-case** per `insert`/`evict`/`query` for FIFO windows, $2n+O(1)$ space, requiring only associativity. **DABA Lite** later reduces the space constant.
- **FlatFAT / Reactive Aggregator** — Tangwongsan, Hirzel, Schneider, Wu (VLDB 2015): $O(\log n)$ per update via a flat balanced tree, but supports *out-of-order* updates and shared multi-window queries.
- **FiBA (Finger B-Tree Aggregator)** — Tangwongsan, Hirzel, Schneider (VLDB 2019): out-of-order SWAG with amortized $O(\log d)$ where $d$ is the distance of the change from a window boundary; $O(1)$ amortized for in-order. Current systems SOTA for general out-of-order.

## 4. Upper Bound

- **In-order FIFO:** $O(1)$ **worst-case** semigroup ops per operation, $O(n)$ space — DABA (DEBS 2017). This is optimal for in-order under the semigroup-operation model.
- **Out-of-order:** FiBA achieves $O(\log d)$ amortized (distance-sensitive), degrading gracefully to $O(\log n)$; $O(n)$ space. FlatFAT gives $O(\log n)$ worst-case.

## 5. Lower Bound

In the **semigroup-operation (black-box) model**, every operation must touch the operator at least once, so $\Omega(1)$ per op is trivial and matched in-order. For **arbitrary range** semigroup queries over a static array (the multi-window / variable-size relaxation), Yao's and the Alon–Schieber results give an $\Theta(n\,\alpha(k,n))$ preprocessing trade-off for $k$ queries — strictly super-linear and inverse-Ackermann-tight, ruling out $O(1)$-preprocessed constant-query for general non-invertible aggregates. No unconditional super-constant lower bound is known for the *out-of-order single-window* update problem.

## 6. The Gap

For **in-order FIFO** the gap is **closed**: DABA's $O(1)$ worst-case matches the trivial $\Omega(1)$. The genuinely open frontier is **out-of-order**: FiBA's distance-sensitive $O(\log d)$ has no matching $\Omega(\log d)$ lower bound, so it is open whether out-of-order SWAG admits $o(\log n)$ worst-case for far-from-boundary updates, or whether a cell-probe / semigroup lower bound forces logarithmic cost. The variable-size multi-window case sits against inverse-Ackermann bounds but the constants and the exact streaming (online) analogue are unresolved.

## 7. Current Research (as of June 2026)

Active work targets (i) GPU/SIMD-vectorized SWAG and parallel de-amortization, (ii) SWAG over *approximate* aggregates (sketch-valued semigroups) where the cost model mixes ops and error, and (iii) tightening out-of-order bounds. The IBM/CMU line (Tangwongsan, Hirzel, Schneider) remains central; streaming-systems groups (TU Berlin, TU Darmstadt, ETH Zürich) integrate these aggregators into Flink/Timely-style runtimes *(frontier — verify)*. Interest is rising in **retraction-aware** SWAG for incremental view maintenance over streams (DBSP-style differential dataflow).

## 8. Future Work

- Matching lower bound (or sub-logarithmic algorithm) for out-of-order single-window SWAG.
- Optimal *shared* aggregation across many concurrent windows of differing sizes with one pass.
- SWAG for non-associative but "nearly associative" aggregates (e.g., floating-point with error tracking).
- Energy/cache-aware optimality models beyond pure op-counting.

## 9. Key References

- **[SOTA]** Kanat Tangwongsan, Martin Hirzel, Scott Schneider. *Low-Latency Sliding-Window Aggregation in Worst-Case Constant Time (DABA).* DEBS, 2017. — [DOI](https://doi.org/10.1145/3093742.3093925)
- **[Foundational]** Kanat Tangwongsan, Martin Hirzel, Scott Schneider, Kun-Lung Wu. *General Incremental Sliding-Window Aggregation (FlatFAT / Reactive Aggregator).* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752940)
- **[SOTA]** Kanat Tangwongsan, Martin Hirzel, Scott Schneider. *Optimal and General Out-of-Order Sliding-Window Aggregation (FiBA).* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3339490.3339499)
- **[Foundational]** Noga Alon, Baruch Schieber. *Optimal Preprocessing for Answering On-Line Product Queries.* Tech. Report / TAU, 1987. — [arXiv](https://arxiv.org/abs/2406.06321)
- **[Survey]** Martin Hirzel et al. *A Catalog of Stream Processing Optimizations.* ACM Computing Surveys, 2014. — [DOI](https://doi.org/10.1145/2528412)

## 10. Worked Example

Take $\oplus=\max$ (non-invertible: no "un-max" on evict) and window size $n=3$. The **two-stacks** aggregator keeps a `front` stack of suffix-maxes and a `back` stack of prefix-maxes; `query` $=\max(\text{front.top},\text{back.top})$.

Stream $7,3,9$ then evict-oldest, insert $5$. Window goes $[7,3,9]\to[3,9,5]$.

State after the three inserts (back stack holds running prefix-max as items arrive): $\text{back}=[7,\;\max(7,3){=}7,\;\max(7,9){=}9]$, so $\text{back.top}=9$; `front` empty. `query` $=9$. Correct: $\max(7,3,9)=9$.

Now **evict** the oldest ($7$). With `front` empty we flip `back` into `front`, recomputing suffix-maxes right-to-left over $[7,3,9]$: $\text{front}=[\,\max(7,3,9){=}9,\;\max(3,9){=}9,\;9\,]$. Pop the oldest (top) element $\Rightarrow \text{front}=[9,9]$ for window $[3,9]$. **Insert** $5$: push onto `back`, $\text{back}=[5]$. `query` $=\max(\text{front.top}{=}9,\;\text{back.top}{=}5)=9=\max(3,9,5)$. ✓

Each element is pushed once and flipped once, so over the run the work is $O(1)$ **amortized** per operation — the flip's $O(n)$ cost is what DABA de-amortizes to $O(1)$ worst-case.

---
*Part of the [DBMS Research catalog](../../README.md).*
