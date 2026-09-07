---
id: 33-benchmarking-testing/differential-testing-heterogeneous
title: "Differential Testing Across Heterogeneous DBMSs"
topic: 33-benchmarking-testing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-09
last_substantive_update: 2026-09
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Differential Testing Across Heterogeneous DBMSs

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/differential-testing-heterogeneous` · **Status:** partially-solved

## 1. Problem Statement

**Differential testing** runs the same query $q$ on instance $I$ across multiple engines $D_1,\dots,D_n$ and flags a disagreement $D_i(q,I)\neq D_j(q,I)$ as a candidate bug. The challenge: cross-engine differences are frequently **legitimate** (NULL ordering, collation, type coercion, float precision, implementation-defined behavior). The problem is to build a differential oracle whose disagreements imply **real bugs** — i.e., separate genuine defects from sanctioned semantic divergence.

Variants:
- **Decision variant:** Is a given disagreement a true bug or legitimate divergence?
- **Equivalence-class variant:** Partition outputs into semantic equivalence classes modulo a *divergence theory* $\equiv_\Delta$; flag only cross-class disagreement.
- **Query-restriction variant:** Generate only queries whose semantics is engine-invariant.

## 2. Mathematical Foundations

Let each engine implement a semantics $\llbracket\cdot\rrbracket^{(i)}$ that differs from a common core $\llbracket\cdot\rrbracket^{\star}$ only on a *divergence set* $\Delta_i$ (NULL/collation/type rules). A **sound differential oracle** must report a bug only when outputs differ *outside* a congruence $\equiv_\Delta$ capturing all sanctioned divergences:
$$ \text{bug}(q,I) \iff \exists i,j:\ D_i(q,I) \not\equiv_\Delta D_j(q,I). $$

If $\equiv_\Delta$ is **too coarse**, real bugs are masked (false negatives); **too fine**, legitimate divergences raise false positives. The central object is the divergence theory $\equiv_\Delta$, ideally derived from the SQL standard's *implementation-defined* clauses and each dialect's documented semantics. Multiset comparison under order-insensitivity is canonicalization (sort/normalize) costing $O(|A|\log|A|)$; collation-aware comparison composes a normalization monoid.

A useful framing: differential testing approximates the unattainable exact oracle by **majority/voting** across engines — sound only if the divergence theory subtracts all benign differences first.

## 3. State of the Art (SOTA)

- **RAGS** (Slutz, VLDB 1998): the original stochastic SQL differential tester across commercial DBMSs — already grappled with comparison normalization.
- **APOLLO** (Jung et al., VLDB 2020): differential testing for *performance regressions* across DB versions.
- **SQLancer** can run in differential mode but the authors emphasize *single-engine* metamorphic oracles precisely because cross-engine divergence is noisy.
- **SQLsmith** (Seltenreich) drives random queries into multiple engines; widely used in PostgreSQL/SQLite CI.
- **AMOEBA / DQE** and recent **NoREC/TLP** are partly motivated by avoiding the divergence problem. Industrial: ClickHouse, CockroachLabs, and DuckDB CI run cross-engine and version-differential suites with curated normalization rules.

## 3a. Why "partially-solved"

Single-engine metamorphic oracles sidestep divergence entirely and are robust; pure cross-engine differential testing remains noisy and is solved only *pragmatically* via hand-tuned normalization, not a principled, complete divergence theory.

## 4. Upper Bound

Per query, differential testing costs $n$ executions plus $O(n\cdot|A|\log|A|)$ canonicalized comparison. Building $\equiv_\Delta$ is offline engineering. With $n$ engines, a *majority oracle* tolerates up to $\lfloor (n-1)/2\rfloor$ engines sharing a fault before masking — analogous to fault-tolerant voting (no false bug if a strict majority is correct and divergence is normalized away).

## 5. Lower Bound

- Deciding whether two outputs are "the same modulo legitimate divergence" generalizes **query equivalence under a divergence theory**, undecidable for full SQL; NP-hard already for CQ containment.
- **Information-theoretic masking:** if all $n$ engines share a wrong behavior (common ancestry, shared spec misreading), no differential oracle can detect it — a fundamental limit independent of compute.
- Distinguishing benign divergence from a bug with no formal spec is **undecidable in principle** (no ground truth) — it requires an external semantics.

## 6. The Gap

The gap is between (a) pragmatic differential testing that finds many real bugs but emits false positives needing manual triage, and (b) a *principled* oracle with a formal divergence theory $\equiv_\Delta$ that would make every flagged disagreement a true bug. No complete, mechanized $\equiv_\Delta$ exists for any pair of mainstream engines; this keeps the problem partially-solved. Closing it requires formalizing the implementation-defined surface of SQL and each dialect.

## 7. Current Research (as of June 2026)

- Formalizing dialect-specific NULL/collation/type rules into machine-checkable divergence theories *(frontier — verify)*.
- LLM-assisted triage to auto-classify disagreements as benign vs. bug, with human-in-the-loop confirmation *(frontier — verify)*.
- Restricting generated queries to an **engine-invariant fragment** so differential testing becomes sound by construction.
- Groups: Manuel Rigger (NUS), Taesoo Kim's group (APOLLO), DuckDB/ClickHouse/Cockroach engineering teams, formal-SQL-semantics groups (Cheung/Chu/Suciu).
- For the **floating-point** slice of the divergence theory §1 calls for, the decisive quantity turns out to be the engine's *algorithm*, not the query. Taking ground truth as the exact rational value of the stored doubles (arithmetic, not another engine), each discrepancy classifies as *exact*, *bounded* or *indeterminate*, with relative error obeying $\mathrm{rel\_err} \le C_A(n,u)\,\kappa_f^{\,p}$ and a testability boundary $\kappa^\star_{f,A} = (1/C_A)^{1/p}$ beyond which **no** oracle can separate a bug from rounding. SUM/AVG are the linear case $p=1$; variance is $p=2$ one-pass and $p=1$ for Welford. Across eight engines in four classes the measured exponent recovers each algorithm. Honest negative: the sweep found **no engine bug** — zero anomalies is evidence the oracle is sound, not that the engines are correct (Samyama, arXiv:2609.00381) *(frontier — verify)*.

## 8. Future Work

- A reusable, certified divergence library per dialect pair.
- Sound query-generators restricted to the cross-engine-invariant SQL fragment.
- Automatic discovery of divergence rules from observed engine behavior, with statistical confidence.
- Extending differential testing to transactions/isolation levels, not just single queries.

## 9. Key References

- **[Foundational]** D. R. Slutz. *Massive Stochastic Testing of SQL (RAGS).* VLDB, 1998. — [DBLP](https://dblp.org/rec/conf/vldb/Slutz98.html)
- **[SOTA]** J. Jung, H. Hu, J. Arulraj, T. Kim, W. Kang. *APOLLO: Automatic Detection and Diagnosis of Performance Regressions in Database Systems.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3357377.3357382)
- **[SOTA]** M. Rigger, Z. Su. *Testing Database Engines via Pivoted Query Synthesis (PQS).* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/rigger) · [arXiv](https://arxiv.org/abs/2001.04174)
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Survey]** R. B. Evans, A. Savoia. *Differential Testing: A New Approach to Change Detection.* ESEC/FSE, 2007. — [DOI](https://doi.org/10.1145/1287624.1287707)

- **[SOTA]** Samyama Research. *Bounded, Indeterminate, or a Bug: A Condition-Aware Oracle for Differential Testing of SQL Aggregates.* arXiv:2609.00381 (cs.DB; cs.SE), 2026. — [arXiv](https://arxiv.org/abs/2609.00381) · [code](https://github.com/samyama-ai/numeric-semantics-oracle)
## 10. Worked Example

Run one query on three engines over table `t(name TEXT)` with rows $\{$`'apple'`, `NULL`, `'Banana'`$\}$:

```sql
SELECT name FROM t ORDER BY name;
```

| Engine | Output order |
|--------|--------------|
| $D_1$ (PostgreSQL) | `apple`, `Banana`, `NULL` (NULLs last; case-sensitive `'B' < 'a'` is false → `Banana` after `apple`) |
| $D_2$ (SQLite) | `NULL`, `Banana`, `apple` (NULLs first; ASCII: `'B'`=66 < `'a'`=97) |
| $D_3$ (MySQL, `utf8_general_ci`) | `NULL`, `apple`, `Banana` (NULLs first; case-*insensitive* collation) |

A naive differential oracle flags all three as disagreeing → 3 candidate "bugs", **all false positives**: NULL ordering and collation are *implementation-defined* in the SQL standard. The fix is to quotient by a divergence theory $\equiv_\Delta$ that (a) treats NULL-first vs NULL-last as equivalent and (b) normalizes collation by mapping each engine to its declared collation before comparing. After applying $\equiv_\Delta$, the multisets are identical and no bug is reported.

If instead $D_2$ had *dropped* the NULL row entirely, that difference lies *outside* $\equiv_\Delta$ (cardinality change, not an ordering/collation rule) — and is correctly flagged as a real bug. This is exactly why single-engine metamorphic oracles (PQS/TLP) sidestep the brittle $\equiv_\Delta$ construction.

---
*Part of the [DBMS Research catalog](../../README.md).*
