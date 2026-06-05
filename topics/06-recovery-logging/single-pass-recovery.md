# Single-pass vs multi-pass recovery

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/single-pass-recovery` · **Status:** open

## 1. Problem Statement
ARIES recovery proceeds in **three passes** over the log: **analysis** (reconstruct the dirty-page table and transaction table from the last checkpoint to the log end, identifying losers and the redo start point), **redo** (replay history forward, repeating *all* logged actions from the oldest dirty-page LSN), and **undo** (roll back losers backward). Each pass exists for a reason — analysis needs the end of the log to know who lost, redo's start point depends on analysis's dirty-page LSNs, and undo needs the post-redo state. The question is: **under what conditions can ARIES's three-pass recovery be provably reduced to two passes, one pass, or constant-work "instant" recovery, without losing generality** (i.e., still recovering every workload ARIES handles: fine-grained locking, partial rollbacks, nested top actions, CLRs)?

Variants:
- **Decision:** given a recovery specification (durability + atomicity guarantees) and a log format, does a correct $k$-pass recovery algorithm exist for $k<3$?
- **Lower bound / impossibility:** prove a minimum number of *sequential log scans* any correct recovery must perform under a given log/checkpoint model.
- **Design/optimization:** minimize total I/O (passes × log size) and time-to-first-transaction, possibly trading more logging or checkpointing at runtime for fewer recovery passes.

## 2. Mathematical Foundations
Model the log as a totally ordered sequence of records $r_1\!\prec\!\cdots\!\prec\!r_n$ with LSNs; recovery is a function $R(\text{log},\text{checkpoint},\text{disk})\to$ the unique committed-prefix state. Correctness is the **repeating-history** invariant: redo brings the database to the exact state at crash, *then* undo removes losers — formalized via per-page LSN comparison ($\text{redo if }LSN_{\text{rec}}>LSN_{\text{page}}$) guaranteeing **idempotent, restartable** recovery (recovery of a recovery yields the same result).

The pass count is fundamentally about **information dependencies / scan direction**. Analysis is a forward scan computing the loser set $L$ and the firstDirtyLSN; redo is forward; undo is backward. The dependency $\text{redo-start} \Leftarrow \text{analysis}$ is what forbids fusing them naively. Reducing passes is an exercise in **streaming computation with bounded state**: can the quantities analysis computes (dirty-page table, loser set) be derived *online* during a single forward scan, or pushed to runtime (logged eagerly)? This connects to **read-once / one-pass streaming** lower bounds: if determining the redo start requires the end of the log, a single forward pass cannot both decide it and act on it — a two-scan lower bound unless the runtime log is enriched.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Real engines already collapse passes opportunistically. **Fuzzy checkpoints + a recent dirty-page table** let analysis start near the log end, shrinking each pass. **Hekaton** (in-memory, Microsoft) does effectively single-pass redo from the checkpoint + tail log because there is no buffer-pool/disk-LSN mismatch. **Graefe's instant recovery** turns recovery into on-demand, per-page redo triggered by access — amortizing replay to *zero* up-front passes and making the system available almost immediately.
- **Theory-SOTA:** there is no clean theorem stating "$k$ passes is necessary and sufficient for recovery class $X$." Most reductions are engineering arguments tied to a particular log/checkpoint design rather than general impossibility results — hence **open**.

## 4. Upper Bound
Two-pass recovery is achievable when runtime logging is enriched: log enough at commit/abort time that the **loser set and redo start are known from the checkpoint alone**, fusing analysis into redo (one forward pass) plus one undo pass. **One-pass / zero-pass** is achievable for in-memory and instant-recovery engines: redo from the most recent checkpoint with no separate analysis (Hekaton-style), or defer all replay to first-touch page faults so up-front recovery work is $O(1)$ and the system is available immediately (Graefe et al.). These hold in specific runtime-logging/checkpointing models, not for arbitrary ARIES logs.

## 5. Lower Bound
For a **vanilla ARIES log with fuzzy checkpoints**, a forward scan cannot determine the redo start point without reaching the log end (the dirty-page table at crash is only known there), giving an intuitive **2-scan lower bound** in a read-once streaming model: any algorithm that both computes the loser/dirty set *and* applies redo correctly needs the end-of-log information before it can safely skip records, forcing either two forward scans or unbounded buffering of the entire log (an $\Omega(n)$ space/Ω(log-size) cost). This is an information-dependency argument, not an established complexity-theoretic theorem; a fully general lower bound parameterized by the recovery class is not known.

## 6. The Gap
The gap is the absence of a **general theory** linking (a) the guarantees a recovery class must provide (fine-grained locking, partial rollback, nested top actions) and the runtime-logging budget, to (b) the *minimum number of log scans / I/O* recovery requires. We have point solutions (instant recovery ≈ 0 up-front passes; Hekaton ≈ 1) and ARIES's 3, but no impossibility result saying "for class $X$ with checkpoint scheme $Y$, fewer than $k$ passes is impossible." Closing it means either a matching streaming lower bound or a constructive single-pass algorithm general enough to subsume ARIES's feature set.

## 7. Current Research (as of June 2026)
- **Instant / constant-time recovery** continues (Graefe, Sauer, Härder lineage) — single-page and single-transaction failures, lazy on-demand replay — now extended to media and node failures *(frontier — verify)*.
- Log-disaggregated clouds (Aurora/Socrates/Neon) make "analysis" implicit and apply redo per-page asynchronously, effectively eliminating up-front passes; formalizing this as 0/1-pass recovery is open *(frontier — verify)*.
- Persistent-memory engines with stable byte-addressable state collapse the redo pass entirely, shifting attention to undo-only recovery *(frontier — verify)*.

## 8. Future Work
- A general pass-count lower bound parameterized by recovery class and logging budget.
- A provably single-pass recovery algorithm covering ARIES's full feature set, or an impossibility proof.
- Trade-off curves: runtime logging/checkpoint cost vs. recovery passes vs. time-to-first-transaction.
- Unifying instant recovery, in-memory single-pass redo, and classical ARIES under one model.

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H. & Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** Gray, J. & Reuter, A. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)
- **[SOTA]** Diaconu, C. et al. *Hekaton: SQL Server's Memory-Optimized OLTP Engine.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2463710)
- **[SOTA]** Graefe, G. *Instant Recovery for Data Center Savings.* ACM SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814716)
- **[SOTA]** Sauer, C., Graefe, G. & Härder, T. *Instant Restore After a Media Failure.* ADBIS 2017 / VLDB Journal, 2018. — [arXiv](https://arxiv.org/abs/1702.08042)
- **[Survey]** Härder, T. & Reuter, A. *Principles of Transaction-Oriented Database Recovery.* ACM Computing Surveys, 1983. — [DOI](https://doi.org/10.1145/289.291)

## 10. Worked Example

Tiny log after the last fuzzy checkpoint, LSNs $10$–$50$ on pages $A,B,C$:

| LSN | record | page | note |
|----|--------|------|------|
| 10 | T1 update | A | |
| 20 | T2 update | B | |
| 30 | T1 update | C | |
| 40 | T1 **commit** | — | T1 wins |
| 50 | T2 update | A | crash after this; T2 never commits $\Rightarrow$ loser |

The checkpoint's dirty-page table had $\text{recLSN}(A)=10,\ \text{recLSN}(B)=20$. **Analysis** (forward scan to LSN 50) is what tells us the loser set is $\{T2\}$ and that $C$ became dirty at 30 — but you cannot know T2 lost *until you reach the end of the log* and see no commit. That is the 2-scan dependency: redo must start from $\min\text{recLSN}=10$, yet whether to undo LSN 20/50 depends on end-of-log information.

**Redo** replays 10,20,30,50 wherever $\text{LSN}_{\text{rec}} > \text{LSN}_{\text{page}}$ (repeating history). **Undo** then rolls back T2's 20 and 50 via CLRs. A single forward pass cannot both decide T2's fate and safely apply/skip its records without buffering the whole log ($\Omega(n)$ space) — illustrating section 5's lower bound. Hekaton-style engines sidestep this: with no page/disk-LSN mismatch, redo replays the checkpoint + tail in one pass with no separate analysis.

---
*Part of the [DBMS Research catalog](../../README.md).*
