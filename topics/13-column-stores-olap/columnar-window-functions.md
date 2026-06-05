# Window-Function Execution on Columns

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/columnar-window-functions` · **Status:** open

## 1. Problem Statement
SQL window functions — `OVER (PARTITION BY ... ORDER BY ... ROWS/RANGE/GROUPS BETWEEN ...)` — compute, for each row, an aggregate or ranking over a *frame* of neighboring rows within its partition. On columnar engines the challenge is to evaluate them **efficiently over packed, vectorized columns** without materializing wide intermediate rows, while handling: (1) **partitioning** (segmenting), (2) **ordering** (sorting within partitions), (3) **framing** (`ROWS`, `RANGE`, `GROUPS`, with unbounded/sliding bounds and `EXCLUDE`), and (4) **incremental evaluation** of the aggregate as the frame slides.

Variants:
- **Optimization (focus):** minimize total work given $N$ rows, $p$ partitions, frame width $w$; ideally $O(N)$ or $O(N\log N)$ rather than $O(N\cdot w)$.
- **Decision/structural:** which physical operator (full sort vs. hash-partition vs. exploit existing sort order) and which incremental algorithm per aggregate.
- Mixing **multiple windows** with different `PARTITION/ORDER` clauses in one query (operator ordering, shared sorts).

## 2. Mathematical Foundations
For a row $i$ with frame $F_i \subseteq$ its partition, output is $f(\{x_j : j\in F_i\})$. Sliding windows form a **range-aggregate** problem over a sequence. Key algebraic structure:
- **Invertible aggregates** (`SUM`, `COUNT`, `AVG`): maintain a running value, add entering / subtract leaving elements — $O(1)$ amortized per slide via **prefix sums** $P_k=\sum_{j\le k}x_j$, frame sum $=P_u-P_{l-1}$.
- **Non-invertible / order-statistic** (`MAX`, `MIN`, `MEDIAN`, `FIRST_VALUE`): need monotone deques or balanced trees. The classic **sliding-window minimum** is $O(N)$ amortized via a monotone deque. General associative-but-not-invertible aggregates use the **DABA / FlatFAT / Two-Stacks (Reactive Aggregator)** algorithms achieving $O(1)$ amortized per element for any associative operator over a sliding window.
- Ranking (`RANK`, `DENSE_RANK`, `NTILE`, `ROW_NUMBER`) reduces to scanning sorted partitions in $O(N)$ after an $O(N\log N)$ sort.
The lower bound for arbitrary-order window aggregation is governed by **sorting** ($\Omega(N\log N)$ comparisons) when no usable sort order exists; with exploitable clustering it can drop to $O(N)$.

## 3. State of the Art (SOTA)
- **Leis, Kundhikanjana, Kemper, Neumann.** *Efficient Processing of Window Functions in Analytical SQL Queries.* PVLDB 2015 — the canonical work: segment-tree-based aggregation, partition-parallel evaluation, and frame-type-specific algorithms; basis for HyPer/Umbra and influential on DuckDB.
- **DuckDB** window operator: vectorized, parallel, uses segment trees for general frames and specialized paths for `ROWS`/running aggregates; partition-by-hash with merge.
- **Streaming SOTA for sliding aggregation:** **FlatFAT** (Tangwongsan et al., VLDB 2015) and **DABA / DABA Lite** (Tangwongsan, Hirzel, Schneider) — amortized $O(1)$ per element for general associative windows, used in stream processors and applicable to columnar batch windows.
- Vectorized engines (Velox, DataFusion, ClickHouse, Photon) implement similar partition→sort→frame pipelines with SIMD running aggregates.

## 4. Upper Bound
Ranking and prefix-sum window aggregates: $O(N\log N)$ dominated by sorting, then $O(N)$ evaluation. For **sliding-window general associative** aggregates, segment trees give $O(\log w)$ per output / $O(N\log w)$ total; **DABA/Two-Stacks** improve this to **$O(1)$ amortized per element**, i.e., $O(N)$ overall, optimal. Invertible aggregates over arbitrary frames are $O(N)$ via prefix sums. When the input already carries the required `ORDER BY` (e.g., co-sorted columnar layout), the sort is elided and total cost is linear — a key columnar opportunity.

## 5. Lower Bound
When the window's `ORDER BY` does not match any existing physical order, evaluating ranking/ordered windows requires sorting, giving $\Omega(N\log N)$ in the comparison model (and matching cache-oblivious / external-memory sorting bounds $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$). For sliding general associative aggregation, $\Omega(1)$ amortized per element is trivially tight (DABA matches). For multiple windows with incompatible orderings, you provably need $\ge$ one sort per distinct `(PARTITION, ORDER)` equivalence class unless a single order refines several — choosing a minimal covering set of sorts is itself an optimization (chain-cover / interesting-orders) problem.

## 6. The Gap
Per-window asymptotics are essentially **closed** (sorting + $O(1)$-amortized sliding aggregation are optimal). The genuinely **open** problems are systems/optimization-level: (a) **multi-window plans** — globally minimizing sorts/partitionings across many windows (interesting-orders for windows) lacks a clean optimal algorithm; (b) exploiting **columnar sort order and zone maps** to skip partitions/sorts adaptively; (c) **spilling** large partitions to disk while keeping incremental aggregation cheap; (d) parallel/vectorized constant factors for `RANGE`/`GROUPS`/`EXCLUDE` frames remain far from the $O(1)$ ideal.

## 7. Current Research (as of June 2026)
- **Order-aware optimization** extending Selinger interesting-orders to window clauses, reusing sorts across windows and upstream operators *(frontier — verify)*.
- **Out-of-core / spilling window operators** in DuckDB and DataFusion for partitions exceeding memory.
- **GPU and SIMD** window execution (Velox, HeavyDB, ClickHouse) pushing constant factors down.
- Groups: TUM (Neumann/Kemper — HyPer/Umbra), CWI/DuckDB (Raasveldt/Mühleisen), IBM/streaming-aggregation lineage (Hirzel, Tangwongsan, Schneider), Meta Velox and Apache DataFusion communities.

## 8. Future Work
- A principled cost model and algorithm for **minimal sort/partition covering** across multi-window queries.
- Adaptive window execution that **exploits existing columnar order and zone maps**.
- Memory-bounded incremental aggregation with provable spill behavior.
- Distributed window functions with low shuffle for skewed partitions.

## 9. Key References
- **[SOTA]** Leis, Kundhikanjana, Kemper, Neumann. *Efficient Processing of Window Functions in Analytical SQL Queries.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2794367.2794375)
- **[SOTA]** Tangwongsan, Hirzel, Schneider, Wu. *General Incremental Sliding-Window Aggregation (FlatFAT).* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752940)
- **[SOTA]** Tangwongsan, Hirzel, Schneider. *Low-Latency Sliding-Window Aggregation in Worst-Case Constant Time (DABA).* DEBS, 2017. — [DOI](https://doi.org/10.1145/3093742.3093925)
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational DBMS.* SIGMOD, 1979 (interesting orders). — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Bellamkonda et al. *Adaptive and Big Data Scale Parallel Execution of Window Functions* / Oracle window optimizations. PVLDB, 2013. — [DOI](https://doi.org/10.14778/2536222.2536235)
- **[Survey]** Abadi, Boncz, Harizopoulos et al. *The Design and Implementation of Modern Column-Oriented Database Systems.* FnT Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Query: `SUM(x) OVER (ORDER BY t ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING)` — a sliding sum of width $w=3$. Input column (already sorted by $t$): $x = [4, 2, 7, 1, 5]$.

Using prefix sums $P = [0,4,6,13,14,19]$ (with $P_0=0$, $P_k=\sum_{j\le k}x_j$), the frame for row $i$ is $[\max(1,i-1),\min(N,i+1)]$ and its sum is $P_u - P_{l-1}$:

| i | frame | $P_u - P_{l-1}$ | result |
|---|-------|-----------------|--------|
| 1 | [1,2] | $P_2 - P_0 = 6$  | 6 |
| 2 | [1,3] | $P_3 - P_0 = 13$ | 13 |
| 3 | [2,4] | $P_4 - P_1 = 10$ | 10 |
| 4 | [3,5] | $P_5 - P_2 = 13$ | 13 |
| 5 | [4,5] | $P_5 - P_3 = 6$  | 6 |

Because `SUM` is invertible, each output is one subtraction — $O(N)$ total, with no $O(N\cdot w)$ rescan (§4). Since the input already carries the `ORDER BY t` physical order, the $O(N\log N)$ sort is elided — the columnar opportunity of §4.

---
*Part of the [DBMS Research catalog](../../README.md).*
