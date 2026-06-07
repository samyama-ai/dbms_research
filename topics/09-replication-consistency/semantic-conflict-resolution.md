---
id: 09-replication-consistency/semantic-conflict-resolution
title: "Conflict resolution beyond last-writer-wins"
topic: 09-replication-consistency
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Conflict resolution beyond last-writer-wins

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/semantic-conflict-resolution` · **Status:** open

## 1. Problem Statement
When two replicas accept conflicting concurrent updates to the same logical object, the system must **reconcile** them. The pervasive default — **last-writer-wins (LWW)** — picks the update with the larger timestamp and *silently discards* the other. LWW is convergent and cheap but **loses data** and violates application invariants (e.g. a concurrent "deposit \$50" and "deposit \$30" collapse to one deposit). The problem is to define **principled, application-semantic merge functions** that (a) are deterministic and convergent across replicas, (b) preserve application invariants, and (c) come with a **formal correctness specification** rather than ad-hoc code.

Variants:
- **Synthesis/existence (decision):** given a sequential ADT and an invariant, does a convergent, invariant-preserving merge exist; and can it be derived automatically?
- **Verification:** given a candidate merge, prove it is commutative/associative/idempotent (convergent) *and* invariant-preserving.
- **Optimization:** among correct merges, minimize semantic "loss" / divergence from a hypothetical serial execution.

## 2. Mathematical Foundations
A replicated object has state space $S$, sequential operations $op: S \to S$, and a **merge** $\bowtie: S \times S \times S \to S$ taking two states and (often) their lowest common ancestor $S_{lca}$ — a **three-way merge**, as in version control. State-based convergence requires $\bowtie$ (when $lca$-free, the join $\sqcup$) to form a **bounded join-semilattice**: $\sqcup$ commutative, associative, idempotent (Shapiro et al.). The **strong convergence** theorem says replicas applying the same update set under such a $\sqcup$ reach identical states.

Operation-based CRDTs instead require concurrent operations to **commute**: $op_i \circ op_j = op_j \circ op_i$ for concurrent $i,j$ (Preguiça/Shapiro). Invariant preservation is captured by the **CALM theorem** (Hellerstein; Ameloot–Neven–Van den Bussche) — a program has a coordination-free, consistent implementation **iff it is monotone** — and, for invariants under updates, by **invariant-confluence / I-confluence** (Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica, VLDB 2015): a set of transactions $T$ with invariant $I$ can run coordination-free **iff** $I$ is preserved under merge of $I$-valid divergent states ("$I$-confluent"). Formally, MRDTs (Kaki et al.) and **Katara** (Laddad et al.) derive merges from a *relational/sequential specification* and discharge correctness with SMT.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** *I-confluence* (Bailis et al., VLDB 2015) is the decision criterion for whether semantic merge can be coordination-free; **CALM** (Hellerstein & Alvaro, CACM 2020) characterizes the monotone boundary; **Mergeable Replicated Data Types** (Kaki, Sivaramakrishnan, Jagannathan, OOPSLA 2019) derive merges from relational specs via three-way merge.
- **Systems/synthesis-SOTA:** **Katara** (Laddad, Power, Milano, Cheung, Hellerstein, OOPSLA 2022) *synthesizes* verified CRDTs from sequential data types; **Hamsaz / Hamband** (Houshmand & Lesani, POPL 2019) automatically determine which operations need coordination to preserve invariants and synthesize the protocol; **Quark/replicated-store verification** lines. Production: Riak's *Bucket Types*/CRDTs, Automerge & Yjs (JSON/text MRDTs for collaborative editing) implement domain-specific semantic merges; Git's three-way merge is the canonical manual instance.

## 4. Upper Bound
For data types whose operations are **commutative or monotone** (counters, OR-sets, grow-only structures), invariant-preserving convergent merge exists and is *coordination-free* (CALM/I-confluence give the positive direction). Katara and Hamsaz **automatically synthesize** correct merges/coordination for a broad class of sequential ADTs, with verification discharged by SMT — practical upper bound is "decidable and automatable for first-order-expressible specs." Where I-confluence fails, the *minimal* coordination needed is exactly the set of conflicting operation pairs Hamsaz identifies.

## 5. Lower Bound
- **Impossibility:** by I-confluence, if an invariant is **not** I-confluent (e.g. a uniqueness or non-negative-balance constraint over concurrent decrements), **no** merge function can preserve it without coordination — this is a hard impossibility, independent of cleverness (Bailis et al. 2015). By CALM, **non-monotone** queries provably require coordination.
- **Hardness:** deciding I-confluence / invariant preservation for general first-order invariants and arbitrary operations is **undecidable** in the limit (reduces to satisfiability of unbounded first-order theories); bounded fragments are decidable but the verification is typically **co-NP-hard / PSPACE** depending on the logic. Synthesis inherits this.

## 6. The Gap
**Genuinely open.** The boundary "coordination-free iff monotone/I-confluent" is theoretically *closed*, but (1) **automatically synthesizing low-loss merges** for rich types (nested JSON, ordered lists, graphs with referential integrity) is not solved — text/list MRDTs still suffer interleaving anomalies; (2) there is **no agreed quantitative notion of "semantic loss"** to optimize, so "best correct merge" is ill-defined; (3) verification scalability for real application invariants is open. Closing it needs both a loss metric with optimality theory and scalable verified synthesis.

## 7. Current Research (as of June 2026)
- Verified CRDT/MRDT **synthesis** beyond Katara: lists/trees with anti-interleaving guarantees (Automerge/peritext-style formalization) *(frontier — verify)*.
- Proof frameworks for invariant-preserving merges (Sivaramakrishnan, Lesani, Gotsman, Jagannathan groups).
- LLM-assisted merge-function generation with formal post-hoc verification *(frontier — verify)*.
- Quantifying and minimizing divergence/anomaly under semantic merge (links to anomaly-quantification work).

## 8. Future Work
- A principled "semantic loss" metric and optimal-merge theory.
- Scalable verified synthesis for nested/ordered/graph data with referential invariants.
- Mixed-consistency runtimes that invoke coordination *only* on non-I-confluent operation pairs automatically.

## 9. Key References
- **[Foundational]** Shapiro, Preguiça, Baquero, Zawirski. *Conflict-free Replicated Data Types.* SSS, 2011. — [DBLP](https://dblp.org/rec/conf/sss/ShapiroPBZ11.html)
- **[Foundational]** Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica. *Coordination Avoidance in Database Systems* (I-confluence). VLDB, 2015. — [DOI](https://doi.org/10.14778/2735508.2735509)
- **[Foundational]** Hellerstein, Alvaro. *Keeping CALM: When Distributed Consistency is Easy.* CACM, 2020. — [DOI](https://doi.org/10.1145/3369736)
- **[SOTA]** Kaki, Priya, Sivaramakrishnan, Jagannathan. *Mergeable Replicated Data Types.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360580)
- **[SOTA]** Laddad, Power, Milano, Cheung, Hellerstein. *Katara: Synthesizing CRDTs with Verified Lifting.* OOPSLA, 2022. — [DOI](https://doi.org/10.1145/3563336)
- **[SOTA]** Houshmand, Lesani. *Hamsaz: Replication Coordination Analysis and Synthesis.* POPL, 2019. — [DOI](https://doi.org/10.1145/3290387)

## 10. Worked Example

A bank balance starts at $S_{lca}=100$. Replicas $A$ and $B$ partition and accept concurrent ops:
$$A:\ \text{deposit }50 \Rightarrow 150,\qquad B:\ \text{deposit }30 \Rightarrow 130.$$

**LWW merge** (larger timestamp wins): if $B$'s write has the later clock, result $=130$ — the \$50 deposit is *silently lost*. Convergent (both replicas agree on $130$) but wrong.

**Three-way semantic merge** for a counter: $\bowtie(S_A,S_B,S_{lca}) = S_A + S_B - S_{lca} = 150 + 130 - 100 = 180$. This is commutative, associative, idempotent — a join-semilattice op — so replicas converge to $180$, preserving *both* deposits. This is the PN-counter CRDT.

**Where it breaks (I-confluence fails):** add the invariant $balance \ge 0$ and allow concurrent withdrawals. From $S_{lca}=100$, $A:\,\text{withdraw }80\Rightarrow20$ and $B:\,\text{withdraw }80\Rightarrow20$; merge $=20+20-100=-60 <0$. Each branch is individually $I$-valid, yet the merge violates $I$. By Bailis et al., **no** coordination-free merge can preserve $balance \ge 0$ under concurrent decrements — withdrawals must coordinate.

---
*Part of the [DBMS Research catalog](../../README.md).*
