# Verifying Query Optimizer Transformation Rules

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/verify-optimizer-rules` · **Status:** partially-solved

## 1. Problem Statement
A rule-based optimizer rewrites a logical plan via a catalog of transformation rules $\{r_1,\dots,r_m\}$ (predicate pushdown, join reordering/associativity, subquery decorrelation, aggregate pushdown, outer-join reordering, etc.). The task: **formally prove**, for each rule $r$, that whenever its precondition holds, the input expression $E$ and output expression $r(E)$ are *semantically equivalent* — under **bag (multiset) semantics** and SQL's **three-valued logic (3VL)** with NULLs — i.e. $\llbracket E\rrbracket_D = \llbracket r(E)\rrbracket_D$ for every database $D$.

Variants:
- **Per-rule verification (decision):** is rule $r$ sound (equivalence-preserving) on its stated precondition?
- **Bug-finding (refutation):** find a counterexample $D$ where $r$ changes the result (an *unsound* rule).
- **Conditional soundness:** synthesize the *weakest precondition* under which $r$ is sound.

Equivalence must respect: multiplicities (bags, not sets), NULL propagation (3VL: `WHERE` keeps only TRUE), and the difference between set and bag operators.

## 2. Mathematical Foundations
Bag query equivalence differs sharply from set equivalence. For **set** conjunctive queries, equivalence is decidable via **homomorphism / query containment** (Chandra–Merlin 1977) and is NP-complete. For **bag** semantics, equivalence of conjunctive queries reduces to isomorphism-type conditions and **bag-containment of CQs is undecidable in general** (Ioannidis–Ramakrishnan; Jayram–Kolaitis–Vee, PODS 2006), which is precisely why optimizer rules need *proof per rule* rather than a decision procedure.

Formally, an expression denotes a function $\llbracket E\rrbracket: \mathbf{Inst}\to \mathbb{N}^{\mathrm{Tup}}$ (multiplicity vector). 3VL is modeled with truth values $\{\mathsf{T},\mathsf{F},\mathsf{U}\}$ and Kleene connectives; selection keeps tuples evaluating to $\mathsf{T}$. A clean algebraic foundation is **K-relations / semiring-annotated relations** (Green–Karvounarakis–Tannen, PODS 2007): over the semiring $(\mathbb{N},+,\times,0,1)$ a relation is a function to $\mathbb{N}$, and positive-relational-algebra identities are exactly the semiring identities — giving an equational theory in which many rules become checkable rewrites. NULLs and difference fall outside the positive fragment, requiring explicit 3VL reasoning.

## 3. State of the Art (SOTA)
- **Mechanized/automated provers for SQL equivalence:**
  - **Cosette** (Chu, Wang, Cheung, Suciu; CIDR 2017) — a solver/prover for SQL equivalence using both a counterexample finder and a Coq-based prover.
  - **HoTTSQL / UDP** (Chu et al., SIGMOD 2017) — denotes SQL with NULLs/bags into homotopy type theory / unbounded semirings (U-semiring) and proves rewrite-rule equivalences in Coq.
  - **SPES / Spark-rule verification** (Zhou, Arch, et al., VLDB 2019/2020) — symbolic, SMT-backed prover for *bag* equivalence used to verify Calcite rewrite rules, scaling to many real rules.
  - **WeTune** (Wang et al., SIGMOD 2022) — automatically *discovers* and verifies new rewrite rules with an SMT-based verifier.
- **Bug-finding for optimizers:** **SQLancer** (TLP/NoREC, Rigger–Su) catches *unsound* optimizations differentially in production engines (Postgres, MySQL, SQLite, CockroachDB, DuckDB).
- These tools have verified large fractions of real catalogs (e.g., Calcite), hence **partially-solved**; full-catalog, fully-mechanized soundness for an industrial optimizer is not complete.

## 4. Upper Bound
For the **positive bag-relational-algebra** fragment, U-semiring/HoTTSQL reasoning yields a sound (and for many decidable subcases, decision) procedure; SPES decides bag-equivalence for a broad SMT-expressible fragment and verifies hundreds of Calcite rules automatically. WeTune verifies discovered rules with bounded SMT search. Counterexample search (Cosette's solver mode, SQLancer) refutes unsound rules in time polynomial in a bounded instance size. So *per-rule* verification within these fragments is effectively automatic.

## 5. Lower Bound
Equivalence is **undecidable** in full generality: bag-equivalence/containment of conjunctive queries is undecidable (Jayram–Kolaitis–Vee, PODS 2006), and adding difference/negation and 3VL NULLs only worsens it (set CQ-equivalence is already **NP-complete**, Chandra–Merlin 1977). Thus no algorithm decides soundness for *all* rules over the full SQL algebra; verification must restrict the fragment or accept incompleteness.

## 6. The Gap
The gap is between (a) automated, *complete* verification on decidable fragments (positive bag algebra, SMT-expressible cases — essentially closed) and (b) full SQL with correlated subqueries, recursion (`WITH RECURSIVE`), window functions, and intricate 3VL/outer-join interactions, where verification is **undecidable** and current tools are sound-but-incomplete or limited to bounded counterexample search. The open problem is maximizing the *verified fragment* and producing machine-checked end-to-end soundness for an entire real catalog including these features. Closing it needs richer decidable fragments and mechanized proofs for the hard operators.

## 7. Current Research (as of June 2026)
Directions: (1) extending U-semiring/SMT verifiers to window functions, recursion, and full outer-join reordering *(frontier — verify)*; (2) rule *synthesis*-plus-verification (WeTune successors) to grow and certify optimizer catalogs automatically; (3) coupling differential bug-finders (SQLancer) with provers so refutations become regression specs. Groups: Cheung & Wang (U. Washington, Cosette/HoTTSQL/WeTune lineage), Suciu (UW, semiring semantics), Rigger (ETH Zürich, SQLancer), and the Apache Calcite community (Hortonworks/independent contributors) verifying production rewrite rules.

## 8. Future Work
- Mechanized, machine-checked soundness for a *full* industrial optimizer catalog (Calcite/Orca-scale).
- Decision procedures or sound-complete fragments covering recursion and window functions.
- Weakest-precondition synthesis so partially-sound rules are repaired rather than discarded.
- Integration of verified rules into the optimizer build so soundness is a CI gate.

## 9. Key References
- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings (K-relations).* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Jayram, Kolaitis, Vee. *The Containment Problem for Real Conjunctive Queries with Inequalities / bag semantics.* PODS, 2006. — [DOI](https://doi.org/10.1145/1142351.1142363)
- **[SOTA]** Chu, Weitz, Cheung, Suciu. *HoTTSQL: Proving Query Rewrites with Univalent SQL Semantics.* PLDI/SIGMOD, 2017. — [arXiv](https://arxiv.org/abs/1607.04822)
- **[SOTA]** Zhou, Arch, et al. *SPES: A Symbolic Approach to Proving Query Equivalence Under Bag Semantics.* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2004.00481)
- **[SOTA]** Wang, Zhou, Cheung, et al. *WeTune: Automatic Discovery and Verification of Query Rewrite Rules.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526125)

## 10. Worked Example

**An unsound "rule" caught by bag semantics.** Consider pushing a join through a projection's duplicate behavior — concretely the candidate rewrite "`SELECT a FROM R, S WHERE R.a = S.a`" vs. "`SELECT a FROM R`" when the optimizer wrongly assumes $S$ acts as a no-op filter.

Take $R(a)$ with row $\{1\}$ (multiplicity 1) and $S(a)$ with rows $\{1,1\}$ (multiplicity 2). Under **bag** semantics the join multiplies multiplicities:

$$[\![R\bowtie S]\!](1) = R(1)\times S(1) = 1\times 2 = 2,\qquad [\![R]\!](1) = 1.$$

So the rewrite changes the result ($2$ copies of `1` vs. $1$) — **unsound**. Under *set* semantics both yield $\{1\}$, so a set-only checker (homomorphism, Chandra–Merlin, NP) would wrongly certify it. A bijection-based prover (SPES) or U-semiring normalizer detects the mismatch because the multiplicity polynomials $R(a)\cdot S(a)$ and $R(a)$ are not equal as functions $\mathbb{N}^{\mathrm{Tup}}$. SQLancer would expose the same bug differentially: seed $R,S$ as above, run both plans, observe row counts $2 \neq 1$. This is exactly why each rule needs per-rule proof under bags rather than a single set-semantics decision procedure.

---
*Part of the [DBMS Research catalog](../../README.md).*
