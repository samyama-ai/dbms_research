# End-to-End Plan-Cost Sensitivity to CE Error

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/plan-cost-sensitivity` · **Status:** empirically-open

## 1. Problem Statement

Cardinality estimates feed a cost model, which feeds plan enumeration. But most estimation errors are **harmless**: they shift a cost slightly without changing the chosen plan, or change a plan whose runtime is nearly identical. The problem: **identify which CE errors actually flip the optimizer's choice to a materially worse plan, and quantify each estimate's end-to-end leverage** — so estimation effort and accuracy budgets can be spent where they change outcomes.

Variants:

- **Sensitivity (decision):** for an estimate $\hat c_i$ at subplan $i$, does the true value lie in an interval that keeps the optimal plan unchanged? Compute the *robustness radius* of each estimate.
- **Attribution (optimization):** decompose realized plan suboptimality (regret) onto the individual estimation errors that caused it.
- **Budget allocation:** given a fixed accuracy/compute budget, allocate it across subplans to minimize expected plan regret rather than estimation error.

This reframes CE: the objective is not minimal q-error but minimal **plan regret**, $\text{cost}(\hat p)-\text{cost}(p^\star)$, where $\hat p$ is the plan chosen under estimates and $p^\star$ under truth.

## 2. Mathematical Foundations

A plan $p$ has cost $C(p;\,\mathbf c)$ depending on the vector of subplan cardinalities $\mathbf c$. The optimizer returns $\hat p=\arg\min_p C(p;\hat{\mathbf c})$. **Plan regret** is $\rho(\hat{\mathbf c})=C(p^\star;\mathbf c)$ vs $C(\hat p;\mathbf c)$ — note it is evaluated at *true* cardinalities. Because $\arg\min$ is piecewise-constant in $\hat{\mathbf c}$, regret is a **step function**: small estimate changes do nothing until a decision boundary (where two plans tie) is crossed.

Foundations:

- **Moerkotte–Neumann–Steinbrunn (VLDB 2009):** a factor-$\theta$ q-error bound on all estimates implies at most a $\theta^{?}$ factor on plan cost — linking multiplicative estimation error to bounded suboptimality. This is an *upper* sensitivity; the per-estimate *exact* sensitivity is sharper.
- **Parametric query optimization (PQO):** the plan-optimal regions tessellate cardinality space into polytopes; the boundary geometry determines sensitivity (Hulgeri–Sudarshan; Ganguly).
- **Robustness radius:** the largest perturbation of $\hat c_i$ keeping $\hat p$ optimal — a per-coordinate distance to the nearest plan-switch hyperplane in the cost model.
- Cost models are typically posynomial/monotone in cardinalities, so $C$ is well-behaved (often log-convex) between boundaries, enabling interval propagation.

## 3. State of the Art (SOTA)

- **Foundational diagnosis:** the **"How Good Are Query Optimizers, Really?"** study (Leis et al., VLDB 2015) using the **Join Order Benchmark (JOB)** isolated CE error as the dominant cause of bad plans and showed many errors are tolerable while a few are catastrophic.
- **Robustness-aware optimization:** robust/least-expected-cost PQO and risk-aware optimizers; **bounded q-error → bounded plan cost** theory (Moerkotte et al.).
- **Systems-SOTA:** error-injection and what-if frameworks that perturb estimates and observe plan changes; learned-optimizer work (Neo/Bao, Marcus et al., VLDB 2019/2021) that implicitly learns which estimates matter via end-to-end reward. *(frontier — verify)* recent tools compute per-subplan regret-sensitivity to prioritize estimator effort.

## 4. Upper Bound

- **Global:** if every estimate has q-error $\le\theta$, plan cost is within a bounded factor of optimal (Moerkotte et al.) — a coarse but provable RAM-model bound, exponential in query height in the worst case but small in practice.
- **Per-estimate:** the robustness radius is computable by solving, for each competing plan, the cost-equality constraint — an LP/parametric program when the cost model is piecewise-posynomial; polynomial per candidate-plan pair, but the candidate set can be exponential.

## 5. Lower Bound

- **Combinatorial explosion:** the number of plan-optimal regions can be exponential in the number of joins, so exhaustively mapping sensitivity is intractable; deciding optimal-plan stability under adversarial estimate perturbation is at least as hard as join-order optimization (NP-hard, Ibaraki–Kameda for general cost models).
- **Information-theoretic:** without runtime feedback, no estimator can know which of its errors crossed a decision boundary — the boundary depends on true cardinalities it does not have.
- **Brittleness:** one can construct instances where an arbitrarily small error in a single estimate flips to an arbitrarily worse plan (zero robustness radius at a near-tie), so no nontrivial worst-case per-estimate tolerance exists in general.

## 6. The Gap

We know (empirically, JOB) that *few* errors matter, but we lack a cheap, predictive, optimizer-integrated way to flag *which* — without first knowing the truth. The gap is **empirically open**: global q-error→cost bounds are loose, exact per-estimate sensitivity is exponential to enumerate, and learned optimizers capture sensitivity only implicitly. Closing it needs a tractable per-subplan regret-sensitivity score with guarantees, plus optimizer cost models exposing decision-boundary geometry.

## 7. Current Research (as of June 2026)

- Regret-centric CE: training/evaluating estimators against plan regret rather than q-error *(frontier — verify)*.
- Sensitivity-guided budget allocation: spend sampling/learning effort on high-leverage subplans (links to robust PQO).
- Learned and feedback optimizers (Bao, Neo, Balsa) that route around bad estimates via end-to-end reward (Marcus, Kraska/MIT; Stoica/Berkeley).
- Differentiable/relaxed optimizers exposing $\partial\,\text{cost}/\partial\,\hat c$ to attribute regret to estimates *(frontier — verify)*.

## 8. Future Work

- A cheap, calibrated "leverage" score per estimate, usable inside the optimizer.
- Cost models that emit robustness radii natively.
- Regret-optimal accuracy-budget allocation with guarantees.
- Standard regret-based CE benchmarks complementing q-error (ties to the benchmarks problem).

## 9. Key References

- **[Foundational]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really? (Join Order Benchmark).* VLDB, 2015.
- **[Foundational]** Moerkotte, Neumann, Steinbrunn. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009.
- **[Foundational]** Ibaraki, Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984.
- **[Foundational]** Hulgeri, Sudarshan. *Parametric Query Optimization for Linear and Nonlinear Cost Functions.* VLDB, 2003.
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
