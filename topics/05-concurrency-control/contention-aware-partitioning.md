---
id: 05-concurrency-control/contention-aware-partitioning
title: "Contention-Aware Data Partitioning"
topic: 05-concurrency-control
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Contention-Aware Data Partitioning

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/contention-aware-partitioning` · **Status:** open

## 1. Problem Statement

In a partitioned (sharded) OLTP system, each transaction that touches a single partition can commit with cheap local concurrency control, while a **cross-partition** ("distributed") transaction must pay coordination cost (2PC, distributed locking, or deterministic global ordering). The **Contention-Aware Data Partitioning** problem asks: given a workload — a set of transactions, the data items each accesses, access frequencies, and a *contention model* (how often concurrent accesses conflict) — **partition the data across $k$ nodes to minimize coordination cost**, i.e., minimize the (weighted) number of cross-partition transactions and/or the contention-induced abort/lock-wait cost, subject to balance constraints.

Variants:
- **Decision/Optimization:** minimize cross-partition transaction weight subject to load-balance (a constrained graph/hypergraph partitioning problem).
- **Contention-aware:** weight edges not merely by co-access but by *conflict probability* under the CC protocol (lock contention, abort rates).
- **Dynamic/online:** re-partition as the workload drifts, amortizing migration cost.

Status **open**: the static objective is NP-hard graph partitioning; the contention-modeled and dynamic versions lack approximation guarantees.

## 2. Mathematical Foundations

Model the workload as a **hypergraph** $G=(V,E)$: vertices $V$ are data items (or tuple groups), and each transaction $t$ contributes a hyperedge $e_t$ over the items it accesses, with weight $w_t$ (frequency × conflict factor). A $k$-partition $\Pi=\{P_1,\dots,P_k\}$ of $V$ has cost
$$
\mathrm{cut}(\Pi) = \sum_{t : e_t \text{ spans } >1 \text{ part}} w_t ,
$$
the weight of cross-partition transactions, minimized subject to balance $|P_i| \le (1+\varepsilon)\,|V|/k$. This is **balanced (hyper)graph partitioning** — NP-hard, and even the minimum-bisection special case has no PTAS (it is APX-hard / believed to require polylog approximation).

A **contention model** refines edge weights: under 2PL the expected lock-wait/abort cost grows superlinearly in concurrent conflicting access rate $\rho$ (e.g., classic results show throughput collapse near a critical multiprogramming level $\propto 1/\sqrt{\text{conflict prob}}$, Gray et al. / Thomasian). The objective then becomes minimizing *expected coordination + contention cost*, a non-linear function of the partition, no longer a simple cut — making it harder than standard partitioning. Submodular structure is sometimes exploitable: coverage-style coordination objectives can be submodular, enabling $(1-1/e)$ greedy bounds, but contention non-linearities generally break submodularity.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **Schism** (Curino, Jones, Zhang, Madden, VLDB 2010) builds a graph of tuple co-accesses and applies **METIS** graph partitioning + decision-tree range extraction to minimize distributed transactions — the canonical contention/co-access partitioner. **Horticulture / Houdini** (Pavlo, Curino, Zdonik, SIGMOD 2012) does automatic partitioning for H-Store via large-neighborhood search. **E-Store** (Taft et al., VLDB 2014) and **Clay** (Serafini et al., VLDB 2016) do *online, contention/skew-aware* repartitioning and hot-tuple migration. **Calvin/deterministic** systems sidestep cross-partition locking via global ordering rather than partitioning quality.

**Theory-SOTA.** Balanced graph/hypergraph partitioning theory: best general approximation for minimum balanced cut is $O(\sqrt{\log n})$ (Arora-Rao-Vazirani sparsest cut, 2009) feeding balanced-separator algorithms; hypergraph partitioning is solved heuristically (KaHyPar, hMETIS) without tight guarantees.

## 4. Upper Bound

For the static balanced-cut objective, the **Arora–Rao–Vazirani** $O(\sqrt{\log n})$-approximation for sparsest cut yields $O(\sqrt{\log n})$-pseudo-approximate balanced separators (bicriteria), the best known general guarantee in the **polynomial-time** model. In practice, multilevel partitioners (METIS/KaHyPar) achieve near-optimal cuts on real workloads in near-linear time, and Schism-style pipelines reduce distributed-transaction fraction by large factors. For the *contention-weighted* objective there is no proven approximation; greedy/local-search heuristics (Horticulture, Clay) are the upper-bound state of practice.

## 5. Lower Bound

**Minimum bisection** and balanced $k$-partitioning are **NP-hard**, and minimum bisection is hard to approximate within any constant under standard assumptions (no PTAS; the best hardness/approximation gap remains a notorious open problem, with only polylogarithmic approximations known). Thus optimal contention-aware partitioning is NP-hard even in the linear-cut special case. The **dynamic** variant inherits this hardness plus online migration-cost lower bounds (no online algorithm can match the clairvoyant optimum without paying migration; competitive lower bounds follow from metrical-task-system arguments). For the contention-modeled non-linear objective, no approximation lower bound is known — the hardness landscape itself is open.

## 6. The Gap

Genuinely **open**. (1) The static cut problem is NP-hard with a large theory gap (constant-factor approximation for min-bisection is unresolved), but heuristics work well empirically. (2) The *contention-aware non-linear* objective has **no approximation algorithm with guarantees** and no matching hardness — we don't even know whether it admits a constant-factor or only polylog approximation. (3) The *dynamic/online* version lacks competitive-ratio results balancing partition quality against migration cost. Closing the gap requires either a principled approximation for the contention-weighted objective or a hardness result, plus an online theory of repartitioning.

## 7. Current Research (as of June 2026)

Directions: (i) **learned/ML-guided partitioners** predicting access patterns and conflict probabilities to set edge weights *(frontier — verify)*; (ii) contention-model integration — using runtime abort/lock-wait telemetry to drive repartitioning (Clay/E-Store lineage); (iii) **deterministic and partition-aware execution** reducing the *cost* of cross-partition transactions so partition quality matters less (Aria, Calvin — Abadi, Thomson); (iv) elastic cloud repartitioning with migration-cost-aware planning. Groups: MIT (Madden, Curino now industry), CMU-DB (Pavlo — Horticulture/H-Store lineage), EPFL/Brown (Serafini, Zdonik — Clay/E-Store), and graph-partitioning theory groups (KaHyPar at KIT). HTAP and serverless OLTP elasticity push the dynamic frontier.

## 8. Future Work

- Approximation algorithms (or hardness) for the contention-weighted, non-linear coordination objective.
- Online repartitioning with provable competitive ratio against migration + coordination cost.
- Tighter integration of CC-protocol contention models (2PL vs. OCC vs. deterministic) into the partition objective.
- Learned cost models with guarantees, and co-optimization of partitioning with replica placement and routing.

## 9. Key References

- **[SOTA]** C. Curino, E. Jones, Y. Zhang, S. Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)
- **[SOTA]** A. Pavlo, C. Curino, S. Zdonik. *Skew-Aware Automatic Database Partitioning in Shared-Nothing, Parallel OLTP Systems (Horticulture).* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213844)
- **[SOTA]** M. Serafini, R. Taft, A. Elmore, A. Pavlo, A. Aboulnaga, M. Stonebraker. *Clay: Fine-Grained Adaptive Partitioning for General Database Schemas.* VLDB, 2016. — [DOI](https://doi.org/10.14778/3025111.3025125)
- **[SOTA]** R. Taft et al. *E-Store: Fine-Grained Elastic Partitioning for Distributed Transaction Processing.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735514)
- **[Foundational]** S. Arora, S. Rao, U. Vazirani. *Expander Flows, Geometric Embeddings and Graph Partitioning.* Journal of the ACM, 2009. — [DOI](https://doi.org/10.1145/1502793.1502794)
- **[Foundational]** J. Gray, P. Homan, R. Obermarck, H. Korth. *A Straw Man Analysis of the Probability of Waiting and Deadlock in a Database System.* IBM RJ, 1981. — [DBLP search](https://dblp.org/search?q=Straw+Man+Analysis+Probability+Waiting+Deadlock+Database)

## 10. Worked Example

Six data items $V=\{a,b,c,d,e,f\}$, $k=2$ nodes, balance cap $3$ items each. Four transaction hyperedges (weight = frequency):

- $t_1=\{a,b\}, w{=}10$; $t_2=\{b,c\}, w{=}8$; $t_3=\{d,e\}, w{=}9$; $t_4=\{e,f\}, w{=}7$; plus one cross link $t_5=\{c,d\}, w{=}2$.

Consider the partition $P_1=\{a,b,c\}$, $P_2=\{d,e,f\}$. Each part has 3 items (balance satisfied). Which hyperedges are *cut* (span both parts)? Only $t_5=\{c,d\}$ crosses, so
$$\mathrm{cut}(\Pi)=\sum_{t\text{ cut}} w_t = w_{t_5}=2.$$
$t_1,t_2$ live wholly in $P_1$; $t_3,t_4$ wholly in $P_2$ — they run as cheap single-partition transactions. The naive split $\{a,b,d\},\{c,e,f\}$ would instead cut $t_2,t_3,t_5$ for cost $8{+}9{+}2=19$ — nearly $10\times$ worse. This is exactly what Schism's METIS step finds: cluster co-accessed tuples to push the few cross-partition (2PC) transactions to the lowest-weight edge. The minimization is NP-hard in general (section 5), but the structure here makes the optimum obvious.

---
*Part of the [DBMS Research catalog](../../README.md).*
