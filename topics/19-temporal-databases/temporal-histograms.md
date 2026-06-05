# Temporal Multidimensional Histograms

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-histograms` · **Status:** empirically-open

## 1. Problem Statement

A query optimizer estimating the selectivity of a temporal predicate — `period OVERLAPS [a,b)`, `CONTAINS`, `PRECEDES`, or a temporal join — needs the **joint distribution of period endpoints** $(s,e)$ with $s\le e$. Treating start and end as independent 1-D histograms badly mis-estimates, because endpoints are strongly correlated (long-lived rows have small $s$ and large $e$; bursty short events cluster near the diagonal). The problem: design a **multidimensional histogram** (a summary of bounded size $B$) over the 2-D endpoint space that yields accurate cardinality estimates for the full family of temporal/Allen predicates, is cheaply **constructible and maintainable** under inserts/expiry, and degrades gracefully under skew.

Variants: *construction* (given the dataset, build the $B$-bucket histogram minimizing estimation error — an optimization problem), *estimation* (answer a selectivity query from the histogram), *maintenance* (update under streaming inserts and now-relative expiry), *counting/quantile* (support temporal aggregation estimates). A central subtlety: the feasible region is the triangle $\{(s,e): s\le e\}$, so good bucketing must respect this geometry and the *duration* axis $d=e-s$.

## 2. Mathematical Foundations

Model the data as $n$ points in the half-plane $\{(s,e)\in\mathbb{T}^2 : s\le e\}$. A predicate like `OVERLAPS [a,b)` corresponds to the half-plane-intersection region $\{s<b \wedge e>a\}$ — an axis-parallel rectangular corner in $(s,e)$-space. Selectivity is the *2-D range count* of points in that region; thus the problem reduces to **2-D range-count estimation** from a space-bounded summary. The optimal partition into $B$ axis-parallel buckets minimizing sum-squared error is the classic **V-Optimal histogram**, whose exact 1-D solution is dynamic programming (Jagadish et al., *VLDB 1998*); in $\ge 2$ dimensions, optimal partitioning into arbitrary/hierarchical rectangles is **NP-hard** (Muthukrishnan–Poosala–Suel), forcing heuristics (MHIST, GENHIST, STHoles, the wavelet and **min-skew** methods of Acharya–Poosala–Ramaswamy for spatial data).

The error metric is typically relative $q$-error over a query workload; the information-theoretic lower bound on summary size relates to the **VC dimension** of the query class (axis-parallel rectangles in 2-D have VC dimension 4) via $\varepsilon$-approximations / **range-counting coresets**: a random sample of size $O(\varepsilon^{-2}(d + \log\frac1\delta))$ is an $\varepsilon$-approximation for rectangle ranges (Vapnik–Chervonenkis; Li–Long–Srinivasan), giving a *sampling* baseline against which histograms must justify their structure. Endpoint correlation is captured by the *duration distribution* $f_d$ conditioned on $s$; a faithful histogram is effectively a 2-D density over $(s,d)$ on the triangular support.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Multidimensional V-Optimal is NP-hard; practical near-optimal summaries are STHoles-style *self-tuning* histograms (Bruno–Chaudhuri–Gravano, *SIGMOD 2001*) that refine buckets from query feedback, and min-skew / GENHIST for correlated 2-D data. VC-based sampling gives distribution-free error guarantees but ignores structure.
- **Systems-SOTA:** Mainstream optimizers (PostgreSQL, SQL Server, Oracle, DB2) estimate temporal predicates with **per-column 1-D histograms + an independence/range assumption**, which is the documented weak point for period/range types; PostgreSQL's range-type selectivity uses bound histograms and an empirically tuned overlap heuristic but no true joint endpoint histogram. **Learned cardinality estimators** (MSCN, deep-learning and query-driven models) and **sampling-based** estimators are the most accurate available but are not period-aware out of the box. No production optimizer ships a dedicated 2-D endpoint histogram.

## 4. Upper Bound

A random sample (or 2-D $\varepsilon$-approximation / coreset) of size $O(\varepsilon^{-2}\log\frac1\delta)$ estimates any Allen-predicate selectivity to additive error $\varepsilon n$ with probability $1-\delta$ (VC dimension of rectangle ranges is constant). For *structured* histograms, GENHIST/min-skew with $B$ buckets give heuristic estimates computable in $O(\log B)$ per query and $O(n + B^2)$-ish construction; STHoles refines to near-V-Optimal accuracy on the observed workload with $O(B)$ feedback updates. Maintaining a 2-D equi-depth / wavelet summary under inserts costs $O(\log B)$ amortized per point, and now-relative expiry can be handled by aging the $e$-axis. So the achievable upper bound is: **$\varepsilon$-additive accuracy with $O(\varepsilon^{-2})$ space** distribution-free, or smaller workload-tuned summaries with no worst-case guarantee.

## 5. Lower Bound

Any summary giving additive $\varepsilon n$ error for **all** axis-parallel rectangle (hence overlap) queries must have size $\Omega(\varepsilon^{-1})$ in 1-D and the VC/discrepancy lower bounds push 2-D rectangle $\varepsilon$-approximations to $\Omega(\varepsilon^{-1}\log^{c}\varepsilon^{-1})$ (combinatorial discrepancy of axis-parallel boxes; Larsen and others) — strictly more than 1-D, formalizing why independent per-axis histograms cannot suffice. Computing the **optimal** $B$-bucket multidimensional histogram is **NP-hard** (Muthukrishnan–Poosala–Suel). For temporal *joins*, worst-case selectivity is governed by the **AGM bound** (Atserias–Grohe–Marx) on the underlying conjunctive query, and matching estimates from a bounded summary inherit the inherent multiplicative-error hardness of join-size estimation under bounded space (communication-complexity lower bounds for set-intersection size).

## 6. The Gap

This is **empirically open**: distribution-free sampling gives guarantees but is often too coarse/expensive at optimizer-relevant accuracy; structured 2-D histograms (min-skew, STHoles) and learned estimators are accurate on observed workloads but lack worst-case guarantees and are not period-aware in production. There is *no* standard, principled endpoint-correlation summary that (a) respects the triangular support, (b) covers the whole Allen-predicate family, (c) is maintainable under high-velocity insert/expiry, and (d) comes with usable error bounds. Closing it requires either a temporal-specialized histogram with provable $q$-error on Allen predicates, or a learned model with calibrated uncertainty — and a benchmark to compare them.

## 7. Current Research (as of June 2026)

- Period-aware and **learned** cardinality estimation for range/interval predicates, extending MSCN/deep-set models with explicit endpoint correlation features *(frontier — verify)*.
- Improved range-type / `tstzrange` selectivity in PostgreSQL and bound-histogram refinements, plus min-skew-style 2-D endpoint histograms studied in academic temporal-optimizer work (Dignös–Böhlen–Gamper line) *(frontier — verify)*.
- Coreset / sketch constructions for interval-overlap and temporal-join estimation with streaming maintenance under expiry *(frontier — verify)*.

## 8. Future Work

- A 2-D endpoint histogram with provable $q$-error guarantees across all Allen predicates and bounded space.
- Streaming-maintainable temporal histograms with explicit now-relative aging and skew robustness.
- Calibrated learned estimators for temporal joins integrated with AGM-aware worst-case fallbacks, plus a shared temporal-estimation benchmark.

## 9. Key References

- **[Foundational]** H. V. Jagadish, N. Koudas, S. Muthukrishnan, V. Poosala, K. Sevcik, T. Suel. *Optimal Histograms with Quality Guarantees.* VLDB, 1998. — [ACM](https://dl.acm.org/doi/10.5555/645924.671191)
- **[Foundational]** S. Muthukrishnan, V. Poosala, T. Suel. *On Rectangular Partitionings in Two Dimensions: Algorithms, Complexity, and Applications.* ICDT, 1999 (NP-hardness). — [DOI](https://doi.org/10.1007/3-540-49257-7_16)
- **[SOTA]** N. Bruno, S. Chaudhuri, L. Gravano. *STHoles: A Multidimensional Workload-Aware Histogram.* ACM SIGMOD, 2001. — [DOI](https://doi.org/10.1145/375663.375686)
- **[Foundational]** S. Acharya, V. Poosala, S. Ramaswamy. *Selectivity Estimation in Spatial Databases (min-skew).* ACM SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304182.304184)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM Journal on Computing, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[Foundational]** Y. Li, P. M. Long, A. Srinivasan. *Improved Bounds on the Sample Complexity of Learning (ε-approximations / VC).* JCSS, 2001. — [DOI](https://doi.org/10.1006/jcss.2000.1741)
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)

## 10. Worked Example

Take $n=6$ intervals as endpoint points $(s,e)$ in the triangle $s\le e$: three short bursty events near the diagonal $\{(0,1),(2,3),(4,5)\}$ and three long-lived rows $\{(0,5),(0,6),(1,6)\}$.

Query: `period OVERLAPS [3,4)`, i.e. count points with $s<4 \wedge e>3$. Scanning: $(0,5)$ yes, $(0,6)$ yes, $(1,6)$ yes, $(2,3)$ no ($e=3\not>3$), $(4,5)$ no ($s=4\not<4$), $(0,1)$ no. **True selectivity $=3/6$.**

Now estimate with *independent* 1-D histograms. Marginal $P(s<4)=5/6$ (only $s=4$ excluded); marginal $P(e>3)=4/6$ (the three long rows plus $(4,5)$). Independence gives $\hat P = \tfrac{5}{6}\cdot\tfrac{4}{6}=\tfrac{20}{36}\approx 0.56$, predicting $\approx 3.3$ rows — close here by luck, but it credits $(4,5)$ and the short events with overlap mass they don't have, because it ignores that **large $e$ correlates with small $s$** (long-lived rows). A joint $(s,e)$ bucket placed on the long-row cluster captures this; the independence assumption cannot, which is the core failure mode the 2-D endpoint histogram targets.

---
*Part of the [DBMS Research catalog](../../README.md).*
