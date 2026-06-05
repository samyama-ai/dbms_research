# Set operations and multiset semantics complexity

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/set-operation-complexity` · **Status:** partially-solved

## 1. Problem Statement

SQL's `INTERSECT`, `UNION`, `EXCEPT` come in **set** (`DISTINCT`) and **multiset** (`ALL`) flavors, and real query plans constantly compute them implicitly (e.g., during deduplication, grouped distinct-aggregation, and semijoin reduction). Under **bag (multiset) semantics** each tuple carries a multiplicity, and the operators are defined by arithmetic on multiplicities — $\min$ for `INTERSECT ALL`, sum for `UNION ALL`, truncated subtraction for `EXCEPT ALL`. The problem: *what are the optimal time and space bounds for these operators, output-sensitively and in the presence of duplicates, and how do those bounds change between set and multiset semantics, sorted vs. unsorted inputs, and exact vs. approximate counting?*

Variants: (a) **decision** (is the intersection nonempty? are two bags equal?); (b) **construction/optimization** (produce the result bag with multiplicities, minimizing comparisons/probes); (c) **counting** (just the result *cardinality* or distinct-count, e.g. for `COUNT(DISTINCT ...)`); (d) **streaming/approximate** distinct and set-membership under bounded memory; (e) **adaptive** intersection of many sorted lists where instance difficulty varies.

## 2. Mathematical Foundations

A bag over domain $U$ is a function $m:U\to\mathbb{Z}_{\ge 0}$. Operators: $(A\cap_{\text{bag}}B)(x)=\min(m_A(x),m_B(x))$; $(A\cup_{\text{bag}}B)(x)=m_A(x)+m_B(x)$ for `UNION ALL`; $(A\setminus_{\text{bag}}B)(x)=\max(0,m_A(x)-m_B(x))$. Set semantics applies the support indicator $\mathbf{1}[m(x)>0]$. The **bag relational algebra** (Dayal–Goodman–Katz; Albert) gives equivalences and the laws that hold (e.g. $\cup_{\text{bag}}$ is commutative/associative but absorption and idempotence *fail*), which is what makes multiset query rewriting subtler than set algebra. Lower bounds rest on **comparison-tree** and **adaptive-analysis** frameworks (encoding/certificate complexity, Demaine–López-Ortiz–Munro) and, for distinct-counting, on **communication complexity** and **information theory** (the $\Omega(\epsilon^{-2})$ sketch-size barriers). Set intersection nonemptiness connects to the **Orthogonal Vectors / SETH** fine-grained hierarchy.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Sorted multi-set intersection is solved by *adaptive* algorithms whose cost matches an instance-optimal certificate/gap-encoding bound (Barbay–Kenyon; Demaine–López-Ortiz–Munro), $O(\sum_i g_i \log(\ldots))$ where $g_i$ is the "gap" structure. Distinct counting is solved up to constants by **HyperLogLog** (Flajolet et al.) and the optimal **$F_0$ sketch** of Kane–Nelson–Woodruff achieving $O(\epsilon^{-2}+\log n)$ space. **Systems-SOTA:** Engines implement set ops via sort-merge or hash-aggregate; multiplicity is tracked with running counters. Vectorized hash tables (DuckDB, Velox, Photon) compute `INTERSECT`/`EXCEPT` by hashing one side with counts and probing the other, taking $\min$/subtracting per group. SIMD sorted-set intersection (roaring bitmaps, Lemire) dominates for dense integer keys.

## 4. Upper Bound

For two unsorted bags of sizes $n,m$: hash-based set/multiset intersection, union, and difference run in $O(n+m)$ expected time and $O(\min(n,m))$ space (hash the smaller, probe and arithmetic-combine multiplicities), in the RAM model with hashing. For sorted inputs: $O(n+m)$ deterministic merge; adaptive variants achieve **instance-optimal** $O(\sum \log g_i)$ comparisons for $k$-way sorted intersection. Distinct cardinality of the result: $(1\pm\epsilon)$ approximation in $O(\epsilon^{-2}+\log n)$ bits (optimal $F_0$). Exact result-with-multiplicities is output-sensitive: $O(n+m+|\text{out}|)$.

## 5. Lower Bound

Any comparison-based two-set intersection needs $\Omega(n+m)$ in the worst case; for *sorted* $k$-way intersection the adaptive lower bound matches the certificate/gap encoding (instance-optimal — tight). Set-disjointness (decision) has $\Omega(n)$ **communication complexity** (Kalyanasundaram–Schnitger; Razborov), giving distributed/streaming lower bounds. Approximate $F_0$ requires $\Omega(\epsilon^{-2}+\log n)$ bits (Indyk–Woodruff; Kane–Nelson–Woodruff) — tight. Deciding whether two sets of $d$-dim 0/1 vectors share an "orthogonal/disjoint" pair is **OV-hard**, so certain batched set-intersection problems have no $O(n^{2-\delta})$ algorithm under **SETH**.

## 6. The Gap

For the core single-pair operators (sorted and hashed), bounds are **closed**: $\Theta(n+m)$ time, instance-optimal for adaptive sorted intersection, optimal sketches for distinct-counting — hence *partially-solved* overall. The genuinely open pieces are: (a) tight bounds for **many-way** multiset intersection/union under skew and partial sorting with payloads; (b) exact distinct-count lower-space tradeoffs beyond approximation; (c) batched/joined set-operation workloads where the SETH/OV barrier may or may not bite given structure. The arithmetic-on-multiplicities does not change asymptotics but the constants and vectorizability differ, and a clean cost model unifying set/bag/approximate variants is still missing.

## 7. Current Research (as of June 2026)

(1) **Vectorized & SIMD set ops** — roaring bitmaps, GPU multi-set intersection, and compressed-domain `INTERSECT`/`EXCEPT` (Lemire and collaborators). (2) **Sketch-based approximate set operations** — mergeable HLL/theta sketches for `INTERSECT`/`UNION` cardinality at scale (Apache DataSketches), with error bounds for chained operations. (3) **Instance-optimal / learned intersection** ordering of many posting lists. (4) **Differentially private set operations** and private set intersection feeding query results. Groups: Lemire (UQAM), the DataSketches/Yahoo lineage, Woodruff (CMU) on sketch lower bounds. *(frontier — verify)* 2025–2026 work reports learned set-intersection schedulers beating classic adaptive bounds on real posting-list distributions in expectation.

## 8. Future Work

- Tight time/space bounds for $k$-way **multiset** intersection/difference under skew with payload columns.
- Composable error analysis for chains of approximate set operations (theta-sketch algebra).
- A unified cost model spanning set/bag/exact/approximate that an optimizer can use to pick the operator implementation.
- Hardware-conscious (SIMD/GPU) bag-difference and `EXCEPT ALL` with provable throughput.
- Fine-grained classification of which batched set-operation workloads are OV/SETH-hard vs. tractable.

## 9. Key References

- **[Foundational]** Dayal, Goodman, Katz. *An Extended Relational Algebra with Control over Duplicate Elimination.* PODS 1982. — [DOI](https://doi.org/10.1145/588111.588132)
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* AofA 2007. — [DMTCS](https://dmtcs.episciences.org/3545)
- **[SOTA]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** Barbay, Kenyon. *Adaptive Intersection and t-Threshold Problems.* SODA 2002. — [DBLP](https://dblp.org/rec/conf/soda/BarbayK02.html)
- **[SOTA]** Demaine, López-Ortiz, Munro. *Adaptive Set Intersections, Unions, and Differences.* SODA 2000. — [DBLP](https://dblp.org/rec/conf/soda/DemaineLM00.html)
- **[SOTA]** Lemire, Boytsov, Kurz. *SIMD Compression and the Intersection of Sorted Integers.* Software: Practice & Experience, 2016. — [DOI](https://doi.org/10.1002/spe.2326)
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases* (bag semantics chapters). Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Two bags over $U=\{a,b,c,d\}$ with multiplicities $m_A=\{a{:}3,\,b{:}1,\,c{:}2\}$ and
$m_B=\{a{:}1,\,c{:}5,\,d{:}4\}$.

- **`INTERSECT ALL`** ($\min$): $a{:}\min(3,1){=}1$, $c{:}\min(2,5){=}2$; $b,d$ drop (other side $0$). Result $\{a{:}1,\,c{:}2\}$.
- **`UNION ALL`** (sum): $\{a{:}4,\,b{:}1,\,c{:}7,\,d{:}4\}$.
- **`EXCEPT ALL`** $A\setminus B$ (truncated minus): $a{:}\max(0,3{-}1){=}2$, $b{:}1$, $c{:}\max(0,2{-}5){=}0$. Result $\{a{:}2,\,b{:}1\}$.

Algorithm: hash the smaller bag $A$ (3 distinct keys) into a counter table, then probe $B$'s
keys and apply the per-key arithmetic — $O(|A|+|B|)$ expected time, $O(\min)$ space, matching
the section-4 upper bound.

Set semantics differs: `INTERSECT` (`DISTINCT`) ignores counts, returning support
$\{a,c\}$. Note idempotence fails for bags — $A \cup_{\text{bag}} A$ doubles every
multiplicity rather than returning $A$ — which is exactly why multiset rewriting is subtler
than Boolean set algebra.

---
*Part of the [DBMS Research catalog](../../README.md).*
