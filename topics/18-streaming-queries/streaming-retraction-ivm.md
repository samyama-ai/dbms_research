---
id: 18-streaming-queries/streaming-retraction-ivm
title: "Retraction and incremental view maintenance over streams"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Retraction and incremental view maintenance over streams

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-retraction-ivm` · **Status:** partially-solved

## 1. Problem Statement
A streaming materialized view $V = Q(\text{input streams})$ must be kept correct as inputs change — including **deletions/retractions** (negative tuples) arising from late-event corrections, window expiry, upstream updates, or aggregate recomputation. Given a delta (insertions and **retractions**) on inputs, compute the corresponding delta on $V$ correctly and efficiently, propagating *negative* multiplicities through selections, projections, joins, aggregations, and **recursion/fixpoints**.

Variants:
- **Correctness:** the maintained view equals re-evaluating $Q$ from scratch (consistency under arbitrary insert/delete interleavings).
- **Efficiency (decision/optimization):** minimize work per delta; ideally proportional to delta + affected output, not to view size.
- **Recursive views:** retraction under recursion (e.g., transitive closure) where deleting one edge may invalidate many derived facts (the "derivation counting" / DRed problem).
- **Bounded latency / out-of-order:** retractions caused by late events must be applied without blocking the live stream.

## 2. Mathematical Foundations
Views are computed over **$\mathbb{Z}$-relations** (or bags with integer multiplicities): a tuple's annotation is an integer, negative = retraction. Relational operators lift to **homomorphisms over the abelian group/ring $\mathbb{Z}$** — this is the core of **differential dataflow** (McSherry, Murray, Isaacs, Isard) and DBToaster's algebra. The delta rules generalize the classic **count/derivation algorithm** (Gupta–Mumick–Subrahmanian, SIGMOD 1993): $\Delta(A\bowtie B)=\Delta A\bowtie B \;\uplus\; A\bowtie\Delta B \;\uplus\;\Delta A\bowtie\Delta B$, valid with signed multiplicities. Iterating delta rules (**recursive IVM**) requires the **DRed** algorithm (Delete-and-Rederive) or counting of derivations to correctly retract recursively-derived tuples.

**Higher-order IVM** (DBToaster, Koch et al.): maintain the view *and* a hierarchy of auxiliary materialized deltas, so each maintenance step is itself a (cheaper) view; for queries up to degree $k$ this gives polynomial speedups and, for many queries, $O(1)$-amortized maintenance. **Differential dataflow** generalizes to a **partial order of (time, iteration) lattice** so updates at different logical times and iteration rounds compose as elements of a commutative group indexed by a lattice, enabling correct incremental *and* iterative computation with **arrangements** (shared indexed state).

Aggregates need **group/monoid** structure: invertible aggregates (SUM, COUNT) retract in $O(1)$; non-invertible (MIN/MAX) need auxiliary structures (e.g., a sorted/heap or the "subtractable" reformulation) because a retraction may un-mask a previous extremum.

## 3. State of the Art (SOTA)
- **DRed / counting algorithms** (Gupta, Mumick, Subrahmanian, SIGMOD 1993): foundational recursive IVM with deletions.
- **DBToaster / higher-order IVM** (Koch, Ahmad, Kennedy, Nikolic, Lerner, et al., VLDBJ 2014): recursive delta compilation; best-in-class single-node maintenance throughput.
- **Differential Dataflow / Timely** (McSherry, Murray, Isard, Abadi; CIDR 2013) and its product **Materialize**: incremental + iterative maintenance with retractions and consistency under out-of-order via virtual times; systems-SOTA for general streaming SQL views.
- **F-IVM** (Nikolic, Olteanu, SIGMOD 2018): factorized IVM with rings, unifying analytics/aggregates.
- **DYN / IVMε** (Berkholz, Keppmann, Schweikardt, Kanté; Idris–Ugarte–Vansummeren, SIGMOD 2017): worst-case-optimal *dynamic* query evaluation with constant-delay enumeration after updates.
- Systems: Flink Table API **changelog/retract streams**, Spark, ksqlDB, **Noria** (Gjengset et al., OSDI 2018) partial-state IVM web caches.

## 4. Upper Bound
**Higher-order IVM** (DBToaster) maintains any positive relational query up to degree $k$ with per-update cost polynomial in the database and, for a broad class, **amortized $O(1)$** per single-tuple update (insert or delete). For **conjunctive queries**, dynamic evaluation with **worst-case-optimal** update time and **constant-delay enumeration** is achievable for the *q-hierarchical* fragment (Berkholz–Keppeler–Schweikardt, PODS 2017; Idris et al.) — $O(1)$ amortized update, constant-delay output. Differential dataflow maintains general (including recursive) dataflows with update cost proportional to the *changed* portion of the computation, holding in the timely/lattice model.

## 5. Lower Bound
The dynamic-evaluation lower bounds are **conditional / fine-grained**: a conjunctive query admits $O(1)$-update, constant-delay maintenance **iff** it is *q-hierarchical*; otherwise, assuming the **Online Matrix-Vector (OMv) conjecture**, any algorithm needs $\Omega(n^{1/2-\delta})$ (or worse) per update — proven for the simplest non-hierarchical query, the 2-path/triangle-detection-style views (Berkholz–Keppeler–Schweikardt). Recursive retraction (DRed) can require re-deriving $\Omega$(view-size) facts: deleting one base tuple may invalidate a number of derived facts that is not bounded by the delta (no "local" maintenance), an unavoidable worst case for transitive closure under deletion. Non-invertible aggregates (MIN/MAX) provably cannot be maintained in $O(1)$ extra state under retraction without auxiliary order structure.

## 6. The Gap
For **positive / q-hierarchical** queries the picture is essentially **closed**: q-hierarchical iff $O(1)$-update + constant-delay, with matching OMv lower bounds. Genuinely **partial/open**: (a) tight bounds for **non-hierarchical** and **cyclic/recursive** views under deletion (current bounds are OMv-conditional, not unconditional, and upper/lower bounds don't always match for $\ge 3$-way joins); (b) optimal recursive retraction beyond DRed's pessimistic over-deletion (avoiding re-derivation work); (c) retraction with **bounded latency** under out-of-order arrival, where late-event retractions interleave with live processing; (d) factorized/worst-case-optimal IVM for full aggregation+retraction. Closing these needs either unconditional lower bounds or algorithms breaking the OMv barrier for structured workloads.

## 7. Current Research (as of June 2026)
- Worst-case-optimal **dynamic** query evaluation and constant-delay enumeration beyond q-hierarchical (Olteanu, Schweikardt, Vansummeren, Keppeler) *(frontier — verify)*.
- Differential-dataflow/Materialize advances on incremental recursion, **consistency**, and retraction under late data; sharing of arrangements *(frontier — verify)*.
- Factorized and **ring/semiring** IVM (F-IVM) extended to ML/linear-algebra workloads.
- Partial-state and eviction-aware IVM (Noria-style) with correctness under cache misses + retraction.

## 8. Future Work
- Unconditional (non-OMv) lower bounds for non-hierarchical IVM under deletion.
- Recursive retraction that avoids DRed over-deletion (provenance-guided minimal re-derivation).
- Low-latency retraction propagation interleaved with out-of-order streaming.
- Unified theory of aggregation + recursion + retraction with worst-case-optimal guarantees.

## 9. Key References
- **[Foundational]** Gupta, A., Mumick, I.S., Subrahmanian, V.S. *Maintaining Views Incrementally (Counting and DRed).* SIGMOD, 1993. — [DOI](https://doi.org/10.1145/170035.170066)
- **[Foundational]** McSherry, F., Murray, D., Isaacs, R., Isard, M. *Differential Dataflow.* CIDR, 2013. — [PDF](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf)
- **[SOTA]** Koch, C., Ahmad, Y., Kennedy, O., Nikolic, M., Nötzli, A., Lupei, D., Shaikhha, A. *DBToaster: Higher-Order Delta Processing for Dynamic, Frequently Fresh Views.* VLDB Journal, 2014. — [DOI](https://doi.org/10.1007/s00778-013-0348-4) — [arXiv](https://arxiv.org/abs/1207.0137)
- **[SOTA]** Berkholz, C., Keppeler, J., Schweikardt, N. *Answering Conjunctive Queries under Updates.* PODS, 2017. — [DOI](https://doi.org/10.1145/3034786.3034789) — [arXiv](https://arxiv.org/abs/1702.06370)
- **[SOTA]** Nikolic, M., Olteanu, D. *Incremental View Maintenance with Triple Lock Factorization Benefits (F-IVM).* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3183758) — [arXiv](https://arxiv.org/abs/1703.07484)
- **[SOTA]** Gjengset, J., Schwarzkopf, M., Behrens, J., et al. *Noria: Dynamic, Partially-Stateful Data-Flow for High-Performance Web Applications.* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/gjengset)
- **[Survey]** Idris, M., Ugarte, M., Vansummeren, S. *The Dynamic Yannakakis Algorithm: Compact and Efficient Query Processing Under Updates.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064027)

## 10. Worked Example

Maintain $V = R \bowtie S$ over $\mathbb{Z}$-relations on join key $k$. Initial state:

$R = \{(k{=}1)\mapsto +1,\ (k{=}2)\mapsto +1\}$,  $S = \{(k{=}1)\mapsto +1\}$.
So $V = \{(k{=}1)\mapsto +1\}$ (one matching row).

Apply a delta: insert $(k{=}2)$ into $S$ and **retract** $(k{=}1)$ from $S$, i.e. $\Delta S = \{(k{=}2)\mapsto +1,\ (k{=}1)\mapsto -1\}$. Using the signed delta rule $\Delta V = R \bowtie \Delta S$ (since $\Delta R = \varnothing$):

- $R(k{=}2){\cdot}\Delta S(k{=}2) = (+1)(+1) = +1$ → emit $(k{=}2)$ with $+1$.
- $R(k{=}1){\cdot}\Delta S(k{=}1) = (+1)(-1) = -1$ → emit $(k{=}1)$ with $-1$ (retraction).

New $V = \{(k{=}2)\mapsto +1\}$, matching a from-scratch re-evaluation. Cost is $O(|\Delta S|)$, proportional to the delta and not to $|V|$ — the hallmark of $\mathbb{Z}$-relation IVM. Note SUM/COUNT retract in $O(1)$ here; had the aggregate been MIN over $k$, the $-1$ on $k{=}1$ could un-mask a previous minimum, forcing the auxiliary order structure noted in section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
