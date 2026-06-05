# Learned Estimator Generalization & Drift

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/learned-estimator-drift` · **Status:** empirically-open
> **Verification note:** The VLDB 2009 q-error paper's third author is Gabriele Steidl (the prior "Steinbrunn" was a citation error, now corrected).

## 1. Problem Statement

Learned cardinality estimators (LCE) replace hand-tuned statistics with ML models that map a query (and/or data) to a predicted cardinality. The problem: **characterize, detect, and bound the degradation of an LCE when the query workload or data distribution at inference time differs from training time** ("off-distribution" or "drift").

Variants:

- **Generalization (decision/estimation):** given a model trained on workload $W_{train}$ over data $D_{train}$, bound expected/worst-case q-error on a *different* test distribution $W_{test}, D_{test}$.
- **Detection (monitoring):** decide online whether the current query/data is out-of-distribution (OOD) enough that the prediction is untrustworthy, ideally without ground-truth cardinalities.
- **Adaptation (optimization):** update the model under bounded resources so accuracy is restored after drift, without catastrophic forgetting.

Why it matters: a single severe under-estimate can flip a plan to a catastrophic nested-loop join; optimizers need *reliability*, not just average accuracy.

## 2. Mathematical Foundations

The target is selectivity $s(q)\in[0,1]$ or cardinality $c(q)=s(q)\cdot n$. Standard error metric is **q-error**: $\mathrm{qerr}(q)=\max\!\big(\hat c(q)/c(q),\, c(q)/\hat c(q)\big)\ge 1$, which is the multiplicative metric that controls plan-cost bounds (Moerkotte–Neumann–Steidl, VLDB 2009: bounding q-error bounds plan suboptimality).

Drift is a distribution shift: training draws $(q,c)\sim P_{train}$, deployment draws from $Q\ne P_{train}$. Classic learning theory bounds generalization *within* a distribution via VC-dimension / Rademacher complexity $\hat R_m(\mathcal F)$, giving $|R(\hat f)-\hat R(\hat f)|\le 2\hat R_m(\mathcal F)+O(\sqrt{\log(1/\delta)/m})$. Under shift these break; the relevant tools are **domain-adaptation bounds** (Ben-David et al.): $\epsilon_T(h)\le \epsilon_S(h)+\tfrac12 d_{\mathcal H\Delta\mathcal H}(P_S,P_T)+\lambda$, where $d_{\mathcal H\Delta\mathcal H}$ is a divergence between train/test marginals. The data-side analogue uses changes in the joint $\Pr[A_1,\dots,A_k]$ that an autoregressive density model (e.g. a deep model of $\prod_j \Pr[A_j\mid A_{<j}]$) has learned.

## 3. State of the Art (SOTA)

- **Query-driven:** MSCN (Kipf et al., CIDR 2019) — multi-set convolutional network over (tables, joins, predicates). Lightweight, but degrades on unseen join templates.
- **Data-driven:** Naru / NeuroCard (Yang et al., VLDB 2019/2020) — deep autoregressive models of the joint distribution with progressive sampling; DeepDB (Hilprecht et al., VLDB 2020) — sum-product networks (relational SPNs).
- **Benchmark-SOTA:** the unified study **"Are We Ready for Learned Cardinality Estimation?"** (Wang et al., VLDB 2021) showed data-driven models dominate accuracy but suffer on updates/drift; **CEB / job-light / STATS-CEB** are the standard stress benchmarks.
- **Robustness thread:** RobustMSCN and factorized/uncertainty-aware estimators; *(frontier — verify)* recent work adds conformal wrappers and OOD detectors on top of MSCN/Naru.

## 4. Upper Bound

There is no general worst-case approximation guarantee for LCEs off-distribution — this is precisely why status is *empirically-open*. **Conditional** upper bounds exist:

- Domain-adaptation theory bounds test error by $d_{\mathcal H\Delta\mathcal H}$ plus the ideal joint risk $\lambda$; when $\lambda$ is large (no hypothesis good on both), no useful bound follows.
- For data-driven density models, if the learned density has KL divergence $\le \kappa$ from the true joint, range-query selectivity error is bounded by a function of $\kappa$ and predicate volume — but $\kappa$ itself is unbounded under drift.

## 5. Lower Bound

- **Information-theoretic:** if test predicates touch regions with zero training support, any estimator's error is unbounded — no algorithm can recover unseen joint mass (this is the OOD impossibility, analogous to no-free-lunch).
- **Detection hardness:** distinguishing a benign shift from a malignant one without labels reduces to two-sample / density-ratio testing, which has sample-complexity lower bounds growing with dimension (curse of dimensionality in multi-column joints).
- **Sampling barrier inherited:** any LCE that internally samples to answer inherits the $\Omega(\sqrt{n/r})$ NDV/selectivity sampling bounds for selective predicates.

## 6. The Gap

The gap is **genuinely open and largely empirical**: we lack (a) a metric on queries/data that *provably* predicts q-error degradation, and (b) any LCE with a worst-case off-distribution guarantee. What would close it: distribution-shift-aware training with certified bounds (e.g. conformal prediction giving valid coverage under covariate shift via weighting), or a hardness theorem proving no compact learned model can be both accurate and drift-robust across a stated workload class.

## 7. Current Research (as of June 2026)

- Conformalized cardinality estimation: wrapping LCEs to emit calibrated intervals with coverage guarantees under exchangeability/weighted shift *(frontier — verify)*.
- Update-aware / incremental models (Naru-style retraining triggers, DDUp) and drift detectors using model confidence or density-ratio monitors.
- Hybrid "guardrail" architectures: learned point estimate + classical pessimistic upper bound (e.g. AGM/sketch) as a safety floor (Cai et al. "pessimistic CE" line; CEB authors; groups of Kemper/Neumann at TUM, Kraska/MIT, Stoica/Berkeley, Chaudhuri/Microsoft Research).
- Benchmarks emphasizing *robustness* (STATS-CEB with updates) over single-shot accuracy.

## 8. Future Work

- Certified q-error bounds under bounded distribution shift.
- Cheap, label-free OOD signals tied directly to optimizer risk.
- Lifelong/continual LCE with bounded forgetting and provable recovery time after drift.
- Standard reporting of *tail* q-error (e.g. 99.9th percentile) rather than median.

## 9. Key References

- **[Foundational]** Moerkotte, Neumann, Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009. — [DBLP](https://dblp.org/rec/journals/pvldb/MoerkotteNS09.html)
- **[SOTA]** Kipf, Kipf, Radke, Leis, Boncz, Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019; *NeuroCard.* VLDB, 2021. — [arXiv](https://arxiv.org/abs/1905.04278)
- **[SOTA]** Hilprecht et al. *DeepDB: Learn from Data, not from Queries!* VLDB, 2020. — [arXiv](https://arxiv.org/abs/1909.00607)
- **[Survey/SOTA]** Wang, Qu, Wu, Wang, Zhou. *Are We Ready for Learned Cardinality Estimation?* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2012.06743)
- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)

## 10. Worked Example

Train an LCE on a `sales` table where the workload only filters `year IN {2023, 2024}`. For these years the model learns the empirical selectivity of `region='West'` accurately: say true $s=0.30$ and $\hat s=0.31$.

**Drift at inference.** A new query filters `year=2025`, a region/year combination absent from training. Suppose the true 2025 selectivity of `region='West'` is $s=0.05$ (the West market shrank), but the model — having only seen 2023–24 — predicts $\hat s\approx0.30$. On $n=10^6$ rows:
$$\hat c=0.30\times10^6=300{,}000,\qquad c=0.05\times10^6=50{,}000,\quad \mathrm{qerr}=\frac{300{,}000}{50{,}000}=6.$$
A factor-6 over-estimate. If a join with this predicate feeds a hash build, the optimizer over-allocates; worse, a factor-6 *under*-estimate on the other branch can flip to a catastrophic nested loop.

**Why detection is hard.** Without executing the 2025 query we have no ground-truth $c$, so the q-error of $6$ is invisible. A label-free OOD signal — e.g. the density model assigning low likelihood to the `year=2025` slice, or a domain-divergence $d_{\mathcal H\Delta\mathcal H}$ spike between the 2025 marginal and training marginal — is exactly what is needed to flag "this estimate is untrustworthy" before the plan commits.

---
*Part of the [DBMS Research catalog](../../README.md).*
