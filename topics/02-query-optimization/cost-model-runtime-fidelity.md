# Cost models that predict real runtime

> **Topic:** Query Optimization · **ID:** `02-query-optimization/cost-model-runtime-fidelity` · **Status:** empirically-open

## 1. Problem Statement

An optimizer's job is to pick the plan that runs fastest. It does so via a **cost model** $C$ that
maps a plan to a scalar proxy for runtime. The model need not predict absolute time — it must
**rank** plans the same way wall-clock time does. The problem: **build a cost model whose induced
ordering over candidate plans matches measured wall-clock runtime on modern hardware** (multi-core,
deep cache hierarchies, SIMD, NUMA, SSD/NVMe, GPUs), across data sizes and concurrency.

Formally, given the plan space $\mathcal{T}$ for a query and the true runtime $R: \mathcal{T} \to
\mathbb{R}_{+}$, find $C$ minimizing a **ranking loss** (e.g. number of inverted pairs, or regret of
the $C$-argmin vs. the $R$-argmin):
$$\text{regret}(C) = \frac{R(\arg\min_T C(T))}{\min_T R(T)} .$$
This is "empirically-open": no closed-form model is known to be faithful, and the question is largely
measured rather than proven.

## 2. Mathematical Foundations

Traditional cost models are **analytic**: $C = w_{cpu}\cdot \text{tuples} + w_{io}\cdot \text{pages}
+ \dots$ with hand-tuned weights, assuming the bottleneck is I/O or tuple count. Modern engines are
often **CPU/cache/memory-bandwidth bound**, so the relevant cost is dominated by cache misses, branch
mispredictions, and vectorization efficiency — quantities poorly captured by tuple counts.

The fidelity requirement is **ordinal**: we need $C$ to be a **monotone surrogate** of $R$ on
$\mathcal{T}$, i.e. preserve the argmin and ideally the ranking (Kendall-$\tau$ / Spearman
correlation, or pairwise inversion count). A model can be badly miscalibrated in absolute terms yet
rank-faithful. The Leis et al. JOB study decomposed optimizer error into **cardinality** error vs.
**cost-model** error and found cardinality dominates — but with perfect cardinalities, residual
cost-model/runtime mismatch persists, which is the target here.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Sparse. The abstract ASI/$C_{out}$ models are analytically tractable but
  acknowledged to be poor runtime predictors; there is no theory guaranteeing rank-fidelity on real
  hardware.
- **Systems-SOTA:** Learned cost models — **MSCN** (Kipf et al., CIDR 2019), **QPP-Net / tree
  convolution** (Marcus–Papaemmanouil 2019), **Bao** (Marcus et al., SIGMOD 2021), and learned
  end-to-end optimizers (**Neo**, **Balsa**) — predict latency directly from plan features and
  empirically improve plan ranking over analytic models. Leis et al. (VLDB 2015, 2018) and the
  "Cardinality Estimation Done Right" / re-optimization lines provide the strongest empirical
  baselines. Hyper/Umbra calibrate cost weights to compiled, vectorized execution.

## 4. Upper Bound

- No proven upper bound on achievable rank-fidelity exists. Empirically, learned models report
  high pairwise-ranking accuracy and substantial **end-to-end latency** improvements over
  PostgreSQL's analytic model on benchmarks (JOB, Stack, TPC-DS) — but with no guarantee and known
  out-of-distribution degradation (model: empirical, fixed hardware/workload).
- With perfect cardinalities, a well-calibrated analytic model achieves near-optimal plan choice on
  JOB (Leis et al.), bounding how much remaining error is *cost-model* vs. *cardinality*.

## 5. Lower Bound

- This is fundamentally an **empirical / lower-bound-free** problem: runtime depends on hardware
  micro-architecture, concurrent load, data placement, and JIT effects that are not fully observable
  at plan time, so a *perfect* a-priori model is impossible in any realistic model (an
  information-availability barrier, not a complexity one).
- Learned models inherit **distribution-shift** lower bounds: no fixed model can be faithful across
  arbitrary unseen schemas/hardware without retraining (a no-free-lunch / generalization argument).

## 6. The Gap

The gap is **empirical and definitional**: we lack (a) an agreed benchmark and metric for *rank*
fidelity (not absolute-error), (b) hardware-portable cost models that transfer without per-system
retraining, and (c) any theoretical handle on when a surrogate provably preserves the argmin. Because
the obstacle is observability rather than computational hardness, the problem stays "empirically-open"
— progress is measured on real systems, not closed by a proof.

## 7. Current Research (as of June 2026)

- Hybrid analytic+learned cost models with uncertainty and transfer learning across hardware (TUM,
  MIT, CMU). *(frontier — verify)*
- Zero-shot / pre-trained cost models that generalize to unseen databases (e.g. the "zero-shot cost
  estimation" line). *(frontier — verify)*
- Hardware-aware costing for GPUs, NVMe, and disaggregated cloud storage; costing under concurrency.

## 8. Future Work

- A standard rank-fidelity benchmark and metric for cost models.
- Portable, hardware-parameterized models requiring minimal calibration.
- Theoretical conditions under which a surrogate cost preserves the optimal plan.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[SOTA]** Kipf, Kipf, Radke, Leis, Boncz, Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** Marcus, Negi, Mao, et al. *Neo: A Learned Query Optimizer.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3342263.3342644)
- **[Survey]** Lan, Bao, Peng. *A Survey on Advancing the DBMS Query Optimizer: Cardinality Estimation, Cost Model, and Plan Enumeration.* Data Science and Engineering, 2021. — [DOI](https://doi.org/10.1007/s41019-020-00149-7)

## 10. Worked Example

Three candidate plans for one query, with the analytic cost model $C$ (tuples + pages) and measured wall-clock $R$ (seconds):

| Plan | $C$ (model) | $R$ (real) |
|------|------------|-----------|
| $P_1$ (nested-loop join) | 1.0 | 4.0 |
| $P_2$ (hash join, cache-friendly) | 1.5 | 1.0 |
| $P_3$ (sort-merge) | 1.2 | 2.5 |

The model ranks $P_1 < P_3 < P_2$ and picks $P_1$. The true ranking is $P_2 < P_3 < P_1$ — so the model's argmin ($P_1$) is the *worst* plan. Regret:
$$\text{regret}(C) = \frac{R(\arg\min_T C(T))}{\min_T R(T)} = \frac{R(P_1)}{R(P_2)} = \frac{4.0}{1.0} = 4.0.$$

A $4\times$ slowdown despite "minimizing cost." The failure is **ordinal**: $C$ rewards $P_1$'s low tuple count but ignores that its nested-loop pattern thrashes cache, while $P_2$'s vectorized hash probe stays in L2. Note $C$ need not be calibrated in absolute terms — it only needs to invert *zero* pairs. Here it inverts all three, the canonical rank-infidelity that learned cost models target.

---
*Part of the [DBMS Research catalog](../../README.md).*
