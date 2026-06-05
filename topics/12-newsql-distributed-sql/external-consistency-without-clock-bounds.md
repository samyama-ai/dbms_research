# Clock-uncertainty-free external consistency

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/external-consistency-without-clock-bounds` · **Status:** open

## 1. Problem Statement
**External consistency** (a.k.a. strict serializability with real-time order) requires: if transaction $T_1$ commits before $T_2$ begins in real time, then $T_1$ precedes $T_2$ in the serialization order — across the *entire* distributed system, not just per shard. Spanner achieves this using **TrueTime**, a clock service exposing a bounded uncertainty interval $[t-\epsilon, t+\epsilon]$, and "commit-wait" of $2\epsilon$ to guarantee the ordering. The problem: **achieve external consistency without relying on physical clocks with a provable error bound** $\epsilon$.

Variants:
- **Decision:** Does a protocol exist providing external consistency in a partially synchronous system with *no* bounded-error physical clock, using only message passing / logical time?
- **Performance:** If yes, what latency must it pay relative to TrueTime's $2\epsilon$ commit-wait?
- **Impossibility direction:** Is some form of clock synchronization or explicit cross-partition communication *provably required* to realize real-time order?

It is open: logical clocks alone (Lamport, vector, HLC) capture causal/happens-before order but **cannot recover real-time order between concurrent, non-communicating transactions** — yet external consistency demands exactly that ordering. Whether one can substitute communication or weaker timing assumptions for bounded clocks, and at what cost, is unresolved.

## 2. Mathematical Foundations
Lamport's happens-before $\to$ is a partial order; logical clocks $C$ satisfy the **clock condition** $a\to b \Rightarrow C(a)<C(b)$ but *not the converse*. External consistency requires capturing the *real-time* order $<_{rt}$, which is strictly stronger than $\to$ for transactions that do not exchange messages. Formally, the issue: there exist executions indistinguishable under message order but with opposite real-time order; without a physical clock, no algorithm can order them consistently with $<_{rt}$ (an indistinguishability argument akin to Attiya–Welch 1994).

TrueTime supplies an interval oracle with $|t_{true}-t_{local}|\le\epsilon$ w.h.p.; commit-wait of $2\epsilon$ enforces that commit timestamps respect $<_{rt}$. The open question is whether a protocol can guarantee $$T_1 <_{rt} T_2 \Rightarrow ts(T_1) < ts(T_2)$$ without any such $\epsilon$, using instead a **causal token / barrier** mechanism that forces communication whenever real-time ordering must be witnessed. Related: the "*clock-SI*", "*MaaT*", and "*Sundial*" timestamp-management schemes, and the theory of consistency hierarchies (Viotti–Vukolić 2016).

## 3. State of the Art (SOTA)
- **Clock-based:** Spanner/TrueTime (OSDI 2012) is the reference. AWS Time Sync with bounded error and FaRM follow.
- **Clock-free / loosely-synced:** CockroachDB uses HLCs with a configured **max clock offset** (still a bound, but uncertainty-driven *uncertainty restarts* rather than commit-wait). Clock-SI (Du et al., 2013) provides snapshot isolation with loosely synchronized clocks. MaaT (Mahmoud et al., VLDB 2014) uses dynamic timestamp ranges without synchronized clocks but provides serializability, not full real-time external consistency without communication. Sundial (Yu et al., VLDB 2018) computes logical leases.
- **Causal/communication-based:** Approaches enforcing real-time order via a coordination service (e.g., a global timestamp oracle as in Percolator/TiDB's TSO) shift the bound to a single sequencer's latency.

## 4. Upper Bound
With a **centralized timestamp oracle** (Percolator/TiDB Placement-Driver TSO), external consistency is achievable with *no clock-error bound* — at the cost of a round trip to the oracle per transaction and a single-point scalability bottleneck. With loosely synchronized HLCs (CockroachDB), external consistency holds *probabilistically* up to the configured offset, with uncertainty-induced retries. Model: partially synchronous, crash faults. No protocol is known that matches TrueTime's local-commit latency while removing the $\epsilon$ assumption entirely.

## 5. Lower Bound
An indistinguishability/communication argument shows: to order two transactions by real time without a bounded physical clock, the slower transaction must **observe a message** causally linking it to the earlier one — i.e., real-time order between non-communicating transactions is *unrecoverable from logical information alone* (extends Lamport 1978 and the Attiya–Welch 1994 uncertainty bound). Thus any clock-free external-consistency protocol must inject coordination (oracle round trip or barrier), paying at least one wide-area message delay where TrueTime pays only $2\epsilon$ local wait. CAP/partition constraints further bound availability.

## 6. The Gap
The gap separates two regimes: (a) **clock-based** schemes pay local commit-wait $2\epsilon$ but need trusted bounded clocks; (b) **clock-free** schemes pay a coordination round trip (oracle/barrier) but need no clock bound. No result proves whether one can get TrueTime-like local-only latency without *any* timing assumption — the conjecture (supported by indistinguishability) is **no**, but a clean impossibility theorem stating "external consistency without bounded clocks requires $\ge 1$ message delay of coordination per externally-ordered pair" is not yet crisply established and matched.

## 7. Current Research (as of June 2026)
- Decentralized, low-overhead timestamp oracles and hierarchical TSOs (TiDB, *(frontier — verify)* sharded-TSO designs reducing the single-sequencer bottleneck).
- HLC-based external consistency with tighter, *adversarially robust* offset handling (overlaps with the HLC-drift problem).
- *(frontier — verify)* formal frameworks (groups including Daniel Abadi/UMD, Natacha Crooks/Berkeley, MPI-SWS) characterizing the minimal coordination cost of real-time order without physical clocks.
- Hardware time (PTP, White Rabbit, AWS Time Sync) shrinking $\epsilon$ — sidestepping rather than removing the assumption.

## 8. Future Work
- A tight impossibility/lower-bound theorem on coordination cost of clock-free external consistency.
- Practical clock-free protocols competitive with Spanner latency.
- Hybrid schemes that fall back to communication only for cross-region real-time-ordered pairs.
- Quantifying the safety risk of clock-bound violations vs. coordination latency.

## 9. Key References
- **[Foundational]** L. Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978. — [DOI](https://doi.org/10.1145/359545.359563)
- **[Foundational]** H. Attiya, J. Welch. *Sequential Consistency versus Linearizability.* ACM TOCS, 1994. — [DOI](https://doi.org/10.1145/176575.176576)
- **[SOTA]** J. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** J. Du, S. Elnikety, W. Zwaenepoel. *Clock-SI: Snapshot Isolation for Partitioned Data Stores Using Loosely Synchronized Clocks.* SRDS, 2013. — [DOI](https://doi.org/10.1109/SRDS.2013.26)
- **[SOTA]** H. Mahmoud et al. *MaaT: Effective and Scalable Coordination of Distributed Transactions in the Cloud.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732269.2732270)
- **[Survey]** P. Viotti, M. Vukolić. *Consistency in Non-Transactional Distributed Storage Systems.* ACM Computing Surveys, 2016. — [DOI](https://doi.org/10.1145/2926965)

## 10. Worked Example

Two clients, no messages between them. At real time $t{=}100\text{ms}$ client $A$ commits $T_1$ (write $x{=}5$); at $t{=}120\text{ms}$, after $T_1$ returned, client $B$ begins $T_2$ (write $y{=}9$). Since $T_1 <_{rt} T_2$, external consistency demands $ts(T_1) < ts(T_2)$.

TrueTime path: with uncertainty $\epsilon = 5\text{ms}$, $T_1$ picks $ts(T_1)=t.\text{latest}=105$ then **commit-waits** $2\epsilon = 10\text{ms}$ until real time $\ge 105$ guaranteed past. $T_2$ later reads $t.\text{earliest} \ge 120 > 105$, so $ts(T_2) > ts(T_1)$ — ordering holds with only local waiting.

Clock-free path: logical clocks give $C(T_1), C(T_2)$ but since the transactions never exchange a message, happens-before does not relate them; an adversary scheduler can make them indistinguishable from the reverse real-time order. To recover $<_{rt}$, $T_2$ must observe a message causally after $T_1$ — e.g., a round trip to a timestamp oracle returning $ts > ts(T_1)$. That costs one wide-area delay where TrueTime paid only $2\epsilon$ locally, illustrating the conjectured impossibility.

---
*Part of the [DBMS Research catalog](../../README.md).*
