---
id: 08-distributed-databases/disaggregated-shuffle
title: "Disaggregated-Storage Shuffle Design"
topic: 08-distributed-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Disaggregated-Storage Shuffle Design

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/disaggregated-shuffle` · **Status:** empirically-open

## 1. Problem Statement
In disaggregated architectures, compute and storage scale independently: shuffle intermediate data is written to and read from a remote object/blob store (S3, GCS, EBS-style) rather than colocated local disks. This decouples elasticity (add/remove workers freely, tolerate stragglers and spot reclamation) from the all-to-all exchange, but pays a price in latency, request overhead, and per-byte storage/egress cost. The problem: **design a shuffle layer over disaggregated/object storage** that (a) lets the number of map and reduce workers change *between or during* a shuffle, (b) minimizes the dominant cost — number of object-store requests and bytes — under the store's per-request and per-byte pricing, and (c) preserves fault tolerance without re-running upstream stages.

Variants:
- **Optimization:** minimize total cost $= \alpha \cdot (\text{\\#requests}) + \beta \cdot (\text{bytes}) + \gamma \cdot (\text{latency})$ subject to a parallelism schedule.
- **Decision:** can a shuffle of $N$ bytes between $m$ mappers and $r$ reducers be realized with $\le Q$ object-store operations?
- **Elastic/online:** worker count is revealed online (autoscaling, spot churn); choose write/read granularity adaptively.

It is "empirically-open": several production systems demonstrate large wins, but there is no tight cost model or lower bound on object-store operations for an elastic shuffle.

## 2. Mathematical Foundations
A shuffle is an $m \times r$ all-to-all data movement. With local-disk shuffle, each of $m$ mappers writes $r$ partitions, so $m\cdot r$ logical segments. On object storage the **per-request cost** dominates because reads/writes are billed and latency-bound per object, giving a granularity tradeoff:
$$ \text{\\#ops} \;=\; \Theta(m \cdot r) \ \ \text{(fine-grained)} \quad\text{vs}\quad \Theta(m + r) \ \ \text{(coarse, via a merge/intermediary)} . $$
A merge step (push-based aggregation, à la Magnet/Cosco) trades extra bytes for fewer requests, an instance of an **I/O / external-memory tradeoff**: with block size $B$ and store-op cost, the shuffle resembles a transposition in the **external-memory (DAM) model** where transposing an $m\times r$ matrix costs $\Theta\!\big(\frac{mr}{B}\log_{M/B}\frac{mr}{B}\big)$ I/Os in the worst case. Elasticity adds a **scheduling** dimension: the partition function must be **decoupled from physical worker count** (e.g., hash to a large logical key space, then range-assign logical partitions to whatever workers exist), so reassignment costs $O(1)$ metadata rather than re-reading data. Fault tolerance reduces to durability of the intermediate objects: once written, a reducer failure costs only a re-read, not upstream recomputation (lineage truncation).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Amazon **EMR/S3 shuffle**, **Apache Celeborn** (formerly RSS, remote shuffle service), **Uber/LinkedIn push-based shuffles**, Meta **Cosco/Zeus**, Google **Dataflow Shuffle** (fully managed disaggregated shuffle), and serverless analytics (**Lambada**, **Starling**, **Boxer**, **Pixels-serverless**) that shuffle through object storage. Snowflake and Databricks separate compute from storage and use managed/temp object-store spill for large shuffles.
- **Theory-SOTA:** External-memory/cache-oblivious transposition and sorting bounds (Aggarwal–Vitter; Frigo et al.) bound the I/O of the exchange; MPC load bounds (Beame–Koutris–Suciu) bound communication. Neither directly models object-store per-request pricing plus elasticity.

## 4. Upper Bound
Coarse-grained merged shuffle achieves $\tilde O(m + r)$ object-store operations (plus $O(N/B)$ byte transfers) by funneling each mapper's output through a merge service that emits per-reducer streams — at the cost of extra intermediate bytes; this holds in a **request-counting external-memory model**. Sorting/transposition over the store costs $O\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ I/Os (Aggarwal–Vitter optimal external sort). With a decoupled logical partition space, elastic rescaling between map and reduce phases is achievable at $O(\text{\\#logical partitions})$ metadata cost, independent of $N$.

## 5. Lower Bound
In the **external-memory (DAM) model**, permuting/transposing $N$ elements requires $\Omega\!\big(\min(N, \frac{N}{B}\log_{M/B}\frac{N}{B})\big)$ I/Os (Aggarwal–Vitter permutation lower bound), so no shuffle can avoid the sorting-complexity floor in the worst case. Any all-to-all exchange must move $\Omega(N)$ bytes (information-theoretic), and distinguishing whether $m\cdot r$ distinct nonempty cells exist forces $\Omega(m+r)$ object operations even in the best granularity. In the **online elastic** setting, adversarial worker-count changes force a competitive-ratio penalty: a deterministic scheduler that commits to a write granularity can be forced into $\Omega(\log(\text{scale range}))$ extra request cost. No tight bound combining per-request pricing, bytes, and elasticity is known.

## 6. The Gap
The byte and I/O floors are classical and essentially tight (Aggarwal–Vitter). The open gap is the **request-cost + elasticity objective**: there is no algorithm with a proven approximation/competitive ratio that jointly minimizes object-store request count, bytes, and rescaling overhead under realistic tiered pricing, nor a matching lower bound in that combined model. Practice (Celeborn, Dataflow Shuffle, Cosco) shows order-of-magnitude wins via merging and managed services, but the design space (merge fan-in, object granularity, replication for durability, when to rescale) is explored empirically. Closing it requires a cost model that captures per-request pricing and online scale changes, plus an algorithm provably near-optimal in it.

## 7. Current Research (as of June 2026)
Remote/disaggregated shuffle services are an active systems area: Apache Celeborn maturation, push-based merge tuning, and serverless analytics that treat object storage as the only durable medium (Boxer, Pixels, successors to Lambada/Starling) *(frontier — verify)*. There is growing interest in **tiered intermediate storage** (fast NVMe cache in front of object store) and in **disaggregated memory (CXL/RDMA far memory)** as a faster shuffle substrate that changes the cost model *(frontier — verify)*. Theory groups are beginning to model object-store request pricing as a first-class cost in external-memory analyses.

## 8. Future Work
- A formal cost model unifying per-request pricing, byte cost, and elasticity, with a provably competitive elastic shuffle.
- Optimal merge fan-in / object-granularity selection under tiered (cache + object store) hierarchies.
- Durability-vs-cost tradeoffs: how much replication of intermediate objects is needed to truncate lineage cheaply.
- Shuffle designs exploiting CXL/RDMA disaggregated memory rather than object storage.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* Communications of the ACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** M. Frigo, C. Leiserson, H. Prokop, S. Ramachandran. *Cache-Oblivious Algorithms.* FOCS, 1999. — [DBLP](https://dblp.org/rec/conf/focs/FrigoLPR99.html)
- **[SOTA]** M. Shen et al. *Magnet: Push-based Shuffle Service for Large-scale Data Processing.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3415478.3415558)
- **[SOTA]** I. Müller, R. Marroquín, G. Alonso. *Lambada: Interactive Data Analytics on Cold Data Using Serverless Cloud Infrastructure.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/1912.00937)
- **[SOTA]** M. Perron et al. *Starling: A Scalable Query Engine on Cloud Functions.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/1911.11727)
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* JACM, 2017. — [DOI](https://doi.org/10.1145/3125644)

## 10. Worked Example

Take $m = 1000$ mappers and $r = 1000$ reducers shuffling $N = 1\text{ TB}$ through S3. Suppose pricing is $\alpha = \$0.0004$ per 1000 PUT/GET requests and $\beta$ for bytes (egress free within-region).

**Fine-grained** (each mapper writes one object per reducer): $\\#\text{ops} = m\cdot r = 10^6$ writes $+ 10^6$ reads $= 2\times10^6$ ops. Cost $\approx 2000 \times \$0.0004 = \$0.80$, and each object is only $1\text{ TB}/10^6 = 1\text{ MB}$ — small, latency-bound objects.

**Coarse merged** (push to one merge service per reducer, à la Magnet): $\\#\text{ops} = \Theta(m + r) = 2000$ ops, a $1000\times$ request reduction, at the cost of one extra pass over the bytes ($N$ written twice).

So the request term collapses from $\Theta(mr)=10^6$ to $\Theta(m+r)=2\times10^3$. If instead we scaled reducers from $1000$ to $1500$ mid-shuffle, a decoupled logical key space (say $2^{16}$ logical partitions) makes the reassignment $O(2^{16})$ metadata updates — independent of $N$ — rather than re-reading the 1 TB.

---
*Part of the [DBMS Research catalog](../../README.md).*
