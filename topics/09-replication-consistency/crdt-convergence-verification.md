# Verifying convergence of arbitrary CRDT designs

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/crdt-convergence-verification` · **Status:** partially-solved

## 1. Problem Statement

Strong eventual consistency (SEC) for a replicated data type requires that replicas that have applied the same *set* of updates reach the *same* state, regardless of delivery order or duplication. For operation-based CRDTs this reduces to proving that concurrent operations **commute**; for state-based CRDTs it reduces to merge being a **join** on a semilattice (commutative, associative, idempotent — ACI). Designers routinely introduce subtle bugs (an OR-Set that resurrects elements, a sequence CRDT whose interleaving violates intention preservation) that break convergence only under specific concurrent schedules.

The problem: **Given a user-defined replicated data type — its state, operations, and merge/effector functions — automatically prove (or refute) that it is strongly eventually consistent.**

- **Decision variant:** decide whether a given (effect, merge) pair guarantees SEC over all reachable states and all delivery orders.
- **Verification variant:** produce a machine-checkable proof of commutativity/ACI, or a concrete counterexample schedule.
- **Synthesis variant:** automatically repair or synthesize a conflict-resolution rule restoring convergence.

## 2. Mathematical Foundations

Op-based SEC holds iff concurrent operations commute on the abstract state: for concurrent $o_1, o_2$, $\mathit{eff}(o_2)\circ \mathit{eff}(o_1) = \mathit{eff}(o_1)\circ \mathit{eff}(o_2)$. State-based SEC holds iff $(S, \sqcup)$ is a **join-semilattice**: $\sqcup$ is commutative, associative, idempotent, and updates are inflationary ($x \sqsubseteq \mathit{up}(x)$). Convergence is then a least-upper-bound argument (Shapiro et al.).

Verification is an instance of checking algebraic laws over a (possibly infinite) state space — undecidable in general by reduction from the **word problem / equivalence of programs**. Practical attacks restrict to decidable fragments: encode operations as transformations and discharge commutativity as SMT queries over linear arithmetic / arrays (decidable theories), or use **reduction theorems** that bound the number of replicas/operations needed to witness any violation (a *small-model property*). Bounded model checking explores schedules up to depth $k$; full proofs need induction over the reachable-state relation.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Gomes, Kleppmann, Mulligan, Beresford's Isabelle/HOL framework (OOPSLA 2017) gives the first mechanized, reusable proof of SEC, verifying RGA and OR-Set. The "small-model"/reduction approach (Nagar & Jagannathan, CONCUR 2019; *Liu et al.*) reduces convergence/consistency checking to bounded queries.
- **Systems SOTA:** automated tools — *VeriFx* (De Porre, Boix et al., 2023) compiles CRDT specs to SMT proof obligations and verifies commutativity/SEC; *Katara* (Laddad, Hellerstein et al., 2022) synthesizes verified CRDTs from sequential specs; *Hamsaz/Hampa* synthesizes coordination for replicated objects. Maven-style property testing (Jepsen-style) catches violations empirically.

## 4. Upper Bound

For data types whose operations are expressible in a decidable SMT theory (arrays, linear integer arithmetic, sets), VeriFx-style verification discharges SEC as a finite set of validity queries — terminating, sound, and complete *for that fragment*. Reduction theorems give a **small-model bound**: any convergence violation is witnessed by a schedule with a constant number of replicas (typically 2–3) and a bounded number of operations, making bounded checking complete up to that bound. Synthesis (Katara) runs in time polynomial in the spec size given an SMT oracle.

## 5. Lower Bound

Convergence verification for *arbitrary* operations over unbounded state is **undecidable** (reduction from the halting/word problem for the operation transformers). Even within decidable fragments, the SMT queries are NP-hard (QF-LIA) or worse (with quantifiers/arrays, the problem can be undecidable or non-elementary). Refuting SEC by finding a divergent schedule is at least NP-hard. Thus no algorithm verifies SEC for all user-defined CRDTs; completeness is fragment-relative.

## 6. The Gap

The frontier "solved" region is: decidable-fragment data types get automatic, sound, complete verification (VeriFx) or mechanized proofs (Isabelle). The open region is everything outside those fragments — rich data types (trees, ordered sequences with intention preservation, nested CRDTs), liveness/GC interactions, and full automation of the inductive invariant. The gap is between *bounded/fragment-complete* automation and *general* (undecidable) verification; closing it means richer decidable abstractions and invariant inference, not a single decision procedure.

## 7. Current Research (as of June 2026)

Push toward end-to-end verified CRDT compilers and toward verifying *security/integrity* and *GC* alongside convergence *(frontier — verify)*. VeriFx and Katara lines (VUB, UC Berkeley/Hydro — Hellerstein, Laddad), Kleppmann's group (TU Munich/Cambridge), and Nagar/Jagannathan (Purdue) on bounded reductions remain active. LLM-assisted invariant synthesis for replicated-object proofs is an emerging, unverified direction *(frontier — verify)*.

## 8. Future Work

- Decidable abstractions for ordered/tree CRDTs with intention preservation.
- Automatic inductive-invariant inference to lift bounded checking to unbounded proofs.
- Unified verification of convergence + GC + security policies in one framework.

## 9. Key References

- **[Foundational]** V. Gomes, M. Kleppmann, D. Mulligan, A. Beresford. *Verifying strong eventual consistency in distributed systems.* OOPSLA, 2017.
- **[Foundational]** M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski. *Conflict-free Replicated Data Types.* SSS, 2011.
- **[SOTA]** K. De Porre, C. Scholliers, et al. *VeriFx: Correct Replicated Data Types for the Masses.* ECOOP, 2023.
- **[SOTA]** S. Laddad, C. Power, M. Milano, A. Cheung, J. M. Hellerstein. *Katara: Synthesizing CRDTs with verified lifting.* OOPSLA, 2022.
- **[SOTA]** K. Nagar, S. Jagannathan. *Automated parameterized verification of CRDTs.* CONCUR/CAV, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
