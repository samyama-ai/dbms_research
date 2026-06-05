# Optimal Tombstone Garbage Collection

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/tombstone-garbage-collection` · **Status:** open

## 1. Problem Statement

In an LSM-tree / log-structured KV store, a delete does not erase data in place; it writes a **tombstone** — a marker that shadows older versions until compaction physically removes both the value and (eventually) the tombstone itself. A tombstone may only be **safely dropped** once it is guaranteed that (a) no surviving older version of the key exists below it in any level, and (b) no reader, replica, or consistency/TTL requirement still depends on observing the delete. Drop too early and a deleted key may "resurrect" (a deleted value reappears, violating correctness); drop too late and tombstones accumulate, inflating space and degrading read/scan latency (the classic Cassandra "tombstone hell").

- **Decision variant:** Given a tombstone $\tau$ for key $k$ at sequence/timestamp $s$, the set of replicas, the consistency level, anti-entropy bounds, and TTLs — is it *safe* to physically purge $\tau$ now?
- **Optimization variant:** Choose, per tombstone, the *earliest* safe purge point to minimize space and scan amplification, subject to never causing resurrection or violating bounded-staleness/TTL semantics.
- **Counting/analysis variant:** Bound the steady-state tombstone population and its contribution to read cost under a given delete rate and purge policy.

"Solving" means a policy that purges each tombstone at (or near) the earliest provably-safe instant under tunable consistency and TTLs.

## 2. Mathematical Foundations

Let keys carry versions with logical timestamps. A tombstone $\tau_k$ at time $t_\tau$ shadows any value $v_k$ with $t_v < t_\tau$. Safe local purge requires that all such older $v_k$ have been compacted away in the same merge — i.e., the merge spans all levels that could hold $k$ (a *full* or *bottommost* compaction), giving local condition $L_{\text{purge}}(\tau)$.

**Distributed safety** is the hard part. Under replication, a delete must propagate to all replicas before its tombstone is dropped, else a lagging replica replays an old value and read-repair resurrects it. The classical safeguard is **gc\_grace** — purge only after a grace period $G \ge \Delta_{\text{anti-entropy}} + \epsilon$, where $\Delta$ bounds hinted-handoff/repair convergence and $\epsilon$ clock skew. This is a *real-time* bound; with logical clocks one instead needs a **stable timestamp** / low-water-mark $\sigma$ such that every replica has applied all writes with $t \le \sigma$ (a distributed snapshot / GC frontier, analogous to garbage collection of MVCC versions below the oldest active read).

TTLs add a deterministic expiry: a key with TTL $\theta$ becomes logically absent at $t_v+\theta$, after which a tombstone is unnecessary — but the *expiry itself* must still be observed consistently. The interaction of *tunable* consistency (R+W vs N) means the safe frontier depends on the **weakest** durability guarantee any reader relies on. Formally this is a **distributed version-GC** problem: compute the maximal set of tombstones below a globally-known safe frontier, which reduces to agreeing on a low-water-mark — a (weak) coordination problem.

## 3. State of the Art (SOTA)

- **Systems SOTA:** Cassandra/ScyllaDB use **gc\_grace\_seconds** + repair: tombstones are droppable only after grace *and* a successful repair, with bottommost-level garbage-collecting compaction and *tombstone compaction* triggers (droppable-tombstone ratio thresholds). RocksDB has `DeleteRange` (range tombstones) and compaction filters; it drops point tombstones at the bottommost level when no snapshot pins them, using the **oldest snapshot sequence number** as the safety frontier. HBase uses major-compaction + KEEP\_DELETED\_CELLS semantics. TTL-driven expiry is handled by per-SSTable min/max timestamp metadata to skip/drop expired data.
- **Theory SOTA:** No dedicated optimality theory; the relevant grounding is MVCC garbage collection (snapshot-based version reclamation), distributed snapshot/low-water-mark computation (Chandy–Lamport lineage), and CRDT delete semantics (tombstone-free or bounded-tombstone CRDTs, e.g., observed-remove sets and their GC).

## 4. Upper Bound

With a globally-known safe frontier $\sigma$ (oldest active snapshot, or replicated low-water-mark), **all** tombstones with $t_\tau \le \sigma$ that have been merged with all older versions can be purged — and this is *optimal* locally: no safe policy can purge earlier without risking resurrection. Computing $\sigma$ costs one round of low-water-mark gossip, $O(N)$ messages for $N$ replicas, amortized over many tombstones. Under TTLs, expired-data dropping is $O(1)$ per SSTable via min/max-timestamp metadata. So given $\sigma$, the purge decision is *tight*; the residual cost is the latency of *learning* $\sigma$.

## 5. Lower Bound

Any safe purge under replication requires knowing that the delete is durable on every replica that could otherwise serve a stale value — this is a distributed-agreement-flavored requirement. **Impossibility flavor:** in an asynchronous system with possible failures, you cannot in bounded time *certify* that a crashed/partitioned replica has seen the delete (FLP-style), so purely time-free safe purge is impossible; gc\_grace trades correctness for a real-time assumption (it can be *wrong* if repair misses the window — a known resurrection bug class). Thus there is an **information-theoretic floor**: safe purge needs either (a) a real-time bound on convergence, or (b) explicit acknowledgment from all relevant replicas ($\Omega(N)$ messages / one barrier). Under tunable consistency with possibly-absent replicas, *no* finite-time policy is both always-safe and always-prompt.

## 6. The Gap

The gap is genuinely open. Locally, the purge condition is tight; **distributively**, current practice (gc\_grace) is a heuristic real-time bound that is neither minimal (often far too conservative, bloating space) nor always safe (resurrection on missed repair). No system computes the *earliest provably-safe* purge point under tunable $(R,W,N)$ + TTL semantics, and there is no characterization of the optimal trade-off between purge promptness and resurrection risk. Closing it requires a formal distributed-GC frontier protocol with proven safety under partial synchrony and an optimality argument against it.

## 7. Current Research (as of June 2026)

- Repair-aware GC: coupling tombstone purge to verified anti-entropy completion (Merkle-tree repair receipts) rather than wall-clock grace. *(frontier — verify)*
- Bounded-/tombstone-free CRDTs (e.g., delta-state ORSWOT, "Causal stability") that GC tombstones once causal stability is reached — bringing principled frontiers from the CRDT community into KV engines. (Baquero, Almeida, Shapiro.)
- Range-tombstone cost modeling and fragmentation control in RocksDB-derived engines.
- Snapshot-frontier coordination in disaggregated / multi-writer KV stores. *(frontier — verify)*
- Groups: HASLab/INESC (Baquero, Almeida — causal stability), Harvard DASlab (LSM cost), and Cassandra/Scylla engineering on tombstone management.

## 8. Future Work

- A provably-minimal, always-safe distributed purge frontier under partial synchrony + tunable consistency.
- Integrating TTL expiry, snapshot pins, and replica durability into one safety predicate.
- Quantified resurrection-risk vs space trade-off (probabilistic safety knobs).
- Causal-stability-based GC adapted to non-CRDT, last-writer-wins KV stores.

## 9. Key References

- **[Foundational]** O'Neil, P. et al. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996.
- **[Foundational]** Chandy, K.M., Lamport, L. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985.
- **[SOTA]** Baquero, C., Almeida, P.S., Shapiro, M. et al. *Making Operation-Based CRDTs Operation-Based / Causal Stability for CRDT GC.* (DAIS / related), 2014.
- **[Foundational]** Shapiro, M., Preguiça, N., Baquero, C., Zawirski, M. *Conflict-Free Replicated Data Types.* SSS, 2011.
- **[Survey]** Luo, C., Carey, M. *LSM-based Storage Techniques: A Survey.* VLDB Journal, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
