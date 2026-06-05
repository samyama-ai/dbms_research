# Provenance Under Schema Evolution

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-schema-evolution` · **Status:** open

## 1. Problem Statement

Stored provenance refers to schemas, queries, and transformations *as they were when the data was produced*. When schemas migrate (rename/split/merge columns, change types, add/drop tables), queries are rewritten, and transformation pipelines change, previously-captured lineage may become **unreadable, ambiguous, or semantically stale**. The problem is to **maintain and reinterpret lineage across schema/query/transformation evolution** so provenance queries remain answerable and *correct under the current schema*.

Variants:
- **Migration (maintenance):** given old provenance $P$ and a schema mapping $m: S_{\text{old}} \to S_{\text{new}}$, compute migrated provenance $P' = \mathsf{migrate}(P,m)$ such that provenance queries over $S_{\text{new}}$ are answered correctly — exactly, or with characterized information loss.
- **Reinterpretation (decision):** given evolved queries/transformations, decide whether historical lineage is still *valid* (the derivation still holds) or *invalidated* by the change.
- **Cross-version (optimization):** answer a provenance query spanning multiple schema epochs with minimal recomputation / minimal stored deltas.

The hard cases are **non-information-preserving** mappings (lossy splits/merges, type narrowings) where exact migration is impossible and the question becomes the best sound approximation.

## 2. Mathematical Foundations

Schema evolution is formalized as **schema mappings** — source-to-target tuple-generating and equality-generating dependencies (s-t tgds/egds), the **data-exchange** framework (Fagin–Kolaitis–Miller–Popa). Migrating provenance is **composing provenance with a mapping**: provenance polynomials in $\mathbb{N}[X_{\text{old}}]$ must be transported along $m$ to $\mathbb{N}[X_{\text{new}}]$, which is well-defined when $m$ induces a **semiring homomorphism** on annotations, and only approximable otherwise.

Core tools: **mapping composition** (the composition of two schema mappings — Fagin–Kolaitis–Popa–Tan, shown not closed under FO but closed under second-order tgds), the **chase** for computing certain answers under the migrated mapping, and **information-preservation / invertibility** of mappings (Fagin's *inverse*, *quasi-inverse*, *maximum recovery*). A mapping is **invertible** iff provenance migrates without loss; lossy mappings give only **certain provenance** (the provenance true under all valid target instances), formalizable via $\mathbb{N}[X]$-annotated certain answers.

Where evolution rewrites *queries*, the relevant notion is **query equivalence under constraints** (containment via the chase), undecidable in general but decidable for CQ-under-tgds fragments where the chase terminates.

## 3. State of the Art (SOTA)

Largely **unaddressed as a unified problem**; components exist. **Data-exchange / schema-mapping theory** (Fagin–Kolaitis–Miller–Popa, ICDT 2003; mapping composition and inversion, PODS 2004–2009) supplies the algebra but does not transport provenance. **PRISM / PRISM++** (Curino–Moon–Zaniolo, VLDB 2008/2013) rewrites *queries* across schema versions using Schema Modification Operators (SMOs) and reports information preservation — directly relevant but provenance-agnostic. **Temporal/versioned schema** systems and **dataset versioning** (DataHub/OrpheusDB, Decibel) track lineage of *versions* but not annotation-level lineage reinterpretation. Provenance-management systems (GProM, ProvSQL) assume a fixed schema. Systems-SOTA is thus *query rewriting across versions* (PRISM) plus *version lineage* (DataHub), with no transport of fine-grained annotation provenance through mappings.

## 4. Upper Bound

- **Invertible (information-preserving) mappings:** exact provenance migration in PTIME data complexity by composing the annotation homomorphism with $m$ — RAM model.
- **CQ schema mappings, terminating chase (weakly acyclic tgds):** migrated certain provenance computable in PTIME data complexity via the chase — data-exchange model.
- **Mapping composition:** representable by **second-order tgds**, with composition computable; certain-answer query evaluation under the composed mapping in PTIME data complexity (combined complexity higher) — Fagin–Kolaitis–Popa–Tan.
- **Cross-version answering:** with stored per-epoch deltas, a provenance query touching $k$ epochs answered in $O(\sum_i |\Delta_i| + |\text{out}|)$.

## 5. Lower Bound

- **Query/mapping equivalence under constraints** (deciding whether evolved lineage is still valid): **undecidable** in general (implication of tgds/egds is undecidable) — first-order logic; decidable but **EXPTIME/NP-hard** for restricted CQ-under-tgd fragments.
- **Chase termination** for arbitrary tgds is **undecidable**, so exact migration via chase has no algorithm in general.
- **Lossy mappings:** exact provenance migration is **impossible** (information-theoretic) — a non-invertible mapping discards the distinctions a why/where query needs; only certain (sound, incomplete) provenance is recoverable.
- **Composition blowup:** the composed second-order tgd can be **exponentially larger**, and certain-answer combined complexity is **coNP-/$\Pi_2^p$-hard** for expressive mapping classes.

## 6. The Gap

**Open and barely charted.** Data-exchange gives a rigorous mapping algebra and PRISM gives practical query rewriting, but **no one has defined `migrate(provenance, mapping)` with soundness/completeness guarantees**, nor characterized which evolution operators (SMOs) are provenance-invertible vs. lossy, nor given the complexity of cross-epoch provenance answering. The decidability frontier (query-equivalence-under-constraints) bounds what *automatic* reinterpretation can ever achieve. Closing the gap needs: a provenance-transport operator over schema mappings, an SMO-by-SMO information-preservation classification for annotations, and a tractable cross-version provenance evaluation algorithm.

## 7. Current Research (as of June 2026)

(1) **Provenance-aware data exchange** — transporting semiring annotations and certain provenance through s-t tgds, extending GKT-provenance to the chase (Tannen, Kolaitis circles) *(frontier — verify)*. (2) **Lineage across dataset/lakehouse versions** (Iceberg/Delta schema evolution) with column-mapping metadata used to reinterpret old lineage *(frontier — verify)*. (3) **PRISM-style evolution** revisited for ML/feature pipelines where transformation code, not just schema, evolves. (4) Catalogs (OpenLineage/Marquez, Unity Catalog) accumulating cross-version lineage, motivating formal reinterpretation semantics.

## 8. Future Work

- A sound/complete `migrate` operator with an SMO information-preservation classification.
- Decidable tractable fragments for "is historical lineage still valid?"
- Cross-epoch provenance query evaluation with bounded recomputation.
- Handling transformation-code evolution (not just schema) in pipeline lineage.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* ICDT, 2003 / TCS, 2005. — [DOI](https://doi.org/10.1007/3-540-36285-1_14)
- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Composing Schema Mappings: Second-Order Dependencies and the Inverse.* PODS / ACM TODS, 2004–2009. — [DOI](https://doi.org/10.1145/1114244.1114249)
- **[SOTA]** C. Curino, H. J. Moon, C. Zaniolo et al. *Graceful Database Schema Evolution: PRISM / PRISM++.* PVLDB, 2008 / 2013. — [DBLP](https://dblp.org/rec/journals/pvldb/CurinoMZ08.html)
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** S. Huang, L. Xu, A. Elmore, A. Parameswaran et al. *OrpheusDB: Bolt-on Versioning for Relational Databases.* PVLDB, 2017. (DataHub line; Bhardwaj et al., CIDR 2015.) — [DOI](https://doi.org/10.14778/3115404.3115417)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases* (chase, tgds/egds, undecidability of implication). Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Old schema has `Emp(name, dept)` with one tuple $e_1 = (\text{Ann}, \text{Sales})$, annotated $x_1 \in \mathbb{N}[X]$. A view $V = \pi_{\text{dept}}(\text{Emp})$ produced output tuple $(\text{Sales})$ with provenance polynomial $p = x_1$.

**Lossless evolution (rename):** the SMO `RENAME dept TO division` is a bijective mapping $m$. It induces a semiring *isomorphism* on annotations, so $\mathsf{migrate}(p,m) = x_1$ unchanged — the why/where answer ("Sales came from $e_1$") survives exactly. Invertible $\Rightarrow$ no loss.

**Lossy evolution (merge):** now `MERGE COLUMNS (dept, location) INTO site` collapses two source columns into one. Suppose $e_1=(\text{Ann},\text{Sales},\text{NYC})$ and $e_2=(\text{Bob},\text{Sales},\text{LA})$, with $V$'s tuple $(\text{Sales})$ carrying $p = x_1 + x_2$. After the merge, the target has distinct sites $\text{Sales@NYC}$, $\text{Sales@LA}$; the predicate "dept = Sales" is no longer recoverable from `site` alone. Exact migration is *impossible*. The **certain provenance** — what holds under every valid target instance — degrades to the safe under-approximation $p' = \mathbf{0}$ for the now-unanswerable query, illustrating the information-theoretic lower bound of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
