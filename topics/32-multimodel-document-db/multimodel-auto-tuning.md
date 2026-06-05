# Auto-tuning storage for mixed workloads

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/multimodel-auto-tuning` · **Status:** empirically-open

## 1. Problem Statement
A multi-model engine serves an **HTAP** workload that mixes document (path/array) access, graph traversals, and relational scans/joins, with both point-lookup (OLTP) and analytic (OLAP) phases. The system must *self-tune* its physical design — which **indexes** (B-tree, inverted/path, adjacency/CSR, zone maps), **storage layouts** (row vs. column vs. document-blob vs. shredded), and **materializations** (views, secondary copies, denormalizations) to maintain — under a budget, with the workload shifting over time.

Variants:
- **Static design (optimization):** given a fixed workload $W$ and a space/maintenance budget $B$, choose a configuration $S$ minimizing total cost. This is the *index/view/layout selection* problem.
- **Online/adaptive:** the workload is a stream; choose and *change* the configuration over time, paying reconfiguration cost, to minimize cumulative cost (regret).
- **Mixed-model coupling:** the same logical data may be reachable through document, graph, and relational paths whose physical structures *interact* (a graph adjacency index and a relational foreign-key index may be redundant) — the open part is tuning across models *jointly*, not per-model.

## 2. Mathematical Foundations
- **Index/materialized-view selection** is classically modeled as a constrained optimization over a candidate set; the benefit of a configuration is *not* additive (an index helps a query only given other choices), so the natural structure is **submodular benefit under a knapsack (budget) constraint**, admitting $(1-1/e)$-style greedy guarantees when benefit is monotone submodular — but interactions (anti-monotone "index interaction," Schnaitter–Polyzotis) break pure submodularity.
- **Online tuning** maps to **Metrical Task Systems / convex body chasing**: configurations are states, reconfiguration is movement cost, query batches are tasks; competitive analysis of MTS gives the relevant lower/upper bounds (Borodin–Linial–Saks). Special cases reduce to **ski-rental / online caching** (build index now vs. pay scans).
- **Learning view:** treat tuning as a contextual bandit / RL problem (state = workload features + current design, action = design delta, reward = − cost); cost-model error is the central difficulty.
- HTAP adds an **isolation/freshness** dimension: maintaining analytic copies (column groups, MVs) versus transactional latency is a Pareto tradeoff, formally a multi-objective optimization over consistency vs. throughput.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** index-interaction theory (Schnaitter, Polyzotis, Chaudhuri) and submodular/greedy view selection (Gupta–Mumick on materialized-view maintenance and selection) frame the static problem; online caching/MTS competitive results bound the adaptive variant in the abstract.
- **Systems-SOTA:** Microsoft **AutoAdmin / Database Tuning Advisor** and DB2 Design Advisor (Chaudhuri–Narasayya lineage) for relational; **self-driving / learned** systems — CMU **Peloton/NoisePage** "self-driving DBMS," **OtterTune** (knob tuning), and learned index/partition advisors. HTAP storage with auto-adaptive layouts: **SAP HANA**, **TiDB/TiFlash**, **SingleStore**, **HTAP "Proteus"-style** adaptive-format engines, and **H2O/adaptive storage** research. Multi-model specifically: **ArangoDB**, **OrientDB**, **Cosmos DB**, and document engines auto-creating path indexes. No system jointly auto-tunes across document+graph+relational with guarantees.

## 4. Upper Bound
For **static** selection with monotone submodular benefit under a cardinality/budget constraint, greedy achieves a **$(1-1/e)$ approximation** (Nemhauser–Wolsey–Fisher) in the value-oracle model; with knapsack budget, a modified greedy gives $(1-1/e)$ as well. For the **online** layout/index decision in the caching/MTS abstraction, deterministic algorithms achieve competitive ratio $O(k)$ (and randomized $O(\log k)$ for paging-like instances). These bounds hold in idealized models with an exact cost oracle; real systems use estimated benefits, so guarantees degrade with cost-model error.

## 5. Lower Bound
- **Index/view selection is NP-hard** (it generalizes set-cover/knapsack; materialized-view selection under maintenance cost is NP-hard, Gupta–Mumick), and inapproximable beyond $(1-1/e)$ for the submodular-maximization core (Feige) — so greedy is essentially optimal in that model.
- **Online lower bound:** any deterministic algorithm for the $k$-state MTS/caching abstraction has competitive ratio $\ge k$ (and $\ge \Omega(\log k)$ randomized), so no online auto-tuner can beat these without workload predictions.
- **Cost-model dependence:** because benefits are interaction-dependent (anti-submodular in places), no oracle-free algorithm can guarantee optimality; with adversarial workload shifts, regret is lower-bounded by the reconfiguration cost.

## 6. The Gap
The *single-model, static* problem is theoretically **near-closed** (greedy matches the $(1-1/e)$ inapproximability). The genuinely open part is **empirical and cross-model**: (1) building accurate, *transferable* cost/benefit models across document, graph, and relational access in one engine; (2) handling *joint* physical structures whose interactions violate submodularity; and (3) achieving good *online* behavior under real HTAP drift with bounded reconfiguration. The status is *empirically-open*: we have abstract bounds but no system or theory that demonstrably auto-tunes mixed-model HTAP storage near-optimally with guarantees — closing it needs both a faithful cost model and an online algorithm with provable regret under realistic workload models.

## 7. Current Research (as of June 2026)
- Learned/RL-based self-driving design (CMU NoisePage lineage, learned advisors) and learned cost models continue; HTAP-aware adaptive storage formats (column/row morphing) are active in industry engines *(frontier — verify which 2025–2026 systems do cross-model joint tuning vs. per-model)*.
- Reinforcement-learning index advisors (e.g., SWIRL-style, DB+RL workshops) and Bayesian-optimization knob tuners are maturing.
- Multi-model benchmark-driven tuning (UniBench-derived) and HTAP freshness/isolation co-tuning are emerging SIGMOD/VLDB directions.

## 8. Future Work
- A unified, transferable **cost model** spanning path, traversal, and relational access enabling joint design search.
- **Online** auto-tuning with provable regret under workload-drift models (beyond worst-case MTS).
- Tuning that co-optimizes physical design *and* the HTAP freshness/consistency Pareto frontier.
- Safe exploration: changing physical design without violating tail-latency SLAs.

## 9. Key References
- **[Foundational]** S. Chaudhuri, V. Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN97.html)
- **[Foundational]** A. Gupta, I. S. Mumick. *Selection of Views to Materialize Under a Maintenance Cost Constraint.* ICDT, 1999. — [DOI](https://doi.org/10.1007/3-540-49257-7_28)
- **[Foundational]** G. L. Nemhauser, L. A. Wolsey, M. L. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[Foundational]** A. Borodin, N. Linial, M. Saks. *An Optimal On-Line Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[SOTA]** A. Pavlo et al. *Self-Driving Database Management Systems (Peloton/NoisePage).* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLLMMMPQ17.html)
- **[SOTA]** D. Van Aken, A. Pavlo, G. J. Gordon, B. Zhang. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[Foundational]** K. Schnaitter, S. Abiteboul, T. Milo, N. Polyzotis. *On-Line Index Selection for Shifting Workloads (COLT/index interaction line).* ICDE workshops, 2007. — [DBLP](https://dblp.org/rec/conf/icde/SchnaitterAMP07.html)

## 10. Worked Example

Budget $B = 2$ indexes. Candidate set $\{a,b,c\}$ with workload benefits (cost saved) when an index is *added to the current set*:

| add to $\emptyset$ | $a$:10 | $b$:8 | $c$:7 |
|---|---|---|---|
| add to $\{a\}$ | — | $b$:3 | $c$:6 |

Note $b$'s marginal benefit drops $8 \to 3$ once $a$ is present (they cover overlapping queries) — diminishing returns, i.e. submodular.

*Greedy.* Pick the best singleton: $a$ (gain 10). Then pick the best marginal addition: $c$ (gain 6) beats $b$ (gain 3). Result $\{a,c\}$, total benefit $10+6 = 16$.

*Optimum.* Enumerate size-2 sets: $\{a,b\}=10+3=13$, $\{a,c\}=16$, $\{b,c\}=8+7=15$. Optimum is $\{a,c\}=16$, so greedy is exact here. The theory guarantees greedy $\ge (1-1/e)\cdot \mathrm{OPT} \approx 0.632\cdot 16 = 10.1$ in the worst case; we comfortably beat the bound.

*Where multi-model bites:* suppose $a$ is a graph adjacency index and $c$ a relational FK index serving the *same* logical join through different models. Then their true joint benefit is **not** additive and can even be *anti*-submodular (one makes the other redundant), violating the greedy guarantee — the open cross-model coupling of Section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
