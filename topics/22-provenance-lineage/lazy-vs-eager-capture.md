# Lazy vs. Eager Provenance Capture

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/lazy-vs-eager-capture` · **Status:** empirically-open

## 1. Problem Statement
Two strategies capture provenance. **Eager** propagation annotates every intermediate tuple during query execution (semiring annotations flow through operators), paying space and runtime overhead on *every* query regardless of whether provenance is ever queried. **Lazy** recomputation stores nothing extra at query time and reconstructs provenance on demand by *replaying / reenacting* the query (instrumenting only the slice needed to explain a specific output tuple). The problem: **for which workloads does lazy beat eager, and can a system choose the strategy adaptively per query/operator to minimize total cost?**

Variants: **(decision)** given a workload with capture cost model, does lazy dominate eager? **(optimization)** minimize expected total cost $= \alpha\cdot(\text{capture overhead}) + \beta\cdot(\text{provenance-query latency}) + \gamma\cdot(\text{storage})$ over a query stream with provenance-query probability $p$. **(online/adaptive)** without knowing future provenance-query rate, choose per-query to be competitive against the best fixed strategy.

## 2. Mathematical Foundations
Model a workload as a stream of queries; query $i$ has eager capture overhead $e_i$ (paid always) and, if provenance is later requested (probability $p_i$), a lazy recomputation cost $\ell_i$ (re-running the relevant subquery) versus an eager-read cost $r_i \ll \ell_i$. Expected cost:
$$ C_{\text{eager}} = \sum_i e_i + p_i r_i, \qquad C_{\text{lazy}} = \sum_i p_i \ell_i. $$
Lazy wins on query $i$ iff $p_i \ell_i < e_i + p_i r_i$, i.e. $p_i < e_i/(\ell_i - r_i)$. The decision is per-query *threshold on the provenance-query probability*. This is a **ski-rental / rent-or-buy** structure: pay incrementally (lazy) or buy upfront (eager). Recomputation correctness rests on **deterministic reenactment**: replaying $Q$ on the (possibly time-travel) base state reproduces the same provenance — formalized via the semiring homomorphism property of provenance-aware reenactment (Arab–Glavic). Lazy capture interacts with the **AGM/factorization** cost of the subquery: $\ell_i$ scales with the join's output, which the eager case may have already factorized.

## 3. State of the Art (SOTA)
- **Eager:** **Perm / GProM** (Glavic, Arab) rewrite queries to propagate provenance; **ProvSQL** propagates semiring circuits; **Trio** carried lineage eagerly for uncertain data. **Smoke** (Psallidas–Wu, 2018) builds lineage indexes *during* execution — a tuned eager point.
- **Lazy:** **GProM reenactment** (Arab et al., 2018) recomputes provenance of past transactions/queries via time-travel + rewriting, storing nothing eagerly. **DBNotes / where-provenance** systems and replay-based debuggers (e.g., dataflow lineage in Spark via RDD replay) are lazy in spirit.
- **Hybrid:** systems exposing both modes exist, but **adaptive per-query selection driven by a learned/observed $p_i$ is largely unaddressed**; the choice is typically a static configuration flag.

## 4. Upper Bound
For the online rent-or-buy formulation, the classic deterministic **ski-rental** algorithm is **2-competitive** (switch from lazy to eager once accumulated lazy cost reaches the eager buy-in), and the randomized variant achieves $\tfrac{e}{e-1} \approx 1.58$-competitive against the optimal offline strategy. With a learned predictor of $p_i$, **learning-augmented ski-rental** (Purohit–Svitkina–Kumar, NeurIPS 2018) interpolates: consistency $\to 1$ as predictions become accurate, robustness bounded by the worst-case ratio. Eager capture overhead is bounded multiplicatively: GProM-style rewriting incurs $O(1)$ extra operators per source operator, so eager runtime is within a constant factor of the base query for SPJ.

## 5. Lower Bound
No deterministic online algorithm beats **2-competitive** for ski-rental, and no randomized one beats $e/(e-1)$ — a tight info-theoretic lower bound that transfers directly to lazy/eager selection without future knowledge. There is **no closed-form analytic dominance**: the crossover depends on instance-specific $\ell_i$ (recomputation blow-up) and $p_i$, both of which are workload-dependent and not bounded a priori — hence the *empirically-open* status. Worst-case, lazy recomputation can cost $\Theta(|D|^{\rho^*})$ (full join re-evaluation) for a single explanation, while eager would have amortized that across the original run.

## 6. The Gap
The *theoretical* competitive question (rent-or-buy) is **closed** (tight 2 / 1.58). What remains **open is empirical and modeling**: there is no validated cost model that predicts $\ell_i, e_i, p_i$ accurately enough across realistic OLTP/OLAP/streaming workloads to drive the adaptive switch, and no published system that learns $p_i$ online and provably realizes near-optimal total cost. Closing it requires standardized benchmarks measuring the actual recompute-vs-annotate crossover.

## 7. Current Research (as of June 2026)
- Reenactment-based lazy provenance extended to **window/streaming and transactional** histories (Glavic group).
- Learning-augmented online algorithms applied to systems "rent-or-buy" knobs; applying them to provenance capture is an emerging thread *(frontier — verify)*.
- Workload-aware **hybrid materialization**: eager-annotate hot subqueries, lazy-replay cold ones, guided by a provenance-query log *(frontier — verify)*.

## 8. Future Work
A public benchmark fixing $(e_i,\ell_i,r_i,p_i)$ measurements across engines. Per-operator (not per-query) granularity — eager for cheap-to-annotate filters, lazy for blow-up joins. Online learning of $p_i$ with regret guarantees coupled to ski-rental robustness. Integration with time-travel storage so lazy replay is cheap.

## 9. Key References
- **[Foundational]** Boris Glavic, Gustavo Alonso. *Perm: Processing Provenance and Data on the Same Data Model through Query Rewriting.* ICDE, 2009.
- **[SOTA]** Bahareh Arab, Su Feng, Boris Glavic, Seokki Lee, Xing Niu, Qitian Zeng. *GProM — A Swiss Army Knife for Your Provenance Needs / Reenactment.* IEEE Data Eng. Bulletin, 2018.
- **[SOTA]** Fotis Psallidas, Eugene Wu. *Smoke: Fine-grained Lineage at Interactive Speed.* PVLDB, 2018.
- **[Foundational]** Manish Purohit, Zoya Svitkina, Ravi Kumar. *Improving Online Algorithms via ML Predictions.* NeurIPS, 2018.
- **[Survey]** Boris Glavic. *Data Provenance: Origins, Applications, Algorithms, and Models.* Foundations and Trends in Databases, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
