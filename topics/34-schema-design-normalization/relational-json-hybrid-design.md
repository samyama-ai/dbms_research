# Optimal Normalize-vs-JSON Hybrid Layout

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/relational-json-hybrid-design` · **Status:** empirically-open

## 1. Problem Statement
Given a relational/document-capable DBMS (e.g., PostgreSQL with `jsonb`, SQL Server, MySQL, or a NewSQL store), a logical entity with attribute set $A$, and a workload $W$ of queries and updates with frequencies, decide for each attribute (or attribute group) whether to store it as a **first-class normalized relational column** or to **nest it inside a semi-structured JSON/document column**. The hybrid layout must minimize expected workload cost subject to constraints on storage, schema-evolution agility, and integrity guarantees.

- **Decision variant:** Does a layout exist with expected cost $\le \tau$ under cost model $C$?
- **Optimization variant:** Find the layout minimizing $\sum_{q\in W} f_q\, C(q,\text{layout})$.
- **Online/evolution variant:** Re-decide as the schema of incoming documents drifts (sparse, heterogeneous, late-arriving attributes).

The crux is that JSON columns trade write-flexibility and schema agility against read efficiency (no native column statistics, harder indexing, type erosion, predicate pushdown limits), and the optimal split is workload- and engine-dependent.

## 2. Mathematical Foundations
Model the layout as a partition/labeling $\ell: A \to \{\text{REL}, \text{JSON}\}$ (or a finer assignment to multiple JSON sub-documents). Let access cost for query $q$ decompose as
$$C(q,\ell)=\sum_{a\in \text{read}(q)} r_a(\ell(a)) + \sum_{a\in \text{write}(q)} w_a(\ell(a)) + \text{join/extract}(q,\ell),$$
where extraction cost for JSON-resident attributes includes per-tuple path navigation and deserialization. This generalizes the **attribute-partitioning** formulation and is closely related to **vertical partitioning** (see sibling problem) but with asymmetric, non-linear per-store cost functions and integrity-constraint side effects.

Key tools: cost models combine **selectivity estimation** over erased-type JSON (information loss raises estimation variance), and the choice interacts with **functional dependencies** — embedding an attribute in JSON can hide an FD from the optimizer, weakening normalization guarantees (BCNF/4NF reasoning via the **chase**). When grouping attributes into documents, co-location benefits are **supermodular** in co-access, making the assignment a non-trivial combinatorial optimization rather than independent per-attribute choices.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Hybrid storage is mainstream — PostgreSQL `jsonb` with GIN/expression indexes; SQL Server JSON + computed persisted columns; Google Spanner/F1 and Snowflake VARIANT with automatic columnar shredding of semi-structured data. Snowflake's automatic sub-column extraction and Apache Parquet/ORC nested-column shredding represent the strongest automatic relational/nested co-storage.
- **Research-SOTA:** Work on **schema-less / NoSQL-to-relational physical design** (Argo, Sinew) and on automatic **JSON shredding** ("schema inference + columnar materialization", e.g., Spark/Drill schema-on-read). Recent learned approaches predict which JSON paths to promote to virtual/materialized columns based on observed access.

There is no single accepted optimizer that jointly chooses the relational-vs-JSON split with provable guarantees; production systems rely on heuristics and DBA judgment.

## 4. Upper Bound
No general approximation guarantee is established. The natural ILP/MILP formulation is solvable to optimality only for small $|A|$. For the **restricted case** where per-attribute costs are independent (no co-location/grouping term), the problem decomposes into independent per-attribute decisions and is solvable in $O(|A|\cdot|W|)$ — a trivial exact upper bound. With grouping and supermodular co-access, the best practical "upper bound" is local-search / greedy heuristics with empirically good but unbounded ratio.

## 5. Lower Bound
With attribute grouping into a bounded number of documents and arbitrary co-access benefits, the layout problem embeds **balanced graph partitioning / hypergraph partitioning**, which is NP-hard and APX-hard in general; minimizing cross-document extraction joins is reducible from such partitioning. The independent-cost special case is polynomial, so hardness arises specifically from co-location and join-cost coupling. No fine-grained or information-theoretic lower bound specific to the hybrid choice is known; the open hardness frontier concerns whether realistic, monotone cost models admit a constant-factor approximation.

## 6. The Gap
The gap is wide and largely **empirical**: we lack (a) accepted, validated cost models that capture JSON deserialization/selectivity-estimation penalties across engines, and (b) any approximation algorithm with guarantees for the grouped formulation. Closing it requires both a canonical cost model (benchmarked against real engines) and matching algorithmic upper/lower bounds — currently neither exists, so the problem is genuinely open in practice.

## 7. Current Research (as of June 2026)
- Learned "column promotion" advisors that observe JSON-path access and auto-create materialized/virtual columns *(frontier — verify)*.
- Self-describing columnar formats (Parquet variant/shredding, BtrBlocks-style encodings) blurring the relational/nested boundary *(frontier — verify)*.
- Integration with LLM-assisted schema design suggesting hybrid layouts from natural-language requirements *(frontier — verify)*.
- Groups: CMU (Pavlo, self-driving DB line), TUM (Neumann/Kemper, columnar + adaptive storage), MIT (Madden), and cloud-warehouse vendors (Snowflake, Databricks) drive the systems frontier.

## 8. Future Work
- A canonical, engine-portable cost model for JSON extraction and selectivity estimation.
- Approximation algorithms (or hardness proofs) for the grouped supermodular formulation.
- Online re-layout under schema drift with bounded reorganization cost.
- Preserving FD/integrity guarantees when attributes migrate into JSON (chase-aware layout).
- Joint optimization with indexing and partitioning rather than in isolation.

## 9. Key References
- **[Foundational]** E. F. Codd. *A Relational Model of Data for Large Shared Data Banks.* CACM, 1970. — [DOI](https://doi.org/10.1145/362384.362685)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[SOTA]** D. Tahara, T. Diamond, D. J. Abadi. *Sinew: A SQL System for Multi-Structured Data.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2612183)
- **[SOTA]** C. Chasseur, Y. Li, J. M. Patel. *Enabling JSON Document Stores in Relational Systems (Argo).* WebDB, 2013. — [DBLP](https://dblp.org/rec/conf/webdb/ChasseurLP13.html)
- **[Survey]** M. Stonebraker, U. Çetintemel. *"One Size Fits All": An Idea Whose Time Has Come and Gone.* ICDE, 2005. — [DOI](https://doi.org/10.1109/ICDE.2005.1)
- **[SOTA]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)

## 10. Worked Example

Entity `Order` has attributes $A=\{\text{id}, \text{total}, \text{tags}\}$ and a workload $W$ of two queries:
- $q_1$ (freq $f_1=900$): `WHERE total > 100` — filters on `total`.
- $q_2$ (freq $f_2=100$): reads `tags` (a variable-length list) for display only.

Per-attribute read costs (cost units): a relational column scan costs $r_a(\text{REL})=1$; a JSON-path extraction costs $r_a(\text{JSON})=4$ (path navigation + deserialization). Compare the two pure layouts for attribute `total`:

$$C(W,\,\text{total}{=}\text{REL}) = f_1\cdot 1 = 900, \qquad C(W,\,\text{total}{=}\text{JSON}) = f_1\cdot 4 = 3600.$$

So the hot, filtered `total` belongs in a **relational** column. For `tags`, which is only displayed (never filtered) and is heterogeneous/sparse, JSON costs $f_2\cdot 4 = 400$ versus a relational normalization into a side table `OrderTag(order_id, tag)` requiring a join: say $f_2\cdot 6 = 600$. Here **JSON wins** for `tags`.

The optimal hybrid layout is $\ell=\{\text{total}\mapsto\text{REL},\ \text{tags}\mapsto\text{JSON}\}$ with total cost $900+400=1300$, beating all-REL ($900+600=1500$) and all-JSON ($3600+400=4000$). This illustrates the per-attribute, workload-driven split at the heart of the problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
