# Tightening HLC drift bounds

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/hlc-drift-bounds` · **Status:** partially-solved

## 1. Problem Statement
**Hybrid Logical Clocks (HLC)** combine a physical-clock reading with a bounded logical counter so that the resulting timestamp both (a) captures causality (happens-before) and (b) stays close to physical time. The guarantee depends on a bound $\epsilon$ on the divergence between any node's physical clock and true time. The problem: derive **tight, provable bounds on HLC drift** — i.e., how far an HLC timestamp can lag or lead true physical time, and how large the logical counter can grow — *under adversarial clock behavior* (drift, jumps, NTP step corrections, malicious skew), and use these to give **freshness/staleness guarantees** for reads.

Variants:
- **Bounding:** Worst-case bound on $|l.j - pt_j|$ (HLC value minus physical time) and on the logical-counter component $c$ as a function of clock-skew bound $\epsilon$ and message patterns.
- **Adversarial:** Bounds when an adversary controls some clocks within model limits (jumps, partial synchrony violations).
- **Staleness:** Given a follower read at HLC $T$, bound the real-time staleness of returned data.

It is "partially solved": the original HLC paper (Kulkarni et al. 2014) proves $|l.j - pt_j| \le \epsilon$ and bounds the counter $c$ under well-behaved clocks; tightening these under adversarial drift and deriving end-to-end staleness guarantees remains active.

## 2. Mathematical Foundations
Each node $j$ keeps $hlc_j=(l_j,c_j)$. On a local event with physical time $pt_j$: $l_j' \leftarrow \max(l_j, pt_j)$, and $c_j'$ increments if $l_j'=l_j$ else resets to 0. On receiving message with timestamp $(l_m,c_m)$: $l_j'\leftarrow\max(l_j,l_m,pt_j)$ with the counter updated accordingly. The clock condition $e\to f \Rightarrow hlc(e) < hlc(f)$ holds (lexicographic order on $(l,c)$).

Core theorems (Kulkarni–Demirbas–Madappa–Avva–Leone 2014), assuming $|pt_j - pt_{true}|\le\epsilon$ for all $j$:
$$|l_j - pt_j| \le \epsilon, \qquad c_j \le f(\epsilon)$$
with the counter bounded by a function of $\epsilon$ and the clock granularity. The adversarial version replaces the uniform $\epsilon$ assumption with a model where clocks may drift at rate $\rho$ and step by bounded jumps; the question is the resulting worst-case bound. Information-theoretically, no clock algorithm beats the underlying synchronization quality $\epsilon$ — HLC inherits it (cf. lower bounds on clock synchronization, Lundelius–Lynch 1984: optimal achievable skew is $\epsilon(1-1/n)$).

## 3. State of the Art (SOTA)
- **Theory:** Kulkarni et al. (OPODIS 2014) is the canonical HLC result with the $\epsilon$ bound and counter bound. Lundelius–Lynch (1984) gives the matching lower bound on achievable clock skew.
- **Systems:** CockroachDB and YugabyteDB use HLCs with a configured **max-offset** $\epsilon$; reads within the uncertainty interval trigger *uncertainty restarts* to preserve consistency. MongoDB uses HLC-like cluster time for causal consistency. These systems treat $\epsilon$ as a safety parameter — exceeding it risks consistency violations, motivating tighter, *monitored* bounds.

## 4. Upper Bound
Best-known: under the standard assumption $|pt_j - pt_{true}|\le\epsilon$, HLC guarantees $|l_j - pt_j|\le\epsilon$ and a logical-counter bound, giving **read staleness $\le 2\epsilon$** for bounded-staleness follower reads. With hardware clocks (PTP/AWS Time Sync) $\epsilon$ can be sub-millisecond, tightening staleness accordingly. Model: partially synchronous, clocks with bounded skew; no Byzantine clocks.

## 5. Lower Bound
Lundelius–Lynch (1984): in a system with message-delay uncertainty $u$, no clock-synchronization algorithm can guarantee skew better than $u(1-1/n)$ — so HLC's freshness can be **no tighter than the underlying synchronization bound** $\epsilon$. Under adversarial clocks that may step or drift beyond $\epsilon$, *no logical-clock scheme can preserve the freshness guarantee* — an indistinguishability argument: a node cannot tell a benign delay from an adversarial clock jump. Thus tightening requires either stronger synchronization (hardware) or detection/monitoring, not algorithmic cleverness alone.

## 6. The Gap
For *well-behaved* clocks the bounds are essentially tight (matching Lundelius–Lynch). The genuine gap is **adversarial/abnormal clock behavior**: NTP step corrections, VM live-migration clock jumps, and skew exceeding the configured $\epsilon$ are common in practice and can silently violate consistency. There is no tight, *self-verifying* bound that holds under such conditions, nor a clean characterization of staleness when $\epsilon$ is violated transiently. Closing it means either (a) detection mechanisms with provable coverage, or (b) protocols whose safety degrades gracefully rather than breaking when $\epsilon$ is exceeded.

## 7. Current Research (as of June 2026)
- Murat Demirbas's group (and successors) continuing HLC theory and TLA+-verified bounds.
- *(frontier — verify)* "clock-fault-detecting" HLC variants that bound staleness even when physical clocks misbehave, integrating signed time sources and hardware-attested clocks.
- Tighter staleness bounds for follower/stale reads in CockroachDB/YugabyteDB driven by AWS Time Sync / PTP sub-ms offsets.
- *(frontier — verify)* formal analyses linking HLC drift to external-consistency safety in geo-distributed deployments.

## 8. Future Work
- Provable bounds under adversarial drift and bounded jumps (a clean theorem with matching construction).
- Graceful-degradation HLC: bounded inconsistency rather than safety violation when $\epsilon$ is exceeded.
- Runtime monitoring with coverage guarantees for clock anomalies.
- Byzantine-tolerant hybrid clocks for permissioned/cross-org databases.

## 9. Key References
- **[Foundational]** S. Kulkarni, M. Demirbas, D. Madappa, B. Avva, M. Leone. *Logical Physical Clocks (HLC).* OPODIS, 2014.
- **[Foundational]** L. Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978.
- **[Foundational]** J. Lundelius, N. Lynch. *An Upper and Lower Bound for Clock Synchronization.* Information and Control, 1984.
- **[SOTA]** J. Corbett et al. *Spanner: Google's Globally-Distributed Database* (TrueTime context). OSDI, 2012.
- **[SOTA]** CockroachDB Labs. *Living Without Atomic Clocks* (HLC + max-offset / uncertainty restarts design write-up). Cockroach Labs, 2016+.

---
*Part of the [DBMS Research catalog](../../README.md).*
