# Constant-time recovery theory

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/constant-time-recovery-bounds` · **Status:** empirically-open

## 1. Problem Statement

Classical recovery time grows with the log: ARIES redo scans from the last checkpoint, so restart time scales with the volume of work since the checkpoint, and large undo work scales with the longest in-flight transaction. "Instant" or **constant-time recovery (CTR)** aims to make the database *available* in time **independent of log size and database size** — the system comes online almost immediately and finishes redo/undo lazily, on-access, in the background.

**Problem:** characterize *which workloads and storage models admit recovery whose time-to-availability is $O(1)$* (independent of $|\text{log}|$ and $|\text{DB}|$), and quantify the residual cost: per-access redo latency, background completion time, and the steady-state overhead paid during normal operation to *enable* instant recovery.

Variants: (a) *decision* — does a given (workload, storage, durability-semantics) triple admit $O(1)$ time-to-first-availability? (b) *optimization* — minimize the steady-state tax (extra logging/versioning) subject to $O(1)$ availability; (c) what is recovered "instantly" — read availability, write availability, or full-consistency availability?

## 2. Mathematical Foundations

Decompose recovery cost. Let $T_{\text{avail}}$ = time to accept queries, $T_{\text{redo}}$ = work to bring all pages current, $T_{\text{undo}}$ = work to roll back losers. ARIES has $T_{\text{avail}} = \Theta(T_{\text{redo}} + T_{\text{undo}})$. CTR seeks $T_{\text{avail}} = O(1)$ by deferring: $T_{\text{redo}}$ becomes a sum of *per-access* lazy redo costs amortized over future accesses, and $T_{\text{undo}}$ is made invisible via versioning.

The clean theoretical handle is **multi-versioning**. If each row carries version/visibility metadata and aborted versions are simply *not visible* (rather than physically undone), undo is logically instantaneous: recovery only needs the set of loser transaction IDs, $O(|\text{losers}|)$ bits, and undo becomes lazy garbage collection. Redo can be made lazy if pages are self-describing (per-page `pageLSN` + access-time replay), so a page is brought current only when touched: amortized redo cost is $\sum_p \mathbb{1}[\text{accessed}]\cdot \text{redo}(p)$, which is $O(1)$ for the *first* query touching few pages.

The condition for true $O(1)$ availability is thus: (i) **bounded loser set** that can be loaded in $O(1)$; (ii) **on-access lazy redo** so no eager full-DB scan is needed; (iii) a **durability/visibility model** (MVCC) where rollback is logical. Where these fail — e.g., long-running transactions with huge undo footprints, or single-version in-place engines requiring physical undo — $O(1)$ availability is not achievable without unbounded deferred work surfacing on the critical path.

## 3. State of the Art (SOTA)

- **Constant Time Recovery in Azure SQL Database** (Antonopoulos, Byrne, Chen, Diaconu, et al.; VLDB 2019) — the landmark systems result: combines a **persistent version store (PVS)** with MVCC so undo is logical, plus a redesigned logical-revert; achieves recovery time *independent of transaction sizes and the amount of in-flight work*. This is the de facto SOTA and the reason the area is "empirically-open" rather than open — it works in production but lacks a general theory of *when* it must hold.
- **Hekaton / in-memory MVCC recovery** (Diaconu et al., SIGMOD 2013; Larson et al.) — checkpoint + parallel log replay; recovery scales with data, motivating CTR.
- **Instant recovery / "Instant Restart"** line (Sauer, Graefe, Härder; ICDE/EDBT 2015–2018) — on-demand single-page redo and on-demand undo so the system is available immediately and self-heals on access.

## 4. Upper Bound

Best achieved (systems): **$T_{\text{avail}} = O(1)$ in practice** — Azure SQL CTR makes time-to-availability independent of log and transaction size; Instant Restart makes it independent via on-demand page redo. The cost is moved into: (a) a steady-state tax (persistent version store maintenance, richer per-row metadata) and (b) per-access redo latency on first touch of a stale page (one log-region replay, typically $O(\log)$ records per page). Background cleanup completes in $O(|\text{deferred work}|)$ but off the critical path.

## 5. Lower Bound

No NP-hardness; the bound is *workload-conditional* and information-theoretic. To make *any* page readable consistently, you must eventually apply $\Omega(\text{its outstanding redo})$ — total work is conserved; CTR only *reschedules* it. So $\sum_p T_{\text{avail-of-}p} = \Omega(T_{\text{redo}})$: you cannot make *all* pages instantly current, only the *first few accessed*. For engines without multi-versioning, physical undo of a loser touching $k$ pages forces $\Omega(k)$ work before those pages are consistent — so single-version in-place storage provably *cannot* offer $O(1)$ full-consistency availability in the worst case. The loser set must be persisted, an $\Omega(|\text{losers}|)$ floor.

## 6. The Gap

The systems result outruns the theory — hence *empirically-open*. We lack a crisp characterization theorem of the form "workload class $\mathcal{W}$ + storage model $\mathcal{S}$ admits $O(1)$ time-to-availability iff conditions $C_1,\dots,C_k$." Open questions: a tight model relating steady-state tax to availability latency; whether $O(1)$ *write* availability (not just read) is always achievable; worst-case bounds on per-access lazy-redo latency; and the precise dividing line for single-version engines. Closing it needs a formal cost model unifying lazy redo, logical undo, and versioning overhead.

## 7. Current Research (as of June 2026)

Active: extending CTR to disaggregated / log-as-storage cloud architectures (Aurora, Socrates, Azure) where redo lives in a storage tier and "recovery" is largely metadata; instant recovery for NVM and for LSM/log-structured engines; formal cost models for lazy recovery *(frontier — verify)*. Groups: Microsoft (Azure SQL / Hekaton lineage — Antonopoulos, Diaconu), Graefe/Sauer/Härder (instant recovery), and cloud-DB teams. A 2025–2026 thread studies recovery-time SLAs as a first-class optimization target under serverless auto-pause/resume *(frontier — verify)*.

## 8. Future Work

- A characterization theorem for $O(1)$-availability workloads and storage models.
- Bounding and minimizing per-access lazy-redo tail latency.
- CTR with strong steady-state-tax guarantees (cheap version stores).
- Constant-time recovery for non-MVCC and for byte-addressable NVM engines.

## 9. Key References

- **[SOTA]** Panagiotis Antonopoulos, Peter Byrne, Wayne Chen, Cristian Diaconu, et al. *Constant Time Recovery in Azure SQL Database.* VLDB, 2019.
- **[SOTA]** Caetano Sauer, Goetz Graefe, Theo Härder. *Instant Restart for the Lock Manager / Single-Page Recovery* (Instant Recovery line). ICDE/EDBT, 2015–2018.
- **[Foundational]** Cristian Diaconu, Craig Freedman, Erik Ismert, Per-Åke Larson, et al. *Hekaton: SQL Server's Memory-Optimized OLTP Engine.* SIGMOD, 2013.
- **[Foundational]** C. Mohan et al. *ARIES.* ACM TODS, 1992.
- **[Survey]** Goetz Graefe, Wey Guy, Caetano Sauer. *Instant Recovery with Write-Ahead Logging.* Morgan & Claypool Synthesis Lectures, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
