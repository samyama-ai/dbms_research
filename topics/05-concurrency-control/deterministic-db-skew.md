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

- **[Foundational]** Thomson, A.; Diaconu, T.; Ren, K.; Shah, P.; Abadi, D.; et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[SOTA]** Faleiro, J.; Abadi, D. *Rethinking Serializable Multiversion Concurrency Control (Bohm).* PVLDB, 2015. — [arXiv](https://arxiv.org/abs/1412.2324)
- **[SOTA]** Lu, Y.; Yu, X.; Cao, L.; Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* PVLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[SOTA]** Qadah, T.; Sadoghi, M. *QueCC: A Queue-Oriented, Control-Free Concurrency Architecture.* Middleware, 2018. — [DOI](https://doi.org/10.1145/3274808.3274810)
- **[SOTA]** Ren, K.; Li, D.; Abadi, D. *SLOG: Serializable, Low-latency, Geo-replicated Transactions.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3342263.3342647)
- **[Survey]** Abadi, D.; Faleiro, J. *An Overview of Deterministic Database Systems.* Communications of the ACM, 2018. — [DOI](https://doi.org/10.1145/3181853)

## 10. Worked Example

A batch of $n = 8$ transactions runs on a 4-core deterministic engine. Each transaction writes one hot key plus one private key. Suppose 6 of the 8 write the hottest key $x$ and the other 2 write a cold key $y$ each:

- Writers of $x$: $T_1, T_2, T_3, T_4, T_5, T_6$ — must run in $\prec$-order, forming a chain of length 6.
- Writers of $y$: $T_7, T_8$ — independent, run anywhere.

Per-key critical path bound: $\text{makespan} \ge \max_x(\#\text{writers}) = 6$. With per-transaction hot-section time $\tau = 1$ ms, makespan $\ge 6$ ms regardless of cores — adding cores past 1 cannot help the $x$-chain. The 4 cores sit mostly idle: effective parallelism is $8/6 \approx 1.33$, not 4.

**Amdahl analogy.** Serial fraction $f = 6/8 = 0.75$; speedup $\le 1/(f + (1-f)/4) = 1/(0.75 + 0.0625) = 1.23\times$. Under Zipfian $\theta \to 1$ the hottest-key count grows like $n/H_{N,\theta}$, so the chain — and the bottleneck — scales linearly with $n$. Commutative updates (if writes to $x$ were $+1$ counters) could collapse the chain to $O(\log n)$ or $O(1)$, breaking the barrier.

---
*Part of the [DBMS Research catalog](../../README.md).*
