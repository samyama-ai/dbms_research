---
id: 18-streaming-queries/backpressure-slo-preserving
title: "Backpressure that preserves end-to-end SLOs"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Backpressure that preserves end-to-end SLOs

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/backpressure-slo-preserving` · **Status:** open

## 1. Problem Statement
In a dataflow DAG of streaming operators with heterogeneous service rates, a slow downstream operator must throttle upstream producers to avoid unbounded queue growth — this is **backpressure**. The problem: design a flow-control mechanism that, while preventing buffer overflow, also **preserves end-to-end SLOs** — a tail-latency target $L_{p99}$ and/or a throughput floor $\Theta_{min}$ — across an operator graph where operators differ in cost, selectivity, and parallelism, and where bottlenecks shift over time.

The subtlety: naive backpressure (block upstream when a downstream buffer fills) is *correct* (no loss, no overflow) but **SLO-oblivious** — it can propagate a single slow operator into a global stall, inflate latency for unrelated paths sharing a source, cause oscillation, and interact badly with checkpointing. Decision variant: given per-operator service-rate distributions and an SLO, does a credit/rate allocation exist that meets the SLO without overflow? Optimization variant: maximize admitted throughput (or minimize tail latency) subject to bounded buffers and the SLO. Status open: production backpressure is robust for *stability* but offers no SLO guarantees.

## 2. Mathematical Foundations
Model the DAG as a **queueing network**; under Poisson-ish arrivals each operator is an $M/G/1$ (or $G/G/1$) station, and end-to-end latency is the sum along a path of per-station sojourn times. For a tandem of stations with utilizations $\rho_i$, latency blows up as $\sum_i \frac{\rho_i}{1-\rho_i}\cdot\frac{1}{\mu_i}$, so the SLO defines a feasible-utilization region. Backpressure is a **distributed flow-control / congestion-control** problem: credit-based flow control (à la network switches) caps in-flight data; the stability question maps to **Lyapunov drift** analysis of the **backpressure (Tassiulas–Ephremides) routing/scheduling** algorithm, which is throughput-optimal for queue stability but **does not** by itself bound delay.

The tension is precisely **throughput-optimal vs. delay-optimal**: max-weight/backpressure scheduling stabilizes any admissible load yet can incur poor (even growing) delay. SLO-aware control must add **deadline/latency** terms, turning it into a constrained network-utility-maximization (NUM) problem $\max \sum U(\text{rate})$ s.t. stability and $L_{p99}\le L$. Heterogeneous operator graphs add the **bottleneck-shifting** and **fan-in/fan-out fairness** dimensions.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Tassiulas–Ephremides backpressure (throughput-optimal) and the delay-aware variants (e.g. backpressure with delay/Lyapunov drift-plus-penalty); NUM-based congestion control.
- **Systems-SOTA:** **Apache Flink** — credit-based flow control over network buffers (per-channel credits) replacing TCP-level backpressure (since 1.5). **Spark Structured Streaming** — micro-batch rate limiting / backpressure on receiver. **Heron** — explicit backpressure protocol with spout throttling; **Dhalion** layers SLO-driven scaling on top. Faust/Kafka-Streams rely on consumer-lag-driven flow control. None give end-to-end tail-latency guarantees.

## 4. Upper Bound
Credit-based flow control bounds in-flight bytes per channel to a constant, guaranteeing **no overflow with $O(1)$ buffering per edge** and zero loss (the stability/correctness guarantee Flink provides). Backpressure scheduling is **throughput-optimal** (stabilizes any load strictly inside the capacity region) by Lyapunov drift. Drift-plus-penalty variants achieve an **$[O(1/V),\,O(V)]$ utility-vs-delay tradeoff**: arbitrarily close to optimal admitted throughput at the cost of $O(V)$ queue/delay — a tunable but not free SLO knob.

## 5. Lower Bound
There is a fundamental **throughput–delay tradeoff**: no scheduling/flow-control policy can be simultaneously throughput-optimal and minimize worst-case delay; the drift-plus-penalty $O(V)$/$O(1/V)$ curve is order-optimal for the class. Distributed flow control faces **information-delay** lower bounds — control signals traverse the same graph they regulate, so a feedback loop of diameter $d$ cannot react faster than $\Omega(d)$ hops, bounding how tightly any decentralized scheme can hold an SLO under sudden bottleneck shifts (a control-theoretic / communication-delay impossibility). Meeting hard per-path deadlines while keeping all queues stable is, in the worst case, infeasible (the feasible region can be empty).

## 6. The Gap
Stability and throughput-optimality are **solved**; the open gap is **SLO-preserving** control: no deployed mechanism provably maintains a tail-latency SLO across a heterogeneous DAG while keeping buffers bounded and avoiding oscillation. The theory (drift-plus-penalty) bounds *average* delay, not p99 tails, and assumes models real engines violate (bursty, correlated, out-of-order arrivals). Closing it needs (a) tail-latency-aware distributed flow control with provable p99 bounds, (b) co-design with elastic scaling (backpressure that triggers rescaling instead of stalling), and (c) fairness across shared source paths.

## 7. Current Research (as of June 2026)
Active: coupling backpressure with auto-scaling so sustained pressure elastically adds parallelism rather than stalling (Flink reactive mode + DS2-style controllers) *(frontier — verify)*; learning-based / control-theoretic (PID, MPC) rate controllers for streaming SLOs *(frontier — verify)*; SLO-aware admission and prioritized flow control for multi-tenant streaming clouds. Groups: KTH/Edinburgh (Kalavri), TU Berlin DIMA, Microsoft/Google streaming-infra teams, and the Flink/Heron communities.

## 8. Future Work
- Distributed flow control with provable tail-latency (p99) guarantees on heterogeneous DAGs.
- Unified backpressure-plus-elasticity: pressure as a scaling signal, not just a throttle.
- Fairness guarantees across queries/paths sharing a congested source.
- Models robust to bursty, correlated, out-of-order arrivals (beyond Poisson).

## 9. Key References
- **[Foundational]** L. Tassiulas, A. Ephremides. *Stability Properties of Constrained Queueing Systems and Scheduling Policies for Maximum Throughput (Backpressure).* IEEE TAC, 1992. — [DOI](https://doi.org/10.1109/9.182479)
- **[Foundational]** M. J. Neely. *Stochastic Network Optimization with Application to Communication and Queueing Systems (Drift-plus-Penalty).* Morgan & Claypool, 2010. — [DOI](https://doi.org/10.2200/S00271ED1V01Y201006CNT007)
- **[SOTA]** P. Carbone, A. Katsifodimos, S. Ewen, V. Markl, S. Haridi, K. Tzoumas. *Apache Flink: Stream and Batch Processing in a Single Engine.* IEEE Data Eng. Bulletin, 2015. — [PDF](https://asterios.katsifodimos.com/assets/publications/flink-deb.pdf) · [DBLP](https://dblp.org/rec/journals/debu/CarboneKEMHT15.html)
- **[SOTA]** S. Kulkarni, N. Bhagat, M. Fu, et al. *Twitter Heron: Stream Processing at Scale.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2742788)
- **[SOTA]** A. Floratou, A. Agrawal, B. Graham, S. Rao, K. Ramasamy. *Dhalion: Self-Regulating Stream Processing in Heron.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137786)

## 10. Worked Example

Consider a 2-stage tandem $S \to A \to B$, each an $M/M/1$ station. Source rate $\lambda = 90$ tuples/s. Operator $A$ serves at $\mu_A = 100$/s, operator $B$ at $\mu_B = 95$/s. Utilizations: $\rho_A = 0.90$, $\rho_B = 0.947$. Mean sojourn time per station is $W_i = \frac{1}{\mu_i - \lambda}$, so

$$W_A = \frac{1}{100-90} = 0.100\text{ s}, \qquad W_B = \frac{1}{95-90} = 0.200\text{ s}.$$

End-to-end mean latency $= W_A + W_B = 0.300$ s. The tail is dominated by the near-saturated stage $B$ (the bottleneck). Suppose the SLO is $L_{p99} = 0.5$ s. For an $M/M/1$ queue the response time is exponential, so $L_{p99} = W \cdot \ln(100) \approx 4.6\,W$; stage $B$ alone gives $0.2 \times 4.6 = 0.92$ s — already violating the SLO.

Now apply naive backpressure: when $B$'s buffer fills, it blocks $A$, which blocks the source. This caps queues (no overflow) but does nothing for latency. The fix is admission/rate control: throttle $\lambda$ to $80$/s. Then $W_B = \frac{1}{95-80} = 0.067$ s and $L_{p99,B} \approx 0.31$ s — SLO met, at the cost of shedding $\approx 11\%$ of load. This illustrates the throughput–delay tension: stability is free, but the $p99$ target forces a $\rho_B$ below capacity, the knob that drift-plus-penalty parameterizes as $O(1/V)$ utility loss vs. $O(V)$ queue/delay.

---
*Part of the [DBMS Research catalog](../../README.md).*
