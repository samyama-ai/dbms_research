# Mixed deterministic/nondeterministic execution

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/hybrid-deterministic-execution` · **Status:** open

## 1. Problem Statement

**Deterministic database systems** (Calvin-style) eliminate distributed-commit coordination by
agreeing on a **total order** of transactions *before* execution: given the same input order, every
replica produces the same result, so no 2PC and no replica divergence. Their cost is **inflexibility**:
they need the transaction's read/write set known in advance (or a reconnaissance pass), and they
handle interactive / dependent / long-running transactions poorly. Traditional **nondeterministic**
concurrency control (2PL, OCC, MVCC) is flexible but pays coordination and can diverge.

The problem: build **one engine** that runs **both** deterministic transactions and traditional
nondeterministic transactions **concurrently over shared data**, with a unified correctness guarantee
(serializability / strict serializability) and **no anomalies** at the boundary between the two
regimes.

- **Decision/correctness variant:** does a mixed schedule of deterministic and nondeterministic txns
  preserve (strict) serializability, given each subsystem's local guarantees?
- **Construction variant:** design the bridging concurrency-control protocol that lets the two modes
  share locks/versions/timestamps soundly.
- **Optimization variant:** route each transaction to the mode minimizing latency/aborts subject to
  the global correctness invariant.

## 2. Mathematical Foundations

A deterministic system fixes a **sequence number** $\mathit{seq}(T)$ per transaction; the serialization
order *is* the sequence order, and execution must be **equivalent** to that order. A nondeterministic
system derives order *during* execution (lock acquisition order, commit timestamp, or validation).
The hazard is the **boundary conflict**: a deterministic $T_d$ with $\mathit{seq}(T_d)$ and a
nondeterministic $T_n$ may conflict on a key, but $T_n$'s effective serialization point is decided
dynamically — if it lands "between" deterministic sequence numbers inconsistently across replicas, or
if $T_d$ reads a value $T_n$ has not yet ordered, the merged **conflict-serialization graph** can cycle
or, worse, **diverge across replicas** (breaking determinism's replica-equivalence invariant).

Soundness requires a single global serialization order consistent with *both* the deterministic
sequence and the nondeterministic txns' chosen points. Formally, one needs an injection of all txns
into a total order $<$ such that (i) $T_d <_{} T_d' \iff \mathit{seq}(T_d) < \mathit{seq}(T_d')$ and
(ii) every conflict edge respects $<$ (conflict-serializability), and (iii) the order is **identical at
every replica** for the deterministic portion. Achieving (iii) while $T_n$'s point is dynamic is the
crux: nondeterminism must be "pinned" to a deterministic position before it can be replicated, or
deterministic txns must be shielded from in-flight nondeterministic state.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **Calvin** (SIGMOD 2012) and **Aria** (VLDB 2020) are purely deterministic;
  **Bohm** (deterministic MVCC) and **PWV** explore deterministic variants. The hybrid idea is
  newer: **QueCC** decouples planning from execution; some engines run a deterministic *fast path* for
  pre-declared one-shot txns and fall back to OCC/2PL for interactive ones — but a **unified,
  anomaly-free** coexistence over shared data is not a solved, shipped design. **FaunaDB** is
  deterministic end-to-end; **Spanner/CockroachDB** are nondeterministic (2PL+2PC / serializable
  MVCC). No mainstream system advertises sound concurrent mixed-mode execution.
- **Theory SOTA:** the deterministic-database analyses (Abadi–Faleiro, "An Overview of Deterministic
  Database Systems," CACM 2018) frame the trade-offs; the *composition* correctness theory for mixing
  modes is underdeveloped.

## 4. Upper Bound

A sound construction exists by **subordination**: treat nondeterministic txns as occupying reserved
sequence slots — i.e., assign each $T_n$ a deterministic sequence number *before* its effects become
visible, then execute it under local CC but commit it *as if* it were at that slot (a "deterministic
envelope" around an opportunistic execution). This yields strict serializability with $O(1)$ extra
ordering metadata per txn and no extra commit round for the deterministic majority; nondeterministic
txns that touch undeclared keys pay a reconnaissance/abort-retry cost. This is the best known *sound*
recipe, but it largely re-imposes determinism's constraints on the nondeterministic side, so its
**practical** value (how much flexibility survives) is unquantified.

## 5. Lower Bound

Any engine preserving determinism's **replica-equivalence** must ensure that the relative order of
every pair of conflicting transactions is **agreed before execution diverges** — for a nondeterministic
txn this means its serialization point must be communicated/fixed, costing $\ge 1$ coordination step
exactly when it conflicts with not-yet-executed deterministic work (a consequence of the FLP/CAP-style
need to agree on order under concurrency). Thus the coordination savings of determinism **cannot** be
retained for nondeterministic txns that conflict with the deterministic stream — there is no free lunch:
mixed conflicts cost at least the coordination that pure determinism avoids. No protocol can give both
full nondeterministic flexibility *and* zero-coordination determinism on the *same conflicting keys*.

## 6. The Gap

This is **open**. A sound construction exists (Section 4) but it is essentially "make the
nondeterministic side behave deterministically when it conflicts," which forfeits much of the flexibility
that motivated mixing. There is **no** design that demonstrably keeps the deterministic fast path
coordination-free while giving nondeterministic txns genuine flexibility *and* provable anomaly-freedom
over shared data — and no lower bound says one is impossible beyond the per-conflict coordination floor.
The gap is between a heavy-handed sound recipe and a hypothetical lightweight one; closing it needs either
a clever bridging protocol with quantified flexibility, or a hardness result pinning the cost of mixed-mode
conflicts.

## 7. Current Research (as of June 2026)

- **Adaptive per-transaction mode selection**: route pre-declarable one-shot txns to the deterministic
  path and interactive/dependent ones to MVCC/OCC, with a verified bridging invariant *(frontier — verify)*.
- **Deterministic MVCC** (Bohm-lineage) as a substrate that more naturally coexists with snapshot reads.
- Formal (TLA+/Coq) proofs of mixed-mode serializability to rule out boundary anomalies *(frontier — verify)*.
- Reconnaissance-free deterministic execution (learned read/write-set prediction) to widen the
  deterministic path's applicability and shrink the nondeterministic remainder.
Groups: Yale (Abadi, Faleiro), MIT, CMU (Pavlo), and deterministic-DB startups (Fauna lineage).

## 8. Future Work

- A bridging concurrency-control protocol with a **proven** flexibility/coordination trade-off.
- Characterizing exactly which transaction classes can stay coordination-free when mixed.
- Compiler/optimizer support to classify and route transactions automatically by declarability.
- Benchmarks combining interactive and one-shot workloads to measure mixed-mode quality.

## 9. Key References

- **[Foundational]** Thomson, A., Diaconu, T., Ren, K., et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[Survey]** Abadi, D., Faleiro, J. *An Overview of Deterministic Database Systems.* CACM, 2018.
- **[SOTA]** Lu, Y., Yu, X., Cao, L., Madden, S. *Aria: A Fast and Practical Deterministic OLTP Database.* VLDB, 2020.
- **[SOTA]** Faleiro, J., Abadi, D. *Rethinking Serializable Multiversion Concurrency Control (Bohm).* VLDB, 2015.
- **[Foundational]** Bernstein, P., Hadzilacos, V., Goodman, N. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.

---
*Part of the [DBMS Research catalog](../../README.md).*
