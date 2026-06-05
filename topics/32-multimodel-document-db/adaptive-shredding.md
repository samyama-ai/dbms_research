# Adaptive shredding of nested data

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/adaptive-shredding` · **Status:** empirically-open

## 1. Problem Statement
*Shredding* is the decomposition of nested (JSON/XML/Protobuf-style) records into flat relational columns. Given a stream of semistructured documents and an evolving query workload, decide **online** which nested substructures (fields, paths, repeated subtrees) to *materialize* as typed relational columns versus leaving them opaque in a blob/variant column.

- **Optimization variant:** choose a materialization set $M \subseteq P$ over the set of paths $P$ that minimizes expected workload cost plus storage/maintenance cost, subject to a storage budget $B$.
- **Online/decision variant:** at each timestep $t$ commit to a (possibly incremental) change $\Delta M_t$ to the materialized set under unknown future workload, competing against the best fixed offline $M^*$ (drift-aware).
- **Counting flavor:** estimate per-path access frequency and presence probability under sampling.

The hard part is *workload drift*: the optimal shredding under last week's queries may be pessimal today, and re-shredding is not free.

## 2. Mathematical Foundations
Model documents as ordered, labeled trees; let $P$ be observed root-to-leaf paths with presence probabilities $\pi(p)$ and per-query access indicators. Workload cost for a query $q$ under materialization $M$ is $c(q,M)$; shredded paths are read with column-scan cost, unshredded paths pay a parse/navigation penalty $\rho(p)$. Total objective:
$$\min_{M:\, \mathrm{store}(M)\le B}\ \sum_{q\in W} f(q)\, c(q,M) + \lambda\,\mathrm{maint}(M).$$
When $c$ has diminishing returns (each added column only helps the queries touching it), the benefit function is **monotone submodular**, so greedy gives a $(1-1/e)$ approximation (Nemhauser–Wolsey–Fisher) under a cardinality/knapsack budget. The online drift problem is a **metrical task system / online caching** instance: materializing/dropping columns are state transitions with switching cost, admitting competitive analysis and **regret** bounds (FTRL / online convex relaxations of the indicator vector $x\in[0,1]^{|P|}$). Presence estimation is a streaming frequency-moment problem (Count-Min / sampling, with $\varepsilon,\delta$ guarantees).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Snowflake's *VARIANT* with automatic sub-columnarization, Google **Dremel**/Capacitor (repetition/definition levels), Apache **Parquet/ORC** nested encoding, and **DuckDB**/ClickHouse JSON-type column inference. Snowflake and Amazon Redshift `SUPER` perform partial, statistics-driven shredding of frequently accessed paths.
- **Research-SOTA:** *Sinew* (Tahara et al., SIGMOD 2014) pioneered storing common JSON attributes as columns plus an overflow blob; *Argo*/NoBench benchmarks; learned/workload-driven physical design lines from *AutoAdmin* (Chaudhuri–Narasayya) and self-driving systems (**Peloton/NoisePage**, Pavlo et al.). Recent "JSON tiles" and adaptive flattening work (Durner, Leis, Neumann, **SIGMOD 2021**) is the closest direct attack.

## 4. Upper Bound
Offline budgeted version: greedy submodular maximization yields $(1-1/e)\approx 0.632$ of optimal benefit in $O(|P|\cdot|W|)$ oracle calls; partial-enumeration + greedy gives $(1-1/e)$ under a knapsack budget. The online caching reduction gives an $O(\log k)$-competitive randomized policy (Bansal–Buchbinder–Naor) where $k$ is the budget in columns, and FTRL gives $O(\sqrt{T})$ regret against the best fixed shredding in hindsight. These hold in the **oracle/online-learning model** with accurate cost estimates.

## 5. Lower Bound
- Exact budgeted selection generalizes weighted set cover / knapsack-constrained coverage: **NP-hard**, and inapproximable beyond $(1-1/e)$ unless P=NP (Feige).
- Deterministic online column caching is $\Omega(k)$-competitive (paging lower bound); randomized is $\Omega(\log k)$.
- Drift detection is information-theoretically bounded: distinguishing a distribution shift of magnitude $\delta$ needs $\Omega(1/\delta^2)$ samples (Le Cam / hypothesis-testing).

## 6. The Gap
Theory cleanly bounds the *static* and *adversarial-online* abstractions. The genuine openness is **empirical**: real cost functions are non-submodular (column groups interact via vectorization and I/O), drift is neither adversarial nor stationary, and re-shredding cost depends on data layout. No system has a policy with both provable drift-competitiveness *and* measured wins on production-like JSON workloads. Closing it requires cost models validated against real engines plus an online policy whose guarantees survive non-submodular interactions.

## 7. Current Research (as of June 2026)
Active directions: learned cost models for variant access, reinforcement-learning column advisors extending self-driving DBMS work, and "lazy/just-in-time" shredding that materializes on first repeated access. The TUM group (Neumann, Leis) and CMU self-driving DB group remain central; cloud-warehouse vendors publish incremental adaptive-columnarization results. *(frontier — verify: claims that production Snowflake/Redshift now do fully online drift-aware re-shredding rather than threshold-triggered materialization.)*

## 8. Future Work
- Drift-aware online policies with switching cost tuned to real reorganization cost.
- Joint optimization of shredding with vectorized execution (see *vectorized-nested-execution*) and statistics maintenance (see *evolving-schema-statistics*).
- Non-submodular benefit handling via curvature-aware greedy or supermodular degree bounds.
- Benchmarks capturing realistic schema/field drift.

## 9. Key References
- **[Foundational]** G. Nemhauser, L. Wolsey, M. Fisher. *An analysis of approximations for maximizing submodular set functions—I.* Mathematical Programming, 1978.
- **[Foundational]** S. Melnik et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010.
- **[SOTA]** D. Tahara, T. Diamond, D. Abadi. *Sinew: A SQL System for Multi-Structured Data.* SIGMOD, 2014.
- **[SOTA]** D. Durner, V. Leis, T. Neumann. *JSON Tiles: Fast Analytics on Semi-Structured Data.* SIGMOD, 2021.
- **[Foundational]** N. Bansal, N. Buchbinder, J. Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012.
- **[Survey]** S. Chaudhuri, V. Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
