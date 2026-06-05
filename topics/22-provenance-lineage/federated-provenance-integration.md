# Cross-System Federated Provenance

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/federated-provenance-integration` · **Status:** open

## 1. Problem Statement

Modern data pipelines span heterogeneous engines — an OLTP DB, a Spark/Flink job, a dbt/SQL warehouse, a feature store, an ML trainer — each capturing provenance in its own model, granularity, and vocabulary (or none). The problem is to **reconcile and compose these partial, heterogeneous provenance records into a single coherent, queryable end-to-end lineage**, so that why/how/where and impact-analysis queries can be answered *across system boundaries*.

Sub-problems:
- **Entity reconciliation (decision/matching):** decide when an output of system $A$ and an input of system $B$ are the *same* data entity (same file/table/row/cell), across naming, format, and granularity mismatches — a provenance-specific record-linkage problem.
- **Semantic composition:** compose the local provenance algebras (different semirings/granularities) into a global one with sound propagation across the seams.
- **Gap handling:** reason about lineage when some systems are *opaque* (no provenance) — infer or bound the missing edges.
- **Querying (optimization):** answer a global provenance query with minimal cross-system data movement.

## 2. Mathematical Foundations

Each system exposes a local provenance graph/annotation $P_i$ over its own vocabulary; integration is a **schema-/ontology-mediated mapping** problem: align entities via mappings $m_{ij}$ and **compose mappings** (data-exchange composition, Fagin–Kolaitis–Popa–Tan). The W3C **PROV** data model gives a shared abstract vocabulary (entity/activity/agent, `wasDerivedFrom`), so composition is a **graph merge under equivalence** $\equiv$ on nodes (the reconciliation relation), i.e., quotienting the union $\bigsqcup_i P_i / \equiv$.

Reconciliation is **entity resolution**: maximize matching quality, a problem with **submodular** correlation-clustering objectives (minimize disagreements) — correlation clustering is APX-hard, with constant-factor LP/region-growing approximations. Composing *annotations* across heterogeneous semirings requires **semiring homomorphisms** at the seams; when local semantics differ (bag vs. probabilistic vs. trust), composition is sound only along homomorphisms (GKT functoriality), and lossy otherwise.

Opaque-system gaps make the merged graph **partial**: end-to-end ancestry becomes **certain reachability** under all completions consistent with observed boundary conditions — a problem of reasoning over **possible worlds** of the lineage graph.

## 3. State of the Art (SOTA)

No system delivers sound cross-engine annotation-level lineage; the practical SOTA is **catalog-level lineage integration**. **OpenLineage** + **Marquez** (LF AI&Data) define an event spec that engines (Airflow, Spark, dbt) emit, assembled into a job/dataset graph — coarse (dataset/column), best-effort matching. **DataHub**, **Apache Atlas**, **Egeria**, and **Unity Catalog** ingest connector-emitted lineage and reconcile by name/URN. **Ground** (Hellerstein et al., CIDR 2017) proposed a context/lineage service across systems. **PROV-DM/PROV-O** standardize the model for interchange. Research SOTA on the *semantic* side is in workflow-provenance interoperability and provenance integration via mediated schemas, but **column/row/cell-level reconciliation with guarantees is open**. Most production lineage is name-matched, table/column-grained, and unverified across seams.

## 4. Upper Bound

- **Graph merge under a given reconciliation:** computing the quotient $\bigsqcup_i P_i/\equiv$ and answering ancestry RPQs in **$O(|Q|\cdot|P|)$** — RAM model.
- **Entity reconciliation (correlation clustering):** constant-factor approximation (e.g., $\le 3$ via region-growing / $O(1)$ LP rounding) to the minimum-disagreement matching — approximation model.
- **Annotation composition along homomorphisms:** exact, PTIME propagation when seam mappings are semiring homomorphisms (GKT) — data-complexity model.
- **Certain reachability with opaque gaps:** for monotone (positive) pipelines, PTIME via treating each opaque system as a total-connectivity hyperedge (sound over-approximation).

## 5. Lower Bound

- **Optimal entity reconciliation:** **NP-hard / APX-hard** (correlation clustering, minimum-disagreement) — no PTAS unless P=NP — approximation model.
- **Mapping composition:** requires **second-order tgds** and can blow up exponentially; certain-answer querying across composed mappings is **coNP-hard** in data complexity for expressive classes.
- **Lossy seams:** when local semirings are not homomorphically compatible, *exact* cross-system annotation provenance is **impossible** (information-theoretic) — only sound approximations survive.
- **Opaque-system inference:** deciding exact end-to-end lineage through a black-box (non-replayable) component is **undecidable** (reduces to program/UDF behavior); even possible-world reasoning is **coNP-hard** for non-monotone pipelines.
- **Communication:** assembling lineage across $k$ systems has an inherent **communication-complexity** lower bound $\Omega(\text{boundary size})$ — distributed model.

## 6. The Gap

**Wide open.** Catalog systems (OpenLineage/DataHub/Atlas) give *coarse, name-matched, unverified* lineage; the theory (PROV merge, data-exchange composition, GKT homomorphisms) gives the building blocks but no end-to-end soundness statement. The central missing result is a **composition theorem**: under what reconciliation quality and seam-homomorphism conditions does the merged lineage *soundly and completely* answer global why/how queries — and how to handle opaque systems with provable bounds rather than silent gaps. Closing it requires guaranteed cross-granularity reconciliation, homomorphic seam composition, and possible-world semantics for missing provenance.

## 7. Current Research (as of June 2026)

(1) **Column- and row-level lineage** in OpenLineage/DataHub/Unity Catalog, pushing below dataset granularity with SQL-parse-based field mapping *(frontier — verify)*. (2) **Semantic provenance integration** via shared ontologies (PROV-O + domain ontologies) and ML-based entity reconciliation across catalogs *(frontier — verify)*. (3) **Verifiable / tamper-evident** cross-system lineage so seams can be cryptographically attested (links to verifiable-provenance work). (4) Formal **composition of provenance algebras** across heterogeneous semirings (Tannen, Glavic, Senellart circles) *(frontier — verify)*.

## 8. Future Work

- A soundness/completeness theorem for composed cross-system provenance.
- Cross-granularity reconciliation with quality guarantees (row/cell linkage).
- Possible-world semantics and bounds for opaque-component gaps.
- Standardized homomorphic seam interfaces between engine provenance models.

## 9. Key References

- **[Foundational]** L. Moreau, P. Missier et al. *PROV-DM: The PROV Data Model.* W3C Recommendation, 2013.
- **[SOTA]** J. M. Hellerstein et al. *Ground: A Data Context Service.* CIDR, 2017.
- **[SOTA]** OpenLineage / Marquez Project (LF AI & Data). *OpenLineage Specification.* 2021–.
- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Composing Schema Mappings.* PODS / TODS, 2004–2009.
- **[Foundational]** N. Bansal, A. Blum, S. Chawla. *Correlation Clustering.* Machine Learning / FOCS, 2004.
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
