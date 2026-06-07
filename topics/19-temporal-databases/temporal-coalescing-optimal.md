---
id: 19-temporal-databases/temporal-coalescing-optimal
title: "Optimal Temporal Coalescing Algorithms"
topic: 19-temporal-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal Temporal Coalescing Algorithms

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-coalescing-optimal` · **Status:** partially-solved

## 1. Problem Statement
Given a temporal relation in which each tuple carries a value (the non-temporal attributes) and an associated time period (an interval over a discrete or dense time domain), *coalescing* merges every maximal run of value-equivalent tuples whose periods are adjacent (meet) or overlap into a single tuple spanning the union of those periods. The output is the unique **canonical minimal representation**: for each distinct value, a set of maximal disjoint, non-adjacent maximal periods.

Variants:
- **Optimization (computational):** produce the coalesced relation with minimum time/space.
- **Decision:** is a given relation already coalesced (a normal-form test)?
- **Incremental/maintenance:** maintain coalescing under insertions, deletions, and updates.
- **Distributed/parallel:** coalesce a partitioned relation with minimum communication or rounds.

The subtlety is that coalescing is *not* a per-tuple operation: it requires grouping by value and then a per-group interval union, and naive SQL formulations (recursive or correlated-subquery based) are quadratic or worse.

## 2. Mathematical Foundations
Let the time domain be a linearly ordered set $T$ (e.g. $\mathbb{Z}$ or $\mathbb{Q}$). A period is $[t_s, t_e)$ with $t_s < t_e$. Two periods $p, q$ are *mergeable* if they overlap or **meet** (Allen's relations `overlaps`, `during`, `starts`, `finishes`, `equals`, `meets`). For a fixed value $v$, coalescing computes the *union of intervals*, the classic computational-geometry problem solvable by sorting endpoints and a single sweep in $O(k \log k)$ for $k$ intervals, or $O(k)$ if already endpoint-sorted.

The full operator is $\textsf{coalesce}(R) = \bigcup_{v} \{ (v, p) : p \in \textsf{IntervalUnion}(\{ q : (v,q)\in R\}) \}$. Formally coalescing realizes the *temporal normal form* in which no two tuples are value-equivalent with mergeable periods; it is the analogue of duplicate elimination lifted to the temporal dimension. Snodgrass's TSQL2 and the SQL:2011 period model both define it as the semantic basis for temporal projection and set difference. The lower-bound structure rests on a reduction from sorting/element-distinctness in the comparison model.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Coalescing reduces to grouping plus interval union. With a comparison-based sort the whole relation coalesces in $O(n \log n)$; with integer/bounded time domains, radix-style sorting gives $O(n)$ expected. Böhlen, Snodgrass, and Soo (VLDB 1996) gave the definitive treatment of coalescing semantics and a battery of SQL implementation strategies.

**Systems-SOTA:** SQL:2011 period predicates plus window functions yield a standard "gaps-and-islands" formulation; engines such as Teradata, MariaDB (system-versioned tables), and PostgreSQL (via `range_agg`/`multirange` since PG 14) coalesce using sort-merge over `range` types. Vectorized columnar engines push the interval-union sweep into a single pass after partitioned sort.

## 4. Upper Bound
Best-known upper bound is $O(n \log n)$ time, $O(n)$ space in the **comparison/RAM model**: stable-sort by $(\text{value}, t_s)$ then a linear sweep coalescing within each value group. With integer time and bounded universe, $O(n)$ expected via radix sort. The interval-union subroutine is optimal at $O(k \log k)$ per group in the comparison model and $O(k)$ given sorted input. Parallel: $O(\log n)$ depth, $O(n \log n)$ work in the PRAM/EREW model via parallel sort plus segmented prefix-max scan.

## 5. Lower Bound
Coalescing is at least as hard as **element distinctness** and **sorting**: from any multiset one can build a single-value relation whose coalesced output reveals the sorted distinct order, giving an $\Omega(n \log n)$ comparison-model lower bound (and the $\Omega(n \log n)$ algebraic-decision-tree bound for element distinctness). In integer models with $O(n)$ space the bound drops, matching radix sort. No super-linearithmic hardness is known; the operation is *not* believed to be 3SUM- or APSP-hard.

## 6. The Gap
For the batch problem the gap is **closed** up to model assumptions: $\Theta(n \log n)$ in the comparison model, $\Theta(n)$ with integer time and linear space. The genuinely open frontier is **incremental coalescing**: maintaining the canonical form under a stream of period insertions/deletions with sub-linear amortized cost per update, and **distributed coalescing** with provably minimal communication when value groups straddle partitions. Tight bounds for the dynamic variant are not established.

## 7. Current Research (as of June 2026)
Active threads: (i) pushing coalescing into vectorized/columnar execution and avoiding materialization via streaming multiranges; (ii) coalescing semantics interacting with SQL:2011 application-time tables in MariaDB/Teradata; (iii) GPU and SIMD interval-union sweeps. Dignös, Böhlen, and Gamper continue work on the broader *temporal alignment/splitting* primitives that subsume coalescing in their reduction-based temporal algebra. *(frontier — verify)* Recent vectorized-engine papers report near-memory-bandwidth coalescing throughput using partitioned merge plus segmented scans.

## 8. Future Work
- Provably optimal **dynamic** coalescing with worst-case sub-linear updates.
- Communication-optimal distributed coalescing and its lower bound.
- Coalescing over **indeterminate** / probabilistic periods and over dense (rational/real) time with exactness guarantees.
- Cost-based optimizer integration so coalescing is reordered with joins and aggregation rather than treated as a post-pass.

## 9. Key References
- **[Foundational]** Böhlen, M., Snodgrass, R., Soo, M. *Coalescing in Temporal Databases.* VLDB, 1996. — [PDF](https://www.vldb.org/conf/1996/P180.PDF)
- **[Foundational]** Snodgrass, R. T. *Developing Time-Oriented Database Applications in SQL.* Morgan Kaufmann, 2000. — [PDF](https://www2.cs.arizona.edu/~rts/tdbbook.pdf)
- **[SOTA]** Dignös, A., Böhlen, M., Gamper, J. *Temporal Alignment.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213886)
- **[Survey]** Kulkarni, K., Michels, J.-E. *Temporal Features in SQL:2011.* SIGMOD Record, 2012. — [DOI](https://doi.org/10.1145/2380776.2380786)
- **[Foundational]** Preparata, F., Shamos, M. *Computational Geometry: An Introduction.* Springer, 1985. (interval-union sweep, element-distinctness bounds) — [DOI](https://doi.org/10.1007/978-1-4612-1098-6)

## 10. Worked Example

Coalesce a salary-history relation `Sal(emp, period)` (value $=$ emp; periods half-open $[t_s,t_e)$):

| emp | period |
|---|---|
| Ann | $[1,4)$ |
| Ann | $[4,7)$ |
| Ann | $[9,11)$ |
| Bob | $[2,5)$ |
| Bob | $[3,6)$ |

**Step 1 — group + stable-sort** by $(\text{emp}, t_s)$: Ann's rows in order $[1,4),[4,7),[9,11)$; Bob's $[2,5),[3,6)$.

**Step 2 — per-group sweep**, merging while the next start $\le$ current end (they *meet* or *overlap*):

- Ann: $[1,4)$ then $[4,7)$ — $4\le 4$ they **meet**, merge to $[1,7)$. Next $[9,11)$ has $9>7$, gap, so emit $[1,7)$ and start $[9,11)$.
- Bob: $[2,5)$ then $[3,6)$ — $3\le 5$ they **overlap**, merge to $[2,6)$.

**Result (canonical minimal form):**

| emp | period |
|---|---|
| Ann | $[1,7)$ |
| Ann | $[9,11)$ |
| Bob | $[2,6)$ |

No two value-equal tuples now have mergeable periods. Cost is dominated by the sort: $O(n\log n)$ comparisons, then one linear sweep. The $\Omega(n\log n)$ lower bound follows by building a single-emp relation from any multiset of $n$ point-intervals $[x_i,x_i{+}1)$ — the coalesced output lists the distinct $x_i$ in sorted order, solving element distinctness / sorting.

---
*Part of the [DBMS Research catalog](../../README.md).*
