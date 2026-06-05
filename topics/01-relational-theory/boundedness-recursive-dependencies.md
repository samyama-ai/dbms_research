# Boundedness of Recursive Dependencies

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/boundedness-recursive-dependencies` · **Status:** open

## 1. Problem Statement

A recursive specification — a set of recursive dependencies (tgds) or a **Datalog** program $P$ — is **bounded** if its least-fixpoint semantics is reached after a *constant* number of iterations independent of the input database; equivalently, $P$ is equivalent to a **non-recursive** (union of conjunctive queries / first-order) program. Boundedness matters because bounded programs admit FO evaluation, parallel ($\mathrm{AC}^0$) evaluation, and aggressive optimization.

**The boundedness problem (decision):** given $P$, decide whether $P$ is bounded. Variants: **program boundedness** (some bound holds for all input) vs. **predicate boundedness** (a specific IDB predicate stabilizes); **uniform** vs. **program-dependent** bound. The analogous question for **recursive sets of dependencies** asks whether the chase / implication closure is equivalent to a finite non-recursive dependency set.

## 2. Mathematical Foundations

For a Datalog program $P$ with immediate-consequence operator $T_P$, the semantics is $\bigcup_k T_P^k(\emptyset)$. $P$ is **bounded** iff $\exists k\;\forall D:\; T_P^{k}(D)=T_P^{k+1}(D)$. Boundedness is equivalent to **FO-expressibility** of the recursive predicate (for the standard semantics, modulo subtleties): a bounded Datalog program is rewritable to a UCQ.

Key structural notion: a recursion is bounded iff every "expansion tree" (proof tree / unfolding) beyond depth $k$ is *subsumed* by a shallower one via homomorphism. This ties boundedness to the **chase**: a set of tgds is bounded iff the chase terminates in uniformly bounded steps and the result is captured by finitely many CQ patterns.

**Theorem (Gaifman–Mairson–Sagiv–Vardi, 1987).** Boundedness is **undecidable** for general Datalog. **Theorem.** For **linear** Datalog (single recursive atom per rule body), boundedness is **decidable** (but with high complexity, e.g., 2EXPSPACE-type bounds for some subclasses); for **monadic** Datalog it is decidable (PSPACE-hard, in EXPTIME-range). Single-rule ("sirup") boundedness is decidable in several cases yet open in general.

## 3. State of the Art (SOTA)

- **Theory SOTA**: undecidability of general boundedness (GMSV 1987) is the anchoring negative result. Positive decidability is known for **monadic Datalog** (Cosmadakis–Gaifman–Kanellakis–Vardi 1988) and **linear Datalog**. Tight complexity for many subclasses (e.g., monadic, single-rule with restrictions) was pinned down through the 1990s; some single-recursive-rule cases remain **open**. For dependencies, boundedness connects to **chase termination** (CT), itself undecidable in general with decidable sufficient conditions (weak acyclicity, MFA, MSA).
- **Systems SOTA**: practical Datalog engines (Soufflé, RecStep, LogicBlox lineage) do not decide boundedness; they use **semi-naive evaluation** plus magic sets, and detect *specific* non-recursive patterns syntactically.

## 4. Upper Bound

When decidable: **monadic Datalog** boundedness is in **2EXPTIME / EXPSPACE** depending on formulation; **linear** Datalog boundedness is decidable with elementary but high bounds. For dependency sets satisfying **weak acyclicity** the chase terminates in PTIME-many steps (data complexity), giving a non-recursive equivalent and thus a *sufficient* boundedness witness. Sufficient conditions like **MFA/MSA** (model-faithful / model-summarizing acyclicity) provide decidable EXPTIME-checkable guarantees of bounded chase.

## 5. Lower Bound

General Datalog boundedness is **undecidable** (reduction from the halting/word problem via GMSV). Even where decidable, lower bounds are steep: monadic boundedness is **PSPACE-hard**; deciding **chase termination** is undecidable for all-instances and remains so for the "some sequence terminates" variant. These impossibilities are *recursion-theoretic* (Turing-undecidable), the strongest form of lower bound.

## 6. The Gap

The problem is **genuinely open** at the boundary: undecidable in general, decidable in restricted fragments, with a **no-man's-land** of single-recursive-rule and guarded/frontier-guarded recursive dependencies whose boundedness status (and exact complexity) is unsettled. Closing it requires either pushing decidability up to a maximal natural fragment or proving undecidability sharply below current thresholds (e.g., for specific sirup classes).

## 7. Current Research (as of June 2026)

Groups: **Benedikt (Oxford)**, **Barceló (PUC/IMFD Chile)**, **Bourhis**, **Calautti / Gottlob (existential rules & chase termination)**, **Bárány / ten Cate (guarded fragments)**. Threads: boundedness of **guarded / frontier-guarded existential rules**; connections between boundedness, **bounded-treewidth** expansions, and the **finite-controllability**/ FO-rewritability frontier; learning-based detection of bounded fragments for compilation *(frontier — verify)*; and boundedness in **Datalog$^\pm$** for ontology-mediated querying.

## 8. Future Work

(1) Settle boundedness/complexity for outstanding single-rule and guarded classes. (2) Unify boundedness with **FO-rewritability** results from description logics / OMQ. (3) Practical static analyses that *certify* boundedness for compiler optimization. (4) Boundedness under **aggregation / negation** (stratified Datalog). (5) Approximate / per-instance boundedness as an optimization heuristic.

## 9. Key References

- **[Foundational]** Gaifman, Mairson, Sagiv, Vardi. *Undecidable Optimization Problems for Database Logic Programs.* PODS 1987 / JACM 1993.
- **[Foundational]** Cosmadakis, Gaifman, Kanellakis, Vardi. *Decidable Optimization Problems for Database Logic Programs.* STOC 1988.
- **[SOTA]** Marcinkowski. *Achilles, Turtle, and Undecidable Boundedness Problems for Small Datalog Programs.* SIAM J. Computing, 1999.
- **[SOTA]** Grahne, Onet / Calautti, Gottlob, Pieris. *Chase Termination & Boundedness for Existential Rules.* PODS/ICDT, 2010s.
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Datalog chapters).

---
*Part of the [DBMS Research catalog](../../README.md).*
