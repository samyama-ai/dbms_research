# Provably-Correct Recovery Verification

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/recovery-correctness-verification` · **Status:** open

## 1. Problem Statement
An IMDB's durability relies on the interplay of **write-ahead logging, checkpointing/snapshotting, and replay**. A bug in any of these — a missed log record, a torn checkpoint, a replay that reorders dependent writes, a fuzzy-checkpoint inconsistency — silently corrupts the recovered state, often undetected until much later. The problem: **formally verify (machine-checked) that a given logging + checkpoint + replay design recovers, after any crash, a state that is *externally consistent* — i.e. reflects exactly a prefix-closed, serializable set of committed transactions consistent with what clients were told — under a realistic crash/persistence model.**

Variants:
- *Decision (verification):* given a recovery protocol $P$ and a crash model $\mathcal{C}$, does $P$ satisfy the recovery correctness specification $\varphi$? (Undecidable in general; the practical target is mechanized proof for a concrete $P$.)
- *Synthesis:* derive a provably-correct recovery procedure from a logging spec.
- *Bug-finding:* exhaustively/model-check small instances for counterexamples (bounded).

## 2. Mathematical Foundations
The specification is **opacity / strict serializability + crash-consistency (prefix recovery)**. Define histories of transactions; the recovered state after a crash at point $\pi$ must equal the state produced by some serial schedule of exactly the transactions whose commit was *durable* at $\pi$, and that set must be **prefix-closed** w.r.t. client acknowledgments (no acknowledged commit lost, no unacknowledged/uncommitted effect surviving) — this is **external consistency** in the Spanner sense (Corbett et al., OSDI 2012).

The crash model must capture **persistence semantics**: which stores have reached non-volatile/replicated stable storage at crash time, allowing reordering and partial (torn) writes within the not-yet-fenced window. This is formalized by **persistency memory models** (Pelley–Chen–Wenisch, "Memory Persistency", ISCA 2014) and crash-consistency logics: **separation logic under crashes** — notably **Perennial / Crash Hoare Logic** (Chajed et al., SOSP 2019; Chen et al., FSCQ, SOSP 2015), which add a *crash condition* and *recovery obligation* to Hoare triples $\{P\}\,c\,\{Q\}\,\{Q_{\text{crash}}\}$. ARIES (Mohan et al., TODS 1992) is the reference algorithm whose invariants (repeating history, redo/undo idempotence, CLRs) are exactly what must be proven: **idempotent replay** and **monotone recovery** are the core lemmas. Linearizability/strict-serializability of the live concurrency control is a precondition.

## 3. State of the Art (SOTA)
- **Systems-SOTA (verified storage):** **FSCQ** (Chen et al., SOSP 2015) — first machine-checked crash-safe file system (Coq, CHL); **Perennial/GoJournal** (Chajed et al., SOSP 2019, OSDI 2021) — verified concurrent crash-safe journaling; **VeriBetrKV** (Hance et al., OSDI 2020) — verified crash-safe key-value store with a B^ε-tree. Verified consensus: **Verdi/IronFleet** (Wilcox et al., PLDI 2015; Hawblitzel et al., SOSP 2015) machine-check replicated state machines (Raft/Paxos) including liveness. Model-checking: **TLA+/TLC** specs of ARIES-style recovery and of logging protocols; **MongoDB/AWS** use TLA+ for replication-recovery design.
- **Theory-SOTA:** ARIES correctness arguments (Mohan et al.) and serializability theory (Bernstein–Hadzilacos–Goodman) give the paper-proof foundation; opacity (Guerraoui–Kapałka) specifies transactional-memory correctness.

## 4. Upper Bound
The constructive upper bound is **existence of fully machine-checked crash-safe storage stacks**: FSCQ, Perennial/GoJournal, and VeriBetrKV demonstrate that logging + recovery for a storage engine can be proven correct end-to-end in a proof assistant under an explicit crash model, with idempotent-replay and prefix-recovery lemmas discharged. IronFleet shows the *full* RSM (incl. recovery-relevant safety and liveness) is mechanizable. These bound the problem: it is *achievable* for concrete systems, at high proof-engineering cost (proof-to-code ratios of $\sim$5–20×).

## 5. Lower Bound
General verification is **undecidable** (Rice's theorem / reduction from halting for arbitrary recovery code over unbounded state), so no algorithm verifies all protocols — only mechanized per-system proofs or bounded model checking are possible. **FLP** bounds verified *liveness* of recovery under asynchrony. Bounded model checking faces **state-explosion** (PSPACE-hard reachability), and the crash/persistency nondeterminism multiplies the state space (every store reordering within the unfenced window). Information-theoretically, recovery cannot reconstruct state that was never made durable — so any "loss-window" $W>0$ design provably cannot be verified to a $W=0$ spec; the spec must match the achievable guarantee (links to *durability-volatile-only*).

## 6. The Gap
We can verify *specific* engines at great cost, and we can model-check *bounded* instances, but there is **no scalable, reusable methodology** that takes a real IMDB's logging+checkpoint+replay and yields a machine-checked external-consistency proof against a realistic persistency model with concurrency — proofs don't compose across the live concurrency-control layer and the crash-recovery layer cleanly, and persistency-model fidelity to real hardware/replication is incomplete. Genuinely open: closing it needs compositional crash+concurrency logics and far lower proof cost (more automation/synthesis).

## 7. Current Research (as of June 2026)
Threads: compositional crash-and-concurrency separation logics (Perennial line) extended to full transactional engines; verified MVCC + recovery co-proofs; auto-active verification (Dafny/Verus) to cut proof cost; SMT/model-checking of persistency-model reorderings for recovery *(frontier — verify)*; verified durability over replicated (network-only) stable storage tying into consensus proofs. Groups: MIT (Kaashoek/Zeldovich — FSCQ/Perennial), CMU (Chajed), UW (Tatlock/Wang — verified systems, VeriBetrKV), Microsoft Research (IronFleet/Verus), Technion/EPFL (transactional opacity).

## 8. Future Work
- Compositional logics proving concurrency control and crash recovery *together* for one engine.
- Drastically cheaper proofs via synthesis / auto-active verification at engine scale.
- High-fidelity persistency + replication models so the verified spec matches real durability ($W$).

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992.
- **[Foundational]** Pelley, S., Chen, P., Wenisch, T. *Memory Persistency.* ISCA, 2014.
- **[SOTA]** Chen, H., Ziegler, D., Chajed, T., Chlipala, A., Kaashoek, M. F., Zeldovich, N. *Using Crash Hoare Logic for Certifying the FSCQ File System.* SOSP, 2015.
- **[SOTA]** Chajed, T., Tassarotti, J., Kaashoek, M. F., Zeldovich, N. *Verifying Concurrent, Crash-Safe Systems with Perennial.* SOSP, 2019.
- **[SOTA]** Hance, T., et al. *Storage Systems are Distributed Systems (So Verify Them That Way) — VeriBetrKV.* OSDI, 2020.
- **[SOTA]** Hawblitzel, C., et al. *IronFleet: Proving Practical Distributed Systems Correct.* SOSP, 2015.
- **[Foundational]** Corbett, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
