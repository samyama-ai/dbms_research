---
id: 12-newsql-distributed-sql/geo-si-bounded-aborts
title: "Geo-replicated SI with bounded abort rate"
topic: 12-newsql-distributed-sql
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Geo-replicated SI with bounded abort rate

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/geo-si-bounded-aborts` · **Status:** open

## 1. Problem Statement
Provide snapshot isolation (SI) — or a recognizable strengthening such as serializable SI (SSI) — over data replicated across geographic regions, while giving a *provable* upper bound on the rate of transactions aborted due to cross-region write–write conflicts.

- **Decision variant.** Given a workload, a placement, and a target abort budget $\beta$, decide whether an SI protocol can guarantee abort rate $\le \beta$ under a given fault/latency model.
- **Optimization variant.** Minimize the steady-state abort rate (or maximize goodput) subject to SI correctness and a latency SLO.
- **Counting/analysis variant.** Given an arrival process and conflict graph, compute or bound the expected number of first-committer-wins (FCW) aborts per unit time.

The crux: SI's FCW rule requires that no two concurrent transactions write the same item; detecting this across regions demands either a global ordering authority (latency) or optimistic validation (aborts). The open question is whether one can have *low-latency local commits* and a *worst-case-bounded* abort rate simultaneously, rather than trading one for the other.

## 2. Mathematical Foundations
Model an execution as a set of transactions $T_i$ each with a start timestamp $s_i$ and commit timestamp $c_i$ drawn from a (possibly partial) order. SI requires: each $T_i$ reads from the snapshot as of $s_i$, and for any committed $T_i, T_j$ writing a common item, their $[s,c]$ intervals are disjoint (FCW).

Cahill–Röhm–Fekete characterize SI anomalies via the **dependency serialization graph (DSG)**: SI permits cycles containing two consecutive anti-dependency (rw) edges between concurrent transactions (the "dangerous structure"); SSI aborts to break these. Geo-replication adds a *commit-latency* term: under bounded clock skew $\varepsilon$ and one-way delay $d$, any protocol enforcing a total commit order pays $\Omega(d)$ on the critical path (akin to the CAP/PACELC latency tax).

Abort rate can be modeled with a conflict graph $G=(V,E)$ where $V$ are concurrently active transactions and $E$ are write-conflicting pairs; expected aborts relate to the expected number of edges, $\mathbb{E}[|E|]$, under the arrival process. For Poisson arrivals with rate $\lambda$ and validation window $w \approx d$, conflict probability scales with $\lambda w \cdot p_{\text{collide}}$, giving $\text{aborts} \sim \lambda^2 w \cdot p_{\text{collide}}$ in the small-conflict regime.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** Spanner (Corbett et al., OSDI 2012) gives external consistency via TrueTime, paying commit-wait $\approx 2\varepsilon$; CockroachDB uses HLC + uncertainty intervals; YugabyteDB mirrors Spanner-style design. These offer serializability, not a *bounded* abort guarantee. Calvin (Thomson et al., SIGMOD 2012) avoids aborts via deterministic ordering but sacrifices the SI commit model.
- **Theory-SOTA.** Walter (Sovran et al., SOSP 2011) and *Parallel SI* give SI with local reads. Lazy Replication / COPS-style causal+ systems bound coordination but not SI aborts. Binnig et al.'s distributed-SI analyses quantify abort behavior empirically rather than with closed-form worst-case bounds.

## 4. Upper Bound
With deterministic ordering (Calvin-style), abort rate from write conflicts can be driven to **zero** at the cost of pre-declared read/write sets and a sequencing layer adding $O(d)$ latency. With optimistic geo-SI, best-known bounds are *workload-dependent*: under bounded conflict degree $\Delta$ and validation window $w$, expected aborts are $O(\lambda \Delta w)$. No protocol is known that achieves both single-region-RTT commit latency and a workload-independent abort bound.

## 5. Lower Bound
PACELC / CAP-style impossibility: in the presence of partitions, no SI protocol can be both available and consistent. Absent partitions, enforcing FCW across regions inherits a coordination lower bound — any protocol detecting all cross-region write conflicts must, in the worst case, communicate $\Omega(d)$ on the commit path (a latency lower bound, provable by an indistinguishability/communication argument). Deciding whether a schedule is SI-serializable is tractable, but choosing a placement minimizing conflicts is NP-hard (reduction from graph partitioning; see the placement problem).

## 6. The Gap
The gap is genuinely open: we can get zero aborts with high latency (deterministic) or low latency with unbounded (workload-dependent) aborts (optimistic). No protocol provably interpolates with a *tunable, certified* abort bound at near-local latency. Closing it likely requires either a new commit primitive (e.g., escrow/commutativity-aware SI) or a tight characterization of which workloads admit bounded-abort geo-SI.

## 7. Current Research (as of June 2026)
Active threads: commutativity- and CRDT-aware transaction systems that sidestep write-write conflicts (Bailis et al.'s coordination-avoidance / I-confluence lineage); deterministic databases beyond Calvin (Abadi/Thomson line, e.g., Aria, Caracal *(frontier — verify)*); learned/predictive conflict avoidance that pre-routes conflicting keys to one region. The CMU (Pavlo), MIT/UMD (Abadi), and Berkeley (Hellerstein) groups remain central. *(frontier — verify)* recent work on "bounded-staleness SI with abort SLAs" appears in 2025 VLDB/SIGMOD venues but a closed-form worst-case bound remains unestablished.

## 8. Future Work
- Define an *abort-rate SLA* primitive and prove which isolation/latency points are simultaneously achievable.
- Combine I-confluence analysis with SI to certify conflict-free fragments statically.
- Adaptive home-region assignment with online regret bounds on aborts.

## 9. Key References
- **[Foundational]** Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995. — [DOI](https://doi.org/10.1145/223784.223785)
- **[Foundational]** Cahill, Röhm, Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376690)
- **[SOTA]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Sovran, Power, Aguilera, Li. *Transactional Storage for Geo-replicated Systems (Walter).* SOSP, 2011. — [DOI](https://doi.org/10.1145/2043556.2043592)
- **[SOTA]** Thomson, Diamond, Weng, Ren, Shao, Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[Survey]** Bailis, Davidson, Fekete, Ghodsi, Hellerstein, Stoica. *Highly Available Transactions: Virtues and Limitations.* VLDB, 2014. — [arXiv](https://arxiv.org/abs/1302.0309)

## 10. Worked Example

Two regions, US and EU, each run SI locally and replicate. A "popular product" row $x$ is updated from both. Consider concurrent transactions over a validation window $w \approx d = 80\text{ ms}$ (one-way WAN delay):

- $T_1$ (US): start $s_1 = 0$, writes $x$, commits at $c_1 = 5\text{ ms}$.
- $T_2$ (EU): start $s_2 = 2\text{ ms}$ (snapshot before $T_1$'s commit propagates), writes $x$.

Under **first-committer-wins**, $T_2$'s $[s_2,c_2]$ interval overlaps $T_1$'s and both write $x$, so $T_2$ must **abort**. EU only learns of $T_1$'s commit after $d = 80\text{ ms}$, so every EU write to $x$ launched within that window aborts.

**Abort-rate estimate (Section 2):** with Poisson write arrivals to $x$ at $\lambda = 50\,\text{s}^{-1}$ and collision probability $p_{\text{collide}} = 1$ on a single key, expected aborts $\sim \lambda^2 w \cdot p_{\text{collide}} = 50^2 \times 0.08 = 200\,\text{s}^{-1}$ in the small-conflict regime — illustrating how the $\Omega(d)$ window, not CPU, drives the abort rate.

---
*Part of the [DBMS Research catalog](../../README.md).*
