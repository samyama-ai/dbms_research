# Schema Evolution over Temporal Data

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-schema-evolution` · **Status:** open

## 1. Problem Statement
A temporal database stores facts stamped with valid time and/or transaction time. Independently, the *schema* itself evolves: attributes are added, dropped, renamed, split, merged, retyped, or have their constraints changed, and each such change is itself stamped in time. The problem is to answer a query posed against one schema version (typically the current one, or a user-chosen "reference" schema) **consistently over data that was written under different, possibly incompatible schema versions**, without materializing every history into a single fixed schema.

Variants:
- **Decision:** given a query and a target schema version, is every historical tuple expressible (losslessly) under that version? (schema-mapping satisfiability)
- **Optimization:** compute the answer with minimum rewriting / migration cost.
- **Counting/certain-answers:** when an evolution step loses information (e.g. a dropped column), what are the *certain* vs *possible* answers across versions?

This is the temporal lift of *schema evolution* and *data exchange*: now the mappings between versions are themselves time-indexed, and "the schema at time $t$" is a query input, not a constant.

## 2. Mathematical Foundations
Model a schema history as a sequence of schemas $S_0, S_1, \dots, S_k$ with transition mappings $m_i : S_i \to S_{i+1}$ expressed as **source-to-target tuple-generating dependencies (s-t tgds)** and **equality-generating dependencies (egds)** — the data-exchange setting of Fagin–Kolaitis–Miller–Popa. Each $m_i$ has a validity period $[\tau_i, \tau_{i+1})$ in transaction time. A query $Q$ over reference schema $S_r$ must be evaluated against instance fragments $I_j$ each conforming to $S_j$.

Evaluation reduces to chasing $I_j$ through the composition of mappings $m_j \circ \dots \circ m_{r-1}$ (or their inverses). The relevant machinery: the **chase** and its termination (weak acyclicity), **composition of schema mappings** (which is *not* closed in FO and may require second-order tgds — Fagin et al.), **certain answers** $\mathsf{certain}(Q,I)=\bigcap\{Q(J): J \models \Sigma\}$, and the **inverse / quasi-inverse** of a mapping for backward (older-schema) evaluation. Lossy steps make $\mathsf{certain}$ and $\mathsf{possible}$ answers diverge, formalized via incomplete-information semantics (naïve tables, conditional tables).

## 3. State of the Art (SOTA)
**Theory-SOTA:** Composition and inversion of schema mappings (Fagin–Kolaitis–Popa–Tan, PODS/TODS 2004–2009) give the algebra; certain-answer evaluation under tgds is coNP-complete in data complexity in general, PTIME for weakly-acyclic, terminating chase. The PRISM/PRISM++ line (Curino, Moon, Zaniolo, VLDB 2008/2013) operationalizes schema evolution with *Schema Modification Operators (SMOs)* and integrity-constraint modification operators, automatically rewriting queries across versions and reporting information loss.

**Systems-SOTA:** Temporal/system-versioned tables in SQL:2011 engines (MariaDB, Db2, SQL Server, Oracle Flashback) handle *data* history but treat schema change largely manually (migration scripts, `ALTER ... ADD SYSTEM VERSIONING`). Liquibase/Flyway version DDL but offer no cross-version query semantics. Datomic and "schema-on-read" lakehouse formats (Apache Iceberg, Delta Lake) keep evolving schemas with column-id mapping enabling time-travel reads — the closest deployed approximation, but limited to add/drop/rename/widen, not arbitrary semantic remapping.

## 4. Upper Bound
For mappings given by **weakly-acyclic** sets of tgds+egds, certain-answer computation of unions of conjunctive queries across versions is in **PTIME (data complexity)** in the RAM model via the polynomial-size canonical universal solution produced by the terminating chase; combined complexity is EXPTIME-hard. PRISM++ shows that for the SMO algebra, every history-preserving rewrite is computable and the rewriting itself is polynomial in the number of SMOs. With column-id–based formats, point time-travel read under add/drop/rename/widen is $O(1)$ schema-resolution overhead per column.

## 5. Lower Bound
Certain-answer evaluation under arbitrary tgds is **undecidable** (chase may not terminate); for general s-t tgds it is **coNP-complete in data complexity** (Fagin et al.), inherited here per version. Mapping **composition** can require second-order existential quantifiers and **SO-tgd** are needed — first-order schema mappings are *not* closed under composition (Fagin–Kolaitis–Popa–Tan), so any system restricting to FO mappings is provably incomplete. Recovering an exact **inverse** of a lossy evolution step is impossible in general; only quasi-/maximum-recoveries exist (Arenas–Pérez–Riveros), an information-theoretic loss bound.

## 6. The Gap
The algebra of mappings (composition, inversion) and per-version certain answers are well understood, but the **temporal binding** is the open part: there is no accepted semantics for a single query that ranges over *valid-time* histories whose *schema* also varies in *transaction time* — a genuinely bitemporal-plus-schema object. No tight complexity characterization exists for "evaluate $Q$ as-of schema version $v$ over the union of all data ever written," nor an optimizer that costs cross-version rewriting against migration. The gap is open: closing it needs a confluent semantics unifying data-exchange certain answers with bitemporal as-of evaluation, plus decidable fragments capturing real SMO workloads.

## 7. Current Research (as of June 2026)
Active directions: (i) schema evolution in lakehouse table formats — Iceberg/Delta column-mapping and "schema-on-read" time travel, with vendors extending to type-promotion lineage; (ii) extending PRISM-style SMO rewriting to NoSQL/document and graph stores (Zaniolo, Möller, Klettke, Störl on *NoSQL schema evolution* and *Darwin/MigCast* cost models); (iii) entity-resolution-aware evolution. *(frontier — verify)* Recent work couples LLM-assisted migration synthesis with verified chase-based equivalence checking to certify that a generated migration preserves certain answers. Groups: Zaniolo (UCLA), Klettke/Störl (Rostock/Darmstadt), Arenas/Barceló (PUC/IMFD Chile) on mapping theory.

## 8. Future Work
- A confluent **bitemporal + schema-versioned** query semantics with decidable, PTIME fragments.
- Optimizer that reorders cross-version rewriting with joins and chooses lazy-rewrite vs eager-migrate by cost.
- Information-loss *quantification* (which certain answers are lost by a proposed SMO) surfaced at DDL time.
- Verified, possibly LLM-assisted, migration synthesis with chase-based equivalence certificates.

## 9. Key References
- **[Foundational]** Fagin, R., Kolaitis, P., Miller, R., Popa, L. *Data Exchange: Semantics and Query Answering.* ICDT/TCS, 2003/2005.
- **[Foundational]** Fagin, R., Kolaitis, P., Popa, L., Tan, W.-C. *Composing Schema Mappings: Second-Order Dependencies to the Rescue.* PODS/TODS, 2004/2005.
- **[SOTA]** Curino, C., Moon, H. J., Zaniolo, C. *Graceful Database Schema Evolution: the PRISM Workbench.* VLDB, 2008. (and PRISM++, ICDE 2013)
- **[Foundational]** Arenas, M., Pérez, J., Riveros, C. *The Recovery of a Schema Mapping: Bringing Exchanged Data Back.* TODS, 2009.
- **[Survey]** Roddick, J. F. *A Survey of Schema Versioning Issues for Database Systems.* Information and Software Technology, 1995.
- **[SOTA]** Störl, U., Klettke, M., Scherzinger, S. *NoSQL Schema Evolution and Big Data Migration at Scale.* IEEE Big Data, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
