---
id: 12-newsql-distributed-sql/geo-transaction-routing-slas
title: "Geo-distributed transaction routing under SLAs"
topic: 12-newsql-distributed-sql
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Geo-distributed transaction routing under SLAs

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/geo-transaction-routing-slas` · **Status:** empirically-open

## 1. Problem Statement

In a geo-distributed SQL system, a transaction's latency is dominated by *where* its data
replicas live, *where* its coordinator runs, and *how many* WAN round-trips its commit
protocol incurs. Given a workload of transaction templates with origin distributions, a set
of regions with pairwise latencies, replication/consensus constraints, and per-class
**latency SLAs** (e.g., p99 ≤ 50 ms for class A), the problem is to choose a **data
placement** (which keys/partitions replicated in which regions, leader placement) and a
**routing policy** (which region coordinates each transaction, follower-read targets) that
**meets the SLAs at minimum cost** (replication storage + WAN bandwidth + compute).

Variants: (i) **Decision** — does a feasible placement+routing meeting all SLAs exist?
(ii) **Optimization** — minimize cost s.t. SLA satisfaction (or minimize SLA violations s.t.
budget). (iii) **Online/adaptive** — the workload and inter-region latencies drift; maintain
a near-optimal placement under bounded reconfiguration (migration) cost.

## 2. Mathematical Foundations

Model regions as a complete graph $G=(R,E)$ with edge weights $\ell_{ij}$ (RTT). A
transaction class $t$ has an access set $A_t \subseteq K$ over keys $K$, an origin
distribution $\pi_t$ over $R$, and an SLA $L_t$ (e.g., a quantile target). A placement is a
map $\rho: K \to 2^R$ (replica regions) with a designated leader $\lambda(k) \in \rho(k)$
subject to a quorum constraint $|\rho(k)| \ge 2f+1$. The commit latency of an instance is a
function of the farthest required quorum round-trip and cross-shard fan-out, e.g.,
$\mathrm{lat} \approx \max_{k \in A_t}\big(\ell_{o,\lambda(k)} + \mathrm{quorum\text{-}RTT}(\rho(k))\big)$.

This is a **capacitated facility-location / replica-placement** problem with latency and
quorum constraints — a generalization of $k$-median/$k$-center with SLA (covering-radius)
side constraints. The leader/quorum choice ties it to **min-cost quorum placement**.
Workload-driven co-location to reduce cross-region distributed commits is a **graph/hypergraph
partitioning** problem (minimize the weight of edges cut across regions), NP-hard via
balanced min-cut. Tail-latency SLAs introduce **chance constraints**
$\Pr[\mathrm{lat} > L_t] \le \delta$, turning it into stochastic/robust optimization.

## 3. State of the Art (SOTA)

**Systems SOTA.** Spanner (Corbett et al., OSDI 2012) places Paxos leaders by region and
uses directory-level movement; CockroachDB and YugabyteDB expose **geo-partitioning** and
follower/leaseholder placement, "duplicate indexes," and region-survival goals.
Akkio (Annamalai et al., OSDI 2018, Facebook) migrates data "shards" to where access
originates to cut WAN latency. Tuba and Volley (Agarwal et al., NSDI 2010) optimized data
placement in geo-distributed stores from access traces. PNUTS, Pileus/Tuba target
consistency-SLA tradeoffs.

**Theory SOTA.** Approximation algorithms for facility location ($1.488$, Li 2013) and
$k$-median ($\approx 2.67$, Byrka et al.) underpin placement, but the *combined* quorum +
tail-SLA + cross-shard-commit objective has no clean tight approximation; practice relies on
ILP/MILP solvers and heuristics (greedy, local search, LP rounding).

## 4. Upper Bound

For the simplified **uncapacitated replica/leader-placement minimizing mean latency**
(ignoring tail and cross-shard commit), constant-factor approximations follow from facility
location / $k$-median (e.g., $1.488$ for metric facility location; $\approx 2.67$ for
$k$-median). Co-location to minimize cross-region commits inherits balanced-partitioning
approximations (e.g., $O(\sqrt{\log n \log k})$ for balanced cut). In practice, **MILP
formulations** solved to near-optimality on region-scale instances (tens of regions) give
the operational upper bound; online variants use competitive caching/migration analysis
(metrical task systems) for the reconfiguration cost.

## 5. Lower Bound

The decision/optimization problem is **NP-hard**: it generalizes uncapacitated facility
location and balanced graph partitioning, both NP-hard, and with capacities/quorum
constraints it captures generalized assignment. Tail-SLA (chance-constrained) variants are
harder still — chance-constrained programs with discrete decisions are generally
NP-hard and can be inapproximable without distributional assumptions. There are also
**physical lower bounds**: any strictly/strongly consistent commit pays at least the
one-way speed-of-light delay to a quorum, so some SLAs are *infeasible at any cost* (cf.
the strict-serializability latency lower bounds problem). This makes part of the difficulty
information-/physics-theoretic rather than purely combinatorial.

## 6. The Gap

Tagged **empirically-open**: the combinatorial core is well-understood (NP-hard with known
approximations for relaxations), but no algorithm jointly handles (a) tail-latency SLAs,
(b) quorum/consensus round-trip structure, (c) cross-shard distributed-commit fan-out, and
(d) online drift with bounded migration cost — with provable guarantees. Real systems solve
it with heuristics and MILP on traces and validate **empirically**. The open question is
whether a principled algorithm with bounded competitive/approximation ratio under realistic
latency models can match or beat the production heuristics, and how to *predict* tail
latency accurately enough to certify SLA satisfaction before deployment.

## 7. Current Research (as of June 2026)

Active directions: learned/ML-driven placement advisors that ingest workload traces and
predict tail latency for candidate placements *(frontier — verify)*; reinforcement-learning
controllers for online leaseholder rebalancing in CockroachDB/YugabyteDB-style systems
*(frontier — verify)*; and integration of placement with **carbon/cost-aware** region
selection. Industrial work (Google, Microsoft, Meta, CockroachLabs, Yugabyte) continues on
automated geo-partitioning advisors. Robust-optimization formulations handling latency
uncertainty are an emerging academic thread.

## 8. Future Work

- A tight approximation (or hardness-of-approximation) result for the joint
  quorum-placement + tail-SLA objective.
- Online algorithms with competitive bounds against migration cost under non-stationary
  latency.
- Accurate, certifiable tail-latency models for distributed commit usable as SLA oracles.
- Co-optimization of placement with the *choice of commit protocol* (fast-path conditions,
  leaderless vs. leader-based) per workload.

## 9. Key References

- **[Foundational]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Annamalai et al. *Sharding the Shards: Managing Datastore Locality at Scale with Akkio.* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/annamalai)
- **[SOTA]** Agarwal, Dunagan, Jain, Saroiu, Wolman, Bhogan. *Volley: Automated Data Placement for Geo-Distributed Cloud Services.* NSDI, 2010. — [USENIX](https://www.usenix.org/conference/nsdi10-0/volley-automated-data-placement-geo-distributed-cloud-services)
- **[Foundational]** Li. *A 1.488 Approximation Algorithm for the Uncapacitated Facility Location Problem.* Information and Computation, 2013. — [PDF](https://cse.buffalo.edu/~shil/papers/UFL-IC2013.pdf)
- **[Systems]** Ardekani, Terry. *A Self-Configurable Geo-Replicated Cloud Storage System (Tuba).* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/ardekani)

## 10. Worked Example

Three regions with RTTs $\ell_{\text{US-EU}}=80$, $\ell_{\text{US-AP}}=140$, $\ell_{\text{EU-AP}}=160$ ms. A 3-replica quorum ($2f{+}1$, $f{=}1$) needs the **closest 2 of 3** acks; a leader-coordinated commit costs $\ell_{o,\lambda} + \text{quorum-RTT}$.

Class A transactions originate 90% in the US, SLA p99 $\le 50$ ms. Compare two placements of the leader $\lambda$:

- **Leader in EU:** US origin pays $\ell_{\text{US-EU}}=80$ ms just to reach $\lambda$ — already $> 50$ ms. **Infeasible** at any cost (Section 5 physical floor).
- **Leader in US, replicas {US, EU, AP}:** US origin reaches local $\lambda$ ($\approx 1$ ms); quorum needs the nearer follower, EU at $80$ ms RTT $\Rightarrow$ commit $\approx 81$ ms. Still $> 50$ ms.
- **Leader + a 2nd replica both US-region (US-east, US-west, RTT $20$ ms), 3rd in EU:** quorum = leader + nearest follower at $20$ ms $\Rightarrow$ commit $\approx 21$ ms. **Meets SLA.**

So the strict-serializable p99 $\le 50$ ms SLA is feasible only if two replicas sit within $\le 50$ ms of the US origin — co-locating the quorum, at the cost of weaker geographic fault tolerance.

---
*Part of the [DBMS Research catalog](../../README.md).*
