# Verified Reference Implementation of SQL Semantics

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/verified-sql-semantics` · **Status:** partially-solved

## 1. Problem Statement

Most DBMS testing reduces to "is the engine's answer correct?" — which presupposes a *trusted oracle*. The grand goal here is a **machine-checked formalization of full SQL** in a proof assistant (Coq/Rocq, Lean, Isabelle) whose executable evaluator can serve as that oracle, and over which **query-equivalence/optimization rules can be proven sound**.

"Full SQL" is the hard part: **three-valued logic with NULLs**, **bag (multiset) semantics**, **aggregation** (`GROUP BY`, `HAVING`, aggregate functions over bags), **correlated subqueries**, `EXISTS`/`IN`/`ANY`/`ALL`, `ORDER BY`/`LIMIT`, and `NULL`-sensitive grouping/duplicate elimination. Variants:
- **Specification variant:** a denotational semantics matching the SQL standard (or a chosen dialect) including all the above corners.
- **Executable-oracle variant:** an extracted/compiled evaluator, proven to refine the spec, fast enough to test real engines.
- **Equivalence-checker variant:** a decision/semi-decision procedure for $Q_1 \equiv Q_2$ certified against the spec (used for rewrite verification and equivalent-mutant detection).

## 2. Mathematical Foundations

The denotational core: a query denotes a function from environments to **bags** (finite multisets), modeled as $\mathbb{D} \to \mathbb{N}$ (multiplicity functions) or, in the **HoTTSQL** approach, as functions into a commutative semiring / homotopy types where two queries are equal iff their denotations are provably equal. SQL's WHERE filters with **three-valued logic** $\{\mathsf{true},\mathsf{false},\mathsf{unknown}\}$ (Kleene logic), keeping only `true` rows; `NULL` propagation is defined per operator.

Aggregation is a fold over the bag with NULL-skipping semantics; `GROUP BY` partitions by a NULL-aware equivalence. Equivalence proofs reduce algebraic SQL identities to equalities in the semiring of multisets; **U-semiring** (Chu et al.) generalizes this so summation/duplication and predicates live in one structure, making rewrite proofs compositional. The metatheory rests on classic results: **bag-CQ equivalence ≈ isomorphism** (Chaudhuri–Vardi); **set-CQ containment** by homomorphism (Chandra–Merlin); and the undecidability of full **relational-calculus/FOL equivalence** (Trakhtenbrot) which bounds what any complete checker can achieve.

## 3. State of the Art (SOTA)

- **HoTTSQL / Cosette** (Chu, Wang, Cheung, Suciu; SIGMOD/PLDI 2017–2018) — SQL semantics in Coq via homotopy type theory and **U-semirings**, with an automated rewrite-rule prover; Cosette is the front-end equivalence checker.
- **A Coq Formalization of the Relational Data Model / SQLCert / DataCert** (Benzaken, Contejean et al., ESOP 2014 onward) — a careful Coq formalization of SQL including NULLs, bag semantics and the SQL algebra, with an **executable, extracted** compiler — the closest to a verified reference evaluator.
- **SQLSolver / equivalence provers** (recent) push automated equivalence checking using semiring/integer-arithmetic encodings and SMT, handling more of the bag+aggregate fragment *(frontier — verify)*.
- **Systems use:** Cosette-style checks have found bugs in optimizer rewrite rules; formalizations underpin proposals for verified optimizers (cf. cost-model and rewrite work).

## 4. Upper Bound

The Benzaken–Contejean formalization yields an **executable evaluator** by extraction — correct by construction relative to its spec — so as an *oracle* it is "complete" for the formalized fragment (you can always compute $Q(I)$). For equivalence checking, the **U-semiring** approach decides a large class of UCQ-with-bag rewrites automatically and discharges aggregation identities via normalization; complexity is that of the underlying SMT/normalization, exponential in the worst case but practical on real rules. For set-CQ fragments, equivalence is in **NP** (homomorphism). No procedure is complete for full SQL (see below).

## 5. Lower Bound

Equivalence of full SQL is **undecidable**: SQL subsumes relational calculus / first-order logic with arithmetic, and FOL validity/equivalence is undecidable (Church/Turing; finite-model version Trakhtenbrot — *finite* satisfiability is also undecidable/non-r.e.). Hence no sound-and-complete equivalence checker can exist. Even decidable fragments are hard: **CQ containment** is **NP-complete** (Chandra–Merlin); **UCQ with inequalities** climbs to **$\Pi_2^p$** (van der Meyden); adding **aggregation** quickly leaves known-decidable territory. These bound any certified equivalence tool and any attempt at *minimal* oracle construction.

## 6. The Gap

Partially solved. Executable verified evaluators exist for substantial SQL fragments (DataCert/SQLCert), and automated equivalence is strong for bag-UCQ + simple aggregation (Cosette/U-semiring). The gap: (1) no single formalization covers *all* corners simultaneously — three-valued NULL logic, full aggregation, correlated subqueries, ordering/`LIMIT`, and window functions — with a *fast* extracted oracle; (2) equivalence is undecidable in general, so the checker is necessarily incomplete and the open question is *how large a decidable, automatable fragment* can be carved out; (3) matching a *real dialect's* idiosyncrasies (PostgreSQL vs. standard) is unformalized. Closing the gap is incremental coverage + faster certified execution, not a single theorem.

## 7. Current Research (as of June 2026)

- Extending U-semiring/Cosette equivalence to window functions, richer aggregation, and outer joins; integer-arithmetic/SMT encodings (SQLSolver lineage) *(frontier — verify)*.
- Porting/redeveloping SQL formalizations in **Lean 4** and Rocq with performance-oriented extraction for use as test oracles *(frontier — verify)*.
- Coupling verified semantics with SQLancer-style differential testing — using the proof-assistant evaluator as the differential oracle.
- Verified query optimizers: proving rewrite rules sound against the formal semantics (Cheung/Suciu and Benzaken/Contejean lineages).

## 8. Future Work

- A reference oracle covering a named dialect end-to-end, fast enough for high-volume fuzzing.
- Characterizing maximal decidable fragments for automated equivalence under bag + aggregate semantics.
- Mechanized proofs that production optimizer rewrites preserve semantics.
- A shared, versioned formal SQL standard the community can extend and trust.

## 9. Key References

- **[SOTA]** S. Chu, K. Weitz, A. Cheung, D. Suciu. *HoTTSQL: Proving Query Rewrites with Univalent SQL Semantics.* PLDI, 2017.
- **[SOTA]** S. Chu, B. Murphy, J. Roesch, A. Cheung, D. Suciu. *Axiomatic Foundations and Algorithms for Deciding Semantic Equivalences of SQL Queries (U-semiring).* VLDB, 2018.
- **[SOTA]** V. Benzaken, É. Contejean, S. Dumbrava. *A Coq Formalization of the Relational Data Model.* ESOP, 2014.
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977.
- **[Foundational]** S. Chaudhuri, M. Y. Vardi. *Optimization of Real Conjunctive Queries.* PODS, 1993.
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995.

---
*Part of the [DBMS Research catalog](../../README.md).*
