---
id: 11-nosql-kv/schema-on-read-optimization
title: "Schema-on-Read Query Optimization"
topic: 11-nosql-kv
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Schema-on-Read Query Optimization

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/schema-on-read-optimization` · **Status:** open

## 1. Problem Statement
Schema-on-read stores (document/KV systems holding JSON, BSON, Protobuf, or opaque blobs — MongoDB, Couchbase, DynamoDB document items, Elasticsearch) impose no fixed catalog: values are heterogeneous and semi-structured, and the "schema" is discovered at query time. Classic cost-based optimization assumes a known catalog with per-column statistics (cardinalities, histograms, NDVs) and fixed physical layouts. The problem: **optimize queries over schemaless, semi-structured KV values without a fixed catalog** — i.e., choose access paths, projection pushdown, join orders, and physical operators when the structure, types, and statistics of fields must themselves be inferred and may vary per record.

- **Optimization variant:** find a min-cost plan given *uncertain/approximate* schema and statistics inferred from samples.
- **Counting/estimation variant:** estimate selectivity of path/predicate expressions (e.g., `$.a.b[*].c > 5`) over heterogeneous documents.
- **Decision variant:** does a given (possibly partial/sparse) secondary index cover a query whose predicates reference optional, possibly-absent fields?

## 2. Mathematical Foundations
Semi-structured data is modeled as **trees/forests** or edge-labeled graphs (the Object Exchange Model, OEM; Abiteboul et al.) and queried with path expressions (JSONPath, XPath-like, MongoDB query operators). The foundational theory is **queries over semistructured data and schema inference**: a "schema" becomes a **dataguide** / graph-summary (Goldman–Widom) or an inferred type. Optimization rests on (1) **cardinality/selectivity estimation** for path predicates — connecting to *graph/tree pattern* selectivity, sketches (HyperLogLog for NDV, Count-Min for frequencies), and the **AGM bound** / worst-case-optimal-join theory (Ngo–Porat–Ré–Rudra) when path queries are reframed as conjunctive/relational joins; and (2) **plan search** with the System R / Selinger dynamic-programming framework, but over an *uncertain* catalog. Type heterogeneity introduces a *union-typing* lattice; a field's "type" is a distribution over observed types, making statistics themselves random variables — selectivity estimation becomes estimation under a mixture model with sampling error bounds (Chernoff/VC-dimension generalization guarantees for the inferred schema's predictive accuracy).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** MongoDB's cost-based optimizer (since the "slot-based execution engine" and the CBO introduced in 7.x) uses sampled statistics over flexible documents; Couchbase N1QL/Analytics and AsterixDB optimize over heterogeneous JSON with adaptive plans; Snowflake/BigQuery/Spark **shred** semi-structured `VARIANT`/JSON columns into columnar sub-columns with inferred schema, then apply standard columnar CBO (the "schema-on-read meets columnar" approach). Elasticsearch infers field mappings (dynamic mapping) approximating schema-on-write. Apache Drill explicitly executes "schema-free SQL" with runtime schema discovery.
- **Theory-SOTA:** Semistructured-data foundations (Abiteboul–Buneman–Suciu, *Data on the Web*, 2000); dataguides (Goldman–Widom, VLDB 1997); JSON schema-inference (Baazizi et al., counting types/witnesses). Worst-case-optimal joins (Ngo–Ré–Rudra) underpin path-as-join optimization.

## 4. Upper Bound
The strongest practical approach: **shred-and-columnarize** — infer a (possibly sparse/union) schema from a sample, materialize frequent paths as typed columns with sketch-based statistics, and fall back to lazy parsing for rare paths; then standard cost-based optimization gives plans within the usual CBO guarantees *for the materialized part*. For path queries reframed as joins, **worst-case-optimal join** algorithms (Generic Join / Leapfrog Triejoin) achieve the AGM-bound runtime $O(\mathrm{AGM}(Q))$, optimal in the worst case. Selectivity from samples carries Chernoff-style error bounds: a sample of size $O(\epsilon^{-2}\log(1/\delta))$ estimates a predicate's selectivity within $\pm\epsilon$ w.p. $1-\delta$. No method gives end-to-end optimality guarantees when the schema itself is adversarially heterogeneous.

## 5. Lower Bound
Query optimization with a known catalog is already **NP-hard** (join-order optimization; Ibaraki–Kameda hardness for general queries), and uncertainty only enlarges the search space. Selectivity estimation over correlated heterogeneous fields inherits the known **impossibility of bounded-error multi-predicate estimation** without distributional assumptions (estimation from samples cannot beat $\Omega(\epsilon^{-2})$ sample complexity for $\pm\epsilon$ error — an information-theoretic bound). For path-pattern matching reframed as joins, the AGM bound is a matching lower bound (no algorithm beats $\Omega(\mathrm{AGM}(Q))$ in the worst case). Schema inference itself: deciding the most specific schema can be intractable for expressive schema languages (JSON Schema satisfiability/inclusion is hard), bounding what a catalog-free optimizer can know.

## 6. The Gap
**Open.** Mature optimization theory exists *given* a catalog and statistics; catalog-free optimization has strong engineering heuristics (shredding, adaptive re-optimization, sampling) but **no theory of optimization-under-inferred-schema with provable plan-quality guarantees** as a function of schema heterogeneity and sample budget. Missing pieces: (1) a robust optimization formulation where statistics are random variables with confidence intervals, yielding plans with bounded regret vs. the perfect-information optimum; (2) tight selectivity estimators for path predicates over union-typed fields; (3) principled budget allocation between schema discovery and execution. The gap is between rich relational/WCOJ theory and the absence of guarantees once the catalog is itself estimated.

## 7. Current Research (as of June 2026)
Directions: **learned cardinality estimation over JSON/semi-structured data** and learned schema inference *(frontier — verify)*; **adaptive/robust query optimization** (re-optimization mid-execution, à la Eddies/Lookahead Information Passing) applied to schemaless inputs; **WCOJ engines for document/graph paths** (e.g., systems extending Leapfrog Triejoin to nested data); columnar-shredding advances in lakehouse engines (Parquet variant/shredded-VARIANT, the open "variant shredding" specs in Apache Spark/Iceberg). Groups/people: the AsterixDB team (Michael Carey et al.), Mohamed Baazizi / Dario Colazzo (JSON schema inference), Hung Q. Ngo–Atri Rudra–Christopher Ré (WCOJ), and database-ML researchers on learned estimation (e.g., the Tübingen/MIT/CMU learned-optimizer groups).

## 8. Future Work
- Robust optimization with statistics-as-distributions and bounded-regret plan selection.
- Tight selectivity estimators for nested/union-typed path predicates with provable error.
- Sample-budget vs. plan-quality trade-off theory for schema discovery.
- Integration of WCOJ guarantees with heterogeneous, partially-typed document data.

## 9. Key References
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[Foundational]** Abiteboul, Buneman, Suciu. *Data on the Web: From Relations to Semistructured Data and XML.* Morgan Kaufmann, 2000. — [DBLP search](https://dblp.org/search?q=Data%20on%20the%20Web%20From%20Relations%20to%20Semistructured%20Data%20and%20XML)
- **[Foundational]** Goldman, Widom. *DataGuides: Enabling Query Formulation and Optimization in Semistructured Databases.* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/GoldmanW97.html)
- **[SOTA]** Ngo, Porat, Ré, Rudra. *Worst-case Optimal Join Algorithms.* JACM, 2018 (PODS 2012). — [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Baazizi, Colazzo, Ghelli, Sartiani. *Schema Inference for Massive JSON Datasets.* EDBT, 2017. — [DOI](https://doi.org/10.5441/002/edbt.2017.21)
- **[Survey]** Davoudian, Chen, Liu. *A Survey on NoSQL Stores.* ACM Computing Surveys, 2018. — [DOI](https://doi.org/10.1145/3158661)

## 10. Worked Example

A document collection holds 4 records with a heterogeneous `age` field:
`{age: 25}`, `{age: 30}`, `{age: "unknown"}`, `{}` (absent). A query filters `age > 28`. With a fixed catalog the optimizer would have a histogram; here the field's "type" is itself a distribution: $P(\text{int})=0.5$, $P(\text{string})=0.25$, $P(\text{absent})=0.25$. Only the 2 integer-typed records can satisfy `> 28`, and exactly one does, so the true selectivity is $1/4=0.25$.

Estimating this from a sample of size $n$ carries Chernoff error: to get selectivity within $\pm\epsilon=0.05$ with confidence $1-\delta=0.95$ needs $n = O(\epsilon^{-2}\log(1/\delta)) \approx \frac{\ln(1/0.05)}{2\cdot0.05^2} \approx 600$ sampled documents. The plan decision — use a sparse secondary index on `age` vs. full scan — flips depending on whether the estimate clears the index break-even selectivity (say $0.1$). Because the string/absent mass ($0.5$) never matches, ignoring type heterogeneity and assuming all 4 records are integers would overestimate selectivity at $0.5$, wrongly favoring a scan.

---
*Part of the [DBMS Research catalog](../../README.md).*
