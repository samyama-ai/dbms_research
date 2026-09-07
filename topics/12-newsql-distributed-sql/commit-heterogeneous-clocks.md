---
id: 12-newsql-distributed-sql/commit-heterogeneous-clocks
title: "Commit protocol for heterogeneous replica clocks"
topic: 12-newsql-distributed-sql
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Commit protocol for heterogeneous replica clocks

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/commit-heterogeneous-clocks` · **Status:** open

## 1. Problem Statement

Distributed SQL systems that offer external consistency (linearizability of transactions) order commits by physical timestamps drawn from imperfect clocks. Spanner's TrueTime assumes a *uniform* clock-uncertainty bound $\varepsilon$ across all nodes, enforced by commit-wait of duration $2\varepsilon$. The problem: in a realistic fleet, replicas have **heterogeneous** clock quality — some sit next to a GPS/atomic reference ($\varepsilon \approx 1$ ms), others run plain NTP ($\varepsilon$ in the tens of ms), and some experience transient drift or asymmetric network delay.

We want a commit protocol that (i) preserves external consistency — if $T_1$ commits before $T_2$ begins in real time, then $\mathit{ts}(T_1) < \mathit{ts}(T_2)$; (ii) minimizes commit latency, ideally letting accurate replicas pay near-zero commit-wait rather than the worst-case $2\varepsilon_{\max}$; and (iii) remains safe when a replica's *claimed* uncertainty is wrong (a clock fault).

**Decision variant:** given per-replica uncertainty intervals, decide whether a proposed commit timestamp is safe to acknowledge now. **Optimization variant:** minimize expected commit-wait subject to a target violation probability $\delta$. **Robustness variant:** bound the externally-visible inconsistency when up to $f$ replicas report dishonest or stale uncertainty.

## 2. Mathematical Foundations

Model each node $i$ with a true time $t$ and a local reading $C_i(t)$ satisfying $|C_i(t) - t| \le \varepsilon_i(t)$ under a *correct-clock* assumption. TrueTime exposes $[\mathit{earliest}, \mathit{latest}]$ with width $2\varepsilon$; external consistency follows from the rule: pick $\mathit{ts} = \mathit{TT.now().latest}$ and wait until $\mathit{TT.now().earliest} > \mathit{ts}$ before releasing locks, so the commit's real time provably precedes any later transaction's timestamp.

With heterogeneous $\varepsilon_i$, the safety invariant becomes a constraint over the *coordinator's* interval, not the fleet's max. The core object is the **uncertainty lattice**: a partial order on intervals where $[a,b] \prec [c,d]$ iff $b < c$. Commit-wait is the operation that shrinks an interval to a point provably in the past. Probabilistic relaxations replace the hard bound with a tail model $\Pr[|C_i - t| > x] \le g_i(x)$ (e.g. sub-Gaussian), turning commit-wait into a quantile: wait $w$ s.t. $g_i(w) \le \delta$. This connects to clock-synchronization theory (Lamport–Melliar-Smith, Srikanth–Toueg lower bounds on achievable skew $\Omega(\varepsilon(1-1/n))$) and to interval-order scheduling.

## 3. State of the Art (SOTA)

- **TrueTime / Spanner** (Corbett et al., OSDI 2012): uniform $\varepsilon$, commit-wait. The reference design but pays the global worst case.
- **Clock-bound / AWS TimeSync + ClockBound** (2021–): exposes per-instance error bounds to applications, enabling heterogeneous reasoning, used in Aurora DSQL.
- **CockroachDB** uses HLCs with a configurable max-offset and aborts on uncertainty restarts rather than commit-waiting — avoiding tight clocks at the cost of read-restart amplification.
- **Sundial / Clock-SI / SLOG** and hybrid-logical-clock (HLC, Kulkarni et al. 2014) give logical fallbacks decoupled from physical accuracy.

## 4. Upper Bound

With honest heterogeneous bounds, commit-wait at the *coordinator* of $2\varepsilon_{\text{coord}}$ suffices for external consistency if the coordinator's timestamp dominates all participants' read intervals — so a system can route commits through the most accurate available replica, achieving $O(\varepsilon_{\min})$ wait rather than $O(\varepsilon_{\max})$. Probabilistic commit-wait achieves expected wait $\inf\{w : g(w)\le\delta\}$ with externally-visible violation probability $\le\delta$ per commit. These are constructive but **assume correct clocks**.

## 5. Lower Bound

Any externally-consistent protocol that commits without inter-node communication at commit time must wait at least the true clock uncertainty of the timestamping node — you cannot certify "now is past $\mathit{ts}$" faster than your own error bar. Srikanth–Toueg gives an $\Omega(\varepsilon(1-1/n))$ floor on achievable synchronization, so commit-wait cannot be driven below the residual skew. Under Byzantine/faulty clocks, FLP-style and clock-fault impossibilities apply: with no bound on a faulty node's error, no deterministic protocol guarantees external consistency without extra rounds (a CAP-flavored tradeoff between waiting and aborting).

## 6. The Gap

The honest-clock upper bound ($O(\varepsilon_{\text{coord}})$) and the per-node lower bound nearly match *when bounds are trusted*. The genuinely open gap is **robustness**: there is no protocol that simultaneously (a) exploits heterogeneity for low latency and (b) tolerates an adversarial or silently-faulty clock with provable, tight inconsistency bounds, without degrading to either global worst-case wait or HLC-style restart amplification. Closing it requires a fault model bridging probabilistic skew and Byzantine clocks.

## 7. Current Research (as of June 2026)

Aurora DSQL's clock architecture and the broader ClockBound ecosystem are pushing application-exposed heterogeneous bounds into production *(frontier — verify)*. Academic work studies probabilistic external consistency and clock-fault detection via cross-checking (gossiped uncertainty + outlier rejection). Groups at MIT/CMU on deterministic databases (SLOG/Calvin lineage, Abadi) and the CockroachDB/Cockroach Labs research arm on uncertainty-interval minimization are active. There is renewed interest in attested/secure time and PTP-grade fleet sync as commodity *(frontier — verify)*.

## 8. Future Work

- Tight competitive analysis of adaptive commit-wait that learns per-replica $g_i$ online.
- Byzantine-clock-tolerant external consistency with sub-worst-case latency.
- Co-designing follower reads (see staleness-bounds problem) with heterogeneous-clock commit.
- Formal verification (TLA+/Ivy) of heterogeneous commit-wait under mixed fault models.

## 9. Key References

- **[Foundational]** Corbett, Dean, et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[Foundational]** Kulkarni, Demirbas, et al. *Logical Physical Clocks (HLC).* OPODIS, 2014. — [DOI](https://doi.org/10.1007/978-3-319-14472-6_2)
- **[Foundational]** Srikanth, Toueg. *Optimal Clock Synchronization.* JACM, 1987. — [DOI](https://doi.org/10.1145/28869.28876)
- **[SOTA]** Ren, Li, Abadi. *SLOG: Serializable, Low-latency, Geo-replicated Transactions.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3342263.3342647)
- **[SOTA]** Demirbas et al. *ClockBound and bounded-error time for distributed databases.* (AWS TimeSync ecosystem), 2021–. — [GitHub](https://github.com/aws/clock-bound)
- **[Survey]** Lamport, Melliar-Smith. *Synchronizing Clocks in the Presence of Faults.* JACM, 1985. — [DOI](https://doi.org/10.1145/2455.2457)

## 10. Worked Example

Three replicas with heterogeneous honest uncertainty: $\varepsilon_1 = 1$ ms (GPS), $\varepsilon_2 = 1$ ms (GPS), $\varepsilon_3 = 25$ ms (plain NTP). A transaction touches $r_1$ and $r_3$.

Uniform-TrueTime Spanner must use the fleet worst case: commit-wait $\approx 2\varepsilon_{\max} = 50$ ms.

Heterogeneous routing: choose the coordinator to be an *accurate* node, say $r_1$, and assign $\mathit{ts} = \mathit{TT}_{r_1}.\mathit{latest}$. External consistency needs only the coordinator's interval to be certified past, so commit-wait $= 2\varepsilon_{\mathrm{coord}} = 2\,\text{ms}$ — a $25\times$ latency reduction. The catch: $r_3$'s reads must still be dominated by $\mathit{ts}$; if $r_3$'s read interval reaches $\mathit{ts}+24$, safety requires the coordinator's timestamp to dominate it, partly clawing back the win.

Probabilistic variant: with sub-Gaussian tail $\Pr[|C_3-t|>w]\le e^{-w^2/2\sigma^2}$, $\sigma=8$, a target $\delta=10^{-6}$ needs $w \approx \sigma\sqrt{2\ln(1/\delta)} \approx 8\times5.26 \approx 42$ ms — showing why a *hard* $\Omega(\varepsilon)$ bound, not the mean, drives the cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
