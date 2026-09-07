---
id: 12-newsql-distributed-sql/determinism-throughput-tradeoff
title: "Determinism vs. throughput tradeoff"
topic: 12-newsql-distributed-sql
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Determinism vs. throughput tradeoff

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/determinism-throughput-tradeoff` · **Status:** open

## 1. Problem Statement

**Deterministic** database systems (Calvin, SLOG, Aria, Caracal) order transactions in a single global sequence *before* execution, so every replica deterministically produces the same result without per-replica agreement on outcomes. This eliminates two-phase commit and simplifies replication, but imposes a global ordering discipline that can serialize otherwise-independent work. **Opportunistic** (non-deterministic) concurrency control (OCC, MVCC, 2PL) lets transactions interleave freely and commit in whatever order they finish, extracting more parallelism but paying for coordination/aborts.

The problem: characterize the **fundamental throughput limits** imposed by determinism versus opportunistic concurrency. Is there an inherent throughput tax for determinism, and if so, how large is it as a function of contention, transaction-class structure, and the need to pre-declare read/write sets?

**Decision variant:** given a workload, decide whether a deterministic schedule can match the throughput of the best opportunistic schedule within factor $\rho$. **Optimization variant:** maximize committed transactions/sec under a determinism constraint. **Structural variant:** characterize workload classes where determinism is throughput-free vs. strictly costly.

## 2. Mathematical Foundations

Model a workload as a stream of transactions, each a set of read/write keys (an access pattern). A schedule is **serializable** if equivalent to some serial order; **deterministic** if the committed order is a fixed function of the input sequence (independent of timing/aborts). The relevant combinatorial object is the **conflict graph** $G$ over a batch: vertices are transactions, edges connect conflicting pairs. Maximum achievable parallelism within a batch relates to a coloring / scheduling of $G$; the critical-path length lower-bounds latency, and the independent-set structure upper-bounds concurrency.

Determinism forces a *fixed* topological order consistent with the global sequence, so the achievable schedule is constrained to linear extensions compatible with the pre-assigned sequence — whereas opportunistic CC may pick *any* serializable order, including ones that finish faster. The gap is governed by how much reordering freedom is worth, formalizable via the difference between the optimal makespan over all serializations and the makespan under a fixed order. Pre-declaration of read/write sets adds a "reconnaissance" cost when sets are data-dependent (the OLLP / dependent-transaction problem in Calvin), modeled as an extra read-only pass.

## 3. State of the Art (SOTA)

- **Calvin** (SIGMOD 2012, Thomson–Abadi): global sequencing layer; no distributed commit; throughput scales with sequencer + lock-acquisition discipline.
- **Aria** (VLDB 2020): deterministic *without* pre-declared read/write sets, using a batch execute-then-reorder/commit scheme; closes much of the pre-declaration gap.
- **Caracal / Bohm / PWV**: deterministic MVCC variants improving intra-batch parallelism.
- **Opportunistic SOTA:** Silo (SOSP 2013) for single-node OCC; Sundial, Cicada, TicToc for high-throughput timestamp-ordered CC. These set the non-deterministic throughput ceiling deterministic systems are measured against.

## 4. Upper Bound

For workloads with **statically knowable** read/write sets and bounded contention, deterministic systems achieve throughput within a constant factor of opportunistic CC (Calvin/Aria empirically match or exceed 2PC-based systems precisely because they skip distributed commit). Aria shows the pre-declaration penalty can be removed for many workloads, giving an upper bound: deterministic throughput $\ge (1-o(1))\times$ opportunistic for low-conflict batches. Under high contention determinism can *win* (fewer aborts), so the "tax" is not uniformly positive — the best-known bound is workload-dependent and currently only empirical for general workloads.

## 5. Lower Bound

There is no tight, general lower bound proving an unavoidable determinism throughput tax — this is what keeps the problem **open**. Partial results: for *data-dependent* transaction sets, any deterministic protocol must either run a reconnaissance pass (extra work) or abort-and-retry on misprediction, giving a provable overhead on adversarial dependent workloads. For high-skew (single hot key) workloads, both deterministic and opportunistic schemes are throughput-bounded by the conflict critical path $\Omega(\text{longest conflict chain})$ — a shared floor, not a separation. A clean separation theorem (a workload where every deterministic scheme is asymptotically slower than some opportunistic scheme, or vice versa) is not established.

## 6. The Gap

The gap is **genuinely open**: we lack a theory predicting, from workload statistics (contention, dependency structure, read/write-set predictability), whether determinism costs or saves throughput, and by how much. Upper bounds are largely empirical; matching lower bounds (an unconditional separation or an equivalence theorem) are missing. Closing it requires (1) a formal model relating reordering freedom to achievable makespan, and (2) lower bounds — possibly fine-grained or communication-complexity-based — showing when pre-ordering provably forfeits parallelism.

## 7. Current Research (as of June 2026)

Active: deterministic MVCC with finer intra-batch parallelism (Caracal lineage); hybrid systems that switch between deterministic and opportunistic execution per partition based on observed contention; and SLOG-style designs that keep determinism's replication benefits while restoring multi-region locality. Abadi's group (UMD), and systems groups at CMU and MIT continue this line *(frontier — verify)*. There is interest in formal complexity-theoretic separations between deterministic and non-deterministic transaction scheduling *(frontier — verify)*.

## 8. Future Work

- A separation or equivalence theorem for deterministic vs. opportunistic throughput.
- Workload classifiers that provably pick the better regime online (with regret bounds).
- Removing reconnaissance cost for dependent transactions with bounded misprediction.
- Co-design with deterministic replication to quantify the end-to-end (commit-free) gain.

## 9. Key References

- **[Foundational]** Thomson, Abadi, et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[Foundational]** Tu, Zheng, et al. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** Lu, Yu, Madden, et al. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[SOTA]** Ren, Li, Abadi. *SLOG: Serializable, Low-latency, Geo-replicated Transactions.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3342263.3342647)
- **[SOTA]** Faleiro, Abadi. *Rethinking serializable multiversion concurrency control (Bohm).* VLDB, 2015. — [DOI](https://doi.org/10.14778/2809974.2809981)
- **[Survey]** Abadi, Faleiro. *An Overview of Deterministic Database Systems.* Communications of the ACM, 2018. — [DOI](https://doi.org/10.1145/3181853)

## 10. Worked Example

Batch of $4$ transactions accessing keys: $T_1\{a\}$, $T_2\{a,b\}$, $T_3\{c\}$, $T_4\{c,d\}$. Conflict graph $G$ has edges $T_1\!-\!T_2$ (share $a$) and $T_3\!-\!T_4$ (share $c$); the two components are independent.

**Opportunistic CC** can run all of $\{T_1\text{ or }T_2\}$ and $\{T_3\text{ or }T_4\}$ in parallel and commit in *any* finish order — makespan $\approx 2$ conflict-serialized steps, picking whichever order finishes first.

**Deterministic** systems fix a global sequence, say $T_1\!<\!T_2\!<\!T_3\!<\!T_4$. The independent components still parallelize (2 lanes), so makespan is also $2$ steps here — determinism is "throughput-free" because the pre-assigned order admits a linear extension matching the optimal schedule.

Now add a hot key: every $T_i$ writes $h$. Then $G$ is a clique, the conflict critical path is $\Omega(4)$, and *both* paradigms are floored at makespan $4$ — a shared bound, not a separation. This illustrates §5: skew gives a common floor, and no clean separation theorem is known.

---
*Part of the [DBMS Research catalog](../../README.md).*
