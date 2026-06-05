# Write-Skew Detection and Repair

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/write-skew-detection` · **Status:** partially-solved

## 1. Problem Statement

**Write skew** is the canonical anomaly that snapshot isolation (SI) admits but serializability forbids: two transactions read overlapping data, make disjoint writes, and each commit individually preserves an invariant that their *combination* violates (the textbook hospital on-call example: two doctors each go off duty, leaving zero on call). The problem is to **detect** (and then **prevent/repair**) write-skew anomalies — statically over transaction templates and dynamically over executing histories — while adding the *minimum* extra serialization (locks, promotions, or aborts).

Variants: **static decision** — given transaction programs, can a write-skew arise? **dynamic detection** — flag/abort at runtime exactly the executions that would produce non-serializable skew. **optimization/repair** — given a workload that admits skew, insert the minimum-cost set of conflict-materializing operations (e.g., promote a read to a write, add a `SELECT … FOR UPDATE`, or introduce a guard row) so that no SI execution is non-serializable. **counting** — how many distinct dangerous structures exist (relevant to abort-rate estimation).

## 2. Mathematical Foundations

Work in Adya's **multiversion serialization graph (MVSG)**. Nodes are committed transactions; edges are ww, wr, and **rw anti-dependencies** ($T_i \xrightarrow{rw} T_j$ when $T_i$ reads a version that $T_j$ later overwrites). The Fekete et al. theorem characterizes SI non-serializability precisely:

$$\text{An SI history is non-serializable} \iff \text{its MVSG has a cycle containing two consecutive } \xrightarrow{rw} \text{edges.}$$

The minimal witness is the **dangerous structure** $T_{\text{in}} \xrightarrow{rw} T_{\text{pivot}} \xrightarrow{rw} T_{\text{out}}$ with the pivot committing first; write skew is the special two-transaction case $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_1$. Predicate reads turn edge existence into a **satisfiability** question over read/write predicates (phantom anti-dependencies), which is where undecidability creeps in for unrestricted predicates.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Fekete, Liarokapis, O'Neil, O'Neil, Shasha (TODS 2005) — dangerous-structure theory and a static sufficient test; Jorwekar, Fekete, Ramamritham, Sudarshan (VLDB 2007) — automatic static detection of SI anomalies in real applications, including write skew. The transaction-template robustness line (Vandevoort, Ketsman, Koch, Neven, PVLDB 2021–2023) gives tight complexity for known-read/write-set programs.

**Systems-SOTA:** PostgreSQL **Serializable Snapshot Isolation (SSI)** (Cahill, Röhm, Fekete, SIGMOD 2008; Ports & Grittner, VLDB 2012) detects dangerous structures *dynamically* by tracking rw-conflict in/out flags and aborting the pivot. Wu et al. (PVLDB 2017) systematically evaluate MVCC designs including SSI-style certification.

## 4. Upper Bound

Dynamic SSI detection runs in $O(1)$ amortized per conflict edge: it does not materialize the full MVSG but uses the local *two-consecutive-rw* test, aborting whenever a transaction has both an incoming and an outgoing rw conflict to/from a concurrent pivot — a provably **sufficient** condition that may yield false aborts. Static detection over fixed templates with known read/write sets is **PTIME** (graph cycle search with the two-rw condition); robustness certification places several variants in P. Repair via greedy promotion gives a feasible (serializable) workload in polynomial time but without optimality.

## 5. Lower Bound

Exact dynamic detection (abort *only* genuine non-serializable executions, never falsely) is impossible online without unbounded lookahead — SSI's safe-but-conservative aborts are a consequence. For static analysis, once transaction programs gain control flow and parameters, robustness/skew-freedom is **coNP-hard** and up to **PSPACE-hard** (Vandevoort et al.); with arbitrary read **predicates** it is **undecidable** (reduction from predicate satisfiability / phantom reasoning). The minimum-cost **repair** (fewest promotions to kill all dangerous structures) is a hitting-set-style problem and is **NP-hard** in general.

## 6. The Gap

**Partially solved.** For fixed, known-read/write-set templates the detection question is closed (PTIME), and SSI is a deployed, sound dynamic enforcer. Open gaps: (i) closing the false-abort rate of online detection toward the true non-serializable set; (ii) decidability/complexity for predicate, insert, and delete semantics; (iii) provably minimum-cost repair, where only heuristics exist. The minimal-serialization-overhead objective has no matching upper/lower bound.

## 7. Current Research (as of June 2026)

The Hasselt/Antwerp group (Neven, Vandevoort, Ketsman) extends template robustness to predicates and inserts *(frontier — verify)*. There is renewed interest in **learned conflict prediction** to pre-emptively promote likely-skew reads, and in compiling static skew certificates into ORMs and query optimizers so applications get serializability for free where possible. Lower false-abort SSI variants and deterministic alternatives that sidestep skew entirely are actively compared.

## 8. Future Work

- Online detection with provably bounded false-abort rate approaching the exact non-serializable set.
- Complete the static decidability map for predicates, inserts, deletes, and control flow.
- Provably minimum-cost repair (promotion / guard-row insertion) algorithms.
- Optimizer/ORM-integrated, certified skew analysis emitting the cheapest serialization patches.

## 9. Key References

- **[Foundational]** Fekete, A.; Liarokapis, D.; O'Neil, E.; O'Neil, P.; Shasha, D. *Making Snapshot Isolation Serializable.* ACM TODS, 2005.
- **[Foundational]** Berenson, H.; Bernstein, P.; Gray, J.; Melton, J.; O'Neil, E.; O'Neil, P. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995.
- **[SOTA]** Jorwekar, S.; Fekete, A.; Ramamritham, K.; Sudarshan, S. *Automating the Detection of Snapshot Isolation Anomalies.* VLDB, 2007.
- **[SOTA]** Cahill, M.; Röhm, U.; Fekete, A. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008.
- **[SOTA]** Vandevoort, B.; Ketsman, B.; Koch, C.; Neven, F. *Robustness Against Read Committed for Transaction Templates.* PVLDB, 2021.
- **[Survey]** Adya, A. *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions.* PhD thesis, MIT, 1999.

---
*Part of the [DBMS Research catalog](../../README.md).*
