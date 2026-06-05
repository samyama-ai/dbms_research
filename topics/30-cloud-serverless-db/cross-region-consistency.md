# Cross-region replicated cloud-database consistency

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/cross-region-consistency` · **Status:** open

## 1. Problem Statement
A cloud database is replicated across a set $R$ of geographic regions. Clients in each region issue reads and writes; the operator wants every read to be served from (or near) the client's region to minimize latency, while honoring a configured *consistency contract* — typically **bounded staleness**: a read may return a value at most $\Delta$ time-units (or $k$ versions) behind the latest committed write. The twist that distinguishes the cloud variant from classical geo-replication is **pricing asymmetry**: inter-region egress, cross-region request, and per-region compute/storage costs differ by region pair and are billed separately, so the cost of keeping a replica fresh is not symmetric.

- **Decision variant:** Given a replica/placement plan, a staleness bound $\Delta$, and per-region latency SLOs, does there exist a replication schedule (which writes to propagate where, and when) that satisfies all SLOs?
- **Optimization variant:** Minimize total dollar cost (egress + request + compute) subject to: (i) read tail-latency SLO per region, and (ii) staleness $\le \Delta$ everywhere reads are served.
- **Counting/robustness variant:** Over an uncertain demand distribution, bound the probability that the staleness contract is violated.

## 2. Mathematical Foundations
Model replicas as nodes in a weighted graph $G=(R,E)$ with propagation delay $d_{ij}$ and per-byte egress price $p_{ij}$ on edge $(i,j)$. Writes arrive as a stream; let $W_i(t)$ be the write set known at region $i$ by time $t$. A read at region $i$ is **$\Delta$-fresh** if it observes all writes globally committed before $t-\Delta$.

The hard constraint is the **CAP / PACELC** tradeoff: under a network partition one must sacrifice consistency (C) or availability (A); *else* (no partition) one still trades latency (L) against consistency (C). Formally, no protocol can guarantee linearizable reads with local-region latency below the one-way delay $d_{\min}$ to a quorum (Lipton–Sandberg / Attiya–Welch lower bound: for sequentially consistent memory, $\text{read} + \text{write latency} \ge d$, the round-trip diameter).

Bounded staleness relaxes this: it is captured by **consistency models on a lattice** (linearizable $\succ$ sequential $\succ$ bounded-staleness $\succ$ eventual), and by the **$t$-visibility / $k$-staleness** framework. The cost-optimization layer is a constrained network-design / facility-location problem; with per-region capacity it is an integer program whose LP relaxation admits submodular-style rounding when the freshness benefit is monotone submodular in the set of propagation edges activated.

$$
\min_{x} \sum_{(i,j)\in E} p_{ij}\, b_{ij}(x) \quad\text{s.t.}\quad \forall i:\ \text{stale}_i(x)\le \Delta,\ \ \Pr[L_i > \ell_i]\le \epsilon_i .
$$

## 3. State of the Art (SOTA)
**Systems-SOTA.** Google **Spanner** (OSDI 2012) achieves external consistency globally using TrueTime-bounded clock uncertainty; bounded-staleness reads are a first-class read mode. **Amazon Aurora Global Database** and **DynamoDB Global Tables** offer asynchronous cross-region replication with last-writer-wins or eventual semantics. **CockroachDB** and **YugabyteDB** use Raft per range with "follower reads" at a configurable staleness. **Azure Cosmos DB** exposes five tunable consistency levels including an explicit *bounded staleness* level parameterized by $(k,\Delta)$ — the closest production system to the formal contract here.

**Theory-SOTA.** The **PBS (Probabilistic Bounded Staleness)** model (Bailis et al., VLDB 2012) predicts staleness distributions for quorum systems. Consistency-aware replica placement is studied as a variant of connected facility location and capacitated $k$-median.

## 4. Upper Bound
For the cost-optimization variant with monotone submodular freshness coverage and a knapsack-style budget, greedy/continuous-greedy gives a $(1-1/e)$-approximation. Capacitated $k$-median placement (choosing where replicas live) admits constant-factor approximations (best known $\approx 7.08 + \epsilon$ for capacitated $k$-median, Demirci–Li and successors). Latency-only quorum reads achieve optimal one-round-trip-to-nearest-quorum cost, matching the Attiya–Welch bound up to clock skew $2\varepsilon$ (TrueTime).

## 5. Lower Bound
The optimization variant is **NP-hard** (it generalizes capacitated facility location / $k$-median). The latency–consistency floor is **information-theoretic / impossibility-theoretic**: CAP (Gilbert–Lynch, 2002) forbids C+A under partitions; Attiya–Welch (1994) shows any sequentially consistent implementation has read+write latency $\ge d$ (network diameter), so local-latency linearizable reads across regions are impossible without sacrificing either freshness or availability. These are unconditional and pricing-independent.

## 6. The Gap
The *feasibility floor* (CAP/Attiya–Welch) is closed and tight — we know exactly what is impossible. The genuinely **open** part is the *cost-optimal* schedule under asymmetric pricing and stochastic demand: there is no tight approximation hardness matching the $(1-1/e)$ / constant-factor upper bounds once you add (a) per-region price asymmetry, (b) tail-latency (not mean) SLOs, and (c) demand uncertainty. Closing it requires either an APX-hardness result for the joint freshness+tail-latency+egress objective or an algorithm with provable cost competitiveness against an offline optimum.

## 7. Current Research (as of June 2026)
- Learned/predictive replica placement and adaptive consistency that shifts the $(k,\Delta)$ knob per workload phase. *(frontier — verify)*
- Egress-aware replication that exploits CDN-style hierarchical caching to cut cross-region bytes; active in the Cosmos DB and CockroachDB teams.
- TrueTime-without-atomic-clocks: software clock-bound tightening (e.g., Amazon Time Sync, AWS's clock-bound API) narrowing the $\varepsilon$ floor. *(frontier — verify)*
- Groups: Bailis-lineage consistency theory (Berkeley RISE/Sky lab), Abadi (PACELC, UMD), Spanner/AlloyDB teams, CMU CockroachDB-adjacent work.

## 8. Future Work
- A unified objective combining dollar cost, tail latency, and staleness with provable guarantees.
- Online/competitive algorithms for replication schedules under adversarial or stochastic demand.
- Verified consistency-level downgrades (safely weakening from bounded staleness to eventual during partitions, then re-converging) with formal staleness re-bounding.

## 9. Key References
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* ACM SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[Foundational]** Attiya, H., Welch, J. *Sequential Consistency versus Linearizability.* ACM TOCS, 1994. — [DOI](https://doi.org/10.1145/176575.176576)
- **[SOTA]** Corbett, J. et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [DBLP](https://dblp.org/rec/conf/osdi/CorbettDEFFFGGHHHKKLLMMNQRRSSTWW12.html)
- **[SOTA]** Bailis, P., Venkataraman, S., Franklin, M., Hellerstein, J., Stoica, I. *Probabilistically Bounded Staleness for Practical Partial Quorums.* VLDB, 2012. — [DOI](https://doi.org/10.14778/2212351.2212359) · [arXiv](https://arxiv.org/abs/1204.6082)
- **[Survey]** Abadi, D. *Consistency Tradeoffs in Modern Distributed Database System Design: CAP is Only Part of the Story (PACELC).* IEEE Computer, 2012. — [DOI](https://doi.org/10.1109/MC.2012.33)

## 10. Worked Example

Three regions $R=\{\text{us-east}, \text{eu-west}, \text{ap-south}\}$ with one-way propagation delays $d_{\text{us},\text{eu}}=40\,\text{ms}$, $d_{\text{us},\text{ap}}=110\,\text{ms}$, $d_{\text{eu},\text{ap}}=90\,\text{ms}$, and a staleness bound $\Delta=150\,\text{ms}$. A write commits in us-east at $t=0$.

*Bounded-staleness check.* A read in ap-south at time $t$ is $\Delta$-fresh if it sees all writes committed before $t-\Delta$. Async replication delivers the us-east write to ap-south at $t=110\,\text{ms}$. So any ap-south read at $t \ge 110$ already reflects it; even a read at $t=110$ is fresh because $110 - 150 = -40 < 0$, i.e. the contract only requires seeing writes older than $t-\Delta$, and $110 \le \Delta$ means the bound is never violated for this single write. The contract is satisfied with pure async replication — no quorum round trip needed.

*Why linearizability would cost more.* By Attiya–Welch, a linearizable read in ap-south needs read+write latency $\ge d$ across the system diameter. The diameter here is $d_{\text{us},\text{ap}}=110\,\text{ms}$, so a strongly-consistent cross-region read pays $\ge 110\,\text{ms}$, versus a local follower read of roughly $1\,\text{ms}$. Bounded staleness buys back $\approx 109\,\text{ms}$ of tail latency at the price of at most $\Delta=150\,\text{ms}$ of version lag — the exact knob Cosmos DB exposes as $(k,\Delta)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
