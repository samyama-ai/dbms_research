---
id: 26-cardinality-estimation/groupby-result-cardinality
title: "Group-By / Aggregation Result Cardinality"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Group-By / Aggregation Result Cardinality

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/groupby-result-cardinality` · **Status:** open

## 1. Problem Statement
Given a query `SELECT g_1,...,g_k, AGG(...) FROM R WHERE p GROUP BY g_1,...,g_k`, predict the number of *distinct groups* in the output — i.e. the number of distinct tuples in $\pi_{g_1,\dots,g_k}(\sigma_p(R))$. This is the **number of distinct values (NDV)** of a composite key over a *filtered* relation.

Three variants matter:
- **Counting variant:** compute the exact group count (a `COUNT(DISTINCT ...)` over a projected, filtered relation).
- **Estimation variant (the practical problem):** approximate the group count from synopses (histograms, sketches, samples) without touching the data.
- **Decision variant:** decide whether the group count exceeds a threshold $\tau$ (used in plan choice, e.g. hash vs. sort aggregation, memory sizing).

Difficulty arises from (a) **correlation among grouping keys** (NDV of a composite is between $\max_i d_i$ and $\prod_i d_i$, and the true value can sit anywhere in that range), and (b) **interaction with the filter** $p$, which selects an unknown, possibly non-uniform subset of groups.

## 2. Mathematical Foundations
Let $d_i = |\pi_{g_i}(R)|$ be the per-column NDV and $D = |\pi_{g_1,\dots,g_k}(R)|$ the composite NDV. Two classical bounds frame the problem:
$$ \max_i d_i \;\le\; D \;\le\; \min\Big(|R|,\ \textstyle\prod_i d_i\Big). $$
Under an **attribute-value independence (AVI)** assumption, optimizers estimate $D \approx \min(|R|, \prod_i d_i)$, which is badly wrong under correlation. A principled alternative is the **distinct-value entropy** view: $D$ relates to the joint distribution's support size, and predicting it from marginals is the **support-size estimation** problem.

For the filter interaction, given a sample of size $n$ from a population of $D$ groups, estimating the number of *unseen* groups is the classical **species/support-size estimation** problem. The Good–Turing estimator, the unseen estimator of Valiant–Valiant, and the Chao/jackknife estimators all bound the bias. A key hardness fact: from a sample of size $n$, the support size is only learnable up to a $\Theta(n/\log n)$ factor in the worst case (Valiant–Valiant), giving an information-theoretic floor on sample-based NDV estimation.

## 3. State of the Art (SOTA)
**Theory-SOTA:** sketch-based distinct counting — **HyperLogLog** (Flajolet et al., 2007) gives $D$ within relative error $\varepsilon$ using $O(\varepsilon^{-2}\log\log D)$ bits; mergeable, so groups can be counted per-partition. For *unseen* support from samples, the **Valiant–Valiant unseen estimator** (STOC 2011 / 2017) is sample-optimal up to constants.

**Systems-SOTA:** commercial optimizers combine per-column NDV (from HLL or sampling) with damping heuristics for composite keys. Multi-column statistics (SQL Server multi-column density, Postgres `CREATE STATISTICS (ndistinct)`) directly store composite $D$ for declared groups. Learned approaches (e.g. deep autoregressive density models such as **Naru/NeuroCard**, VLDB 2019–2020) model the joint distribution and can read off group counts, but train per-table and degrade out-of-distribution.

## 4. Upper Bound
For *exact* distinct counting with a full pass: $O(|R|)$ time, $O(D)$ space (hash table). For *approximate* counting in one pass: HyperLogLog achieves $(1\pm\varepsilon)$ relative error in $O(\varepsilon^{-2}\log\log D)$ bits — optimal up to the $\log\log$ factor (Kane–Nelson–Woodruff, PODS 2010, prove $\Omega(\varepsilon^{-2} + \log D)$). For sample-based prediction of group count under a filter, the unseen estimator achieves accuracy with $O(D/\log D)$ samples, matching the lower bound.

## 5. Lower Bound
- **Streaming/sketch:** any algorithm estimating distinct count to relative error $\varepsilon$ requires $\Omega(\varepsilon^{-2} + \log D)$ bits (Indyk–Woodruff; Kane–Nelson–Woodruff).
- **Sample-based:** estimating support size to a constant factor requires $\Omega(D/\log D)$ samples (Valiant–Valiant), so any synopsis built from a uniform sample inherits this floor for the unseen-groups-after-filter case.
- **Composite NDV from marginals:** without joint information the prediction is underdetermined across the full $[\max_i d_i,\ \prod_i d_i]$ range; no estimator using only marginals can beat worst-case multiplicative error $\Omega(\prod_i d_i / \max_i d_i)$.

## 6. The Gap
For *unconditioned* distinct counting the gap is essentially **closed** (sketches are space-optimal up to $\log\log$). The genuinely **open** problem is *correlated, filter-conditioned* group counting: predicting $D$ over $\sigma_p(R)$ from compact, query-independent synopses. No synopsis simultaneously (i) handles arbitrary filters $p$, (ii) captures key correlation, and (iii) stays sublinear in $D$ with provable error. Closing it requires either a synopsis that encodes enough of the joint distribution or a proof that the filter-conditioned problem is information-theoretically hard for any sub-$D$ structure.

## 7. Current Research (as of June 2026)
- **Learned joint-density models** for NDV-under-predicate, extending Naru/NeuroCard to read off conditional group counts; work on robustness and update cost is active *(frontier — verify)*.
- **Sketch composition under predicates** — predicate-aware HLL / KMV variants and "sketch-of-sketches" for sliced distinct counting.
- **Multi-column statistics auto-tuning**: which composite NDV stats to materialize (a knapsack over query workloads), connecting to the index-selection literature.
- Theoretical work tightening species-estimation bounds for *structured* (e.g. low-rank or sparse) joint distributions, where worst-case floors may be beaten.

## 8. Future Work
- A synopsis with provable error for $D$ over arbitrary conjunctive filters, sublinear in $D$.
- Bridging the species-estimation lower bound with practical workloads by exploiting distributional structure (Zipfian keys, functional dependencies).
- Confidence intervals on group-count estimates that propagate into robust plan selection (hash-aggregate memory, parallelism degree).
- Incremental maintenance of composite-NDV synopses under updates.

## 9. Key References
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166v1)
- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[SOTA]** G. Valiant, P. Valiant. *Estimating the Unseen: Improved Estimators for Entropy and Other Properties.* STOC 2011 / JACM 2017. — [STOC 2011 (DOI)](https://doi.org/10.1145/1993636.1993727) · [JACM (DOI)](https://doi.org/10.1145/3125643)
- **[SOTA]** D. Kane, J. Nelson, D. Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DBLP](https://dblp.org/rec/conf/pods/KaneNW10.html) · [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** Z. Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* PVLDB, 2019; *NeuroCard.* PVLDB, 2020. — [Naru (arXiv)](https://arxiv.org/abs/1905.04278) · [NeuroCard (arXiv)](https://arxiv.org/abs/2006.08109)
- **[Survey]** P. J. Haas, J. F. Naughton, S. Seshadri, L. Stokes. *Sampling-Based Estimation of the Number of Distinct Values of an Attribute.* VLDB, 1995. — [PDF](https://www.vldb.org/conf/1995/P311.PDF)

## 10. Worked Example

Relation $R$ has $|R| = 12$ rows over columns `(state, city)`:

| state | city |
|-------|------|
| CA | LA |
| CA | LA |
| CA | SF |
| CA | SF |
| NY | NYC |
| NY | NYC |
| NY | NYC |
| TX | DAL |
| TX | DAL |
| TX | HOU |
| TX | AUS |
| TX | AUS |

Per-column NDV: $d_{\text{state}} = 3$ (CA, NY, TX), $d_{\text{city}} = 6$. The composite-key bounds give
$$\max(3,6) = 6 \;\le\; D \;\le\; \min(12,\ 3\times 6) = 12.$$
The true composite NDV is $D = 6$ (the distinct `(state,city)` pairs), sitting at the **bottom** of the range because cities are functionally nested under states — strong correlation. The AVI estimate $\min(|R|,\prod_i d_i) = \min(12,18) = 12$ overestimates by $2\times$, which would push a planner toward a too-large hash-aggregate.

Now add a filter `WHERE state = 'TX'`: the surviving 5 rows have group set $\{(TX,DAL),(TX,HOU),(TX,AUS)\}$, so $D_{\sigma} = 3$. A uniform sample of size $n=2$ might draw two AUS rows and see only $1$ group — the unseen-groups problem; species estimators (Good–Turing) would then inflate the estimate to account for groups not yet sampled.

---
*Part of the [DBMS Research catalog](../../README.md).*
