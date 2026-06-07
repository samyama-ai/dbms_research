---
id: 33-benchmarking-testing/reproducible-performance-benchmarking
title: "Reproducible Performance Benchmarking"
topic: 33-benchmarking-testing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Reproducible Performance Benchmarking

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/reproducible-performance-benchmarking` · **Status:** empirically-open

## 1. Problem Statement

Given two systems (or two versions / configurations) $A$ and $B$ and a workload $W$, produce a **statistically sound, reproducible** comparison of throughput and latency such that:
- the reported difference is **real** (not measurement noise), with quantified uncertainty;
- a different lab, re-running the same artifact, reaches the **same conclusion** within stated confidence.

The obstacles: micro-architectural and OS noise (frequency scaling, NUMA, cache/TLB state, interrupts, co-tenancy in the cloud), **warmup / JIT / buffer-pool** transients, sensitivity to dozens of **configuration knobs**, and the temptation to report a single peak number.

Variants:
- **Estimation:** estimate the steady-state throughput distribution $\Theta_A$ and tail-latency quantiles ($p99$, $p99.9$) with confidence intervals.
- **Decision / comparison:** test $H_0: \Theta_A = \Theta_B$ vs. the alternative, controlling Type-I error despite repeated measurements and multiple configs.
- **Reproducibility:** bound the variance attributable to environment so an independent rerun lands in the same interval.

Marked **empirically-open**: the statistics are known; reliably *applying* them to DBMS measurement under noise and config sensitivity remains unsolved in practice.

## 2. Mathematical Foundations

Treat each run as drawing latencies $X_1,\dots,X_n$ from an unknown, **heavy-tailed, autocorrelated** steady-state distribution $F$ (after a warmup transient). Two core statistical problems:

**Steady-state detection.** The throughput time series is non-stationary during warmup. Methods: **Marriott–Welch / MSER-5** truncation heuristics; CUSUM change-point detection to find the start of steady state.

**Interval estimation under autocorrelation.** I.i.d. CIs are invalid because consecutive measurements correlate. The classical fix is **batch means**: partition the run into $b$ batches, average each, treat batch means as approximately i.i.d., and form
$$\bar X \pm t_{b-1,1-\alpha/2}\,\frac{s_{\text{batch}}}{\sqrt{b}}.$$
For tail quantiles, use order statistics / the **bootstrap**; for ratios of throughputs, propagate variance or bootstrap the ratio.

**Multiple comparisons.** Sweeping configs inflates false positives; correct with Bonferroni/Benjamini–Hochberg. **Effect size** (e.g., ratio with CI), not just $p$-value, is what should be reported.

> **Key principle (Hooke / Georges-Buytaert-Eeckhout).** Report a *distribution with a confidence interval*, never a single number; use **geometric mean** for ratios across heterogeneous workloads, and ensure the comparison is **rigorous** (state $n$, warmup, hardware, and CI).

Reproducibility is formalized via **variance decomposition**: total variance = within-run + between-run + between-environment; reproducibility requires the between-environment term be characterized and controlled.

## 3. State of the Art (SOTA)

**Methodology-SOTA.**
- **Georges, Buytaert, Eeckhout** (OOPSLA 2007) — *Statistically Rigorous Java Performance Evaluation*; canonical recipe for warmup handling and CIs, widely adopted in systems benchmarking.
- **Kalibera & Jones** (2013) — rigorous methodology with quantified repetition levels and steady-state detection; standard reference for "how many times to repeat."
- **Hooke's** "How NOT to lie with benchmarks" lineage and **SIGMOD/VLDB Reproducibility** (artifact evaluation, ACM badges) institutionalize sharing artifacts + scripts.

**Systems-SOTA.**
- Standard DBMS benchmarks: **TPC-C / TPC-H / TPC-DS**, **YCSB** (Cooper et al., SoCC 2010) for KV stores, **OLTP-Bench / BenchBase** (Difallah et al., VLDB 2014; CMU) — a unified, configurable harness emphasizing rate control and repeatability.
- Cloud-noise mitigation: **dedicated/bare-metal instances**, CPU pinning, `cset`/`isolcpus`, disabling turbo, and statistical co-tenant detection.

## 4. Upper Bound

- **Estimation cost:** batch-means / bootstrap CIs need $O(n)$ samples plus enough batches ($b \ge \sim 20$–30) for the $t$-approximation; variance shrinks as $1/\sqrt{n}$ — diminishing returns set a practical ceiling on precision per unit run time.
- **Repetitions** to reach a target CI width scale as $\propto \sigma^2/\epsilon^2$ (Kalibera–Jones give explicit two-level repetition formulas).
- Best achievable reproducibility is bounded by the *irreducible* between-environment variance; on controlled bare-metal it is small, on shared cloud it can dominate.

## 5. Lower Bound

- **Information-theoretic / statistical:** distinguishing two distributions whose means differ by $\delta$ with confidence $1-\alpha$ requires $\Omega(\sigma^2/\delta^2)$ effective (de-correlated) samples — heavy tails inflate $\sigma^2$, raising the floor for tail-latency claims.
- **Irreducible environment variance:** in multi-tenant clouds, co-tenancy noise is not controllable by the experimenter, so reproducibility across environments has a hard variance floor — an empirical impossibility absent dedicated hardware.
- **No free lunch in warmup detection:** steady-state detection from a finite prefix is a change-point problem with unavoidable detection-delay vs. false-alarm tradeoffs (statistical lower bounds on sequential change detection).

## 6. The Gap

The statistical machinery is **mature** (CIs, batch means, bootstrap, Kalibera–Jones), so the gap is not mathematical — it is in *adoption, standardization, and the cloud-noise floor*. Many published DBMS results still report single numbers without CIs, undisclosed warmup, or cherry-picked configs; cross-paper comparison is unreliable. Closing it requires: (1) community-mandated reporting (CIs, full config, hardware, artifact); (2) validated cloud-noise normalization; (3) automated config-fairness so each system is measured near its own optimum, not the author's favored one.

## 7. Current Research (as of June 2026)

- **Automated configuration tuning** (e.g., OtterTune-lineage, ML/Bayesian-opt knob tuners) used to ensure *each* system is benchmarked near its optimum, removing config-unfairness as a confound *(frontier — verify)*.
- Cloud-noise modeling and "performance clamps" (cgroups v2, bare-metal cloud) for reproducibility; co-tenant interference detection.
- Reproducibility infrastructure: containerized artifacts, `Reprozip`/Nix-pinned environments, SIGMOD/VLDB/SOSP artifact-evaluation expansion.
- Continuous performance regression testing with change-point detection on CI time series (used in CockroachDB, ClickHouse, etc.).

## 8. Future Work

- A standard, machine-checkable benchmarking report schema (n, warmup policy, CIs, config, hardware) enforced at submission.
- Validated statistical correction for cloud co-tenancy noise.
- Fair multi-config protocols (tune both systems with equal budget) to neutralize over-tuning.
- Power/energy and tail-latency as first-class, statistically reported metrics.

## 9. Key References

- **[Foundational]** A. Georges, D. Buytaert, L. Eeckhout. *Statistically Rigorous Java Performance Evaluation.* OOPSLA, 2007. — [DOI](https://doi.org/10.1145/1297027.1297033)
- **[Foundational]** T. Kalibera, R. Jones. *Rigorous Benchmarking in Reasonable Time.* ISMM, 2013. — [DOI](https://doi.org/10.1145/2464157.2464160)
- **[SOTA]** B. F. Cooper, A. Silberstein, E. Tam, R. Ramakrishnan, R. Sears. *Benchmarking Cloud Serving Systems with YCSB.* SoCC, 2010. — [DOI](https://doi.org/10.1145/1807128.1807152)
- **[SOTA]** D. E. Difallah, A. Pavlo, C. Curino, P. Cudré-Mauroux. *OLTP-Bench: An Extensible Testbed for Benchmarking Relational Databases.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732240.2732246)
- **[Foundational]** J. Gray (ed.). *The Benchmark Handbook for Database and Transaction Systems.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/collections/gray93.html)
- **[Survey]** Transaction Processing Performance Council. *TPC-C / TPC-H / TPC-DS Specifications.* tpc.org. — [TPC](https://www.tpc.org/information/benchmarks5.asp)

## 10. Worked Example

We compare DB versions $A$ and $B$ on TPC-C throughput. Each run yields $n = 10{,}000$ correlated tps samples (post-warmup). I.i.d. CIs are invalid, so use **batch means** with $b = 25$ batches of $400$ samples each.

System $A$: batch means have $\bar X_A = 5000$ tps, batch std $s_A = 120$. The 95% CI is
$$\bar X_A \pm t_{24,0.975}\,\frac{s_A}{\sqrt b} = 5000 \pm 2.064 \cdot \frac{120}{\sqrt{25}} = 5000 \pm 49.5 = [4950.5,\ 5049.5].$$
System $B$: $\bar X_B = 5080$, $s_B = 130$ ⇒ CI $= 5080 \pm 53.6 = [5026.4,\ 5133.6]$.

The intervals **overlap** ($[5026.4, 5049.5]$ in common), so $H_0:\Theta_A = \Theta_B$ is *not* rejected at 95% — the apparent $80$-tps edge for $B$ is within noise. To resolve a true $\delta = 80$ tps gap with $\sigma \approx 125$, the sample-size floor is $n \gtrsim (z_{0.975}\,\sigma/\delta)^2 \cdot 2 \approx (1.96\cdot 125/80)^2 \cdot 2 \approx 19$ *independent* batches per side — feasible, but reporting either single peak number ($5000$ vs $5080$) as "B wins" would be the classic benchmarking lie this problem targets.

---
*Part of the [DBMS Research catalog](../../README.md).*
