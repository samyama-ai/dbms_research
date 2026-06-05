# Optimal Block-Granularity for Random vs Sequential I/O

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/block-granularity-tradeoff` · **Status:** open

## 1. Problem Statement

Every storage engine must fix a **transfer/block granularity** $b$ — the unit of I/O between durable storage and the buffer pool (B-tree node size, columnar row-group/page chunk, object-store range-GET size, RocksDB block size). The choice is a tension:

- **Large $b$** amortizes per-I/O fixed cost (seek, queueing, network round-trip, request-billing) and serves sequential/scan-heavy access cheaply, but inflates **read amplification** for point access — fetching $b$ bytes to use a few hundred — wasting bandwidth and polluting the cache.
- **Small $b$** minimizes wasted bytes on random access but pays the fixed per-request overhead on every fetch and shrinks effective sequential throughput.

The catch: the **read mix** (fraction of random vs sequential, selectivity, reuse) is *unknown a priori* and *drifts*. 

**Decision variant:** does a block size $b$ exist achieving expected per-query I/O time $\le \tau$ for a given workload distribution? **Optimization variant:** choose $b$ (or a small set of $b$'s for a tiered layout) minimizing expected I/O time $\mathbb{E}[T(b)]$ over an unknown/adversarial mix. **Online variant:** adapt $b$ as the observed mix shifts, paying reorganization cost. A counting flavor asks how many distinct queries a given $b$ serves "efficiently" (no over-read beyond a factor).

## 2. Mathematical Foundations

Model per-I/O cost as **affine**: fetching a block of size $b$ costs $T(b) = \alpha + \beta b$, where $\alpha$ is the fixed per-request latency (seek/round-trip/billing) and $\beta$ the per-byte transfer time — the classic **disk-access / latency–bandwidth** model and the affine cost underlying the **External Memory (EM) / cache-oblivious** model (Aggarwal–Vitter), where the block size $B$ is the central parameter and bounds are stated in I/Os of size $B$.

Let a query touch a *useful* payload of $u$ bytes spread over the data. A random point read into a $b$-byte block wastes $b - u_{\text{point}}$ bytes; a scan of $S$ bytes costs $\lceil S/b\rceil(\alpha+\beta b) \approx \alpha S/b + \beta S$. With workload mix $\pi$ = fraction random:

$$\mathbb{E}[T(b)] \approx \pi\bigl(\alpha + \beta b\bigr) + (1-\pi)\Bigl(\tfrac{\alpha S}{b} + \beta S\Bigr).$$

Minimizing over $b$ gives an interior optimum $b^\star = \sqrt{(1-\pi)\,\alpha S / (\pi\beta)}$ — an **EOQ/square-root law** (formally identical to the economic-order-quantity and to $\sqrt{\alpha/\beta}$ block-size rules). Robustness against an *unknown* $\pi$ turns this into a **minimax** problem: choose $b$ minimizing the worst-case ratio to the per-mix optimum, which connects to competitive analysis. Cache-oblivious layouts (van Emde Boas) sidestep a single $B$ by being simultaneously efficient at all granularities — the theoretical escape hatch.

## 3. State of the Art (SOTA)

**Systems-SOTA:** fixed engineering defaults — InnoDB 16 KB pages, PostgreSQL 8 KB, RocksDB 4–32 KB blocks, Parquet/ORC row groups of 128 MB with sub-page chunks, object-store range-GETs sized to amortize per-request billing (S3 $\sim$ MBs). **Umbra** (CIDR'20) uses *variable-size pages*; **LeanStore** size-class pools approximate multiple granularities. Cloud engines (Snowflake, BigQuery) pick large immutable micro-partitions/row-groups for scan throughput plus secondary indexes/zone maps to cut over-read. **Theory-SOTA:** the **cache-oblivious** model (Frigo–Leiserson–Prokop, FOCS'99; Bender et al. cache-oblivious B-trees) provides layouts asymptotically optimal across *all* $B$ simultaneously, the cleanest answer to "unknown granularity." Self-driving/auto-tuning DBs (CMU NoisePage/OtterTune lineage) treat $b$ as a tunable knob.

## 4. Upper Bound

In the **external-memory model** with known $B$, the I/O optima are tight: scanning is $\Theta(N/B)$, searching $\Theta(\log_B N)$, sorting $\Theta(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B})$. For **unknown $B$**, cache-oblivious B-trees (Bender–Demaine–Farach-Colton) achieve $O(\log_B N)$ search and $\Theta(N/B)$ scan *simultaneously for every $B$* — an upper bound matching the granularity-aware optimum up to constants without committing to one $b$. For the **affine-cost mixed-mix** objective, the square-root rule gives the exact per-mix optimum; for unknown $\pi$, a fixed $b$ chosen at the geometric mean of the mix-endpoints is a $\Theta(\sqrt{\text{range}})$-robust minimax choice, and a doubling/online policy that adapts $b$ achieves $O(\log)$ competitiveness against the offline best fixed $b$.

## 5. Lower Bound

The external-memory bounds are matching lower bounds in the **I/O / indivisibility model** (sorting and permutation lower bounds of Aggarwal–Vitter; the searching $\Omega(\log_B N)$ comparison/I/O bound). For the **unknown-mix** problem, an adversary alternating pure-random and pure-sequential phases forces any *single fixed* $b$ to be a factor $\Theta(\sqrt{\alpha S/(\beta u)})$ from the per-phase optimum — an information-theoretic floor for non-adaptive granularity. Cache-oblivious results show this floor is *avoidable asymptotically* with the right layout, but only up to constant factors: there is a provable constant-factor penalty (the cache-oblivious vs cache-aware gap) for not knowing $B$. No NP-hardness governs the single-$b$ choice; the offline *multi-granularity layout* selection (partition data into regions each with its own $b$ to minimize total over-read) is NP-hard by reduction from partition/bin-packing.

## 6. The Gap

For *static, known* workloads in the EM model the bounds are closed (tight $\Theta$). The genuinely **open** gap is the **online, drifting-mix** problem under a *realistic* cost model (per-request billing + bandwidth + cache-pollution from over-read, on real NVMe/object stores). We lack a policy with a proven competitive ratio that (a) adapts $b$, (b) charges for the buffer-pool pollution large blocks cause, and (c) accounts for reorganization cost of changing granularity. Cache-oblivious theory answers "unknown $B$" but assumes the indivisibility model and ignores per-request fixed cost $\alpha$ and pollution — so it does not close the *systems* version. Closing the gap means either a tight competitive online granularity policy or a hardness result for the multi-objective online variant.

## 7. Current Research (as of June 2026)

- **Variable / adaptive page-size engines** (Umbra, LeanStore size classes) and learned page-size selection in self-driving systems (CMU; TU Munich) *(frontier — verify)*.
- **Cloud-cost-aware granularity:** sizing object-store range reads against per-request + egress billing, not just latency (Snowflake/Databricks-style micro-partitioning research) *(frontier — verify)*.
- **Cache-oblivious revival** for NVMe/SSD where the "block" is fuzzy across FTL/controller layers.
- Co-design of zone maps / min-max indexes with block size to bound over-read while keeping scans coarse.

## 8. Future Work

- A competitive online algorithm for granularity under drifting mix with a cost model including pollution and reorganization.
- Tight cache-oblivious lower/upper bounds that incorporate the fixed per-request cost $\alpha$ (not just the indivisibility model).
- Per-region / hybrid granularity layout with provable approximation for the NP-hard offline version.
- Granularity selection coupled with compression (compressed block size $\neq$ logical block size).

## 9. Key References

- **[Foundational]** Alok Aggarwal, Jeffrey Scott Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** Matteo Frigo, Charles E. Leiserson, Harald Prokop, Sridhar Ramachandran. *Cache-Oblivious Algorithms.* FOCS, 1999. — [DBLP](https://dblp.org/rec/conf/focs/FrigoLPR99.html)
- **[SOTA]** Michael A. Bender, Erik D. Demaine, Martin Farach-Colton. *Cache-Oblivious B-Trees.* SIAM Journal on Computing, 2005. — [DOI](https://doi.org/10.1137/S0097539701389956)
- **[SOTA]** Thomas Neumann, Michael Freitag. *Umbra: A Disk-Based System with In-Memory Performance.* CIDR, 2020. — [DBLP](https://dblp.org/rec/conf/cidr/NeumannF20.html)
- **[Foundational]** Jeffrey Scott Vitter. *Algorithms and Data Structures for External Memory.* Foundations and Trends in Theoretical Computer Science, 2008. — [DOI](https://doi.org/10.1561/0400000014)
- **[Survey]** Goetz Graefe. *Modern B-Tree Techniques.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000028)

## 10. Worked Example

Object store: per-request latency $\alpha = 20\,000\,\mu s$ (20 ms round-trip), per-byte $\beta = 0.002\,\mu s$/byte (500 MB/s). A scan touches $S = 10^8$ bytes; workload is $\pi = 0.5$ random / sequential.

The square-root rule gives the optimum block size

$$b^\star = \sqrt{\frac{(1-\pi)\,\alpha S}{\pi\,\beta}} = \sqrt{\frac{0.5\cdot 20000\cdot 10^8}{0.5\cdot 0.002}} = \sqrt{10^{15}} \approx 3.16\times 10^7\ \text{bytes} \approx 32\ \text{MB}.$$

Sanity-check two candidates via $\mathbb{E}[T(b)] = \pi(\alpha+\beta b) + (1-\pi)(\alpha S/b + \beta S)$ (drop the constant $\beta S$ term):

- $b = 1\,\text{MB}$: random $= 20000 + 0.002\cdot10^6 = 22000$; scan-ops $= 20000\cdot10^8/10^6 = 2{,}000{,}000$. Half-weighted sum $\approx 1{,}011{,}000\,\mu s$.
- $b = 32\,\text{MB}$: random $= 20000 + 0.002\cdot3.2\times10^7 = 84000$; scan-ops $= 20000\cdot10^8/3.2\times10^7 = 62{,}500$. Half-weighted sum $\approx 73{,}250\,\mu s$.

The 32 MB block is $\sim$14$\times$ cheaper here: with a large fixed per-request fee, the EOQ optimum pushes blocks large — which is exactly why object-store range-GETs are sized in the tens of MB.

---
*Part of the [DBMS Research catalog](../../README.md).*
