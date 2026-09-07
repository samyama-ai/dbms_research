---
id: 17-approximate-query-processing/stratified-sample-design
title: "Optimal Stratified Sample Design"
topic: 17-approximate-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal Stratified Sample Design

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/stratified-sample-design` · **Status:** open

## 1. Problem Statement
Given a table $T$ with $N$ rows, a **space budget** $B$ rows for offline samples, and a (partially) **unknown future query workload**, choose (a) a partition of $T$ into strata $\{H_1,\dots,H_L\}$ — typically by a subset of columns — and (b) a per-stratum allocation $\{n_1,\dots,n_L\}$ with $\sum_\ell n_\ell \le B$, so as to **minimize expected aggregate error** over the workload distribution $\mathcal W$. Two coupled sub-problems: **stratum design** (which columns/cuts define strata — combinatorial) and **allocation** (how many sample rows per stratum — continuous, convex given strata). Optimization variant: minimize worst-case or expected error subject to $B$. Decision variant: does a design exist meeting error $\le \epsilon$ for all $q\in\mathcal W$ within budget $B$? The difficulty is robustness: a design tuned for one query class can be arbitrarily bad for another, and $\mathcal W$ is unknown at build time.

## 2. Mathematical Foundations
For a stratified estimator of a population total, variance is
$$\mathrm{Var}(\hat\theta)=\sum_{\ell=1}^{L} N_\ell^2\,\frac{\sigma_\ell^2}{n_\ell}\Bigl(1-\tfrac{n_\ell}{N_\ell}\Bigr),$$
with $N_\ell=|H_\ell|$ and $\sigma_\ell^2$ the in-stratum variance. For a **fixed** stratification, minimizing this under $\sum n_\ell=B$ yields **Neyman allocation** $n_\ell \propto N_\ell\sigma_\ell$ (Lagrange/KKT — a convex program). Choosing the strata themselves is the hard part: it interacts with the *predicate* distribution, since selective predicates concentrate error in few strata. BlinkDB frames it as an **error-latency-profile** optimization over column-set "templates." Multi-query robustness ties to **minimax** design and to **submodular** coverage of query templates, enabling greedy $(1-1/e)$ guarantees for template selection. Skew makes per-group `COUNT` error sensitive to the smallest $N_\ell$ — linking to the rare-subpopulation problem.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BlinkDB** (Agarwal et al., EuroSys 2013) — multi-dimensional stratified samples per column-set template, allocation by an optimization over a parameterized error-latency profile; **AQP++/Sample+Seek** (Ding, Huang, Chaudhuri, Chakrabarti, Wang, SIGMOD 2016) — combine a measure-augmented sample with an index to bound error for range/point predicates; **STRAT / congressional sampling** (Acharya, Gibbons, Poosala, SIGMOD 2000) — hybrid uniform+per-group allocation for group-by robustness.
- **Theory-SOTA:** Neyman/optimal allocation (Neyman 1934) is exact for fixed strata; learning-augmented and submodular template-selection bounds are the current theory frontier.

## 4. Upper Bound
Given fixed strata, optimal allocation is solved exactly by Neyman allocation in $O(L)$ time (closed form / convex). For template *selection* under a submodular surrogate of workload coverage, greedy gives a $(1-1/e)$-approximation to the best size-$k$ template set. Sample+Seek bounds the relative error of any single-predicate aggregate to $\epsilon$ with sample size $\tilde O(1/\epsilon^2)$ independent of $N$ (measure-biased + index correction).

## 5. Lower Bound
Joint **strata + allocation** design over an arbitrary workload is **NP-hard**: optimal multi-column stratification under a budget reduces from set-cover / partition problems, and template selection inherits set-cover's $(1-1/e)$ inapproximability (Feige) under $\mathsf{P}\ne\mathsf{NP}$. Information-theoretically, no fixed budget-$B$ design can guarantee bounded relative error for *all* future predicates: an adversary can select a subpopulation of size $< N/B$ that the design under-samples (counting/adversarial argument), so worst-case relative error is unbounded without workload assumptions.

## 6. The Gap
The **allocation** sub-problem is closed (Neyman is optimal). The **design** sub-problem is genuinely open: existing systems fix the strata to enumerated column templates and optimize within them, but no algorithm with provable workload-robustness guarantees chooses strata for a *drifting/unknown* $\mathcal W$. The gap is between $(1-1/e)$-greedy template coverage and the true minimax-optimal design; closing it needs either tight workload-distribution assumptions or online/learning-augmented designs with regret bounds.

## 7. Current Research (as of June 2026)
Directions: learning-augmented stratification using workload-prediction models with worst-case fallbacks; online stratum re-design under drift; reinforcement-learning sample tuners; jointly designing strata for sampling *and* differential privacy. Groups: Surajit Chaudhuri / Bolin Ding / Vivek Narasayya (MSR), Barzan Mozafari (Keebo), Tim Kraska / learned-systems (MIT). *(frontier — verify)* RL-based stratifiers reporting workload-robust designs that beat BlinkDB templates on production traces.

## 8. Future Work
Provable regret bounds for online stratum redesign; minimax-optimal multi-column strata under bounded workload shift; unifying stratified design with sketches for high-cardinality group-by; budget-sharing across many tables in a schema.

## 9. Key References
- **[Foundational]** Neyman. *On the Two Different Aspects of the Representative Method.* J. Royal Statistical Society, 1934. — [DOI](https://doi.org/10.2307/2342192)
- **[Foundational]** Acharya, Gibbons, Poosala. *Congressional Samples for Approximate Answering of Group-By Queries.* SIGMOD 2000. — [DOI](https://doi.org/10.1145/342009.335450)
- **[SOTA]** Agarwal, Mozafari, Panda, Milner, Madden, Stoica. *BlinkDB.* EuroSys 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[SOTA]** Ding, Huang, Chaudhuri, Chakrabarti, Wang. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD 2016. — [DBLP](https://dblp.org/rec/conf/sigmod/DingHCC016.html)
- **[Foundational]** Feige. *A Threshold of ln n for Approximating Set Cover.* J. ACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)

## 10. Worked Example

Suppose $T$ has $L=2$ strata with sizes $N_1=900$, $N_2=100$ and in-stratum standard deviations $\sigma_1=2$, $\sigma_2=20$ (stratum 2 is small but volatile). Budget $B=100$ sample rows.

**Proportional allocation** ($n_\ell\propto N_\ell$) gives $n_1=90,\,n_2=10$. The variance of the total estimate is
$$\textstyle\sum_\ell N_\ell^2\sigma_\ell^2/n_\ell = \tfrac{900^2\cdot4}{90}+\tfrac{100^2\cdot400}{10}=36{,}000+400{,}000=436{,}000.$$

**Neyman allocation** ($n_\ell\propto N_\ell\sigma_\ell$): weights $900\cdot2=1800$ and $100\cdot20=2000$, sum $3800$, so $n_1=\lfloor100\cdot1800/3800\rfloor=47$, $n_2=53$. Variance:
$$\tfrac{900^2\cdot4}{47}+\tfrac{100^2\cdot400}{53}\approx68{,}900+75{,}500=144{,}400.$$

Neyman cuts variance by $3\times$ by shifting samples toward the high-$\sigma$ stratum — exactly $n_\ell\propto N_\ell\sigma_\ell$. The *open* part: had the workload predicate hit only stratum 2's rare subpopulation, even this design under-samples it.

---
*Part of the [DBMS Research catalog](../../README.md).*
