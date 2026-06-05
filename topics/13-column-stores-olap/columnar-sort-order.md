# Optimal Sort Order for Columnar Storage

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/columnar-sort-order` · **Status:** open

## 1. Problem Statement
Given a table with columns $A_1,\dots,A_m$ stored column-wise in blocks, choose a **global tuple ordering** (a permutation of rows, typically expressed as a lexicographic/composite sort key or a space-filling clustering) that jointly maximizes:
- **Run-length / encoding compression** — sorting clusters equal values into long runs (RLE, delta, dictionary) shrinking each column; and
- **Predicate pushdown / data skipping** — sorted/clustered blocks yield tight **zone maps** (min/max), letting scans prune blocks.

A single global order serves all columns at once, so improving one column's locality can hurt another's. Variants:
- **Optimization:** minimize total stored bytes and/or expected scanned blocks for a workload.
- **Decision:** is there an order achieving compressed size $\le S$ and expected skip $\ge K$?
- **Counting/structural:** characterize achievable (compression, skipping) Pareto frontiers.

## 2. Mathematical Foundations
Sorting by a lexicographic key $(A_{\pi(1)},\dots,A_{\pi(k)})$ makes the *first* key column perfectly run-length-compressible and progressively degrades subsequent ones; the compression of column $A_j$ depends on the number of distinct prefixes above it, i.e., on **column cardinalities and correlations**. Choosing the *ordering of sort keys* to minimize total run count is related to **optimal lexicographic ordering** and is provably hard: deciding the row permutation minimizing total RLE size generalizes problems reducible from **Optimal Linear Arrangement** and TSP-like locality objectives, hence **NP-hard**. For predicate skipping, a sort/clustering induces **locality** measured by how tightly each block's value-range covers few queries; multi-column locality is captured by **space-filling curves** (Z-order/Morton, Hilbert) which bound the dilation between value-space and storage-order distance. Information-theoretically, the minimum compressed size is lower-bounded by the data's entropy $H$; sorting can only help an encoder approach the conditional entropy $H(A_j \mid \text{prefix})$. The joint objective is **multi-objective** (compression vs. skipping) and generally has no single optimum — only a Pareto set.

## 3. State of the Art (SOTA)
- **C-Store / Vertica** (Stonebraker et al., VLDB 2005): multiple *projections*, each with its own sort order, sidestep the single-order limitation by storing redundant copies sorted differently.
- **Z-order / Hilbert multi-dimensional clustering:** used in Databricks **Z-ordering** and **Liquid Clustering**, Amazon Redshift compound/interleaved sort keys; balances skipping across several columns.
- **Correlation-aware ordering:** work on choosing compound sort keys and **column ordering for compression** (e.g., heuristics ordering by ascending cardinality to maximize downstream runs).
- **Systems-SOTA:** Parquet/ORC row-group min/max + Bloom filters; Snowflake micro-partition clustering; Apache Iceberg sort orders. WiscKey/learned approaches and **BtrBlocks** (Kuschewski et al., SIGMOD 2023) study encoding selection given an order.

## 4. Upper Bound
Heuristic upper bounds dominate practice: **order sort keys by ascending distinct-count** to maximize total run length (greedy), and use **Z-order/Hilbert** clustering to get provably bounded multi-column locality (space-filling-curve dilation bounds). For a *fixed* sort key, optimal per-column encoding selection is solvable greedily/DP (BtrBlocks-style), and zone-map skipping is then computable exactly. With redundant projections (C-Store), each query class can be served by an order that is optimal *for it*, trading storage for a near-optimal per-query bound. No polynomial algorithm is known to optimize the single global order exactly.

## 5. Lower Bound
Choosing the row permutation minimizing total RLE/compressed size is **NP-hard** (reductions from Optimal Linear Arrangement / Hamiltonicity-style locality objectives); the multi-column **interleaving** that simultaneously optimizes skipping for several predicates is likewise NP-hard. Information-theoretically, no order can compress below the joint entropy $H(A_1,\dots,A_m)$, and a single linear order cannot achieve every column's conditional-entropy bound simultaneously (a provable tension — only the prefix columns reach it). Space-filling curves have an inherent **dilation lower bound**: no single curve preserves all pairwise multi-dimensional proximity, bounding achievable skipping.

## 6. The Gap
The problem is **genuinely open**. We have NP-hardness for the exact objective and good heuristics, but **no tight approximation algorithm** with a proven ratio for the joint compression-plus-skipping objective, and no clean characterization of the compression/skipping Pareto frontier. The gap between greedy/space-filling heuristics and the (unknown) optimum is uncharacterized; whether a constant-factor approximation exists for realistic objectives is open.

## 7. Current Research (as of June 2026)
Active work: **learned and workload-aware clustering** (choosing sort/cluster keys from query logs), Liquid Clustering theory for lakehouses, and **encoding-aware ordering** that co-optimizes the sort key with the compression scheme (BtrBlocks, FSST string compression). *(frontier — verify)* Recent efforts explore approximation algorithms for interleaved/Z-order key selection and reinforcement-learning clustering advisors, plus joint optimization of sort order with zone-map/Bloom-filter sidecar structures.

## 8. Future Work
- Provable approximation algorithms for the joint compression + skipping objective.
- A characterization of the compression/skipping Pareto frontier and when redundant projections beat a single order.
- Workload-adaptive, drift-aware sort orders (links to *Adaptive Column Layout Reorganization*).
- Co-design of sort order with SIMD scan kernels and encodings (links to *Optimal SIMD Operator Kernels*).

## 9. Key References
- **[Foundational]** Stonebraker, Abadi, Batkin, Chen, Cherniack, et al. *C-Store: A Column-Oriented DBMS.* VLDB, 2005.
- **[Foundational]** Abadi, Madden, Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006.
- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023.
- **[SOTA]** Lemire, Boytsov. *Decoding Billions of Integers per Second through Vectorization.* Software: Practice and Experience, 2015.
- **[Foundational]** Gaede, Günther. *Multidimensional Access Methods* (space-filling curves / Z-order, Hilbert). ACM Computing Surveys, 1998.
- **[SOTA]** Boncz, Neumann, Leis. *FSST: Fast Static Symbol Table String Compression.* VLDB, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
