# Self-Tuning / Feedback-Driven Statistics

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/feedback-driven-statistics` · **Status:** partially-solved

## 1. Problem Statement

Cardinality estimates produced before execution are routinely wrong (independence/uniformity assumptions, stale stats). **Feedback-driven** (a.k.a. self-tuning, learning-from-execution) statistics observe the **actual** cardinalities of operators during/after query execution and use them to correct future estimates and refine synopses — without an explicit, expensive statistics-collection scan.

Formally: maintain a synopsis / model $M$ that maps a predicate or sub-plan $p$ to an estimate $\hat{c}(p)$. After executing queries we obtain observations $(p_i, c_i)$ where $c_i$ is the true cardinality. The task is to update $M \to M'$ so that estimates improve on the observed and on **future related** queries, subject to (a) bounded synopsis space, (b) consistency with structurally valid observations, and (c) avoiding overfitting to a non-stationary workload.

Variants: **online learning** (regret over a query stream), **synopsis-correction** (adjust histogram bucket counts), and **query-driven model fitting** (train an estimator on a query log).

## 2. Mathematical Foundations

Cast as **online / regret-minimizing learning**: estimates are predictions, observed cardinalities are losses (e.g. squared log-error $(\log \hat{c} - \log c)^2$, the q-error metric $\max(\hat{c}/c, c/\hat{c})$). The goal is sublinear regret against the best fixed synopsis in hindsight.

The correction problem under structural constraints is a **constrained least-squares / maximum-entropy** problem: given marginal observations, find the distribution of minimum relative entropy (KL divergence) consistent with them — the **iterative proportional fitting / maximum-entropy** principle (Markl et al.'s "Consistently Estimating the Selectivity of Conjuncts"). For histogram correction, STHoles frames bucket refinement to minimize observed error.

Foundations drawn upon: convex optimization (max-entropy is convex), online learning theory (regret bounds, expert aggregation), and active learning (which queries are most informative to observe).

## 3. State of the Art (SOTA)

**Systems-SOTA:**
- **LEO — DB2's LEarning Optimizer** (Stillger, Lohman, Markl, Raman, VLDB 2001): compares estimated vs. actual cardinalities at runtime and stores adjustments; the canonical feedback-driven system.
- **STHoles** (Bruno–Chaudhuri–Gravano, SIGMOD 2001): workload-aware self-tuning multidimensional histogram built purely from query feedback.
- **Max-entropy consistency** (Markl et al., VLDB 2005): combines multiple feedback selectivities into a single consistent model.
- **ISOMER** (Srivastava et al., ICDE 2006): information-theoretic (max-entropy) histogram refinement from feedback, with principled handling of stale feedback.
- **Query-driven learned estimators:** MSCN (Kipf et al., CIDR 2019), and feedback loops in commercial optimizers (SQL Server's auto-stats / cardinality feedback in recent releases).

## 4. Upper Bound

Max-entropy reconciliation is a convex program solvable to $\varepsilon$-accuracy in polynomial time (per update, in the number of feedback constraints). ISOMER bounds the synopsis size by retaining only the most informative constraints (LP-based selection), giving controlled space. Online-learning formulations yield $O(\sqrt{T})$ regret over a stream of $T$ queries against the best fixed model, with multiplicative-weights / online-convex-optimization analyses. In practice LEO-style correction provably never increases error on the exact repeated query (it stores the truth) and empirically improves neighbors.

## 5. Lower Bound

Hardness is fundamentally about **generalization and non-stationarity**, not single-query correction (which is trivial — store the answer). Information-theoretically, no bounded synopsis can be accurate for an adversarial, ever-shifting workload: any learner suffers $\Omega(\sqrt{T})$ regret in the worst case (standard online-learning lower bound). Reconstructing a joint distribution from a limited set of marginal/range feedbacks is underdetermined — many distributions fit, so error on unseen queries is unavoidable without distributional assumptions (an info-theoretic identifiability gap). Active-learning lower bounds limit how fast feedback reduces uncertainty.

## 6. The Gap

The problem is **partially solved**: correcting *seen* queries and reconciling feedback consistently (max-entropy/ISOMER) is well understood and deployed. The **open** part is principled **generalization to unseen queries** and **robustness under drift**: when to trust stale feedback, how to forget, how to avoid feedback-loop instability (estimates affecting plans affecting which feedback is gathered). Closing it needs regret/generalization guarantees for the *query-prediction* problem under realistic distribution shift, plus exploration strategies that gather the most informative feedback.

## 7. Current Research (as of June 2026)

- **Robust and uncertainty-aware learned estimators** that incorporate execution feedback online and quantify confidence *(frontier — verify)*.
- **Bandit / active-learning** views of which sub-plans to materialize feedback for.
- **Drift detection and forgetting** policies for streaming workloads; reinforcement-learning optimizers (Neo, Bao, Balsa lineage) that consume execution feedback.
- Stability analysis of optimizer–statistics feedback loops to prevent oscillation.

## 8. Future Work

- Provable generalization bounds for query-driven estimators under workload shift.
- Unified frameworks combining data-driven synopses with query feedback (best of both).
- Safe exploration so feedback collection does not regress plan quality.
- Theory of feedback-loop stability between optimizer and self-tuning stats.

## 9. Key References

- **[Foundational]** Stillger, Lohman, Markl, Raman. *LEO – DB2's LEarning Optimizer.* VLDB, 2001.
- **[Foundational]** Bruno, Chaudhuri, Gravano. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD, 2001.
- **[SOTA]** Markl, Haas, Kutsch, Megiddo, Srivastava, Tran. *Consistently Estimating the Selectivity of Conjuncts of Predicates (max-entropy).* VLDB, 2005.
- **[SOTA]** Srivastava, Haas, Markl, Kutsch, Tran. *ISOMER: Consistent Histogram Construction Using Query Feedback.* ICDE, 2006.
- **[SOTA]** Kipf, Kipf, Radke, Leis, Boncz, Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019.
- **[Survey]** Chaudhuri, Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
