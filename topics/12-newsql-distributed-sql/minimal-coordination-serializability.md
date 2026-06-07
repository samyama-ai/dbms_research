---
id: 12-newsql-distributed-sql/minimal-coordination-serializability
title: "Minimizing coordination for serializability"
topic: 12-newsql-distributed-sql
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Minimizing coordination for serializability

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/minimal-coordination-serializability` · **Status:** partially-solved

## 1. Problem Statement

Coordination — cross-shard/cross-replica synchronous communication on the critical path of
a transaction — is the dominant cost in distributed databases. The question is: given an
application (a set of transaction templates plus integrity constraints), determine the
**maximal coordination-free fragment** that still guarantees the target correctness
criterion, typically **(one-copy) serializability** or **invariant confluence**.

Variants: (i) **Decision** — given a program $\Pi$ and invariant set $\Sigma$, is $\Pi$
executable without any coordination while preserving $\Sigma$ (and, separately, while
preserving serializability)? (ii) **Optimization** — partition the operations into a
coordinated and a coordination-free set so as to minimize the expected/worst-case number
of coordination rounds subject to correctness. (iii) **Synthesis** — emit the minimal set
of synchronization points (e.g., which writes need a consensus round) that makes $\Pi$
correct.

## 2. Mathematical Foundations

The central concept is **invariant confluence (I-confluence)** (Bailis et al., VLDB 2015):
a system state is modeled as a join-semilattice of replica states under a merge operator
$\sqcup$; a set of transactions $T$ and invariant $I$ are **$I$-confluent** iff for all
$I$-valid reachable states, merging divergent replicas preserves $I$. Theorem: a globally
$I$-valid, convergent, and coordination-free execution exists **iff** $T$ is $I$-confluent
w.r.t. $I$. This decouples "needs coordination" from "is a write conflict."

A complementary lens is the **CALM theorem** (Hellerstein; Ameloot–Neven–Van den Bussche,
PODS 2011): a query/program is computable by a **coordination-free**, monotone, eventually
consistent distributed program **iff it is expressible in monotone logic** (a
$\textsf{Datalog}^{\neg}$ / monotonicity condition). Non-monotonicity (aggregation,
negation, set difference) is exactly what forces coordination.

For serializability specifically, the relevant structure is the **conflict graph** and the
notion that two operations commute. Let $\mathrm{commute}(op_i, op_j)$ hold iff
$op_i \circ op_j = op_j \circ op_i$ on all states. Coordination is provably avoidable
between commuting operations; the residual coordination requirement is governed by the
**non-commuting, invariant-threatening** pairs.

## 3. State of the Art (SOTA)

**Theory SOTA.** I-confluence (Bailis–Fekete–Franklin–Ghodsi–Hellerstein–Stoica, VLDB
2015) gives the exact condition for coordination-free invariant preservation and analyzes
standard SQL constraints (foreign keys, uniqueness, check constraints). CALM
(Ameloot–Neven–Van den Bussche, PODS 2011; Hellerstein–Alvaro CACM 2020) gives the
monotonicity characterization. The **RedBlue consistency** framework (Li et al., OSDI 2012)
classifies operations into commutative "blue" (async) and "red" (coordinated) ops and
shifts as much as possible to blue.

**Systems SOTA.** Homeostasis / "demarcation"-style escrow and reservation protocols allow
constraint-preserving coordination avoidance (e.g., for inventory/quantity invariants).
Quelea (Sivaramakrishnan–Kaki–Jagannathan, PLDI 2015) lets programmers declare contracts
and synthesizes the weakest sufficient consistency level. IPA, Sieve, and Carol provide
tool support for inferring coordination requirements from invariants.

## 4. Upper Bound

When $T$ is $I$-confluent, the upper bound on coordination is **zero rounds** — fully
coordination-free, with merge handling convergence; only local validation is needed.
For non-$I$-confluent fragments, escrow/reservation techniques reduce coordination to
**amortized $O(1)$** rounds by pre-acquiring divisible budget (e.g., split a stock count
across replicas), paying coordination only on budget refill. The RedBlue/Quelea approach
upper-bounds coordination by the number of "red"/strong operations, which the analysis
minimizes by promoting operations to commutative form.

## 5. Lower Bound

Lower bounds are **impossibility-theoretic**, from the CALM theorem and CAP/FLP: any
program requiring a non-monotone result (e.g., a global uniqueness check, a count that can
both increase and decrease across a threshold) **cannot** be implemented coordination-free
while remaining consistent and available — coordination is *necessary*, not merely
convenient. Deciding $I$-confluence for *arbitrary* invariants and transactions is
**undecidable in general** (it subsumes reachability of an invariant-violating state in a
program with unbounded data); it is decidable/tractable only for restricted invariant
classes (linear-arithmetic constraints, per-row checks). For relational programs the
monotonicity test underlying CALM is tied to the (undecidable in general) monotonicity of
query expressions, decidable for fragments like positive relational algebra.

## 6. The Gap

The *characterization* is essentially closed in principle (I-confluence and CALM give
exact iff-conditions), so the problem is partially solved. The genuine open gap is
**algorithmic and quantitative**: (1) decidable, push-button procedures that, for realistic
SQL workloads with rich invariants, compute the maximal coordination-free fragment rather
than requiring expert annotation; (2) *minimizing* residual coordination (the optimization
variant) is largely unstudied as an approximation problem — what is its hardness and best
achievable ratio? (3) coordination-free fragments that still guarantee **serializability**
(not just invariant preservation under weak consistency) are narrower and less well
mapped.

## 7. Current Research (as of June 2026)

Active directions: automated I-confluence/CALM analysis embedded in compilers for
distributed applications; SMT-backed invariant-confluence checkers for SQL constraint sets
*(frontier — verify)*; and integration with CRDT-based stores to push more operations into
the coordination-free regime. Groups associated with Hellerstein, Alvaro, Gotsman, Enea,
and Jagannathan remain active; recent work explores **mixed-consistency type systems** that
statically certify the coordination level per operation *(frontier — verify)*.

## 8. Future Work

- An approximation theory for the coordination-minimization optimization variant.
- Decidable I-confluence for broader invariant logics (aggregates, recursive constraints).
- Coordination-free **serializable** fragments and their compositional closure.
- Runtime adaptivity: switching a transaction between coordinated and coordination-free
  paths based on observed conflict rates while preserving the static safety proof.

## 9. Key References

- **[Foundational]** Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica. *Coordination Avoidance in Database Systems.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2735508.2735509)
- **[Foundational]** Ameloot, Neven, Van den Bussche. *Relational Transducers for Declarative Networking (CALM).* PODS, 2011 / J. ACM. — [arXiv](https://arxiv.org/abs/1012.2858)
- **[SOTA]** Li, Porto, Clement, Gehrke, Preguiça, Rodrigues. *Making Geo-Replicated Systems Fast as Possible, Consistent when Necessary (RedBlue).* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/li)
- **[SOTA]** Sivaramakrishnan, Kaki, Jagannathan. *Declarative Programming over Eventually Consistent Data Stores (Quelea).* PLDI, 2015. — [DOI](https://doi.org/10.1145/2737924.2737981)
- **[Survey]** Hellerstein, Alvaro. *Keeping CALM: When Distributed Consistency is Easy.* CACM, 2020. — [DOI](https://doi.org/10.1145/3369736)

## 10. Worked Example

Invariant $I:\ \texttt{stock} \ge 0$, replicated across two regions, starting at $\texttt{stock}=10$.

**Decrements alone are not $I$-confluent.** Txn $T:\ \texttt{stock}\mathrel{-}=8$ runs at each
region against the $I$-valid state $10$: region 1 yields $2$, region 2 yields $2$ — both valid.
But merging the divergent replicas (each applied its own decrement) gives
$10 - 8 - 8 = -6 < 0$, violating $I$. So $\{T\}$ is **not** $I$-confluent w.r.t. $I$, and the
theorem says coordination is *necessary*.

**Escrow makes it coordination-free.** Split the budget: region 1 holds $5$ units, region 2
holds $5$. Each region serves decrements only against its local escrow; a sale of $3$ in region
1 leaves local budget $2$, no cross-region message. Merging never goes negative because
$5+5=10$ and neither side overspends its share. Coordination drops to **amortized $O(1)$** —
paid only when a region's local budget is exhausted and must be refilled.

Contrast: a global **uniqueness** check (insert-if-absent) is non-monotone — by CALM it
*cannot* be made coordination-free, no escrow trick applies.

---
*Part of the [DBMS Research catalog](../../README.md).*
