# Weakest Failure Detector for Commit

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/weakest-fd-atomic-commit` · **Status:** partially-solved

## 1. Problem Statement
The **Non-Blocking Atomic Commit (NBAC)** problem asks $n$ processes, each proposing `yes`/`no`, to agree on `commit`/`abort` such that: (Agreement) no two processes decide differently; (Validity) `commit` is decided only if all vote `yes`; (Abort-Validity) if some process votes `no` or any failure occurs, `abort` is permitted; (Termination) every correct process eventually decides. In an asynchronous system, NBAC is unsolvable with crash failures (it subsumes the difficulty of FLP). A **failure detector** is an oracle giving (possibly unreliable) hints about crashes; the question is the *weakest* such oracle — the minimum failure-detection power — that makes NBAC solvable, and how it relates to the weakest detector for consensus, $\Omega$ (eventual leader).

The decision variant: "Is detector $D$ sufficient/necessary for NBAC?" The reduction variant: "Does $D$ emulate $D'$?" The catalog question is whether the NBAC requirement is *strictly stronger* than consensus's, and by exactly what increment.

## 2. Mathematical Foundations
Model: asynchronous message-passing, $n$ processes, up to $t$ crash faults, reliable channels. A failure detector is a function from failure patterns/histories to local oracle outputs (Chandra–Hadzilacos–Toueg formalism). Detector $D$ is **weaker** than $D'$ ($D \preceq D'$) iff an algorithm using $D'$ can emulate $D$. The *weakest detector for problem $P$* is $D_w$ such that $D_w$ solves $P$ and $D_w \preceq D$ for every $D$ that solves $P$.

Key oracles:
- $\Omega$: eventually all correct processes trust one common correct leader — **weakest for consensus** (CHT 1996).
- $\Diamond P$ (eventually perfect), $?P$ (anonymously perfect), $\mathcal{S}$ (strong).
- The **quittable consensus** abstraction and detector $\Psi$ used to characterize NBAC.

Theorem (Guerraoui–Kouznetsov, Delporte-Gallet et al.): the weakest detector for NBAC is $$D_{\text{NBAC}} \;=\; \Omega \,\sqcup\, \mathit{?P} \quad(\text{anti-}\Omega/?P\text{ combination}),$$ i.e. NBAC requires **strictly more** than $\Omega$ — it must additionally detect *whether any failure occurred at all* ($?P$-like power), because Abort-Validity ties the decision to the global failure pattern. Equivalently NBAC $\equiv$ consensus $+$ a fault-sensing component.

## 3. State of the Art (SOTA)
Theory-SOTA: the characterization $\{\Omega, ?P\}$ (or the equivalent "$\Psi$" hierarchy) is established for $t < n$ and refined for the $t=1$ vs $t>1$ regimes, where the necessary fault-detection strength differs (Delporte-Gallet, Fauconnier, Guerraoui; Distributed Computing line of work). Systems-SOTA does not use failure detectors explicitly: production systems (Spanner, CockroachDB, FoundationDB) implement commit via **consensus-replicated** 2PC participants — the coordinator's decision log is Paxos/Raft, sidestepping NBAC's blocking by making the coordinator itself fault-tolerant rather than invoking a fault oracle.

## 4. Upper Bound
NBAC is solvable with $\{\Omega, ?P\}$ in $O(1)$ stable-period message rounds once the leader and fault-sensor stabilize; message complexity $O(n^2)$ per instance. With consensus available as a black box, NBAC reduces to **one consensus instance** over the multiset of votes plus a fault-detection prefix, giving the same round/latency profile as the underlying consensus (e.g. 2 rounds in the common case). Holds in: asynchronous crash model augmented with the named detector.

## 5. Lower Bound
NBAC cannot be solved with $\Omega$ alone: any algorithm must extract $?P$-equivalent information, proved by a partitioning/indistinguishability argument — a run with no failures and a run where one process crashes silently after voting `yes` are indistinguishable to the rest, yet Validity forbids the same decision. Hence $\Omega \prec D_{\text{NBAC}}$ strictly. The base impossibility (no detector, pure async) follows from FLP. Model: asynchronous crash, reliable links.

## 6. The Gap
For the *power-level* characterization the gap is **closed**: NBAC's weakest detector is pinned to $\{\Omega, ?P\}$. What remains open is (a) **quantitative**: the exact message/round overhead the $?P$ component adds beyond consensus under realistic partial synchrony, not just the qualitative ordering; (b) the **Byzantine** analogue, where the weakest-detector framework is far less settled; and (c) reconciling the oracle-theoretic answer with the consensus-replicated-coordinator engineering answer, which never names a detector.

## 7. Current Research (as of June 2026)
Active work refines failure-detector hierarchies for *generalized* commit (k-set agreement commit, partial-order commit) and for crash-recovery models where $?P$ must be made recoverable. Groups: Delporte-Gallet & Fauconnier (IRIF/Paris), Guerraoui & collaborators (EPFL), Raynal (IRISA). A 2025–2026 thread connects weakest-detector results to **deterministic-aborting** commit in blockchain cross-chain settings, asking what oracle replaces $?P$ when participants are mutually distrustful *(frontier — verify)*.

## 8. Future Work
- Tight quantitative overhead of the fault-sensing component under $\Diamond$-synchrony, not just $\preceq$ ordering.
- Weakest-detector characterization for **Byzantine** NBAC and for commit with omission faults.
- Bridging the theory (oracle) and practice (Paxos-coordinator) views into a single cost model that operators can use.
- Detectors for *energy/cost-aware* abort decisions.

## 9. Key References
- **[Foundational]** Chandra, T., Hadzilacos, V., Toueg, S. *The Weakest Failure Detector for Solving Consensus.* JACM, 1996.
- **[Foundational]** Guerraoui, R. *Non-Blocking Atomic Commit in Asynchronous Distributed Systems with Failure Detectors.* Distributed Computing, 2002.
- **[SOTA]** Delporte-Gallet, C., Fauconnier, H., Guerraoui, R., et al. *The Weakest Failure Detectors to Solve Certain Fundamental Problems in Distributed Computing.* PODC, 2004.
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[Survey]** Raynal, M. *Fault-Tolerant Message-Passing Distributed Systems: An Algorithmic Approach.* Springer, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
