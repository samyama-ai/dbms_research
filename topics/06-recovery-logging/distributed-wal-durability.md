# Distributed WAL with single-copy durability

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/distributed-wal-durability` · **Status:** open

## 1. Problem Statement
A write-ahead log (WAL) must be durable: a committed transaction's log records survive failures with overwhelming probability. The naive durable distributed design replicates every log record to $N$ nodes (e.g., $N=3$ for quorum majorities), paying $N\times$ write bandwidth, storage, and a quorum round-trip on the commit critical path. The problem: **provide durability that survives correlated failures while avoiding the cost of full $N$-way log replication** — "single-copy durability" in the sense that the *steady-state* storage/bandwidth overhead approaches $1\times$ plus a small redundancy term, rather than $N\times$.

Variants:
- **Optimization:** minimize storage + write-amplification + commit latency subject to a durability target $\Pr[\text{loss}] \le \delta$ under a specified failure model.
- **Decision (feasibility):** given a correlated-failure model (rack/zone/power-domain correlation matrix) and target $\delta$, does an encoding + placement achieving overhead $< r$ exist?
- **Lower-bound (counting):** what is the minimum redundancy to tolerate $f$ correlated failures with recovery?

## 2. Mathematical Foundations
Durability is fundamentally a **coding-theory** question: an $(n,k)$ erasure code (Reed–Solomon, LRC, regenerating codes) stores $k$ data and $n-k$ parity chunks, tolerating $n-k$ erasures with overhead $n/k$, versus replication's $n/1$. The **Singleton bound** $d \le n-k+1$ caps fault tolerance per redundancy; **MDS codes** meet it.

Correlated failure breaks the independence assumption behind quorum math. Model failures as a distribution over subsets (a **failure-domain hypergraph** / copyset structure); the relevant quantity is not "any $f$ nodes" but "any failure *domain*." **Copyset placement** (Cidon et al.) minimizes the probability that a single correlated event hits a full copyset.

Consensus is the other pillar: a replicated log is the canonical **state-machine replication** object. **FLP impossibility** forbids deterministic async consensus with one crash; **CAP** forbids availability under partition with strong consistency. Commit durability reduces to ensuring a record is in a **persistent quorum** whose intersection survives the failure model — formalized via quorum-system intersection ($\forall Q_1,Q_2: Q_1\cap Q_2 \ne \emptyset$) and **regenerating-code repair-bandwidth** bounds (Dimakis et al.) governing reconstruction cost.

The tension is **information-theoretic**: to survive a failure event of "weight" $w$ you need redundancy $\ge$ the event's erasure mass; correlated events have large mass concentrated on few placements, so cheap codes plus smart placement, not blind replication, is the lever.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Disaggregated log services that replace per-tuple page replication with a thin, durably-replicated *redo log*: **Amazon Aurora** (Verbitski et al., SIGMOD 2017) — "the log is the database," 6-way quorum across 3 AZs but only the *log* is replicated, and parallel/cheap; **Microsoft Socrates** (SIGMOD 2019) separates a durable "XLOG" landing zone from page servers; **Meta LogDevice**, **Apache BookKeeper**, **Kafka tiered storage**, and **Neon/PolarDB** follow the shared-log pattern (Corfu, Balakrishnan et al., NSDI 2012; **Delos**, OSDI 2020).
- **Theory-SOTA:** Erasure-coded consensus — **RS-Paxos** and successors encode log entries so each replica stores a fraction of the entry, cutting per-entry storage toward $\approx n/k$ while preserving quorum durability.

## 4. Upper Bound
With an $(n,k)$ MDS code over a quorum of $n$ nodes, steady-state storage and write bandwidth overhead is $n/k$ (e.g., $1.5\times$ for a $(9,6)$ scheme) while tolerating $n-k$ erasures — strictly below $3\times$ replication at equal fault tolerance. Erasure-coded consensus (RS-Paxos-style) achieves commit with a quorum of $\lceil (n+k)/2\rceil$ acknowledgements, storage per entry $\approx (n/k)\times$ entry size. Copyset placement reduces correlated-loss probability to $O(\text{scatter}^{-1})$ relative to random placement at fixed redundancy.

## 5. Lower Bound
- **Coding:** Singleton bound forces $n-k+1 \le d$; you cannot tolerate $f$ erasures with less than $f$ redundancy chunks — so "single-copy" with positive fault tolerance is information-theoretically impossible; some redundancy $r>0$ is mandatory.
- **Consensus:** FLP (Fischer–Lynch–Paterson, 1985) impossibility of deterministic async consensus; CAP (Gilbert–Lynch, 2002) trade-off; quorum systems require pairwise intersection, lower-bounding acknowledgement set sizes (any durable write must reach a set intersecting every future read quorum).
- **Repair:** regenerating-code cut-set bound (Dimakis et al., 2010) lower-bounds repair bandwidth, so cheap storage trades against expensive node-rebuild.

## 6. The Gap
Codes and consensus are each near-optimal in isolation, but **the joint optimum under correlated, non-i.i.d. failure is open**. Real failure correlation (shared power, rack, firmware, AZ) is hard to model and adversarial events (gray failures, region outages) violate the i.i.d. assumptions of both quorum and coding analysis. The gap is between the clean MDS/quorum overhead lower bound under independent failures and the *unknown* minimum overhead under a realistic correlated-failure distribution — likely genuinely open and partly empirical (you must estimate the correlation structure).

## 7. Current Research (as of June 2026)
- Shared-log / log-as-a-service maturation: Delos virtualized consensus and its descendants generalize the durable log substrate *(frontier — verify)*.
- Erasure-coded WAL on the commit path with sub-millisecond tails using RDMA/NVMe-oF and CXL-attached durable buffers *(frontier — verify)*.
- Correlated-failure-aware placement learned from telemetry, extending copyset theory to time-varying correlation.
- Cross-region durability without synchronous N-way replication (causal + bounded-staleness durability tiers).

## 8. Future Work
- A durability model that is *provably tight* under specified correlated-failure distributions, not just independent ones.
- Joint code-and-quorum co-design minimizing commit-latency tail and repair bandwidth simultaneously.
- Formal accounting of "durability debt" when acknowledging on fewer copies and back-filling redundancy asynchronously.

## 9. Key References
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: Design Considerations for High-Throughput Cloud-Native Relational Databases.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056101)
- **[SOTA]** Antonopoulos, P. et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3314047)
- **[Foundational]** Fischer, M., Lynch, N. & Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** Dimakis, A., Godfrey, P. B., Wu, Y., Wainwright, M. & Ramchandran, K. *Network Coding for Distributed Storage Systems.* IEEE Trans. Information Theory, 2010. — [arXiv](https://arxiv.org/abs/0803.0632)
- **[SOTA]** Balakrishnan, M. et al. *Virtual Consensus in Delos.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/balakrishnan)
- **[Foundational]** Cidon, A. et al. *Copysets: Reducing the Frequency of Data Loss in Cloud Storage.* USENIX ATC, 2013. — [USENIX](https://www.usenix.org/conference/atc13/technical-sessions/presentation/cidon)

## 10. Worked Example

Compare 3-way replication against a $(9,6)$ MDS code for a 1 MB log segment.

**Replication:** store 3 full copies $\Rightarrow$ 3 MB on disk, overhead $3\times$. Tolerates 2 node losses.

**$(9,6)$ MDS:** split the 1 MB into $k=6$ data chunks of $\tfrac{1}{6}$ MB each, compute $n-k=3$ parity chunks of the same size, scatter all 9 over 9 nodes. Storage $= 9 \times \tfrac{1}{6} = 1.5$ MB, overhead $n/k = 1.5\times$. By the Singleton bound any $d = n-k+1 = 4$, so it tolerates $n-k = 3$ erasures — strictly *better* fault tolerance at *half* the storage of replication.

**Commit quorum (RS-Paxos-style):** acknowledge after $\lceil (n+k)/2\rceil = \lceil 15/2\rceil = 8$ chunks land. Any two such write/read quorums of size 8 over 9 nodes intersect in $\ge 8+8-9 = 7 \ge k$ nodes, so every read can reconstruct.

**Correlated-failure caveat:** if all 3 parity chunks sit in one rack and that rack's power domain fails together (one event, weight 3), the segment is *still* recoverable (3 erasures $\le d-1$); but if a 4-node domain fails, no $(9,6)$ code survives — motivating copyset-aware placement, not just raising $n/k$.

---
*Part of the [DBMS Research catalog](../../README.md).*
