# Holistic Aggregates in MPC

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/holistic-aggregates-mpc` · **Status:** open

## 1. Problem Statement

In the **Massively Parallel Computation (MPC)** model, $p$ machines each hold $O(N/p)$ of the input and proceed in synchronous *rounds* of computation interleaved with all-to-all communication; the cost measures are the **number of rounds** $r$ and the **per-machine load** $L$ (max bytes sent/received per round, typically targeted at $L = O(N/p)$ or $L = O(N^{1-\epsilon})$). The problem: **evaluate non-decomposable ("holistic") aggregates — MEDIAN/quantiles, COUNT DISTINCT, MODE — with simultaneously optimal rounds and load**, per group for a `GROUP BY`.

An aggregate is *holistic* (Gray et al.) when no constant-size partial state summarizes a sub-multiset: $\mathrm{MEDIAN}(A\cup B)$ is not a function of bounded summaries of $A$ and $B$ alone. This breaks the two-phase pre-aggregation that makes SUM/COUNT trivially parallel.

- **Decision variant:** Given target $(r, L)$, does a protocol computing the exact holistic aggregate exist?
- **Optimization variant:** Minimize rounds subject to load budget $L$ (and vice versa); trace the rounds–load Pareto frontier.
- **Approximation variant:** Allow $(\varepsilon,\delta)$ error and ask for the minimal load — usually far cheaper than exact.

The exact, low-load, low-round point is what is **open**.

## 2. Mathematical Foundations

The MPC model (Karloff–Suri–Vassilvitskii; Beame–Koutris–Suciu) generalizes MapReduce: with load $L=N^{1-\epsilon}$, sorting and many primitives take $O(1/\epsilon)$ rounds. Holistic aggregates reduce to **order/rank** and **distinctness** primitives:

- **Quantiles/MEDIAN** $\equiv$ **selection by rank** $k$: find $x$ with $\mathrm{rank}(x)=k$. Distributed selection has the classic randomized **$O(\log\log p)$-round** / deterministic $O(\log p)$-round structure, and the streaming lower bound for exact $\phi$-quantiles is $\Omega(N)$ space in one pass (Munro–Paterson), making *exact* quantiles fundamentally heavier than approximate ones.
- **COUNT DISTINCT** $\equiv$ **set cardinality** $|\bigcup_i S_i|$: exact distinct-count over $p$ machines is, in *communication complexity*, as hard as **set-disjointness/intersection-size**, with an $\Omega(N)$ total-communication lower bound for exactness (no sublinear exact protocol exists).
- **MODE** $\equiv$ **heavy-hitter / max-frequency**: finding the exact most-frequent value reduces to $F_\infty$ estimation, which has $\Omega(N)$ communication for exactness.

The approximate side is governed by **mergeable summaries** (Agarwal et al.): KLL/GK sketches for $\varepsilon$-quantiles in $O(\frac1\varepsilon\log\frac1\varepsilon)$ space, HyperLogLog / theta-sketches for $(1\pm\varepsilon)$ distinct-count in $O(\varepsilon^{-2})$ space, Count-Min/Misra–Gries for approximate mode. Mergeability restores associativity, collapsing the holistic aggregate to a *decomposable* one over summaries — but only approximately.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** MPC selection and sorting (Goodrich–Sitchinava–Zhang; Beame–Koutris–Suciu round/load theory) give $O(1/\epsilon)$-round sorting at load $N^{1-\epsilon}$, which solves exact quantiles by sorting then ranking. Exact distinct-count and mode inherit set-disjointness communication lower bounds, so no low-load exact protocol is known. The rounds–load Pareto frontier for *per-group, skewed* holistic aggregation is uncharted.
- **Systems-SOTA:** Engines (Spark, BigQuery, Presto/Trino, Druid, ClickHouse) ship **approximate** holistic aggregates — `APPROX_QUANTILES` (KLL/t-digest), `APPROX_COUNT_DISTINCT` (HLL++), theta-sketch set ops — precisely because exact versions force a hot reducer. Exact `COUNT(DISTINCT)`/`MEDIAN` fall back to a full sort/shuffle of the group, the very bottleneck this problem targets.

## 4. Upper Bound

For **approximate** holistic aggregates, mergeable summaries give an essentially optimal **$O(1)$-round, $O(p \cdot s(\varepsilon))$-load** tree-merge ($s(\varepsilon)$ = summary size), matching the streaming space lower bounds up to logs — this part is well in hand. For **exact** aggregates, the best general upper bound is *sort-then-scan*: $O(1/\epsilon)$ rounds at load $N^{1-\epsilon}$ (MPC sorting), or $O(\log_{L/N\cdot p} p)$ rounds at load $L$. These hold in the **MPC / BSP model** with the stated load. No upper bound avoids the sort-equivalent cost for exact distinct-count or mode under skew.

## 5. Lower Bound

Exactness is the barrier. **Communication complexity:** exact COUNT DISTINCT and exact MODE reduce from **set-disjointness**, whose randomized communication complexity is $\Omega(N)$ (Kalyanasundaram–Schnitger; Razborov), forcing $\Omega(N/p)$ load or super-constant rounds — an information-theoretic floor independent of computational assumptions. **One-pass streaming:** exact quantiles require $\Omega(N)$ space (Munro–Paterson), and even $p$-pass exact selection has $\Omega(N^{1/p})$ tradeoffs. **MPC round lower bounds** are conditional: unconditional $\omega(1)$-round lower bounds for $L=N^{1-\epsilon}$ would separate complexity classes, so for holistic aggregates we have the **conditional barrier** tied to the famous open *"one-versus-multiple rounds"* and *connectivity* MPC conjectures (no $o(\log N)$-round connectivity at low load, conjectured). Thus exact holistic aggregation is hard for the same reasons graph connectivity is conjectured hard in MPC.

## 6. The Gap

**Genuinely open** on the exact side. Approximate holistic aggregation is essentially closed (mergeable summaries are space/round optimal). The gap is: (1) **exact** holistic aggregates have an $\Omega(N)$ communication lower bound but no matching low-round protocol that meets it gracefully under **per-group skew** (one heavy group still funnels $\Omega(|g|)$ to one machine); (2) the **rounds-vs-load Pareto frontier** for exact selection/distinctness is not tight — we lack unconditional super-constant round lower bounds, blocked by the broader MPC lower-bound barrier; (3) no characterization couples *exact-vs-approximate error* with the *rounds × load* product. Closing (2) likely requires resolving central MPC conjectures.

## 7. Current Research (as of June 2026)

- Mergeable-summary theory pushed to relative-error quantiles and to **private** holistic aggregates (DP medians/distinct-counts), with optimal error–space tradeoffs *(frontier — verify)*.
- MPC lower-bound program (Roughgarden–Vassilvitskii–Wang conditional bounds; Ghaffari, Charikar, Im) continues attacking round complexity for selection/connectivity-like primitives *(frontier — verify)*.
- Sketch-accelerated exact engines: ClickHouse/DuckDB-style vectorized exact distinct under skew, and GPU quantile selection, motivated by hot-group bottlenecks *(frontier — verify)*.
- Overlap with secure computation: holistic aggregates under **cryptographic MPC** (secret-sharing) where rounds are also the cost metric, linking this to private-query systems.

## 8. Future Work

- A tight rounds–load characterization for **exact** per-group quantiles/distinct/mode under arbitrary value skew.
- Unconditional MPC round lower bounds for holistic primitives (would follow from, or feed into, the connectivity conjecture).
- A unified frontier trading approximation error $\varepsilon$ against the rounds × load product.
- Skew-aware exact protocols that split a single heavy group's holistic computation across machines without an $\Omega(|g|)$ funnel — connecting to skew-resilient aggregation.

## 9. Key References

- **[Foundational]** Jim Gray, Surajit Chaudhuri, Adam Bosworth, et al. *Data Cube: A Relational Aggregation Operator (distributive/algebraic/holistic taxonomy).* Data Mining and Knowledge Discovery, 1997.
- **[Foundational]** Paul Beame, Paraschos Koutris, Dan Suciu. *Communication Steps for Parallel Query Processing.* JACM, 2017 (PODS 2013).
- **[Foundational]** Howard Karloff, Siddharth Suri, Sergei Vassilvitskii. *A Model of Computation for MapReduce.* SODA, 2010.
- **[SOTA]** Pankaj K. Agarwal, Graham Cormode, Zengfeng Huang, Jeff M. Phillips, Zhewei Wei, Ke Yi. *Mergeable Summaries.* ACM TODS, 2013 (PODS 2012).
- **[Foundational]** J. Ian Munro, Mike S. Paterson. *Selection and Sorting with Limited Storage.* Theoretical Computer Science, 1980.
- **[SOTA]** Zohar Karnin, Kevin Lang, Edo Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016.
- **[SOTA]** Tim Roughgarden, Sergei Vassilvitskii, Joshua R. Wang. *Shuffles and Circuits: On Lower Bounds for Modern Parallel Computation.* JACM, 2018 (SPAA 2016).

---
*Part of the [DBMS Research catalog](../../README.md).*
