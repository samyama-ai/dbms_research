---
id: 32-multimodel-document-db/polystore-transactions
title: "Consistent transactions across polystores"
topic: 32-multimodel-document-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Consistent transactions across polystores

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/polystore-transactions` · **Status:** partially-solved

## 1. Problem Statement

A transaction $T$ reads and writes data spread across autonomous stores $S_1, \dots, S_k$ with **heterogeneous concurrency-control models** — e.g. $S_1$ uses strict two-phase locking (serializable), $S_2$ uses MVCC snapshot isolation (SI), $S_3$ is a document store offering only single-document atomicity, $S_4$ is eventually consistent. The goal: provide a **global** isolation guarantee (serializability or snapshot isolation) for multi-store transactions, despite each store enforcing only its own local guarantee and exposing limited control (often no 2PC, no external lock manager, no visibility into local schedules).

Variants:
- **Decision/verification:** given an execution, decide whether the global schedule is serializable (testing for an acyclic conflict graph).
- **Mechanism:** design a commit/CC protocol achieving global serializability or global SI with minimal blocking.
- **Impossibility-boundary:** characterize which combinations of local guarantees admit a global guarantee.

The autonomy constraint distinguishes this from distributed databases with a single CC: the federation cannot redesign each store's CC.

## 2. Mathematical Foundations

- **Serializability theory:** a history is **conflict-serializable** iff its conflict (serialization) graph is acyclic (Bernstein–Hadzilacos–Goodman). Testing serializability of a *given* history is in P (cycle detection); deciding whether an *arbitrary* interleaving is serializable (the scheduler must guarantee acyclicity online) is the CC problem.
- **Global serializability over autonomous stores:** even if every local history is serializable, the *global* history may not be — the local serialization orders can be mutually inconsistent (the classic result of Breitbart–Garcia-Molina–Silberschatz on multidatabase transaction management). Achieving global serializability requires a *ticket* method or rigorous (strong-strict 2PL) local schedules.
- **Snapshot isolation:** SI is characterized by the absence of write-write conflicts on overlapping transactions plus first-committer-wins; **Serializable SI (SSI)** (Cahill–Röhm–Fekete, SIGMOD 2008) adds dangerous-structure detection. Composing SI across stores requires a globally consistent snapshot timestamp.
- **Atomic commitment:** 2PC solves atomicity but blocks on coordinator failure; the **FLP impossibility** shows no deterministic asynchronous consensus tolerates one crash, bounding non-blocking commit.
- **CAP:** under partition, a federation cannot be both globally consistent (linearizable/serializable) and available (Gilbert–Lynch).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** the **ticket method** and rigorous-history approach (Georgakopoulos–Rusinkiewicz–Sheth; Breitbart et al., 1990s) give *provably* global serializability over autonomous stores that only guarantee local serializability — this is why the status is *partially-solved*. Global SI via a coordinator assigning snapshot/commit timestamps (e.g., the "Global Snapshot Isolation" line) is well understood when stores expose SI.
- **Systems-SOTA:** Google **Spanner** (Corbett et al., OSDI 2012) achieves external (strict) serializability across shards via TrueTime + 2PC over Paxos — but on *homogeneous* stores. **Cherry Garcia** / RAMP-style multi-item atomicity over heterogeneous key-value stores (Dey et al.; Bailis et al. RAMP, SIGMOD 2014) give atomic visibility without locking. Polystores (BigDAWG, TransAction-aware connectors), CockroachDB/YugabyteDB (SSI across shards). Epoxy (Kraska/Madden lineage, VLDB 2023) provides cross-engine transactions layering MVCC over heterogeneous stores *(frontier — verify)*.

## 4. Upper Bound

If every store guarantees **local serializability** and supports a *probe transaction* (the ticket), the ticket method yields **global serializability** by forcing a total order on local serialization graphs; commit uses 2PC. For SI stores exposing snapshot+commit hooks, a coordinator timestamp protocol yields **global SI** with one extra round. Spanner-class systems give external serializability at the cost of a 2PC round plus a commit-wait of one TrueTime uncertainty bound $2\epsilon$. RAMP gives read-atomic isolation in 1–2 round-trips, lock-free. So for the cooperative-store regime, near-optimal (constant extra rounds) protocols exist.

## 5. Lower Bound

- **FLP (Fischer–Lynch–Paterson, 1985):** no deterministic protocol achieves non-blocking atomic commit (consensus) in an asynchronous system with one crash — so any globally atomic commit either blocks or assumes synchrony/failure detectors.
- **CAP (Gilbert–Lynch, 2002):** during a network partition, global serializability and availability cannot both hold.
- **Autonomy impossibility (Breitbart–Garcia-Molina–Silberschatz):** if stores only guarantee local serializability and expose *no* control beyond submitting transactions, the federation cannot guarantee global serializability without additional mechanism (tickets/rigorousness) — purely local serializable stores do **not** compose.
- **Coordination lower bounds:** strongly-consistent multi-item transactions require coordination; invariant-confluence (Bailis et al.) characterizes exactly which transactions can avoid it — those that aren't I-confluent provably need coordination.

## 6. The Gap

**Partially solved.** When stores cooperate (expose tickets / SI hooks / 2PC), global serializability and global SI are achievable with constant overhead — gap effectively closed. The *open* gap is the **maximally-autonomous, heterogeneous** regime: mixing a serializable store, an SI store, and a single-document-atomic store with *no* shared control, while staying non-blocking and available. Here FLP/CAP and the autonomy impossibility bite, and no protocol matches the (weak) achievable guarantees. Open: a precise map from {local guarantees} × {exposed hooks} to the strongest composable global guarantee, plus minimal-coordination protocols within it.

## 7. Current Research (as of June 2026)

- Cross-engine transaction layers (Epoxy and successors) providing serializable transactions over heterogeneous OLTP/OLAP/KV stores *(frontier — verify)*.
- Deterministic/Calvin-style ordering applied to polystores to avoid 2PC blocking *(frontier — verify)*.
- Invariant-confluence analysis tooling to auto-detect coordination-free multi-store transactions.
- Groups: MIT DSAIL (Madden, Kraska), Berkeley (Bailis lineage / RISELab), Google (Spanner), CMU (Pavlo).

## 8. Future Work

- Composability theory: strongest global isolation as a function of local models + exposed control.
- Non-blocking commit for heterogeneous stores under realistic partial synchrony.
- Mixing SI and serializable stores with provable anomaly-freedom.
- Standardized transaction-control interface for autonomous stores.

## 9. Key References

- **[Foundational]** Bernstein, Hadzilacos, Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)
- **[Foundational]** Fischer, Lynch, Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** Breitbart, Garcia-Molina, Silberschatz. *Overview of Multidatabase Transaction Management.* VLDB Journal, 1992. — [DOI](https://doi.org/10.1007/BF01231700)
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[SOTA]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [DBLP](https://dblp.org/rec/conf/osdi/CorbettDEFFFGGHHHKKLLMMNQRRSSTWW12.html)
- **[SOTA]** Bailis, Fekete, Ghodsi, Hellerstein, Stoica. *Coordination Avoidance in Database Systems (Invariant Confluence) / RAMP Transactions.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735509), [arXiv](https://arxiv.org/abs/1402.2237)
- **[SOTA]** Cahill, Röhm, Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376690)

## 10. Worked Example

Two stores: $S_1$ (serializable, holds account $A$) and $S_2$ (serializable, holds account $B$). Two global transfers run concurrently:

- $T_1$: read $A$ ($S_1$), write $B$ ($S_2$).
- $T_2$: read $B$ ($S_2$), write $A$ ($S_1$).

Each *local* history is serializable. But $S_1$ may serialize $T_2 \to T_1$ (its $T_2$ write on $A$ precedes $T_1$'s read), while $S_2$ serializes $T_1 \to T_2$. The global conflict graph then has edges $T_2 \to T_1$ (from $S_1$) and $T_1 \to T_2$ (from $S_2$) — a **cycle**, so no serial order is consistent with both. Local serializability did *not* compose (Breitbart et al.).

Ticket fix: each $T_i$ increments a per-store ticket counter as an ordinary transaction. The federation reads ticket values and ensures the ticket order agrees across $S_1,S_2$; if $T_1$ takes ticket $5$ at $S_1$ it must take a *larger* ticket than $T_2$ at $S_2$ too. A disagreement forces an abort, breaking the cycle and yielding global serializability with one extra (ticket) operation per store.

---
*Part of the [DBMS Research catalog](../../README.md).*
