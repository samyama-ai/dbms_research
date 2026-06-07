---
id: 34-schema-design-normalization/polystore-schema-decomposition
title: "Polystore and Multi-Engine Schema Decomposition"
topic: 34-schema-design-normalization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Polystore and Multi-Engine Schema Decomposition

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/polystore-schema-decomposition` · **Status:** open

## 1. Problem Statement
Given a single logical schema $\mathcal{S}$ and a workload $W$ (a distribution over queries and updates), partition or replicate $\mathcal{S}$'s data across a set of heterogeneous storage engines $E = \{e_1,\dots,e_p\}$ — relational, key-value, document, columnar, graph — so that the total cost of executing $W$ (subject to consistency and capacity constraints) is minimized.

- **Optimization variant:** choose an assignment $\phi$ of logical fragments to engines minimizing $\sum_{q\in W} \Pr[q]\cdot \mathrm{cost}(q\mid\phi)$, where cost reflects each engine's access model (point-lookup on KV, traversal on graph, scan on columnar).
- **Decision variant:** given a budget $B$, does an assignment exist with expected cost $\le B$?
- **Replication / counting variants:** allow a fragment to live on several engines (read-cheap, write-expensive); count or enumerate Pareto-optimal placements over (latency, storage, write-amplification).

The difficulty is the cross-product of *normalization choices* (how to decompose into fragments) and *engine choices* (where each fragment lives), with cross-engine joins incurring shipping/transformation cost.

## 2. Mathematical Foundations
Model the logical schema as a hypergraph $H=(V,F)$ where $V$ are attributes and $F$ are candidate fragments (e.g., BCNF/4NF projections, denormalized views). An assignment is $\phi: F \to 2^E$. Query cost over a relational core uses worst-case optimal join theory: an acyclic conjunctive query on fragments respects the **AGM bound** $\prod \rho^*$ (Atserias–Grohe–Marx), so fragmentation that destroys acyclicity inflates intermediate-result size and reconstruction cost.

Lossless-join and dependency preservation constrain decomposition: a decomposition $\{R_1,\dots,R_k\}$ is lossless iff some $R_i$ contains a key of the join (Chase / Rissanen), and we want $\Join_i \pi_{R_i}(R) = R$. Cross-engine reassembly cost is then bounded by intermediate sizes governed by the join tree's width (treewidth / fractional hypertree width).

The placement objective is frequently **submodular** in read benefit but **supermodular** in write/consistency cost, so the combined objective is neither, and the problem generalizes **graph partitioning** and **uncapacitated facility location**. Multi-engine cost models also draw on the I/O / external-memory model (each engine has its own $B$, block size, and access primitive set).

## 3. State of the Art (SOTA)
**Systems-SOTA.** **BigDAWG** (Stonebraker, Mattson et al., 2015–2017) pioneered the *island* abstraction with cross-engine CAST/SCOPE operators. **Myria** (Halperin et al., 2014), **Estocada** (Bugiotti, Manolescu et al., 2015) for view-based access-path selection across stores, **MISO** (LeFevre et al., SIGMOD 2014) tuning HDFS/RDBMS placement, and **Polypheny-DB** (2018–) with automatic data-placement advisors are the canonical multi-store engines. **CloudMdsQL** and **RHEEM/Apache Wayang** (Agrawal et al.) optimize cross-platform plans.

**Theory-SOTA.** There is no tight approximation algorithm for the full problem; the best framing reduces fragment placement to **min-cost partitioning with replication**, solved heuristically (ILP, simulated annealing) per system. Workload-driven vertical/horizontal partitioning (the AutoAdmin/DB2 Design Advisor lineage; Agrawal–Chaudhuri–Narasayya, VLDB 2004) supplies the relational-only special case.

## 4. Upper Bound
For the relational-only fragment-placement special case, workload-aware partitioning is solvable by **ILP** (exponential worst case) or by **LP-rounding heuristics** with no general guarantee. Restricted to vertical partitioning of one relation under a linear cost model, dynamic programming over attribute orders gives **$O(2^n)$** exact (Navathe-style) and polynomial greedy approximations. Cross-engine join reconstruction on an acyclic fragment tree runs in **$O(\mathrm{in} + \mathrm{out})$** via Yannakakis, i.e., the placement that preserves acyclicity admits worst-case-optimal reassembly.

## 5. Lower Bound
The decision variant is **NP-hard**: it contains balanced **graph partitioning** and **uncapacitated facility location** as special cases (reduction from multiway cut by treating cross-engine join edges as cut edges). With replication and consistency constraints, choosing read replicas under a write penalty is **NP-hard** and **APX-hard** by inheritance from facility location. Under distributed-consistency requirements, no placement can simultaneously guarantee strong consistency, availability, and partition tolerance — **CAP** (Gilbert–Lynch, 2002) bounds what any cross-engine transactional layer can promise, independent of placement quality.

## 6. The Gap
The gap is wide and genuinely open. We lack (a) a unified cost model that composes heterogeneous engine primitives with provable accuracy, and (b) any constant-factor approximation for joint decompose-and-place even under simplifying assumptions. Closing it requires either a tractable structural restriction (bounded fractional hypertree width fragments) with an approximation guarantee, or a hardness result showing no $o(\log n)$ approximation exists (likely, given the facility-location embedding).

## 7. Current Research (as of June 2026)
Active directions: (1) **learned cost models** and reinforcement-learning placement advisors that transfer across engines *(frontier — verify)*; (2) HTAP and lakehouse designs (Databricks, Snowflake) that blur row/column placement, reframing decomposition as a storage-format problem; (3) cross-platform query optimization in **Apache Wayang** and successors; (4) verification that cross-engine plans preserve lossless-join/consistency. Groups: Manolescu (Inria), Stonebraker/Tatbul lineage (MIT), Naumann/Polypheny (HPI), Chaudhuri–Narasayya (Microsoft self-tuning).

## 8. Future Work
- Provable approximation for joint normalization + placement under a composable engine-cost algebra.
- Online/elastic re-placement as workload drifts, with bounded migration cost.
- Consistency-aware replication that exposes the CAP trade-off as a tunable knob per fragment.
- Benchmarks with ground-truth optimal placements (see *schema-design-benchmarks*).

## 9. Key References
- **[Foundational]** Stonebraker, M., et al. *The BigDAWG Polystore System.* SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814713) — [DBLP](https://dblp.org/rec/journals/sigmod/DugganESBHKMMMZ15.html)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 / SIAM J. Comput., 2013. — [DOI](https://doi.org/10.1137/110859440) — [arXiv](https://arxiv.org/abs/1711.03860)
- **[SOTA]** LeFevre, J., et al. *MISO: Souping Up Big Data Query Processing with a Multistore System.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588568)
- **[SOTA]** Agrawal, S., Narasayya, V., Yang, B. *Integrating Vertical and Horizontal Partitioning into Automated Physical Database Design.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007609)
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[Survey]** Tan, R., Chirkova, R., et al. *Enabling Query Processing across Heterogeneous Data Models: A Survey.* IEEE Big Data, 2017. — [DOI](https://doi.org/10.1109/BigData.2017.8258302)

## 10. Worked Example

A logical schema has three fragments and two engines: a key-value store $e_{KV}$ (cheap point lookups) and a columnar store $e_{COL}$ (cheap scans/aggregates).

- $F_1 = \text{User}(\text{uid},\text{name})$
- $F_2 = \text{Session}(\text{sid},\text{uid},\text{ts})$
- $F_3 = \text{Event}(\text{sid},\text{type},\text{value})$

Workload $W$: $\Pr=0.7$ point lookup "fetch user by uid" (KV-friendly), $\Pr=0.3$ "average $\text{value}$ over all events" (scan-friendly). Per-query unit costs:

| fragment | on $e_{KV}$ | on $e_{COL}$ |
|----------|-------------|--------------|
| lookup $F_1$ | 1 | 10 |
| scan $F_3$ | 50 | 2 |

Assignment $\phi:\{F_1\mapsto e_{KV},\,F_3\mapsto e_{COL}\}$ gives expected cost $0.7\cdot 1 + 0.3\cdot 2 = 1.3$. The naive all-KV placement costs $0.7\cdot1 + 0.3\cdot50 = 15.7$; all-COL costs $0.7\cdot10 + 0.3\cdot2 = 7.6$. So the heterogeneous split is $\approx 6\times$ better. But the lookup-then-aggregate query joining $F_1\bowtie F_2\bowtie F_3$ now spans both engines: keeping the join tree acyclic lets Yannakakis reassemble in $O(\text{in}+\text{out})$, whereas a fragmentation that broke acyclicity would inflate the intermediate result toward the AGM bound $\prod\rho^*$. Choosing $\phi$ jointly over $2^{|F|}\cdot p$ options is the NP-hard core (graph-partitioning / facility-location).

---
*Part of the [DBMS Research catalog](../../README.md).*
