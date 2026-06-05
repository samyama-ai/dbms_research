# Encrypted Query Optimization and Planning

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/encrypted-query-optimization` · **Status:** open

## 1. Problem Statement

Classical cost-based optimization (Selinger) relies on **statistics** — histograms, cardinalities, selectivities — to estimate plan costs and pick join orders. In an **encrypted database** (CryptDB-style onion encryption, encrypted indexes, ORAM-backed stores, or secure-MPC/TEE engines), those statistics are *themselves sensitive*: revealing exact cardinalities or selectivities leaks plaintext information (the same volume/selectivity side channels exploited by leakage-abuse attacks). The problem is to perform **cost-based query optimization when the statistics the optimizer needs are encrypted, noised, or available only under a bounded-leakage / DP budget** — choosing join orders, access paths, and operator implementations that minimize encrypted-execution cost without the optimization process itself becoming a leakage oracle.

Variants:
- **Optimization:** choose the min-cost encrypted plan given only DP/encrypted statistics.
- **Decision:** decide whether plan $A$ dominates plan $B$ using leakage-bounded statistics.
- **Counting/estimation:** privately estimate cardinalities/selectivities under an $(\varepsilon,\delta)$ budget for use in costing.

## 2. Mathematical Foundations

A plan is a tree of physical operators with cost $\mathrm{cost}(p)=\sum_{o\in p} c(o,\hat\sigma)$ where $\hat\sigma$ are estimated cardinalities/selectivities. Under encryption, operator costs differ from plaintext: oblivious/ORAM operators have **data-independent worst-case cost** (a sorted-network join is $O(n\log^2 n)$ regardless of selectivity), so selectivity may not even *help* — unless DP-padded intermediate sizes (Shrinkwrap-style) are used, in which case the optimizer reasons about *noised cardinalities* $\hat N_i = N_i + \mathrm{Lap}(1/\varepsilon)$ with their own variance. Costing then minimizes **expected cost over the noise distribution** subject to a composition constraint $\sum_i \varepsilon_i \le \varepsilon$ on statistics gathering. The AGM bound $\prod_e \rho_e$ bounds worst-case intermediate sizes used when exact selectivities are hidden. The optimizer's *choice* is also an information channel: which plan it picks reveals something about $\hat\sigma$, so the planning decision must itself be leakage-bounded (analogous to simulatable auditing).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **Worst-case-optimal join** algorithms (Ngo, Porat, Ré, Rudra, *Generic Join* / Leapfrog Triejoin) give cardinality bounds (the AGM bound) usable when exact selectivities are unavailable — a natural fit for statistics-blind encrypted planning. DP cardinality/selectivity estimation reuses DP-quantile and DP-histogram theory.
- **Systems-SOTA:** **CryptDB** (Popa et al., SOSP 2011) executes SQL over onion-encrypted data but offloads optimization to the plaintext-shaped query structure; it does not optimize over encrypted stats. **Shrinkwrap** (Bater et al., VLDB 2019) and **SMCQL** (Bater et al., VLDB 2017) plan *oblivious* query execution and use DP-noised intermediate cardinalities to size padding — the closest to encrypted-statistics-aware planning. TEE-based engines (**EnclaveDB**, **Opaque** — Zheng et al., NSDI 2017) provide oblivious operators with cost models but largely fixed/oblivious plans. **Senate** (Poddar et al., USENIX Security 2021) plans collaborative MPC queries cost-aware.

## 4. Upper Bound

Worst-case-optimal join runs in time $O(\mathrm{AGM}(Q))$ — meeting the fractional-edge-cover bound — *without* needing per-relation selectivities, an upper bound that survives statistics being hidden. Oblivious operators (Opaque/Shrinkwrap) execute in data-independent $O(n\log^2 n)$ (oblivious sort/join) with DP-padded intermediates of expected size true + $O(\frac1\varepsilon\log\frac1\delta)$. Costing over noised cardinalities is a poly-time expected-cost minimization once the plan space is enumerated; selectivity estimation under DP achieves $\pm O(\frac1\varepsilon\log n)$ error per estimate.

## 5. Lower Bound

Join-order optimization is **NP-hard** (Ibaraki–Kameda) already in the plaintext, cleartext-statistics model; adding encrypted/noised statistics only makes the estimation inputs worse, so the problem inherits NP-hardness. Oblivious execution inherits the **$\Omega(\log n)$ ORAM bandwidth lower bound** (Larsen–Nielsen, CRYPTO 2018), so no encrypted plan can beat plaintext cost asymptotically without conceding leakage. Information-theoretically, accurate selectivity estimation under $(\varepsilon,\delta)$-DP has error $\Omega(1/\varepsilon)$ (Laplace lower bound), so plan choices that hinge on fine selectivity differences are fundamentally uncertain. The planning *decision channel* is bounded by DP composition over the statistics queried.

## 6. The Gap

The gap is **genuinely open**. There is no Selinger-style optimizer that (a) costs *encrypted/oblivious* operators accurately, (b) consumes only **leakage-bounded statistics** with a formal budget, and (c) proves its plan choice is near-optimal *and* non-disclosive. Today's encrypted engines either run fixed oblivious plans (no real optimization) or optimize on plaintext-shaped statistics (leaky). Closing it needs: an encrypted-operator cost model, a DP/leakage accountant for statistics gathering integrated into costing, and a treatment of the optimizer's own decision as a bounded-leakage channel — plus approximation guarantees over noised inputs.

## 7. Current Research (as of June 2026)

- Cost models for **oblivious / TEE operators** with DP-noised intermediate cardinalities folded into plan enumeration *(frontier — verify)*.
- DP selectivity/cardinality sketches (private Count-Min / HyperLogLog) feeding a leakage-budgeted optimizer *(frontier — verify)*.
- Worst-case-optimal-join-based planning for encrypted stores to sidestep selectivity leakage entirely.
- Groups: the secure-query-processing line (Bater/Rogers/Kantarcioglu — SMCQL/Shrinkwrap), MPC-query systems (Senate, Poddar/Popa), and TEE engines (Opaque/EnclaveDB).

## 8. Future Work

- A provably near-optimal encrypted optimizer over DP-noised statistics with a leakage budget.
- Treating the chosen plan as a controlled leakage channel (simulatable planning).
- Adaptive re-optimization on encrypted data without re-leaking.
- Cost models unifying ORAM, MPC, and TEE operator families.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018.
- **[SOTA]** Popa, Redfield, Zeldovich, Balakrishnan. *CryptDB: Protecting Confidentiality with Encrypted Query Processing.* SOSP, 2011.
- **[SOTA]** Bater, Elliott, Eggen, Goel, Kho, Rogers. *SMCQL: Secure Querying for Federated Databases.* VLDB, 2017.
- **[SOTA]** Bater, He, Ehrich, Machanavajjhala, Rogers. *Shrinkwrap: Efficient SQL Query Processing in Differentially Private Data Federations.* VLDB, 2019.
- **[SOTA]** Zheng, Dave, Beekman, Popa, Gonzalez, Stoica. *Opaque: An Oblivious and Encrypted Distributed Analytics Platform.* NSDI, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
