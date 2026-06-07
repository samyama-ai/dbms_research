---
id: 31-time-series-db/tag-inverted-index-design
title: "Inverted-index design for tag matching"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Inverted-index design for tag matching

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/tag-inverted-index-design` · **Status:** partially-solved

## 1. Problem Statement
Queries select series by **boolean predicates over labels/tags**: `method="GET" AND region=~"us-.*" AND NOT env="staging"`. The engine must resolve such a predicate into the set of matching series ids (a *posting set*) quickly, then scan only those series' chunks. The design problem: build an index over (label, value) → series-id postings that is simultaneously **space-optimal** (it sits alongside huge raw data) and **latency-optimal** for arbitrary conjunctions, disjunctions, negations, and regex/range matchers.

- **Decision variant:** is series $s$ in the answer set of predicate $P$?
- **Set/enumeration variant:** materialize $\{s : P(s)\}$ — the real workload, an intersection/union/difference of posting lists.
- **Optimization variants:** (a) minimize index bytes per (label,value) pair given a latency SLO; (b) minimize predicate-evaluation time given a space budget; (c) order the intersection of $k$ posting lists to minimize total work.

It is **partially-solved**: inverted-index + compressed-bitmap technology is mature and near-optimal for conjunctions, but optimal handling of high-cardinality values, regex/range matchers, and worst-case-optimal multi-list intersection remain open.

## 2. Mathematical Foundations
The index is a classic **inverted index**: for each term $(L{=}v)$ a sorted posting list $P_{L,v}\subseteq[N]$. A conjunction is a **sorted-set intersection** $\bigcap P_{L_i,v_i}$; disjunction a union; negation a complement against the universe. Postings are stored as **compressed bitmaps** (Roaring) or delta-gap-encoded integer lists.

Multi-list intersection has an **instance-optimal** theory: with $k$ sorted lists, the lower bound is $\Omega(\log\binom{m}{t})$-style — captured by the *proof/certificate* (gallop/SvS) framework of Demaine–López-Ortiz–Munro and Barbay–Kenyon; adaptive intersection runs in time proportional to the smallest *certificate of the answer*, not the list sizes. Worst-case-optimal **join** theory (NPRR / Leapfrog Triejoin, Ngo–Ré–Rudra) bounds the work of multi-way predicate evaluation by the **AGM bound** of the underlying hypergraph, the same quantity governing realized cardinality. Boolean predicate selectivity connects to set-cover / **submodular** coverage when choosing which list to probe first.

Regex/range matchers over a label's value set reduce to enumerating matching terms (an FST/trie lookup, as in Lucene's automaton intersection) then unioning their postings; an **FST** stores the term dictionary in near-entropy space with automaton-driven prefix/regex traversal.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Prometheus TSDB uses per-block inverted indexes with sorted posting lists and label→value FST-like dictionaries; intersection by sorted merge. **Roaring bitmaps** (Lemire et al.) are the de-facto posting representation in Druid, Pinot, M3DB, and many TSDBs — hybrid array/bitmap/run containers giving SIMD-friendly AND/OR/ANDNOT. VictoriaMetrics builds a custom inverted index optimized for high cardinality. Lucene's FST term dictionary + automaton intersection is the canonical regex/range design.
- **Theory-SOTA:** Leapfrog Triejoin / worst-case-optimal joins (Veldhuizen; Ngo–Ré–Rudra) for multi-predicate evaluation; adaptive sorted-set intersection (Barbay–Kenyon) for the instance-optimal conjunction.

## 4. Upper Bound
- **Conjunction of $k$ lists:** adaptive intersection in $O(\text{certificate} \cdot \log k)$ comparisons (instance-optimal); SvS/gallop in practice. Roaring AND is $O(\text{containers})$ with SIMD constants.
- **Worst-case multi-predicate:** Leapfrog Triejoin runs in $O(\text{AGM bound})$ time, instance-/worst-case-optimal.
- **Space:** Roaring postings approach the information-theoretic minimum for the density regime; FST term dictionary near $H_0$ entropy of the value set.
- **Regex/range:** automaton-intersection on the FST is linear in matched-term + posting-union size.

## 5. Lower Bound
Sorted-set intersection has an **adaptive lower bound** of $\Omega(\sum \log(\text{gap}))$ — the certificate complexity (Demaine–López-Ortiz–Munro): no algorithm beats the answer's intrinsic proof size. Worst-case multi-predicate evaluation cannot beat the **AGM bound** (it is a true output-size lower bound: the result can be that large). For predecessor/range probes into a posting structure, **cell-probe** lower bounds (Pătraşcu–Thorup) give $\Omega(\log\log)$-type query costs at near-linear space. Exact membership across all series is $\Omega(N)$ space (each series distinguishable).

## 6. The Gap
For pure conjunctions the gap is **essentially closed**: adaptive intersection + Roaring match the certificate lower bound up to constants, and Leapfrog Triejoin is worst-case-optimal. The **open** residue: (1) optimal *probe ordering* for mixed AND/OR/NOT with regex matchers, where selectivity estimation drives cost and current planners use crude heuristics; (2) space–latency Pareto for *very high-cardinality* labels (millions of values) where posting lists are tiny but numerous — the FST/dictionary overhead dominates; (3) cache/SIMD-optimal layouts whose theory lags the engineering. These are practical/optimality gaps, not existence gaps.

## 7. Current Research (as of June 2026)
Roaring continues evolving (Roaring64, SIMD/AVX-512 kernels) as the posting standard. Research on **worst-case-optimal-join planners applied to tag matching** and on **learned cardinality estimation** for posting-list intersection ordering is active *(frontier — verify maturity)*. VictoriaMetrics and Grafana Mimir publish ongoing index-compression and per-day-index work for the high-cardinality regime. Succinct/FST term-dictionary research (and SuRF-style range filters) targets the value-explosion case. Groups: Daniel Lemire (Roaring), Ngo/Ré/Rudra and the worst-case-optimal-join community, Lucene/Tantivy maintainers, VictoriaMetrics.

## 8. Future Work
- Cost-based predicate planners that pick intersection order and AND/OR/NOT decomposition optimally under learned selectivity.
- Index layouts on the proven space–latency Pareto frontier for million-value labels.
- WCOJ-style guarantees integrated into production TSDB query planners.
- Succinct range/regex filters (SuRF-class) co-designed with posting compression.

## 9. Key References
- **[Foundational]** Demaine, López-Ortiz, Munro. *Adaptive Set Intersections, Unions, and Differences.* SODA, 2000. — [ACM](https://dl.acm.org/doi/10.5555/338219.338634) — [DBLP](https://dblp.uni-trier.de/rec/conf/soda/DemaineLM00.html)
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018. — [arXiv](https://arxiv.org/abs/1203.1952) — [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Lemire, Boytsov, Kurz, et al. *Roaring Bitmaps: Implementation of an Optimized Software Library.* Software: Practice and Experience, 2018. — [arXiv](https://arxiv.org/abs/1709.07821) — [DOI](https://doi.org/10.1002/spe.2560)
- **[SOTA]** Veldhuizen. *Leapfrog Triejoin: A Simple, Worst-Case Optimal Join Algorithm.* ICDT, 2014. — [arXiv](https://arxiv.org/abs/1210.0481) — [DOI](https://doi.org/10.5441/002/icdt.2014.13)
- **[Foundational]** Pătraşcu, Thorup. *Time-Space Trade-offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043) — [DOI](https://doi.org/10.1145/1132516.1132551)
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (relational/boolean query foundations). — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)

## 10. Worked Example

Universe of 10 series, ids $0..9$. Posting lists:
- $P_{\text{method=GET}} = \{0,2,3,5,6,8,9\}$ (7 ids)
- $P_{\text{region=us-east}} = \{2,5,9\}$ (3 ids)
- $P_{\text{env=staging}} = \{3,5\}$ (2 ids)

Evaluate `method="GET" AND region="us-east" AND NOT env="staging"`.

**Probe ordering matters.** Intersect the two smallest lists first: $P_{\text{region}} \cap P_{\text{method}}$. Galloping the 3-element region list into the 7-element method list, each lookup is $O(\log)$ in the *gap* it skips, not the full list — certificate-driven cost. Result: $\{2,5,9\}$ (all three are GET). Now subtract $P_{\text{env=staging}}=\{3,5\}$: drop $5$, giving $\{2,9\}$.

Had we started with the 7-element list, we would touch more elements for the same answer — the adaptive lower bound $\Omega(\sum\log(\text{gap}))$ says the *intrinsic* certificate here is tiny ($|$answer$|=2$), and gallop-from-smallest nearly achieves it. With Roaring, each list is an array container; AND/ANDNOT run as SIMD-friendly merges over containers, the same plan at machine scale.

---
*Part of the [DBMS Research catalog](../../README.md).*
