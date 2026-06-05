# Property-Based Testing of Transaction APIs

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/property-based-transaction-testing` · **Status:** partially-solved
> **Verification note:** In §2 the "two consecutive rw edges (dangerous structure)" condition is the criterion for an SI execution to be *non*-serializable, not a definition of SI itself (SI = snapshot reads + first-committer-wins); read it as the SI-serializability characterization of Fekete et al.

## 1. Problem Statement

Transactional systems promise **isolation** and **consistency** guarantees (serializability, snapshot isolation, causal consistency, linearizability of key-value ops). Property-based testing (PBT) checks such guarantees by *generating* concurrent client programs, executing them against the SUT, recording an observed **history**, and checking it against a **consistency property** — without a handwritten expected output.

Variants:
- **History-checking (decision) variant:** given a recorded history $H$, decide whether it is admissible under isolation level $L$ (e.g., is $H$ serializable / snapshot-isolated / linearizable?).
- **Generation/exploration variant:** design generators and schedulers that produce *meaningful* concurrent histories — covering anomaly-prone interleavings — rather than uniformly random ones.
- **Counting/coverage variant:** quantify how much of the interleaving space (or the anomaly catalog) a test campaign exercises.

## 2. Mathematical Foundations

A history $H$ is a set of operations with a partial **program order** (per session) and a **read-from** relation $\mathsf{wr}$ (which write each read observes). Isolation levels are defined axiomatically (Cerone–Bernardi–Gotsman, Biswas–Enea) by *dependency relations* $\mathsf{wr}, \mathsf{ww}, \mathsf{rw}$ and the requirement that a derived relation be **acyclic**. **Serializability** $\Leftrightarrow$ the *conflict graph* (Bernstein–Hadzilacos–Goodman) is acyclic; **Snapshot Isolation** $\Leftrightarrow$ no cycle with two consecutive $\mathsf{rw}$ anti-dependency edges (the **dangerous structure** of Fekete et al.). **Linearizability** (Herlihy–Wing) requires a total order consistent with real-time precedence and the sequential spec.

Checking serializability of an *arbitrary* history is **NP-complete** (the classic VSR/CSR result of Papadimitriou). Restricting to **conflict-serializability** makes it polynomial (cycle detection). Biswas–Enea show that for histories where each session is sequential and the read-from is recorded, checking several isolation levels is **polynomial** by reasoning over the dependency axioms — the key enabler for modern checkers. Generation quality can be framed as covering the **anomaly lattice** (dirty read, lost update, write skew, …); maximizing distinct anomalies covered is a submodular objective ⇒ greedy $(1-1/e)$.

## 3. State of the Art (SOTA)

- **Jepsen / Elle** (Kyle Kingsbury): the de-facto systems-SOTA. Elle (VLDB 2020) *infers* dependency edges from list/register values and detects cycles, producing minimal witnesses of isolation violations; Jepsen drives fault injection (partitions, clock skew).
- **Theoretical checkers:** **Biswas & Enea** (OOPSLA 2019) — polynomial-time checking of read-atomic/causal/SI/serializability under recorded read-from. **Cobra** (Tan, Alagappan et al., OSDI 2020) — verifying serializability of black-box databases using SMT + GPU-accelerated pruning.
- **PBT frameworks:** QuickCheck/Hypothesis with stateful/model-based extensions; **Quviq QuickCheck** has industrial use for distributed databases. **MonkeyDB** (Biswas et al., OOPSLA 2021) is a mock KV store with *configurable weak isolation* for testing applications against weak guarantees.

## 4. Upper Bound

Conflict-serializability checking is $O(|H| + E)$ (graph cycle detection). With recorded read-from, **causal consistency** and **read-atomicity** are polynomial; SI and serializability are polynomial *under bounded session/communication width* but the general black-box serializability problem (read-from unknown) is verified by Cobra in worst-case exponential SMT but practically fast via polynomial-time pruning. Linearizability checking is decidable; with bounded concurrency, $O(n!)$ in the worst case but tractable with Wing–Gong / partial-order reduction. Generation exploration uses **partial-order reduction (DPOR)** to enumerate only Mazurkiewicz-equivalence-class representatives, an exponential-to-polynomial-per-class saving.

## 5. Lower Bound

- **View-serializability and general serializability** of a history are **NP-complete** (Papadimitriou, JACM 1979).
- **Black-box serializability checking** (read-from not observed) is **NP-complete** (Cobra paper; reduction from the same).
- **Linearizability checking** of a single history against an arbitrary object spec is **NP-complete** (Gibbons–Korach, SICOMP 1997); for unbounded concurrency the verification problem is harder still.
- **FLP impossibility** (Fischer–Lynch–Paterson, JACM 1985) and **CAP** (Gilbert–Lynch) bound what guarantees a system can *offer* under asynchrony/partition, shaping which properties are even testable on a partitioned SUT.

## 6. The Gap

Partially solved. For histories with **recorded read-from**, polynomial checkers (Biswas–Enea, Elle) close the gap for causal/RA/SI and give witnesses. The remaining gaps: (1) **black-box** serializability is NP-complete and Cobra's tractability is empirical, not guaranteed; (2) **generation** has no theory of "interleaving coverage" that provably correlates with anomaly-finding power — DPOR reduces redundancy but the space is still exponential; (3) checking **mixed/heterogeneous** isolation (some txns SI, some serializable) lacks complete polynomial algorithms. Bridging needs both better recorded-metadata instrumentation and coverage-guided schedulers with formal guarantees.

## 7. Current Research (as of June 2026)

- Coverage-guided concurrency testing for databases combining DPOR with feedback (Elle-style witnesses driving the next schedule) *(frontier — verify)*.
- Extending polynomial isolation checkers to **transactional causal consistency** and **mixed isolation**, and to **predicate reads/range queries** (Enea group, IMDEA/Gotsman lineage) *(frontier — verify)*.
- Cobra-style SMT verification scaled with incremental/online checking for long-running production traces.
- MonkeyDB-style configurable mock stores to test *application-level* invariants under weak isolation (note: such mocks are testing scaffolds, not production substitutes).

## 8. Future Work

- A principled, falsifiable notion of interleaving/anomaly coverage with sample-complexity bounds.
- Sound, complete polynomial checkers for SI/serializability without recorded read-from, or proof of impossibility.
- PBT generators that target *specific* anomalies (write skew) by construction from the isolation axioms.
- Integration of fault injection (Jepsen) with property generators in one coverage-driven loop.

## 9. Key References

- **[Foundational]** C. H. Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** M. Herlihy, J. Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[SOTA]** R. Biswas, C. Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360591)
- **[SOTA]** K. Kingsbury, P. Alvaro. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3430915.3430918)
- **[SOTA]** C. Tan, C. Zhao, S. Mu, M. Walfish. *Cobra: Making Transactional Key-Value Stores Verifiably Serializable.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/tan)
- **[Foundational]** A. Fekete, D. Liarokapis, E. O'Neil, P. O'Neil, D. Shasha. *Making Snapshot Isolation Serializable.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1071610.1071615)

## 10. Worked Example

**Write-skew under Snapshot Isolation.** Two doctors share an on-call invariant: at least one of $x, y$ must stay $1$ (on call). Start state $x = y = 1$. A PBT generator emits two concurrent transactions:

- $T_1$: `r1[x=1] r1[y=1] w1[x=0]` (doctor 1 goes off call after seeing doctor 2 is on)
- $T_2$: `r2[x=1] r2[y=1] w2[y=0]` (doctor 2 goes off, symmetric)

Under SI both read the same snapshot ($x{=}y{=}1$), neither writes what the other reads, so there is **no write–write conflict** — both commit. Final state $x = y = 0$, violating the invariant.

Now check the recorded history $H$. Build dependency edges: $T_1$ reads $y$, $T_2$ later overwrites $y$ ⇒ anti-dependency $T_1 \xrightarrow{\mathsf{rw}} T_2$. Symmetrically $T_2 \xrightarrow{\mathsf{rw}} T_1$. The serialization graph has a cycle $T_1 \to T_2 \to T_1$ with **two consecutive $\mathsf{rw}$ edges** — exactly the *dangerous structure* of Fekete et al. So $H$ is **not serializable** (the checker reports it), yet it **is** admissible under SI. A PBT oracle parameterized by isolation level returns: *serializability violated, SI satisfied* — pinpointing write skew with a minimal 2-transaction witness.

---
*Part of the [DBMS Research catalog](../../README.md).*
