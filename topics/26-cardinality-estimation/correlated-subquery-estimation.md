# Correlated Predicates Across Subqueries

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/correlated-subquery-estimation` · **Status:** open

## 1. Problem Statement
Estimate the selectivity / output cardinality of queries containing **correlated and nested subquery predicates**, e.g.
```sql
SELECT * FROM R WHERE EXISTS (SELECT 1 FROM S WHERE S.k = R.k AND S.a < R.b)
```
or `IN`/`NOT IN`/`ANY`/`ALL`/scalar-subquery comparisons. The outer-row predicate's truth depends on an *inner aggregate or existence test* whose selectivity varies **per outer row** and is **correlated** with outer attributes.

Variants:
- **Estimation variant:** predict $\Pr_{r\sim R}[\text{subquery predicate holds for } r]$ and the join/semijoin output size.
- **Decision variant:** is the predicate selective enough to justify decorrelation/unnesting into a (semi/anti)join vs. nested-loop evaluation?
- **Counting variant (exact):** counting query answers with nested aggregation, generally `#P`-hard in the query.

The crux: correlation operates **across the subquery boundary**. After the standard *unnesting* transformation (subquery → semijoin/antijoin/groupby-join), the resulting plan's cardinality depends on **cross-relation, multi-attribute correlation** that per-relation statistics cannot see.

## 2. Mathematical Foundations
A correlated subquery is, semantically, a **semijoin** $R \ltimes_\theta S$ (for `EXISTS`), an **antijoin** $R \rhd S$ (for `NOT EXISTS`), or a **grouped join** (for aggregate subqueries). Selectivity of $R\ltimes_\theta S$ is
$$ s = \Pr_{r}\big[\exists\, s\in S:\ \theta(r,s)\big], $$
which is **not** a product of marginal selectivities — it depends on the per-key match distribution (degree distribution of the join). Under independence/uniformity the optimizer approximates it, but real data violates this (skewed keys, correlated filter and join columns).

Two formal anchors:
- **AGM / fractional-cover bounds** upper-bound the *materialized* join $R\bowtie S$ size; the semijoin is at most $|R|$ but its true value depends on the *coverage* of $S$ over $R$'s keys.
- **Counting complexity:** evaluating (and thus exactly counting) nested/correlated queries with aggregation is **`#P`-hard** in general (Provan–Ball; counting conjunctive query answers is `#P`-complete), so exact cardinality is intractable and approximation is forced.

The error of plug-in estimators compounds **multiplicatively** through the nesting depth — a classic source of catastrophic underestimation in optimizers.

## 3. State of the Art (SOTA)
**Systems-SOTA:** the dominant technique is **subquery unnesting / decorrelation** (Kim 1982; Dayal 1987; Neumann–Kemper "Unnesting Arbitrary Queries," BTW 2015) which rewrites correlated subqueries into joins/semijoins so that *standard join-cardinality estimation* applies — pushing the problem onto join estimation (still hard under correlation). Magic-set rewriting and **sideways information passing** propagate bindings and tighten estimates.

**Theory/learning-SOTA:** learned join-cardinality estimators (**MSCN**, Kipf et al., CIDR 2019; **Naru/NeuroCard**; **Flow-Loss / robust learned CE**) that featurize the full (decorrelated) join graph and predict cardinality end-to-end, implicitly capturing cross-relation correlation seen at training time. **Pessimistic/bound-based estimation** (Cai et al., SIGMOD 2019; "safe" upper bounds via degree sequences) gives *guaranteed* upper bounds on join output that are robust for plan selection.

## 4. Upper Bound
Once unnested, the semijoin/antijoin output is bounded by $\min(|R|, |R\bowtie S|)$ and the join itself by the **AGM bound** $\prod_e |R_e|^{x_e}$ — computable in closed form from cardinalities. Pessimistic bound-based estimators compute provable upper bounds in time near-linear in the synopsis size. Sampling-based estimation (evaluate the subquery on a sample of outer rows) gives additive-$\varepsilon$ selectivity in $O(\varepsilon^{-2})$ outer samples, each costing one subquery probe.

## 5. Lower Bound
- **Exact counting:** `#P`-hard for general nested/correlated conjunctive queries with aggregation (Provan–Ball; Dalvi–Suciu for probabilistic variants), ruling out efficient exact cardinality.
- **From-marginals impossibility:** cross-relation correlation between the subquery's join key and the outer filter is invisible to per-relation synopses; no estimator using only single-relation statistics can avoid worst-case multiplicative error $\Omega(|S|)$ on the semijoin coverage.
- **Communication:** estimating semijoin/join size when $R$ and $S$ are summarized separately inherits the $\tilde\Omega(\sqrt n)$ communication lower bound for join-size estimation.

## 6. The Gap
**Open.** Even after decorrelation reduces the problem to join estimation, the underlying *correlated multi-relation join-size* estimation has no tight, compact-synopsis solution (see the synopsis-limits problem). Specific to subqueries, there is no principled estimator for the *per-outer-row varying* selectivity of correlated aggregate subqueries; systems rely on unnesting + independence heuristics and absorb large errors. Closing the gap means either a join-aware synopsis capturing key/filter correlation or a proof that compact synopses cannot.

## 7. Current Research (as of June 2026)
- **Learned cardinality for full query graphs** including (anti/semi) joins, with emphasis on robustness and bounded over/under-estimation (Flow-Loss, robust MSCN successors) *(frontier — verify)*.
- **Pessimistic / guaranteed-bound estimators** extended to semijoins, antijoins, and nested aggregation, prized because plan-robustness matters more than point accuracy.
- **Decorrelation-aware optimization** (Neumann/Kemper lineage) integrating estimation directly into the unnesting rewrite.
- **Factorized / FAQ-AI** approaches that compute aggregates over joins without materialization, yielding exact or tightly-bounded subquery cardinalities for restricted (acyclic, bounded-width) cases.

## 8. Future Work
- Synopses that capture cross-relation correlation between join keys and local filters.
- Tight approximation/hardness dichotomy for correlated-subquery selectivity by query structure (acyclicity, treewidth, fractional hypertree width).
- Error-propagation models bounding compounded estimation error through nesting depth.
- Robust (bounded-error) estimators that guarantee plans never blow up, even when point estimates are off.

## 9. Key References
- **[Foundational]** W. Kim. *On Optimizing an SQL-like Nested Query.* ACM TODS, 1982. — [DOI](https://doi.org/10.1145/319732.319745)
- **[Foundational]** U. Dayal. *Of Nests and Trees: A Unified Approach to Processing Queries That Contain Nested Subqueries, Aggregates, and Quantifiers.* VLDB, 1987. — [DBLP](https://dblp.org/rec/conf/vldb/Dayal87.html)
- **[SOTA]** T. Neumann, A. Kemper. *Unnesting Arbitrary Queries.* BTW, 2015. — [DBLP](https://dblp.org/rec/conf/btw/0001K15.html)
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** W. Cai, M. Balazinska, D. Suciu. *Pessimistic Cardinality Estimation.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[Foundational]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018. — [arXiv](https://arxiv.org/abs/1203.1952)

## 10. Worked Example

Take `SELECT * FROM R WHERE EXISTS (SELECT 1 FROM S WHERE S.k = R.k)`, the semijoin $R \ltimes S$. Let $|R| = 100$ with key column $k$ taking values $\{1,\dots,10\}$, $10$ rows each. Suppose $S$ has $50$ rows but every $S.k = 1$ (extreme skew). The true answer: only $R$'s $10$ rows with $k=1$ survive, so $|R \ltimes S| = 10$.

Now watch a typical optimizer estimate. It treats the semijoin selectivity as the fraction of $R$-keys that appear in $S$. Assuming **uniformity** over $S$'s distinct keys, it sees $|\pi_k(S)|$ — and if its NDV estimate for $S.k$ is, say, $5$ (sampling missed the total skew), it guesses $5/10 = 0.5$ of $R$'s distinct keys match, predicting $\hat{c} = 0.5 \times 100 = 50$.

True $= 10$, estimate $= 50$: a $5\times$ over-estimate, q-error $5$. The error is entirely in the **degree distribution** of $S.k$ — invisible to a per-relation NDV synopsis. If three such correlated subqueries nest, the multiplicative model gives end-to-end q-error up to $5^3 = 125$, the catastrophic blow-up Section 2 warns about.

---
*Part of the [DBMS Research catalog](../../README.md).*
