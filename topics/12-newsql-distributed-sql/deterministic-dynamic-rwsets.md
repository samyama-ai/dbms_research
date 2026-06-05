# Deterministic execution with dynamic read/write sets

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/deterministic-dynamic-rwsets` · **Status:** open

## 1. Problem Statement
**Deterministic database systems** (e.g., Calvin) eliminate the cost of distributed commit by agreeing on a global *transaction order* up front and having all replicas execute it deterministically — given the same input order, every replica reaches the same final state with no replica coordination at commit time. This requires knowing each transaction's **read/write set** (the keys it accesses) *before* execution, to plan locking and partition routing. The problem: support **deterministic execution when the read/write set is dynamic** — i.e., the keys accessed depend on values read at runtime (e.g., `UPDATE accounts WHERE balance > (SELECT ...)`, secondary-index lookups, dependent reads).

Variants:
- **Decision:** Can a transaction with data-dependent access sets be executed deterministically with bounded extra rounds?
- **Optimization:** Minimize the overhead (extra "reconnaissance" reads, aborts) of discovering access sets while preserving determinism.
- **Expressiveness:** Characterize which transaction classes admit efficient deterministic execution.

It is open because the leading technique — **OLLP (Optimistic Lock-Location Prediction)**: run a reconnaissance query to *guess* the read/write set, then execute deterministically and *abort-and-retry* if the guess was wrong — has no tight bound on retries under contention and skewed/adversarial workloads, and no general guarantee of progress.

## 2. Mathematical Foundations
A deterministic execution is a function $\sigma: (\text{input order } O, \text{initial state } s_0) \mapsto s_f$ such that all replicas computing $\sigma$ agree. Determinism requires the *schedule* to be a function of $O$ alone, not of nondeterministic timing. With static read/write sets $R(T), W(T)$, a deterministic lock manager grants locks in $O$-order, guaranteeing a serial-equivalent schedule (Thomson–Abadi, Calvin, SIGMOD 2012).

For **dynamic** sets, $R(T)$ is not a function of $O$ alone but of intermediate reads: $R(T) = R(T, s)$. OLLP introduces a *reconnaissance phase* producing a predicted set $\hat R$; execution is deterministic conditioned on $\hat R \supseteq R(T,s)$. If the predicate $\hat R \supseteq R(T,s)$ fails (state changed between recon and execution), the transaction must abort to preserve determinism. The cost model is the expected number of recon→execute rounds, governed by the probability that the relevant state changed — related to contention rate $\lambda$ and the "footprint" of conflicting writes. No closed-form tight bound exists; worst-case adversarial interleavings can force unbounded retries (a livelock concern absent a fairness mechanism).

## 3. State of the Art (SOTA)
- **Calvin / OLLP** (Thomson, Abadi et al., SIGMOD 2012; VLDB) — the canonical deterministic system and the reconnaissance technique for dynamic sets.
- **Aria** (Lu, Yu, Cao, Madden, VLDB 2020) — deterministic execution *without* prior knowledge of read/write sets, using a deterministic reordering/conflict-detection phase after a speculative execution, avoiding the recon round but paying an abort/fallback phase.
- **Bohm / PWV** — deterministic MVCC variants. **Caracal**, **Detock** (geo-deterministic) extend the line.
- **QueCC** (Qadah–Sadoghi) — priority-queue-based deterministic concurrency control reducing coordination.

## 4. Upper Bound
Best-known: **OLLP** — one reconnaissance read pass plus one execution pass in the common case ($O(1)$ extra rounds amortized under low contention); **Aria** removes the recon pass, executing in a fixed number of deterministic phases (read, reserve, commit/fallback) with $O(1)$ rounds but with aborts proportional to conflict density. Model: deterministic concurrency control, single-version or MVCC, partitioned store. Both are constant-round *in expectation* but lack worst-case retry bounds under adversarial contention.

## 5. Lower Bound
No matching lower bound is established. Informally: discovering a data-dependent access set requires *reading the data*, so at least one read round is necessary before a key-aware deterministic plan can be fixed — this gives a trivial $\ge 1$-round lower bound. Under adversarial concurrent writers, an indistinguishability argument suggests recon-based schemes cannot guarantee a constant retry bound without a fairness/serialization mechanism, but a formal hardness result (e.g., showing $\Omega(k)$ rounds for some workload class, or a communication-complexity lower bound on access-set discovery) is **missing**. This absence of a tight lower bound is precisely why the problem is open.

## 6. The Gap
Upper bounds are constant-round *in expectation* under benign workloads; there is **no lower bound** characterizing worst-case cost, and no upper bound guaranteeing bounded retries under contention/adversarial writes. The gap is wide open: we lack both (a) a deterministic scheme with provable worst-case round/abort bounds for arbitrary dynamic transactions, and (b) a hardness result proving such bounds are unattainable. Closing it requires either a progress-guaranteeing deterministic protocol (e.g., escalating to pessimistic global ordering for repeatedly-aborting transactions) or a lower bound on access-set discovery rounds.

## 7. Current Research (as of June 2026)
- Daniel Abadi's group (UMD) and the Calvin/Aria/Detock lineage extending deterministic execution to dynamic and geo-distributed settings.
- *(frontier — verify)* hybrids that combine speculative execution with deterministic conflict resolution to avoid recon rounds while bounding aborts.
- Deterministic execution on modern hardware (RDMA, in-memory) reducing per-round cost (work from MIT/Madden, Sadoghi's ExpoLab at UC Davis).
- *(frontier — verify)* formal characterizations of which SQL fragments admit efficient deterministic execution with dynamic predicates.

## 8. Future Work
- A deterministic protocol with provable worst-case retry/round bounds for dynamic read/write sets.
- A matching lower bound (communication or round complexity) on access-set discovery.
- Adaptive escalation from optimistic recon to pessimistic global ordering under contention.
- Extending guarantees to range predicates, secondary indexes, and stored procedures with control flow.

## 9. Key References
- **[Foundational]** A. Thomson, T. Diamond, S. Weng, K. Ren, P. Shao, D. Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[Foundational]** A. Thomson, D. Abadi. *The Case for Determinism in Database Systems.* VLDB, 2010.
- **[SOTA]** Y. Lu, X. Yu, L. Cao, S. Madden. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020.
- **[SOTA]** T. Qadah, M. Sadoghi. *QueCC: A Queue-Oriented, Control-Free Concurrency Architecture.* Middleware, 2018.
- **[Survey]** D. Abadi, J. Faleiro. *An Overview of Deterministic Database Systems.* CACM, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
