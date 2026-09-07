---
id: 12-newsql-distributed-sql/cross-database-transactions
title: "Composable cross-database distributed transactions"
topic: 12-newsql-distributed-sql
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Composable cross-database distributed transactions

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/cross-database-transactions` · **Status:** open

## 1. Problem Statement

Given $k\ge 2$ **independent, autonomous** distributed-SQL systems
$D_1,\dots,D_k$ — each internally ACID, each with its own concurrency-control protocol,
clock, and failure model, and *none* willing to cede control of its commit decision — the
problem is to execute a transaction $T$ touching multiple $D_i$ such that the *composite*
execution is **atomic** and **serializable globally**, while preserving each system's
autonomy.

- **Decision variant:** given the local protocols, decide whether a global serializable
  schedule exists for a given set of multi-database transactions.
- **Construction variant:** design a coordination layer (commit + concurrency) that yields
  global ACID with minimal assumptions on the $D_i$.
- **Isolation variant:** what is the strongest *global* isolation level achievable when each
  $D_i$ exports only a black-box `begin/commit/abort` + isolation level?

This is the classic **multidatabase / federated transaction** problem reborn for
distributed SQL: each participant is itself a Spanner-class system, not a single node.

## 2. Mathematical Foundations

Let each $D_i$ produce a **local serialization order** $<_i$. A global schedule is
**globally serializable** iff the union of local conflict orders plus inter-database
conflicts is acyclic. The core obstruction is the **indirect / hidden conflict**: two
global transactions $T_a, T_b$ may not conflict *directly* at any single $D_i$, yet a
**local** transaction at $D_i$ can order them $T_a <_i T_b$ while another $D_j$ orders
$T_b <_j T_a$, producing a cycle invisible to every participant. Formally, global
serializability requires the **global conflict graph**
$\mathit{GCG}=\bigcup_i \mathit{CG}_i \cup \mathit{CG}_{\text{inter}}$ to be acyclic, but
the coordinator sees only commit order, not $<_i$.

**Atomic commitment** is governed by the **2PC** family and the impossibility results
around it: with even one faulty process and asynchrony, *non-blocking* atomic commitment is
impossible (a corollary of FLP, Fischer–Lynch–Paterson 1985); 3PC restores non-blocking only
under bounded synchrony. Autonomy forbids the coordinator from holding participant locks,
which is what makes classical **rigorous/strong-recoverable** schedules unattainable as a
black box.

## 3. State of the Art (SOTA)

- **Theory SOTA:** the multidatabase concurrency-control results of **Breitbart, Garcia-Molina,
  Silberschatz** (1992 survey) establish that global serializability over autonomous systems
  generally requires either a **ticket** mechanism (force a direct conflict at each site so
  hidden conflicts surface — Georgakopoulos–Rusinkiewicz–Sheth, the *optimistic/conservative
  ticket* method) or restricting to commit-order-deducible isolation.
- **Systems SOTA:** **X/Open XA** two-phase commit federates heterogeneous resource managers
  but gives only atomicity, *not* global serializability, and blocks on coordinator failure.
  **Sagas** (Garcia-Molina–Salem 1987) trade atomicity for compensations. Cloud-era systems
  use **outbox + event-sourcing** and idempotent compensators rather than true ACID.
- Cross-engine federation (Postgres FDW, Trino, Spanner external consistency exported via
  TrueTime) gives consistent *reads* but not composable global *writes*.

## 4. Upper Bound

With the **ticket method**, global serializability is achievable: each global txn updates a
local ticket at every site it touches, forcing all global txns into a *direct* conflict so
their relative order is identical everywhere; the coordinator then validates ticket order is a
consistent total order (optimistic ticketing aborts on disagreement). Cost: one extra
conflicting write per site, plus a validation phase — $O(k)$ messages per commit beyond 2PC,
preserving full local autonomy. For atomicity alone, 2PC achieves it in $2$ rounds /
$O(k)$ messages; 3PC adds a round for non-blocking under synchrony.

## 5. Lower Bound

- **Atomic commit:** no fault-tolerant, non-blocking atomic commitment protocol exists in an
  asynchronous system with one crash (FLP corollary). Hence any black-box federation that does
  not assume synchrony or a fault-tolerant external coordinator (e.g., Paxos-replicated
  coordinator, as in Spanner) can **block** on coordinator failure.
- **Global serializability without forced conflicts:** if participants reveal only commit
  order and refuse extra writes, hidden indirect conflicts make global serializability
  **undecidable to detect** from the coordinator's view — provably no commit-order-only
  protocol guarantees it (Breitbart et al.). This is an *autonomy-vs-correctness* impossibility,
  the federated analogue of CAP.

## 6. The Gap

Atomicity (2PC/3PC) and a sufficient construction for global serializability (tickets) both
exist, so a *correct* solution is known — but at the price of **forced conflicts** that erode
performance and require each $D_i$ to expose a writable ticket resource, partially breaking
autonomy. The open gap is whether **strict** global serializability (external consistency) is
achievable across truly opaque, clock-independent systems *without* shared mechanism, and what
the minimal interface each $D_i$ must export. No protocol matches the autonomy lower bound while
giving strict serializability and non-blocking commit.

## 7. Current Research (as of June 2026)

- **Standardized cross-database transaction interfaces** — proposals to export TrueTime-style
  bounded-clock or HLC timestamps so independent distributed-SQL systems can compose external
  consistency *(frontier — verify)*.
- Cross-cloud / cross-vendor transactions over **deterministic** participants, where global
  order can be agreed *before* execution, sidestepping hidden conflicts.
- **Workflow + saga** correctness with formally verified compensations as a pragmatic substitute.
- Verified TLA+/Ivy models of layered commit (coordinator-as-Paxos) for non-blocking federation.
Groups: Yale (Abadi), UW-Madison, MPI-SWS, and database-vendor consortia.

## 8. Future Work

- A minimal **interface contract** (what each system must export — commit timestamps? lock
  intents? ticket slots?) that provably enables global strict serializability.
- Composable isolation algebra: given each $D_i$'s isolation level, derive the strongest sound
  global level automatically.
- Cost lower bounds for forced-conflict mechanisms; can hidden conflicts be detected cheaper
  than full ticketing?

## 9. Key References

- **[Survey]** Breitbart, Y., Garcia-Molina, H., Silberschatz, A. *Overview of Multidatabase Transaction Management.* VLDB Journal, 1992. — [DOI](https://doi.org/10.1007/BF01231700)
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** Garcia-Molina, H., Salem, K. *Sagas.* SIGMOD, 1987. — [DOI](https://doi.org/10.1145/38713.38742)
- **[Foundational]** Georgakopoulos, D., Rusinkiewicz, M., Sheth, A. *On Serializability of Multidatabase Transactions Through Forced Local Conflicts.* ICDE, 1991. — [DBLP](https://dblp.org/rec/conf/icde/GeorgakopoulosRS91.html)
- **[SOTA]** Corbett, J., Dean, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[Foundational]** Gray, J., Lamport, L. *Consensus on Transaction Commit.* ACM TODS, 2006. — [DOI](https://doi.org/10.1145/1132863.1132867)

## 10. Worked Example

Two autonomous systems $D_1, D_2$. Global txns $T_a$ and $T_b$ each touch one item in each: $T_a$ writes $x\in D_1$ and reads $p\in D_2$; $T_b$ writes $y\in D_1$ and reads $q\in D_2$. They share no item, so no *direct* conflict. But a **local** txn $L_1$ at $D_1$ reads $x$ then writes $y$, ordering $T_a <_1 L_1 <_1 T_b$; a local $L_2$ at $D_2$ orders $T_b <_2 L_2 <_2 T_a$. The global conflict graph has $T_a \to T_b$ (via $D_1$) and $T_b \to T_a$ (via $D_2$): a cycle, so the schedule is **not** globally serializable — yet each site sees only a locally serializable order and the coordinator, seeing just commit timestamps, cannot detect it.

Ticket fix: each global txn increments a ticket row at every site it visits. Now $T_a$ and $T_b$ both write the $D_1$ ticket and the $D_2$ ticket, creating direct conflicts. Optimistic ticketing checks that ticket order agrees across sites; here $D_1$ says $T_a < T_b$ but $D_2$ says $T_b < T_a$, so validation **aborts** one txn — restoring global serializability at the cost of $O(k)$ extra writes.

---
*Part of the [DBMS Research catalog](../../README.md).*
