---
id: 26-cardinality-estimation/synopsis-information-limits
title: "Information-Theoretic Limits of CE Synopses"
topic: 26-cardinality-estimation
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Information-Theoretic Limits of CE Synopses

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/synopsis-information-limits` · **Status:** partially-solved

## 1. Problem Statement
A **cardinality-estimation synopsis** is a compact data structure $\mathcal{S}$ (histogram, sketch, sample, learned model) summarizing a relation (or joint distribution) so that, for queries $q$ in a class $\mathcal Q$, an estimator returns $\widehat{|q|}$ close to the true cardinality $|q|$. The problem: **determine the minimum space (bits) of any synopsis** that guarantees a target estimation error $\varepsilon$ for a given query class.

Variants:
- **Space-for-accuracy (optimization):** minimize $|\mathcal S|$ s.t. error $\le \varepsilon$ on all $q\in\mathcal Q$.
- **Accuracy-for-space (dual):** given $B$ bits, minimize worst-case error.
- **Per-class instantiations:** range queries (1-D and multi-D), equality/point queries, conjunctive (join) queries, distinct-value queries — each has its own lower-bound regime.

This is the *theoretical backbone* under all the other CE problems: it asks what is **fundamentally impossible**, independent of cleverness in algorithm design.

## 2. Mathematical Foundations
The natural tools are **communication complexity**, the **cell-probe model**, and **information theory**:
- **Range counting / range queries:** lower bounds come from the cell-probe and group models; for $d$-dimensional range counting, structures face $\Omega\big((\log n/\log\log n)\big)$-type query-time lower bounds (Pătraşcu) and space–query tradeoffs.
- **Distinct elements:** $\Omega(\varepsilon^{-2}+\log n)$ bits for relative-error $\varepsilon$ (Indyk–Woodruff; Kane–Nelson–Woodruff) — a tight info-theoretic floor.
- **Frequency/quantile summaries:** $\varepsilon$-approximate quantiles need $\Theta(\frac1\varepsilon \log(\varepsilon n))$ space (Greenwald–Khanna; the $\Omega$ side via comparison/communication arguments; later tightened).
- **Join-size estimation:** under the **AGM bound**, $|q|\le \prod_e |R_e|^{x_e}$ for any fractional edge cover $x$; degree/heavy-light synopses (e.g. degree sequences) provably capture worst-case join size, but *distributional* estimates face communication lower bounds (estimating $|R\bowtie S|$ requires $\Omega(\cdot)$ communication when relations are split across parties).

Formally, a synopsis of $B$ bits answering a family of $m$ "well-separated" queries to error $\varepsilon$ must satisfy $B \ge \Omega(\log N_\varepsilon(\mathcal Q))$ where $N_\varepsilon$ is an $\varepsilon$-packing number of the inducible cardinality vectors — an encoding/VC-type argument.

## 3. State of the Art (SOTA)
**Theory-SOTA:** matching upper/lower bounds exist for several isolated classes — distinct elements (tight up to $\log\log$), quantiles (Greenwald–Khanna and KLL sketch, the latter optimal $O(\frac1\varepsilon\log\log\frac1\delta)$), and frequency estimation (Count-Min/Count-Sketch with matching $\Omega(\varepsilon^{-1})$/$\Omega(\varepsilon^{-2})$ bounds). For **join cardinality**, worst-case-optimal-join (WCOJ) theory (Ngo–Porat–Ré–Rudra) and degree-based bounds give upper limits, and there are communication lower bounds for distributed join-size estimation.

**Systems-SOTA:** the practical synopsis zoo — equi-depth/max-diff histograms, wavelet synopses, AKMV/HLL sketches, learned density models — with empirical accuracy/space curves but rarely matching information-theoretic optimality for the *multi-dimensional joint* case.

## 4. Upper Bound
Per-class optimal synopses are known: **KLL** for quantiles ($O(\frac1\varepsilon\log\log\frac1\delta)$ words), **HLL** for distinct ($O(\varepsilon^{-2}\log\log n)$ bits), **Count-Sketch** for frequencies ($O(\varepsilon^{-2}\log n)$). For range counting in fixed dimension, linear-space structures answer in $O(\log n)$ time. For join cardinality, the AGM/WCOJ bound is the tight *worst-case* upper bound on $|q|$ itself, and synopses storing degree sequences achieve it.

## 5. Lower Bound
- **Distinct:** $\Omega(\varepsilon^{-2}+\log n)$ bits (Kane–Nelson–Woodruff).
- **Quantiles:** $\Omega(\frac1\varepsilon \log \frac1\varepsilon)$ for deterministic comparison-based; KLL nearly matches.
- **Multi-dimensional range / conjunctive selectivity:** cell-probe and communication lower bounds show that **no synopsis sub-polynomial in the domain can answer all conjunctive (multi-attribute) selectivity queries to constant factor** — the curse of dimensionality is provable, not merely empirical.
- **Joins:** estimating join size to within a constant factor from independently-summarized relations requires $\tilde\Omega(\sqrt n)$ communication in adversarial instances (correlation hidden across relations).

## 6. The Gap
**Partially solved.** For 1-D and single-statistic classes the gap is essentially **closed**. The open core is the **multi-dimensional joint / join-conditioned** regime: there is no tight characterization of the minimal synopsis size that guarantees error $\varepsilon$ for general conjunctive/join queries over correlated attributes. Upper bounds (learned models, multi-D sketches) and lower bounds (communication, cell-probe) leave a wide polynomial gap, and it is open whether *any* polynomially-sized synopsis can beat the AVI worst case for arbitrary correlation.

## 7. Current Research (as of June 2026)
- **Lower bounds for learned CE models:** translating communication/VC arguments into "no learned synopsis of size $B$ can be accurate on all workloads" statements *(frontier — verify)*.
- **Instance-optimal / workload-aware synopses:** minimizing size relative to a *given* query distribution rather than worst case (connecting to the data-driven-algorithms agenda).
- **Sketch lower bounds for joins** under the AGM/polymatroid framework, sharpening when degree sketches are and aren't sufficient.
- **Differential-privacy crossover:** private synopses share the same packing-number machinery; cross-pollination on tight space bounds.

## 8. Future Work
- A tight space–error characterization for multi-attribute conjunctive selectivity (close the dimensionality gap).
- Provable space lower bounds for *any* learned model class (not just classical sketches).
- Synopses that are provably workload-instance-optimal with online adaptation.
- Unified theory linking AGM/WCOJ worst-case bounds to *distributional* (average-case) join estimation error.

## 9. Key References
- **[Foundational]** P. Indyk, D. Woodruff. *Tight Lower Bounds for the Distinct Elements Problem.* FOCS, 2003. — [DOI](https://doi.org/10.1109/SFCS.2003.1238202)
- **[Foundational]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018. — [arXiv](https://arxiv.org/abs/1203.1952) · [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** D. Kane, J. Nelson, D. Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[Foundational]** M. Pătraşcu. *Lower Bounds for Data Structures (cell-probe).* PhD thesis / STOC-FOCS line, 2008–2011. — [arXiv: Unifying the Landscape of Cell-Probe Lower Bounds](https://arxiv.org/abs/1010.3783)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

A packing/encoding lower bound in miniature. Let the query class $\mathcal Q$ be point-cardinality queries over a domain of size $N=4$, and consider relations whose per-value counts lie in $\{0,1,\dots,7\}$ (3 bits each). Suppose we demand *exact* answers to all 4 point queries.

There are $8^4 = 2^{12}$ distinguishable cardinality vectors. Any synopsis answering all 4 queries exactly must map distinct vectors to distinct states (else two vectors collide and at least one query is wrong), so it needs $\ge \log_2 2^{12} = 12$ bits — exactly storing the 4 counts. No compression is possible against this adversarial class.

Now relax to additive error $\varepsilon\cdot 7$ per count: counts within one $\varepsilon$-bucket become indistinguishable, so the $\varepsilon$-packing number drops to $\big(\lceil 1/(2\varepsilon)\rceil\big)^4$, giving a floor of $B \ge 4\log_2\lceil 1/(2\varepsilon)\rceil$ bits. This is the encoding/packing argument $B \ge \Omega(\log N_\varepsilon(\mathcal Q))$ in section 2: accuracy $\varepsilon$ buys you space only logarithmically in the packing number, which is why distinct-elements bottoms out at $\Theta(\varepsilon^{-2}+\log n)$ and conjunctive multi-D queries stay provably expensive.

---
*Part of the [DBMS Research catalog](../../README.md).*
