# Consensus-Free Coordination Avoidance

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/coordination-avoidance` · **Status:** partially-solved

## 1. Problem Statement

Coordination (consensus, locking, two-phase commit) is the dominant latency and availability cost in distributed databases. Yet many operations *commute* or *cannot* break application invariants and so never need to coordinate. **Consensus-free coordination avoidance** asks for a *static, sound* certification:

> Given a set of operations and a set of application **invariants** $I$, decide which operations may execute **coordination-free** (locally, replicated, asynchronously) such that *every* reachable replicated state still satisfies $I$ — and force coordination only on the rest.

Variants:
- **Decision:** is invariant $I$ preserved under all coordination-free interleavings of operation set $T$? (I-confluence test.)
- **Optimization:** find the *minimal* set of operations/conflict pairs that must coordinate (minimize coordination while keeping $I$).
- **Synthesis:** automatically generate the coordination protocol / tokens for the operations that do need it.

## 2. Mathematical Foundations

**I-confluence** (Bailis et al., 2015): a set of transactions $T$ and invariant $I$ are *I-confluent* iff for all $I$-valid states $s$ reachable, merging divergent $I$-valid states (via the replicated merge $\sqcup$) yields an $I$-valid state:
$$ \forall s_1, s_2 \text{ reachable and } I\text{-valid}: \quad I(s_1)\wedge I(s_2) \implies I(s_1 \sqcup s_2). $$
If $(T, I)$ is I-confluent, a coordination-free, available, convergent (transactionally available) execution exists; if not, *some* coordination is provably required. The criterion is invariant-by-invariant: equality/uniqueness invariants (e.g., unique keys) are **not** I-confluent (two concurrent inserts of the same key both valid, union invalid); monotone invariants and CRDT-mergeable conditions often are.

Related foundations: **CALM theorem** (Hellerstein; proved by Ameloot et al.) — *a query/program has a coordination-free distributed implementation iff it is monotone* (expressible without negation/aggregation that is not monotone), connecting coordination-freedom to **logical monotonicity** and the Bloom/Dedalus model. **CRDTs** give the merge $\sqcup$ as a join on a semilattice. **RedBlue consistency** partitions operations into *blue* (commutative, globally commutative, coordination-free) and *red* (must be totally ordered) and proves safety when the partition respects invariants + commutativity.

## 3. State of the Art (SOTA)

**Theory-SOTA.** *I-confluence* (Bailis et al., VLDB 2015) — the canonical decision criterion, with a per-invariant analysis showing most standard SQL isolation anomalies and many invariants are coordination-free. *CALM* (Hellerstein 2010; Ameloot–Neven–Van den Bussche, PODS 2013 proof) — the monotonicity characterization. *RedBlue consistency* (Li et al., OSDI 2012).

**Systems-SOTA.** *Bloom/Bloom^L* and the **Hydro/Anna** lineage (Berkeley) compile monotone programs to coordination-free dataflow and flag points needing coordination. *Indigo / Explicit Consistency* (EuroSys 2015) statically analyzes invariants, detects conflicting operation pairs, and synthesizes reservation/escrow tokens (numeric, ownership, partition locks) so only genuinely-conflicting ops coordinate. *CISE* (Cause-Is-Everywhere / "‘Cause I’m Strong Enough", POPL 2016) provides a **proof rule and SMT-backed tool** to verify which operations are safe coordination-free, and *Soteria*/*Hamsaz*/*Hampa* synthesize the minimal coordination (conflict-relation + serializability of the residual).

## 4. Upper Bound

When $(T,I)$ is I-confluent (or CALM-monotone), the upper bound is **zero coordination**: operations run locally with $O(1)$ latency, fully available under partition, converging via CRDT merge. For mixed workloads, tools (CISE, Hamsaz) compute a **conflict relation** and synthesize coordination only on conflicting pairs; the residual coordination is provably *minimal* with respect to the analysis (only invariant-threatening or non-commuting pairs are serialized). Escrow/reservation techniques (Indigo) further turn many "must-coordinate" numeric invariants into *amortized* coordination, contacting peers only when a local budget is exhausted.

## 5. Lower Bound

The **I-confluence theorem itself is a lower bound**: if $(T,I)$ is *not* I-confluent, then **no** coordination-free, globally-available, convergent implementation exists — coordination is mathematically required, a CAP-style impossibility specialized to invariants. **CALM** gives the matching converse: non-monotone programs *cannot* be coordination-free. Concretely, uniqueness/foreign-key/limit invariants under concurrent inserts are non-I-confluent and force at least one round of agreement. Deciding I-confluence/monotonicity in general is **undecidable** for arbitrary first-order invariants (reduces to satisfiability/containment), so the *certification* problem is itself hard — tools are sound but necessarily incomplete, restricting to decidable fragments (EPR/SMT-checkable invariants).

## 6. The Gap

"Partially solved": the *characterization* is complete and beautiful (I-confluence ⇔ coordination-free; CALM ⇔ monotone). The gaps are (i) **decidability/automation** — the test is undecidable in full generality, so practical certification covers only restricted invariant logics, and pushing that frontier (richer invariants, aggregates, derived data) is open; (ii) **minimality of synthesized coordination** — proving the residual coordination is truly optimal, not just analysis-minimal, for general workloads; (iii) **dynamic** coordination avoidance that adapts certification as schema/invariants evolve. Closing these needs better decidable fragments and tighter synthesis-optimality proofs.

## 7. Current Research (as of June 2026)

(1) **SMT/EPR-based invariant certification** at greater expressiveness (CISE descendants, Soteria, Hampa) — automating more of the I-confluence test *(frontier — verify)*; (2) **Hydroflow / Hydro** (Berkeley) compiling to coordination-free dataflow with automatic coordination insertion at non-monotone points; (3) verified CRDT libraries with machine-checked I-confluence; (4) coordination avoidance for **transactional + ML/derived-data** workloads. People/groups: Joseph Hellerstein & the Hydro/Anna team (Berkeley), Peter Alvaro (UCSC, Bloom/CALM), Marc Shapiro & Nuno Preguiça (CRDTs, CISE), Mahsa Najafzadeh, and Indigo/Antidote (EuroSys) authors.

## 8. Future Work

- Wider decidable invariant fragments for automatic I-confluence checking.
- Provably minimal (not just sound) coordination synthesis for general invariants.
- Coordination avoidance integrated with serializable isolation guarantees end-to-end.
- Certification under schema/invariant evolution and for derived/materialized state.
- Quantitative coordination-cost models to choose escrow budgets automatically (links to bounded-staleness).

## 9. Key References

- **[Foundational]** P. Bailis, A. Fekete, M. Franklin, A. Ghodsi, J. Hellerstein, I. Stoica. *Coordination Avoidance in Database Systems (I-Confluence).* VLDB, 2015. — [DOI](https://doi.org/10.14778/2735508.2735509)
- **[Foundational]** J. M. Hellerstein. *The Declarative Imperative (CALM Conjecture).* SIGMOD Record, 2010. — [DOI](https://doi.org/10.1145/1860702.1860704)
- **[Foundational]** T. Ameloot, F. Neven, J. Van den Bussche. *Relational Transducers for Declarative Networking (CALM Proof).* JACM / PODS, 2013. — [DOI](https://doi.org/10.1145/2450142.2450151)
- **[SOTA]** C. Li, D. Porto, A. Clement, J. Gehrke, N. Preguiça, R. Rodrigues. *Making Geo-Replicated Systems Fast as Possible, Consistent when Necessary (RedBlue Consistency).* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/li)
- **[SOTA]** V. Balegas, S. Duarte, C. Ferreira, R. Rodrigues, N. Preguiça, et al. *Putting Consistency Back into Eventual Consistency (Indigo / Explicit Consistency).* EuroSys, 2015. — [DOI](https://doi.org/10.1145/2741948.2741972)
- **[SOTA]** A. Gotsman, H. Yang, C. Ferreira, M. Najafzadeh, M. Shapiro. *'Cause I'm Strong Enough: Reasoning about Consistency Choices in Distributed Systems (CISE).* POPL, 2016. — [DBLP](https://dblp.org/rec/conf/popl/GotsmanYFNS16.html)

## 10. Worked Example

Two replicas $r_1, r_2$ start from a shared bank account with `balance = 100`. Merge $\sqcup$ is "apply both operations."

**I-confluent invariant — none / monotone counter.** Invariant $I$: `total_deposits` only grows. $r_1$ does `deposit(+30)`, $r_2$ does `deposit(+50)` concurrently. Each local state is $I$-valid; merging gives `balance = 180`, still $I$-valid. So $I(s_1)\wedge I(s_2)\Rightarrow I(s_1\sqcup s_2)$ holds — runs **coordination-free**.

**Non-I-confluent invariant — $balance \ge 0$.** Now $I$: `balance >= 0`. $r_1$ does `withdraw(70)` (local: $100-70=30$, valid), $r_2$ does `withdraw(80)` (local: $100-80=20$, valid). Both states are $I$-valid individually, but $s_1\sqcup s_2$ applies both: $100-70-80 = -50 < 0$, violating $I$. The implication fails, so by the I-confluence theorem **no** coordination-free, available, convergent execution is safe — at least one withdrawal must coordinate (or use an escrow budget splitting the $\$100$ into per-replica reservations of $\$50$ each).

---
*Part of the [DBMS Research catalog](../../README.md).*
