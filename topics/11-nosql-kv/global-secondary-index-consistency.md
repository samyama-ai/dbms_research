# Global Secondary Index Consistency

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/global-secondary-index-consistency` · **Status:** open

## 1. Problem Statement
A *global secondary index* (GSI) on a partitioned key-value store maps non-primary attributes to base-row primary keys, but is itself partitioned by the indexed attribute, so a single base write at partition $p$ generally touches an index entry at a *different* partition $q \neq p$. The problem: maintain the index so that queries observe a state consistent with the base table, **without** running a cross-partition distributed transaction (no 2PC, no global lock) on the write path.

Variants:
- **Decision:** given a read protocol and an index-maintenance protocol, decide whether every query result is *index-consistent* (no phantom entries pointing at stale/absent base rows; no missing entries for committed rows).
- **Optimization:** minimize staleness window / write amplification / extra round-trips subject to a target consistency level (eventual, read-your-writes, snapshot, serializable).
- **Counting/repair:** quantify and bound the number of *dangling* and *orphaned* index entries under failure, and the cost of asynchronous reconciliation.

The hard cases are concurrent updates that change the indexed attribute (an entry must be deleted in $q_{old}$ and inserted in $q_{new}$) interleaved with reads, plus partial failures between the base write and index write.

## 2. Mathematical Foundations
Model the store as a set of partitions, each a local linearizable register set. A base update is an operation $w = (k, a_{old}\!\to\! a_{new})$; the induced index mutations are $\delta^-(q_{old})$ and $\delta^+(q_{new})$. Consistency is a property of the *history* $H$ of base + index operations. We want: for every index read $r$ returning key set $K$, there is a point $t$ such that $K = \{k : \text{base}(k).a = v \text{ at } t\}$ — i.e., the index is a materialized view and we require **view consistency** in the sense of view-serializability / view maintenance.

Key results it rests on: incremental view maintenance and the *delta rules* of Gupta–Mumick; the **CALM theorem** (Hellerstein–Ameloot) — a distributed query is coordination-free iff it is monotone, and index maintenance with deletes/attribute-changes is *non-monotone*, so some coordination is provably required for strong levels. Snapshot isolation across partitions reduces to global timestamp ordering; serializable GSI maintenance is reducible to atomic multi-partition commit, hence inherits its impossibility envelope. Convergence under eventual consistency is framed via CRDT/lattice theory: an index is a join-semilattice of (key, version) sets and *anti-entropy* converges iff tombstones are causally tracked (e.g., dotted version vectors).

## 3. State of the Art (SOTA)
**Systems-SOTA.** DynamoDB GSIs are eventually consistent and explicitly *not* transactional with the base write; Cassandra materialized views use per-replica local index updates plus a batchlog for atomicity that is known to be unsafe under concurrent updates to the same row. Google **Spanner** and **F1** provide strongly-consistent global indexes but *by paying* for 2PC + TrueTime — i.e., they do not avoid distributed transactions, they make them cheap. **CockroachDB** and **YugabyteDB** maintain consistent secondary indexes via Raft-replicated, transactionally-committed writes. **FoundationDB** layers build indexes inside its serializable transactions.

**Theory-SOTA.** The CALM framework and *Bloom*/Dedalus give a syntactic monotonicity test deciding when coordination-free maintenance is possible. Coordination-avoidance (Bailis et al., *I-confluence*) characterizes exactly which integrity constraints (including index integrity) are preservable without coordination.

## 4. Upper Bound
For **eventual + convergent** GSIs: maintenance is achievable with $O(1)$ extra writes per update and *no* coordination, using causal tombstones; convergence is guaranteed (lattice join) but staleness is unbounded in an asynchronous network. For **read-your-writes**, a single piggybacked version vector suffices. For **snapshot/serializable**, the upper bound is that of multi-partition atomic commit: $O(1)$ extra round-trips with Spanner-style timestamping, or one 2PC ($2$ round-trips, $f+1$ replicas per partition) — this is the best known and is *coordination-bound*.

## 5. Lower Bound
The **CALM theorem** gives the sharp impossibility: any consistency level that must reflect deletions/attribute-changes (non-monotone) **cannot** be maintained coordination-free; coordination (a synchronization round) is necessary. *I-confluence* shows index uniqueness/foreign-key-style integrity is *not* I-confluent, so it provably requires coordination. Strong (serializable) GSI maintenance inherits **CAP** (Gilbert–Lynch): under partition you cannot have both availability and a linearizable index. Atomic cross-partition update is subject to the coordination lower bounds of consensus (FLP: no deterministic async termination guarantee).

## 6. The Gap
The *qualitative* gap is closed by CALM/I-confluence: we know exactly when coordination is mandatory. The *open* gap is **quantitative and practical**: (a) tight bounds on staleness/anomaly count as a function of clock skew, replication lag, and conflict rate; (b) protocols that pay coordination *only* on the rare attribute-changing/uniqueness-violating updates and run coordination-free otherwise, with provable bounds on how often the slow path fires; (c) reconciliation cost to repair dangling/orphan entries after failure. No system gives a closed-form anomaly bound for the common "mostly-append, occasionally-mutate" workload.

## 7. Current Research (as of June 2026)
Active directions: *mixed-consistency* indexes that classify each update as monotone (fast path) vs. non-monotone (coordinated) at runtime; escrow/reservation techniques for unique secondary indexes; verified IVM for distributed stores (work building on DBSP / differential dataflow giving incrementally-maintained, provably-correct views — Budiu, McSherry, and the *DBSP* line) *(frontier — verify)*. Cloud-vendor work on strongly-consistent GSIs layered on transactional KV (DynamoDB transactions, Spanner) continues; academic groups around Bailis/Hellerstein-lineage coordination-avoidance and the CRDT community (Shapiro, Preguiça) on causally-consistent index convergence remain central. *(frontier — verify)* proposals for SNOW-optimal index reads.

## 8. Future Work
- Closed-form staleness/anomaly bounds parameterized by network and conflict models.
- Hybrid protocols proven to invoke coordination at frequency $\le$ conflict rate.
- Self-healing reconciliation with bounded repair cost and detectability guarantees.
- Verified, machine-checked GSI maintenance specs (TLA+/Ivy) for production stores.

## 9. Key References
- **[Foundational]** A. Gupta, I. S. Mumick. *Maintenance of Materialized Views: Problems, Techniques, and Applications.* IEEE Data Eng. Bull., 1995.
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002.
- **[SOTA]** J. M. Hellerstein, P. Alvaro. *Keeping CALM: When Distributed Consistency is Easy.* CACM, 2020.
- **[SOTA]** P. Bailis, A. Fekete, M. J. Franklin, A. Ghodsi, J. M. Hellerstein, I. Stoica. *Coordination Avoidance in Database Systems (I-confluence).* VLDB, 2014.
- **[SOTA]** J. C. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[Survey]** M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski. *Conflict-free Replicated Data Types.* SSS, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
