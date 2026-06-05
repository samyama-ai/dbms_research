# Temporal Selectivity Estimation

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-selectivity-estimation` · **Status:** empirically-open

## 1. Problem Statement

The optimizer needs the **cardinality** of temporal predicates *before* execution to choose join order and physical operators. The two workhorses are:

- **Interval-overlap:** `|{ t : t.period OVERLAPS [a,b] }|` (and pairwise overlap-join size), and
- **As-of / timeslice:** `|{ t : a IN t.period }|`, i.e. "as the world looked at instant $a$".

Estimating these accurately is hard because real temporal data exhibit **correlated time skew**: arrival bursts, heavy-tailed interval durations, periodic seasonality, and correlation between an interval's *start* and its *length* (long-lived facts often start early). Treating start-time and duration as independent — the standard simplifying assumption — produces estimates that can be off by orders of magnitude on as-of queries deep in history. The problem is to build a **synopsis** (histogram, sketch, or learned model) of bounded space that gives provable or empirically robust relative-error guarantees for overlap and as-of selectivity under correlation, ideally update-able for streaming append-only temporal logs.

Variants: *point* as-of estimation (1-D stabbing count), *range* overlap estimation (2-D), the *join-size* (overlap self-join) counting variant, and the *quantile/worst-case* variant (bound error over all query instants).

This page is marked **empirically-open**: clean estimators exist for idealized inputs, but none is known to be robust across real correlated temporal workloads, and the gap is demonstrated by experiment rather than by a theorem.

## 2. Mathematical Foundations

Map each interval $[s,e]$ to the point $(s,e)$ in the half-plane $s\le e$. Then:
- **As-of($a$)** = stabbing count = points with $s \le a \le e$ = a 2-D dominance/orthogonal range count (a corner query).
- **Overlap($[a,b]$)** = $\{ s \le b \land e \ge a\}$ = a 2-D orthogonal range count.

So temporal selectivity is **2-D range counting** over the endpoint cloud, which is exactly where independence assumptions fail: the mass concentrates near the diagonal and along the $s$-axis.

Foundational machinery:
- **Histograms:** equi-depth, V-optimal (Jagadish et al.), MaxDiff/MHIST and the **STHoles** self-tuning multi-dimensional histogram (Bruno–Chaudhuri–Gravano, SIGMOD 2001) — directly applicable in endpoint space.
- **Sketches / sampling:** Count-Min (Cormode–Muthukrishnan), AGMS, and **distinct/range sampling**; **VC-dimension** bounds (Haussler–Welzl) say a random sample of size $O(\frac{d}{\varepsilon^2}\log\frac1\delta)$ is an $\varepsilon$-approximation for the range space of 2-D rectangles ($d=$ VC-dim, finite for orthogonal ranges), giving additive guarantees independent of skew.
- **Information theory:** the achievable error relates to the entropy of the joint $(s,e)$ distribution; correlation *reduces* effective dimensionality and can be exploited.

## 3. State of the Art (SOTA)

- **Theory:** $\varepsilon$-sample / $\varepsilon$-approximation theory (VC dimension) yields the cleanest *distribution-free* guarantee for as-of/overlap counts; **wavelet** and **AGMS sketch** synopses give space-error tradeoffs for range sums.
- **Temporal-specific:** histogram-based interval selectivity in PostgreSQL range types; the **GiST/SP-GiST** statistics on lower/upper bounds; work on **interval-join cardinality** estimation building on the endpoint-cloud view.
- **Learned estimators:** deep/learned cardinality estimators (MSCN — Kipf et al., 2019; and density-model approaches like Naru/DeepDB) applied to temporal/range predicates; empirically strong but without worst-case guarantees and sensitive to drift.
- **Systems:** commercial optimizers mostly model `period` predicates with 1-D histograms on start (or on a single endpoint), ignoring start/length correlation — the documented source of as-of mis-estimates.

## 4. Upper Bound

Using **VC-dimension $\varepsilon$-samples**, a uniform sample of $O(\varepsilon^{-2}\log\delta^{-1})$ intervals answers *every* overlap/as-of count with additive error $\varepsilon n$ w.p. $1-\delta$, independent of correlation — a strong distribution-free upper bound on space and accuracy. For *multiplicative* error, $q$-error-bounded histograms and 2-D V-optimal partitioning give bounded relative error but with space exponential in dimension in the worst case (mitigated to 2-D here). Streaming overlap counts admit $(\varepsilon,\delta)$ sketches in polylog space for range-sum queries.

## 5. Lower Bound

Multiplicative-error estimation of as-of counts in the *tail* (rare historical instants) is information-theoretically hard: distinguishing selectivity 0 from $1/n$ requires $\Omega(n)$ space in the worst case (a reduction from **set membership / index** in communication complexity), so no sublinear synopsis gives bounded *relative* error for arbitrarily rare instants. For 2-D range counting, **cell-probe** lower bounds (Pătraşcu) give $\Omega(\log n / \log\log n)$ query time for near-linear-space structures, and approximate range counting has matching space-time trade-offs. These bounds show the "robust under correlation, sublinear, multiplicative-error" combination is unattainable in full generality.

## 6. The Gap

The gap is **empirical, not asymptotic**: distribution-free additive guarantees (VC samples) exist but additive error is useless for the deep-history selective queries optimizers care about, while multiplicative accuracy is provably impossible in the tail. Between these poles, **no synopsis is known to be reliably accurate on real correlated temporal workloads** — learned models win benchmarks but lack guarantees and degrade under drift; classical 1-D histograms systematically mis-estimate as-of queries. Closing it means either a workload-aware estimator with PAC-style guarantees under a realistic correlation model, or a sharp characterization of which temporal distributions admit small accurate synopses.

## 7. Current Research (as of June 2026)

Active: correlation-aware 2-D synopses over the endpoint cloud; **learned + sketch hybrids** that fall back to sampling for tail queries with confidence bounds *(frontier — verify)*; robustness of learned cardinality estimators under temporal drift (continual learning) *(frontier — verify)*; and selectivity for as-of queries in cloud system-versioned tables. Relevant communities: the cardinality-estimation line (Kipf/Boncz/Leis on benchmarks like JOB), sketching (Cormode), and temporal-join groups (Dignös/Böhlen). Benchmark-driven "are learned estimators ready?" studies continue to report fragility on skewed/correlated data *(frontier — verify)*.

## 8. Future Work

- A correlation model for temporal data with provable synopsis size/error trade-offs.
- Drift-robust learned estimators with calibrated uncertainty for as-of/overlap.
- Tail-aware hybrids combining $\varepsilon$-samples (worst-case) with learned models (average-case).
- Standardized correlated-temporal benchmarks to make the "empirically-open" gap measurable.

## 9. Key References

- **[Foundational]** Selinger, P.G. et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Cormode, G., Muthukrishnan, S. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005.
- **[Foundational]** Bruno, N., Chaudhuri, S., Gravano, L. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD, 2001.
- **[Foundational]** Haussler, D., Welzl, E. *Epsilon-Nets and Simplex Range Queries.* Discrete & Computational Geometry, 1987.
- **[SOTA]** Kipf, A., Kipf, T., Radke, B., Leis, V., Boncz, P., Kemper, A. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019.
- **[Foundational]** Pătraşcu, M. *Lower Bounds for 2-Dimensional Range Counting.* STOC, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
