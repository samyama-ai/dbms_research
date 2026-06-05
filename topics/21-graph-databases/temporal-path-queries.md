# Temporal and time-respecting path queries

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/temporal-path-queries` · **Status:** open

## 1. Problem Statement
A *temporal graph* assigns time labels to edges; an interaction $(u,v,t,\lambda)$ means $u$ can influence $v$ departing at time $t$ and arriving at $t+\lambda$. A **time-respecting (temporal) path** is a sequence of edges with non-decreasing (or strictly increasing) timestamps. The core problems:

- **Temporal reachability / single-source:** does a time-respecting path from $s$ to $v$ exist within a query window $[t_0,t_1]$? Compute earliest-arrival, latest-departure, fastest, and shortest (fewest-hops / min-cost) temporal distances.
- **Temporal pattern matching:** find subgraph embeddings whose edges satisfy both topological and temporal-ordering constraints (e.g., a motif that occurs *in order* within a duration $\Delta$).
- **Index design:** preprocess so window-constrained reachability/distance queries answer in (near-)constant or polylog time.

Decision (reachability), optimization (min-arrival/min-cost path), and counting (number of temporal paths/patterns) variants all arise. The problem is **open**: no index simultaneously achieves small space, fast queries across all four temporal-distance metrics, and supports updates.

## 2. Mathematical Foundations
Model a temporal graph $\mathcal{G}=(V,E,\tau)$ with $E$ a multiset of timestamped edges; $T=$ number of distinct timestamps. The **transformation to a static DAG** ("time-expanded" / "static expansion") creates a node per (vertex, time) event, with $O(|E|)$ nodes and edges, making earliest-arrival paths solvable by a single linear scan (Wu et al., VLDB 2014). Key facts:

- Temporal paths are **non-transitive and non-FIFO** in general: composition of optimal sub-paths need not be optimal under the "shortest (hop)" metric, breaking standard Dijkstra/2-hop assumptions.
- $2$-hop / hub labeling generalizes to **TopChain** and temporal hub labels, but label size depends on $T$.
- Counting temporal paths is **#P-hard**; even *restless* temporal path existence (bounded waiting time) is **NP-hard** (Casteigts et al.).

## 3. State of the Art (SOTA)
**Theory-SOTA:** Single-source earliest/latest/fastest/shortest temporal paths computable in $O(|E|\log T)$ via the one-pass / time-expanded algorithms of Wu, Cheng, Huang, Ke, Lu, Xu (VLDB 2014). Restless and waiting-time-bounded variants are NP-hard (Casteigts, Himmel, Molter, Zschoche 2021).

**Systems-SOTA:** Temporal-graph engines and indexes: **TopChain** (Wu et al., ICDE 2016) for reachability; **TVL / temporal 2-hop labeling** for distance; chronograph/streaming systems (Tegra, Raphtory, the GraphTides/Gradoop temporal extensions). General graph DBs (Neo4j, Kùzu, TigerGraph) handle temporal constraints only via predicate filtering, not specialized temporal indexes.

## 4. Upper Bound
- Single-source, all four metrics: $O(|E|\log T)$ time, $O(|V|+|E|)$ space (Wu et al.).
- Window reachability via TopChain: query $O(k)$ with $O(k|E|)$ index ($k$ = chain cover parameter).
- Temporal 2-hop distance labels: query $O(L)$, but worst-case label size $\Theta(|V|\cdot T)$.
- Restless path / pattern matching: FPT in temporal-pattern size by color-coding, $2^{O(k)}|E|\log T$.

## 5. Lower Bound
- **Restless temporal path** (existence with bounded waiting) is NP-complete (Casteigts et al. 2021).
- **Temporal pattern matching** generalizes subgraph isomorphism → NP-hard; counting is #P-hard.
- **Conditional fine-grained:** under SETH/OMv, no exact dynamic temporal-reachability index can support both updates and queries in $O(n^{1-\delta})$; static APSP-style barriers carry to all-pairs temporal distance.
- Index-space lower bounds: any reachability labeling for general temporal graphs requires $\Omega(|V|\cdot \text{(temporal width)})$ bits in the worst case.

## 6. The Gap
For *single-source* queries the time complexity is essentially settled (near-linear). The open frontier is **all-pairs window-constrained** distance with small index and updates: current labelings blow up with $T$, while lower bounds only forbid the most aggressive simultaneous guarantees — leaving a wide unresolved corridor between $\Theta(|V|T)$ space labelings and the $\Omega(\text{temporal width})$ bound. No dichotomy yet characterizes which temporal-graph classes admit polylog-query, near-linear-space indexes.

## 7. Current Research (as of June 2026)
Active groups: Molter/Zschoche/Niedermeier-lineage on parameterized temporal-graph algorithms; Cheng/Wu (HKUST/CUHK) on temporal indexing; Raphtory and Pometry on streaming temporal analytics. *(frontier — verify)* Recent directions include **temporal core/truss indexing** for window queries, GPU temporal BFS, and learned indexes predicting reachable sets. *(frontier — verify)* Emerging interest in **SQL/PGQ + temporal extensions** following the GQL/SQL:2023 property-graph standard, and in differentially-private temporal-path release.

## 8. Future Work
- Compact, updatable all-pairs temporal-distance index with provable query/space trade-off.
- Complexity dichotomy for temporal pattern matching by graph/temporal-width parameters.
- Unifying the four distance metrics under one cost-based optimizer in a property-graph engine.
- Approximate temporal reachability with sublinear sketches under sliding windows.

## 9. Key References
- **[Foundational]** Wu, Cheng, Huang, Ke, Lu, Xu. *Path problems in temporal graphs.* PVLDB, 2014.
- **[SOTA]** Wu, Huang, Cheng, Zhou, Yu, Lu. *Reachability and time-based path queries in temporal graphs (TopChain).* ICDE, 2016.
- **[Foundational]** Casteigts, Himmel, Molter, Zschoche. *Finding temporal paths under waiting-time constraints.* Algorithmica, 2021.
- **[Survey]** Holme, Saramäki. *Temporal networks.* Physics Reports, 2012.
- **[Survey]** Michail. *An introduction to temporal graphs: An algorithmic perspective.* Internet Mathematics, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
