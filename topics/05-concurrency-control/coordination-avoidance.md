# Coordination Avoidance Boundaries

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/coordination-avoidance` · **Status:** partially-solved

## 1. Problem Statement

Coordination (locks, consensus, atomic commit, synchronous replication) is the dominant cost in distributed transactions and the source of unavailability under partitions. **Coordination avoidance** asks: which application correctness criteria — expressed as **invariants** $I$ over database state — can be maintained while letting replicas execute and commit **without** synchronizing, merging their effects later? The central concept is **invariant confluence (I-confluence)**: an invariant $I$ and a set of transactions $\mathcal{T}$ are I-confluent if every state reachable by merging divergent, individually-$I$-preserving executions also satisfies $I$. The problem is to **precisely characterize** the boundary — to decide, for a given $(I, \mathcal{T})$, whether coordination-free execution preserves $I$, and to do so for rich, practically relevant invariant languages.

Variants: the **decision** problem (is $(I, \mathcal{T})$ I-confluent?); the **synthesis/optimization** problem (given a non-I-confluent workload, place the minimum coordination — fewest synchronization points — to restore safety); the **classification** problem (map common SQL/application invariants to confluent vs. not).

## 2. Mathematical Foundations

Model state as elements of a join-semilattice or, more generally, a set $S$ with a **merge** operator $\sqcup$ that is commutative, associative, and idempotent (the CRDT setting) or an application-defined reconciliation. A transaction is a function $t : S \to S$. Given an initial $I$-valid state $s_0$ and transactions each preserving $I$ locally, $(I, \mathcal{T})$ is **I-confluent** iff for all reachable divergent states $s_1, s_2$ (each $I$-valid),

$$I(s_1) \wedge I(s_2) \;\Rightarrow\; I(s_1 \sqcup s_2).$$

The Bailis et al. (VLDB 2014) theorem: *coordination-free, available, convergent execution that maintains $I$ is possible iff $(I,\mathcal{T})$ is I-confluent.* This is the database analogue of the **CALM theorem** (Hellerstein; Ameloot, Neven, Van den Bussche, PODS 2013): a query/program has a coordination-free (eventually consistent, confluent) distributed implementation **iff it is monotone**. Monotone invariants ($\subseteq$-closed, e.g., "$x$ has been assigned" growing sets) are confluent; **non-monotone** ones (uniqueness, foreign-key under deletes, bounded counters, "exactly one winner") generally are not. The formal bridge is logical monotonicity / Datalog stratification and lattice theory.

## 3. State of the Art (SOTA)

**Theory-SOTA:** the **CALM theorem** (Ameloot, Neven, Van den Bussche, PODS 2013; Hellerstein & Alvaro, CACM 2020) gives the monotonicity↔coordination-freeness equivalence for distributed query semantics. **I-confluence** (Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica, VLDB 2014) gives the transactional/invariant analogue and classifies common SQL invariants. Indigo / explicit invariant-preservation reservations (Balegas et al., EuroSys 2015), Blazes (Alvaro et al.), and the **RedBlue consistency** framework (Li et al., OSDI 2012) operationalize the boundary by splitting operations into coordinated (red) and coordination-free (blue). CRDT theory (Shapiro, Preguiça, Baquero, Zawirski, 2011) underlies the merge side.

**Systems-SOTA:** Read-Atomic / RAMP transactions (Bailis et al., SIGMOD 2014), AntidoteDB (transactional causal+ with CRDTs), and bounded-counter / escrow techniques realize coordination avoidance in production-style systems.

## 4. Upper Bound

For invariants expressible in restricted fragments, I-confluence/monotonicity is **decidable**: monotone (positive, no negation/aggregation) Datalog programs are coordination-free by CALM, checkable structurally. Equality-generating-dependency-free, $\subseteq$-monotone invariants are confluent by inspection. Synthesis upper bounds: RedBlue and Indigo place coordination only on the non-confluent (red) operations, achieving coordination cost proportional to the count of conflicting operation pairs rather than all transactions. Escrow/reservation techniques make bounded-counter constraints confluent with $O(\text{partitions})$ pre-allocated quota.

## 5. Lower Bound

Many useful invariants are provably **not** I-confluent — uniqueness (primary keys), foreign keys with deletion, and bounded numeric constraints (e.g., non-negative inventory) require coordination; this is a hard impossibility, not a heuristic gap (Bailis et al.). It aligns with the **CAP theorem** (Gilbert & Lynch, 2002): maintaining a non-monotone global invariant with availability under partition is impossible. Deciding I-confluence for *general* first-order invariants with arbitrary transactions is **undecidable** (it subsumes satisfiability/validity over the invariant logic); for expressive decidable fragments it can be **coNP-** or higher-complexity-hard. Minimum-coordination synthesis is **NP-hard** (covering the non-confluent conflict pairs is a hitting-set problem).

## 6. The Gap

**Partially solved.** The conceptual boundary is settled — monotonicity / I-confluence is the right characterization, and the two extremes (purely monotone vs. uniqueness/bounded constraints) are classified. What remains open: (i) **decision procedures** for rich, practically common invariant languages (SQL CHECK constraints, aggregates, foreign keys under inserts *and* deletes) — much is undecidable or unmapped; (ii) **automatic, minimum-cost** coordination placement with optimality guarantees; (iii) tight characterization for invariants over CRDT merge semantics beyond join-semilattices.

## 7. Current Research (as of June 2026)

Directions: automated **verification tools** that check I-confluence / monotonicity of application code and synthesize minimal coordination (the CISE-style proof rule, Gotsman, Yang, Ferreira, Najafzadeh, Shapiro, POPL 2016, remains the workhorse, with newer SMT-backed checkers) *(frontier — verify)*; mixed consistency programming models; coordination avoidance for serverless and geo-replicated transactional stores. Groups: Hellerstein/Alvaro (Berkeley — Hydro/Anna lineage), Shapiro/Preguiça/Gotsman (Sorbonne/IMDEA — CRDTs, CISE), Bailis-lineage practical systems.

## 8. Future Work

- Decision procedures and complexity maps for SQL-grade invariants (aggregates, FK under deletes).
- Sound, automatic, minimum-cost coordination synthesis with optimality guarantees.
- I-confluence over general CRDT merges and partial-order replication beyond lattices.
- Integrating confluence analysis into compilers/ORMs so coordination is inserted only where provably required.

## 9. Key References

- **[Foundational]** Gilbert, S.; Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* ACM SIGACT News, 2002.
- **[Foundational]** Ameloot, T.; Neven, F.; Van den Bussche, J. *Relational Transducers for Declarative Networking (CALM).* PODS, 2013 / JACM.
- **[SOTA]** Bailis, P.; Fekete, A.; Franklin, M.; Ghodsi, A.; Hellerstein, J.; Stoica, I. *Coordination Avoidance in Database Systems.* PVLDB, 2014.
- **[SOTA]** Li, C.; Porto, D.; Clement, A.; Gehrke, J.; Preguiça, N.; Rodrigues, R. *Making Geo-Replicated Systems Fast as Possible, Consistent when Necessary (RedBlue).* OSDI, 2012.
- **[SOTA]** Gotsman, A.; Yang, H.; Ferreira, C.; Najafzadeh, M.; Shapiro, M. *'Cause I'm Strong Enough: Reasoning about Consistency Choices in Distributed Systems (CISE).* POPL, 2016.
- **[Survey]** Hellerstein, J.; Alvaro, P. *Keeping CALM: When Distributed Consistency Is Easy.* Communications of the ACM, 2020.
- **[Foundational]** Shapiro, M.; Preguiça, N.; Baquero, C.; Zawirski, M. *Conflict-Free Replicated Data Types.* SSS, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
