# Benchmarks and theory for schema flexibility

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/schema-flexibility-benchmarks` · **Status:** open

## 1. Problem Statement
Document/multi-model systems sell *schema flexibility* — "schema-on-read" (store heterogeneous JSON now, impose structure at query time) versus the relational "schema-on-write" (enforce structure on ingest). Practitioners pick between them by folklore. The problem is to produce a **principled, quantitative theory and benchmark** that measures the *cost–benefit tradeoff* of schema flexibility along its real axes: ingest/evolution agility, storage overhead, query performance, and the probability and cost of data-quality defects.

Variants:
- **Metric design (definitional):** define a measure $\mathrm{Flex}(D,W)$ for a dataset $D$ and workload/evolution stream $W$ that is comparable across systems and predictive of real costs.
- **Optimization:** given an evolving workload, choose the point on the schema-on-read↔schema-on-write spectrum (including partial schemas, schema "hints," and per-collection enforcement) that minimizes total cost.
- **Benchmark construction (empirical):** a workload generator with controllable schema heterogeneity, drift rate, and evolution events that exposes the tradeoff — analogous to what TPC-C/TPC-H/YCSB did for OLTP/OLAP/KV but for *schema dynamics*.

The problem is open: no accepted metric, and existing benchmarks (YCSB, LinkBench, TPC-*) hold schema essentially fixed.

## 2. Mathematical Foundations
The tradeoff is fundamentally **information-theoretic and economic**:
- **Schema as compression / MDL:** a schema is a model; storing data plus schema costs $L(\text{schema}) + L(\text{data}\mid\text{schema})$ bits (Rissanen's Minimum Description Length). Rigid schemas minimize per-record cost when data is homogeneous; heterogeneous data inflates $L(\text{data}\mid\text{schema})$ via NULLs/exceptions. A natural flexibility metric is the *redundancy* $R = L_{\text{rigid}} - L_{\text{flexible}}$ relative to the data's entropy $H(D)$.
- **Schema entropy / heterogeneity:** treat each document's "shape" (set of paths/types) as a random variable; the entropy $H(\text{shape})$ and the number of distinct shapes quantify how much a single fixed schema must waste.
- **Cost model:** let $C_{\text{ingest}}, C_{\text{query}}, C_{\text{evolve}}, C_{\text{defect}}$ be expected costs; schema-on-write trades higher $C_{\text{ingest}}+C_{\text{evolve}}$ for lower $C_{\text{query}}+C_{\text{defect}}$. The optimum is an argmin over a policy space; under stochastic workloads this is a Markov decision / online-decision problem.
- Foundations also draw on **schema inference / typing for JSON** (e.g., JSON Schema witness/typing results, Baazizi–Colazzo–Ghelli–Sartiani's schema inference) to make "the inferred schema" a well-defined object.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** JSON schema inference and "schema profiling" (Baazizi et al.; Klettke–Störl–Scherzinger on schema extraction and evolution) give algorithms to *summarize* heterogeneity, and MDL/typing frameworks exist — but no unified flexibility metric tying them to cost.
- **Systems-SOTA:** Benchmarks adjacent to the problem include **YCSB** (KV/document throughput), **NoBench** and the **UniBench** multi-model benchmark (Zhang et al.), and document-store-specific suites; schema-evolution tooling (Darwin, MongoDB's flexible schema validation, PostgreSQL `jsonb` + partial relationalization) addresses pieces. None isolates and *scores* schema flexibility as the primary dimension.

## 4. Upper Bound
There is no algorithmic "upper bound" in the usual sense because the metric is undefined; the closest positive results are **computable approximations**: schema/shape inference runs in near-linear time in the corpus size (single-pass shape aggregation), and MDL-based schema selection is tractable for restricted schema classes (e.g., choosing which optional fields to promote to columns is a submodular/knapsack-style selection solvable greedily with constant-factor guarantees under submodular cost). So the *measurement* primitives are efficient; the *predictive validity* of any metric is the open question.

## 5. Lower Bound
- Choosing an **optimal relational decomposition / which fields to columnize** to minimize storage+query cost is **NP-hard** in general (it subsumes attribute-partitioning / vertical-partitioning problems known to be NP-hard).
- **Information-theoretic floor:** no representation can store dataset $D$ in fewer than $H(D)$ bits; thus any schema's overhead is lower-bounded by $L(\text{repr}) - H(D) \ge 0$, giving an unavoidable cost to enforcing a wrong (over-rigid) schema on heterogeneous data.
- A *predictive* lower bound — proving any cheap-to-compute statistic cannot predict real workload cost without bounded error — is itself open and would likely be a no-free-lunch / distribution-dependent statement.

## 6. The Gap
This is genuinely **open and largely pre-formal**: the gap is the absence of (a) a validated metric and (b) a benchmark that the community agrees measures the right thing. Unlike a closed bounds problem, closing this means *defining the question well*: a flexibility metric with demonstrated predictive validity across real systems, plus a generator producing reproducible, parameterized schema-dynamics workloads. The deepest open piece is connecting the information-theoretic ideal (MDL/entropy) to *operational* cost (defects, evolution effort) — these live in different units and no accepted exchange rate exists.

## 7. Current Research (as of June 2026)
- Schema-evolution and schema-extraction research (Störl, Scherzinger, Klettke groups) continues, increasingly with NoSQL-to-relational migration cost models *(frontier — verify which 2025–2026 benchmarks formalize a flexibility score)*.
- Multi-model benchmarking (UniBench lineage) is being extended toward schema heterogeneity as a first-class knob.
- "Lakehouse" schema-evolution semantics (Delta/Iceberg/Hudi schema-on-read with enforced contracts) are pushing the relational community toward exactly this tradeoff, motivating measurement.

## 8. Future Work
- A reference **flexibility metric** validated against real ingest/evolution/defect costs, with confidence intervals.
- A parameterized **schema-dynamics benchmark** (drift rate, shape entropy, evolution-event distribution) with a standard scoring rule.
- Online policies that *adapt* the schema enforcement point as a workload's heterogeneity changes, with regret bounds.
- Linking MDL-optimal schemas to data-quality outcomes (defect probability as a function of enforcement).

## 9. Key References
- **[Foundational]** J. Rissanen. *Modeling by Shortest Data Description (MDL).* Automatica, 1978. — [DOI](https://doi.org/10.1016/0005-1098(78)90005-5)
- **[Foundational]** E. F. Codd. *A Relational Model of Data for Large Shared Data Banks.* CACM, 1970. — [DOI](https://doi.org/10.1145/362384.362685)
- **[SOTA]** M. A. Baazizi, D. Colazzo, G. Ghelli, C. Sartiani. *Parametric Schema Inference for Massive JSON Datasets.* VLDB Journal, 2019. — [DOI](https://doi.org/10.1007/s00778-018-0532-7)
- **[SOTA]** C. Zhang, J. Lu, et al. *UniBench: A Benchmark for Multi-Model Database Management Systems.* TPCTC, 2018. — [DOI](https://doi.org/10.1007/978-3-030-11404-6_2)
- **[Survey]** M. Klettke, U. Störl, S. Scherzinger, et al. *Schema Evolution and Schema Extraction in NoSQL Databases.* (schema-management survey line), 2015–2021. — [DBLP search](https://dblp.org/search?q=Klettke+St%C3%B6rl+Scherzinger+schema+evolution+NoSQL)
- **[SOTA]** B. F. Cooper, A. Silberstein, E. Tam, R. Ramakrishnan, R. Sears. *Benchmarking Cloud Serving Systems with YCSB.* SoCC, 2010. — [DOI](https://doi.org/10.1145/1807128.1807152)

## 10. Worked Example

A tiny collection $D$ of 4 user documents with two "shapes":

- 3 docs: `{id, name, email}` (shape $A$)
- 1 doc: `{id, name, phone}` (shape $B$)

**Shape entropy.** With $p_A = 3/4, p_B = 1/4$:
$$H(\text{shape}) = -\tfrac34\log_2\tfrac34 - \tfrac14\log_2\tfrac14 \approx 0.81 \text{ bits/doc}.$$
Low entropy ⇒ data is *nearly* homogeneous, so a rigid schema wastes little.

**Schema-on-write cost (MDL view).** Force one relational schema `{id, name, email, phone}`. Each doc now stores one NULL for its missing column: 4 NULLs total. The rigid encoding pays $L(\text{schema}) + L(\text{data}\mid\text{schema})$ where the $4 \times$ NULL overhead is the redundancy $R$.

**Schema-on-read cost.** Store each doc as-is (no NULLs), but every query filtering on `email` must handle docs lacking the field, raising $C_{\text{query}} + C_{\text{defect}}$.

The flexibility metric $\mathrm{Flex}(D,W)$ should reward schema-on-read here (small $H$, few NULLs) only if the *workload* $W$ rarely queries the variant fields. If $H(\text{shape})$ rose toward $\log_2(\#\text{shapes})$, the rigid schema's NULL waste would dominate — exactly the tradeoff a principled benchmark must score.

---
*Part of the [DBMS Research catalog](../../README.md).*
