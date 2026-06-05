# Cross-shard secondary index consistency

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/cross-shard-secondary-index` · **Status:** partially-solved

## 1. Problem Statement

A sharded primary table is partitioned by primary key, but a **global secondary index (GSI)** on a non-key column is partitioned independently (by the indexed value). A single-row write to the base table can therefore touch a base shard and one or more index shards living on different nodes. Maintaining a **strongly consistent** GSI — every committed read of the index reflects exactly the committed base state, with no orphaned or missing index entries — naively demands a distributed transaction (2PC) on *every* base write, which is expensive at scale.

The problem: maintain a strongly consistent cross-shard secondary index **without paying a full 2PC round per write**, ideally amortizing or eliminating cross-shard coordination while preserving serializability (or a clearly stated weaker-but-sufficient level).

**Decision variant:** given a write and an index-maintenance plan, decide whether index and base updates are guaranteed atomic-visible. **Optimization variant:** minimize coordination cost (messages/latency) per write subject to a target consistency level. **Consistency-level variant:** characterize which index reads (point lookup, range, covering) need full serializability vs. tolerate bounded staleness.

## 2. Mathematical Foundations

Model base table $R(k, a, \dots)$ sharded by $k$; index $I(a, k)$ sharded by $a$. An update $a: v_1 \to v_2$ must delete $(v_1,k)$ and insert $(v_2,k)$ atomically with the base change. Consistency is the invariant $\forall (a,k)\in I \iff R[k].a = a$. Violations are **orphans** (index entry without matching base row) and **dangling** (base value not indexed). Serializability requires the multi-shard write to appear atomic in the global order.

Key techniques rest on: (i) **index entries co-versioned with base timestamps** so a reader can validate an index entry against the base snapshot (MVCC visibility predicate), turning a write-time 2PC into a read-time check; (ii) **asynchronous maintenance + read-repair**, where consistency is restored lazily and reads filter stale entries (a chase-like validation); (iii) **deterministic ordering** (Calvin/SLOG) where index updates ride the same global sequence as base updates, so atomicity is free of commit. The cost model is communication complexity: full 2PC is $2$ round-trips $\times$ #shards; the goal is $O(1)$ or amortized sub-2PC coordination.

## 3. State of the Art (SOTA)

- **Spanner / F1** (F1, VLDB 2013): global indexes maintained transactionally; correct but 2PC-backed, the gold standard for consistency.
- **CockroachDB** GSIs: maintained within the same transaction using its parallel-commit + intent mechanism, reducing latency vs. classic 2PC.
- **YugabyteDB** distributed indexes; **TiDB** global/clustered indexes with async backfill + transactional online updates.
- **DynamoDB GSIs** (eventually consistent) — the explicit *weak* point of the design space, contrasting with strongly-consistent NewSQL indexes.
- **Deterministic approach:** Calvin/SLOG fold index maintenance into the deterministic batch, avoiding per-write commit votes.

## 4. Upper Bound

With **parallel commit / one-phase optimizations** (CockroachDB-style), a base+index write across $s$ shards commits in effectively one round-trip in the common (no-conflict) case by making the transaction record's commit status implicitly determined by all writes being staged — bringing per-write coordination to $O(1)$ round-trips amortized rather than the $2$-round 2PC. **MVCC co-versioning + read-side validation** can move the consistency check entirely to read time, so writes do only local index puts (no synchronous cross-shard agreement), with read cost $O(\text{matches})$ extra validation. **Deterministic batching** amortizes ordering over a whole batch, giving $O(1)$ per-write coordination in the limit.

## 5. Lower Bound

If a base write and its index entries reside on different shards and must be **atomically visible** under serializability, then in an asynchronous system with failures, achieving atomic commitment requires at least the equivalent of a consensus/commit decision — you cannot have all-or-nothing visibility across a partition boundary without either a commit protocol or a pre-agreed global order. This is the atomic-commit lower bound (2PC blocking / non-blocking commit needs extra rounds; FLP-style impossibility of single-round fault-tolerant agreement). Thus *true* synchronous strong consistency cannot beat one consensus decision per atomic unit — fast paths only help in the failure-free, conflict-free case.

## 6. The Gap

The space is **partially solved**: parallel-commit and read-validation push the *common-case* cost well below classic 2PC, and determinism removes per-write commit entirely. The remaining gap: under contention or failures these fast paths fall back to full agreement, and there is no protocol that is simultaneously (a) strongly consistent, (b) coordination-free on writes in *all* cases, and (c) cheap on reads — the atomic-commit lower bound forbids the ideal. Open: tight characterization of which index-read patterns truly need serializability, so the rest can safely use cheaper bounded-staleness paths.

## 7. Current Research (as of June 2026)

Directions: read-time validation / lazy index maintenance with provable orphan-freedom; covering-index design to avoid base round-trips; and consistency-level-aware query planning that mixes strong and bounded-staleness index reads. Cockroach Labs (parallel commits), PingCAP (TiDB global indexes), and Yugabyte publish on this *(frontier — verify)*. Academic work on deterministic index maintenance (SLOG/Aria lineage) and on minimizing 2PC via logical leases (Sundial) continues *(frontier — verify)*.

## 8. Future Work

- A provable taxonomy of index-read patterns by required consistency level.
- Coordination-free strongly-consistent maintenance for restricted workloads (e.g. append-mostly).
- Tight bounds on read-side validation overhead vs. write-side coordination.
- Online physical design: when a GSI's maintenance cost outweighs its query benefit.

## 9. Key References

- **[Foundational]** Shute, et al. *F1: A Distributed SQL Database That Scales.* VLDB, 2013.
- **[Foundational]** Gray, Lamport. *Consensus on Transaction Commit (Paxos Commit).* ACM TODS, 2006.
- **[SOTA]** Taft, et al. *CockroachDB: The Resilient Geo-Distributed SQL Database* (parallel commits). SIGMOD, 2020.
- **[SOTA]** Huang, et al. *TiDB: A Raft-based HTAP Database.* VLDB, 2020.
- **[SOTA]** Thomson, Abadi, et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[Survey]** Bernstein, Hadzilacos, Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.

---
*Part of the [DBMS Research catalog](../../README.md).*
