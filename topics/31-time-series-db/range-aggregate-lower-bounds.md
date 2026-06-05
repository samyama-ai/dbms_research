# Range-aggregate query lower bounds

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/range-aggregate-lower-bounds` · **Status:** partially-solved

## 1. Problem Statement

A core TSDB query is the **time-range aggregate**: given $[a,b]$, return $\bigoplus_{i\in[a,b]} x_i$ for an aggregate $\oplus$ (sum, max, count, quantile). Over **compressed, multi-resolution** stores (Gorilla blocks, downsampled rollups, columnar segments), what are the fundamental **space–time lower bounds** for answering such queries — how many memory cells must any data structure probe, as a function of space, to answer a range-aggregate, especially when the data is stored compressed and exact?

Variants:
- **Group (invertible $\oplus$, e.g. sum):** prefix sums give $O(1)$ — but on *compressed* / *dynamic* / *out-of-order* data?
- **Semigroup (non-invertible, e.g. min/max):** the classic **range-semigroup** problem with inverse-Ackermann bounds.
- **Approximate (quantiles, distinct):** sketch-based, with their own space lower bounds.
- **Dynamic / partial-sums:** updates interleaved with range queries.

Marked **partially-solved**: for static arrays the cell-probe story is tight in several cases; for *compressed multi-resolution* stores with *updates* the exact bounds are open.

## 2. Mathematical Foundations

The reference model is **cell-probe** (Yao): memory is $S$ cells of $w=\Theta(\log n)$ bits; query/update cost is the number of cells probed; computation is free. Two pillars:

- **Dynamic prefix-sum / partial-sums:** Pătraşcu–Demaine (STOC 2004) prove $\Omega(\log n / \log(w/\delta))$ amortized for updates of $\delta$ bits — matching the $O(\log n)$ Fenwick/BIT upper bound. For groups, prefix sums give $O(1)$ static queries.
- **Static range-semigroup (min/max):** Yao's classic result — with $O(n)$ space, range-semigroup queries cost $\Theta(\alpha(n))$ (inverse Ackermann) per query (Yao 1982; Alon–Schieber); the **sparse-table** gives $O(1)$ for idempotent ops (min/max) with $O(n\log n)$ space. So min/max ($O(1)$, idempotent) and sum (group, $O(1)$ prefix) are *easy* statically; general semigroup is $\Theta(\alpha(n))$.

For **approximate** holistic aggregates, the space floor comes from streaming/communication: exact distinct needs $\Omega(n)$; $\epsilon$-quantiles need $\Omega(\frac{1}{\epsilon}\log\frac{1}{\epsilon})$ (KLL-optimal). On **compressed** stores, lower bounds couple **succinct-data-structure** redundancy (Pătraşcu's "succincter") with probe complexity: a structure using $\text{OPT}+r$ bits may need more probes as $r\to 0$.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Pătraşcu–Demaine dynamic partial-sums bounds; Yao / Alon–Schieber inverse-Ackermann range-semigroup; KLL optimal quantile sketches; succinct range-aggregate structures (wavelet trees for range-quantile in $O(\log \sigma)$).
- **Systems-SOTA:** **multi-resolution rollups** (Druid, Timescale continuous aggregates, M3/Mimir/VictoriaMetrics recording rules) answer long ranges from coarse buckets in $O(\#\text{buckets})$; Gorilla/columnar blocks scan compressed runs with block-skipping (min/max zone maps, page indexes in Parquet). **DataSketches** mergeable sketches for approximate range aggregates over segments.
- **Approximate query processing** (BlinkDB-style sampling) as the practical escape from exact lower bounds.

## 4. Upper Bound

- **Sum/count (group), static:** $O(1)$ per range via prefix sums; **dynamic:** $O(\log n)$ (Fenwick/segment tree).
- **Min/max (idempotent semigroup):** $O(1)$ query, $O(n\log n)$ space (sparse table) or $O(n)$/$O(\alpha(n))$ (Cartesian-tree RMQ ⇒ $O(1)$ with $O(n)$ space).
- **General semigroup:** $O(\alpha(n))$ static (Yao); $O(\log n)$ dynamic (segment tree).
- **Range-quantile:** $O(\log \sigma)$ with a wavelet tree on $O(n\log\sigma)$ bits; mergeable sketches give $\epsilon$-approx in $\tilde O(1/\epsilon)$ space per segment.
- **Multi-resolution rollup:** answering $[a,b]$ touches $O(\log(b-a))$ buckets across resolutions (dyadic decomposition).

## 5. Lower Bound

- **Dynamic partial sums (cell-probe):** $\Omega(\log n / \log(w/\delta))$ per operation (Pătraşcu–Demaine, STOC 2004) — tight against Fenwick trees.
- **Static range-semigroup:** $\Omega(\alpha(n))$ per query with linear space (Yao 1982; Alon–Schieber) — min/max escape via idempotence, general semigroups do not.
- **Approximate aggregates:** $\Omega(\frac{1}{\epsilon}\log\frac{1}{\epsilon})$ space for $\epsilon$-quantiles (matching KLL); $\Omega(n)$ for exact distinct (communication complexity).
- **Compressed/succinct regime:** Pătraşcu's succinct lower bounds imply probe-time penalties as redundancy $\to 0$ — exact bounds for range-aggregates over *entropy-compressed multi-resolution* stores are **not fully characterized** (the open part).

## 6. The Gap

For **static, uncompressed** arrays the picture is essentially tight: $O(1)$/$\Theta(\alpha(n))$ static, $\Theta(\log n / \log w)$ dynamic. The genuinely open gap is the **compressed + multi-resolution + dynamic** intersection: there is no matching upper/lower bound for range-aggregates over a store that is (i) compressed near entropy, (ii) layered at multiple resolutions, and (iii) updated by out-of-order ingest. Whether compression *must* cost extra probes for range-aggregates (beyond the succinct-dictionary results) is unresolved.

## 7. Current Research (as of June 2026)

- Succinct/learned multi-resolution structures with provable range-aggregate probe bounds; learned indices meeting partial-sum lower bounds *(frontier — verify)*.
- Mergeable-sketch theory for range-quantile/distinct over compressed segments (Apache DataSketches, KLL/REQ extensions).
- Lower-bound transfer from dynamic partial sums to out-of-order rollup maintenance (link to continuous-rollup problem).

## 8. Future Work

- Tight cell-probe bounds for range-aggregates over entropy-compressed, multi-resolution, dynamic stores.
- Separation (or collapse) between compressed and uncompressed range-aggregate probe complexity.
- Optimal mergeable sketches for holistic range-aggregates with proven space–accuracy–probe trade-offs.

## 9. Key References

- **[Foundational]** A. C. Yao. *Space-Time Tradeoff for Answering Range Queries.* STOC, 1982.
- **[Foundational]** M. Pătraşcu, E. Demaine. *Lower Bounds for Dynamic Connectivity / Tight Bounds for the Partial-Sums Problem.* STOC, 2004.
- **[Foundational]** N. Alon, B. Schieber. *Optimal Preprocessing for Answering On-Line Product Queries.* TR, 1987.
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016.
- **[Foundational]** M. Pătraşcu. *Succincter.* FOCS, 2008.
- **[Survey]** P. Bose et al. / G. Navarro. *Compact Data Structures.* Cambridge Univ. Press, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
