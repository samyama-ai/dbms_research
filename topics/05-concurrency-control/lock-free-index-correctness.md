---
id: 05-concurrency-control/lock-free-index-correctness
title: "Lock-Free Index Concurrency Correctness"
topic: 05-concurrency-control
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Lock-Free Index Concurrency Correctness

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/lock-free-index-correctness` · **Status:** partially-solved

## 1. Problem Statement

Modern in-memory databases use **lock-free or latch-light** index structures — Bw-Tree (delta-chained B-tree), Masstree, ART, and concurrent skip lists — to scale point/range access on many cores. The research problem is to **prove that these indexes are linearizable** (each operation appears to take effect atomically at a single instant between its invocation and response) and, crucially, that this linearizability **composes correctly with transactional isolation**: an index used inside a serializable/SI transaction must not introduce *phantoms*, lost structural updates, or read-anomalies through its internal concurrency.

Variants:
- **Standalone correctness:** prove a given lock-free index is linearizable (and lock-free/wait-free as claimed).
- **Composition correctness:** prove the index's linearization points are compatible with the surrounding concurrency-control protocol (no phantom reads under range scans; predicate locking or index-versioning correctness).
- **Memory-reclamation safety:** prove safe reclamation (epoch/hazard pointers/RCU) preserves linearizability without use-after-free.

Status **partially-solved**: individual structures have hand proofs and several machine-checked proofs exist, but a *general, composable* framework spanning index + isolation + reclamation is incomplete.

## 2. Mathematical Foundations

**Linearizability** (Herlihy & Wing 1990): a concurrent history $H$ is linearizable iff it is equivalent to some legal sequential history $S$ that respects $H$'s real-time order ($op_1 \prec_H op_2 \Rightarrow op_1 \prec_S op_2$). Each operation has a **linearization point** within its execution interval. Lock-free progress: some operation always completes in a finite number of steps system-wide; **wait-freedom** strengthens this per-operation.

Index correctness rests on showing every interleaving is linearizable, typically via single-CAS linearization points or via *helping*. For B-tree variants, structural modifications (splits, merges, **SMOs**) must be made atomic or appear so; the Bw-Tree uses **delta records** appended by CAS to a mapping table, so a node's logical state is "base + delta chain," and the linearization point is the successful CAS installing a delta.

Composition with isolation requires the index's logical contents to match a *serializable schedule of the transactions*. **Phantoms** arise when a range predicate's truth changes between reads; preventing them needs **predicate/next-key locking** (the classic ARIES/KVL of Mohan) or **index-level versioning**. Formal tools: **linearizability via refinement** (forward/backward simulation), **separation logic** (concurrent / RGSep / Iris) for machine-checked proofs, and **observational refinement** to connect linearizability to contextual program correctness (Filipović, O'Hearn, Rinetzky, Yang 2010).

## 3. State of the Art (SOTA)

**Systems-SOTA.** **Bw-Tree** (Levandoski, Lomet, Sengupta, ICDE 2013; in SQL Server Hekaton/Azure), **Masstree** (Mao, Kohler, Morris, EuroSys 2012), **ART / adaptive radix tree** (Leis, Kemper, Neumann, ICDE 2013) with optimistic lock coupling (OLC) and **ROWEX**, and lock-free skip lists (Fraser; Herlihy-Lev-Shavit) define practice. The **OpenBw-Tree** reimplementation (Wang et al., SIGMOD 2018) documented subtle correctness/performance pitfalls in the original. Memory reclamation: **epoch-based reclamation** (Fraser), **hazard pointers** (Michael 2004), and RCU (McKenney).

**Theory-SOTA.** Machine-checked linearizability proofs exist for concurrent skip lists and Michael-Scott queues (in CIVL, Iris, FCSL). General B-link tree correctness traces to Lehman & Yao (1981) and Sagiv. Composable proofs of index + transaction isolation remain mostly hand-written.

## 4. Upper Bound

Lock-free indexes achieve $O(\log n)$ expected work per operation (skip list / balanced tree height) with linearizable semantics, and **lock-free progress** guarantees (Bw-Tree, Harris-Michael lists). Optimistic lock coupling (ART-OLC) gives near-lock-free read scaling with $O(1)$ amortized validation. On the verification side, **automated linearizability checking** is decidable for fixed linearization points and bounded thread counts; tools (Line-Up, CIVL, Iris-based proofs) verify specific structures. The achievable result: per-structure, machine-checked linearizability + lock-freedom is attainable in the **asynchronous shared-memory model with CAS**.

## 5. Lower Bound

Fundamental limits constrain lock-free indexes: **(1)** wait-free implementations of many objects require $\Omega(\cdot)$ overhead, and consensus number theory (Herlihy 1991) shows CAS is universal but read/write alone cannot implement lock-free updates — a hardware-primitive lower bound. **(2)** Verifying linearizability of a concurrent implementation against an atomic spec is **EXPSPACE-complete** in general and undecidable for unbounded threads (Bouajjani, Emmi, Enea, Hamza 2013) — a hard limit on full automation. **(3)** Disjoint-access-parallelism impossibility (Israeli-Rappoport; Attiya et al.) bounds how lock-free range operations can avoid contention. **(4)** Phantom prevention provably requires predicate-level synchronization; pure key-value linearizability is insufficient for serializable range queries.

## 6. The Gap

**Partially closed.** Standalone linearizability of the major structures is established (hand proofs widely; machine-checked for several). The genuine open gap is **composability**: a *general, mechanized* theory proving that (lock-free index) ∘ (memory reclamation) ∘ (transactional isolation protocol) is correct end-to-end, including phantom-freedom for range scans and use-after-free safety under EBR/hazard pointers. Today each combination is re-verified ad hoc; subtle bugs (e.g., OpenBw-Tree findings) show the gap is real. Closing it requires a modular refinement/separation-logic framework where index linearizability plugs into an isolation-level specification as a verified component.

## 7. Current Research (as of June 2026)

Directions: (i) **mechanized concurrent-index proofs in Iris/separation logic**, extending to reclamation safety *(frontier — verify)*; (ii) verified OLC/ROWEX templates so new index variants inherit correctness; (iii) composable specs linking index linearizability to SI/serializability (phantom-free range scans); (iv) persistent-memory lock-free indexes whose crash-consistency + linearizability must be jointly proven (e.g., PM-aware Bw-Tree/ART variants). Groups: TU Munich (Leis, Neumann — ART/OLC), MIT/Harvard (Kohler, Morris — Masstree), Microsoft Research (Lomet, Levandoski — Bw-Tree), and verification groups (MPI-SWS Iris; Enea/Bouajjani on concurrent-object verification). Persistent-memory and disaggregated-memory indexes are the active correctness frontier.

## 8. Future Work

- A modular, machine-checked framework composing index linearizability with isolation-level specs and reclamation safety.
- Verified, reusable concurrency *templates* (OLC, ROWEX, delta-chaining) that transfer proofs to new structures.
- Provably phantom-free lock-free range scans integrated with SSI/serializable certification.
- Crash-consistent + linearizable correctness for persistent-memory and disaggregated-memory indexes.

## 9. Key References

- **[Foundational]** M. P. Herlihy, J. M. Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** P. L. Lehman, S. B. Yao. *Efficient Locking for Concurrent Operations on B-Trees.* ACM TODS, 1981. — [DOI](https://doi.org/10.1145/319628.319663)
- **[SOTA]** J. Levandoski, D. Lomet, S. Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)
- **[SOTA]** V. Leis, A. Kemper, T. Neumann. *The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544812)
- **[SOTA]** Y. Mao, E. Kohler, R. T. Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012. — [DOI](https://doi.org/10.1145/2168836.2168855)
- **[Foundational]** A. Bouajjani, M. Emmi, C. Enea, J. Hamza. *Verifying Concurrent Programs against Sequential Specifications.* ESOP, 2013. — [DOI](https://doi.org/10.1007/978-3-642-37036-6_17)
- **[Foundational]** M. Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)

## 10. Worked Example

Consider a Bw-Tree leaf with base page $P=\{10,20,30\}$ and mapping-table slot $M[P]$. Two threads race:

- $T_1$: insert 15. Builds delta $d_1=\langle\text{ins }15\rangle$ pointing at $P$, then $\mathrm{CAS}(M[P]: P \to d_1)$.
- $T_2$: insert 25. Builds delta $d_2=\langle\text{ins }25\rangle$ also pointing at $P$, then $\mathrm{CAS}(M[P]: P \to d_2)$.

Both CAS expect the old value $P$; hardware serializes them, say $T_1$ wins. The slot now reads $d_1\!\to\!P$. $T_2$'s CAS expected $P$ but sees $d_1$, so it **fails**, re-reads $M[P]=d_1$, rebuilds $d_2'=\langle\text{ins }25\rangle\!\to\!d_1$, and retries $\mathrm{CAS}(M[P]: d_1 \to d_2')$, which succeeds.

Logical state: $d_2'\!\to\!d_1\!\to\!P = \{10,15,20,25,30\}$. The two successful CAS instants are the **linearization points**; no update is lost. A scan reading $M[P]=d_1$ before $T_2$ retries sees a consistent prefix $\{10,15,20,30\}$ — linearizable, with $O(\text{chain length})$ read cost until consolidation.

---
*Part of the [DBMS Research catalog](../../README.md).*
