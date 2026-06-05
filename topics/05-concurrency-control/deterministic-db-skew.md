# Deterministic DB Throughput Under Skew

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/deterministic-db-skew` · **Status:** empirically-open

## 1. Problem Statement

**Deterministic databases** (Calvin and its descendants) eliminate the cost of distributed agreement *during* execution by agreeing on a total order of transactions *before* execution: every replica deterministically executes the same input batch in the same logical order, so no two-phase commit and no replica divergence is possible. The catch: determinism typically requires knowing each transaction's read/write set in advance and serializing transactions that touch the same key according to the predetermined order. Under **skew** — a small set of *hot* keys touched by a large fraction of transactions (Zipfian access) — that predetermined per-key serialization collapses concurrency: hot-key transactions execute essentially sequentially, and throughput becomes bound by the latency of the hot-key critical section.

The problem: **sustain high committed-transaction throughput in a deterministic database when key access follows a heavy-tailed/skewed distribution.** Variants: the **optimization** form (maximize throughput / minimize makespan of a batch given a contention graph), the **scheduling** form (order/partition transactions within a batch to maximize intra-batch parallelism while preserving the agreed equivalence), and the **decision** form (can a batch of $n$ transactions over a hot set of size $k$ achieve parallelism $p$?).

## 2. Mathematical Foundations

A batch is a set of transactions with read/write sets over keys $K$. Build the **conflict graph** $G$: vertices are transactions, edges join transactions sharing a written key. Deterministic execution must respect a fixed serial order $\prec$ consistent across replicas; two conflicting transactions on the same key must execute in $\prec$-order. The achievable parallelism is governed by the **longest conflict chain** through hot keys: if a hot key $x$ is written by $m$ transactions, those form a path of length $m$, giving a makespan lower bound

$$\text{makespan} \ge \max_{x \in K} (\text{#writers of } x) \quad (\text{the per-key critical path}).$$

Under a Zipfian distribution with skew $\theta$, the expected number of transactions hitting the single hottest key in a batch of size $n$ grows like $n / H_{N,\theta}$ (with $H_{N,\theta}$ the generalized harmonic number), so the hot-key critical path — and hence the serial bottleneck — grows linearly in $n$ as $\theta \to 1$. This is a deterministic analogue of Amdahl's law where the serial fraction is the hot-key chain.

## 3. State of the Art (SOTA)

**Systems-SOTA:** Calvin (Thomson, Diaconu, Abadi et al., SIGMOD 2012) established deterministic execution with pre-ordered locking. Aria (Lu, Yu, Suo, Madden, PVLDB 2020) removes the read/write-set-in-advance requirement via a batch-then-reorder OCC-style commit with deterministic conflict resolution and a *fallback* path for contended batches. Bohm (Faleiro, Abadi, VLDB 2015) gives MVCC-based deterministic execution decoupling lock acquisition. QueCC (Qadah, Sadoghi, Middleware 2018) uses a priority-queue planner/executor split to exploit intra-batch parallelism. Caracal and other deterministic-MVCC works target contention directly. SLOG (Ren et al., PVLDB 2019) tackles geo-distribution.

## 4. Upper Bound

Within a batch, deterministic schedulers achieve parallelism equal to the **width** of the conflict DAG (transactions on disjoint keys run concurrently). Bohm's MVCC layout lets readers of a hot key proceed against an older version while a writer installs the next, lifting read-heavy skew throughput to roughly the per-version chain length rather than the read+write chain length. Aria's deterministic reordering provably executes any conflict-free subset in parallel and bounds the contended residue to a fallback pass — an $O(\text{contended count})$ serial tail. These are RAM/shared-memory systems bounds; the hard serial residue equals the hot-key write chain.

## 5. Lower Bound

The hot-key critical path is a genuine lower bound: any execution equivalent to the agreed serial order must order all writers of a hot key, so for a single hot key written by $m$ transactions the makespan is $\Omega(m \cdot \tau)$ where $\tau$ is per-transaction hot-section time — independent of the number of cores. Under Zipfian $\theta \to 1$ this forces throughput $O(1/\tau)$ on the hottest key regardless of parallelism, an information-flow/critical-path bound, not a complexity-class one. Optimal intra-batch scheduling that minimizes makespan is **NP-hard** in general (it embeds precedence-constrained scheduling / DAG makespan minimization).

## 6. The Gap

**Empirically open.** We have systems (Aria, Bohm, QueCC) that dramatically improve skew throughput in practice, but no tight theory tying achievable deterministic throughput to the skew parameter $\theta$, batch size, and core count. The gap between the hot-key critical-path lower bound and what real schedulers attain (commutativity exploitation, version chains, sub-batching) is not characterized. Whether commutative/abstract-data-type writes can provably break the linear-in-skew barrier is unresolved.

## 7. Current Research (as of June 2026)

Directions: exploiting **operation commutativity** (counters, sets) so hot-key updates need not be totally ordered, and **deterministic MVCC with version-chain pipelining** to overlap hot-key work *(frontier — verify)*. Groups: Abadi (UMD) and the Calvin/SLOG lineage, Sadoghi (UC Davis, QueCC/L-Store/ResilientDB), Madden/Lu (MIT, Aria). There is cross-pollination with smart-contract/blockchain deterministic execution where skew (hot accounts) is the dominant bottleneck.

## 8. Future Work

- A throughput model parameterized by skew $\theta$, batch size, and cores with matching upper/lower bounds.
- Provable gains from commutativity-aware deterministic execution on hot keys.
- Adaptive batch sizing / sub-batching that trades latency for hot-key parallelism with guarantees.
- Determinism without full read/write-set knowledge under skew, beyond Aria's fallback.

## 9. Key References

- **[Foundational]** Thomson, A.; Diaconu, T.; Ren, K.; Shah, P.; Abadi, D.; et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[SOTA]** Faleiro, J.; Abadi, D. *Rethinking Serializable Multiversion Concurrency Control (Bohm).* PVLDB, 2015.
- **[SOTA]** Lu, Y.; Yu, X.; Suo, L.; Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* PVLDB, 2020.
- **[SOTA]** Qadah, T.; Sadoghi, M. *QueCC: A Queue-Oriented, Control-Free Concurrency Architecture.* Middleware, 2018.
- **[SOTA]** Ren, K.; Li, D.; Abadi, D. *SLOG: Serializable, Low-latency, Geo-replicated Transactions.* PVLDB, 2019.
- **[Survey]** Abadi, D.; Faleiro, J. *An Overview of Deterministic Database Systems.* Communications of the ACM, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
