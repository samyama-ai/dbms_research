# Schema evolution without migration

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/schema-evolution-no-migration` · **Status:** empirically-open

## 1. Problem Statement
Support *in-place* schema changes (rename/add/remove field, change type, restructure nesting, split/merge collections) over a collection of billions of documents in which many *versions* of the structure coexist, **without** a global rewrite/migration that touches every document. New writes use the latest shape; old documents remain physically unchanged; reads must transparently see data "as if" migrated.

- **Optimization variant:** minimize total cost = (storage of version metadata + lazy-rewrite I/O + per-read transformation overhead) over a sequence of evolutions and a workload.
- **Correctness/decision variant:** given a chain of schema deltas, does a read transformation exist that is *well-defined* (deterministic, total) on every stored version? (Invertibility of the delta chain.)
- **Online variant:** schedule lazy/background rewrites under a latency/throughput budget so the system never stalls.

This is the operational counterpart of schema-on-read: rather than typing queries, we must *evolve* the logical schema while data is heterogeneous and the migration must be amortized, incremental, and reversible.

## 2. Mathematical Foundations
Each evolution is a **schema modification operation (SMO)** — a small algebra of add/drop/rename/copy/move/split/merge — composing into a *delta chain*. The theory rests on:
- **Schema mappings** and the **chase**: an SMO is a source-to-target tuple-generating dependency; reading old data through the latest schema is *data exchange* / answering queries using views, with the chase computing the canonical universal solution.
- **Invertibility of schema mappings** (Fagin, Kolaitis, Popa, Tan): when can a mapping be inverted (quasi-inverse / maximum recovery) so old data is reconstructable without information loss? This bounds which evolutions are losslessly lazy-migratable.
- **Bidirectional transformations / lenses** (Foster et al.): a get/put pair with round-trip laws models reading old docs forward and writing back consistently.
- **Versioned/temporal storage**: amortized-cost analysis (potential method) for lazy vs. eager rewrite; the workload determines whether eager amortizes better than lazy.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** document stores rely on *application-level* versioning — a `schema_version` field plus read-time up-converters (the "expand-and-contract"/"lazy migration" pattern; MongoDB's documented Schema Versioning pattern). PostgreSQL `jsonb` evolves implicitly (no declared schema). *Online schema change* tools for the relational world — **gh-ost** and **pt-online-schema-change** (Percona) — do non-blocking migrations but still ultimately rewrite. *Southpaw*, *Liquibase*, and event-sourcing upcasters formalize delta chains in industry.
- **Theory-SOTA:** PRISM/PRISM++ (Curino, Moon, Zaniolo, VLDB 2008/2013) formalized SMOs with rewriting and provenance for relational evolution; data-exchange and mapping-inversion theory (Fagin et al.) provides the correctness backbone. A complete theory for *lazy, version-coexisting, billion-document* evolution is not established.

## 4. Upper Bound
*Lazy migration* gives an upper bound of $O(1)$ amortized write-time cost per evolution (only metadata is updated) plus a per-read transformation cost proportional to the *delta-chain length* between a document's stored version and the current schema — i.e., $O(d)$ transformation steps per read where $d$ is the number of intervening SMOs. Background "trickle" rewrites bound chain length over time. For invertible (information-preserving) SMO chains, the chase computes the read transformation in PTIME (data complexity) for weakly-acyclic dependencies, the best known guarantee.

## 5. Lower Bound
Fundamental obstacles: (i) **non-invertible SMOs** (drop/merge that lose information) make exact "as-if-migrated" reads *impossible* — an information-theoretic lower bound; only *certain answers* are recoverable, and computing certain answers under target dependencies can be **coNP-hard** in data complexity. (ii) Chase *termination* is undecidable in general; restricting to weak acyclicity is what buys PTIME. (iii) Any scheme that avoids global rewrite must pay *somewhere* — a read/write/storage trilemma reminiscent of the **RUM conjecture** (you cannot simultaneously minimize Read, Update, and Memory overhead). No global rewrite ⇒ unbounded read-side transformation cost as deltas accumulate unless background work is done.

## 6. The Gap
Practice (lazy up-converters) works but is *ad hoc, application-coded, and unverified*: no system gives a proven bound on read overhead, no guarantee that the delta chain stays invertible, and no automatic scheduler that provably amortizes background rewrite under a budget. Theory (mapping inversion, chase, certain answers) gives correctness conditions but isn't connected to the billion-document, mixed-version operational reality. The gap is *empirical*: closing it means a system whose lazy evolution is both formally sound (invertibility-aware) and has proven amortized cost bounds.

## 7. Current Research (as of June 2026)
Active: declarative schema-evolution DSLs with provenance (PRISM lineage); event-sourcing upcaster verification; *(frontier — verify)* automatic lazy-migration schedulers and "schema-version-aware" storage in cloud document/lakehouse engines, plus LLM-assisted generation of up-converter functions from delta specs, are being explored in 2025–2026 without published cost guarantees. Data-exchange/mapping-inversion theory continues (Fagin–Kolaitis lineage; Arenas, Barceló, Libkin).

## 8. Future Work
A sound lazy-evolution system with proven amortized read/write/storage bounds; static detection of non-invertible (lossy) SMOs with user warnings; cost-based scheduling of background rewrite under latency budgets; integration with schema-on-read typing so coexisting versions are statically checkable; certain-answer semantics for reads after lossy evolution.

## 9. Key References
- **[Foundational]** Curino, Moon, Deutsch, Zaniolo. *Automating the Database Schema Evolution Process (PRISM++).* VLDB Journal, 2013.
- **[Foundational]** Fagin, Kolaitis, Popa, Tan. *Quasi-Inverses of Schema Mappings.* ACM TODS, 2008.
- **[Foundational]** Fagin, Kolaitis, Miller, Popa. *Data Exchange: Semantics and Query Answering.* ICDT/TCS, 2005 (the chase, certain answers).
- **[Foundational]** Foster, Greenwald, Moore, Pierce, Schmitt. *Combinators for Bidirectional Tree Transformations (Lenses).* ACM TOPLAS, 2007.
- **[SOTA]** Athanassoulis, Kester, Maas, Stoica, Idreos, Ailamaki, et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016.
- **[Survey]** Roddick. *Schema Evolution in Database Systems — A Survey.* (and successors in NoSQL schema management), 1995 / updated.

---
*Part of the [DBMS Research catalog](../../README.md).*
