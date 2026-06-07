---
id: 25-query-languages-expressiveness/nl-to-query-semantics
title: "Translating Natural Language to Formal Queries"
topic: 25-query-languages-expressiveness
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Translating Natural Language to Formal Queries

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/nl-to-query-semantics` · **Status:** empirically-open

## 1. Problem Statement
**Natural-language-to-query (NL2Query / Text-to-SQL, Text-to-SPARQL, Text-to-Cypher)** is the task of mapping a natural-language question $u$, given a database schema $S$ (and possibly instance/values), to a formal query $q$ over $S$ such that $q$ is *executable* and *semantically faithful* to the user's intent. The core scientific problem is not just producing some query, but providing **correctness guarantees**: that $q(D)$ returns exactly what $u$ asks.

Variants:
- **Generation:** produce $q$ (the dominant empirical setting; benchmarked by exact-match and execution accuracy).
- **Verification / certification:** decide whether a produced $q$ is *equivalent* to a gold query, or whether it provably matches a formal specification extracted from $u$.
- **Ambiguity & abstention:** detect when $u$ is genuinely ambiguous (multiple non-equivalent faithful $q$) and ask a clarifying question rather than guessing.
- **Robustness:** invariance to paraphrase, schema renaming, and unseen databases (cross-domain generalization).

## 2. Mathematical Foundations
Semantically, the gold object is a **denotation** $\llbracket q \rrbracket_D$; two queries are *equivalent* if $\llbracket q_1\rrbracket = \llbracket q_2\rrbracket$ on all databases. Faithfulness is therefore a **query-equivalence** problem, which is undecidable for full relational calculus but **NP-complete for conjunctive queries** (Chandra–Merlin, via homomorphism) and decidable under bag/set semantics for restricted fragments. This is why "execution accuracy" on one instance $D$ is an *unsound* proxy: $\llbracket q_1\rrbracket_D = \llbracket q_2\rrbracket_D$ does not imply equivalence.

Compositional semantics (Montague-style) and **semantic parsing** ground $u$ into a logical form (lambda-calculus, $\lambda$-DCS, FunQL, or directly SQL AST). Modern systems frame this as conditional generation $\Pr_\theta(q \mid u, S)$ with an LLM/seq2seq model, optionally **constrained decoding** to the grammar of valid queries (so every output is syntactically and schema-valid by construction). Guarantees, when present, come from: (i) **grammar-constrained** decoding (soundness of *form*), (ii) **execution-guided** decoding / self-consistency, and (iii) post-hoc **equivalence verification** against constraints.

## 3. State of the Art (SOTA)
- **Empirical-SOTA:** LLM-based pipelines dominate **Spider / Spider 2.0 / BIRD** leaderboards. Techniques: schema linking + few-shot/RAG (DIN-SQL, DAIL-SQL), self-correction and self-consistency, and agentic decomposition. BIRD (Li et al., NeurIPS 2023) added efficiency and noisy real-world schemas; **Spider 2.0** (2024) raised difficulty to enterprise-scale, nested, dialect-specific SQL where top systems still fall well short of human accuracy *(frontier — exact leaderboard numbers shift; verify current best on Spider 2.0)*.
- **Method-SOTA:** Grammar/PICARD-style **constrained decoding** (Scholak et al., EMNLP 2021) guarantees parseable, schema-valid SQL; **execution-guided** decoding; tool-augmented agents that run, observe, and repair queries.

## 4. Upper Bound
With **grammar-constrained decoding**, one can *guarantee* the output is a syntactically valid, schema-consistent query (a structural upper bound on error: zero parse/binding failures). Execution-guided generation guarantees the query *runs* and is non-empty/typed. For the *conjunctive* sublanguage, a produced query can be **certified equivalent** to a reference by an NP equivalence check (homomorphism test) or refuted with a counterexample database — a decidable correctness oracle for that fragment.

## 5. Lower Bound
Faithfulness has **no general algorithmic guarantee**: deciding equivalence of two relational-calculus queries is **undecidable**, so certifying that $q$ exactly matches an arbitrary intent is undecidable in the worst case. Even restricted to checking against a gold query, equivalence is NP-hard (CQ). Information-theoretically, when $u$ is **ambiguous**, no deterministic translator can be correct on all interpretations — abstention is necessary. Empirically, accuracy degrades sharply with schema size, value linking, and dialect, and current systems exhibit a persistent gap to human performance on realistic benchmarks (this is the sense in which the problem is *empirically open*).

## 6. The Gap
The gap is between **strong empirical generation** (high execution accuracy on simple/seen schemas) and the **absence of correctness guarantees** on realistic, ambiguous, large-schema queries. We can guarantee *form* (grammar) but not *meaning* (denotation) in general. Closing it requires either (a) restricting to decidable query fragments with equivalence certificates, (b) interactive disambiguation that provably resolves intent, or (c) calibrated abstention with bounded error — none of which is yet a complete solution.

## 7. Current Research (as of June 2026)
- **Agentic Text-to-SQL** with execution feedback, schema-exploration tools, and self-repair; multi-candidate generation + verification/selection.
- **Equivalence-aware evaluation** and verifiers (e.g., bounded-model query equivalence via solvers like Cosette/SQLSolver) used to score or filter candidates *(frontier — adoption of formal equivalence checking in NL2SQL is nascent; verify)*.
- **Ambiguity-aware** and **clarification** models; uncertainty calibration and selective prediction; cross-dialect and enterprise (Spider 2.0) generalization.

## 8. Future Work
- Translators that emit a *certificate* (proof or counterexample) of faithfulness for a decidable fragment.
- Provably-calibrated abstention/clarification policies with bounded intent-error.
- Tight benchmarks measuring semantic equivalence (not single-instance execution match) and robustness to schema/paraphrase perturbation.

## 9. Key References
- **[Foundational]** A. Chandra, P. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977 (query equivalence/containment). — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** P. Liang, M. Jordan, D. Klein. *Learning Dependency-Based Compositional Semantics.* ACL, 2011 ($\lambda$-DCS semantic parsing). — [ACL](https://aclanthology.org/P11-1060/) — [arXiv](https://arxiv.org/abs/1109.6841)
- **[SOTA]** T. Scholak, N. Schucher, D. Bahdanau. *PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models.* EMNLP, 2021. — [arXiv](https://arxiv.org/abs/2109.05093) — [ACL](https://aclanthology.org/2021.emnlp-main.779/)
- **[SOTA]** J. Li et al. *Can LLM Already Serve as a Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQLs (BIRD).* NeurIPS, 2023. — [arXiv](https://arxiv.org/abs/2305.03111)
- **[Survey]** T. Yu et al. *Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL.* EMNLP, 2018. — [arXiv](https://arxiv.org/abs/1809.08887) — [ACL](https://aclanthology.org/D18-1425/)
- **[SOTA]** F. Lei et al. *Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows.* 2024. — [arXiv](https://arxiv.org/abs/2411.07763)

## 10. Worked Example

Schema: `Emp(id, name, dept, salary)`. Question $u$: *"Who earns more than every employee in 'Sales'?"*

A model emits $q_1$ (correlated `>` all) vs. $q_2$ (`> MAX`):

- $q_1$: `SELECT name FROM Emp e WHERE NOT EXISTS (SELECT 1 FROM Emp s WHERE s.dept='Sales' AND e.salary <= s.salary)`
- $q_2$: `SELECT name FROM Emp WHERE salary > (SELECT MAX(salary) FROM Emp WHERE dept='Sales')`

Why single-instance execution accuracy is unsound: take $D$ where Sales is **empty**. Then $q_1$ returns *all* employees (the `NOT EXISTS` is vacuously true), while $q_2$ returns the empty set (`MAX` of no rows is `NULL`, and `salary > NULL` is unknown). So $\llbracket q_1\rrbracket_D \neq \llbracket q_2\rrbracket_D$ — this $D$ is a **counterexample database** witnessing non-equivalence. But on any $D$ with a nonempty Sales department they agree, so testing only such an instance would wrongly certify them equal. This concretely shows execution match on one $D$ does not imply $\llbracket q_1\rrbracket = \llbracket q_2\rrbracket$ on all $D$ (Section 2), and that faithfulness needs an equivalence check, not a single run.

---
*Part of the [DBMS Research catalog](../../README.md).*
