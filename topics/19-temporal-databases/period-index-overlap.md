# Period Indexing for Overlap Queries

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/period-index-overlap` · **Status:** partially-solved
> **Verification note:** The Period Index paper (Behrend, Dignós, Gamper et al.) appeared at SSTD 2019, not SSDBM; venue corrected in §3 and §9.

## 1. Problem Statement
Index a large collection of $n$ time periods (intervals) so that, given a query, the structure efficiently answers:
- **Stabbing query:** report (or count) all stored intervals containing a query *point* $q$.
- **Overlap / intersection query:** report all stored intervals intersecting a query *interval* $[q_s, q_e)$.
- **Range/containment variants:** intervals contained in, or containing, the query.

The goal is an index with **provably good bounds** — output-sensitive query time, near-linear space, and good update cost — that is also practical on disk/SSD and in columnar engines. Decision (does any interval overlap?), reporting (list them), and counting (how many) variants have distinct optimal complexities, and the dynamic (insert/delete) and external-memory (I/O) settings each change the achievable bounds.

## 2. Mathematical Foundations
The canonical internal-memory structure is the **interval tree** (Edelsbrunner / McCreight): a balanced BST on interval midpoints/medians answering stabbing in $O(\log n + k)$ and overlap in $O(\log n + k)$, $O(n)$ space, $O(\log n)$ updates. The **segment tree** gives $O(\log n + k)$ stabbing with $O(n \log n)$ space; the **priority search tree** (McCreight) handles 3-sided/half-open range and grounded interval queries in $O(\log n + k)$, $O(n)$ space.

Lower bounds come from **range-searching theory**: in the pointer-machine and cell-probe models, $d$-dimensional range/stabbing reporting obeys space–time tradeoffs of the form $S \cdot Q^{?}$; intervals map to points in 2D ($t_s, t_e$) with overlap becoming a *2-sided/3-sided* orthogonal range query, so Chazelle's optimal range-reporting bounds and the $\Omega(\log n / \log\log n)$ predecessor/cell-probe bounds apply. External memory uses the **I/O model** ($B$ block size, $M$ memory): the **external interval tree** (Arge–Vitter) achieves optimal $O(\log_B n + k/B)$ I/Os with linear blocks.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Interval tree and priority search tree are optimal in internal memory ($O(\log n + k)$, linear space); the **external interval tree** (Arge & Vitter, SICOMP 2003) is I/O-optimal; relative/multiversion B-trees give optimal stabbing/version queries on disk.

**Systems-SOTA:** Practical period indexes diverge from textbook structures for cache/SSD efficiency: the **Timeline Index** (SAP HANA, SIGMOD 2013), **RD-tree / GiST** range indexes (PostgreSQL SP-GiST and GiST over `range`/`tstzrange`), **Period Index** (Behrend, Dignós, Gamper et al., SSTD 2019) — a grid/duration-partitioned structure tuned for overlap and duration queries — and segment/interval-tree variants in time-series stores. R-trees and their interval specializations remain common in spatial-temporal DBMSs.

## 4. Upper Bound
- **Internal memory, static & dynamic:** stabbing and overlap reporting in $O(\log n + k)$ time, $O(n)$ space, $O(\log n)$ updates (interval tree / priority search tree) — optimal up to constants in the pointer-machine model.
- **Counting:** $O(\log n)$ stabbing count via augmented BST / fractional cascading.
- **External memory:** $O(\log_B n + k/B)$ I/Os, $O(n/B)$ blocks (external interval tree), I/O-optimal.
- **Practical:** Period Index and Timeline Index give near-constant-factor wins via duration partitioning and bitmap event lists, without improving asymptotics.

## 5. Lower Bound
- Pointer-machine range/stabbing reporting requires $\Omega(\log n + k)$ time with linear space; trading space allows no asymptotic query improvement for these 1D-interval / 2-3-sided queries.
- **Cell-probe / predecessor** lower bounds ($\Omega(\log n / \log\log n)$, Pătrașcu–Thorup) apply because point stabbing subsumes predecessor search on endpoints.
- In external memory, $\Omega(\log_B n + k/B)$ I/Os is necessary, matching the external interval tree.
These bounds make the *static* problem essentially closed.

## 6. The Gap
For static and standard dynamic settings in both internal and external memory, **upper and lower bounds match** — the problem is solved asymptotically. The remaining gaps are practical and in harder settings: (i) **cache-/SSD-aware** constants and write amplification on LSM/columnar stores; (ii) **highly dynamic, versioned** workloads (insert-heavy temporal streams) where update cost vs. query cost tradeoffs are not tight; (iii) **approximate / learned** period indexes with provable error and space bounds; (iv) multi-attribute (period + key + value) combined queries where optimal multidimensional bounds re-open. Hence: partially-solved.

## 7. Current Research (as of June 2026)
- Duration-aware and grid-based period indexes (Bozen-Bolzano group: Behrend, Dignós, Gamper) refining the Period Index for overlap+duration predicates.
- **Learned / ML-augmented** interval and range indexes; recursive-model-index analogues for periods, with attention to worst-case guarantees.
- Period indexing inside lakehouse/columnar formats (Iceberg/Parquet zone maps, min/max skipping for `validfrom/validto`) — *(frontier — verify)* "time-travel pruning" indexes co-designed with version metadata.
- GPU/SIMD interval-stabbing and compressed succinct interval structures.

## 8. Future Work
- Provably good **dynamic** period indexes optimized for LSM/SSD write amplification.
- Learned period indexes with worst-case (not just empirical) query and space guarantees.
- Combined period+value multidimensional indexes with tight bounds.
- Succinct / compressed interval indexes approaching the information-theoretic space lower bound while keeping output-sensitive queries.

## 9. Key References
- **[Foundational]** Edelsbrunner, H. *Dynamic Data Structures for Orthogonal Intersection Queries.* TR, TU Graz, 1980. (interval tree) — [PDF](https://pub.ista.ac.at/~edels/Papers/1980-01-R-OrthogonalIntersectionQueries.pdf)
- **[Foundational]** McCreight, E. *Priority Search Trees.* SIAM J. Computing, 1985. — [DOI](https://doi.org/10.1137/0214021)
- **[Foundational]** Arge, L., Vitter, J. S. *Optimal External Memory Interval Management.* SIAM J. Computing, 2003. — [DOI](https://doi.org/10.1137/S009753970240481X)
- **[SOTA]** Behrend, A., Dignós, A., Gamper, J., et al. *Period Index: A Learned 2D Hash Index for Range and Duration Queries.* SSTD, 2019. — [DBLP search](https://dblp.org/search?q=Period%20Index%20Behrend%20Dignos%20Gamper%20duration)
- **[SOTA]** Kaufmann, M. et al. *Timeline Index.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465293)
- **[Foundational]** Chazelle, B. *Filtering Search: A New Approach to Query-Answering.* SIAM J. Computing, 1986. (range-reporting lower/upper bounds) — [DOI](https://doi.org/10.1137/0215051)

## 10. Worked Example

Store $n=4$ periods (half-open):

| id | $[t_s, t_e)$ |
|----|--------------|
| A  | $[1, 5)$ |
| B  | $[3, 8)$ |
| C  | $[6, 9)$ |
| D  | $[2, 4)$ |

**Stabbing query** at point $q=3$: an interval is stabbed iff $t_s \le 3 < t_e$. Check: A ($1\le3<5$ yes), B ($3\le3<8$ yes), C ($6\le3$ no), D ($2\le3<4$ yes). Result $\{A,B,D\}$, $k=3$.

**Overlap query** with $[q_s,q_e)=[4,6)$: overlap iff $t_s < q_e \wedge q_s < t_e$, i.e. $t_s<6 \wedge 4<t_e$. A: $1<6 \wedge 4<5$ yes; B: $3<6 \wedge 4<8$ yes; C: $6<6$ false; D: $4<4$ false. Result $\{A,B\}$.

**Why output-sensitive matters.** An interval tree answers each in $O(\log n + k)$: here $\log_2 4 = 2$ comparisons to locate the relevant subtree plus $O(k)$ to emit. Mapping intervals to 2D points $(t_s,t_e)$, the overlap test is the 2-sided box $t_s<6,\;t_e>4$ — a quadrant range query, which is exactly the priority-search-tree's $O(\log n + k)$ regime.

---
*Part of the [DBMS Research catalog](../../README.md).*
