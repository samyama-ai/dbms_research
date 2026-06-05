# Approximate Cube / Rollup Synopses

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/approximate-cube-synopses` · **Status:** partially-solved

## 1. Problem Statement
Given a fact relation over $d$ dimensions, build a **sublinear-space synopsis** that answers data-cube aggregate queries — group-bys and roll-ups over any subset of dimensions, with range constraints — approximately, with **provable error bounds**, instead of materializing the $2^d$ cuboids exactly. Variants:

- **Optimization:** minimize synopsis space subject to a relative/absolute error guarantee $\epsilon$ on a query class.
- **Query-class scope:** point cells, range-sums (orthogonal range aggregation), `COUNT`/`SUM` (linear, sketchable) vs. **DISTINCT**/**quantile** (holistic).
- **Counting/cardinality:** estimate number of non-empty cells, or distinct counts per cuboid.

It is *partially solved*: for linear aggregates (SUM/COUNT, range queries) strong synopses with tight bounds exist (wavelets, AMS/Count-Min, sampling); for holistic measures and the *full* high-dimensional cube under worst-case skew, optimal space-error tradeoffs remain open.

## 2. Mathematical Foundations
The synopsis question is information-theoretic: how many bits suffice to answer a query class within error $\epsilon$? Key tools:

- **Linear sketches** for $\mathsf{SUM}/\mathsf{COUNT}$: AMS ($F_2$), Count-Min (point/heavy-hitters, additive $\epsilon\lVert f\rVert_1$ error in $O(\frac1\epsilon\log\frac1\delta)$ space), all mergeable across cuboids since roll-up is linear.
- **Distinct count:** HyperLogLog gives relative error $1.04/\sqrt{m}$ in $O(m\log\log n)$ bits; the **$\Theta(\epsilon^{-2} + \log n)$** space bound (Kane–Nelson–Woodruff) is optimal.
- **Quantiles:** KLL sketch achieves $\epsilon$-approximate rank in $O(\frac1\epsilon\log\log\frac1\delta)$ space (optimal up to the $\log\log$).
- **Range-sum:** prefix-sum / wavelet (Haar) decompositions give the best-$B$-term $L_2$ synopsis; multidimensional **dyadic** decomposition answers range queries via $O(\log^d n)$ canonical ranges.
- **Sampling**: a uniform sample of size $O(\epsilon^{-2}\log\frac1\delta)$ bounds additive error per aggregate (Hoeffding/VC over the query range space, whose **VC dimension** controls uniform convergence).

Mergeability of sketches mirrors the cuboid lattice: a coarser cuboid's synopsis is the $\oplus$-merge of finer ones, so a single base-level sketch family can serve all roll-ups.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Count-Min (Cormode–Muthukrishnan, 2005), AMS (Alon–Matias–Szegedy, 1996), HyperLogLog (Flajolet et al., 2007) with optimal $F_0$ bounds (Kane–Nelson–Woodruff, PODS 2010), KLL quantiles (Karnin–Lang–Liberty, FOCS 2016), and wavelet/probabilistic-wavelet synopses (Garofalakis–Gibbons; Matias–Vitter–Wang).
- **Systems-SOTA:** Apache Druid and ClickHouse embed HLL/quantile sketches per cuboid; **Apache DataSketches** (Yahoo/Apache) is the production library; BlinkDB / approximate-query engines and sketch-augmented OLAP cubes (e.g., "Sketch Cube" style designs) deliver interactive approximate roll-ups; cloud warehouses expose `APPROX_COUNT_DISTINCT`/`APPROX_QUANTILE` backed by these.

## 4. Upper Bound
Per-measure: $\mathsf{COUNT}/\mathsf{SUM}$ point queries in $O(\epsilon^{-1}\log\frac1\delta)$ (Count-Min); $F_0$/distinct in $O(\epsilon^{-2}+\log n)$ bits (optimal); $\epsilon$-quantiles in $O(\epsilon^{-1}\log\log\frac1\delta)$ (KLL); range-sum within $\epsilon\lVert\cdot\rVert$ using $O(B)$ wavelet terms or $O(\log^d n)$ dyadic sketches per query. Crucially, **one base sketch family answers all $2^d$ roll-ups** via lattice merging, giving total space *polynomial in $1/\epsilon, d, \log n$* rather than exponential cube size — the headline win over exact cubes (model: streaming/sketch, word-RAM).

## 5. Lower Bound
$F_0$ (distinct) requires $\Omega(\epsilon^{-2}+\log n)$ bits — matching, so optimal (Kane–Nelson–Woodruff, communication-complexity reduction). Quantiles need $\Omega(\epsilon^{-1})$ space; Count-Min's $\Omega(\epsilon^{-1}\log\frac1\delta)$ heavy-hitter space is tight. **Multidimensional range-counting** has a cell-probe lower bound $\Omega((\log n/\log\log n)^{?})$-type for exactness, and approximate range-sum over $d$ dimensions inherits $\Omega(\log^{d-1} n)$ canonical-range costs. For arbitrary holistic measures with relative error, no $o(n)$ synopsis exists in general (information-theoretic: medians/exact distinct over adversarial skew). Communication-complexity (multi-party set-disjointness) underlies most of these.

## 6. The Gap
Closed for individual canonical measures (distinct, quantiles, point SUM/COUNT — optimal up to logs). The **open gap**: (i) joint synopses answering *mixed* holistic + linear cube queries with a single space-optimal structure; (ii) worst-case-optimal multidimensional range-aggregate synopses for $d>2$ with both tight space and query time; (iii) error bounds that hold under correlated dimensions and skew, not just independence. Hence "partially solved."

## 7. Current Research (as of June 2026)
Active: differentially-private cube synopses (composing DP mechanisms over the roll-up lattice with per-cuboid error); learned/data-aware sketches that beat worst-case sketches on real distributions; sketch fusion for multi-measure cubes (Apache DataSketches roadmap); GPU/vectorized sketch maintenance; **sketch-aware query optimization** choosing exact vs. approximate per subquery. Frontier: *space-optimal joint synopses for mixed holistic-and-linear high-dimensional cubes with correlation-robust bounds* remain unresolved *(frontier — verify)*. Groups: Cormode (Warwick), Woodruff (CMU), Liberty/DataSketches community, Garofalakis (TU Crete), warehouse vendors.

## 8. Future Work
- A unified, space-optimal synopsis for mixed measure types across the full cube lattice.
- Correlation- and skew-robust error bounds (beyond worst-case independence).
- Differentially-private rollup synopses with provable per-cuboid utility.
- Learned sketches with distribution-dependent guarantees, not just empirical wins.

## 9. Key References
- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005.
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA 2007.
- **[SOTA]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS 2010.
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams.* FOCS 2016 (KLL).
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
