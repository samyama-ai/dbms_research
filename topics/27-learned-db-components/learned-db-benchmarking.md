# Benchmarks and Reproducibility for Learned DB

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-db-benchmarking` · **Status:** empirically-open
> **Verification note:** The "Design Space Exploration and a Comparative Evaluation" survey (Ref 6) is authored by Sun, Zhang, Sun, Li, Tang (PVLDB 2022), not Kipf/Kemper; corrected in Section 9.

## 1. Problem Statement

Claims that a learned component "beats" a classical one are only meaningful relative to a *strong* baseline, a *representative* workload, a *fair* metric, and a *reproducible* protocol. The benchmarking problem for learned DB components asks for all four, jointly:

1. **Workloads** that exhibit the data/query regularities learning is supposed to exploit *and* the irregularities/drift it must survive — not just JOB/TPC-H/TPC-DS run once.
2. **Metrics** that capture end-to-end value: not only model accuracy (q-error) but realized query latency, *and* training/data-collection cost, retraining cost, memory, and tail behavior.
3. **Baselines** that are genuinely strong (a well-tuned classical optimizer/index, not a strawman).
4. **Protocols** controlling for hardware, warm vs. cold cache, train/test split leakage, and out-of-distribution evaluation.

This is empirically-open: there is broad recognition that early results were inflated by weak baselines, in-distribution test sets, and excluded training costs.

## 2. Mathematical Foundations

The core methodological hazard is **train/test distribution mismatch and leakage**. Generalization is governed by classical learning theory: with hypothesis class of VC dimension $d$ and $m$ i.i.d. samples, with probability $1-\delta$,

$$
\mathrm{err}_{\text{true}} \le \mathrm{err}_{\text{train}} + O\!\left(\sqrt{\tfrac{d \ln(m/d) + \ln(1/\delta)}{m}}\right).
$$

But DB workloads are **not i.i.d.** — they drift and contain repeated templates, so in-distribution test error systematically *underestimates* deployment error; the proper measure is risk under a shifted distribution $\mathcal{D}_{\text{test}} \neq \mathcal{D}_{\text{train}}$, bounded by terms in a divergence $d(\mathcal{D}_{\text{train}}, \mathcal{D}_{\text{test}})$ (domain-adaptation bounds, Ben-David et al. 2010). For cardinality estimators the standard accuracy metric is **q-error** $\max(\hat c/c,\, c/\hat c)$; a key foundational point is that q-error is only *loosely* coupled to plan quality — small q-error can still cause large plan regressions and vice versa, so accuracy and end-to-end latency must both be reported.

## 3. State of the Art (SOTA)

- **Workload-SOTA:** **JOB** (Join Order Benchmark; Leis et al., PVLDB 2015) became the de-facto cardinality/optimizer benchmark because it has correlated real-world (IMDb) data and hard joins; **TPC-H/TPC-DS** for breadth; **Stats-CEB / CEB** (Negi et al.) for cardinality estimation; **redbench** and out-of-distribution workload generators for drift evaluation *(frontier — verify)*.
- **Methodology-SOTA:** the "**Are We Ready for Learned Cardinality Estimation?**" study (Wang et al., PVLDB 2021) and the **"How Good Are Query Optimizers, Really?"** study (Leis et al., 2015) are the canonical fair-comparison protocols, showing many learned wins shrink or vanish under strong baselines and out-of-distribution tests.

## 4. Upper Bound

The achievable "fairness" upper bound today is a **multi-axis report**: q-error distribution (median + tail), end-to-end latency vs. a tuned PostgreSQL/commercial baseline, training + data-collection time, model size, and explicit in-distribution *and* out-of-distribution splits — as instantiated by the Wang et al. (2021) and Negi et al. CEB protocols. No protocol yet certifies "this comparison is unbiased," so the upper bound is best-practice, not a guarantee.

## 5. Lower Bound

There is an **impossibility-flavored** lower bound: no finite benchmark can certify worst-case behavior of a learned component, because the adversary can always craft an out-of-distribution workload on which a fixed model fails (no-free-lunch / generalization floor). Formally, for any model trained on $m$ samples there exists a distribution shift of bounded divergence on which expected error is arbitrarily bad unless capacity is restricted — so benchmark scores are *necessary but never sufficient* evidence. Reproducibility itself is bounded by nondeterminism (GPU floating-point, thread scheduling, cache state), preventing bit-exact replication.

## 6. The Gap

The gap is between *current practice* (single-workload, in-distribution, training-cost-excluded comparisons) and *adequate practice* (multi-workload, drift-stressed, full-TCO, strong-baseline). It is genuinely open which workload features predict learned-vs-classical wins, and there is no community-standard leaderboard with frozen baselines and out-of-distribution holdouts. Closing it requires: (a) curated drift-bearing workloads, (b) a TCO-inclusive metric standard, (c) shared, versioned baseline implementations, (d) registered protocols to prevent cherry-picking.

## 7. Current Research (as of June 2026)

Directions: out-of-distribution and *workload-drift* benchmarks (redbench-style); standardized end-to-end harnesses that bundle training cost; reproducibility artifacts and SIGMOD/VLDB availability badges; foundation-model cardinality estimation raising new "did it see this schema in pretraining?" leakage concerns *(frontier — verify)*. Groups: Kemper/Neumann (TUM), Kraska/Marcus (MIT), the CEB/Stats-CEB authors (Negi et al.), and the PVLDB experiments-and-analysis track community pushing fair-comparison studies.

## 8. Future Work

- A community leaderboard with frozen strong baselines and held-out drifting workloads.
- A standardized TCO metric (accuracy, latency, training cost, memory, tail) with confidence intervals.
- Workload generators parameterized by measurable "learnability" (correlation, template repetition, drift rate).
- Leakage audits for pretrained/foundation estimators.

## 9. Key References

- **[Foundational]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really? (Join Order Benchmark).* PVLDB 2015. — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[SOTA]** Wang, Qu, Li, et al. *Are We Ready for Learned Cardinality Estimation?* PVLDB 2021. — [arXiv](https://arxiv.org/abs/2012.06743)
- **[SOTA]** Negi, Marcus, Kipf, et al. *Flow-Loss / CEB: Cardinality Estimation Benchmark.* PVLDB 2021. — [arXiv](https://arxiv.org/abs/2101.04964)
- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[Foundational]** Vapnik, Chervonenkis. *On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities.* 1971. — [DOI](https://doi.org/10.1137/1116025)
- **[Survey]** Sun, Zhang, Sun, Li, Tang. *Learned Cardinality Estimation: A Design Space Exploration and a Comparative Evaluation.* PVLDB 2022 (experiments & analysis). — [DOI](https://doi.org/10.14778/3485450.3485459)

## 10. Worked Example

Consider reporting a learned estimator $M$ against PostgreSQL on a JOB-style workload. Two evaluation protocols give opposite verdicts.

**In-distribution (the inflated result).** Train on 90 query templates, test on a held-out 10% *of the same templates*. Median q-error: $M=1.8$ vs PostgreSQL $9.0$. End-to-end runtime: $M$ wins by 30%. Headline: "learned beats classical."

**Drift-stressed (the fair result).** Hold out *entire join shapes* never seen in training. Now the q-error distribution develops a heavy tail: median still $2.1$, but the **99th percentile** jumps to $4\times10^4$ while PostgreSQL stays at $\sim200$. One tail mis-estimate picks a nested-loop plan that runs $50\times$ slower, erasing the average win.

**Why the metric matters.** q-error and plan quality are only loosely coupled (Section 2): a median q-error of $2$ looks great, yet a single cell where $\hat c=10$ but $c=4\times10^5$ ($q\text{-error}=4\times10^4$) is enough to flip the optimal plan. And the training cost — say $6$ GPU-hours to collect $10^5$ labeled runtimes — is often excluded entirely. A TCO-honest report must show median *and* tail q-error, in- *and* out-of-distribution latency, plus training cost, against a *tuned* PostgreSQL baseline.

---
*Part of the [DBMS Research catalog](../../README.md).*
