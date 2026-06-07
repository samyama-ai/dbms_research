---
id: 06-recovery-logging/recovery-time-slo
title: "Recovery-time SLO guarantees"
topic: 06-recovery-logging
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Recovery-time SLO guarantees

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/recovery-time-slo` · **Status:** open

## 1. Problem Statement
Operators promise **Recovery Time Objectives (RTO)** — "after a crash, the database is available within $T_{\text{SLO}}$" — but engines deliver recovery time only *empirically*; it emerges from log length, dirty-page state, replay parallelism, and buffer warm-up, and is rarely a *guaranteed, provable* quantity. The problem: make worst-case recovery time a **first-class, schedulable resource** — a quantity the system continuously bounds and admits/throttles work against, with a *provable* guarantee that post-crash recovery completes within $T_{\text{SLO}}$ (ideally with high probability $1-\delta$ over crash timing).

This means: (i) a model that upper-bounds recovery time as a function of controllable state, (ii) a runtime mechanism that keeps that bound $\le T_{\text{SLO}}$ by regulating checkpointing/flushing/log growth, and (iii) admission/scheduling that treats "recovery-time budget" like CPU or memory — reserved, accounted, and enforced.

**Variants.** *Decision:* is current state recovery-safe (predicted $T_{\text{rec}}\le T_{\text{SLO}}$)? *Optimization:* maximize throughput s.t. $T_{\text{rec}}\le T_{\text{SLO}}$ always. *Scheduling:* allocate a recovery-time budget across tenants/shards (multi-tenant RTO). The lack of *provable* worst-case guarantees in real engines keeps this **open**.

## 2. Mathematical Foundations
Decompose recovery into **analysis + redo + undo** (ARIES) plus optional buffer warm-up:
$$T_{\text{rec}} \le T_{\text{analysis}} + \frac{R_{\text{redo}}}{\beta_{\text{redo}}} + \frac{R_{\text{undo}}}{\beta_{\text{undo}}},$$
where $R_{\text{redo}}$ is redo log bytes from the oldest dirty-page `recLSN` (bounded by checkpoint/flush policy), $\beta$ are replay bandwidths (scaling with recovery parallelism $P$), and $T_{\text{undo}}$ depends on the longest in-flight transaction's work. To *bound* $T_{\text{rec}}$, the system must bound $R_{\text{redo}}$ (cap unflushed dirty data) and bound undo work (cap in-flight transaction size/age). This is precisely a **real-time scheduling / admission-control** problem: treat the recovery budget $T_{\text{SLO}}$ as a deadline and the dirty-state growth as a task that must be "serviced" (flushed) fast enough — analogous to rate-monotonic / EDF feasibility tests, where flushing is the periodic task and write traffic is the demand.

Probabilistic framing: with stochastic crash arrival and workload, guarantee $\Pr[T_{\text{rec}} > T_{\text{SLO}}] \le \delta$ — a chance-constrained control problem. Multi-tenant RTO is a *resource-allocation/scheduling* problem over a shared flush/replay capacity, with feasibility governed by a utilization bound $\sum_i U_i \le 1$ analogous to classic schedulability.

## 3. State of the Art (SOTA)
**Systems-SOTA.** SQL Server *indirect checkpoints* expose `TARGET_RECOVERY_TIME`, the closest deployed *recovery-time-as-knob* mechanism — the engine flushes to keep redo bounded to the target. InnoDB adaptive flushing bounds redo-log fill (an indirect recovery cap). Cloud databases advertise RTO/RPO and meet them via fast failover to replicas (Aurora's storage-level redo replay; Spanner/CockroachDB Raft failover) rather than single-node redo — turning "recovery" into "promote a hot standby" with near-zero RTO at the cost of replication. *Instant/constant-time recovery* (SAP HANA, and the "Constant Time Recovery" line in SQL Server via persistent version store) makes database availability independent of in-flight transaction size by deferring undo.

**Theory-SOTA.** ARIES gives the cost decomposition; real-time scheduling theory (Liu–Layland, EDF) supplies feasibility tests, but a unified *provable RTO* framework binding flush scheduling to a deadline guarantee is not standard in engines.

## 4. Upper Bound
With indirect/target-driven checkpointing that caps $R_{\text{redo}}$ to $\rho$ and parallel redo at bandwidth $\beta P$, recovery is bounded $T_{\text{rec}} \le T_{\text{analysis}} + \rho/(\beta P) + T_{\text{undo}}$; *constant-time recovery* removes the $T_{\text{undo}}$ dependence by deferring undo (logical/MVCC version cleanup), yielding availability time independent of transaction size. Replica failover gives $T_{\text{RTO}} \le$ failover-detection + promotion time, effectively $O(\text{seconds})$ regardless of log length, at replication cost. These are the best-known constructive upper bounds (SQL Server / Aurora / Spanner), in the WAL + replicated-state-machine model.

## 5. Lower Bound
For single-node redo-based recovery, $T_{\text{rec}} \ge R_{\text{redo}}/\beta_{\max}$: you must read and replay the redo since the last consistent point, lower-bounded by I/O bandwidth — an information-theoretic floor. Bounding it below $T_{\text{SLO}}$ *forces* flushing fast enough, and under adversarial write bursts no bounded flush rate can keep $R_{\text{redo}}$ small without throttling throughput (a competitive/online lower bound: an oblivious adversary forces either SLA violation or throughput loss, mirroring online-paging $k$-competitiveness). For replicated failover, FLP and consensus lower bounds floor failover/agreement latency under asynchrony. The hardness is *information-theoretic (I/O) + competitive (online) + consensus (FLP)*, not NP-hardness.

## 6. The Gap
The gap is between **empirical** RTO (engines *usually* recover in time) and **provable worst-case** RTO treated as a scheduled, enforced resource. No mainstream engine offers a feasibility test guaranteeing $T_{\text{rec}}\le T_{\text{SLO}}$ under all admissible workloads, nor multi-tenant recovery-budget scheduling with isolation. It is genuinely open whether, for characterized (bounded-burst) workloads, an admission-control + flush-scheduling mechanism gives a *provable* RTO with near-optimal throughput. Closing it needs a faithful recovery-cost model, a schedulability theory mapping flush capacity to the deadline, and enforcement that throttles only when necessary.

## 7. Current Research (as of June 2026)
Active: constant-time / instant recovery extended to more engines; cloud providers tightening RTO via faster failover and storage-side redo; learned recovery-time predictors feeding admission control *(frontier — verify)*; recovery-time-as-a-resource framing in serverless/multi-tenant databases where many tenants share flush/replay capacity *(frontier — verify)*. Groups: Microsoft (Constant Time Recovery, SQL Server team), SAP HANA recovery team, AWS Aurora, and academic real-time/database crossovers. Connections to self-tuning recovery and epoch durability are increasingly explicit.

## 8. Future Work
(i) A schedulability theory for recovery time (EDF/utilization-bound analogue for flushing vs. RTO deadline). (ii) Multi-tenant recovery-budget isolation and reservation. (iii) Provable RTO under bounded-burst adversaries with throughput near-optimality. (iv) Composing single-node bounds with replica-failover RTO into an end-to-end guarantee. (v) Recovery-time SLO as a first-class field in the query optimizer / admission controller.

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[SOTA]** Antonopoulos, P. et al. *Constant Time Recovery in Azure SQL Database.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3352063.3352131)
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056101)
- **[Foundational]** Liu, C.L., Layland, J. *Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment.* JACM, 1973. — [DOI](https://doi.org/10.1145/321738.321743)
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Survey]** Härder, T., Reuter, A. *Principles of Transaction-Oriented Database Recovery.* ACM Computing Surveys, 1983. — [DOI](https://doi.org/10.1145/289.291)

## 10. Worked Example

Suppose the SLO is $T_{\text{SLO}} = 60\,s$ and the workload writes redo at $w = 200\,\text{MB/s}$. Recovery replays at $\beta P = 800\,\text{MB/s}$ with $P=4$ parallel workers, after a fixed $T_{\text{analysis}} = 5\,s$, and constant-time recovery defers undo so $T_{\text{undo}} \approx 0$. The budget for redo replay is $60 - 5 = 55\,s$, so the *maximum tolerable unflushed redo* is

$$\rho_{\max} = \beta P \cdot 55\,s = 800 \times 55 = 44{,}000\,\text{MB} = 44\,\text{GB}.$$

Indirect/target-driven checkpointing must therefore cap dirty redo at $\le 44\,\text{GB}$. At the write rate, redo reaches that cap in $\rho_{\max}/w = 44000/200 = 220\,s$, so a checkpoint flushing every $\le 220\,s$ keeps $T_{\text{rec}}\le 60\,s$.

Schedulability view: treat flushing as a periodic task with utilization $U = w/(\text{flush BW})$. If flush bandwidth is $400\,\text{MB/s}$, then $U = 200/400 = 0.5 \le 1$ — feasible. The lower bound bites if an adversarial burst pushes $w$ above flush capacity: then $R_{\text{redo}}$ grows unbounded unless throughput is throttled — the open SLA-vs-throughput tension.

---
*Part of the [DBMS Research catalog](../../README.md).*
