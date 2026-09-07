---
id: 05-concurrency-control/real-time-cc-deadlines
title: "Real-Time Concurrency Control Guarantees"
topic: 05-concurrency-control
status: open
first_added: 2026-06
last_reviewed: 2026-09
last_substantive_update: 2026-09
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Real-Time Concurrency Control Guarantees

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/real-time-cc-deadlines` · **Status:** open

## 1. Problem Statement

A **real-time database** transaction carries a deadline; value accrues only if the transaction commits in time (hard deadlines: zero value past deadline; firm: discard; soft: decaying value). Concurrency control (CC) must preserve correctness (serializability or a defined weaker level) **and** schedule conflicting transactions so as to satisfy timing constraints. The difficulty is the interaction: a CC mechanism induces *blocking* (2PL), *restarts* (OCC), or *priority inversion* (a low-priority transaction holding a lock needed by a high-priority, deadline-tight one). The problem is to design CC with **provable deadline-miss bounds** — guarantees of the form "no transaction in feasible set $\mathcal{F}$ misses its deadline" or "the miss ratio is at most $\rho$ under load $U$."

Variants: **decision/schedulability** — given a transaction set with deadlines, periods, WCETs, and a conflict structure, is it schedulable under CC policy $P$? **optimization** — minimize weighted deadline misses (or maximize accrued value) online. **competitive** — bound the online miss/value ratio against a clairvoyant optimum.

## 2. Mathematical Foundations

Combine real-time scheduling theory with serialization theory. A transaction $T_i$ has release time $r_i$, deadline $d_i$, worst-case execution time $C_i$, and a set of data items (resources) it accesses. Without conflicts, **EDF (earliest-deadline-first)** is optimal on one processor and schedulable iff utilization $U = \sum_i C_i / P_i \le 1$. Data conflicts act as **shared resources**; classic results bound the **blocking term** $B_i$ a job suffers, modifying the test to

$$\forall i:\quad \sum_{j:\, d_j \le d_i} \frac{C_j}{P_j} + \frac{B_i}{P_i} \le 1,$$

with $B_i$ governed by the resource protocol. The **Priority Ceiling Protocol** (Sha, Rajkumar, Lehoczky, 1990) bounds $B_i$ to the duration of a *single* lower-priority critical section and prevents deadlock and chained inversion. Serializability adds the constraint that the committed schedule's conflict graph be acyclic, so the scheduler optimizes deadlines *subject to* an acyclicity constraint — a constrained online scheduling problem. Online firm-deadline scheduling with overload connects to the $\mathcal{O}(1/4)$-competitive bound of TD1/$D^{over}$-style results.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Priority Ceiling / Stack Resource Policy give analyzable blocking bounds for lock-based real-time CC. Abbott & Garcia-Molina (TODS 1992) pioneered real-time CC scheduling (priority-based 2PL with priority inheritance/abort). OCC variants with priority (OCC-TI, OCC broadcast commit; Haritsa, Carey, Livny, 1990s) tune restart vs. block for firm deadlines. Mixed-criticality scheduling theory (Vestal, RTSS 2007; Baruah et al.) provides the modern framework for differentiated timing guarantees.

**Systems-SOTA:** Real-time and time-sensitive data systems remain niche; in-memory deterministic engines and predictable-latency stores (e.g., bounded-tail-latency KV stores, automotive/industrial time-series DBs) are the practical embodiments, but few provide *provable* per-transaction deadline bounds end to end.

## 4. Upper Bound

For lock-based CC with the Priority Ceiling Protocol on a uniprocessor, blocking is bounded by a single critical section, and the EDF+PCP schedulability test above is *sufficient* — giving a provable "no miss in $\mathcal{F}$" guarantee when satisfied. For firm-deadline overload, online scheduling admits constant-competitive value guarantees ($\tfrac14$-competitive against clairvoyant for unit-value, importance-ratio-1 jobs). OCC with priority-abort bounds wasted work to the contending lower-priority transaction's progress. These hold in the uniprocessor real-time model; multiprocessor/distributed bounds are markedly weaker.

## 5. Lower Bound

Online firm-deadline scheduling under overload is provably hard: no online algorithm can be better than $\tfrac14$-competitive in accrued value against a clairvoyant adversary even without data conflicts (Baruah et al. competitive-analysis lower bound), and with conflicts the adversary is strictly stronger. On multiprocessors, global EDF suffers utilization loss (Dhall's effect), so 100% utilization guarantees are impossible. Deciding feasibility of a conflicting transaction set with arbitrary precedence/resource constraints is **NP-hard** (general resource-constrained scheduling). Distributed timing adds FLP-style limits: under asynchrony with crashes you cannot bound commit latency, so hard end-to-end deadlines are *impossible* without synchrony assumptions.

## 6. The Gap

**Open.** Uniprocessor lock-based CC has clean schedulability tests, but (i) OCC/MVCC and modern multiversion engines lack tight, composable deadline-miss bounds; (ii) multiprocessor and distributed real-time CC have no matching upper/lower characterization; (iii) serializability-preserving online value-maximization has constant-competitive bounds only in restricted settings. The integration of mixed-criticality theory with transactional CC is largely unmapped, leaving a wide gap between practical heuristics and provable guarantees.

## 7. Current Research (as of June 2026)

Directions: predictable-latency in-memory transactional engines with WCET-style analysis; bringing **mixed-criticality** scheduling to MVCC commit pipelines; real-time guarantees for edge/IoT and automotive (AUTOSAR-adjacent) data stores *(frontier — verify)*. Communities: RTSS/RTAS/ECRTS real-time-systems researchers (Baruah, Davis, Brandenburg on real-time locking/MrsP), intersecting with data-systems groups exploring tail-latency SLOs. Real-time concerns also resurface in streaming/CEP systems with latency contracts.

## 8. Future Work

- Composable deadline-miss bounds for OCC/MVCC and multiversion commit protocols.
- Multiprocessor and distributed real-time CC with provable schedulability tests.
- Competitive online algorithms for serializability-constrained value maximization under overload.
- A unifying mixed-criticality transaction model spanning hard/firm/soft deadlines.

## 9. Key References

- **[Foundational]** Sha, L.; Rajkumar, R.; Lehoczky, J. *Priority Inheritance Protocols: An Approach to Real-Time Synchronization.* IEEE Trans. Computers, 1990. — [DOI](https://doi.org/10.1109/12.57058)
- **[Foundational]** Abbott, R.; Garcia-Molina, H. *Scheduling Real-Time Transactions: A Performance Evaluation.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/132271.132276)
- **[Foundational]** Haritsa, J.; Carey, M.; Livny, M. *Data Access Scheduling in Firm Real-Time Database Systems.* Real-Time Systems, 1992. — [DOI](https://doi.org/10.1007/BF00365312)
- **[Foundational]** Baruah, S.; Koren, G.; Mishra, B.; Raghunathan, A.; Rosier, L.; Shasha, D. *On-line Scheduling in the Presence of Overload.* FOCS, 1991. — [DOI](https://doi.org/10.1109/SFCS.1991.185354)
- **[SOTA]** Vestal, S. *Preemptive Scheduling of Multi-criticality Systems with Varying Degrees of Execution Time Assurance.* RTSS, 2007. — [DOI](https://doi.org/10.1109/RTSS.2007.47)
- **[Survey]** Ramamritham, K.; Son, S.; DiPippo, L. *Real-Time Databases and Data Services.* Real-Time Systems, 2004. — [DOI](https://doi.org/10.1023/B:TIME.0000045317.37980.a5)

## 10. Worked Example

Three periodic transactions on one processor, each accessing a shared item via a critical section:

| $T_i$ | $C_i$ | $P_i=d_i$ | critical section $\xi_i$ |
|-------|-------|-----------|--------------------------|
| $T_1$ (high) | 2 | 10 | 1 |
| $T_2$ (mid)  | 2 | 15 | 0 |
| $T_3$ (low)  | 3 | 30 | 2 |

Utilization $U = \tfrac{2}{10}+\tfrac{2}{15}+\tfrac{3}{30} = 0.2+0.133+0.1 = 0.433 \le 1$, so without conflicts EDF schedules it.

**Priority inversion risk:** if $T_3$ holds the lock and $T_1$ arrives, $T_1$ waits. Under the **Priority Ceiling Protocol**, $T_1$'s blocking is bounded by one lower-priority critical section: $B_1 = \max(\xi_3)=2$.

**Schedulability test** for $T_1$: $\sum_{d_j\le d_1}\tfrac{C_j}{P_j} + \tfrac{B_1}{P_1} = \tfrac{2}{10} + \tfrac{2}{10} = 0.4 \le 1$ ✓ — $T_1$ provably meets its deadline.

Drop PCP and allow chained inversion: $T_1$ could be blocked by *both* $\xi_3$ and an intervening $T_2$ run, pushing $B_1$ past the single-section bound and risking a miss. PCP's single-section cap is exactly what makes the bound provable on a uniprocessor; no comparable tight cap is known for MVCC commit pipelines.

---
*Part of the [DBMS Research catalog](../../README.md).*
