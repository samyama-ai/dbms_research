---
id: 26-cardinality-estimation/join-crossing-correlation
title: "Join-Crossing Correlation Estimation"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Join-Crossing Correlation Estimation

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/join-crossing-correlation` · **Status:** open
> **Verification note:** FactorJoin's authors are Wu, Negi, Alizadeh, Kraska, Madden (PACMMOD/SIGMOD 2023); the §9 citation has been corrected accordingly ("Shaikhha" was not an author).

## 1. Problem Statement
Estimate the cardinality of a multi-way join with selection predicates where the **correlations span the join graph**: a predicate on one table is statistically correlated with values (and predicates) on another table reachable only through joins. The classic failure is assuming **join uniformity / predicate independence across tables** — e.g., in a star schema, filtering `dim_a.x = v` may strongly bias the distribution of join keys flowing into a fact table, but per-table statistics cannot see this. The problem: model and exploit join-crossing correlation to estimate $|\sigma_{P}(R_1 \bowtie R_2 \bowtie \dots \bowtie R_n)|$ accurately and compactly. Variants: **acyclic** vs **cyclic** join graphs; **point** vs **subquery** estimation; and the **statistics-design** variant (what cross-table statistics to materialize within a budget).

## 2. Mathematical Foundations
A join query is a hypergraph; after applying selections the relevant quantity is the size of a (semi-)join-reduced instance. Under independence assumptions the textbook estimate is
$$ |R_1 \bowtie R_2| \approx \frac{|R_1|\,|R_2|}{\max(\,|\mathrm{dom}(J)_1|,\,|\mathrm{dom}(J)_2|\,)} $$
for join attribute $J$, which ignores how a selection reshapes the *join-key distribution*. Correct estimation requires the **conditional join-key distribution** $P(J \mid \sigma_P)$ and its correlation with the partner table's key multiplicities (degree sequence). Information-theoretically, join-crossing correlation is captured by mutual information between a predicate's indicator and the partner's degree. **AGM/polymatroid bounds** bound worst case but ignore correlation sign; **sampling**-based methods (e.g., correlated/index-based sampling, *wander join* random walks) estimate join-crossing effects directly with variance controlled by join-key skew. The acyclic case admits exact factorization via the **chase / Yannakakis** semijoin reduction.

## 3. State of the Art (SOTA)
**Systems-SOTA:** No commercial optimizer models arbitrary join-crossing correlation by default; they fall back to independence plus join fanout heuristics, often with magnification of error along the plan. Research SOTA: **wander join / random-walk** estimators (Li, Wu, Yi, Zhang, SIGMOD 2016) sample join paths and give unbiased estimates with confidence intervals, directly capturing cross-table effects. **Correlated sampling** and **index-based join sampling** (Leis et al., CIDR 2017) sample with join semantics. Learned join estimators — **MSCN** (Kipf et al., CIDR 2019, multi-set convolutional networks over query encodings), **NeuroCard** (single-model over a full schema), and **graph-neural** estimators — learn cross-table correlation from a workload or from data. **Factorized / FDB** and **relational SPN** approaches (DeepDB) propagate joint structure across joins.

## 4. Upper Bound
For **acyclic** queries with materialized two-table join statistics, Yannakakis-style semijoin reduction gives exact intermediate sizes in time linear in input + output, so estimation reduces to representing pairwise conditional distributions. Sampling estimators (wander join) achieve, for $\epsilon,\delta$ accuracy, sample complexity scaling with the variance induced by join-key skew — $O(\mathrm{Var}/\epsilon^2 \log(1/\delta))$ — and run online with bounded memory. Learned estimators answer queries in time linear in the encoded query size after offline training.

## 5. Lower Bound
Estimating multi-way join size within a constant factor from samples requires, in the worst case, sample complexity polynomial in the data (heavy-key adversaries force large variance); for some join patterns any single-table-statistics estimator has unbounded multiplicative error (information-theoretic: the cross-table correlation is simply not present in the statistics). Cyclic-query intermediate sizes are governed by AGM tightness, and exact counting is #P-hard. Communication-complexity arguments lower-bound the space for streaming/distributed multi-way join size estimation.

## 6. The Gap
There is a wide, genuinely open gap. Worst-case bounds (AGM) ignore correlation direction; independence heuristics ignore it too but in the optimistic direction. Sampling captures correlation but suffers variance blow-up under skew and join-path explosion; learned methods capture it on the training workload/data but lack guarantees and degrade under drift and unseen join templates. No method offers compact, certified, correlation-aware multi-way estimates. Closing it needs cross-table statistics whose space is bounded yet whose error against adversarial correlation is controlled.

## 7. Current Research (as of June 2026)
Active: (i) **schema-level learned models** (NeuroCard, FactorJoin) that combine learned single-table joints with principled join propagation, reducing data needed and improving generalization across templates *(frontier — verify)*; (ii) **robust sampling** with variance reduction for skewed join keys and adaptive walk strategies; (iii) **hybrid bound+estimate** systems giving an optimistic learned estimate plus a pessimistic certificate. Groups: Berkeley (Stoica/RISELab lineage), TUM (Neumann/Leis), HKUST (Yi), and the learned-DB community broadly.

## 8. Future Work
Compact cross-table correlation statistics with error guarantees; integrating join-crossing estimates into plan enumeration without combinatorial cost; principled handling of cyclic queries; drift-robust learned join estimators; and benchmarks isolating join-crossing correlation (most benchmarks conflate it with single-table error).

## 9. Key References
- **[Foundational]** Yannakakis. *Algorithms for Acyclic Database Schemes.* VLDB, 1981. — [DBLP](https://dblp.org/rec/conf/vldb/Yannakakis81.html)
- **[Foundational]** Leis et al. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)
- **[SOTA]** Li, Wu, Yi, Zhang. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[SOTA]** Kipf et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** Yang et al. *NeuroCard: One Cardinality Estimator for All Tables.* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2006.08109)
- **[SOTA]** Wu, Negi, Alizadeh, Kraska, Madden. *FactorJoin: A New Cardinality Estimation Framework for Join Queries.* SIGMOD, 2023. — [arXiv](https://arxiv.org/abs/2212.05526) · [DOI](https://doi.org/10.1145/3588721)

## 10. Worked Example

A star schema: fact table $F$ (sales, 1000 rows) joins dimension $D$ (product, 10 rows) on `pid`. Query: `SELECT * FROM D JOIN F ON D.pid=F.pid WHERE D.category='luxury'`.

Suppose $D$ has $9$ `standard` products and $1$ `luxury` product (pid $= 7$). The selection keeps $1$ of $10$ rows, so $s_D = 0.1$. In $F$, the **degree** (number of sales) per product is skewed: the luxury product 7 has only $10$ sales, while the nine standard products average $110$ sales each.

The independence/uniformity estimate multiplies the filtered $D$ size by the *average* fanout: $|F|/|\text{dom(pid)}| = 1000/10 = 100$, giving
$$\hat{|\bowtie|} \approx 1 \times 100 = 100.$$
But the **true** result is $F$'s rows for pid $7$ only: $10$. The estimate is $10\times$ too high because the predicate `category='luxury'` is correlated with a *low-degree* join key — exactly the join-crossing correlation per-table stats cannot see (the fact-table degree distribution is invisible to a predicate on $D$). A wander-join random walk that starts from the qualifying $D$ row and steps to its matching $F$ tuples samples this degree directly and returns an unbiased estimate near $10$.

---
*Part of the [DBMS Research catalog](../../README.md).*
