# Fairness-Aware Data Cleaning

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/fairness-aware-cleaning` · **Status:** empirically-open

## 1. Problem Statement

Cleaning operations — imputation, deduplication, outlier removal, repair — are not group-neutral. Missing-data imputation can encode majority patterns onto minorities; outlier removal can delete legitimate minority records; ER can under-merge sparse groups. The problem: **clean data so that it does not introduce or amplify bias against protected groups** $A$ (e.g., race, sex), while still improving quality and (ideally) provably preserving or improving downstream model fairness.

Variants:
- **Decision:** Does a proposed repair $D'$ satisfy a fairness criterion $\Phi$ (e.g., demographic-parity gap $\le \tau$) on a target query/model?
- **Constrained optimization:** Among quality-improving repairs, find one minimizing a fairness-violation measure (or Pareto-optimal in quality vs. fairness).
- **Counting/auditing:** Over the space of cleanings, what is the range of achievable fairness — i.e., is unfairness an artifact of the cleaning choice?

Crucially, fairness is a property of the *downstream use*, so cleaning must be evaluated end-to-end, not in isolation.

## 2. Mathematical Foundations

- **Group-fairness metrics:** demographic parity $\Pr(\hat Y=1\mid A=a)$ equal across $a$; equalized odds (Hardt–Price–Srebro); calibration. These can conflict — the **Kleinberg–Mullainathan–Raghavan / Chouldechova impossibility**: calibration, balance for the positive and negative class cannot all hold simultaneously unless base rates are equal or prediction is perfect.
- **Counterfactual / causal fairness:** Kusner et al. — a decision is fair if invariant under counterfactual change of $A$; cleaning that breaks causal paths can help or hurt.
- **Missing-data theory:** MCAR/MAR/MNAR (Rubin). Imputation correctness and its *differential* effect across groups hinge on whether missingness is MAR *within* groups; MNAR breaks identifiability.
- **Distribution shift:** cleaning changes the empirical distribution $P_n \to P_n'$; fairness impact bounded by group-conditional total-variation / Wasserstein shift $\sum_a \pi_a\, W(P_a, P'_a)$.
- **Multi-objective optimization:** quality vs. fairness as a Pareto frontier; scalarization or constrained repair.

## 3. State of the Art (SOTA)

Young field; empirically driven.
- **Audits of cleaning's fairness impact** — Guha, Khan, Stoyanovich et al. and the "data cleaning and fairness" line show different imputation/cleaning methods change downstream group accuracy/parity, sometimes adversely; no method dominates.
- **Fair imputation** — group-aware and fair-MICE variants, fairness-regularized imputation; results are dataset-dependent.
- **Fairness-aware ER** — work showing entity matching has disparate error rates across groups (e.g., names, dialects) and proposing balanced thresholds.
- **Responsible-data tooling** — mlinspect / Fairlearn / Aequitas measure but do not *optimize* cleaning for fairness; Ranking/“nutritional labels” (Stoyanovich) for transparency.
- **CPClean-style robustness** — checking whether cleaning choices can flip a *fairness* verdict *(frontier — verify)*.

## 4. Upper Bound

- For a fixed model class and a finite candidate-repair set, *checking* whether some repair meets a fairness threshold is decidable by enumeration; with $k$ dirty cells and convex surrogates, fairness-constrained imputation is solvable in **PTIME** via convex programming.
- Fair post-processing of a *given* classifier (Hardt et al.) achieves the optimal fairness–accuracy tradeoff via a **linear program** — an upper bound when cleaning is framed as label/threshold adjustment.
- Reweighing / massaging (Kamiran–Calders) gives PTIME pre-processing repairs with provable parity on the training distribution.

## 5. Lower Bound

- **Impossibility (information-theoretic):** Kleinberg–Mullainathan–Raghavan & Chouldechova — no cleaning can make all standard fairness metrics simultaneously hold when group base rates differ; this is a hard tradeoff barrier, not an algorithmic gap.
- **MNAR non-identifiability:** under not-missing-at-random missingness, the true group distribution is statistically **unidentifiable**; no imputation can be guaranteed fair without untestable assumptions.
- **NP-hardness:** jointly optimal repair under both a minimal-change (consistency) constraint and a fairness constraint is **NP-hard** (combines repair NP-hardness with fairness combinatorics; reductions from constrained subset selection).

## 6. The Gap

**Empirically open.** There is broad evidence that cleaning *affects* fairness and a clear theory of fairness *impossibilities*, but no agreed formalization of "fair cleaning," no method that provably improves both quality and downstream fairness across datasets, and no benchmark that measures it deployment-realistically. The gap is conceptual + empirical: we lack (i) a fairness-aware repair *semantics* compatible with minimal-change cleaning, (ii) identifiability conditions under which fair imputation is possible, and (iii) end-to-end benchmarks. Closing it needs causal missing-data models plus Pareto-optimization integrated into cleaning systems.

## 7. Current Research (as of June 2026)

- Causal/counterfactual imputation that targets fairness under explicit MNAR assumptions *(frontier — verify)*.
- Fairness-constrained repair as multi-objective ILP with anytime Pareto frontiers (Stoyanovich, Roy, Salimi groups) *(frontier — verify)*.
- LLM-based imputation audited for demographic bias amplification *(frontier — verify)*.
- Connecting database repair semantics (CQA) with fairness: "fair certain answers" over the repair space.

## 8. Future Work

- Identifiability theory for fair imputation under realistic missingness.
- Repair operators with formal fairness-preservation guarantees end-to-end.
- Group-aware ER with balanced error and uncertainty quantification.
- Benchmarks pairing dirty data, protected attributes, and downstream tasks with ground-truth fairness (links to Benchmarking page).

## 9. Key References

- **[Foundational]** Hardt, Price, Srebro. *Equality of Opportunity in Supervised Learning.* NeurIPS, 2016. — [arXiv](https://arxiv.org/abs/1610.02413)
- **[Foundational]** Kleinberg, Mullainathan, Raghavan. *Inherent Trade-Offs in the Fair Determination of Risk Scores.* ITCS, 2017. — [arXiv](https://arxiv.org/abs/1609.05807)
- **[Foundational]** Rubin. *Inference and Missing Data.* Biometrika, 1976. — [DOI](https://doi.org/10.1093/biomet/63.3.581)
- **[SOTA]** Guha, Khan, Stoyanovich, Schelter. *Automated Data Cleaning Can Hurt Fairness in Machine Learning-Based Decision Making.* IEEE TKDE, 2024. — [DOI](https://doi.org/10.1109/TKDE.2024.3365524)
- **[SOTA]** Salimi, Rodriguez, Howe, Suciu. *Interventional Fairness: Causal Database Repair for Algorithmic Fairness.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319901)
- **[Survey]** Mehrabi, Morstatter, Saxena, Lerman, Galstyan. *A Survey on Bias and Fairness in Machine Learning.* ACM Computing Surveys, 2021. — [DOI](https://doi.org/10.1145/3457607)

## 10. Worked Example

Consider a loan dataset with protected attribute $A\in\{a,b\}$ and a binary income feature used by a downstream classifier $\hat Y$. Group $a$ has 6 records, group $b$ has 4, but $b$ has 2 missing-income cells (missingness rate $0.50$ vs. $0$ for $a$).

**Mean imputation.** Observed incomes in $b$ are $\{30k, 30k\}$, so both missing cells get $30k$. This collapses $b$'s income variance to near-zero and pins every imputed record below the classifier's $40k$ approval threshold, giving $\Pr(\hat Y{=}1\mid A{=}b)=0$.

**Group-aware draws.** Instead, sample each missing cell from $b$'s posterior, which (with a wider prior) yields $\{30k, 55k\}$. Now one imputed record clears the threshold: $\Pr(\hat Y{=}1\mid A{=}b)=1/4=0.25$.

If group $a$ has $\Pr(\hat Y{=}1\mid A{=}a)=0.33$, the demographic-parity gap moves from $|0.33-0|=0.33$ (mean imputation) to $|0.33-0.25|=0.08$. Same quality target, very different fairness — illustrating that the *cleaning choice*, not the model, drove the disparity.

---
*Part of the [DBMS Research catalog](../../README.md).*
