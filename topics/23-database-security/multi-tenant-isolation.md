# Multi-Tenant Isolation Guarantees

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/multi-tenant-isolation` · **Status:** empirically-open

## 1. Problem Statement

Cloud databases (DBaaS, serverless query engines, shared analytics warehouses) co-locate many *tenants* on shared physical resources: buffer pools, CPU caches, indexes, query-plan caches, statistics, connection pools, and sometimes shared tables with row-level security. **Isolation** means tenant $A$ can neither read nor *infer* tenant $B$'s data, and $B$'s workload cannot degrade $A$'s availability beyond agreed bounds.

The problem has two faces:

- **Logical isolation** (access control): provable absence of a *direct* read path between tenants. This is the easier, largely solved part (separate schemas/RLS/verified monitors).
- **Side-channel and resource isolation** (the open part): even with perfect access control, *shared state leaks information*. A tenant can infer another's data via timing of shared locks, cache occupancy, buffer-pool hit/miss patterns, query-plan/statistics caches, deduplication, compression ratios, and contention.

Decision/optimization variants:
- **(Decision)** Given a system design, does a side channel of bandwidth $> b$ bits/s exist between tenants?
- **(Quantitative)** Bound the leakage (mutual information / min-entropy) of shared-component design $X$.
- **(Optimization)** Maximize resource sharing (cost) subject to a leakage budget $\varepsilon$ and a performance-interference SLA.

Status is *empirically open*: deployed systems rely on measured/audited isolation and partitioning heuristics, not on a proof that no exploitable channel remains.

## 2. Mathematical Foundations

Model the shared system as a channel $C: \mathcal{D}_B \to \mathcal{O}_A$ mapping tenant $B$'s secret data to tenant $A$'s observations (latencies, hit rates). Leakage is quantified information-theoretically:
$$\mathcal{L} = I(D_B; O_A) \quad\text{or}\quad \text{min-entropy leakage } \mathcal{L}_\infty = \log_2 \frac{\sum_o \max_d P(o\mid d)P(d)}{\max_d P(d)}.$$
A design is *$\varepsilon$-isolating* if $\mathcal{L}\le\varepsilon$ over all admissible $B$-behaviors. **Noninterference** (Goguen–Meseguer) is the $\varepsilon=0$ ideal; practical systems seek *quantitative* / *probabilistic noninterference*.

Performance interference is captured by **noisy-neighbor** queueing models (shared-resource $M/G/1$-style contention) and by **differential privacy on resource usage** when only aggregate statistics are shared. Constant-time / oblivious techniques (ORAM, oblivious query processing) aim to make $O_A$ statistically independent of $D_B$, paying $\Omega(\log n)$ (Goldreich–Ostrovsky lower bound) overhead per access.

The optimization variant is a constrained packing: maximize tenants-per-host s.t. pairwise leakage $\le\varepsilon$ — related to graph coloring / interval packing and generally **NP-hard**.

## 3. State of the Art (SOTA)

- **Systems:** AWS Aurora/RDS, Azure SQL, Google Spanner/BigQuery use mixes of per-tenant VMs/containers, dedicated compute (Snowflake virtual warehouses), and shared storage with encryption. BigQuery/Snowflake isolate *compute* per tenant but share *storage and metadata*. Query-result and plan caches are increasingly partitioned after cross-tenant cache-timing concerns.
- **Side-channel defenses:** cache-partitioning (Intel CAT), constant-time crypto, page-coloring; **Oblivious databases** — ObliDB (Eskandarian–Zaharia), Opaque (Zheng et al., NSDI 2017) — give cryptographic obliviousness inside TEEs (SGX) at significant cost.
- **Theory:** quantitative information flow (Smith; Köpf–Basin) for bounding side-channel bandwidth; differential privacy applied to shared statistics.

## 4. Upper Bound

Strong isolation is *achievable* but expensive. Oblivious query processing (ORAM-backed storage, oblivious joins/sorts) provides $\varepsilon\!\to\!0$ data-access isolation at $O(\log n)$ to $O(\log^2 n)$ access overhead (path-ORAM) and constant-time operators. TEE-based systems (Opaque, ObliDB) reach near-zero memory-access leakage with 1.6×–46× slowdowns depending on operator. For *resource/performance* isolation, dedicated-compute-per-tenant (Snowflake-style) gives a clean upper bound: zero cross-tenant resource leakage at the cost of no statistical multiplexing. Quantitative-leakage upper bounds for specific shared components (e.g., a partitioned cache) are computable via QIF analysis.

## 5. Lower Bound

- **Obliviousness cost:** Goldreich–Ostrovsky proves any ORAM scheme hiding access patterns incurs $\Omega(\log n)$ amortized overhead — you *cannot* get perfect access-pattern isolation for free.
- **Sharing ⇒ channel:** any *observable* shared, contended resource carries a covert channel of strictly positive capacity; closing it requires either partitioning (lose sharing benefit) or adding noise/padding (lose performance). This is an information-theoretic impossibility of "free lunch" isolation under sharing.
- **CAP/availability tension:** strict performance isolation under bounded resources caps achievable multiplexing (a packing lower bound). The packing/placement optimization is NP-hard.
- No nontrivial *general* lower bound exists on detecting whether an arbitrary system has an exploitable channel — channel existence is undecidable in the general program setting (reduces to noninterference checking, a 2-safety hyperproperty).

## 6. The Gap

The gap is wide and empirical. We have (a) provably-isolating-but-costly designs (oblivious/TEE, dedicated compute) and (b) cheap shared designs whose *actual* leakage is measured, not bounded. There is **no accepted methodology to certify a production shared query engine as $\varepsilon$-isolating end-to-end** across all shared components simultaneously (buffers + plan cache + stats + locks + compression). Closing it requires composable leakage accounting across components and a way to trade leakage budget for sharing benefit with proofs, not benchmarks.

## 7. Current Research (as of June 2026)

- Serverless/disaggregated isolation: per-query micro-VMs (Firecracker) vs. shared runtimes; leakage of shared *metadata* and *autoscaling signals* *(frontier — verify)*.
- TEE-backed analytics (Intel TDX, AMD SEV-SNP, confidential VMs) making oblivious processing cheaper; new oblivious operators.
- QIF tooling to *bound* cache/plan-cache leakage automatically (Köpf, Pasareanu lineage).
- Differentially-private resource sharing and noisy metering to cap cross-tenant inference from billing/telemetry.
- Cross-tenant attacks on shared LLM/vector-index features in DBaaS *(frontier — verify)*.

## 8. Future Work

- Composable, component-wise leakage budgets that sum to a system-level guarantee.
- Cheap obliviousness for joins/aggregations (sub-log overhead, or hardware-assisted).
- Certified $\varepsilon$-isolation as a deployable contract with continuous monitoring.
- Formal account of plan-cache, statistics, and compression side channels specific to query engines.

## 9. Key References

- **[Foundational]** Goldreich, O., Ostrovsky, R. *Software Protection and Simulation on Oblivious RAMs.* JACM, 1996.
- **[Foundational]** Goguen, J., Meseguer, J. *Security Policies and Security Models.* IEEE S&P, 1982.
- **[SOTA]** Zheng, W., et al. *Opaque: An Oblivious and Encrypted Distributed Analytics Platform.* NSDI, 2017.
- **[SOTA]** Eskandarian, S., Zaharia, M. *ObliDB: Oblivious Query Processing for Secure Databases.* VLDB, 2019.
- **[Survey]** Smith, G. *On the Foundations of Quantitative Information Flow.* FoSSaCS, 2009.
- **[Survey]** Köpf, B., Basin, D. *An Information-Theoretic Model for Adaptive Side-Channel Attacks.* CCS, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
