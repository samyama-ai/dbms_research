# Deterministic recovery and replay determinism

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/deterministic-recovery-replay` · **Status:** partially-solved
> **Verification note:** Aria's authors are Lu, Yu, Cao, Madden and it appeared at VLDB 2020 (not SIGMOD); the §9 author list and the "SIGMOD-class" tag in §3 have been corrected accordingly.

## 1. Problem Statement
Guarantee that, after a crash, all replicas of a partition reconstruct **bit-identical state** by replaying the same committed log prefix — and that re-execution from a checkpoint plus log yields exactly the state that existed before the crash. This is the foundation of replicated state machines (RSM): if replay is non-deterministic, replicas diverge silently and consensus on the *log* no longer implies consensus on *state*.

- **Decision variant.** Given a transaction program (with UDFs, system calls, ordering choices), decide whether its execution is deterministic given the log — i.e., whether log order uniquely determines state.
- **Construction variant.** Transform an arbitrary transactional workload into an equivalent deterministic one (e.g., Calvin-style pre-ordering) preserving semantics.
- **Verification variant.** Certify, post-recovery, that two replicas reached identical state (e.g., via Merkle/state hash) without full state comparison.

## 2. Mathematical Foundations
An RSM is a deterministic transition function $\delta: S \times C \to S$ over states $S$ and commands $C$; given identical start state $s_0$ and command sequence $c_1\dots c_n$, all replicas reach $s_n = \delta(\dots\delta(s_0,c_1)\dots,c_n)$. **Determinism is the precondition that makes consensus-on-log $\Rightarrow$ consensus-on-state.**

Sources of non-determinism break $\delta$ into a relation: wall-clock reads, `RANDOM()`, hash-map iteration order, floating-point reassociation, concurrent thread interleavings, and external calls. Formally, replay determinism requires that the *effective* input includes every non-logged source, or that such sources are eliminated.

The **deterministic-database** result (Calvin, Thomson–Abadi) reframes this: by sequencing transactions into a total order *before* execution and forbidding non-deterministic constructs, $\delta$ becomes a pure function of the input batch, so replicas need only agree on the order — no two-phase commit of *results* is required. Recovery then reduces to: checkpoint $s_k$ + deterministic replay of log suffix $\Rightarrow s_n$. Correctness rests on **strict serializability** of the predetermined order and on idempotent, side-effect-confined execution.

State-equivalence checking uses Merkle trees: a root hash $h(s)$ collides only with negligible probability, giving an $O(\log |s|)$-comparison certificate of bit-identity.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** Calvin (Thomson et al., SIGMOD 2012) and successors (Aria, VLDB-class deterministic OLTP; FaunaDB) deliver deterministic execution and thus trivial replica recovery. ARIES (Mohan et al., TODS 1992) is the canonical *single-node* recovery algorithm (WAL + redo/undo) guaranteeing repeatable post-crash state. CockroachDB/Spanner replicate via Raft/Paxos over a logical log and rely on deterministic apply (RocksDB write batches). VoltDB requires deterministic stored procedures and crashes on detected non-determinism.
- **Theory-SOTA.** RSM theory (Schneider's 1990 survey) establishes that determinism is necessary and sufficient for replica consistency given consensus on order.

## 4. Upper Bound
For deterministic workloads, recovery is *optimal*: checkpoint interval $\tau$ bounds replay work to $O(\tau)$ log records; state-equality verification is $O(\log|s|)$ via Merkle roots; agreement requires only consensus on order, not on results, avoiding 2PC's $\Omega(\text{rounds})$ on the commit path. ARIES gives provably correct single-node redo/undo recovery in time linear in the active log suffix.

## 5. Lower Bound
If execution admits *any* unlogged non-deterministic input, no replay protocol can guarantee bit-identity — an information-theoretic barrier: the missing entropy cannot be reconstructed from the log. Thus determinism is *necessary*. Detecting non-determinism in arbitrary programs is undecidable in general (reduces to behavioral equivalence / halting-flavored properties), so static guarantees require restricting the language. Consensus on order itself is subject to FLP impossibility under full asynchrony.

## 6. The Gap
"Partially solved": the deterministic-execution paradigm *closes* the problem for workloads that fit its restrictions (declared read/write sets, no ambient non-determinism). The remaining gap is **general-purpose** workloads — arbitrary UDFs, foreign function calls, floating-point, and external side effects — where bit-identity is not guaranteed and non-determinism may be silent. Bridging requires either record-and-replay of all entropy sources (overhead, storage) or sound static analyses that certify determinism for richer languages.

## 7. Current Research (as of June 2026)
Active: deterministic concurrency control beyond Calvin (Aria, Caracal, Lotus) improving throughput while keeping replay determinism *(frontier — verify)*; record/replay for confining non-determinism (floating-point and syscall capture); formal verification of recovery (machine-checked ARIES and Raft-apply proofs, e.g., Verdi/IronFleet lineage from UW/MSR). The Abadi (UMD), Pavlo (CMU), and verification groups (UW, MPI-SWS) are central. *(frontier — verify)* "deterministic UDF sandboxes" reported in 2025 are early-stage.

## 8. Future Work
- Sound, practical static analyses certifying determinism for SQL+UDF languages.
- Low-overhead entropy capture to make legacy workloads replay-deterministic.
- End-to-end machine-checked proofs linking log consensus to bit-identical state.

## 9. Key References
- **[Foundational]** Mohan, Haderle, Lindsay, Pirahesh, Schwarz. *ARIES: A Transaction Recovery Method...* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** Schneider. *Implementing Fault-Tolerant Services Using the State Machine Approach: A Tutorial.* ACM Computing Surveys, 1990. — [DOI](https://doi.org/10.1145/98163.98167)
- **[SOTA]** Thomson, Diamond, Weng, Ren, Shao, Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[SOTA]** Lu, Yu, Cao, Madden. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[SOTA]** Hawblitzel, Howell, Kapritsos, Lorch, Parno, et al. *IronFleet: Proving Practical Distributed Systems Correct.* SOSP, 2015. — [DOI](https://doi.org/10.1145/2815400.2815428)

## 10. Worked Example

Two replicas of a partition apply the same committed log $c_1,c_2,c_3$ from checkpoint $s_0$. With a *deterministic* $\delta$, both compute $s_3=\delta(\delta(\delta(s_0,c_1),c_2),c_3)$ identically — consensus on the log order implies consensus on state.

**Non-determinism breaks it.** Suppose $c_2$ is `UPDATE t SET tag = RANDOM()`. Replica $A$ draws $0.47$, replica $B$ draws $0.91$. Now $s_3^A \ne s_3^B$ despite identical logs — silent divergence. Fix: log the drawn value as effective input, so $c_2$ carries $\text{rand}=0.47$ and both replay it.

**Verification.** After recovery, compare Merkle roots $h(s_3^A)$ and $h(s_3^B)$ rather than full state. If equal, bit-identity holds with collision probability $\le 2^{-256}$; if a single record differs, the mismatch is localized in $O(\log|s|)$ hash comparisons down the tree.

**Recovery cost.** With checkpoint interval $\tau=1000$ records and a crash $300$ records past the last checkpoint, replay touches only the $O(\tau)=300$-record suffix — no result-level 2PC needed, only agreement on order.

---
*Part of the [DBMS Research catalog](../../README.md).*
