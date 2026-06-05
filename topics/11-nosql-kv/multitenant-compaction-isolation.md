# Multi-Tenant Compaction Isolation

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/multitenant-compaction-isolation` · **Status:** empirically-open

## 1. Problem Statement

In a shared LSM-tree-based KV service (RocksDB, Cassandra, ScyllaDB, HBase) many tenants share the same physical nodes, disk bandwidth, page cache, and a pool of background **compaction** threads. Compaction is a write-amplifying, IO- and CPU-heavy background process; when one tenant ingests heavily, its compaction work and write-stalls can consume shared IO and block another tenant's foreground reads. The problem: **schedule compaction and IO so that each tenant receives an isolation guarantee** — e.g., bounded read-latency degradation or a guaranteed share of throughput — regardless of neighbors' write behavior.

- **Decision variant:** Given per-tenant SLOs (e.g., $p99$ read latency $\leq L_i$) and a compaction/IO schedule, are all SLOs simultaneously satisfiable on this hardware?
- **Optimization variant:** Choose, online, which tenant's SSTables to compact, when, and with what IO rate, to maximize a fairness/utility objective (e.g., max-min throughput, or minimize worst-case SLO violation) subject to space-amplification caps.
- **Mechanism-design variant:** Charge/account compaction debt to the tenant that created it so cross-tenant interference is internalized.

"Solving" means a scheduler with provable (or at least robustly empirical) interference bounds: tenant $i$'s read tail is a bounded function of *its own* workload, not of $\sum_{j\neq i}$ write rates.

## 2. Mathematical Foundations

Each tenant's data lives in an LSM with levels $L_0,\dots,L_k$, size ratio $T$. A tenant ingesting at rate $w_i$ generates compaction IO of roughly $w_i \cdot O(T\log_T(N_i/B))$ bytes (write amplification of leveled compaction), where $N_i$ is data size and $B$ buffer size. Total background IO demand is $\sum_i w_i \cdot \text{WA}_i$; foreground read demand competes for the same bounded device bandwidth $C$.

This is a **multi-resource scheduling / fair-queuing** problem. Relevant theory: **Dominant Resource Fairness** (DRF, Ghodsi et al., NSDI 2011) for sharing CPU+IO+memory; **mClock** (Gulati, OSDI 2010) for proportional-share + reservation + limit IO scheduling; and **stochastic latency analysis** — read latency is governed by the number of overlapping SSTables (the "read amplification" $\propto$ levels + $L_0$ files), which a starved compactor lets grow. Write-stall onset is a queueing threshold: when $L_0$ file count exceeds a trigger, ingestion is throttled, coupling tenants through a shared backpressure signal. Formally one wants a schedule that keeps each tenant's $L_0$/overlap bounded so its read cost stays $O(\log N_i)$ while respecting $\sum$ IO $\le C$.

## 3. State of the Art (SOTA)

- **Systems SOTA:** RocksDB supports rate-limited compaction (token-bucket `WriteController`/`RateLimiter`), per-column-family compaction priorities, and subcompactions; but cross-tenant isolation is best-effort. **ScyllaDB** uses a userspace IO scheduler (Seastar) with per-class shares and a controller that allocates bandwidth between reads, writes, and compaction via feedback control — the strongest production isolation. **Cassandra** offers compaction throughput throttling and per-table strategies. Cloud KV services (DynamoDB, Bigtable) isolate tenants largely by *partitioning onto separate resource units* rather than truly sharing compaction.
- **Theory SOTA:** No tight scheduling result specific to LSM compaction isolation; the closest formal grounding is DRF/mClock fairness and competitive analysis of IO scheduling, plus LSM cost models (Dostoevsky/Monkey, Dayan & Idreos) that quantify per-tenant read/write/space amplification.

## 4. Upper Bound

Proportional-share IO schedulers (mClock) provably enforce **reservations, limits, and weighted shares** with bounded service lag, giving each tenant a guaranteed fraction of $C$. Combined with per-tenant LSM cost models, one can *bound* read amplification if compaction for tenant $i$ is guaranteed share $\ge w_i \cdot \text{WA}_i / C$. ScyllaDB-style feedback controllers empirically hold $p99$ within target under adversarial neighbors. The achievable guarantee is essentially: *if* the device has slack ($\sum_i w_i\text{WA}_i + \text{read demand} \le C$), weighted fair queuing keeps interference bounded; this is the best known constructive upper bound.

## 5. Lower Bound

When the device is **saturated** ($\sum_i w_i \text{WA}_i$ exceeds available background bandwidth), isolation is *impossible* without throttling ingestion — a pigeonhole/conservation argument: bytes that must be compacted exceed bytes the device can move, so either some tenant's reads degrade (overlap grows) or some tenant's writes stall. This mirrors a scheduling lower bound: no work-conserving scheduler can give every tenant both full write admission and bounded read tail under overload. Online competitiveness suffers too — without knowledge of future ingestion bursts, any online compaction scheduler is $\Omega(1)$-competitive away from the offline optimum on adversarial arrival sequences (standard online-scheduling lower bounds). There is no published tight, LSM-specific lower bound, which is precisely why the status is **empirically-open**.

## 6. The Gap

There is no formal model that maps (per-tenant ingest rates, data sizes, compaction policy, device bandwidth) to a *provable* per-tenant read-tail guarantee, nor a matching lower bound delineating the feasible SLO region. Production systems demonstrate *empirically* strong isolation (ScyllaDB) but offer no worst-case guarantee, and behavior under adversarial bursty multi-tenant workloads is not characterized. Closing the gap needs (a) a tractable queueing/scheduling model of compaction-induced interference and (b) a scheduler proven to track its feasible frontier.

## 7. Current Research (as of June 2026)

- Feedback-controlled IO schedulers extending Seastar's controller to formal stability guarantees; learned controllers that predict write-stall onset. *(frontier — verify)*
- Compaction "debt" accounting and chargeback so tenants pay for their own write amplification; admission control that rejects ingestion threatening neighbor SLOs.
- Serverless/disaggregated KV (compaction offloaded to a separate compute tier, e.g., Rockset-style or remote compaction in cloud RocksDB forks) to physically decouple tenant compaction. *(frontier — verify)*
- Groups: Harvard DASlab (Idreos, Dayan — LSM cost models), VMware/Seastar lineage, ScyllaDB engineering, and cloud-KV teams (AWS, Google).

## 8. Future Work

- A provable feasible-region characterization for multi-tenant LSM SLOs.
- Online compaction scheduling with regret/competitive guarantees under bursty tenants.
- Tenant-aware compaction policy selection (leveled vs tiered per tenant) under a shared IO budget.
- Coordinating write-stall backpressure so it is charged to the offending tenant only.

## 9. Key References

- **[Foundational]** Gulati, A., Merchant, A., Varman, P. *mClock: Handling Throughput Variability for Hypervisor IO Scheduling.* OSDI, 2010.
- **[Foundational]** Ghodsi, A. et al. *Dominant Resource Fairness: Fair Allocation of Multiple Resource Types.* NSDI, 2011.
- **[SOTA]** Dayan, N., Idreos, S. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores.* SIGMOD, 2018.
- **[SOTA]** Kakaraparthy, A. et al. / Cao, Z. et al. *Characterizing, Modeling, and Benchmarking RocksDB Key-Value Workloads at Facebook.* FAST, 2020.
- **[Systems]** Kivity, A. et al. *Seastar / ScyllaDB IO Scheduler.* (design docs / ScyllaDB engineering), 2017–.

---
*Part of the [DBMS Research catalog](../../README.md).*
