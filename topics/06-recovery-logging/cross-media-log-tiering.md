---
id: 06-recovery-logging/cross-media-log-tiering
title: "Cross-media log tiering"
topic: 06-recovery-logging
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cross-media log tiering

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/cross-media-log-tiering` · **Status:** open

## 1. Problem Statement

A modern durability stack spans media with wildly different cost/latency/bandwidth profiles: byte-addressable **persistent memory / NVDIMM** (sub-microsecond, expensive, small), local **NVMe SSD** (tens of microseconds, cheap-per-GB), and **cloud object/log storage** (milliseconds, effectively infinite, cheapest, geo-durable). The problem: **decide which log records live on which tier, and when to migrate them, to jointly optimize (a) commit latency and (b) recovery time** — under capacity and cost budgets.

This is a placement/scheduling problem. The commit path wants the fastest tier for the *durable point*; recovery wants log laid out for fast sequential replay; cost wants cold log on the cheapest tier; geo-durability wants a copy off-box. These objectives conflict.

Variants: (a) *decision* — is there a placement meeting commit-latency SLO $L$, recovery-time SLO $T$, and cost budget $C$? (b) *optimization* — minimize a weighted objective $\alpha\cdot\text{commit-latency} + \beta\cdot\text{recovery-time} + \gamma\cdot\text{cost}$; (c) *online* — make placement/migration decisions without future knowledge.

## 2. Mathematical Foundations

Tiers $1,\dots,m$ have per-byte write latency $\ell_i$, bandwidth $b_i$, capacity $K_i$, and \$/byte $c_i$, with $\ell_1 \le \dots \le \ell_m$ and $c_1 \ge \dots \ge c_m$. A commit becomes durable when its records reach some tier (or quorum of tiers) deemed *stable*. Let recovery scan rate from tier $i$ be $b_i$.

**Commit latency** of transaction $t$ placed on tier set $S_t$ is $\max_{i \in S_t}\ell_i$ (must wait for the slowest required durable copy). **Recovery time** $\approx \sum_i (\text{log bytes on tier } i)/b_i$ plus seek/fetch overhead, since recovery must read the whole relevant log suffix.

The offline optimization is a **constrained assignment / knapsack-flow**: assign each log segment to a tier (or migrate over time) to minimize the weighted objective subject to $\sum$(bytes on $i$) $\le K_i$. With migration over time and a working-set of recent log, it becomes a **caching / k-tier paging** problem; the online version is a **metrical task system** / **online caching with eviction cost**, for which competitive ratios are the natural yardstick. Two-tier caching admits $k$-competitive deterministic and $O(\log k)$-competitive randomized algorithms (Sleator–Tarjan; Fiat et al.); the multi-tier, latency-weighted, geo-durability variant has no tight characterization.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Cloud OLTP systems already tier the log. **Amazon Aurora** (Verbitski et al., SIGMOD 2017) ships only redo log to a quorum of storage nodes (log-as-database), persisting to fast local storage then replicating; **Microsoft Socrates** (Antonopoulos et al., SIGMOD 2019) separates a low-latency "log service" (landing zone on fast storage) from long-term log on cheap storage. **Hyder**, **FoundationDB**, and PM-fronted WALs (e.g., **WAL on NVDIMM, then flush to SSD**) realize 2–3 tier pipelines. **Taurus**, **PolarDB**, and **Neon** (separating WAL "safekeepers" from object-storage page servers) are further points *(frontier — verify)*.
- **Theory-SOTA:** No dedicated theory; closest formal grounding is online caching/paging and tiered-storage cost models. Placement is largely heuristic (recent log hot, old log cold).

## 4. Upper Bound

Best constructive results are systems pipelines: **commit latency at the fastest tier's $\ell_1$** (PM/NVDIMM landing zone, sub-µs) while **cost approaches the cheapest tier's $c_m$** by promptly draining cold log down-tier — achieving near-PM latency at near-cloud cost in the common case. For the online migration sub-problem, treating it as weighted caching gives a **$k$-competitive** deterministic placement (tiers as cache levels) and **$O(\log k)$** randomized, in the metrical-task-system model. Recovery time is bounded by keeping the *recent* (since-last-checkpoint) log on a high-bandwidth tier so replay reads at $b_1$.

## 5. Lower Bound

- **Online competitive lower bound:** any deterministic online tier-placement is $\ge k$-competitive against adversarial access (inherited from paging lower bounds; Sleator–Tarjan); randomized is $\Omega(\log k)$ (Fiat–Karp–Luby–McGeoch–Sleator–Young).
- **Latency floor:** commit cannot be acknowledged before a durable copy lands, so commit latency $\ge \min_{i \in \text{stable tiers}} \ell_i$ — a tier strictly slower than PM cannot beat PM's $\ell_1$ on the critical path (the "no premature ack" durability floor).
- **Recovery floor:** recovery must read $\Omega(\text{bytes of unreplayed log})$ from wherever it sits; placing cold-but-needed log on a slow tier forces a $\text{bytes}/b_m$ penalty (external-memory bandwidth bound).
- No tight problem-specific NP-hardness or fine-grained lower bound is established for the joint objective.

## 6. The Gap

Genuinely open. We have strong *systems* pipelines and borrowed *caching* theory, but no model that jointly captures commit-latency, recovery-time, cost, and geo-durability across $\ge 3$ heterogeneous tiers, nor matching online bounds for it. The gap: is the joint problem just multi-level weighted caching (then $O(\log k)$ randomized closes it), or does the recovery-time coupling (a *batch* read cost, not per-access) and the commit-quorum structure make it strictly harder? Settling that — and giving a workload-parameterized optimal policy — would close it.

## 7. Current Research (as of June 2026)

Active directions: log-as-a-service architectures (Aurora, Socrates, Neon, PolarDB) refining the landing-zone-to-cold pipeline; learned/ML-driven tier placement and migration prediction *(frontier — verify)*; CXL memory as a new tier between PM and SSD reshaping $\{\ell_i\}$ *(frontier — verify)*; serverless OLTP where recovery-time SLOs (cold-start) dominate placement. Groups: AWS/Aurora, Microsoft (Socrates/Azure SQL), CMU-DB, TUM (Leis/Neumann) on tiered storage engines.

## 8. Future Work

- A formal multi-tier model with matching online competitive bounds for the joint commit/recovery/cost objective.
- Recovery-aware placement: lay out log so the expected-replay suffix is always on the highest-bandwidth tier.
- Incorporating geo-durability/quorum as an explicit tier with its own latency and failure-independence.
- Learned migration policies with worst-case (competitive) guardrails.

## 9. Key References

- **[Foundational]** Daniel Sleator, Robert Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** Amos Fiat, Richard Karp, Michael Luby, Lyle McGeoch, Daniel Sleator, Neal Young. *Competitive Paging Algorithms.* J. Algorithms, 1991. — [arXiv](https://arxiv.org/abs/cs/0205038)
- **[SOTA]** Alexandre Verbitski, Anurag Gupta, et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056101)
- **[SOTA]** Panagiotis Antonopoulos, Alex Budovski, et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3314047)
- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)

## 10. Worked Example

Three tiers: PM ($\ell_1=0.5\,\mu s$, $b_1=10\,\text{GB/s}$, $c_1=\$5$/GB, $K_1=8\,\text{GB}$), NVMe ($\ell_2=20\,\mu s$, $b_2=3\,\text{GB/s}$, $c_2=\$0.2$/GB), object store ($\ell_3=10\,\text{ms}$, $b_3=0.5\,\text{GB/s}$, $c_3=\$0.02$/GB). Workload: $40\,\text{GB}$ of log since checkpoint.

**Commit latency.** Land the durable point on PM: commit acks at $\ell_1=0.5\,\mu s$ — beating an NVMe-only design's $20\,\mu s$ by $40\times$. The durability floor $\ge\min_i\ell_i$ is met exactly.

**Recovery.** Keep the recent $8\,\text{GB}$ on PM, drain the cold $32\,\text{GB}$ to object store. Replay time $= 8/10 + 32/0.5 = 0.8 + 64 = 64.8\,s$ — dominated by the slow tier. Instead keeping all $40\,\text{GB}$ on NVMe gives $40/3 \approx 13.3\,s$: recovery-aware placement trades cost for the bandwidth floor $\text{bytes}/b_m$.

**Cost.** PM-only for $40\,\text{GB} = \$200$; tiered ($8$ PM $+ 32$ object) $= \$40.64$ — near-cheapest-tier cost at near-PM commit latency, exposing the recovery-vs-cost tension.

---
*Part of the [DBMS Research catalog](../../README.md).*
