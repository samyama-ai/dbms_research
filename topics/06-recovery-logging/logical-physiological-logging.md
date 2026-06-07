---
id: 06-recovery-logging/logical-physiological-logging
title: "Logical vs physiological logging tradeoff"
topic: 06-recovery-logging
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Logical vs physiological logging tradeoff

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/logical-physiological-logging` · **Status:** open

## 1. Problem Statement
A recovery log can record updates at different semantic levels:
- **Physical logging:** byte/page images (before- and/or after-images of pages or page regions). Idempotent, easy to redo/undo, but voluminous.
- **Logical logging:** high-level operations (e.g., "insert tuple $t$ into relation $R$"). Compact, but not generally idempotent and requires an action-consistent database state to replay correctly.
- **Physiological logging** (Gray's term, "physical-to-a-page, logical-within-a-page"): log the operation *as applied to one specific page*, identified by page id + log sequence number (LSN). The ARIES sweet spot.

**Problem:** formally characterize, for a given workload $W$ and storage/replication model, **which logging granularity minimizes total cost = runtime logging overhead + recovery time + log volume**, and prove the boundaries between regimes.

Variants: **optimization** (pick the cost-minimizing scheme, possibly per-operation), **decision** (does logical logging beat physiological by margin $\ge \epsilon$ on $W$?), and **counting** (minimum bits per operation to remain recoverable — links to the [log-compression bounds](./log-compression-reclamation.md) problem).

## 2. Mathematical Foundations
Let an update $u$ have a *physical footprint* $\phi(u)$ (bytes of page state changed) and a *logical description length* $\ell(u)$ (bits to name the operation + parameters). Runtime log cost $\approx$ (bytes written) $\times$ (per-byte flush/replication cost); recovery cost $\approx$ (records replayed) $\times$ (per-record CPU) for logical, vs (pages re-applied) for physical.

The core formal object is the **redo/undo correctness condition**. Physiological logging requires the **page-LSN invariant**: a logged action is redone iff `page.LSN < record.LSN`, giving *exactly-once* application — a **test-and-set idempotency** mechanism. Logical replay lacks a cheap idempotency token, so it needs **action consistency** (a sharp-point state), historically enforced by fuzzy-checkpoint plus operation-level locking, and a **logical undo** that is the operation's inverse, requiring the operation to be invertible.

This is an **information-theoretic vs. operational** trade: $\ell(u) \le \phi(u)$ typically (a logical op is more compact than its page delta — think "increment counter" vs. a 8-byte page write inside an 8KB page), so logical wins on log volume / replication bandwidth, but pays in replay complexity and weaker idempotency. The crossover depends on the **amplification ratio** $\phi(u)/\ell(u)$ and the **replay-cost ratio**. For LSM/log-structured stores the calculus shifts: the data *is* a log, and compaction interacts with logical record reuse. One can frame optimal per-operation choice as a **mixed-integer / submodular** selection over the log schema given a workload distribution.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **ARIES** (Mohan et al., TODS 1992) established physiological logging + WAL + repeating-history redo as the durable standard; it is the de facto SOTA for disk-based engines (DB2, SQL Server, Postgres heap). **Command/logical logging** dominates in **deterministic** and main-memory systems: **H-Store/VoltDB** (command logging, Malviya et al., ICDE 2014) shows logical logging gives far lower runtime overhead but slower recovery; **Calvin** (Thomson et al., SIGMOD 2012) logs only the input transaction (pure logical) because determinism makes replay reproducible. **SiloR** (Zheng et al., OSDI 2014) and **Hekaton** use value/physical logging tuned for parallel recovery.
- **Theory-SOTA:** There is no accepted closed-form theory selecting the optimal granularity for an arbitrary workload — hence **open**. Existing results are recovery-correctness theorems (ARIES) and empirical crossover studies (Malviya et al.).

## 4. Upper Bound
Per the Malviya et al. ICDE 2014 study, command (logical) logging reduces runtime logging overhead by up to an order of magnitude vs. physiological in a main-memory OLTP engine, at the cost of recovery time growing with the *replay work* of the transactions (recovery $\approx$ re-execution). Physiological logging upper-bounds recovery time at $O(\text{pages dirtied since checkpoint})$ independent of compute, via idempotent page re-application. So each scheme is the SOTA upper bound on *its* favored axis; no scheme dominates on both.

## 5. Lower Bound
- **Volume:** any recoverable log must encode enough to reconstruct committed state; the per-operation lower bound is the operation's logical (Kolmogorov-style / entropy) description length given the recovery context — you cannot log fewer bits than the information needed to redo, an information-theoretic floor (see the compression-bounds problem).
- **Recovery vs. logging trade:** there is a genuine tension — a cheap-to-write log (logical, few bits) forces expensive replay; an idempotent fast-replay log (physical) forces more bytes. No single scheme can simultaneously hit the volume floor *and* the $O(\text{dirty pages})$ replay bound for general workloads. A clean formal lower bound proving this incompatibility is, to our knowledge, not established — part of why the problem is open.

## 6. The Gap
The endpoints (ARIES correctness; H-Store empirics) are well understood, but **no theory predicts the crossover** as a function of workload skew, transaction compute intensity, page-fill factor, and replication bandwidth. The gap is the absence of a model that, given $W$, outputs the optimal (possibly hybrid, per-operation) logging granularity *with a guarantee*. Closing it needs a cost model with provable optimality plus a matching lower bound on the runtime+recovery product.

## 7. Current Research (as of June 2026)
- Hybrid / adaptive logging that switches granularity per operation or per phase (e.g., logical at runtime, physiological for hot pages) in HTAP and main-memory engines *(frontier — verify)*.
- Logging co-designed with LSM compaction and with disaggregated storage, where replication bandwidth dominates and logical logging's compactness is decisive *(frontier — verify)*.
- Determinism-assisted recovery (Calvin-lineage) reducing logical logging to input logging, pushing recovery cost into deterministic re-execution on many cores.

## 8. Future Work
- A provably optimal per-workload (or per-operation) granularity selector.
- Formal lower bound on the runtime-overhead × recovery-time product separating the schemes.
- Granularity choice integrated with parallel/instant recovery and with bandwidth-constrained replication.

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H. & Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://dl.acm.org/doi/10.1145/128765.128770)
- **[Foundational]** Gray, J. & Reuter, A. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [WorldCat](https://search.worldcat.org/title/transaction-processing-concepts-and-techniques/oclc/26303792)
- **[SOTA]** Malviya, N., Weisberg, A., Madden, S. & Stonebraker, M. *Rethinking Main Memory OLTP Recovery (command vs. ARIES logging).* ICDE, 2014. — [DOI](https://doi.org/10.1109/ICDE.2014.6816685)
- **[SOTA]** Zheng, W., Tu, S., Kohler, E. & Liskov, B. *Fast Databases with Fast Durability and Recovery Through Multicore Parallelism (SiloR).* OSDI, 2014. — [DBLP](https://dblp.org/rec/conf/osdi/ZhengTKL14.html)
- **[SOTA]** Thomson, A. et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://dl.acm.org/doi/10.1145/2213836.2213838)

## 10. Worked Example

A transaction runs `UPDATE accounts SET bal = bal + 1 WHERE id = 42`, touching $4$ bytes inside an $8$ KB page.

- **Physical logging** writes a before/after image of the changed page region. Even byte-ranged, a record carries page id + offset + $4$+$4$ bytes of image $\approx 24$ B; a full-page-image scheme would log $8$ KB. Replay is idempotent: re-apply the after-image, cost $O(1)$ page write, no recompute.
- **Logical logging** writes the operation: op-id `add`, key $42$, delta $+1$ $\approx \ell(u) = 12$ B. Amplification ratio here is modest, $\phi(u)/\ell(u) = 24/12 = 2$ (or $8192/12 \approx 680$ vs. full-page). But replay must re-execute the `add` against an *action-consistent* state and undo needs the inverse ($-1$).

So with $10^6$ such updates, physiological logs $\approx 24$ MB and recovers in $O(\text{dirty pages})$; logical logs $\approx 12$ MB (half the bandwidth — decisive for replication) but recovery $\approx$ re-running $10^6$ ops. Neither hits both the volume floor and the $O(\text{dirty pages})$ replay bound — the open crossover the problem asks to characterize.

---
*Part of the [DBMS Research catalog](../../README.md).*
