# Page Clustering / Co-Location for Locality

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/page-coclustering` · **Status:** open

## 1. Problem Statement

Given a set of tuples (or records) and a query workload, assign tuples to physical pages so that, under the buffer pool's replacement policy, the **number of distinct pages touched per query is minimized** — equivalently, maximize buffer locality. Co-locating correlated tuples means a query that needs them faults in fewer pages and they remain resident together.

Formally: let pages hold $B$ tuples each; a workload is a multiset of queries $q$, each accessing a tuple set $S_q \subseteq T$. Find a partition $\pi : T \to \text{pages}$ (each block size $\le B$) minimizing the expected **distinct pages fetched**, $\sum_q w_q \cdot |\{\pi(t) : t \in S_q\}|$, possibly under a replacement model.

Variants:
- **Optimization:** minimize total pages touched (a *graph/hypergraph partitioning* problem).
- **Decision:** can a layout touch $\le k$ pages for the workload?
- **Online/adaptive:** re-cluster as the workload drifts, amortizing reorganization cost.
- **Counting:** number of distinct co-clustering layouts achieving optimum (rarely needed).

## 2. Mathematical Foundations

**Hypergraph partitioning model.** Build a hypergraph $H=(T,E)$ where vertices are tuples and each query $q$ is a hyperedge $S_q$ (weight $w_q$). Packing tuples into pages of capacity $B$ to minimize edges "cut across multiple pages" is **balanced minimum-cut hypergraph partitioning** — the canonical NP-hard formulation underlying database clustering (the "minimize page accesses" objective generalizes the **bandwidth/min-linear-arrangement** family).

**Submodularity.** The coverage function "pages saved by co-locating set $X$" is **monotone submodular**, so greedy merging gives a $(1-1/e)$-type guarantee for cardinality-constrained variants; but the *partition into equal pages* constraint is a matroid/partition constraint that breaks pure greedy optimality.

**Connections.** Special cases reduce to **minimum linear arrangement (MinLA)**, **graph bisection**, and **correlation clustering**. With pairwise co-access weights $A_{ij}$ (how often $i,j$ co-occur), maximizing intra-page weight is **max-$k$-cut's complement** / **graph partitioning**, APX-hard. The 1-D ordering relaxation (place tuples on a line, then chop into pages) connects to **spectral ordering** via the Fiedler vector of the Laplacian.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **AutoClust / data-driven clustering** in column stores and **Z-order / Hilbert space-filling curves** (used in Amazon Redshift, Databricks Delta "ZORDER", Snowflake micro-partition clustering) co-locate multidimensionally correlated rows. **Database Cracking** (Idreos et al., CIDR 2007) reorganizes incrementally under query pressure. **Qd-tree** (Yang et al., SIGMOD 2020) learns a workload-aware data layout (block assignment) via RL. Multilevel hypergraph partitioners (**hMETIS**, **KaHyPar**) are the practical engines.

**Theory-SOTA.** MinLA admits an $O(\sqrt{\log n}\,\log\log n)$ approximation (Charikar et al./Feige–Lee); balanced separators give $O(\sqrt{\log n})$ (Arora–Rao–Vazirani) for the cut quality feeding partition recursion.

## 4. Upper Bound

- **Balanced partitioning / MinLA:** $O(\sqrt{\log n}\,\log\log n)$-approximation (RAM model, SDP-based, Charikar–Hajiaghayi–Karloff–Rao).
- **Min bisection:** $O(\log^{1.5} n)$ approximation (Krauthgamer–Feige).
- **Submodular co-location subproblems:** $(1-1/e)$ greedy under cardinality, $1/2$ under matroid constraints.
- **Practical:** multilevel KaHyPar/hMETIS give near-optimal cuts empirically; Qd-tree's learned layouts beat hand-tuned in evaluation but carry **no worst-case guarantee**.

## 5. Lower Bound

- **Balanced graph/hypergraph partitioning is NP-hard** and **APX-hard**; min-bisection has no PTAS unless P=NP (and is hard to approximate within any constant under stronger assumptions).
- **MinLA is NP-hard** (Garey–Johnson–Stockmeyer) and admits no PTAS unless P=NP.
- Under the **Small-Set-Expansion / Unique-Games** conjecture, balanced separator and partition objectives have no constant-factor approximation.
- The **online/adaptive** version inherits competitive-ratio limits from metrical task systems when re-clustering cost is charged.

## 6. The Gap

This is **genuinely open**. The static layout problem is NP-/APX-hard with only **polylog-approximation** upper bounds, leaving a wide gap to the constant-factor lower bounds — and even those upper bounds optimize *cut*, not the true *replacement-policy-aware page-fault* objective, which no approximation result directly models. Closing it requires either (a) a workload model under which co-clustering is poly-time/constant-approximable, or (b) hardness for the page-fault objective itself, plus (c) bridging from cut-minimization to the interaction with LRU/ARC eviction, which current theory ignores. Learned layouts (Qd-tree) work empirically but lack guarantees.

## 7. Current Research (as of June 2026)

- **Learned, workload-adaptive layouts** unifying partitioning, sort order, and indexing (Qd-tree successors; MIT DSAIL, Microsoft Research). *(frontier — verify)*
- **Space-filling-curve clustering with learned key orders** in lakehouse formats (Delta/Iceberg liquid clustering). *(frontier — verify)*
- **Replacement-aware co-design** that optimizes layout *and* eviction jointly rather than treating cut as a proxy. *(frontier — verify)*
- Online re-clustering with bounded reorganization cost (database-cracking lineage, CWI).

## 8. Future Work

- An approximation algorithm for the true **expected-pages-fetched** objective (not the cut proxy) under a stated replacement model.
- Hardness or constant-factor results for replacement-aware co-clustering.
- Provably-bounded **online** re-clustering amortizing layout-change I/O.
- Multi-query / shared-scan co-location that accounts for concurrent buffer contention.

## 9. Key References

- **[Foundational]** Garey, Johnson, Stockmeyer. *Some Simplified NP-Complete Graph Problems.* TCS, 1976.
- **[Foundational]** Arora, Rao, Vazirani. *Expander Flows, Geometric Embeddings and Graph Partitioning.* JACM, 2009.
- **[SOTA]** Yang, Wu, Kandula, et al. *Qd-tree: Learning Data Layouts for Big Data Analytics.* SIGMOD, 2020.
- **[Foundational]** Idreos, Kersten, Manegold. *Database Cracking.* CIDR, 2007.
- **[SOTA]** Schlag, Heuer, Sanders, et al. *KaHyPar: Multilevel Hypergraph Partitioning.* ALENEX/JEA, 2016–2023.
- **[Survey]** Charikar, Hajiaghayi, Karloff, Rao. *$\ell_2^2$ Spreading Metrics for Vertex Ordering Problems.* SODA/Algorithmica, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
