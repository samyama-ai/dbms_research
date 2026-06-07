---
id: 02-query-optimization/order-optimization
title: "Order optimization and interesting orders"
topic: 02-query-optimization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Order optimization and interesting orders

> **Topic:** Query Optimization · **ID:** `02-query-optimization/order-optimization` · **Status:** partially-solved

## 1. Problem Statement
Physical query plans care about *physical properties* of intermediate results, chiefly **sort order** and **grouping**. A sort-merge join, a streaming aggregate, a merge union, or a duplicate-eliminating distinct can avoid an explicit sort if its input already satisfies a required order. The **order-optimization** problem is: during plan enumeration, decide which orders (and groupings) are worth maintaining or producing — the *interesting orders* — and propagate them correctly across operators so the optimizer neither misses a beneficial reuse nor explodes its search space tracking useless orders.

Variants:
- **Decision/feasibility:** does plan $P$ produce an output satisfying a required order $O$ (under functional dependencies and predicates)?
- **Optimization:** find the min-cost plan, where the cost of each operator depends on whether its input order satisfies its requirement (else a sort/partial-sort is inserted).
- **Inference:** given input orders, predicates, and FDs, compute the strongest order/grouping the operator's output is guaranteed to satisfy.

## 2. Mathematical Foundations
Model a tuple stream's order as a sequence of **ordering columns** $O = \langle a_1, a_2, \dots, a_k\rangle$ meaning lexicographic sort. A **grouping** $G = \{a_1,\dots,a_k\}$ is order-agnostic clustering. Orders form a prefix-closed structure: if a stream is sorted on $\langle a,b,c\rangle$ it is also sorted on $\langle a,b\rangle$ and $\langle a\rangle$.

Reasoning is driven by:
- **Functional dependencies (FDs).** If $a \to b$ holds and the stream is sorted on $\langle a\rangle$, it is also "sorted on" $\langle a,b\rangle$ for matching purposes; a constant predicate $a = c$ makes $a$ a *trivial* column removable from any order.
- **Equivalence / order classes.** Selinger's *interesting orders* are the set of orders mentioned in `ORDER BY`, `GROUP BY`, join columns, and `DISTINCT`. A plan is kept in dynamic programming if it is cheapest *or* cheapest-for-some-interesting-order — i.e., DP is over (relation set, interesting order) pairs.
- **Order property automaton.** Neumann–Moerkotte formalize order inference as **functional-dependency-driven reduction**: represent the set of satisfied orders compactly and use an automaton/FSM to test, in near-constant time, whether an operator's output satisfies an interesting order, replacing expensive on-the-fly FD closure.

Key result: combining order *and* grouping properties (groupings can be inferred from orders and from hash operators) and reducing both modulo the active FD set yields sound, complete propagation for the standard operator algebra.

## 3. State of the Art (SOTA)
- **Selinger et al. (System R, SIGMOD 1979)** introduced interesting orders and the DP-over-orders enumeration still used by virtually every cost-based optimizer.
- **Simmen, Shekita, Malkemus (SIGMOD 1996)** gave FD-based order propagation ("Fundamental Techniques for Order Optimization") — the canonical method in DB2/commercial systems.
- **Neumann & Moerkotte (VLDB 2004)** "A Combined Framework for Grouping and Order Optimization" unified orders and groupings with precomputed FSMs; this is the systems SOTA, shipping conceptually in HyPer/Umbra-style optimizers.
- Cascades/Volcano (Graefe) handle this via **required/derived physical properties** and *enforcers* (sort, partition) — the dominant framework in SQL Server, Greenplum/Orca, CockroachDB, Calcite.

## 4. Upper Bound
With the Neumann–Moerkotte FSM precomputation, **per-operator order/grouping satisfaction tests run in $O(1)$** after a one-time build of size polynomial in the number of interesting orders and FDs. The surrounding DP join enumeration is the dominant cost: $O(3^n)$ for $n$ relations in general (or polynomial per connected-subgraph pair via DPccp), multiplied by the number of relevant interesting orders, which is bounded by the query's syntactic order/group/join references. Thus order optimization adds only a polynomial factor (in interesting-order count) over plain join-order DP.

## 5. Lower Bound
Order optimization inherits the hardness of join-order enumeration: **optimal join ordering is NP-hard** for general (cross-product-free, cyclic) query graphs (Ibaraki–Kameda; Cluet–Moerkotte showed NP-hardness even for cost functions with cross products). The order-tracking component itself is *not* the bottleneck — testing/inferring orders modulo FDs is polynomial — so no separate strong lower bound is known for the order machinery; the open hardness is entirely in search-space size. Counting optimal plans is #P-hard in the join-graph dimension.

## 6. The Gap
For the **inference and propagation** subproblem the gap is essentially **closed**: FSM-based methods give optimal (constant-time) satisfaction tests with sound and complete FD reasoning over the standard algebra. The residual openness is *integration*: interesting orders interact multiplicatively with the already-exponential join search, with set operations, with sideways information passing, and with parallel/partitioned plans (where *partitioning* is a third physical property). No framework cleanly co-optimizes order, grouping, **and** data partitioning with provable optimality and tractable enumeration.

## 7. Current Research (as of June 2026)
- Extending order/grouping reasoning to **partitioning and distribution** properties in MPP/columnar engines (Orca, Calcite, DataFusion, Velox) — treating interesting partitionings symmetrically with interesting orders. *(frontier — verify)*
- **Learned enumeration** that prunes interesting-order branches predicted to be useless, trading completeness for speed. *(frontier — verify)*
- Order reasoning for **window functions and recursive/streaming** queries, where order requirements chain across many operators.
- Groups: Moerkotte/Neumann (TUM), the CockroachDB and Apache Calcite optimizer communities, Microsoft (SQL Server/Orca lineage).

## 8. Future Work
- A unified property algebra co-optimizing order + grouping + partitioning with completeness guarantees.
- Cost-aware *partial* sorting and "almost-sorted" inputs (replacement selection, k-sorted streams).
- Robust interaction with learned cardinality/cost so that order choices remain beneficial under estimation error.

## 9. Key References
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Simmen, Shekita, Malkemus. *Fundamental Techniques for Order Optimization.* SIGMOD, 1996. — [DOI](https://doi.org/10.1145/233269.233320)
- **[SOTA]** Neumann, Moerkotte. *A Combined Framework for Grouping and Order Optimization.* VLDB, 2004. — [DBLP](https://dblp.org/rec/conf/vldb/NeumannM04.html)
- **[Foundational]** Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bulletin, 1995. — [DBLP](https://dblp.org/rec/journals/debu/Graefe95a.html)
- **[Survey]** Moerkotte. *Building Query Compilers* (manuscript), chapters on order and grouping optimization. *(unverified)*

## 10. Worked Example

Consider `SELECT ... FROM R JOIN S ON R.a = S.a WHERE R.a = R.b ORDER BY R.b`, with index `R(a)` giving a scan already sorted on $\langle a\rangle$.

Interesting orders are collected from the query: the join key $\langle a\rangle$ (enables sort-merge join) and the `ORDER BY` key $\langle b\rangle$. The FD set includes the predicate-induced equivalence $a = b$ (so $a\to b$ and $b\to a$).

Trace: the `R(a)` scan satisfies $\langle a\rangle$. The sort-merge join on $a$ needs $\langle a\rangle$ on both inputs — $R$ already qualifies, saving one sort. The join output is still ordered on $\langle a\rangle$. Now the `ORDER BY b`: naively this requires a sort. But the FSM, reducing modulo $a = b$, rewrites $\langle a\rangle \equiv \langle b\rangle$, so the stream already satisfies $\langle b\rangle$ — **the final sort is eliminated**.

Without FD reasoning the optimizer inserts a needless sort of cost $O(n\log n)$; with it, the plan costs only the merge join. The satisfaction test itself is $O(1)$ via the precomputed automaton.

---
*Part of the [DBMS Research catalog](../../README.md).*
