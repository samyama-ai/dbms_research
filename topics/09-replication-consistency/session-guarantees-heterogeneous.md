---
id: 09-replication-consistency/session-guarantees-heterogeneous
title: "Read-your-writes across heterogeneous sessions"
topic: 09-replication-consistency
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Read-your-writes across heterogeneous sessions

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/session-guarantees-heterogeneous` · **Status:** partially-solved

## 1. Problem Statement
A *session* is a sequence of read/write operations issued by one logical client. The four classic **session guarantees** (Terry et al., 1994) are: read-your-writes (RYW), monotonic reads (MR), monotonic writes (MW), and writes-follow-reads (WFR). The problem is to enforce these guarantees **continuously** even when the physical substrate of a session changes underneath it: the client migrates between replicas (geo-failover, mobile handoff), reads are served by a sharded backend (different keys live on different replicas with independent replication lag), and a tiered cache (CDN, client-side store, look-aside cache) sits between client and database.

Variants:
- **Decision:** given an execution and a session-context labeling, does it satisfy a given subset $G \subseteq \{RYW,MR,MW,WFR\}$?
- **Enforcement/optimization:** design a protocol that guarantees $G$ while minimizing (a) staleness/latency, (b) context metadata carried per request, and (c) rejected/blocked reads. The hard case is *heterogeneity*: the session's identity is not bound to a single replica, connection, or cache tier.

## 2. Mathematical Foundations
Model an execution as a partial order $(O, \prec)$ over operations with a *session order* $\rightarrow_{so}$ (program order within a client) and a *visibility* relation $\mathit{vis}$. Each session guarantee is an axiom constraining $\mathit{vis}$ relative to $\rightarrow_{so}$ and the *arbitration* (version) order $\mathit{ar}$. Following Burckhardt's *replicated data type* framework, RYW is:
$$\forall w, r:\; w \rightarrow_{so} r \wedge \mathit{same\text{-}obj}(w,r) \Rightarrow (w,r)\in \mathit{vis}.$$
MR requires $\mathit{vis}$ to be "monotone along $\rightarrow_{so}$": if $r_1 \rightarrow_{so} r_2$ then everything visible to $r_1$ is visible to $r_2$. The four guarantees are independent and strictly weaker than causal consistency; their conjunction is implied by causal+ consistency.

The standard implementation device is a **version vector / dependency token** $V$: a read returns $(value, V_{\text{read}})$, the session merges tokens via $V \sqcup V'$ (join in the lattice of version vectors), and subsequent reads carry $\bigsqcup$ of all tokens seen, requiring any serving replica to have applied at least $V$. Correctness reduces to monotonicity of the join-semilattice of dependency tokens; heterogeneity breaks the implicit assumption that a single replica's logical clock totally summarizes a session's frontier.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Bailis et al.'s *Bolt-on causal consistency* (SIGMOD 2013) shows session/causal guarantees can be layered over an eventually-consistent store using explicit dependency metadata. The "sticky availability" result (Bailis, Davidson, Fekete, Ghodsi, Hellerstein, Stoica, *Highly Available Transactions*, VLDB 2014) proves session guarantees are achievable with availability **only if sessions are sticky** to a replica.
- **Systems-SOTA:** *COPS* (SOSP 2011) and *Eiger* tracked explicit dependencies; production systems (DynamoDB's session tokens, MongoDB causal-consistency `afterClusterTime`/`operationTime`, Cosmos DB's session consistency level via session tokens) implement RYW/MR by passing logical timestamps the client must echo. CDNs/edge caches mostly *do not* honor these and are the weak link.

## 4. Upper Bound
With **sticky sessions** to a single replica, all four guarantees are achievable with **zero extra coordination** and $O(1)$ per-request metadata (the replica's own clock), under high availability (HAT result). With *non-sticky* heterogeneous sessions, RYW+MR are achievable by carrying a dependency token of size $O(\text{\\#shards touched})$ (a version vector restricted to touched partitions) and blocking a serving replica until its applied frontier dominates the token — latency bounded by replication lag $\Delta$, so worst-case read latency $O(\Delta)$ but no aborts.

## 5. Lower Bound
Under genuine non-stickiness and full availability, session guarantees clash with the CAP/HAT boundary: *Highly Available Transactions* proves **no highly-available, non-sticky** implementation can provide all session guarantees during partitions — stickiness or unavailability is required (a CAP-style impossibility, not NP-hardness). Metadata lower bound: to enforce RYW across $k$ independently-lagging shards, a session must in the worst case carry $\Omega(k)$ distinct version components — a version vector cannot be compressed below the number of causally-relevant origins without losing precision (a communication/encoding argument).

## 6. The Gap
The single-shard, sticky case is **closed**. Genuinely open in practice: how to bound metadata when sessions touch many shards *and* traverse caches that cannot block. Compressed/probabilistic dependency tracking (Bloom-clocks, bounded version vectors) trades soundness for size, but the precise three-way tradeoff between metadata size, staleness, and false-blocking rate is not characterized by matching bounds.

## 7. Current Research (as of June 2026)
- Edge/CDN-aware session tokens that propagate `operationTime` through cache layers *(frontier — verify)*.
- Bloom-clock and probabilistic causal stamps to cap metadata growth across many shards (follow-ups to Kulkarni et al.'s Bloom clocks).
- Verification tooling: extending Jepsen/Elle and the **Ostrowski/Kleppmann**-style consistency checkers to certify session guarantees under client migration.

## 8. Future Work
- Formal model where a "session" spans heterogeneous tiers with explicit, composable guarantee contracts per tier.
- Tight metadata/staleness/false-block lower bounds for multi-shard RYW.
- Cache-coherent session tokens standardized across CDN APIs.

## 9. Key References
- **[Foundational]** Terry, Demers, Petersen, Spreitzer, Theimer, Welch. *Session Guarantees for Weakly Consistent Replicated Data.* PDIS, 1994. — [ACM DL](https://dl.acm.org/doi/10.5555/645792.668302)
- **[Foundational]** Burckhardt. *Principles of Eventual Consistency.* Foundations and Trends in Programming Languages, 2014. — [DOI](https://doi.org/10.1561/2500000011)
- **[SOTA]** Bailis, Davidson, Fekete, Ghodsi, Hellerstein, Stoica. *Highly Available Transactions: Virtues and Limitations.* VLDB, 2014. — [arXiv](https://arxiv.org/abs/1302.0309)
- **[SOTA]** Bailis, Ghodsi, Hellerstein, Stoica. *Bolt-on Causal Consistency.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465279)
- **[SOTA]** Lloyd, Freedman, Kaminsky, Andersen. *Don't Settle for Eventual* (COPS). SOSP, 2011. — [DOI](https://doi.org/10.1145/2043556.2043593)

## 10. Worked Example

A client writes its profile, then reads it back after a geo-failover. Shards: `A` (profile) and `B` (settings), each with applied-frontier clocks.

1. Client (sticky to replica $R_1$) writes `profile=v2`. $R_1$ returns token $V=\{A:5\}$ (its 5th update on shard $A$). Session frontier $\sqcup = \{A:5\}$.
2. Failover: next read routes to replica $R_2$, which has only applied $\{A:4\}$ on shard $A$ (lag $\Delta$).
3. RYW requires $R_2$'s applied frontier to dominate the carried token: need $A \ge 5$, but $R_2$ has $A=4$. So $R_2$ **blocks** until it applies update 5, then serves `v2`. No stale read, no abort — latency cost bounded by $\Delta$.

Now suppose the read also touches shard `B`. The token grows to $\{A:5, B:3\}$ — size $O(\\#\text{shards touched})$, matching the $\Omega(k)$ metadata lower bound: each independently-lagging origin needs its own component, or RYW can silently break.

---
*Part of the [DBMS Research catalog](../../README.md).*
