# Witness/Flexible Replica Cost Models

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/witness-replica-cost` · **Status:** partially-solved

## 1. Problem Statement

Classic majority-quorum replication (Paxos/Raft) requires $2f+1$ full replicas — each storing the complete state and log — to tolerate $f$ crash failures. This is expensive: storage, compute, and especially cross-region network cost scale with the number of *full* replicas. **Witness** (or *tiebreaker*) replicas participate in voting but store little or no data; **flexible-quorum** and **learner** designs let some replicas hold state without voting, or vote without holding state.

The problem: **characterize exactly when a witness/learner/flexible configuration reduces cost (storage, $/byte/month, network) without introducing a hidden liveness or durability penalty** — i.e., without secretly shrinking the fault-tolerance margin or creating a window where committed data can be lost. Variants: (a) *decision* — given a target $(f_{\text{crash}}, f_{\text{durability}})$ and a cost model, does a witnessed configuration meet it? (b) *optimization* — minimize expected $ cost subject to a fixed safety/liveness envelope; (c) *counting/feasibility* — enumerate the quorum systems that preserve intersection while minimizing full-replica count.

The subtlety is that witnesses are "cheap" precisely because they store nothing, but that same property means a quorum dominated by witnesses can *acknowledge* a write that survives on too few full replicas — trading visible cost for invisible durability risk.

## 2. Mathematical Foundations

A **quorum system** over node set $N$ is a collection $\mathcal{Q} \subseteq 2^N$ such that any two quorums intersect: $\forall Q_1,Q_2 \in \mathcal{Q}: Q_1 \cap Q_2 \neq \emptyset$. Paxos requires only that **read (leader-election) quorums** $\mathcal{Q}_e$ and **write (replication) quorums** $\mathcal{Q}_r$ satisfy $\forall Q_e \in \mathcal{Q}_e, Q_r \in \mathcal{Q}_r: Q_e \cap Q_r \neq \emptyset$ — the **Flexible Paxos** relaxation (Howard, Malkhi, Spiegelman, 2016): majorities are sufficient but *not necessary*; e.g. $|Q_r| = f+1$ replication quorums with $|Q_e| = n-f$ election quorums intersect.

Witnesses partition $N$ into **full** replicas $F$ (store state) and **witnesses** $W$ (vote only). Safety (intersection) is a property of *voting* membership; **durability** is a separate property: a value is durable only if it persists on enough *full* replicas to survive $f$ crashes. Define $\delta(Q) = |Q \cap F|$, the data-bearing weight of a quorum. The durability invariant is

$$ \forall Q_r \in \mathcal{Q}_r: \; \delta(Q_r) \ge d, $$

for target durability $d$. A configuration is **cost-sound** iff it satisfies intersection *and* $\delta \ge d$ *and* the liveness condition that enough quorums remain available under the assumed failure distribution. The hidden-penalty pitfall is exactly a system that meets intersection but lets $\delta(Q_r) \to 1$.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **Flexible Paxos** (Howard, Malkhi, Spiegelman, OPODIS 2016) decouples election and replication quorums, formalizing when non-majority quorums are safe. **Vertical Paxos** (Lamport, Malkhi, Zhou, PODC 2009) and **Cheap Paxos** (Lamport & Massa, DSN 2004) introduce auxiliary/witness acceptors used only during reconfiguration or failure.
- **Systems-SOTA:** **Spanner** and **CockroachDB** support non-voting replicas (learners) and witness replicas for cost-tuned geo-replication; **Azure/SQL Server Always On** and **MongoDB** arbiters are production witnesses; **PolarDB**, **TiDB** witness replicas reduce cross-AZ storage cost. **DPaxos**, **WPaxos** (Ailijiang et al., 2019) optimize quorum placement for geo-latency and implicitly cost.

## 4. Upper Bound

Flexible Paxos shows the **minimum replication-quorum size can be as small as $f+1$** (vs. majority $\lceil(n+1)/2\rceil$) while preserving safety, provided election quorums grow to $n-f$. With witnesses, you can tolerate $f$ crash failures with $f+1$ *full* replicas plus $f$ witnesses ($2f+1$ voters but only $f+1$ data copies), cutting storage/network to roughly half of full replication while keeping the same crash-fault tolerance — this is the established, provably-safe upper bound on cost reduction for crash faults. Cheap Paxos formalizes that witnesses need only be active during failures, reducing steady-state cost further.

## 5. Lower Bound

- **Intersection floor:** any safe quorum system needs $|Q_e| + |Q_r| > n$, so you cannot shrink *both* below majority; reducing replication-quorum cost forces larger (costlier-to-assemble, less available) election quorums — a conservation law, not a free lunch.
- **Durability floor:** to survive $f$ *simultaneous* full-replica crashes without data loss you need $\ge f+1$ full replicas; no witness count substitutes for data copies. This is an information-theoretic lower bound — witnesses carry no state, so they cannot reconstruct it.
- **Availability penalty:** $n-f$ election quorums mean a *single* extra failure beyond $f$ blocks leader election; the cost saving is paid in reduced availability margin for the election path (a liveness, not safety, cost).

## 6. The Gap

The *safety/durability* side is essentially closed (Flexible Paxos + the durability invariant give necessary and sufficient conditions). The genuinely open part is the **cost-optimization** side: given a concrete cloud pricing model (per-GB storage, per-GB egress, per-AZ/region fees), heterogeneous failure rates, and an SLO, what is the *cost-minimal* full/witness/learner assignment and quorum partition — and is it computable efficiently or NP-hard? No tight characterization or approximation guarantee exists; current systems use hand-tuned heuristics.

## 7. Current Research (as of June 2026)

Active work: cost-aware quorum placement integrating real cloud pricing into replica-configuration optimizers (CockroachDB Labs, TiDB/PingCAP) *(frontier — verify)*; witness replicas backed by cheaper storage tiers and the interaction with erasure-coded logs to bound durability without full copies *(frontier — verify)*; formal verification (TLA+/Ivy) of flexible/witness configurations to rule out hidden-durability bugs (Howard and collaborators). The Lamport/Malkhi line on reconfiguration safety remains the theoretical anchor.

## 8. Future Work

- A complexity classification (P vs NP-hard) and approximation algorithm for cost-minimal witness/learner placement under cloud pricing.
- Unifying erasure coding with witness voting so durability $d$ is met with sub-$(f+1)$ full copies.
- Online/adaptive reconfiguration that retunes the full/witness split as prices and failure rates drift, with proven safety across the transition.
- SLO-aware models that price the *availability* penalty of $n-f$ election quorums explicitly.

## 9. Key References

- **[Foundational]** Leslie Lamport, Dahlia Malkhi, Lidong Zhou. *Vertical Paxos and Primary-Backup Replication.* PODC, 2009. — [ACM](https://dl.acm.org/doi/10.1145/1582716.1582783)
- **[Foundational]** Leslie Lamport, Mike Massa. *Cheap Paxos.* DSN, 2004. — [DBLP](https://dblp.org/rec/conf/dsn/LamportM04.html)
- **[SOTA]** Heidi Howard, Dahlia Malkhi, Alexander Spiegelman. *Flexible Paxos: Quorum Intersection Revisited.* OPODIS, 2016. — [DOI](https://doi.org/10.4230/LIPIcs.OPODIS.2016.25)
- **[SOTA]** Ailidani Ailijiang, Aleksey Charapko, Murat Demirbas, Tevfik Kosar. *WPaxos: Wide Area Network Flexible Consensus.* IEEE TPDS, 2019. — [DOI](https://doi.org/10.1109/TPDS.2019.2929793)
- **[Foundational]** David K. Gifford. *Weighted Voting for Replicated Data.* SOSP, 1979. — [ACM](https://dl.acm.org/doi/10.1145/800215.806583)

## 10. Worked Example

Tolerate $f=1$ crash. Full majority needs $2f+1=3$ full replicas $\{A,B,C\}$, each storing all data — three copies.

**Witnessed alternative:** keep $f+1=2$ full replicas $\{A,B\}$ plus $1$ witness $W$ (votes, stores nothing). Voters $=\{A,B,W\}$, so safety still uses majority-of-3 quorums (size 2), and any two intersect. Data copies drop from 3 to 2 — roughly half the storage/egress.

Check the durability invariant $\delta(Q_r)\ge d$ with target $d=2$. Quorum $\{A,B\}$: $\delta=2$ (both full) — safe. Quorum $\{A,W\}$: $\delta=1$. If a write is acknowledged by $\{A,W\}$ and then $A$ crashes, the value survives on **zero** full replicas — lost, even though the quorum was "valid." This is the hidden-durability pitfall: intersection holds but $\delta(Q_r)\to1$.

Fix via Flexible Paxos: force replication quorums to be exactly $\{A,B\}$ (size $f+1=2$, both full, $\delta=2$) while election quorums grow to $n-f=2$ including $W$. Safety + durability both hold; the price is one less unit of election availability.

---
*Part of the [DBMS Research catalog](../../README.md).*
