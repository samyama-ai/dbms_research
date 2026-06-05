# Physical layout selection for semistructured data

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/physical-layout-selection` · **Status:** empirically-open

## 1. Problem Statement
Given a collection of semistructured (JSON/BSON-like) documents with irregular, deeply nested structure, automatically choose a *physical layout* for each field (or path) that minimizes a workload cost. Candidate per-field layouts include: row-major (keep the value inline with its document), columnar (extract the path into a separate column, à la Dremel/Parquet), *shredded* relational (normalize repeated/nested groups into child tables joined by surrogate keys), and *native* opaque blob (store the subtree verbatim, parse on demand).

- **Optimization variant:** minimize expected workload cost $\sum_q f_q \cdot \mathrm{cost}(q, L)$ over a layout assignment $L$, subject to a storage budget $B$.
- **Decision variant:** does there exist $L$ with cost $\le c$ and storage $\le B$?
- **Online variant:** adapt $L$ as the workload and the document distribution drift, amortizing reorganization cost.

The difficulty is that paths are not independent: choosing to shred a repeated field changes the cost of *every* query touching its siblings and ancestors, and presence/absence of fields is itself data-dependent (schema-on-read).

## 2. Mathematical Foundations
Model the collection as a forest of labeled trees; the *schema tree* is the union of all paths $p \in P$ with a frequency (fill rate) $\phi(p) \in [0,1]$ and a repetition/definition-level distribution (Dremel's striping model). A layout is a map $L : P \to \{\text{row}, \text{col}, \text{shred}, \text{native}\}$ subject to *consistency constraints*: shredding a node forces a consistent treatment of its repeated ancestors (record/repetition levels must be reconstructable).

Cost combines scan, reconstruction (the *record assembly* automaton of Dremel), and join cost for shredded paths. The problem generalizes **vertical partitioning** and **automated physical design** (index/MV selection), both NP-hard, and is closely tied to *factorized databases* where layout = a variable order / d-tree whose cost is governed by **fractional hypertree width** $\mathrm{fhtw}$ and the information-theoretic *factorization width*. Storage of a factorized representation is $O(N^{\mathrm{fhtw}})$ and reconstruction interacts with the AGM bound.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Dremel/Parquet/ORC fix a single columnar striping; *Apache Arrow* and *DuckDB* support nested columnar. Sinew, Argo, and *NoSE* explored relational shredding of JSON. Snowflake's `VARIANT` and *Procella* use a hybrid: columnarize frequent paths, keep a residual blob for the rare "tail" — a two-class approximation to per-field selection. JSON Tiles (Durner, Leis, Neumann, SIGMOD 2021) infer frequent sub-structures and tile them into columns at load time, leaving the irregular remainder inline — the closest published automatic layout selector.
- **Theory-SOTA:** factorized databases (Olteanu–Schleich) and worst-case-optimal storage give principled cost models, but per-field discrete layout selection over irregular data has no tight algorithm.

## 4. Upper Bound
No closed-form optimal algorithm. Practical upper bounds are *greedy / cost-model-driven*: JSON Tiles and Sinew run in roughly $O(|P|\cdot N)$ to profile paths plus a per-path greedy decision, with no approximation guarantee. Restricting to independent per-field choices (ignoring cross-path coupling) makes the problem separable and solvable in $O(|P|)$ given per-path cost estimates, but the independence assumption is what makes it suboptimal. Under a *factorized* cost model, the optimal variable order over $k$ attributes is computable in $O(2^k \cdot \mathrm{poly})$ dynamic programming — exponential in path count, hence only practical for shallow schemas.

## 5. Lower Bound
The decision variant is **NP-hard** by reduction from vertical partitioning / automated index selection (which embed Knapsack and Weighted Set Cover). Coupling among paths means the cost function is non-separable and, in general, non-submodular, so greedy lacks a $(1-1/e)$ guarantee. There is no known fine-grained or info-theoretic lower bound *specific* to nested-layout selection beyond inherited NP-hardness; tightening this is open.

## 6. The Gap
We have NP-hardness on one side and unguaranteed greedy heuristics on the other. Missing: (i) a clean cost model that captures reconstruction + join coupling, (ii) an approximation algorithm with a provable ratio under a structured (e.g., submodular-after-relaxation) special case, and (iii) lower bounds explaining whether the coupling makes even constant-factor approximation hard. The gap is genuinely open and *empirical*: systems pick layouts heuristically and report wins workload-by-workload.

## 7. Current Research (as of June 2026)
Active threads: learned/cost-based tiling extending JSON Tiles to *query-adaptive* re-tiling; integration of layout selection with learned cardinality estimation over nested data; HTAP engines (Umbra, DuckDB) exploring per-column adaptive encodings that blur row/column lines. *(frontier — verify)* Reinforcement-learning layout advisors for `VARIANT`-style columns and self-reorganizing lakehouse formats are being prototyped in 2025–2026 but lack published guarantees.

## 8. Future Work
Provable-ratio approximation for the coupled objective; online/streaming layout adaptation with bounded reorg amortization; unifying factorized-DB variable-order theory with discrete per-field layout; cost models that incorporate compression and vectorized-scan effects; benchmarks with realistic irregularity (heavy-tailed path frequencies).

## 9. Key References
- **[SOTA]** Durner, Leis, Neumann. *JSON Tiles: Fast Analytics on Semi-Structured Data.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452809)
- **[Foundational]** Melnik et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920886)
- **[Foundational]** Olteanu, Schleich. *Factorized Databases.* SIGMOD Record, 2016. — [DOI](https://doi.org/10.1145/3003665.3003667)
- **[SOTA]** Tahara, Diamond, Abadi. *Sinew: A SQL System for Multi-Structured Data.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2612183)
- **[Survey]** Idreos et al. *The Periodic Table of Data Structures.* IEEE Data Eng. Bulletin, 2018. — [DBLP search](https://dblp.org/search?q=The%20Periodic%20Table%20of%20Data%20Structures%20Idreos)

## 10. Worked Example

A collection of 1000 event documents has three paths with fill rates: `user.id` ($\phi=1.0$, scalar), `tags[]` (repeated, $\phi=0.9$, avg 4 elements), and `debug.trace` ($\phi=0.02$, large blob). A workload of two queries: $q_1$ = "scan `user.id`" ($f=100$), $q_2$ = "filter on `tags[]`" ($f=20$).

Per-path layout decision under a simple cost model (cost $\approx$ bytes scanned):
- `user.id`: dense and frequently scanned. **Columnar** — $q_1$ reads one tight 1000-value column instead of parsing 1000 whole documents. Saves $\approx 100 \times (|doc| - 4\text{B})$.
- `tags[]`: repeated, fairly dense, queried. **Columnar with repetition levels** (Dremel striping) so $q_2$ avoids record assembly until needed.
- `debug.trace`: $\phi=0.02$, never queried. Columnarizing wastes space on 980 nulls. **Native blob inline** — the "tail" residual, exactly JSON Tiles' frequent/tile vs. rare/inline split.

Now the coupling bite: if a query joined `tags[]` back to its parent `user.id`, shredding `tags` into a child table would add a reconstruction join, changing `user.id`'s best layout too. That non-separability is what makes the global assignment NP-hard (section 5), so systems settle for this per-path greedy.

---
*Part of the [DBMS Research catalog](../../README.md).*
