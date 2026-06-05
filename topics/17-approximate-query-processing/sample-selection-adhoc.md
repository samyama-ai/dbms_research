# Sample Selection for Ad-Hoc Workloads

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sample-selection-adhoc` · **Status:** open

## 1. Problem Statement
Offline AQP systems precompute a portfolio of samples (uniform, stratified on various column sets, measure-biased) under a total space budget $B$, then route each incoming query to the best-matching sample. The problem: **which samples to materialize when the future query and predicate distribution is unknown or drifting**. Formally, choose a set $\mathcal S=\{S_1,\dots,S_m\}$ with $\sum_i |S_i|\le B$ to minimize $\mathbb E_{q\sim\mathcal W}[\text{err}(q,\mathcal S)]$, where $\mathcal W$ is unknown, possibly adversarial, or **non-stationary**. This subsumes (a) **offline** selection from a sampled $\mathcal W$, (b) **online/streaming** selection under drift with regret against the best fixed portfolio in hindsight, and (c) **routing** — given $\mathcal S$, pick the sample minimizing error for query $q$. Distinct from stratified *design* (single sample's strata): here the unit of choice is a *whole sample artifact*, and selection is combinatorial over artifacts.

## 2. Mathematical Foundations
Model each candidate sample as an element with a **utility** $u(S,q)$ = error reduction for query $q$. Expected workload utility $U(\mathcal S)=\mathbb E_q[\max_{S\in\mathcal S} u(S,q)]$ is **monotone submodular** in $\mathcal S$ (each query is "covered" by its best sample), so budgeted maximization admits a greedy $(1-1/e)$ guarantee (Nemhauser–Wolsey–Fisher) — knapsack-constrained variants give $(1-1/e)$ via the cost-benefit greedy. Under **unknown** $\mathcal W$, the online problem becomes **adversarial / experts**: treat each candidate sample as an arm and use regret-minimizing portfolio selection, or **submodular bandits**, with regret $\tilde O(\sqrt{mT})$. Drift is handled by sliding-window or discounted reward. The **VC dimension** of the predicate class bounds how many sample-error observations are needed to generalize the utility estimates ($\tilde O(d/\epsilon^2)$ queries to estimate utilities to $\epsilon$).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BlinkDB** column-set sample portfolio selection by frequency of column appearance in past queries; **PASS / Sample Stores** and commercial AQP that maintain multiple stratified samples; **DeepDB / learned synopses** that fit a model instead of choosing samples. **Keebo** (Mozafari) commercializes workload-driven sample/aggregate selection.
- **Theory-SOTA:** Submodular budgeted maximization (Sviridenko 2004 for knapsack-constrained greedy) and online submodular optimization (Streeter–Golovin) give the cleanest guarantees; learning-augmented selection with predictor + worst-case fallback is the active theory frontier.

## 4. Upper Bound
For a *known* workload sample, greedy budgeted selection achieves $(1-1/e)$ of optimal expected error-reduction in $O(m\,|\mathcal W|)$ utility evaluations. In the online/adversarial setting, no-regret portfolio selection guarantees $\tilde O(\sqrt T)$ regret versus the best fixed budget-$B$ portfolio in hindsight. Routing a query to its best sample is $O(m)$ per query, or $O(\log m)$ with an index over sample metadata.

## 5. Lower Bound
Budgeted sample selection is **NP-hard** and inherits set-cover's $(1-1/e)$ inapproximability under $\mathsf P\ne\mathsf{NP}$ (Feige), so greedy is essentially optimal among poly-time algorithms. Information-theoretically, against a fully **adversarial drifting** $\mathcal W$, any online selector has regret $\Omega(\sqrt{mT})$ (lower bound from prediction-with-experts). For truly ad-hoc single queries with no prior, no offline sample can guarantee bounded relative error on an adversarially chosen selective predicate (same subpopulation argument as stratified design).

## 6. The Gap
The **offline, known-distribution** case is essentially closed ($(1-1/e)$ matching). The open gap is the **drift/unknown** regime: bridging worst-case $\Omega(\sqrt{mT})$ regret with the much better performance achievable when workload predictors are accurate. Learning-augmented selection promises near-optimal under good predictions and graceful degradation otherwise, but tight consistency/robustness trade-off bounds for *sample portfolios* (as opposed to caching) are not established.

## 7. Current Research (as of June 2026)
Directions: learning-augmented portfolio selection with consistency/robustness guarantees; bandit-style online sample materialization under drift; LLM/workload-forecasting to predict $\mathcal W$; jointly selecting samples and materialized aggregates. Groups: Barzan Mozafari (Michigan/Keebo), Bolin Ding / Surajit Chaudhuri (MSR/Alibaba), learned-systems groups (MIT, CMU). *(frontier — verify)* forecasting-driven selectors claiming sub-$\sqrt T$ regret on real drifting cloud-warehouse traces.

## 8. Future Work
Tight consistency-robustness frontiers for learning-augmented sample selection; budget sharing across samples, aggregates, and caches; selection that co-optimizes with the optimizer's plan choices; privacy-aware selection where each artifact has a privacy cost.

## 9. Key References
- **[Foundational]** Nemhauser, Wolsey, Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Math. Programming, 1978.
- **[Foundational]** Chaudhuri, Das, Narasayya. *Optimized Stratified Sampling for Approximate Query Processing.* ACM TODS, 2007.
- **[SOTA]** Agarwal, Mozafari, Panda, Milner, Madden, Stoica. *BlinkDB.* EuroSys 2013.
- **[SOTA]** Sviridenko. *A Note on Maximizing a Submodular Set Function Subject to a Knapsack Constraint.* Operations Research Letters, 2004.
- **[Survey]** Mitzenmacher, Vassilvitskii. *Algorithms with Predictions.* Comm. ACM, 2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
