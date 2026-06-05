# Hybrid Row/Column In-Memory Layout

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/hybrid-row-column-layout` · **Status:** open

## 1. Problem Statement

An HTAP in-memory store partitions a table into fragments (e.g., row groups, tiles,
delta/main partitions). For each fragment $i$ we must choose a **physical layout**
$\ell_i \in \{\text{row}, \text{column}, \text{PAX/tile}, \text{hybrid-}k\}$ (and possibly
a compression/encoding) so that the combined cost of a mixed workload — short OLTP point
reads/updates that favor row layout and analytical scans/aggregations that favor column
layout — is minimized. Because workloads drift, the layout must **adapt online**: data
migrates from a write-optimized form (hot, recent) to a read-optimized form (cold,
scanned), the classic *delta→main* lifecycle.

- **Decision variant:** is there a layout assignment with total cost $\le B$?
- **Optimization variant (static):** given a workload distribution, minimize
  $\sum_i \text{cost}(\ell_i, W)$ — a physical-design / layout-selection problem.
- **Online variant:** minimize cost over a workload *sequence* including migration cost,
  i.e., a competitive-analysis problem (when to flip a fragment's layout).

"Solving" means a principled, near-optimal, online per-fragment layout policy with
provable guarantees — currently absent.

## 2. Mathematical Foundations

**Cost model.** A query touching attributes $A \subseteq$ columns over $n$ rows costs,
for column layout, $\sum_{a \in A} n \cdot w_a$ bytes scanned (only referenced columns,
SIMD-friendly, bandwidth-bound), versus row layout $n \cdot \sum_{a} w_a$ (whole tuples,
cache-line at a time) but $O(1)$ to fetch/update one tuple. Let $r$ = fraction of OLTP
ops, $s$ = scan selectivity, $|A|/|cols|$ = projectivity. The crossover where column beats
row depends on projectivity and selectivity; the **layout-selection** problem generalizes
**vertical partitioning**, which is NP-hard.

**Online formulation.** Treat each fragment as a *metrical task system* / *ski-rental*:
keep current layout (pay per-query mismatch) vs. pay migration cost $M_i$ to switch.
Optimal offline is a min-cost layout schedule; online policies are judged by competitive
ratio. Adaptive variants connect to **database cracking** (self-organizing under queries)
and **learned layout** (predicting access patterns).

**Storage-amplification constraint.** Keeping both layouts (full HTAP duplication) costs
$2\times$ memory; the objective often includes a memory budget, making it a *constrained*
optimization (knapsack-like): which fragments earn a second copy.

## 3. State of the Art (SOTA)

**Systems SOTA.** **SAP HANA** uses delta (row/write-optimized) + main (columnar,
compressed) with periodic merge. **HyPer** (TUM) and its successor **Umbra** keep a
unified representation with compiled queries; **Hyrise** (Plattner et al., CIDR 2010) is
the original variable-width hybrid that *automatically* picks row/column per-attribute
from workload traces. **Peloton** (Pavlo et al., SIGMOD 2017) introduced *self-driving*
tile-based layout that morphs between row and column (the FSM/"tile group" model).
**DuckDB**, **SingleStore** (row in-memory + columnar disk), **Oracle Database In-Memory**
(dual-format) are production dual-layout engines. **BTrim / adaptive tiles** continue the
morphing line.

**Theory SOTA.** Vertical-partitioning and layout selection are studied as NP-hard
physical-design problems; no tight approximation or competitive-ratio result is the
accepted standard for the *online HTAP morphing* version.

## 4. Upper Bound

Static layout selection admits ILP/heuristic solutions and, as a constrained
partitioning problem, has bounded-approximation variants for special cost models. For the
online single-fragment ski-rental abstraction, deterministic 2-competitive and randomized
$e/(e-1)\approx 1.58$-competitive policies are known. Systems achieve good *empirical*
results via cost-model-driven greedy morphing (Peloton, Hyrise) but without worst-case
guarantees for the full multi-attribute, multi-fragment, migration-coupled problem.

## 5. Lower Bound

**Vertical partitioning / optimal layout selection is NP-hard** (reduction from
hypergraph partitioning / set-cover-style arguments), so the static optimization variant
is intractable in general. The online variant inherits competitive-ratio lower bounds:
any deterministic policy for the migrate-or-stay decision is $\ge 2$-competitive
(ski-rental lower bound), and adversarial workload sequences can force $\Omega(M)$
migration regret. Joint multi-fragment selection under a memory budget contains a
knapsack, hence weakly NP-hard. No tight bound matching the *adaptive, drift-aware*
objective is established.

## 6. The Gap

We have NP-hardness for static selection and ski-rental bounds for the trivial per-fragment
online decision, but **no algorithm with provable guarantees for the realistic problem**:
many fragments, per-attribute granularity, migration cost, memory budget, *and* drifting
workloads, with the additional complication that the optimal layout interacts with
compression, SIMD, and NUMA placement. Production systems use cost-model heuristics with
no regret bound. Closing the gap needs a model that captures drift + migration and an
online algorithm with a proven competitive ratio (or a hardness result showing none is
possible).

## 7. Current Research (as of June 2026)

Active: **self-driving / learned** layout (CMU-DB Peloton lineage, "NoisePage"), using ML
to forecast access patterns and trigger morphing *(frontier — verify)*; HTAP on
disaggregated/CXL memory where layout interacts with far-memory bandwidth; unified
"tile/zone" formats that avoid full duplication; adaptive layout coupled with **learned
indexes** and compression. Groups: SAP/HPI (Plattner, Hyrise/HANA), TUM (Neumann, Umbra),
CMU-DB (Pavlo), MIT (cracking lineage, Kraska on learned components).

## 8. Future Work

- A competitive-analysis framework for online HTAP layout morphing with migration cost.
- Joint optimization of layout + compression + NUMA placement under a memory budget.
- Drift-aware, regret-bounded policies; benchmarks separating layout from query-engine effects.
- Avoiding $2\times$ duplication while serving both workloads (single morphable format).

## 9. Key References

- **[Foundational]** M. Grund, J. Krüger, H. Plattner, et al. *Hyrise: A Main Memory Hybrid Storage Engine.* VLDB / CIDR, 2010.
- **[SOTA]** J. Arulraj, A. Pavlo, P. Menon. *Bridging the Archipelago between Row-Stores and Column-Stores for Hybrid Workloads (Peloton tiles).* SIGMOD, 2016.
- **[Foundational]** A. Ailamaki, D. DeWitt, M. Hill, M. Skounakis. *Weaving Relations for Cache Performance (PAX).* VLDB, 2001.
- **[SOTA]** V. Sikka, F. Färber, et al. *Efficient Transaction Processing in SAP HANA.* SIGMOD, 2012.
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
