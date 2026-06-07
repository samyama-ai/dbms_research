---
id: 17-approximate-query-processing/groupby-error-guarantees
title: "Error Guarantees for Group-By Queries"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

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
- **[Foundational]** Acharya, Gibbons, Poosala. *Congressional Samples for Approximate Answering of Group-By Queries.* SIGMOD 2000. — [DBLP search](https://dblp.org/search?q=Congressional%20Samples%20for%20Approximate%20Answering%20of%20Group-By%20Queries)
- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimation Error Guarantees for Distinct Values.* PODS 2000. — [ACM](https://dl.acm.org/doi/10.1145/335168.335230)
- **[SOTA]** Ding, Huang, Chaudhuri, Chakkappen, Zhou. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD 2016. — [DBLP](https://dblp.org/rec/conf/sigmod/DingHCC016.html)
- **[Foundational]** McAllester, Schapire. *On the Convergence Rate of Good-Turing Estimators.* COLT 2000. — [ACM](https://dl.acm.org/doi/10.5555/648299.755182)
- **[SOTA]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA 2007. — [HAL](https://hal.science/hal-00406166v2)

## 10. Worked Example

A table of $N=10{,}000$ sales rows grouped by `region`, sizes: A=9700, B=250, C=49, D=1. Uniform-sample at rate $p=n/N=0.01$ ($n=100$ rows).

**Missing-group probability** for each group $g$ is $(1-p)^{N_g}\approx e^{-pN_g}$:
- A: $e^{-97}\approx 0$ (always present)
- B: $e^{-2.5}\approx 0.082$
- C: $e^{-0.49}\approx 0.61$
- D: $e^{-0.01}\approx 0.99$ (almost surely missing)

Expected missing groups $=\sum_g e^{-pN_g}\approx 0+0.082+0.61+0.99\approx 1.68$. **Good–Turing**: if the sample contains $U$ groups seen exactly once, the unseen-group *mass* is estimated as $U/n$.

**Per-group CI width** scales as $1/\sqrt{n_g}$ with $n_g\approx pN_g$: group A gets $n_g\approx 97$ rows (tight), but C gets $\approx 0.5$ rows — no usable interval. **Congressional sampling** instead floors each group at $n_0$ rows: setting $n_0=30$ guarantees relative error $O(1/\sqrt{30})\approx 0.18$ even for C and D, at the cost of over-sampling tiny groups. This illustrates why no sample-only method bounds D's presence: with $N_D=1$, $\Omega(N/N_{\min})=\Omega(10^4)$ samples — the whole table — would be needed.

---
*Part of the [DBMS Research catalog](../../README.md).*
