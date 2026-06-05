# Multi-Attribute Correlation Without Independence

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/multi-attribute-correlation` · **Status:** open

## 1. Problem Statement
Classical optimizers estimate the selectivity of a conjunctive predicate $\sigma_{p_1 \wedge \dots \wedge p_k}(R)$ by multiplying per-column selectivities under the **attribute value independence (AVI)** assumption. When columns are correlated (e.g., `city` and `zip`, `make` and `model`), AVI produces estimates off by orders of magnitude. The problem: build a **compact** model of the joint distribution over many (possibly all) attributes of a relation that (i) answers arbitrary conjunctive selectivity queries with bounded error, (ii) uses space and build time sub-linear or modest relative to the data, and (iii) is maintainable under updates. Variants: **point selectivity** (one conjunctive predicate), **range/aggregate** queries, and the **model-selection** variant (which subsets of columns to model jointly given a space budget).

## 2. Mathematical Foundations
Let $R$ have attributes $A_1, \dots, A_m$ with joint distribution $P(A_1, \dots, A_m)$. Selectivity of predicate $p$ is $\Pr_{P}[p]$. AVI assumes $P = \prod_i P(A_i)$. The exact joint table has size $\prod_i |\mathrm{dom}(A_i)|$ — infeasible. Compact models trade off via factorizations:
$$ P(A_1,\dots,A_m) \approx \prod_{c} \psi_c(A_{S_c}), $$
graphical-model style (Bayesian/Markov networks), where each factor $\psi_c$ ranges over a small attribute set $S_c$. The quality of a factorization is governed by **conditional mutual information** $I(A_i; A_j \mid \cdot)$ and the **treewidth** of the dependency graph; inference cost is exponential in treewidth. Alternatives: multi-dimensional histograms (partition the joint domain into buckets minimizing intra-bucket variance), kernel density estimators, and **autoregressive factorizations** $P = \prod_i P(A_i \mid A_{<i})$ learned by neural nets (deep autoregressive models). Error is typically measured in **q-error** $\max(\hat{s}/s,\, s/\hat{s})$.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Learned single-table estimators dominate accuracy benchmarks — **Naru/NeuroCard** (Yang et al., VLDB 2019/2020) use deep autoregressive models with progressive sampling; **DeepDB** (Hilprecht et al., VLDB 2020) uses sum-product networks (relational SPNs) giving fast, interpretable joint models; **FLAT** and **FACE** (normalizing-flow density) push accuracy further. Classical SOTA: multi-dimensional histograms (GENHIST, STHoles — self-tuning from query feedback) and **column-group statistics** as shipped in commercial systems (e.g., Microsoft SQL Server multi-column stats, Oracle extended statistics). Graphical-model estimators (BayesCard, Wu et al.) revive PGM inference with modern learning.

## 4. Upper Bound
For a fixed factorization of bounded treewidth $w$, exact selectivity inference is $O(m \cdot d^{w})$ where $d$ bounds per-attribute domain in a bucketized representation — polynomial for constant $w$. Autoregressive models answer a conjunctive query by progressive/importance sampling with cost linear in $m$ and the sample size; variance bounds give probabilistic error guarantees but no worst-case q-error bound. STHoles refines buckets to drive observed error down with query feedback, with space bounded by a bucket budget.

## 5. Lower Bound
There is no free lunch: representing an arbitrary joint distribution to within multiplicative error $\epsilon$ on all conjunctive queries requires space exponential in the number of jointly-correlated attributes in the worst case (an information-theoretic counting / communication argument — most distributions are incompressible). Finding the optimal bounded-treewidth structure (structure learning) is NP-hard (Chickering, for Bayesian networks). Worst-case q-error of any sub-exponential-space single-table estimator is unbounded for adversarial correlation patterns.

## 6. The Gap
The gap is between **practical accuracy on benign real data** (learned models achieve median q-error near 1 on benchmarks) and **worst-case guarantees** (none of the compact models bound q-error against adversarial correlation). No model simultaneously offers: small space, fast updates, *and* certified per-query error. Closing it likely requires hybrid models (compact factorization plus a residual/sampling correction with a tail bound) and a principled, data-adaptive choice of which correlations to capture under a space budget — an open optimization problem.

## 7. Current Research (as of June 2026)
Directions: (i) **update-friendly learned estimators** — retraining cost and drift remain the Achilles heel; incremental/online updates and concept-drift detection are active *(frontier — verify)*; (ii) **density models with error bars** (normalizing flows, diffusion-style density) that emit calibrated uncertainty (Stanford, TUM, MIT groups); (iii) **structure learning under space budgets** combining mutual-information screening with bucketization. Robustness studies (Wang et al., "Are We Ready for Learned Cardinality Estimation?", VLDB 2021) keep pressure on generalization and update behavior.

## 8. Future Work
Certified-error compact joint models; automatic column-group/correlation discovery integrated with the optimizer; lightweight maintenance under inserts/deletes; unifying single-table joint models with join estimation; and benchmarks that stress adversarial and shifting correlations rather than static snapshots.

## 9. Key References
- **[Foundational]** Poosala, Ioannidis. *Selectivity Estimation Without the Attribute Value Independence Assumption.* VLDB, 1997. — [ACM](https://dl.acm.org/doi/10.5555/645923.673638)
- **[Foundational]** Bruno, Chaudhuri, Gravano. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD, 2001. — [DOI](https://doi.org/10.1145/375663.375686)
- **[SOTA]** Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019; *NeuroCard.* VLDB, 2020. — [arXiv](https://arxiv.org/abs/1905.04278)
- **[SOTA]** Hilprecht et al. *DeepDB: Learn from Data, not from Queries!* VLDB, 2020. — [arXiv](https://arxiv.org/abs/1909.00607)
- **[SOTA]** Wu, Shaikhha, Zhu, Zeng, Han, Zhou. *BayesCard: Revitilizing Bayesian Frameworks for Cardinality Estimation.* 2020/2021. — [arXiv](https://arxiv.org/abs/2012.14743)
- **[Survey]** Wang et al. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2012.06743)

## 10. Worked Example

A `cars` relation with $n=10{,}000$ rows has attributes `make` and `model`. Say `make='Toyota'` holds for $2{,}000$ rows ($P(\text{Toyota})=0.20$) and `model='Camry'` holds for $500$ rows ($P(\text{Camry})=0.05$). The predicate is `make='Toyota' AND model='Camry'`.

**AVI estimate.** Assuming independence,
$$\hat s_{\text{AVI}}=P(\text{Toyota})\cdot P(\text{Camry})=0.20\times0.05=0.01\Rightarrow\hat c=0.01\times10{,}000=100.$$

**Truth under correlation.** A Camry is *always* a Toyota, so every one of the $500$ Camry rows has `make='Toyota'`: $c=500$, $s=0.05$. The functional dependency `model → make` makes the two columns maximally correlated, so $P(\text{Toyota}\mid\text{Camry})=1\ne P(\text{Toyota})=0.20$.

**Error.** $\mathrm{qerr}=\max(100/500,\,500/100)=5$ — a 5× under-estimate from a single 2-column correlation. A compact joint model that stores the factor $\psi(\text{make},\text{model})$ over just this correlated pair (a 1-bucket column-group statistic recording $P(\text{Camry, Toyota})=0.05$) recovers $\hat c=500$ exactly. The combinatorial blow-up the field worries about appears only when *many* attributes are mutually correlated, forcing factors over large $S_c$ whose inference cost grows as $d^{w}$ in the treewidth $w$.

---
*Part of the [DBMS Research catalog](../../README.md).*
