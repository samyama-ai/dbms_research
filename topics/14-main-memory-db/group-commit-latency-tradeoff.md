# Group Commit vs Latency Tradeoff

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/group-commit-latency-tradeoff` · **Status:** partially-solved

## 1. Problem Statement
Even an in-memory database must make committed transactions **durable** by writing the redo log to stable storage (NVMe SSD, battery-backed DRAM, or replicated remote memory). The log-flush `fsync`/`fdatasync` is the dominant commit-path cost. **Group commit** amortizes it: instead of flushing once per transaction, the system batches the log records of many transactions and issues one flush, dividing the fixed I/O latency across the batch.

This creates a fundamental tradeoff. Larger batches raise **throughput** (fewer flushes per commit) but raise **commit latency**, because an early transaction in a batch waits for the batch to fill or for a timer. **The problem:** choose the batching policy — batch size $B$ and/or flush-timeout $\tau$ — that maximizes durable-commit throughput while **bounding tail latency** (e.g., p99 commit delay $\le D$).

Variants: *(optimization)* maximize throughput s.t. p99 $\le D$; *(online/adaptive)* set $B,\tau$ without knowing arrival rate; *(scheduling)* decision version — does a policy meeting both a throughput and a tail-latency SLO exist for a given arrival process?

## 2. Mathematical Foundations
Model commit requests as arrivals with rate $\lambda$. A flush has fixed cost $c$ (queueing + device service) independent of payload up to a size threshold. Under size-triggered batching with batch size $B$, sustainable throughput is bounded by $\mu = B/c$ flushes' worth of work, so $\lambda < B/c$ is required for stability — larger $B$ raises capacity. But the **mean batching delay** a transaction incurs while the batch fills is $\approx (B-1)/(2\lambda)$, and **tail latency** is dominated by the worst-case wait $\le \max(\tau,\ B/\lambda)+c$.

This is an **M/D/1-with-batch-service** (bulk-service queue, Bailey/$M^{[X]}/D/1$) problem. The throughput–latency frontier is governed by Little's Law $L=\lambda W$ and by the convexity of mean response time in $\rho=\lambda c/B$: as $\rho\to1$ latency diverges. The optimal *fixed* policy minimizes
$$\min_{B,\tau}\ \mathbb{E}[\text{flushes/sec}]\quad\text{s.t.}\quad \text{p99-delay}(B,\tau,\lambda)\le D,$$
and the key structural result is that the throughput-optimal batch size grows like $B^\star=\Theta(\lambda c)$ (flush as soon as the last flush returns — *self-clocking*), which under heavy load both maximizes throughput and is near-latency-optimal.

## 3. State of the Art (SOTA)
- **Group commit** originates with DeWitt et al. (*Implementation Techniques for Main Memory Database Systems*, SIGMOD 1984) and IBM IMS/DB2 (Gawlick, Gray).
- **Silo** (Tu, Zheng, Kohler, Liskov, Madden — SOSP 2013): epoch-based group commit; transactions in an epoch commit together when the epoch's log is durable — decouples per-transaction synchronization from durability and is the canonical IMDB design.
- **Self-clocking / "flush-when-idle"**: the practical SOTA in modern engines (e.g., Aether logging — Johnson, Pandis, Stoica, Athanassoulis, Ailamaki, VLDB 2010 — *Aether: A Scalable Approach to Logging*), which combines flush pipelining, early lock release, and adaptive group size.
- Systems: MySQL/InnoDB `binlog_group_commit`, PostgreSQL `commit_delay`/`commit_siblings`, RocksDB WAL group commit — all expose the $B,\tau$ knobs.

## 4. Upper Bound
**Self-clocked group commit** (start the next flush the instant the previous returns, batching whatever accumulated) is *throughput-optimal*: it keeps the log device 100% utilized, achieving the device's maximum flush rate, and adds at most one in-flight flush's latency ($\le c$ batching delay under heavy load) — simultaneously near latency-optimal. Aether-style flush pipelining further hides $c$ by overlapping consecutive flushes, giving throughput $\to 1/c_{\text{service}}$ (device bandwidth bound) with bounded, load-adaptive latency. This is the best-known policy and is provably 2-competitive in mean delay against the offline optimum for Poisson arrivals.

## 5. Lower Bound
The tradeoff is **information-theoretically real and unavoidable**: durability requires the commit to survive a crash, so a transaction cannot be acknowledged before its log record is on stable storage — a hard $\ge c_{\text{device}}$ latency floor per *independent* flush (a CAP/availability-style constraint specialized to durability). Batching can amortize but not eliminate $c$: any policy guaranteeing tail latency $\le D$ can batch at most $D\cdot\lambda$ commits, capping per-flush amortization, so **throughput is upper-bounded by $\min(\text{device rate},\ (D\lambda)/c\cdot \text{...})$** — you cannot have both unbounded batching and bounded tail. Under adversarial (bursty) arrivals, no online policy can match the offline optimum better than a constant competitive factor (the classic ski-rental structure of "flush now vs. wait").

## 6. The Gap
For **steady / Poisson** loads the problem is essentially *solved*: self-clocking + flush pipelining is throughput-optimal and near latency-optimal, hence "partially-solved." The residual gap is **bursty and SLO-constrained** regimes: an online policy that provably minimizes p99 under adversarial arrivals (the ski-rental-style timeout choice) with the *best possible* competitive ratio is not fully settled, and multi-tenant fairness (one tenant's batch inflating another's tail) lacks tight bounds. Disaggregated/replicated logs (where $c$ is a network round-trip with its own tail) reopen the analysis.

## 7. Current Research (as of June 2026)
- Group commit over **replicated / disaggregated logs** (Raft/quorum or RDMA log shipping) where the flush cost is a tail-prone network RTT — adaptive batching against network jitter *(frontier — verify)*.
- **Persistent-memory / CXL** logging that shrinks $c$ toward DRAM latency, shifting the optimal batch size toward 1 and changing the whole tradeoff *(frontier — verify)*.
- Learned / control-theoretic commit schedulers that set $(B,\tau)$ from observed arrival statistics to hit explicit p99 SLOs *(frontier — verify)*.
- Groups: MIT (Madden/Kohler/Liskov lineage), EPFL DIAS (Ailamaki), CMU DB Group, TUM.

## 8. Future Work
- Tight competitive analysis of online batch-timeout selection under adversarial bursts.
- SLO-aware, multi-tenant group commit with per-tenant tail guarantees.
- Co-design of group commit with persistent memory and quorum replication.
- Energy-aware batching (flush cost as energy, not just latency).

## 9. Key References
- **[Foundational]** D. DeWitt, R. Katz, F. Olken, L. Shapiro, M. Stonebraker, D. Wood. *Implementation Techniques for Main Memory Database Systems.* SIGMOD, 1984. — [DOI](https://doi.org/10.1145/971697.602261)
- **[Foundational]** D. Gawlick, D. Kinkade. *Varieties of Concurrency Control in IMS/VS Fast Path.* IEEE Data Eng. Bull., 1985. — [DBLP](https://dblp.org/db/journals/debu/debu8.html)
- **[SOTA]** S. Tu, W. Zheng, E. Kohler, B. Liskov, S. Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** R. Johnson, I. Pandis, R. Stoica, M. Athanassoulis, A. Ailamaki. *Aether: A Scalable Approach to Logging.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920928)
- **[Foundational]** J. Gray, A. Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1992 (group commit, ch. on logging). — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)

## 10. Worked Example

Suppose commit requests arrive at $\lambda = 50{,}000$/s and one log flush costs $c = 100\,\mu s$ (fixed, payload-independent up to the batch threshold).

**No batching ($B=1$):** each commit triggers its own flush, so max throughput is $1/c = 10{,}000$/s — but $\lambda = 50{,}000 > 10{,}000$, so the queue is *unstable*. The system cannot keep up.

**Size batching, $B = 10$:** capacity $\mu = B/c = 10/(100\,\mu s) = 100{,}000$/s, comfortably above $\lambda$. Mean batching delay while a batch fills $\approx (B-1)/(2\lambda) = 9/(100{,}000) = 90\,\mu s$; total commit latency $\approx 90 + 100 = 190\,\mu s$.

**Self-clocking:** the next flush starts the instant the previous returns. In each $100\,\mu s$ window, $\lambda c = 50{,}000 \times 100\,\mu s = 5$ commits accumulate, so $B^\star \approx 5$ adapts automatically. Throughput stays at the device limit $1/c = 10{,}000$ flushes/s carrying $50{,}000$ commits/s, while the added delay is just one in-flight flush ($\le c = 100\,\mu s$) — illustrating the throughput/tail-latency frontier.

---
*Part of the [DBMS Research catalog](../../README.md).*
