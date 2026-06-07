---
id: 26-cardinality-estimation/sketches-for-join-cardinality
title: "Sketches for Join Cardinality"
topic: 26-cardinality-estimation
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Sketches for Join Cardinality

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/sketches-for-join-cardinality` · **Status:** partially-solved

## 1. Problem Statement
Build small, **mergeable** sketches of base relations from which the size of a multi-way join (with predicates) can be estimated with **provable error**, ideally in a single pass and in a streaming/distributed setting. A sketch is a sublinear-space summary; *mergeable* means sketches of partitions combine into a sketch of the union (essential for distributed and incremental settings). The problem: which sketch families support join-size estimation with relative-error guarantees, for which join shapes, and at what space/time cost. Variants: **two-way self/equi-join** (the $\sum f_i g_i$ inner-product / $F_2$-style quantity), **multi-way joins**, **set-valued** (distinct) vs **bag-valued** semantics, and **predicate-restricted** joins.

## 2. Mathematical Foundations
For an equi-join on attribute $A$ with frequency vectors $f, g$ (frequency of each value in $R, S$), the join size is the inner product $|R \bowtie_A S| = \sum_v f_v g_v = \langle f, g\rangle$. **AMS / tug-of-war sketches** (Alon–Matias–Szegedy) estimate $\langle f, g\rangle$ via random $\pm1$ projections $X = \sum_v \epsilon_v f_v$, $Y = \sum_v \epsilon_v g_v$ (shared 4-wise-independent $\epsilon$), with $\mathbb{E}[XY] = \langle f,g\rangle$ and variance $\le \|f\|_2^2 \|g\|_2^2$; averaging/medianing $O(\frac{1}{\epsilon^2}\log\frac1\delta)$ copies gives an $(\epsilon\,\|f\|_2\|g\|_2)$-additive estimate. **Count-Min / Count-Sketch** estimate per-value frequencies and support skew-aware join estimation. For **distinct** join cardinality, **HyperLogLog** and **KMV (k-minimum-values) / bottom-k** sketches estimate $|\,\pi(R \bowtie S)\,|$ and are mergeable. Multi-way joins require **degree-aware** or **sampling-augmented** sketches because naive AMS variance explodes with join arity and skew.

## 3. State of the Art (SOTA)
**Theory-SOTA:** AMS sketches (1996) give the canonical $F_2$/inner-product guarantee; **Count-Sketch** (Charikar–Chen–Farach-Colton, 2002) and **Count-Min** (Cormode–Muthukrishnan, 2005) are the workhorses for skewed frequencies and ship in many systems. For distinct-value joins, **HLL** (Flajolet et al., 2007) and theoretically-optimal distinct-counting sketches (Kane–Nelson–Woodruff, 2010) are mergeable with relative-error guarantees. Multi-way join sizes under sketches were advanced by **Dobra–Garofalakis–Gehrke–Rastogi** (sketch-based processing of aggregate queries over streams) and **degree-based / "join sampling with sketches"** lines. **Systems-SOTA:** sketches are used for distinct counts and heavy hitters widely (Spark, Redis, DataSketches/Apache); join-cardinality use is more limited, with recent learned + sketch hybrids and **degree-sketch** estimators feeding optimizers.

## 4. Upper Bound
For two-way equi-join inner product, AMS achieves an $\epsilon\|f\|_2\|g\|_2$ additive error (hence small *relative* error when the join is not dominated by tiny-frequency cancellation) using $O(\frac{1}{\epsilon^2}\log\frac1\delta)$ words, in one pass, fully mergeable, with $O(1)$ amortized update. Distinct-join cardinality via KMV/HLL: $(1\pm\epsilon)$ relative error in $O(\epsilon^{-2}\log\frac1\delta)$ space, mergeable. Count-Sketch yields point-frequency estimates with $\ell_2$ error guarantees usable for skew-corrected join estimates. These hold in the **streaming / mergeable-summary model**.

## 5. Lower Bound
Estimating the **bag join size** $\langle f,g\rangle$ to relative error $\epsilon$ in the streaming model requires $\Omega(\epsilon^{-2})$ space, matching AMS up to logs (via communication complexity of GAP-HAMMING / INDEX-style reductions). Worse, for **multi-way** joins, relative-error estimation from sketches alone can require space polynomial in the data on adversarial skewed inputs — the variance/space lower bounds grow with join arity because the estimand is a higher-order tensor contraction, not a single inner product. Distinct counting has a tight $\Omega(\epsilon^{-2} + \log n)$ space lower bound (Kane–Nelson–Woodruff). Heavy cancellation/skew can make any small sketch's relative error unbounded.

## 6. The Gap
Partially solved. **Two-way** equi-join and **distinct** join cardinality are essentially closed: matching $\Theta(\epsilon^{-2})$ upper/lower bounds, mergeable, practical. The open gap is **multi-way joins with predicates under skew**: no mergeable sketch gives relative-error guarantees with sublinear space in the worst case, and practical variance is large. Closing it likely requires combining sketches with **degree/sampling** information (so heavy keys are handled exactly and light keys via sketch), and tighter analysis of multi-way variance — bridging to worst-case-optimal-join and degree-constrained-bound theory.

## 7. Current Research (as of June 2026)
Directions: (i) **degree- and sample-augmented sketches** for multi-way joins that cap variance under skew *(frontier — verify)*; (ii) **learned sketches** and learning-augmented frequency estimation (Hsu et al., learning-based Count-Min) improving constants on real data with retained worst-case fallback; (iii) **mergeable sketches for distributed/streaming optimizers** integrated as certified statistics; (iv) sketch + bound hybrids feeding pessimistic estimators. Groups: Cormode (Warwick), Woodruff (CMU), Garofalakis, and the Apache DataSketches community.

## 8. Future Work
Mergeable multi-way join sketches with provable relative error under skew; predicate-aware sketches (join restricted by selections); tight space–accuracy trade-offs for cyclic joins; learning-augmented sketches with guaranteed worst-case behavior; and standard integration as maintainable optimizer statistics under updates.

## 9. Key References
- **[Foundational]** Alon, Matias, Szegedy. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996 / JCSS, 1999. — [DOI](https://doi.org/10.1145/237814.237823)
- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[SOTA]** Charikar, Chen, Farach-Colton. *Finding Frequent Items in Data Streams (Count-Sketch).* ICALP, 2002. — [DOI](https://doi.org/10.1007/3-540-45465-9_59)
- **[SOTA]** Dobra, Garofalakis, Gehrke, Rastogi. *Processing Complex Aggregate Queries over Data Streams.* SIGMOD, 2002. — [DOI](https://doi.org/10.1145/564691.564699)
- **[SOTA]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Two-way equi-join $R\bowtie_A S$ on a domain $\{1,2,3\}$. Frequencies: $f=(3,1,0)$ in $R$ (value 1 appears 3 times, value 2 once), $g=(2,0,4)$ in $S$. True join size is the inner product $\langle f,g\rangle = 3\cdot2 + 1\cdot0 + 0\cdot4 = 6$ (the 3 tuples with $A{=}1$ in $R$ pair with 2 in $S$).

AMS sketch: draw $\pm1$ signs $\epsilon=(\epsilon_1,\epsilon_2,\epsilon_3)$. Build $X=\sum_v \epsilon_v f_v$ over $R$ and $Y=\sum_v \epsilon_v g_v$ over $S$ using the *shared* signs. Say $\epsilon=(+1,-1,+1)$: then $X = 3-1+0 = 2$, $Y = 2-0+4 = 6$, and the single-copy estimate is $XY = 12$ — noisy. Over the random signs, $\mathbb{E}[XY] = \sum_v f_v g_v = 6$ (cross terms $\epsilon_u\epsilon_v$ vanish in expectation since $\mathbb{E}[\epsilon_u\epsilon_v]=0$ for $u\neq v$). Averaging $O(\varepsilon^{-2})$ independent copies drives the estimate to $6$ with additive error $\varepsilon\|f\|_2\|g\|_2 = \varepsilon\sqrt{10}\cdot\sqrt{20}\approx 14.1\,\varepsilon$. Crucially $X,Y$ are computed in one pass and are mergeable: signs are shared, so partition sketches simply add.

---
*Part of the [DBMS Research catalog](../../README.md).*
