# Optimal join ordering complexity for general query graphs

> **Topic:** Query Optimization · **ID:** `02-query-optimization/join-ordering-complexity` · **Status:** open

## 1. Problem Statement

Given $n$ relations and a **query graph** $G=(V,E)$ whose edges are equi-join predicates, plus a
**cost function** $C$ that scores a join tree, find a join tree of minimum total cost. Variants:

- **Decision:** Is there a join tree of cost $\le k$?
- **Optimization:** Return the minimum-cost tree.
- **Counting:** How many distinct optimal trees exist?

The space of trees may be restricted to **left-deep**, **zig-zag**, or unrestricted **bushy**
shapes, and may **forbid** or **admit cross products**. The open question is to settle, for each
combination of (graph class $\times$ cost class $\times$ tree shape), whether optimal ordering is in
P or NP-hard, and where the exact boundary lies. Trees / chains / stars are known easy in special
cases; general cyclic graphs with realistic cost functions are the frontier.

## 2. Mathematical Foundations

A join tree is a full binary tree whose leaves are the $n$ relations. The classic **$C_{out}$**
cost sums intermediate-result cardinalities: $C_{out}(T)=\sum_{v \in \text{inner}(T)} |v|$, with
$|R \bowtie S| = |R|\,|S|\,\prod f$ over selectivities $f$ on the joining predicates. Cost functions
of interest include $C_{out}$, $C_{nlj}$ (nested-loop), $C_{hj}$ (hash), $C_{smj}$ (sort-merge), and
the abstract class **ASI** (Adjacent Sequence Interchange) cost functions admitting a rank function
$\mathrm{rank}(S)=\frac{T(S)-1}{C(S)}$.

Key structural results: for ASI cost and a query **tree** restricted to left-deep plans without
cross products, the **IKKBZ** algorithm computes the optimum in $O(n^2)$. The AGM bound
$|Q| \le \prod_e |R_e|^{x_e}$ (fractional edge cover LP) bounds output size and underlies
worst-case reasoning but does not by itself yield orderings.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Ibaraki–Kameda (1984) and Krishnamurthy–Boral–Zaniolo (IKKBZ, 1986) give
  polynomial optimal left-deep ordering for acyclic queries under ASI cost. Cluet & Moerkotte (1995)
  proved join ordering with cross products NP-hard; Scheufele & Moerkotte established hardness for
  bushy trees with general cost. DPccp (Moerkotte–Neumann, VLDB 2006) is the SOTA **exact** bushy
  enumerator, optimal in the number of connected-subgraph/complement pairs.
- **Systems-SOTA:** PostgreSQL, DuckDB, and commercial optimizers use DPccp/DPhyp for small $n$ and
  switch to greedy / genetic / randomized search (e.g. `GEQO`) beyond a threshold.

## 4. Upper Bound

- Acyclic query, left-deep, ASI cost, no cross products: **$O(n^2)$** optimal (IKKBZ), RAM model.
- General bushy, arbitrary cost: exact DP runs in $O(3^n)$ time / $O(2^n)$ space; **DPhyp**
  (Moerkotte–Neumann 2008) achieves time linear in the number of csg-cmp-pairs, which is
  near-optimal for the *enumeration* problem but still exponential in $n$ for dense graphs.

## 5. Lower Bound

- Join ordering admitting cross products is **NP-hard** (Cluet–Moerkotte 1995), reduction from a
  scheduling/ASI argument.
- Bushy join ordering for clique/cyclic query graphs under $C_{out}$ is **NP-hard**
  (Moerkotte). No sub-exponential exact algorithm is known; whether one exists is tied to
  fine-grained conjectures, but **no tight SETH-conditional lower bound** is established for the
  general bushy case — this is part of what is open.

## 6. The Gap

The boundary is mapped at the extremes (easy: acyclic + left-deep + ASI; hard: cyclic + cross
products) but the **interior is open**: e.g. acyclic graphs with *bushy* trees under realistic
hash-join cost, or bounded-treewidth graphs. Closing the gap means either a polynomial algorithm
parameterized by treewidth/cost-class, or a fine-grained (SETH/$3$SUM) lower bound matching the
$2^{O(n)}$ DP.

## 7. Current Research (as of June 2026)

- Parameterized complexity by query-graph treewidth and by "join-graph" sparsity (Marx-style
  structural results applied to ordering). *(frontier — verify)*
- Learned and reinforcement-learning enumerators (Bao, Balsa, LEON) that sidestep worst-case
  hardness empirically; Neumann/Moerkotte (TUM) continue exact-enumeration refinements.
- Connections to worst-case-optimal joins and the AGM/polymatroid bound for cost lower-bounding.

## 8. Future Work

- A complete complexity dichotomy over (graph class, cost class, tree shape).
- Tight fine-grained lower bounds for bushy enumeration.
- Approximation algorithms with provable ratios for $C_{out}$ on general graphs.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Krishnamurthy, Boral, Zaniolo. *Optimization of Nonrecursive Queries (IKKBZ).* VLDB, 1986.
- **[Foundational]** Cluet, Moerkotte. *On the Complexity of Generating Optimal Left-Deep Processing Trees with Cross Products.* ICDT, 1995.
- **[SOTA]** Moerkotte, Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm for the Generation of Optimal Bushy Join Trees without Cross Products (DPccp).* VLDB, 2006.
- **[SOTA]** Moerkotte, Neumann. *Dynamic Programming Strikes Back (DPhyp).* SIGMOD, 2008.
- **[Survey]** Moerkotte. *Building Query Compilers.* (lecture notes / draft book), ongoing.

---
*Part of the [DBMS Research catalog](../../README.md).*
