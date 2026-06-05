# Compression-Aware Query Optimization

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/compression-aware-optimization` · **Status:** open

## 1. Problem Statement

Build a query optimizer in which **encoding/compression is a first-class physical property** — like sort order or partitioning — that influences operator selection, cost estimation, and plan enumeration. The optimizer must reason about plans where some operators execute on compressed/coded data (cheap) and others force decompression (expensive), and where the **output encoding** of one operator is the input property of the next.

- **Optimization variant:** Over the plan search space, find the minimum-cost plan when each operator's cost depends on the encoding of its inputs and it may **preserve, transform, or destroy** that encoding.
- **Decision variant:** Does a plan with cost $\le C$ exist under encoding-aware cost functions?
- **Property-tracking variant:** Correctly propagate "interesting encodings" through the plan (analogous to interesting orders) without exploding the search space.

## 2. Mathematical Foundations

Extend the System-R / Cascades framework: a plan is searched over **(logical expression, physical properties)** where physical properties now include $\langle \text{sort}, \text{partition}, \text{encoding}\rangle$. Encoding-transparency of operators (from the *direct-computation-on-compressed* problem) defines a property-derivation relation $\Rightarrow_E$. The optimizer's DP recurrence becomes

$$
\mathrm{best}(G, p) = \min_{\text{impl }o,\ \text{children props } q}\ \mathrm{cost}_o(q \to p) + \sum_{c}\mathrm{best}(G_c, q_c),
$$

where $p$ now ranges over encoding properties as well. "Interesting encodings" play the role Selinger's **interesting orders** play, and **enforcer** operators (decode, re-encode) are added like sort enforcers. The cost model needs encoding-dependent operator costs grounded in entropy (size) and decode-throughput terms.

Plan search with multiple physical properties is a generalization of optimal join ordering — **NP-hard**, and the encoding dimension multiplies the property lattice.

## 3. State of the Art (SOTA)

- **Foundational:** Selinger (interesting orders, 1979); Graefe's **Cascades** framework for property-driven optimization (1995) — the natural host for encoding as a property.
- **Systems-SOTA:** Most production column stores (Vertica, DuckDB, ClickHouse, Snowflake) treat compression mainly as a **storage/scan** concern and apply ad-hoc rules (e.g., "push selection so it runs on dictionary codes"), not full property-tracked enumeration. Vectorwise/Photon propagate dictionary/selection-vector state through pipelines but without a complete cost-based encoding optimizer.
- No mainstream optimizer enumerates plans with **encoding as a fully cost-modeled, enforced physical property** end to end.

## 4. Upper Bound

Given a fixed finite set of $E$ interesting encodings, Cascades/DP search runs in time polynomial in (#plans × $E$) — i.e., the property lattice grows by a factor $E$ over the encoding-free optimizer, which is already exponential in query size in the worst case but practical with memoization and pruning. For **fixed-treewidth** query graphs, the encoding-aware DP remains FPT in treewidth × $E$.

## 5. Lower Bound

Encoding-aware plan optimization is **NP-hard**, inheriting hardness from join-order optimization with physical properties (Ibaraki–Kameda / Cluet–Moerkotte style results show even restricted join-ordering with cost interactions is NP-hard). Adding encoding enforcers strictly enlarges the property lattice, so hardness is preserved and the constant blow-up is genuine. No sub-quadratic or polynomial exact algorithm is expected for general query graphs; no fine-grained conditional separation specific to the encoding dimension is yet established.

## 6. The Gap

**Open.** The framework (Cascades + properties) tells us *how* to incorporate encoding, but two things are missing: (1) a **validated cost model** mapping (encoding, operator) → time that is accurate enough to drive plan choice, and (2) **pruning theory** that keeps the $E$-fold property blow-up tractable while retaining optimality. Closing the gap means a principled set of "interesting encodings" (provably sufficient to not miss the optimal plan) plus calibrated costs.

## 7. Current Research (as of June 2026)

- Treating **dictionary/RLE state** as a propagated property so group-by and joins stay coded for as long as possible *(frontier — verify)*.
- **Learned cost models** that predict decode-vs-direct execution cost per operator and encoding, feeding the optimizer *(frontier — verify)*.
- Joint optimization of encoding selection, materialization timing, and plan choice as one problem.
- Groups: TUM (Neumann — optimizer/codegen), CMU (Pavlo), CWI/DuckDB, Snowflake/Databricks query-engine teams.

## 8. Future Work

- A "sufficiency" theorem for interesting encodings (analogue of interesting-orders completeness).
- Robust, learning-augmented encoding-aware cost models with error bounds.
- Unified physical-design + optimization that picks encodings and plans together.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Engineering Bulletin, 1995. — [DBLP](https://dblp.org/rec/journals/debu/Graefe95a.html)
- **[Foundational]** Abadi, Madden, Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)
- **[SOTA]** Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* PVLDB, 2011. — [DOI](https://doi.org/10.14778/2002938.2002940)
- **[Survey]** Abadi, Boncz, Harizopoulos, Idreos, Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Query: `SELECT region, SUM(sales) FROM T GROUP BY region`, where `region` is dictionary-encoded (codes 0..49) and `sales` is FOR/bit-packed. Two candidate plans, both costed with encoding as a physical property (§2):

- **Plan A (encoding-aware):** group-by hashes the integer *codes* directly, deferring the dictionary lookup to one final decode of $\le 50$ group keys. Cost $\approx z$ scan + $50$ decodes.
- **Plan B (decode-first):** an enforcer decodes `region` to strings up front, then hashes wide string keys. Cost $\approx z$ scan + $n$ decodes + wider hashing.

With $n = 10^7$ rows, Plan A does $\sim 50$ decodes vs Plan B's $\sim 10^7$ — a $10^5\times$ gap. The optimizer only finds Plan A if "dictionary-coded" is tracked as an *interesting encoding* and the group-by is modeled as encoding-preserving (the §6 property-tracking gap). Adding the encoding axis multiplies the property lattice by the number $E$ of interesting encodings, preserving the NP-hardness of plan search (§5).

---
*Part of the [DBMS Research catalog](../../README.md).*
