---
id: 30-cloud-serverless-db/cold-start-lower-bounds
title: "Provable cold-start lower bounds"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Provable cold-start lower bounds

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/cold-start-lower-bounds` · **Status:** open

## 1. Problem Statement

A serverless database that *scales to zero* releases all compute when idle and must *resume* on the next request. The resume — the **cold start** — incurs latency to re-provision compute, reload working state (buffer pool, catalog, prepared plans, connection state), and reach steady-state throughput. The problem: establish **provable lower bounds** relating the unavoidable cold-start latency $L$ to the resident state size $W$, the storage-fetch bandwidth/latency, and the scale-to-zero idle-cost savings. Formally: for a policy that keeps at most $C$ dollars/sec of warm resources during idle, what is the minimum worst-case resume latency it can guarantee?

Variants: (a) **decision** — can a policy achieve resume latency $\le L$ while keeping idle cost $\le C$? (b) **trade-off curve** — characterize the Pareto frontier of (idle cost, p99 resume latency); (c) **competitive** — online keep-warm vs. scale-down under unknown inter-arrival times.

## 2. Mathematical Foundations

The keep-warm decision is a **rent-or-buy / ski-rental** problem: keeping resources warm costs $c$ per unit idle time; a cold start costs a one-time penalty $P$ (latency monetized, or SLO violation). Against an adversarial idle gap, the classic deterministic ski-rental bound gives a competitive ratio of $2$, and randomized policies achieve $\tfrac{e}{e-1}\approx 1.58$.

The latency floor is information-theoretic. To make $W$ bytes of warm state available, a resuming node must transfer them over a link of bandwidth $B$ and latency $\delta$, giving an unavoidable
$$L \ge \delta + \frac{W_{\text{critical}}}{B},$$
where $W_{\text{critical}}$ is the *minimum* state needed before the first query can make progress (catalog, root index pages, plan cache). No prefetch can beat $\delta$ for the first byte; no compression beats the entropy $H(W_{\text{critical}})$ of the essential state. Snapshot/restore approaches reduce $W_{\text{critical}}$ but cannot drive it to zero while preserving correctness of in-flight transactions.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Aurora Serverless v2 and Neon (separating Postgres compute from a multi-tenant pageserver) resume in single-digit seconds; Neon's architecture (log-structured storage + stateless compute) is the canonical scale-to-zero design. Firecracker microVM snapshotting (NSDI 2020) and CRIU-style restore reduce VM cold start to tens of ms. PlanetScale, CockroachDB Serverless, and Fauna offer scale-to-zero tiers.
- **Theory-SOTA:** the keep-warm scheduling problem is analyzed as ski-rental / TCP-acknowledgment; no DB-specific tight lower bound on resume latency vs. state size is established.

## 4. Upper Bound

Randomized ski-rental gives a keep-warm policy that is $\tfrac{e}{e-1}$-competitive in expected cost against the optimal offline keep-warm schedule. On the latency side, snapshot-restore plus lazy page fault-in achieves resume latency $\approx \delta + W_{\text{critical}}/B$, matching the information floor up to the lazy-loading constant; warm-pool pre-provisioning hides $\delta$ at the price of nonzero idle cost $C>0$.

## 5. Lower Bound

Information-theoretic: $L \ge \delta + H(W_{\text{critical}})/B$ for any correct resume, since the essential state must cross the link. Online: any deterministic keep-warm policy is $\ge 2$-competitive (ski-rental), and any randomized policy is $\ge \tfrac{e}{e-1}$-competitive — both tight. A scale-to-*exactly*-zero policy ($C=0$) cannot guarantee sub-$\delta$ tail latency: there is no free lunch where idle cost is zero *and* resume is instantaneous.

## 6. The Gap

The *online cost* side is closed (ski-rental is tight). The open part is the **DB-specific latency–state–cost trilemma**: a clean theorem stating the minimal $W_{\text{critical}}$ for a transactionally correct resume, and the exact Pareto frontier between idle cost and p99 latency, is not established. Closing it needs a model of which state is genuinely on the critical path versus prefetchable, plus matching constructions.

## 7. Current Research (as of June 2026)

Active work on snapshot/restore (Firecracker, gVisor checkpoint), "keep-warm" prediction from arrival-rate forecasting, and disaggregated-memory resume. Groups: AWS (Firecracker/Aurora), the Neon team, Microsoft Research, and academic serverless groups at UW, Berkeley (RISELab successors), and ETH. *(frontier — verify)* 2025–2026 efforts on CXL far-memory and "snapshot-as-a-service" claim sub-100ms DB resume by keeping warm state in pooled memory rather than re-fetching from object storage.

## 8. Future Work

- A formal characterization of $W_{\text{critical}}$ for ACID resume.
- Learned keep-warm policies with regret bounds under stochastic (not adversarial) arrivals.
- Joint optimization of snapshot granularity, compression, and lazy fault-in.
- Tail-latency SLOs as a first-class constraint in the rent-or-buy formulation.

## 9. Key References

- **[Foundational]** Karlin, Manasse, Rudolph, Sleator. *Competitive Snoopy Caching* / ski-rental analysis. Algorithmica, 1988. — [DOI](https://doi.org/10.1007/BF01762111)
- **[SOTA]** Agache, Brooker, et al. *Firecracker: Lightweight Virtualization for Serverless Applications.* NSDI, 2020. — [USENIX](https://www.usenix.org/conference/nsdi20/presentation/agache)
- **[SOTA]** Brooker, et al. *Aurora Serverless* / *On-demand Container Loading in AWS Lambda.* USENIX ATC, 2023. — [arXiv](https://arxiv.org/abs/2305.13162)
- **[Survey]** Jonas, Schleier-Smith, et al. *Cloud Programming Simplified: A Berkeley View on Serverless Computing.* Tech report, 2019. — [arXiv](https://arxiv.org/abs/1902.03383)
- **[SOTA]** Neon. *Neon: Serverless Postgres — Separation of Storage and Compute.* (project documentation), 2022–2024. — [docs](https://neon.tech/docs/introduction)

## 10. Worked Example

**Latency floor.** Suppose the essential warm state on the critical path is $W_{\text{critical}} = 256$ MB (catalog + root index pages + plan cache), fetched from object storage with first-byte latency $\delta = 30$ ms over a link of bandwidth $B = 1$ GB/s. The information-theoretic floor is

$$L \ge \delta + \frac{W_{\text{critical}}}{B} = 30\ \text{ms} + \frac{256\ \text{MB}}{1024\ \text{MB/s}} = 30 + 250 = 280\ \text{ms}.$$

No prefetch beats the $30$ ms first-byte $\delta$; no compression beats the entropy of the $256$ MB. A warm pool that keeps state resident pays idle cost $C>0$ but hides the $280$ ms.

**Keep-warm cost (ski-rental).** Idle compute costs $c = \$0.0001$/s to keep warm; a cold start costs a monetized penalty $P = \$0.05$ (SLO breach + reload). Break-even idle gap is $P/c = 500$ s. The deterministic $2$-competitive rule keeps the node warm for $500$ s after the last request, then scales to zero. If the true inter-arrival gap is $200$ s we stay warm and avoid the penalty; if gaps are always $10{,}000$ s we waste $\$0.05$ of warm time per idle period before scaling down — at most $2\times$ the offline optimum. Randomized ski-rental tightens this to $\tfrac{e}{e-1}\approx 1.58$.

---
*Part of the [DBMS Research catalog](../../README.md).*
