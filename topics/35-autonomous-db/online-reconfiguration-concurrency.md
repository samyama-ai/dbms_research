# Concurrency Control for Online Reconfiguration

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/online-reconfiguration-concurrency` · **Status:** open

## 1. Problem Statement
A self-driving DBMS continuously rewrites its own **physical and logical schema**: adding/dropping indexes, repartitioning, changing layouts (row↔column), splitting/merging tablets, evolving the logical schema. Each such reconfiguration $\rho$ must execute **concurrently** with a live transaction stream while preserving:
- **Isolation correctness:** the chosen isolation level (serializability, snapshot isolation) holds over the *combined* history of user transactions and reconfiguration steps.
- **Non-blocking progress:** reconfiguration must not hold long, coarse-grained locks that stall the workload (the *availability* requirement).
- **Atomic visibility / linearizable cutover:** before some commit point readers/writers see the old structure with old semantics; after, the new one — with no torn intermediate state.

Variants:
- **Decision:** given a reconfiguration plan and an isolation level $L$, does a non-blocking concurrent execution preserving $L$ exist?
- **Optimization:** minimize makespan / lock-hold time / abort rate / extra writes subject to preserving $L$.
- **Scheduling:** order a *batch* of pending reconfigurations to minimize interference with a forecast workload.

## 2. Mathematical Foundations
Model histories as in classical concurrency theory: a **history** $H$ is a partial order over read/write/commit events. Treat each reconfiguration as a (possibly long-running) transaction $T_\rho$ emitting reads/writes plus *predicate* operations (it touches all rows matching a partition predicate), so **phantoms** appear and **predicate locking** / serialization-graph reasoning over the *conflict graph* $\mathrm{SG}(H)$ is required: $H$ is conflict-serializable iff $\mathrm{SG}(H)$ is acyclic (Bernstein–Hadzilacos–Goodman).

Key machinery:
- **Online schema change as a multi-phase state machine.** The canonical safe pattern (Google F1's online, asynchronous schema change) forbids two schema versions to differ by more than one *intermediate* state at a time; correctness is proven by showing every pair of co-existing states is mutually consistent ("no orphan / no missing data").
- **MVCC version mapping.** Under snapshot isolation a reconfiguration is correct if there is a transform $\phi$ from old to new versions such that every snapshot timestamp $t$ reads a consistent projection; $\phi$ must commute with concurrent updates.
- **Linearizability of cutover** (Herlihy–Wing): the visibility switch is an atomic register flip; backfill must be *idempotent and monotone* so concurrent writes are never lost.
- **Lock-free reasoning:** non-blocking guarantees (wait-/lock-freedom) bound worst-case interference but interact with the chase-like need to maintain index/materialized-view consistency incrementally.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Google **F1**'s asynchronous online schema change (VLDB 2013) is the reference protocol for distributed, lock-free schema evolution via staged intermediate states. PostgreSQL's `CREATE INDEX CONCURRENTLY`, MySQL/InnoDB online DDL, and **gh-ost / pt-online-schema-change** (trigger- or binlog-based shadow-table copy + cutover) are production-grade for single-table changes. Online **repartitioning** appears in Spanner, CockroachDB (range splits/merges with leaseholder handoff), and Vitesse/Vitess resharding. Microsoft's *online physical design* and self-driving prototypes (Peloton/NoisePage, OtterTune) schedule reconfiguration but largely **assume** an underlying safe primitive.

**Theory-SOTA:** classical serializability theory and predicate locking (Eswaran et al.) give correctness conditions; formal verification of F1-style staged changes has been modeled in TLA+-style specs. No general theory unifies arbitrary reconfiguration with arbitrary isolation levels under a provable non-blocking guarantee.

## 4. Upper Bound
For *single-table, single-version-step* changes, the F1 staged protocol gives a **non-blocking, serializable** reconfiguration whose extra cost is one backfill pass plus $O(1)$ catalog flips; cutover is $O(1)$ linearizable. For MVCC engines, online index build is achievable with **bounded** blocking ($O(1)$ short latch at validation) and a single consistent-snapshot scan, i.e. amortized cost proportional to table size with no long exclusive lock. These hold in the standard read/write transactional model with predicate locking.

## 5. Lower Bound
- **Multi-version-jump impossibility:** F1 proves that skipping an intermediate state (≥2 schema-version gap among concurrent nodes) can produce orphaned/missing data — a *correctness* impossibility, not merely a performance one. So a minimum number of staged steps is forced.
- **Blocking is sometimes unavoidable** under strict serializability when the reconfiguration's predicate conflicts with an in-flight transaction that has already taken a conflicting lock: a cycle in $\mathrm{SG}(H)$ must be broken by aborting or waiting (no free lunch from serialization theory).
- **CAP/coordination:** in a partitioned distributed setting, a globally atomic cutover requires coordination; by CAP it cannot be both available and strongly-consistent under partition, bounding non-blocking cutover.

## 6. The Gap
**Open.** We have safe *primitives* for narrow cases (one table, one version step, specific engines) but **no general calculus** that, given an arbitrary reconfiguration and a target isolation level, synthesizes a provably non-blocking, minimal-interference schedule — and proves the combined history correct. The gap is between per-system engineered protocols and a unifying theory with matching interference lower bounds. Closing it needs: (a) a formal language for reconfigurations as predicate-transactions, (b) a synthesis procedure producing staged plans with verified invariants, (c) interference lower bounds parameterized by workload conflict structure.

## 7. Current Research (as of June 2026)
- Verified / model-checked schema-change protocols (TLA+, Ivy) extended beyond F1 to repartitioning and layout changes. *(frontier — verify)*
- Self-driving systems (CMU NoisePage lineage, OtterTune commercial) integrating *when* and *how* to apply changes with HTAP layout migration. *(frontier — verify)*
- Lock-free / RDMA-era online reorganization in main-memory engines (HyPer/Umbra lineage at TU Munich). *(frontier — verify)*
- Cloud-native elastic resharding (Spanner, CockroachDB, TiDB teams) publishing on online range moves with bounded latency tails.

## 8. Future Work
- A general theory pairing **reconfiguration class × isolation level** with tight non-blocking feasibility results.
- Cost models that let the autonomous planner trade abort rate vs. makespan vs. write amplification, and *schedule* reconfigurations against a **forecast** workload (couples with end-to-end architecture).
- Rollback/compensation primitives so a mid-flight reconfiguration can abort safely under load spikes.
- Formal guarantees for *logical* (application-visible) schema evolution, not just physical.

## 9. Key References
- **[Foundational]** P. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)
- **[Foundational]** K. Eswaran, J. Gray, R. Lorie, I. Traiger. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[SOTA]** I. Rae, E. Rollins, J. Shute, S. Sodhi, R. Vingralek. *Online, Asynchronous Schema Change in F1.* PVLDB / VLDB, 2013. — [DOI](https://doi.org/10.14778/2536222.2536230)
- **[Foundational]** M. Herlihy, J. Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[SOTA]** N. Bruno, S. Chaudhuri. *An Online Approach to Physical Design Tuning.* ICDE, 2007. — [DBLP](https://dblp.org/rec/conf/icde/BrunoC07.html)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)

## 10. Worked Example

Take F1's "add a secondary index $I$ on column $c$" as a single logical change, and watch why one staged step is insufficient. Suppose servers may sit one schema version apart. If we jumped directly from state $S_0$ (*no index*) to $S_2$ (*index public, used for reads*), a server still on $S_0$ that **inserts** row $r$ writes no entry into $I$; a server on $S_2$ then **reads via $I$** and misses $r$ — an *orphaned* / missing-data anomaly.

F1 inserts the intermediate **`delete-only`** state $S_1$: in $S_1$ a server maintains $I$ on deletes/updates but does not serve reads from it. The staged sequence is
$$S_0 \;(\text{absent}) \to S_1 \;(\text{delete-only}) \to S_{1.5}\;(\text{write-only, backfill}) \to S_2\;(\text{public}).$$
Now any two co-existing states differ by at most one step, and every adjacent pair is mutually consistent: a writer always at least maintains entries a reader might rely on. With $N$ servers the protocol needs only $3$ catalog transitions plus one idempotent backfill scan — $O(1)$ version steps, no global lock — illustrating the upper bound of Section 4 and the multi-version-jump impossibility of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
