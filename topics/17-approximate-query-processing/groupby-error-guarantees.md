# Error Guarantees for Group-By Queries

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/groupby-error-guarantees` · **Status:** partially-solved

## 1. Problem Statement
Given a group-by aggregate `SELECT g, AGG(x) FROM T GROUP BY g` answered over a sample of size $n$, provide guarantees on (a) **per-group error** — a valid CI for each group's aggregate — and (b) **missing-group probability** — the chance a true group is absent from the sample and hence from the answer. The challenge is **high cardinality and skew**: with $G$ groups whose sizes follow a heavy-tailed distribution, a uniform sample of size $n$ allocates $\approx n\cdot N_g/N$ rows to group $g$, so small groups receive few or zero rows. Variants: **counting** (estimate the number of distinct groups present), **decision** (does group $g$ exist with `COUNT` $>\tau$?), **optimization** (allocate a budget to minimize max per-group error or expected missing-group count). Distinct from single-aggregate AQP because errors must hold *simultaneously across all groups*, requiring multiplicity correction.

## 2. Mathematical Foundations
Under uniform sampling at rate $p=n/N$, group $g$ with $N_g$ rows appears with probability $1-(1-p)^{N_g}\approx 1-e^{-pN_g}$; the expected number of **missing groups** is $\sum_g (1-p)^{N_g}$, dominated by the smallest groups (a coupon-collector / Good–Turing regime). The **Good–Turing** estimator bounds the total mass of unseen groups by $U/n$ where $U$ is the count of groups seen exactly once. Per-group estimates use the **Horvitz–Thompson** correction with the group's effective sample size $n_g$; per-group variance scales as $1/n_g$, so guarantees degrade for small $n_g$. **Simultaneous** validity over $G$ groups requires a union bound ($\delta/G$) or FDR control, widening intervals by $\sqrt{\log G}$. **Stratified / congressional** sampling reallocates rows to guarantee a floor $n_g\ge n_0$ per group, trading total accuracy for tail coverage. Distinct-group counting connects to **distinct-element sketching** (HyperLogLog, $O(\epsilon^{-2}\log\log N)$ space).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Congressional sampling** (Acharya, Gibbons, Poosala, SIGMOD 2000) — hybrid uniform + per-group "house+senate" allocation guaranteeing a per-group floor; **BlinkDB** stratified samples key strata on group columns; **Sample+Seek** (Ding et al., SIGMOD 2016) adds an index ("seek") to recover small/missing groups missed by the sample. Measure-biased sampling (Wander-Join-style) for group-by-join.
- **Theory-SOTA:** Good–Turing missing-mass concentration (McAllester–Schapire) gives provable bounds on unseen-group mass; distinct-count sketches give tight space-optimal group-presence estimates.

## 4. Upper Bound
With congressional/stratified allocation giving each present group $\ge n_0$ rows, per-group relative error is $O(1/\sqrt{n_0})$ with simultaneous validity at the cost of a $\sqrt{\log G}$ union-bound factor. Good–Turing bounds the missing-group mass within $O(1/\sqrt n)$ additive error w.h.p. Sample+Seek attains $\epsilon$ relative error per group with sample+index space $\tilde O(1/\epsilon^2)$ independent of $G$ for the groups it indexes. Distinct-group count to $1\pm\epsilon$ uses $O(\epsilon^{-2}\log\log N)$ space (HLL).

## 5. Lower Bound
**Information-theoretic:** a group with $N_g$ rows is invisible to any uniform sample of size $o(N/N_g)$, so guaranteeing presence of *all* groups requires $\Omega(N/N_{\min})$ samples — unbounded as $N_{\min}\to 1$ (coupon-collector). Hence no sample-only method can bound missing-group probability for arbitrarily small groups; some index/sketch is provably necessary. Estimating the number of distinct groups to constant factor from a sample requires $\Omega(N/N_{\min})$ samples (Charikar–Chaudhuri–Motwani–Narasayya lower bound for distinct-value estimation).

## 6. The Gap
**Partially solved**: per-group error for groups with a guaranteed sample floor is well-bounded, and missing-mass is estimable. The residual gap: tight *simultaneous* per-group guarantees under heavy skew without paying the full union-bound penalty, and bounding the *identity* (not just mass) of missing groups without a full index. Sample+Seek closes much of this for indexable predicates, but ad-hoc group columns with no precomputed index remain open.

## 7. Current Research (as of June 2026)
Directions: combining stratified samples with compact per-group sketches; FDR-controlled simultaneous CIs for group-by-having; learned models predicting small-group values; differentially private group-by where small groups face both sampling noise and privacy suppression. Groups: Bolin Ding / Surajit Chaudhuri (MSR/Alibaba), Graham Cormode (sketches), Barzan Mozafari (Keebo). *(frontier — verify)* sketch+sample hybrids claiming simultaneous per-group CIs at HLL-like space for million-group cubes.

## 8. Future Work
Provable simultaneous per-group CIs without $\sqrt{\log G}$ slack; missing-group *recovery* with sublinear auxiliary structures; integration with cube/materialized-view selection; private skewed group-by with utility floors.

## 9. Key References
- **[Foundational]** Acharya, Gibbons, Poosala. *Congressional Samples for Approximate Answering of Group-By Queries.* SIGMOD 2000.
- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimation Error Guarantees for Distinct Values.* PODS 2000.
- **[SOTA]** Ding, Huang, Chaudhuri, Chakkappen, Zhou. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD 2016.
- **[Foundational]** McAllester, Schapire. *On the Convergence Rate of Good-Turing Estimators.* COLT 2000.
- **[SOTA]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA 2007.

---
*Part of the [DBMS Research catalog](../../README.md).*
