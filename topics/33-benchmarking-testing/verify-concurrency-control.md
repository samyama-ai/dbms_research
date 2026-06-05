# Formal Verification of Concurrency Control

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/verify-concurrency-control` · **Status:** partially-solved

## 1. Problem Statement
Given an *implementation* of a concurrency-control (CC) protocol — strict two-phase locking (S2PL), multiversion CC (MVCC), snapshot isolation (SI), serializable snapshot isolation (SSI), optimistic CC (OCC), or a distributed variant (Percolator, Calvin, deterministic CC) — **mechanically verify** that *every* execution it admits, over *all* interleavings of an arbitrary set of transactions, satisfies its claimed **isolation level** $I$ (e.g., serializability, snapshot isolation, read-committed).

Variants:
- **Implementation verification (the target):** prove the *code/operational model* of the protocol guarantees $I$ for all schedules — a $\forall$-interleavings safety property.
- **Protocol/spec verification:** prove the *abstract algorithm* (e.g., in TLA+) refines $I$, decoupled from the code.
- **Model checking (bounded):** exhaustively check $I$ over all interleavings up to $k$ transactions / $n$ operations (refutation-complete, not a full proof).

The claim is a *universal* property over a combinatorial explosion of schedules, which is what makes manual reasoning unreliable and mechanization valuable.

## 2. Mathematical Foundations
The classical framework is **serializability theory** (Bernstein–Hadzilacos–Goodman 1987): a schedule is **conflict-serializable** iff its **conflict (serialization) graph** $\mathrm{SG}(s)$ — nodes = transactions, edges = conflicting operation orderings — is **acyclic**. Isolation levels are characterized by which **dependency edges** (ww, wr, rw "anti-dependencies") may appear in cycles, formalized by **Adya's** generalized dependency graphs (DSG) and the phenomena $G0/G1/G2$ (Adya–Liskov–O'Neil, ICDE 2000). Snapshot isolation is characterized by the *Start-Dependency/SI* graph and the **write-skew** anomaly; **SSG** analysis (Fekete et al., TODS 2005) shows SI failures correspond to specific rw-edge "dangerous structures," the basis of SSI.

Mechanized proofs cast the protocol as a **state machine / labeled transition system** and the isolation level as an **invariant** or a **refinement** of an atomic specification. Tools rely on **TLA+/Apalache** model checking, **Coq/Isabelle** invariant proofs, or **separation-logic / Iris**-style concurrent program logics to discharge the $\forall$-interleavings obligation, often via an inductive invariant on the dependency graph's acyclicity.

## 3. State of the Art (SOTA)
- **Spec-level mechanization:** **TLA+** specifications of SI, MVCC, and distributed CC are mainstream; e.g., MongoDB and others publish TLA+ models of their replication/transaction protocols, model-checked with TLC/Apalache.
- **Theory-grounded mechanization:** Fekete–O'Neil–Shasha's SI/SSI theory (TODS 2005) underpins **PostgreSQL's SSI** (Ports–Grittner, VLDB 2012) — a verified-by-construction design, with the protocol's safety argued from dependency-graph theorems.
- **Proof-assistant verification:** mechanized proofs of 2PL/serializability and of transactional-memory/STM correctness exist in Coq/Isabelle (e.g., verified STM and the **CertiKOS/Iris** lineage for concurrent objects). **Verdi/IronFleet** (SOSP 2015) mechanically verify distributed protocols, providing methodology reused for distributed CC.
- **Bounded checking:** **Elle/Jepsen** check observed histories (see the conformance problem); **MonkeyDB** and CC model checkers explore interleavings under weak isolation.
- Individual protocols *have* been verified at spec level and key designs proven from theory — hence **partially-solved**; full *implementation*-level mechanized proofs for production engines are not complete.

## 4. Upper Bound
At spec level, bounded model checking of an isolation invariant is decidable and automatic for fixed $k$ transactions / $n$ operations (exponential in $k,n$ but routinely run with TLC/Apalache). Acyclicity of the dependency graph is checkable in $O(V+E)$ per schedule. Refinement proofs in TLA+/Iris give *unbounded* (all-interleavings) guarantees once an inductive invariant is found; the SSI dependency-structure theorem yields a provably-correct serializable protocol with $O(1)$-per-conflict bookkeeping.

## 5. Lower Bound
Verifying weak-isolation properties is hard in general. **Testing/deciding serializability of a given history is NP-complete** (Papadimitriou, JACM 1979) — the conflict-graph criterion is the polynomial *sufficient* relaxation. For *parameterized* verification (all numbers of transactions/threads), the problem is **undecidable** in general (parameterized concurrent verification reduces from reachability of unbounded systems), so unbounded implementation proofs require non-automatable invariant discovery. Distributed CC additionally meets **CAP/FLP** style impossibilities for liveness under partitions/asynchrony, bounding what *availability* can be guaranteed alongside the safety property.

## 6. The Gap
Spec-level verification (TLA+) and theory-grounded designs (SSI) are mature, but there is a real gap to **machine-checked correctness of the actual deployed code** (millions of lines, optimized latching, version-chain management) for production isolation levels. Bounded model checking refutes bugs but cannot *prove* all-interleaving safety; unbounded proofs are blocked by undecidability of parameterized verification, demanding hand-crafted inductive invariants. Closing it means scalable refinement proofs from optimized implementations to the abstract isolation spec, or sound abstractions that make the parameterized problem decidable for real protocols.

## 7. Current Research (as of June 2026)
Directions: (1) Iris/separation-logic mechanized proofs of MVCC/SI implementations and transactional libraries *(frontier — verify)*; (2) automated reductions that make parameterized weak-isolation verification decidable via *small-model* theorems (bounding the number of transactions needed to expose any anomaly) *(frontier — verify)*; (3) coupling Elle-style history checking with model checkers (MonkeyDB) to verify *clients* against weak isolation; (4) TLA+/Apalache models of deterministic and distributed CC (Calvin/Percolator-style). Groups: the Jepsen/Elle effort (Kingsbury), Enea/Bouajjani et al. (weak-isolation decidability), the Iris/concurrency-logic community, and TLA+-based verification at MongoDB/CockroachLabs.

## 8. Future Work
- Mechanized refinement proofs from *optimized* MVCC/SI implementations to abstract isolation specs.
- Small-model / cut-off theorems making parameterized isolation verification decidable for real protocols.
- Verified distributed CC (Calvin/Percolator) combining safety proofs with explicit CAP/FLP liveness boundaries.
- Reusable, certified libraries of dependency-graph invariants usable across engines.

## 9. Key References
- **[Foundational]** Bernstein, Hadzilacos, Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979.
- **[Foundational]** Adya, Liskov, O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000.
- **[Foundational]** Fekete, Liarokapis, O'Neil, O'Neil, Shasha. *Making Snapshot Isolation Serializable.* ACM TODS, 2005.
- **[SOTA]** Ports, Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012.
- **[SOTA]** Hawblitzel, Howell, et al. *IronFleet: Proving Practical Distributed Systems Correct.* SOSP, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
