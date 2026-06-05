# Schema-and-Data Co-Generation for Stress Tests

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/schema-data-co-generation` · **Status:** open

## 1. Problem Statement
Automatically and *jointly* synthesize a schema $\mathcal{S}$ (tables, types, keys, integrity constraints), a query/workload $Q$, and a data instance $D \models \mathcal{S}$ such that executing $Q$ on $D$ *provably* exercises a targeted corner case $\phi$ of a database engine — e.g., a specific optimizer transformation, a hash-join spill boundary, an overflow in cardinality estimation, a particular plan operator, or a code path in the executor.

Variants:
- **Decision:** given target predicate $\phi$ (over plans/runtime states), does there exist $(\mathcal{S}, Q, D)$ with $D\models\mathcal{S}$ and $\phi$ triggered?
- **Constructive/optimization:** produce a *minimal* witness $(\mathcal{S},Q,D)$ (smallest $|D|$, fewest tables) triggering $\phi$ — useful as a reduced bug repro.
- **Counting/coverage:** generate a *set* maximizing coverage of a family $\{\phi_i\}$ (operators, rules, plan shapes) under a size budget.

The novelty versus classic data generation: schema and constraints are *outputs*, not fixed inputs, and the guarantee is *provable triggering*, not merely statistical resemblance.

## 2. Mathematical Foundations
Constraints are modeled as **tuple-** and **equality-generating dependencies** (tgds/egds); a valid instance is a model of the dependency theory, and instance existence under constraints is governed by the **chase** (termination is undecidable in general; decidable for weakly-acyclic sets). Generating $D \models \mathcal{S}$ that also satisfies a *query-induced* condition is a **constraint-satisfaction / SMT** problem: the executor's branch conditions and the optimizer's cost/cardinality formulas become logical constraints over the synthesized tuples.

For "trigger transformation rule $r$", the condition is that the optimizer's pattern-match precondition for $r$ holds on the plan compiled from $Q$ over $\mathcal{S}$ — a reachability condition in the rule-application graph. Cardinality-corner cases invoke the **AGM bound** and its tightness (worst-case-optimal join instances realize the bound, giving provable blow-ups). Coverage maximization over $\{\phi_i\}$ is a **maximum-coverage / submodular** optimization, hence $(1-1/e)$-approximable greedily when coverage is monotone submodular.

## 3. State of the Art (SOTA)
- **Data-only generation with constraints:** **QAGen** (Binnig et al., SIGMOD 2007) and **MyBenchmark/DataSynth**-style reverse query processing generate data so a *given* query yields target intermediate cardinalities, via symbolic/constraint solving. **Touchstone** (Li et al., ATC 2018) and **Hydra** (Sanghi et al., VLDB 2018/TODS) scale cardinality-constraint-preserving generation to large volumes and parallel execution.
- **Schema/query exploration for testing:** **SQLancer** (Rigger–Su, OSDI/ESEC-FSE 2020) finds logic bugs via randomly generated schemas+queries with oracles (TLP/NoREC/PQS) but does *not prove* triggering. **SQLsmith** does grammar-based random query generation. Mutation/coverage-guided fuzzers (e.g., **SQLRight**, **Squirrel**) add code-coverage feedback.
- There is currently **no system** that co-generates schema + constraints + data with a *formal proof* that a chosen optimizer/executor corner case is triggered — hence **open**.

## 4. Upper Bound
For the data-given-schema-and-query subproblem with *acyclic* cardinality constraints, reverse-query-processing (QAGen/Hydra) generates a satisfying instance in time polynomial in output size; Hydra reports near-linear scaling. For coverage selection over a fixed corner-case family, greedy yields a $(1-1/e)$-approximation. SMT/CSP-backed constructive synthesis is "solver-bounded": correct when it returns, but with no general polynomial guarantee.

## 5. Lower Bound
The general decision problem is **undecidable**: query equivalence/containment under arbitrary constraints and chase termination are undecidable, so "does some $D\models\mathcal{S}$ make plan-condition $\phi$ hold" inherits undecidability. Even bounded fragments are hard: satisfying conjunctive-query cardinality constraints is **NP-hard** (embeds subgraph/homomorphism counting), and producing a *minimum* witness is NP-hard via minimal-model/Set-Cover-style reductions. Worst-case-optimal-join instances show some blow-ups are *necessarily* exponential in instance size.

## 6. The Gap
The gap is wide and genuinely open. Practical tools either (a) prove cardinality targets but take schema+query as *fixed input* (QAGen/Hydra), or (b) explore schemas+queries broadly but offer *no proof* of triggering (SQLancer/fuzzers). No framework unifies symbolic data synthesis with schema/constraint synthesis under a provable-trigger objective, and there is no tight complexity characterization for the *joint* problem restricted to optimizer-relevant fragments (e.g., weakly-acyclic tgds + acyclic CQs). Closing it requires both a decidable, expressive target logic and a constructive solver with completeness over that fragment.

## 7. Current Research (as of June 2026)
Directions: (1) coverage-guided + symbolic hybrid generators that lift SQLancer-style oracles with SMT back-ends to *target* specific rules/operators *(frontier — verify)*; (2) using the optimizer's own rule set (e.g., Calcite/Orca/learned optimizers) as the specification against which witnesses are synthesized; (3) LLM-assisted schema/query proposal with a solver as the verifier of triggering, keeping proofs sound. Groups: Rigger (ETH Zürich, SQLancer/automated DB testing), Haritsa's lab (IISc, Hydra/Picasso cardinality work), Binnig (TU Darmstadt). Differential testing across engines (CockroachDB, DuckDB, SQLite, Postgres) remains an active empirical frontier.

## 8. Future Work
- A decidable target logic for "optimizer/executor corner case" + a complete constructive synthesizer over it.
- Minimal-witness (delta-debugging-style) reduction integrated with co-generation.
- Provable coverage guarantees over a rule/operator catalog with formal triggering certificates.
- Co-generation targeting *physical* corner cases (spills, NUMA imbalance, lock escalation), not just logical plans.

## 9. Key References
- **[Foundational]** Binnig, Kossmann, Lo, Özsu. *QAGen: Generating Query-Aware Test Databases.* SIGMOD, 2007.
- **[SOTA]** Sanghi, Sood, Haritsa, et al. *Scalable and Dynamic Regeneration of Big Data Volumes (Hydra).* VLDB/EDBT, 2018.
- **[SOTA]** Li, Zhang, Chen, et al. *Touchstone: Generating Enormous Query-Aware Test Databases.* USENIX ATC, 2018.
- **[SOTA]** Rigger, Su. *Finding Bugs in Database Systems via Query Partitioning (SQLancer/TLP).* OOPSLA, 2020.
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995. (chase, dependencies, decidability)
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Computing, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
