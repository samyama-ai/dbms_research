---
id: 19-temporal-databases/versioning-gc-policy
title: "Versioning Garbage Collection Policy"
topic: 19-temporal-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Versioning Garbage Collection Policy

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/versioning-gc-policy` · **Status:** empirically-open

## 1. Problem Statement
System-versioned and MVCC-style stores accumulate obsolete tuple versions. A **garbage
collection (GC) policy** decides *which* versions to physically reclaim and *when*, subject to
a **retention contract**: time-travel SLAs (e.g., "any AS-OF query within the last 30 days must
succeed"), long-running snapshot transactions, replicas, and legal/audit holds. The problem:
design a *provably safe* policy — never reclaim a version that some admissible reader may still
need — that is simultaneously *cost-effective* (minimize storage, reclamation I/O, and the
read-amplification GC induces). Variants: (a) **decision/safety** — given retention bounds and
the set of live snapshots, is version $v$ reclaimable? (b) **optimization (online)** — choose a
reclamation schedule minimizing expected storage-time cost under an unknown future request
stream (competitive analysis); (c) **counting/sizing** — bound the steady-state version count
under an arrival/expiry process.

## 2. Mathematical Foundations
Model storage as a set of versions $v$, each with a *validity window in transaction time*
$[\text{born}(v), \text{dead}(v))$ and a chain per key. The **reachable set** at GC time is
$\mathcal{R} = \{ v : \exists\, \text{admissible read time } \tau,\ \tau \in [\text{born}, \text{dead})\}$,
where admissible $\tau$ are determined by the **retention horizon** $H$ (so $\tau \ge \mathrm{now} - H$)
plus the **low-water mark** $\mathrm{lwm} = \min$ start-time over active snapshots/transactions.
Safety: reclaim $v$ only if $\mathrm{dead}(v) < \min(\mathrm{lwm}, \mathrm{now}-H)$. This is the
MVCC GC invariant (the version is dominated by a newer one before any live reader).

Cost is a **storage-rent** integral $\int (\text{bytes live}) \, dt$ plus reclamation work; the
online schedule is naturally analyzed as a variant of **ski-rental / online rent-or-buy** (defer
GC and pay storage rent, or reclaim now and pay I/O) and as a **caching/eviction** problem where
"keep version" $\approx$ keep in cache, giving a connection to the $k$-server / weighted-caching
lower bounds. Steady-state version count follows from a queueing/birth-death model: with version
creation rate $\lambda$ and retention $H$, expected live versions $\approx \lambda H$ (Little's
law), plus the tail held by long snapshots.

## 3. State of the Art (SOTA)
**Systems SOTA:** PostgreSQL's `VACUUM` (and the long-running-transaction "xmin horizon"
problem), Oracle Undo/Flashback retention, SQL Server snapshot version store, and LSM/HTAP
designs. Recent research targets MVCC GC bottlenecks: **HyPer/Umbra** GC, **Steam** (Böttcher,
Neumann et al., *Scalable Garbage Collection for In-Memory MVCC Systems*, VLDB 2019) which
bounds version-chain traversal, and **HANA / Hekaton** cooperative cleaners. Time-travel/data-lake
systems (Delta Lake, Apache Iceberg, Snowflake Time Travel + Fail-safe) implement
*retention-window* GC by snapshot expiration and manifest rewriting. For data lakes, GC = orphan
file / expired snapshot removal under a retention SLA.

## 4. Upper Bound
Safety checking is cheap: maintaining $\mathrm{lwm}$ and horizon $H$, reclaimability of a version
is $O(1)$ amortized; Steam-style chain pruning reclaims in time linear in versions removed with
bounded traversal, $O(1)$ amortized per version in the **RAM model**. For the *online
storage-vs-I/O* tradeoff, the ski-rental reduction gives a deterministic **2-competitive** policy
(reclaim once accumulated rent equals reclamation cost) and a randomized
$\tfrac{e}{e-1} \approx 1.58$-competitive policy, against an offline optimum that knows future
reads — these bounds are inherited, not proven tight for the temporal-GC structure.

## 5. Lower Bound
Any deterministic online rent-or-buy GC policy is **$\ge 2$-competitive** and any randomized one
**$\ge \tfrac{e}{e-1}$-competitive** (classical ski-rental lower bounds, oblivious/adaptive
adversary model). When versions interact across keys with shared pages, the eviction problem
generalizes weighted caching, whose deterministic competitive ratio lower bound is $k$ (cache
size), so page-granular GC inherits an $\Omega(k)$ barrier. *Safety* is not hard; the hardness is
**online optimality under unknown future time-travel demand**, plus the empirical fact that real
workloads' future AS-OF demand is essentially unpredictable, which is why the problem is tagged
empirically-open rather than closed by these competitive constants.

## 6. The Gap
Safety is solved; *cost-optimality is not*. The competitive bounds above hold for the abstract
rent-or-buy reduction, but real systems face (i) **page/cluster granularity** (cannot reclaim a
single version without rewriting a block), (ii) correlated retention holds (one long snapshot
pins everything), and (iii) read-amplification from delaying GC. No policy is known to be optimal
across these coupled costs, and no benchmark consensus exists, so the gap between any
deployed heuristic and a true cost-optimal schedule is **empirically unquantified**. Closing it
needs either workload models with provable guarantees or learned policies with regret bounds.

## 7. Current Research (as of June 2026)
Active directions: **learned / ML-guided GC and retention prediction** for cloud warehouses
*(frontier — verify)*; tightening MVCC GC for high-core-count in-memory engines (Neumann/Böttcher
line, TU Munich); Iceberg/Delta **snapshot-expiry and orphan-file GC** scaling for petabyte
lakes, including cost-based compaction-vs-retention scheduling *(frontier — verify)*. Long-running
analytical transactions on HTAP systems (the "long reader pins the horizon" problem) remain a
focus, with proposals for **per-tuple visibility deltas** and **decoupled retention tiers**
(hot reclaim fast, cold archived) *(frontier — verify)*.

## 8. Future Work
- Online GC policies with provable competitive ratios under page-granular reclamation.
- Workload-aware / learned retention with regret guarantees against AS-OF demand.
- Decoupling time-travel SLA tiers from physical GC to bound the horizon-pinning effect.
- Benchmarks measuring storage-time cost, read-amplification, and SLA-miss rate jointly.

## 9. Key References
- **[Foundational]** D. Lomet et al. *Transaction Time Support Inside a Database Engine* (Immortal DB
  project). ICDE, 2006. — [DBLP](https://dblp.org/rec/conf/icde/LometBMS06.html)
- **[SOTA]** J. Böttcher, V. Leis, T. Neumann, A. Kemper. *Scalable Garbage Collection for
  In-Memory MVCC Systems.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364328)
- **[Foundational]** P. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database
  Systems* (MVCC foundations). Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)
- **[Foundational]** A. Karlin, M. Manasse, L. Rudolph, D. Sleator. *Competitive Snoopy
  Caching / Ski-Rental.* Algorithmica, 1988. — [DOI](https://doi.org/10.1007/BF01762111)
- **[SOTA]** M. Armbrust et al. *Delta Lake: High-Performance ACID Table Storage over Cloud
  Object Stores.* PVLDB, 2020. — [DOI](https://doi.org/10.14778/3415478.3415560)

## 10. Worked Example

A single key's transaction-time version chain, with retention horizon $H = 30$ and "now" $= 100$, so the horizon cutoff is $\mathrm{now} - H = 70$:

| version | $[\text{born}, \text{dead})$ |
|--|--|
| $v_1$ | $[10, 40)$ |
| $v_2$ | $[40, 65)$ |
| $v_3$ | $[65, 90)$ |
| $v_4$ | $[90, \infty)$ (live) |

One long-running snapshot transaction started at $\mathrm{lwm} = 55$. The safety rule: reclaim $v$ only if $\mathrm{dead}(v) < \min(\mathrm{lwm}, \mathrm{now}-H) = \min(55, 70) = 55$.

- $v_1$: $\mathrm{dead}=40 < 55$ → reclaimable.
- $v_2$: $\mathrm{dead}=65 \not< 55$ → **pinned** (the snapshot at $55$ falls inside $[40,65)$, so it may still read $v_2$).
- $v_3, v_4$: visible to current/recent readers → keep.

So only $v_1$ is collected. Note the **horizon-pinning** effect: drop the long snapshot and $\mathrm{lwm}$ jumps to $\mathrm{now}-H = 70$, making $v_2$ ($\mathrm{dead}=65<70$) reclaimable too. One long reader thus pins extra storage — the coupled cost that makes online cost-optimality (§6) hard.

---
*Part of the [DBMS Research catalog](../../README.md).*
