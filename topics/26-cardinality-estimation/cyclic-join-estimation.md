# Cardinality Estimation for Cyclic Joins

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/cyclic-join-estimation` · **Status:** open

## 1. Problem Statement

Given a (multi-way) natural-join query $Q$ whose hypergraph contains cycles — e.g. the triangle $R(A,B) \bowtie S(B,C) \bowtie T(A,C)$ — and per-relation statistics (sizes, degrees, distinct counts, samples, sketches), estimate $|Q|$, the number of output tuples. Cyclic queries are exactly where the **tree/acyclic** assumptions underlying classical optimizers (independence + uniformity propagated along a join tree) break down, because cyclicity creates correlations no single join edge captures.

Variants:
- **Estimation variant:** produce $\hat{c} \approx |Q|$ with small relative error.
- **Bounding variant:** produce a provable upper bound $U \ge |Q|$ (for worst-case-optimal planning).
- **Counting/decision flavors:** exact counting of homomorphisms (e.g. triangle counting) is the hard limit case.

The output size of a single cyclic query can be polynomially larger or smaller than any acyclic relaxation predicts, so per-edge selectivity multiplication is systematically biased.

## 2. Mathematical Foundations

Model $Q$ as a join hypergraph $H = (V, E)$ where vertices are attributes and hyperedges are relations. The **AGM bound** (Atserias–Grohe–Marx) gives a tight worst-case output-size upper bound:
$$|Q| \le \prod_{F \in E} |R_F|^{\,x_F}, \qquad \text{where } \mathbf{x} \text{ is a fractional edge cover of } H,$$
minimized over fractional edge covers; the optimum exponent is the **fractional edge cover number** $\rho^*(H)$. For the triangle, $x_F = 1/2$ each gives $|Q| \le \sqrt{|R||S||T|}$.

Refinements use **entropy / information theory**: the tight bound under degree (functional-dependency and cardinality) constraints is the **polymatroid bound**, solving a linear program over Shannon-type entropy inequalities (Gottlob–Lee–Valiant–Valiant; Abo Khamis–Ngo–Suciu "What do Shannon-type inequalities tell us about join sizes"). The **chase** and tree decompositions (fractional hypertree width $\mathsf{fhw}$, submodular width $\mathsf{subw}$) govern algorithmic tractability. Average-case estimation instead models data statistically; bound-based estimation is worst-case.

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- **AGM bound** (FOCS 2008) and **worst-case-optimal join** algorithms NPRR / **Generic Join** / **Leapfrog Triejoin** (Ngo–Porat–Ré–Rudra PODS 2012; Veldhuizen) that run in time $O(\text{AGM bound})$.
- **Degree-aware / polymatroid bounds (PANDA)** (Abo Khamis–Ngo–Suciu, PODS 2017) tightening AGM with statistics.
- **Submodular width** algorithms (Marx) for the finest tractability frontier.

**Systems-SOTA:**
- **Pessimistic cardinality estimators** using AGM-style bounds with sketches (Cai–Balazinska–Suciu, SIGMOD 2019) — provable upper bounds usable by an optimizer.
- **Bound-sketch / degree-sequence** methods; **SafeBound** (Deeds et al., SIGMOD 2023).
- **Learned multi-relation estimators** (NeuroCard, FactorJoin, Wu et al.) attempt cyclic correlation but degrade on hard cycles.

## 4. Upper Bound

For provable output-size bounds: the AGM bound is computable in time polynomial in the query (solving the cover LP) and is **tight in the worst case** over all databases with the given relation sizes. With degree/FD constraints, the polymatroid (PANDA) bound is tighter and remains LP-computable. Algorithmically, generic-join computes $Q$ in $\tilde{O}(\text{AGM})$ time and $O(\mathsf{subw})$-style bounds give the best general tractability. For *average-case* estimation, sampling-based estimators (e.g. **wander join** / random-walk online aggregation, Li et al. SIGMOD 2016) give unbiased estimates with variance bounds.

## 5. Lower Bound

Exact counting for cyclic patterns is hard: counting triangles / $k$-cliques is conjectured to require $n^{\omega}$-type time, and under SETH/3SUM many subgraph-counting problems have fine-grained lower bounds. The AGM bound is **information-theoretically unimprovable** given only relation sizes — there exist databases meeting it, so no estimator using only sizes can do better in the worst case. Detecting whether $|Q|>0$ for cyclic queries inherits subgraph-isomorphism hardness. Sampling estimators face high-variance lower bounds when the output is dominated by few heavy join keys (skew).

## 6. The Gap

For **worst-case bounds**, the gap is essentially closed: AGM/polymatroid bounds are tight given the available statistics, and matching WCO algorithms exist. The **open** problem is **average-case / instance-optimal estimation**: closing the often orders-of-magnitude gap between a (correct but loose) upper bound and the true cardinality for real, skewed, correlated data. What would close it: estimators that interpolate provably between worst-case bounds and data-dependent refinements (richer statistics — degree sequences, conditional sketches) with quantified error, plus a theory of which statistics suffice for which cycle structures.

## 7. Current Research (as of June 2026)

- **Tighter degree-aware bounds** and their use as optimizer-safe estimates (Suciu, Ngo, Abo Khamis lineage; SafeBound follow-ups) *(frontier — verify)*.
- **FactorJoin** and factorized learned estimators combining bounds with learned corrections.
- **Sketch-based join-size estimation** with correlation awareness (Count-Min/AGMS for multi-way joins).
- Information-theoretic accounting of **what statistics are worth collecting** for cyclic queries.

## 8. Future Work

- Provable interpolation between AGM upper bounds and unbiased average-case estimates.
- Robust handling of skew and heavy hitters in cyclic-join estimation.
- Composable statistics that survive both cyclicity and predicates.
- Integrating WCO-bound reasoning natively into cost-based optimizers.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008.
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 (JACM 2018).
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019.
- **[SOTA]** Deeds, Suciu, Balazinska, et al. *SafeBound: A Practical System for Generating Cardinality Bounds.* SIGMOD, 2023.
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
