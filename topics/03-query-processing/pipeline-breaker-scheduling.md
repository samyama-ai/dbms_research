# Pipeline breaker minimization

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/pipeline-breaker-scheduling` · **Status:** open

## 1. Problem Statement

A **pipeline breaker** is any operator that must fully consume (materialize) at least one of its inputs before producing output: sort, hash-join *build*, grouping/aggregation, distinct, and spill-to-disk boundaries. Pipeline breakers force intermediate materialization, consume memory, and create scheduling dependencies that limit how morsels/vectors stream through a plan. The problem: *given a physical plan (or the freedom to choose one) and a memory budget, schedule and shape the plan to minimize total materialized bytes (or peak memory, or critical-path stall) at pipeline breakers, while preserving correctness and not blowing up CPU cost.*

Variants: (a) **plan-shaping** — choose join order, build/probe sides, and aggregate placement so fewer/cheaper breakers occur; (b) **scheduling** — given a fixed plan, order pipeline execution and assign memory to minimize peak/total materialization (a resource-constrained scheduling problem); (c) **decision** — can the plan run within memory budget $M$ without spilling?; (d) **online/adaptive** — decide breaker placement as cardinalities are revealed at runtime. Objective functions of interest: peak memory, total materialized volume, makespan/critical path, and spill I/O.

## 2. Mathematical Foundations

Model a physical plan as a DAG $G=(V,E)$ of operators; a subset $B\subseteq V$ are breakers, each with a materialization cost $w(b)$ proportional to the cardinality of the input it buffers. **Pipelines** are maximal breaker-free paths; a plan decomposes into a set of pipelines whose execution order respects breaker dependencies, giving a DAG-scheduling instance. Minimizing peak memory over a schedule of a DAG with buffer weights generalizes **register allocation / pebbling** (black-pebble and red-blue pebble games, Hong–Kung) and **parallel scheduling with memory bounds**, both NP-hard in general. The choice of build vs. probe side and join order interacts with cardinality estimates via the **AGM bound** and standard selectivity models; "minimize materialized bytes" over join orders is a generalization of the classic **join-ordering** optimization (NP-hard, Ibaraki–Kameda). Tradeoffs are naturally cast as constrained optimization with **submodular**-flavored coverage of which intermediate results can be fused.

## 3. State of the Art (SOTA)

**Theory-SOTA:** No clean tight result; the problem inherits NP-hardness from join-ordering and pebbling, and is studied via approximation/heuristics. **Systems-SOTA:** **HyPer/Umbra**'s data-centric compilation (Neumann, VLDB 2011) maximizes pipeline length by keeping tuples in registers across non-breaking operators and only materializing at breakers — the canonical "push" model that *minimizes* breaker crossings. **Morsel-driven parallelism** (Leis et al., SIGMOD 2014) schedules pipeline morsels NUMA-locally. DuckDB, Velox, Photon, and Spark's whole-stage codegen all organize execution around pipeline/stage boundaries and assign memory per breaker. Adaptive spill/grace-hash and partition-wise aggregation reduce per-breaker footprint. Cardinality-driven build-side selection is standard. None provide provable optimality of breaker placement.

## 4. Upper Bound

For a *fixed* plan, scheduling pipelines to respect breaker dependencies admits the trivial $O(|V|+|E|)$ topological schedule; memory-minimizing schedules are obtained by heuristics with no general guarantee. For tree-shaped plans, peak-memory pebbling is solvable in polynomial time, giving an exact algorithm when the join graph is a tree (acyclic). For series-parallel / bounded-treewidth plan DAGs, dynamic programming yields polynomial-time optimal breaker scheduling. Join-order-with-breaker-cost over left-deep trees is solvable by Selinger-style DP in $O(2^n n)$ — exponential but exact for modest $n$. Approximation guarantees for general DAG peak-memory minimization follow from pebbling approximations (polylog factors).

## 5. Lower Bound

Minimizing materialized volume over join orders is **NP-hard** (reduction from join ordering with cross products; Ibaraki–Kameda, Cluet–Moerkotte). Peak-memory scheduling of a general operator DAG is **NP-hard** via the **pebbling / register-sufficiency** reduction (Sethi: register sufficiency is NP-complete; black pebbling is PSPACE-complete in the most general game). Thus exact minimization is intractable in the worst case, and even approximating peak pebbling is hard within certain factors. These are classical-complexity (NP/PSPACE) lower bounds; no fine-grained conditional sharpening specific to query plans is established.

## 6. The Gap

For *trees / bounded-treewidth* plans the problem is essentially closed (polynomial exact algorithms). For *general DAG* plans — which arise with shared subplans, bushy joins, and common-table-expression reuse — the gap between heuristic systems practice and any approximation guarantee is wide and **genuinely open**: there is no algorithm that provably minimizes (or $c$-approximates) peak/total breaker materialization for arbitrary plans under a memory budget, and no matching hardness-of-approximation tailored to realistic plan structure. Closing it means either an approximation algorithm with a query-relevant guarantee or a tight inapproximability result, plus a cost model validated against real spill behavior.

## 7. Current Research (as of June 2026)

(1) **Memory-aware adaptive execution** — runtime spill decisions and dynamic build-side flipping in DuckDB/Umbra/Velox, with work on minimizing materialization under concurrency. (2) **Sub-plan reuse & materialization-vs-recompute** for DAG plans with shared CTEs (a coverage/submodular tradeoff). (3) **Pipeline scheduling for heterogeneous hardware** (GPU/CPU, disaggregated memory) where breaker placement governs data movement. (4) **Robust/learning-based** breaker placement under cardinality uncertainty. Groups: Neumann/Leis (TUM), the DuckDB team (CWI), Velox/Meta. *(frontier — verify)* 2025–2026 efforts report DP-based breaker schedulers for bushy plans on disaggregated memory that bound peak footprint; guarantees remain restricted to special plan shapes.

## 8. Future Work

- A provable approximation for peak/total breaker materialization on general plan DAGs under a memory budget.
- Tight inapproximability tailored to query plan structure (vs. generic pebbling hardness).
- Joint optimization of join order *and* breaker scheduling rather than sequential phases.
- Robust breaker placement under cardinality uncertainty with regret guarantees.
- Cost models for disaggregated/tiered memory where materialization cost is non-uniform.

## 9. Key References

- **[Foundational]** Sethi. *Complete Register Allocation Problems.* SIAM J. Computing, 1975.
- **[Foundational]** Hong, Kung. *I/O Complexity: The Red-Blue Pebble Game.* STOC 1981.
- **[Foundational]** Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* VLDB 2011.
- **[SOTA]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism.* SIGMOD 2014.
- **[Foundational]** Ibaraki, Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984.
- **[SOTA]** Raasveldt, Mühleisen. *DuckDB: An Embeddable Analytical Database.* SIGMOD 2019 (and execution-engine papers).

---
*Part of the [DBMS Research catalog](../../README.md).*
