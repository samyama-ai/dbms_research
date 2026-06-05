# Optimal dynamic-programming join enumeration scaling

> **Topic:** Query Optimization · **ID:** `02-query-optimization/dp-enumeration-scaling` · **Status:** partially-solved

## 1. Problem Statement

Cost-based optimizers find an optimal join order by **dynamic programming over connected subgraphs** (DPccp): build optimal plans for larger relation sets from optimal plans for smaller ones. The challenge is that the number of subproblems is exponential in the number of relations $n$, so exact DP becomes infeasible at moderate $n$. The problem: **how far can exact (optimality-preserving) DP join enumeration be pushed in time and space, and what is the true complexity as a function of query-graph structure?**

- **Optimization variant:** Given a query graph $G$, a cost function with the *principle of optimality* (subplan independence), and a space of allowed plan shapes (left-deep, zig-zag, bushy; with/without cross products), compute a minimum-cost plan.
- **Counting variant:** Count the **csg-cmp-pairs** — connected-subgraph/complement pairs — which exactly equals the number of DP join-pair evaluations and thus the lower bound on enumeration work for any DP that considers all bushy plans.
- **Enumeration variant:** Enumerate connected subgraphs (and their valid complements) in an order respecting DP dependencies, with $O(1)$ amortized work per emitted item.

"Solving" means matching the algorithm's running time to the *intrinsic* number of subproblems for the given graph, not to the worst case.

## 2. Mathematical Foundations

A query graph is $G=(V,E)$, $|V|=n$. A **connected subgraph (csg)** is $S\subseteq V$ inducing a connected subgraph; a **csg-cmp-pair** is $(S_1,S_2)$ with both connected, disjoint, and joined by an edge. The seminal result (Moerkotte & Neumann, VLDB 2006) is that DPccp performs exactly
$$\#\text{ccp}(G)=\sum_{(S_1,S_2)} 1$$
join evaluations, and this count is **graph-shape dependent**: for a **chain** it is $\Theta(n^3)$, for a **cycle** $\Theta(n^3)$, for a **star** $\Theta(n\,2^n)$, for a **clique** $\Theta(3^n)$. Thus there is no single complexity — the right measure is $\#\text{ccp}(G)$ itself. The DP recurrence
$$\mathrm{best}[S]=\min_{(S_1,S_2):\,S_1\cup S_2=S}\mathrm{cost}\big(\mathrm{best}[S_1]\bowtie\mathrm{best}[S_2]\big)$$
requires the cost function to satisfy the optimality principle (no cross-plan interaction) — violated by features like sort-order/interesting-orders, which expand the state with physical properties.

## 3. State of the Art (SOTA)

- **Theory/algorithm SOTA:** *DPccp* (Moerkotte–Neumann, VLDB 2006) generates exactly the csg-cmp-pairs with no wasted enumeration, optimal up to a constant per pair. *DPhyp* (Moerkotte–Neumann, VLDB 2008) generalizes this to **hypergraphs**, handling non-inner joins and complex predicates while preserving the "no redundant pairs" property.
- **Systems SOTA:** HyPer / Umbra (Neumann, TUM) use DPhyp with an **adaptive optimizer** that switches from exact DP to *Iterative DP* / greedy / *Linearized DP* heuristics past a relation-count threshold; Microsoft SQL Server, PostgreSQL's GEQO, and DuckDB use similar thresholds. Graph-aware parallel/GPU DP and *worst-case-optimal* multiway operators are integrated in research systems.

## 4. Upper Bound

In the RAM model, DPccp/DPhyp run in $O(\#\text{ccp}(G))$ join-pair evaluations plus enumeration overhead, with space $O(2^n)$ for the memo (one entry per relevant subset). For dense/clique graphs this is $\Theta(3^n)$ time and $\Theta(2^n)$ space — the cost of the recurrence summed over all subset splits $\sum_S 2^{|S|}=3^n$. For sparse graph families (chains, trees, bounded treewidth), $\#\text{ccp}$ is polynomial, so DP is polynomial. Memory is the binding constraint in practice; $2^n$ memo entries become prohibitive around $n\approx 20$–$25$.

## 5. Lower Bound

Any DP that explores all bushy plans must evaluate every csg-cmp-pair, so $\#\text{ccp}(G)$ is an **unconditional lower bound for the bushy-DP model**; DPccp is therefore optimal *within that model*. Beyond DP, optimal join ordering for general graphs with cross products is **NP-hard** (Ibaraki–Kameda 1984 for tree queries with a specific cost class; Cluet–Moerkotte 1995 for cross products), so no polynomial exact algorithm exists in the general case unless P=NP. Under SETH, no $2^{o(n)}$ exact algorithm is expected for the clique case. Cardinality-based cost functions make even left-deep optimal ordering NP-hard.

## 6. The Gap

For the bushy-DP model the bounds are **matched** — DPccp/DPhyp hit the $\#\text{ccp}$ lower bound exactly; this part is *closed*. The genuinely open part is **whether a smaller exact algorithm exists for structured-but-dense graphs**: e.g., is there an exact join-ordering algorithm running in $c^n$ with $c<3$ for cliques, or parameterized algorithms in $f(\text{treewidth})\cdot\mathrm{poly}(n)$ that beat naive DP across all shapes? The space side is also open: can optimality be preserved with $\mathrm{poly}(n)\cdot 2^{o(n)}$ memory? Practical scaling to "dozens of relations" currently relies on heuristics that *abandon* optimality, so the gap is between provable optimality and the $n$ achievable in interactive time.

## 7. Current Research (as of June 2026)

- **Parameterized / treewidth-aware DP** to make the dense-graph cases tractable when the query graph has bounded width (Neumann/TUM; theory side connecting to submodular width). *(frontier — verify)*
- **Hybrid exact-then-heuristic** switching with provable optimality gaps (adaptive optimization in Umbra; *Linearized DP*, *IDP$_2$* lineage of Kossmann–Stocker).
- **Vectorized / parallel / GPU enumeration** of csg-cmp-pairs and lock-free memo tables to lower the constant factor. *(frontier — verify)*
- Integrating **worst-case-optimal multiway joins** into the DP cost space so the enumerator chooses between binary and multiway sub-plans (see *wcoj-vs-binary-plans*).

## 8. Future Work

- An exact join-ordering algorithm beating $3^n$ for cliques, or a fine-grained lower bound ruling it out.
- Polynomial-space exact DP, or rigorous space/time tradeoff curves.
- Closing the optimality gap of the heuristics used past the DP threshold with approximation guarantees.
- DP whose state cleanly incorporates physical properties (orders, partitioning) without exponential blowup of the memo.

## 9. Key References

- **[Foundational]** Moerkotte, Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm for the Generation of Optimal Bushy Join Trees without Cross Products.* VLDB, 2006. — [DBLP](https://dblp.org/rec/conf/vldb/MoerkotteN06.html)
- **[SOTA]** Moerkotte, Neumann. *Dynamic Programming Strikes Back.* SIGMOD, 2008. (DPhyp) — [DOI](https://doi.org/10.1145/1376616.1376672)
- **[Foundational]** Ibaraki, Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1270.1498)
- **[Foundational]** Cluet, Moerkotte. *On the Complexity of Generating Optimal Left-Deep Processing Trees with Cross Products.* ICDT, 1995. — [DOI](https://doi.org/10.1007/3-540-58907-4_6)
- **[Survey]** Moerkotte. *Building Query Compilers.* (manuscript / lecture notes), ongoing. — [PDF](https://pi3.informatik.uni-mannheim.de/~moer/querycompiler.pdf)
- **[SOTA]** Neumann, Radke. *Adaptive Optimization of Very Large Join Queries.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3183733)

## 10. Worked Example

Take a **chain** query $R_1 - R_2 - R_3 - R_4$ ($n=4$, edges $\{12,23,34\}$). The number of csg-cmp-pairs DPccp generates is $\binom{n+1}{3}=\binom{5}{3}=10$ (counting unordered $(S_1,S_2)$ splits), matching the $\Theta(n^3)$ chain formula. By contrast a **clique** on the same 4 relations forces the full $3^n$ recurrence: $\sum_{S}(2^{|S|}-2)/2$ over all $2^4$ subsets gives $\tfrac{3^4-2^{4+1}+1}{2}=\tfrac{81-32+1}{2}=25$ pairs.

Concretely the memo fills bottom-up: singletons $\{1\},\{2\},\{3\},\{4\}$; then connected pairs $\{12\},\{23\},\{34\}$ (note $\{13\},\{14\},\{24\}$ are *skipped* for the chain — disconnected); then $\{123\},\{234\}$; finally $\{1234\}$, whose best plan is chosen by comparing the splits $\{1\}|\{234\}$, $\{12\}|\{34\}$, $\{123\}|\{4\}$. So $10$ chain pairs vs. $25$ clique pairs on identical relations — the enumeration cost is purely a function of graph shape, not $n$ alone.

---
*Part of the [DBMS Research catalog](../../README.md).*
