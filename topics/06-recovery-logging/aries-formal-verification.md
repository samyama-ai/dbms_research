---
id: 06-recovery-logging/aries-formal-verification
title: "Provably correct ARIES variants"
topic: 06-recovery-logging
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Provably correct ARIES variants

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/aries-formal-verification` · **Status:** partially-solved

## 1. Problem Statement

ARIES is the canonical recovery algorithm behind most relational engines. Its correctness is subtle: it combines write-ahead logging, **physiological** redo, the three-phase **Analysis → Redo → Undo** restart, idempotent redo via per-page LSNs, **Compensation Log Records (CLRs)** with `UndoNxtLSN` chaining to guarantee bounded, restart-safe rollback, fuzzy checkpoints, nested top actions, and partial rollbacks. Each optimization interacts with crash recovery, and a crash can occur *during recovery itself* (repeated failures).

**Problem:** produce a **machine-checked proof** (in a proof assistant: Coq/Rocq, Isabelle/HOL, or via a verified model checker / refinement framework like TLA+/Ivy with a checked proof) that a *full-featured* ARIES implementation — including all the above optimizations — correctly recovers a transaction-consistent state under an arbitrary crash-and-restart adversary, and that recovery is **idempotent** (recoverable from crashes mid-recovery).

Variants: (a) verify the *abstract algorithm*; (b) verify a *concrete implementation* (code-level, with the abstract proof as refinement); (c) verify specific optimizations (fuzzy checkpointing, CLRs, nested top actions) compose.

## 2. Mathematical Foundations

The specification is a **refinement / linearizability-style** statement: the durable state after restart must be observationally equivalent to a *prefix-consistent* serial state — all committed transactions' effects present, all loser transactions' effects absent.

Formally, model the log as a sequence $L = \langle r_1,\dots,r_m\rangle$ of records, each carrying $\mathit{LSN}$, $\mathit{prevLSN}$, page id, before/after images, and for CLRs an $\mathit{UndoNxtLSN}$. Define page state $\mathit{page}.\mathit{pageLSN}$. The core **redo invariant**: applying record $r$ to page $p$ is a no-op iff $p.\mathit{pageLSN} \ge r.\mathit{LSN}$ — giving idempotence: $\mathit{redo}\circ\mathit{redo}=\mathit{redo}$. The **WAL invariant**: $\forall p:\ \mathit{persisted}(p) \Rightarrow \mathit{persisted}(\text{log up to } p.\mathit{pageLSN})$.

Undo correctness uses a well-founded order: the `UndoNxtLSN` chain strictly decreases, so rollback terminates, and CLRs are redo-only (never undone), making the undo phase *itself* idempotent under re-crash. The proof obligation is invariant preservation under the transition relation that includes a *crash* transition (zeroing volatile state, keeping persistent state) at any point, closed under the analysis/redo/undo step relation — a standard inductive-invariant + well-founded-termination argument.

## 3. State of the Art (SOTA)

- **Crash-Hoare Logic / FSCQ** (Chen, Chajed, Kaashoek, Zeldovich; SOSP 2015) — verified a crash-safe file system with a logging layer in Coq, introducing *crash conditions* and *recovery reasoning*; methodology directly applicable but the artifact is a file-system journal, not full ARIES.
- **Perennial / GoJournal** (Chajed et al.; OSDI 2021) — machine-checked, concurrent, crash-safe write-ahead journaling with recovery, in Coq; the strongest verified *WAL with recovery* artifact, but simpler than ARIES (no fine-grained physiological undo with CLR chains, no nested top actions).
- **TLA+/PlusCal models** of recovery and of ARIES-like restart exist and are model-checked for bounded instances, but model checking is not a full proof.
- Pen-and-paper correctness arguments for ARIES (Mohan 1992; Kuo's formal treatment, 1990s) predate machine checking. A complete, mechanically-checked proof of *full* ARIES with all optimizations is not yet published — hence *partially-solved*.

## 4. Upper Bound

What is achievable today: machine-checked, *implementation-level* proofs of crash-safe WAL with recovery (Perennial/GoJournal) including concurrency, at the cost of a *restricted* logging discipline (redo-only or simple undo, page-granular). Verification effort is large but tractable: proof-to-code ratios of roughly 10–20:1 lines. For the *abstract* ARIES algorithm, an Isabelle/Coq inductive-invariant proof of Analysis/Redo/Undo idempotence is within reach and partially done in the literature for simplified variants.

## 5. Lower Bound

There is no computational hardness lower bound — correctness verification is a (manual + automated) proof effort, undecidable in general but feasible for fixed protocols. The "lower bound" is the *specification difficulty*: capturing the full crash adversary (crash during recovery, partial page writes, torn writes) and proving optimizations *compose*. Counterexamples found by model checking show naive CLR or fuzzy-checkpoint handling can break recoverability under repeated crashes — i.e., the invariants are genuinely necessary, not slack. Cell-probe/communication lower bounds are not the relevant frame; the barrier is proof-engineering and faithful modeling.

## 6. The Gap

The gap is between (a) verified *simplified* WAL with recovery (achieved) and (b) verified *full-featured ARIES* with physiological logging, CLRs + `UndoNxtLSN`, nested top actions, partial rollbacks, fuzzy checkpoints, and re-crash idempotence — *and* a refinement down to a real implementation. No single artifact yet covers all optimizations together. Closing it needs: a faithful crash model including torn/out-of-order persistence, modular proofs that each optimization preserves the redo/WAL/undo-termination invariants, and a refinement to executable code.

## 7. Current Research (as of June 2026)

Active: the Perennial/Verus/Iris-based verified-storage community (MIT/CSAIL — Kaashoek, Zeldovich, Chajed now at Wisconsin; VMware Research) extending verified journaling toward richer recovery semantics; verified key-value/storage engines (VeriBetrKV, Verus-based work) *(frontier — verify)*. Separation-logic + crash reasoning (Iris, "Perennial 2.0") is the dominant toolchain. A 2025–2026 direction targets verifying *physiological* (not just physical) redo and concurrent ARIES-style undo *(frontier — verify)*.

## 8. Future Work

- A modular, reusable formalization of WAL/ARIES invariants reusable across engines.
- Machine-checked composition proofs for CLRs, nested top actions, and fuzzy checkpoints together.
- Refinement from the verified abstract algorithm to a production engine's recovery code.
- Extending proofs to NVM persistency models (out-of-order persist) rather than idealized stable storage.

## 9. Key References

- **[Foundational]** C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh, Peter Schwarz. *ARIES.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)
- **[SOTA]** Haogang Chen, Daniel Ziegler, Tej Chajed, Adam Chlipala, M. Frans Kaashoek, Nickolai Zeldovich. *Using Crash Hoare Logic for Certifying the FSCQ File System.* SOSP, 2015. — [DOI](https://doi.org/10.1145/2815400.2815402)
- **[SOTA]** Tej Chajed, Joseph Tassarotti, Mark Theng, M. Frans Kaashoek, Nickolai Zeldovich, et al. *GoJournal: A Verified, Concurrent, Crash-Safe Journaling System.* OSDI, 2021. — [USENIX](https://www.usenix.org/conference/osdi21/presentation/chajed)
- **[SOTA]** Ralf Jung et al. *Iris: Higher-Order Concurrent Separation Logic.* JFP / POPL, 2018 (foundation for Perennial). — [DOI](https://doi.org/10.1017/S0956796818000151)

## 10. Worked Example

A re-crash during undo shows why CLRs are necessary. Transaction $T_1$ writes log records and then aborts; the volatile log is:

| LSN | record | prevLSN | page | content |
|-----|--------|---------|------|---------|
| 10 | update | — | P1 | A: 5→9 |
| 20 | update | 10 | P1 | B: 0→7 |

Rollback of LSN 20 writes a **CLR** at LSN 30 (undo of 20, sets `UndoNxtLSN=10`) and applies it to P1, bumping `pageLSN`. Suppose the system **crashes again** before undoing LSN 10.

On restart, Analysis finds $T_1$ a loser; Redo re-applies committed/CLR records idempotently — including the CLR at LSN 30, whose effect on P1 is a no-op since $\mathit{page}.\mathit{pageLSN}=30 \ge 30$. Undo then resumes at $\mathit{UndoNxtLSN}=10$ (not 20 — the CLR records that 20 is already undone), undoes LSN 10, and writes a final CLR. Because CLRs are **redo-only and never undone**, the `UndoNxtLSN` chain strictly decreases $30\to10\to\bot$, so undo terminates and is idempotent across arbitrarily many re-crashes — the core invariant the proof must establish.

---
*Part of the [DBMS Research catalog](../../README.md).*
