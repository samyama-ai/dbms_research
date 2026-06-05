# Online model maintenance under concept drift

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/online-model-drift` · **Status:** empirically-open

## 1. Problem Statement
An in-database forecaster or anomaly detector is fitted to historical series, then must stay accurate as the underlying data-generating distribution **drifts** (seasonality changes, regime shifts, deployment changes, sensor recalibration). The problem: maintain in-DB models so that predictive quality stays within a tolerance of the best model-in-hindsight, with **bounded staleness** (model lag $\le \Delta$) and a bounded *maintenance budget* (CPU/memory per ingested point), across millions of concurrently drifting series. Decisions: *when* to update/retrain (trigger), *how much* (incremental update vs. full refit), and *what to forget* (window/decay). Distinguish **abrupt** drift (changepoint), **gradual/incremental** drift, and **recurring/seasonal** drift, which demand different forgetting strategies.

The "empirically-open" status reflects that strong *empirical* methods exist (drift detectors + online learners) but **provable** bounds tying regret to drift magnitude under realistic per-point compute budgets at TSDB scale do not.

## 2. Mathematical Foundations
Frame maintenance as **online learning against a changing comparator**. With losses $\ell_t(\theta)$, performance is *dynamic regret*
$$ R_T^{\mathrm{dyn}} = \sum_{t=1}^T \ell_t(\theta_t) - \sum_{t=1}^T \ell_t(\theta_t^\star), \qquad \theta_t^\star=\arg\min_\theta \ell_t(\theta), $$
bounded in terms of the **path length** $P_T=\sum_t\|\theta_t^\star-\theta_{t-1}^\star\|$ or number of changepoints. Online gradient/mirror descent and *Online Newton Step* achieve $R_T^{\mathrm{dyn}}=O(\sqrt{T(1+P_T)})$ (Zinkevich 2003; Hall–Willett; Zhang–Lu–Zhou 2018), and *strongly-adaptive* / sleeping-experts meta-algorithms (Hazan–Seshadhri; Daniely–Gonen–Shalev-Shwartz 2015) guarantee low *static* regret on every interval, automatically tracking abrupt drift. Drift **detection** rests on sequential change-point theory: CUSUM, Page's test, and ADWIN (Bifet–Gavaldà 2007) give adaptive-window estimators with false-positive/detection-delay trade-offs. Forgetting is formalized via exponential decay or sliding windows; the optimal window is a bias–variance trade-off against local stationarity length.

## 3. State of the Art (SOTA)
**Systems-SOTA:** River (online ML, merged Creme + scikit-multiflow), Vowpal Wabbit, and streaming-ML in Spark/Flink provide incremental learners + drift detectors (ADWIN, DDM, EDDM, Page-Hinkley). In-DB: BigQuery ML and ClickHouse retrain on schedule (time-triggered, not drift-triggered); ML-on-streams in ksqlDB/Materialize is nascent. Vendor anomaly stacks (Datadog watchdog, Grafana ML) adapt models continuously but publish no guarantees *(frontier — verify)*. **Theory-SOTA:** dynamic-regret and strongly-adaptive online learning (Zhang et al. 2018; Daniely et al. 2015), and optimal sequential change detection (Lai 1998; Lorden). These are not yet unified with *per-point compute budgets* across many series.

## 4. Upper Bound
For a single series with convex losses, projected online gradient descent gives $R_T^{\mathrm{dyn}}=O(\sqrt{T(1+P_T)})$, and with curvature, $O(\sqrt{T\,V_T})$ where $V_T$ is comparator variation — both with $O(d)$ time/space per step (RAM/online model). Strongly-adaptive methods add only an $O(\log T)$ factor while guaranteeing near-optimal regret on *every* sub-interval, i.e., automatic recovery after any abrupt drift. ADWIN detects a distribution change of magnitude $\epsilon$ with $O(\log(1/\delta))$-bounded false-alarm rate and detection delay $O(\sigma^2\log(1/\delta)/\epsilon^2)$, using $O(\log W)$ memory.

## 5. Lower Bound
Dynamic regret is **provably lower-bounded** by $\Omega(\sqrt{T(1+P_T)})$ — no online algorithm beats the path-length rate (information-theoretic, via a two-point/adversary construction). For change *detection*, there is a fundamental **detection-delay vs. false-alarm** trade-off: Lorden/Lai lower bounds force expected delay $\gtrsim \log(\text{ARL})/\mathrm{KL}$ for a target average run length to false alarm. Thus *zero-staleness* maintenance under nonzero drift is impossible; some lag is information-theoretically required. Under a *fixed per-point compute budget* shared across $m$ series, an adversary can force $\Omega(m)$ aggregate staleness — formalizing this budget-vs-freshness barrier is largely open.

## 6. The Gap
Single-series theory is tight ($\Theta(\sqrt{T(1+P_T)})$ dynamic regret; matching detection-delay bounds). The **gap is at scale and under budget**: there is no proven characterization of achievable staleness/accuracy when a *bounded total compute budget* must be scheduled across millions of independently drifting series, nor of how drift-triggered (vs. periodic) retraining provably allocates that budget. This is **empirically open** — practitioners have working heuristics; matching upper/lower bounds for the *multi-series budgeted* problem do not exist.

## 7. Current Research (as of June 2026)
Threads: **budgeted retraining scheduling** as a restless-bandit / scheduling problem over series, prioritizing the most-drifted under a compute cap *(frontier — verify)*; continual/online adaptation of TS *foundation models* (test-time adaptation of TimesFM/Chronos without catastrophic forgetting) *(frontier — verify)*; drift-aware conformal recalibration linking to `in-db-forecasting-bounds.md`; and theory unifying strongly-adaptive online learning with change detection (Willett/Wisconsin, Zhang/Nanjing, Orabona). Streaming-DB integration (Materialize, RisingWave, Feldera) for incremental model state is an active systems direction.

## 8. Future Work
- Provable accuracy/staleness bounds for *budget-constrained multi-series* maintenance (scheduling + bandits + dynamic regret unified).
- Drift-triggered vs. periodic retraining with formal regret/cost guarantees.
- Test-time adaptation of large TS foundation models inside the DB without full refits.
- Standard drift benchmarks at TSDB cardinality (millions of series, realistic regime shifts).

## 9. Key References
- **[Foundational]** M. Zinkevich. *Online Convex Programming and Generalized Infinitesimal Gradient Ascent.* ICML, 2003. — [ACM](https://dl.acm.org/doi/10.5555/3041838.3041955), [DBLP](https://dblp.org/rec/conf/icml/Zinkevich03.html)
- **[Foundational]** A. Bifet, R. Gavaldà. *Learning from Time-Changing Data with Adaptive Windowing (ADWIN).* SDM, 2007. — [DOI](https://doi.org/10.1137/1.9781611972771.42)
- **[SOTA]** L. Zhang, S. Lu, Z.-H. Zhou. *Adaptive Online Learning in Dynamic Environments.* NeurIPS, 2018. — [arXiv](https://arxiv.org/abs/1810.10815)
- **[SOTA]** A. Daniely, A. Gonen, S. Shalev-Shwartz. *Strongly Adaptive Online Learning.* ICML, 2015. — [PMLR](https://proceedings.mlr.press/v37/daniely15.html), [arXiv](https://arxiv.org/abs/1502.07073)
- **[Foundational]** T. L. Lai. *Information Bounds and Quick Detection of Parameter Changes in Stochastic Systems.* IEEE Trans. Information Theory, 1998. — [DOI](https://doi.org/10.1109/18.737522)
- **[Survey]** J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, A. Bouchachia. *A Survey on Concept Drift Adaptation.* ACM Computing Surveys, 2014. — [DOI](https://doi.org/10.1145/2523813)

## 10. Worked Example

A sensor's forecaster tracks a mean that abruptly jumps at $t=500$ from $\mu=10$ to $\mu=14$ (a regime shift). Compare two maintenance policies.

**Periodic retrain (every 100 steps).** Between the drift at $t=500$ and the next scheduled refit at $t=600$, the model predicts $\hat\mu=10$ while truth is $14$, paying squared loss $\approx 16$ per step for $100$ steps $\Rightarrow$ accumulated excess loss $\approx 1600$. Staleness $\le 100$ regardless of when drift happens.

**Drift-triggered (ADWIN + online GD).** ADWIN holds a window and splits it when two sub-windows differ by more than a Hoeffding bound $\epsilon_{\text{cut}}$. With variance $\sigma^2=1$, shift $\delta=4$, confidence $\delta_{\text{conf}}=0.05$, detection delay is $O\!\big(\tfrac{\sigma^2\log(1/\delta_{\text{conf}})}{\delta^2}\big)\approx \tfrac{1\cdot 3}{16}\approx$ a handful of steps; say the cut fires at $t=510$. The model retrains on the post-cut window and excess loss is incurred for only $\approx 10$ steps $\Rightarrow \approx 160$, a $10\times$ reduction.

**Why some lag is unavoidable.** The Lai/Lorden bound forces expected detection delay $\gtrsim \log(\text{ARL})/\mathrm{KL}$. Here $\mathrm{KL}$ between $\mathcal N(10,1)$ and $\mathcal N(14,1)$ is $\delta^2/2 = 8$; targeting average run length to false alarm $\text{ARL}=10^4$ gives delay $\gtrsim \ln(10^4)/8 \approx 1.15$ steps — so even an optimal detector cannot reach zero staleness.

---
*Part of the [DBMS Research catalog](../../README.md).*
