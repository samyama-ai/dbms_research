# Self-tuning replication factor and quorum sizing

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/adaptive-replication-factor` · **Status:** empirically-open

## 1. Problem Statement
Build an online control loop that continuously adjusts a replicated store's **replication factor** $N$ (number of replicas per data item/shard) and its **read/write quorum sizes** $(R, W)$ to meet operator targets on **durability**, **availability**, **tail latency**, and **cost**, under shifting workload, failure rates, and network conditions — without violating the configured consistency level.

Variants:
- **Optimization:** minimize cost (storage + cross-AZ bandwidth) subject to durability $\ge$ target, $p99$ latency $\le$ SLO, and a consistency constraint (e.g., $R+W>N$ for strong reads).
- **Control / online:** a feedback loop that *reconfigures* $N, R, W$ safely while serving traffic (live re-replication, quorum hand-off).
- **Per-key / per-shard:** heterogeneous policies driven by access skew (hot keys get more replicas/closer placement).

This is "empirically-open": prototypes exist, but there is no agreed objective, no stability/optimality guarantees, and no standard benchmark.

## 2. Mathematical Foundations
Durability under independent replica failure probability $f$ over a repair window: data loss probability $\approx \binom{N}{N-k+1}f^{\,N-k+1}$ for a $k$-of-$N$ erasure/quorum scheme; for plain replication, loss $\approx f^{N}$, giving the classic "nines per replica" curve. Consistency couples to quorums via the intersection rule: strong (linearizable) reads require $R + W > N$ and $W > N/2$; sloppy/eventual configs relax this. Latency is governed by **order statistics**: a quorum of $q$ from $N$ replicas yields response time $= q$-th order statistic of replica latencies — the tail-at-scale phenomenon (Dean–Barroso). The control problem is a constrained sequential decision process (MDP/contextual bandit) with reconfiguration cost; the static slice is an integer program trading $N$ (cost) against the order-statistic latency and the durability exponent. Reconfiguration safety relies on quorum-overlap invariants during membership change (akin to Raft joint consensus / Vertical Paxos).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** No closed-form optimal controller. Foundations: Dynamo's tunable $(N,R,W)$ (DeCandia et al., SOSP 2007); FLP/CAP framing of which configs are admissible; reconfiguration via Vertical Paxos (Lamport–Malkhi–Zhou) and Raft membership change.
- **Systems-SOTA:** Cassandra/ScyllaDB expose per-query consistency levels but tune $N$ manually; **Azure Cosmos DB** offers tunable consistency tiers; autoscaling tier-ers and learned configuration advisors (OtterTune-style) and cloud "auto-rebalancing" (CockroachDB, DynamoDB adaptive capacity) adjust placement/replicas reactively. RL-based replica controllers appear in research prototypes.

## 4. Upper Bound
No proven competitive ratio is established for the full online problem. For the **static** sub-problem (fixed workload), choosing $N,R,W$ to minimize cost under durability + latency-SLO constraints is solvable by enumeration over the small discrete grid of $(N,R,W)$ ($N$ typically $\le 7$), i.e., $O(N^2)$ evaluations — practically trivial, modulo accurate latency/failure models. For the online/reconfiguration version, the best *known* guarantees are heuristic stability (controllers shown empirically not to oscillate) rather than competitive bounds.

## 5. Lower Bound
- **CAP / consistency floor:** any config serving strongly-consistent reads must keep $R+W>N$; under partition it must sacrifice availability or consistency (CAP, Gilbert–Lynch 2002) — model: asynchronous network impossibility. This bounds the feasible region the controller may explore.
- **Online hardness:** with adversarial workload/failure sequences, no online reconfiguration policy can match the offline optimum (a standard $\Omega(\cdot)$ competitive lower bound for online resource allocation with switching cost). No tight ratio is published for this specific problem.
- **Durability:** to tolerate $t$ simultaneous failures with quorum reads you need $N \ge 2t+1$ (or $\ge t + k$ with erasure) — an information-theoretic floor on replica count.

## 6. The Gap
The static feasibility region is well-understood (quorum intersection + durability exponent + order-statistic latency). The open gap is the **online control** layer: no agreed objective function, no proven stability/optimality, no benchmark, and reconfiguration-safety guarantees that are decoupled from the tuning objective. Closing it requires (1) a formal model unifying durability, tail latency, cost, and consistency into one constrained-MDP with switching cost, and (2) controllers with provable competitive or regret bounds — currently absent.

## 7. Current Research (as of June 2026)
Active: cloud-database teams (AWS DynamoDB adaptive capacity, CockroachDB Labs, Microsoft Cosmos DB) on reactive replica/placement rebalancing; the learned-DB-config community (Pavlo/CMU, OtterTune lineage) extending tuning to replication; RL-for-systems groups applying contextual bandits to quorum selection *(frontier — verify)*. Emerging threads: jointly learning *placement* and *quorum* to exploit geo-latency *(frontier — verify)*; SLO-driven per-key replication with bandit regret guarantees *(frontier — verify)*.

## 8. Future Work
- A standard benchmark and objective for self-tuning replication (durability × latency × cost × consistency).
- Controllers with provable regret/competitive ratios under switching (re-replication) cost.
- Safe online reconfiguration co-designed with the optimizer (joint consensus that respects the latency/cost objective).
- Per-key heterogeneous policies driven by online skew estimation.

## 9. Key References
- **[Foundational]** DeCandia et al. *Dynamo: Amazon's Highly Available Key-Value Store.* SOSP, 2007. — [DOI](https://doi.org/10.1145/1294261.1294281)
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[Foundational]** Dean, Barroso. *The Tail at Scale.* CACM, 2013. — [DOI](https://doi.org/10.1145/2408776.2408794)
- **[SOTA]** Lamport, Malkhi, Zhou. *Vertical Paxos and Primary-Backup Replication.* PODC, 2009. — [DOI](https://doi.org/10.1145/1582716.1582783)
- **[SOTA]** Van Aken, Pavlo, et al. *Automatic Database Management System Tuning Through Large-Scale Machine Learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)

## 10. Worked Example

Take per-replica annual failure probability $f = 0.02$ over the repair window. For plain replication, durability is $1 - f^{N}$: at $N=3$, loss $\approx 0.02^3 = 8\times10^{-6}$ ("five nines"); at $N=5$, loss $\approx 3.2\times10^{-9}$ ("eight nines"). Suppose the SLO needs $\ge$ six nines durability — then $N=3$ falls short, $N=4$ ($1.6\times10^{-7}$) suffices.

Now pick $(R,W)$ for $N=4$ with strong reads. The intersection rule requires $R+W>N$ and $W>N/2$, so $W\ge3$. Choosing $W=3,R=2$ gives $R+W=5>4$ (valid); writes wait on the 3rd-fastest of 4 replicas, reads on the 2nd-fastest. If replica latencies are i.i.d. $\sim 10\text{ms}\cdot\text{Exp}$, the $q$-th order statistic of $N$ has mean $10\sum_{i=N-q+1}^{N}\frac1i$ ms: read ($q=2,N=4$) $\approx 10(\tfrac13+\tfrac14)=5.8$ ms, write ($q=3$) $\approx 10(\tfrac12+\tfrac13+\tfrac14)=10.8$ ms. The static optimizer enumerates this tiny grid ($N\le7$) to find the cheapest config meeting all constraints.

---
*Part of the [DBMS Research catalog](../../README.md).*
