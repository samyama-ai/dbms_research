# Pay-per-query pricing-truthfulness

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/pricing-truthfulness` · **Status:** open

## 1. Problem Statement

Query-as-a-service platforms (BigQuery, Athena, Snowflake serverless, Redshift Serverless) charge **per query** based on a metered resource — bytes scanned, slot-seconds, or estimated compute. A pricing function $p:\mathcal{Q}\times\mathcal{D}\to\mathbb{R}_{\ge0}$ maps a query $q$ over data $D$ to a charge. The problem: design $p$ that is **incentive-compatible / truthful** — a tenant cannot lower their bill below their true resource consumption by *gaming* the system: rewriting queries to fool the **cost estimator**, exploiting estimator under-counting, fragmenting/batching to exploit pricing nonlinearities, or strategically structuring data/queries so the *charged* metric diverges from *actual* cost incurred by the provider.

Variants:
- **Mechanism-design (truthfulness):** is there $p$ such that for every tenant, truthful query submission (no obfuscating rewrite) weakly minimizes their charge, while $p$ covers provider cost? 
- **Robust-estimation:** bound the gap $|c_{\text{charged}} - c_{\text{actual}}|$ when the estimator is adversarially probed.
- **Fairness/individual rationality:** ensure no tenant subsidizes another and each prefers participating.

## 2. Mathematical Foundations

This sits at the intersection of **algorithmic mechanism design** and **query optimization**. Truthfulness is the mechanism-design notion of **dominant-strategy incentive compatibility (DSIC)**; the canonical truthful mechanism is **VCG**, and the **revelation principle** says we may restrict attention to direct truthful mechanisms. Pricing that is *consistent* (charge equals an intrinsic cost) connects to **cost-sharing** mechanisms and the **Shapley value** for splitting shared scan/compute among co-running queries; **Moulin mechanisms** give group-strategyproof cost sharing for submodular costs.

The estimator is the weak point: query optimizers estimate cost from **cardinality estimates**, which are provably error-prone — selectivity estimation has worst-case multiplicative error and known *propagation-of-error* blowups (Ioannidis–Christodoulakis); the **AGM bound** gives the only tight worst-case size guarantee for joins, so any charge tied to estimated intermediate sizes can be manipulated up to the estimator's error. Robustness to gaming is naturally an **adversarial / online** problem: bound the **competitive ratio** or **regret** of $p$ against a strategic tenant, or prove a **price of anarchy** for the induced game.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Production pricing is *deliberately simple to be hard to game*: BigQuery's **bytes-scanned** model prices on a quantity measurable *exactly after the fact* (not an estimate), with columnar pruning and partition/cluster pruning making the metric data-dependent but verifiable; Snowflake/Redshift Serverless price on **credits/compute-seconds** (warehouse time, RPU-hours). These trade *truthfulness-by-measurability* for poor *predictability* (users cannot cheaply forecast the bill) and still admit gaming via partition design and result caching. There is no deployed mechanism with a *proven* incentive-compatibility guarantee for query pricing.

**Theory-SOTA.** The closest rigorous lines are **"query-based pricing"** / **pricing the data itself** — Koutris, Upadhyaya, Balazinska, Howe, Suciu (*Query-Based Data Pricing*, PODS/JACM 2012–2015), which builds *arbitrage-free* and *discount-free* price functions over queries — and the broader **data-market / data-valuation** literature (Shapley-value data pricing; Agarwal–Dahleh–Sarkar data-market designs). These give axiomatic pricing but target *information value*, not *provider resource truthfulness*.

## 4. Upper Bound

Positive results are *conditional*. If the charged metric is **ex-post measurable and reproducible** (bytes actually scanned), then charging that metric is trivially truthful in the sense that no query rewrite reduces the bill without reducing real work — an exact mechanism with zero charge–cost gap, at the price of unpredictability. For *predictable* pricing on estimates, the achievable robustness is bounded by the estimator: a $(1\pm\varepsilon)$-accurate, manipulation-resistant estimator yields a charge within factor $(1\pm\varepsilon)$ of cost, but no general optimizer provides such $\varepsilon$ adversarially. Query-based pricing gives **arbitrage-free** price functions (a structural upper bound on consistency) computable for restricted query classes (conjunctive queries) — but with hardness for general queries.

## 5. Lower Bound

Several impossibilities. **(a)** Determining arbitrage-free prices for general (even conjunctive) query pricing is **coNP-hard / #P-hard** in cases (Koutris et al.), so an *efficiently computable* fully-consistent price function does not exist for rich query classes unless complexity classes collapse. **(b)** Any pricing tied to *estimated* cost inherits cardinality-estimation's worst-case error, which is unbounded multiplicatively in the worst case; thus a tenant can in principle drive the charged–actual gap arbitrarily by adversarial query/data construction (an information-theoretic / estimator lower bound). **(c)** General mechanism-design impossibilities (Green–Laffont; Myerson–Satterthwaite-style) imply no mechanism is simultaneously truthful, budget-balanced, efficient, and individually rational in the general setting — so *some* desideratum must be sacrificed.

## 6. The Gap

Wide open. Industry sidesteps truthfulness by pricing an *ex-post verifiable* metric, sacrificing predictability and still leaving structural gaming (partition/cache exploitation). Theory has axiomatic *data*-pricing (arbitrage-freeness) but not *resource*-pricing truthfulness for query execution; the two literatures have not been unified. No known mechanism is provably (i) incentive-compatible against estimator gaming, (ii) budget-balanced for the provider, (iii) predictable to the tenant, and (iv) efficiently computable. Closing it requires either (a) manipulation-resistant cost estimators with provable adversarial error bounds, or (b) a mechanism whose truthfulness does not depend on the estimator at all (measurement-based), made predictable via bounds.

## 7. Current Research (as of June 2026)

Directions: **learned cost models** (and learned cardinality estimators) with calibrated, *adversarially robust* uncertainty so charges can be bounded *(frontier — verify)*; **data-market mechanism design** extending Shapley-value pricing toward incentive properties; and **multi-tenant fair cost-sharing** for shared scans/serverless pools (who pays for a co-used scan?). Groups/people: Suciu and Balazinska and Koutris (UW — query-based pricing), Dahleh and Sarkar and Agarwal (MIT — data markets), and the learned-query-optimization community (Kraska, Marcus, Negi) on robust cost estimation. Frontier claim: *robust learned cost estimators with certified error bands could enable predictable yet hard-to-game pricing, but no production system yet ships one* *(frontier — verify)*.

## 8. Future Work

- Estimator designs with *certified* adversarial error bounds usable as a pricing basis.
- A unified axiomatic framework merging arbitrage-free data pricing with provider-resource truthfulness.
- Group-strategyproof cost-sharing for multi-tenant serverless pools (shared scans, shared caches).
- Mechanisms trading off the four desiderata with quantified Pareto frontiers; price-of-anarchy analysis of real pricing schemes.

## 9. Key References

- **[Foundational]** N. Nisan, A. Ronen. *Algorithmic Mechanism Design.* Games and Economic Behavior / STOC, 1999. — [DOI](https://doi.org/10.1006/game.1999.0790) · [STOC DOI](https://doi.org/10.1145/301250.301287)
- **[Foundational]** H. Moulin, S. Shenker. *Strategyproof Sharing of Submodular Costs.* Economic Theory, 2001. — [DOI](https://doi.org/10.1007/PL00004200)
- **[SOTA]** P. Koutris, P. Upadhyaya, M. Balazinska, B. Howe, D. Suciu. *Query-Based Data Pricing.* PODS 2012 / JACM, 2015. — [JACM DOI](https://doi.org/10.1145/2770870) · [PODS DOI](https://doi.org/10.1145/2213556.2213582)
- **[Foundational]** Y. Ioannidis, S. Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991. — [DOI](https://doi.org/10.1145/115790.115835) · [DBLP](https://dblp.org/rec/conf/sigmod/IoannidisC91.html)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Computing / FOCS, 2008. — [SIAM DOI](https://doi.org/10.1137/110859440) · [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html)
- **[SOTA]** A. Agarwal, M. Dahleh, T. Sarkar. *A Marketplace for Data: An Algorithmic Solution.* EC, 2019. — [arXiv](https://arxiv.org/abs/1805.08125) · [DOI](https://doi.org/10.1145/3328526.3329589)

## 10. Worked Example

Bytes-scanned pricing is truthful-by-measurability. A table $T$ has columns (id, region, amount); a tenant runs `SELECT amount FROM T WHERE region='EU'`. With columnar storage the engine reads only the `region` and `amount` columns — say $2$ GB of the $6$ GB table — and charges on $2$ GB *actually scanned*, at \$5/TB $= \$0.01$. No rewrite lowers the bill without doing less real work, so the charge–cost gap is $0$.

Contrast estimate-based pricing. Suppose the optimizer estimates an intermediate join result at $10^4$ rows but the AGM bound only guarantees $|Q| \le \prod_e |R_e|^{x_e}$; for a 3-way cycle join on relations of size $N$ the bound is $N^{3/2}$. With $N=10^3$ the worst-case true size is $\approx 31{,}600$, more than $3\times$ the estimate. A tenant crafting data to hit this worst case is charged on $10^4$ but consumes $31{,}600$ — the charged–actual gap is unbounded multiplicatively as $N$ grows (section 5(b)).

Mechanism tension: by Myerson–Satterthwaite no pricing is simultaneously truthful, budget-balanced, efficient, and individually-rational — industry sacrifices predictability to keep the first three.

---
*Part of the [DBMS Research catalog](../../README.md).*
