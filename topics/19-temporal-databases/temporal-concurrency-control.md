# Temporal Data Model Concurrency

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-concurrency-control` · **Status:** open

## 1. Problem Statement
Temporal databases keep *versioned histories*: a logical record maps to a sequence of versions distinguished by **transaction time** (system-versioned, append-only and immutable once committed) and/or **valid time** (application-time, freely updatable). The concurrency-control problem is to define and enforce an isolation criterion over this versioned, **append-mostly** workload that is both *correct* (serializable, or a well-specified weaker level) and *efficient* given the structure: writes overwhelmingly *append new versions* rather than overwrite, and reads frequently scan period-overlapping ranges ("as-of $\tau$", "between $\tau_1,\tau_2$").

Concretely we want protocols answering:
- **Decision (correctness):** given a schedule of temporal transactions (each a set of as-of reads and version-appends plus valid-time period updates), is it serializable / temporally consistent?
- **Synthesis (protocol):** a scheduler — MVCC variant, OCC, or 2PL specialization — admitting a maximal set of conflict-free interleavings of append-mostly histories.
- **Optimization:** minimize abort rate / latency / version-storage and index churn while preserving the chosen isolation level, exploiting that committed transaction-time versions are immutable.

The distinguishing subtlety versus ordinary MVCC: the *version chain is itself the user-visible history*, so reads of the past must be **non-blocking and never abort**, valid-time updates create **interval write–write conflicts** (period overlap, not point key equality), and "now" is a moving target (now-relative bounds) that makes predicate locks span an open-ended interval.

## 2. Mathematical Foundations
Model a temporal database as a set of versioned objects; object $x$ has a version set $V(x)=\{(v_i, \mathit{tt}_i, \mathit{vt}_i)\}$ where $\mathit{tt}_i$ is a transaction-time period $[c_i, \infty)$ closed by a later delete, and $\mathit{vt}_i$ a valid-time period $[a_i,b_i)$. A history $H$ is a partial order over operations $r_T(x\,@\,\tau)$, $\mathit{append}_T(x, v, \mathit{vt})$, $\mathit{logical\text{-}delete}_T(x\,@\,\mathit{tt})$.

Correctness is **conflict serializability** lifted with version order: as in **Multiversion Serializability** (Bernstein–Goodman–Hadzilacos), a multiversion history is correct iff it is *view-equivalent* to a serial monoversion history; this is captured by acyclicity of the **multiversion serialization graph** $\mathrm{MVSG}(H,\ll)$ over some version order $\ll$. Testing whether *some* version order makes $\mathrm{MVSG}$ acyclic is **NP-complete** in general (Papadimitriou; Bernstein–Goodman). Snapshot isolation is characterized by Adya's *Generalized Isolation Levels* via forbidding anomaly cycles with **rw-antidependency** edges; Cahill–Röhm–Fekete's **Serializable Snapshot Isolation (SSI)** forbids two consecutive rw-edges on a "dangerous structure" $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_3$.

Valid-time write conflicts are **interval conflicts**: two appends conflict iff their valid-time periods overlap on the same key, i.e. a *stabbing/overlap* predicate, linking concurrency control to interval/predicate locking and to the *commutativity* of append operations: appends with disjoint $\mathit{vt}$ on the same key **commute**, an algebraic fact that admits more interleavings than key-level locking sees.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Multiversion serializability theory (Bernstein–Hadzilacos–Goodman, 1987) remains the correctness backbone; Adya's cycle-based isolation characterization (1999) and **SSI** (Cahill et al., SIGMOD 2008; TODS 2009) give the practical serializable-over-snapshot result, implemented in PostgreSQL. For append-mostly logs, **timestamp-ordering** and epoch-based validation dominate.

**Systems-SOTA:** SQL:2011 system-versioned and application-time tables fix the syntax; engines realize concurrency very differently. MVCC over immutable committed versions is the natural fit — *committed transaction-time history is read without locks and never causes a writer to abort a historical reader*. **Hekaton** (Larson et al., VLDB 2011/2012) and **HyPer/Umbra** (Neumann–Mühlbauer–Kemper, SIGMOD 2015 serializable MVCC) provide the high-performance optimistic MVCC validation that temporal stores inherit. MariaDB, SQL Server, DB2, and Teradata implement system-versioning atop their existing MVCC/2PL.

## 4. Upper Bound
For the **synthesis/runtime** problem, optimistic MVCC with precision-locking validation (Neumann et al., SIGMOD 2015) certifies serializability of a committing transaction in time *proportional to its read/write set against concurrent writes*, with as-of/historical reads served in $O(1)$ extra synchronization (no locks, no aborts) since committed versions are immutable — the strongest practical upper bound for append-mostly histories. SSI adds $O(1)$-amortized rw-edge bookkeeping per conflicting access to upgrade snapshot isolation to serializable. Interval write conflicts are detected with a temporal/interval index (interval tree, or `range`/GiST) giving $O(\log n + k)$ overlap tests per append. These are **RAM-model** runtime bounds, not optimality results.

## 5. Lower Bound
Deciding whether a multiversion history is serializable **for some version order** is **NP-complete** (Papadimitriou 1979; Bernstein–Shipman–Wong / Bernstein–Goodman for the multiversion case) — so any online scheduler must commit to version order heuristically, accepting either lost concurrency or run-time aborts. Independently, no protocol can be simultaneously **serializable, non-blocking for reads, and abort-free for writers** in the presence of rw-conflicts: this is the multiversion analogue of the impossibility that snapshot isolation cannot be made serializable without *either* aborts *or* blocking (the "write-skew" anomaly is unavoidable under pure first-committer-wins). For distributed temporal stores, the **CAP** theorem (Gilbert–Lynch, 2002) bounds availability of as-of-now reads under partition, and **FLP** (Fischer–Lynch–Paterson, 1985) bounds agreement on commit order/timestamps.

## 6. The Gap
The *correctness theory* is essentially closed: multiversion serializability and its cycle characterizations are tight. The genuine open gap is **how much extra concurrency the append-mostly + interval-commutativity structure buys** over generic MVCC, and whether a scheduler can *provably* exploit valid-time disjointness to admit a strictly larger conflict-free class than SSI without unbounded validation cost. No tight characterization exists of the optimal abort rate for temporal workloads, nor a matching lower bound showing SSI/precision-locking is optimal for them. Likewise, **distributed bitemporal commit ordering** — reconciling transaction-time monotonicity with valid-time correctness across partitions — lacks a tight protocol-vs-impossibility boundary.

## 7. Current Research (as of June 2026)
Active directions: (i) extending serializable MVCC validation (HyPer/Umbra lineage — Neumann, Kemper, Leis) to first-class temporal/period predicates so interval-overlap antidependencies are tracked precisely rather than over-conservatively; (ii) **commutativity-aware** concurrency control treating disjoint valid-time appends as commuting, building on transactional-boosting/abstract-lock ideas; (iii) lock-free, epoch-reclaimed version chains for immutable transaction-time history with non-blocking time-travel reads. *(frontier — verify)* Recent work reports HTAP engines serving as-of historical scans entirely lock-free while running serializable OLTP via optimistic validation, and explores **deterministic** scheduling (Calvin-style) to sidestep distributed commit-order agreement for bitemporal data. Groups: Snodgrass/Dignös/Böhlen/Gamper (temporal semantics), Neumann/Leis (MVCC), Fekete/Röhm (isolation theory).

## 8. Future Work
- A tight concurrency characterization for append-mostly histories exploiting valid-time **interval commutativity**, with a matching lower bound on achievable abort rate.
- Non-blocking, abort-free **time-travel reads** as a proven guarantee co-existing with serializable current-time updates.
- Concurrency control for **now-relative / indeterminate** valid-time bounds, where the conflict predicate itself moves with the clock.
- Distributed bitemporal commit protocols reconciling transaction-time monotonicity with valid-time consistency under CAP/FLP constraints; deterministic vs optimistic trade-offs.
- Storage/index co-design so version-chain growth and temporal-index maintenance do not erode the append-mostly advantage.

## 9. Key References
- **[Foundational]** Bernstein, P., Hadzilacos, V., Goodman, N. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. (multiversion serializability theory)
- **[Foundational]** Papadimitriou, C. *The Serializability of Concurrent Database Updates.* JACM, 1979. (NP-completeness of serializability testing)
- **[SOTA]** Cahill, M., Röhm, U., Fekete, A. *Serializable Isolation for Snapshot Databases.* SIGMOD 2008 / ACM TODS, 2009.
- **[SOTA]** Neumann, T., Mühlbauer, T., Kemper, A. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015.
- **[Foundational]** Adya, A., Liskov, B., O'Neil, P. *Generalized Isolation Level Definitions.* ICDE, 2000.
- **[Survey]** Kulkarni, K., Michels, J.-E. *Temporal Features in SQL:2011.* SIGMOD Record, 2012.
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002.

---
*Part of the [DBMS Research catalog](../../README.md).*
