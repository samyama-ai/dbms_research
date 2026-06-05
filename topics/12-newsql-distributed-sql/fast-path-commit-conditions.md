# Failure-free fast-path commit conditions

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/fast-path-commit-conditions` · **Status:** partially-solved

## 1. Problem Statement

Many consensus and atomic-commit protocols offer a **fast path** that decides in a single round-trip (one message delay to a fast quorum) when conditions are favorable, falling back to a slower path (extra round, leader, or recovery) otherwise. Examples: Fast Paxos, Generalized Paxos, EPaxos's fast quorum, and parallel-commit / one-phase commit in distributed SQL. The problem is to **characterize precisely the conditions under which a one-round-trip fast-path commit is safe** — i.e., guarantees the standard agreement/atomicity and durability properties — versus when it *must* invoke full consensus.

**Decision variant:** given the current configuration (proposers, quorum sizes, observed conflicts), decide whether a value can be fast-path committed safely. **Optimization variant:** maximize the fraction of commits taking the fast path subject to safety. **Bounds variant:** determine the minimal fast-quorum size and the maximal failure/conflict regime for which a single round is provably sufficient.

## 2. Mathematical Foundations

Consider $n$ acceptors with up to $f$ failures. Classic Paxos needs a quorum of $\lceil (n+1)/2 \rceil$ and two phases. The fast path collapses to one phase but requires a **fast quorum** $Q_f$ large enough that any two fast quorums plus any classic quorum intersect in a way that prevents two different values from both looking "chosen." Fast Paxos requires $|Q_f| > \tfrac{2}{3}n$ region constraints (e.g. $Q_f \ge n - \lfloor (n-1)/3 \rfloor$), trading a larger quorum for fewer rounds. Formally, safety holds iff the **quorum intersection** condition is met: for any classic quorum $Q$ and fast quorums $Q_{f1}, Q_{f2}$, $|Q \cap Q_{f1} \cap Q_{f2}| \ge 1$ with the value-recovery rule resolving collisions.

For commit, the fast path is safe in the **failure-free, conflict-free** case: all participants vote yes and no concurrent conflicting transaction exists, so the commit decision is implied without a separate decision round (parallel commit makes the transaction record's status a function of all writes being durably staged). Conflict is modeled via the dependency/interference relation in generalized consensus (EPaxos): non-interfering commands commit on the fast path; interfering ones may need the slow path. The boundary is thus a predicate over (failure count, quorum intersection, command interference).

## 3. State of the Art (SOTA)

- **Fast Paxos** (Lamport, 2006): formalizes the single-round fast path with enlarged fast quorums and collision recovery.
- **Generalized Paxos** (Lamport, 2005) / **EPaxos** (Moraru et al., SOSP 2013): fast path for non-interfering (commutative) commands; leaderless, one round in the conflict-free case.
- **Parallel Commits** (CockroachDB, SIGMOD 2020): one-round-trip distributed commit when all writes stage successfully; recovery reconstructs status on failure.
- **Tapir / Janus / TAPIR-style** (OSDI 2015, etc.): consistency + commit co-design to commit in one round in the common case; **Mencius**, **Caesar** further refine fast-quorum conditions.

## 4. Upper Bound

In the failure-free, conflict-free regime, commit/consensus is achievable in **one** message delay (a single round-trip to a fast quorum) — optimal, since at least one round-trip is necessary to reach any remote acceptor. Fast Paxos commits in 2 message delays total (client→acceptors→learner) versus 3–4 for classic. EPaxos commits non-interfering commands in one round with a fast quorum of size $\approx \lceil 3n/4 \rceil$ region-dependent. Parallel commit achieves one-round commit for transactions whose writes do not conflict and whose participants stay up. These match the per-message-delay lower bound in the favorable case.

## 5. Lower Bound

Fast paths cannot be universal: **Lamport's lower bounds** show that tolerating $f$ failures while committing in one round requires fast quorums strictly larger than majority (roughly $n > 2f$ for classic but $n > 3f$-style constraints for collision-free fast decisions), so you cannot have both a one-round path and minimal quorums. **FLP impossibility** forbids guaranteed termination of a deterministic single-round protocol under asynchrony with one failure — hence a fallback path is mandatory. For commit, the **non-blocking atomic commit** lower bound (a single-round failure-free commit must still degrade to extra rounds / a recovery protocol on coordinator failure) is unavoidable. Thus the fast path is provably a *common-case* optimization, never a replacement for consensus.

## 6. The Gap

The *favorable-case* bounds are essentially tight (one message delay, matching the trivial lower bound), so the protocols are optimal where they apply. The **partially-solved** frontier is characterizing the *boundary* precisely: exactly which interference/conflict and failure patterns force the slow path, and how to **maximize fast-path coverage** for real workloads (minimizing collisions in Fast Paxos, dependencies in EPaxos, conflicts in parallel commit). There is no tight general theory predicting fast-path hit-rate from workload structure, nor an optimal quorum-size choice balancing fast-path size against slow-path recovery cost.

## 7. Current Research (as of June 2026)

Directions: reducing EPaxos's dependency-tracking overhead and slow-path frequency under contention (Accord, used in Apache Cassandra's transactions, refines this) *(frontier — verify)*; leaderless commit protocols (Caesar, Tempo, Detock) tightening fast-quorum conditions; and co-designing commit with replication (Tapir/Janus lineage) to widen the fast-path regime. Work on **flexible quorums** (Howard et al.) reframes the quorum-intersection conditions enabling new fast/slow tradeoffs. Production systems (CockroachDB parallel commits, FoundationDB, Cassandra/Accord) report fast-path hit rates *(frontier — verify)*.

## 8. Future Work

- A predictive theory of fast-path hit-rate from workload conflict statistics.
- Optimal fast-quorum sizing balancing common-case latency vs. recovery cost.
- Adaptive protocols that resize fast quorums online as contention shifts.
- Unifying generalized-consensus interference and transaction-conflict definitions.

## 9. Key References

- **[Foundational]** Lamport. *Fast Paxos.* Distributed Computing, 2006. — [DOI](https://doi.org/10.1007/s00446-006-0005-x)
- **[Foundational]** Fischer, Lynch, Paterson. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** Gray, Lamport. *Consensus on Transaction Commit.* ACM TODS, 2006. — [DOI](https://doi.org/10.1145/1132863.1132867)
- **[SOTA]** Moraru, Andersen, Kaminsky. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2517350)
- **[SOTA]** Zhang, et al. *Building Consistent Transactions with Inconsistent Replication (TAPIR).* SOSP/OSDI, 2015. — [DOI](https://doi.org/10.1145/2815400.2815404)
- **[SOTA]** Howard, Malkhi, Spiegelman. *Flexible Paxos: Quorum Intersection Revisited.* OPODIS, 2016. — [DOI](https://doi.org/10.4230/LIPIcs.OPODIS.2016.25)
- **[SOTA]** Taft, et al. *CockroachDB: The Resilient Geo-Distributed SQL Database* (parallel commits). SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3386134)

## 10. Worked Example

Fast Paxos quorum sizing with $n=5$ acceptors. A classic quorum is any majority, $|Q| = 3$. The fast path needs $|Q_f|$ such that two fast quorums and one classic quorum always share an acceptor: $|Q_f| \ge n - \lfloor (n-1)/3 \rfloor = 5 - \lfloor 4/3 \rfloor = 5 - 1 = 4$. So a fast quorum is $4$ of $5$ — larger than the majority of $3$, the price of skipping a round.

Check intersection: any $Q_{f1}, Q_{f2}$ of size $4$ overlap in $\ge 3$ acceptors, and any classic $Q$ of size $3$ meets that overlap in $\ge 3+3-5 = 1$. So no two distinct values can both look chosen — safety holds.

Latency: client $\to$ 4 acceptors $\to$ learner is **2 message delays** versus 4 for classic Paxos (client $\to$ leader $\to$ acceptors $\to$ learner). But if two clients propose concurrently to overlapping-but-not-identical fast quorums, a *collision* occurs and the protocol falls back to the slow path — illustrating why the fast path is a common-case optimization, never a replacement, exactly the FLP-mandated fallback.

---
*Part of the [DBMS Research catalog](../../README.md).*
