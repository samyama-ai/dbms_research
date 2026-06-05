# Optimal Flexible Quorum Systems

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/flexible-quorum-optimality` · **Status:** partially-solved

## 1. Problem Statement
Classical majority quorums require any two quorums to intersect. Flexible Paxos (FPaxos) observed that consensus only needs **phase-1 (leader-election) quorums** $\mathcal{Q}_1$ to intersect **phase-2 (replication) quorums** $\mathcal{Q}_2$ — i.e. $Q_1\cap Q_2\ne\varnothing$ for all $Q_1\in\mathcal{Q}_1, Q_2\in\mathcal{Q}_2$ — but quorums *within* $\mathcal{Q}_2$ need not intersect each other. This decouples read/write (or election/replication) costs, enabling small fast write quorums at the price of large recovery quorums.

The problem: *characterize the full Pareto frontier of $(\,|\mathcal{Q}_2|,\ |\mathcal{Q}_1|,\ \text{fault tolerance},\ \text{expected latency}\,)$ trade-offs under heterogeneous failure probabilities and asymmetric network delays.* Variants: **decision** — given target availability/latency, does a valid quorum system exist? **optimization** — minimize expected commit latency (or maximize availability) subject to the cross-intersection constraint; **counting** — enumerate the Pareto-optimal quorum assignments. Heterogeneity (per-node crash probability $p_i$, per-link delay $D_{ij}$) makes uniform-size majorities suboptimal.

## 2. Mathematical Foundations
Let $\mathcal{Q}_1,\mathcal{Q}_2 \subseteq 2^{[n]}$. FPaxos correctness condition:
$$\forall Q_1\in\mathcal{Q}_1,\ Q_2\in\mathcal{Q}_2:\quad Q_1\cap Q_2\neq\varnothing.$$
A sufficient size rule: $|Q_1|+|Q_2| > n$. Setting $|Q_2|=k$ gives a system tolerating $n-k$ failures on the write path but requiring $|Q_1|\ge n-k+1$ for recovery. **Availability** of a quorum system under independent failures: $A(\mathcal{Q})=\Pr[\exists Q\in\mathcal{Q}: \text{all }i\in Q \text{ alive}]$, a function to maximize over node-failure probabilities $p_i$. The relevant combinatorial objects are **coteries** and the Garcia-Molina–Barbara theory of *dominated* vs *non-dominated* coteries; a non-dominated coterie is Pareto-undominated in availability. Grid quorums achieve $O(\sqrt n)$ quorum size. Latency cost of a coordinator $c$ is the weighted-quorum-radius $\min_{Q}\max_{j\in Q}(D_{cj}+D_{jc})$, coupling the combinatorial choice to geography.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Garcia-Molina & Barbara, *How to Assign Votes in a Distributed System* (JACM 1985), establish coterie domination and non-dominated optimality. Flexible Paxos (Howard, Malkhi, Spiegelman, 2016) generalizes the intersection requirement. Weighted/biased quorums and the "vote assignment" optimization frame heterogeneity.
- **Systems-SOTA:** WPaxos (2019) uses flexible quorums for geo-replication with object stealing. Read-lease and witness-replica designs (e.g. CockroachDB leases, Spanner read replicas, Azure-style witness quorums) exploit asymmetry. WHEAT and other latency-aware quorum systems weight nearby replicas to shrink commit latency.

## 4. Upper Bound
Best-known: any size split with $|Q_1|+|Q_2|>n$ is correct, so write-path latency can be driven to the smallest $|Q_2|$ consistent with desired write-availability — down to $|Q_2| = \lfloor n/2 \rfloor$ paired with $|Q_1|=\lceil n/2\rceil+1$, or asymmetric extremes ($|Q_2|$ small, $|Q_1|$ near $n$). Grid quorums give per-operation $O(\sqrt n)$ size with good load balance. Under heterogeneous $p_i$, the availability-maximizing system is the non-dominated coterie selected by the vote-assignment optimization. Holds in the **partially synchronous** consensus model with the cross-intersection condition.

## 5. Lower Bound
The cross-intersection condition is necessary: if some $Q_1\cap Q_2=\varnothing$, two leaders can commit conflicting values (safety violation). Hence $|Q_1|+|Q_2|\ge n+1$ for threshold quorums, giving a fundamental size trade-off — you cannot shrink both paths below the majority line simultaneously. Garcia-Molina–Barbara show dominated coteries are strictly suboptimal, bounding the achievable availability frontier. Selecting the availability-optimal non-dominated coterie under arbitrary $p_i$ is combinatorially hard in general (exponential coterie space), an enumeration/optimization barrier rather than a latency one.

## 6. The Gap
**Partially solved.** The *correctness* frontier (cross-intersection) is fully characterized, and the homogeneous availability frontier (non-dominated coteries) is classical. The open part is the **joint latency × availability Pareto frontier under heterogeneous $(p_i, D_{ij})$**: no tractable algorithm is known to enumerate or even approximate the full frontier when both per-node failure heterogeneity and asymmetric delays interact, especially combined with leader placement and read leases. Closing the gap means an efficient (or approximation) characterization of Pareto-optimal flexible-quorum assignments over both axes.

## 7. Current Research (as of June 2026)
Directions: latency-aware quorum weighting (WHEAT-style), witness/learner replicas to cheapen quorums, and read-lease geography co-optimized with write quorums. Heather Howard's FPaxos line and geo-Paxos variants (WPaxos, Atlas-style $f$-aware quorums) remain active at Cambridge, SUNY Buffalo, and IMDEA. *(frontier — verify)* Recent work claims near-optimal heterogeneous quorum placement via integer-programming / learned cost models over live latency and failure telemetry, but a tight tractability characterization of the joint frontier is unresolved.

## 8. Future Work
- An efficient algorithm (or hardness proof) for the joint latency/availability Pareto frontier under heterogeneous $(p_i, D_{ij})$.
- Co-optimizing flexible quorums with leader placement, read leases, and reconfiguration.
- Online quorum re-selection that tracks drifting failure rates and delays with safety preserved.
- Extending the theory to weighted/Byzantine quorum systems.

## 9. Key References
- **[Foundational]** Hector Garcia-Molina, Daniel Barbara. *How to Assign Votes in a Distributed System.* JACM, 1985.
- **[SOTA]** Heidi Howard, Dahlia Malkhi, Alexander Spiegelman. *Flexible Paxos: Quorum Intersection Revisited.* OPODIS, 2016.
- **[SOTA]** Ailidani Ailijiang, Aleksey Charapko, Murat Demirbas, Tevfik Kosar. *WPaxos: Wide Area Network Flexible Consensus.* IEEE TPDS, 2019.
- **[Foundational]** David Peleg, Avishai Wool. *The Availability of Quorum Systems.* Information and Computation, 1995.
- **[SOTA]** João Sousa, Alysson Bessani. *Separating the WHEAT from the Chaff: Latency-Aware Quorums.* SRDS, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
