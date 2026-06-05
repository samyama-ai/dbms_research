# Worst-Case-Optimal Joins from Degree Constraints

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/wcoj-degree-constraints` · **Status:** partially-solved

## 1. Problem Statement

Given a (natural/conjunctive) join query $Q$ over relations whose sizes and **degree/cardinality constraints** (and functional dependencies) are known, determine the **tight worst-case output size** $\mathrm{OUT}^{\star}$ and an algorithm that runs in time $\tilde{O}(\mathrm{OUT}^{\star} + \mathrm{IN})$ — i.e., **worst-case optimal** under those statistics.

The **AGM bound** solves this when only relation *cardinalities* are known. The richer problem, **partially solved**, is:

- **Bounding (optimization/counting):** compute the *best* output-size upper bound given a set of degree constraints $\{ \deg(B \mid A) \le N_{A,B} \}$, FDs, and cardinalities — strictly tighter than AGM.
- **Algorithmic (matching):** design a join algorithm whose runtime matches that refined bound on every input.
- **Variants:** Boolean evaluation, full enumeration, aggregation (FAQ/sum-product), and the bound's behavior under *acyclic* vs *cyclic* structure.

## 2. Mathematical Foundations

For a join with hypergraph $H=(V,E)$ and relation sizes $|R_e|=N_e$, the **AGM bound** is
$$|Q| \;\le\; \prod_{e\in E} N_e^{\,x_e}, \qquad \text{minimized over fractional edge covers } x \;\big(\textstyle\sum_{e \ni v} x_e \ge 1\big),$$
and is **tight** (Atserias–Grohe–Marx 2008). Its dual/log form is an LP; the optimum is $\rho^{\star}(H)$, the fractional edge-cover number.

With **degree constraints** the bound generalizes to an **information-theoretic / entropy** program. Output size is bounded by $2^{\max_h H(\text{all vars})}$ where $h$ ranges over **polymatroids** (or the smaller cone of *entropic* vectors) satisfying the constraints
$$h(B\mid A) \le \log N_{A,B}.$$
This is the **entropic / Shannon-flow bound**; using polymatroids gives the **polymatroid bound** computed by a linear program over **submodular** functions. The matching algorithmic notion is **submodular width** $\mathrm{subw}(H)$, refining fractional hypertree width.

## 3. State of the Art (SOTA)

- **AGM bound** (Atserias–Grohe–Marx, FOCS 2008) — tight cardinality-only bound.
- **Worst-case-optimal join algorithms:** **NPRR** (Ngo–Porat–Ré–Rudra, PODS 2012), **Leapfrog Triejoin** (Veldhuizen, ICDT 2014, used in LogicBlox), and the unifying **Generic Join** (Ngo–Ré–Rudra, SIGMOD Record 2013) — all run in $\tilde O(\mathrm{IN}^{\rho^\star} + \mathrm{OUT})$.
- **Degree-aware bounds + algorithms:** **PANDA** (Abo Khamis–Ngo–Suciu, PODS 2017) achieves runtime matching the **polymatroid bound** under degree constraints and proves the **submodular-width** upper bound for general CQs; the **FAQ** framework (Abo Khamis–Ngo–Rudra 2016) lifts this to aggregation.
- Systems-SOTA: WCOJ in LogicBlox, Umbra/free-join, DuckDB experiments, EmptyHeaded, and graph engines (RelationalAI), plus **degree-aware optimizers** that mix binary and WCOJ plans.

## 4. Upper Bound

- **Cardinality only:** $\tilde O(\mathrm{IN}^{\rho^\star(H)} + \mathrm{OUT})$ in the RAM model (NPRR / Generic Join / LFTJ), matching AGM.
- **With degree constraints / FDs:** output size $\le 2^{\text{polymatroid bound}}$, and **PANDA** evaluates any CQ in time $\tilde O(2^{\mathrm{subw}(H)} \cdot \mathrm{poly})$ up to the polymatroid bound (RAM model), strictly improving on $\mathrm{fhw}$ when degree info is present.
- **FAQ / sum-product** queries inherit the same bounds for aggregation over a commutative semiring.
- For **acyclic** queries with FDs, the bound collapses toward linear $\tilde O(\mathrm{IN}+\mathrm{OUT})$ (Yannakakis-style), with FDs further shrinking $\mathrm{OUT}$.

## 5. Lower Bound

- **AGM tightness:** the $\mathrm{IN}^{\rho^\star}$ exponent is information-theoretically **unimprovable** with cardinalities only (matching instances exist) — a **counting / information-theoretic** lower bound.
- **Comparison-/RAM model:** any worst-case-optimal join must, on some instance, spend $\Omega(\mathrm{IN}^{\rho^\star})$ — binary-join plans are provably suboptimal (the triangle query needs $\Omega(\mathrm{IN}^{3/2})$, beating any pairwise plan's $\Theta(\mathrm{IN}^2)$).
- **Entropic vs polymatroid gap:** the *true* tight bound uses **entropic** functions; the computed **polymatroid** bound can be strictly larger because the entropic cone is **not polyhedral** (non-Shannon inequalities; Zhang–Yeung). Thus the best *computable* bound provably overshoots the information-theoretic optimum for some constraint sets.
- Conditional **3SUM/SETH** lower bounds pin specific cyclic queries (e.g., triangle-listing) to their WCOJ exponents.

## 6. The Gap

For pure cardinalities, the gap is **closed** (AGM is tight; WCOJ algorithms match). With **degree constraints**, a genuine gap remains: the achievable/computable **polymatroid (submodular-width)** bound can be **strictly above the true entropic bound**, because the entropic cone's boundary is governed by infinitely many (non-Shannon) inequalities and is not even known to be decidable. So the *exact* worst-case output size under arbitrary degree constraints is, in general, **not known to be computable**, and matching algorithms inherit this slack. Closing it requires either characterizing the relevant entropic region or proving the polymatroid bound is achievable (or tight) for the query classes that matter.

## 7. Current Research (as of June 2026)

(1) **Entropic vs polymatroid** bound gap and when degree constraints make them coincide; new **Shannon-flow** inequalities and their algorithmic realization (Abo Khamis, Ngo, Suciu) *(frontier — verify)*. (2) **Output-sensitive and instance-optimal** joins, **free-join** adaptivity unifying WCOJ with binary joins (Wang–Willsey–Suciu). (3) Degree-aware **cardinality estimation** and bounds feeding real optimizers (RelationalAI, Umbra, DuckDB) *(frontier — verify)*. (4) WCOJ for **differential/incremental** maintenance, for **conjunctive queries with predicates**, and for **FAQ-AI** (ML aggregates over joins). (5) Lower bounds tying specific bounds to fine-grained conjectures (Fan, Koutris, Berkholz).

## 8. Future Work

- Decide/characterize the exact entropic output-size bound under degree constraints.
- Algorithms provably matching the entropic (not just polymatroid) bound for broad CQ classes.
- Practical, robust degree-constraint estimation and plan selection in mainstream engines.
- Extending tight bounds to joins with aggregation, predicates, and updates.

## 9. Key References

- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 / SIAM J. Comput., 2013.
- **[Foundational]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018.
- **[SOTA]** H. Q. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, D. Suciu. *What Do Shannon-Type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017.
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, A. Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016.
- **[SOTA]** T. L. Veldhuizen. *Triejoin: A Simple, Worst-Case Optimal Join Algorithm.* ICDT, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
