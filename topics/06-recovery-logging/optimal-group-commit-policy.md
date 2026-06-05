# Optimal group-commit policy

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/optimal-group-commit-policy` · **Status:** empirically-open

## 1. Problem Statement
Group commit amortizes the fixed cost of a durable log flush (an `fsync`, an NVMe write barrier, or an `fdatasync` to a replicated quorum) across many concurrently committing transactions. The policy decides *when* to release a batch: after a fixed timer $T$, after a batch size $K$, or via some adaptive rule conditioned on observed load. The central question is to derive a **latency-throughput-optimal adaptive batching policy under unknown and possibly non-stationary transaction arrival distributions**.

Variants:
- **Optimization (online):** minimize a chosen objective — e.g., mean commit latency subject to a throughput floor, or a weighted sum $\alpha\,\mathbb{E}[\text{latency}] + \beta\,(\text{flush rate})$ — with arrival statistics revealed only as transactions arrive.
- **Decision:** given a latency SLO (p99 $\le L$) and a device flush-cost model, does a feasible policy exist, and is a given policy feasible?
- **Competitive (adversarial):** bound the ratio between an online policy's cost and the optimal offline policy that knows the full arrival sequence.

## 2. Mathematical Foundations
Model commits as an arrival process $\{A_i\}$ with rate $\lambda$; a flush incurs fixed cost $c$ (latency) and serializes the device. This is an instance of **dynamic batching / control of a bulk-service queue** (the $M/G^{[K]}/1$ and $M^X/M/1$ batch-service models). The waiting transaction set grows until a *release rule* fires.

Key tension: the *acquisition delay* (how long the first transaction in a batch waits) trades against *amortization* (transactions per flush). For Poisson arrivals at rate $\lambda$ with flush cost $c$, the classic timer-vs-size analysis gives an expected per-transaction overhead minimized near a batch interval scaling as $\sqrt{c/\lambda}$ — echoing the **EOQ / $\sqrt{}$-rule** of inventory control. Under heavy traffic the problem maps to **Brownian control / drift-diffusion** approximations, where the optimal policy is a state-dependent threshold.

For the unknown-distribution case the natural frame is **online learning / regret minimization**: treat the timer as an action and bound regret against the best fixed policy in hindsight, or use a **competitive-ratio** ("ski-rental"-style) argument — waiting for more arrivals vs. flushing now is structurally the rent-or-buy dilemma, giving the canonical $e/(e-1)$ randomized and $2$ deterministic bounds for the two-action abstraction.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Adaptive group commit ships in essentially every serious engine. PostgreSQL exposes `commit_delay`/`commit_siblings`; MySQL/InnoDB uses binlog group commit with a leader-follower flush pipeline; Aurora and Socrates batch redo to a quorum'd log service. The **"early lock release / flush pipelining"** line (Johnson, Pandis, Stoica, Ailamaki, *Aether*, VLDB 2010) decouples commit from log I/O and is the practical reference design.
- **Theory-SOTA:** Bulk-service queue optimal-threshold results (Deb & Serfozo, 1973) and Brownian batch-control are the cleanest closed-form characterizations, but only under known/stationary statistics. There is no accepted optimal *adaptive* policy under unknown non-stationary load — hence *empirically-open*.

## 4. Upper Bound
For known Poisson arrivals, a static-threshold policy achieving the bulk-service optimum is computable; per-transaction amortized flush overhead is $\Theta(\sqrt{c/\lambda})$. For the rent-or-buy abstraction, deterministic timer policies are **2-competitive** and randomized are $\frac{e}{e-1}\approx 1.58$-competitive against the offline optimum. Online-learning timer selection achieves $O(\sqrt{T})$ regret against the best fixed delay over a horizon of $T$ commits.

## 5. Lower Bound
The rent-or-buy structure yields a matching **2 deterministic / $\frac{e}{e-1}$ randomized** competitive lower bound, so the abstracted problem is tight. For the *full* problem these bounds do not transfer cleanly: arrivals are correlated with the policy's own latency (closed-loop / self-clocking), workloads are non-stationary, and the cost is multi-objective — no nontrivial lower bound is known for the realistic adaptive, non-stationary, closed-loop setting. The hardness is one of *modeling*, not (yet) of established complexity.

## 6. The Gap
The clean abstractions (bulk-service, ski-rental) are tight, but they discard exactly the features that matter operationally: closed-loop arrivals, non-stationarity, device-specific flush-cost curves (group-commit on NVMe vs. quorum replication differ qualitatively), and multi-tenant fairness. The gap is between *provably optimal under idealized assumptions* and *empirically tuned heuristics in production*. Closing it requires either a control-theoretic policy with regret/competitive guarantees under closed-loop non-stationary load, or an impossibility result showing no such guarantee exists.

## 7. Current Research (as of June 2026)
- Learned/RL-based commit and I/O batching controllers, extending the learned-systems agenda (MIT DSAIL, CMU) to durability control *(frontier — verify)*.
- Disaggregated-log durability (cloud OLTP: Aurora, Socrates, Neon, PolarDB) reframes the batch target as a remote quorum, changing $c$ from a local `fsync` to a network-tail-latency distribution; optimal batching there is largely unstudied analytically *(frontier — verify)*.
- Persistent-memory / CXL durability domains shrink $c$ toward zero, which questions whether group commit should exist at all for some tiers.

## 8. Future Work
- A unifying model with provable regret under non-stationary, closed-loop arrivals.
- Multi-objective Pareto characterization (latency tail vs. throughput vs. energy/flush-amplification).
- Co-design with quorum replication: jointly optimize batch size and quorum acknowledgement.
- SLO-aware policies giving p99 guarantees rather than mean-latency optima.

## 9. Key References
- **[Foundational]** Gawlick, D. & Kinkade, D. *Varieties of Concurrency Control in IMS/VS Fast Path.* IEEE Database Engineering Bulletin, 1985. (Origin of group commit.)
- **[SOTA]** Johnson, R., Pandis, I., Stoica, R., Athanassoulis, M. & Ailamaki, A. *Aether: A Scalable Approach to Logging.* VLDB, 2010.
- **[Foundational]** Deb, R. K. & Serfozo, R. F. *Optimal Control of Batch Service Queues.* Advances in Applied Probability, 1973.
- **[Foundational]** Karlin, A., Manasse, M., McGeoch, L. & Owicki, S. *Competitive Randomized Algorithms for Nonuniform Problems (ski rental / rent-or-buy).* Algorithmica, 1994.
- **[Foundational]** DeWitt, D. et al. *Implementation Techniques for Main Memory Database Systems.* SIGMOD, 1984. (Early group-commit batching analysis.)

---
*Part of the [DBMS Research catalog](../../README.md).*
