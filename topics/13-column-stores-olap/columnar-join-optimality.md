# Columnar Join Algorithm Optimality

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/columnar-join-optimality` · **Status:** open

## 1. Problem Statement

Joins dominate OLAP cost. In a column store the join problem is reshaped by three columnar realities: (i) inputs are **columns**, so the join key arrives separately from payload attributes; (ii) **late materialization** lets the join produce *position lists / row-ID pairs* and fetch payload columns only after all filters and joins prune; (iii) execution is **vectorized** (batched, SIMD, cache-conscious) rather than tuple-at-a-time. The problem: design join algorithms — and the *materialization strategy* binding positions to values — that are **optimal** for columnar inputs.

Variants:

- **Single (binary) join, algorithm choice:** hash vs. sort-merge vs. index/invisible-join, tuned for vectorized probes and late binding.
- **Materialization-strategy variant:** when to materialize payloads (early vs. late vs. per-operator), minimizing bytes touched — itself an optimization problem over the plan.
- **Multi-way / worst-case-optimal variant:** for cyclic/many-relation joins, achieve the **AGM** output-size-optimal bound, and integrate it with columnar storage and late materialization.

## 2. Mathematical Foundations

For a multi-way natural join $Q = R_1 \bowtie \cdots \bowtie R_k$, the **AGM bound** (Atserias–Grohe–Marx) gives the worst-case output size $|Q| \le \prod_e |R_e|^{x_e}$ where $\{x_e\}$ is an optimal **fractional edge cover** of the query hypergraph; this is the LP dual of the fractional cover number $\rho^*$. **Worst-case-optimal join (WCOJ)** algorithms — **NPRR** (Ngo, Porat, Ré, Rudra, PODS 2012), **Leapfrog Triejoin** (Veldhuizen, ICDT 2014), and **Generic Join** — run in $\tilde O(\text{AGM bound})$ time, beating any binary-join plan on cyclic queries (e.g. triangle: binary plans need $\Theta(n^2)$, WCOJ $O(n^{3/2})$). For binary joins, the classic radix/partitioned **hash join** is $O(|R|+|S|+|R\bowtie S|)$ and cache-optimal partitioning costs $O((|R|+|S|)\log_{M/B}\ldots)$ in the **external-memory (DAM)** model.

**Late materialization** is an optimization over a *positional* algebra: operators consume/produce position vectors $\subseteq \{1,\dots,n\}$; a value fetch is a gather $\text{col}[pos]$. The cost is bytes-gathered; choosing fetch points is a DAG-scheduling problem. The **invisible join** (Abadi et al., SIGMOD 2008) rewrites star-schema joins into a sequence of predicate-rewrites + a final positional fetch, provably reducing payload materialization. Vectorized probe cost is governed by cache/TLB behavior — partitioned hash join's radix passes minimize cache misses (Manegold–Boncz–Kersten cost model).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Vectorized partitioned **hash join** (MonetDB/X100, VectorWise; Balkesen et al. ICDE 2013 SIMD/NUMA radix join), **invisible join** for star schemas (C-Store/Vertica), Velox/Photon/DuckDB vectorized hash joins with late materialization and runtime filters (semijoin/Bloom pushdown). GPU joins. **Umbra/Hyper** compile join pipelines.
- **Theory-SOTA:** **WCOJ** family — NPRR, Leapfrog Triejoin, Generic Join — and **PANDA** / submodular-width algorithms (Khamis, Ngo, Suciu) for beyond-AGM (degree-aware, functional-dependency-aware) optimality. Hybrid binary+WCOJ optimizers (e.g., free-join, Wang–Willsey–Suciu, SIGMOD 2023) *(frontier — verify)*.

## 4. Upper Bound

Binary hash join: $O(N + |\text{out}|)$ time, $O(N)$ space ($N$ = input size); cache-conscious radix join achieves near-bandwidth-bound throughput with $O(\log_{M/B})$ partition passes. WCOJ: $\tilde O(\prod_e |R_e|^{x_e})$ — **worst-case optimal** w.r.t. AGM, with Generic Join matching it for *every* fractional cover. Submodular-width algorithms (PANDA) further reduce to $\tilde O(N^{\mathrm{subw}(Q)})$, the best-known general upper bound. Late materialization upper-bounds payload bytes touched by $O(|\text{surviving positions}| \times \text{payload width})$ rather than full-column width.

## 5. Lower Bound

The AGM bound is a **matching lower bound** on *output size*, so any join enumerating the result needs $\Omega(\text{AGM})$ time — WCOJ is optimal in this sense for full enumeration. For **detecting/counting** (e.g., triangle detection) the conjectured fine-grained barriers apply: triangle detection in $O(n^{3-\delta})$ would refute popular hardness assumptions; Boolean-matrix-multiplication / **3SUM**-style and **SETH**-conditional lower bounds rule out generic sub-polynomial improvements for many join-related problems. In the **external-memory** model, partitioned join is I/O-optimal $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$. The *optimal materialization-strategy* decision (early vs. late vs. mixed across a plan) is plan-dependent and, as a joint optimization with join ordering, is NP-hard (join ordering already is).

## 6. The Gap

**Genuinely open.** Per-query optimality is understood in isolation (AGM/WCOJ for output, hash-join for binary, I/O bounds for external memory), but the **integration** is not: there is no theory delivering a *single* algorithm that is simultaneously WCOJ-optimal, late-materialization-optimal, vectorization/cache-optimal, and chosen optimally by a cost-based planner over real columnar storage. The submodular-width upper bound is not matched by a comparably tight conditional lower bound for all queries, and the WCOJ-vs-binary crossover under columnar late materialization lacks a closed cost model.

## 7. Current Research (as of June 2026)

- **Free Join** and hybrid binary/WCOJ execution unifying the two paradigms in vectorized engines (Wang, Willsey, Suciu) *(frontier — verify)*.
- WCOJ inside production columnar/vectorized engines (DuckDB, Umbra) with column-aware late materialization *(frontier — verify)*.
- **PANDA / submodular-width** practical realizations and degree-aware joins; GPU/SIMD WCOJ kernels.

## 8. Future Work

- A unified cost model + lower bound for late-materialized, vectorized WCOJ choosing materialization points optimally.
- Tight conditional lower bounds matching submodular-width for general conjunctive queries.
- Adaptive runtime switching between hash, sort-merge, and WCOJ per pipeline under observed skew.

## 9. Key References

- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 / SICOMP, 2013.
- **[Foundational]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018.
- **[SOTA]** T. L. Veldhuizen. *Leapfrog Triejoin: A Simple, Worst-Case Optimal Join Algorithm.* ICDT, 2014.
- **[SOTA]** D. Abadi, D. Myers, D. DeWitt, S. Madden. *Materialization Strategies in a Column-Oriented DBMS.* ICDE, 2007; and *Column-Stores vs. Row-Stores (invisible join).* SIGMOD, 2008.
- **[SOTA]** C. Balkesen, J. Teubner, G. Alonso, M. T. Özsu. *Main-Memory Hash Joins on Multi-Core CPUs.* ICDE, 2013.
- **[Survey]** M. Abo Khamis, H. Q. Ngo, D. Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
