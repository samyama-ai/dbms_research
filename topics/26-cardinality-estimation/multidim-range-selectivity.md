# Range-Predicate Selectivity in High Dimensions

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/multidim-range-selectivity` · **Status:** open

## 1. Problem Statement

Given a relation $R$ over $d$ numeric attributes $A_1,\dots,A_d$ and an axis-parallel range query $Q = \bigwedge_{i=1}^{d} (l_i \le A_i \le u_i)$ (with some predicates possibly absent), estimate the **selectivity** $\sigma(Q) = |\{t \in R : t \models Q\}| / |R|$. The challenge is to build a **compact synopsis** (sublinear in $|R|$, and not exponential in $d$) that answers arbitrary range queries with bounded relative error.

Variants:
- **Counting / estimation variant:** return an approximate count $\hat{c}$ with $|\hat{c} - c| \le \varepsilon$ guarantees (additive over $|R|$, or multiplicative).
- **Construction (optimization) variant:** under a space budget $B$, build the synopsis minimizing worst-case or expected query error.
- **Online variant:** support insertions/deletions while preserving the bound.

The core difficulty is **attribute correlation**: assuming independence factorizes $\sigma(Q) = \prod_i \sigma_i$, which is cheap but badly wrong under correlation, while a full $d$-dimensional histogram costs $O(b^d)$ buckets.

## 2. Mathematical Foundations

Model $R$ as an empirical measure on $\mathbb{R}^d$; a range query asks for the measure of an axis-parallel box. This is the dual of the **range-counting** problem in computational geometry. The relevant complexity is governed by the **VC dimension** of axis-parallel boxes in $\mathbb{R}^d$, which is $2d$. An **$\varepsilon$-approximation** of size $O((d/\varepsilon^2)\log(d/\varepsilon))$ exists (Vapnik–Chervonenkis / Li–Long–Srinivasan), giving additive $\varepsilon|R|$ error for all boxes simultaneously, *independent of $d$ except polynomially*.

Synopsis families and their algebra:
- **Multidimensional histograms:** partition $\mathbb{R}^d$ into buckets, assume uniformity within a bucket; error driven by intra-bucket variance.
- **Wavelets / DCT:** store top-$k$ coefficients of the data distribution; selectivity is a linear functional, recoverable from coefficients.
- **Sketches:** $\varepsilon$-approximations, Count-Min over a grid, or **range-summable random variables** for dyadic decomposition ($O(\log^d n)$ canonical ranges).
- **Models:** kernel density estimators and, recently, learned autoregressive factorizations $\Pr[A_1,\dots,A_d] = \prod_i \Pr[A_i \mid A_{<i}]$.

Information-theoretically, capturing an arbitrary joint distribution to multiplicative accuracy requires $\Omega(b^d)$ bits in the worst case; tractability hinges on **low-rank / low-entropy structure** in real data.

## 3. State of the Art (SOTA)

**Theory-SOTA:** $\varepsilon$-approximations / $\varepsilon$-nets give dimension-robust additive guarantees; coresets for range counting (Phillips, Agarwal–Har-Peled–Varadarajan) refine constants. Dyadic Count-Min and range-summable sketches give $O(\text{polylog})$ canonical-range decompositions.

**Systems-SOTA:**
- **GENHIST** and **STHoles** (Bruno–Chaudhuri–Gravano, SIGMOD 2001) — multidimensional/feedback histograms.
- **Wavelet-based** synopses (Chakrabarti–Garofalakis–Rastogi–Shim, VLDB 2000).
- **Learned models:** **Naru/NeuroCard** (Yang et al., VLDB 2020/2021) — deep autoregressive density estimators answering range queries via progressive sampling; **DeepDB** (Hilprecht et al., VLDB 2020) — relational sum-product networks; **FLAT**, **Quicksel** (kernel-based, Park et al. 2020). These dominate single-table range-selectivity benchmarks but cost training and are stale under updates.

## 4. Upper Bound

For all-box additive error $\varepsilon |R|$ with probability $1-\delta$: a random sample of size $O(\varepsilon^{-2}(d\log(1/\varepsilon) + \log(1/\delta)))$ suffices (VC sampling bound). Deterministic $\varepsilon$-approximations of size $O(d \, \varepsilon^{-2}\log(d/\varepsilon))$ are constructible. Range-tree / dyadic synopses answer a box in $O(\log^d |R|)$ canonical-range lookups with $O(|R|\log^{d-1}|R|)$ space. Learned autoregressive models achieve strong empirical multiplicative error in $O(d)$ network passes per estimate, but **no distribution-free multiplicative bound** is known.

## 5. Lower Bound

Multiplicative selectivity estimation under arbitrary correlations is information-theoretically hard: distinguishing a near-empty box from a populated one to within a constant factor can require $\Omega(b^d)$ space (a counting argument over $b^d$-cell distributions). Range-counting data structures face cell-probe lower bounds: for $d$-dimensional dominance/range counting, $\Omega(\log n / \log\log n)$ query time with near-linear space (Pătrașcu, and Pătrașcu–Thorup style bounds). For approximate range counting, the VC bound is essentially tight up to logarithmic factors (matching lower bounds on $\varepsilon$-approximation size).

## 6. The Gap

The **additive**, all-queries problem is essentially closed (VC upper bound matches lower bound up to logs). The genuinely **open** problem is **multiplicative** accuracy for selective (small-result) queries under correlation within a *sub-exponential-in-$d$* budget: learned models do well empirically but lack worst-case guarantees, and the worst-case lower bound is exponential. What would close it: a structural assumption (bounded statistical rank, sparse dependency graph) under which provable multiplicative bounds with polynomial-in-$d$ space are achievable, plus matching hardness for that structured class.

## 7. Current Research (as of June 2026)

- **Learned cardinality estimators** under updates and distribution shift; robustness/uncertainty quantification for Naru-style models *(frontier — verify)*.
- **Factorized / structured density models** bridging sum-product networks and autoregressive models with formal error bounds.
- **Coreset and $\varepsilon$-approximation** refinements for streaming, high-velocity settings (Agarwal, Phillips, Matoušek lineage).
- Benchmark-driven critiques (the "Are We Ready for Learned CE?" line, Wang et al.) pushing reproducibility and worst-case stress tests.

## 8. Future Work

- Distribution-free or structure-parameterized **multiplicative** guarantees for range selectivity.
- Synopses that compose across joins (single-table accuracy does not survive joins).
- Cheap incremental maintenance of learned synopses under high update rates.
- Tight characterization of which real-world correlation structures admit sub-exponential synopses.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Vapnik, Chervonenkis. *On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities.* 1971.
- **[SOTA]** Bruno, Chaudhuri, Gravano. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD, 2001.
- **[SOTA]** Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2020.
- **[SOTA]** Hilprecht et al. *DeepDB: Learn from Data, not from Queries.* VLDB, 2020.
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
