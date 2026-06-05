# Elastic index build and maintenance

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/elastic-index-maintenance` · **Status:** empirically-open

## 1. Problem Statement

In disaggregated, serverless databases the serving tier (queries) and a separately-scalable compute tier (index building) draw from the same persistent storage. We want to **build** secondary indexes (B-trees, LSM components, inverted lists, vector indexes) and **incrementally maintain** them under a write stream, using ephemeral elastic compute whose size is decoupled from the serving tier — minimizing dollar cost and build latency while never blocking or stale-serving beyond an SLA.

Variants:
- **Build:** Given $N$ rows in remote storage and a pool of up to $K$ elastic workers, build the index in min time-under-budget (or min $-under-deadline). Speedup vs. workers is the question.
- **Maintenance (decision):** Given a write rate $\lambda$ and freshness bound $\Delta$, is there an elastic-worker schedule keeping index staleness $\le \Delta$ within budget?
- **Online/dynamic:** Workload and write rate vary; provision workers online (right-sizing) with bounded over/under-provisioning cost.

The novelty over classic parallel index build: workers are **stateless, transient, and priced per second**, storage is **remote**, and the serving tier must stay live (online build) — so consistency between an in-flight build and concurrent writes is central.

## 2. Mathematical Foundations

Parallel build cost follows a **work-span (Brent) model**: total work $W$ (e.g., $O(N\log N)$ to sort keys), span $S$ (critical path); with $K$ workers, time $T_K \ge \max(W/K,\,S)$ and Brent's theorem gives $T_K \le W/K + S$. Remote storage adds an I/O term; per the disaggregated cost model, $T \approx \max(W/K, R\mu_L/p, RB^{-1})$. **Amdahl/Gustafson** scaling bounds the achievable speedup given a serial fraction (merge/commit step).

Online index maintenance under writes is governed by **LSM amplification theory**: write amplification $\sim O(\log_T N)$ for size ratio $T$, read amplification $\sim O(\log_T N)$, with the **RUM conjecture** (Athanassoulis et al.) asserting you cannot simultaneously minimize Read, Update, and Memory overheads. Provisioning workers to hold staleness $\le \Delta$ under arrival rate $\lambda$ is a **queueing / capacity** problem ($M/G/k$): keep service rate $K\mu \ge \lambda$ with safety margin for the tail. Online right-sizing maps to **ski-rental / one-way trading** (spin up vs. wait).

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Snowflake's automatic clustering and search-optimization service rebuild indexes on elastic warehouses *(frontier — verify)*; Aurora/AlloyDB do online `CREATE INDEX` with concurrent-writes handling; LSM engines (RocksDB, **ScyllaDB**, Cassandra) do compaction as background maintenance; **vector DBs** (Milvus, Pinecone, pgvector/DiskANN) build HNSW/IVF on separate compute and hot-swap. Spark/Iceberg compaction jobs rebuild table indexes/manifests on elastic clusters.
- **Theory-SOTA.** Parallel external-memory sorting/B-tree bulk-loading (PEM model); LSM design space and the RUM conjecture; concurrent index construction protocols (online B-tree build with logical undo). No tight theory for *priced elastic* build/maintenance scheduling.

## 4. Upper Bound

Bulk index build achieves near-linear speedup up to the merge/commit serial fraction: $T_K \le W/K + S$ (Brent), and parallel external sorting attains the AV/PEM optimal I/O bound. For maintenance, an $M/G/k$ provisioning with $K = \lceil \lambda/\mu \rceil + O(\sqrt{\cdot})$ workers keeps expected staleness bounded. Online worker right-sizing is **e/(e-1)-competitive** in the randomized ski-rental abstraction and constant-competitive for simple scale-up/down. Cost-optimal $K$ under a deadline has a closed-form crossover (pay for parallelism until I/O- or span-bound).

## 5. Lower Bound

Speedup is capped by the **span** $S$ (critical path) — Amdahl's law gives an unconditional ceiling; the merge/commit step lower-bounds latency regardless of $K$. The **RUM conjecture** posits an inherent three-way tradeoff barring an index that is simultaneously read-, update-, and memory-optimal. Parallel external-memory sorting has the Aggarwal–Vitter I/O lower bound $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$. Online provisioning inherits the ski-rental **2-competitive (deterministic)** lower bound. No fine-grained or unconditional lower bound exists for the *full priced-elastic online maintenance* objective — hence empirically-open.

## 6. The Gap

Individual pieces have matching bounds (Brent for build speedup, ski-rental for provisioning, AV for I/O). The gap is the **integrated, priced, online** problem: there is no algorithm with a proven competitive ratio for "build + maintain under a write stream with elastic, per-second-priced, transient workers and a freshness SLA, over remote storage," nor a matching lower bound. Practical systems pick worker counts with heuristics and lack worst-case guarantees on dollar cost or staleness. Closing it needs an online provisioning-and-scheduling policy with consistency guarantees against concurrent writes plus a competitive-ratio or hardness result.

## 7. Current Research (as of June 2026)

Directions: serverless index/compaction offload (RocksDB-Cloud, Iceberg auto-compaction on elastic compute); **vector-index** build-cost reduction and incremental HNSW/DiskANN maintenance, very active given RAG workloads (Microsoft Research DiskANN line, Milvus/Zilliz) *(frontier — verify)*; learned/auto index selection meeting elasticity (the "self-driving DB" line, CMU Andy Pavlo's group); right-sizing serverless compute with learning-augmented predictions. Snowflake/Databricks ship managed clustering/optimization services whose policies are largely undisclosed *(frontier — verify)*.

## 8. Future Work

- Competitive online provisioning for build+maintenance under priced transient workers.
- Consistency protocols for online index build concurrent with elastic writers.
- Incremental maintenance of approximate (vector) indexes with quality SLAs.
- Joint optimization of index freshness, query staleness, and dollar cost.
- Benchmarks coupling write traces with cloud pricing for reproducibility.

## 9. Key References

- **[Foundational]** R. P. Brent. *The Parallel Evaluation of General Arithmetic Expressions.* JACM, 1974.
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988.
- **[SOTA]** M. Athanassoulis et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016.
- **[SOTA]** S. J. Subramanya, R. Krishnaswamy, et al. *DiskANN: Fast Accurate Billion-point ANN Search on a Single Node.* NeurIPS, 2019.
- **[Survey]** C. Luo, M. J. Carey. *LSM-based storage techniques: a survey.* The VLDB Journal, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
