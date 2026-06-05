# DP Under Foreign-Key Constraints and Schemas

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/dp-with-fk-constraints` · **Status:** open

## 1. Problem Statement

Differential privacy was defined for a single table where the unit of privacy is one row. Real databases are **normalized multi-relation schemas** with **foreign-key (FK) referential integrity**: e.g., `Patients(pid)` ← `Visits(pid)` ← `Labs(visit_id)`. The privacy "entity" (a patient) lives in one table but its data fan out through FK chains into many others. The problem: **define a coherent neighbor relation** on the whole schema that (a) captures "one entity's data," (b) keeps databases referentially valid, and (c) admits **bounded, computable sensitivity** for queries spanning multiple relations.

Variants:
- **Definitional:** what does $D\sim D'$ mean when removing a patient must cascade-delete dependent rows to preserve FK validity?
- **Sensitivity (counting/optimization):** given an entity-level neighbor relation, compute/approximate per-query sensitivity through FK joins.
- **Mechanism (optimization):** achieve minimal-error DP for SQL over the schema at the chosen granularity.

## 2. Mathematical Foundations

A schema is a set of relations with FK dependencies forming a DAG (a set of *inclusion dependencies* / tuple-generating dependencies). Referential integrity: every FK value references an existing PK. A **neighboring** definition must respect this — naive row add/remove can violate integrity (orphan rows). Candidate notions:

- **Entity-DP / one-out-of (Kotsogiannis et al., PrivateSQL):** pick a *primary private relation* $P$; $D\sim D'$ iff they differ by one entity in $P$ **together with the transitive cascade-deletion** along FK edges. Sensitivity is then the worst-case fan-out, bounded via the schema's FK *multiplicities* (max degree per FK edge).
- **Multiple-private-relations:** several entity types, each with its own budget/granularity (a *privacy lattice*).

Sensitivity through a join chain is governed by the product of FK degrees; under a true FK (many-to-one) the *parent* side has degree 1, so a tuple in the child references exactly one parent — this **asymmetry can drastically reduce sensitivity** compared to arbitrary joins (AGM bound specializes). Formally, with an *acyclic FK schema* and entity granularity, $\Delta_Q \le$ max number of $P$-entity-reachable tuples participating in $Q$, computable via the **chase** over inclusion dependencies. Lipschitz-extension/truncation (cap an entity's fan-out at $\tau$) restores bounded sensitivity when degrees are unbounded.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **R2T** (Dong, Yi et al., SIGMOD 2022) gives instance-optimal (up to $\log$) DP for SUM/COUNT over FK-joined schemas using Lipschitz extensions + LP, explicitly modeling foreign keys.
- **Systems-SOTA:** **PrivateSQL** (Kotsogiannis, Tao, He, Hay, Machanavajjhala, Miklau, VLDB 2019) is the reference system: it defines a *primary private relation*, derives a **privacy view** over the schema, and provides multi-relation sensitivity. **Tumult Analytics** supports multi-table "key sets" and truncation at entity granularity. Earlier, **PINQ/wPINQ** handled limited transformations.

## 4. Upper Bound

For acyclic FK schemas with a single primary private relation and SUM/COUNT-over-join queries, **R2T** achieves error within $O(\log n)$ of the instance-optimal truncation mechanism, in polynomial time, under entity-level neighbors. PrivateSQL gives a *sound* (not optimal) bounded-sensitivity mechanism for general DP-SQL over the schema. Truncation-based mechanisms give $\tilde{O}(\tau \cdot \mathrm{poly}(1/\varepsilon))$ error with tunable $\tau$.

## 5. Lower Bound

Choosing the optimal truncation/sensitivity for general schemas with **cyclic** inclusion dependencies or **multiple interacting private relations** is hard: it inherits NP-hardness from multi-join sensitivity (clique/subgraph reductions) once FKs allow many-to-many bridge tables. Information-theoretically, entity-level error is $\Omega(\text{max entity fan-out})$ in the worst case (a single high-degree entity forces large noise), so no mechanism can avoid large error on skewed schemas — a packing lower bound. There is no general impossibility for the *definitional* question, but no canonical neighbor definition is provably "right."

## 6. The Gap

The field has **working systems** (PrivateSQL, R2T, Tumult) for *single-primary-relation, acyclic FK, SUM/COUNT* — there the gap is small. It is **open** for: (i) **multiple correlated private entities** (e.g., both patients and doctors are sensitive) where no agreed neighbor relation or tight composition exists; (ii) **cyclic / many-to-many** schemas; (iii) a *canonical, axiomatized* definition of schema-level neighbors with optimal sensitivity. Closing it needs both a definitional consensus and instance-optimal mechanisms beyond the acyclic single-entity case.

## 7. Current Research (as of June 2026)

- Multi-entity / lattice-of-privacy-units DP for normalized schemas, extending PrivateSQL's primary-relation model *(frontier — verify)*.
- DP for *denormalized vs. normalized* representations — proving equivalence/optimality of sensitivity across normal forms *(frontier — verify)*.
- Chase-based sensitivity propagation under general TGDs/EGDs (constraint-aware DP), connecting DP to classical database theory.

## 8. Future Work

- Axiomatic neighbor definition for arbitrary schemas with referential and functional dependencies.
- Instance-optimal DP for many-to-many and cyclic FK graphs.
- Composition across multiple private entity types under one global budget (links to `privacy-budget-accounting-workloads`).
- Synthetic-data generation that preserves FK integrity under DP.

## 9. Key References

- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (chase, inclusion dependencies).
- **[Foundational]** Kifer, Machanavajjhala. *No Free Lunch in Data Privacy.* SIGMOD, 2011 (why the neighbor/granularity definition matters).
- **[SOTA]** Kotsogiannis, Tao, He, Hay, Machanavajjhala, Miklau. *PrivateSQL: A Differentially Private SQL Query Engine.* VLDB, 2019.
- **[SOTA]** Dong, Yi, et al. *R2T: Instance-optimal Truncation for Differentially Private Query Evaluation with Foreign Keys.* SIGMOD, 2022.
- **[SOTA]** Tao, McKenna, Hay, Machanavajjhala, Miklau. *Benchmarking Differentially Private Synthetic Data Generation Algorithms.* (multi-relation context), 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
