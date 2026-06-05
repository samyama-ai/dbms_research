# Drift Detection and Retraining Triggers

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/ce-drift-retraining-triggers` · **Status:** open

## 1. Problem Statement

A learned estimator, learned index, or learned optimizer is trained on a snapshot of
data and workload. As the data and query distribution **drift**, its accuracy decays.
The problem: detect, with **formal staleness bounds**, when a learned component has
degraded enough to warrant retraining (or fallback), minimizing total cost = (errors
from staleness) + (retraining cost), ideally **without** materializing ground truth.

- **Decision variant:** at time $t$, decide RETRAIN vs. KEEP given observed signals.
- **Optimization variant:** an online policy minimizing cumulative regret
  $\sum_t \mathrm{loss}(t) + \lambda\cdot(\text{retrains})$ over a stream of updates
  and queries.
- **Detection variant:** raise an alarm within delay $\Delta$ of a change of magnitude
  $\ge\eta$, with bounded false-alarm rate.

"Solving" means a trigger with provable guarantees on detection delay, false-alarm
rate, and post-trigger staleness — not a hand-tuned heuristic threshold.

## 2. Mathematical Foundations

This is **online change-point detection** plus **competitive online decision-making**:

- **Change detection:** CUSUM and the Shiryaev–Roberts procedure are optimal in the
  minimax (Lorden) and Bayesian senses for detecting a distribution shift with
  minimum expected delay subject to a false-alarm constraint; ADWIN gives adaptive
  windowing with bounds for streaming. For estimator drift the monitored statistic is
  q-error or a distance $d(\mathcal D_t, \mathcal D_{\text{train}})$.
- **Staleness as distribution distance:** total variation / Wasserstein /
  $f$-divergence between training and current data distributions upper-bounds the
  added estimation error via Lipschitz/sensitivity arguments,
  $|L_t - L_{\text{train}}| \le C\cdot d(\mathcal D_t,\mathcal D_{\text{train}})$.
- **Online learning / regret:** RETRAIN-vs-KEEP is a metrical task / ski-rental-like
  problem; competitive ratios bound performance vs. the optimal offline retrain
  schedule. PAC-style concept-drift bounds (Bartlett) relate drift rate to achievable
  error.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Classical optimal change detection (Page 1954; Lorden 1971;
  Shiryaev) and streaming drift detectors with guarantees — **ADWIN**
  (Bifet–Gavaldà, SDM 2007) bounds false positives/negatives via Hoeffding. These are
  not DB-specific but directly applicable to a monitored q-error stream.
- **Systems SOTA:** Learned-index updatability — **ALEX** (SIGMOD 2020), **LIPP**,
  **PGM-index** (VLDB 2020) — handle inserts with bounded error online, partially
  sidestepping retraining. For learned optimizers, **Bao** (SIGMOD 2021) uses bandit
  feedback to adapt online; production guidance favors monitoring plan regressions.
  No system ties retraining to a *formal* staleness bound on q-error.

## 4. Upper Bound

For a monitored loss with sub-Gaussian fluctuations, CUSUM/SR achieve expected
detection delay $O\!\big(\log(1/\alpha)/\,\mathrm{KL}(\text{post}\|\text{pre})\big)$
for false-alarm rate $\alpha$ — **information-theoretically order-optimal**. Cast as
ski-rental, the RETRAIN/KEEP decision admits a deterministic $2$-competitive and a
randomized $e/(e-1)$-competitive policy against the offline optimum (**online model**).
ADWIN bounds both error rates with window size adapting to the true change.

## 5. Lower Bound

Detection delay is fundamentally limited: any procedure with false-alarm period $\ge T$
incurs worst-case expected delay $\ge \log T/\mathrm{KL}(\text{post}\|\text{pre})$
(Lorden's **information-theoretic** lower bound) — small drift is provably slow to
detect. Without observing ground-truth cardinalities, distinguishing a benign query-
mix change from genuine data drift can require $\Omega(1/\eta^2)$ samples (estimation
lower bound). Ski-rental gives a matching competitive lower bound of $2$
(deterministic) for the keep/retrain trade-off.

## 6. The Gap

The detection-theory side is essentially **closed** (matching delay bounds); the open
gap is **DB-specific**: (1) the staleness signal is usually *unlabeled* (true
cardinalities unknown at query time), so the monitored statistic is a proxy whose
relationship to actual plan regret is not tightly characterized; (2) no end-to-end
bound links data-distribution distance → estimator q-error → optimizer plan regret →
runtime cost. Closing it means a verified Lipschitz chain from drift magnitude to
runtime regret, and cheap unlabeled drift proxies with provable correlation to q-error.

## 7. Current Research (as of June 2026)

- Self-supervised / proxy drift signals (embedding-distribution shift, feedback from
  actual vs. estimated row counts in completed queries) *(frontier — verify)*.
- Cost-aware retraining schedulers using bandit/RL over the keep-retrain decision,
  extending Bao-style feedback to estimators *(frontier — verify)*.
- Incremental and continual learning for indexes/estimators to reduce retrain cost
  (ALEX/PGM lineage), shifting the trade-off rather than just detecting it.

## 8. Future Work

- Certified end-to-end staleness → plan-regret bounds.
- Optimal joint policy over {monitor, partial-retrain, full-retrain, fallback}.
- Drift detectors robust to adversarial / seasonal workloads with bounded false alarms.

## 9. Key References

- **[Foundational]** G. Lorden. *Procedures for Reacting to a Change in Distribution.* Ann. Math. Statist., 1971.
- **[Foundational]** A. Bifet, R. Gavaldà. *Learning from Time-Changing Data with Adaptive Windowing (ADWIN).* SDM 2007.
- **[SOTA]** J. Ding et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD 2020.
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021.
- **[Survey]** J. Gama et al. *A Survey on Concept Drift Adaptation.* ACM Computing Surveys, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
