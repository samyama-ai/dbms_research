---
id: 06-recovery-logging/deterministic-db-durability
title: "Durability for deterministic databases"
topic: 06-recovery-logging
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Durability for deterministic databases

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/deterministic-db-durability` · **Status:** partially-solved

## 1. Problem Statement
A **deterministic database** (Calvin, FaunaDB, Aria, and the deterministic-execution line) guarantees that, given the same initial state and the same totally ordered sequence of transaction *inputs*, every replica produces the identical final state — execution is a pure function of (state, input order). This unlocks a radically cheaper durability scheme: instead of logging *physical effects* (before/after images of pages or rows, as in ARIES), the system can log only the **inputs/commands** (the transaction requests and their agreed order). Recovery then *re-executes* from a checkpoint. The problem is to **replace physical/ARIES-style logging with input (command) logging in deterministic engines while bounding recovery time** — re-execution can be slow, so the challenge is bounding time-to-recover without giving back the runtime savings.

Variants:
- **Optimization:** minimize a weighted cost of (runtime logging overhead + storage) and (recovery/re-execution time), choosing checkpoint frequency and replay parallelism.
- **Decision:** given a recovery-time SLO $T_{\text{rec}}$, does a checkpoint+command-log schedule meeting it exist for a workload?
- **Robustness:** preserve determinism (hence command-log correctness) in the presence of non-deterministic operations (wall-clock, RNG, external reads) — i.e., make the log *sufficient*.

## 2. Mathematical Foundations
Let state evolve as $s_{i} = \delta(s_{i-1}, x_i)$ where $x_i$ is the $i$-th input and $\delta$ is the **deterministic transition function**. Determinism means $\delta$ is a function (no hidden randomness), so the entire history is recoverable from $(s_0, x_1,\dots,x_n)$. **Command logging** persists the $x_i$'s; **physical logging** would persist the $\delta$-effects. The information-theoretic insight: under determinism, the effects are *redundant* given the inputs and the function — so command logging is near-minimal (Malviya, Weisberg, Madden, Stonebraker, ICDE 2014 formalize the runtime/recovery trade-off as "Rethinking Main Memory OLTP Recovery").

Recovery from checkpoint $s_k$ replays $x_{k+1..n}$: recovery time $\approx (n-k)\cdot \bar{t}_{\text{exec}}$, i.e. *re-execution* cost, versus physical redo whose cost is $\approx (n-k)\cdot \bar{t}_{\text{apply}}$ with $\bar{t}_{\text{apply}} \ll \bar{t}_{\text{exec}}$. This is the core tension: command logging wins at runtime (log volume, no undo, deterministic so no analysis pass) but loses at recovery (must redo the *work*, not just the *writes*). Replay can be parallelized exactly because determinism + the agreed order define a **conflict DAG** (see parallel log replay), so recovery time is bounded by the critical path $C_\infty$ of re-execution, not the serial sum. Determinism also removes the need for an **undo** log entirely (no in-place dirty writes escape; aborts are deterministic), shrinking the recovery state machine.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Calvin** (Thomson, Abadi et al., SIGMOD 2012) established deterministic execution with a replicated input log as the durability/replication substrate — replicas stay consistent by agreeing on input order, not by shipping effects. **VoltDB/H-Store** ship **command logging** as a first-class option (Malviya et al., ICDE 2014) precisely for high-throughput in-memory OLTP, trading recovery time for runtime throughput. **Aria** (Lu, Yu, Suo, Madden, VLDB 2020) is deterministic without pre-declared read/write sets. **FaunaDB** uses a Calvin-style log.
- **Theory-SOTA:** the runtime/recovery trade-off is well characterized for serial replay; parallel deterministic replay bounded by the conflict-graph critical path is understood but not tightly optimized — hence **partially-solved**.

## 4. Upper Bound
Command logging reduces runtime logging to $O(\text{input size})$ per transaction (no before/after images, no undo log), and removes the analysis and undo passes. Recovery time is bounded by **parallel re-execution**: with the deterministic conflict DAG and $p$ cores, recovery makespan $\le W/p + C_\infty$ (Graham/Brent), where $W$ is total re-execution work since the checkpoint and $C_\infty$ the longest dependency chain — far below serial $(n-k)\bar t_{\text{exec}}$ for conflict-sparse workloads. Checkpoint frequency $f$ caps the replay window, so recovery time is tunable to an SLO at a known runtime checkpointing cost.

## 5. Lower Bound
Any command-log recovery must, in the worst case, **redo the computation** for transactions since the last checkpoint: there is an information-theoretic floor of $\Omega(C_\infty)$ wall-clock for the longest dependency chain of re-execution (you cannot apply $\delta$ out of dependency order), independent of cores — an Amdahl/critical-path bound. For pathological serial-conflict workloads (one hot key, long chains) command-log recovery is provably **slower than physical redo** by the ratio $\bar t_{\text{exec}}/\bar t_{\text{apply}}$, which is the fundamental price of logging inputs rather than effects. Preserving determinism in the presence of non-deterministic ops is a *correctness* lower bound: without canonicalizing those ops, no command log is sufficient to recover the unique state.

## 6. The Gap
The runtime side is essentially solved (command logging is cheap and undo-free). The **partially-solved** frontier is *recovery-time bounding*: closing the gap between command logging's slow re-execution and physical redo's fast apply, without surrendering runtime savings. Levers — checkpoint frequency, parallel deterministic replay along $C_\infty$, hybrid value/command logging for hot chains — exist but lack a unified optimal policy with provable recovery-SLO guarantees under skew. Also open: a clean theory for *hybrid* logging that command-logs cheap transactions and value-logs the few critical-path-dominating ones.

## 7. Current Research (as of June 2026)
- Deterministic-execution systems continue at Maryland (Abadi group), MIT (Madden/Aria lineage), and in cloud OLTP; integrating command logging with **disaggregated storage** and Raft/Paxos input logs is active *(frontier — verify)*.
- **Hybrid logging** that adaptively chooses command vs. value logging per transaction class to bound recovery time *(frontier — verify)*.
- Bounded-recovery parallel replay that schedules re-execution along the conflict DAG to hit a recovery SLO under skew *(frontier — verify)*.
- Making more operations deterministic (canonicalized time/RNG, deterministic external reads) so command logging stays sufficient.

## 8. Future Work
- A provably optimal checkpoint-frequency + hybrid-logging policy for a given recovery-time SLO.
- Tight bounds on parallel deterministic replay under realistic skew.
- Command logging integrated with geo-replicated consensus logs as a single durability layer.
- Determinism-preserving handling of UDFs, external calls, and non-deterministic built-ins.

## 9. Key References
- **[Foundational]** Thomson, A., Diamond, T., Weng, S.-C., Ren, K., Shao, P. & Abadi, D. J. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)
- **[SOTA]** Malviya, N., Weisberg, A., Madden, S. & Stonebraker, M. *Rethinking Main Memory OLTP Recovery (command logging).* ICDE, 2014. — [DOI](https://doi.org/10.1109/ICDE.2014.6816685)
- **[SOTA]** Lu, Y., Yu, X., Cao, L. & Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3407790.3407808)
- **[Foundational]** Abadi, D. J. & Faleiro, J. M. *An Overview of Deterministic Database Systems.* Communications of the ACM, 2018. — [DOI](https://doi.org/10.1145/3181853)
- **[Foundational]** Kallman, R. et al. *H-Store: A High-Performance, Distributed Main Memory Transaction Processing System.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1454159.1454211)
- **[SOTA]** Faleiro, J. M., Abadi, D. J. & Hellerstein, J. M. *High Performance Transactions via Early Write Visibility.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3055540.3055553)

## 10. Worked Example

A deterministic engine checkpoints at $s_k$, then processes $n-k = 10{,}000$ input txns before a crash. Each txn re-executes in $\bar t_{\text{exec}} = 50\,\mu s$; physical redo would apply effects in $\bar t_{\text{apply}} = 2\,\mu s$.

**Serial command-log recovery.** Replay all $10{,}000$ txns: $10{,}000 \times 50\,\mu s = 0.5\,s$. Physical redo would take $10{,}000 \times 2\,\mu s = 0.02\,s$ — command logging is $25\times$ slower at recovery, the price $\bar t_{\text{exec}}/\bar t_{\text{apply}}$ of logging inputs not effects.

**Parallel replay.** Build the conflict DAG. Suppose total work $W = 0.5\,s$, longest dependency chain $C_\infty = 0.05\,s$ (200 txns deep on one hot key), and $p = 16$ cores. Brent's bound: makespan $\le W/p + C_\infty = 0.5/16 + 0.05 = 0.031 + 0.05 = 0.081\,s$.

So parallelism nearly matches physical redo — but the $C_\infty = 0.05\,s$ critical path is an irreducible floor: more cores cannot beat it. With a pathological single chain ($C_\infty = W$), parallel replay collapses back to $0.5\,s$.

---
*Part of the [DBMS Research catalog](../../README.md).*
