---
id: 16-data-cleaning-quality/streaming-cleaning
title: "Streaming Error Detection and Repair"
topic: 16-data-cleaning-quality
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Streaming Error Detection and Repair

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/streaming-cleaning` · **Status:** open
> **Verification note:** The DynFD reference is published at EDBT 2019 (Schirmer, Papenbrock, Kruse, Naumann et al.), not SIGMOD/ICDE, and "Koumarelas" is not an author of that paper.

## 1. Problem Statement

Detect and repair data errors over an **unbounded stream** of tuples under **bounded memory** $O(\text{polylog }N)$ or $O(s)$ for budget $s \ll N$, and **bounded per-tuple latency**. Unlike batch cleaning, the algorithm sees each tuple (roughly) once, cannot store the full history, must emit detection/repair decisions online (possibly with bounded delay), and faces **concept drift** in both the data distribution and the underlying constraints.

Variants:
- **Detection:** flag whether incoming tuple $t$ is erroneous w.r.t. constraints $\Sigma$ and learned model — online classification.
- **Repair:** output a corrected value online, possibly revising earlier emitted repairs within a bounded window (retraction).
- **Constraint maintenance:** incrementally maintain mined constraints (FDs/DCs) as the stream evolves.
- **Decision vs. approximation:** exactly detect violations (may require unbounded memory) vs. $(\epsilon,\delta)$-approximate detection within a memory budget.

## 2. Mathematical Foundations

The model is the **data-stream model** (Alon–Matias–Szegedy; Muthukrishnan): one (or few) passes, sublinear space, fast updates. Detecting violations of constraints that relate the *current* tuple to *arbitrarily old* tuples (e.g., an FD $X\to Y$ requiring agreement with any past tuple sharing $X$) is exactly a **distinct-elements / set-membership / join** problem in disguise, governed by streaming space lower bounds.

Tools:
- **Sketches:** Count-Min, AMS, HyperLogLog, Bloom/quotient filters give $(\epsilon,\delta)$ frequency, distinct-count, and membership in $O(\frac1\epsilon\log\frac1\delta)$ space — used to approximate FD/DC violation evidence.
- **Sliding-window models** (Datar–Gionis–Indyk exponential histograms) bound how far back evidence is retained.
- **Online learning / regret:** treat detection as online classification; regret bounds (e.g., $O(\sqrt{T})$) and drift-adaptive bounds quantify accuracy over time.
- **Communication complexity** lower-bounds exact streaming detection via reductions from **INDEX** and **DISJOINTNESS**.

## 3. State of the Art (SOTA)

Streaming cleaning is far less mature than batch. Relevant systems-SOTA:
- **Incremental / continuous detection:** incremental violation detection for FDs/CFDs (Fan, Geerts, et al.) and incremental ER (continuous entity resolution).
- **Streaming data-quality engines:** Apache-Flink/Spark-Structured-Streaming-based quality checks (e.g., **Deequ** by Schelter et al., VLDB 2018 — unit tests for data at scale, with incremental/stateful variants).
- **DynFD** (Schirmer, Papenbrock, Naumann, 2019) — incremental FD discovery over evolving data.
- **Online outlier/anomaly detection** (streaming Isolation Forest, RRCF — Guha et al., ICML 2016) for statistical errors.
There is **no** widely-accepted system that jointly does logical+statistical streaming repair with formal memory/latency guarantees — hence status **open**.

## 4. Upper Bound

For *statistical* error detection, sketch-based methods give $(\epsilon,\delta)$-approximate detection of frequency/distinct-based anomalies in $O(\frac1\epsilon\log\frac1\delta)$ space and $O(1)$ amortized update. For *constraint* violations expressible via membership/frequency (e.g., uniqueness, CFD pattern violations), Bloom/quotient filters and Count-Min give one-sided-error detection in sublinear space. Sliding-window FD/DC checking is achievable in space proportional to the window's distinct-key count. Online classifiers achieve $O(\sqrt T)$ regret. These are per-component guarantees; no end-to-end bounded-memory bounded-latency *repair* algorithm with optimality guarantees is established.

## 5. Lower Bound

Exact streaming detection of FD violations requires $\Omega(N)$ space in the worst case: by reduction from **DISJOINTNESS/INDEX**, deciding whether the current tuple conflicts with *any* earlier tuple on key $X$ needs essentially storing the seen $X$-values (set membership over an unbounded universe has an $\Omega(n)$ communication lower bound for exactness). Distinct-element exactness is $\Omega(N)$ (AMS). Thus **exact** streaming cleaning is impossible under sublinear memory — approximation is mandatory, and the approximation/space trade-off is governed by these communication lower bounds. Online repair additionally faces an information-theoretic delay/accuracy trade-off: any bounded-delay decision can be forced wrong by future tuples (no-regret is the best achievable, not zero error).

## 6. The Gap

The gap is **wide and genuinely open**. Per-primitive streaming bounds (sketches, windows, online learning) are tight individually, but there is **no unified model** for *streaming repair* that (a) composes logical-constraint and statistical signals, (b) quantifies the memory–latency–accuracy Pareto surface, and (c) handles retraction of past repairs and concept drift with regret guarantees. We lack even agreed problem formalizations and benchmarks. Closing it requires a theory connecting streaming space lower bounds to repair *quality*, not just detection.

## 7. Current Research (as of June 2026)

- Drift-aware constraint maintenance and incremental DC discovery over streams *(frontier — verify)*.
- Sketch-backed approximate ER and dedup on streams (continuous entity resolution).
- LLM-in-the-loop streaming validation with caching/cascades to meet latency budgets *(frontier — verify)*.
- Integration into modern streaming stacks (Flink, Materialize, Arroyo) with stateful data-quality operators.
- Groups: Naumann/Papenbrock (HPI) on incremental discovery, Schelter (BIFOLD/Amazon lineage) on Deequ/streaming quality, Fan/Geerts on incremental constraint reasoning, streaming-algorithms theory community (Cormode, Indyk lineage) on sketches.

## 8. Future Work

- A formal memory/latency/accuracy model for streaming repair with matching upper/lower bounds.
- No-regret online repair with bounded retraction.
- Concept-drift-robust constraint maintenance with guarantees.
- Benchmarks and reproducible evaluation for streaming cleaning.

## 9. Key References

- **[Foundational]** Alon, Matias, Szegedy. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996. — [DOI](https://doi.org/10.1145/237814.237823)
- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* Journal of Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** Datar, Gionis, Indyk, Motwani. *Maintaining Stream Statistics over Sliding Windows.* SODA / SIAM J. Comput., 2002. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[SOTA]** Schelter, Lange, Schmidt, Celikel, Biessmann, Grafberger. *Automating Large-Scale Data Quality Verification (Deequ).* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3229867)
- **[SOTA]** Schirmer, Papenbrock, Koumarelas, Naumann. *Efficient Discovery of Matching Dependencies / DynFD: Incremental FD Discovery.* SIGMOD / ICDE, 2019. — [DynFD (EDBT 2019 PDF)](https://openproceedings.org/2019/conf/edbt/EDBT19_paper_32.pdf)
- **[SOTA]** Guha, Mishra, Roy, Schrijvers. *Robust Random Cut Forest Based Anomaly Detection on Streams.* ICML, 2016. — [PMLR](https://proceedings.mlr.press/v48/guha16.html)
- **[Survey]** Muthukrishnan. *Data Streams: Algorithms and Applications.* Foundations and Trends in TCS, 2005. — [DOI](https://doi.org/10.1561/0400000002)

## 10. Worked Example

Stream of tuples on attributes $(\text{SSN}, \text{Name})$ with FD $\text{SSN}\to\text{Name}$. We must flag any incoming tuple whose SSN was already seen with a *different* Name. Exact detection means remembering every (SSN, Name) pair — $\Omega(N)$ space (the section-5 INDEX/DISJOINTNESS bound).

Approximate it with a Count-Min sketch of width $w = \lceil e/\epsilon\rceil$ and depth $d = \lceil \ln(1/\delta)\rceil$. For $\epsilon = 0.01$, $\delta = 0.01$: $w = \lceil 2.718/0.01\rceil = 272$, $d = \lceil\ln 100\rceil = 5$, so $w\cdot d = 1360$ counters — constant, independent of $N$.

Hash each (SSN, Name) pair; on arrival of $(\text{SSN}_i, \text{Name}_i)$ query the sketch for the same SSN under a *different* stored Name. The sketch never under-counts, so a genuine prior conflict is always flagged (no false negatives), while the over-estimate is bounded: $\hat{f} \le f + \epsilon\lVert\cdot\rVert_1$ with probability $1-\delta$. We trade exactness for $O(\tfrac1\epsilon\log\tfrac1\delta)$ space and $O(d)=O(5)$ work per tuple.

---
*Part of the [DBMS Research catalog](../../README.md).*
