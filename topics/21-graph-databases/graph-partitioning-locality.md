---
id: 21-graph-databases/graph-partitioning-locality
title: "Graph partitioning for query locality"
topic: 21-graph-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Graph partitioning for query locality

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/graph-partitioning-locality` · **Status:** empirically-open

## 1. Problem Statement
Partition a property graph $G=(V,E)$ across $p$ machines (or storage shards) so that **navigational query processing incurs minimal cross-partition traversal** (network hops / remote fetches), while keeping partitions **balanced** (load) and supporting **online evolution** of both the graph and the workload. The twist versus classical graph partitioning: the workload is a set of **navigational/path queries** (traversals, RPQs, pattern matches) that is often **unknown a priori** and **drifts over time**; partitions must be maintained incrementally as edges arrive and access patterns shift. Variants: (a) static workload-aware partitioning (minimize expected cut weighted by traversal frequency); (b) workload-oblivious (minimize edge cut / surrogate); (c) **online/streaming** partitioning with bounded migration; (d) vertex-cut vs. edge-cut formulations.

## 2. Mathematical Foundations
Classical formulation: **balanced minimum edge cut** — partition $V$ into $p$ parts of size $\le (1+\epsilon)|V|/p$ minimizing cut edges. This is **NP-hard**, and even hard to approximate: no constant-factor approximation for **balanced cut** unless P=NP; the best approximations are **$O(\sqrt{\log n})$** (Arora–Rao–Vazirani for sparsest cut) via SDP. **Spectral** methods relate the cut to the **Fiedler value** $\lambda_2$ of the Laplacian and **Cheeger's inequality** $\frac{\phi^2}{2}\le \lambda_2 \le 2\phi$ (conductance $\phi$). Workload-aware partitioning recasts the objective as minimizing **expected query cut** $\sum_q f_q \cdot \mathrm{cut}_q(\Pi)$ over a query distribution — but for *navigational* workloads the cut of a traversal depends on the *paths* taken, making the objective a function over walk distributions (random-walk / PageRank-style locality, hitting-time, and **modularity/community** structure). **Vertex separators** and **streaming partitioning** (one-pass heuristics like LDG, Fennel — Tsourakakis et al.) give online surrogates. Power-law degree distributions defeat uniform balance, motivating **vertex-cut** (PowerGraph) formulations.

## 3. State of the Art (SOTA)
- **Algorithmic-SOTA:** **METIS / ParMETIS** (multilevel Kernighan–Lin/Fiduccia–Mattheyses) remain the practical edge-cut workhorse; **KaHIP / KaHyPar** push quality; **spectral / SDP (ARV)** give the best theoretical approximations.
- **Streaming-SOTA:** **Fennel** (Tsourakakis–Gkantsidis–Radunovic–Vojnovic, WSDM 2014) and **LDG / HDRF / 2PS** for one-pass and vertex-cut partitioning.
- **Systems-SOTA:** **PowerGraph / GraphX** (vertex-cut), **Pregel/Giraph** (edge-cut), distributed graph DBs (**Neo4j Fabric, TigerGraph, JanusGraph, Nebula**) use hash or workload-hint partitioning; **Schism / SWORD / Clay** do workload-driven (re)partitioning for OLTP/graph workloads.

## 4. Upper Bound
Best provable approximation for the underlying **balanced/sparsest cut** is $O(\sqrt{\log n})$ (Arora–Rao–Vazirani, STOC 2004) via SDP rounding; spectral partitioning gives a Cheeger-type $O(\sqrt{\phi})$ guarantee. Streaming heuristics (Fennel) achieve strong empirical cut with one pass and $O(m)$ time but **no worst-case locality guarantee**. For *navigational query cut* specifically, **no algorithm with a provable approximation guarantee** is known — only empirical objectives and ML-guided heuristics.

## 5. Lower Bound
Balanced minimum cut / minimum bisection is **NP-hard** and admits **no PTAS** under standard assumptions; sparsest cut is **APX-hard / Unique-Games-hard** to approximate within any constant (Khot–Vishnoi). Thus exact workload-optimal partitioning is intractable. There is **no known nontrivial lower bound tailored to the *navigational-query-cut* objective** — its complexity (including the online/competitive version against drifting workloads) is essentially uncharacterized, which is precisely why the problem is *empirically-open*: practice outruns theory.

## 6. The Gap
This is **empirically-open**: systems ship effective partitioners (METIS, Fennel, vertex-cut) and report wins, but there is **(a)** no clean theoretical model that captures the *navigational/path-traversal* cut objective, **(b)** no approximation or competitive-ratio bound for *online* partitioning under *unknown, drifting* workloads, and **(c)** no consensus on whether edge-cut, vertex-cut, or hybrid is right for property-graph traversals. The gap is between strong empirical heuristics and the absence of a principled cost model + guarantees; closing it needs a workload-cut formalization and competitive online algorithms with bounded migration.

## 7. Current Research (as of June 2026)
**Tsourakakis** (streaming/Fennel lineage), **Schloegel/Karypis** (METIS), **Sanders/Schulz** (KaHIP/KaHyPar); workload-aware (re)partitioning by **Pavlo/Curino** (Schism/Clay lineage) and graph-DB vendors. *(frontier — verify)* 2025–2026 directions: **learned / RL-based** online partitioners that adapt to traversal logs, **GNN-guided** cut prediction, locality-aware partitioning for GQL/SQL-PGQ traversal plans, and HTAP graph stores co-designing storage layout with the query optimizer. Migration-bounded online repartitioning with competitive guarantees remains the open theoretical prize.

## 8. Future Work
- A formal **navigational-query-cut** objective and its complexity/approximability.
- **Competitive** online partitioning under drifting workloads with bounded data migration.
- Co-design of partitioning with the **query optimizer** (locality-aware plan + layout).
- Benchmarks isolating traversal locality (beyond edge-cut) for property graphs.

## 9. Key References
- **[Foundational]** Karypis, Kumar. *A Fast and High Quality Multilevel Scheme for Partitioning Irregular Graphs (METIS).* SIAM J. Sci. Comput., 1998. — [DOI](https://doi.org/10.1137/S1064827595287997)
- **[Foundational]** Arora, Rao, Vazirani. *Expander Flows, Geometric Embeddings and Graph Partitioning.* STOC 2004 / J. ACM 2009. — [DOI](https://doi.org/10.1145/1502793.1502794)
- **[SOTA]** Tsourakakis, Gkantsidis, Radunovic, Vojnovic. *FENNEL: Streaming Graph Partitioning for Massive Scale Graphs.* WSDM 2014. — [DOI](https://doi.org/10.1145/2556195.2556213)
- **[SOTA]** Gonzalez, Low, Gu, Bickson, Guestrin. *PowerGraph: Distributed Graph-Parallel Computation on Natural Graphs.* OSDI 2012. — [DBLP](https://dblp.org/rec/conf/osdi/GonzalezLGBG12.html)
- **[Survey]** Buluç, Meyerhenke, Safro, Sanders, Schulz. *Recent Advances in Graph Partitioning.* Algorithm Engineering, 2016. — [arXiv](https://arxiv.org/abs/1311.3144)

## 10. Worked Example

**Edge-cut vs. navigational-query cut.** Take a 6-vertex graph: a path $1\!-\!2\!-\!3\!-\!4\!-\!5\!-\!6$ plus one extra edge $1\!-\!6$. Partition into $p=2$ balanced parts of 3 vertices each.

A min-edge-cut partition $\{1,2,3\}\mid\{4,5,6\}$ cuts the edges $3\!-\!4$ and $6\!-\!1$, so **edge cut $=2$** (optimal). Now suppose the *workload* is the single 2-hop traversal "start at 2, walk to 4" with frequency $f=1000$. Every such walk crosses the $3\!-\!4$ boundary once, so **navigational cut $=1000$ remote hops**.

Alternative partition $\{2,3,4\}\mid\{1,5,6\}$ has edge cut $=3$ (cuts $1\!-\!2$, $4\!-\!5$, $1\!-\!6$) — *worse* by the classical objective — yet the hot walk $2\to3\to4$ stays entirely inside one part, giving **navigational cut $=0$**.

This shows the two objectives diverge: minimizing $\sum_q f_q\cdot\mathrm{cut}_q(\Pi)$ is not the same as minimizing edge cut. Since balanced min-cut is already NP-hard (best approximation $O(\sqrt{\log n})$, ARV), and the navigational variant lacks any proven approximation guarantee, the problem stays empirically-open.

---
*Part of the [DBMS Research catalog](../../README.md).*
