---
id: 14-main-memory-db/scalable-concurrency-control
title: "Concurrency Control Without Central Bottleneck"
topic: 14-main-memory-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Concurrency Control Without Central Bottleneck

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/scalable-concurrency-control` · **Status:** partially-solved

## 1. Problem Statement

Design a concurrency-control (CC) protocol for an in-memory transactional engine whose
**committed-transaction throughput scales (near-)linearly** as core count $p$ grows into
the hundreds, **without any global serialization point** — no single shared lock, latch,
counter, or memory location that every transaction must touch and that thus serializes at
the cache-coherence layer.

- **Decision/feasibility variant:** for a given workload (read/write ratio, contention
  level, access skew), does a CC protocol exist whose throughput $\Theta(p)$ for
  $p \to$ many cores?
- **Optimization variant:** maximize throughput / minimize abort rate at fixed isolation
  level (serializability) under contention.

The qualifier **"without a central bottleneck"** is the crux: protocols may be correct
and fast at low core counts yet collapse because of one contended cache line (a global
lock-manager hash bucket, a TSO timestamp counter, a centralized validation structure).
"Solving" means a protocol that is provably free of *workload-independent* shared
hot-spots and degrades gracefully only under *intrinsic* data contention.

## 2. Mathematical Foundations

**Correctness.** Serializability = the transaction schedule is conflict-equivalent to some
serial order; modeled via the **conflict (serialization) graph** being acyclic (Bernstein,
Hadzilacos, Goodman). Snapshot isolation, SSI, and MVCC variants relax/augment this.

**Scalability model.** Treat throughput under the **Universal Scalability Law**:
$X(p) = \frac{p}{1 + \alpha(p-1) + \beta p(p-1)}$, where $\alpha$ is the serial fraction
(contention) and $\beta$ is *coherence/crosstalk*. A "central bottleneck" is any shared
write set making $\beta > 0$, which forces $X(p)$ to *peak and decline*. The goal is
$\alpha,\beta \to 0$ except for intrinsic data conflicts. Amdahl bounds the speedup by the
serial fraction; the central-counter problem is exactly a nonzero serial fraction induced
by the protocol, not the data.

**Conflict lower bound.** Under *inherent* contention — $k$ transactions all writing one
hot record — any correct protocol serializes them, so throughput on that record is
$O(1/\text{conflict latency})$; scalability claims are therefore always conditional on a
low-contention or partitionable workload.

## 3. State of the Art (SOTA)

**Systems SOTA.** **Silo** (Tu, Zheng, Kohler, Liskov, Madden, SOSP 2013) is the landmark:
optimistic CC with **decentralized, epoch-based** commit — no global critical section on
the fast path, scaling to dozens of cores. **Hekaton** (Larson et al., VLDB 2011/2013) uses
optimistic MVCC. **TicToc** (Yu, Pavlo, Sanchez, Devadas, SIGMOD 2016) computes commit
timestamps *data-driven* from accessed tuples, eliminating the global timestamp counter.
**Cicada** (Lim, Kaminsky, Andersen, SIGMOD 2017) is multi-version optimistic with
contention-tuned validation. **MOCC / IC3 / Bamboo** address high-contention robustness.
Partitioned single-thread-per-core engines (**H-Store/VoltDB**) avoid CC entirely within a
partition but suffer under cross-partition transactions and skew.

**Theory SOTA.** Classical serializability theory (Eswaran et al.; BHG) is settled; the
*scalability* question is a systems/architecture frontier with no closed-form optimum.

## 4. Upper Bound

Silo demonstrates near-linear scaling to ~32 cores on low-contention OLTP with **no
fast-path global write**; epoch boundaries are the only coarse synchronization and are
amortized. TicToc and Cicada extend this by removing the shared timestamp counter,
empirically scaling to higher core counts. The achievable upper bound is essentially
$X(p) = \Theta(p)$ for *partitionable / low-conflict* workloads; per the conflict bound,
no protocol exceeds $O(1)$ throughput on a single hot record. So the "upper bound" is
workload-conditional linear scaling, realized in practice but without a closed theorem of
optimality.

## 5. Lower Bound

The dominant lower bounds are architectural/impossibility-flavored rather than classical
complexity:

- **Coherence lower bound:** any memory location written by all $p$ transactions serializes
  at $\Omega(p)$ on the cache-coherence interconnect (each write invalidates others),
  giving $\beta > 0$ in the USL — a genuine wall. Thus *any* global counter/lock makes
  linear scaling impossible.
- **Inherent-conflict bound:** for a workload with a hot record touched by all $p$,
  serializability forces serial execution there ($\Theta(p)$ slowdown) — unavoidable.
- FLP/consensus-style results bound coordination in the distributed/replicated case.

No unconditional lower bound says serializable CC *must* have a central bottleneck on
benign workloads — and indeed Silo/TicToc show it need not — but no protocol is proven
optimal across all contention regimes.

## 6. The Gap

"Partially solved": for **low-contention, partitionable** workloads, decentralized OCC
(Silo/TicToc/Cicada) effectively achieves linear scaling with no protocol-induced
bottleneck. The **open** part is **high-contention** and **skewed** workloads, where every
known protocol either thrashes (aborts) or reintroduces a serialization point. There is no
protocol that is provably bottleneck-free *and* robust under contention, nor a tight
characterization of the achievable throughput frontier as a function of the contention
parameter. Closing it needs either a contention-robust decentralized protocol with proven
scaling, or an impossibility result delimiting it.

## 7. Current Research (as of June 2026)

Active: **contention-aware / hybrid** CC that switches between OCC, 2PL, and deterministic
execution per partition (Bamboo, Polyjuice — learned CC) *(frontier — verify)*;
**deterministic** databases (Calvin lineage, Abadi) that pre-order transactions to remove
runtime coordination; CC for **disaggregated/CXL** and many-core (100s of cores) hardware;
learned/RL-tuned protocol selection. Groups: MIT (Madden, Devadas — Silo/TicToc), CMU-DB
(Pavlo — Cicada/Bamboo), Yale (Abadi — deterministic/Calvin), Tsinghua/HKUST on Polyjuice.

## 8. Future Work

- A decentralized serializable protocol provably robust under high contention and skew.
- Tight throughput-vs-contention frontier characterization (matching upper/lower bounds).
- CC co-designed with timestamp allocation (see companion problem) and version GC.
- Hardware-assisted (HTM, RDMA, CXL atomics) bottleneck-free commit.

## 9. Key References

- **[Foundational]** P. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/db/books/dbtext/bernstein87.html)
- **[SOTA]** S. Tu, W. Zheng, E. Kohler, B. Liskov, S. Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** X. Yu, A. Pavlo, D. Sanchez, S. Devadas. *TicToc: Time Traveling Optimistic Concurrency Control.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2882935)
- **[SOTA]** H. Lim, M. Kaminsky, D. Andersen. *Cicada: Dependably Fast Multi-Core In-Memory Transactions.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064015)
- **[Survey]** X. Yu, G. Bezerra, A. Pavlo, S. Devadas, M. Stonebraker. *Staring into the Abyss: An Evaluation of Concurrency Control with One Thousand Cores.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735511)

## 10. Worked Example

Apply the Universal Scalability Law to quantify a central bottleneck. Suppose a protocol
has serial fraction $\alpha = 0.02$ and the *global timestamp counter* contributes coherence
crosstalk $\beta = 0.0005$. Then

$$X(p) = \frac{p}{1 + \alpha(p-1) + \beta\, p(p-1)}.$$

At $p = 64$: denominator $= 1 + 0.02(63) + 0.0005(64)(63) = 1 + 1.26 + 2.016 = 4.276$, so
$X \approx 14.97\times$. The peak is at $p^* \approx \sqrt{(1-\alpha)/\beta} = \sqrt{0.98/0.0005}
\approx 44$ cores; beyond that, throughput *declines*. Removing the shared counter (TicToc's
data-driven timestamps) drives $\beta \to 0$, giving $X(64) = 64/(1+1.26) \approx 28.3\times$
— nearly double, and now monotonically increasing.

This is the crux: the $\beta\,p(p-1)$ term — one cache line written by all cores — is what
makes throughput peak and fall, independent of the actual data contention captured by
$\alpha$. Eliminating protocol-induced shared writes is precisely "no central bottleneck."

---
*Part of the [DBMS Research catalog](../../README.md).*
