# Timestamp Allocation at Scale

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/scalable-timestamp-allocation` · **Status:** partially-solved

## 1. Problem Statement

Many-core MVCC engines assign each transaction a **timestamp** (begin-ts and/or commit-ts)
that defines its position in the serialization/visibility order. The naive implementation
is a single global monotonic counter incremented with an atomic fetch-and-add (FAA). On a
machine with hundreds of cores, *every* transaction hammering one cache line creates a
**shared-counter scalability wall**: the line ping-pongs across the coherence fabric, and
throughput peaks then declines.

The problem: allocate timestamps that are (a) **monotonic / consistent** enough to order
transactions correctly for the target isolation level (serializable or SI), (b) at a rate
that scales (near-)linearly with cores, (c) without a single contended hot location.

- **Decision variant:** is there an allocator giving correct ordering with $\Theta(p)$
  allocation throughput?
- **Optimization variant:** minimize allocation latency / coherence traffic while
  preserving the ordering guarantee MVCC needs.
- Tension: weaker (e.g., loosely-synchronized or vector) timestamps scale better but may
  permit anomalies or complicate visibility checks.

## 2. Mathematical Foundations

**Ordering requirement.** MVCC needs a relation $\prec$ on transactions such that a reader
with snapshot $ts_r$ sees exactly versions with commit-ts $< ts_r$, and serializability
needs $\prec$ consistent with the conflict order. A **total order** (single counter)
suffices but is stronger than necessary; a **partial order** consistent with real conflicts
is enough — this is the slack the scalable schemes exploit (cf. Lamport clocks / vector
clocks for causal vs. total order).

**Contention model.** A single FAA'd counter is a serialization point: under the Universal
Scalability Law its crosstalk term $\beta > 0$, forcing throughput to peak at
$p^* \approx \sqrt{(1-\alpha)/\beta}$ and decline. The bottleneck is *coherence*: one
cache line written by all cores costs $\Omega(p)$ interconnect transactions per "epoch."

**Hardware clocks.** Synchronized invariant TSC / hardware clocks (and Google's
TrueTime-style bounded-uncertainty clocks) let each core *read* a globally-monotonic value
locally without a shared write — converting a write-contended counter into a read-only
clock with bounded skew $\epsilon$, at the cost of waiting out uncertainty (commit-wait).

## 3. State of the Art (SOTA)

**Systems SOTA.**
- **Batched / epoch-based allocation** (Silo, SOSP 2013): transactions get an *epoch* (a
  coarse global tick advanced periodically) plus a local sequence; only the epoch counter
  is shared and it is touched rarely.
- **Data-driven timestamps** (TicToc, SIGMOD 2016): *no global counter at all* — commit
  timestamps are computed from the read/write set's per-tuple timestamps, eliminating the
  hot location entirely.
- **Decentralized / per-core counters with composition** (Cicada, SIGMOD 2017) use
  per-thread clocks plus a global reference advanced lazily.
- **Hardware-clock timestamps** (HW-TS / TSC-based; "Scalable Timestamp Allocation," and
  spanner-style TrueTime in distributed systems) read a synchronized clock locally.
- Hekaton uses a global atomic counter (fine at its scale); the scalable variants target
  100s of cores.

**Theory SOTA.** Lamport (1978) logical clocks and Fidge/Mattern vector clocks frame
which orderings are necessary; the *scalable allocation* question is a systems frontier.

## 4. Upper Bound

TicToc achieves timestamp ordering with **zero shared-counter traffic** (timestamps are a
function of accessed tuples), so allocation contributes no central bottleneck —
$\Theta(p)$ in principle, bounded only by data contention. Silo's epoch scheme reduces
shared-counter touches to $O(1)$ per epoch ($\sim$ every 40 ms), making per-transaction
amortized counter contention $\to 0$. Hardware-TSC reads are $O(1)$ local with no
coherence write. Thus the practical upper bound is *near-linear allocation throughput* for
these designs, conditional on the visibility logic absorbing the weaker ordering.

## 5. Lower Bound

**Coherence lower bound:** any allocator using one shared, written location serializes at
$\Omega(p)$ coherence transactions, so a *single FAA counter cannot scale linearly* — an
architectural impossibility for that design. **Causality lower bound:** to capture an
arbitrary partial order without a shared counter, vector-clock-style schemes need
$\Omega(p)$ space per timestamp (Charron-Bost: vector clocks of dimension $p$ are necessary
to characterize causality), trading counter contention for timestamp size. **Clock-skew
bound:** hardware-clock schemes must pay commit-wait $\ge 2\epsilon$ to mask uncertainty,
lower-bounding latency by the clock skew. So you cannot simultaneously have a single small
totally-ordered scalar, no shared write, and zero extra latency.

## 6. The Gap

Partially solved: epoch batching (Silo) and data-driven timestamps (TicToc) remove the
single-counter wall for serializable OCC, and hardware clocks help. The remaining gap:
(i) these weaken the ordering (epoch granularity, data-derived order, clock uncertainty),
which complicates *long-running readers*, *external consistency*, and *cross-engine /
distributed* visibility; (ii) no scheme is simultaneously scalar-compact, contention-free,
strongly-monotonic, and skew-free — the lower bounds suggest a genuine trilemma. Closing it
means either a proof of the trilemma or a clock/structure that evades it (e.g., hardware
support for a globally-readable monotonic counter without coherence writes).

## 7. Current Research (as of June 2026)

Active: **hardware-clock and synchronized-TSC** timestamping for many-core and
**disaggregated/CXL** systems where no single node owns the counter *(frontier — verify)*;
hybrid logical clocks (HLC) bridging physical and logical order for HTAP and distributed
MVCC; co-design of timestamp allocation with **version GC watermarks** (the oldest active
timestamp must be cheap to compute too). Groups: CMU-DB (Pavlo — Cicada/timestamp studies),
MIT (Devadas/Madden — TicToc), Yale (Abadi — deterministic ordering avoids the issue),
research on Spanner/TrueTime-style clocks in cloud-native engines.

## 8. Future Work

- Hardware primitive for a globally-monotonic, locally-readable counter without coherence writes.
- A formal trilemma (compactness vs. contention vs. strong monotonicity) or a scheme refuting it.
- Joint allocation + GC-watermark computation that is both scalable and cheap.
- Timestamp schemes for CXL/disaggregated and geo-distributed MVCC with bounded skew.

## 9. Key References

- **[Foundational]** L. Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978.
- **[SOTA]** X. Yu, A. Pavlo, D. Sanchez, S. Devadas. *TicToc: Time Traveling Optimistic Concurrency Control.* SIGMOD, 2016.
- **[SOTA]** S. Tu, W. Zheng, E. Kohler, B. Liskov, S. Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013.
- **[Foundational]** B. Charron-Bost. *Concerning the Size of Logical Clocks in Distributed Systems.* Information Processing Letters, 1991.
- **[SOTA]** J. Corbett et al. *Spanner: Google's Globally-Distributed Database (TrueTime).* OSDI, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
