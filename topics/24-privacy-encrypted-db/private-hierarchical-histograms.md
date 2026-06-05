# Truthful Private Histograms over Hierarchies

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/private-hierarchical-histograms` · **Status:** partially-solved

## 1. Problem Statement

Many analytics workloads are **hierarchical range-count queries**: counts at the leaf level (e.g., per-ZIP), roll-ups (per-state, per-nation), and arbitrary 1-D/multi-D range sums (the census "geographic hierarchy"). We must release **consistent** (a.k.a. *truthful*) DP answers: the noisy answers must satisfy the hierarchy's additivity (parent = sum of children), be non-negative, and ideally integral, **while minimizing error** over the whole workload of $O(n)$ range/hierarchy queries under pure $(\varepsilon,0)$ or approximate $(\varepsilon,\delta)$ DP.

Variants:
- **Optimization:** minimize worst-case / average squared error over all hierarchy nodes (and all dyadic ranges).
- **Consistency/post-processing (constraint-satisfaction):** project noisy answers onto the consistency polytope (non-negativity + additivity) with minimal distortion.
- **Counting:** answer all $k$ range queries; how does error scale with $k$, $n$, domain dimension $d$?

## 2. Mathematical Foundations

A 1-D range query over domain $[n]$ is a linear query. Naively perturbing each of the $n$ leaves gives $O(n)$ error for a range sum. The **Hierarchical / tree mechanism** (Hay–Rastogi–Miklau–Suciu 2010; Chan–Shi–Song "binary counting" 2011; Dwork–Naor–Pitassi–Rothblum continual observation) builds a $b$-ary tree of partial sums, noises each node, and answers any range with $O(\log_b n)$ nodes, giving error $O((\log n)^{1.5}/\varepsilon)$ per range — exponentially better than flat. **Consistency** is enforced by least-squares projection onto the additive subtree constraints (closed-form via two-pass weighting, Hay et al.) and onto non-negativity (NNLS). The **Matrix Mechanism** view: the workload is a matrix $W$, a *strategy* $A$ is measured under DP, and $W A^{+}$ reconstructs; optimal $A$ minimizes $\|W A^{+}\|$-type error. Lower bounds come from **discrepancy theory**: the error of any DP mechanism on a workload $W$ is $\Theta(\mathrm{disc}(W)/\varepsilon)$ for $\delta>0$ (Muthukrishnan–Nikolov; Nikolov–Talwar–Zhang), and from **VC/fat-shattering** dimension of range spaces.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** For all 1-D dyadic ranges, the optimal hierarchical/binary-tree mechanism is near-optimal; the **factorization / matrix mechanism** (HDMM, McKenna et al. 2018) and **dense/correlated strategies** achieve workload-optimal error up to small constants for 1-D and low-D. For continual release, the **binary mechanism** and its **constant-factor-optimal** refinements (Henzinger–Upadhyay–Upadhyay, SODA 2023) are state of the art.
- **Systems-SOTA:** The **U.S. Census TopDown Algorithm** (Abowd et al., 2020/2022) is the flagship deployment: hierarchical geographic measurement + non-negative integer consistency via constrained optimization, used for the 2020 Census.

## 4. Upper Bound

For 1-D range/hierarchy workloads, the tree mechanism gives per-query error $O((\log n)^{1.5}/\varepsilon)$ for pure DP and $O(\log n \cdot \sqrt{\log(1/\delta)}/\varepsilon)$ for approximate DP, with **consistency obtained for free** by least-squares post-processing (post-processing preserves DP). Matrix/factorization mechanisms reach the **discrepancy-optimal** constant for the all-ranges workload. Henzinger et al. give a continual-counting mechanism within a $(1+o(1))$ factor of optimal. TopDown scales this to multi-attribute census hierarchies in practice.

## 5. Lower Bound

Any DP mechanism answering all 1-D range queries has worst-case error $\Omega(\log n /\varepsilon)$ (for $\delta>0$) and $\Omega((\log n)/\varepsilon)$-type bounds from **discrepancy** of the range matrix (Nikolov–Talwar–Zhang, STOC 2013) — matching the upper bound up to $\sqrt{\log n}$ factors for pure DP, and up to constants for approximate DP. Hence the per-query gap is essentially $O(\sqrt{\log n})$ between pure and approximate regimes. For **2-D and higher** range queries, lower bounds grow as $\Theta((\log n)^{d}/\varepsilon)$ (discrepancy of $d$-dim ranges), and matching upper bounds in high $d$ are not fully resolved.

## 6. The Gap

In **1-D**, the problem is **largely closed**: matched discrepancy upper/lower bounds give constant-factor-optimal mechanisms, and consistency is free — hence "partially-solved." The remaining gaps: (i) the $\sqrt{\log n}$ pure-vs-approximate gap for all-ranges; (ii) **multi-dimensional** hierarchies, where optimal constants and the right dependence on $d$ are open; (iii) **non-negativity + integrality** consistency provably preserving near-optimal error (TopDown's constrained projection lacks tight utility guarantees). Closing (ii)/(iii) is the active frontier.

## 7. Current Research (as of June 2026)

- Near-optimal *factorization mechanisms* for multi-dimensional and continual-release hierarchies; matrix-factorization for DP-SGD reuses the same machinery *(frontier — verify)*.
- Provable-utility consistency under non-negativity/integrality for census-style releases beyond heuristic NNLS *(frontier — verify)*.
- Banded/streaming factorizations (Henzinger, Kairouz, McMahan et al.) lowering constants for hierarchical continual counting *(frontier — verify)*.

## 8. Future Work

- Tight optimal constants for $d$-dimensional range/hierarchy workloads.
- Consistency (additivity + non-negativity + integrality) with provable error preservation.
- Adaptive hierarchies (data-dependent tree shapes) with DP-optimal partitioning.
- Marrying hierarchical histograms with DP synthetic data over multi-relation schemas.

## 9. Key References

- **[Foundational]** Hay, Rastogi, Miklau, Suciu. *Boosting the Accuracy of Differentially Private Histograms Through Consistency.* VLDB, 2010.
- **[Foundational]** Dwork, Naor, Pitassi, Rothblum. *Differential Privacy Under Continual Observation.* STOC, 2010.
- **[Foundational]** Chan, Shi, Song. *Private and Continual Release of Statistics.* ICALP, 2010 / ACM TISSEC, 2011 (binary mechanism).
- **[SOTA]** Nikolov, Talwar, Zhang. *The Geometry of Differential Privacy: The Sparse and Approximate Cases.* STOC, 2013.
- **[SOTA]** McKenna, Miklau, Hay, Machanavajjhala. *Optimizing Error of High-Dimensional Statistical Queries (HDMM).* VLDB, 2018.
- **[SOTA]** Henzinger, Upadhyay, Upadhyay. *Almost Tight Error Bounds for Differentially Private Continual Counting.* SODA, 2023.
- **[Survey]** Abowd et al. *The 2020 Census Disclosure Avoidance System TopDown Algorithm.* Harvard Data Science Review, 2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
