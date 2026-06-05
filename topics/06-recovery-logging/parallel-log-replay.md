# Parallel log replay scalability

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/parallel-log-replay` · **Status:** partially-solved

## 1. Problem Statement
After a crash (or on a hot-standby replica, or when restoring from a backup + log), the recovery process must apply a possibly enormous redo log and roll back loser transactions. Serial replay makes recovery time scale with log volume, which on modern multi-TB-per-hour workloads can mean minutes-to-hours of downtime. The problem is to **maximally parallelize redo and undo replay across many cores/threads while respecting the dependency constraints that make replay correct** — i.e., produce the same final database state as the canonical serial replay, but in less wall-clock time.

Variants:
- **Optimization:** minimize replay makespan (or maximize speedup/scalability with cores $p$) subject to dependency constraints.
- **Decision/scheduling:** given the log's dependency DAG and $p$ workers, is a schedule with makespan $\le T$ achievable?
- **Online/streaming:** for log shipping to replicas, parallelize replay of a *continuously arriving* log while bounding apply lag and preserving read-consistent snapshots.

## 2. Mathematical Foundations
The log induces a **dependency DAG** $G=(V,E)$: vertices are log records (or sub-transactions), and an edge $u\to v$ means $v$ must be applied after $u$. Two records *conflict* (and must be ordered) when they touch the same page/key and at least one writes — a per-object **conflict (Bernstein-style) serialization** constraint. Page-granularity LSN ordering is the classic sufficient condition: redo records to the *same page* must be applied in LSN order; records to disjoint pages are independent and parallelizable.

Replay is then **DAG scheduling**: minimize makespan on $p$ identical machines. With the critical-path length $C_\infty$ (longest dependency chain) and total work $C_1$, **Graham's bound / Brent's theorem** give makespan $C_p \le C_1/p + C_\infty$, and any greedy list scheduler is within a factor $2$ of optimal. The achievable speedup is capped by **parallelism** $C_1/C_\infty$; a long chain of updates to one hot page is an Amdahl bottleneck. Finer partitioning (per-record, per-key, logical "command" replay) shrinks $C_\infty$ at the cost of dependency-tracking overhead. Minimizing makespan exactly on a DAG is **NP-hard** (P|prec|$C_{\max}$).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Parallel redo by page-hash partitioning is mature — **SQL Server** parallel/accelerated recovery, **Oracle** parallel media recovery, **PostgreSQL** recovery prefetch (`recovery_prefetch`, 14+) and the long-running effort toward parallel WAL apply, **MySQL/InnoDB** multi-threaded redo apply. Replica-side: **MySQL multi-threaded replication** (logical-clock / writeset-based, `binlog_transaction_dependency_tracking = WRITESET`) parallelizes apply by computing transaction writesets and only serializing conflicts. Microsoft **Hekaton**/in-memory engines exploit per-record independence for near-linear redo.
- **Theory-SOTA:** the scheduling reduction is classical; the database contribution is the *dependency-extraction* side — writeset/commit-timestamp tracking that produces a maximally sparse DAG cheaply.

## 4. Upper Bound
A greedy list scheduler over the page/writeset DAG achieves makespan $C_p \le C_1/p + C_\infty$, i.e. a **$(2-1/p)$-approximation** to optimal makespan (Graham, 1969) in the PRAM/identical-machines model. Speedup is therefore bounded by the DAG's parallelism $C_1/C_\infty$; with sufficiently fine (per-key/logical) records and uniform skew, $C_\infty$ shrinks and speedup approaches linear until I/O bandwidth saturates. Writeset-based replica apply gives near-linear apply throughput on conflict-sparse OLTP in practice.

## 5. Lower Bound
Two hard limits. (1) **Combinatorial:** makespan minimization on precedence-constrained DAGs is NP-hard, and even with $\le 3$ distinct execution times no PTAS is known; for general DAGs there is a conditional inapproximability (Svensson, under a variant of the Unique Games / new hardness assumptions) ruling out $(2-\epsilon)$ on related machines. (2) **Structural / Amdahl:** any schedule has makespan $\ge \max(C_1/p,\ C_\infty)$; a hot page or a long write-write chain forces $C_\infty$ to dominate, so no amount of cores helps — an information-theoretic floor set by the workload's serialization graph, independent of algorithm.

## 6. The Gap
The makespan-scheduling gap (Graham's $2$ vs. NP-hardness) is essentially closed *as a scheduling problem*. The genuinely open, **partially-solved** part is **cheap, fine-grained dependency extraction**: page-granularity over-serializes (false conflicts on hot pages), while per-record logical tracking costs CPU and log space. The frontier is (i) reducing $C_\infty$ by logical/command replay without paying prohibitive tracking overhead, and (ii) overlapping replay with I/O prefetch so the bound that bites is bandwidth, not the schedule. No system today provably achieves the workload-optimal $C_\infty$ with bounded tracking overhead.

## 7. Current Research (as of June 2026)
- **Disaggregated / log-as-the-database** clouds (Aurora, Socrates, Neon, PolarDB) push redo to the storage tier and apply continuously and in parallel per page-group, making "recovery" near-instant; optimal scheduling of that distributed apply is active *(frontier — verify)*.
- Learned/skew-aware partitioning of the redo stream to balance worker load under hot-key skew *(frontier — verify)*.
- Constant-time / "instant" recovery that defers replay to first-access page faults (Graefe's instant-recovery line) combined with background parallel apply.
- Parallel **undo** (rollback of losers) is less studied than redo and is receiving renewed attention for long-running aborts.

## 8. Future Work
- Provably makespan-optimal replay schedulers under realistic skew with bounded dependency-tracking cost.
- Unified redo+undo parallel scheduling with read-consistent intermediate snapshots for replicas.
- Co-design of log record granularity with the replay scheduler (choose the DAG you will later schedule).
- Energy/contention-aware scheduling on many-core and NUMA hardware.

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H. & Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992.
- **[Foundational]** Graham, R. L. *Bounds on Multiprocessing Timing Anomalies.* SIAM J. Applied Math, 1969.
- **[Foundational]** Bernstein, P. A., Hadzilacos, V. & Goodman, N. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[SOTA]** Graefe, G. *Instant Recovery for Data Center Savings.* ACM SIGMOD Record, 2015 (and the instant-recovery line, Graefe, Guy, Sauer).
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017.
- **[Survey]** Sauer, C., Graefe, G. & Härder, T. *Instant Restore After a Media Failure.* ADBIS / VLDB-J line, 2017–2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
