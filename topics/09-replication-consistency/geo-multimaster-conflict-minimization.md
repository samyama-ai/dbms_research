# Geo-replicated multi-master conflict minimization

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/geo-multimaster-conflict-minimization` · **Status:** open

## 1. Problem Statement
In a geo-distributed **multi-master** store, every region accepts writes locally for low latency; conflicting concurrent writes to the same item from different regions must later be reconciled (last-writer-wins, CRDT merge, or app-level resolution). Such conflicts cost throughput, can lose intent, and force users to handle merge semantics. The problem: **minimize the rate (and severity) of cross-region write conflicts** through *data placement*, *partitioning/sharding*, and *request scheduling/routing* — **without** serializing writers (i.e., without falling back to single-master or global consensus per key).

Variants:
- **Optimization (placement):** assign each data item a "home"/affinity and route writes to minimize expected concurrent cross-region writes subject to latency SLOs.
- **Online scheduling:** delay/batch/route writes to reduce temporal overlap without violating latency budgets.
- **Counting/prediction:** estimate the conflict rate of a placement under a workload model (input to the optimizer).

## 2. Mathematical Foundations
Model items $I$, regions $G$, and an access workload as a stream; for item $x$, conflicts arise when two writes from different regions are *concurrent* (incomparable in the causal order) within the inter-region propagation delay $\Delta$. Expected pairwise conflict rate for $x$ under Poisson arrivals with regional rates $\lambda_{g,x}$ scales as $\sum_{g\neq g'} \lambda_{g,x}\lambda_{g',x}\,\Delta$ — the conflict "birthday" effect. Minimizing total conflicts by **affinity assignment** $h: I \to G$ is a graph-partitioning / facility-location problem: build a hypergraph where co-accessed items from the same region cluster; the objective resembles **min-cut / quadratic assignment** and is NP-hard. Placement also trades against latency: assigning $x$'s home far from a hot region raises that region's write latency (a metric-facility-location penalty). Scheduling adds a temporal axis: deliberately ordering/delaying writes within $\Delta$ to avoid overlap is an online scheduling problem with deadline constraints. Conflict-free types (CRDTs) change the *severity* function but not the underlying overlap counting.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** No optimal placement algorithm; the static problem is NP-hard (reduces from balanced graph partitioning / QAP). Related: Schism (Curino et al., VLDB 2010) graph-partitioning for transaction locality; RACS/Volley (Agarwal et al., NSDI 2010) for geo data placement minimizing inter-DC traffic.
- **Systems-SOTA:** **Cosmos DB**, **DynamoDB Global Tables**, **Cassandra** multi-DC use LWW/CRDT reconciliation with mostly *manual* region affinity. **Spanner/CockroachDB** avoid the problem via leaseholder/single-master per range (i.e., they *serialize* per key — the regime this problem explicitly excludes). **Calvin/SLOG** (Abadi et al.) reduce conflicts via deterministic ordering and home-region designation, the closest principled systems answer.

## 4. Upper Bound
For the **static placement** sub-problem, conflict-minimizing affinity can be approximated by metric/facility-location and balanced-partition approximation algorithms: e.g., an $O(\sqrt{\log n}\,\log\log n)$ approximation for the balanced-cut surrogate (ARV-style), or LP-rounding constant-factor results for the uncapacitated facility-location relaxation of the latency-vs-conflict trade-off — but no approximation is known for the *combined* conflict+latency+capacity objective. For **online scheduling**, deadline-aware batching achieves provable conflict reduction only under restrictive arrival models. SLOG/Calvin achieve *zero* cross-region abort for single-home transactions, at the cost of a remote round trip for multi-home ones.

## 5. Lower Bound
- **NP-hardness:** the static conflict-minimizing placement (with capacity/latency constraints) is NP-hard via reduction from balanced graph partitioning / quadratic assignment.
- **Impossibility floor:** for items genuinely co-written from multiple regions, *some* conflict or coordination is unavoidable: the **CALM theorem** (Hellerstein–Alvaro) states a program is coordination-free iff it is monotone; non-monotone updates require coordination, so conflict-freedom without any serialization is impossible for those operations. CAP/PACELC bound the latency–consistency trade-off any solution can reach.
- No tight approximation lower bound is published for the combined objective.

## 6. The Gap
This is **genuinely open**. We have NP-hardness for the static surrogate and CALM as an impossibility floor for the consistency side, but **no algorithm with provable guarantees for the real objective** (joint conflict-rate + latency-SLO + capacity, under a temporal/online workload). The gap between "minimize conflicts" and "don't serialize writers" is precisely the unexplored middle: principled placement + scheduling that provably reduces conflicts toward the CALM-imposed floor without per-key consensus. Closing it needs (1) a tractable, accurate conflict-rate model usable as an optimizer objective, and (2) approximation or online-competitive algorithms for it.

## 7. Current Research (as of June 2026)
Active: Abadi (UMD) and the Calvin/SLOG line on home-region designation; Alvaro/Hellerstein (UCSC/Berkeley) on CALM and coordination-avoidance; geo-distributed systems groups (MIT, Cornell) on latency-aware placement. Frontier threads: learned/predictive placement that forecasts regional access shift and pre-migrates affinity *(frontier — verify)*; conflict-aware request routing co-designed with CRDT merge cost *(frontier — verify)*; using workload embeddings to estimate conflict rate online *(frontier — verify)*.

## 8. Future Work
- A validated conflict-rate cost model suitable as an optimization objective.
- Approximation / online-competitive algorithms for joint conflict + latency + capacity placement.
- Co-design of placement, scheduling, and merge semantics so reconciliation cost is part of the objective.
- Automatic detection of which items/operations are monotone (CALM-safe) to exempt them from conflict accounting.

## 9. Key References
- **[Foundational]** Hellerstein, Alvaro. *Keeping CALM: When Distributed Consistency Is Easy.* CACM, 2020. — [DOI](https://doi.org/10.1145/3369736)
- **[Foundational]** Curino, Jones, Zhang, Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)
- **[SOTA]** Ren, Li, Abadi. *SLOG: Serializable, Low-latency, Geo-replicated Transactions.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3342263.3342647)
- **[Foundational]** Agarwal et al. *Volley: Automated Data Placement for Geo-Distributed Cloud Services.* NSDI, 2010. — [USENIX](https://www.usenix.org/conference/nsdi10-0/volley-automated-data-placement-geo-distributed-cloud-services)
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture (CAP).* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)

## 10. Worked Example

Two regions, US and EU, both accept writes to a hot key $x$. Propagation delay $\Delta = 100$ ms. Poisson write rates: $\lambda_{US,x} = 20$/s, $\lambda_{EU,x} = 5$/s. Using the birthday-style pairwise estimate, expected conflict rate is
$$\sum_{g\neq g'}\lambda_{g,x}\lambda_{g',x}\,\Delta = 2\cdot(20)(5)(0.1) = 20 \text{ conflicts/s}.$$

Now apply **affinity placement**: home $x$ in US and route EU writes there. EU writes pay $+80$ ms latency, but cross-region *concurrent* writes vanish, so the conflict term $\lambda_{US}\lambda_{EU}\Delta \to 0$.

Versus **single-master via consensus**: every write (including all 20/s US writes) pays a quorum round trip — far worse aggregate latency. Affinity captures most of the benefit because the workload is US-skewed (80%). The optimizer's job is exactly this trade: when EU's rate rises toward US's, the latency penalty of one-sided affinity stops being worth it, and CRDT merge or splitting $x$ becomes preferable.

---
*Part of the [DBMS Research catalog](../../README.md).*
