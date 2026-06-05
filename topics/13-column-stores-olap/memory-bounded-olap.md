# Spilling and Memory-Bounded OLAP

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/memory-bounded-olap` · **Status:** open

## 1. Problem Statement
OLAP queries build large in-memory state — **hash tables for joins and aggregations**, sort runs, window partitions. When the working set exceeds available RAM (a memory budget $M$, possibly shared and shrinking under concurrency), the engine must **spill** to disk/SSD/object storage and finish correctly without catastrophic slowdown or out-of-memory failure. The problem: design **robust, near-optimal spill strategies** that (a) minimize I/O, (b) degrade gracefully (no cliffs), (c) handle **skew** (a few heavy keys), and (d) adapt to a budget that changes mid-query.

Variants:
- **Hash join under memory bound:** Grace/hybrid partitioning, recursive repartitioning on skew.
- **Hash aggregation under memory bound:** partition-and-spill vs. pre-aggregation; high-cardinality group-by.
- **Optimization:** minimize external-memory I/O ($O(\frac{N}{B}\cdot\#\text{passes})$); **online/competitive** variant when $M$ varies adversarially.
- **Counting/decision:** can the query complete within budget $M$ at all (memory admission control)?

## 2. Mathematical Foundations
The natural model is the **external-memory / I/O (Aggarwal–Vitter) model**: $N$ items, memory $M$, block $B$; sorting and hash-partitioning cost $\Theta(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/Os. **Hybrid hash join** keeps one partition resident, achieving fewer passes when $M$ is only modestly below the build size. With $p=\lceil |R|/M\rceil$ partitions, a single repartition suffices if each partition fits; otherwise recursion adds $\log_{M/B}$ factors. **Skew** breaks uniform partitioning: a heavy key with frequency $f$ forces an oversized partition; bounds depend on the **frequency moment** $F_\infty$ / heavy-hitter structure. Spilling under a **time-varying budget** is an **online problem**; competitive analysis bounds the ratio to an offline optimum that knows future memory availability. Aggregation spill relates to the **distinct-elements / heavy-hitters** sketch theory: pre-aggregation effectiveness is governed by group cardinality vs. $M$.

## 3. State of the Art (SOTA)
- **Hybrid hash join** (DeWitt et al.; Shapiro, *Join Processing in Database Systems with Large Main Memories*, TODS 1986) — the foundational spill-aware join.
- **Radix / partitioned hash joins** (Manegold, Boncz, Kersten; Balkesen et al., ICDE 2013) — cache- and memory-hierarchy-conscious partitioning, the vectorized-engine standard.
- **Systems:** Spark SQL spillable hash aggregate/join with external sort fallback; DuckDB **out-of-core** hash join and aggregation (Raasveldt et al.) with graceful spilling; Snowflake/Redshift spill to local SSD then remote storage with tiered penalty; Umbra/HyPer memory-aware operators.
- **Skew handling:** dynamic repartitioning, "skew join" hints, and detection of heavy hitters at runtime (Spark, Flink).
- **Memory management/admission:** Vertica/Snowflake resource pools; adaptive grant resizing.

## 4. Upper Bound
External-memory hash join/aggregation completes in $O(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/Os, and **only $O(\frac{N}{B})$** (a constant number of passes) when $M=\Omega(\sqrt{NB})$ (the "two-pass" regime) — matching sorting's optimal external bound. Hybrid hash join interpolates smoothly: if build side is $b\cdot M$ ($b\ge1$), expected passes $\approx \lceil \log_{M/B} b\rceil$. Robust spilling frameworks (DuckDB) keep per-operator memory $\le M$ with bounded I/O proportional to the overflow $\max(0, |state|-M)$, the ideal "pay only for what spills" property.

## 5. Lower Bound
Hash join is conditionally hard: under the **3SUM** / **APSP** fine-grained hypotheses, certain join/aggregation problems have no strongly subquadratic algorithm. In external memory, sorting and hashing lower bounds give $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/Os for permutation-hard instances. For **online** spilling under adversarial memory fluctuation, paging/caching lower bounds apply — any deterministic policy is $\Omega(M/B)$-competitive in the worst case (cf. competitive paging), and randomization helps only logarithmically. Skew imposes an information-theoretic floor: a partition containing a heavy hitter of frequency $f$ cannot be made smaller than $f$ by hashing alone.

## 6. The Gap
Static, known-budget spilling is **well understood** (matching external-memory bounds). The open gap is **robustness under realures**: (a) **adversarial/dynamic memory** — no policy with tight competitive guarantees that also performs well in practice; (b) **skew** — graceful, provably-bounded repartitioning without manual hints; (c) **tiered/heterogeneous spill** (RAM → local NVMe → remote object store) where each tier has different bandwidth/latency, turning spill placement into a multi-level cost-optimization with no clean optimal algorithm; (d) **concurrency** — many queries sharing a shrinking pool (a fairness + global-optimality problem).

## 7. Current Research (as of June 2026)
- **Adaptive, hint-free skew handling** with runtime heavy-hitter detection and targeted repartitioning *(frontier — verify)*.
- **Tiered spilling to object storage** (separation of storage/compute): Snowflake/Databricks/DuckDB spilling to S3-class tiers with prefetch and cost-aware placement.
- **Memory-fair multi-query scheduling** and learned admission control.
- **Disaggregated-memory / CXL** OLAP: spilling to far memory instead of disk *(frontier — verify)*.
- Groups: CWI/DuckDB (Raasveldt, Mühleisen) on robust out-of-core; TUM Umbra (Neumann) on memory-aware operators; CMU-DB; Databricks Photon and Snowflake engineering.

## 8. Future Work
- Competitive online spill policies with provable ratios under fluctuating budgets.
- Provably bounded skew-resilient hash partitioning.
- Cost models and optimal placement for multi-tier (RAM/NVMe/object/CXL) spill.
- Global memory arbitration across concurrent OLAP queries with SLO guarantees.

## 9. Key References
- **[Foundational]** Shapiro. *Join Processing in Database Systems with Large Main Memories.* ACM TODS, 1986. — [DOI](https://doi.org/10.1145/6314.6315)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Balkesen, Teubner, Alonso, Özsu. *Main-Memory Hash Joins on Multi-Core CPUs.* ICDE, 2013. — [DBLP](https://dblp.org/rec/conf/icde/BalkesenTAO13.html)
- **[SOTA]** Manegold, Boncz, Kersten. *Optimizing Main-Memory Join on Modern Hardware.* IEEE TKDE, 2002. — [DOI](https://doi.org/10.1109/TKDE.2002.1019210)
- **[SOTA]** Raasveldt, Mühleisen et al. *DuckDB: An Embeddable Analytical Database* (and out-of-core operator work). SIGMOD/CIDR, 2019–. — [DOI](https://doi.org/10.1145/3299869.3320212)
- **[Survey]** Graefe. *Query Evaluation Techniques for Large Databases.* ACM Computing Surveys, 1993. — [DOI](https://doi.org/10.1145/152610.152611)

## 10. Worked Example

Hash-join build side $R$ with $|R| = 8$ GB, memory budget $M = 2$ GB, block $B = 256$ KB.

**Grace partitioning:** split $R$ into $p = \lceil |R|/M \rceil = 4$ partitions of $\approx 2$ GB each — but each still exceeds $M$, so one repartition pass is not enough. The external-memory cost is $\Theta(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B})$. With $\tfrac{M}{B} = \tfrac{2\,\text{GB}}{256\,\text{KB}} = 8192$, the $\log_{M/B}$ factor is small: $\log_{8192}(8\,\text{GB}/256\,\text{KB}) = \log_{8192}(32768) \approx 1.15$, so essentially **two passes** — we are in the two-pass regime since $M = 2\,\text{GB} \ge \sqrt{N B} = \sqrt{8\,\text{GB}\cdot 256\,\text{KB}} \approx 45$ MB.

**Skew floor:** suppose one join key appears in $f = 1.5$ GB of $R$. Hashing alone cannot split that key, so its partition is $\ge 1.5$ GB regardless of $p$ — the information-theoretic skew lower bound of section 5. The fix (section 7) is runtime heavy-hitter detection plus targeted broadcast/replication of just that key, not uniform repartitioning.

---
*Part of the [DBMS Research catalog](../../README.md).*
