# Speculative Execution Rollback Bounds

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/speculative-execution-bounds` · **Status:** empirically-open

## 1. Problem Statement

To hide consensus latency, many replicated systems **execute speculatively**: a replica applies a command (and may reply to the client) *before* agreement is finalized, betting the proposed order will be the committed order. If the bet is wrong — a different value is chosen, the leader changes, or a fast-path quorum is not met — the speculative state must be **rolled back** and re-executed, and any work that *depended* on the speculative result must also unwind, producing a **rollback cascade**.

The problem: **bound the wasted work and the depth/size of rollback cascades as a function of conflict rate, contention, and failure/reordering frequency**, and design protocols that keep that bound small. Variants: (a) *decision* — given a workload and reordering model, is expected wasted work below a threshold? (b) *optimization* — choose speculation policy (how far ahead, what to externalize) minimizing expected wasted work subject to a latency target; (c) *counting* — distribution of cascade depth (number of dependent commands that must re-execute per misspeculation).

The tension: aggressive speculation cuts latency on the common path but, when misspeculation correlates (e.g., a leader change invalidates a whole batch), wasted work and tail latency can explode — and these effects are observed empirically far more than they are bounded theoretically.

## 2. Mathematical Foundations

Model commands as a stream with a **conflict graph** $G=(C,E)$ where $c_i \sim c_j$ if they access overlapping keys non-commutatively. Speculative execution commits to a tentative total order $\hat{\pi}$; the protocol later fixes the true order $\pi$. A command is **misspeculated** if its committed position/value differs from its speculative one. Define the **dependency closure** $\text{dep}^*(c)$: the set of speculatively-executed commands reachable from $c$ in the data-dependency DAG. On misspeculation of $c$, the **rollback set** is $R(c) = \{c\} \cup \{c' : c \in \text{dep}^*(c')\}$ — everyone who *read* $c$'s speculative output.

Wasted work is $W = \sum_{c \text{ misspec}} \text{cost}(R(c))$. If misspeculation is independent with probability $p$ per command and the dependency DAG has branching factor $b$, expected cascade size grows like a **branching process**: $\mathbb{E}[|R(c)|] \approx \sum_{k\ge0}(pb)^k$, which is **finite iff $pb < 1$** and *diverges* (cascade) as $pb \to 1$. This $pb<1$ criticality threshold is the core mathematical object — but real misspeculation is *correlated* (a view change flips a whole prefix), breaking independence and making closed-form bounds elusive.

## 3. State of the Art (SOTA)

- **Theory/protocol-SOTA:** **Generalized Paxos** (Lamport, 2005) and **Egalitarian Paxos / EPaxos** (Moraru, Andersen, Kaminsky, SOSP 2013) commit *commutative* commands out of order, shrinking the conflict set that can trigger rollback. **Speculative Paxos** (Ports, Li, Szekeres, Krishnamurthy, NSDI 2015) and **NOPaxos** (Li et al., OSDI 2016) use the network to make misspeculation rare, so wasted work is empirically tiny — but bounded only under their network-ordering assumptions.
- **Systems-SOTA:** **Zyzzyva** (Kotla et al., SOSP 2007) pioneered speculative BFT with client-driven rollback; **PBFT** tentative execution; **TAPIR** (Ports et al., SOSP 2015) speculates across replication+transaction layers. Deterministic databases (**Calvin**) avoid speculation entirely as a contrast point.

## 4. Upper Bound

Under the independence + commutativity model, EPaxos-style ordering bounds rollback to the **non-commutative conflict component**: only commands in the same conflict-connected component can cascade, so $\mathbb{E}[|R|] = O(1/(1-pb))$ when $pb<1$, and exactly $0$ wasted work for fully-commutative streams. Speculative Paxos shows that with **ordered unreliable multicast**, misspeculation probability $p$ drops to the packet-reorder/drop rate, making expected wasted work $O(p \cdot n)$ — negligible in a well-provisioned datacenter. These are the best constructive guarantees, but each holds only inside its assumed reordering model.

## 5. Lower Bound

- **FLP-adjacent:** in an asynchronous network you cannot avoid *some* speculation window without giving up either liveness or the latency benefit; any non-trivial speedup over the agreement round-trip implies a nonzero misspeculation set in some execution.
- **Adversarial cascade:** for non-commutative workloads, an adversary controlling reordering/view-changes can force $\Omega(L)$ rollback where $L$ is the speculative-prefix length — i.e., a single late-arriving high-priority command can invalidate an entire executed prefix. No protocol bounds worst-case wasted work below the speculation depth without restricting the adversary (network assumptions).
- **No closed-form for correlated faults:** the branching-process bound is information-theoretically tight only under independence; correlated leader-change misspeculation has no matching analytical lower bound — this is precisely why the problem is *empirically-open*.

## 6. The Gap

The independent-misspeculation regime is well-bounded ($pb<1$ criticality). The gap is the **correlated/adversarial regime** that dominates real systems: leader changes, GC pauses, and bursty reordering create heavy-tailed cascade distributions with no tight analytical characterization. We have empirical measurements and per-system network assumptions, but no general theory predicting wasted-work distribution from workload + failure statistics, and no protocol with a *proven* worst-case wasted-work bound under realistic (correlated) faults. Closing it needs a stochastic model of correlated misspeculation with matching upper/lower bounds.

## 7. Current Research (as of June 2026)

Active directions: speculation policies that adaptively throttle how far ahead they execute based on observed misspeculation rate *(frontier — verify)*; integrating commutativity analysis (CRDT/object semantics) to statically prune cascade edges; measurement studies quantifying cascade-depth tails under leader churn in production SMR (CMU-DB, MIT PDOS, UW Syslab lineage) *(frontier — verify)*; speculative BFT revisited for blockchain/rollup settings where reorg depth is the cascade metric. EPaxos derivatives and "tempo"/leaderless designs continue to shrink the conflict surface.

## 8. Future Work

- A stochastic model of *correlated* misspeculation (view changes, bursts) yielding tight tail bounds on cascade depth.
- Protocols with provable worst-case wasted-work bounds under a bounded-adversary reordering model, not just average-case.
- Adaptive speculation depth as a control problem with regret guarantees.
- Cross-layer rollback accounting where speculation spans replication, transactions, and application caches.

## 9. Key References

- **[Foundational]** Ramakrishna Kotla, Lorenzo Alvisi, Mike Dahlin, Allen Clement, Edmund Wong. *Zyzzyva: Speculative Byzantine Fault Tolerance.* SOSP, 2007.
- **[SOTA]** Iulian Moraru, David G. Andersen, Michael Kaminsky. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013.
- **[SOTA]** Dan R. K. Ports, Jialin Li, Vincent Liu, Naveen Kr. Sharma, Arvind Krishnamurthy. *Designing Distributed Systems Using Approximate Synchrony in Data Center Networks (Speculative Paxos).* NSDI, 2015.
- **[SOTA]** Jialin Li, Ellis Michael, Naveen Kr. Sharma, Adriana Szekeres, Dan R. K. Ports. *Just Say NO to Paxos Overhead (NOPaxos).* OSDI, 2016.
- **[Foundational]** Leslie Lamport. *Generalized Consensus and Paxos.* Microsoft Research Technical Report MSR-TR-2005-33, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
