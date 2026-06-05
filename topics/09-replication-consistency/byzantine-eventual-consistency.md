# Byzantine-tolerant eventual consistency

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/byzantine-eventual-consistency` · **Status:** open

## 1. Problem Statement

Classical CRDTs and anti-entropy protocols assume **crash-only** replicas: they may stall or lose messages, but never lie. In open, federated, or adversarial deployments (collaborative editors with untrusted peers, blockchains/local-first apps, sensor meshes), a replica may be **Byzantine** — it can *equivocate* (send conflicting states to different peers), forge causal metadata (fake version vectors/timestamps to suppress or resurrect updates), inflate counters, or replay deltas.

The problem: **design replicated data types and anti-entropy/reconciliation protocols that still guarantee Strong Eventual Consistency (SEC) among the correct replicas — they converge to the same value once they have seen the same set of *correct* updates — despite up to $f$ equivocating/malicious replicas**, while keeping the metadata and verification overhead bounded.

Variants: (a) **convergence-only** (correct replicas agree, no bound on *which* value beyond admissible ones); (b) **integrity** (a Byzantine node cannot make correct nodes accept an operation a correct client never issued); (c) **accountability** (equivocation is detectable/attributable); (d) the optimization of minimizing crypto/metadata cost per operation.

## 2. Mathematical Foundations

A state-based CRDT is a join-semilattice $(S,\sqcup)$ with monotone updates; SEC holds because $\sqcup$ is commutative/associative/idempotent, so correct replicas that have absorbed the same updates compute the same join. Byzantine faults break the implicit assumption that *the multiset of updates seen is consistent across honest replicas*: equivocation makes a malicious node present different "histories" to different honest peers.

The fix relies on making history **tamper-evident and non-equivocable**. Each operation carries a **hash-chained / Merkle-DAG** identity: an op's dot is $h = H(\text{payload} \,\|\, \text{deps})$, so dependencies form a content-addressed DAG (as in Git, IPFS, and Byzantine causal broadcast). Equivocation becomes a *fork* in a per-author chain — two ops with the same author-sequence but different hashes — which is a publishable **proof of misbehavior** (PeerReview-style accountability).

Key impossibility background: with $n$ replicas, **Byzantine reliable broadcast / agreement** needs $n \ge 3f+1$ for safety+liveness in async (BFT bound). But SEC is weaker than agreement — it forgoes a *total* order — so Byzantine **causal** broadcast (BCB) can give causal SEC with lighter assumptions, the central object of study.

## 3. State of the Art (SOTA)

- **Byzantine causal broadcast for CRDTs:** Kleppmann & Howard, *Byzantine Eventual Consistency and the fundamental limits of resilient replicated systems* (2020) — shows BEC is achievable and characterizes its limits; introduces the framework most current work cites.
- **Practical local-first:** Kleppmann's **secure-scuttlebutt / Automerge** lineage — hash-DAG ops give integrity + equivocation detection; Matrix's event DAG is a deployed Byzantine-ish causal store.
- **Theory-SOTA:** Hash-chained CRDTs with **dependency cones** give SEC among honest replicas without consensus; **$3f+1$** only re-enters if you also want to *bound counter values* (e.g. a Byzantine-tolerant counter cannot be made tight without quorum certification).
- **Systems-SOTA:** Blockchains achieve a strong (totally ordered) form at high cost; the open niche is *coordination-free* BEC matching CRDT performance.

## 4. Upper Bound

With a Merkle-DAG and per-author signatures, integrity and equivocation-detection cost **$O(1)$ signature + $O(\#\text{deps})$ hashes** per op; convergence among honest replicas needs **no extra round trips** (anti-entropy unchanged, just verify-before-merge). Bounded-value objects (counters, sets resistant to inflation) need quorum certificates of size $O(f)$ and $n\ge 3f+1$. Bounds hold in the **asynchronous authenticated message model with collision-resistant hashes and digital signatures**.

## 5. Lower Bound

- **$n \ge 3f+1$** for any object requiring Byzantine *agreement* on a bound/total order (async authenticated model; Bracha/Toueg, Dwork–Lynch–Stockmeyer).
- Without cryptographic authentication, Byzantine causal broadcast is **impossible** for $n \le 3f$ in the relevant models; signatures are necessary to attribute equivocation.
- **Kleppmann–Howard** prove fundamental limits: certain operations (e.g. those needing a global maximum/uniqueness) cannot be made Byzantine-fault-tolerant *and* coordination-free — an impossibility separating "mergeable" from "agreement-needing" semantics.
- FLP still forbids deterministic async termination for the agreement-flavored variants.

## 6. The Gap

SEC-among-honest is solved for **mergeable** datatypes via hash-DAGs; genuinely open: (1) tight characterization of *which* datatype semantics admit coordination-free BEC vs. require $3f+1$ quorums; (2) bounding **metadata growth** of the tamper-evident DAG (GC of a Byzantine causal history — equivocation makes causal stability harder, linking to the GC problem); (3) **Sybil/membership** — most results assume a known $n$; open membership undermines $f$-bounds. The boundary between coordination-free and consensus-requiring BEC is only partially mapped.

## 7. Current Research (as of June 2026)

- Extending Kleppmann–Howard limits to richer transactional/relational CRDTs and to **partial replication** *(frontier — verify)*.
- Accountability-first designs (publishable equivocation proofs, auto-eviction) merging PeerReview with anti-entropy (TU Munich / Cambridge local-first groups).
- Byzantine-robust **delta** CRDTs with bounded DAG growth and verified merge functions *(frontier — verify)*.
- Sybil-resistant open-membership BEC using stake/PKI, bridging blockchain and CRDT communities.

## 8. Future Work

- A full dichotomy theorem: coordination-free-BEC-able vs. agreement-hard datatypes.
- Garbage collection of Byzantine causal histories with safety proofs under equivocation.
- Machine-checked BEC protocols (Coq/Isabelle), extending verified-CRDT efforts.
- Quantitative resilience/overhead tradeoffs (signatures-per-op vs. anomaly exposure).

## 9. Key References

- **[SOTA]** Kleppmann, M., Howard, H. *Byzantine Eventual Consistency and the fundamental limits of resilient replicated systems.* arXiv:2012.00472, 2020.
- **[Foundational]** Shapiro, M., Preguiça, N., Baquero, C., Zawirski, M. *Conflict-free Replicated Data Types.* SSS, 2011.
- **[Foundational]** Bracha, G., Toueg, S. *Asynchronous consensus and broadcast protocols.* JACM, 1985.
- **[Foundational]** Castro, M., Liskov, B. *Practical Byzantine Fault Tolerance.* OSDI, 1999.
- **[SOTA]** Haeberlen, A., Kouznetsov, P., Druschel, P. *PeerReview: practical accountability for distributed systems.* SOSP, 2007.
- **[Survey]** Kleppmann, M., Wiggins, A., van Hardenberg, P., McGranaghan, M. *Local-first software.* Onward!, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
