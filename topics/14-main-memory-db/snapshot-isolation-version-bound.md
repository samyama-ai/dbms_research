---
id: 14-main-memory-db/snapshot-isolation-version-bound
title: "Snapshot Isolation Without Version Explosion"
topic: 14-main-memory-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Snapshot Isolation Without Version Explosion

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/snapshot-isolation-version-bound` · **Status:** open

## 1. Problem Statement
Main-memory databases overwhelmingly use **multi-version concurrency control (MVCC)**: each write creates a new tuple version, and transactions read from a consistent **snapshot**. This gives readers a stall-free view and enables **Snapshot Isolation (SI)** and, with extra checks, **Serializable Snapshot Isolation (SSI)**. The cost is a **version store** that grows with the write rate; old versions can only be reclaimed (garbage-collected) once no active or future transaction can read them. A single **long-running read transaction** pins the *global low-water mark*, preventing reclamation and causing **version explosion** — unbounded memory growth, longer version-chain traversals, and degraded performance.

**Problem:** provide **serializable** snapshot isolation in memory with a **provable bound** on version-store size (and on version-chain length / reclamation lag), independent of (or gracefully degrading with) the presence of long readers, while preserving throughput. Variants:
- **Decision:** Given a workload and memory budget $M$, can SSI be guaranteed without exceeding $M$ versions?
- **Optimization:** Minimize peak version-store size subject to an isolation-level guarantee and abort-rate ceiling.
- **Online GC:** When/what to reclaim without future knowledge, bounding lag.

## 2. Mathematical Foundations
Each logical tuple has a version chain ordered by commit timestamp. A transaction $T$ with start timestamp $t_s$ reads, for each tuple, the latest version with commit ts $\le t_s$. A version $v$ is **garbage** iff no active transaction's snapshot, and no transaction that may yet start, can read $v$ — i.e., once a newer version is visible to all current and future snapshots. The reclamation frontier is the **global minimum active start timestamp** $t_{\min} = \min_{T \in \text{active}} t_s(T)$; versions superseded before $t_{\min}$ are collectable. Version-store size is bounded by
$$|\text{versions}| \le n + W \cdot (\text{now} - t_{\min}),$$
where $W$ is write throughput — so a single old long reader (small $t_{\min}$) makes the bound blow up linearly in its duration.

**Serializability** of SI requires preventing *write-skew*: SI permits non-serializable schedules with **dangerous structures** — two consecutive rw-antidependency edges in the serialization graph (Adya; Fekete et al.). **SSI** (Cahill–Röhm–Fekete) tracks rw-conflicts and aborts to break these, achieving serializability with bounded overhead. Bounding versions interacts with isolation: aggressive GC can violate snapshots; conservative GC explodes memory.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** **Hekaton** (Diaconu et al., SIGMOD 2013) — lock-free in-memory MVCC with optimistic validation. **HyPer's MVCC** (Neumann, Mühlbauer, Kemper, SIGMOD 2015) — *serializable* MVCC with precision-locking-style validation and efficient version maintenance, with careful GC. **Cicada** (Lim, Kaminsky, Andersen, SIGMOD 2017) — high-performance multi-core MVCC with best-effort inlining and rapid GC. **Steam / vacuuming** GC (Böttcher, Leis, Neumann, Kemper, *Scalable Garbage Collection for In-Memory MVCC Systems*, VLDB 2019) directly attacks version pruning, intra-version-chain cleaning, and the long-reader problem.
- **Theory-SOTA.** **Serializable Snapshot Isolation** (Cahill, Röhm, Fekete, SIGMOD 2008 / TODS 2009) — the canonical method to make SI serializable by detecting dangerous rw-edge structures.

No system gives a *provable* version-store bound that survives adversarial long readers — it remains open.

## 4. Upper Bound
With timestamp-frontier GC, version count is $O(n + W \cdot \Delta)$ where $\Delta = \text{now} - t_{\min}$ is the reclamation lag. **Steam-style** GC reduces constants and prunes intermediate (non-visible) versions eagerly, and supports *interval-based* GC that can collect versions invisible to *all* snapshots even when $t_{\min}$ is old — improving the practical bound when long readers touch few tuples. Snapshot/checkpoint techniques (copy-on-write virtual snapshots, HyPer's fork-based snapshots) let a long reader run against a *separate frozen snapshot*, decoupling it from the live version store and capping live versions at $O(n + W\cdot\delta)$ for short $\delta$. SSI adds $O(1)$ amortized conflict-tracking per access.

## 5. Lower Bound
There is an **information-theoretic / adversarial lower bound**: to serve a read transaction a consistent snapshot taken at time $t_s$, the system must retain *some* representation of every value as of $t_s$ that the reader might access. An adversarial long reader that may access *any* tuple forces retention of the entire as-of-$t_s$ state until it finishes — so peak memory $\Omega(n + W\cdot \tau)$ for reader duration $\tau$ is unavoidable in the worst case *without* materializing a separate snapshot (which itself costs $\Omega(n)$ space). Thus no SSI scheme can bound version-store growth below the reader's footprint times its lifetime in the adversarial model — a genuine impossibility. Additionally, providing serializability under SI inherently requires either aborts (SSI) or locking; first-committer/first-updater-wins aborts are necessary to prevent write-skew, lower-bounding the abort rate for adversarial write-skew workloads.

## 6. The Gap
Practical GC (Steam, Cicada, HyPer fork-snapshots) handles realistic workloads well, but the **adversarial long-reader bound** shows version-store growth cannot be bounded below the reader's reachable footprint times its duration. The open gap: is there a scheme that achieves a **provable** bound — e.g., $O(n + W\cdot\delta)$ live versions *regardless* of long readers by offloading them to bounded-cost separate snapshots — *without* paying $\Omega(n)$ per snapshot or degrading throughput, and while staying serializable? No design simultaneously proves bounded version-store size, serializability, and high throughput under arbitrary long readers. It is **genuinely open**.

## 7. Current Research (as of June 2026)
Directions: interval/epoch-based and "two-version" GC that decouples long readers; learned/predictive GC scheduling; delta-compressed and columnar version stores reducing the per-version cost; offloading long analytical readers to HTAP snapshot replicas (SAP HANA, Umbra, TUM lines) so OLTP version stores stay bounded; and formal verification of GC safety. Groups: TU Munich (Neumann, Kemper, Leis — Steam, Umbra), CMU (Pavlo, Andersen — Cicada), Microsoft Research (Hekaton), and the isolation-theory community (Fekete, Adya lineage). Provably bounded version stores under HTAP snapshot offloading are an active 2025-2026 frontier *(frontier — verify)*.

## 8. Future Work
- A serializable MVCC scheme with a *proven* version-store bound independent of long-reader duration (via bounded-cost snapshot offload).
- Tight upper/lower bounds for adversarial write-skew abort rates under SSI.
- Compressed/columnar version stores with provable space and chain-traversal bounds.
- Machine-checked proofs of GC safety co-designed with the isolation level.

## 9. Key References
- **[Foundational]** Cahill, Röhm, Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD 2008 / ACM TODS, 2009. — [DOI](https://doi.org/10.1145/1620585.1620587)
- **[SOTA]** Neumann, Mühlbauer, Kemper. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2749436)
- **[SOTA]** Böttcher, Leis, Neumann, Kemper. *Scalable Garbage Collection for In-Memory MVCC Systems (Steam).* VLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364328)
- **[SOTA]** Lim, Kaminsky, Andersen. *Cicada: Dependably Fast Multi-Core In-Memory Transactions.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064015)
- **[SOTA]** Diaconu, Freedman, Ismert, Larson, Mittal, Stonecipher, Verma, Zwilling. *Hekaton: SQL Server's Memory-Optimized OLTP Engine.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2463710)
- **[Foundational]** Berenson, Bernstein, Gray, Melton, O'Neil, O'Neil. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995. — [DOI](https://doi.org/10.1145/223784.223785)

## 10. Worked Example

A tuple $x$ has version chain $x_0$ (commit ts 10) $\to x_1$ (ts 20) $\to x_2$ (ts 30). Active transactions: a long analytical reader $T_L$ started at $t_s=12$, plus short writers continuously committing. The reclamation frontier is $t_{\min}=\min$ active start $=12$.

$T_L$ reads the latest version with commit ts $\le 12$, namely $x_0$. So $x_0$ cannot be collected. Even though $x_1,x_2$ supersede it for everyone newer, $T_L$ pins $x_0$ until it finishes.

Now apply the bound $|\text{versions}| \le n + W\cdot(\text{now}-t_{\min})$. With write rate $W=10^5$/s and $T_L$ running $\tau=60$ s, the store accumulates up to $6\times10^6$ extra versions — pure version explosion from one old reader.

Steam-style interval GC helps if $T_L$ touches few tuples: versions of keys $T_L$ never reads are invisible to *all* snapshots and collectable despite the old $t_{\min}$. Fork-snapshot offload instead frees $x_0$ entirely by serving $T_L$ from a frozen copy, restoring the live bound to $O(n + W\cdot\delta)$ for small $\delta$.

---
*Part of the [DBMS Research catalog](../../README.md).*
