# Adaptive Failure Detector Accuracy

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/adaptive-failure-detectors` · **Status:** empirically-open

## 1. Problem Statement
A **failure detector** is an oracle that each process queries to suspect crashed peers; it is the modular liveness ingredient that lets consensus circumvent FLP (the weakest such oracle is $\Diamond W$ / $\Omega$). In real deployments, network delays drift (load spikes, congestion, geo-variability), so a detector tuned for one regime either falsely suspects live nodes (hurting availability and triggering needless leader changes) or detects real crashes too slowly (hurting liveness/recovery time).

The problem: *design a failure detector that provably tracks changing network conditions, bounding simultaneously the **false-positive (mistake) rate** and the **detection latency**, and characterize the achievable trade-off frontier.* The status is **empirically-open**: adaptive detectors (φ-accrual, Chen–Toueg–Aguilera estimators) work well in practice and there is a clean QoS theory for *stationary* delay distributions, but *provable* guarantees under *non-stationary / adversarial* network drift remain unestablished. Variants: **decision** — can a target (mistake-rate, latency) pair be met for a given delay process? **optimization** — minimize detection latency subject to a mistake-rate ceiling (or vice versa).

## 2. Mathematical Foundations
Chandra–Toueg (1996) classify detectors by **completeness** (every crash eventually suspected) and **accuracy** (live processes not wrongly suspected), yielding classes $P, \Diamond P, S, \Diamond S, \Omega, \dots$; $\Omega$ (eventual leader) is the weakest detector sufficient for consensus (Chandra–Hadzilacos–Toueg). The **QoS** framework (Chen, Toueg, Aguilera, 2002) quantifies a detector by: detection time $T_D$, mistake recurrence time $T_{MR}$, and mistake duration $T_M$. Given a probabilistic message-delay model (e.g. heartbeat period $\eta$, delay distribution with mean and variance), one computes the freshness-point / timeout to meet target QoS. **φ-accrual** (Hayashibara et al., 2004) outputs a continuous suspicion level $\varphi(t) = -\log_{10} P(\text{no heartbeat by } t \mid \text{history})$, decoupling detection from a binary timeout. Non-stationarity breaks the i.i.d. assumption underlying the QoS closed forms; the open theory needs online estimators with regret-style bounds against a drifting delay process $D_t$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Chandra–Toueg failure-detector hierarchy and the $\Omega$-weakest-detector result; Chen–Toueg–Aguilera QoS analysis giving optimal timeout configuration for *stationary* stochastic delays.
- **Systems-SOTA:** φ-accrual failure detector (Hayashibara et al., 2004) — used in Akka, Apache Cassandra (gossip), and many production clusters; adapts the suspicion threshold to a sliding window of inter-arrival times. SWIM (DSN 2002) and Lifeguard provide scalable, low-false-positive membership/failure detection with infection-style dissemination and local-health-aware timeouts; used in HashiCorp Serf/Consul. These are empirically strong but lack drift-robust proofs.

## 4. Upper Bound
Best-known *provable* result is for **stationary** delays: given a delay distribution, the QoS theory (Chen et al. 2002) configures heartbeat period and timeout to *optimally* trade detection time $T_D$ against mistake recurrence $T_{MR}$ — a Pareto-optimal point on the stationary frontier. φ-accrual and SWIM-Lifeguard give strong *empirical* upper bounds on false positives under moderate drift by adapting thresholds online, but without formal regret guarantees. These hold in a **probabilistic partial-synchrony / stochastic-delay** model.

## 5. Lower Bound
A fundamental impossibility floor: in pure asynchrony no detector can be *both* complete and accurate (this is precisely why FLP holds); any always-correct (perfect $P$) detector requires synchrony bounds. Information-theoretically, distinguishing "slow but alive" from "crashed" within time $t$ is impossible when the delay distribution's tail beyond $t$ has non-negligible mass — so for any finite detection latency there is an irreducible mistake probability tied to the delay-tail. Under *adversarial* (non-stationary) delays, no online estimator can guarantee simultaneously bounded false positives and bounded latency without an assumption limiting how fast conditions change — a no-free-lunch barrier analogous to online-learning lower bounds.

## 6. The Gap
**Empirically-open.** For stationary delays the trade-off is essentially solved (QoS theory). The gap is the absence of *provable* guarantees under realistic **non-stationary / adversarial** delay drift: practitioners rely on φ-accrual and SWIM-Lifeguard heuristics that demonstrably work but carry no theorem bounding both mistake rate and detection latency as conditions change. Closing it requires (i) a formal drift model (bounded-variation or comparator-class delay processes) and (ii) an online detector with regret-style guarantees against the best fixed-in-hindsight timeout, matching the stochastic-delay lower bound.

## 7. Current Research (as of June 2026)
Directions: learning-augmented / predictor-based timeouts; bandit and online-learning formulations of adaptive timeout selection with regret bounds; tail-aware detectors for cloud and geo networks with heavy-tailed RTTs; integration with leader-election stability (avoiding leader thrashing in Raft/HotStuff). Groups continue from the Toueg/Aguilera and SWIM (Cornell) lineages, plus systems teams at HashiCorp, Datadog, and cloud providers. *(frontier — verify)* Recent learning-augmented failure-detection proposals claim regret bounds under bounded-drift delays, but rigorous matching lower bounds and adversarial guarantees are not yet settled.

## 8. Future Work
- A formal non-stationary delay model with an online detector achieving regret-bounded (mistake-rate, latency) guarantees.
- Tight lower bounds tying delay-distribution drift to unavoidable mistake/latency trade-offs.
- Co-design of failure detection with leader-election stability to suppress unnecessary view changes.
- Heavy-tailed and correlated-failure–aware detectors for large geo-distributed clusters.

## 9. Key References
- **[Foundational]** Tushar Deepak Chandra, Sam Toueg. *Unreliable Failure Detectors for Reliable Distributed Systems.* JACM, 1996.
- **[Foundational]** Tushar Chandra, Vassos Hadzilacos, Sam Toueg. *The Weakest Failure Detector for Solving Consensus.* JACM, 1996.
- **[SOTA]** Wei Chen, Sam Toueg, Marcos K. Aguilera. *On the Quality of Service of Failure Detectors.* IEEE TC, 2002.
- **[SOTA]** Naohiro Hayashibara, Xavier Défago, Rami Yared, Takuya Katayama. *The φ Accrual Failure Detector.* SRDS, 2004.
- **[SOTA]** Abhinandan Das, Indranil Gupta, Ashish Motivala. *SWIM: Scalable Weakly-consistent Infection-style Process Group Membership Protocol.* DSN, 2002.

---
*Part of the [DBMS Research catalog](../../README.md).*
