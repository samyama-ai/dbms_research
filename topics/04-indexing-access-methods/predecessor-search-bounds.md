# Predecessor search optimality gaps

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/predecessor-search-bounds` · **Status:** partially-solved

## 1. Problem Statement
Given a set $S \subseteq \{0,\dots,2^w-1\}$ of $n$ $w$-bit keys, **predecessor search** answers $\text{pred}(x) = \max\{y \in S : y \le x\}$. It is the primitive underlying every ordered index: range scans, B-tree descents, IP routing, and successor queries all reduce to it. The question is the **cell-probe complexity**: how many memory cells of width $w$ must be probed, as a function of $n$, $w$, and the space $s$ (in cells)?

The problem: **determine the exact optimal query time for static and dynamic predecessor search across the full $(n, w, s)$ parameter space, closing the remaining gaps between known upper and lower bounds.**

- **Static decision/search variant:** preprocess $S$ into $s$ cells minimizing query probes.
- **Dynamic variant:** support `insert`/`delete` and `pred`, trading update vs. query time.
- **Approximate / colored variants:** approximate predecessor, predecessor among a subset.

*Partially solved:* the **static** complexity is essentially **resolved** (Pătraşcu–Thorup gave matching bounds for the natural regimes); **dynamic** lower bounds and some space/word-size corners retain gaps.

## 2. Mathematical Foundations
The model is the **cell-probe model** (Yao): memory is $s$ cells of $w$ bits; cost = number of cells probed; computation is free. Key landmarks:

- **van Emde Boas trees:** $O(\log w) = O(\log\log U)$ query in $O(U)$ or (with hashing, **y-fast tries**, Willard) $O(n)$ space.
- **Fusion trees** (Fredman–Willard): $O(\log_w n)$ query, beating comparison's $\log n$ for large $w$.
- **Optimal static bound (Pătraşcu–Thorup 2006/2007):** for space $s = n \cdot 2^a$, the optimal query time is
$$\Theta\!\left(\min\left\{ \log_w n,\ \frac{\log w}{\log\frac{\log w}{\log(s/n) \cdot 1/\log\log w}},\ \log\frac{\log w}{\log\frac{\log w \cdot \log(s/n)}{\log\log w}} \right\}\right)$$
i.e., a tight trichotomy combining the fusion-tree and vEB regimes, governed by space $s$ and word size $w$.
- **Communication-complexity / round-elimination** technique (Miltersen, Sen, Ajtai) underlies the lower bounds; **chronogram / information-transfer** methods (Pătraşcu–Demaine) drive dynamic bounds.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Pătraşcu–Thorup's bounds **tightly characterize static** predecessor for polynomial space and natural word sizes, unifying vEB, fusion trees, and the space-time tradeoff. For **dynamic**, Pătraşcu–Demaine (STOC 2004/2006) prove $\Omega(\log n / \log\log n)$-type tradeoffs via the information-transfer method, with matching upper bounds in several regimes.
- **Systems-SOTA:** practical indexes (B+-trees, ART, Masstree, learned indexes, succinct tries / **FST**) realize $O(\log_B n)$ external or near-vEB internal behavior; learned indexes exploit data distribution to beat worst-case constants empirically but do not change cell-probe worst case.

## 4. Upper Bound
The upper bounds matching the Pătraşcu–Thorup characterization are achieved by **combining fusion trees** ($O(\log_w n)$ for large $w$, near-linear space) and **vEB/y-fast tries** ($O(\log\log U)$, $O(n)$ space), selected by regime; explicit data structures realize each branch of the trichotomy. In the **cell-probe / word-RAM model** these are optimal for static search up to constants in the stated parameter ranges. Dynamic upper bounds achieve $O(\log n / \log\log n)$ query with comparable update in the relevant regime.

## 5. Lower Bound
The **cell-probe lower bounds** of Pătraşcu–Thorup match the static upper bounds (so static is closed in the natural regimes), proved via round elimination over the **asymmetric communication** game of predecessor search. For **dynamic** predecessor, the strongest lower bounds come from the **information-transfer / chronogram** method (Pătraşcu–Demaine), giving $\max(t_q, t_u) = \Omega(\log n / \log\log n)$ for cell width $w = \Theta(\log n)$ — but with residual gaps for **large word sizes** and **non-polynomial space**, and the precise dynamic trichotomy is not fully matched.

## 6. The Gap
Static predecessor is, for practical purposes, **closed** (matching $\Theta$ bounds). The genuinely open gaps are in the **dynamic** setting — exact query/update tradeoff for all $(w, s)$ corners — and in **succinct/space-restricted** regimes where $s = n(1+o(1))$ cells, where the interaction of compression and probe count is not tight. Closing these requires either stronger dynamic cell-probe lower bounds (extending information-transfer to large $w$) or new dynamic data structures matching them.

## 7. Current Research (as of June 2026)
- **Dynamic predecessor in succinct space** and **for learned/distribution-aware** settings, seeking instance-optimal probe counts *(frontier — verify)*.
- **Cell-probe lower-bound techniques** beyond round elimination (e.g., via data-structure / cell-sampling lower bounds) to close large-word dynamic gaps *(frontier — verify)*.
- Connections to **range-emptiness / approximate-membership** lower bounds and to learned-index worst-case analysis.
- Groups: Kasper Green Larsen (Aarhus), Huacheng Yu (Princeton), Omri Weinstein, the late Mihai Pătraşcu's lineage (MIT), Thorup (Copenhagen).

## 8. Future Work
- A complete tight trichotomy for **dynamic** predecessor across all $(n, w, s)$.
- Predecessor lower/upper bounds in the **succinct** ($n + o(n)$ words) regime.
- Reconciling **learned-index** average-case optimality with cell-probe worst case.

## 9. Key References
- **[Foundational]** P. van Emde Boas. *Preserving Order in a Forest in Less Than Logarithmic Time.* FOCS, 1975.
- **[Foundational]** M. Fredman, D. Willard. *Surpassing the Information-Theoretic Bound with Fusion Trees.* JCSS, 1993.
- **[SOTA]** M. Pătraşcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC, 2006.
- **[SOTA]** M. Pătraşcu, E. Demaine. *Logarithmic Lower Bounds in the Cell-Probe Model.* SIAM J. Computing, 2006.
- **[Foundational]** A. Yao. *Should Tables Be Sorted?* JACM, 1981.
- **[Survey]** K. G. Larsen. *Cell-Probe Lower Bounds for Data Structures* (survey / thesis material), 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
