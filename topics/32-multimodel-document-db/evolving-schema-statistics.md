---
id: 32-multimodel-document-db/evolving-schema-statistics
title: "Statistics maintenance for evolving schemas"
topic: 32-multimodel-document-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Statistics maintenance for evolving schemas

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/evolving-schema-statistics` · **Status:** empirically-open

## 1. Problem Statement
Document stores have an **implicit, latent schema**: fields appear, disappear, change type, and shift distribution over time. The optimizer still needs accurate **statistics** — per-path presence/null rates, value histograms, distinct-value counts (NDV), and multi-path correlations — to estimate selectivities and cardinalities. The problem: **incrementally maintain accurate statistics under schema and distribution drift**, with bounded space and update cost, without full rescans.

- **Maintenance variant:** given a stream of inserts/updates/deletes, keep a sketch $S_t$ so that selectivity estimates stay within error $\varepsilon$.
- **Detection variant:** decide when drift has invalidated current stats enough to warrant recomputation (change-point detection).
- **Counting variants:** NDV/heavy-hitters/quantiles per path, and joint distinct counts across optional paths.

## 2. Mathematical Foundations
Each path is a stream; maintaining stats is **streaming/sketching**. Distinct counts use **HyperLogLog** ($O(\varepsilon^{-2})$ registers for relative error, mergeable); frequencies use **Count-Min** ($\varepsilon,\delta$ guarantees, space $O(\tfrac1\varepsilon\log\tfrac1\delta)$); quantiles use **GK / t-digest / KLL** ($\epsilon$-approximate, $O(\tfrac1\epsilon\log\ldots)$). Drift detection is **change-point / two-sample testing**: distinguishing distributions at distance $\delta$ needs $\Omega(\delta^{-2})$ samples (Le Cam). Multi-path correlation estimation invokes the information-theoretic limits of **sketch size vs. error** and the curse of conjunctive selectivity (independence assumption error). Sliding-window sketches (Datar–Gionis–Indyk–Motwani exponential histograms) handle recency under drift with $O(\tfrac1\varepsilon\log^2 N)$ space.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** HLL (Flajolet et al., 2007), Count-Min (Cormode–Muthukrishnan, 2005), KLL quantiles (Karnin–Lang–Liberty, FOCS 2016), DGIM sliding windows (2002). These are mergeable and incremental — directly applicable per path.
- **Systems-SOTA:** Apache **DataSketches** (used in Druid, Pinot, BigQuery `APPROX_*`); MongoDB's sampling-based plan stats; Snowflake/BigQuery column-level approximate stats over `VARIANT`/`JSON`; **learned cardinality estimators** (MSCN — Kipf et al.; NeuroCard; Naru/UAE — deep autoregressive). Self-driving DBMS stat-refresh policies (CMU NoisePage). Most document engines still under-maintain *per-path correlated* stats.

## 4. Upper Bound
Per-path: mergeable sketches give *one-pass, incremental* maintenance with provable $(\varepsilon,\delta)$ accuracy and $O(\mathrm{polylog})$ space; merges across partitions are exact-in-distribution, so distributed maintenance is cheap. Sliding-window NDV/quantiles achieve relative error $\varepsilon$ in $\mathrm{polylog}(N)$ space (DGIM-style). Change-point detection achieves detection delay $O(\log(1/\alpha)/\mathrm{KL})$ via CUSUM under known pre/post distributions. These hold in the **streaming model** with single-path assumptions.

## 5. Lower Bound
- Exact distinct count requires $\Omega(n)$ space; even constant-factor approximation needs $\Omega(\varepsilon^{-2})$ (Indyk–Woodruff; Alon–Matias–Szegedy for frequency moments).
- Joint/correlated selectivity over $k$ paths: estimating multi-way distinct counts has communication-complexity lower bounds exponential in the worst case; independence assumptions provably mis-estimate (multiplicative error unbounded).
- Drift cannot be detected faster than $\Omega(\delta^{-2})$ samples (info-theoretic), so there is an irreducible staleness window.

## 6. The Gap
Single-path streaming is essentially **closed** (matching upper/lower bounds). The empirical openness is everything *between* paths and *over time*: (1) **correlations** across optional/repeated fields, where worst-case is hard and practical sketches lack guarantees; (2) **when to refresh** — no policy provably balances staleness-induced plan regret against recompute cost; (3) **schema-drift-aware error** — current estimators silently degrade when a field's type/semantics changes. No system combines mergeable per-path sketches with a proven drift-triggered refresh policy and correlation-aware joint estimation. This is why the status is empirically-open.

## 7. Current Research (as of June 2026)
Learned and hybrid estimators (autoregressive density models, query-driven feedback like DB2 LEO / self-correcting histograms) are being adapted to JSON paths; uncertainty-aware estimators that detect their own staleness are an active thread. *(frontier — verify: claims that production warehouses now maintain drift-triggered correlated VARIANT statistics rather than periodic recompute.)* Groups: CMU (Pavlo), TUM (Neumann/Leis), MIT (learned estimation), and the DataSketches community.

## 8. Future Work
- Correlation-aware mergeable sketches with guarantees over optional paths.
- Plan-regret-optimal refresh scheduling (ties to *adaptive-shredding*).
- Drift-robust learned estimators that self-flag distribution shift.
- Benchmarks with realistic field-level drift.

## 9. Key References
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm.* AofA, 2007. — [DOI](https://doi.org/10.46298/dmtcs.3545)
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** N. Alon, Y. Matias, M. Szegedy. *The Space Complexity of Approximating the Frequency Moments.* JCSS, 1999. — [DOI](https://doi.org/10.1006/jcss.1997.1545)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** A. Kipf et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations & Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Consider a collection where each document may carry a `shipping.zip` path. We keep one **HyperLogLog** sketch to estimate NDV (distinct zips) and one **Count-Min** sketch for heavy-hitter zips. HLL standard error is $\sigma \approx 1.04/\sqrt{m}$; to hit $2\%$ relative error we need $m \ge (1.04/0.02)^2 \approx 2704$ registers — round up to $m = 2^{12} = 4096$ (about 4 KB at 1 byte/register), giving $\sigma \approx 1.04/64 \approx 1.6\%$.

Now drift hits: a new ingestion source emits `shipping.zip` as a 9-digit *integer* instead of a 5-char *string*. Under per-path-per-type tracking these hash into a *fresh* HLL, so the old sketch reports NDV stably while the new path's count grows. A two-sample drift test on the type-tag stream flags the shift after $\Omega(\delta^{-2})$ samples; for a type-mix change of distance $\delta = 0.1$ that is on the order of $10^2$ documents before the change-point is reliably detectable. The optimizer then knows to treat `shipping.zip` as a union of two typed sub-paths rather than silently averaging an NDV estimate across incompatible value spaces.

---
*Part of the [DBMS Research catalog](../../README.md).*
