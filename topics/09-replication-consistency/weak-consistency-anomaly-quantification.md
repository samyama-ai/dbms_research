# Quantifying observable anomalies under weak consistency

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/weak-consistency-anomaly-quantification` · **Status:** empirically-open

## 1. Problem Statement
Weak/eventual consistency trades correctness for availability and latency, but the cost is **anomalies**: stale reads, lost updates, non-monotonic reads, fractured (non-read-atomic) transactions, causality violations. The classical theory tells us *which* anomalies are **possible**; it says little about *how often* and *how badly* they are actually **observed** by users on a given workload and deployment. The problem is to **measure and predict** the **rate** (frequency) and **severity** (user-perceived impact, value error) of consistency anomalies in production-like settings.

Variants:
- **Measurement (empirical):** instrument or sample a running system and estimate anomaly rate/severity with statistical guarantees.
- **Prediction (analytic/probabilistic):** given replication lag distributions, workload (read/write mix, key skew, session structure), and protocol, predict the anomaly rate *a priori*.
- **Verification (decision):** does a recorded history actually contain a violation of a target model (checking), and how many — a counting variant.

## 2. Mathematical Foundations
A history is a set of operations with real-time and session orders; an **anomaly** is a violation of a consistency axiom on the *visibility*/arbitration relations (Burckhardt's framework). Checking a history against, e.g., serializability or causal consistency reduces to **acyclicity of a dependency graph** (Adya's *Direct Serialization Graphs*, 1999). The state-of-art checker **Elle** (Kingsbury & Alvisi, VLDB 2020) recovers dependency edges from "list-append" datatypes and detects the Adya G0/G1/G2 anomalies; checking general serializability is **NP-complete** (Papadimitriou 1979), but Elle exploits structure to scale.

For *prediction*, the seminal model is **Probabilistically Bounded Staleness (PBS)** (Bailis, Venkataraman, Franklin, Hellerstein, Stoica, VLDB 2012): for Dynamo-style quorums with $N$ replicas, read quorum $R$, write quorum $W$, it computes $P(\text{stale read})$ as a function of read-after-write delay $t$ and the message-latency distribution via a "WARS" model (write/ack/read/response latencies), giving $t$-visibility and $k$-staleness curves
$$P_{\text{consistent}}(t) = 1 - P\big(\text{fewer than } W{+}R{-}N \text{ acked replicas overlap within } t\big).$$
Severity needs a **metric on value error** — $k$-atomicity (bounded staleness in versions), $\Delta$-atomicity (time-bounded staleness, Golab et al., PODC 2011), or application-defined cost functions; this connects to the information-theoretic question of *how much* observed state diverges.

## 3. State of the Art (SOTA)
- **Measurement-SOTA:** **Elle** + **Jepsen** (Kingsbury) are the de-facto tools for finding anomalies in real databases; **Gretchen**, **dbcop** (Biswas & Enea, OOPSLA 2019) decide weak-consistency models on histories. **$\Delta$/k-atomicity meters** (Golab, Li, Shah, Wylie et al.) measure online staleness.
- **Prediction-SOTA:** **PBS** (VLDB 2012) remains the canonical analytic staleness predictor; refinements model contention and read-repair. Simulation frameworks and trace-driven estimators extend it but lack tight error bounds on *observed* (not just possible) anomalies.

## 4. Upper Bound
For *measurement*: anomaly *checking* of bounded-width / list-append histories is **polynomial** via Elle's recovered dependency graph; sampling-based estimators give the anomaly rate within $\epsilon$ with $O(\epsilon^{-2}\log\delta^{-1})$ samples (Hoeffding). For *prediction*: PBS computes staleness probabilities in **closed form / fast Monte-Carlo** given latency distributions; under quorum overlap $W+R>N$ anomaly probability is exactly bounded by the tail of the latency convolution. These are the best-known *constructive* upper bounds on cost-to-measure/predict.

## 5. Lower Bound
- **Checking hardness:** deciding **serializability** of a general history is **NP-complete** (Papadimitriou, JACM 1979); deciding **causal consistency** and several weak models is also **NP-hard** in general (Bouajjani, Enea et al.) — so exact, model-general anomaly counting is intractable without structural assumptions.
- **Information-theoretic / impossibility:** you cannot *observe* anomalies you don't probe for — a sampling lower bound (need $\Omega(\epsilon^{-2})$ samples for additive-$\epsilon$ rate). Predicting exact observed rates is fundamentally limited by uncertainty in latency/workload distributions; PBS itself is *probabilistic*, not worst-case, reflecting that tight a-priori prediction is information-limited.

## 6. The Gap
This is **empirically open**, not theoretically closed. We can (a) *detect* anomalies post-hoc (Elle) and (b) *predict staleness probability* for quorum stores (PBS), but there is **no validated, general model** linking workload + deployment to the **user-observed** anomaly rate *and severity* across modern protocols (causal, TCC, leaderless, edge). Severity metrics are ad hoc; correlated failures and real skew are under-modeled; and there is no standard benchmark that reports observed-anomaly rates the way TPC reports throughput. Closing it requires standardized severity metrics, validated predictive models, and large-scale production measurement.

## 7. Current Research (as of June 2026)
- Online, low-overhead **consistency oracles/meters** running in production to sample observed anomalies *(frontier — verify)*.
- Extending Elle/dbcop to causal+/TCC and to richer datatypes; ML-based anomaly-rate prediction from telemetry *(frontier — verify)*.
- Application-aware **severity** models (dollar/UX cost of a stale read) and SLA formulations over anomaly rate.
- Workload-driven what-if tools predicting anomaly rate under proposed consistency-level changes.

## 8. Future Work
- A unified, validated predictor of observed anomaly rate **and** severity for arbitrary protocols.
- Standard severity metrics and an anomaly-rate benchmark suite.
- Scalable exact/approximate checkers for causal and transactional weak models under correlated failures.

## 9. Key References
- **[Foundational]** Bailis, Venkataraman, Franklin, Hellerstein, Stoica. *Probabilistically Bounded Staleness for Practical Partial Quorums.* VLDB, 2012.
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979.
- **[Foundational]** Adya. *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions.* PhD thesis, MIT, 1999.
- **[SOTA]** Kingsbury, Alvisi. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020.
- **[SOTA]** Golab, Li, Shah. *Analyzing Consistency Properties for Fun and Profit* (Δ/k-atomicity). PODC, 2011.
- **[SOTA]** Biswas, Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
