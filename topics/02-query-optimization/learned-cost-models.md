# Learned cost models with reliability guarantees

> **Topic:** Query Optimization · **ID:** `02-query-optimization/learned-cost-models` · **Status:** empirically-open

## 1. Problem Statement
A query optimizer compares candidate physical plans using a **cost model** $\hat c(p)$ that predicts execution cost (latency, CPU, I/O). Classical cost models are hand-tuned analytic formulas over cardinality estimates; they are systematically biased and brittle. A **learned cost model** replaces (part of) $\hat c$ with a model trained on observed plan executions.

The problem has two intertwined goals:
1. **Accuracy / generalization:** predict cost for **unseen queries, schemas, and data** (out-of-distribution), not just queries resembling the training workload.
2. **Reliability / calibrated uncertainty:** produce a *trustworthy* uncertainty estimate $u(p)$ such that the optimizer can (a) prefer plans whose cost it can predict confidently, and (b) fall back or re-optimize when prediction is unreliable — with **statistical guarantees** (e.g. valid coverage of prediction intervals).

Variants: point-cost regression; interval/quantile prediction; plan *ranking* (only relative order matters for plan choice); and the *guarantee* variant — distribution-free coverage on the prediction interval.

## 2. Mathematical Foundations
Learn $\hat c_\theta: \mathcal{Q}\times\mathcal{P} \to \mathbb{R}_{\ge 0}$ from samples $(p_i, y_i)$, $y_i$ = measured cost, minimizing a loss (often **Q-error** $\max(\hat y/y, y/\hat y)$ rather than MSE, since plan choice is scale-invariant and ratio-sensitive). Plan structure is encoded with **tree/graph neural networks** over the operator tree (TCNNs, tree-LSTMs).

**Generalization** is bounded in terms of model capacity: classical **VC-dimension / Rademacher complexity** bounds give $\text{gen-error} \le \tilde O(\sqrt{\mathfrak{R}_n(\mathcal F)/n})$ on the training distribution — but offer *no* guarantee under **distribution shift** to unseen schemas/queries, which is the operative regime.

**Calibrated uncertainty** is the formal lever for reliability. **Conformal prediction** yields distribution-free, finite-sample marginal coverage: for any model and miscoverage $\alpha$, a calibration set gives an interval $C(p)$ with
$$ \Pr[\,y \in C(p)\,] \ge 1-\alpha, $$
**provided exchangeability** holds. Because queries are *not* exchangeable with training under shift, only **weaker guarantees** (e.g. via weighted/adaptive conformal, or coverage that degrades gracefully with a bounded shift) survive — this is the crux. Bayesian/deep-ensemble uncertainty gives heuristic $u(p)$ without coverage guarantees.

## 3. State of the Art (SOTA)
- **Cardinality side:** learned estimators — MSCN (Kipf et al., CIDR 2019), deep autoregressive/Naru (Yang et al., VLDB 2019/2020), and unsupervised data models — feed cost models.
- **End-to-end cost/latency:** **QPP-Net** (Marcus–Papaemmanouil, 2019), **Neo** (Marcus et al., VLDB 2019) learns value/cost jointly with search, and **Bao** (Marcus et al., SIGMOD 2021) learns to *steer* the existing optimizer with a learned model + **Thompson-sampling uncertainty** — the systems SOTA for *practical, uncertainty-aware* deployment.
- **Zero-shot / transferable cost models** (Hilprecht–Binnig, VLDB 2022) generalize across unseen databases — closest to the OOD goal.
- **Robustness benchmarks:** the work showing learned estimators degrade under shift (Wang et al., "Are We Ready for Learned Cardinality Estimation?", VLDB 2021) frames the empirical openness.

## 4. Upper Bound
On-distribution, learned models achieve **low median Q-error (often < 2)** and tail Q-error far below classical estimators, with TCNN/GNN encoders. With **conformal calibration**, prediction intervals attain the **target marginal coverage $1-\alpha$ under exchangeability** with finite-sample validity (no distributional assumptions). Zero-shot models empirically transfer with bounded accuracy loss to unseen schemas. These are empirical/assumption-conditional upper bounds; there is **no proven worst-case bound** on cost-prediction error for arbitrary unseen queries.

## 5. Lower Bound
- **No-free-lunch / distribution-shift impossibility:** without assumptions linking train and test distributions, **no learner can guarantee bounded prediction error on arbitrary OOD queries** — an information-theoretic barrier; conformal coverage *provably fails* once exchangeability is violated, and the coverage gap can be as large as the total-variation shift.
- **Cardinality propagation:** even a perfect single-table model gives unbounded join-size error in the worst case (correlations), and lower bounds on cardinality sketches/estimators (e.g. communication-complexity bounds for distinct/join-size estimation) propagate into cost error.
- Thus reliability with *hard* guarantees on truly unseen queries is provably impossible in full generality; only *conditional* (bounded-shift) guarantees are attainable.

## 6. The Gap
The gap is **empirically open and partly impossibility-bounded**: on-distribution accuracy and exchangeable-case calibration are essentially solved, but the *operative* regime — unseen schemas/queries under shift — admits no model with worst-case error or coverage guarantees, and empirically models still mispredict badly on tail/OOD plans. Closing the *practical* gap means engineering models + uncertainty that **detect** their own OOD inputs and degrade gracefully; closing the *theoretical* gap requires realistic structural assumptions (bounded shift, schema-invariance) under which provable coverage is recoverable.

## 7. Current Research (as of June 2026)
- **Uncertainty-aware optimization:** using calibrated $u(p)$ to gate plan choice, trigger re-optimization, or blend learned and analytic costs (Bao-style steering generalized). *(frontier — verify)*
- **Transferable/foundation cost models** pretrained across many databases for true zero-shot use; LLM-assisted plan/cost reasoning. *(frontier — verify)*
- **Shift-robust conformal** and selective prediction for query cost; OOD detection on plan trees.
- Groups: Marcus/Kraska & MIT DSAIL, Binnig (TU Darmstadt, zero-shot), Microsoft/Alibaba/cloud-warehouse learned-optimizer teams, robust-estimation benchmarkers.

## 8. Future Work
- Distribution-free coverage guarantees valid under bounded, *measured* workload shift.
- Cost models with monotonicity/physics constraints baked in (so predictions stay sane OOD).
- Joint cardinality+cost uncertainty propagated coherently through plan enumeration.

## 9. Key References
- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1904.03711)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** Hilprecht, Binnig. *Zero-Shot Cost Models for Out-of-the-Box Learned Cost Prediction.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2201.00561)
- **[Survey]** Wang, Qu, Li, et al. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2012.06743)
- **[Foundational]** Vovk, Gammerman, Shafer. *Algorithmic Learning in a Random World* (conformal prediction). Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)

## 10. Worked Example

**Q-error and why plan choice survives miscalibration.** Two plans $A,B$ for one query have true costs $y_A=100$, $y_B=400$. A learned model predicts $\hat y_A=150$, $\hat y_B=300$. Per-plan Q-error is $\max(\hat y/y,\,y/\hat y)$: for $A$, $\max(1.5,0.67)=1.5$; for $B$, $\max(0.75,1.33)=1.33$. Both modest, and crucially the model preserves the *ranking* $\hat y_A<\hat y_B$, so it still picks the truly cheaper plan $A$ — illustrating why ratio metrics and ranking matter more than absolute MSE.

**Conformal interval.** Suppose a calibration set of $n=99$ held-out plans yields absolute residuals; for target $\alpha=0.1$ we take the $\lceil(1-\alpha)(n+1)\rceil=90$-th smallest residual, say $q=120$. The interval for a new plan is $\hat y \pm 120$, with guaranteed marginal coverage $\Pr[y\in C]\ge 0.9$ — *only* if the new plan is exchangeable with calibration. Deploy on an unseen schema and exchangeability breaks: empirical coverage can collapse toward $1-\alpha-\text{TV}$, the crux of section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
