---
id: 13-column-stores-olap/learned-data-skipping
title: "Learned Data Skipping Indexes"
topic: 13-column-stores-olap
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Learned Data Skipping Indexes

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/learned-data-skipping` · **Status:** empirically-open

## 1. Problem Statement

Classical data skipping (zone maps, Bloom filters) uses fixed summaries that are oblivious to the data distribution and the query workload. A **learned data-skipping index** replaces or augments these with a model — trained on data and/or query history — that maps a block (or a multi-dimensional region) to a *predicted* answer to "could a row satisfying predicate $P$ live here?", with the guarantee that *false negatives are impossible* (no qualifying block is skipped) and *false positives* (unnecessarily scanned blocks) are bounded.

Variants:

- **Decision / membership variant (per-block):** learn, per block, a compact filter such that $\Pr[\text{scan} \mid \text{no match}]$ — the **false-positive scan amplification** — is provably bounded, for point and range predicates, possibly multi-dimensional.
- **Optimization variant (global):** jointly choose a data layout *and* the learned summaries to minimize expected bytes scanned over a workload distribution, under a space budget for the index.
- **Counting variant:** estimate the number of surviving blocks for the optimizer's cost model with calibrated error.

The status is *empirically open*: strong empirical results exist, but no broadly accepted structure provides **worst-case bounded false-positive scan amplification** across adversarial workloads and data drift while remaining update-friendly.

## 2. Mathematical Foundations

Let blocks be regions $R_1,\dots,R_m \subseteq \mathbb{R}^d$ (after some layout). A skipping index is a family of predicates $h_j : \text{Query} \to \{\text{scan}, \text{skip}\}$ that is **sound**: $h_j(q)=\text{skip} \Rightarrow R_j \cap q = \emptyset$. Define the **false-positive rate** $\mathrm{FPR}_j(q) = \Pr[h_j(q)=\text{scan} \mid R_j\cap q=\emptyset]$; the objective is to minimize $\mathbb{E}_{q\sim\mathcal{W}} \sum_j \mathrm{FPR}_j(q)$.

Foundations:

- **Learned Bloom filters** (Kraska et al., SIGMOD 2018; Mitzenmacher's analysis, NeurIPS 2018): a model $f$ plus a backup filter achieves expected FPR below classic Bloom for *learnable* key distributions, with the sandwiching theorem giving a space–FPR trade-off. Soundness (no false negatives) requires the backup filter; the model alone is not sound.
- **Information theory:** a filter for a set $S$ of $|S|=k$ keys from universe $U$ needs $\ge k\log_2(1/\epsilon)$ bits for FPR $\epsilon$ (Bloom optimality, Carter–Wegman). Learning helps only when $S$ has *structure* (low Kolmogorov complexity / smooth CDF).
- **Range and multi-D:** learned CDF models (RMI, PGM-index) bound prediction error $\le \varepsilon$, turning range pruning into interval lookups; multi-dimensional learning ties to **VC dimension** of the region class and to space-filling-curve dilation.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Mitzenmacher's *sandwiched learned Bloom filters* (NeurIPS 2018) give the cleanest space/FPR analysis; **Adaptive/partitioned learned Bloom filters** (Vaidya, Knorr, Mitzenmacher, Kraska — ICLR 2021) tighten FPR by score-bucketed thresholds.
- **Systems-SOTA:** **PGM-index** (Ferragina & Vinciguerra, VLDB 2020) for sorted/range; **Tsunami** (Ding et al., VLDB 2020) and **Flood** (Nathan et al., SIGMOD 2020) for learned multi-dimensional in-memory layouts/grids; **Qd-tree** (Yang et al., SIGMOD 2020) for block layout via RL; **LISA** (Li et al., SIGMOD 2020) for learned spatial indexing on disk. ClickHouse/Parquet remain on classic Bloom + min/max in production.

## 4. Upper Bound

Sandwiched learned Bloom filters achieve expected FPR $\epsilon$ using $\le k\log_2(1/\epsilon) + |f|$ bits, where $|f|$ is the model size — beating classic Bloom when the model's *recall-at-budget* exceeds the entropy it costs. PGM-index gives $O(1)$ expected / $O(\log\log n)$ query with $\varepsilon$-bounded error and space provably $\le$ a tuned B-tree, *worst-case optimal* among $\varepsilon$-piecewise-linear models. Flood/Tsunami report multiplicative scan reductions (often $1$–$3$ orders of magnitude) empirically but **without** distribution-free worst-case scan-amplification guarantees.

## 5. Lower Bound

Any sound membership filter inherits the **Bloom information lower bound** $\ge k\log_2(1/\epsilon)$ bits, so learning cannot beat it for *incompressible* key sets (cell-probe / counting argument). For multi-dimensional range skipping, the single-layout survival lower bound $\Omega(m^{1-1/d})$ (space-filling-curve dilation) still applies regardless of how the summaries are learned. **Adversarial / adaptive** queries can drive a learned filter's FPR to its backup-filter fallback, so any worst-case guarantee degenerates to the classic structure's bound — the learning advantage is *distributional, not worst-case*. No NP-hardness is needed: the obstruction is information-theoretic and adversarial.

## 6. The Gap

The gap is **wide and open**. Empirically, learned skipping wins big on real, skewed, low-entropy data; theoretically, no structure offers *simultaneously* (i) soundness, (ii) distribution-free bounded false-positive scan amplification, (iii) sub-linear update cost under drift. Closing it likely requires either accepting distributional assumptions with verified-at-runtime fallback, or new lower bounds proving the trade-off is fundamental.

## 7. Current Research (as of June 2026)

- Robustness to **data/query drift**: online retraining and drift detection for learned layouts; incremental Flood/Tsunami successors *(frontier — verify)*.
- **Workload-aware multi-dimensional skipping** combining Qd-tree layouts with learned per-block filters under a unified byte-scanned objective *(frontier — verify)*.
- Theoretical work on *adversarially robust* learned Bloom variants and on calibrated survival-count estimation for the optimizer.

## 8. Future Work

- Distribution-free or smoothed-analysis bounds on false-positive scan amplification.
- Update-efficient learned skipping (LSM-friendly) with bounded rebuild amortization.
- Joint optimization of layout + encoding + skipping under one I/O cost model.

## 9. Key References

- **[Foundational]** T. Kraska, A. Beutel, E. H. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[Foundational]** M. Mitzenmacher. *A Model for Learned Bloom Filters and Optimizing by Sandwiching.* NeurIPS, 2018. — [NeurIPS](https://proceedings.neurips.cc/paper/2018/hash/0f49c89d1e7298bb9930789c8ed59d48-Abstract.html)
- **[SOTA]** V. Nathan, J. Ding, M. Alizadeh, T. Kraska. *Learning Multi-dimensional Indexes (Flood).* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380579)
- **[SOTA]** J. Ding et al. *Tsunami: A Learned Multi-dimensional Index for Correlated Data and Skewed Workloads.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3425879.3425880)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-index.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)

## 10. Worked Example

A column is stored in $m=4$ blocks of $250$ rows each, holding sorted-ish `timestamp` values. A query asks `WHERE ts BETWEEN 1700 AND 1750`.

**Classic zone map** stores per-block $[\min,\max]$:

| Block | min | max | overlaps [1700,1750]? |
|------|------|------|------|
| $B_1$ | 1000 | 1490 | no — skip |
| $B_2$ | 1480 | 1720 | yes — scan |
| $B_3$ | 1710 | 1995 | yes — scan |
| $B_4$ | 1990 | 2400 | no — skip |

Soundness holds: a block is skipped only if $[\min,\max]\cap[1700,1750]=\emptyset$, so no qualifying row is missed. Here $2$ of $4$ blocks scan; if the matching rows actually all sit in $B_2$, then $B_3$ is a **false positive** — scanned for nothing. Its $\mathrm{FPR}$ contribution is $1$.

A **learned** summary fits the block CDF and predicts where $1750$ lands within $B_3$, possibly pruning it — but only the backup zone map keeps soundness. The information floor still bites: a sound filter on $k$ keys with target FPR $\epsilon$ needs $\ge k\log_2(1/\epsilon)$ bits, so learning helps only when the data has structure (a smooth CDF), not on incompressible keys.

---
*Part of the [DBMS Research catalog](../../README.md).*
