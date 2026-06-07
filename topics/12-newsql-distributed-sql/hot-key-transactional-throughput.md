---
id: 12-newsql-distributed-sql/hot-key-transactional-throughput
title: "Transactional throughput under skewed hot keys"
topic: 12-newsql-distributed-sql
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Transactional throughput under skewed hot keys

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/hot-key-transactional-throughput` · **Status:** empirically-open

## 1. Problem Statement

Given a distributed SQL database that guarantees **serializability** (or strict
serializability), and a transactional workload whose access pattern is **skewed** — a
small set $H$ of "hot" keys receives a $\Theta(1)$ fraction of all reads and writes —
the problem is to **sustain peak throughput** (committed transactions per second) that
degrades gracefully, rather than collapsing, as skew increases.

- **Optimization variant:** maximize committed throughput $T$ subject to a fixed
  isolation level and a latency SLO, over a workload with Zipfian parameter $s$.
- **Decision variant:** given a target $T^\*$ and skew $s$, decide whether any
  schedule/protocol achieves $\ge T^\*$ without violating serializability.
- **Lower-bound variant:** what is the maximum *contention-bounded* throughput any
  serializable protocol can achieve on a single hot key?

Hot keys arise from auction inventory, popular accounts, sequence/counter rows,
leaderboard aggregates, and reference rows joined by everyone.

## 2. Mathematical Foundations

Model transactions as a set of operations over keys; conflicts induce a
**conflict graph** $G$. Serializability requires the **conflict-serialization graph**
to be acyclic (Eswaran–Gray–Lorie–Traiger). Throughput on a contended key is governed
by the **critical-section length** $L$ (lock-hold or validation-to-commit window):
under a fluid model, max throughput on one key is bounded by $1/L$, the inverse of the
time a writer holds exclusive access. With replication, $L \ge$ one consensus round
($\sim$WAN RTT for cross-region quorums), giving the *replication contention wall*.

Under Zipfian skew with parameter $s$ over $N$ keys, the hottest key absorbs a fraction
$\propto 1/H_{N,s}$ of accesses, where $H_{N,s}=\sum_{k=1}^{N}k^{-s}$. As $s\to 1^+$
the hot fraction stays $\Theta(1/\ln N)$; for $s>1$ it is $\Theta(1)$, so a single key's
$1/L$ ceiling caps the *whole system*. This is the structural reason single-key
contention, not aggregate CPU, sets the limit.

Commutativity helps: if hot-key updates are over a **commutative/abelian** structure
(counters, CRDT-like increments, escrow on a numeric column), conflicts can be relaxed
to **integrity-constraint** checks (escrow/fragmented locking, O'Neil 1986), raising the
ceiling toward $1/\ell$ for a much smaller per-op latch $\ell \ll L$.

## 3. State of the Art (SOTA)

- **Systems SOTA:** Deterministic engines (**Calvin**, Thomson et al., SIGMOD 2012)
  pre-order transactions so hot-key contention costs no extra coordination round; FaunaDB
  and the deterministic line build on this. **Spanner** (OSDI 2012) pays a WAN commit
  round per hot write. **CockroachDB** and **YugabyteDB** mitigate via leaseholder
  locality, write pipelining, and (Cockroach) *unreplicated locks*. **TiDB** uses
  percolator-style optimistic + pessimistic modes.
- **Contention-specific:** **escrow/phase reconciliation**, *combining* and *batching*
  of hot-row updates, and **deterministic aggregation** of counter increments.
- **Theory SOTA:** contention-bound results for transactional memory and the
  *disjoint-access-parallelism* literature characterize when non-conflicting txns avoid
  shared-memory contention; they transfer to the distributed setting as latency floors.

## 4. Upper Bound

For a single serializable hot key under replication, achievable throughput is
$\Theta(1/L)$ where $L$ is the commit-coordination latency; deterministic ordering makes
$L$ a *batch* epoch rather than per-txn (amortizing the round across a batch of $B$
hot-key txns, yielding $\Theta(B/L_{\text{epoch}})$). With commutative escrow on a numeric
hot column the bound improves to $\Theta(1/\ell)$, latch-bounded and independent of WAN
RTT, *as long as* no integrity threshold is crossed. These are the best general
constructive bounds; all are workload-parametric, not worst-case-free.

## 5. Lower Bound

Any protocol guaranteeing serializability with **real-time/strict** ordering must, for
two conflicting writes to the same key on different replicas, exchange at least one
message — yielding a per-conflict latency $\ge$ one network delay (a CAP/PACELC-style
**latency–consistency** lower bound; Abadi 2012, and the impossibility framing of
Gilbert–Lynch 2002). Hence a single hot key's strict-serializable write throughput is
$O(1/\delta)$ for one-way delay $\delta$ — *no* protocol beats the round-trip wall when
updates do not commute. For commuting updates the bound vanishes, separating the two
regimes. No unconditional super-constant lower bound on *aggregate* skewed throughput
beyond this per-key wall is known.

## 6. The Gap

The per-key latency wall (Section 5) is matched by deterministic batching and escrow
*for restricted operation algebras*. The genuinely open part is the **general SQL** case:
arbitrary read-modify-write transactions touching hot keys with non-commutative logic and
secondary-index/constraint side effects. No protocol is known to approach the
$\Theta(1/L)$ ceiling for general transactions while preserving full SQL semantics, and no
matching lower bound rules it out — it is **empirically open**: systems differ by orders of
magnitude on the same skewed benchmark without a tight theoretical separator.

## 7. Current Research (as of June 2026)

- Adaptive switching between optimistic, pessimistic, and deterministic execution *per
  key* based on observed contention (CockroachDB, TiDB) *(frontier — verify)*.
- **Learned hot-key detection** and pre-emptive splitting/coalescing of ranges; automatic
  promotion of hot rows to deterministic or escrow paths.
- Revisiting **deterministic databases** (Aria, Detock) for contention-oblivious commit;
  Detock's *graph-based* deadlock-free ordering targets exactly cross-shard hot conflicts
  *(frontier — verify)*.
- Hardware-assisted commit (RDMA, programmable switches) to shrink $L$.
Groups: Yale (Abadi), CMU (Pavlo/OtterTune), MIT, and the Cockroach/Yugabyte/TiDB
engineering teams.

## 8. Future Work

- A tight, SQL-general lower bound separating commutative from non-commutative hot-key
  throughput.
- Automatic synthesis of escrow/commutativity certificates from SQL+constraints so the
  engine can *prove* when the cheap path is safe.
- Cost models that let the optimizer choose execution strategy per key under a latency SLO.
- Standard skewed-OLTP benchmarks beyond YCSB-Zipfian and TPC-C district rows.

## 9. Key References

- **[Foundational]** O'Neil, P. *The Escrow Transactional Method.* ACM TODS, 1986. — [DOI](https://doi.org/10.1145/7239.7265)
- **[Foundational]** Eswaran, K., Gray, J., Lorie, R., Traiger, I. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[SOTA]** Thomson, A., Diamond, T., Ren, K., et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[SOTA]** Corbett, J., Dean, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Lu, Y., Yu, X., Cao, L., Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[Survey]** Abadi, D. *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC).* IEEE Computer, 2012. — [DOI](https://doi.org/10.1109/MC.2012.33)

## 10. Worked Example

A leaderboard counter row $x$ is the hot key, with cross-region commit latency $L = 5$ ms per serializable write (one quorum round). Under the fluid model, single-key throughput is capped at $1/L = 1/0.005 = 200$ writes/s — regardless of cluster size.

**Skew effect.** With $N = 10^6$ keys and Zipfian $s = 1.2 > 1$, the hottest key absorbs a $\Theta(1)$ fraction; say $1/H_{N,s} \approx 0.45$. If the workload offers $10{,}000$ writes/s, about $4{,}500$/s target $x$ but only $200$/s can commit — the row caps the **whole system** at $200/0.45 \approx 444$ effective writes/s.

**Escrow path.** If updates are pure increments (commutative), conflicts relax to an integrity check; the per-op latch $\ell = 50\,\mu\text{s}$ replaces $L$. Ceiling rises to $1/\ell = 1/0.00005 = 20{,}000$ writes/s — a $100\times$ gain, valid as long as no constraint (e.g. "count $\ge 0$") threshold is crossed.

**Deterministic batching.** Calvin-style epochs of $B = 100$ hot-key txns amortize one round: $B/L_{\text{epoch}} = 100/0.005 = 20{,}000$/s, matching escrow without requiring commutativity.

---
*Part of the [DBMS Research catalog](../../README.md).*
