---
id: 04-indexing-access-methods/disaggregated-index
title: "Tree indexes on disaggregated storage"
topic: 04-indexing-access-methods
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Tree indexes on disaggregated storage

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/disaggregated-index` · **Status:** empirically-open

## 1. Problem Statement
**Disaggregated storage** separates compute nodes from a remote storage tier (cloud object stores like S3, or RDMA-attached far memory / NVMe-over-fabric pools) connected by a network. The storage tier is **high-latency** (hundreds of µs to tens of ms), **paginated/coarse-grained** (object stores bill and serve in large blocks; you cannot cheaply read 8 bytes), and often **bandwidth-metered**. Classic B-tree and LSM access methods assume cheap, fine-grained local I/O — assumptions that collapse here: a B-tree root-to-leaf descent becomes a *chain of dependent network round-trips*, each amplified to a full page/object fetch.

The problem: **design tree/ordered access methods optimized for compute/storage separation — minimizing dependent round-trips, request count, and bytes transferred — while preserving consistency under concurrent multi-compute access and caching.**

- **Optimization variant:** minimize a weighted cost of network round-trips, request count, and bytes moved per lookup/scan, subject to a local-cache budget.
- **Decision variant:** can an ordered index serve point lookups in $O(1)$ *dependent* round-trips with $\tilde O(n)$ remote space?
- **Consistency variant:** maintain a globally consistent index across many stateless compute nodes sharing one storage tier.

*Empirically-open:* cloud-native engines (Aurora, Socrates, Neon, ROART/Sherman-style RDMA indexes) demonstrate big practical wins, but no access method is *proven* optimal for the paginated/high-latency disaggregated cost model, and the round-trip lower bounds are not tight.

## 2. Mathematical Foundations
Replace the single-cost DAM model with a **disaggregated cost model** parameterized by round-trip latency $\lambda$, per-request overhead, page/object size $P$, and bandwidth $\beta$:
$$\text{cost}(q) = \lambda \cdot (\text{dependent round-trips}) + (\text{requests}) \cdot c_{\text{req}} + (\text{bytes}) / \beta.$$
The dominant term is usually **dependent round-trips**, because they cannot be pipelined. Key tools:

- **Latency-bound / external-memory hybrids:** a B-tree of fanout $B$ has depth $\log_B n$ dependent fetches; increasing $B$ (fatter nodes) trades bytes for fewer round-trips — an explicit $\lambda$-vs-$\beta$ optimization.
- **RDMA one-sided vs. two-sided:** one-sided reads bypass remote CPU but force the client to *traverse* remotely, multiplying round-trips; caching internal nodes locally cuts the dependent chain (Sherman, FUSEE designs).
- **Consistency:** with many stateless compute nodes, index updates need a coordination protocol; **disaggregated concurrency control** and lease/versioning bounds apply; CAP-style tradeoffs surface when the storage tier partitions.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Amazon Aurora** ("the log is the database," SIGMOD 2017) and **Socrates** (Azure SQL DB, SIGMOD 2019) pioneered storage disaggregation; **Neon** (Postgres-on-S3) separates compute and pageserver. For *indexes specifically*: **Sherman** (Wang et al., SIGMOD 2022) is an RDMA-based disaggregated B+-tree using hierarchical locks and write-combining; **FUSEE** and **ROLEX/learned** disaggregated indexes; **dLSM / Nova-LSM** (Huang et al., SIGMOD 2021) disaggregates LSM compaction and storage. Object-store-native B-trees underlie **DuckDB-on-S3** and lakehouse table formats.
- **Theory-SOTA:** no clean optimality theorem; the closest formal grounding is the external-memory model generalized with a latency term, and round-complexity bounds from distributed data structures.

## 4. Upper Bound
A B-tree with fanout tuned to the object/page size $P$ gives point lookups in $O(\log_P n)$ **dependent round-trips** and scans in $O(r/P)$ requests; caching the top $h$ levels locally reduces the dependent chain to $O(\log_P n - h)$. Sherman demonstrates near-constant effective round-trips for hot paths via internal-node caching plus one-sided RDMA, with throughput scaling across compute nodes. These are **constructions in the disaggregated/RDMA cost model**, systems-SOTA — not proven round-optimal. Write-combining and batching reduce request count by amortizing $c_{\text{req}}$.

## 5. Lower Bound
Lower bounds here are **round-complexity / communication** in flavor: any ordered index resolving a predecessor over $n$ remote keys with bounded local cache must, in the worst case, incur $\Omega(\log_{P} n)$ dependent fetches unless it precomputes structure that itself costs space/bandwidth — a direct lift of the external-memory $\Omega(\log_B n)$ search bound with $B \to P$. For the **consistency** dimension, **CAP/FLP**-style impossibility applies: under network partition between compute and storage, the index cannot be both linearizable and available. No tight latency-model-specific lower bound (jointly over round-trips, requests, and bytes) is established.

## 6. The Gap
The gap is between **strong empirical systems** (Aurora/Socrates/Sherman show order-of-magnitude wins) and the **absence of a cost model with matching upper/lower bounds** for the paginated, high-latency, metered setting. It is open what the optimal dependent-round-trip vs. local-cache vs. bandwidth tradeoff is, and whether caching can provably reduce ordered lookups to $O(1)$ dependent round-trips with sublinear local memory. Closing it needs a formal disaggregated access-method model and tight round/communication lower bounds within it.

## 7. Current Research (as of June 2026)
- **Learned and cache-aware disaggregated indexes** that prefetch internal nodes to collapse the dependent chain, with provable round-trip bounds *(frontier — verify)*.
- **CXL / far-memory** access methods exploiting cache-line-granular (not page-granular) remote access, changing the $P$ parameter *(frontier — verify)*.
- **Multi-writer disaggregated B-trees** with scalable concurrency control and consistency under stateless compute.
- **Compaction on disaggregated storage** (ties to compaction-scheduling) where bandwidth is metered.
- Groups: Xingda Wei / Haibo Chen (SJTU, Sherman/FUSEE), Tianzheng Wang (SFU), CMU (Pavlo), MIT (Kraska), Microsoft/Amazon cloud-DB teams.

## 8. Future Work
- A disaggregated cost model with proven round/bandwidth-optimal ordered indexes.
- Provable cache-budget vs. round-trip tradeoffs for tree descents.
- Consistency protocols for multi-writer indexes tolerating compute/storage partition.

## 9. Key References
- **[Foundational]** A. Verbitski, et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056101)
- **[SOTA]** P. Antonopoulos, et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3314047)
- **[SOTA]** Q. Wang, et al. *Sherman: A Write-Optimized Distributed B+Tree Index on Disaggregated Memory.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2112.07320)
- **[SOTA]** H. Huang, S. Ghandeharizadeh. *Nova-LSM: A Distributed, Component-based LSM-tree Key-value Store.* SIGMOD, 2021. — [arXiv](https://arxiv.org/abs/2104.01305)
- **[Foundational]** A. Aggarwal, J. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)

## 10. Worked Example

Index $n=10^9$ keys on an S3-style tier: round-trip $\lambda=10$ ms, object size $P=16{,}384$ keys/node, bandwidth $\beta$ ample so the round-trip term dominates.

A B-tree of fanout $P$ has depth $\log_P n=\log_{16384}10^9=\frac{\ln 10^9}{\ln 16384}\approx\frac{20.7}{9.7}\approx 2.1$, so $3$ levels. A point lookup is a *chain of dependent fetches* — root, internal, leaf — that cannot be pipelined:
$$\text{cost}=3\cdot\lambda=30\text{ ms}.$$

Now **cache the top $h=2$ levels** locally (root + internal layer = $1+16384$ nodes, easily resident). The dependent chain collapses to $\log_P n - h = 1$ remote fetch:
$$\text{cost}=1\cdot\lambda=10\text{ ms} \quad(3\times\text{ faster}).$$

Compare a fanout-$256$ B-tree (smaller nodes): depth $\log_{256}10^9\approx 3.7\Rightarrow 4$ levels, $40$ ms uncached. Fatter nodes trade more bytes/fetch for fewer dependent round-trips — the explicit $\lambda$-vs-$\beta$ tradeoff. The open question: can caching a *sublinear* number of nodes drive lookups to $O(1)$ dependent round-trips with a matching lower bound?

---
*Part of the [DBMS Research catalog](../../README.md).*
