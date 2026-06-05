# Log-structured durability for OLTP

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/log-structured-oltp-durability` · **Status:** open

## 1. Problem Statement
The "log is the database" principle makes the durable, append-only log the *authoritative* store: state is the (replayed) log, and any materialized B-tree/heap is a cache. This is durability-ideal (sequential writes, trivial atomicity, natural replication) but historically penalizes OLTP because **point queries** and **recovery** require reconstructing per-key current state from a long log. The problem: design a log-structured durability architecture in which (i) commit is a sequential log append, (ii) point-query latency stays bounded (comparable to in-place engines), and (iii) recovery time stays bounded (sub-linear in log length / proportional only to a bounded recovery window), simultaneously, for OLTP read/write workloads.

**Variants.** *Decision:* given target point-query latency $q^\star$ and recovery bound $T^\star$, does a log-structured design with compaction/indexing policy $\pi$ achieve both at write amplification $\le \alpha^\star$? *Optimization:* minimize the (read-amp, write-amp, space-amp, recovery-time) cost vector — the classic LSM "RUM" tradeoff extended with recovery. The tension between read amplification and recovery on one side and write amplification/compaction overhead on the other keeps this **open** as a frontier rather than a settled design point.

## 2. Mathematical Foundations
Model the log as an append-only sequence; the current value of key $k$ is the latest record for $k$. A pure log gives $O(1)$ writes but $O(n)$ point lookups, so an **index** maps key → latest log offset. Log-structured **merge trees (LSM)** organize records into $L$ exponentially growing levels with size ratio $T$; standard analysis (Dayan, Athanassoulis, Idreos) gives:
- point-lookup I/O $O(L) = O(\log_T \tfrac{N}{B})$ (with Bloom filters, $\approx O(e^{-bits})$ false-positive cost),
- write amplification $O(T \cdot L)$,
- space amplification governed by the largest level.

The **RUM conjecture** states Read, Update, and Memory overheads cannot all be minimized simultaneously — a Pareto tension. Recovery cost is governed by the suffix of the log not yet *flushed/compacted* into durable, indexed levels: $T_{\text{rec}} \propto$ size of the in-memory memtable + unindexed log tail, which is bounded by the flush policy. Thus recovery time trades against write amplification: more frequent flush/checkpoint shrinks the recovery window but raises write amp. Formally this is a constrained point on the (read-amp, write-amp, space-amp, recovery-window) polytope; tight characterizations exist for sub-pieces (e.g., Bloom-filter bit allocation via Lagrangian optimization in Monkey).

## 3. State of the Art (SOTA)
**Systems-SOTA.** LSM engines — LevelDB, RocksDB, Cassandra, ScyllaDB, HBase — are the dominant log-structured OLTP/HTAP stores; *WiscKey* (Lu et al., FAST 2016) separates keys from values to cut write amplification; *Monkey* and *Dostoevsky*/*lazy-leveling* (Dayan, Idreos) navigate the RUM tradeoff with near-optimal Bloom-filter allocation and merge policies. *Aurora* (SIGMOD 2017) realizes "the log is the database" at cloud scale by shipping redo to storage. *Bw-tree/LLAMA* (Levandoski et al.) and *FASTER* (Chandramouli et al., SIGMOD 2018) give log-structured, latch-free point-update stores with hybrid log + index. Deterministic/log-replicated systems (Calvin) treat an ordered input log as the database.

**Theory-SOTA.** The LSM cost model and RUM/lazy-leveling Pareto analysis are the theory backbone; learned indexes over sorted runs add another axis. A *unified* read/write/recovery optimality theorem for OLTP is not established.

## 4. Upper Bound
With tiered/leveled LSM and per-level Bloom filters, point lookups cost $O(\log_T \tfrac{N}{B})$ I/Os with constant expected filter overhead, write amplification $O(T\log_T\tfrac{N}{B})$, in the external-memory (DAM) model. Monkey's Lagrangian Bloom allocation achieves the asymptotically optimal point-lookup cost for fixed memory. Recovery is bounded to the unflushed log tail, $T_{\text{rec}} = O(\text{memtable size}/\text{replay bw})$, made arbitrarily small by flush frequency at the cost of write amp. These are the best-known constructive upper bounds; they hold in the external-memory/DAM model.

## 5. Lower Bound
The **RUM conjecture / external-memory tradeoffs** lower-bound the simultaneous achievability of low read, update, and memory overhead: a comparison/external-memory argument shows you cannot get $O(1)$ point lookups *and* $O(1)$ amortized writes *and* linear space on an unbounded key space without extra memory — there is an inherent product/sum lower bound on (read-amp × write-amp). Indexing the log to beat $O(n)$ lookups provably costs memory and write amplification. The hardness is *information-theoretic / external-memory* (cell-probe and DAM lower bounds for dictionaries), not NP-hardness.

## 6. The Gap
For the read/write/memory sub-triangle, upper bounds nearly meet the RUM/external-memory lower bounds (Monkey-style results are near-optimal). The genuinely open gap is **incorporating recovery time as a fourth, co-optimized dimension** with matching lower bounds: no tight theorem states the achievable (read-amp, write-amp, space-amp, recovery-window) region for OLTP. Whether log-structured durability can match in-place engines on point-query *tail* latency under crash recovery while keeping write amplification low remains empirically contested and theoretically uncharacterized.

## 7. Current Research (as of June 2026)
Active: separating durability log from index (FASTER/Bw-tree lineage), key–value separation, learned and adaptive compaction (RocksDB compaction policies driven by RL/learned cost models) *(frontier — verify)*; LSM on persistent memory and on disaggregated/cloud storage; HTAP designs where the log feeds both row and column stores. Groups: Harvard DASlab (Stratos Idreos — Monkey/Dostoevsky/RUM), Microsoft Research (FASTER/Bw-tree — Badrish Chandramouli, Phil Bernstein lineage), and cloud-database teams (AWS Aurora, Meta/RocksDB). LLM/learned-policy compaction tuning is nascent *(frontier — verify)*.

## 8. Future Work
(i) A four-way RUM+Recovery lower bound and matching design. (ii) Bounded *tail*-latency point queries under ongoing compaction. (iii) Recovery-window-aware compaction scheduling. (iv) Co-design with persistent memory / CXL to shrink the unindexed tail. (v) Unifying deterministic log-replication (Calvin) durability with single-node LSM recovery.

## 9. Key References
- **[Foundational]** O'Neil, P., Cheng, E., Gawlick, D., O'Neil, E. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DBLP](https://dblp.org/rec/journals/acta/ONeilCGO96.html)
- **[Foundational]** Rosenblum, M., Ousterhout, J. *The Design and Implementation of a Log-Structured File System.* ACM TOCS, 1992. — [DOI](https://dl.acm.org/doi/10.1145/146941.146943)
- **[SOTA]** Dayan, N., Athanassoulis, M., Idreos, S. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://dl.acm.org/doi/10.1145/3035918.3064054)
- **[SOTA]** Chandramouli, B., Prasaad, G., Kossmann, D., Levandoski, J., Hunter, J., Barnett, M. *FASTER: A Concurrent Key-Value Store with In-Place Updates.* SIGMOD, 2018. — [DOI](https://dl.acm.org/doi/10.1145/3183713.3196898)
- **[SOTA]** Lu, L., Pillai, T., Gopalakrishnan, H., Arpaci-Dusseau, A., Arpaci-Dusseau, R. *WiscKey: Separating Keys from Values in SSD-Conscious Storage.* FAST, 2016. — [DBLP](https://dblp.org/rec/conf/fast/LuPAA16.html)
- **[Survey]** Athanassoulis, M., Kester, M., Maas, L., Stoica, R., Idreos, S., Ailamaki, A., Callaghan, M. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016. — [DBLP](https://dblp.org/rec/conf/edbt/AthanassoulisKM16.html)

## 10. Worked Example

Take an LSM with $N/B = 10^6$ data blocks and size ratio $T = 10$, so there are $L = \log_{10} 10^6 = 6$ levels. A point lookup that misses the memtable probes a Bloom filter per level; with naive uniform bit allocation ($\approx 10$ bits/key, false-positive rate $\epsilon \approx 0.01$ each), worst-case extra I/Os $\approx L\cdot\epsilon = 6\cdot 0.01 = 0.06$, plus the one true hit. Write amplification is $O(T\cdot L) = 10\cdot 6 = 60$: a key is rewritten up to 60 times migrating to the bottom level.

Now the recovery axis. Suppose the memtable holds $64$ MB of unflushed records and replay bandwidth is $512$ MB/s. Recovery time is $T_{\text{rec}} = 64/512 = 0.125$ s — independent of the $L=6$ levels, because flushed levels are already durable and indexed. Halving the flush threshold to $32$ MB cuts $T_{\text{rec}}$ to $0.0625$ s but raises write amplification (more frequent flushes ⇒ more compaction). This is the exact (write-amp ↔ recovery-window) trade the problem says lacks a tight four-way bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
