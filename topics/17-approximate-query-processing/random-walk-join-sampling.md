# Wander-Join and Random-Walk Sampling

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/random-walk-join-sampling` · **Status:** partially-solved

## 1. Problem Statement
Estimate aggregates (or cardinality) over a multi-way join **without materializing it**, by performing **index-assisted random walks** along join paths: start at a random tuple of one relation, follow an index to a random matching tuple in the next relation, and so on, forming one full join *path* per walk. Each successful walk yields an unbiased Horvitz–Thompson estimator. The problem is to design walks with **controlled (ideally minimized) variance**, support **cyclic** and **many-way** join graphs, and bound the per-walk cost.

Variants:
- **Acyclic / chain / star** joins (Wander Join's original scope) vs. **cyclic** joins (the hard case).
- **Aggregate estimation** (`SUM`/`AVG`/`COUNT`) vs. **uniform answer sampling** (drawing a uniformly random join tuple).
- **Variance-control variant:** choose the walk *order* and per-step *trial* strategy to minimize estimator variance.

The challenge: a random walk visits a join path with probability proportional to the product of inverse out-degrees, so the inclusion probabilities are non-uniform and skew-sensitive — variance can explode on heavy-degree nodes unless the walk is biased or rejection-corrected.

## 2. Mathematical Foundations
Model the join as a graph where a walk visits tuples $t_1\in R_1,\dots,t_k\in R_k$ forming a valid join path $\gamma$. If at step $i$ there are $d_i(t_{i-1})$ matching candidates and one is chosen uniformly, the path probability is
$$p(\gamma)=\frac{1}{|R_1|}\prod_{i=2}^{k}\frac{1}{d_i(t_{i-1})}.$$
The **Horvitz–Thompson** estimator $\hat\theta=\frac1m\sum_{j=1}^m \frac{f(\gamma_j)\,\mathbb{1}[\gamma_j\ \text{valid}]}{p(\gamma_j)}$ is **unbiased**; its variance is
$$\mathrm{Var}(\hat\theta)=\frac1m\Big(\sum_{\gamma} \frac{f(\gamma)^2}{p(\gamma)} - \theta^2\Big),$$
minimized when $p(\gamma)\propto f(\gamma)$ (importance sampling). Foundations: **Horvitz–Thompson** estimation, **importance sampling**, **Markov-chain** mixing, the **AGM bound** (output size $\le$ product of fractional-edge-cover weights), and **fractional hypertree width / tree decompositions** for handling cycles. For cyclic joins, no acyclic walk order exists, so one samples over a decomposition and corrects with rejection, paying an AGM-vs-output overhead.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** **Wander Join** (Li, Wu, Yu, Nakayama, SIGMOD 2016 / TODS 2019) established index-assisted random-walk OLA with provable unbiasedness and CIs for acyclic joins; an optimal *walk-order* selection minimizes variance. Subsequent worst-case-optimal join-sampling results (Zhao, Christensen, Li, Hu, Yi; and Chen–Yi) give uniform join-answer sampling in expected time tied to the **AGM bound** for *both acyclic and cyclic* queries — the current theory frontier.
- **Systems-SOTA:** **XDB** integrated Wander Join into PostgreSQL with progressive results; random-walk samplers appear in graph/SPARQL engines and in research AQP layers over columnar stores. Production support remains experimental.

## 4. Upper Bound
- Acyclic (Wander Join): unbiased estimate; expected per-walk cost $O(k)$ index lookups for a $k$-relation chain; aggregate CI half-width $O(\sigma_W m^{-1/2})$ over $m$ walks, with $\sigma_W$ the walk-estimator standard deviation; optimal walk order reduces $\sigma_W$.
- Uniform join-answer sampling: a single sample drawn in expected time $\tilde O(\mathrm{AGM}_Q/\max(1,\mathrm{OUT}))$ for acyclic queries; for cyclic queries, $\tilde O(\mathrm{AGM}_Q/\mathrm{OUT})$ after near-linear preprocessing using fractional-cover decompositions (Chen–Yi 2020; Deng–Lu–Tao and the Zhao et al. line).
- Importance/degree-biased walks lower variance toward the $p\propto f$ optimum.

## 5. Lower Bound
- **Sample complexity:** estimating join `COUNT` to relative error $\varepsilon$ needs $\Omega(\mathrm{AGM}/(\varepsilon^2\,\mathrm{OUT}))$ samples — when $\mathrm{AGM}\gg\mathrm{OUT}$ (sparse output, dense inputs), any random-walk sampler suffers high rejection/variance (information-theoretic second-moment bound).
- **Conditional / fine-grained:** beating AGM-based sampling time for general (esp. cyclic) joins would contradict **worst-case-optimal join** lower bounds and related fine-grained hardness (3SUM / SETH-style for triangle-like cyclic queries).
- **Communication complexity:** distributed join-size estimation inherits $\Omega(\sqrt N)$ disjointness lower bounds.

## 6. The Gap
For **acyclic** joins the gap is largely **closed**: Wander Join's unbiased estimators with optimal walk order match the $\mathrm{AGM}/\mathrm{OUT}$ sample-complexity floor up to logs. For **cyclic / many-way** joins the gap is **partially open**: recent worst-case-optimal samplers achieve near-AGM expected time, but (i) tight *variance* control (not just expected cost), (ii) practical, low-overhead implementations of the decomposition-based correction, and (iii) anytime-valid CIs under heavy skew are not yet fully matched between theory and systems.

## 7. Current Research (as of June 2026)
Active directions: (1) **worst-case-optimal join sampling for cyclic queries** via tree/hypertree decompositions and degree-aware rejection, pushing toward output-sensitive guarantees *(frontier — verify)*; (2) learned / adaptive walk biasing that estimates degrees online to approach the $p\propto f$ optimum; (3) random-walk sampling on **graph and RDF** workloads (path and subgraph queries); (4) maintaining walk samplers under updates. Groups: Yi (HKUST) and collaborators (Zhao, Hu, Deng, Tao) on join-sampling complexity, Wu (online join, Wander Join lineage), and the worst-case-optimal-join theory community (Ngo, Ré, Rudra).

## 8. Future Work
- Provably variance-optimal random walks for arbitrary cyclic join graphs.
- Output-sensitive samplers whose cost adapts to actual (not worst-case AGM) output.
- Skew-robust, update-friendly walk indices.
- Tight anytime-valid running CIs for random-walk OLA.

## 9. Key References
- **[SOTA]** F. Li, B. Wu, K. Yu, A. Nakayama. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016 (extended: ACM TODS, 2019). — [DOI](https://doi.org/10.1145/2882903.2915235), [TODS](https://doi.org/10.1145/3284551)
- **[SOTA]** Y. Chen, K. Yi. *Random Sampling and Size Estimation Over Cyclic Joins.* ICDT, 2020. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2020.7)
- **[SOTA]** K. Zhao, R. Christensen, F. Li, X. Hu, K. Yi. *Random Sampling over Joins Revisited.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3183739)
- **[Foundational]** D. G. Horvitz, D. J. Thompson. *A Generalization of Sampling Without Replacement from a Finite Universe.* JASA, 1952. — [DOI](https://doi.org/10.1080/01621459.1952.10483446)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008. — [DOI](https://doi.org/10.1137/110859440)
- **[Foundational]** H. Q. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [DOI](https://doi.org/10.1145/2590989.2590991), [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

Take a 3-chain $R_1(A) \bowtie R_2(A,B) \bowtie R_3(B)$ and estimate `COUNT`. Say $|R_1| = 4$. We start a walk by picking a tuple $t_1 \in R_1$ uniformly, so $\Pr[t_1] = 1/4$. From $t_1$ there are $d_2(t_1) = 5$ matching tuples in $R_2$; pick one uniformly, $\Pr = 1/5$. From that $R_2$ tuple there are $d_3 = 2$ matches in $R_3$; pick one, $\Pr = 1/2$. The path probability is
$$p(\gamma) = \tfrac14 \cdot \tfrac15 \cdot \tfrac12 = \tfrac{1}{40}.$$

For a `COUNT`, $f(\gamma) = 1$ on every valid path, so each successful walk contributes the inverse probability:
$$\hat\theta_{\text{walk}} = \frac{1}{p(\gamma)} = 40.$$
Averaging $m$ such walks gives an unbiased estimate of $|R_1\bowtie R_2\bowtie R_3|$.

Now suppose one $R_2$ tuple is a heavy hitter with $d_3 = 100$ instead of $2$: a walk through it has $p = \tfrac14\cdot\tfrac15\cdot\tfrac1{100} = \tfrac{1}{2000}$ and contributes $2000$ — a 50$\times$ spike. This single high-degree node blows up $\sum_\gamma f(\gamma)^2/p(\gamma)$, illustrating the skew-driven variance of Section 2 and why degree-aware biasing toward $p \propto f$ is needed.

---
*Part of the [DBMS Research catalog](../../README.md).*
