# The Test Oracle Problem for SQL

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/sql-test-oracle-problem` · **Status:** open

## 1. Problem Statement

Given a DBMS $D$, a query $q$ over a database instance $I$, and the answer $A = D(q, I)$ produced by $D$, decide whether $A$ is **correct**, i.e., whether $A$ equals the answer prescribed by the formal semantics of SQL. The **oracle problem** is the absence of a generally trusted mechanism that decides this without a second, already-trusted reference engine.

Variants:
- **Decision variant:** Is $A = \llbracket q \rrbracket_I$? (Boolean correctness.)
- **Counting/diff variant:** Report the multiset symmetric difference $A \,\triangle\, \llbracket q \rrbracket_I$ and its cardinality.
- **Localization variant:** If incorrect, attribute the fault to a query operator/optimizer rewrite.

A *sound* oracle never flags a correct answer as buggy (no false positives); a *complete* oracle detects every incorrect answer. The open problem is a **sound, general** oracle that needs no trusted reference.

## 2. Mathematical Foundations

Let SQL semantics be a partial function $\llbracket \cdot \rrbracket : \mathcal{Q} \times \mathcal{I} \to \mathcal{R}$ over bag-relational algebra $\mathcal{BA}$ with three-valued logic ($\{\text{true},\text{false},\text{unknown}\}$) for NULL handling. An oracle is a predicate $\mathcal{O}(q, I, A) \in \{\text{pass}, \text{fail}\}$.

A **partial oracle** decides correctness only on a subset $S \subseteq \mathcal{Q}\times\mathcal{I}$. Metamorphic and equivalence-partitioning oracles are partial: they assert invariants $\Phi$ such that $\Phi(q,I,A)$ must hold for all correct engines, e.g. for predicate $p$ over rows $R$:
$$ |\sigma_p(R)| + |\sigma_{\neg p}(R)| + |\sigma_{p\ \mathrm{IS\ UNKNOWN}}(R)| = |R|. $$

Soundness of such an oracle reduces to proving the invariant is a theorem of the bag-algebra semantics. Completeness is bounded by **coverage**: the fraction of incorrect $(q,I,A)$ triples that violate at least one asserted invariant — generally not 1.

Full correctness checking is at least as hard as **query equivalence** under bag semantics, which is undecidable for relational algebra with difference (reduction from Hilbert's 10th / two-counter machines), so a *general* exact oracle cannot be both sound and complete and terminating.

## 3. State of the Art (SOTA)

Practical oracles are all *partial*:
- **PQS — Pivoted Query Synthesis** (Rigger & Su, OSDI 2020): pick a random *pivot* row, synthesize a query guaranteed to contain it; soundly detects fetch bugs.
- **NoREC — Non-optimizing Reference Engine Construction** (Rigger & Su, ESEC/FSE 2020): compare an optimized query to a semantically equivalent unoptimizable form (push predicate into `SELECT`); finds optimizer bugs.
- **TLP — Ternary Logic Partitioning** (Rigger & Su, OOPSLA 2020): partition rows by $p$ / $\neg p$ / $p$ IS NULL and require the union to equal the unpartitioned result.
- **SQLancer** ecosystem operationalizes all three; **CERT** (cardinality oracle), **DQP** (distributed query plans, 2024) extend coverage to performance and plan bugs.

## 4. Upper Bound

For the partial-oracle family, checking one metamorphic invariant costs $O(\text{cost}(q))$ per transformed query — a small constant factor over normal execution. PQS row-containment is $O(|\text{schema}|)$ per pivot. There is **no nontrivial general upper bound** for exact correctness because equivalence checking is undecidable; the only universal "oracle" is a trusted reference engine, which merely shifts trust and runs in the cost of re-executing $q$.

## 5. Lower Bound

- **Undecidability:** Equivalence of relational-algebra queries with difference/aggregation is undecidable; hence no algorithm is a sound, complete, total exact oracle (Trakhtenbrot-style / two-counter reductions).
- **Containment of conjunctive queries** is NP-complete (Chandra-Merlin 1977); even the decidable fragment is intractable.
- **Information-theoretic:** without a reference, an oracle that observes only $(q,I,A)$ cannot distinguish $D$'s consistent-but-wrong semantics from a legitimate engine on inputs where no asserted invariant is violated — coverage $<1$ is unavoidable for any finite invariant set.

## 6. The Gap

The gap is qualitative, not a constant factor: between **partial sound oracles** (coverage well below 100%, no false positives) and the **impossible** sound-complete-total exact oracle. Closing it is not achievable in general; the realistic frontier is *increasing coverage* of partial oracles toward the full SQL surface (window functions, recursive CTEs, JSON, time-zone/collation-dependent operators) while preserving provable soundness.

## 7. Current Research (as of June 2026)

- Extending metamorphic oracles to **window functions, recursive CTEs, and JSON/array** semantics, where soundness proofs are subtle *(frontier — verify)*.
- **LLM-assisted oracle synthesis** proposing candidate invariants later machine-checked against a formal SQL semantics *(frontier — verify)*.
- Mechanized SQL semantics for oracle soundness proofs, building on HoTTSQL / "A Formal Semantics of SQL" lines of work.
- Groups: Manuel Rigger (NUS, SQLancer), Alvin Cheung / Shumo Chu (formal SQL semantics), TU Darmstadt / ETH testing groups.

## 8. Future Work

- A machine-checked library of *provably sound* metamorphic relations spanning the SQL:2023 surface.
- Quantitative coverage metrics: what fraction of the semantics each oracle family can witness.
- Oracles for **performance/plan correctness** and for transactional/isolation anomalies, not just result correctness.
- Composable oracles with formal soundness preserved under composition.

## 9. Key References

- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [book site](http://webdam.inria.fr/Alice/)
- **[SOTA]** M. Rigger, Z. Su. *Testing Database Engines via Pivoted Query Synthesis.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/rigger)
- **[SOTA]** M. Rigger, Z. Su. *Finding Bugs in Database Systems via Query Partitioning (TLP).* OOPSLA, 2020. — [DOI](https://doi.org/10.1145/3428279)
- **[SOTA]** M. Rigger, Z. Su. *Detecting Optimization Bugs via Non-optimizing Reference Engine Construction (NoREC).* ESEC/FSE, 2020. — [DOI](https://doi.org/10.1145/3368089.3409710) · [arXiv](https://arxiv.org/abs/2007.08292)
- **[Foundational]** S. Chu, K. Weitz, A. Cheung, D. Suciu. *HoTTSQL: Proving Query Rewrites with Univalent SQL Semantics.* PLDI, 2017. — [DOI](https://doi.org/10.1145/3062341.3062348) · [arXiv](https://arxiv.org/abs/1607.04822)

## 10. Worked Example

A TLP (Ternary Logic Partitioning) oracle in action — no reference engine needed. Table $t(c)$:

| c |
|---|
| 1 |
| NULL |
| 3 |

Original query $Q_0$: `SELECT c FROM t` returns $\{1, \text{NULL}, 3\}$ (3 rows).

Pick predicate $p \equiv (c > 1)$. TLP runs three partition queries with a `WHERE` clause:
- $Q_T$: `WHERE c > 1` → $\{3\}$ (1 row; $1>1$ is false, NULL$>1$ is unknown).
- $Q_F$: `WHERE NOT (c > 1)` → $\{1\}$ (1 row).
- $Q_N$: `WHERE (c > 1) IS NULL` → $\{\text{NULL}\}$ (1 row; the NULL row).

Oracle invariant: $Q_T \cup_{\text{ALL}} Q_F \cup_{\text{ALL}} Q_N \equiv Q_0$ as multisets. Here $\{3\} \uplus \{1\} \uplus \{\text{NULL}\} = \{1,3,\text{NULL}\}$, which equals $Q_0$. **Pass.**

Now suppose a buggy optimizer mishandled 3-valued logic and evaluated $Q_N$ as empty (treating `IS NULL` on the predicate as always false). Then the union has 2 rows $\ne 3$ rows — a *sound* failure flagged with zero false positives, because the invariant $|σ_p| + |σ_{¬p}| + |σ_{p\,\text{IS UNKNOWN}}| = |R|$ is a theorem of bag semantics.

---
*Part of the [DBMS Research catalog](../../README.md).*
