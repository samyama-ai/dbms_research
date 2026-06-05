# Optimal time-partitioning (chunking) policy

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/time-chunking-policy` · **Status:** open

## 1. Problem Statement
Time-series engines physically split each series (or hypertable) into *chunks* — contiguous, time-bounded partitions that are the unit of compression, retention, indexing, and query pruning. The **chunking policy** decides chunk boundaries $0 = t_0 < t_1 < \dots$ (equivalently chunk durations/widths) so as to co-optimize four coupled costs: (i) ingest throughput (small recent chunks fit in memory and absorb out-of-order writes cheaply); (ii) compression ratio (larger, homogeneous chunks amortize codec headers and exploit longer runs); (iii) query pruning (finer chunks let the planner skip more data via min/max time and value zonemaps); (iv) retention/tiering (chunks are dropped or migrated whole).

We distinguish three variants. **Decision:** given a workload and a budget $B$ (bytes or dollars), does a boundary set exist with total cost $\le B$? **Optimization:** minimize expected weighted cost $\sum_w \alpha_w \cdot \mathrm{cost}_w(\text{boundaries})$ over ingest/compress/scan/retention terms. **Online:** boundaries must be chosen as data arrives, without knowing future arrival rates, cardinality, or the query mix.

## 2. Mathematical Foundations
Model a series as points $(t_i, v_i)$ with arrival process $\lambda(t)$ and a query distribution $\mathcal{Q}$ over time ranges $[a,b]$ and predicates. A partition $\Pi = \{[\tau_j, \tau_{j+1})\}$ induces cost
$$ C(\Pi) = \underbrace{\sum_j g_{\mathrm{ing}}(\tau_{j+1}-\tau_j)}_{\text{ingest}} + \underbrace{\sum_j g_{\mathrm{cmp}}(\text{block}_j)}_{\text{storage}} + \underbrace{\mathbb{E}_{[a,b]\sim\mathcal{Q}}\!\big[\textstyle\sum_j \mathbf{1}[[\tau_j,\tau_{j+1})\cap[a,b]\ne\emptyset]\cdot s_j\big]}_{\text{scan after pruning}} + g_{\mathrm{ret}}(\Pi). $$
When per-chunk costs are *additive and separable* over a 1-D timeline, the optimal offline boundary set is a classic **interval-partition DP**: with $n$ candidate boundaries, $\mathrm{OPT}[k]=\min_{j<k}\mathrm{OPT}[j]+c(j,k)$ solves in $O(n^2)$, reducible to $O(n\log n)$ under the Monge/quadrangle-inequality (concave) condition via SMAWK or the Knuth–Yao speedup. The scan term, however, couples boundaries to a *query distribution*, and value-zonemap pruning makes $c(j,k)$ depend on data order, breaking separability — this is where hardness enters. Online versions connect to **competitive analysis** of list/partition maintenance and to the *bin-packing-with-time* and *interval scheduling* literatures.

## 3. State of the Art (SOTA)
**Systems-SOTA:** TimescaleDB popularized fixed-interval "hypertable" chunking with a heuristic target of "chunk fits in 25% of memory"; InfluxDB IOx and Apache Arrow/Parquet engines use shard/partition durations plus row-group sizing; Gorilla/Prometheus TSDB use fixed 2-hour blocks compacted into wider blocks. Apache IoTDB and QuestDB use time-partition directories. All ship *static, hand-tuned* defaults with optional manual override; none solve the co-optimization formally. **Theory-SOTA:** the separable offline case is solved optimally by SMAWK-accelerated DP (Aggarwal et al. 1987 monotone-matrix machinery); histogram/V-optimal partitioning (Jagadish et al., VLDB 1998) gives the closest formal analog for the storage+scan trade-off.

## 4. Upper Bound
For the **offline, additive, concave-cost** model: $O(n\log n)$ time (SMAWK / Knuth-optimization DP) for the exact optimum over $n$ candidate boundaries, in the RAM model. With a query distribution but *time-only* pruning (no value zonemaps), the scan term remains a sum of interval-overlap indicators and the problem stays poly-time via the same DP. For the **online** setting, a doubling/merge scheme (start fine, merge adjacent chunks geometrically as they cool) gives $O(1)$-competitive *storage* amortization à la LSM compaction, but no known constant-competitive bound jointly over scan+ingest.

## 5. Lower Bound
No unconditional super-linear lower bound is known for the clean separable case (the DP is near-optimal). Hardness arises once boundaries interact with **value-based pruning** and **multi-series shared partitions**: choosing boundaries to maximize zonemap skip across a query set generalizes **weighted interval/set problems** and is NP-hard by reduction from partition/knapsack-style packing when chunk costs are non-separable. Online, an adversarial-arrival argument gives an $\Omega(\log(\text{ratio}))$ competitive lower bound on storage amortization analogous to LSM amplification bounds; the joint ingest+scan online competitive ratio is *open*.

## 6. The Gap
The separable offline problem is essentially **closed** (matching $O(n\log n)$ DP). The realistic problem — non-separable value-pruning, multi-series co-partitioning, unknown future workload — is **genuinely open**: we lack both a tight approximation algorithm and a matching hardness/competitive lower bound. Closing it requires either a PTAS for the non-separable scan term or an NP/APX-hardness reduction, plus a competitive-ratio characterization for the online variant under stochastic arrivals.

## 7. Current Research (as of June 2026)
Active threads: learned/adaptive partitioning that ties chunk width to live cardinality and ingest pressure (Timescale, QuestDB engineering); workload-driven physical design borrowing from self-driving DB tuners (CMU NoisePage/OtterTune lineage) applied to TSDB layout *(frontier — verify)*; and zonemap/data-skipping co-design with reordering (work descending from Hyrise/Snowflake micro-partitioning). RL-based online chunk-merging policies have appeared in vendor blogs but lack published competitive guarantees *(frontier — verify)*.

## 8. Future Work
- A formal cost model unifying ingest, compression-ratio-vs-width, value-zonemap pruning, and tiering into one objective with proven approximation guarantees.
- Online competitive analysis under stochastic/adversarial arrival and drifting query mixes.
- Multi-series *shared* partition boundaries (co-partitioning correlated series) as a clustering+partition joint optimization.
- Integration with the cost-based optimizer (see `tsdb-cost-based-optimization.md`) so partitioning decisions are planner-visible.

## 9. Key References
- **[Foundational]** H. V. Jagadish, N. Koudas, S. Muthukrishnan, V. Poosala, K. Sevcik, T. Suel. *Optimal Histograms with Quality Guarantees.* VLDB, 1998. — [DBLP](https://dblp.org/rec/conf/vldb/JagadishKMPSS98.html)
- **[Foundational]** A. Aggarwal, M. Klawe, S. Moran, P. Shor, R. Wilber. *Geometric applications of a matrix-searching algorithm (SMAWK).* Algorithmica, 1987. — [DOI](https://doi.org/10.1007/BF01840359)
- **[SOTA]** M. Stonebraker et al. / Timescale. *TimescaleDB: SQL made scalable for time-series data.* (system; hypertable chunking design), 2017–. *(unverified)*
- **[SOTA]** T. Pelkonen et al. *Gorilla: A Fast, Scalable, In-Memory Time Series Database.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824078)
- **[Survey]** S. Chaudhuri, V. Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN07.html)

## 10. Worked Example

Consider a 6-hour ingest with candidate boundaries every hour: $t_0,\dots,t_6$. We must pick a sub-partition. Define a separable chunk cost $c(j,k)$ for the chunk $[t_j,t_k)$ as $\text{storage} + \text{scan}$, where storage favors *wider* chunks (codec header $h=2$ amortized once per chunk) and scan favors *finer* chunks (queries touch only overlapping chunks).

Suppose each hour holds 100 points; storage $=h + 0.5\cdot(\text{points})$ and the workload is one recurring query over $[t_2,t_4)$ that pays a flat $20$ per chunk it must open. Two candidate partitions:

- **One chunk** $[t_0,t_6)$: storage $=2+0.5\cdot600=302$; the query opens 1 chunk $\Rightarrow$ scan $=20$. Total $=322$.
- **Hourly chunks** ($6$ chunks): storage $=6\cdot(2+50)=312$; the query overlaps exactly 2 chunks ($[t_2,t_3),[t_3,t_4)$) $\Rightarrow$ scan $=40$. Total $=352$.
- **Aligned split** $\{[t_0,t_2),[t_2,t_4),[t_4,t_6)\}$: storage $=3\cdot(2+100)=306$; query opens 1 chunk $\Rightarrow$ scan $=20$. Total $=\mathbf{326}$.

The DP recurrence $\mathrm{OPT}[k]=\min_{j<k}\mathrm{OPT}[j]+c(j,k)$ finds the single-chunk optimum (322) here, but note how *boundary alignment* to the query edge ($t_2,t_4$) lets the 3-chunk plan undercut hourly chunks — illustrating why the scan term couples boundaries to the query distribution.

---
*Part of the [DBMS Research catalog](../../README.md).*
