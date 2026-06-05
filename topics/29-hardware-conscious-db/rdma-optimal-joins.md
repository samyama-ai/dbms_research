# RDMA-optimal distributed join algorithms

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/rdma-optimal-joins` · **Status:** partially-solved

## 1. Problem Statement

Remote Direct Memory Access (RDMA) lets a node read/write a peer's registered memory without involving the peer's CPU (*one-sided* verbs: READ, WRITE, atomics) or with CPU help (*two-sided* SEND/RECV). The problem: design distributed equi-joins (and theta/multiway joins) that minimize the dominant costs on RDMA fabrics — **network round trips (latency)** and **bytes transferred (bandwidth)** — under realistic constraints: limited registered/pinned memory per node, one-sided verbs that bypass the remote CPU but offer only primitive synchronization, and a fixed number of queue pairs.

Variants:
- **Optimization:** given relations partitioned across $n$ nodes, compute the join minimizing total bytes and/or rounds.
- **Decision/cost:** is the join feasible within a memory/round budget?
- **Multiway:** extend to acyclic and cyclic multi-relation joins where worst-case-optimal (WCOJ) ideas interact with network cost.

## 2. Mathematical Foundations

Two cost models matter. **Massively Parallel Computation (MPC)** (Beame, Koutris, Suciu, PODS 2013) bounds rounds and per-machine load $L$ for joins; a single-round join over $p$ machines needs load $L = \tilde O(|R|/p^{1/\rho^*})$ where $\rho^*$ is the **fractional edge cover number** of the query, tying network cost to the **AGM bound** $|{\bowtie}| \le \prod_e |R_e|^{x_e}$. **Worst-case-optimal joins** (Ngo, Porat, Ré, Rudra, PODS 2012) give sequential output-sensitive bounds; HyperCube / Shares (Afrati–Ullman, Beame et al.) gives the optimal single-round multiway partitioning whose communication is governed by $\rho^*$.

RDMA adds a *primitive-level* cost: a one-sided READ is one round trip; chasing a remote pointer (e.g. a hash bucket then its overflow) costs a round trip per dereference. So algorithms trade **bytes** (push data) against **rounds** (pull via one-sided reads). Registered-memory limits cap the working set, connecting to external-memory / I/O-bound analysis.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Barthels et al., *Distributed Join Algorithms on Thousands of Cores* (VLDB 2017) and the earlier *Rack-Scale In-Memory Join* (SIGMOD 2015) showed radix-hash and sort-merge joins scaling to thousands of cores using one-sided RDMA and careful overlap of compute/communication. *FaRM* (Dragojević et al., NSDI 2014) underpins RDMA hash-table designs. Rödiger et al.'s *flow-join* (ICDE 2016) and *high-speed query processing over fast networks* (VLDB 2015/2016) handle skew and saturate InfiniBand. *NAM-DB* (Binnig/Crotty/Zamanian) advanced the network-attached-memory architecture.
- **Theory-SOTA.** MPC-optimal single-round joins (HyperCube/Shares) and multi-round MPC algorithms give round/load-optimal results for many query classes; WCOJ governs output-sensitive cost.

## 4. Upper Bound

For a single equi-join on $p$ machines, hash partitioning achieves load $\tilde O((|R|+|S|)/p)$ in **one round** with bytes $O(|R|+|S|)$ shuffled. For multiway joins, HyperCube reaches the single-round load lower bound $\tilde O(\text{IN}/p^{1/\rho^*})$ matching AGM. With one-sided RDMA, semi-join-style designs pull only matching tuples, reducing bytes toward output size at the cost of extra round trips (one per probe). Barthels et al. demonstrate near-line-rate radix joins; competitive in practice with $O(1)$ communication rounds for the partitioned phase.

## 5. Lower Bound

In MPC, a tight load lower bound $\Omega(\text{IN}/p^{1/\psi})$ (where $\psi$ relates to the fractional vertex/edge cover) holds for single-round computation of conjunctive queries (Koutris–Suciu and follow-ups) — provably you cannot do better in one round. Multi-round lower bounds are weaker and partly conditional. The AGM bound is an unconditional output-size lower bound forcing any algorithm to potentially move $\Omega$(output) bytes. At the *primitive* level, pointer-chasing arguments imply one-sided traversal of a remote structure of depth $d$ needs $\Omega(d)$ round trips — a communication-complexity-style bound. No tight lower bound jointly captures rounds-and-bytes under one-sided-verb + bounded-registered-memory constraints.

## 6. The Gap

Theory (MPC/AGM/WCOJ) gives tight single-round bounds in an *abstract* cost model that counts only bytes/rounds and ignores one-sided-verb semantics, registered-memory caps, queue-pair limits, and the CPU-bypass asymmetry. Systems achieve excellent throughput but optimize empirically. The gap is the **absence of a model that is both tight and RDMA-faithful**: e.g., no proven optimal trade-off curve between rounds (one-sided pulls) and bytes (pushes) under pinned-memory limits. Hence **partially-solved**: clean theory exists for an idealized network; practice wins benchmarks; the two are not reconciled by a matching lower bound in the realistic model.

## 7. Current Research (as of June 2026)

- Joins over **SmartNIC / DPU offload** and programmable switches, moving partitioning into the network *(frontier — verify)*.
- Reconciling **WCOJ with distributed/RDMA execution** for cyclic queries (graph patterns) at scale *(frontier — verify)*.
- Memory-disaggregation joins (CXL + RDMA pooled memory). Active groups: ETH Zürich (Alonso), TU Darmstadt/Brown (Binnig), TUM, University of Washington (Suciu/Koutris theory lineage, now also Wisconsin).

## 8. Future Work

- A tight rounds-vs-bytes lower bound under one-sided verbs and bounded registered memory.
- WCOJ-optimal distributed multiway joins minimizing both AGM-bytes and round trips.
- Skew-robust RDMA joins with provable guarantees, not just empirical flow-join heuristics.
- Network-offloaded join primitives with cost models.

## 9. Key References

- **[Foundational]** Beame, Koutris, Suciu. *Communication Steps for Parallel Query Processing.* PODS, 2013.
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 (JACM 2018).
- **[SOTA]** Barthels, Müller, Schneider, Alonso, Hoefler. *Distributed Join Algorithms on Thousands of Cores.* VLDB, 2017.
- **[SOTA]** Rödiger, Idicula, Kemper, Neumann. *Flow-Join: Adaptive Skew Handling for Distributed Joins over High-Speed Networks.* ICDE, 2016.
- **[Foundational]** Dragojević, Narayanan, Castro, Hodson. *FaRM: Fast Remote Memory.* NSDI, 2014.
- **[Survey]** Atikoglu/Binnig et al. and Zamanian et al. *The End of Slow Networks: It's Time for a Redesign.* VLDB, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
