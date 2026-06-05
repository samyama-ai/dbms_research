# Partition Scheme Selection Under Workloads

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/workload-aware-partitioning` · **Status:** open

## 1. Problem Statement
Given a database schema, a set of nodes, and a **query workload** $W$ (with frequencies, possibly drifting over time), choose a **data-partitioning layout** — hash/range/replication choices and partitioning keys per table, plus optional co-location and replication — that **minimizes expected cross-node communication** (shuffle/repartition traffic) to answer the workload, subject to storage and balance constraints.

Variants:
- **Static optimization:** fixed $W$; pick a single layout minimizing $\sum_{q} f_q \cdot \text{traffic}(q)$.
- **Decision:** Is there a layout with expected traffic $\le B$ and per-node storage $\le S$?
- **Online / drifting workload:** minimize traffic plus repartitioning (migration) cost as $W$ evolves — a competitive-analysis / regret problem.
- **Replication-aware:** allow tables/columns to be replicated to remove shuffles at storage cost.

## 2. Mathematical Foundations
Model the workload as a hypergraph/graph: vertices = tuples or table fragments, hyperedges = co-accessed tuples within a query. **Minimizing cross-partition edges** under balance is **balanced graph/hypergraph partitioning** — NP-hard, with the canonical **balanced min-cut** and **min $k$-cut** formulations. Schober/quotient-cut approximations rely on **spectral** and **multicommodity-flow / LP** relaxations (e.g., $O(\sqrt{\log n})$ for sparsest cut, Arora–Rao–Vazirani). For query-driven layout, the objective couples per-query shuffle cost (determined by whether join keys are co-partitioned) with frequency weights $f_q$. The online variant invokes **metrical task systems / competitive ratio** for layout migration. **Submodularity** of coverage/replication benefit enables greedy $(1-1/e)$ guarantees for replication subproblems.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Balanced (hyper)graph partitioning hardness and approximations (Andreev–Räcke; ARV sparsest cut). Workload-driven formulations reduce to weighted hypergraph min-cut with no constant-factor guarantee in general.
- **Systems-SOTA:** **Schism** (Curino et al., VLDB 2010) — graph-partitioning on a workload trace via METIS. **SWORD**, **Clay** (incremental/online repartitioning, Serafini et al., VLDB 2016), **AdaptDB**, and **Amazon Redshift / Snowflake auto-clustering**. **Learned** layout selection (e.g., reinforcement-learning partition advisors) and Microsoft's **AutoAdmin**-lineage physical-design tools.

## 4. Upper Bound
No general constant-factor approximation is known for the full workload-layout objective. For the reduced **balanced min-cut** core, $O(\sqrt{\log n})$ (sparsest cut, ARV) and $O(\log n)$-type bounds for balanced $k$-cut apply; METIS-style multilevel heuristics dominate practice. Replication subproblems with submodular benefit admit greedy $(1-1/e)$ approximations. Online migration: constant-competitive only under restricted cost models.

## 5. Lower Bound
**NP-hardness** of balanced min-cut / min-bisection (Garey–Johnson). Min-bisection is hard to approximate within any constant under standard assumptions, and **Unique-Games-hardness** results constrain sparsest/balanced cut approximability. The workload-layout problem inherits this hardness and adds the combinatorial choice of partition keys, making it at least as hard. Online layout selection has lower bounds from **metrical task system** competitive-ratio theory.

## 6. The Gap
There is a large gap between **NP-hardness / inapproximability** of the exact objective and the **purely heuristic** (METIS, RL) systems that work well empirically but offer no guarantees. No principled approximation algorithm captures the joint (key choice + replication + balance + online migration) problem. **Open**: a guaranteed-approximation, workload-aware layout selector, and tight hardness for the combined objective.

## 7. Current Research (as of June 2026)
Learned/RL partition advisors and **LLM-assisted physical design** are active in industry and academia *(frontier — verify)*. Online/adaptive repartitioning under drift (extending Clay/AdaptDB) with bounded migration is a live theory-systems topic *(frontier — verify)*. Groups: Curino/Madden lineage (MIT/Microsoft Gray Systems Lab), Pavlo (CMU, self-driving DBs / OtterTune), Idreos (Harvard, data layouts / "data calculator").

## 8. Future Work
- Approximation algorithms with provable guarantees for the joint key-selection + replication objective.
- Robust layouts minimizing worst-case regret over uncertain/drifting workloads.
- Tight inapproximability results for the combined problem; principled migration-cost-aware online schemes.

## 9. Key References
- **[Foundational]** Curino, Jones, Zhang, Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010.
- **[SOTA]** Serafini, Taft, Elmore, Pavlo, Aboulnaga, Stonebraker. *Clay: Fine-Grained Adaptive Partitioning.* VLDB, 2016.
- **[Foundational]** Arora, Rao, Vazirani. *Expander Flows, Geometric Embeddings and Graph Partitioning.* JACM, 2009.
- **[Foundational]** Andreev, Räcke. *Balanced Graph Partitioning.* SPAA, 2004.
- **[Survey]** Chaudhuri, Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
