# Grammar-Aware SQL Fuzzing Coverage

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/grammar-aware-sql-fuzzing` · **Status:** empirically-open

## 1. Problem Statement

Generate SQL inputs that are not only **syntactically valid** (pass the parser) but **semantically valid** (pass binding/type checking) and **deep-reaching** — driving execution into the optimizer's rewrite rules, join-order search, and executor operators rather than being rejected early. The problem: maximize meaningful code/behavioral coverage of a DBMS under test per unit of generation budget.

Variants:
- **Coverage-maximization (optimization) variant:** choose a generation policy maximizing covered code/plan space under a query budget.
- **Validity variant:** maximize the fraction of generated queries that bind and type-check.
- **Rare-feature variant:** reach low-probability features (recursive CTEs, window frames, lateral joins, specific rewrites).

## 2. Mathematical Foundations

Model SQL by a (context-sensitive) grammar $G$; purely context-free sampling yields high parse-acceptance but low *semantic* validity because scoping, typing, and aggregation rules are context-sensitive. Let $C$ be the set of coverage targets (basic blocks, optimizer rules, plan shapes) and $\text{cov}(q)\subseteq C$. We seek a distribution $\mathcal{P}$ over queries maximizing
$$ \mathbb{E}_{q\sim\mathcal{P}}\Big[\big|\textstyle\bigcup_{q} \text{cov}(q)\big|\Big] \quad\text{s.t. budget } |Q|\le B. $$

Marginal coverage gain is **submodular** (diminishing returns), so greedy/coverage-guided selection enjoys a $(1-1/e)$ guarantee against the offline optimum — but the per-query coverage oracle is only observable *after* execution, making this an online/bandit problem. Grammar fuzzing relates to sampling derivations of $G$; semantic validity adds attribute-grammar constraints (an attributed context-free grammar with a typing relation $\Gamma \vdash e : \tau$). Coverage feedback turns generation into a **reinforcement/MAB** loop over grammar production weights.

## 3. State of the Art (SOTA)

- **SQLsmith** (Seltenreich, 2016): grammar- and catalog-aware random query generator; foundational, found 100s of real bugs. High semantic validity via schema awareness.
- **SQLancer generators** (Rigger): typed, schema-aware generation feeding metamorphic oracles.
- **SQUIRREL** (Zhong et al., CCS 2020): combines a SQL grammar with coverage-guided mutation (AFL-style) and a semantic *instantiation* step — strong validity + coverage.
- **SQLRight** (Liang et al., USENIX Security 2022): integrates coverage feedback, validity, and oracles (NoREC/TLP) in one loop — a leading systems result.
- **DynSQL**, **Griffin**, and learned/LLM generators are recent entrants raising deep-coverage validity.

## 4. Upper Bound

Coverage-guided greedy generation gives a $(1-1/e)$-approximation to maximum offline coverage *if* per-query coverage were known a priori (submodular max). Online, regret bounds from contextual bandits over production weights apply but with engine-specific constants. In practice "upper bound" is the *reachable* coverage of the engine's feasible plan/operator space — a finite but unenumerated target; no closed-form optimum is known.

## 5. Lower Bound

- Generating an input that exercises a *specific* deep target is as hard as reaching a target program point — **undecidable** in general (reduces to reachability); for queries, deciding satisfiability of a generated `WHERE` (so a row survives to deeper operators) is **NP-hard** and undecidable with arbitrary functions.
- Optimal coverage-set selection is **NP-hard** (Max-Coverage); $(1-1/e)$ is best possible in poly time unless P=NP.
- Why **empirically-open**: there is no agreed formal model of "deep optimizer coverage," no proven optimal generator, and progress is measured by *empirical* bug counts and coverage percentages across engines — not by closing a clean theoretical gap.

## 6. The Gap

The gap is between (a) heuristic, coverage-guided generators that empirically reach high but plateauing coverage and (b) any principled notion of *maximal achievable* deep coverage. Because both the target space (optimizer rule firings, plan shapes) and the optimum are only empirically characterized, the problem is open in the empirical sense: we cannot certify how far from optimal current fuzzers are. Closing it needs a formal coverage model for optimizer/executor behavior and generators provably driving toward it.

## 7. Current Research (as of June 2026)

- **LLM-guided and learned grammar weighting** to reach rare features and pass semantic checks at higher rates *(frontier — verify)*.
- Plan-shape / optimizer-rule coverage as the feedback signal rather than raw basic blocks *(frontier — verify)*.
- Hybrid generation+mutation with constraint solving to keep rows alive through deep operators.
- Groups: Manuel Rigger (NUS, SQLancer), Taesoo Kim / Insu Yun (SQUIRREL, SQLRight lineage), Andreas Seltenreich (SQLsmith), DuckDB/ClickHouse fuzzing teams.

## 8. Future Work

- A standardized **deep-coverage metric** for query engines (beyond line coverage).
- Provable online-coverage guarantees for adaptive generators.
- Cross-dialect transfer of generation policies; targeting newly added features automatically.
- Co-optimizing generation with oracles (NoREC/TLP) so reached code is also *checked*.

## 9. Key References

- **[Foundational]** A. Seltenreich. *SQLsmith: A Random SQL Query Generator.* Open-source project, 2016. — [GitHub](https://github.com/anse1/sqlsmith)
- **[SOTA]** R. Zhong, Y. Chen, H. Hu, H. Zhang, W. Lee, D. Wu. *SQUIRREL: Testing Database Management Systems with Language Validity and Coverage Feedback.* ACM CCS, 2020. — [arXiv](https://arxiv.org/abs/2006.02398) — [DOI](https://doi.org/10.1145/3372297.3417260)
- **[SOTA]** Y. Liang, S. Liu, H. Hu. *Detecting Logical Bugs of DBMS with Coverage-based Guidance (SQLRight).* USENIX Security, 2022. — [USENIX](https://www.usenix.org/conference/usenixsecurity22/presentation/liang)
- **[SOTA]** M. Rigger, Z. Su. *Finding Bugs in Database Systems via Query Partitioning.* OOPSLA, 2020. — [DOI](https://doi.org/10.1145/3428279)
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)

## 10. Worked Example

A purely context-free SQL grammar can emit `SELECT a FROM t WHERE b > 'x'`, but if column `b` is `INTEGER`, the binder rejects it — *syntactically* valid, *semantically* invalid, so it never reaches the optimizer. A schema-aware (attribute-grammar) generator instead consults $\Gamma$: `t(a INT, b INT)` and emits `SELECT a FROM t WHERE b > 5`, which binds and exercises predicate pushdown.

Submodular coverage in action. Suppose three candidate queries cover optimizer rules:
$\text{cov}(q_1)=\{r_1,r_2\}$, $\text{cov}(q_2)=\{r_2,r_3\}$, $\text{cov}(q_3)=\{r_3,r_4,r_5\}$, budget $B=2$.

Greedy: pick $q_3$ (gain 3) $\Rightarrow \{r_3,r_4,r_5\}$; then $q_1$ (marginal gain 2, since $r_2$ new but $r_3$ already covered) $\Rightarrow$ 5 rules. The offline optimum here is also $\{q_3,q_1\}=5$. The $(1-1/e)\approx 0.63$ guarantee bounds greedy's worst case; note coverage of $q_2$ dropped to marginal gain 1 once $q_3$ was chosen — the diminishing-returns (submodular) effect that justifies the greedy bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
