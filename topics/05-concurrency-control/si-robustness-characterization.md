---
id: 05-concurrency-control/si-robustness-characterization
title: "Robustness Against Snapshot Isolation Anomalies"
topic: 05-concurrency-control
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Robustness Against Snapshot Isolation Anomalies

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/si-robustness-characterization` · **Status:** partially-solved

## 1. Problem Statement

Snapshot Isolation (SI) reads from a transaction-consistent snapshot and uses first-committer-wins for write–write conflicts, but permits the **write-skew** and **read-only** anomalies, so SI executions need not be serializable. A workload (a set of transaction *programs*, not a single history) is **robust against SI** if *every* SI execution of it is serializable. The **decision problem**: given a workload specification (program skeletons / read–write templates), decide robustness against SI. Variants: robustness against weaker levels (Read Committed, Parallel SI), the **counting/optimization** variant of inserting the minimum number of conflict-materializing operations (promotions) to make a non-robust workload robust, and the *allocation* problem — assign each transaction the cheapest isolation level preserving global serializability.

## 2. Mathematical Foundations

The key object is the **static dependency graph** over transaction templates with three edge types: ww (write–write), wr (write–read), and rw (anti-dependency). Adya's formalism and the Fekete et al. theory show:

$$\text{Every SI execution is serializable} \iff \text{no cycle has two consecutive } \xrightarrow{rw} \text{ anti-dependency edges.}$$

A cycle witnessing non-serializability under SI is a **dangerous structure**: $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_3$ where $T_3$ may equal $T_1$ and the pivot $T_2$ commits first. Robustness checking reduces to detecting such structures in the static graph; with predicate reads this requires reasoning about read/write *predicates* and potential phantoms, making edge existence a satisfiability question.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Fekete, Liarokapis, O'Neil, O'Neil, Shasha (TODS 2005) gave the dangerous-structure characterization and a sufficient static test. Cerone, Bernardi, Gotsman (CONCUR 2015) recast robustness for SI and Parallel SI in an axiomatic framework. Vandevoort, Ketsman, Koch, Neven (PODS 2021–2023) established **decidability and complexity** of robustness for restricted (read-/write-set-known) workloads and built tighter graph criteria. **Systems-SOTA:** PostgreSQL's **Serializable Snapshot Isolation (SSI)** (Cahill, Röhm, Fekete, SIGMOD 2008; Ports & Grittner, VLDB 2012) enforces serializability dynamically by aborting pivots, rather than statically certifying robustness.

## 4. Upper Bound

For workloads with statically known read/write sets, robustness against SI is decidable; Vandevoort et al. place precise variants in **PTIME** (counting-free, transaction-level graph constructions) and identify **coNP** / **PSPACE** complexity for richer template languages with parameters and control flow. SSI gives an *online* upper bound: per-transaction overhead $O(\text{conflicts})$ with bounded false-abort rate. Allocation-to-min-level admits polynomial heuristics with provable serializability but not provable cost-optimality.

## 5. Lower Bound

When transaction programs include conditional control flow or unbounded loops, deciding robustness becomes **coNP-hard** and, for some template languages, **PSPACE-hard** (Vandevoort et al.) — the lower bounds come from encoding emptiness/cycle problems over the program graph. With predicate reads, robustness is at least as hard as predicate satisfiability, hence undecidable for unrestricted predicates. No nontrivial fine-grained lower bound is known for the PTIME-decidable fragments.

## 6. The Gap

The problem is **partially solved**: tight criteria and complexity exist for *fixed, known-read/write-set* templates (closed), but the gap remains open for (i) workloads with rich control flow and parameterized predicates, where decidability boundaries are not fully mapped; (ii) **multi-version / MVCC variants beyond standard SI** (e.g., RC, Parallel SI on real engines) where the dangerous-structure analogue is incompletely characterized; (iii) the optimization variant — minimum-cost promotion/allocation is not known to be polynomial.

## 7. Current Research (as of June 2026)

The Hasselt/Antwerp group (Neven, Vandevoort, Ketsman) continues to push robustness across isolation levels and toward *insert/delete and predicate* semantics *(frontier — verify)*. Cerone and Gotsman's axiomatic consistency line feeds robustness for replicated and transactional-causal systems. There is growing interest in **automatic level allocation** in cloud OLTP (e.g., serverless databases) and in compiling robustness certificates into the query optimizer.

## 8. Future Work

- Complete the decidability/complexity map for templates with predicates, inserts, and deletes.
- Tight robustness criteria for Parallel SI, RC, and causal+ consistency on replicated stores.
- Provably minimum-cost promotion (conflict materialization) and isolation-level allocation.
- Certified, optimizer-integrated static robustness analysis for production engines.

## 9. Key References

- **[Foundational]** Berenson, H.; Bernstein, P.; Gray, J.; Melton, J.; O'Neil, E.; O'Neil, P. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995. — [DOI](https://doi.org/10.1145/223784.223785)
- **[Foundational]** Fekete, A.; Liarokapis, D.; O'Neil, E.; O'Neil, P.; Shasha, D. *Making Snapshot Isolation Serializable.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1071610.1071615)
- **[SOTA]** Cahill, M.; Röhm, U.; Fekete, A. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376690)
- **[SOTA]** Cerone, A.; Bernardi, G.; Gotsman, A. *A Framework for Transactional Consistency Models with Atomic Visibility.* CONCUR, 2015. — [DOI](https://doi.org/10.4230/LIPIcs.CONCUR.2015.58)
- **[SOTA]** Vandevoort, B.; Ketsman, B.; Koch, C.; Neven, F. *Robustness Against Read Committed for Transaction Templates.* PVLDB, 2021. — [arXiv](https://arxiv.org/abs/2107.12239)
- **[Survey]** Adya, A. *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions.* PhD thesis, MIT, 1999. — [MIT](https://pmg.csail.mit.edu/papers/adya-phd.pdf)

## 10. Worked Example

Workload of two transaction templates over a table `Doctors(id, oncall)` with invariant *"at least one doctor on call."* Initially $d_1.\text{oncall}=d_2.\text{oncall}=\text{true}$.

- $P_1$: read both rows (check $\ge 1$ on call), set $d_1.\text{oncall}=\text{false}$.
- $P_2$: read both rows, set $d_2.\text{oncall}=\text{false}$.

Build the static dependency graph. $P_1$ reads $d_2$, which $P_2$ writes: edge $P_1 \xrightarrow{rw} P_2$. Symmetrically $P_2$ reads $d_1$, which $P_1$ writes: $P_2 \xrightarrow{rw} P_1$. This is a 2-cycle with **two consecutive $rw$ edges** — a dangerous structure.

By the Fekete characterization, the workload is **not robust against SI**: an SI execution where both run on the same snapshot commits both (first-committer-wins sees no $ww$ conflict, since writes are disjoint), violating the invariant. Minimal repair: promote one read to a write (e.g. `SELECT … FOR UPDATE`), materializing a $ww$ edge that breaks the dangerous double-$rw$ cycle, restoring robustness.

---
*Part of the [DBMS Research catalog](../../README.md).*
