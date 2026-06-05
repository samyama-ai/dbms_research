# Unbiased Sampling Over Joins

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sampling-over-joins` · **Status:** partially-solved

## 1. Problem Statement
Given base relations $R_1,\dots,R_k$ and a (possibly cyclic) conjunctive query $J = R_1 \bowtie R_2 \bowtie \cdots \bowtie R_k$, produce a sample $S$ of the join output such that an aggregate estimator $\hat\theta$ computed on $S$ is **unbiased** ($\mathbb{E}[\hat\theta]=\theta$) and has low variance, **without materializing** $J$ — whose size can be quadratic to exponential in the input. Variants: (i) **uniform** sampling, each output tuple equally likely; (ii) **weighted / measure-biased** sampling, probability proportional to the aggregation measure to minimize estimator variance; (iii) the **online / streaming** variant, where samples are drawn incrementally with running error bounds. The core obstacle: a uniform sample of each base relation does **not** induce a uniform sample of the join, because join multiplicities correlate with key frequencies, so naive per-table sampling is both biased and high-variance.

## 2. Mathematical Foundations
Let $|J|$ be the true join size. The **AGM bound** (Atserias–Grohe–Marx) caps worst-case output: $|J| \le \prod_e |R_e|^{x_e}$ for any fractional edge cover $\{x_e\}$ of the query hypergraph, and **worst-case-optimal join** algorithms (NPRR, Generic-Join) meet it. Unbiased samplers reuse this structure via **degree statistics** $d_i(v)=|\{t\in R_i : t.\text{key}=v\}|$. For a two-table join, drawing $t_1\in R_1$ with probability $\propto d_2(t_1.\text{key})$ then a uniform match in $R_2$ gives a uniform output tuple (the **Olken** scheme), and the **Horvitz–Thompson** estimator
$$\hat\theta=\frac1n\sum_{i=1}^n \frac{f(o_i)}{p(o_i)},\qquad \mathbb{E}[\hat\theta]=\theta$$
is unbiased. For multi-way joins, **random-walk sampling** (Wander-Join) walks a join path $t_1\!\to\!t_2\!\to\!\cdots$ and records the inverse path probability $p=\prod_j 1/|\Gamma_j|$ as the HT correction. Variance is governed by the second moment $\mathbb{E}[(f/p)^2]$, which blows up under skew; measure-biased weights minimize it. Exact weights require full degree indexes; approximate weights use the fractional-cover LP.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Chen & Yi, *Random Sampling and Size Estimation Over Cyclic Joins* (ICDT 2020), and the Deng–Kim–Ngo–Nguyen–Olteanu line give near-optimal expected-time samplers tied to the AGM/fractional-cover bound: for any conjunctive query a uniform sample is drawn in $\tilde O(\text{AGM}/\max(1,\text{OUT}))$ after near-linear preprocessing. Recent work extends this to join-project (existential) queries.
- **Systems-SOTA:** **Wander-Join / XDB** (Li, Wu, Yi, Zhang, SIGMOD 2016) — online index-assisted random walks with running CIs; **RippleJoin** and online aggregation for streaming joins; commercial AQP layers add join-correction on top of `TABLESAMPLE`. Learned/ML join samplers exist but lack worst-case guarantees.

## 4. Upper Bound
In the RAM model with preprocessing, a single uniform output tuple of an acyclic CQ is drawn in expected $O(\text{AGM}/\max(1,\text{OUT}))$ time after $\tilde O(\text{IN})$ preprocessing (Zhao–Christensen–Li–Yi–Wu, SIGMOD 2018; Chen–Yi 2020). For cyclic queries the cost matches AGM up to polylog factors. Online Wander-Join gives an unbiased estimate with variance decreasing as $O(1/n)$ in the number of successful walks; with index support each walk costs $O(k\log n)$.

## 5. Lower Bound
Any uniform sampler must spend $\Omega(\text{AGM}/\text{OUT})$ expected time in the worst case, because producing even one sample certifies a nonempty join, and AGM-tightness instances force this work (information-theoretic / fractional-cover argument). Conditional hardness: exact join-size estimation under SETH inherits the lower bounds of WCOJ — sub-AGM enumeration is impossible for instances meeting the bound. Variance lower bounds for fixed-budget HT estimators follow from Cauchy–Schwarz on the skew of $f/p$.

## 6. The Gap
For **acyclic** queries the gap is essentially **closed** (matching AGM-relative upper and lower bounds). The genuinely open frontier: (a) tight per-sample cost for **cyclic** queries below AGM under realistic degree constraints; (b) samplers that achieve *minimum-variance* (not just unbiased) under skew without full degree indexes; (c) maintaining sampler validity under **updates** without rebuilding indexes.

## 7. Current Research (as of June 2026)
Active directions: variance-optimal measure-biased walks; join sampling under differential privacy; GPU/vectorized Wander-Join; samplers for queries with projections and self-joins. Groups: Ke Yi (HKUST), Hung Ngo / Dan Olteanu / Dan Suciu (relational learning + sampling), Zhuoyue Zhao / Feifei Li / Jeffrey Naughton. *(frontier — verify)* learned-cardinality-guided importance sampling claiming near-optimal variance on TPC-DS-scale cyclic joins.

## 8. Future Work
Unify worst-case-optimal sampling with cost-model-aware optimization; dynamic samplers with $\tilde O(1)$ amortized update; tight variance theory for general CQs; sampling over join-aggregate-groupby pipelines with composable error; private and secure join sampling.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* SIAM J. Comput., 2013 (FOCS 2008).
- **[Foundational]** Olken. *Random Sampling from Databases.* PhD thesis, UC Berkeley, 1993.
- **[SOTA]** Li, Wu, Yi, Zhang. *Wander Join: Online Aggregation via Random Walks.* SIGMOD 2016.
- **[SOTA]** Chen, Yi. *Random Sampling and Size Estimation Over Cyclic Joins.* ICDT 2020.
- **[SOTA]** Zhao, Christensen, Li, Yi, Wu. *Random Sampling over Joins Revisited.* SIGMOD 2018.
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
