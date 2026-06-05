# Optimal Log Record Granularity

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/log-granularity-optimality` · **Status:** open

## 1. Problem Statement
A main-memory database must persist a recovery log so that, after a crash, a durable, transaction-consistent state can be reconstructed. The *granularity* of a log record is the abstraction level at which a transaction's effect is recorded: **physical** (before/after byte images of pages), **physiological** (per-record, "redo this operation on this slot"), **logical/operation** (a tuple-level insert/update/delete), or **command** (the parameterized stored procedure or SQL statement that produced the effect). Coarser granularity (command logging) writes far less data but forces deterministic, full re-execution during recovery; finer granularity (physiological) writes more but enables fast, parallel apply.

We seek a logging scheme — possibly *adaptive per transaction or per operation* — that **jointly minimizes** (a) steady-state log write volume / latency on the durability path and (b) expected recovery (replay) time, subject to a correctness constraint (recoverability to a transaction-consistent snapshot). Variants:
- **Decision:** Given a workload and a recovery-time budget $R$, does a granularity assignment exist with log volume $\le V$?
- **Optimization:** Minimize a cost $\alpha \cdot V + \beta \cdot \mathbb{E}[T_{\text{replay}}]$ over per-operation granularity choices.
- **Online:** Choose granularity per transaction without knowing the future workload (competitive analysis vs. an offline optimum).

## 2. Mathematical Foundations
Model a transaction $t$ as a sequence of operations $o_1,\dots,o_k$. Each operation $o_i$ admits a set $G_i$ of legal granularities; choosing $g \in G_i$ incurs log bytes $b_i(g)$ and replay cost $r_i(g)$. Command logging requires *determinism*: re-execution must be reproducible, formalized by a logical-equivalence relation $\equiv$ on schedules. Concretely, command logging is correct only if the serialization order is itself logged and the procedure is a deterministic function of its inputs and the recovered prefix state.

Let $x_i \in G_i$ denote the choice. The objective is
$$\min_{x} \;\; \alpha \sum_i b_i(x_i) \;+\; \beta\, \mathbb{E}\Big[\textstyle\sum_i r_i(x_i)\Big]$$
subject to recoverability constraints linking choices across operations (e.g., a logical update is replayable only if the index structures it touches are themselves recoverable, inducing dependency constraints $x_i \preceq x_j$). These cross-operation dependencies make the feasible set non-product, distinguishing the problem from independent per-item selection. Determinism requirements connect this to the theory of *deterministic transaction execution* (Calvin/H-Store): if the schedule is a total order fixed in advance, command logging needs only that order plus inputs — an information-theoretic lower bound of $\log_2 |\text{inputs}|$ bits per transaction.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** H-Store/VoltDB introduced **command logging** (Malviya, Weber, Madden, Stonebraker, *Rethinking Main-Memory OLTP Recovery*, ICDE 2014), showing command logging slashes log volume but raises recovery time vs. physiological ARIES-style logging. SiloR (Zheng et al., OSDI 2014) achieves high-throughput value (logical/physiological) logging with parallel recovery. Hekaton (SQL Server) uses logical logging tightly coupled to MVCC.
- **Hybrid.** *Adaptive logging* (Yao, Chen, Jagadish, et al., SIGMOD 2016) interpolates between command and ARIES logging, dynamically picking granularity to balance runtime cost against recovery time — the closest direct attack on this problem.

No system provably solves the joint-minimization optimization; choices are heuristic.

## 4. Upper Bound
For a *fixed* offline workload with independent per-operation costs and no cross-dependencies, the per-operation choice is separable and solvable in $O(\sum_i |G_i|)$. With dependency constraints forming a DAG and a recovery-time budget, the problem becomes a constrained assignment; a pseudo-polynomial DP over the budget yields $O(k \cdot R)$ time. In the online setting, a deterministic threshold policy (log commands until estimated replay risk exceeds a threshold, then switch to physiological) yields a constant-competitive ratio under bounded cost ratios $b(g)/r(g)$, analogous to ski-rental — the best general upper bound is a $2$-competitive rent-or-buy style guarantee under those assumptions.

## 5. Lower Bound
The information-theoretic floor on durable bytes is the *entropy of the committed state transition*: no recoverable scheme can write fewer than $H(\text{committed effect} \mid \text{recovered prefix})$ bits, which command logging approaches only when inputs are highly compressible and execution deterministic. The budget-constrained decision variant with arbitrary cross-operation dependencies is NP-hard by reduction from knapsack/precedence-constrained scheduling (the precedence constraints encode recoverability dependencies). In the online model, ski-rental's $2 - o(1)$ deterministic competitive lower bound transfers, so no online policy beats a factor $2$ in the worst case without prediction.

## 6. The Gap
The constant-competitive online result and pseudo-poly offline DP are clean only under simplifying independence/cost-ratio assumptions. The genuine open problem is the **realistic** joint objective where (i) recovery time depends on *parallelism* available at replay (super-linear interactions), (ii) determinism is partial (some procedures are non-deterministic), and (iii) the workload is non-stationary. No matching upper/lower bound exists for this realistic model — it is genuinely open whether a poly-time approximation with a provable ratio for $\mathbb{E}[T_{\text{replay}}]$ under parallel apply exists.

## 7. Current Research (as of June 2026)
Active directions: learned/adaptive logging policies that predict per-transaction abort and replay cost; integration with persistent memory (PMEM/CXL) that changes the $\alpha/\beta$ ratio because the durability path cost collapses *(frontier — verify)*; and deterministic-database lines (Abadi's Calvin descendants) that make command logging near-optimal by fixing the order a priori. Groups: MIT (Madden), CMU (Pavlo's NoisePage lineage on self-driving recovery), Yale (Abadi). Recent CXL-attached-memory recovery work reopens the volume/replay tradeoff *(frontier — verify)*.

## 8. Future Work
- A provable approximation for the parallel-replay objective.
- Online policies with workload prediction beating the ski-rental barrier (learning-augmented competitive analysis).
- Formal treatment of partial determinism and its byte-cost penalty.
- Co-design with NVM/CXL where the durability primitive is sub-microsecond.

## 9. Key References
- **[SOTA]** Malviya, Weisberg, Madden, Stonebraker. *Rethinking Main-Memory OLTP Recovery.* ICDE, 2014. — [DOI](https://doi.org/10.1109/ICDE.2014.6816685)
- **[SOTA]** Zheng, Tu, Kohler, Liskov. *Fast Databases with Fast Durability and Recovery through Multicore Parallelism (SiloR).* OSDI, 2014. — [DBLP](https://dblp.org/rec/conf/osdi/ZhengTKL14.html)
- **[SOTA]** Yao, Chen, Jagadish, et al. *Adaptive Logging: Optimizing Logging and Recovery Costs in Distributed In-Memory Databases.* SIGMOD, 2016. — [arXiv](https://arxiv.org/abs/1503.03653)
- **[Foundational]** Mohan, Haderle, Lindsay, Pirahesh, Schwarz. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** Thomson, Diamond, Weng, Ren, Shao, Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)

## 10. Worked Example

A stored procedure `Transfer(A,B,$100)` debits one row and credits another (2 tuple updates), invoked $N=10{,}000$ times between checkpoints.

**Command logging.** Each record = procedure name + params $\approx 40$ bytes. Steady-state volume $V_\text{cmd}=10{,}000\times40=400$ KB. Recovery must *re-execute* all 10,000 procedures: $T_\text{replay}\approx 10{,}000\times c_\text{exec}$.

**Physiological logging.** Each tuple update logs a before/after image $\approx 120$ bytes; 2 per call. Volume $V_\text{phys}=10{,}000\times2\times120=2.4$ MB ($6\times$ larger). Recovery just *applies* images: $T_\text{replay}\approx 20{,}000\times c_\text{apply}$, and $c_\text{apply}\ll c_\text{exec}$ (no logic, no contention).

**The ski-rental online choice (§4).** Suppose re-execution is $\beta$-times costlier to replay than apply. The threshold policy logs commands ("renting" cheap durability) until the estimated replay penalty exceeds the byte savings, then switches to physiological ("buying"). With cost objective $\alpha V + \beta\,\mathbb{E}[T_\text{replay}]$, the break-even is where $\alpha(V_\text{phys}-V_\text{cmd}) = \beta(T^\text{cmd}_\text{replay}-T^\text{phys}_\text{replay})$ — and the deterministic policy stays within $2\times$ of the offline optimum.

---
*Part of the [DBMS Research catalog](../../README.md).*
