# Wide-Table and Sparse-Column Storage

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/wide-sparse-column-storage` · **Status:** open

## 1. Problem Statement
Analytical tables increasingly have **thousands to tens of thousands of columns** (ML feature stores, ad-tech event tables, IoT/observability, EAV-derived schemas), most of which are **NULL/absent for most rows** (sparsity often >95%). Naïve dense columnar storage allocates a physical column per attribute, wasting space (NULL bitmaps, file handles, metadata) and slowing planning, schema evolution, and per-column I/O.

The problem: design **storage and access methods** that (a) store sparse wide tables compactly, (b) allow fast projection of an arbitrary subset of $k$ columns out of $m\gg k$, (c) support schema evolution (adding columns is cheap), and (d) keep metadata/catalog overhead sublinear in $m$.

Variants:
- **Decision:** does row $r$ have a value for column $c$ (presence)?
- **Optimization:** choose a physical layout (dense-per-column vs. key-value "flexible" columns vs. column groups) minimizing total cost over a query workload.
- **Counting:** number of non-null cells / distinct columns touched.

## 2. Mathematical Foundations
A sparse wide table is a partial matrix $M \in (\mathcal{V}\cup\{\bot\})^{N\times m}$ with non-null set $\Omega=\{(r,c): M_{r,c}\neq\bot\}$, $|\Omega|=\mathrm{nnz}$. The information-theoretic lower bound for storing presence is the entropy of $\Omega$: a uniformly random sparse mask of density $\rho=\mathrm{nnz}/(Nm)$ needs $\approx Nm\,H(\rho)$ bits, but **structured sparsity** (column co-occurrence, clustering) compresses far below this. The **column-grouping** problem — partition $m$ columns into groups co-stored together — is the classic **vertical partitioning** problem, NP-hard (reduces from graph partitioning / hypergraph clustering), with cost driven by per-query column **affinity** $w_{ij}=$ co-access frequency. Sparse presence is naturally a **succinct/compressed bitmap** problem: a presence matrix supports rank/select in $\mathrm{nnz}\log\frac{Nm}{\mathrm{nnz}}+o(\cdot)$ bits (CSR-like / Roaring). Wide projection relates to **set-cover / hitting** over column groups.

## 3. State of the Art (SOTA)
- **Interpreted storage / sparse columns:** Beckmann et al., *Extending RDBMSs To Support Sparse Datasets* (ICDE 2006) — interpreted "wide" tables storing only present cells.
- **Vertica Flex Tables, Snowflake VARIANT, BigQuery JSON, ClickHouse `Map`/`JSON` columns:** semi-structured "flexible" columns that materialize sub-columns on demand (schema-on-read with statistics-driven sub-columnarization).
- **Dremel / Parquet / ORC nested model:** Melnik et al., *Dremel* (VLDB 2010) — repetition/definition levels encode sparse nested fields compactly; the de-facto industrial answer for sparse, nested, evolving schemas.
- **Apache Arrow** dictionary + null-bitmap + nested/union layouts; **Procella / Capacitor** (Google) adaptive encodings.
- **Column groups / PAX-style hybrids** and feature-store systems (Feast, Tecton) layering sparse access over Parquet.

## 4. Upper Bound
Presence + values can be stored in $O(\mathrm{nnz}\log\frac{Nm}{\mathrm{nnz}} + \mathrm{nnz}\cdot \bar{b})$ bits (CSR/Roaring presence + packed values, $\bar b$ = avg value bits), with $O(\log)$ rank/select to test presence and project. Dremel-style shredding gives projection of $k$ fields in I/O proportional to those fields' encoded size, independent of $m$ — the key "only pay for columns you read" property. Materialized sub-column promotion (ClickHouse/Snowflake) makes hot sparse keys behave like dense columns. Vertical-partitioning heuristics (graph clustering on affinity) give good, not optimal, column-group layouts in polynomial time.

## 5. Lower Bound
Optimal **vertical partitioning / column grouping** is NP-hard (reduction from balanced graph partitioning and from the set-basis problem); no PTAS is known under standard cost models. Storing an arbitrary sparse mask is bounded below by $Nm\,H(\rho)$ bits information-theoretically; for *unstructured* sparsity you cannot beat this. Supporting presence queries with rank/select hits the **succinct dictionary** lower bound $\mathrm{nnz}\log\frac{Nm}{\mathrm{nnz}} - o(\cdot)$ bits (Pătraşcu, succinct rank/select). Adaptive layout that is competitive against the best static layout faces online/metrical-task-system lower bounds.

## 6. The Gap
The gap is **open and largely empirical**: industrial systems handle sparse wide tables pragmatically (Dremel shredding, VARIANT/JSON sub-columnarization), but there is no principled, workload-optimal theory tying (a) which sparse keys to promote to dense columns, (b) how to group thousands of columns, and (c) how to bound metadata/planning cost — with provable competitiveness. Optimal grouping is NP-hard, so the realistic target is **approximation / online competitiveness guarantees** and self-tuning promotion, which remain unsolved at the thousands-of-columns scale.

## 7. Current Research (as of June 2026)
- **Adaptive sub-columnarization**: automatically promoting frequently-accessed JSON/VARIANT paths to physical columns with statistics; ClickHouse dynamic columns, Snowflake's typed VARIANT pruning *(frontier — verify)*.
- **ML feature-store storage**: thousands of sparse features, point-in-time joins; research on layout co-design with training/inference access (Tecton, Feast, Hopsworks).
- **Learned / workload-aware vertical partitioning** revisited with RL.
- Groups: Google (Dremel/Capacitor lineage), CWI/DuckDB on nested + sparse encodings, CMU-DB on self-driving layout, feature-store vendors.
- Standardization of nested/sparse via **Arrow** and **Parquet v2 / Lance / Nimble (Meta)** new columnar file formats targeting wide ML tables.

## 8. Future Work
- Approximation algorithms with guarantees for column grouping at $m\sim10^4$.
- Online promotion of sparse keys with competitive-ratio bounds.
- Sublinear-in-$m$ catalog/planning structures.
- Co-design with vectorized execution so projecting $k\ll m$ columns has no $m$-dependent overhead.

## 9. Key References
- **[Foundational]** Melnik et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010.
- **[Foundational]** Beckmann, Halverson, Krishnamurthy, Naughton. *Extending RDBMSs To Support Sparse Datasets.* ICDE, 2006.
- **[SOTA]** Abadi, Madden, Hachem. *Column-Stores vs. Row-Stores: How Different Are They Really?* SIGMOD, 2008.
- **[SOTA]** *Apache Arrow / Parquet* columnar format specifications (project documentation).
- **[Foundational]** Navathe, Ceri, Wiederhold, Dou. *Vertical Partitioning Algorithms for Database Design.* ACM TODS, 1984.
- **[Survey]** Abadi, Boncz, Harizopoulos et al. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
