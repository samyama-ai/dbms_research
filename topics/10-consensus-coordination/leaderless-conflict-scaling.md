---
id: 10-consensus-coordination/leaderless-conflict-scaling
title: "Leaderless Consensus Conflict Scaling"
topic: 10-consensus-coordination
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Leaderless Consensus Conflict Scaling

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/leaderless-conflict-scaling` · **Status:** partially-solved

## 1. Problem Statement
Leaderless consensus protocols (EPaxos, Caesar, Atlas, Tempo) let any replica propose commands and commit non-conflicting commands in one wide-area round trip. Commands that *conflict* (operate on overlapping keys and at least one writes) must be ordered relative to each other; this is captured by attaching a **dependency set** to each command and committing a partial order rather than a total order. The problem: *characterize how commit latency, the slow-path frequency, and execution-time throughput degrade as the conflict rate $\gamma$ (probability that two concurrent commands conflict) rises.*

Variants: (a) **latency/decision** — expected number of message rounds to commit as a function of $\gamma$ and concurrency; (b) **counting** — expected size and longest path of the dependency graph that must be traversed before a command executes; (c) **throughput/optimization** — sustainable command rate before dependency-graph processing (strongly-connected-component detection and linearization) becomes the bottleneck.

## 2. Mathematical Foundations
Each command $c$ carries dependencies $\mathrm{dep}(c)\subseteq C$. The induced **dependency graph** $G=(C,E)$ with $E=\{(c,d): d\in\mathrm{dep}(c)\}$ must be executed in a deterministic order consistent with: (1) the partial order of $E$, and (2) per-SCC tie-breaking by sequence number. Execution requires Tarjan-style SCC decomposition; a command cannot execute until all transitively reachable dependencies are committed and the enclosing SCC is fully formed. If concurrent commands number $k$ and pairwise conflict with probability $\gamma$, the conflict graph is an Erdős–Rényi $G(k,\gamma)$; once $\gamma k > 1$ a **giant component** emerges (phase transition), and expected longest dependency chain (graph diameter) grows, lengthening execution wait. Fast-path correctness requires a fast quorum that guarantees any two coordinators agree on $\mathrm{dep}(c)$; otherwise a **slow path** (extra round + Paxos-style recovery) is taken. Let $p_{\text{slow}}(\gamma)$ be the slow-path probability; EPaxos commits in 1 RTT w.p. $1-p_{\text{slow}}$ and 2 RTT otherwise.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** EPaxos (SOSP 2013) introduced the model. Atlas (EuroSys 2020) shrinks dependencies using $f$-aware fast quorums of size $\lfloor n/2\rfloor + f$, lowering $p_{\text{slow}}$ at small $f$. Tempo (EuroSys 2021) uses timestamp-based ordering to bound dependency tracking and improve tail latency under contention. Caesar (DSN 2017) orders by logical timestamps to reduce slow paths. Accord (Apache Cassandra) brings a leaderless reorder-buffer design to production.
- **Theory-SOTA:** dependency-graph execution is well understood as deterministic topological/SCC linearization; the *scaling law* of latency vs. $\gamma$ is characterized empirically and via random-graph heuristics but lacks a closed-form tight bound.

## 4. Upper Bound
Best-case commit: **1 RTT** (2 message delays) for conflict-free commands from any replica — matching the consensus floor. Worst-case commit on the slow path: **2 RTT** plus dependency-union recovery. Execution latency upper bound is $O(\text{diameter of the committed dependency DAG})$ rounds of waiting; under $G(k,\gamma)$ this is $O(\log k)$ below the giant-component threshold and grows linearly once a giant SCC forms. These hold in **partial synchrony** with $n\ge 2f+1$.

## 5. Lower Bound
Any leaderless protocol must, in the worst case, take $\ge 2$ RTT for some conflicting pair (Lamport's 2-delay learning bound applies to the contended decision). Information-theoretically, distinguishing the order of two concurrent conflicting commands proposed at distinct sites requires at least one extra cross-site round, so $p_{\text{slow}}>0$ whenever $\gamma>0$ and proposers are distributed. SCC detection on the committed graph is inherently sequential along its longest path — a fundamental execution-latency floor tied to graph diameter. No sub-quadratic dependency-tracking scheme is known that preserves single-RTT fast paths at high $\gamma$.

## 6. The Gap
Partially solved: the *no-conflict* regime is optimal and the *high-conflict* regime is understood to degrade toward leader-based or worse. The open gap is a **tight closed-form** linking $\gamma$, concurrency $k$, and $f$ to expected commit latency and execution throughput, including the giant-component transition. Atlas/Tempo narrow but do not close the slow-path cost; whether one can keep $p_{\text{slow}}$ and dependency-graph diameter simultaneously small at high $\gamma$ without reverting to a single sequencer is open.

## 7. Current Research (as of June 2026)
Directions: timestamp/logical-clock ordering to bound dependency sets (Tempo, Accord); workload-aware sharding to keep $\gamma$ low per shard; hybrid leaderless/leadered protocols that switch by measured contention. Groups: CMU (Andersen/Moraru lineage), IMDEA / U. Lisbon (Atlas, Tempo), Apache Cassandra/Accord community. *(frontier — verify)* Recent designs claim bounded dependency growth under skewed/hot-key workloads via adaptive conflict detection, but a proven scaling theorem remains absent.

## 8. Future Work
- A random-graph theorem giving tight expected commit/execution cost vs. $(\gamma,k,f)$.
- Dependency-set compression that survives high contention without slow-path blowup.
- Adaptive protocols that provably interpolate between leaderless and leadered as $\gamma$ varies.
- Execution-engine designs that parallelize SCC linearization to lift the diameter bottleneck.

## 9. Key References
- **[Foundational]** Iulian Moraru, David G. Andersen, Michael Kaminsky. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013. — [ACM](https://dl.acm.org/doi/10.1145/2517349.2517350)
- **[SOTA]** Vitor Enes et al. *State-Machine Replication for Planet-Scale Systems (Atlas).* EuroSys, 2020. — [arXiv](https://arxiv.org/abs/2003.11789)
- **[SOTA]** Vitor Enes et al. *Efficient Replication via Timestamp Stability (Tempo).* EuroSys, 2021. — [arXiv](https://arxiv.org/abs/2104.01142)
- **[SOTA]** Balaji Arun et al. *Speeding up Consensus by Chasing Fast Decisions (Caesar).* DSN, 2017. — [arXiv](https://arxiv.org/abs/1704.03319)
- **[Foundational]** Leslie Lamport. *Generalized Consensus and Paxos.* MSR-TR, 2005. — [MSR](https://www.microsoft.com/en-us/research/publication/generalized-consensus-and-paxos/)

## 10. Worked Example

Take $n=5$ replicas, $f=2$, and $k=4$ concurrent commands $\{a,b,c,d\}$ where each pair conflicts independently with probability $\gamma=0.5$ (e.g. all touch a hot key set). Suppose the realized conflict graph has edges $a\!-\!b$, $b\!-\!c$, $c\!-\!a$, with $d$ isolated. Then $d$ commits and executes immediately (1 RTT, empty deps). But $a,b,c$ form a 3-cycle: each carries the other two in its dependency set, so they create one strongly connected component. The execution engine must wait until all three are committed, run Tarjan SCC detection, and linearize the cycle deterministically by sequence number — say $a<b<c$. Phase-transition check: the giant-component threshold is $\gamma k = 0.5\times4 = 2 > 1$, so a large SCC is expected, matching what we see. Had $\gamma=0.2$, then $\gamma k=0.8<1$ and chains stay short ($O(\log k)\approx 2$), keeping execution latency near the floor.

---
*Part of the [DBMS Research catalog](../../README.md).*
