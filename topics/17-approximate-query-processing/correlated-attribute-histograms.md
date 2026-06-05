# Histograms Under Attribute Correlation

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/correlated-attribute-histograms` · **Status:** open

## 1. Problem Statement
Classical histograms summarize the marginal distribution of a single attribute and answer range-count / selectivity queries with bounded error. The open problem is to build a *multidimensional* synopsis that faithfully captures the **joint distribution** of $d$ attributes — including their statistical dependencies — while using space and construction time that grow gracefully (ideally polynomially, not exponentially) in $d$.

Concretely, given a relation $R$ over attributes $A_1,\dots,A_d$, build a synopsis $S$ of size $B$ such that for any axis-parallel rectangular range $Q$, the estimate $\hat{f}(Q)$ of the true count $f(Q)$ satisfies a worst-case or average error guarantee. Variants:
- **Optimization variant:** minimize the $\ell_p$ (typically $\ell_2$ or $\ell_\infty$) error of selectivity estimates for a fixed budget $B$.
- **Decision variant:** does there exist a $B$-bucket partition achieving error $\le \varepsilon$?
- **Counting/learning variant:** estimate the joint density (a $d$-dimensional contingency table) to within total-variation distance $\varepsilon$.

The core obstacle is the **attribute-value independence (AVI) assumption** baked into product-of-marginals estimators, which is badly violated under correlation (e.g., `city = 'Seattle'` $\wedge$ `state = 'WA'`), causing selectivity estimates — and hence query plans — to be off by orders of magnitude.

## 2. Mathematical Foundations
Let the data live in a $d$-dimensional grid $[n]^d$ with joint frequency tensor $\mathbf{F} \in \mathbb{R}_{\ge 0}^{n^d}$. The product-of-marginals (AVI) estimate is the rank-1 / outer-product approximation $\hat{\mathbf{F}} = \bigotimes_{i} m_i$ where $m_i$ is the $i$-th marginal; its error is governed by the **mutual information** $I(A_i;A_j)$ among attributes.

- **V-optimal histograms** minimize $\sum_{b}\sum_{x\in b}(f(x)-\bar f_b)^2$; the 1-D optimal $B$-bucket partition is solvable by dynamic programming in $O(n^2 B)$ (Jagadish et al.), but the $d$-D partition-into-rectangles problem is **NP-hard** for $d\ge 2$.
- **Hierarchical / grid summaries:** wavelets (Haar coefficient thresholding), the **GENHIST** overlapping-bucket scheme, and **STHoles** (a "holey" self-tuning histogram learned from query feedback) trade exactness for adaptivity.
- **Dimensionality blow-up:** a faithful equi-depth grid needs $\Theta(k^d)$ buckets for $k$ resolution per axis — the curse of dimensionality. Low-rank / tensor-decomposition (CP, Tucker) and graphical-model factorizations exploit conditional independence: if the joint factors over a junction tree of treewidth $w$, storage drops to $O(n^{w+1})$.
- **Sketch connection:** the **AGMS/Count-Min** family and the **Fast-AGMS** sketch give unbiased join-size estimators with variance bounds, and link histogram error to $\|\mathbf F\|_2$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Density estimation of distributions with bounded mutual information / low-treewidth Bayesian-network structure (Chow–Liu trees, and PAC-style learning of bounded-treewidth graphical models). Optimal 1-D V-optimal histograms (Jagadish, Koudas, Muthukrishnan, Poosala, Sevcik, Suel, VLDB 1998).
- **Systems-SOTA:** Production optimizers use 1-D histograms plus *multi-column statistics* / *extended statistics* (PostgreSQL `CREATE STATISTICS (dependencies, ndistinct, mcv)`; SQL Server multi-column stats; Oracle column-group and dynamic stats). Learned cardinality estimators — **MSCN** (Kipf et al., CIDR 2019), **Naru/NeuroCard** (deep autoregressive density models, Yang et al., VLDB 2019/2020), and sum-product networks (**DeepDB**, Hilprecht et al., VLDB 2020) — now dominate accuracy benchmarks for correlated multi-attribute selectivity.

## 4. Upper Bound
- 1-D V-optimal: $O(n^2B)$ time, $O(B)$ space, exact error-optimal (Jagadish et al. 1998); $(1+\varepsilon)$-approximate in near-linear time via approximate DP (Guha, Koudas, Shim).
- Bounded-treewidth-$w$ joint: $O(d\cdot n^{w+1})$ space recovers the joint exactly under the factorization assumption; Chow–Liu builds the optimal tree ($w=1$) in $O(d^2 n)$.
- Autoregressive/SPN learned models achieve sub-1% median q-error empirically but carry **no worst-case guarantee** — they are heuristic upper bounds on accuracy, not on error.

## 5. Lower Bound
- **NP-hardness:** computing the error-optimal $B$-bucket *rectangular* histogram in $d\ge2$ dimensions is NP-hard (Muthukrishnan, Poosala, Suel — tiling/partition reductions).
- **Information-theoretic:** representing an arbitrary joint over $[n]^d$ to total-variation $\varepsilon$ requires $\Omega(n^d/\varepsilon^2)$ bits in the worst case; no synopsis sublinear in the table can be accurate for *adversarially* correlated data — correlation can encode any function.
- **Communication / cell-probe:** range-counting data structures over $d$ dimensions inherit $\Omega(\log n / \log\log n)$-type cell-probe lower bounds (Pătrașcu) and, for additive-error sketches, dimension-dependent space lower bounds.

## 6. The Gap
For *structured* correlation (low treewidth, low mutual information, low rank) the gap is essentially **closed**: factorized synopses match the information-theoretic floor. For *general* correlation the gap is **genuinely open and largely fundamental** — the $\Omega(n^d)$ lower bound says no compact synopsis can be both general and worst-case accurate, so progress means characterizing *which realistic correlation structures* admit compact, provably-bounded synopses. Learned models close the empirical gap but lack the error certificates that the theory side demands; bridging "good in practice" to "provably bounded" is the live frontier.

## 7. Current Research (as of June 2026)
Active directions: (1) **learned cardinality estimation with guarantees** — calibrating deep density models (Naru/NeuroCard descendants) to emit confidence intervals rather than point estimates *(frontier — verify)*; (2) factorized / sum-product synopses (DeepDB lineage) extended to updates and joins; (3) hybrid sketch-plus-model estimators that fall back to AGMS/Count-Min bounds when the model is out-of-distribution; (4) robustness and *worst-case q-error* training objectives. Groups: the Markl/Kipf lineage on learned estimation, the Stanford/Berkeley density-model groups (Yang, Kipf), the data-summarization/streaming community (Cormode, Muthukrishnan), and PostgreSQL/MS-SQL optimizer teams on extended statistics.

## 8. Future Work
- Provable error bounds for learned multidimensional estimators (distribution-free or assumption-light).
- Synopses that are simultaneously *mergeable*, *updatable*, and correlation-aware.
- Tight characterization of the achievable space/error trade-off as a function of a measurable correlation parameter (mutual information, treewidth, rank).
- Robustness to distribution shift and adversarial query workloads.

## 9. Key References
- **[Foundational]** H. V. Jagadish, N. Koudas, S. Muthukrishnan, V. Poosala, K. Sevcik, T. Suel. *Optimal Histograms with Quality Guarantees.* VLDB, 1998.
- **[Foundational]** C. K. Chow, C. N. Liu. *Approximating Discrete Probability Distributions with Dependence Trees.* IEEE Trans. Information Theory, 1968.
- **[Foundational]** N. Bruno, S. Chaudhuri, L. Gravano. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD, 2001.
- **[SOTA]** Z. Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019; and *NeuroCard: One Cardinality Estimator for All Tables.* VLDB, 2020.
- **[SOTA]** B. Hilprecht et al. *DeepDB: Learn from Data, not from Queries.* VLDB, 2020.
- **[SOTA]** A. Kipf et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019.
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
