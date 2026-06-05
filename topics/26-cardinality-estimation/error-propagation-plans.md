# Error Propagation Through Query Plans

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/error-propagation-plans` · **Status:** open

## 1. Problem Statement
A query plan is a tree of operators; the optimizer estimates each operator's output cardinality, but these estimates feed *into* the estimates above them. Small per-operator errors can **compound multiplicatively** up the tree, and the cost model amplifies them into catastrophic plan choices. The problem: **characterize and bound how per-operator cardinality-estimation errors propagate through a plan tree**, and design estimators/optimizers whose end-to-end error (or resulting plan sub-optimality) is controlled. Variants: **forward error analysis** (bound output error given input errors), **plan-robustness** (choose plans insensitive to estimation error), and the **decision variant** (does estimation error change the optimal plan?). The seminal empirical finding (Leis et al.) is that errors grow exponentially with the number of joins under independence assumptions.

## 2. Mathematical Foundations
Let a plan have operators $o_1, \dots, o_k$ in topological order, with true cardinalities $c_i$ and estimates $\hat{c}_i$. Define per-operator **q-error** $q_i = \max(\hat{c}_i/c_i,\, c_i/\hat{c}_i)$. Under independence-style multiplicative composition, the estimate at a node is a product of child estimates and a per-operator selectivity factor, so log-errors *add*:
$$ \log \hat{c}_{\text{root}} - \log c_{\text{root}} = \sum_i (\log \hat{c}_i - \log c_i) + \text{(model bias)}, $$
giving worst-case end-to-end q-error $\prod_i q_i$ — exponential in plan depth. Tighter analysis treats the optimizer's cost $C(\cdot)$ as a function of the cardinality vector; if $C$ is, say, Lipschitz in log-cardinalities with constant $L$, then plan-cost error is bounded by $L \sum_i |\log q_i|$. **Plan robustness** can be framed as minimizing worst-case regret over an uncertainty set (a box/ellipsoid in cardinality space), connecting to robust optimization. The **principle of least expected cost vs. least worst-case cost** distinguishes risk-neutral and risk-averse plan selection.

## 3. State of the Art (SOTA)
**Empirical SOTA:** Leis et al. (*How Good Are Query Optimizers, Really?*, VLDB 2015) quantified exponential growth of error with join count and showed cardinality estimation, not the cost model, dominates plan quality. **Robustness SOTA:** *Robust Query Processing* and **plan diagrams / parametric query optimization** (Haritsa's group — *Plan Bouquets*, SIGMOD 2014) give worst-case performance guarantees by executing a calibrated sequence of plans, bounding sub-optimality independent of estimate accuracy. **Adaptive query processing** (Eddies; mid-query re-optimization, Kabra–DeWitt; LEO learning optimizer, Stillger et al.) corrects errors at runtime. Learned cost models and end-to-end learned optimizers (Bao, Balsa, Neo) implicitly target end-to-end outcomes rather than per-operator accuracy.

## 4. Upper Bound
Plan Bouquets give a **provable worst-case sub-optimality bound**: for selectivity spaces of dimension $d$, the competitive ratio relative to an oracle is bounded (e.g., a small constant for $d=1$, growing with $d$), *independent of the actual estimation error*, by executing a discretized "bouquet" of plans with cost-budget doubling. Runtime re-optimization caps wasted work to a constant factor of detected error. If per-operator q-error is bounded by $q$ over a depth-$h$ plan and cost is log-Lipschitz with constant $L$, end-to-end cost error is at most $L \cdot h \cdot \log q$ — a benign linear (not exponential) bound *when errors are bounded and non-adversarially aligned*.

## 5. Lower Bound
Worst-case multiplicative error of $\prod_i q_i$ is achievable: adversarial instances make per-operator errors align and multiply, so any optimizer relying purely on bottom-up estimates with bounded per-operator q-error $q$ over depth $h$ can suffer $q^{h}$ end-to-end error (information-theoretic, from the multiplicative model). For parametric/robust optimization, lower bounds on the **competitive ratio** of any plan-selection strategy grow with the dimensionality of the selectivity/uncertainty space (Haritsa et al.), showing robustness cannot be free.

## 6. The Gap
Open. Bottom-up estimation has matching exponential upper/lower worst-case bounds, so the interesting gap is *avoiding* the regime: robust/parametric methods bound sub-optimality but at runtime cost and limited dimensionality; adaptive methods react but cannot prevent an already-launched bad plan. No framework offers tight, low-overhead, dimension-scalable guarantees on end-to-end plan quality under realistic correlated errors. Closing it needs error models that capture *correlation between operator errors* (they are not independent) and optimizers that propagate uncertainty, not point estimates.

## 7. Current Research (as of June 2026)
Directions: (i) **uncertainty-propagating optimization** — carrying distributions or intervals instead of point cardinalities and choosing risk-aware plans *(frontier — verify)*; (ii) **learned optimizers with safety nets** (Bao-style steering, Balsa) that bound regret against a trusted baseline; (iii) revisiting **Plan Bouquets** and parametric optimization for higher dimensions and with learned estimates; (iv) formal study of how *correlated* per-operator errors compose, beyond the worst-case product bound. Groups: IISc (Haritsa), TUM (Neumann), MIT/Berkeley (learned optimizers).

## 8. Future Work
Models of correlated operator-error propagation; optimizers that consume calibrated uncertainty from learned estimators; scalable robust optimization beyond low selectivity-dimension; theory linking per-operator q-error guarantees to plan-regret bounds; and standardized benchmarks measuring *end-to-end* robustness rather than estimator accuracy in isolation.

## 9. Key References
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Ioannidis, Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991.
- **[SOTA]** Leis et al. *How Good Are Query Optimizers, Really?* VLDB, 2015.
- **[SOTA]** Dutt, Haritsa. *Plan Bouquets: Query Performance Robustness via Estimation-Free Execution.* SIGMOD, 2014.
- **[SOTA]** Stillger, Lohman, Markl, Kandil. *LEO – DB2's LEarning Optimizer.* VLDB, 2001.
- **[SOTA]** Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
