# Optimal Bloom/filter memory allocation

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/filter-memory-allocation` · **Status:** partially-solved

## 1. Problem Statement
In an LSM-tree (log-structured merge tree), each run holds a probabilistic membership filter (classically a Bloom filter) consulted before a (costly) I/O to that run. Given a **global memory budget** $M$ bits shared across all runs, choose per-run bit allocations to **minimize the expected number of false-positive I/Os** for point lookups (and ideally for negative lookups specifically).

- **Optimization variant:** minimize $\sum_i w_i \cdot p_i(m_i)$ subject to $\sum_i m_i \le M$, where $m_i$ is bits assigned to run $i$, $p_i$ its false-positive rate (FPR), and $w_i$ the access weight (lookup frequency reaching that run).
- **Decision variant:** does an allocation exist meeting a target expected-FP-I/O rate within budget $M$?
- A richer variant jointly optimizes filter type (Bloom vs. quotient/cuckoo/ribbon), filter bits, and **fence-pointer / block-cache** memory — a multi-resource knapsack.

## 2. Mathematical Foundations
A Bloom filter on $n$ keys with $m$ bits and optimal hash count has FPR
$$p(m,n) \approx \left(1 - e^{-kn/m}\right)^k,\quad k=\tfrac{m}{n}\ln 2,\quad \Rightarrow\ p \approx e^{-(m/n)\ln^2 2}.$$
So $\ln p$ is (approximately) **linear** in bits-per-element $b=m/n$: $\ln p \approx -b\ln^2 2$. The expected FP cost is $\sum_i w_i\, e^{-b_i \ln^2 2}$. Because each term is convex decreasing in $b_i$ and the constraint is linear, the Lagrangian/KKT conditions give a clean optimum: marginal FPR reduction per bit must be equalized across runs. This yields the Monkey insight — under a leveled LSM, larger (deeper) levels should receive *fewer* bits per element, with optimal $b_i$ growing logarithmically toward shallower levels. The information-theoretic lower bound on bits for FPR $\varepsilon$ is $n\log_2(1/\varepsilon)$; Bloom filters are within a $\log_2 e \approx 1.44$ factor, while quotient/cuckoo/ribbon filters approach the bound.

## 3. State of the Art (SOTA)
- **Monkey** (Dayan, Athanassoulis, Idreos; SIGMOD 2017) solved the classic allocation analytically and showed the optimal allocation is *non-uniform*, cutting lookup cost asymptotically.
- **Dostoevsky** (SIGMOD 2018) and **the design continuum / Cosine** work generalized to the merge-policy/filter co-design space.
- **Systems-SOTA:** RocksDB ships ribbon filters (space-near-optimal) and per-level bits-per-key tuning; **SuRF**, **Chucky** (cuckoo-based, Dayan & Twitter 2021), and **ElasticBF** (adaptive per-SSTable allocation) push the runtime-adaptive frontier.

## 4. Upper Bound
For the fixed-workload, point-lookup-only objective with the linear $\ln p$ model, the optimum is computable in $O(L)$ closed form ($L$ = number of levels) via Lagrange multipliers (Monkey). With arbitrary convex per-run FPR curves, the continuous knapsack is solvable to $\varepsilon$-accuracy in polynomial time by greedy marginal allocation (convex separable resource allocation). Model: RAM / I/O cost model with known access weights.

## 5. Lower Bound
The **space** lower bound is information-theoretic: $n\log_2(1/\varepsilon)$ bits per filter; no allocation beats the per-filter Shannon limit. The *allocation* problem itself is easy (convex), so hardness arises only when (a) access weights are workload-dependent and shift online (then it becomes an online/regret problem), or (b) memory is shared with caches under integral, non-convex interactions, making the joint multi-resource version a knapsack-style NP-hard integer program.

## 6. The Gap
For the static, known-workload, point-lookup objective the gap is **closed** — hence "partially solved." Genuinely open: (i) optimality under *mixed* point+range+negative workloads with correlated keys, where the simple $\ln p$ model breaks; (ii) online allocation with shifting weights and provable regret; (iii) integral joint filter+cache+fence-pointer allocation with approximation guarantees.

## 7. Current Research (as of June 2026)
Active directions: workload-adaptive and learned allocation that observes live access skew and reallocates bits without rebuilds (ElasticBF lineage); filter-type co-optimization (ribbon/cuckoo) where the $\ln p$-linear assumption no longer holds, requiring per-type curves *(frontier — verify)*; and "memory-elastic" LSM engines that trade filter bits against block cache under a unified budget. Groups: Athanassoulis (BU DiSC), Idreos (Harvard), Dayan (industry/CMU lineage), and the RocksDB/Speedb teams. *(frontier — verify)* recent work on negative-lookup-specialized and prefix/range-aware allocation under unified budgets.

## 8. Future Work
- Provable online/regret-optimal reallocation under drifting workloads.
- Unified, integral filter + cache + fence-pointer allocation with approximation ratios.
- Allocation aware of key correlation and update/compaction amortization, not just steady-state FPR.

## 9. Key References
- **[SOTA]** Niv Dayan, Manos Athanassoulis, Stratos Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** Niv Dayan, Stratos Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Niv Dayan, Moshe Twitto. *Chucky: A Succinct Cuckoo Filter for LSM-Tree.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3457273)
- **[Foundational]** Burton H. Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970. — [DOI](https://doi.org/10.1145/362686.362692)
- **[Survey]** Chen Luo, Michael J. Carey. *LSM-based Storage Techniques: A Survey.* The VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)

## 10. Worked Example

Two LSM levels, each $n=10^6$ keys, equal lookup weight $w_1=w_2=1$. Budget $M=24$ Mbit total, i.e. average $b=12$ bits/element. Recall $\ln p\approx -b\ln^2 2$, so $p(b)=e^{-b\ln^2 2}$ with $\ln^2 2\approx 0.4805$.

**Uniform split** ($b_1=b_2=12$): $p=e^{-12\cdot0.4805}=e^{-5.77}\approx 3.1\times10^{-3}$ each. Expected FP I/Os per lookup $=p_1+p_2\approx 6.2\times10^{-3}$.

**Monkey optimum:** KKT requires equalizing the marginal FP-reduction per bit. Since both levels have equal $n$ and $w$ here, the symmetric point $b_1=b_2=12$ is already optimal *for two equal levels* — the interesting case is unequal sizes. Make level 2 hold $4\times$ the keys ($n_2=4n_1$) under the same $24$ Mbit. Equalizing marginals (each term $\propto n_i e^{-b_i\ln^2 2}$) gives $b_1-b_2=\frac{\ln 4}{\ln^2 2}=\frac{1.386}{0.4805}\approx 2.9$ bits: the **deeper, larger level gets fewer bits/element**. Plugging the budget constraint $n_1 b_1+n_2 b_2=24\text{M}$ yields $b_1\approx 14.3$, $b_2\approx 11.4$, cutting total expected FP I/Os below the uniform allocation — the Monkey insight that optimal filter memory is non-uniform across levels.

---
*Part of the [DBMS Research catalog](../../README.md).*
