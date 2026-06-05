# Consistency-aware caching at the edge

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/edge-cache-consistency` · **Status:** empirically-open

## 1. Problem Statement

Modern applications interpose **multi-tier caches** between clients and origin stores: browser/SDK caches, CDN/PoP caches, regional edge KV stores (Cloudflare Workers KV/Durable Objects, Fastly, Akamai EdgeWorkers, AWS CloudFront/Lambda@Edge). These tiers are populated by independent fills and TTL expiries, so a client's read path can return values that violate even weak guarantees — e.g. a **read-your-writes** violation when a client writes through one PoP and reads a stale fill at another.

The problem: **provide a *defined* client-observable consistency model — session guarantees (RYW, monotonic reads/writes, writes-follow-reads), causal consistency, or bounded staleness — across a hierarchy of partially-coordinating edge caches, without routing every request through a central coordinator**, while preserving the cache hit-rate / latency benefit that motivates edge caching at all.

Variants: (a) **mechanism** — what minimal token/metadata must travel with a client/request to enforce a target model; (b) **optimization** — maximize hit rate (minimize origin egress / tail latency) subject to a consistency SLA; (c) **measurement/empirical** — characterize anomaly rates of deployed CDN configurations.

## 2. Mathematical Foundations

Model the system as tiers $T_0$ (client) $\prec T_1 \prec \dots \prec T_m$ (origin). Each tier holds a partial map key $\to$ (value, version). Client sessions are sequences of operations; **session guarantees** (Terry et al., 1994) are predicates over the per-session order and the (value,version) returned. RYW: a read in session $s$ must return a version $\ge$ the latest write of $s$; this is enforceable iff the read tier holds a version dominating the session's **write-set vector** $W_s$.

Causal consistency requires returned versions to respect happens-before; enforced via **causal cuts**: a request carries a dependency vector $D$, and a cache may serve a fill only if its stored version's vector $\ge D$ (else miss to next tier). Bounded staleness: serve iff $\text{now} - \text{fill\_time} \le t$ or version-lag $\le k$.

Hit rate vs. consistency is a constrained optimization: maximize $\Pr[\text{servable at tier} \le j]$ subject to the cut/staleness predicate — an instance of caching under a **freshness constraint**, related to TTL tuning and the **competitive caching** literature (the predicate makes some hits *unsafe*, shrinking the feasible cache).

## 3. State of the Art (SOTA)

- **Foundational mechanism:** **Bayou session guarantees** (Terry, Demers, Petersen et al., 1994) — read/write-sets carried in the session; the canonical model edge designs reuse.
- **Causal at edge:** **SwiftCloud** (Zawirski et al., 2015) provides causal+ to clients with client-side caches and a small server set; closest principled multi-tier design.
- **Systems-SOTA:** Cloudflare **Durable Objects** give a single-writer coordination point per key (strong within an object) atop eventually-consistent KV; Fastly/Akamai expose TTL + purge but **no defined cross-PoP model**. Facebook's **TAO/cache-invalidation** and **RIPQ/CacheLib** target hit rate, not formal guarantees.
- This split — strong theory (session/causal) vs. shipping caches with only TTL/purge — is why status is *empirically-open*.

## 4. Upper Bound

Session guarantees are enforceable with **$O(\text{write-set})$** metadata per session and zero extra round trips on a hit (miss to a higher tier on a guard failure); causal cuts cost $O(\text{deps})$ metadata, compressible to a vector of size $O(\#\text{datacenters})$ via dependency-vector summarization. Bounded-$t$ staleness needs only loosely synchronized clocks and $O(1)$ per entry. These hold in the **asynchronous message-passing model with sticky-or-token-following sessions**.

## 5. Lower Bound

Genuine partial replication implies an $\Omega(\#\text{relevant DCs})$ causal-metadata floor (catalog problem "causal-consistency-metadata-lower-bounds"). For latency: any guarantee stronger than eventual that must survive an edge–origin partition runs into **CAP** — during a partition an edge tier must either serve possibly-violating data or miss/stall. **PACELC** Else-Latency: even without partition, enforcing causal/bounded reads forces extra misses (origin RTs), a quantifiable latency tax. No tight lower bound exists relating hit-rate loss to the consistency level — this is the empirical gap.

## 6. The Gap

Theory gives sound mechanisms; what's missing is **quantitative**: (1) tight hit-rate / tail-latency cost of each consistency level on real CDN topologies and workloads; (2) coordination-free causal across *many* tiers without per-key single-writer chokepoints; (3) measurement of anomaly rates in production CDNs to know which guarantee users even need. Closing it needs both a lower-bound theory (freshness-constrained competitive caching) and large-scale measurement.

## 7. Current Research (as of June 2026)

- Consistency-as-a-config in edge platforms (Durable Objects, regional Aurora/DynamoDB Global Tables, FaunaDB) — but mostly per-key strong or pure eventual, not tunable causal across tiers *(frontier — verify)*.
- Verifiable edge caching: signed version certificates so clients detect staleness without trusting the PoP, building on session-token ideas.
- WebAssembly-edge stateful operators enabling causal cuts at PoPs (Cloudflare/Fastly research) *(frontier — verify)*.

## 8. Future Work

- A competitive-ratio theory for freshness/causal-constrained multi-tier caching.
- Workload-driven anomaly-rate prediction to choose the *minimal sufficient* model per app.
- Co-design of invalidation/purge with causal stability so invalidations are themselves causally ordered.

## 9. Key References

- **[Foundational]** Terry, D. B., Demers, A. J., Petersen, K., Spreitzer, M., Theimer, M., Welch, B. *Session guarantees for weakly consistent replicated data.* PDIS, 1994. — [DOI](https://doi.org/10.5555/645792.668302)
- **[SOTA]** Zawirski, M., Preguiça, N., Duarte, S., Bieniusa, A., Balegas, V., Shapiro, M. *Write fast, read in the past: causal consistency for client-side applications (SwiftCloud).* Middleware, 2015. — [DOI](https://doi.org/10.1145/2814576.2814733)
- **[SOTA]** Lloyd, W., Freedman, M. J., Kaminsky, M., Andersen, D. G. *Don't settle for eventual: scalable causal consistency for wide-area storage with COPS.* SOSP, 2011. — [DOI](https://doi.org/10.1145/2043556.2043593)
- **[Survey]** Bermbach, D., Tai, S. *Eventual consistency: how soon is eventual?* / *Benchmarking edge consistency.* (consistency benchmarking line), 2011–2014. — [DOI](https://doi.org/10.1145/2093185.2093186)
- **[SOTA]** Bronson, N. et al. *TAO: Facebook's distributed data store for the social graph.* USENIX ATC, 2013. — [USENIX](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson)

## 10. Worked Example

A user in London writes `avatar = v5` through PoP-London, which forwards to origin (now at version 5). Their phone, on cellular, reads through PoP-Paris, whose cached fill is `avatar = v3` (TTL not yet expired). Without a session guard the read returns `v3` — a **read-your-writes (RYW) violation**: the user sees their old avatar.

Fix with a session write-set vector $W_s = \{\text{avatar}:5\}$ carried in the request. The serving rule: a tier may serve a cached entry only if its stored version $\ge W_s$. PoP-Paris holds version 3; $3 \not\ge 5$, so it **misses** and forwards to origin (or to a tier holding $\ge 5$), returning `v5`. RYW restored.

Cost ledger:
- Metadata: $O(|\text{write-set}|)$ per session — here one key.
- On a hit ($\ge W_s$): zero extra round-trips.
- On a guard failure: one miss to a higher tier (the PACELC Else-Latency tax).

If London–Paris were partitioned and Paris could not reach origin, CAP forces the choice: serve possibly-stale `v3` (available, inconsistent) or stall (consistent, unavailable) — no edge config escapes this trade-off.

---
*Part of the [DBMS Research catalog](../../README.md).*
