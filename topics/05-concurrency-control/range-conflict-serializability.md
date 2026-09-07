---
id: 05-concurrency-control/range-conflict-serializability
title: "Range-Conflict Serializability Theory"
topic: 05-concurrency-control
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Range-Conflict Serializability Theory

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/range-conflict-serializability` · **Status:** open

## 1. Problem Statement
Classical serializability theory models operations as reads/writes on **individual data items**. Real transactions issue **predicate** and **range** operations — `SELECT ... WHERE age BETWEEN 20 AND 30`, range scans, index probes — which can conflict with **inserts/deletes of items that do not yet exist** (the *phantom problem*). The problem: extend conflict-serializability theory to **predicate/range reads and writes**, giving (1) a correct conflict relation that captures phantoms, and (2) tight complexity for **recognizing** whether a schedule of predicate operations is serializable.

Variants:
- *Recognition (decision):* given a history with predicate/range operations and their semantics, is it conflict-serializable?
- *Acceptance/scheduling:* design a protocol (locking or validation) admitting exactly the serializable predicate schedules, maximizing concurrency.
- *Complexity-of-conflict:* deciding whether two predicate operations conflict (a predicate $P$ read vs. a write changing whether some tuple satisfies $P$) — itself a **satisfiability** question over the predicate language.

The core difficulty: a predicate read conflicts with a write iff the write changes the *set of tuples satisfying the predicate*; deciding that is as hard as the satisfiability of the predicate logic, so conflict-detection complexity is tied to the predicate fragment.

## 2. Mathematical Foundations
- **Predicate locks** (Eswaran, Gray, Lorie, Traiger, *The Notions of Consistency and Predicate Locks in a Database System*, CACM 1976): the foundational model. Two predicate operations on predicates $P, Q$ with at least one a write conflict iff $\exists$ a possible tuple $t$ (over the schema) with $P(t) \wedge Q(t)$ — i.e., conjunction satisfiability. **Deciding predicate-lock conflict is the satisfiability of $P \wedge Q$**, which is NP-hard / undecidable depending on the predicate language (e.g., NP-hard for general boolean arithmetic predicates).
- **Phantom problem & multigranularity:** practical systems approximate predicate locks with **index-range / next-key locking** and **multigranularity locks** (Gray), trading precision for cheap conflict tests.
- **Serializability graph:** extend the conflict graph with predicate-write anti-dependencies; serializability $\Leftrightarrow$ acyclicity still holds, but **building the edges** requires the (hard) conflict test.
- **Formal frameworks:** Adya's generalized isolation with **predicate-based dependencies** (predicate-read/write G-edges) gives the cleanest semantic definition; SSI (Cahill–Röhm–Fekete) handles predicate anti-dependencies via index-range rw-conflict tracking.
- Relevant complexity tools: NP-completeness of serializability recognition (Papadimitriou 1979) carries over and *increases* once conflict edges themselves require satisfiability tests.

## 3. State of the Art (SOTA)
**Theory-SOTA.** EGLT predicate-lock theory (1976) gives the semantically exact conflict relation; Adya's predicate-dependency formalization (ICDE 2000) is the modern semantic reference. Recognition complexity inherits Papadimitriou's NP-completeness for the graph and adds the predicate-conflict satisfiability layer — the exact tight bound for natural fragments (conjunctive range predicates, with/without arithmetic) is **not fully settled**.

**Systems-SOTA.** No system implements exact predicate locks (too expensive). Instead:
- **Next-key / index-range locking** (System R, ARIES/KVL, InnoDB, SQL Server) prevents phantoms conservatively over the index structure.
- **Serializable Snapshot Isolation (SSI)** (Cahill–Röhm–Fekete, SIGMOD 2008; PostgreSQL SSI, VLDB 2012) detects rw-anti-dependencies including range conflicts via *SIREAD* locks on index ranges — sound and reasonably precise, the de-facto modern answer.
- Precision-locking and granular locking remain textbook but unused at scale.

## 4. Upper Bound
- **Recognition:** given pre-computed conflict edges, conflict-serializability is decidable in polynomial time (cycle detection $O(V+E)$); the *expensive* part is edge computation. For **conjunctive range predicates** over ordered attributes, the conflict test (does a written tuple fall in a queried range?) is polynomial — so for that fragment, full recognition is in **P** (modulo edge construction). For general boolean/arithmetic predicates, conflict testing is in **NP** (guess a witnessing tuple), so recognition is in NP overall.
- **Protocols:** index-range locking gives serializable phantom-free schedules with per-operation cost $O(\log N)$ (B-tree key locking); SSI adds $O(|\text{read set ranges}|)$ tracking. These hold in the **B-tree / index-structure model**.

## 5. Lower Bound
- **Conflict-test hardness:** deciding whether two predicates conflict is **NP-hard** for boolean combinations of arithmetic constraints (reduction from SAT / integer feasibility), and **undecidable** if predicates may use unrestricted first-order arithmetic — so an *exact* general predicate-lock scheduler cannot run in polynomial time, and no algorithm exists in the unrestricted case.
- **Recognition lower bound:** serializability recognition is **NP-complete** even for plain read/write histories (Papadimitriou 1979); the predicate setting is at least as hard and strictly harder once conflict edges require satisfiability.
- **Phantom impossibility:** any concurrency-control method using only item-granularity locks **cannot** guarantee serializability in the presence of inserts/deletes (the phantom theorem, EGLT) — a structural impossibility forcing predicate- or index-range-level reasoning.

## 6. The Gap
Two gaps: (1) **theory gap** — a tight characterization of recognition/scheduling complexity as a function of the predicate fragment (conjunctive ranges vs. disjunctive vs. arithmetic vs. with joins) is incomplete; we know endpoints (P for simple ranges, NP-hard/undecidable for rich predicates) but lack a sharp dichotomy. (2) **theory-vs-systems gap** — exact predicate locking is semantically right but intractable; deployed index-range/SSI methods are tractable but **conservatively over-conflict** (false aborts) or are tied to a specific index. Closing it means a *dichotomy theorem* over predicate fragments plus protocols whose imprecision is provably bounded. Genuinely open.

## 7. Current Research (as of June 2026)
- Tighter range-conflict tracking in MVCC/SSI engines (PostgreSQL, CockroachDB, Umbra) reducing false positives on range anti-dependencies. *(frontier — verify)*
- Fine-grained complexity classification of predicate-conflict testing for SQL-relevant fragments (conjunctive queries, range + equality), connecting to CSP/SAT dichotomy results. *(frontier — verify)*
- Groups: Fekete/Röhm (Sydney) on SSI and range conflicts; Neumann/Kemper (TUM, Umbra) on precise predicate locking; Adya-lineage isolation theory.

## 8. Future Work
- A serializability-recognition **dichotomy theorem** parameterized by predicate language.
- Provably bounded-imprecision predicate-locking protocols (quantified false-conflict rate).
- Extension to predicate operations involving **joins** and aggregates, where conflict semantics are largely unformalized.

## 9. Key References
- **[Foundational]** K. P. Eswaran, J. N. Gray, R. A. Lorie, I. L. Traiger. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[Foundational]** C. H. Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** A. Adya, B. Liskov, P. O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000. — [DBLP](https://dblp.uni-trier.de/rec/conf/icde/AdyaLO00.html)
- **[SOTA]** M. J. Cahill, U. Röhm, A. D. Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008. — [ACM](https://dl.acm.org/doi/10.1145/1376616.1376690)
- **[SOTA]** D. R. K. Ports, K. Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1208.4179)
- **[Survey]** P. A. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)

## 10. Worked Example

Consider attribute domain $\text{age} \in \{1,\dots,100\}$ and two predicate operations:

- $T_1$ reads predicate $P:\ 20 \le \text{age} \le 30$.
- $T_2$ writes (inserts) a tuple $t$ with $\text{age}=25$.

**Conflict test (conjunctive ranges).** Do they conflict? Decide $\exists t:\ P(t)\wedge (t.\text{age}=25)$, i.e. $20 \le 25 \le 30$ — true. So there is a predicate anti-dependency edge $T_1 \xrightarrow{rw} T_2$. This test is a single interval-membership check: $O(1)$, hence **polynomial** for the range fragment, and recognition reduces to cycle detection in $O(V+E)$.

**Now make it arithmetic.** Let $P:\ (\text{age} \bmod 7 = 0)\wedge(\text{age} \text{ prime})$ and $T_2$ insert $\text{age}=x$. Deciding conflict means deciding satisfiability of a boolean-arithmetic predicate — no longer an interval lookup; in general it is **NP-hard** (guess a witnessing tuple, verify in P, so the test sits in NP).

The two cases — same schedule shape, conflict-test cost flipping from $O(1)$ to NP-hard purely by predicate language — are exactly why a fragment-parameterized dichotomy theorem is the open target.

---
*Part of the [DBMS Research catalog](../../README.md).*
