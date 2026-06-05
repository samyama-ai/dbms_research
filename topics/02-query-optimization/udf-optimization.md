# Optimizing queries with user-defined functions

> **Topic:** Query Optimization · **ID:** `02-query-optimization/udf-optimization` · **Status:** partially-solved

## 1. Problem Statement

Declarative query optimizers reason over relational operators with known cost and selectivity models. **User-defined functions (UDFs)** — scalar, table-valued, aggregate, or procedural (multi-statement, with loops, variables, and embedded SQL) — are *opaque*: their cost, selectivity, and side-effects are unknown to the optimizer, and they are typically executed row-by-row outside the set-oriented engine, defeating optimization.

The problem has several coupled sub-problems:
- **Costing:** estimate per-invocation cost and output cardinality/selectivity of an opaque function.
- **Reordering / placement:** decide where in the plan to evaluate an expensive predicate UDF (predicate migration / *expensive-predicate placement*), since UDF cost can dwarf I/O.
- **Inlining / decorrelation:** transform procedural UDF bodies into relational algebra so the optimizer sees through them (the central "partially solved" advance).
- **Decision variants:** is a UDF *inlinable* into a single relational expression? Is a given predicate ordering optimal under per-tuple UDF costs?

## 2. Mathematical Foundations

**Expensive-predicate optimization** (Hellerstein–Stonebraker) models a query as a set of predicates each with cost $c_i$ per tuple and selectivity $s_i$; the optimal evaluation order of *independent* conjunctive predicates is by ascending **rank** $\text{rank}(p_i)=\frac{s_i-1}{c_i}$ (equivalently descending $\frac{1-s_i}{c_i}$), a classic ratio/exchange-argument result. With join interleaving (*predicate migration*), the problem of optimal placement of expensive predicates within a join plan is solved in polynomial time for a fixed join tree (Hellerstein, ACM TODS 1998) via a network-flow/parametric argument, but becomes NP-hard jointly with join ordering.

**UDF inlining** rests on relational transformation of imperative code: a procedural body is translated to a **single SQL expression** using *Apply* (correlated/lateral join) algebra and then **decorrelated** (Galindo-Legaria–Joshi unnesting), turning iteration and assignment into relational algebra and CASE expressions. Loops and recursion map to **recursive CTEs / fixpoints**; the translatable fragment is exactly the loop-free (or structured-recursion) procedural fragment — outside it, inlining is undecidable in general (arbitrary code → halting). Side-effect-free (pure) UDFs are reorderable; impure ones impose ordering constraints turning the problem into constrained scheduling.

Costing opaque functions connects to **online learning**: per-UDF cost/selectivity learned from execution feedback (LEO-style) with regret bounds.

## 3. State of the Art (SOTA)

**Systems-SOTA — the breakthrough.** Microsoft's **Froid** (Ramachandra et al., PVLDB 2018) automatically inlines multi-statement T-SQL scalar UDFs into the calling query as relational algebra (via Apply + algebraic relational transformations), letting the existing cost-based optimizer reorder and set-orient them — yielding order-of-magnitude speedups; shipped in SQL Server 2019. Follow-ups extend to **table-valued** and **procedural** UDFs and to other languages (*Aggify* for cursor loops → aggregates; *Sirius/Tuplex*-style compilation of Python UDFs to native code; *Apache Spark* and DuckDB UDF vectorization/columnar UDFs).

**Foundational systems-SOTA.** Predicate migration in POSTGRES (Hellerstein–Stonebraker, 1993); the *EXPENSIVE* predicate framework.

**Theory-SOTA.** Optimal expensive-predicate ordering by rank (provably optimal for independent predicates); polynomial predicate placement in a fixed join tree.

## 4. Upper Bound

- **Independent conjunctive expensive predicates:** optimal ordering computable in $O(n\log n)$ by sorting on rank — exact, optimal.
- **Predicate placement in a fixed join tree:** polynomial-time optimal (Hellerstein, parametric/flow argument).
- **UDF inlining:** for the structured, loop-free (and bounded-recursion) procedural fragment, inlining is linear in body size, producing a single relational expression the optimizer then handles with its normal complexity — this is the Froid upper bound and is constructive.
- **Joint reordering with correlated predicates / join order:** only exhaustive/dynamic-programming methods give exact answers (exponential), with greedy/rank heuristics in practice.

## 5. Lower Bound

- **Joint expensive-predicate + join ordering** is **NP-hard** (it generalizes join ordering, NP-hard already, and expensive-predicate placement with arbitrary correlations).
- **Optimal ordering with predicate correlations** (dependent selectivities) is NP-hard — the independence assumption is what makes rank-ordering tractable.
- **General UDF inlining is undecidable:** arbitrary procedural code with unbounded loops/recursion cannot be statically transformed into a finite relational expression (reduction from the halting problem); even deciding semantic equivalence of the inlined form is undecidable. Hence "partially solved" — only a restricted (but practically dominant) fragment is handled.
- Costing opaque pure functions is information-theoretically impossible a priori (no oracle); must be learned, with inherent regret.

## 6. The Gap

For the **classical expensive-predicate** sub-problem the gap is *closed*: rank-ordering and fixed-tree placement are optimal and polynomial, with matching NP-hardness only when correlations or joint join-ordering are admitted. For **inlining**, the gap is a *coverage* gap rather than a complexity gap: Froid-style techniques cover the loop-free/structured fragment optimally, but a large practical tail — unbounded loops, exceptions, external side effects, cross-language UDFs — remains un-inlinable, and there is no characterization of the *maximal* inlinable fragment or principled cost/selectivity learning with guarantees for what cannot be inlined. The genuinely open piece is **opaque-UDF costing under correlation**, where no tractable optimal scheme exists.

## 7. Current Research (as of June 2026)

Active directions: (i) **extending Froid** to richer control flow, recursion, and table-valued/procedural UDFs, and to PostgreSQL/open-source engines (Microsoft GSL, academic ports) *(frontier — verify)*; (ii) **compiling polyglot UDFs** (Python, Java, WASM) to vectorized/columnar native code — Tuplex, DuckDB, Velox, and WASM-based UDF sandboxes *(frontier — verify)*; (iii) **learned UDF cost/selectivity models** feeding the optimizer (online feedback, LEO-style, and ML estimators); (iv) **LLM-assisted UDF-to-SQL rewriting** for fragments beyond static inlining, with verification *(frontier — verify)*; (v) reordering UDFs under provenance/side-effect constraints. Groups: Microsoft Research/GSL, TUM, MIT, Brown (Tuplex), CWI/DuckDB.

## 8. Future Work

- A precise characterization of the maximal automatically-inlinable procedural fragment.
- Cost-/selectivity-aware optimization of UDFs that *cannot* be inlined (learned models with guarantees).
- Verified UDF-to-SQL rewriting (including LLM-assisted) with equivalence checking.
- Optimal expensive-predicate ordering under correlation (approximation algorithms).
- Cross-engine, cross-language UDF optimization with consistent cost semantics and sandboxed side-effect reasoning.

## 9. Key References

- **[Foundational]** J. M. Hellerstein, M. Stonebraker. *Predicate Migration: Optimizing Queries with Expensive Predicates.* SIGMOD, 1993. — [ACM](https://dl.acm.org/doi/10.1145/170036.170078)
- **[Foundational]** J. M. Hellerstein. *Optimization Techniques for Queries with Expensive Methods.* ACM TODS, 1998. — [DBLP](https://dblp.org/rec/journals/tods/Hellerstein98.html)
- **[SOTA]** K. Ramachandra, K. Park, K. V. Emani, A. Halverson, C. Galindo-Legaria, C. Cunningham. *Froid: Optimization of Imperative Programs in a Relational Database.* PVLDB, 2018. — [arXiv](https://arxiv.org/abs/1712.00498)
- **[SOTA]** S. Gupta, K. Ramachandra. *Procedural Extensions of SQL: Understanding their usage in the wild.* PVLDB, 2021. — [ACM](https://dl.acm.org/doi/abs/10.14778/3457390.3457402)
- **[SOTA]** L. F. Spiegelberg, R. Yesantharao, M. Schwarzkopf, T. Kraska. *Tuplex: Data Science in Python at Native Code Speed.* SIGMOD, 2021. — [ACM](https://dl.acm.org/doi/10.1145/3448016.3457244)
- **[Foundational]** C. A. Galindo-Legaria, M. M. Joshi. *Orthogonal Optimization of Subqueries and Aggregation.* SIGMOD, 2001. — [ACM](https://dl.acm.org/doi/10.1145/375663.375748)

## 10. Worked Example

**Expensive-predicate ordering by rank.** A query applies two independent conjunctive predicates per tuple: $p_1$ = cheap range check, $p_2$ = a costly UDF (e.g., image classifier). Costs and selectivities:

| Predicate | cost $c_i$ | selectivity $s_i$ | $\text{rank}=\frac{s_i-1}{c_i}$ |
|-----------|-----------|-------------------|----------------------------------|
| $p_1$ | $1$ | $0.5$ | $-0.50$ |
| $p_2$ | $100$ | $0.1$ | $-0.009$ |

Order by **ascending rank** (most negative first): $p_1$ then $p_2$. On $N=1000$ tuples, evaluate $p_1$ on all 1000 (cost $1000$); only $500$ survive to $p_2$ (cost $500\times100=50{,}000$); total $\approx 51{,}000$. Reverse order $p_2$ then $p_1$: $1000\times100 = 100{,}000$ for $p_2$ alone, then $100$ survivors $\times1=100$; total $\approx100{,}100$ — nearly $2\times$ worse.

The exchange argument confirms optimality: swapping two adjacent predicates improves cost iff they are out of rank order, so sorting on rank ($O(n\log n)$) is exact for **independent** predicates. Introduce correlation between $p_1,p_2$ and the rank rule breaks — that placement becomes NP-hard (§5).

---
*Part of the [DBMS Research catalog](../../README.md).*
