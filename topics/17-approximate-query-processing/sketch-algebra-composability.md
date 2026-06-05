# Sketch Composability and Algebra

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sketch-algebra-composability` · **Status:** partially-solved

## 1. Problem Statement
Modern AQP systems precompute compact synopses ("sketches") per column or partition: Count-Min (CM) for frequency, HyperLogLog (HLL) for distinct counts, AKMV/$\theta$-sketches for set cardinality, and KLL/$t$-digest for quantiles. The composability problem asks for a *principled algebra* in which sketches are first-class values and relational operators — union ($\cup$), intersection ($\cap$), difference ($\setminus$), and equi-joins — map to closed-form operations on sketches with **propagated error bounds**.

Concretely, given sketches $S(A)$, $S(B)$ summarizing multisets $A,B$, we want operators $\oplus_\cup,\oplus_\cap,\oplus_{\setminus},\oplus_{\bowtie}$ such that $S(A)\oplus_\cup S(B)$ approximates $S(A\cup B)$ with a *certified* error $\varepsilon$ that is a known function of input errors and sketch sizes. The optimization variant asks for the minimal-size composite sketch achieving target accuracy; the decision variant asks whether a query plan's sketch pipeline meets an error SLA.

The difficulty: some sketches are linear/mergeable (CM, HLL via max-merge), so union is exact-to-the-sketch; but **intersection and difference are not closed** for HLL, and **joins** generally are not expressible without sketches that preserve coordinated samples (e.g., minhash/$k$-minimum-values with shared hash domain).

## 2. Mathematical Foundations
Let $h:\mathcal{U}\to[0,1]$ be a shared hash. A sketch is *linear* if $S(A\uplus B)=S(A)+S(B)$ (CM matrices add; multiplicity counting Bloom filters add). HLL registers merge by coordinate-wise max, giving exact union on the register state.

Set operations require **coordinated sampling**: AKMV/minhash retain the $k$ smallest hash values; with a shared hash, $J(A,B)=|A\cap B|/|A\cup B|$ is estimated from the fraction of bottom-$k$ values present in both, yielding $|A\cap B|=J\cdot|A\cup B|$ — the *inclusion–exclusion* route HLL lacks. $\theta$-sketches (Apache DataSketches) generalize this with a tunable sampling threshold $\theta$ and give unbiased union/intersection/difference with variance $\propto 1/k$.

Error propagation is the algebraic core: for CM with width $w$, height $d$, point error is $\hat f(x)\le f(x)+\varepsilon\|f\|_1$ w.p. $1-\delta$, $\varepsilon=e/w$, $\delta=e^{-d}$; under union the $\|f\|_1$ term composes additively. The open theory is a *type system* assigning each operator a transfer function on the pair (bias, variance), analogous to interval/affine arithmetic, closed under composition.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Cormode–Garofalakis "Sketching streams through the net" and Cohen's coordinated-sampling framework give composable estimators for unions and (bottom-$k$) intersections with provable variance.
- **Systems-SOTA:** Apache **DataSketches** (Yahoo/Apache, 2015–) ships Theta, HLL, KLL, CPC, and Tuple sketches with documented set-operation algebra and error formulas; **Druid**, **Snowflake** (`HLL`, `APPROX_PERCENTILE`), **BigQuery** (`HLL_COUNT.MERGE`), and **Spark** expose mergeable sketches but with limited intersection/join support.

## 4. Upper Bound
Union of HLL/CM/KLL is $O(m)$ in sketch size $m$ and *lossless at the sketch level* (no added error beyond the operands'). Bottom-$k$/Theta intersection over $r$ sets costs $O(rk)$ time with relative standard error $\Theta(1/\sqrt{k})$ on Jaccard, hence relative error on $|A\cap B|$ that degrades as overlap shrinks. KLL quantile merges achieve $\varepsilon$ rank error with $O(\tfrac{1}{\varepsilon}\log^2\log\tfrac{1}{\delta})$ space, fully mergeable (Karnin–Lang–Liberty, FOCS 2016).

## 5. Lower Bound
Intersection cardinality from independent sketches is information-theoretically hard: distinguishing disjoint vs. overlapping sets requires $\Omega(1/\varepsilon^2)$ samples for relative error $\varepsilon$ (set-disjointness communication lower bound, $\Omega(n)$ bits for exactness). HLL cannot support unbiased intersection at all without auxiliary coordination — inclusion–exclusion compounds variance multiplicatively, so error grows unboundedly as $|A\cap B|/|A\cup B|\to 0$. Difference inherits the same barrier.

## 6. The Gap
Union and quantile merge are essentially closed (matching $\Theta(1/\varepsilon)$-type bounds). The genuinely open part is a **unified algebra spanning all four operators with tight, composable relative-error guarantees**, especially for chained joins where coordination across $>2$ relations is needed. No type system today certifies end-to-end error for an arbitrary sketch query plan.

## 7. Current Research (as of June 2026)
Active work extends Tuple/Theta sketches to *attribute-carrying* joins and "sketch-aware" query optimization. Differentiable/learned sketches and provenance-carrying sketches are explored at MIT, CMU, and by the DataSketches community. *(frontier — verify)* Proposals for a formal "sketch type calculus" with composable error contracts appear in 2025 workshop venues but lack a peer-reviewed tightness proof.

## 8. Future Work
- A compositional type system propagating (bias, variance) through full relational plans.
- Coordinated multi-way join sketches with relative-error guarantees independent of join selectivity.
- Cost-based optimizer integration that treats error as a first-class plan dimension.

## 9. Key References
- **[Foundational]** Cormode, G., Muthukrishnan, S. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** Flajolet, P., Fusy, É., Gandouet, O., Meunier, F. *HyperLogLog.* AOFA, 2007. — [DOI](https://doi.org/10.46298/dmtcs.3545)
- **[SOTA]** Cohen, E. *Coordinated Sampling.* (sampling-based set-operation estimators), various incl. SIGMETRICS/PODS, 2014–2018. — [DOI](https://doi.org/10.1007/978-1-4939-2864-4_576)
- **[SOTA]** Apache DataSketches. *Theta, Tuple, HLL, KLL Sketch Library and Set Operations.* Apache Software Foundation, 2015–. — [Apache](https://datasketches.apache.org/)
- **[Survey]** Cormode, G., Garofalakis, M., Haas, P., Jermaine, C. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

**Union is closed; intersection is not.** Two HLL sketches summarize columns $A$ and $B$ with $p=4$ registers (16 buckets). For three buckets, $S(A)=[\dots,3,1,5,\dots]$ and $S(B)=[\dots,2,4,5,\dots]$ store the max leading-zero count seen per bucket.

*Union* $\oplus_\cup$ is coordinate-wise max: $[\max(3,2),\max(1,4),\max(5,5)] = [3,4,5]$. This is **exact at the sketch level** — the merged registers equal those a single HLL over $A\cup B$ would hold, so the union estimator inherits only the operands' error, no compounding. CM matrices behave the same way but add: $S(A)+S(B)$.

*Intersection* has no such closed register operation for HLL. We must go through inclusion–exclusion: $|A\cap B| = \widehat{|A|}+\widehat{|B|}-\widehat{|A\cup B|}$. Say $\widehat{|A|}=1000$, $\widehat{|B|}=1000$, $\widehat{|A\cup B|}=1900$, true overlap $100$. Each HLL term carries relative error $1.04/\sqrt{16}\approx 26\%$, i.e. absolute std $\approx 260$ on each $\sim$1000-count. The subtraction's error adds in quadrature: $\sqrt{260^2+260^2+494^2}\approx 612$, dwarfing the true answer $100$. So error grows unboundedly as $|A\cap B|/|A\cup B|\to0$ — exactly why Section 6 keeps intersection open while marking union closed.

---
*Part of the [DBMS Research catalog](../../README.md).*
