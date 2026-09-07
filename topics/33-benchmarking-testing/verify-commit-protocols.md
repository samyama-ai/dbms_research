---
id: 33-benchmarking-testing/verify-commit-protocols
title: "Verifying Distributed Commit Protocols"
topic: 33-benchmarking-testing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Verifying Distributed Commit Protocols

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/verify-commit-protocols` · **Status:** partially-solved

## 1. Problem Statement
Distributed commit protocols — Two-Phase Commit (2PC), Three-Phase Commit (3PC), and consensus-backed commit (Paxos/Raft/EPaxos commit, Spanner-style 2PC-over-Paxos) — must guarantee **atomicity** (all-or-nothing across participants) under crashes, message loss, and partitions. The verification problem is to produce **machine-checked** proofs of **safety** (no two participants disagree on commit/abort; durability of decided outcomes) and **liveness** (transactions eventually decide under partial synchrony) for the protocol **as implemented**, not merely an idealized pseudocode abstraction.

Variants:
- **Spec-level verification:** prove the abstract protocol satisfies its consistency contract (largely done).
- **Implementation-level verification (the hard, open part):** prove the *running code* — with its real message formats, persistence, recovery, timeouts, and concurrency — refines the verified spec.
- **Liveness under realistic timing:** 2PC blocks if the coordinator fails; proving conditional progress requires a precise failure/synchrony model.

## 2. Mathematical Foundations
Specify a protocol as a state-transition system $M=(S, S_0, \to)$. **Safety** is an invariant $\square\,\varphi$ (e.g., $\text{decided}_i=\text{commit} \wedge \text{decided}_j=\text{abort}$ is unreachable); **liveness** is $\Diamond\psi$ under fairness assumptions — expressed in **LTL/TLA**. Proof obligations are discharged by **inductive invariants** $I$ with $S_0\subseteq I$ and $I$ closed under $\to$, plus a **ranking/variant function** for termination.

Two verification paradigms:
- **Model checking** (finite/bounded): TLA+/TLC, Spin, P — exhaustive over a bounded configuration; **parameterized** verification (any $n$ participants) needs cutoff theorems or symmetry/abstraction.
- **Deductive (theorem proving):** Coq/Rocq, Isabelle/HOL, Ivy, Dafny — prove inductive invariants over unbounded state. **Refinement** (Abadi–Lamport) links abstract spec to implementation: $\text{Impl} \sqsubseteq \text{Spec}$.

FLP and CAP constrain *what* can be proven: liveness is only provable under **partial synchrony** (Dwork–Lynch–Stockmeyer) or with failure detectors $\Diamond S$ (Chandra–Toueg). Atomic commit's blocking is captured by Skeen's classic result: no protocol is **non-blocking** in fully asynchronous settings with arbitrary failures.

## 3. State of the Art (SOTA)
- **IronFleet** (Hawblitzel et al., SOSP 2015): first end-to-end *machine-checked* proof (in Dafny) of a Paxos-based replicated state machine connecting high-level safety+liveness down to executable code via refinement — the template for implementation-level verification.
- **Verdi** (Wilcox et al., PLDI 2015): Coq framework with *verified system transformers*; produced a verified Raft.
- **IVy** (Padon, Shoham, et al., PLDI 2016): decidable EPR fragment for inductive-invariant verification, applied to Paxos variants and commit-style protocols with push-button checking.
- **TLA+/PlusCal** specs of 2PC and consensus (Lamport) are textbook and machine-checked at spec level; used in production at AWS for protocol designs.
- Recent: verified Raft/Paxos refinements and SMT-driven invariant inference (DistAI, SWISS, P language at AWS/Microsoft).

## 4. Upper Bound
For the **decidable** fragment (EPR / quantifier-restricted, Ivy), checking a *candidate* inductive invariant is decidable and often fast; verification effort shifts to *finding* the invariant. Refinement frameworks (IronFleet, Verdi) give a methodology that, with significant human proof effort, yields a *complete* end-to-end guarantee — the strongest available "upper bound" on assurance. Bounded model checking (TLC, Spin) is complete *up to* the explored bound and fully automatic. Automated invariant inference (DistAI 2021, SWISS) can synthesize inductive invariants for many Paxos/commit protocols without human guidance.

## 5. Lower Bound
**Skeen's impossibility:** no atomic commit protocol is non-blocking in an asynchronous system subject to communication failures — 2PC *must* block on coordinator failure; this bounds what liveness can be proven. **FLP** rules out guaranteed asynchronous termination. **Parameterized verification** of distributed protocols is **undecidable** in general (reductions from reachability of counter machines), so fully automatic verification for arbitrary $n$ is impossible; the EPR fragment regains decidability only by syntactic restriction. Invariant inference is at least as hard as the underlying (undecidable) reachability problem.

## 6. The Gap
"Partially solved": **spec-level safety/liveness is verified** for the main protocols, and IronFleet/Verdi show implementation-level verification is *possible*. The gap is **cost and fidelity**: end-to-end machine-checked proofs of *production* commit code (with real persistence, recovery edge cases, performance optimizations, and message encodings) remain rare and labor-intensive. Undecidability blocks full automation; the practical open problem is closing the spec↔implementation gap cheaply and keeping proofs in sync as code evolves.

## 7. Current Research (as of June 2026)
- **Automated inductive-invariant inference** maturing (DistAI, SWISS, P-based industrial use at AWS) toward push-button verification of commit/consensus *(frontier — verify)*.
- Verified storage + commit stacks (linking transaction commit to verified durable logs); proof-producing compilers narrowing the code-gap.
- LLM-assisted invariant/proof synthesis for TLA+/Ivy *(frontier — verify)*.
- Groups: Lamport (TLA+), Shoham/Padon/Sagiv (Ivy), Hawblitzel/Lorch/Parno (IronFleet/Dafny), Sergey (deductive distributed verification, Disel), Wilcox/Tatlock/Ernst (Verdi).

## 8. Future Work
- Cheap, maintainable refinement proofs that track evolving implementations.
- Verified liveness under realistic partial-synchrony models, not just safety.
- Compositional proofs for layered designs (2PC-over-Paxos, deterministic-transaction commit).
- Bridging verified protocol cores with verified concurrency/recovery in the surrounding engine.

## 9. Key References
- **[Foundational]** Skeen, Stonebraker. *A Formal Model of Crash Recovery in a Distributed System.* IEEE TSE, 1983. — [DOI](https://doi.org/10.1109/TSE.1983.236608)
- **[Foundational]** Lamport. *The Part-Time Parliament (Paxos).* ACM TOCS, 1998. — [DOI](https://doi.org/10.1145/279227.279229)
- **[SOTA]** Hawblitzel, Howell, Kapritsos, Lorch, Parno, et al. *IronFleet: Proving Practical Distributed Systems Correct.* SOSP 2015. — [DOI](https://doi.org/10.1145/2815400.2815428)
- **[SOTA]** Wilcox, Woos, Panchekha, Tatlock, Ernst, et al. *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems.* PLDI 2015. — [DOI](https://doi.org/10.1145/2737924.2737958)
- **[SOTA]** Padon, McMillan, Panda, Sagiv, Shoham. *Ivy: Safety Verification by Interactive Generalization.* PLDI 2016. — [DOI](https://doi.org/10.1145/2908080.2908118)
- **[Foundational]** Dwork, Lynch, Stockmeyer. *Consensus in the Presence of Partial Synchrony.* JACM, 1988. — [DOI](https://doi.org/10.1145/42282.42283)

## 10. Worked Example

Trace 2PC blocking — the safety/liveness tension a verifier must capture. Coordinator $C$, participants $P_1,P_2$. Phase 1: $C$ sends `PREPARE`; both reply `YES` and durably log a *prepared* (in-doubt) state. Phase 2: $C$ logs `COMMIT` and sends it to $P_1$, which commits — then **$C$ crashes before messaging $P_2$**.

Now $P_2$ is stuck in *prepared*: it may not unilaterally abort (a TLA+ safety invariant $\square\neg(\text{decided}_1=\text{commit}\wedge\text{decided}_2=\text{abort})$ forbids disagreeing with $P_1$'s commit), and it cannot commit without the decision. It **blocks** until $C$ recovers and replays its log.

A model checker over the state space $\{\text{working},\text{prepared},\text{committed},\text{aborted}\}^{3}$ confirms the safety invariant holds on *all* $4^3=64$ reachable configurations, but the liveness property $\Diamond(\text{decided}_2)$ **fails** under the fair-but-crash-prone schedule above — exactly Skeen's impossibility ($n=2$): no asynchronous commit protocol is non-blocking. This is why verifiers prove liveness only under partial synchrony (eventual coordinator recovery), not unconditionally.

---
*Part of the [DBMS Research catalog](../../README.md).*
