# Optimal join ordering under cross products

> **Topic:** Query Optimization · **ID:** `02-query-optimization/join-order-cross-products` · **Status:** open

## 1. Problem Statement

Standard join enumerators forbid **cross products** (Cartesian joins between relations with no
connecting predicate) because they blow up intermediate cardinality. Yet for some queries the
*globally optimal* plan must introduce a cross product — e.g. when two tiny dimension tables should
be combined before joining a huge fact table. The problem:

1. **Characterize** the query/cardinality conditions under which an optimal plan *requires* a cross
   product (i.e. every cross-product-free plan is strictly suboptimal).
2. **Quantify** the optimality penalty of disallowing cross products (the "no-CP regret").
3. **Settle the complexity** of optimal ordering once cross products are admitted, across tree
   shapes and cost functions.

Decision / optimization / counting variants mirror the general join-ordering problem, now over the
larger search space that allows any pair of (sub)plans to be joined.

## 2. Mathematical Foundations

Admitting cross products enlarges the search space from "connected subgraph pairs" (csg-cmp-pairs of
$G$) to **all** subset pairs: bushy enumeration grows from the connected-subgraph count to the full
$3^n$ partition recurrence. Formally, without CPs the DP iterates over connected subgraphs $S$ with
$|csg(G)|$ entries; with CPs it iterates over all $2^n$ subsets, and the join may bridge
disconnected components.

A cross product is beneficial when, under $C_{out}$, $|R \times S| = |R|\,|S|$ is smaller than the
cardinality of the cheapest alternative subtree that defers them — typically when $|R|,|S|$ are both
small relative to downstream selectivities. The **rank/ASI** machinery breaks because cross products
violate the adjacency assumptions that make IKKBZ exact.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Cluet & Moerkotte (ICDT 1995) proved that left-deep optimization *with* cross
  products is **NP-hard**, even when the cross-product-free version is polynomial — establishing that
  the penalty for ignoring CPs and the cost of admitting them are both real.
- **Systems-SOTA:** Most optimizers (PostgreSQL, DB2, SQL Server) enumerate cross-product-free plans
  by default and only consider CPs heuristically (e.g. for star schemas, "star-join" detection, or
  when a relation is unconnected). Vectorwise/DuckDB include CP-aware special cases for small
  dimension tables.

## 4. Upper Bound

- Exact CP-admitting bushy enumeration: DP in $O(3^n)$ time, $O(2^n)$ space (full-subset recurrence),
  RAM model.
- For **star queries** with a single fact table, optimal CP placement among $d$ dimensions reduces to
  a tractable subproblem solvable in polynomial time when dimension sizes and selectivities are fixed
  — exploited as the practical "star transformation."

## 5. Lower Bound

- **NP-hardness** of left-deep join ordering with cross products (Cluet–Moerkotte 1995), via
  reduction encoding a hard sequencing problem; the cross product is what destroys the ASI rank
  ordering that otherwise yields polynomial solvability.
- No tight fine-grained (SETH/$3$SUM) lower bound is known specifically isolating the cross-product
  contribution — open.

## 6. The Gap

We know CPs can be *necessary* for optimality and that admitting them makes the problem NP-hard, but
we lack: (a) a clean **structural characterization** of CP-necessary instances, (b) **approximation
guarantees** for CP-restricted plans (how far from optimal can forbidding CPs be?), and (c)
parameterized-tractability results (e.g. "optimal with $\le k$ cross products" FPT in $k$). These are
genuinely open.

## 7. Current Research (as of June 2026)

- FPT formulations parameterized by the number of admitted cross products or by the number of
  small/"snowflake" dimension tables. *(frontier — verify)*
- Learned optimizers implicitly rediscovering beneficial CPs from execution feedback (TUM, MIT).
- Integration with worst-case-optimal join reasoning where disconnected joins arise naturally.

## 8. Future Work

- Provable bounds on no-CP regret as a function of cardinality skew.
- A complexity dichotomy for CP-admitting ordering over graph and cost classes.
- Practical pruning that admits only *provably useful* cross products.

## 9. Key References

- **[Foundational]** Cluet, Moerkotte. *On the Complexity of Generating Optimal Left-Deep Processing Trees with Cross Products.* ICDT, 1995.
- **[Foundational]** Ono, Lohman. *Measuring the Complexity of Join Enumeration in Query Optimization.* VLDB, 1990.
- **[SOTA]** Moerkotte, Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm (DPccp).* VLDB, 2006.
- **[Foundational]** Graefe, DeWitt. *The EXODUS Optimizer Generator.* SIGMOD, 1987.
- **[Survey]** Moerkotte. *Building Query Compilers.* (draft monograph), ongoing.

---
*Part of the [DBMS Research catalog](../../README.md).*
