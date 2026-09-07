---
id: 09-replication-consistency/causal-stability-gc
title: "Causal stability and safe garbage collection"
topic: 09-replication-consistency
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Causal stability and safe garbage collection

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/causal-stability-gc` · **Status:** open

## 1. Problem Statement

In causally consistent replicated stores, replicas accumulate **metadata** (version vectors, dependency dots, sequence numbers) and **tombstones** (delete markers needed so that a delayed concurrent update cannot resurrect removed data). This metadata is required only while some not-yet-delivered operation might still depend on it. An update or tombstone becomes **causally stable** once *every* replica has observed it (and everything it depends on), so no future delivered operation can be causally concurrent with it; at that point its dependency metadata can be compacted and tombstones reclaimed.

The problem: **decide, online and as early as possible, which metadata/tombstones are globally stable and safe to garbage-collect, under continuous membership churn, partitions, and crash/recovery**, without ever reclaiming state that a partitioned-then-returning replica still needs (which would break convergence).

Variants: (a) **decision** — given current knowledge, is dot $d$ stable? (b) **optimization** — minimize steady-state metadata/tombstone footprint subject to a liveness target (max delay before reclamation); (c) **membership-robust** — same under a dynamic, possibly unknown replica set.

## 2. Mathematical Foundations

Model each replica $i \in R$ as producing a totally ordered sequence of events; the global execution is a poset under Lamport's **happens-before** $\to$. A version vector $V_i \in \mathbb{N}^{|R|}$ summarizes $i$'s knowledge. An operation tagged with dot $(j,n)$ is **causally stable at $i$** iff $V_k[j] \ge n$ for all $k\in R$ — i.e. it is in the **causal past of every replica's stable cut**.

The reclaimable frontier is a **consistent global snapshot** in the Chandy–Lamport sense; computing it is exactly distributed **stable-property detection** (GHS/Chandy–Lamport vector-clock minimum): the stable cut is $\min_{k} V_k$ componentwise. The hard part is that $\min_k V_k$ must be learned through anti-entropy, and $|R|$ itself changes.

Lower-level: tombstone necessity is governed by the requirement that delete/add be **commutative and convergent** (strong eventual consistency, $\sqcup$-semilattice of states). Reclaiming a tombstone is sound iff no element below it in the join-semilattice can still arrive — a *causal stability* certificate.

$$\text{stable}(d) \iff d \in \textstyle\bigcap_{k\in R}\,\text{causalPast}(V_k).$$

## 3. State of the Art (SOTA)

- **Theory/systems:** Delta-state CRDTs with **causal stability** (Almeida, Shoker, Baquero, 2018) formalize when delta-groups and tombstones can be dropped using a stable-dot computation.
- **Systems:** Riak/Dynamo-style **dotted version vectors** (Preguiça et al., 2010) bound per-key metadata; SwiftCloud and AntidoteDB implement causal-stability-based compaction.
- **Membership-robust:** EBT/causal broadcast with reconfiguration; Roohitavaf et al.'s GentleRain/Cure stable-snapshot timestamps approximate stability with loosely synchronized clocks.

Systems-SOTA diverges from theory-SOTA: production systems use **clock-based** "all updates before time $T$ are stable" heuristics (GentleRain, Cure) that are simple but fragile under clock skew and stragglers; pure causal (clockless) stability is provably safe but slow to advance the frontier.

## 4. Upper Bound

Detecting stability for a dot costs $O(|R|)$ per check given gathered vectors; advancing the global stable cut is a continuous distributed min-computation with $O(|R|^2)$ vector entries gossiped per anti-entropy round in the naive scheme, $O(|R|)$ amortized with hierarchical aggregation. Clock-based schemes (GentleRain) reduce per-message metadata to **$O(1)$ timestamps** but only under bounded skew. These are **message-passing/asynchronous-model** bounds, not tight.

## 5. Lower Bound

Any clockless causal-stability detector needs each replica to learn a lower bound on *every other* replica's progress, giving an $\Omega(|R|)$ metadata floor per stability certificate — matching the causal-metadata lower bounds for partial replication (related catalog problem). Under partitions, **FLP/CAP** imply you cannot *both* keep advancing the stable frontier *and* stay available: a single unreachable replica halts stability progress indefinitely (a liveness, not safety, impossibility). No tight quantitative lower bound is known relating churn rate to unavoidable tombstone footprint.

## 6. The Gap

Safety is well understood; the open gap is **quantitative and dynamic**: (1) no tight bound on minimal tombstone/metadata footprint as a function of churn rate, partition duration distribution, and target reclamation delay; (2) no provably-safe-and-live reconciliation of clock-based fast frontiers with clockless safety under arbitrary skew; (3) handling **unknown/Byzantine membership** (a crashed-forever replica must be evicted to advance, but premature eviction breaks safety). The gap is genuinely open.

## 7. Current Research (as of June 2026)

- Hybrid clock + causal stability that degrades gracefully under skew, building on HLCs and Cure *(frontier — verify)*.
- **Failure-detector-parameterized** GC: pairing stability with $\Diamond P$-style eviction so a permanently dead replica is safely removed (Baquero/Shoker line; INESC-TEC, Nova Lisboa).
- Stability in **partial replication** where most replicas never hold a key (Antidote, SyncFree/LightKone lineage) *(frontier — verify)*.

## 8. Future Work

- A tight churn-vs-footprint lower bound (information-theoretic or communication-complexity).
- Probabilistic/SLA-based GC: reclaim with bounded resurrection probability $\varepsilon$.
- Verified GC: machine-checked proofs that compaction preserves SEC under dynamic membership.
- Coupling GC with anti-entropy bandwidth optimization end-to-end.

## 9. Key References

- **[Foundational]** Wuu, G., Bernstein, A. *Efficient solutions to the replicated log and dictionary problems.* PODC, 1984. — [ACM](https://dl.acm.org/doi/10.1145/800222.806750)
- **[SOTA]** Almeida, P. S., Shoker, A., Baquero, C. *Delta state replicated data types.* JPDC, 2018. — [DOI](https://doi.org/10.1016/j.jpdc.2017.08.003)
- **[Foundational]** Shapiro, M., Preguiça, N., Baquero, C., Zawirski, M. *Conflict-free Replicated Data Types.* SSS, 2011. — [DOI](https://doi.org/10.1007/978-3-642-24550-3_29)
- **[SOTA]** Du, J., Iorgulescu, C., Roy, A., Zwaenepoel, W. *GentleRain: Cheap and scalable causal consistency with physical clocks.* SoCC, 2014. — [ACM](https://dl.acm.org/doi/10.1145/2670979.2670983)
- **[SOTA]** Akkoorath, D. D. et al. *Cure: Strong semantics meets high availability and low latency (Antidote).* ICDCS, 2016. — [DOI](https://doi.org/10.1109/ICDCS.2016.98)
- **[Foundational]** Chandy, K. M., Lamport, L. *Distributed snapshots: determining global states of distributed systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)

## 10. Worked Example

Three replicas $R=\{A,B,C\}$. Replica $A$ writes key $x$, producing dot $(A,1)$; replica $B$ writes the same key, producing $(B,1)$. These two writes are concurrent (neither in the other's causal past). $A$ later deletes $x$, leaving a **tombstone** tagged with dependency on $(A,1)$.

Version vectors after anti-entropy:
- $V_A=[2,1,0]$, $V_B=[1,1,0]$, $V_C=[0,0,0]$ ($C$ partitioned).

Is dot $(A,1)$ stable? Stable iff $V_k[A]\ge 1$ for **all** $k$. But $V_C[A]=0$, so **not stable** — the tombstone for $x$ cannot be reclaimed: if $C$ returns still holding a stale write of $x$, dropping the tombstone could resurrect $x$.

The stable cut is $\min_k V_k = [\min(2,1,0),\,\min(1,1,0),\,0]=[0,0,0]$: nothing is reclaimable while $C$ lags. Once $C$ catches up to $V_C=[2,1,0]$, the cut advances to $[1,1,0]$, certifying $(A,1)$ and $(B,1)$ stable and freeing the tombstone. One straggler stalls the entire frontier — the liveness cost of clockless safety.

---
*Part of the [DBMS Research catalog](../../README.md).*
