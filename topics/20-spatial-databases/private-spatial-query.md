# Privacy-preserving spatial queries

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/private-spatial-query` · **Status:** partially-solved

## 1. Problem Statement
Given a database $D$ of geo-located records (points, trajectories, or location histories) and a query workload of **range** and **$k$-nearest-neighbor (kNN)** queries, answer the queries while provably limiting what an adversary learns about any individual record. Two largely orthogonal threat models must be distinguished:

- **Output-privacy (statistical):** the *answer* should not reveal whether any one record is in $D$. Formalized by **differential privacy (DP)**: a mechanism $M$ is $(\varepsilon,\delta)$-DP if for neighboring $D\sim D'$ and all measurable $S$, $\Pr[M(D)\in S]\le e^{\varepsilon}\Pr[M(D')\in S]+\delta$. The optimization variant minimizes added error (utility loss) for a target $\varepsilon$.
- **Access-privacy (cryptographic):** an untrusted server must answer without learning the query *or* the access pattern. Formalized by **oblivious RAM (ORAM)**, **structured/searchable encryption**, or **PIR**, where the access-pattern distribution is independent of the query.

The research problem is to obtain **acceptable utility and overhead simultaneously**: DP spatial decompositions with low query error, or oblivious spatial indexes whose bandwidth/round overhead is polylogarithmic rather than catastrophic. Variants: a *decision* form (membership inference resistance), an *optimization* form (minimize $\ell_\infty$/$\ell_2$ workload error at fixed $\varepsilon$), and a *counting* form (DP range-count release).

## 2. Mathematical Foundations
DP spatial answering rests on **spatial decompositions** — quadtrees, kd-trees, and grid hierarchies — whose counts are released via the **Laplace** ($\mathrm{Lap}(\Delta/\varepsilon)$, $\ell_1$-sensitivity $\Delta$) or **Gaussian** mechanism. For a hierarchy of height $h$, sequential composition spends $\varepsilon/h$ per level; **hierarchical/consistency methods** (the **matrix mechanism**, a workload-aware view) optimize variance across a workload via a strategy matrix $A$ minimizing $\|A^{+}W\|$ subject to $\|A\|_1\le 1$ ($\ell_1$ column norm). **PrivTree** gives data-adaptive partitioning without a fixed depth budget.

Range-query error under DP has an information-theoretic floor: answering all $1$-D range (prefix) queries to $\ell_\infty$ error $o(\log n)$ violates $\varepsilon$-DP — the **Hardt–Talwar / Bun–Ullman** discrepancy lower bounds give $\Omega(\log n)$ for the dyadic-interval workload, and $d$-dimensional rectangles scale as $\Omega(\log^{d} n)$ up to constants. For ORAM, the **Goldreich–Ostrovsky** bound forces $\Omega(\log n)$ amortized overhead per logical access in the balls-in-bins model. kNN further requires hiding *result size*, linking to **volume-hiding** encrypted multi-maps.

## 3. State of the Art (SOTA)
- **Theory-SOTA (DP):** Matrix mechanism (Li–Hay–Rastogi–Miklau, PODS 2010); **PrivTree** (Zhang–Xiao–Xie, SIGMOD 2016); near-optimal range-counting via discrepancy (Muthukrishnan–Nikolov, STOC 2012).
- **Systems-SOTA (DP):** the QuadTree/UG/AG comparison of Qardaji–Yang–Li (ICDE 2013) for 2-D range counts; **Geo-indistinguishability** (Andrés et al., CCS 2013) for single-report obfuscation; local-DP location telemetry (Apple/Google deployments).
- **Crypto-SOTA:** Path-ORAM (Stefanov et al., CCS 2013) as the index substrate; oblivious R-trees / oblivious kNN built atop ORAM; encrypted spatial range via order-revealing/structured encryption with controlled leakage.

## 4. Upper Bound
- **DP range counting:** $\ell_\infty$ error $O(\log^{1.5d} n / \varepsilon)$ for $d$-dimensional rectangle workloads via hierarchical strategies; $O(\log^d n)$ for the dyadic decomposition with optimal constants from the matrix mechanism (RAM model, $(\varepsilon,0)$-DP).
- **Oblivious kNN/range:** $O(\log^2 n)$ amortized bandwidth blowup using a tree-ORAM-backed spatial index, $O(\log n)$ rounds (semi-honest server, computational ORAM model). PIR-based single-server schemes achieve sublinear communication under LWE but with heavy compute.

## 5. Lower Bound
- **DP:** $\Omega(\log^d n)$ $\ell_\infty$ error for $d$-dim range counting (discrepancy / packing lower bounds, **information-theoretic**, $\varepsilon$-DP). For $(\varepsilon,\delta)$-DP the floor is $\Omega((\log n)^{?})$ but provably nonzero.
- **Crypto:** Goldreich–Ostrovsky $\Omega(\log n)$ ORAM overhead (balls-in-bins / cell-probe-style); Larsen–Nielsen (CRYPTO 2018) prove $\Omega(\log n)$ holds even for online ORAM in the cell-probe model. PIR has the trivial $\Omega(1)$ communication but $\Omega(n)$ server work without preprocessing (single-server, information-theoretic).

## 6. The Gap
For DP range counting the upper and lower bounds match up to $\mathrm{polylog}$ factors in the exponent's lower-order terms — **essentially closed for the $\ell_\infty$ metric**, open for the constant in $(\varepsilon,\delta)$-DP and for kNN utility (where no clean error notion exists). For oblivious access the $\Theta(\log n)$ asymptotics are tight, but the *constant* overhead and the **kNN-specific** result-size leakage remain genuinely open: no scheme simultaneously hides access pattern, result size, and achieves sub-$10\times$ practical overhead.

## 7. Current Research (as of June 2026)
- Workload-adaptive DP synopses combining PrivTree with the matrix mechanism for *spatiotemporal* (moving-object) workloads *(frontier — verify)*.
- DP for trajectory release under **user-level** (not event-level) neighboring relations; sequence-DP and Fréchet-aware noise.
- Hardware-enclave (TEE)-assisted oblivious spatial indexes as a pragmatic middle ground; oblivious learned indexes.
- Groups: Ashwin Machanavajjhala / Gerome Miklau (DP systems), Ninghui Li (spatial DP), Catuscia Palamidessi (geo-indistinguishability), Elaine Shi / Kasper Green Larsen (ORAM bounds).

## 8. Future Work
Tight result-size-hiding kNN; composing DP output-privacy with cryptographic access-privacy without multiplying overheads; DP under continual observation for streaming location feeds; standardized utility benchmarks for private kNN.

## 9. Key References
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006.
- **[Foundational]** Goldreich, Ostrovsky. *Software Protection and Simulation on Oblivious RAMs.* J. ACM, 1996.
- **[SOTA]** Zhang, Xiao, Xie. *PrivTree: A Differentially Private Algorithm for Hierarchical Decompositions.* SIGMOD, 2016.
- **[SOTA]** Li, Hay, Rastogi, Miklau, McGregor. *Optimizing Linear Counting Queries under Differential Privacy.* PODS, 2010.
- **[SOTA]** Andrés, Bordenabe, Chatzikokolakis, Palamidessi. *Geo-indistinguishability: Differential Privacy for Location-Based Systems.* CCS, 2013.
- **[SOTA]** Larsen, Nielsen. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
