# Worst-case-optimal grouped aggregation

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/wco-grouped-aggregation` · **Status:** open

## 1. Problem Statement

Many analytic queries compute an **aggregate over the result of a join** — `SELECT g, SUM(...) FROM R ⋈ S ⋈ T GROUP BY g` — where the join itself is never the desired output and may be enormous. Naively materializing the join then aggregating costs $\Omega(\mathrm{AGM}(Q))$, which can be polynomially larger than both inputs and outputs. The problem: **evaluate grouped aggregates without materializing the join, in time bounded by the size of the inputs and the (much smaller) aggregate output**, ideally matching a worst-case-optimal or width-parameterized bound.

This is the **Functional Aggregate Query (FAQ)** problem: a sum-product expression over a semiring with free (group-by) and bound (summed-out) variables. Variants: (a) single semiring, single aggregate (the core FAQ); (b) multiple aggregates / multiple semirings in one expression (FAQ-AI, `#`-aggregates mixed with `MIN`); (c) the **counting** variant `#`-output (how many join tuples per group) which is `#P`-style hard in general; (d) approximate vs. exact. Decision form: can the aggregate be computed in $\tilde O(N^{w})$ for width parameter $w$? Optimization form: minimize evaluation cost over variable-elimination orders.

## 2. Mathematical Foundations

An **FAQ** over a commutative semiring $(\mathbf{D},\oplus,\otimes)$ is
$$\varphi(\mathbf{x}_F)\;=\;\bigoplus_{\mathbf{x}_B}\;\bigotimes_{e\in E}\psi_e(\mathbf{x}_e),$$
with variables $V=F\cup B$ (free / bound), factors $\psi_e$ indexed by hyperedges $e$, and an elimination order on $B$. This generalizes join ($\oplus=\vee$ over Booleans is the conjunctive query), `COUNT` ($\mathbb{N}$ with $+,\times$), `SUM`, `MAX-product`, and inference in graphical models. The complexity is governed by the **fractional hypertree width** $\mathrm{fhw}$ and the tighter **FAQ-width / submodular width** $\mathrm{subw}$ (Abo Khamis–Ngo–Rudra). The **AGM bound** $\prod_e |R_e|^{x_e}$ bounds intermediate factor sizes; **InsideOut** eliminates one variable at a time, contracting incident factors via a worst-case-optimal join, with cost $\tilde O(N^{\mathrm{faqw}} + \|\text{output}\|)$. **PANDA** (Proof-Assisted eNtropic Degree-Aware) achieves $\mathrm{subw}$ using information-theoretic (Shannon/entropy) inequalities and the chase of the proof sequence.

## 3. State of the Art (SOTA)

**Theory-SOTA:** InsideOut (Abo Khamis–Ngo–Rudra, PODS 2016) solves FAQ in $\tilde O(N^{\mathrm{faqw}})$ + output; PANDA achieves the submodular width $\mathrm{subw}\le\mathrm{fhw}$ for Boolean conjunctive queries and degree-constrained generalizations. For aggregates that are *not* free-connex, the output can be large and lower bounds bite. **Systems-SOTA:** No mainstream engine is provably worst-case-optimal for grouped aggregation; the dominant practical technique is **eager / partial aggregation pushed below joins** (group-by push-down, Yan–Larson; "Eager and Lazy Aggregation," VLDB 1995) and **factorized query processing** (Olteanu–Schleich) which represents intermediate results compactly and aggregates over the factorized form. LMFAO and the F/AC-family (Schleich, Olteanu, Abo Khamis, Ngo, Nguyen) push FAQ-style aggregation into ML feature computation.

## 4. Upper Bound

In the RAM model, FAQ over a single semiring is solvable in
$$\tilde O\!\big(N^{\mathrm{faqw}(Q,\sigma)} + |\text{output}|\big)$$
by InsideOut for the best elimination order $\sigma$, where $\mathrm{faqw}$ generalizes fractional hypertree width to respect free variables. For Boolean/`COUNT` conjunctive queries the bound improves to $\tilde O(N^{\mathrm{subw}})$ via PANDA. **Free-connex** acyclic aggregate queries admit *linear* $\tilde O(N + |\text{output}|)$ evaluation (generalized Yannakakis). Factorized execution achieves the same width bounds while also producing succinct (factorized) representations whose aggregation is linear in the factorized size $\le N^{\mathrm{fhw}}$.

## 5. Lower Bound

Lower bounds are **conditional and fine-grained**. For non-free-connex acyclic queries, no algorithm runs in $O(N + |\text{output}|)$ unless **Boolean matrix multiplication** has truly subcubic combinatorial algorithms (Bagan–Durand–Grandjean–style dichotomy, extended to aggregates). Computing certain grouped aggregates is as hard as detecting triangles, hitting the **combinatorial BMM / $k$-clique** barriers. For counting answers, `#`-versions are `#P`-hard in general. The submodular-width bound $\mathrm{subw}$ is conjectured optimal under hypotheses connecting it to the **min-fill / treewidth** lower bounds and to SETH for specific query families. These hold in RAM / fine-grained models; matching unconditional bounds are open.

## 6. The Gap

The gap is **genuinely open** on two fronts. (1) *Theory:* whether $\mathrm{subw}$ (not just $\mathrm{fhw}$) is achievable for *general semiring aggregates* — PANDA-style $\mathrm{subw}$ is established mainly for Boolean/count CQs; extending it tightly to arbitrary $\oplus/\otimes$ with group-by variables, and proving matching lower bounds, remains unresolved. (2) *Systems:* the theory-optimal algorithms (InsideOut, PANDA) have large polylog/constant overheads and intricate proof-driven plans; **no production engine implements them**, relying instead on heuristic aggregation push-down with no width guarantee. Bridging width-optimal theory to a vectorized, parallel operator is the practical open problem.

## 7. Current Research (as of June 2026)

Active directions: **factorized databases and FAQ for ML** (Olteanu's group, Oxford/Zürich; Abo Khamis/Ngo/Nguyen at RelationalAI) computing aggregates and gradients over joins without materialization; **information-theoretic bounds** refining $\mathrm{subw}$ and degree-aware (PANDA) execution; **WCOJ-integrated aggregation** folding generic-join intersection with semiring contraction in one pass. *(frontier — verify)* 2025–2026 efforts report engine prototypes that execute degree-constrained FAQ plans and approach $\mathrm{subw}$ on cyclic group-by queries, and connections between FAQ and differential/incremental aggregation. People: Ngo, Abo Khamis, Nguyen (RelationalAI), Olteanu, Schleich (Oxford/CWI), Suciu (UW), Re (Stanford).

## 8. Future Work

- A worst-case-optimal grouped-aggregation *operator* (vectorized, parallel) with provable $\mathrm{faqw}$/$\mathrm{subw}$ bounds, not just a research prototype.
- Tight lower bounds for general-semiring FAQ matching PANDA's $\mathrm{subw}$ upper bound.
- Optimizer integration: choosing elimination orders / variable orders cost-based, with cardinality estimation for intermediate factors.
- Mixed-semiring and FAQ-AI (aggregates with additive inequalities) optimality.
- Incremental / streaming maintenance of grouped aggregates over joins.

## 9. Key References

- **[Foundational]** Abo Khamis, Ngo, Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016. — [arXiv](https://arxiv.org/abs/1504.04044)
- **[Foundational]** Abo Khamis, Ngo, Suciu. *What Do Shannon-Type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017. — [DOI](https://doi.org/10.1145/3034786.3056105)
- **[Foundational]** Yan, Larson. *Eager Aggregation and Lazy Aggregation.* VLDB, 1995. — [PDF](https://www.vldb.org/conf/1995/P345.PDF)
- **[SOTA]** Olteanu, Schleich. *Factorized Databases.* SIGMOD Record, 2016. — [DOI](https://doi.org/10.1145/3003665.3003667)
- **[SOTA]** Schleich, Olteanu, Abo Khamis, Ngo, Nguyen. *A Layered Aggregate Engine for Analytics Workloads (LMFAO).* SIGMOD, 2019. — [arXiv](https://arxiv.org/abs/1906.08687)
- **[Foundational]** Marx. *Tractable Hypergraph Properties for Constraint Satisfaction and Conjunctive Queries (submodular width).* JACM, 2013. — [DOI](https://doi.org/10.1145/2535926)

## 10. Worked Example

Query: `SELECT R.a, SUM(T.v) FROM R(a,b) JOIN S(b,c) JOIN T(c,v) GROUP BY R.a`. Tiny instance: $R=\{(a_1,b_1),(a_2,b_1)\}$, $S=\{(b_1,c_1),(b_1,c_2)\}$, $T=\{(c_1,10),(c_2,20)\}$.

**Naive:** materialize the 3-way join. It has $2\times2\times1 = 4$ tuples, then group/sum. Here the join (4 rows) already exceeds the 3-row output.

**InsideOut / eager aggregation:** eliminate bound variables inside-out. First aggregate $T$ over $c$ irrelevant to grouping — but $c$ joins through $S$, so eliminate $v$'s carrier by pushing SUM: precompute per-$c$ contribution $\sigma(c_1)=10,\sigma(c_2)=20$. Eliminate $c$ via $S$: per-$b$ total $\beta(b_1)=\sigma(c_1)+\sigma(c_2)=30$. Eliminate $b$ via $R$: each $(a_i,b_1)$ inherits $\beta(b_1)=30$. Result: $a_1\!\to\!30,\ a_2\!\to\!30$.

No join tuple was ever materialized; cost is $\tilde O(N)$ here (the query is free-connex acyclic), versus $\Omega(\mathrm{AGM})$ for the naive plan.

---
*Part of the [DBMS Research catalog](../../README.md).*
