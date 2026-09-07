---
id: 33-benchmarking-testing/bounded-equivalence-smt
title: "Bounded-Equivalence Oracle via SMT"
topic: 33-benchmarking-testing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Bounded-Equivalence Oracle via SMT

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/bounded-equivalence-smt` · **Status:** partially-solved

## 1. Problem Statement

Given two query plans (or two SQL queries, or a query and an optimizer-rewritten version) $Q_1$ and $Q_2$ over a fixed schema, decide whether they are **equivalent** — i.e., produce identical results on every database instance. As a **bounded-equivalence test oracle** for DBMS testing, we relax "every instance" to "every instance whose relations have at most $k$ rows over a bounded domain":

$$Q_1 \equiv_k Q_2 \;\;\stackrel{\text{def}}{\Longleftrightarrow}\;\; \forall D \text{ with } |R^D| \le k.\;\; Q_1(D) = Q_2(D).$$

Variants:
- **Decision:** is $Q_1 \equiv_k Q_2$? If not, return a **counterexample database** $D$ with $Q_1(D)\neq Q_2(D)$ — a discriminating test case.
- **Set vs. bag semantics:** equivalence under set semantics (duplicates collapsed) vs. multiset/SQL bag semantics (duplicates counted) — the latter is the relevant one for real engines.
- **Containment** ($Q_1 \sqsubseteq Q_2$) as the building block.

The oracle's value: a sound bug detector. If two plans the optimizer claims are equivalent disagree on a bounded instance, the optimizer (or executor) has a **logic bug** — and bounded counterexamples are usually shrinkable to tiny reproducers.

## 2. Mathematical Foundations

For **conjunctive queries (CQ)** under set semantics, equivalence and containment are decidable via **homomorphism** (Chandra–Merlin):

> **Theorem (Chandra–Merlin 1977).** For CQs $Q_1, Q_2$: $Q_1 \sqsubseteq Q_2$ iff there is a homomorphism from $Q_2$ to $Q_1$ (equivalently to the frozen canonical database of $Q_1$). The problem is NP-complete.

By the **Homomorphism / small-counterexample property**, if two CQs differ, they differ on an instance no larger than the canonical database of one of them — giving a tight bound $k$. Adding union, negation, aggregation, or bag semantics escalates difficulty:

- **Bag-equivalence of CQs** is decidable but its complexity is delicate; bag-containment's decidability was long open and remains subtle.
- Full **relational algebra** equivalence (with difference) is **undecidable**.

The SMT approach encodes bounded equivalence: introduce symbolic tuples (booleans for membership / integers for multiplicities), express $Q_1, Q_2$ as constraints over these, and assert $Q_1(D) \neq Q_2(D)$. A satisfying model is a counterexample; UNSAT (up to bound $k$) certifies $\equiv_k$. Tools build on **provenance polynomials** / **K-relations** (Green–Karvounarakis–Tannen) so bag semantics maps cleanly onto integer arithmetic in the SMT model.

## 3. State of the Art (SOTA)

**Systems-SOTA.**
- **Cosette** (Chu, Wang, Weitz, Cheung; CIDR 2017) — decides SQL equivalence by *either* an SMT-backed counterexample search (disprove) *or* a Coq/Rosette proof (prove); pioneered the dual oracle.
- **HoTTSQL / U-semiring** (Chu et al., SIGMOD 2017) and **UDP** — algebraic decision procedures for bag-semantics SQL equivalence via unbounded semirings.
- **SQLSolver** (Ding et al., 2023/2024) — extends provable equivalence to many real-world rewrite rules using an integer-/U-semiring encoding, outperforming Cosette on rewrite-rule benchmarks.
- **EQUITAS / WeTune** — verify and *discover* rewrite rules; WeTune (SIGMOD 2022) synthesizes new optimizer rewrites and verifies them with an SMT-based bounded checker.

**As a fuzzing oracle.** This decision procedure powers **differential / metamorphic** DBMS testing — though the dominant practical oracles (TLP, PQS, NoREC of Manuel Rigger's group) use *cheaper* logic-equivalence tricks rather than full SMT.

## 4. Upper Bound

- **CQ containment/equivalence (set):** NP-complete; counterexample of size $\le |Q|$ exists (canonical-database bound).
- **Bounded equivalence $\equiv_k$:** decidable by reduction to SMT/SAT; worst case exponential in $k$ and schema arity, but practical solvers (Z3, cvc5) discharge realistic instances fast.
- **Provable (unbounded) equivalence:** decidable for fragments via U-semiring normalization (SQLSolver, UDP) — these *prove* equivalence outright, no bound needed, on their supported fragment.

## 5. Lower Bound

- **NP-hardness** of CQ equivalence/containment (Chandra–Merlin 1977) — already for the simplest fragment.
- **Undecidability** of equivalence for relational algebra with difference / first-order queries (Trakhtenbrot's theorem: validity over finite models is undecidable, hence so is equivalence in the full language).
- **$\Pi_2^p$-completeness** for containment of unions of CQs / CQs with inequalities; aggregation and recursion push further or undecidable.
- The bounded oracle sidesteps undecidability but inherits NP-hardness, so the SMT call is worst-case exponential — a genuine fine-grained barrier, not just an implementation cost.

## 6. The Gap

For **CQs**, theory is closed (NP-complete, decidable). The genuinely **open** region is *full SQL bag semantics with NULLs, three-valued logic, aggregation, window functions, and recursion*, where equivalence is undecidable and even bounded checking lacks a complete, efficient encoding for all features. Current provers cover growing fragments; the gap is the unmodeled tail (correlated subqueries, complex NULL propagation, ordering-sensitive operators). Closing it = either a larger decidable fragment with a complete procedure, or a bounded encoding proven to capture all bugs of a defined class.

## 7. Current Research (as of June 2026)

- Extending U-semiring / SQLSolver-style provers to **window functions, `DISTINCT ON`, and richer NULL handling** *(frontier — verify)*.
- LLM-assisted generation of candidate rewrite rules, then SMT/U-semiring verification (WeTune lineage) to filter unsound ones.
- Tighter integration of bounded-equivalence oracles into continuous fuzzers (combining Rigger-group oracles with SMT fallback for ambiguous cases).
- Provenance/K-relation-based encodings that make multiplicity reasoning native in cvc5.

## 8. Future Work

- A complete decision procedure for a maximal practically-relevant SQL fragment with NULLs and aggregation.
- Counterexample *minimization* tuned for human-readable bug reports.
- Scaling bounded $k$ adaptively (CEGAR-style) to certify equivalence with the smallest sufficient bound.
- Equivalence-modulo-implementation oracles that account for floating-point and locale-dependent semantics.

## 9. Key References

- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** S. Chu, C. Wang, K. Weitz, A. Cheung. *Cosette: An Automated Prover for SQL.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/ChuWWC17.html)
- **[SOTA]** S. Chu, A. Cheung, D. Suciu. *Axiomatic Foundations and Algorithms for Deciding Semantic Equivalences of SQL Queries (U-semiring).* VLDB, 2018. — [DOI](https://doi.org/10.14778/3236187.3236200)
- **[SOTA]** Z. Wang et al. *WeTune: Automatic Discovery and Verification of Query Rewrite Rules.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526125)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (CQ equivalence, decidability boundaries). — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

An optimizer rewrites $Q_1 = \pi_A(R \bowtie_B S)$ into $Q_2 = \pi_A(R) \ltimes \dots$ claiming pushdown is safe. Bounded check with $k=2$, domain $\{0,1\}$.

The SMT encoding introduces, for each candidate tuple, a multiplicity variable. Take $R(A,B)=\{(1,0)\}$ and $S(B,C)=\{(0,9),(0,8)\}$. Under **bag** semantics, $R\bowtie_B S$ yields two tuples $\{(1,0,9),(1,0,8)\}$, so $Q_1$ returns $A=1$ with multiplicity $2$. If the buggy $Q_2$ projects $A$ *before* the join, it returns $A=1$ with multiplicity $1$. The solver finds the model

$$D:\ R=\{(1,0)\},\ S=\{(0,9),(0,8)\}\ \Rightarrow\ Q_1(D)=\{1{:}2\}\neq Q_2(D)=\{1{:}1\},$$

a SAT witness — a $1$-row + $2$-row counterexample database, already minimal. Under **set** semantics both collapse to $\{1\}$ and the check returns UNSAT up to $k$, certifying $Q_1\equiv_k Q_2$. The example shows why bag vs. set semantics is the decisive axis: the same rewrite is a bug in SQL's bag world but sound under set semantics.

---
*Part of the [DBMS Research catalog](../../README.md).*
