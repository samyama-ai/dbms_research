---
id: 23-database-security/covert-channel-bounds
title: "Covert Channel Bandwidth Bounds"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Covert Channel Bandwidth Bounds

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/covert-channel-bounds` · **Status:** open

## 1. Problem Statement

A **covert channel** is a communication path not intended for information transfer, exploited to move data across a security boundary that access control believes is sealed. In a DBMS, covert channels arise from *shared, observable state*:

- **Lock/contention channels:** a high transaction holds/releases a lock; a low transaction infers a bit from whether it blocks.
- **Sequence/identifier channels:** a high insert advances a shared sequence/auto-increment or transaction-id counter that a low subject can read.
- **Optimizer-statistics channels:** high inserts change cardinalities/histograms; a low subject infers them from query *plans* or *latencies* (statistics-as-oracle).
- **Storage channels:** disk allocation, free-space, page splits, materialized-view freshness.
- **Timing channels:** buffer-pool hit/miss, cache occupancy.

The problem:

> **(Quantitative)** Compute or *upper-bound* the **capacity** (bits/second) of each channel for a given DBMS design. **(Synthesis)** Modify the system (delays, padding, partitioning, randomization) to drive capacity below a policy threshold $b^\*$ with minimal performance loss. **(Decision)** Does a design admit any channel of capacity $> b^\*$?

Closing channels to *exactly zero* generally requires eliminating sharing; the realistic goal is a *proven bound* and a principled bandwidth/performance trade-off.

## 2. Mathematical Foundations

A covert channel is a noisy communication channel from sender (high) symbol $X$ to receiver (low) observation $Y$ with transition matrix $P(Y\mid X)$. Its **Shannon capacity** is
$$\mathsf{C} = \max_{P(X)} I(X;Y)\quad\text{bits/use},$$
and the rate in bits/second multiplies by uses/second (e.g., lock acquisitions/s). For channels with timing, the **Shannon–Hartley** and queueing-theoretic *timing-channel capacity* (Anantharam–Verdú: capacity of the exponential-server timing channel is $e^{-1}\mu$ nats/s) apply. The TCSEC "Orange Book" criterion famously flags channels above **1 bit/s** and audits those above 0.1 bit/s.

Min-entropy leakage gives a one-shot guarantee:
$$\mathcal{L}_\infty = \log_2 \sum_y \max_x P(y\mid x).$$
Mitigations map to channel transforms: **adding noise/jitter** lowers $I(X;Y)$ (data-processing inequality); **padding to constant time** makes $Y\perp X$ (zero capacity, full performance cost); **quantizing/fuzzing** shared counters and statistics reduces resolution. The optimization is: minimize expected slowdown subject to $\mathsf{C}\le b^\*$ — a constrained information-theoretic control problem.

## 3. State of the Art (SOTA)

- **Foundational analysis:** the **NRL Pump** (Kang, Moskowitz, 1993–96) bounds the timing channel of an upward data pump and quantifies the noise/throughput trade-off analytically. Moskowitz–Kang's work on *quasi-anonymous* and timing channels is canonical.
- **DB-specific:** classic MLS-DB covert-channel analyses of lock managers and the choice of **replicated/kernelized architectures** to avoid cross-level locks (see polyinstantiation). Sequence-number and timestamp channels are well-documented in Trusted Oracle / Sybase Secure.
- **Modern systems:** constant-time programming, cache-partitioning (Intel CAT), and oblivious processing (Opaque, ObliDB) address timing/cache channels; query-plan/statistics channels are addressed ad hoc by per-tenant statistics. Quantitative information-flow tooling (Köpf, Pasareanu, Phan) *measures* leakage of code paths.

## 4. Upper Bound

Channel-closing upper bounds are constructive. **Constant-time / padded** operators give capacity $0$ at a fixed worst-case latency cost. The **Pump** achieves a *tunable* upper bound: by inserting random acknowledgment delays, the upward timing-channel capacity is driven to an arbitrarily small $\varepsilon$ with throughput degrading gracefully (an explicit $\varepsilon$–throughput curve). Partitioning shared counters/statistics per security level yields capacity $0$ for those channels at $O(L)$ state overhead. Quantitative-IF analyzers compute provable *upper bounds* on a given operator's leakage in time polynomial in the program's symbolic path count (worst-case exponential). So for *individual, identified* channels, tight upper bounds and zeroing constructions exist.

## 5. Lower Bound

- **Positivity under sharing:** any *observable contended* shared resource has **strictly positive** capacity unless fully partitioned or padded — an information-theoretic impossibility of free isolation (data-processing inequality bites only if you add noise, which costs performance).
- **Timing-channel floor:** for a shared server of rate $\mu$, the exponential-timing-channel capacity is $\Theta(\mu)$ (Anantharam–Verdú), so a *busy* shared resource leaks at a rate proportional to its throughput — you cannot have both high throughput and zero timing leakage on the *same* shared component.
- **Discovery hardness:** detecting whether an arbitrary system harbors a channel $> b^\*$ reduces to checking quantitative noninterference, a **hyperproperty** — undecidable in general; even for finite models, computing exact channel capacity is intractable (relates to #P-hard counting of distinguishable behaviors).

## 6. The Gap

For *each individually identified* channel we can bound and close capacity; the **open gap** is twofold. (1) **Compositional bounds:** a DBMS exposes many simultaneous channels (locks + sequences + statistics + timing); their *aggregate* capacity is not simply the sum, and there is no accepted framework to certify a *system-wide* bound $\le b^\*$ across all of them at once. (2) **Discovery:** automatically *finding* all exploitable channels in a real engine (especially optimizer-statistics oracles) is unsolved — channels are typically found by audit, not proof. Closing the gap needs compositional capacity accounting plus channel-discovery that is sound (no missed channel), accepting performance trade-offs with provable bounds.

## 7. Current Research (as of June 2026)

- Optimizer/learned-statistics as side channel: leakage from *plan choice* and *cardinality estimates*, including learned-CE models that memorize data *(frontier — verify)*.
- QIF tooling scaling to systems code (symbolic/probabilistic analysis; Phan, Pasareanu, Köpf lineage).
- Microarchitectural channels (Spectre-class) reaching into DB buffer pools and shared TEE workloads; constant-time DB operators.
- Differentially-private release of database statistics/telemetry to cap inference, bridging covert-channel and DP literatures.
- Compositional/quantitative noninterference with mechanized capacity bounds.

## 8. Future Work

- A compositional capacity calculus yielding system-wide DBMS leakage bounds.
- Sound automated discovery of statistics/sequence/lock channels in production engines.
- Provably-bounded "fuzzed" shared sequences and DP-protected optimizer statistics with quantified utility loss.
- Tight capacity results for modern timing channels (NVMe, RDMA, shared caches) in databases.

## 9. Key References

- **[Foundational]** Lampson, B. *A Note on the Confinement Problem.* CACM, 1973. — [DOI](https://doi.org/10.1145/362375.362389)
- **[Foundational]** Kang, M., Moskowitz, I. *A Pump for Rapid, Reliable, Secure Communication (the NRL Pump).* CCS, 1993. — [DOI](https://doi.org/10.1145/168588.168604)
- **[Foundational]** Anantharam, V., Verdú, S. *Bits Through Queues.* IEEE Trans. Information Theory, 1996. — [DOI](https://doi.org/10.1109/18.481773)
- **[SOTA]** Köpf, B., Basin, D. *An Information-Theoretic Model for Adaptive Side-Channel Attacks.* CCS, 2007. — [DOI](https://doi.org/10.1145/1315245.1315282)
- **[SOTA]** Smith, G. *On the Foundations of Quantitative Information Flow.* FoSSaCS, 2009. — [DOI](https://doi.org/10.1007/978-3-642-00596-1_21)
- **[Survey]** Millen, J. *20 Years of Covert Channel Modeling and Analysis.* IEEE S&P, 1999. — [DOI](https://doi.org/10.1109/SECPRI.1999.766906)

## 10. Worked Example

**A lock-contention channel and its capacity.** A high transaction $H$ encodes one bit per time slot by either holding ($X=1$) or not holding ($X=0$) a lock on row $r$. A low transaction $L$ probes $r$ and observes "blocked" ($Y=1$) or "free" ($Y=0$). Suppose the channel is noisy: with probability $p=0.1$ the observation flips (e.g. $L$'s probe races and misreads).

This is a **binary symmetric channel** with crossover $p=0.1$. Its per-use capacity is
$$\mathsf{C}=1-H_2(p)=1-\big(-0.1\log_2 0.1-0.9\log_2 0.9\big)=1-0.469=0.531\ \text{bits/use}.$$
If $L$ can probe the lock $200$ times per second, the raw covert bandwidth is
$$0.531 \times 200 \approx 106\ \text{bits/s}.$$
Under the TCSEC "1 bit/s" auditing threshold $b^\*$, this channel is wildly out of bounds. To drive it below $b^\*=1$ bit/s without partitioning, the system can inject random delay so probes succeed only $\sim$ once/s, or add noise raising $p$ toward $0.5$ (where $H_2(p)\to 1$ and $\mathsf{C}\to 0$) — each lowering $I(X;Y)$ by the data-processing inequality, at a measurable throughput cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
