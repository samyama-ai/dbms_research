# Crash-consistency testing/fuzzing

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/crash-consistency-fuzzing` · **Status:** empirically-open

## 1. Problem Statement
A database engine claims durability and atomicity guarantees (e.g., "committed transactions survive a crash; no torn or partially-applied transactions are visible after recovery"). **Crash-consistency testing** asks: can we *systematically generate* crash schedules — points at which the process dies and subsets of pending I/O that did or did not reach stable storage — that drive a real engine into a state violating its claimed guarantees after recovery?

Formally, given a program execution producing a sequence of persistence-relevant operations (writes, flushes, FUA/barriers, fsyncs, rename, msync), a crash schedule is a *prefix-and-reorder* of the global store order consistent with the storage stack's allowed reorderings. The task is to search the space of such schedules for one whose post-recovery state violates a consistency oracle.

**Variants.** *Decision:* does there exist a reachable crash state that, after recovery, violates invariant $\Phi$? *Search/optimization:* find a minimal such schedule (fewest reordered/dropped writes) to ease debugging. *Coverage:* maximize the fraction of distinct persistence orderings or recovery code paths exercised under a fixed test budget. Because exhaustive enumeration is astronomically large, this is treated as a *fuzzing/bounded-model-checking* problem rather than a solved decision procedure — hence **empirically-open**.

## 2. Mathematical Foundations
Let $O = \langle o_1,\dots,o_n\rangle$ be the persistence operations of an execution. The storage model defines a **persistence partial order** $\prec_p$: $o_i \prec_p o_j$ iff every crash-consistent state containing $o_j$ also contains $o_i$ (e.g., a write before its dependent `fsync`, or writes separated by a barrier). A **crash state** is a *down-set* (order ideal) $S \subseteq O$ of $\prec_p$ — closed under $\prec_p$-predecessors — optionally with per-block atomicity/torn-write granularity. The set of crash states is the distributive lattice of order ideals (Birkhoff's theorem); its size is exponential in the antichains of $\prec_p$.

A **recovery function** $R$ maps a crash state to a logical database state; the system is crash-consistent w.r.t. invariant $\Phi$ iff $\forall S\,(\text{down-set})\colon \Phi(R(S))$. The test problem is to search the lattice for a counterexample. Weakening the model (allowing reorderings the device permits but the engine assumes away — e.g., write-cache reordering without FUA) enlarges the ideal lattice and exposes bugs. Coverage can be cast as maximizing a **submodular** function over chosen schedules (marginal new code paths diminish), making greedy/budgeted selection near-optimal $(1-1/e)$.

## 3. State of the Art (SOTA)
**Systems-SOTA.** *ALICE* (Pillai et al., OSDI 2014) introduced application-level crash-consistency testing via abstract persistence models and uncovered bugs across many systems. *CrashMonkey/B³* (Mohan et al., OSDI 2018) systematically bounded-model-checks file-system crash consistency. *Jepsen* (Kingsbury) stress-tests distributed databases under faults including process crashes and partitions, with the *Knossos/Elle* linearizability and transactional-anomaly checkers. *Hermit*/record-replay and *PACE* extend crash injection to distributed protocols. For persistent memory, *Yat*, *PMTest*, *XFDetector*, *Jaaru*, and *Agamotto* find PM crash-consistency bugs via model checking and symbolic/coverage-guided search. *Sibylla*/recovery fault injection and *Vinter* (PM, 2022) advance automation.

**Theory-SOTA.** Bounded model checking and partial-order reduction (DPOR) over the persistence partial order; no efficient *complete* decision procedure exists for realistic engines.

## 4. Upper Bound
With persistence partial order $\prec_p$, the number of crash states equals the number of order ideals, exponential in general but polynomial when $\prec_p$ is a chain (sequential fsync discipline). Bounded model checking with **dynamic partial-order reduction** explores one representative per Mazurkiewicz trace, reducing the search from $n!$ orderings toward the number of *distinct* persistence equivalence classes. Coverage-guided fuzzing achieves near-optimal $(1-1/e)$ path coverage under a budget via greedy submodular selection. These are heuristic upper bounds on *test effectiveness*, not on the underlying decision problem.

## 5. Lower Bound
The underlying decision problem — "does a crash state violating $\Phi$ exist?" — is at least as hard as reachability in the recovery program and is undecidable in the general (Turing-complete recovery logic) case; for bounded executions it is NP-hard via the exponential antichain structure of the ideal lattice (reduction from set-cover-style coverage and from reachability in concurrent programs, which is NP-hard / PSPACE-complete depending on formulation). Thus no polynomial-time complete tester can exist unless P=NP, justifying the fuzzing/BMC posture. The hardness is *computational/combinatorial*, not information-theoretic.

## 6. The Gap
The gap is between **completeness** (a sound-and-complete decision procedure, infeasible at scale) and **coverage** (fuzzers find many but provably not all bugs). It is genuinely open whether realistic engine recovery code admits a tractable *abstraction* whose crash-consistency is decidable while preserving the bugs. Closing it would require either a verified recovery DSL with a decidable crash-state theory, or a coverage metric with a provable bug-detection guarantee. Today the field measures success empirically (bugs found), not by closing this gap.

## 7. Current Research (as of June 2026)
Active: coverage-guided crash fuzzing combined with sanitizers for storage engines; PM crash-consistency now extended to CXL persistent memory and to RDMA-attached storage *(frontier — verify)*. Jepsen continues auditing commercial databases. LLM-assisted generation of crash-schedule test cases and of invariant oracles is emerging *(frontier — verify)*. Groups: UT Austin (Vijay Chidambaram's lab — ALICE/CrashMonkey lineage), UC Irvine (Brian Demsky — Jaaru/persistency model checking), Jepsen/independent (Kyle Kingsbury), and systems groups extending DPOR to durability.

## 8. Future Work
(i) Verified, minimized counterexample reduction (delta-debugging crash schedules). (ii) Realistic device models that capture write-cache and FUA semantics faithfully. (iii) Provable coverage guarantees tying schedule selection to recovery code paths. (iv) Continuous-integration crash fuzzing as a default gate for OLTP engines. (v) Unifying distributed crash+partition fault models with single-node persistence models.

## 9. Key References
- **[Foundational]** Pillai, T. et al. *All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications (ALICE).* OSDI, 2014.
- **[SOTA]** Mohan, J., Martinez, A., Ponnapalli, S., Raju, P., Chidambaram, V. *Finding Crash-Consistency Bugs with Bounded Black-Box Crash Testing (CrashMonkey/B³).* OSDI, 2018.
- **[SOTA]** Gao, H., Demsky, B. et al. *Jaaru: Efficient Model Checking of Persistent Memory Programs.* ASPLOS, 2021.
- **[SOTA]** Kingsbury, K., Alvaro, P. *Elle: Inferring Isolation Anomalies from Experimental Observations.* PVLDB, 2020.
- **[Survey]** Liu, S. et al. *Cross-Failure Bug Detection in Persistent Memory Programs (XFDetector) and the PM testing landscape.* ASPLOS, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
