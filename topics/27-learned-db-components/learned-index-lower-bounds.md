# Learned Index Lower Bounds

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-index-lower-bounds` · **Status:** partially-solved

## 1. Problem Statement
A **learned index** approximates the empirical CDF of a sorted key set $S$, $|S| = n$, with a model $F$, then does a bounded last-mile search to correct the prediction (Kraska et al., SIGMOD 2018). The central theoretical question: **how much can any learned index provably beat a comparison-based or implicit static index?** We want lower bounds — information-theoretic, cell-probe, or comparison-tree — that hold *no matter what model* is used, quantifying the irreducible cost of predecessor/membership queries even when the structure is allowed to "learn" the data distribution.

- **Decision variant:** does there exist an input distribution on which every learned index needs $\Omega(\log n)$ probes?
- **Optimization variant:** characterize the optimal query cost as a function of a distributional-complexity parameter (entropy, segment count, smoothness).
- **Counting/space-time variant:** for a space budget $m$ cells of $w$ bits, what is the minimum worst-case query time?

Status is *partially-solved*: classical predecessor lower bounds transfer cleanly, but matching bounds *parameterized by learnability* are only partial.

## 2. Mathematical Foundations
Let keys come from a universe $[U]$, stored in $m$ cells of $w$ bits. The **cell-probe model** (Yao) charges only memory probes; it subsumes comparison and word-RAM models, so any cell-probe lower bound binds learned indexes too. The **predecessor problem** has the tight Pătrașcu–Thorup tradeoff: with space $n \cdot 2^a$, query time is
$$\Theta\!\left(\min\left\{ \tfrac{\log_a w}{\,}, \; \log_w n, \; \tfrac{\log\frac{w}{a}}{\log\frac{a}{\log n}\cdot \log\frac{w}{a}} \right\}\right),$$
optimal up to the regimes they identify. A learned index is just a *static data structure for predecessor*, so this lower bound applies. The slack a learned index exploits is the **last-mile error** $\varepsilon = \max_x |F(x) - \mathrm{rank}(x)|$: search cost is $O(\log \varepsilon)$, and $\varepsilon$ depends on the **PLA/segment complexity** of the CDF. Information-theoretically, distinguishing $n$ ranks needs $\Omega(\log n)$ bits of resolution; for an adversarial CDF no constant-segment model achieves small $\varepsilon$, forcing $\varepsilon = \Theta(n)$.

## 3. State of the Art (SOTA)
- **Theory:** Pătrașcu–Thorup (FOCS 2006/2007) give the tight static predecessor cell-probe tradeoff — the canonical lower-bound vehicle. Ferragina–Lillo–Vinciguerra (*Why Are Learned Indexes So Effective?*, ICML 2020) prove that for keys drawn i.i.d. from a distribution with bounded "gaps," the PGM-index needs $O(n)$ space and $O(\log n)$ time but with a *constant* expected number of segments — explaining empirical wins.
- **Systems/empirical:** SOSD (Marcus et al., VLDB 2020) shows learned indexes beat B-trees on smooth data, lose on adversarial/discrete data — empirically consistent with the lower-bound picture.

## 4. Upper Bound
PGM-index achieves the minimum number of linear segments for fixed $\varepsilon$ with $O(\log n)$ worst-case query and recursive $O(\log_B n)$ I/O; under benign distributions, expected segment count is $O(1)$, so the model layer is $O(1)$ and total cost approaches $O(\log\log n)$ on the last mile for Lipschitz-gap inputs (Ferragina et al.). This is the best *parameterized* upper bound: cost $\propto$ approximation complexity of the CDF, never worse than $O(\log n)$.

## 5. Lower Bound
The adversary picks a CDF where any $s$-segment PLA has error $\varepsilon = \Omega(n/s)$, so with $o(n)$ model space the last-mile search costs $\Omega(\log n)$. In the cell-probe model, Pătrașcu–Thorup forbids beating $\Omega(\log_w n)$ for linear-space integer predecessor — a learned index cannot escape this for worst-case key sets. Communication-complexity reductions (lopsided set disjointness) underlie these bounds. What is **missing**: a lower bound stated *in terms of a learnability parameter* matching the PGM upper bound tightly across all distributional-complexity regimes.

## 6. The Gap
Partly closed for the worst case (predecessor bounds are tight and apply directly) and for benign distributions (PGM matches up to constants). The genuine gap is the **intermediate regime**: a clean parameter $\kappa$ measuring "learnability" with a two-sided bound $\Theta(f(\kappa))$ on query time. Closing it needs a lower bound that an adversary, *restricted to distributions of complexity $\kappa$*, can still force a matching cost.

## 7. Current Research (as of June 2026)
- Lower bounds parameterized by **CDF smoothness / segment entropy**, unifying PGM analysis with cell-probe machinery *(frontier — verify)*.
- Dynamic / update-aware lower bounds bridging to amortized learned-index maintenance *(frontier — verify)*.
- Groups: Ferragina–Vinciguerra (Pisa) on learned-structure theory; Kraska/DSAIL (MIT); cell-probe lineage (Pătrașcu's successors, Larsen at Aarhus).

## 8. Future Work
- Define a canonical learnability complexity measure and prove matching two-sided bounds.
- Extend to multidimensional and string keys where the CDF abstraction breaks.
- Lower bounds under updates and distribution shift.

## 9. Key References
- **[Foundational]** A. Yao. *Should Tables Be Sorted?* JACM, 1981.
- **[Foundational]** M. Pătrașcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC/FOCS, 2006–2007.
- **[SOTA]** P. Ferragina, F. Lillo, G. Vinciguerra. *Why Are Learned Indexes So Effective?* ICML, 2020.
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-Index.* VLDB, 2020.
- **[Survey]** R. Marcus, et al. *Benchmarking Learned Indexes (SOSD).* VLDB, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
