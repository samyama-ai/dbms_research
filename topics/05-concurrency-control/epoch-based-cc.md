# Epoch-Based Concurrency Control Tradeoffs

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/epoch-based-cc` · **Status:** empirically-open

## 1. Problem Statement

**Epoch-based concurrency control** divides time into coarse intervals (*epochs*) and amortizes expensive coordination — global timestamp allocation, durability fsyncs, memory reclamation, distributed commit agreement — across all transactions in an epoch rather than per transaction. Transactions execute optimistically within an epoch; serialization order *between* epochs is fixed by epoch boundaries, while order *within* an epoch is resolved by local validation.

The core research problem is to **quantify and characterize the latency–throughput tradeoff** induced by epoch length $E$ and to determine optimal or near-optimal epoch policies under a workload. Long epochs amortize coordination cost (raising throughput) but delay commit acknowledgment until the epoch closes (raising tail latency and group-commit delay). Variants:
- **Optimization:** choose epoch length / boundary policy minimizing tail latency subject to a throughput floor (or vice versa).
- **Adaptive control:** online adjustment of $E$ under shifting load.
- **Correctness:** prove that epoch boundaries yield a recoverable, serializable commit order without per-transaction global synchronization.

This is marked **empirically-open** because no closed-form optimal policy is known; the frontier is measurement-driven.

## 2. Mathematical Foundations

Let transactions arrive at rate $\lambda$, each requiring local work $s$ and incurring amortizable coordination cost $C$ per epoch. With epoch length $E$ (time) and batch size $B \approx \lambda E$, the per-transaction coordination cost is $C/B$, decreasing in $E$, while the **expected commit latency** for a uniformly-arriving transaction is approximately
$$
\mathbb{E}[L] \approx s + \tfrac{E}{2} + d,
$$
where $d$ is the epoch-closing/durability delay. Throughput is bounded by
$$
X(E) = \frac{B}{E + C} \quad\text{(coordination-bound regime)},
$$
so $X \to 1/(\text{per-txn work})$ as $E$ grows but with $\mathbb{E}[L]$ growing linearly in $E$ — a fundamental **Pareto frontier** between $X$ and $L$. The tradeoff is governed by an M/G/1-style batch-service queue; tail latency follows from the batch waiting-time distribution. Serializability rests on the **epoch as a global commit barrier**: if epoch $k$ fully precedes epoch $k{+}1$ in the serialization order, intra-epoch order need only be acyclic locally (as in Silo's read-validation), giving a two-level serialization argument.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **Silo** (Tu, Zheng, Kohler, Liskov, Madden, SOSP 2013) introduced epoch-based group commit and epoch-bounded memory reclamation: a global epoch advances ~every 40 ms, decoupling the serialization point from per-transaction timestamp contention, enabling 700K+ TPS on multicore. **Cicada** (SIGMOD 2017) and **TicToc** (Yu, Pavlo, Sanchez, Devadas, SIGMOD 2016 — data-driven timestamps) refine the idea by avoiding a centralized timestamp entirely. In the distributed setting, **epoch-based deterministic/2PC-avoiding designs** and **Eris/Aria** (Lu, Yu, Madden, OSDI/VLDB 2020 — Aria is deterministic, batch/epoch executed) push epoching across nodes. RCU/EBR memory reclamation (McKenney) is the systems-theory ancestor.

**Theory-SOTA.** Treatments are largely queueing-theoretic and empirical; no canonical closed-form optimal epoch-length theorem exists.

## 4. Upper Bound

The achievable throughput upper bound in the coordination-amortized regime is $X(E) \to X_{\max} = 1 / w_{\text{txn}}$ (intrinsic per-transaction work), approached as $E \to \infty$; Silo-class systems demonstrate near-linear multicore scaling up to memory-bandwidth limits. For latency, group-commit theory gives an upper bound on mean added delay of $E/2 + d$ under uniform arrivals (M/G/1 batch model). These bounds hold in the **shared-memory multicore** and **batched-distributed** models respectively; they are descriptive, not proven optimal across all policies.

## 5. Lower Bound

There is a hard **latency floor**: any epoch scheme that defers durability/commit to epoch close cannot acknowledge faster than the durability latency $d$ plus expected residual epoch wait, so $\mathbb{E}[L] \ge d$ unconditionally and $\ge d + \Theta(1/\lambda)$ when at least one round-trip of batching is required. In the **distributed** setting, the **FLP impossibility** and **CAP** results bound coordinated commit: no asynchronous protocol guarantees agreement with a faulty participant, so epoch barriers cannot eliminate the coordination round-trip lower bound $\Omega(\text{one network delay})$. No SETH/3SUM-style fine-grained lower bound is known for the epoch-length optimization itself, leaving the precise Pareto-optimality gap open.

## 6. The Gap

The gap is **empirical, not complexity-theoretic**: we lack (1) a validated analytical model predicting the throughput/tail-latency Pareto frontier as a function of $E$ across realistic skewed, bursty workloads, and (2) provable guarantees for adaptive epoch controllers (no regret bound vs. clairvoyant optimum is established). The qualitative tradeoff is understood; the *quantitative, workload-conditioned optimal policy* and its robustness to bursts remain open. Closing it requires either a tight queueing/control-theoretic characterization or a learned controller with proven competitive ratio.

## 7. Current Research (as of June 2026)

Directions: (i) **adaptive epoch sizing** reacting to load/tail-latency SLOs, including RL/control-theoretic tuners *(frontier — verify)*; (ii) **deterministic batch execution** (Aria/Calvin lineage; Abadi, Thomson) where epochs double as deterministic scheduling units; (iii) epoch-based reclamation generalized to NVM/RDMA and disaggregated memory; (iv) hardware-clock-assisted epochs reducing $d$. Active groups: MIT (Madden, Kaashoek/Morris OS lineage), CMU-DB (Pavlo), MIT-CSAIL/Harvard (Kohler), and deterministic-DB researchers (Yale/UMD — Abadi, Thomson). Tail-latency-aware commit batching is an open systems frontier in HTAP and serverless OLTP.

## 8. Future Work

- A predictive analytical model mapping $(E, \lambda, \text{skew})$ to the throughput/tail-latency Pareto curve, validated on standard benchmarks (TPC-C, YCSB, TATP).
- Online epoch controllers with provable regret/competitive bounds under bursty arrivals.
- Cross-layer co-design of epoch length with durability media (NVM, fast NVMe, RDMA log shipping) to shrink $d$.
- Formal recoverability/serializability proofs for nested or hierarchical epoch schemes spanning replicas.

## 9. Key References

- **[SOTA]** S. Tu, W. Zheng, E. Kohler, B. Liskov, S. Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** X. Yu, A. Pavlo, D. Sanchez, S. Devadas. *TicToc: Time Traveling Optimistic Concurrency Control.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2882935)
- **[SOTA]** Y. Lu, X. Yu, L. Cao, S. Madden. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[SOTA]** H. Lim, M. Kaminsky, D. G. Andersen. *Cicada: Dependably Fast Multi-Core In-Memory Transactions.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064015)
- **[Foundational]** M. J. Fischer, N. A. Lynch, M. S. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* Journal of the ACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** P. A. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/db/books/dbtext/bernstein87.html)

## 10. Worked Example

Take arrival rate $\lambda = 50{,}000$ txn/s, per-epoch coordination cost (one group fsync) $C = 1$ ms, and durability delay $d = 1$ ms. Compare two epoch lengths.

**Short epoch, $E = 1$ ms:** batch $B = \lambda E = 50$ txn. Throughput $X = B/(E+C) = 50/(2\text{ ms}) = 25{,}000$ txn/s — coordination eats half the time. Mean commit latency $\mathbb{E}[L] \approx s + E/2 + d = s + 0.5 + 1 = s + 1.5$ ms.

**Long epoch, $E = 40$ ms (Silo-style):** $B = 2000$ txn, $X = 2000/(41\text{ ms}) \approx 48{,}800$ txn/s — within $2.5\%$ of the work-bound ceiling $1/w_{\text{txn}}$. But latency balloons to $\mathbb{E}[L] \approx s + 20 + 1 = s + 21$ ms.

So a $40\times$ longer epoch buys nearly $2\times$ throughput while inflating mean latency $\sim 14\times$. This traces the $X$-vs-$L$ Pareto frontier: throughput saturates as $E$ grows ($25{,}000 \to 48{,}800$) while $\mathbb{E}[L]$ rises linearly in $E$, and never drops below the floor $d = 1$ ms.

---
*Part of the [DBMS Research catalog](../../README.md).*
