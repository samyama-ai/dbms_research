---
id: 27-learned-db-components/learned-index-updates
title: "Learned Indexes Under Updates"
topic: 27-learned-db-components
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Learned Indexes Under Updates

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-index-updates` · **Status:** open

## 1. Problem Statement
A learned index fits a model $F$ to the CDF of a *static* sorted key set and corrects predictions with a bounded last-mile search. Real workloads, however, insert, delete, and shift the key distribution. The open problem: **maintain a learned index's accuracy and lookup bound under arbitrary updates without periodic full retraining**, while keeping insert/delete and lookup costs competitive with a B-tree's $O(\log n)$.

- **Decision variant:** does a fully dynamic learned index exist with worst-case $O(\log n)$ lookup *and* $O(\log n)$ update that never degrades below a B-tree under adversarial update sequences?
- **Optimization variant:** minimize amortized update cost subject to a query-error bound $\varepsilon$ that must hold at all times.
- **Online/drift variant:** under distribution shift, bound the regret of model staleness versus an oracle that retrains every step.

Status is *open*: dynamic systems exist (ALEX, PGM, LIPP) but lack worst-case guarantees robust to adversarial inserts and drift.

## 2. Mathematical Foundations
The invariant to preserve is the **error bound** $\varepsilon = \max_x |F(x) - \mathrm{rank}(x)|$. An insertion shifts ranks of all larger keys by 1, so a single insert can in principle inflate $\varepsilon$ globally. Three structural strategies bound this:
- **Gapped / model-based arrays** (ALEX): leave free slots so inserts are local; lookup stays $O(\log \varepsilon)$ until a node overflows and is split/retrained. Amortized analysis resembles **gapped-array** and **packed-memory-array (PMA)** bounds, giving $O(\log^2 n)$ amortized inserts.
- **Logarithmic method / Bentley–Saxe** decomposition: maintain $O(\log n)$ static learned indexes of geometric sizes, merge on overflow — converts a static structure into a dynamic one with $O(\log n)$ amortized insert, $O(\log^2 n)$ query (PGM-dynamic uses this idea).
- **Distribution shift** is modeled as the CDF $F_t$ drifting; staleness cost relates to $\sup_x |F_t(x) - F_{t_0}(x)|$, an *online learning / regret* quantity.

## 3. State of the Art (SOTA)
- **Systems/empirical:** ALEX (Ding et al., SIGMOD 2020) — gapped arrays + adaptive model splits, strong on real read/write mixes. LIPP (Wu et al., VLDB 2021) — eliminates last-mile search via precise position via recursive in-place models. APEX (Lu et al., VLDB 2022) — persistent-memory updatable learned index. ALEX+/DILI continue the line.
- **Theory:** Dynamic PGM-index (Ferragina–Vinciguerra, VLDB 2020) — the only learned index with *provable worst-case* dynamic bounds, via Bentley–Saxe-style layering.

## 4. Upper Bound
Dynamic PGM: $O(\log n)$ worst-case query, $O(\log n)$ amortized insert/delete, $O(n)$ space, error bound $\varepsilon$ preserved — provable, model-class-restricted (piecewise-linear). ALEX/LIPP give better empirical constants (often near $O(\log\log n)$ effective) but only average-case guarantees under benign data; they can degrade under adversarial inserts that force frequent node splits and retraining.

## 5. Lower Bound
Any dynamic predecessor structure inherits the **Pătrașcu–Thorup / Pătrașcu–Demaine** dynamic cell-probe lower bound: $\Omega(\log n / \log\log n)$ per operation for the dynamic predecessor/membership problem in the cell-probe model with polylog word size. So no learned index can asymptotically beat this under adversarial updates — learned gains under updates are necessarily *distributional*, not worst-case. There is **no** matching lower bound proving that retraining-free maintenance is impossible under bounded drift; that side is open.

## 6. The Gap
Open. Theory gives worst-case-optimal-within-model-class (PGM) and a generic dynamic predecessor floor; systems give strong average-case structures with no robustness proof. The gap: a structure that **simultaneously** (a) matches the dynamic cell-probe floor in the worst case and (b) provably exploits benign/slowly-drifting distributions to do better, with a regret bound on staleness. No construction or impossibility currently spans both.

## 7. Current Research (as of June 2026)
- **Drift-aware** learned indexes with online model updates and regret guarantees against an always-retraining oracle *(frontier — verify)*.
- **Concurrency**: lock-free / latch-free updatable learned indexes for multicore and persistent memory *(frontier — verify)*.
- Hybrid fallback (B-tree on hot adversarial regions, model elsewhere) with worst-case safety nets.
- Groups: Kraska/DSAIL (MIT) and Microsoft Research (ALEX); Ferragina–Vinciguerra (Pisa); HKUST/CUHK (LIPP, APEX).

## 8. Future Work
- Prove amortized bounds for gapped-array learned indexes matching PMA lower bounds.
- Formal regret model for distribution shift with provable staleness/accuracy tradeoff.
- Multidimensional and string-key dynamic learned indexes.

## 9. Key References
- **[Foundational]** T. Kraska, et al. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** J. Ding, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/1905.08898)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-Index: A Fully-Dynamic Compressed Learned Index with Provable Worst-Case Bounds.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[SOTA]** J. Wu, et al. *Updatable Learned Index with Precise Positions (LIPP).* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2104.05520)
- **[Foundational]** M. Pătrașcu, E. Demaine. *Logarithmic Lower Bounds in the Cell-Probe Model.* SIAM J. Computing, 2006. — [arXiv](https://arxiv.org/abs/cs/0502041)
- **[Foundational]** J. L. Bentley, J. B. Saxe. *Decomposable Searching Problems I: Static-to-Dynamic Transformation.* J. Algorithms, 1980. — [DOI](https://doi.org/10.1016/0196-6774(80)90015-2)

## 10. Worked Example

**Gapped-array insert (ALEX-style), then a Bentley–Saxe merge.** A leaf node fits a linear model $F(x)=\lfloor (x-100)/10\rfloor$ to keys $\{100,110,120,130\}$, laid out in a gapped array of capacity 8 with slots: `[100, _, 110, _, 120, _, 130, _]`. Insert key $115$: $F(115)=1$ scaled to slot $\approx 3$; the slot is empty, so we place it locally — **no rank shift, no retrain**, lookup error stays $\varepsilon\le 1$. Now insert $112,114,116$ into the same gap region: the node overflows (density $> $ threshold), triggering a *split + refit* — the amortized cost charged here is the $O(\log^2 n)$ packed-memory-array bound.

**Why worst-case can't beat the floor.** An adversary inserts $1, \tfrac12, \tfrac14, \dots$ all into one tiny key range, forcing repeated splits. Dynamic PGM instead keeps $O(\log n)$ static layers of sizes $1,2,4,\dots$; inserting one key rebuilds layers up to the first empty one, geometric-series amortized to $O(\log n)$, and a query probes all $\log n$ layers: $O(\log^2 n)$. The Pătrașcu–Demaine floor $\Omega(\log n/\log\log n)$ per op means *no* learned structure escapes logarithmic cost on adversarial updates — gains are purely distributional.

---
*Part of the [DBMS Research catalog](../../README.md).*
