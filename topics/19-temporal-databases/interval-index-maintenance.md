# Long-Lived Interval Index Maintenance

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/interval-index-maintenance` · **Status:** partially-solved

## 1. Problem Statement

Temporal access methods index a dynamic set of $n$ intervals $\{[s_i,e_i)\}$ to answer **stabbing** ("which intervals contain point $t$?") and **overlap** ("which intervals intersect $[a,b)$?") queries. The hard regime is **high-velocity insert/expire**: rows arrive continuously and "expire" when their valid- or transaction-time period closes (right endpoint set, often to `NOW`). The index must sustain high insert and delete/expire throughput while keeping queries fast and space linear, and must cope with **long-lived intervals** (a few rows that stay open for the entire history) coexisting with a torrent of short-lived ones.

The challenge is that the textbook optimal static structures (interval tree, segment tree, priority search tree) are balanced over the *current* endpoint set and degrade or rebalance expensively under churn; transaction-time append-only models forbid in-place deletion (expiry = appending a closing version), inflating the live set. Variants: *decision* (is any interval live at $t$?), *reporting* (output all $k$ stabbed), *counting* (how many live at $t$), and the **maintenance** objective itself: minimize amortized/worst-case update cost and I/O while bounding query cost and space, including under a moving `NOW`.

## 2. Mathematical Foundations

Stabbing on $n$ static intervals is solved by the **interval tree** ($O(n)$ space, $O(\log n + k)$ query) and the **segment tree** ($O(n\log n)$ space, $O(\log n + k)$). In external memory, the I/O-optimal structures are the **External Interval Tree** (Arge–Vitter, *SIAM J. Comput. 2003*) and the **External Priority Search Tree**, achieving $O(\log_B n + k/B)$ query and $O(\frac1B\log_B n)$ amortized update in the **I/O model** with block size $B$. Lower bounds come from the **pointer-machine** and **cell-probe** models: any structure answering stabbing in $O(\log n + k)$ needs $\Omega(n)$ space; in external memory, dynamic stabbing has the classic *interval-management* lower bound matching the external interval tree.

The temporal-specific structures are *partially persistent* / *multiversion* access methods. The **Multiversion B-tree (MVBT)** (Becker–Gschwind–Ohler–Seeger–Widmayer, *VLDB J. 1996*) makes a B-tree partially persistent with **$O(\log_B n)$ query and amortized update and $O(n/B)$ space** for transaction-time data, by the *version-split / weak-version-condition* technique. The **Time-Split B-tree** (Lomet–Salzberg) and the **Time-Polygon / TSB-tree** family handle bitemporal data. Long-lived intervals are the formal pain point: a "copy on version split" pattern can replicate an interval that spans many versions, so the *amortized* bounds depend on a charging argument that fat intervals can break; segment-tree-style $\log n$ fragment storage trades space for update locality.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** External Interval Tree / External Priority Search Tree (Arge–Vitter) are I/O-optimal for dynamic stabbing; MVBT (Becker et al.) is the canonical I/O-efficient transaction-time access method with provable bounds.
- **Systems-SOTA:** PostgreSQL **GiST/SP-GiST** over `range`/`tstzrange` types is the deployed interval index; it is heuristic (no worst-case stabbing guarantee) but handles churn well in practice. **RD-tree / R-tree** variants index intervals as 1-D boxes. LSM-tree engines (RocksDB-backed temporal stores, time-series DBs like InfluxDB/TimescaleDB hypertables) absorb high-velocity inserts via append + compaction, indexing time by chunk pruning rather than a true interval index. SQL Server / DB2 system-versioned tables use a history table partitioned by time, relying on partition elimination rather than a stabbing index.

## 4. Upper Bound

In the **I/O model**, dynamic interval stabbing/overlap is achievable in $O(\log_B n + k/B)$ query, $O(\frac1B\log_B n)$ amortized update, $O(n/B)$ space (External Interval Tree, Arge–Vitter). For transaction-time (insert + close-version) workloads, MVBT gives $O(\log_B m + k/B)$ where $m$ is total versions, with $O(m/B)$ space and $O(\log_B m)$ amortized update. **LSM-based** interval indexes trade query for update: $O(1)$ amortized insert (buffered) but query touches $O(\log n)$ levels, mitigated by per-level interval-aware filters; this is the practical high-velocity sweet spot. With long-lived intervals separated into a small *broadcast/overflow* set of size $\ell$, queries pay an additive $O(\ell)$ and the main index keeps its bounds.

## 5. Lower Bound

In the **pointer-machine model**, any data structure answering interval stabbing in $O(\log n + k)$ time must use $\Omega(n)$ space, and segment-tree-style $O(\log n)$-fragment storage is necessary to get $O(\log n + k)$ if intervals are stored by canonical cover. In **external memory**, dynamic interval management has a lower bound matching the external interval tree (Arge–Vitter), so its bounds are *optimal*. For the *update* side, the **cell-probe** lower bounds for dynamic 1-D stabbing/predecessor (Pătraşcu–Thorup) force $\Omega(\log n / \log\log n)$ per operation for exact structures, ruling out $O(1)$ worst-case updates. Append-only transaction-time forbids physical deletion, so the *live-set* lower bound is information-theoretic: an index over total history must, in the worst case, store $\Omega(m/B)$ blocks even if few intervals are live at any instant.

## 6. The Gap

The **static and amortized I/O-optimal** picture is closed (interval tree, external interval tree, MVBT). What remains **partially open / unsolved in practice**: (1) **worst-case** (non-amortized) update bounds under simultaneous high insert *and* high expire rates, where MVBT's amortization can spike during version consolidation; (2) graceful handling of **long-lived intervals**, which break charging arguments and bloat multiversion structures — no deployed index has a clean, provable separation; (3) **moving-`NOW`** right endpoints, where "expiry" is implicit (the interval is open until closed), so the index must reason about the now-diagonal. The gap is the distance between LSM-style practical throughput (no worst-case query/space guarantee) and the theory-optimal trees (poor under bursty churn).

## 7. Current Research (as of June 2026)

- **Learned** and **LSM-interval** hybrid indexes adapting learned-index ideas to interval/stabbing queries and to time-series chunk pruning *(frontier — verify)*.
- Long-lived-interval separation ("hot/cold" or "fat/thin" interval lanes) and update-optimized variants of the external interval tree in column stores *(frontier — verify)*.
- Timescale/Influx-style chunked time partitioning gaining true interval-stabbing secondary indexes; research on bitemporal indexing for system-versioned tables in MariaDB/DB2 *(frontier — verify)*.

## 8. Future Work

- Worst-case-optimal dynamic interval index under combined insert/expire bursts with proven bounds, not just amortized.
- Provable long-lived-interval handling with additive (not multiplicative) query overhead and bounded space.
- Now-relative interval indexing that advances the now-diagonal in $O(\log n)$ amortized without periodic global rebuild.

## 9. Key References

- **[Foundational]** L. Arge, J. S. Vitter. *Optimal External Memory Interval Management.* SIAM Journal on Computing, 32(6), 2003. — [DOI](https://doi.org/10.1137/S009753970240481X)
- **[Foundational]** B. Becker, S. Gschwind, T. Ohler, B. Seeger, P. Widmayer. *An Asymptotically Optimal Multiversion B-Tree.* VLDB Journal, 5(4), 1996. — [DOI](https://doi.org/10.1007/s007780050028)
- **[Foundational]** D. Lomet, B. Salzberg. *The Performance of a Multiversion Access Method (Time-Split B-tree).* ACM SIGMOD, 1990. — [DOI](https://doi.org/10.1145/93605.98744)
- **[Foundational]** M. Pătraşcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* ACM STOC, 2006 (cell-probe lower bounds). — [arXiv](https://arxiv.org/abs/cs/0603043)
- **[Survey]** B. Salzberg, V. J. Tsotras. *Comparison of Access Methods for Time-Evolving Data.* ACM Computing Surveys, 31(2), 1999. — [DOI](https://doi.org/10.1145/319806.319816)
- **[Foundational]** H. Edelsbrunner. *Dynamic Data Structures for Orthogonal Intersection Queries.* TR, TU Graz, 1980 (interval tree). — [PDF](https://pub.ista.ac.at/~edels/Papers/1980-01-R-OrthogonalIntersectionQueries.pdf)

## 10. Worked Example

Consider a transaction-time table with one long-lived row and a torrent of short ones. At version $0$ insert the "fat" interval $F=[0,\infty)$ (still open). Then at each version $i=1,\dots,6$ insert a "thin" row valid for one tick: $T_i=[i,i+1)$, closing each at the next version.

Stabbing query "what is live at $t=3.5$?" should return $\{F, T_3\}$.

Cost in a naive MVBT with **copy-on-version-split**: every page split that occurs while $F$ is open must copy $F$ into the new page. With $6$ insertions triggering, say, $3$ splits, $F$ is replicated $3$ times — its storage is $O(\#\text{splits})$, not $O(1)$. Over $n$ insertions this can reach $\Theta(n)$ copies of one interval, breaking the amortized $O(\log_B n)$ space-charging argument.

The **fat/thin separation** fix: route $F$ to a tiny overflow list of size $\ell=1$; the main index holds only the $T_i$ with clean $O(n/B)$ space and $O(\log_B n + k/B)$ queries. The stab at $t=3.5$ pays the main-index cost plus an additive scan of the $\ell=1$ overflow, returning $\{T_3\}\cup\{F\}$.

---
*Part of the [DBMS Research catalog](../../README.md).*
