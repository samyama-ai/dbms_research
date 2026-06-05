# Subquery decorrelation and unnesting completeness

> **Topic:** Query Optimization · **ID:** `02-query-optimization/subquery-decorrelation` · **Status:** partially-solved

## 1. Problem Statement

A **correlated subquery** references columns from an enclosing query block; naive evaluation runs the inner query once per outer tuple (nested-loops / *tuple-at-a-time*), which is asymptotically poor. **Decorrelation (unnesting)** rewrites a nested query into a flat, set-oriented expression — joins, semi-/anti-joins, group-by, outer joins — that the optimizer can reorder and that runs in set-oriented fashion.

The problem has two faces:
- **Completeness:** is there a rewrite framework that decorrelates *every* form of correlation — arbitrary nesting depth, correlations inside aggregates, EXISTS/NOT EXISTS/IN/ANY/ALL, scalar subqueries with COUNT-bug hazards, lateral references — into correlation-free algebra? (The "partially solved" status: a general unnesting procedure exists, but its cost-optimal use and edge-case completeness are not fully settled.)
- **Cost-awareness:** decorrelation is not always faster; choosing *whether* and *how* to unnest is a cost-based optimization, not a mandatory rewrite.

Decision variant: is a given nested query decorrelatable into correlation-free relational algebra? Optimization variant: choose the unnesting + join order minimizing cost.

## 2. Mathematical Foundations

The workhorse operator is the **dependent join / Apply** $R \mathbin{\text{Apply}} E(r)$ (a.k.a. lateral join), evaluating expression $E$ parameterized by each tuple $r \in R$. Decorrelation is the algebraic problem of **pushing Apply down** past relational operators until its right side no longer references the left, at which point Apply degenerates into an ordinary (semi/anti/outer) join. The key identities (Galindo-Legaria–Joshi; Neumann–Kemper *unnesting arbitrary queries*) are *push-down rules*:

$$R\,A^{\bowtie}\,(\sigma_p E) = \sigma_p(R\,A^{\bowtie} E),\quad R\,A^{\bowtie}(E_1 \bowtie E_2)=\dots,\quad R\,A^{\bowtie}(\Gamma_{g;f} E)=\Gamma_{R\text{-keys},g;f}(R\,A^{\bowtie}E),$$

with care for the **COUNT bug** (scalar aggregates over empty groups must yield $0$/NULL via outer join, not vanish). Neumann–Kemper prove these rules suffice to *fully decorrelate any* correlation by always pushing Apply down — a **completeness** result for the Apply-elimination procedure: every dependent join can be transformed into a regular join (possibly via *magic-set*-style duplicate-elimination of correlation values $D=\Pi_{\text{free}}(R)$).

This connects to **magic sets** (Bancilhon–Maier–Sagiv–Ullman) and **sideways information passing** for Datalog, and to the **chase** for reasoning about the equivalence of rewritten queries under dependencies.

## 3. State of the Art (SOTA)

**Foundational.** Kim (ACM TODS 1982) gave the first systematic unnesting (and exposed the COUNT bug, fixed by Ganski–Wong, SIGMOD 1987). Dayal (VLDB 1987) generalized to aggregates and outer joins. **Galindo-Legaria–Joshi** (SIGMOD 2001) gave the *Apply*-based, cost-based, orthogonal framework used in SQL Server.

**Systems-SOTA — the general result.** **Neumann–Kemper** (BTW 2015), *Unnesting Arbitrary Queries*, give a general algorithm that decorrelates *any* dependent join via systematic push-down, implemented in HyPer/Umbra; widely regarded as the most complete practical framework and adopted (in spirit) by DuckDB and others. Cost-based unnesting decisions remain optimizer-specific.

**Theory-SOTA.** Equivalence of nested vs. flattened forms is grounded in relational-algebra-with-aggregation semantics and bag semantics; completeness for the Apply-elimination procedure is established for the SQL-expressible fragment.

## 4. Upper Bound

Neumann–Kemper's procedure decorrelates an arbitrary dependent join in time **linear in the size of the operator tree** (a syntactic rewrite: each push-down step is local), producing a correlation-free plan. The *magic*/dependent-join then runs in set-oriented time governed by ordinary join complexity rather than $O(|R_{\text{outer}}|)$ re-executions. Thus the rewrite itself is cheap (polynomial, effectively linear); the residual cost is that of the *flattened* query, optimized by the standard (exponential-in-relations) join-order search. For the *decision* "is this decorrelatable into correlation-free algebra?" the answer for the SQL fragment is *always yes* — the procedure is complete by construction.

## 5. Lower Bound

The decorrelation *rewrite* is not where hardness lies; the hardness is downstream:
- **Cost-optimal unnesting + join ordering** is **NP-hard** (it subsumes join-order optimization, NP-hard for general/cyclic queries — Ibaraki–Kameda).
- **Equivalence of two SQL queries with aggregation/negation** (needed to *certify* a non-standard unnesting is correct) is **undecidable** in general (relational calculus with arithmetic), and even conjunctive-query equivalence is NP-complete (Chandra–Merlin). This bounds any *semantic* (as opposed to syntactic-rule-based) decorrelation/optimization.
- For Datalog-style correlations, magic-set transformation is polynomial but optimal sideways-information-passing order is NP-hard.

## 6. The Gap

For the **algorithmic decorrelation** of the SQL-expressible fragment, the gap is essentially *closed*: Neumann–Kemper give a complete, polynomial procedure, matching the trivial lower bound. The remaining openness is twofold and genuine: (i) **cost-awareness** — deciding *when* unnesting helps and *which* unnested form is cheapest is entangled with NP-hard join ordering, and no tight approximation is known; (ii) **completeness beyond the standard fragment** — correlations involving recursion, window functions, ordered/array semantics, and user-defined aggregates are not uniformly covered, and certifying correctness of aggressive rewrites runs into undecidable equivalence. Hence "partially solved": the syntactic backbone is solved; the cost-optimal and full-language frontier is open.

## 7. Current Research (as of June 2026)

Active directions: (i) **extending general unnesting** to window functions, recursive CTEs, and lateral/array correlations (TUM Umbra, DuckDB, CedarDB) *(frontier — verify)*; (ii) **cost-based unnesting** that interleaves decorrelation with join enumeration rather than rewriting eagerly (Microsoft, Snowflake) *(frontier — verify)*; (iii) **verified rewrites** — using Cosette-style SQL equivalence solvers / proof assistants to certify decorrelation rules over bag semantics; (iv) decorrelation for **distributed/streaming** engines where dependent joins are especially costly. Key people/groups: Neumann & Kemper (TUM/CedarDB), Galindo-Legaria (Microsoft), the DuckDB team (CWI), and SQL-equivalence theorists (Chu, Cheung, Suciu — Cosette/UDP).

## 8. Future Work

- A unified, *cost-aware* unnesting framework integrated with join-order enumeration, with approximation guarantees.
- Complete decorrelation for window functions, recursive, and ordered/array correlations with proven equivalence.
- Machine-checked correctness of the full rule set under SQL's bag-with-NULL semantics.
- Decorrelation tailored to vectorized, distributed, and streaming execution models.
- Handling correlated subqueries that embed opaque UDFs (links to UDF optimization).

## 9. Key References

- **[Foundational]** W. Kim. *On Optimizing an SQL-like Nested Query.* ACM TODS, 1982.
- **[Foundational]** R. A. Ganski, H. K. T. Wong. *Optimization of Nested SQL Queries Revisited.* SIGMOD, 1987.
- **[Foundational]** C. A. Galindo-Legaria, M. M. Joshi. *Orthogonal Optimization of Subqueries and Aggregation.* SIGMOD, 2001.
- **[SOTA]** T. Neumann, A. Kemper. *Unnesting Arbitrary Queries.* BTW (Datenbanksysteme für Business, Technologie und Web), 2015.
- **[Foundational]** F. Bancilhon, D. Maier, Y. Sagiv, J. D. Ullman. *Magic Sets and Other Strange Ways to Implement Logic Programs.* PODS, 1986.
- **[SOTA]** S. Chu, K. Weitz, A. Cheung, D. Suciu. *HoTTSQL / Cosette: Proving Query Rewrites with Univalent SQL Semantics.* PLDI / CIDR, 2017–2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
