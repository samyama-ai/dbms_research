---
id: 32-multimodel-document-db/polystore-data-placement
title: "Optimal data placement across polystore tiers"
topic: 32-multimodel-document-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal data placement across polystore tiers

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/polystore-data-placement` · **Status:** open

## 1. Problem Statement
A **polystore** (à la BigDAWG) federates specialized engines — a relational store, a document store, a graph engine, a column/array store, a search index — each best at certain operations. Given a set of datasets/fragments and a (predicted) query workload, **assign each fragment to one or more stores** so as to **minimize total query (and migration/replication) cost**, subject to each store's **capability constraints** (it can only run certain operators on certain data) and capacity/budget limits.

Variants:
- **Decision (feasibility):** is there a placement under which every query in $W$ is executable given store capabilities and cross-store data-movement rules?
- **Optimization:** minimize $\sum_{q\in W} f_q \cdot \mathrm{cost}(q \mid \text{placement}) + \mathrm{cost}_{\text{migration}}$ over placements — the core problem.
- **Replicated placement:** fragments may be copied to multiple stores (read benefit vs. storage + consistency cost).
- **Dynamic/online:** workload drifts; re-place fragments over time paying migration cost (regret minimization).

The open part is doing this *jointly with capability constraints and cross-store query cost*, not as independent per-fragment choices, because the cost of a query depends on where *all* its inputs land (a join is cheap only if both sides are co-located in a store that can join them).

## 2. Mathematical Foundations
- The problem is a **constrained combinatorial assignment**. Stripped of interactions it is a **Generalized Assignment Problem** (fragments→stores with capacities), already NP-hard. With query-level coupling it becomes a **quadratic / hypergraph partitioning** problem: model each query as a hyperedge over the fragments it touches; placing co-accessed fragments in the same capable store reduces cut/cross-store cost — i.e., **min-cost hypergraph partitioning under capability and capacity constraints**.
- **Capability constraints** are modeled as a bipartite feasibility relation $\mathrm{can}(s, \text{op}, \text{frag})$; a placement is feasible iff every query has an executable plan over placed fragments (links to *capability-based pushdown*).
- **Cost** combines local execution cost (store-specific) and **data-movement cost** (cross-store shipping), making the objective a sum of unary placement costs plus pairwise/hyperedge movement costs — the structure of **facility-location / uncapacitated-facility-location** and **graph-partitioning** problems, which carry LP-rounding and local-search approximation theory.
- **Online** re-placement maps to **MTS / online facility location**; replication-with-consistency invokes the CAP/PACELC tradeoff as a hard constraint on multi-store copies.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** approximation algorithms for facility location (Charikar–Guha; Jain–Vazirani primal-dual), generalized assignment ($(1-1/e)$ / 2-approx via LP rounding, Shmoys–Tardos), and balanced graph/hypergraph partitioning (METIS, recursive bisection) provide the building blocks; data-placement-as-partitioning has classic results (Schism, Curino et al., for OLTP partitioning to minimize distributed transactions).
- **Systems-SOTA:** **BigDAWG** polystore (Duggan, Elmore, Stonebraker et al., 2015) with "islands" and CAST/migration; **Myria**, **Musketeer**, **Polypheny-DB** (multi-model with adaptive placement), **Estocada** (view-based polystore placement, Bugiotti–Bursztyn–Deutsch et al.), and cloud "data lakehouse + specialized index" tiering. Placement in these is largely heuristic/cost-model-driven; none gives an approximation guarantee under joint capability constraints.

## 4. Upper Bound
For the **uncapacitated** version with metric movement costs, the placement reduces to facility-location-style objectives admitting **constant-factor approximations** (e.g., $\approx 1.488$ for metric facility location, Li 2013; primal-dual $3$-approx, Jain–Vazirani) in the RAM model with a cost oracle. **Generalized assignment** (with capacities) has a **2-approximation / $(1-1/e)$** via LP rounding (Shmoys–Tardos). For the **hypergraph-partitioning** formulation, recursive multilevel partitioning gives good empirical cuts but only $O(\log n)$-type approximation guarantees for balanced partitioning (Räcke-style). These bounds hold for restricted cost structures (metric, submodular); the general capability-constrained polystore objective has no known constant-factor algorithm.

## 5. Lower Bound
- The optimization problem is **NP-hard** (it contains generalized assignment, uncapacitated facility location, and balanced graph partitioning, all NP-hard).
- **Inapproximability:** general (non-metric) facility location is hard to approximate better than $\Omega(\log n)$ (set-cover reduction); balanced graph partitioning has **no constant-factor approximation** unless P=NP (and is hard even to approximate within any constant under common assumptions). So the *general* polystore-placement objective inherits super-constant inapproximability.
- **Replication + consistency** adds a hard **CAP/PACELC** impossibility: a fragment replicated across stores cannot be simultaneously strongly consistent and available under partition, constraining feasible replicated placements.

## 6. The Gap
Individual relaxations (metric facility location, generalized assignment) are **closed** with tight constant/log approximations. The genuinely **open** problem is the *coupled, capability-constrained, multi-model* version: (1) no algorithm with a provable guarantee handles query-level hyperedge coupling **and** per-store capability feasibility **and** migration cost together; (2) the *online* drift-aware version lacks regret bounds; (3) replicated placement under consistency constraints is unsolved with guarantees. Closing the gap means either an approximation algorithm for the joint objective on realistic cost structures, or a matching hardness showing only heuristics are possible — plus a cost model trustworthy enough that the optimization is meaningful.

## 7. Current Research (as of June 2026)
- Adaptive/learned placement in multi-model and lakehouse systems (Polypheny-DB adaptive placement, learned tiering between hot specialized stores and cold object storage) is active *(frontier — verify which 2025–2026 systems offer guaranteed-near-optimal joint placement)*.
- View-based and materialization-aware placement (Estocada lineage) blends placement with materialized-view selection.
- Workload-prediction-driven online re-placement and RL-based fragment migration are emerging SIGMOD/VLDB directions.

## 8. Future Work
- An approximation algorithm (or hardness) for **joint capability-constrained, coupling-aware** placement with migration cost.
- **Online** placement with provable regret under workload-drift and bounded migration budgets.
- Replicated placement that co-optimizes read cost against consistency/freshness (formal CAP/PACELC-aware objective).
- Tight integration of placement with cross-store query optimization and pushdown-capability negotiation.

## 9. Key References
- **[Foundational]** D. B. Shmoys, É. Tardos. *An Approximation Algorithm for the Generalized Assignment Problem.* Mathematical Programming, 1993. — [DOI](https://doi.org/10.1007/BF01585178)
- **[Foundational]** K. Jain, V. V. Vazirani. *Approximation Algorithms for Metric Facility Location and k-Median Problems (Primal-Dual).* JACM, 2001. — [DOI](https://doi.org/10.1145/375827.375845)
- **[Foundational]** C. Curino, E. Jones, Y. Zhang, S. Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)
- **[SOTA]** J. Duggan, A. J. Elmore, M. Stonebraker, et al. *The BigDAWG Polystore System.* SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814713)
- **[SOTA]** F. Bugiotti, D. Bursztyn, A. Deutsch, I. Ileana, I. Manolescu. *Invisible Glue: Scalable Self-Tuning Multi-Stores (Estocada).* CIDR, 2015. — [PDF](https://www.cidrdb.org/cidr2015/Papers/CIDR15_Paper7.pdf)
- **[Foundational]** S. Li. *A 1.488 Approximation Algorithm for the Uncapacitated Facility Location Problem.* Information and Computation, 2013. — [DOI](https://doi.org/10.1016/j.ic.2012.01.007)
- **[Survey]** R. Tan, R. Chirkova, V. Gadepally, T. Mattson. *Enabling Query Processing across Heterogeneous Data Models: A Survey (Polystore).* IEEE Big Data, 2017. — [DOI](https://doi.org/10.1109/BigData.2017.8258302)

## 10. Worked Example

Three fragments $\{R, D, G\}$ and two stores: a relational store $s_1$ (can join $R,D$) and a graph store $s_2$ (can traverse $G$; cannot join $R,D$). Workload: $q_1$ joins $R\bowtie D$ ($f=10$); $q_2$ traverses $G$ then joins to $R$ ($f=3$). Cross-store shipping costs 5 per fragment moved per query; local ops are free.

Evaluate the candidate placement $L = \{R\to s_1, D\to s_1, G\to s_2\}$:
- $q_1$: $R,D$ co-located in $s_1$, which can join them — cost $0$. Contribution $10 \times 0 = 0$.
- $q_2$: traverse $G$ in $s_2$, then ship the result to $s_1$ to join with $R$ — one cross-store hop, cost $5$. Contribution $3 \times 5 = 15$.
- Total $= 15$.

Compare $L' = \{R\to s_2,\dots\}$: now $q_1$ must ship $R$ from $s_2$ to $s_1$ (cost $10\times5=50$) while $q_2$ improves to $0$ — total $50$. So $L$ wins.

This is the hyperedge view: $q_1$ is a hyperedge over $\{R,D\}$, $q_2$ over $\{G,R\}$; minimizing weighted cross-store cut while respecting "can $s_1$ join? can $s_2$ traverse?" capability constraints is the min-cost capability-constrained hypergraph partition of section 2 — NP-hard once the graph grows.

---
*Part of the [DBMS Research catalog](../../README.md).*
