# Coverage Metrics for DBMS Testing

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/dbms-coverage-metrics` · **Status:** open

## 1. Problem Statement

Software testing measures **adequacy** with coverage metrics — statement, branch, MC/DC, mutation score. For a DBMS these are weak proxies: a test suite can hit 100% of optimizer source lines while exercising a negligible fraction of *SQL semantic behaviors* (join orders, NULL-three-valued-logic paths, type-coercion rules, collation effects, plan shapes). The problem:

> Define a **coverage / adequacy criterion** $C$ over a test suite $S$ and DBMS $D$ that (a) is *automatable* (computable from instrumented runs or static artifacts), (b) is *meaningful* (higher $C$ correlates with higher probability of exposing real semantic/logic bugs), and (c) goes *beyond code-line coverage* to capture SQL-language and query-plan behavior.

Variants:
- **Measurement:** given $S$, compute $C(S)$ — a number or covered-element set.
- **Optimization / generation:** generate $S$ maximizing $C$ under a query budget (a **set-cover / submodular maximization** problem).
- **Comparison:** is criterion $C_1$ a stronger adequacy notion than $C_2$ (subsumption ordering)?

This is **open**: there is no agreed, validated semantic coverage metric for DBMS testing.

## 2. Mathematical Foundations

Classical adequacy is a **subsumption lattice** of criteria; mutation adequacy sits near the top. Formally, a criterion partitions the *behavior space* into *coverage obligations* $\{g_1,\dots,g_m\}$; $C(S) = |\{g_i : \exists t\in S \text{ covering } g_i\}| / m$.

For DBMS, candidate obligation spaces:
- **Plan-space coverage:** the set of distinct physical operators / operator-pairs / plan shapes the optimizer emits. Relates to the (exponential) join-order space; one can bound representativeness via the **AGM bound** on output sizes to weight "interesting" joins.
- **Predicate / 3-valued-logic coverage:** for each boolean condition, cover {true, false, NULL/unknown} — an MC/DC analogue lifted to ternary logic.
- **Grammar / production coverage:** treat SQL as a grammar $G$; obligation = each production (or production pair) used, à la **grammar-based testing**.
- **Mutation coverage:** seed mutants in the engine or in queries; coverage = killed mutants / total. Mutation adequacy is the gold standard but expensive.

Generation-as-optimization: choosing $S$ to maximize covered obligations is **maximum coverage**, NP-hard, but the coverage function is **monotone submodular**, so greedy achieves $(1-1/e)$:
$$C(S_{\text{greedy}}) \ge \left(1-\tfrac1e\right) \cdot C(S^\*).$$

The deep difficulty: defining an obligation set whose *coverage provably correlates with bug exposure* — a statistical/learning question, not just combinatorial.

## 3. State of the Art (SOTA)

**Systems-SOTA.**
- **SQLancer** (Rigger & Su; OOPSLA/ESEC-FSE 2020) — finds hundreds of bugs in real DBMSs via **PQS, NoREC, TLP** metamorphic oracles; notably it does *not* rely on a semantic coverage metric, which underlines the gap.
- **SQLsmith** (Seltenreich) — grammar-based random SQL generation; "coverage" is implicitly grammar productions + crash signals.
- **Squirrel / DynSQL / Griffin** (2021–2023) — coverage-*guided* fuzzers that use **code-coverage feedback** (AFL-style edge coverage) to steer SQL generation — the dominant feedback signal today is still *code* coverage.
- **APOLLO / AMOEBA** — performance-bug oracles using plan/latency differentials, hinting at plan-space coverage.

**Theory-SOTA.** No standard DBMS-semantic adequacy criterion exists. Foundations come from general testing theory (subsumption lattices; mutation analysis, DeMillo–Lipton–Sayward / Hamlet 1977–78) and from query-language complexity (AHV) that bounds the behavior space.

## 4. Upper Bound

- **Computing** a defined criterion: linear in suite size given instrumentation (code-edge coverage is standard and cheap).
- **Generating** a coverage-maximizing suite: greedy submodular gives $(1-1/e)$-optimal under a query budget; randomized grammar sampling gives no guarantee but scales.
- **Mutation adequacy:** killing $N$ mutants costs $O(N \cdot |S|)$ runs; mutant-reduction and parallelism lower the constant. No criterion is known to be *complete* (cover all bug-revealing behaviors) at sub-exponential cost.

## 5. Lower Bound

- **Maximum coverage is NP-hard**, and inapproximable beyond $(1-1/e)$ unless $\mathrm{P}=\mathrm{NP}$ (Feige 1998) — so optimal suite generation under any reasonable obligation set is hard.
- **Plan-space and join-order behavior is exponential** in relation count, so *exhaustive* plan coverage is intractable (the optimizer's own search space lower bound).
- **No coverage criterion can be sound and complete** as a bug oracle: detecting whether a test reveals an arbitrary semantic deviation is undecidable in general (Rice/Trakhtenbrot), so any practical metric is a heuristic proxy with no completeness guarantee.

## 6. The Gap

The gap is **definitional and empirical, not closed**. We can compute code coverage and grammar coverage cheaply, and we can *optimize* coverage with submodular guarantees — but no criterion has been *validated* to predict DBMS bug discovery better than crude code-edge coverage, and code coverage demonstrably saturates while bugs remain (SQLancer keeps finding bugs at "full" code coverage). Closing the gap requires: (1) a semantic obligation space (plan-shape × predicate-logic × type-coercion) that is automatable, and (2) an empirical study showing coverage of it dominates code coverage as a bug predictor.

## 7. Current Research (as of June 2026)

- Combining metamorphic oracles (SQLancer family) with **semantic feedback** — using plan diversity or query-feature coverage instead of pure edge coverage to steer generation *(frontier — verify)*.
- Learning-based coverage: embedding queries/plans and using novelty/diversity in embedding space as a coverage surrogate.
- Mutation testing *of DBMS engines themselves* (engine-mutants) to validate suite adequacy at scale.
- Manuel Rigger's group (NUS) and the Squirrel/DynSQL fuzzing lines remain the most active; standardization efforts around DBMS bug benchmarks (bugbench-style).

## 8. Future Work

- A *validated*, automatable semantic adequacy criterion with a published subsumption relation to code coverage and mutation score.
- Coverage metrics specific to optimizer behavior (plan-shape and cost-crossover coverage).
- Budgeted suite generation with submodular guarantees over the semantic obligation set.
- Benchmarks correlating coverage with held-out real bugs to settle the "meaningfulness" question empirically.

## 9. Key References

- **[Foundational]** R. A. DeMillo, R. J. Lipton, F. G. Sayward. *Hints on Test Data Selection: Help for the Practicing Programmer (Mutation Testing).* IEEE Computer, 1978. — [DOI](https://doi.org/10.1109/C-M.1978.218136)
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)
- **[SOTA]** M. Rigger, Z. Su. *Testing Database Engines via Pivoted Query Synthesis (PQS).* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/rigger) · [arXiv](https://arxiv.org/abs/2001.04174)
- **[SOTA]** M. Rigger, Z. Su. *Finding Bugs in Database Systems via Query Partitioning (TLP).* OOPSLA, 2020. — [DOI](https://doi.org/10.1145/3428279)
- **[SOTA]** R. Zhong et al. *SQUIRREL: Testing Database Management Systems with Language Validity and Coverage Feedback.* CCS, 2020. — [DOI](https://doi.org/10.1145/3372297.3417260) · [arXiv](https://arxiv.org/abs/2006.02398)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (query-language expressiveness/behavior space). — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)

## 10. Worked Example

Take **3-valued predicate coverage** as the obligation set. For a single `WHERE` predicate $p$ over a nullable column, the obligations are $\{p=\text{TRUE},\ p=\text{FALSE},\ p=\text{UNKNOWN(NULL)}\}$, so $m=3$.

Two candidate queries against table `t(x INT)` with rows $\{1, 5, \texttt{NULL}\}$:

- $q_1$: `SELECT * FROM t WHERE x > 3` — on the three rows, $p$ evaluates to FALSE (1), TRUE (5), UNKNOWN (NULL). Covers all 3 obligations: $C(\{q_1\})=3/3=1$.
- $q_2$: `SELECT * FROM t WHERE x > 0` — evaluates TRUE, TRUE, UNKNOWN. Covers $\{$TRUE, UNKNOWN$\}$ only: $C(\{q_2\})=2/3$.

Why this matters: a classic logic bug is treating `x > 3` on a NULL row as FALSE (filtering it correctly) but `NOT (x > 3)` as TRUE (wrongly *including* the NULL) — violating SQL's three-valued logic where `NOT UNKNOWN = UNKNOWN`. Code-line coverage hits 100% of the comparison operator's source on $q_2$ alone, yet never exercises the UNKNOWN path, so the bug survives. The semantic metric exposes the gap that edge coverage saturates over.

Greedy suite selection: starting empty, pick $q_1$ (gain 3), done — matching the $(1-1/e)$ submodular guarantee, here achieving the exact optimum.

---
*Part of the [DBMS Research catalog](../../README.md).*
