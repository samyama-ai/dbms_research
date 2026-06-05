# Provably Correct Online Schema Migration

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/online-schema-migration-correctness` · **Status:** partially-solved

## 1. Problem Statement
Transform a live relational table from schema $\mathcal{S}_{\text{old}}$ to $\mathcal{S}_{\text{new}}$ (add/drop/rename column, change type, split/merge tables, add constraint/index) **without downtime and with minimal locking**, while concurrent transactions continue to read and write, and provide **formal correctness and rollback guarantees**.

- **Correctness (decision) variant:** Given a migration plan and a concurrent transaction schedule, does the migration preserve a stated correctness criterion (serializability/linearizability of application-visible state, and equivalence to an atomic switchover)?
- **Optimization variant:** Minimize migration duration / lock-hold time / extra write amplification / catch-up backlog subject to correctness.
- **Rollback variant:** At any abort point, restore a consistent state recoverable to $\mathcal{S}_{\text{old}}$ semantics.

The crux: clients run against both schema versions during the cutover window, so the system must maintain a **double-write / backfill / dual-read** protocol that is provably equivalent to an instantaneous atomic DDL.

## 2. Mathematical Foundations
Model the live table as a state machine; a migration is a sequence of small steps each individually online (short-lock or lock-free). Correctness is stated as **observational equivalence** between the concurrent execution and a reference execution where the DDL is a single atomic step — a refinement/linearizability argument. The standard pattern (expand–migrate–contract) is provably safe if the intermediate schema is a **common supertype** simultaneously satisfying old and new read/write contracts.

Concurrency reasoning uses **serializability theory** (conflict graphs acyclic) plus an invariant that the *shadow* representation (new column/table) is kept a deterministic function $f$ of the source: $\text{new} = f(\text{old})$ maintained by triggers/double-writes, with a **backfill** that converges because new writes are caught while a bounded backlog drains (a fixpoint/convergence argument, analogous to the **chase** reaching a stable instance). Type changes invoke a total mapping $\tau:\text{dom}_{\text{old}}\to\text{dom}_{\text{new}}$; correctness requires $\tau$ total and, for rollback, an inverse or logged original. Formally these protocols are verified with **TLA+/Ivy**-style refinement proofs.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Online DDL is built into engines (**MySQL/InnoDB online DDL**, **PostgreSQL** non-blocking `CREATE INDEX CONCURRENTLY` / `ADD COLUMN` fast-path) and external tools: **pt-online-schema-change** (Percona), **gh-ost** (GitHub, 2016 — binlog-driven, triggerless, lock-light cutover), **Facebook OSC**, and Vitess/PlanetScale online schema changes with revert. Google **F1/Spanner** pioneered *asynchronous, protocol-driven* schema change across a distributed store with a formally reasoned multi-phase state protocol (Rae et al., VLDB 2013). **Skeema**, **Liquibase**, and Reshape codify expand-contract.

**Theory-SOTA.** The F1 schema-change protocol provides the canonical *proved-correct* scheme (intermediate states + lease-bounded version skew). Recent verification work mechanizes online-DDL protocols in TLA+/Ivy.

## 4. Upper Bound
Most single-table changes are achievable with **O(1) short metadata locks** plus an **O(N) one-pass backfill** and **O(updates-during-window)** catch-up — i.e., linear data-movement, near-zero blocking. gh-ost-style migrations cut over in **O(1)** lock time via atomic rename. Distributed schema change (F1) completes in a number of phases bounded by the version-lease count, with each node converging in **bounded time** after the last write — guaranteeing no orphaned/missing data under a max-two-concurrent-versions invariant.

## 5. Lower Bound
Truly **zero-lock** atomic switchover is impossible in general: by **FLP impossibility**, no asynchronous protocol can guarantee an agreed-upon atomic cutover with faulty nodes, so practical systems assume bounded version leases / partial synchrony. Any correct multi-version DDL must tolerate at least **two simultaneous schema versions** (F1 lower-bound observation): you cannot shrink the live version set to one without a stop-the-world point. Backfill must read every row, giving an unavoidable **$\Omega(N)$** data-touch lower bound for content-changing migrations.

## 6. The Gap
For **single-node, single-table** changes the gap is largely closed: linear backfill + O(1) lock is near-optimal and proven correct in tools. The open gap is in (a) **multi-table / constraint-changing** migrations (splits, FK additions, normalization changes) executed online with *end-to-end* formal proofs rather than per-tool ad-hoc reasoning; (b) **distributed** settings where FLP/lease tradeoffs force liveness vs. safety choices; and (c) **machine-checked correctness** for the full operator set rather than just index/column additions.

## 7. Current Research (as of June 2026)
- Mechanized verification (TLA+, Ivy, Coq) of expand-contract and gh-ost-style protocols, extending the F1 proof to richer operators *(frontier — verify)*.
- **Serverless/cloud-native** online DDL (Aurora, AlloyDB, PlanetScale) with instant revert and "schema branching" *(frontier — verify)*.
- Co-design of online migration with **versioned/temporal** storage so old and new coexist as first-class versions.
- Integration with schema-evolution algebras (see *Schema Evolution Operator Completeness*) to compile high-level evolution into proven-online primitive plans.

## 8. Future Work
- A verified, composable library of online DDL primitives covering normalization-changing operators (split/merge with FK rewiring).
- Liveness/safety frontier characterization for distributed online DDL under partial synchrony.
- Automatic synthesis of double-write/backfill plans from a declarative target schema with proof certificates.

## 9. Key References
- **[Foundational]** Rae, I., Rollins, E., Shute, J., Sodhi, S., Vingralek, R. *Online, Asynchronous Schema Change in F1.* PVLDB, 2013.
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985.
- **[SOTA]** Noach, S. (GitHub). *gh-ost: Triggerless Online Schema Migrations for MySQL.* GitHub Engineering, 2016.
- **[SOTA]** Percona. *pt-online-schema-change* (design documentation), 2011–.
- **[Survey]** Curino, C., Moon, H.J., Zaniolo, C. *Graceful Database Schema Evolution: the PRISM Workbench.* PVLDB, 2008.

---
*Part of the [DBMS Research catalog](../../README.md).*
