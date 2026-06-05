# Benchmarking and Reproducible Evaluation

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/cleaning-benchmarking` · **Status:** empirically-open

## 1. Problem Statement

Data-cleaning research is plagued by non-comparable evaluations: synthetic errors that don't resemble real ones, cherry-picked datasets, leaking ground truth, and metrics (precision/recall/F1 on cell repairs) that do **not** predict whether cleaning helps a real downstream task. The problem: **build realistic, reproducible error benchmarks and metrics whose measured "cleaning quality" predicts real deployment quality** (downstream model accuracy, decision quality, cost).

Variants:
- **Generative:** Produce error processes $\mathcal{E}$ that are *statistically faithful* to real dirty data (realism objective).
- **Metric design:** Define an evaluation score that is *predictive* — monotone in true deployment value (validity objective).
- **Protocol:** Specify train/test, ground-truth handling, and leakage controls so results are *reproducible* and *rankable*.

It is meta-level: success is measured by how well the benchmark forecasts field performance, not by cleaning any one dataset.

## 2. Mathematical Foundations

- **Error process modeling:** an error model is a stochastic map $\mathcal{E}: D^\* \to D$ from clean to dirty; realism = small divergence $\mathrm{KL}(\mathcal{E}(\hat D) \,\|\, P_{\text{real-dirty}})$ or a two-sample test (MMD/Wasserstein) being non-rejecting.
- **Predictive validity:** let $m$ be a benchmark metric and $V$ true deployment value; validity = high rank correlation (Kendall $\tau$ / Spearman $\rho$) between $m$ and $V$ across systems; a metric is **proper** if no system can game $m$ without improving $V$ (analogue of proper scoring rules).
- **Detection/repair metrics:** precision/recall on cells; but the right loss is **task-weighted** — error cost $\sum_{c} w_c \,\mathbb{1}[\text{cell } c \text{ wrong}]$ with $w_c$ from downstream influence (cf. influence functions, Shapley data values).
- **Statistical-power / multiple-comparison theory:** to declare system A > B needs effect-size + variance control across datasets (Demšar-style nonparametric tests, Bonferroni/FDR).
- **No-free-lunch:** no single error model is best for all domains, bounding any universal benchmark's faithfulness.

## 3. State of the Art (SOTA)

- **BART** (Arocena, Glavic, Mecca, Miller, Papotti, Santoro, VLDB 2015) — principled error-generation engine that injects detectable errors w.r.t. constraints with controllable hardness; the closest thing to a faithful synthetic-error standard.
- **CleanML** (Li, Rekatsinas, Chu et al., ICDE 2021) — benchmark studying cleaning's *downstream ML impact* with leakage-controlled protocols; shows cleaning effects are inconsistent and metric-dependent.
- **Error-detection benchmarks** — the Abedjan et al. (VLDB 2016) "Detecting Data Errors: Where are we and what needs to be done?" study; Raha/REIN error-detection suites compiling many real dirty datasets.
- **Dedup/ER** — the Magellan benchmark datasets and DeepMatcher/EM tasks; Leipzig ER benchmark.
- **dirty-data corpora** — collections of real dirty datasets with curated ground truth (Tax, restaurants, hospital, flights, etc.) reused across papers.

## 4. Upper Bound

- BART can generate error sets with **guaranteed detectability/hardness** w.r.t. a constraint set in polynomial time per error class (controlled-injection upper bound).
- With $n$ datasets, distinguishing two systems' true mean performance to confidence $1-\delta$ needs $O(\sigma^2 \epsilon^{-2}\log\frac1\delta)$ samples (concentration) — a sample-complexity upper bound on reliable ranking.
- Validity of a metric is *estimable* in PTIME given paired $(m,V)$ measurements via rank-correlation.

## 5. Lower Bound

- **Statistical impossibility (NFL-flavored):** for any fixed synthetic error model there exists a real-world distribution it fails to match within $\epsilon$ — no universal faithful benchmark (two-sample lower bound).
- **Non-identifiability:** without held-out true deployment outcomes $V$, the predictive validity of a metric is **unfalsifiable** — you cannot certify a benchmark predicts deployment quality from cleaning metrics alone.
- **Sample-complexity lower bound:** distinguishing systems whose true gap is $\Delta$ requires $\Omega(\sigma^2/\Delta^2)$ datasets; with few public dirty datasets, many published "wins" are statistically underpowered.
- **Leakage hardness:** detecting all ground-truth leakage paths in a pipeline is undecidable in general (reduces to dataflow reachability over arbitrary code).

## 6. The Gap

**Empirically open** and arguably the meta-problem behind every other page. We have good *error injectors* (BART) and *downstream-aware studies* (CleanML), but **no benchmark proven to predict deployment quality**, no agreed proper metric beyond cell-F1, and too few real dirty datasets for statistically powered rankings. The gap is between "metrics we can compute" and "the quantity that matters (field value)," plus a reproducibility crisis from leakage and underpowered comparisons. Closing it needs (i) validated error-realism tests, (ii) task-grounded proper metrics, and (iii) large, governed dirty-data corpora with deployment outcomes.

## 7. Current Research (as of June 2026)

- Data-value / influence-weighted cleaning metrics (Shapley-data, Datamodels) to make scores task-predictive *(frontier — verify)*.
- LLM-generated realistic errors and LLM-as-judge for repair quality, with concern over circularity and bias *(frontier — verify)*.
- Leakage-audited, registry-style benchmarks and "data-centric AI" challenge suites; reproducibility checklists in DB/ML venues.
- End-to-end benchmarks pairing dirty data → cleaning → model → decision, reporting deployment-aligned metrics (Abedjan, Chu, Rekatsinas, Stoyanovich, Schelter groups) *(frontier — verify)*.

## 8. Future Work

- Statistically validated tests of error-model realism (calibrated two-sample tests on real corpora).
- Proper, task-grounded cleaning metrics with gaming-resistance guarantees.
- Large, governed, leakage-controlled dirty-data repositories with recorded deployment outcomes.
- Cross-page integration: benchmarks that also measure fairness impact, pipeline propagation, and KG-repair quality.

## 9. Key References

- **[Foundational]** Demšar. *Statistical Comparisons of Classifiers over Multiple Data Sets.* JMLR, 2006. — [JMLR](https://jmlr.org/papers/v7/demsar06a.html)
- **[SOTA]** Arocena, Glavic, Mecca, Miller, Papotti, Santoro. *Messing Up with BART: Error Generation for Evaluating Data-Cleaning Algorithms.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850578.2850579)
- **[SOTA]** Li, Rekatsinas, Chu, et al. *CleanML: A Study for Evaluating the Impact of Data Cleaning on ML Classification Tasks.* ICDE, 2021. — [DOI](https://doi.org/10.1109/ICDE51399.2021.00009)
- **[SOTA]** Abedjan, Chu, Deng, Fernandez, Ilyas, Ouzzani, Papotti, Stonebraker, Tang. *Detecting Data Errors: Where Are We and What Needs to Be Done?* VLDB, 2016. — [DOI](https://doi.org/10.14778/2994509.2994518)
- **[SOTA]** Ghorbani, Zou. *Data Shapley: Equitable Valuation of Data for Machine Learning.* ICML, 2019. — [arXiv](https://arxiv.org/abs/1904.02868)
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books / Morgan & Claypool, 2019. — [DOI](https://doi.org/10.1145/3310205)

## 10. Worked Example

Two cleaning systems A and B are compared on $n = 9$ dirty datasets. Cell-repair F1 favors A on every dataset (mean $0.82$ vs $0.79$), yet what matters is downstream model accuracy $V$. Suppose paired downstream accuracies give B a win on 7 of 9 datasets.

Apply the Wilcoxon signed-rank test (Demšar's recommendation) on the per-dataset accuracy differences $V_B - V_A$. With 7 positive and 2 negative ranks, the test rejects "A $\ge$ B" at $\alpha = 0.05$ — so cell-F1 **mis-ranks** the systems relative to deployment value.

Now the predictive-validity check: Kendall's $\tau$ between metric $m$ (cell-F1) and value $V$ across systems is **negative** here, exposing $m$ as non-proper. To reliably detect a true accuracy gap of $\Delta = 0.02$ with per-dataset SD $\sigma = 0.03$, the sample-complexity bound $\Omega(\sigma^2/\Delta^2) = \Omega(0.0009/0.0004) \approx 2.3$ understates it; in practice $n \gtrsim 30$ datasets are needed for $1-\delta = 0.95$ power — far more than the 9 available, so any single published "win" is statistically underpowered.

---
*Part of the [DBMS Research catalog](../../README.md).*
