# What-If Cost Model Fidelity

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/what-if-cost-fidelity` · **Status:** empirically-open

## 1. Problem Statement
A self-driving designer never builds every candidate structure (index, materialized view, partition layout) to measure its benefit. Instead it asks the optimizer a *what-if* (hypothetical) question: "if structure $s$ existed, what would the optimizer estimate the cost of query $q$ to be?" The **what-if cost model fidelity** problem asks: are these hypothetical estimates accurate enough — relative to *true executed cost* — to make correct design decisions, and can we **bound the error** they introduce into the final design?

Variants:
- **Estimation variant:** bound $|\hat c(q,s) - c^\star(q,s)|$ where $\hat c$ is the what-if estimate and $c^\star$ the true cost.
- **Decision variant:** even if individual estimates are biased, does the *argmax/argmin over designs* survive — i.e. is the chosen design $\hat D$ within $(1+\varepsilon)$ of the truly-optimal $D^\star$?
- **Robust-design variant:** choose $D$ that is good under the *worst* cost model consistent with observed feedback (a min–max / distributionally-robust formulation).

The decision variant is the one that matters: fidelity is sufficient if estimation errors do not change the design ranking, even when each absolute estimate is wrong.

## 2. Mathematical Foundations
Let queries be $q\in Q$ with weights $w_q$, designs $D\subseteq C$ from candidate set $C$ under a budget $B$. The optimizer exposes $\hat c(q,D)$; true cost is $c^\star(q,D)$. Define design objective $F(D)=\sum_q w_q\, c(q,D)$ and the **fidelity gap**
$$\Delta(D) = \big| \hat F(D) - F^\star(D)\big|,\qquad \hat F(D)=\sum_q w_q\,\hat c(q,D).$$
If $\Delta(D)\le \delta$ uniformly over feasible $D$, then the what-if-optimal design $\hat D$ satisfies $F^\star(\hat D)\le F^\star(D^\star)+2\delta$ — a standard *optimization-error* argument. The hard part is that $\delta$ is **not uniform**: cost-estimation error compounds through cardinality estimation, which is itself adversarially unbounded (q-error can be exponential in join depth). Foundations therefore rest on **cardinality-estimation error propagation** (q-error $\hat q = \max(\hat n/n, n/\hat n)$, Moerkotte et al.), the multiplicative propagation of q-error through a plan, and on **selection robustness** results showing that ranking is preserved if errors are *order-consistent* even when not magnitude-accurate.

## 3. State of the Art (SOTA)
**Systems-SOTA.** The what-if interface itself dates to AutoAdmin (Chaudhuri & Narasayya, VLDB 1997) and is the substrate of every commercial advisor (SQL Server DTA, Oracle SQL Tuning Advisor, DB2 Design Advisor). Modern designers (Microsoft's index-tuning service; open-source advisors evaluated in Kossmann et al.'s *Magic mirror* benchmark, VLDB 2020) still depend on it. Learned/hybrid cost models (MSCN, Kipf et al. 2019; learned cost models in Bao/Neo, Marcus et al. 2019–2021) aim to reduce $\Delta$ but introduce their own out-of-distribution error.

**Theory-SOTA.** No general fidelity guarantee exists; the strongest results are conditional: design selection is robust under *monotone* and *bounded-distortion* cost oracles, and PAC-style sampling bounds exist when true costs can be measured for a subset.

## 4. Upper Bound
Under a *$\rho$-distortion oracle* assumption ($\tfrac{1}{\rho} c^\star \le \hat c \le \rho\, c^\star$), any $\alpha$-approximate design under $\hat c$ is a $\rho^2\alpha$-approximate design under $c^\star$ — a clean multiplicative transfer bound (RAM model, exact optimizer queries). Empirically, instance-level upper bounds on $\Delta$ are obtained by *selective execution* (validate the top-$k$ candidate designs) at $O(k)$ true-cost measurements, the dominant systems strategy.

## 5. Lower Bound
There is **no model-free lower bound on $\rho$**: cost estimates inherit cardinality-estimation error, and cardinality estimation under arbitrary correlations/predicates is provably unboundable from limited statistics — q-error can be $\Omega(2^{\text{joins}})$ on adversarial instances (information-theoretic, from the impossibility of multidimensional selectivity estimation without the joint distribution). Consequently the decision variant inherits worst-case unboundedness: there exist workloads where the what-if-optimal design is arbitrarily worse than $D^\star$. This is an *information-theoretic* impossibility, not merely computational.

## 6. The Gap
The gap is between a clean conditional transfer ($\rho^2\alpha$) and the absence of any *unconditional* bound on $\rho$ itself. It is **genuinely open** and largely **empirical**: in practice $\rho$ is small on benchmark workloads but unbounded on adversarial/correlated ones. Closing it requires either (a) cost models with certified per-query error bars, or (b) decision procedures provably robust to bounded-but-unknown distortion.

## 7. Current Research (as of June 2026)
Active directions: *uncertainty-aware* cardinality estimators producing calibrated intervals rather than point estimates (extending deep-learning estimators with conformal prediction) *(frontier — verify)*; robust index selection that optimizes against a confidence set of cost models; and "validation-budget" designers that spend a bounded number of real executions to certify the chosen design (Microsoft Gray Systems Lab, CMU's NoisePage/self-driving line under Pavlo, TU Darmstadt/Binnig on learned cost models). Conformal and distribution-free guarantees over what-if estimates are an emerging 2025–2026 thread *(frontier — verify)*.

## 8. Future Work
- Certified error bars on what-if estimates that compose through a plan.
- Decision-variant guarantees: minimal real-execution budget to certify $(1+\varepsilon)$-optimality of a design.
- Distributionally-robust design over a calibrated set of plausible cost models.
- Benchmarks that report *decision regret* from cost error, not just q-error of cardinalities.

## 9. Key References
- **[Foundational]** Chaudhuri, S., Narasayya, V. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server.* VLDB, 1997.
- **[Foundational]** Moerkotte, G., Neumann, T., Steidl, G. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* PVLDB, 2009.
- **[SOTA]** Kossmann, J., Halfpap, S., Jankrift, M., Schlosser, R. *Magic mirror in my hand, which is the best in the land? An Experimental Evaluation of Index Selection Algorithms.* PVLDB, 2020.
- **[SOTA]** Kipf, A., et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019.
- **[Survey]** Marcus, R., et al. *Neo / Bao: Learned Query Optimization.* PVLDB, 2019–2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
