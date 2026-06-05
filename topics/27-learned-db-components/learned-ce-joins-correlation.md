# Learned CE Under Joins and Correlation

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-ce-joins-correlation` · **Status:** empirically-open

## 1. Problem Statement

Single-table selectivity is well handled, but **join cardinality under attribute and
join-key correlation** remains the central failure mode of cardinality estimation.
The problem: build a learned model that captures, for a multi-way join query $q$
over tables $R_1,\dots,R_k$, the **joint distribution of join keys and filter
attributes** — including conditional dependence across tables — so that $\hat c(q)$
is accurate, **without** materializing or modeling the full joint distribution
(whose support is exponential in $k$).

- **Decision variant:** can a model of size polynomial in the schema represent the
  join-key correlation to within q-error $\rho$?
- **Optimization variant:** minimize expected/tail q-error over a join workload
  subject to a size/latency budget.
- **Counting/representation variant:** which factorizations of the joint distribution
  are expressive enough yet tractable to learn and query?

"Solving" means a representation that defeats the independence/uniformity assumptions
behind classic estimator failures, at sub-exponential cost.

## 2. Mathematical Foundations

The exact answer is $c(q) = \sum_{\mathbf{v}} \prod_i p_i(\mathbf v)\,|R_i|$ over the
joint key/attribute domain — a tensor whose naive representation is exponential.
Tractable modeling rests on **factorization**:

- **Probabilistic graphical models / SPNs:** sum-product networks and Bayesian
  networks give tractable marginals when the dependency graph is sparse; exactness
  requires the model's structure to match the data's conditional-independence map.
- **Factorized databases & FAQ/AJAR:** the algebraic structure of joins
  (semiring aggregation over a hypergraph) means tractability is governed by
  **fractional hypertree width** $\mathrm{fhtw}$ and **submodular width**; a learned
  estimator inherits this width barrier.
- **AGM / polymatroid bound:** worst-case join size $\le \prod_e |R_e|^{x_e}$;
  correlation can push true size anywhere below this envelope, so the model must learn
  *where* in $[\,\cdot\,]$ the instance sits.
- **Information theory:** mutual information $I(A;B)$ between correlated attributes
  lower-bounds the bits any faithful synopsis must store.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Factorized representations with width-parameterized guarantees
  (Olteanu–Schleich; Abo Khamis–Ngo–Rudra FAQ, PODS 2016) describe *exact* tractable
  classes; learning these structures from data is not characterized.
- **Systems SOTA:** Deep autoregressive joint models — **NeuroCard** (VLDB 2021) and
  **Naru** (VLDB 2020) model a sampled full-outer-join table; **DeepDB** (VLDB 2020)
  uses relational SPNs; **FactorJoin** (SIGMOD 2023) factorizes join estimation into
  per-table distributions plus join-key histograms, scaling to many tables;
  **BayesCard** uses Bayesian networks. Benchmarks (Han et al., VLDB 2022;
  Wang et al., VLDB 2021) show these beat traditional estimators on average yet still
  incur large tail errors on highly correlated, many-way joins.

## 4. Upper Bound

For join queries of fractional hypertree width $w$, factorized evaluation and
width-aware synopses answer/represent the distribution in time and space
$\tilde O(N^{w})$ (the FAQ/InsideOut bound, **RAM model**) — a learned model
respecting the same factorization can match this. FactorJoin-style decompositions
achieve space linear in $\sum_i |R_i|$ when join-key dependence is approximately
captured by pairwise factors, with empirically bounded but not certified error.

## 5. Lower Bound

Capturing arbitrary correlation is hard: representing the join distribution exactly
requires $\Omega(N^{\mathrm{subw}})$ for some instances (**submodular-width** lower
bounds for join evaluation, Marx 2013), and detecting a planted high-selectivity
correlation between two tables reduces to **set-disjointness**, giving
$\Omega(N)$ **communication-complexity** space lower bounds for any synopsis that must
answer all join filters within bounded error. Information-theoretically, a model must
store $\Omega(I(\text{keys};\text{filters}))$ bits to remain faithful.

## 6. The Gap

The status is **empirically-open**: systems beat baselines in practice but lack
guarantees, and theory gives width/communication barriers without telling us which
real workloads fall inside the tractable (low-width, low-mutual-information) regime.
The gap is the absence of a learnability theory connecting a *measurable* correlation
parameter of the instance to achievable model size and q-error. Closing it needs a
structure-learning result: given data, recover a factorization whose width and
residual mutual information certify the estimator's accuracy.

## 7. Current Research (as of June 2026)

- Transformer/autoregressive joint models over join samples with cross-table
  attention, and diffusion-based density models for join keys *(frontier — verify)*.
- Hybrid factorized + learned residual models that learn only the correlation
  *deviation* from independence (FactorJoin lineage).
- Connecting learned CE error directly to *plan* regret rather than q-error (Negi et
  al., *Flow-Loss*, VLDB 2021) so models spend capacity where it changes plans.

## 8. Future Work

- Automatic structure learning of the conditional-independence map with width
  certificates.
- Incremental maintenance of join-correlation models under updates.
- Tail-error (not mean) objectives tied to optimizer robustness.

## 9. Key References

- **[Foundational]** M. Abo Khamis, H. Ngo, A. Rudra. *FAQ: Questions Asked Frequently.* PODS 2016. — [arXiv](https://arxiv.org/abs/1504.04044)
- **[Foundational]** D. Marx. *Tractable Hypergraph Properties for Constraint Satisfaction and Conjunctive Queries (submodular width).* J. ACM, 2013. — [DOI](https://doi.org/10.1145/2535926)
- **[SOTA]** Z. Yang et al. *NeuroCard: One Cardinality Estimator for All Tables.* VLDB 2021. — [arXiv](https://arxiv.org/abs/2006.08109)
- **[SOTA]** Z. Wu et al. *FactorJoin: A New Cardinality Estimation Framework for Join Queries.* SIGMOD 2023. — [arXiv](https://arxiv.org/abs/2212.05526)
- **[Survey]** Y. Han et al. *Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation.* VLDB 2022. — [arXiv](https://arxiv.org/abs/2109.05877)

## 10. Worked Example

Consider the join $R(k,A)\bowtie_k S(k,B)$ where the join key $k\in\{1,2\}$ and a filter $B=b_0$ is applied on $S$. Let $|R|=|S|=100$.

Per-key counts: $R$ has $r_1=90,\,r_2=10$; $S$ (after $B=b_0$) has $s_1=2,\,s_2=18$. True join size is the per-key product summed:
$$c = \sum_k r_k\,s_k = 90\cdot2 + 10\cdot18 = 180+180 = 360.$$

A classic estimator assuming **independence/uniformity** uses only marginals: it estimates selectivity of $B=b_0$ as $\tfrac{20}{100}=0.2$, and join size $\approx \tfrac{|R|\,|S|}{\max|\text{dom}(k)|}\cdot 0.2 = \tfrac{100\cdot100}{2}\cdot0.2 = 1000$ — off by $2.8\times$ because it ignores that the filter $B=b_0$ concentrates on key $2$, which is *rare* in $R$.

A FactorJoin-style model keeps the **per-key conditional histograms** $r_k$ and $s_k$ and multiplies key-by-key, recovering $360$ exactly. The cost: storing two pairwise factors of size $|\text{dom}(k)|=2$ instead of the full $2\times|\text{dom}(B)|$ joint. Here mutual information $I(k;B)>0$ is exactly what the independence estimator threw away — and what bounds the bits the synopsis must keep (Section 5).

---
*Part of the [DBMS Research catalog](../../README.md).*
