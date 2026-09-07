---
id: 21-graph-databases/dynamic-analytics-maintenance
title: "Dynamic graph analytics with bounded recomputation"
topic: 21-graph-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Dynamic graph analytics with bounded recomputation

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/dynamic-analytics-maintenance` · **Status:** open

## 1. Problem Statement
A graph $G$ evolves under a stream of edge insertions and deletions. Maintain analytics results **incrementally** so each update costs far less than full recomputation, ideally polylogarithmic or proportional only to the "affected region." Target measures:

- **Centrality:** betweenness, closeness, PageRank, $k$-core / coreness.
- **Connectivity:** connected components, biconnectivity, spanning forest.
- **Decompositions:** $k$-core decomposition, $k$-truss, densest subgraph.

Variants: **fully dynamic** (insert+delete) vs. **incremental/decremental** only; **exact** vs. **$(1\pm\varepsilon)$-approximate**; worst-case vs. amortized update time; the **explicit-maintenance** version (keep the answer materialized) vs. **query** version (answer on demand). The problem is **open**: for several measures (betweenness, exact coreness under deletions) no algorithm with provably sublinear worst-case update time and matching lower bound is known.

## 2. Mathematical Foundations
The relevant complexity framework is **dynamic / online algorithms** with **conditional fine-grained lower bounds**:

- **OMv (Online Matrix–Vector) conjecture** (Henzinger, Krinninger, Nanongkai, Saranurak, STOC 2015): no algorithm maintains certain dynamic problems with both $O(n^{1-\delta})$ update and query time. It yields tight conditional bounds for dynamic reachability, shortest paths, and subgraph detection.
- **3SUM / APSP** conditional barriers for dynamic distance and triangle problems.
- Coreness obeys a **locality / bounded-shift** property: a single edge update changes any vertex's core number by at most 1, bounding the affected set but not its size.
- Approximate counting/centrality uses **sketches**, **random walks**, and **sampling** with concentration (Chernoff/Hoeffding); PageRank maintenance leverages the **push** operation's local support (Andersen–Chung–Lang).

## 3. State of the Art (SOTA)
**Connectivity:** fully dynamic connectivity in $O(\log^2 n)$ amortized (Holm–de Lichtenberg–Thorup 2001); worst-case $O(n^{o(1)})$ via expander decompositions / *deterministic dynamic connectivity* (Chuzhoy–Gao–Li–Nanongkai–Peng–Saranurak, FOCS 2020). MST and 2-edge-connectivity similarly polylog.

**$k$-core:** incremental/decremental coreness maintenance with bounded update sets (Sariyüce et al., "incremental k-core decomposition," VLDB 2013; Zhang et al. order-based, ICDE 2017); $k$-truss maintenance (Huang et al.).

**Centrality:** incremental betweenness (Green–McColl–Bader 2012; KADABRA / Bergamini–Meyerhenke approximate betweenness with absolute error guarantees); dynamic PageRank via local push and Monte-Carlo random walks (Bahmani–Chowdhury–Goel; Zhang et al.).

**Systems-SOTA:** Differential Dataflow / Timely, GraphBolt and KickStarter (Vora et al., incremental streaming analytics with dependency tracking), Tegra, and Aspen (Dhulipala et al., compressed dynamic graphs / C-trees).

## 4. Upper Bound
- Connectivity: $O(\log^2 n)$ amortized / $n^{o(1)}$ worst-case per update.
- $k$-core decomposition: $O(|\text{affected}|)$ per edge update; affected set provably bounded but $\Theta(n)$ in the worst case.
- PageRank ($\varepsilon$-approx): $\tilde O(1/\varepsilon^2)$ or $\tilde O(d/\varepsilon)$ work per update via local push / walk maintenance.
- Approximate betweenness: $\tilde O(\cdot)$ per batch with additive error via sampled shortest-path trees (KADABRA, Bergamini–Meyerhenke).

## 5. Lower Bound
- Under **OMv**, no fully dynamic algorithm maintains $s$-$t$ reachability, subgraph (triangle) detection, or shortest-path distance with both update and query time $O(n^{1-\delta})$ — implying that exact dynamic closeness/betweenness inherit the same $\Omega(n^{1-\delta})$ barrier.
- Dynamic densest-subgraph / exact coreness under deletions: OMv- and SETH-conditional polynomial barriers.
- Cell-probe lower bounds (Pătraşcu–Demaine) give $\Omega(\log n)$ per operation for dynamic connectivity, matched up to a log by HDT.

## 6. The Gap
For **connectivity** the gap is essentially closed (polylog amortized, $n^{o(1)}$ worst-case, $\Omega(\log n)$ cell-probe lower bound). The genuine openness is for **centrality and decompositions**: exact dynamic betweenness/closeness face OMv-conditional $\Omega(n^{1-\delta})$ barriers, yet whether *approximate* versions admit $\tilde O(1)$ worst-case (not just amortized/batched) updates is unresolved. For coreness, the affected-set bound does not translate to a worst-case sublinear guarantee — no matching lower bound rules out a better algorithm, leaving a real gap.

## 7. Current Research (as of June 2026)
Active groups: Saranurak/Nanongkai (expander-based dynamic algorithms), Dhulipala/Shun/Blelloch (parallel batch-dynamic, Aspen, ConnectIt), Meyerhenke (dynamic centrality), Vora/Gupta (KickStarter/GraphBolt). *(frontier — verify)* Strong recent activity in **parallel batch-dynamic** algorithms — processing update batches with low depth — for $k$-core, connectivity, and clustering. *(frontier — verify)* Interest in **dynamic GNN** embedding maintenance and in differentially-private dynamic analytics. Hardness side: extending OMv reductions to centrality and densest-subgraph.

## 8. Future Work
- Worst-case (not amortized) sublinear updates for approximate betweenness/closeness, or matching lower bounds.
- Tight bounds for fully dynamic exact $k$-core and densest subgraph.
- Batch-dynamic algorithms with provable work/depth optimality across decompositions.
- A unified incremental-view-maintenance framework covering analytics inside graph DBs.

## 9. Key References
- **[Foundational]** Holm, de Lichtenberg, Thorup. *Poly-logarithmic deterministic fully-dynamic algorithms for connectivity, MST, 2-edge and biconnectivity.* JACM, 2001. — [DOI](https://doi.org/10.1145/502090.502095)
- **[Foundational]** Henzinger, Krinninger, Nanongkai, Saranurak. *Unifying and strengthening hardness for dynamic problems via the online matrix-vector multiplication conjecture.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1511.06773)
- **[SOTA]** Chuzhoy, Gao, Li, Nanongkai, Peng, Saranurak. *A deterministic algorithm for balanced cut with applications to dynamic connectivity.* FOCS, 2020. — [arXiv](https://arxiv.org/abs/1910.08025)
- **[SOTA]** Sariyüce, Gedik, Jacques-Silva, Wu, Çatalyürek. *Streaming algorithms for k-core decomposition.* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2536336.2536344)
- **[SOTA]** Vora, Gupta, et al. *KickStarter: Fast and accurate computations on streaming graphs via trimmed approximations.* ASPLOS, 2017. — [DOI](https://doi.org/10.1145/3037697.3037748)
- **[SOTA]** Dhulipala, Blelloch, Shun. *Low-latency graph streaming using compressed purely-functional trees (Aspen).* PLDI, 2019. — [arXiv](https://arxiv.org/abs/1904.08380)
- **[Survey]** Bergamini, Meyerhenke. *Approximating betweenness centrality in fully dynamic networks.* Internet Mathematics, 2016. — [arXiv](https://arxiv.org/abs/1510.07971)

## 10. Worked Example

Illustrate the **bounded-shift** property of $k$-core under one edge insertion. Start with a path $1\!-\!2\!-\!3\!-\!4$ plus an extra edge $2\!-\!4$, so degrees are $\deg(1)=1,\deg(2)=3,\deg(3)=2,\deg(4)=2$. Coreness (max $k$ such that the vertex survives repeatedly peeling all vertices of degree $<k$):

- Peel $k=1$: remove vertex 1 (degree 1). Remaining $\{2,3,4\}$ form a triangle, each degree 2.
- So core numbers are $\text{core}(1)=1$, $\text{core}(2)=\text{core}(3)=\text{core}(4)=2$.

Now **insert edge $1\!-\!3$**. Vertex 1's degree rises to 2. The theorem (section 2) guarantees no core number changes by more than $1$. Indeed only the "affected subgraph" reachable from the endpoints is re-examined: vertex 1 can now survive the $k=1$ peel, and the new graph $\{1,2,3,4\}$ with edges $\{12,23,34,24,13\}$ has every vertex of degree $\ge 2$, so $\text{core}(1)$ shifts $1\to 2$; all others stay $2$.

The update touched only $O(|\text{affected}|)=O(1)$ vertices here — but in a star where the hub gains an edge, the affected set can cascade to $\Theta(n)$ vertices, which is exactly why a worst-case sublinear guarantee (section 6) remains open.

---
*Part of the [DBMS Research catalog](../../README.md).*
