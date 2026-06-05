# Log-as-the-database durability bounds

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/log-is-database` · **Status:** partially-solved

## 1. Problem Statement
In the "log is the database" architecture (Aurora's slogan), the compute tier never writes pages to durable storage. It ships only the **redo log records** to a distributed storage fleet, which independently *materializes* (applies the redo to) data pages on demand. A transaction commits as soon as its log records are durable on a write quorum of storage nodes. The research question is: **what are the fundamental latency and throughput limits of this design, and when does log-only shipping provably beat page shipping?**

- **Decision variant:** Given a redo-log generation rate $\lambda$ (bytes/s), storage quorum $(V, V_w)$, and a per-record durability latency target $T$, is there a placement/replication scheme meeting $T$ at sustained $\lambda$?
- **Optimization variant:** Minimize commit latency and/or write amplification subject to durability (survive $f$ failures) and a read-freshness bound for page reads.
- **Counting variant:** Bound the number of log records a storage node must replay (the "redo backlog") to serve a page read at version $v$.

## 2. Mathematical Foundations
Let the storage fleet hold $V$ copies of each *protection group* (Aurora uses $V=6$, across 3 AZs). A write needs $V_w$ acks, a read needs $V_r$, with the quorum invariants $V_w + V_r > V$ and $2V_w > V$ (the latter so writes are totally ordered and survive AZ+1 failure). Aurora's choice $V_w=4, V_r=3, V=6$ tolerates losing one AZ **plus** one extra node while still committing.

Commit latency is governed by **order statistics of the storage-node ack latency**: with i.i.d. node latency $X$, commit latency $\approx X_{(V_w)}$, the $V_w$-th order statistic of $V$ draws — strictly better than waiting for all $V$ (the page-mirroring case waits for $X_{(V)}$). This is the core analytic win: tail latency is set by $X_{(4)}$ of 6, not $X_{(2)}$ of 2.

Throughput is bounded by the **redo log generation rate vs. network**: shipping only redo (a few hundred bytes/op) instead of full 8–16 KB pages reduces write bytes by the redo/page ratio $\rho \ll 1$, so the network-bound throughput improves by $\approx 1/\rho$. Formally, network write amplification drops from $V \cdot \text{pagesize}$ (mirror all pages) to $V_w \cdot \text{redosize}$.

Page materialization is a **log-structured replay**: a page at LSN $v$ requires applying the chain of redo records since the last full image; the backlog length is bounded by checkpoint/coalescing frequency. Read latency therefore depends on $\max$(replay backlog, fetch).

## 3. State of the Art (SOTA)
**Systems-SOTA.** Amazon **Aurora** (SIGMOD 2017 / 2018) is the canonical realization — "the log is the database," quorum $4/6$, continuous background page materialization, no checkpoints/double-write/full-page flushes. **Socrates** (Azure SQL DB, SIGMOD 2019) separates log (XLOG service), page servers, and compute similarly. **AlloyDB** (Google) and **Neon** (open-source, Postgres + log-shipping to "pageservers") extend the pattern; Neon's *pageserver* + *safekeeper* (Paxos-replicated WAL) is the cleanest public instance. **PolarDB** (Alibaba) uses shared storage with RDMA.

**Theory-SOTA.** The durability/latency analysis is quorum-systems theory (Gifford 1979; Malkhi–Reiter Byzantine quorums); the win is quantified via order-statistics tail bounds and the redo/page byte ratio.

## 4. Upper Bound
Commit latency upper bound: one network round-trip to the $V_w$-th fastest of $V$ storage nodes, i.e., $\mathbb{E}[X_{(V_w)}]$, with tail concentration giving $\Pr[\text{commit} > t] \le \binom{V}{V_w}\Pr[X>t]^{V-V_w+1}$-style bounds. Write-throughput upper bound scales as $1/\rho$ versus page shipping. These bounds are *achieved* by Aurora/Neon, which is why the problem is **partially solved**.

## 5. Lower Bound
Durability requires $V_w$ acks, so commit latency is **lower-bounded** by the $V_w$-th order statistic — you cannot commit faster than the $V_w$-th fastest replica responds; this is tight against the upper bound. A second lower bound is **information-theoretic on read freshness**: to serve a page at the latest LSN, a storage node must have received every committed redo record affecting that page, so read latency is bounded below by redo-propagation + replay backlog. FLP impossibility bounds any *consensus-on-the-tail-of-log* step (the safekeeper Paxos), forbidding bounded-time commit under fully asynchronous networks with one crash.

## 6. The Gap
For pure **durability latency**, upper and lower bounds *match* (the $V_w$-order-statistic) — closed. The open residue is on the **read/materialization side**: there is no tight characterization of the optimal trade-off between page-materialization eagerness (replay backlog), storage CPU cost, and read tail latency, especially for analytical scans that touch cold pages whose redo backlog is long. Also open: provably optimal log placement under heterogeneous, asymmetrically priced storage. Hence "partially solved."

## 7. Current Research (as of June 2026)
- Neon's separation of *safekeepers* (WAL durability via Paxos) from *pageservers* (materialization) is an active open-source testbed; work on multi-tenant pageserver sharding and on-demand redo replay. *(frontier — verify)*
- Disaggregated WAL on RDMA/CXL fabrics to push commit latency toward hardware floors. *(frontier — verify)*
- "Computational storage" pushing redo replay into the storage node to cut read amplification.
- Groups: Aurora/Socrates/Neon engineering teams; academic disaggregated-storage work at MIT, CMU, Wisconsin.

## 8. Future Work
- A formal read-latency lower bound tying replay backlog, checkpoint frequency, and storage CPU into one optimum.
- Adaptive materialization policies (eager vs. lazy per page) with provable tail guarantees.
- Extending log-is-the-database to HTAP, where analytical reads stress cold-page materialization.

## 9. Key References
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017.
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: On Avoiding Distributed Consensus for I/Os, Commits, and Membership Changes.* SIGMOD, 2018.
- **[SOTA]** Antonopoulos, P. et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019.
- **[Foundational]** Gifford, D. *Weighted Voting for Replicated Data.* SOSP, 1979.
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.

---
*Part of the [DBMS Research catalog](../../README.md).*
