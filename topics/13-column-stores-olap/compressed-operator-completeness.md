# Direct Computation on Compressed Columns

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/compressed-operator-completeness` · **Status:** partially-solved

## 1. Problem Statement

Characterize **which relational and aggregate operators can be evaluated directly on encoded/compressed column data** — without fully materializing (decompressing) the values — and at what asymptotic cost relative to the encoded size $z$ versus the logical size $n$.

- **Membership variant:** Given an operator $\theta$ (selection, projection, join, group-by, SUM/COUNT/MIN/MAX/AVG, top-k) and an encoding $E$, can $\theta$ run on $E(R)$ with output also in encoded form, in time $\tilde O(z)$ rather than $\Theta(n)$?
- **Completeness variant:** For a fixed encoding family, which fragment of relational algebra is "compression-transparent" (closed under direct evaluation)?
- **Cost variant:** Tight bounds on the multiplicative overhead of compressed execution per operator.

This is the formal core behind "**operate on compressed data**," a defining performance lever of column stores.

## 2. Mathematical Foundations

Treat an encoding as a function $E: R \to \{0,1\}^*$ with a decoder $D$, $D(E(R))=R$. An operator $\theta$ is **directly computable under $E$** if there exists $\hat\theta$ with $\hat\theta(E(R)) = E'(\theta(R))$ for some output encoding $E'$, running in time $g(|E(R)|)$.

Key structure:
- **Order-preserving / RLE:** runs $(v, \ell)$ let SUM/COUNT aggregate over runs in $O(\#\text{runs})$; selection on $v$ filters whole runs.
- **Dictionary encoding:** equality/IN predicates and group-by run on **codes** (integers), deferring dictionary lookup — group-by hashes codes; this connects to **late materialization**.
- **Frame-of-reference / bit-packing:** SIMD predicate evaluation over packed lanes computes selections without unpacking to native width.
- Connections to **compressed pattern matching** and the **algorithmics of compressed text** (computing on SLPs / grammar-compressed strings); aggregation over RLE is the database analogue of computing on run-length-compressed sequences.

This places the problem in the broader theory of **computation over compressed objects** (straight-line programs, grammar compression), where lower bounds are known for some queries.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** C-Store/Vertica, MonetDB/X100 (Vectorwise), DuckDB, ClickHouse, and Apache Arrow/Velox evaluate selections, projections, dictionary-coded group-by, and RLE aggregates directly on encoded data. Abadi et al. (SIGMOD 2006) formalized which operators benefit and introduced the abstraction of a **compressed block API** so the executor stays encoding-agnostic.
- **Theory-SOTA:** For grammar/SLP-compressed inputs, many primitives (random access, pattern matching) admit $O(\mathrm{poly}\log)$-overhead algorithms; some joins/queries are provably hard to speed up on compressed input.

## 4. Upper Bound

- RLE: SUM/COUNT/MIN/MAX/group-by in $O(r)$ where $r=\#$runs $\le n$.
- Dictionary: equality selection, projection, and group-by in $O(z)$ on codes; hash-join on coded keys in $O(z)$ expected when dictionaries are shared/aligned.
- Bit-packed/FOR: range and equality selection via SIMD in $O(z/W)$ word operations.
- For grammar-compressed sequences, aggregation and range queries with $\tilde O(z)$ overhead via balanced SLPs.

## 5. Lower Bound

For **general joins** and predicates that depend on cross-tuple value combinations, no $o(n)$ direct-compressed algorithm can exist when the output is incompressible (information-theoretic: the answer alone has size $\Omega(n)$). For **arbitrary** encodings, deciding direct computability is undecidable in the worst case (it reduces to program equivalence of decoder/operator pairs). On grammar-compressed inputs, certain string/sequence queries are conditionally hard (e.g., fine-grained lower bounds tying compressed pattern problems to SETH/3SUM), implying that not all operators get compression speedups.

## 6. The Gap

**Partially solved**: a clean, near-tight characterization exists for RLE, dictionary, and FOR/bit-packing under selection/projection/aggregation/group-by. The gap is for **multi-column predicates, joins, and arbitrary cascaded encodings**, where we lack a complete dichotomy ("which operator × encoding pairs admit $\tilde O(z)$ evaluation"). A full algebraic completeness theorem remains open.

## 7. Current Research (as of June 2026)

- Extending direct execution to **string-heavy** workloads via FSST and to **nested/Arrow** data *(frontier — verify)*.
- **Compressed joins** on dictionary-shared encodings and learned encodings that preserve order for range predicates *(frontier — verify)*.
- Cross-pollination with grammar-compression theory to obtain provable overhead bounds for analytic operators.
- Groups: CWI (Boncz), MIT/Stanford (Madden, Abadi lineage, Idreos), DuckDB Labs.

## 8. Future Work

- A dichotomy theorem: operator × encoding → $\{\tilde O(z),\ \Omega(n)\}$.
- Closure properties: which encodings are closed under which operators so pipelines stay compressed end-to-end.
- Hardware-conscious bounds (SIMD/GPU) for compressed predicate evaluation.

## 9. Key References

- **[Foundational]** Abadi, Madden, Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)
- **[Foundational]** Stonebraker et al. *C-Store: A Column-oriented DBMS.* VLDB, 2005. — [DBLP](https://dblp.uni-trier.de/rec/conf/vldb/StonebrakerABCCFLLMOORTZ05.html)
- **[SOTA]** Zukowski, Heman, Nes, Boncz. *Super-Scalar RAM-CPU Cache Compression.* ICDE, 2006. — [DOI](https://doi.org/10.1109/ICDE.2006.150)
- **[Survey]** Lohman, Lemire et al. on compressed integer decoding; Lemire, Boytsov. *Decoding Billions of Integers per Second through Vectorization.* Software: Practice and Experience, 2015. — [arXiv](https://arxiv.org/abs/1209.2137)
- **[Survey]** Abadi, Boncz, Harizopoulos, Idreos, Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Column of $n = 12$ values, RLE-encoded as runs $(v, \ell)$:
$$[(3,5),\ (8,4),\ (3,3)]$$
i.e., five 3's, four 8's, three 3's — so $r = 3$ runs while $n = 12$.

**`SUM` directly on the encoding:** $\sum_i v_i \cdot \ell_i = 3\cdot5 + 8\cdot4 + 3\cdot3 = 15 + 32 + 9 = 56$, computed in $O(r) = O(3)$ multiply-adds instead of $O(n) = O(12)$ — the §4 bound.

**Selection $\sigma_{v=3}$:** filters whole runs by value, yielding $[(3,5),(3,3)]$ (8 logical rows) still encoded — output stays compressed, so the operator is *closed* under RLE (§2).

**Why a join can fail:** an equi-join whose output is the full incompressible cross-product has answer size $\Omega(n)$, so no $o(n)$ compressed algorithm exists regardless of input encoding — the information-theoretic lower bound of §5. This is the dichotomy gap (§6): aggregation/selection get $\tilde O(z)$, general joins do not.

---
*Part of the [DBMS Research catalog](../../README.md).*
