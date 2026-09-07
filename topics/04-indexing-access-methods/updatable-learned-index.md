---
id: 04-indexing-access-methods/updatable-learned-index
title: "Updatable learned indexes under writes"
topic: 04-indexing-access-methods
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Updatable learned indexes under writes

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/updatable-learned-index` · **Status:** empirically-open

## 1. Problem Statement
Static learned indexes assume a fixed sorted array; inserts and deletes break the learned key→position mapping, since a model fit to one CDF becomes stale as the distribution shifts. The problem: **support high-throughput inserts/deletes while keeping (a) lookup cost bounded and (b) model error $\varepsilon$ bounded**, without periodic full rebuilds that stall the system.

Formally: maintain $F$ approximating the running empirical CDF so that prediction error stays $\le \varepsilon$ and amortized update cost stays low, with worst-case lookup $O(\log n)$ never violated. Variants:

- **Optimization variant:** minimize amortized update + expected lookup cost subject to a space budget.
- **Decision variant:** can bounded $\varepsilon$ and $O(\log n)$ lookup be maintained under arbitrary update sequences without $\Omega(n)$ rebuilds?

Status *empirically-open*: several systems (ALEX, PGM, LIPP, learned LSM) handle updates well in practice, but **provable** bounds tying update throughput to maintained accuracy under adversarial/skewed write streams are missing.

## 2. Mathematical Foundations
Updates perturb the rank function: inserting key $k$ shifts $\text{rank}(x)$ by $+1$ for all $x > k$, degrading any fixed model. Strategies and their analyses:

- **Gapped/model-based arrays (ALEX):** maintain slack (gaps) so inserts are local; expected $O(\log n)$ with model-based insertion under smoothness assumptions, but worst case degrades with skew.
- **PGM dynamic:** logarithmic-method / **buffered** approach — maintain $O(\log n)$ static PGM indexes of geometrically growing size, merging on overflow, giving amortized $O(\log^2 n)$-style update and $O(\log n)$ query with **worst-case** guarantees (Ferragina–Vinciguerra).
- **LIPP:** precise position via recursive in-place models, eliminating last-mile search but with structural cost under adversarial inserts.

Core tension: the **logarithmic method** (Bentley–Saxe) gives worst-case bounds but adds a $\log$ factor; gap-based methods give better constants but rely on distributional assumptions.

## 3. State of the Art (SOTA)
- **Theory:** Dynamic PGM (worst-case bounds via Bentley–Saxe over learned segments).
- **Systems/empirical:** **ALEX** (SIGMOD 2020, gapped arrays + adaptive RMI), **LIPP** (VLDB 2021, no last-mile search), **APEX** (persistent-memory learned index), **XIndex/FINEdex** (concurrent updatable), and learned components inside LSM engines (**Bourbon**, **Google Bigtable** learned-block lookups). GRE benchmark (VLDB 2022) evaluates updatable learned indexes head-to-head.

## 4. Upper Bound
Dynamic PGM: amortized update $O(\log n + \log^2 n / B)$-style with query $O(\log n)$, space $O(n)$, **worst-case** (model-class) bounds via merging static indexes. ALEX/LIPP achieve near-$O(\log n)$ lookups and high insert throughput **empirically** but with bounds contingent on distribution smoothness/gap density rather than fully worst-case.

## 5. Lower Bound
Dynamic predecessor lower bounds (Pătrașcu–Demaine, cell-probe) impose $t_q \cdot t_u = \Omega(\log n / \log w)$-type tradeoffs that **no learned index can escape** for general integer keys — learning the distribution does not beat the cell-probe barrier on adversarial updates. No lower bound specifically targets the *accuracy-under-writes* objective; the impossibility of "free" updates follows from the rank-shift argument plus these dynamic bounds.

## 6. The Gap
Open. Practical systems exceed B-trees on real write workloads, but there is **no theorem** bounding maintained error $\varepsilon$ as a function of update throughput and skew without resorting to the generic logarithmic-method overhead. The gap: distribution-dependent empirical wins vs. distribution-robust provable guarantees. Closing it needs either (i) an adversarial update model with matching upper/lower bounds, or (ii) proof that gap-based methods retain bounds under bounded distribution drift.

## 7. Current Research (as of June 2026)
- **Concurrent + updatable** learned indexes scaling to many cores (FINEdex, XIndex lineage); contention-aware model maintenance *(frontier — verify)*.
- **Drift-aware** retraining triggered by measured error, with bounded re-fit cost *(frontier — verify)*.
- Learned indexes on **persistent memory / NVMe** and inside LSM compaction (Bourbon lineage).
- Groups: MIT DSAIL, Pisa (Ferragina/Vinciguerra), CUHK/HKUST (LIPP, GRE), Microsoft Research.

## 8. Future Work
- Formal accuracy-vs-throughput tradeoff under adversarial and drifting writes.
- Self-tuning gap allocation with provable worst-case fallback.
- Range/string-key and multi-dimensional updatable learned indexes with guarantees.

## 9. Key References
- **[Foundational]** T. Kraska, et al. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** J. Ding, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389711)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-Index (fully-dynamic, provable worst-case bounds).* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[SOTA]** J. Wu, et al. *LIPP: Updatable Learned Index with Precise Positions.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3457390.3457393)
- **[SOTA]** C. Wongkham, et al. *GRE: Are Updatable Learned Indexes Ready? (benchmark).* VLDB, 2022. — [DOI](https://doi.org/10.14778/3551793.3551848)
- **[SOTA]** Y. Dai, et al. *Bourbon: From WiscKey to Bourbon — Learned Index for Log-Structured Merge Trees.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/dai)

## 10. Worked Example

Suppose keys $1,2,\dots,10{,}000$ are sorted, and a learned index fits the linear model $\hat{p}(k)=k-1$ (key $k$ at position $k-1$), with measured max error $\varepsilon=0$: a lookup jumps directly, no last-mile search.

Now insert key $5000.5$ (a float between $5000$ and $5001$). Its true position is $5000$, but the rank of every key $>5000.5$ shifts by $+1$. The model now under-predicts those positions by $1$, so $\varepsilon$ jumps from $0$ to $1$. After $m$ such inserts spread across the array, worst-case error grows to $\varepsilon=\Theta(m)$, and a lookup must binary-search a window of size $\Theta(m)$ — cost $\Theta(\log m)$ on top of the model.

Dynamic PGM avoids this via Bentley–Saxe: keep $O(\log n)$ static models of sizes $2^0,2^1,\dots$; an insert costs $O(\log n)$ amortized to rebuild merged levels, and a query probes all $O(\log n)$ models, total $O(\log^2 n)$. With $n=10^4$, that is $\approx 14^2\approx 196$ comparisons worst-case — bounded, unlike the unbounded gapped-array drift, which is the empirical-vs-provable tension this problem highlights.

---
*Part of the [DBMS Research catalog](../../README.md).*
