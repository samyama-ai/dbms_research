# Consistency-Aware Caching

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/consistency-aware-caching` · **Status:** partially-solved

## 1. Problem Statement

A client- or edge-side cache sits between application code and a replicated key-value store. Each read request arrives with a declared **consistency level** $c$ drawn from a lattice (e.g., *eventual* $\sqsubseteq$ *read-your-writes* $\sqsubseteq$ *monotonic-reads* $\sqsubseteq$ *causal* $\sqsubseteq$ *linearizable*). The cache must answer a read either locally (a hit) or by forwarding to the backing store, while guaranteeing that the observed history is admissible under $c$ — **without** issuing a coordination round-trip on every request.

- **Decision variant:** Given a cached entry $(k, v, \text{meta})$ and a requested level $c$, is serving $v$ admissible under $c$ for the calling session's history?
- **Optimization variant:** Over a request stream, choose a serve/refresh policy that maximizes hit rate (equivalently minimizes backend load / tail latency) subject to **never** violating $c$ for any session.
- **Counting/analysis variant:** Bound the staleness distribution (max and quantiles) of served values as a function of metadata budget and refresh policy.

"Solving" means a cache discipline that is *safe* (no admissible-history violation) and *competitive* in hit rate against an offline optimum, using bounded per-key and per-session metadata.

## 2. Mathematical Foundations

Model the system as a set of replicas producing a partial order of operations. Consistency levels are formalized as predicates over **visibility** ($\mathsf{vis}$) and **arbitration** ($\mathsf{ar}$) relations (Burckhardt's axiomatic framework). A read $r$ returning version $v$ is admissible under causal consistency iff $\mathsf{vis}$ is transitive and $r$ sees a downward-closed set of writes in happens-before order.

Session guarantees (read-your-writes, monotonic reads) are enforceable with **per-session version vectors** or **dependency timestamps**. Let $V_s$ be the highest version vector the session has observed; a cached entry with vector $W$ is RYW-safe iff $W \geq V_s$ componentwise on keys the session wrote. Causal cuts require tracking dependencies whose size is, in the worst case, $\Theta(N)$ for $N$ writers — the central tension is compressing this to bounded metadata (cf. *causal consistency at scale*).

Bounded staleness uses real-time: with replica anti-entropy period $\Delta$ and known clock skew $\epsilon$, a value stamped at $t$ is at most $(\Delta + \epsilon)$-stale (TACT / continuous consistency). Hit-rate optimality reduces to online caching against an adversary, so competitive analysis ($k$-server, marking) applies, but the *freshness* constraint changes admissible evictions/serves.

## 3. State of the Art (SOTA)

- **Systems SOTA:** Facebook's TAO and the *RYW cache* pattern enforce read-your-writes by remembering recently written keys per session; Pelikan/Memcached lease tokens (Facebook's leases, NSDI 2013) prevent stale-set and thundering herds. DynamoDB Accelerator (DAX) offers eventual-consistency caching only. CRDT-based caches (e.g., Redis-Enterprise active-active) serve causally-consistent values locally.
- **Theory SOTA:** Bailis et al.'s *bolt-on causal consistency* (SIGMOD 2013) shows a shim can upgrade an eventual store to causal using explicit dependency metadata. Explicit/probabilistic bounded staleness (PBS, Bailis VLDB 2012) quantifies the staleness distribution of quorum reads, giving the analytical backbone for "consistency-aware" serve decisions.

## 4. Upper Bound

For **session guarantees** (RYW, monotonic reads/writes), an online cache achieves *safety with zero coordination on hits* using $O(W_s)$ session-local metadata, where $W_s$ is the number of distinct keys the session wrote/read; refresh occurs only when the local version vector cannot certify freshness. Under PBS-style bounded staleness, serving a value within a $(\Delta+\epsilon)$ window is safe with **no** per-request RTT, only background anti-entropy. Hit-rate competitiveness inherits the $O(\log k)$ randomized / $k$-competitive deterministic bounds of online caching, intersected with the freshness-feasible serve set.

## 5. Lower Bound

For **strong consistency (linearizability)**, any cache that can ever serve locally must, in the worst case, coordinate: CAP/FLP implies no protocol provides linearizable reads, availability, and partition tolerance simultaneously, so a local hit during a partition can violate linearizability. Communication-complexity arguments (Attiya–Welch) show linearizable reads cost $\Omega(u/c)$ latency tied to message delay $u$ — local serving is impossible without staleness. For **causal** consistency, Bailis/Charron-Bost-style results imply dependency metadata must in the worst case grow with the number of concurrent writers, lower-bounding metadata at $\Omega(N)$ bits absent assumptions on the dependency graph.

## 6. The Gap

The gap is **stratified by level**. Session and bounded-staleness levels are essentially *closed*: safe, coordination-free serving is achievable with modest metadata. Causal caching has a real **metadata gap** — the $\Omega(N)$ worst case vs. constant-size compressed vectors that work only under graph assumptions; closing it requires either accepting bounded false dependencies or workload-specific structure. Linearizable caching is *provably impossible* to serve locally during partitions; the open question is the best achievable **availability-staleness Pareto frontier** for near-strong levels, which remains uncharacterized.

## 7. Current Research (as of June 2026)

- Explicit-consistency / mixed-consistency caches that let each key choose its level and verify admissibility with type-checked invariants (lines from Indigo, Quelea).
- Edge/CDN integration: serving causally-consistent reads at PoPs with compressed dependency stamps; *(frontier — verify)* several 2025 systems papers report sub-vector dependency encodings using learned key-affinity.
- Verifiable staleness: combining PBS estimation with runtime monitors that detect violations probabilistically.
- Groups: Berkeley RISE/Sky lineage (Bailis-influenced work), MPI-SWS (Burckhardt-style semantics), and CRDT-focused efforts at Nova/INESC (Preguiça, Shapiro).

## 8. Future Work

- Tight competitive analysis of caching *under* a freshness constraint (freshness-aware $k$-server).
- Sub-linear causal metadata with provable false-dependency bounds.
- Cross-session coordination amortization: pay one round-trip to certify many subsequent local hits.
- Formal connection between PBS staleness quantiles and SLA-driven serve thresholds.

## 9. Key References

- **[Foundational]** Burckhardt, S. *Principles of Eventual Consistency.* Foundations and Trends in Programming Languages, 2014. — [DOI](https://doi.org/10.1561/2500000011)
- **[Foundational]** Terry, D. et al. *Session Guarantees for Weakly Consistent Replicated Data.* PDIS, 1994. — [DBLP search](https://dblp.org/search?q=Session%20Guarantees%20for%20Weakly%20Consistent%20Replicated%20Data)
- **[SOTA]** Bailis, P. et al. *Bolt-on Causal Consistency.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465279)
- **[SOTA]** Bailis, P. et al. *Probabilistically Bounded Staleness for Practical Partial Quorums.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1204.6082)
- **[Foundational]** Attiya, H., Welch, J. *Sequential Consistency versus Linearizability.* ACM TOCS, 1994. — [DOI](https://doi.org/10.1145/176575.176576)
- **[Systems]** Nishtala, R. et al. *Scaling Memcache at Facebook.* NSDI, 2013. — [USENIX](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala)

## 10. Worked Example

A session $s$ on a client cache holds version vectors. It wrote key $k$, producing $V_s = \{A{:}5, B{:}2\}$ (replica A at logical time 5, B at 2). The edge cache holds a stale copy $(k, v_{old}, W)$ with $W = \{A{:}3, B{:}2\}$.

**Read-your-writes check.** Serve locally iff $W \ge V_s$ componentwise on keys $s$ wrote. Here $W_A = 3 < 5 = V_{s,A}$, so $W \not\ge V_s$: the cached value is *not* RYW-safe. The cache must refresh from the store (one round-trip) rather than serve $v_{old}$. After refresh it caches $W' = \{A{:}5, B{:}2\} \ge V_s$ — now a hit, with **zero coordination on every subsequent read** until the session writes again. Metadata cost is $O(W_s)$, the keys the session touched.

**Bounded staleness contrast.** With anti-entropy period $\Delta = 50$ ms and clock skew $\epsilon = 5$ ms, a value stamped at $t$ is at most $(\Delta+\epsilon) = 55$ ms stale. If the SLA tolerates 100 ms staleness, the cache serves *any* such entry locally with no RTT — trading freshness precision for a higher hit rate.

---
*Part of the [DBMS Research catalog](../../README.md).*
