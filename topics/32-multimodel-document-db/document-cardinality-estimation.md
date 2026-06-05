# Document store cardinality estimation

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/document-cardinality-estimation` · **Status:** empirically-open

## 1. Problem Statement

Given a schemaless document collection $C = \{d_1, \dots, d_N\}$ (e.g. JSON/BSON documents) and a predicate $\varphi$, estimate the **cardinality** $|\sigma_\varphi(C)|$ — the number of documents satisfying $\varphi$ — without scanning $C$. The hard cases are predicates over *self-describing, irregular* data:

- **Path predicates:** `a.b.c = v` where path `a.b.c` is present in only a sparse subset of documents.
- **Array predicates:** `ANY x IN a.tags : x = v` (existential over a multi-valued field of variable length), plus `ARRAY_LENGTH` and array-contains-all.
- **Existence/type predicates:** `EXISTS(a.b)`, `IS_STRING(a.b)` — selectivity depends on *schema heterogeneity*, not just value distribution.

Variants:
- **Estimation (optimization):** minimize expected q-error $\max(\hat{c}/c, c/\hat{c})$ subject to a synopsis budget $S$ bits.
- **Decision:** is $|\sigma_\varphi(C)| \ge \theta$? (used for join-order pruning).
- **Counting:** exact distinct-path / distinct-value counts feeding the above.

The core difficulty: the predicate space is over a *union of (path, type)* domains where a single field name maps to multiple types and most paths are absent from most documents (extreme sparsity + skew).

## 2. Mathematical Foundations

Model a document as a finite set of **path-value pairs** $d = \{(p, v)\}$ where $p \in \mathcal{P}$ is a root-to-leaf path and $v$ a typed scalar (or an array index step in $p$). A collection induces a relation over the "universal" but mostly-null schema $\bigcup_d \mathrm{paths}(d)$.

Selectivity factorizes only under independence assumptions that *fail* here, so we need joint synopses:
- **Sampling theory:** a uniform sample of size $m$ estimates a selectivity $s$ with standard error $\sqrt{s(1-s)/m}$; sparse paths have $s \to 0$, demanding large $m$ or stratified sampling. Distinct-value (path) counting is governed by the negative results of Charikar–Chaudhuri–Motwani–Narasayya: no estimator from a sample of size $o(N)$ guarantees small ratio error on the number of distinct values.
- **Sketches:** HyperLogLog (Flajolet et al.) for distinct-path/value counts; Count-Min (Cormode–Muthukrishnan) for heavy hitters per path; AMS for join-size moments.
- **Information theory:** the minimum synopsis size to answer all path-existence queries within multiplicative error is tied to the entropy of the path-presence distribution; heavy-tailed path frequencies imply $\Omega(\log)$-many tail buckets.
- **Learned models:** treat $\hat{c}(\varphi)=f_\theta(\varphi)$; PAC/VC bounds relate generalization to the VC dimension of the predicate class (conjunctions over typed paths).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** MongoDB and Couchbase use per-index histograms + sampling; PostgreSQL's `jsonb` relies on generic MCV/histogram stats on the whole column plus functional-index stats. CockroachDB and MongoDB 7.x added query-driven histograms on extracted paths.
- **Path/value sketches:** XSketch and StatiX (XML, Polyzotis–Garofalakis, SIGMOD 2002–2006) pioneered synopses over labeled-tree data — the closest principled prior art for nested/path selectivity.
- **Learned-SOTA:** deep cardinality estimators (MSCN, Kipf et al. 2019; NeuroCard; query-driven models) adapted to extracted JSON paths; data-driven models (Naru/DeepDB, Yang et al. / Hilprecht et al. 2019–2020) over flattened path tables.
- **Sample-driven:** Wander Join / index-based AGM sampling for join cardinalities reused per-path.

## 4. Upper Bound

For a *single* path predicate, an equi-depth histogram over the extracted column gives q-error bounded by the within-bucket value skew, using $O(B)$ space; per-path HLL gives distinct counts with relative error $1.04/\sqrt{k}$ using $k$ registers (Flajolet et al.). For conjunctions, the **AGM bound** upper-bounds join/intersection cardinality from per-path degree statistics, computable in time linear in the query. Learned estimators achieve median q-error near 1.x on benchmarks but with **no worst-case guarantee**. Overall: no algorithm is known to guarantee bounded q-error for arbitrary path+array+type conjunctions within sublinear synopsis space.

## 5. Lower Bound

- **Distinct-value hardness (Charikar et al., PODS 2000):** estimating the number of distinct values/paths to within ratio $\le \alpha$ requires sampling $\Omega(N/\alpha^2)$ documents in the worst case — sparse-path counts are provably hard from samples.
- **Communication complexity:** distinct-elements / set-disjointness reductions give $\Omega(1/\epsilon^2)$ space lower bounds for $\epsilon$-accurate frequency-moment sketches.
- **Independence failure:** without joint stats, multiplying per-path selectivities can be off by factors exponential in predicate length (folklore; provable on adversarial correlated paths).

## 6. The Gap

For single-path scalar predicates the gap is essentially **closed** (histograms + HLL match the sampling lower bounds). For **multi-path conjunctions, array-existential, and type-heterogeneous** predicates the gap is **genuinely open**: learned methods do well empirically but lack any error guarantee, while provable methods either cost $\Omega(N)$ samples (distinct sparse paths) or assume independence. Closing it requires either (a) a synopsis with a provable q-error bound for typed-path conjunctions in sublinear space, or (b) a matching impossibility showing no such synopsis exists.

## 7. Current Research (as of June 2026)

- Query-driven histograms on auto-extracted paths shipping in MongoDB, CockroachDB, Couchbase.
- Learned multi-model estimators that condition on *(path, type)* tokens rather than columns *(frontier — verify)*.
- Robustness/q-error-bounded learned CE (Negi et al. flow-loss line) extended to nested data *(frontier — verify)*.
- Groups: Stanford/UW data-systems (Kraska, Suciu), CWI (Boncz) on JSON-in-columnar stats, EPFL/TUM (Neumann) optimizer integration.

## 8. Future Work

- Joint synopses capturing path-correlation (graphical-model or tensor-sketch over the path lattice).
- Worst-case q-error guarantees for array-existential and type predicates.
- Online/incremental stats under schema drift; concept-drift detection for learned estimators.
- Benchmarks: a standardized skewed-sparse JSON cardinality benchmark (currently missing).

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimation Error Guarantees for Distinct Values.* PODS, 2000.
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* AofA, 2007.
- **[SOTA]** Polyzotis, Garofalakis. *XSKETCH Synopses for XML Data Graphs.* ACM TODS, 2006.
- **[SOTA]** Kipf, Kemper, et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019.
- **[SOTA]** Hilprecht et al. *DeepDB: Learn from Data, not from Queries.* VLDB, 2020.
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* FnT Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
