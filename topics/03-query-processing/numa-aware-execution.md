---
id: 03-query-processing/numa-aware-execution
title: "NUMA-aware operator placement"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# NUMA-aware operator placement

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/numa-aware-execution` · **Status:** empirically-open

## 1. Problem Statement

On a modern many-core server, memory is **non-uniform**: each CPU socket has fast local DRAM
and slower, bandwidth-limited access to remote sockets' memory across the interconnect (UPI/
Infinity Fabric). For bandwidth-bound operators — hash joins, aggregations, scans — query
throughput is governed less by compute than by **cross-socket traffic** and **interconnect
contention**. The problem: decide **where to place data** (which socket holds each partition /
hash table) and **where to run threads** (which socket executes each morsel/operator) so that
cross-socket traffic and remote-memory stalls are minimized while all cores stay busy.

Given a plan, a NUMA topology (sockets, per-socket bandwidth, pairwise distances), and a data
placement, choose a **(data placement, thread placement, work-stealing policy)** triple that
minimizes makespan / maximizes throughput subject to memory-capacity and load-balance
constraints.

Variants: **static** (partition and pin at plan time); **adaptive** (migrate data/threads
using observed remote-access counters); **decision** (does a placement with $\le c$ remote
traffic and balanced load exist?); the last is a constrained graph-partitioning problem.

## 2. Mathematical Foundations

Model the machine as a weighted graph $G=(\mathcal{S}, d)$ over sockets, with $d(i,j)$ the
remote-access penalty and per-socket bandwidth $\beta_i$. An operator's data is a set of pages
assigned by $\pi:\text{pages}\to\mathcal{S}$; threads are assigned by $\tau$. Total
remote-traffic cost is $\sum_{\text{accesses }(t,p)} d(\tau(t),\pi(p))$. Minimizing this subject
to a per-socket load (capacity) balance constraint is exactly **balanced graph / hypergraph
partitioning** — minimize edge cut (cross-socket accesses) with balanced parts — which is
**NP-hard** (it generalizes MIN-BISECTION and MULTIWAY CUT). The achievable throughput is
bounded by the **bottleneck socket bandwidth**: $\text{tput} \le \min_i \beta_i /
(\text{local}_i + \sum_{j\ne i} \text{remote}_{ji})$, a max-flow/min-cut-flavored constraint.
Scheduling threads to balance load while respecting locality is a **locality-constrained
makespan** problem, combining $P\Vert C_{\max}$ with the cut objective — the interaction is
what makes it hard: pure locality (no stealing) can leave cores idle; pure load balance
(global stealing) maximizes remote traffic.

## 3. State of the Art (SOTA)

- **Foundational systems result.** Leis, Boncz, Kemper, Neumann, *"Morsel-Driven Parallelism:
  A NUMA-Aware Query Evaluation Framework"* (SIGMOD 2014) — the canonical design: partition
  data per socket, schedule morsels with **NUMA-local-first** work-stealing so a thread
  prefers local morsels and steals remotely only when idle. Near-linear scaling on many-core
  NUMA machines.
- **Data shuffling / placement.** Li, Pandis, Müller, Raman, Lohman, *"NUMA-Aware Algorithms:
  the Case of Data Shuffling"* (CIDR 2013) quantifies interconnect as the bottleneck and gives
  NUMA-conscious shuffle.
- **Adaptive/relational placement.** Psaroudakis et al. (SAP HANA line, VLDB 2015–2016)
  studied adaptive NUMA-aware data placement and task scheduling under concurrency.
- **Systems** like HyPer, Umbra, SAP HANA, and DBMS-on-many-core research engines ship
  NUMA-local partitioning as standard.

## 4. Upper Bound

For the placement subproblem, balanced graph/hypergraph partitioning admits an
$O(\sqrt{\log n}\,\log n)$-approximation for balanced separators / sparsest cut (Arora–Rao–
Vazirani, JACM 2009), and practical multilevel partitioners (METIS/KaHIP) get near-optimal
cuts on real instances. For scheduling, **NUMA-local-first work-stealing** achieves the
standard $O(T/P + \text{span})$ makespan (Blumofe–Leiserson) while empirically keeping remote
steals to the idle-time tail, so cross-socket traffic is $O(\text{imbalance})$ rather than
$O(\text{total})$. Morsel-driven execution realizes this and is the practical upper bound:
near-linear speedup with remote traffic confined to load-balancing steals.

## 5. Lower Bound

- **NP-hardness:** optimal balanced placement minimizing cross-socket traffic is NP-hard
  (reduction from MIN-BISECTION / MULTIWAY CUT); even approximation is APX-hard for general
  graphs.
- **Bandwidth lower bound:** any execution must move $\Omega(\text{remote working set})$ bytes
  across the interconnect; if a hash table cannot be socket-partitioned along the probe key,
  $\Omega(1)$ fraction of probes are necessarily remote — an information-theoretic floor on
  cross-socket traffic.
- **Locality–balance tension (online):** an adversary placing all hot work on one socket forces
  any locality-respecting scheduler to either idle cores (lose $\Theta(P)$ throughput) or steal
  remotely (incur the bandwidth penalty), giving a competitive lower bound tying makespan to
  the interconnect/local bandwidth ratio.

## 6. The Gap

Morsel-driven NUMA-local scheduling **empirically** closes most of the gap for the common case,
and partitioning theory provides cut approximations — but there is **no algorithm with proven
near-optimal joint placement-plus-scheduling under unknown skew and concurrency**, and no
portable model predicting the right placement across topologies (2-socket vs. 8-socket vs.
chiplet/CXL-attached memory). The open part: a principled, possibly online, controller that
co-optimizes data placement, thread placement, and stealing with guarantees against the
locality–balance lower bound, robust to skew and to multi-tenant interference. Hence
*empirically-open*.

## 7. Current Research (as of June 2026)

- **Adaptive data migration / replication** driven by remote-access hardware counters, moving
  or replicating hot tables to the socket(s) that probe them. Active in TUM (Neumann/Leis),
  SAP HANA (Psaroudakis lineage), and ETH (Alonso).
- **CXL-attached and disaggregated/tiered memory**: extending NUMA-awareness to byte-addressable
  far memory with even larger distance ratios; placement becomes a tiering problem.
  *(frontier — verify)*
- **Joint NUMA + skew + cache scheduling**, unifying this with skew-resilient join scheduling
  and cache/SIMD-optimal joins. *(frontier — verify)*
- **Chiplet-aware placement** for modern multi-die CPUs where intra-package NUMA effects appear.
  *(frontier — verify)*

## 8. Future Work

- A scheduler with provable competitive guarantees against the locality–balance lower bound
  under adversarial skew and concurrency.
- Portable placement models spanning 2-socket to many-socket, chiplet, and CXL-tiered memory.
- Co-optimization of NUMA placement with batch/morsel sizing and cache-optimal join layouts.

## 9. Key References

- **[Foundational]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[Foundational]** Li, Pandis, Müller, Raman, Lohman. *NUMA-Aware Algorithms: the Case of Data Shuffling.* CIDR 2013. — [DBLP](https://dblp.org/rec/conf/cidr/LiPMRL13.html)
- **[SOTA]** Psaroudakis, Scheuer, May, Sellami, Ailamaki. *Adaptive NUMA-Aware Data Placement and Task Scheduling for Analytical Workloads in Main-Memory Column-Stores.* VLDB 2016. — [DOI](https://doi.org/10.14778/3015274.3015275)
- **[Foundational]** Blumofe, Leiserson. *Scheduling Multithreaded Computations by Work Stealing.* JACM 1999. — [DOI](https://doi.org/10.1145/324133.324234)
- **[Foundational]** Arora, Rao, Vazirani. *Expander Flows, Geometric Embeddings and Graph Partitioning.* JACM 2009. — [DOI](https://doi.org/10.1145/1502793.1502794)

## 10. Worked Example

A 2-socket box: local DRAM bandwidth $\beta = 100$ GB/s per socket, remote access at $d=0.5$ (i.e. remote is $2\times$ slower, effective $50$ GB/s). A hash join probes a 40 GB build-side hash table with 80 GB of probe tuples; we run 2 threads, one pinned per socket.

*Naive placement:* put the whole hash table on socket 0. Socket-1's thread issues every probe across the interconnect: $40$ GB of remote hash-table reads. Its effective throughput is capped at $50$ GB/s, so socket 1 takes $\ge 40/50 = 0.8$ s on table traffic alone while socket 0 streams locally — the slower socket sets the makespan.

*NUMA-aware placement:* radix-partition the table on the probe key so half lives on each socket, and route each morsel to the socket holding its partition. Now $\approx 0$ cross-socket table reads; both sockets read locally at $100$ GB/s, and the $40$ GB is split $20/20$, finishing in $\approx 20/100 = 0.2$ s — a $4\times$ win, matching the $\min_i \beta_i/(\text{local}_i+\sum \text{remote}_{ji})$ bound. The open part: when key skew sends $80\%$ of probes to one partition, locality forces that socket to idle the other or steal remotely — exactly the locality–balance tension.

---
*Part of the [DBMS Research catalog](../../README.md).*
