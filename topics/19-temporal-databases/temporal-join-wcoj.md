# Worst-Case-Optimal Temporal Joins

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-join-wcoj` · **Status:** open

## 1. Problem Statement
A **temporal join** combines tuples whose time periods satisfy an interval predicate — most importantly **overlap** (Allen's `overlaps`/`intersects`), but also `meets`, `contains`, `equals`, and `before/after`. The open problem is to design join algorithms whose running time meets an **AGM-style worst-case-optimal (WCOJ) bound** that simultaneously accounts for the equi-join attributes *and* the interval-overlap predicate: i.e., time proportional (up to polylog factors) to input size plus the largest possible output over all databases consistent with the given statistics.

Variants:
- **Binary interval-overlap join** (two relations, overlap predicate, possibly plus an equi-key).
- **Multiway temporal join** (a conjunction of overlap and equality predicates — a temporal analogue of the WCOJ triangle/cycle setting).
- **Decision/counting:** report all overlapping pairs vs. count them vs. detect any overlap.

Overlap is not an equality predicate, so classical WCOJ theory (which is built for equi-joins) does not directly apply; this is the crux of why the problem is open.

## 2. Mathematical Foundations
The **AGM bound** (Atserias, Grohe, Marx) bounds the output of a natural (equi-)join $Q$ by $\prod_e |R_e|^{x_e}$ where $\{x_e\}$ is an optimal **fractional edge cover** of the query hypergraph; **Worst-Case-Optimal Join** algorithms (NPRR / LeapFrog Triejoin / Generic-Join of Ngo, Porat, Ré, Rudra) run in $\tilde{O}(\text{AGM}(Q))$ time, beating any pairwise plan on cyclic queries.

For temporal joins the predicate is $[a_s,a_e) \cap [b_s,b_e) \neq \emptyset \iff a_s < b_e \wedge b_s < a_e$ — a conjunction of two **inequalities**, placing it in the realm of *inequality/theta joins* and **interval-overlap** geometry rather than equality. Relevant theory: output-sensitive interval-overlap reporting (sweepline + interval trees) runs in $O(n \log n + k)$ for output size $k$; the **stabbing**/segment structures give $O(\log n + k)$ per query. The challenge is a unified bound that interpolates between the geometric output-sensitive regime and the AGM combinatorial regime when overlap is mixed with equi-keys and chained across $\geq 3$ relations.

## 3. State of the Art (SOTA)
**Theory-SOTA:** For binary overlap joins, plane-sweep / endpoint-sort algorithms are output-optimal at $O(n \log n + k)$. For multiway and "band"/inequality joins, recent work generalizes WCOJ to inequalities — Khamis et al.'s **PANDA** and functional-aggregate-query (FAQ) framework, and "Joins via Geometric Resolutions" / tetris-style algorithms, give worst-case-optimal results for queries with inequality predicates, which subsumes some temporal-overlap conjunctions, but tight bounds specifically parameterized by interval structure remain partial.

**Systems-SOTA:** Disjoint-interval-partition and **Overlap Interval Partition (OIP) join** (Dignós, Böhlen, Gamper, SIGMOD 2014), sort-merge/forward-scan temporal joins, and the **Timeline Index** (SAP HANA, SIGMOD 2013) are the practical state of the art; vectorized engines and DuckDB-style range joins handle overlap via sorted-band sweeps.

## 4. Upper Bound
- **Binary overlap join:** $O(n \log n + k)$ time, $O(n)$ space (sweepline + interval tree), output-optimal in the comparison/RAM model.
- **Multiway with inequalities:** PANDA / geometric-resolution algorithms achieve $\tilde{O}(\text{output} + \text{poly} \cdot N)$ bounds for queries reducible to the FAQ/inequality framework, i.e. worst-case-optimal up to polylog and the degree of the query, in the RAM model. A clean closed-form AGM-style bound *specialized to overlap conjunctions with equi-keys* is not yet established — only subsumption by the more general (and looser) inequality-FAQ bounds.

## 5. Lower Bound
- Binary overlap reporting has an $\Omega(n \log n + k)$ comparison-model lower bound (sorting reduction).
- For multiway, the AGM/fractional-cover bound is the information-theoretic output lower bound any algorithm must pay; matching it for inequality predicates is conjectured hard in general.
- Detecting a single overlap relates to interval intersection, but the *3-relation chained overlap* and "temporal triangle" detection are suspected to inherit **3SUM**- or **APSP**-conditional hardness from the inequality/all-pairs structure *(frontier — verify)*; no unconditional super-linear bound is known.

## 6. The Gap
For **binary** overlap the gap is closed ($\Theta(n \log n + k)$). For **multiway temporal joins** there is a genuine gap: the only matching-bound algorithms come from the general inequality/FAQ machinery, whose bounds are not tight when specialized to overlap-plus-equality, and whose constants/log-factors are large. Closing the gap requires either an AGM-style bound parameterized by interval geometry (a "temporal fractional cover") with a matching algorithm, or a conditional lower bound proving the general inequality bound is best possible for overlap conjunctions.

## 7. Current Research (as of June 2026)
- WCOJ-for-inequalities and FAQ refinements (Khamis, Ngo, Rudra, Suciu and collaborators); "comparison joins" and bounds beyond worst case (degree-aware, certificate complexity).
- Practical multiway temporal joins in vectorized/columnar engines and on GPUs; range-join optimization in DuckDB and cloud warehouses.
- Bozen-Bolzano group on overlap-interval-partition refinements and sequenced multiway joins.
- *(frontier — verify)* Emerging attempts to define a temporal analogue of the AGM bound using interval-VC-dimension / shattering arguments to capture overlap output size.

## 8. Future Work
- A tight, overlap-specific worst-case output bound and matching multiway algorithm.
- Conditional (3SUM/APSP/SETH) lower bounds for chained temporal overlap joins.
- Beyond-worst-case and adaptive guarantees (instance-optimality, certificate complexity) for temporal joins.
- I/O-optimal external-memory and parallel/distributed WCOJ temporal joins.

## 9. Key References
- **[Foundational]** Ngo, H. Q., Porat, E., Ré, C., Rudra, A. *Worst-Case Optimal Join Algorithms.* JACM, 2018 (PODS 2012). — [DOI](https://doi.org/10.1145/3180143)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins.* SIAM J. Computing, 2013 (FOCS 2008). — [DOI](https://doi.org/10.1137/110859440)
- **[SOTA]** Abo Khamis, M., Ngo, H. Q., Rudra, A. *FAQ: Questions Asked Frequently.* PODS, 2016. — [arXiv](https://arxiv.org/abs/1504.04044)
- **[SOTA]** Dignós, A., Böhlen, M., Gamper, J. *Overlap Interval Partition Join.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2612175)
- **[SOTA]** Kaufmann, M. et al. *Timeline Index: A Unified Data Structure for Processing Queries on Temporal Data in SAP HANA.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465293)
- **[Survey]** Ngo, H. Q. *Worst-Case Optimal Join Algorithms: Techniques, Results, and Open Problems.* PODS (tutorial), 2018. — [arXiv](https://arxiv.org/abs/1803.09930)

## 10. Worked Example

**Binary overlap join.** $R=\{[1,4),[6,9)\}$, $S=\{[2,3),[3,7),[8,10)\}$. Overlap predicate $a_s<b_e \wedge b_s<a_e$.

Plane-sweep: sort all $2(|R|+|S|)=10$ endpoints, sweep left-to-right maintaining the set of currently "open" intervals from each side; emit a pair when an interval opens while an opposite-side interval is open.

- $[1,4)$ open. $[2,3)$ opens → pair $([1,4),[2,3))$. $[3,7)$ opens while $[1,4)$ open → pair $([1,4),[3,7))$.
- $[1,4)$ closes at 4; $[3,7)$ still open. $[6,9)$ opens while $[3,7)$ open → pair $([6,9),[3,7))$. $[8,10)$ opens while $[6,9)$ open → pair $([6,9),[8,10))$.

Output $k=4$ pairs in $O(n\log n + k)$ — the sort dominates, matching the $\Omega(n\log n + k)$ lower bound, so binary overlap is closed.

**Why multiway is open.** Chain $R(x)\bowtie S(x)\bowtie T(x)$ where all three must mutually overlap: this is a *temporal triangle*. The AGM equi-join bound (fractional cover $=3/2$, giving $\sqrt{|R||S||T|}$) does not directly apply because overlap is two inequalities, not equality — so no closed-form WCOJ output bound parameterized by interval geometry is yet known.

---
*Part of the [DBMS Research catalog](../../README.md).*
