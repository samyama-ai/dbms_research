# Deterministic Execution Without Pre-Declared Reads/Writes

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/deterministic-unknown-rwset` · **Status:** open

## 1. Problem Statement

A **deterministic** database executes a fixed input batch of transactions so that every replica reaches the same final state given the same input order — eliminating coordination for replication/recovery. Classical deterministic systems (Calvin) require each transaction's **read/write set to be known before execution**, so the sequencer can build a conflict-consistent lock-acquisition order. Many real transactions are **dependent**: their access set depends on values read at runtime (e.g., secondary-index lookups, `WHERE` predicates, control flow). The problem: **achieve deterministic concurrency control when read/write sets are not pre-declared**, ideally without expensive "reconnaissance" pre-runs, while preserving (a) determinism, (b) serializability, and (c) throughput competitive with non-deterministic OCC/2PL. Decision/feasibility framing: does there exist a deterministic scheduler that, with no a-priori access information, guarantees a serial-equivalent order without speculative re-execution? Optimization framing: minimize the number of re-executions / aborts / coordination rounds.

## 2. Mathematical Foundations

Determinism requires the output to be a function of the *input batch* $B$ and a chosen total order $\pi$ on $B$ alone: $\text{state}_{t+1} = f(\text{state}_t, B, \pi)$. With unknown access sets, the scheduler cannot statically build the conflict graph $SG$; it must discover edges *during* execution while preserving equivalence to the predetermined order $\pi$. The crux is the **predetermination–discovery tension**: lock/ordering decisions must be committed before access sets are known. Reconnaissance (Calvin's OLLP) runs a transaction at snapshot $s$ to *predict* its access set $A$, then validates at execution that $A$ is unchanged; correctness needs

$$A_{\text{recon}}(s) = A_{\text{exec}}(s') \implies \text{deterministic commit}, \quad \text{else abort + retry},$$

which can loop under contention. Aria instead executes in a batch, then deterministically *resolves* conflicts via a reservation table indexed by the fixed transaction order, turning the problem into deterministic conflict arbitration over discovered footprints.

## 3. State of the Art (SOTA)

**Systems-SOTA:** **Calvin** (Thomson et al., SIGMOD 2012) — deterministic locking with reconnaissance (OLLP) for dependent transactions. **Aria** (Lu, Yu, Suo, Madden, VLDB 2020) — runs without pre-declared sets by executing then deterministically reordering with a fallback for write-after-write conflicts; this is the leading answer to the unknown-rwset problem. **Bohm** (Faleiro & Abadi, VLDB 2015) — deterministic MVCC that still benefits from access-set knowledge. **PWV / Caracal / Q-Store** explore deterministic dependency tracking and pipelining. **Theory-SOTA:** thin; determinism as a coordination-avoidance property is studied via the CALM theorem (Hellerstein–Alvaro) and invariant-confluence (Bailis et al.), but a complexity theory of "determinism without footprints" is largely absent.

## 4. Upper Bound

Aria achieves deterministic serializable execution with **no pre-declared sets** at the cost of a deterministic reordering/fallback pass per batch: $O(1)$ extra coordination rounds with a reservation table of size $O(\text{accesses})$, but throughput drops under high write-conflict density (fallback to a Calvin-style ordered phase). Reconnaissance approaches add one snapshot pre-execution per dependent transaction, $O(\text{batch})$ extra reads, with retries bounded only probabilistically. No algorithm is known that matches non-deterministic OCC throughput across all contention levels.

## 5. Lower Bound

There is an inherent barrier: with truly unknown access sets, any deterministic scheduler must either (i) speculatively execute and risk deterministic aborts, or (ii) pre-discover footprints — you cannot order conflicts you have not observed. This yields a coordination/abort lower bound of the form "no pre-declaration ⇒ at least one observation pass or one possible abort per dependent transaction." Formally this resembles an online/competitive lower bound rather than a clean NP-hardness; no SETH/3SUM-conditional bound is established. CALM-style results imply some workloads are *intrinsically* coordination-requiring (not invariant-confluent), so zero-coordination determinism is impossible in general.

## 6. The Gap

**Genuinely open.** Upper bounds (Aria/Calvin) are *constructions*, not optimal algorithms; lower bounds are *informal barriers*, not tight. What would close it: a formal model and complexity-theoretic characterization of deterministic CC with unknown footprints, a tight bound on minimum re-execution/coordination as a function of contention, and an algorithm provably matching it — ideally interpolating smoothly between Aria-fast (low contention) and ordered-deterministic (high contention).

## 7. Current Research (as of June 2026)

Active directions: deterministic concurrency for cloud-native and geo-distributed OLTP (FaunaDB/Calvin lineage, SLOG for low-latency multi-region), and Aria-style batch determinism extended with better dependency prediction and pipelining *(frontier — verify)*. Learned/ML-predicted access sets to shrink reconnaissance cost are an emerging idea. The Yale (Abadi) and MIT (Madden) lines remain central; coordination-avoidance theory (Berkeley lineage) supplies the impossibility scaffolding.

## 8. Future Work

- A formal complexity model for deterministic CC without pre-declared read/write sets.
- Tight bounds on minimum coordination/aborts vs. contention; provably optimal schedulers.
- Accurate, cheap access-set prediction (static analysis or learned models) with guarantees.
- Adaptive engines interpolating between speculative and ordered determinism.

## 9. Key References

- **[SOTA]** Thomson, A.; Diamond, T.; Weng, S.-C.; Ren, K.; Shao, P.; Abadi, D. J. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[SOTA]** Lu, Y.; Yu, X.; Suo, L.; Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* PVLDB, 2020.
- **[SOTA]** Faleiro, J. M.; Abadi, D. J. *Rethinking Serializable Multiversion Concurrency Control.* PVLDB, 2015.
- **[Foundational]** Abadi, D. J.; Faleiro, J. M. *An Overview of Deterministic Database Systems.* CACM, 2018.
- **[Foundational]** Bailis, P.; Fekete, A.; Franklin, M.; Ghodsi, A.; Hellerstein, J.; Stoica, I. *Coordination Avoidance in Database Systems.* PVLDB, 2014.
- **[Survey]** Hellerstein, J. M.; Alvaro, P. *Keeping CALM: When Distributed Consistency Is Easy.* CACM, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
