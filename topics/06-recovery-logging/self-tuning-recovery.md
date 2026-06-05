# Self-tuning recovery parameters

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/self-tuning-recovery` · **Status:** empirically-open

## 1. Problem Statement
Recovery time after a crash depends on parameters the DBA traditionally fixes: checkpoint interval/frequency, dirty-page-flush aggressiveness, log buffer and segment sizes, group-commit batch/timeout, and the recovery parallelism degree. Under shifting workload (changing write rate, working-set size, skew), a static setting either wastes throughput (over-checkpointing) or blows the recovery-time budget (under-checkpointing). The problem is to **autonomously and continuously control** these knobs so the system meets a **recovery-time SLA** (e.g., "redo + undo recovery $\le T_{\text{SLO}}$ with probability $\ge 1-\delta$") while maximizing steady-state throughput.

**Variants.** *Decision:* given current state and a controller, will the SLA hold over horizon $H$? *Optimization:* maximize throughput subject to predicted recovery time $\le T_{\text{SLO}}$. *Online/regret:* minimize regret against the best fixed (or best dynamic) parameter setting under an adversarial or stochastic workload sequence. Because optimal control of a real engine's coupled subsystems lacks a closed-form solution and is pursued via heuristics, control theory, and learning, the problem is **empirically-open**.

## 2. Mathematical Foundations
Recovery cost after a crash is dominated by the redo work since the last consistent checkpoint plus undo of in-flight transactions. In ARIES, redo replays from the oldest dirty-page `recLSN`; the recovery time is approximately
$$T_{\text{rec}} \approx \frac{\text{bytes of redo log since checkpoint}}{\text{replay throughput}} + T_{\text{undo}}(\text{active txns}).$$
Let dirty-page generation rate be $d(t)$ (pages/s) and flush rate $\phi$. Checkpointing at interval $I$ bounds redo work by $\approx d \cdot I$ pages, so $T_{\text{rec}} \le g(d\cdot I)$. The control objective: choose $I(t), \phi(t), \dots$ minimizing checkpoint/flush overhead $C(\phi)$ subject to $g(d(t)\cdot I(t)) + T_{\text{undo}} \le T_{\text{SLO}}$.

This is a constrained stochastic optimal-control / MDP problem: state = (buffer dirtiness, log position, workload features), action = parameter vector, reward = throughput, hard constraint = predicted recovery time. Online-learning framing yields **bandit/contextual-bandit** or **RL** formulations; regret bounds (e.g., $O(\sqrt{T})$ for online convex optimization on the throughput–overhead surface) apply when the cost is convex in the knob. Queueing/Little's-law relations connect flush rate to in-flight durability lag, coupling this problem to bounded-staleness durability.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Production engines implement *adaptive/fuzzy checkpointing*: InnoDB's adaptive flushing drives dirty-page flushing from redo-log fill level and a target; PostgreSQL spreads checkpoints (`checkpoint_completion_target`) and has background-writer heuristics; SQL Server's *indirect checkpoints* expose `TARGET_RECOVERY_TIME` as a near-direct SLA knob — the closest deployed instance of self-tuning recovery. ML-based DBMS auto-tuners — *OtterTune* (Van Aken et al., SIGMOD 2017), *CDBTune* (RL, SIGMOD 2019), *QTune* — tune broad knob sets including some recovery/log parameters but optimize aggregate latency/throughput rather than a recovery-time constraint specifically. *Peloton/self-driving DBMS* (Pavlo et al., CIDR 2017) articulated forecasting-driven autonomous control including reorganization and provisioning.

**Theory-SOTA.** Control-theoretic feedback (PID/MPC) for flush rate and online-learning regret analyses exist in adjacent caching/admission-control settings; recovery-SLA-constrained control lacks a tight unified theory.

## 4. Upper Bound
A model-predictive controller using a workload forecast $\hat d(t)$ can keep predicted $T_{\text{rec}}$ within the SLO whenever the forecast error is bounded; if $C(\phi)$ is convex, online gradient methods achieve $O(\sqrt{T})$ regret versus the best fixed knob, and $O(\sqrt{T \cdot P_T})$ dynamic regret with path-length $P_T$ of the optimal trajectory. SQL Server's `TARGET_RECOVERY_TIME` demonstrates an *achievable* feedback loop that flushes enough to bound redo to the target. These are best-known guarantees under convexity/forecastability assumptions, not unconditional.

## 5. Lower Bound
No controller can guarantee the SLA under fully adversarial, unforecastable load spikes: an adversary can raise the dirty-generation rate $d$ faster than any bounded flush rate $\phi_{\max}$ can absorb, forcing either throughput collapse or SLA violation — an information-theoretic/competitive impossibility analogous to online-paging lower bounds (no online algorithm beats a $k$-competitive ratio without lookahead). Formally, against an oblivious adversary, any online tuner has competitive ratio bounded below by the ratio of peak to sustainable write rate. The hardness is *competitive/online*, plus the underlying joint-knob optimization being non-convex in general.

## 6. The Gap
The gap is between (a) heuristic/learned controllers that *empirically* hold SLAs on observed workloads and (b) controllers with *provable* SLA-satisfaction guarantees under characterized workload classes. It is open whether, for realistic bounded-burst workloads, a tuner with worst-case SLA guarantees and near-optimal throughput exists. Closing it needs a faithful, identifiable recovery-cost model plus a controller with matching regret/competitive guarantees — currently absent end-to-end in any production engine.

## 7. Current Research (as of June 2026)
Active: RL- and Bayesian-optimization-based DBMS tuners increasingly incorporate recovery/availability objectives; cloud providers expose RTO/RPO targets and tune replication+checkpoint behind them. Learned forecasting of workload drift feeding MPC controllers for flushing is an active line *(frontier — verify)*. Self-driving-DBMS research (CMU — Andy Pavlo's group), learned-systems efforts, and OtterTune's commercial lineage continue. LLM-driven knob recommendation is emerging but unvalidated for hard recovery constraints *(frontier — verify)*.

## 8. Future Work
(i) Recovery-time as an explicit, verifiable constraint in autotuners (not just an aggregate-metric term). (ii) Provable SLA guarantees under bounded-burst workload models. (iii) Co-tuning durability lag and recovery time jointly. (iv) Safe exploration that never violates the SLA during learning. (v) Transfer/meta-learning so a tuner adapts across engines and hardware.

## 9. Key References
- **[Foundational]** Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992.
- **[SOTA]** Van Aken, D., Pavlo, A., Gordon, G., Zhang, B. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017.
- **[SOTA]** Zhang, J. et al. *An End-to-End Automatic Cloud Database Tuning System Using Deep Reinforcement Learning (CDBTune).* SIGMOD, 2019.
- **[SOTA]** Pavlo, A. et al. *Self-Driving Database Management Systems.* CIDR, 2017.
- **[Survey]** Chaudhuri, S., Narasayya, V. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
