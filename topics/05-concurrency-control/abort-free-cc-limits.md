# Abort-Free Concurrency Control Limits

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/abort-free-cc-limits` · **Status:** open

## 1. Problem Statement
Optimistic and timestamp-ordered concurrency control protocols **abort** transactions to preserve serializability; aborts waste work, and under contention can cause livelock and unbounded latency. The problem: **characterize the classes of workloads (transaction programs + arrival patterns) for which a serializable schedule can be produced with no aborts (abort-free) and/or no waiting (wait-free)** — and, dually, prove when aborts/waiting are *unavoidable*.

Variants:
- *Abort-freedom:* every submitted transaction commits (possibly after waiting) — exists a serializable schedule with zero aborts?
- *Wait-freedom:* every transaction commits in a bounded number of its own steps regardless of others (a liveness guarantee borrowed from shared-memory theory).
- *Optimization:* among abort-free schedules, maximize concurrency/throughput, or minimize total blocking.
- *Online/competitive:* a scheduler sees transactions arrive online; bound its abort count against an offline optimum.

The deep tension: serializability is a *safety* property; abort-/wait-freedom are *progress* properties. Combining strong safety with strong progress is exactly where impossibility results bite.

## 2. Mathematical Foundations
- **Serializability theory** (Bernstein–Hadzilacos–Goodman; Papadimitriou 1979): a schedule is conflict-serializable iff its conflict graph is acyclic; producing such schedules online is the scheduler's job. **Conflict-serializability recognition is polynomial; view/general serializability is NP-complete.**
- **Scheduling formulation:** with read/write sets known in advance, abort-free serializable scheduling relates to **acyclic orientation / interval scheduling** on the conflict graph; with unknown (data-dependent) accesses it becomes an online problem.
- **Transactional-memory progress theory:** the relevant impossibility results come from **STM/shared-memory**: Guerraoui–Kapałka, *Principles of Transactional Memory*, prove that **obstruction-free / wait-free TM cannot in general be both consistent (opaque/serializable) and provide strong progress** under certain conditions; an *online* TM cannot be both serializable and wait-free against an adversary that creates conflicts. Wait-freedom in the asynchronous shared-memory sense is tied to the **consensus hierarchy** (Herlihy 1991): primitives with consensus number 1 cannot implement wait-free objects that effectively require consensus.
- **Workload structure:** classes likely to admit abort-freedom include *conflict-free / commutative* operations (CRDT-like, $\mathcal{I}$-confluent), *single-key* transactions, *phase-partitioned* (e.g., deterministic Calvin batches), and *acyclic access-graph* workloads (where a static analysis proves the conflict graph is a forest/DAG).

## 3. State of the Art (SOTA)
**Theory-SOTA.** Guerraoui–Kapałka's monograph delineates which progress+safety combinations are achievable for transactional memory, including impossibility of certain wait-free serializable TMs. For databases, the *deterministic database* line (Calvin; Thomson–Abadi, SIGMOD 2012) shows that **pre-declaring read/write sets and pre-agreeing an order eliminates aborts due to concurrency** — the schedule is decided up front, so concurrency control never aborts (only deadlock-avoidance ordering remains).

**Systems-SOTA.**
- **Calvin / deterministic DBs (FaunaDB):** abort-free for concurrency reasons by deterministic sequencing; aborts only for logic/integrity.
- **Commutativity-exploiting CC:** Doppel/phase reconciliation (Narula et al., OSDI 2014) makes highly-contended commutative operations near-abort-free.
- **Star/2PL with deterministic ordering, and bounded-staleness MVCC** reduce but do not eliminate aborts.
- Practical wait-free guarantees remain rare; most systems offer only obstruction-freedom or lock-based blocking.

## 4. Upper Bound
- **Deterministic execution (Calvin):** with full read/write-set pre-declaration and a deterministic global order, concurrency-induced aborts $= 0$; cost is the pre-declaration / reconnaissance overhead and reduced flexibility. Holds in the **deterministic database model**.
- **Commutative workloads:** for operations forming a commutative monoid (or $\mathcal{I}$-confluent set), serializable abort-free execution is achievable with $O(1)$ coordination per op (Doppel; coordination-avoidance results), provably.
- **Acyclic/known-conflict workloads:** if the static conflict graph is acyclic, a topological-order schedule commits all transactions without abort, computable in $O(V+E)$.

## 5. Lower Bound
- **Online impossibility:** against an adaptive adversary that introduces conflicts after a transaction has read, no *online* serializable scheduler can guarantee abort-freedom without **waiting/blocking** — blocking is required, and unbounded blocking violates wait-freedom; thus *serializable + wait-free + online* is impossible in general (TM impossibility results, Guerraoui–Kapałka).
- **Consensus/FLP barrier:** wait-free implementations that must agree on a commit order reduce to consensus; with only read/write registers (consensus number 1) this is impossible (Herlihy 1991; FLP 1985).
- **NP-hardness:** maximizing committed transactions (minimizing aborts) over a general conflict structure with view-serializability is NP-hard (Papadimitriou 1979).

## 6. The Gap
The boundary between abort-admitting and abort-free workloads is only partially mapped. We have clean *positive* classes (commutative, single-key, deterministic-with-predeclared-sets, statically-acyclic) and clean *negative* results (adversarial online serializable+wait-free is impossible). The **open gap** is a *complete characterization*: a precise structural/complexity criterion that, given a workload description, decides "abort-free serializable schedulable?" and quantifies the minimal blocking required when it is. No tight dividing line — and no tight competitive-ratio bounds for online abort minimization — currently exist. Genuinely open.

## 7. Current Research (as of June 2026)
- Pushing **deterministic / batch** databases to richer (non-pre-declarable) workloads via cheap reconnaissance, narrowing the predeclaration cost. *(frontier — verify)*
- **Commutativity inference** (automatically detecting when operations commute to enable abort-freedom) and integration with verified weak isolation. *(frontier — verify)*
- Competitive analysis of online CC schedulers; connections to scheduling theory and to the TM progress hierarchy. Groups: Abadi/Thomson (deterministic DBs), Liskov/Madden lineage (Doppel), Guerraoui (EPFL, TM theory).

## 8. Future Work
- A decidable structural criterion + complexity for abort-free serializable schedulability.
- Tight competitive ratios for online abort minimization under realistic (oblivious vs adaptive) adversaries.
- Hybrid schedulers that prove abort-freedom for a workload subset and fall back gracefully otherwise.

## 9. Key References
- **[Foundational]** C. H. Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** M. Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[Foundational]** R. Guerraoui, M. Kapałka. *Principles of Transactional Memory.* Morgan & Claypool, 2010. — [ACM](https://dl.acm.org/doi/10.5555/3019225)
- **[SOTA]** A. Thomson, T. Diamond, S.-C. Weng, K. Ren, P. Shao, D. J. Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[SOTA]** N. Narula, C. Cutler, E. Kohler, R. Morris. *Phase Reconciliation for Contended In-Memory Transactions (Doppel).* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/narula)

## 10. Worked Example

Consider three transactions on items $\{x,y\}$ with footprints declared up front:
$T_1=\{r(x),w(y)\}$, $T_2=\{r(y),w(x)\}$, $T_3=\{r(x)\}$. Build the static conflict graph from non-commuting pairs: $T_1\xrightarrow{w(y)\,r(y)}T_2$ and $T_2\xrightarrow{w(x)\,r(x)}T_1$ — a 2-cycle. An *online* optimistic scheduler that lets $T_1,T_2$ read concurrently then validate is forced to abort one (the cycle is non-serializable as run).

Now apply the deterministic (Calvin) recipe: pre-agree the global order $T_1<T_2<T_3$ before execution. Every node executes accesses respecting this order; $T_2$ waits for $T_1$'s $w(y)$, so the realized schedule is the serial $T_1;T_2;T_3$ — acyclic, **zero concurrency-induced aborts**. The cost is the up-front footprint declaration plus blocking $T_2$. This illustrates the section-4 upper bound (predeclared sets $\Rightarrow$ aborts $=0$) against the section-5 lower bound (the online adversary that created the cycle forced either an abort or blocking).

---
*Part of the [DBMS Research catalog](../../README.md).*
