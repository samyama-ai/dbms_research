---
id: 12-newsql-distributed-sql/deterministic-interactive-transactions
title: "One-shot vs interactive deterministic transactions"
topic: 12-newsql-distributed-sql
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# One-shot vs interactive deterministic transactions

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/deterministic-interactive-transactions` · **Status:** partially-solved

## 1. Problem Statement
Deterministic databases (Calvin and successors) obtain replica determinism by agreeing on a global transaction order and executing each transaction as a **one-shot** unit — the full transaction logic (typically a stored procedure) is known to the system up front, so every replica runs it identically with no client in the loop. Real applications, however, often use **interactive transactions**: the client issues a statement, reads the result, decides the next statement based on that result and possibly external logic, and only later commits (multiple client↔server round trips inside one transaction, `BEGIN … COMMIT`). The problem: **support multi-round interactive transactions in a deterministic system without losing replica determinism**, since interactivity injects nondeterminism (client-driven branching, timing, external inputs) that replicas cannot independently reproduce.

Variants:
- **Decision:** Can an interactive transaction be made deterministic, given that intermediate client decisions are not visible to all replicas a priori?
- **Performance:** Minimize the latency/throughput penalty relative to one-shot stored procedures.
- **Expressiveness:** Which interactive workloads can be captured without falling back to non-deterministic 2PC?

It is "partially solved": techniques record the client's decisions into the deterministic input log (so replicas replay the *resolved* transaction), or use reconnaissance + speculative replay, but each trades latency, holds locks across client round trips, or restricts expressiveness.

## 2. Mathematical Foundations
Determinism requires the executed schedule to be a function of the agreed input sequence $O$ alone. An interactive transaction is a sequence of operations $op_1, r_1, op_2(r_1), \dots$ where $op_{k}$ depends on results $r_{<k}$ that include client-side computation $\phi$ (possibly nondeterministic / external). For replicas to agree, the *effective* transaction must be reduced to a deterministic function of $O$. Two reductions:
- **Logging / capture:** record the resolved statement stream and client decisions $\phi$-outputs into the ordered input so all replicas replay the same concrete sequence — converts interactive → one-shot *after the fact*, but the originating replica must run first, serializing the client round trips before global ordering.
- **Reconnaissance + deterministic replay:** speculatively execute to learn the access set and the branch taken, then submit a one-shot deterministic transaction (OLLP-style), aborting if the world changed.

The tension is formalized as: interactivity adds rounds $\rho$ of client communication *inside* the critical section; deterministic systems must either hold conflict locks for $\rho$ wide-area round trips (hurting throughput, like the lock-holding cost in 2PC) or move the rounds *outside* the deterministic phase via capture/recon (adding aborts). This recreates much of the coordination cost that determinism was meant to eliminate.

## 3. State of the Art (SOTA)
- **Calvin** (SIGMOD 2012) is one-shot only; interactive transactions are explicitly out of scope, handled via OLLP-style reconnaissance to convert them.
- **Aria** (VLDB 2020) executes without prior read/write sets but is still batch/one-shot oriented.
- **FaunaDB** (built on a Calvin-derived deterministic engine) exposes a query language compiled to deterministic transactions rather than open interactive sessions — a practical "capture" approach.
- **Detock** (geo-distributed deterministic, 2023) and the broader deterministic line continue to assume mostly one-shot transactions.
- Contrast: traditional non-deterministic systems (Spanner, CockroachDB) support full interactive transactions natively at the cost of distributed commit and lock-holding across client round trips.

## 4. Upper Bound
Best-known: interactive transactions are supported by **capturing the resolved statement stream into the deterministic input** (run once on an entry replica, then replicate the concrete transaction) — adding the client round-trip latency *before* global ordering, with no extra aborts, but serializing the interaction on one replica. Alternatively, **reconnaissance + speculative one-shot submission** runs in $O(1)$ extra rounds in the common case with abort-on-staleness. Model: deterministic concurrency control over a partitioned store; constant extra rounds in expectation, but with either lock-holding or abort costs.

## 5. Lower Bound
No tight formal lower bound is established, but a structural argument applies: if a transaction's control flow depends on a runtime read result, the system cannot fix its deterministic schedule until that read is observed — forcing at least one round of execution before deterministic ordering can commit the *branch*. Combined with the determinism requirement (schedule = function of $O$), this implies interactive transactions cannot be both (a) ordered before any execution and (b) deterministic, unless the branch outcome is logged — i.e., some serialization point before global agreement is *necessary*. This is an indistinguishability-style obstruction rather than a complexity-class hardness result.

## 6. The Gap
The gap is between full native interactivity (available in non-deterministic systems at distributed-commit cost) and efficient determinism (available only for one-shot transactions). Current deterministic techniques *handle* interactivity but reintroduce either lock-holding across client rounds or abort overhead — partially negating determinism's advantage. It is **partially solved**: no protocol offers fully interactive transactions with deterministic-system throughput and no extra coordination cost. Closing it needs a protocol that confines client-driven nondeterminism to a pre-ordering phase with bounded, predictable cost, ideally with a proof of how much coordination interactivity *necessarily* reintroduces.

## 7. Current Research (as of June 2026)
- Daniel Abadi's group (UMD) and the Calvin/Aria/Detock lineage exploring interactive-transaction support in deterministic engines.
- *(frontier — verify)* "capture-and-replay" optimizations that pipeline client round trips with speculative deterministic execution to hide latency.
- FaunaDB / deterministic-engine vendors refining compiled-query interfaces as a pragmatic middle ground.
- *(frontier — verify)* formal results quantifying the minimum coordination interactivity forces in deterministic settings (overlaps with the dynamic-rwset problem).

## 8. Future Work
- A deterministic protocol supporting general interactive transactions with bounded extra coordination and no lock-holding across client rounds.
- A lower bound on the coordination cost interactivity necessarily reintroduces.
- Hybrid engines that route one-shot transactions through the deterministic fast path and interactive ones through a bounded fallback.
- Programming-model support (e.g., session compilation) to maximize the one-shot fraction.

## 9. Key References
- **[Foundational]** A. Thomson, T. Diamond, S. Weng, K. Ren, P. Shao, D. Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[Foundational]** A. Thomson, D. Abadi. *The Case for Determinism in Database Systems.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920855)
- **[Survey]** D. Abadi, J. Faleiro. *An Overview of Deterministic Database Systems.* CACM, 2018. — [DOI](https://doi.org/10.1145/3181853)
- **[SOTA]** Y. Lu, X. Yu, L. Cao, S. Madden. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[SOTA]** C. D. T. Nguyen, J. K. Miller, D. Abadi. *Detock: High Performance Multi-region Transactions at Scale.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589293)

## 10. Worked Example

A client runs an interactive booking: `BEGIN; r1 = SELECT seats FROM flight WHERE id=42;` then, *based on $r_1$ and external pricing logic $\phi$*, either `UPDATE flight SET seats=seats-1` or `ROLLBACK`. The branch is invisible to other replicas a priori.

**Naive deterministic attempt.** Order the transaction in sequence $O$ before execution. But the schedule depends on the branch, which depends on $r_1$ — not a function of $O$ alone. Replicas would diverge. So §5's obstruction bites: the schedule cannot be fixed until $r_1$ is observed.

**Capture reduction.** Entry replica runs the round trips first: reads $r_1=\text{seats}=3>0$, evaluates $\phi$, resolves to the concrete one-shot `UPDATE flight SET seats=2 WHERE id=42`. *Only this resolved statement* enters $O$ and is replicated; all replicas replay it deterministically — $0$ extra aborts, but the $\rho=2$ client round trips are serialized on one replica before global ordering.

**Cost contrast.** Holding the conflict lock on $\text{flight}[42]$ across $\rho$ wide-area round trips (the alternative) reintroduces exactly the lock-holding cost determinism aimed to remove — the §6 gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
