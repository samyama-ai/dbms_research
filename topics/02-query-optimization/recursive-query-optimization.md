---
id: 02-query-optimization/recursive-query-optimization
title: "Optimizing recursive and fixpoint queries"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimizing recursive and fixpoint queries

> **Topic:** Query Optimization · **ID:** `02-query-optimization/recursive-query-optimization` · **Status:** open

## 1. Problem Statement

Recursive queries — SQL **recursive CTEs** (`WITH RECURSIVE`), Datalog programs, graph reachability/transitive-closure, and shortest-paths — are evaluated by computing a **least fixpoint** of a monotone operator. Unlike a single relational expression, a recursive query implies an *iterative* computation whose cost depends on join orders *inside* the recursive rule, on the *evaluation strategy* (naive vs. semi-naive), on **sideways-information-passing (SIP)** / magic-set rewrites, and on **termination** behavior.

**Recursive query optimization** is the problem of choosing, cost-based: (a) the join order within the recursive body, (b) the rewrite (magic sets, factorization, aggregate pushdown), and (c) an evaluation/termination strategy, so as to minimize total cost while guaranteeing termination.

Variants:
- **Decision:** does a given recursive program terminate / reach fixpoint in finitely many steps under set semantics? (termination)
- **Optimization:** minimize total fixpoint-evaluation cost over rewrite + join-order choices.
- **Counting/complexity:** data complexity of the recursive query (the size of the fixpoint and number of iterations).

## 2. Mathematical Foundations

Semantics is the **least fixpoint** $\text{lfp}(T_P)$ of the immediate-consequence operator $T_P$ for a (positive) Datalog program $P$; by Knaster–Tarski, a monotone $T_P$ over the powerset lattice has a least fixpoint reached by iterating $T_P^\uparrow$. For positive Datalog this is reached in polynomially many steps (data complexity **PTIME-complete**, Immerman–Vardi: Datalog = PTIME-expressible monotone queries). **Stratified negation** and **recursive aggregation** require stratification or well-founded/stable-model semantics; with arithmetic and unbounded value invention, evaluation becomes **undecidable** (termination undecidable — reduction from Turing machines / Minsky counter machines).

Optimization machinery:
- **Semi-naive evaluation:** only join *newly derived* tuples ($\Delta$-relations) each round, the standard speedup; formalized as differentiating $T_P$.
- **Magic sets / SIP** (Bancilhon–Maier–Sagiv–Ullman; Beeri–Ramakrishnan): a goal-directed rewrite that simulates top-down binding propagation in bottom-up evaluation, restricting the fixpoint to *relevant* facts. Optimal SIP/adornment order is NP-hard.
- **AGM bound** and **worst-case-optimal joins** govern the cost of each recursive step's multiway join (Ngo–Ré–Rudra), and **factorized / FAQ** representations (Olteanu–Schleich; Abo Khamis–Ngo–Rudra) bound fixpoint sizes.
- For shortest-path/provenance recursion, **semiring** (Green–Karvounarakis–Tannen) and **Datalog$^\circ$ / semiring fixpoint** semantics generalize least-fixpoint to non-Boolean lattices, raising **convergence/termination** questions (Khamis et al.).

## 3. State of the Art (SOTA)

**Foundational.** Semi-naive evaluation and magic sets are the bedrock; Aho–Ullman established transitive closure is not expressible in basic relational algebra, motivating recursion.

**Systems-SOTA.** Modern Datalog engines — **Soufflé** (compiled, parallel, semi-naive + specialization), **DDlog**, **RecStep**, **DBSP / Differential Dataflow** (Materialize) for incremental recursive computation — are the performance SOTA. RDBMSs implement `WITH RECURSIVE` but optimize it weakly: most treat the recursive term as a black box and do **not** reorder joins across iterations or cost the fixpoint, a recognized gap. Recent research engines push **worst-case-optimal joins into recursion** and **cost-based magic sets**.

**Theory-SOTA.** Convergence and complexity of **semiring Datalog (Datalog$^\circ$)** and **provenance-aware** recursion (Abo Khamis, Ngo, Pichler, Suciu, et al., 2022–2024) is the active theoretical frontier, characterizing when non-Boolean recursion terminates and at what cost.

## 4. Upper Bound

- **Positive Datalog:** least fixpoint computable in **PTIME** data complexity; number of semi-naive iterations bounded by the recursion depth (e.g. $O(n)$ for linear recursion / transitive closure, where $n=|$active domain$|$). Each iteration's multiway join is **worst-case-optimal** via NPRR/Leapfrog-Triejoin, matching the AGM bound $\prod$-fractional-edge-cover.
- **Transitive closure / reachability:** $O(V\cdot E)$ semi-naive, or via matrix methods $O(V^\omega)$ (Boolean matrix multiplication).
- **Magic-set-rewritten** programs: the upper bound is the cost of the restricted fixpoint, often dramatically smaller, but choosing the rewrite is heuristic; no algorithm computes the *cost-optimal* rewrite in polynomial time.

## 5. Lower Bound

- **General recursive (Datalog with arithmetic / value invention, or `WITH RECURSIVE` over an infinite domain): termination is undecidable** (reduction from the halting problem / Minsky machines) — the core reason status is *open*: you cannot in general cost or even guarantee a plan terminates.
- **Datalog evaluation is PTIME-complete** (Immerman–Vardi), so it is inherently sequential-hard; no NC algorithm unless NC=PTIME.
- **Boundedness** (does a Datalog program collapse to a non-recursive query?) is **undecidable** for general Datalog (Gaifman–Mairson–Sagiv–Vardi), and even for restricted classes it is hard — so the optimizer cannot always decide whether recursion can be eliminated.
- **Optimal join order inside recursion** and **optimal SIP/adornment** are NP-hard; recursion adds the difficulty that the cost depends on the (unknown) fixpoint sizes at each iteration, conditional on data.

## 6. The Gap

The gap is **fundamental and open**. Two distinct chasms: (1) **Decidability** — for the full `WITH RECURSIVE`/Datalog-with-arithmetic language, termination and boundedness are undecidable, so no general cost-based optimizer can both guarantee termination and minimize cost; optimization must restrict to decidable fragments (linear, bounded, stratified). (2) **Cost modeling** — even for positive Datalog where PTIME bounds exist, the optimizer cannot predict per-iteration cardinalities (the fixpoint grows in data-dependent ways), so cost-based join ordering across iterations lacks accurate estimates; there is no accepted cost model for fixpoint computations. Production RDBMSs simply do not optimize recursion well, and there is no tight theory of *optimal* recursive plans. Closing the gap requires both (a) identifying maximal decidable, cost-modelable fragments and (b) accurate fixpoint cardinality estimation.

## 7. Current Research (as of June 2026)

Active directions: (i) **semiring/Datalog$^\circ$ convergence theory** — characterizing termination and cost of non-Boolean recursion (Abo Khamis, Ngo, Pichler, Suciu; ongoing 2024–2026) *(frontier — verify)*; (ii) **worst-case-optimal joins inside recursion** and **factorized fixpoints** (Olteanu, TU Dortmund/Zürich; relationalAI) *(frontier — verify)*; (iii) **incremental/differential recursive evaluation** (DBSP, Differential Dataflow, Materialize) with provable incremental complexity; (iv) **cost-based recursion in RDBMSs** — research on reordering joins across iterations and estimating fixpoint cardinalities (TUM, CWI/DuckDB experiments) *(frontier — verify)*; (v) **learned cardinality for recursion / graph queries**. Industrial pull from graph databases and RelationalAI's Datalog-based engine. Key groups: RelationalAI, TUM, Oxford/Zürich (Olteanu), Soufflé team (Sydney/Oracle Labs).

## 8. Future Work

- Identify maximal fragments of `WITH RECURSIVE`/Datalog admitting decidable termination *and* tractable cost-based optimization.
- Accurate per-iteration fixpoint cardinality estimation (analytic or learned) to drive join ordering.
- A principled cost model unifying semi-naive evaluation, magic sets, and worst-case-optimal joins.
- Termination-aware planning for semiring/aggregate recursion with convergence guarantees.
- First-class recursive optimization in mainstream RDBMS optimizers (not black-box CTE handling).

## 9. Key References

- **[Foundational]** F. Bancilhon, D. Maier, Y. Sagiv, J. D. Ullman. *Magic Sets and Other Strange Ways to Implement Logic Programs.* PODS, 1986. — [DOI](https://doi.org/10.1145/6012.15399)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Foundational]** H. Gaifman, H. Mairson, Y. Sagiv, M. Y. Vardi. *Undecidable Optimization Problems for Database Logic Programs.* JACM, 1993. — [DOI](https://doi.org/10.1145/174130.174142)
- **[SOTA]** H. Q. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2014. — [arXiv](https://arxiv.org/abs/1310.3314)
- **[SOTA]** B. Scholz, H. Jordan, P. Subotić, et al. *On Fast Large-Scale Program Analysis in Datalog (Soufflé).* CC, 2016. — [DOI](https://doi.org/10.1145/2892208.2892226)
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, R. Pichler, D. Suciu, Y. R. Wang. *Convergence of Datalog over (Pre-)Semirings.* PODS, 2022. — [arXiv](https://arxiv.org/abs/2105.14435)
- **[Foundational]** N. Immerman. *Relational Queries Computable in Polynomial Time.* Information and Control, 1986. — [DOI](https://doi.org/10.1016/S0019-9958(86)80029-8)

## 10. Worked Example

Transitive closure of a 4-node chain: edges $E=\{(1,2),(2,3),(3,4)\}$. Rule:
$$T(x,y) \leftarrow E(x,y). \qquad T(x,y) \leftarrow T(x,z), E(z,y).$$

**Semi-naive evaluation** (only join the *new* $\Delta T$ tuples each round):

- Round 0: $\Delta T_0 = E = \{(1,2),(2,3),(3,4)\}$ (3 tuples).
- Round 1: $\Delta T_1 = \Delta T_0 \bowtie E = \{(1,3),(2,4)\}$ (2 new).
- Round 2: $\Delta T_2 = \Delta T_1 \bowtie E = \{(1,4)\}$ (1 new).
- Round 3: $\Delta T_2 \bowtie E = \emptyset \Rightarrow$ fixpoint. Total $|T|=6$.

Iterations $= 3 = $ chain length, matching the $O(n)$ depth bound for linear recursion. Contrast **naive** evaluation, which re-derives all of $T$ each round, performing $\sum$ over the full relation instead of the small $\Delta$ — the semi-naive speedup. A magic-set rewrite seeded by query $T(1, ?)$ would further restrict derivation to tuples reachable from node $1$, never deriving $(2,3),(2,4),(3,4)$ at all.

---
*Part of the [DBMS Research catalog](../../README.md).*
