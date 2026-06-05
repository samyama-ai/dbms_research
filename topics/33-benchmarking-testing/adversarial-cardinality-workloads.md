# Generating Adversarial Cardinality Workloads

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/adversarial-cardinality-workloads` · **Status:** open

## 1. Problem Statement
Given an optimizer's cardinality estimator $\hat{c}$ (white-box or black-box), automatically construct **queries** $Q$ and/or **data** $\mathbf{D}$ that *maximally mislead* the estimates, exposing the plan-regression risk hidden in benign benchmarks. Unlike random benchmarking, the goal is to **search adversarially** for the worst case.

Three variants:
- **Query-adversarial (search):** fix data, find $Q$ maximizing estimation error or, better, the *plan-cost regret*.
- **Data-adversarial:** fix a query template, perturb/generate data so estimates blow up (correlation injection, skew).
- **Joint:** co-optimize $(Q,\mathbf{D})$ — the most powerful and the hardest.

The principled objective is **plan regret**, not raw error: find $(Q,\mathbf{D})$ maximizing $\text{cost}(\text{plan}(\hat{c})) - \min_{p}\text{cost}(p)$, since only errors that flip plan choices cause harm. This directly feeds optimizer hardening, regression test suites, and robustness benchmarks.

## 2. Mathematical Foundations
Let estimator $\hat{c}_\theta$ and true cardinality $c$. Two objectives:
$$\textbf{(error)}\ \max_{Q,\mathbf{D}} \ \max\!\Big(\tfrac{\hat{c}_\theta(Q,\mathbf{D})}{c(Q,\mathbf{D})},\ \tfrac{c(Q,\mathbf{D})}{\hat{c}_\theta(Q,\mathbf{D})}\Big) \quad\text{(q-error)}$$
$$\textbf{(regret)}\ \max_{Q,\mathbf{D}} \ \text{cost}\big(\mathrm{plan}_\theta\big) - \min_p \text{cost}(p).$$

The search space is structured: $Q$ ranges over a predicate/join-graph grammar (combinatorial), $\mathbf{D}$ over an exponential data space. The **AGM bound** $\prod_i|R_i|^{x_i}$ caps achievable $c$ and tells the adversary where intermediate-result explosions are *possible*; independence-assuming estimators fail maximally where realized $c$ approaches AGM while the product estimate stays low — i.e., maximize the gap between estimate and the chase/AGM-feasible truth. White-box differentiable estimators (neural CE) admit **gradient attacks** ($\max \mathcal{L}$ via PGD over a relaxed query/data encoding); classical estimators need black-box search (genetic algorithms, MCTS, Bayesian optimization, coverage-guided fuzzing). Regret is a *bilevel* optimization (inner = optimal plan), generally non-convex and discontinuous (plan choice is piecewise-constant in $\hat{c}$).

## 3. State of the Art (SOTA)
- **Optimizer differential/oracle testing:** SQLancer-derived techniques find result bugs; **Cynthia** / mutation-based query synthesis generate stressing queries.
- **Learned-CE robustness attacks:** studies perturbing data distributions to break Naru/DeepDB/MSCN (Negi et al.; "Are We Ready…" follow-ups) show large q-error under shift, a primitive form of data-adversarial generation.
- **Plan-regret-targeted generation:** workload generators that inject correlations (DSB, Ding et al. 2021) and search-based query generators that hunt for plan regressions; redbook/regression-suite practice at vendors.
- **Worst-case data via the chase:** constructing instances realizing AGM-tight joins to maximize realized cardinality against product-form estimators.

This area is **less mature** than benchmarking: most work generates *hard* workloads, but few *adversarially optimize* end-to-end plan regret.

## 4. Upper Bound
For a fixed query template and a differentiable estimator, gradient-based attacks find high-q-error data perturbations efficiently (polynomial per step, no global guarantee). For black-box, **Bayesian optimization / evolutionary search** give anytime improvement with sample budgets but no optimality certificate. For *data-adversarial* worst-case realized cardinality, **worst-case-optimal joins** + the chase let one *construct* instances meeting the AGM bound in time $O(\text{AGM})$, giving provably maximal true cardinality against any product-form estimate — a constructive upper bound on achievable error for that estimator class.

## 5. Lower Bound
Finding the *global* worst case is hard: maximizing plan regret is a **bilevel combinatorial optimization**; even verifying robustness ("no query in class $\mathcal{Q}$ has q-error $>q$") subsumes NP-hard subproblems. For learned (neural) estimators, the adversarial-example search inherits the **NP-hardness of network robustness verification** (Katz et al., CAV 2017). Counting-based worst cases tie to **#P-hardness** of exact cardinality. Thus exact adversarial generation is intractable; only heuristic/locally-optimal attacks are feasible, and no efficient algorithm can certify an estimator adversary-free.

## 6. The Gap
Open and wide. We have effective *local* attacks and hard-workload generators, but **no scalable method that provably finds (or bounds) the worst-case plan regret** for a given optimizer, and no certified-robustness counterpart. The gap separates "we found a bad case" from "this is the worst case / no worse case exists," which NP/#P-hardness make unattainable exactly. Closing it practically means strong-but-incomplete search (RL/BO/chase-guided) plus *certified* robustness for restricted estimator/query classes.

## 7. Current Research (as of June 2026)
- **RL- and LLM-guided adversarial query synthesis** targeting plan regret rather than raw error *(frontier — verify)*.
- Chase/AGM-guided **data poisoning** generators that drive product-form estimators to maximal true cardinality.
- Coupling adversarial generators with optimizer hardening loops (generate → retrain/guard → regenerate) — adversarial training for estimators *(frontier — verify)*.
- Groups: Rigger (NUS), Leis/Neumann ecosystem (TUM), Binnig (Darmstadt, learned CE), Chaudhuri/Ding (Microsoft, DSB), and the WCOJ/chase theory community (Ngo, Ré, Yi).

## 8. Future Work
- A *plan-regret* benchmark generated adversarially per-optimizer, replacing fixed benchmarks.
- Certified-robustness radii for restricted estimator classes.
- Joint $(Q,\mathbf{D})$ adversarial optimization with theoretical regret bounds for product-form estimators.
- Adversarial training pipelines proven to reduce production regression rates.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Comput., 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[Foundational]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)
- **[SOTA]** Ding, Chaudhuri, et al. *DSB: A Decision Support Benchmark for Workload-Driven and Traditional Database Systems.* VLDB 2021. — [DOI](https://doi.org/10.14778/3484224.3484234)
- **[SOTA]** Rigger, Su. *Finding Bugs in Database Systems via Query Synthesis (SQLancer / NoREC / TLP).* OSDI & ESEC/FSE 2020. — [arXiv](https://arxiv.org/abs/2001.04174)
- **[Foundational]** Katz, Barrett, Dill, Julian, Kochenderfer. *Reluplex: Verifying Deep Neural Networks (robustness NP-hardness).* CAV 2017. — [arXiv](https://arxiv.org/abs/1702.01135)
- **[Survey]** Wang, Qu, Wu, Wang, Zhou. *Are We Ready for Learned Cardinality Estimation?* VLDB 2021. — [arXiv](https://arxiv.org/abs/2012.06743)

## 10. Worked Example

Two tables, $R(A,B)$ and $S(B,C)$, each $|R|=|S|=1000$ rows. Query $Q$: $R \bowtie_B S$ with predicate $A=5 \wedge C=7$.

A product-form estimator assumes independence: $\text{sel}(A=5)=\tfrac{1}{100}$, $\text{sel}(C=7)=\tfrac{1}{100}$, join selectivity $\tfrac{1}{|\text{dom}(B)|}=\tfrac{1}{10}$. It predicts $\hat c = 1000\cdot 1000 \cdot \tfrac{1}{10}\cdot\tfrac{1}{100}\cdot\tfrac{1}{100} = 10$.

Now the data-adversary correlates $B$ with both $A$ and $C$: all rows with $A=5$ share one $B$ value $b^\star$, and so do all rows with $C=7$. Then every $A=5$ tuple (10 of them) joins every $C=7$ tuple (10 of them): true $c=100$.

q-error $=\max(\hat c/c,\,c/\hat c)=\max(0.1,10)=10$. The AGM bound here is $\prod|R_i|^{x_i}=1000^{1}\cdot1000^{0}=10^3$ (cover one edge), so a stronger correlation push could drive $c$ toward $10^3$, widening the gap and flipping the optimizer from a hash join to a far costlier nested-loop plan — exactly the plan-regret the adversary targets.

---
*Part of the [DBMS Research catalog](../../README.md).*
