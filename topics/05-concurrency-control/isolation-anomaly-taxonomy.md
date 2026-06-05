# Isolation-Level Anomaly Completeness

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/isolation-anomaly-taxonomy` · **Status:** partially-solved

## 1. Problem Statement
Construct a *complete* and *formally verified* lattice of concurrency anomalies whose presence or absence exactly characterizes every commercial isolation level (READ UNCOMMITTED, READ COMMITTED, CURSOR STABILITY, SNAPSHOT ISOLATION, REPEATABLE READ, SERIALIZABLE, and vendor-specific variants). The problem has three intertwined variants:

- **Decision variant:** Given two isolation levels $L_1, L_2$, decide whether $L_1 \preceq L_2$ (every history permitted by $L_1$ is permitted by $L_2$) under a fixed anomaly-based definition.
- **Characterization (completeness) variant:** Find a finite set $A$ of anomalies such that each commercial level $L$ equals $\{H : H \text{ avoids } A_L\}$ for some $A_L \subseteq A$, and prove $A$ is *minimal* and *complete* (no two distinct levels collapse, no level needs an anomaly outside $A$).
- **Counting variant:** Enumerate the distinct equivalence classes of histories induced by the lattice.

The open part is producing a *single* taxonomy that is simultaneously implementation-independent, mechanically checked, and faithful to what real systems (PostgreSQL, Oracle, SQL Server, CockroachDB) actually deliver.

## 2. Mathematical Foundations
A *history* $H$ is a partial order over operations $r_i[x], w_i[x], c_i, a_i$. Berenson et al. define anomalies *phenomenologically* (e.g. P1 dirty read, P2 fuzzy read, P3 phantom; broad interpretations A1–A3). Adya's framework instead uses a *Direct Serialization Graph* $DSG(H)$ whose vertices are committed transactions and whose edges are dependencies:

$$T_i \xrightarrow{ww} T_j,\quad T_i \xrightarrow{wr} T_j,\quad T_i \xrightarrow{rw} T_j$$

(write, read, and *anti-* dependencies). Isolation levels are defined by *proscribing graph patterns*: e.g. PL-3 (serializability) forbids any cycle in $DSG$; SI forbids cycles without two consecutive anti-dependency edges. Key theorem (Adya–Liskov–O'Neil): the phenomena $G0$ (write cycle), $G1$ (aborted/intermediate/circular read), $G2$ (anti-dependency cycle) yield implementation-independent definitions equivalent to the ANSI intent for the standard levels.

Fekete et al. add the *dangerous structure* theorem: a non-serializable SI execution must contain two rw-antidependency edges $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_3$ forming a cycle, with $T_1, T_3$ possibly identical — the basis of Serializable Snapshot Isolation.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Adya's cycle-based taxonomy (PODS/ICDE 2000) is the de facto formal reference; Cerone–Bernardi–Gotsman (CONCUR 2015) give a unified axiomatic framework over abstract executions that handles SI, parallel SI, and prefix consistency uniformly. Crooks et al. (PODC 2017) provide a *client-centric* state-based definition that is provably equivalent yet observable without server internals.
- **Systems-SOTA:** Tools like *Elle* (Kingsbury–Alvaro, VLDB 2020) infer anomalies from black-box client observations using list-append datatypes and recover much of the $G0/G1/G2$ structure; *Cobra* (Tan et al., OSDI 2020) verifies serializability of black-box key-value stores via SMT/GPU-accelerated cycle search.

## 4. Upper Bound
Checking a *fixed* level for a given finite history reduces to cycle detection in $DSG(H)$: $O(V+E)$ via Tarjan for $G0/G1$. For serializability *verification* of an arbitrary observed history, the problem is the classic VSR/CSR distinction — testing **conflict** serializability is $O(V+E)$, but testing **view** serializability is NP-complete (Papadimitriou 1979), giving the practical upper bound used by Cobra (NP search with SMT pruning).

## 5. Lower Bound
Testing *view* serializability of a history is **NP-complete** (Papadimitriou, JACM 1979) — this is the canonical hardness result bounding any taxonomy that must decide membership exactly. The completeness/minimality question itself is not known to have a matching hardness bound; the difficulty is *modeling* (capturing predicate/phantom semantics) rather than computational. No information-theoretic or fine-grained lower bound is established for the lattice-construction variant.

## 6. The Gap
Conflict-graph taxonomies are decidable and clean but *under-specify* predicate-based phenomena (phantoms, predicate dependencies), which require sequences-of-states reasoning. The genuinely open gap: no single formally verified lattice reconciles (a) Adya's edge semantics, (b) predicate/phantom anomalies, and (c) the *actual* behavior of commercial engines, which deviate from their advertised levels. Closing it requires a mechanized proof (e.g. Coq/Isabelle) that the proposed minimal anomaly set both separates all commercial levels and matches observed engine behavior.

## 7. Current Research (as of June 2026)
Active threads: mechanized isolation semantics in proof assistants (extensions of the Cerone–Gotsman axiomatics); black-box checkers (Elle, Cobra successors) being pushed toward *predicate* anomalies and toward bounded-staleness/causal levels. *(frontier — verify)* Work formalizing CockroachDB/Spanner external-consistency guarantees against the lattice, and efforts to fold *read-atomic* and *transactional causal consistency* into a single hierarchy, appear active in 2025–2026 PODS/VLDB venues.

## 8. Future Work
- A mechanically verified minimal anomaly basis covering predicate dependencies and phantoms.
- Bridging the *intent* gap where engines silently provide stronger/weaker guarantees than declared.
- Extending the lattice to geo-distributed and HTAP systems with mixed staleness.

## 9. Key References
- **[Foundational]** Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995.
- **[Foundational]** Adya, Liskov, O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000.
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979.
- **[SOTA]** Cerone, Bernardi, Gotsman. *A Framework for Transactional Consistency Models with Atomic Visibility.* CONCUR, 2015.
- **[SOTA]** Crooks, Pu, Alvisi, Clement. *Seeing is Believing: A Client-Centric Specification of Database Isolation.* PODC, 2017.
- **[SOTA]** Kingsbury, Alvaro. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
