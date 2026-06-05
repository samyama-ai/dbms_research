# Online Hot-Shard Splitting

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/online-hot-shard-splitting` · **Status:** empirically-open
> **Verification note:** In Section 10, splitting at key 65 actually yields left/right loads ≈102/98 req/s (not 90/110); the conclusion that this far beats the naive 30/170 split is unchanged.

## 1. Problem Statement

In a range-partitioned key-value store, load is rarely uniform: a small contiguous key range (a "hot shard") can absorb a disproportionate share of traffic (celebrity keys, monotonic timestamps, viral items). **Online hot-shard splitting** is the task of (a) **detecting** that a shard is hot, (b) choosing a **split point** that balances load across the two resulting shards, and (c) **executing** the split (and migrating the new sub-shard to a less-loaded node) **live**, all while:

- not violating **latency SLOs** (e.g., p99 read/write tail) during the split,
- preserving **causal/transactional ordering** of operations on affected keys, and
- avoiding oscillation (split/merge thrashing).

Variants: **detection** (online change-point on a load stream), **split-point selection** (optimization: pick a key that equalizes future load given an access distribution estimated from samples), and **scheduling** (when/where to migrate under a movement and SLO budget). The realistic regime is *adversarial or rapidly drifting* hotness with bounded sampling of the access distribution.

## 2. Mathematical Foundations

Let a shard own key range $[a,b)$ with an (unknown) request-rate density $f(k)$ over keys. The **optimal balancing split point** $k^*$ satisfies $\int_a^{k^*} f = \tfrac12 \int_a^b f$ — the *load median*, estimable from a stream via quantile sketches (**t-digest**, **GK/Greenwald-Khanna**, **DDSketch**) with $\epsilon$-additive rank error using $O(\tfrac1\epsilon \log(\epsilon n))$ space. A **single hot key** ($f$ concentrated on one key) is *unsplittable* by range — detected via heavy-hitter sketches (**Space-Saving**, **Count-Min**) and requiring replication/caching instead of splitting.

Detection is **online change-point detection** (CUSUM, Bayesian online change-point) on load time series, trading detection delay against false-alarm rate (an SPRT-style bound: expected delay $\sim \log(1/\alpha)/\text{KL}$). Live migration must preserve a **consistency invariant**: with causal consistency, the migration must respect happens-before $\prec$; implemented via a brief ownership-transfer barrier or epoch fence so no client observes a non-causal interleaving. Migration cost vs. SLO is a scheduling trade-off; the whole loop is a **control problem** (closed-loop feedback with hysteresis to prevent thrash).

$$ k^* = \arg\min_k \big| \textstyle\int_a^k f - \int_k^b f \big|, \qquad \text{split iff } \widehat{\text{load}}(a,b) > \tau \text{ (with hysteresis)}. $$

## 3. State of the Art (SOTA)

**Systems-SOTA:** Bigtable/Spanner auto-split tablets on size and (later) load; **CockroachDB** has *load-based splitting* that samples request keys and picks a balancing split point, plus a *replica/leaseholder rebalancer*; **TiKV/TiDB** PD performs hot-region detection (read/write flow stats) and scheduling; **HBase** region split policies; **DynamoDB** adaptive capacity and automatic partition splitting for hot partitions (opaque). These are robust engineering solutions but rely on heuristics and lack provable SLO-preservation or optimality guarantees — hence **empirically-open**.

**Theory-SOTA:** quantile/heavy-hitter sketches and online change-point detection give the component primitives with tight bounds, but no end-to-end theory couples detection delay + split-point error + migration to a worst-case SLO guarantee.

## 4. Upper Bound

Split-point estimation: $\epsilon$-accurate load-median from $O(\tfrac1\epsilon \log(\epsilon n))$ space (GK) or $O(\tfrac1\epsilon)$ (DDSketch, relative error). Heavy-hitter detection of all keys with frequency $> \phi n$ in $O(1/\phi)$ space (Space-Saving). Live migration with bounded stall: epoch-fenced ownership transfer moves a sub-range with $O(1)$ coordination messages and a brief write-pause bounded by migration of the *dirty tail*. No published algorithm gives a worst-case p99-SLO bound across the full loop.

## 5. Lower Bound

A **single hot key is information-theoretically unsplittable** by range partitioning — a hard impossibility that forces replication/caching. Online change-point detection has a fundamental **detection-delay vs. false-alarm** trade-off (lower bounds via Lorden/SPRT optimality): you cannot detect a hotness shift instantly without unbounded false alarms. Preserving causal order across a live ownership transfer requires at least one round of coordination (an FLP/consensus-flavored barrier), so a *zero-stall* causally-consistent migration is impossible in an asynchronous network with failures. Heavy-hitter exactness in sublinear space is impossible (must approximate).

## 6. The Gap

Component primitives are tight; the **end-to-end** problem is empirically-open: no theory bounds the *joint* objective (detection delay + balance error + migration stall) against an SLO, and no algorithm provably avoids thrash under adversarial drift while preserving causal consistency. Closing it needs a unified online model with a competitive or SLO-violation guarantee, plus a principled hysteresis/merge policy.

## 7. Current Research (as of June 2026)

Active in production-systems venues: CockroachDB and TiKV teams iterate on load-based splitting and hot-region scheduling; cloud vendors refine adaptive-capacity for hot partitions (largely closed-source). Research interest in *learned* hotness prediction and proactive (pre-emptive) splitting before SLO breach, and in formal models of live data migration preserving transactional/causal guarantees *(frontier — verify)*. Sketch-based load sampling (DDSketch, Apache DataSketches) is the common detection substrate. Cross-over with serverless/autoscaling storage where shards split and migrate at sub-second cadence.

## 8. Future Work

- An end-to-end online algorithm with a provable SLO-violation bound across detect→split→migrate.
- Formal verification of causal/transactional safety for live ownership transfer.
- Proactive, learned hotness prediction with regret guarantees and anti-thrash hysteresis theory.
- Handling unsplittable single-key hotspots via principled replication/caching co-design.

## 9. Key References

- **[Foundational]** James C. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[Foundational]** Michael Greenwald, Sanjeev Khanna. *Space-Efficient Online Computation of Quantile Summaries.* SIGMOD 2001. — [DOI](https://doi.org/10.1145/375663.375670)
- **[SOTA]** Charles Masson, Jee E. Rim, Homin K. Lee. *DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees.* VLDB 2019. — [arXiv](https://arxiv.org/abs/1908.10693)
- **[SOTA]** Ahmed Metwally, Divyakant Agrawal, Amr El Abbadi. *Efficient Computation of Frequent and Top-k Elements in Data Streams (Space-Saving).* ICDT 2005. — [DOI](https://doi.org/10.1007/978-3-540-30570-5_27)
- **[SOTA]** Rebecca Taft et al. *CockroachDB: The Resilient Geo-Distributed SQL Database.* SIGMOD 2020. — [DOI](https://doi.org/10.1145/3318464.3386134)
- **[Foundational]** Gary Lorden. *Procedures for Reacting to a Change in Distribution.* Annals of Mathematical Statistics, 1971. — [DOI](https://doi.org/10.1214/aoms/1177693055)

## 10. Worked Example

A shard owns keys $[0,100)$ with sampled request counts on four sub-buckets: $[0,25)\!:\!10$, $[25,50)\!:\!20$, $[50,75)\!:\!120$, $[75,100)\!:\!50$ req/s — total $200$ req/s, so the hotness threshold $\tau=150$ is breached. The **load median** $k^*$ satisfies $\int_0^{k^*} f = 100$. Cumulative load reaches $30$ at key $50$ and $150$ at key $75$; linearly interpolating inside the hot $[50,75)$ bucket: $k^* \approx 50 + 25\cdot\frac{100-30}{120} \approx 64.6$. Splitting at $65$ yields left shard $[0,65)\approx 90$ req/s and right shard $[65,100)\approx 110$ req/s — far better balanced than a naive *size*-based split at the midpoint $50$ (which would give $30$ vs $170$). Note: if instead all $120$ req/s landed on the single key $60$, no range split helps ($k^*$ is degenerate) — the lower bound's *unsplittable hot key* case, requiring replication/caching of key $60$ rather than a boundary move.

---
*Part of the [DBMS Research catalog](../../README.md).*
