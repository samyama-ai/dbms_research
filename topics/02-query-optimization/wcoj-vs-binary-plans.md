# Worst-case-optimal join order vs. binary plans

> **Topic:** Query Optimization · **ID:** `02-query-optimization/wcoj-vs-binary-plans` · **Status:** partially-solved

## 1. Problem Statement

**Worst-case-optimal joins (WCOJ)** — e.g. NPRR, LeapFrog Triejoin, Generic Join — evaluate a
multiway join in time $\tilde O(\mathrm{AGM}(Q))$, matching the worst-case output bound, by
processing **all attributes at once** via variable orderings rather than joining two relations at a
time. **Classical optimizers** instead build **binary** join trees and choose an order with
cost-based DP. The two paradigms have *incompatible* notions of "order" (an attribute/variable
elimination order vs. a relation join order) and *different* cost models (AGM/worst-case vs.
expected $C_{out}$).

The problem: **build a single optimizer that chooses, per query and per data instance, the best
hybrid of multiway WCOJ subplans and binary-join subplans, and orders both optimally under one cost
model.** Partially solved: hybrid systems exist and theory connects the two via tree decompositions,
but a unified, instance-optimal cost-based search is not settled.

## 2. Mathematical Foundations

For a join query $Q$ with relations $R_e$, the **AGM bound** is
$|Q| \le \prod_{e} |R_e|^{x_e}$ where $x$ is an optimal fractional edge cover of the hypergraph; the
bound is tight. WCOJ algorithms run in $\tilde O(\prod_e |R_e|^{x_e})$, beating binary plans that
can incur intermediate results asymptotically larger than the final output (the classic triangle
query: binary plans need $\Theta(N^2)$, WCOJ needs $O(N^{3/2})$).

Beyond worst case, **fractional hypertree width** $\mathrm{fhw}$ and **submodular width**
$\mathrm{subw}$ (Marx) govern runtime: PANDA achieves $\tilde O(N^{\mathrm{subw}})$, the
finest-grained known. Binary plans correspond to width-1 / acyclic eliminations (Yannakakis); WCOJ +
tree decomposition generalizes this. The unification problem is to **cost** a mixed elimination order
where some bags are evaluated multiway and others by binary joins.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Generic Join (Ngo–Ré–Rudra, PODS/JACM 2018), **PANDA** (Abo Khamis–Ngo–Suciu,
  $\mathrm{subw}$ bound), and the GHD/fhw framework unify cyclic and acyclic evaluation.
- **Systems-SOTA:** EmptyHeaded (Aberger et al., SIGMOD 2017) and **Umbra/DuckDB** integrate WCOJ for
  cyclic subqueries while keeping binary hash joins for acyclic parts; **Graphflow/Kùzu** use WCOJ +
  cost-based binary planning for graph patterns; LogicBlob/RelationalAI cost hybrid plans. Freitag et
  al. (TUM, VLDB 2020) showed adaptive, cost-based selection between WCOJ and binary joins inside one
  optimizer — the closest to a unified solution.

## 4. Upper Bound

- WCOJ: $\tilde O(\mathrm{AGM}(Q))$ time (Generic Join), RAM model; $\tilde O(N^{\mathrm{fhw}})$ with
  a fixed GHD, $\tilde O(N^{\mathrm{subw}})$ via PANDA.
- Hybrid plans (Freitag et al.): cost-based selection achieves the better of binary $C_{out}$ and
  WCOJ on a per-subquery basis, empirically; no closed-form competitive ratio across all instances.

## 5. Lower Bound

- **AGM is tight:** there exist instances achieving $\prod_e |R_e|^{x_e}$, so no join algorithm beats
  it in the worst case (information-theoretic / output-size argument).
- For **purely binary** plans, the triangle and longer-cycle queries force $\Omega(N^{2})$ vs.
  $O(N^{3/2})$ optimal — a provable separation establishing binary plans are *not* worst-case optimal
  (Atserias–Grohe–Marx; Ngo et al.).
- Conditional fine-grained lower bounds (e.g. triangle detection / BMM-hardness) constrain how fast
  cyclic joins can be in the combined model.

## 6. The Gap

What remains open is a **single cost model and search algorithm** that is provably near-optimal over
*both* the binary and multiway plan spaces for arbitrary instances — i.e. instance-optimal hybrid
planning. Current systems make the WCOJ-vs-binary choice heuristically or per-component; a unified DP
with sound cost-based pruning over mixed eliminations, plus its complexity, is not settled. Hence
"partially-solved."

## 7. Current Research (as of June 2026)

- Cost-based hybrid planners that treat variable orderings and join orderings in one DP (TUM,
  RelationalAI, Kùzu). *(frontier — verify)*
- Beyond-worst-case / instance-optimal joins (Minesweeper, Tetris) reconciled with cost-based
  enumeration. *(frontier — verify)*
- Cardinality estimation specialized for WCOJ subplans (degree/heavy-light statistics).

## 8. Future Work

- A unified cost model bridging AGM/worst-case and expected-cost $C_{out}$.
- Provable competitive ratios for hybrid plans vs. the best mixed plan.
- WCOJ-aware cardinality estimators and adaptive switching at runtime.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008 / SICOMP, 2013.
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018.
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017.
- **[SOTA]** Aberger et al. *EmptyHeaded: A Relational Engine for Graph Processing.* SIGMOD, 2017.
- **[SOTA]** Freitag, Bandle, Schmidt, Kemper, Neumann. *Adopting Worst-Case Optimal Joins in Relational Database Systems.* VLDB, 2020.
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
