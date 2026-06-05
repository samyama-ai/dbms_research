# Elastic transaction processing without downtime

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/elastic-oltp-repartition` · **Status:** empirically-open

## 1. Problem Statement

A partitioned OLTP system spreads a relation set over $N$ nodes via a partition map $\pi: K \to [N]$ keyed on a partitioning attribute. **Live repartitioning** is the act of changing $\pi \to \pi'$ (to add/remove nodes, rebalance hot ranges, or co-locate access-correlated tuples) *while transactions continue to commit*. The problem: realize the migration with (i) **no global quiescence** (no stop-the-world), (ii) preserved **serializability** (ideally strict serializability / linearizability) across the cutover, and (iii) a **bounded latency tax** $\Delta$ on transactions that touch migrating data.

Variants:
- **Decision:** given a target map $\pi'$, a deadline $T$, and a latency bound $\Delta$, does a migration schedule exist that completes by $T$ with no transaction delayed beyond $\Delta$ and no abort-rate spike above $\epsilon$?
- **Optimization:** minimize total migration time, peak extra latency, or aborts induced; or minimize data moved subject to a target balance (a graph/hypergraph partitioning objective).
- **Online:** $\pi'$ is not given; the workload is revealed incrementally and the system must *decide what to move and when* to track a shifting hot set.

## 2. Mathematical Foundations

Model the access stream as a hypergraph $H=(V,E)$: vertices are tuples (or key ranges), hyperedges are transactions linking the tuples they co-access, weighted by frequency. Balanced min-cut on $H$ is the offline placement objective; it is the classic **balanced graph partitioning** problem, NP-hard and hard to approximate within any constant under reasonable assumptions, with the best general guarantee being $O(\sqrt{\log n \log k})$ (Krauthgamer–Naor–Schwartz) for $k$-balanced partitioning.

Correctness rests on concurrency-control theory: a migration is correct iff the global history remains in **CSR** (conflict-serializable) — equivalently, the conflict graph stays acyclic across the handoff. The cutover for a key $k$ is a *ownership transfer*; modeling it as a distributed commit gives an FLP-style constraint: with asynchrony and one crash, atomic ownership handoff cannot be both safe and live, so practical protocols assume partial synchrony or use a fault-tolerant log (Paxos/Raft) as the arbiter. Reconfiguration correctness can be framed as **virtual synchrony** / dynamic atomic register reconfiguration (cf. RAMBO, Vertical Paxos).

## 3. State of the Art (SOTA)

**Systems-SOTA.** *Squall* (Elmore et al., SIGMOD 2015) does fine-grained, on-demand tuple migration in H-Store with reactive (pull-on-access) and proactive movement, bounding latency spikes. *E-Store* (VLDB 2015) adds two-tier hot-tuple monitoring and a reprovisioning planner. *Rocksteady* (SOSP 2017, RAMCloud) achieves near-line-rate migration using parallel pull and lineage-style replay to keep tail latency low. Cloud-native engines — **Amazon Aurora**, **Google Spanner** (with non-blocking *movedir* directory moves), **CockroachDB** (range splits/rebalances via Raft snapshots + lease transfers), and **TiDB** (Region split/merge) — perform continuous online rebalancing in production. **Accordion** (VLDB 2016) plans elastic partition placement under capacity constraints.

**Theory-SOTA.** Online repartitioning maps to **online balanced (re)partitioning / dynamic balanced graph partitioning** (Avin–Bienkowski–Loukas–Pacut–Schmid), which gives competitive bounds for the migration-cost-vs-rebalancing tradeoff.

## 4. Upper Bound

For the *offline* min-movement migration to a fixed $\pi'$, optimal schedules are polynomial when conflicts form an interval structure; in general the movement-minimizing balanced target is NP-hard, with $O(\sqrt{\log n\log k})$ approximation for the cut and a pseudo-approximation for balance. For the *online* dynamic balanced partitioning problem, the best deterministic competitive ratios are polynomial in $k$ (the partition count) and the cluster size — e.g. $O(k \log k)$-type bounds for the "learning" variant — and remain far from tight. Systems give *empirical* upper bounds: Rocksteady migrates at ~750 MB/s with sub-millisecond tail impact; Squall keeps 99th-percentile latency within a small constant factor during reconfiguration.

## 5. Lower Bound

Two layers. **(a) Combinatorial:** balanced graph/hypergraph partitioning is NP-hard and admits no PTAS for the balanced version (assuming $P\neq NP$ / SSE-hardness for min-bisection-style objectives). Online balanced repartitioning has competitive lower bounds of $\Omega(k)$ and $\Omega(\log n)$ in various models (Avin et al.). **(b) Distributed:** atomic, non-blocking ownership handoff under asynchrony with crash faults is impossible by **FLP**; the **CAP** theorem forbids a migration that is simultaneously linearizable and available under a partition straddling the old/new owner. Thus *zero* added latency with strict serializability and availability is impossible in the asynchronous model — only bounded $\Delta$ under partial synchrony is achievable.

## 6. The Gap

The *feasibility* gap (can it be done online at all) is essentially closed: production systems repartition live. The *open* gap is **quantitative and tight**: there is no matching characterization of the minimal achievable latency tax $\Delta^\*$ as a function of migration rate, conflict density, and consistency level, nor tight competitive ratios for the online "what/when to move" decision under heavy-tailed, shifting workloads. Empirically, tail-latency spikes during repartitioning are reduced but not provably minimized; we lack a theory connecting the partitioning competitive ratio to observed abort/latency behavior. Closing it needs a model unifying concurrency-control conflict cost with online partitioning cost.

## 7. Current Research (as of June 2026)

Active threads: learned/predictive partitioning that pre-stages migrations from workload forecasts; disaggregated and shared-storage designs (Aurora, Neon, PolarDB) that make repartitioning a *metadata/lease* operation rather than a data-copy operation, shrinking $\Delta$ dramatically *(frontier — verify)*; and consensus-integrated rebalancing (CockroachDB, TiDB, FoundationDB) refining lease-transfer and snapshot pacing. Groups: Pavlo/Aiken (CMU, self-driving DBs), Schmid/Avin/Pacut (online balanced partitioning theory), the Spanner/CockroachDB/TiDB engineering communities. Open frontier claim: *separation of compute from storage reduces live-repartitioning to lease handoff, making sub-millisecond cutover routine* *(frontier — verify)*.

## 8. Future Work

- A tight competitive theory of online repartitioning that *incorporates* transaction conflict cost, not just data-movement cost.
- Provable $\Delta$-bounded protocols under strict serializability with explicit partial-synchrony assumptions.
- Workload-prediction-driven migration with formal regret guarantees, tying §predictive-elasticity-bounds to placement.
- Repartitioning primitives for disaggregated memory (see disaggregated-memory-txn) where "moving data" and "moving ownership" decouple.

## 9. Key References

- **[Foundational]** J. Gray, A. Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)
- **[SOTA]** A. Elmore et al. *Squall: Fine-Grained Live Reconfiguration for Partitioned Main Memory Databases.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2723726)
- **[SOTA]** R. Taft et al. *E-Store: Fine-Grained Elastic Partitioning for Distributed Transaction Processing.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2735508.2735514)
- **[SOTA]** C. Kulkarni et al. *Rocksteady: Fast Migration for Low-Latency In-memory Storage.* SOSP, 2017. — [DBLP](https://dblp.org/rec/conf/sosp/KulkarniKZRS17.html)
- **[SOTA]** J. C. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** C. Avin, M. Bienkowski, A. Loukas, M. Pacut, S. Schmid. *Dynamic Balanced Graph Partitioning.* SIAM J. Discrete Math / SPAA, 2019. — [DOI](https://doi.org/10.1137/17M1158513)

## 10. Worked Example

Take 6 key ranges $\{a,b,c,d,e,f\}$ on $N=2$ nodes. Current map $\pi$: node 1 $=\{a,b,c\}$, node 2 $=\{d,e,f\}$. The transaction stream reveals these co-access hyperedges (with frequencies): $\{a,d\}{:}50$, $\{b,c\}{:}10$, $\{e,f\}{:}10$, $\{a,b\}{:}5$.

Under $\pi$, the heavy $\{a,d\}$ pair (freq $50$) is **cross-node** — every such transaction is distributed (2PC). Cross-node cut weight $= 50 + 5\,(\{a,b\}\text{ stays local, so }0) = 50$ from $\{a,d\}$.

Repartition to $\pi'$: node 1 $=\{a,d\}$, node 2 $=\{b,c,e,f\}$. Now $\{a,d\}$ is co-located (saves the $50$-weight distributed cost), and only $\{a,b\}{:}5$ becomes cross-node. New cut $= 5$ — a $10\times$ reduction in distributed-transaction traffic.

**The migration cost:** moving key $d$ to node 1 and keys $\{b,c\}$ stay, but $d$ must transfer ownership. With **Squall**-style reactive migration, a transaction touching $d$ during cutover pulls it on demand, paying a one-time latency tax $\Delta$ (e.g. $+2$ ms) only on the first access. The online dilemma — was the $50/5$ traffic shift worth migrating $1$ key? — is exactly the dynamic-balanced-partitioning competitive tradeoff: migration cost vs. saved inter-cluster communication.

---
*Part of the [DBMS Research catalog](../../README.md).*
