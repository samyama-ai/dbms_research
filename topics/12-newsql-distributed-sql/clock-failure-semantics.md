---
id: 12-newsql-distributed-sql/clock-failure-semantics
title: "Clock synchronization failure semantics"
topic: 12-newsql-distributed-sql
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Clock synchronization failure semantics

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/clock-failure-semantics` · **Status:** empirically-open

## 1. Problem Statement
Distributed SQL systems use physical-clock-derived timestamps to order transactions: TrueTime (bounded-uncertainty intervals) in Spanner, Hybrid Logical Clocks (HLC) in CockroachDB/YugabyteDB. Their safety arguments assume a *clock invariant* — e.g., TrueTime's true time lies within the reported interval $[\text{earliest}, \text{latest}]$, or HLC tracks causal order within a bounded skew $\varepsilon$. The problem: characterize the **safety and liveness semantics when this invariant is violated**, especially under *silent* failure (clock drifts or jumps but the uncertainty bound is not widened).

- **Safety variant.** Under what clock-failure models can external consistency (linearizability of commit order) still be guaranteed, and which violations cause stale reads, lost writes, or non-serializable schedules?
- **Detection variant.** Can a deployed system *detect* (black-box, at runtime) that its clock invariant has been silently violated before correctness is breached?
- **Liveness variant.** Quantify availability loss when systems conservatively widen uncertainty (commit-wait blows up) versus the correctness loss when they don't.

## 2. Mathematical Foundations
Let each node $n$ have a physical clock $C_n(t)$ with true error $|C_n(t)-t|$. TrueTime exposes an interval $TT_n = [t_{\text{lo}}, t_{\text{hi}}]$ with the **safety invariant** $t \in TT_n$ w.h.p.; commit-wait blocks until $t_{\text{lo}} > c_i$ so that no later transaction gets a smaller timestamp. External consistency follows: if $T_i$ commits before $T_j$ starts (real time), then $c_i < c_j$.

HLC pairs a physical component $pt$ and a logical counter $l$, maintaining $|hlc.pt - pt| \le \varepsilon$ under the assumption that NTP-bounded skew holds. The HLC ordering refines causality (a Lamport-clock property) but its *real-time* meaning depends on $\varepsilon$ being a true bound.

A **silent clock failure** is a model where the assumed bound $\varepsilon$ (or interval width) is reported but the actual error exceeds it: $|C_n(t)-t| > \varepsilon$ while the system believes $\le \varepsilon$. Formally this breaks the indistinguishability premise underlying the safety proof; one can construct executions where two transactions ordered by timestamps violate real-time order, producing an SI/serializability anomaly detectable only in the DSG.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** Spanner relies on GPS/atomic-clock-disciplined TrueTime with armaments to *crash* nodes whose uncertainty exceeds a threshold (fail-stop on clock-bound violation). CockroachDB enforces a `max-offset`; nodes whose skew is detected beyond it self-terminate, and reads within the uncertainty window restart (read-refresh). YugabyteDB similarly bounds `max_clock_skew`.
- **Theory-SOTA.** The Lamport happens-before and HLC (Kulkarni, Demirbas et al., 2014) formalizations give the nominal guarantees; Jepsen analyses (Kingsbury) empirically expose anomalies under injected clock skew. There is no complete formal taxonomy of *silent* failure outcomes.

## 4. Upper Bound
Under a fail-stop clock model (any node exceeding bound $\varepsilon$ halts within detection latency $\delta$), safety is preserved and the cost is a liveness penalty bounded by $O(\delta)$ unavailability of that node. Commit-wait imposes throughput cost $\approx 2\varepsilon$ latency per externally-consistent commit — the best-known "price of correctness" in this model.

## 5. Lower Bound
This is fundamentally an FLP-flavored impossibility: in an asynchronous system you cannot reliably *bound* clock error using the clocks themselves; silent, correlated skew (e.g., a shared bad NTP source) is indistinguishable from correct operation without an external reference. Hence no purely internal mechanism can guarantee detection of all silent clock failures — a safety lower bound by indistinguishability. Any externally-consistent protocol must pay $\Omega(\varepsilon)$ commit latency (commit-wait is essentially optimal for TrueTime-style guarantees).

## 6. The Gap
Theory cleanly covers the fail-stop case (safe but costly) and the asynchronous case (undetectable failures possible). The *empirically open* middle is: real deployments have partial synchrony, correlated NTP failures, VM clock pauses, and leap-second events. We lack a quantified map from realistic failure distributions to anomaly rates, and lack runtime detectors with proven coverage. Closing it needs both a formal failure taxonomy and measured failure-mode statistics from production fleets.

## 7. Current Research (as of June 2026)
Jepsen-style adversarial testing continues to find clock-related anomalies *(frontier — verify)*. Active directions: cheap commodity-clock alternatives to GPS/TrueTime (e.g., software-defined clock bounds, Sundial/data-center-clock research from MIT and Microsoft *(frontier — verify)*); formal verification of HLC-based commit protocols (TLA+/Ivy efforts at Microsoft Research and MPI-SWS); and "clock-skew chaos engineering" frameworks. Demirbas (HLC) and the CockroachDB/Cockroach Labs engineering blog remain primary sources.

## 8. Future Work
- A complete anomaly taxonomy mapping clock-failure modes to isolation violations.
- Runtime detectors that bound the probability of undetected silent skew using independent witnesses.
- Co-design of commit protocols that degrade gracefully (bounded staleness) instead of crashing on skew.

## 9. Key References
- **[Foundational]** Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978. — [DOI](https://doi.org/10.1145/359545.359563)
- **[Foundational]** Fischer, Lynch, Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Kulkarni, Demirbas, Madappa, Avva, Leone. *Logical Physical Clocks (HLC).* OPODIS, 2014. — [DOI](https://doi.org/10.1007/978-3-319-14472-6_2)
- **[Survey]** Kingsbury (Jepsen). *Analyses of distributed databases under clock skew and partition.* jepsen.io, 2016–2023. — [Jepsen](https://jepsen.io/analyses)

## 10. Worked Example

TrueTime with honest uncertainty $\varepsilon = 4$ ms. Transaction $T_i$ commits: it picks $\mathit{ts} = \mathit{TT.latest} = 100$ and commit-waits until $\mathit{TT.earliest} > 100$, i.e. $\approx 2\varepsilon = 8$ ms. A later $T_j$ that starts in real time after $T_i$ commits sees $\mathit{TT.latest} \ge 101 > 100$, so $c_j > c_i$ — external consistency holds.

Now inject a *silent* fault: node $n$'s true error is $9$ ms but it still reports $\varepsilon = 4$. At true time $108$ its clock reads $99$ and it claims interval $[95,103]$. $T_i$ commits at $\mathit{ts}=103$ after a wait of only $8$ ms (true time $116$). A concurrent $T_j$ on a healthy node reads true time $110 < 116$ but is assigned $\mathit{ts}=110 < 103$? No — $110 > 103$, fine; the danger is the reverse: a transaction whose real time precedes $T_i$ can receive $\mathit{ts} > 103$, inverting commit order versus real time. The resulting $rw$/$ww$ inversion appears only as a cycle in the dependency-serialization graph — invisible to either node, exactly the undetectable-by-indistinguishability case the lower bound predicts.

---
*Part of the [DBMS Research catalog](../../README.md).*
