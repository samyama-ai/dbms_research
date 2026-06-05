# End-to-End Pipeline Quality Propagation

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/pipeline-quality-propagation` · **Status:** open

## 1. Problem Statement

Real data flows through multi-stage pipelines — ingestion, deduplication, imputation, transformation, joins, aggregation, model training. Each stage both *removes* and *introduces* error. The problem: given a pipeline $P = s_k \circ \cdots \circ s_1$ and a quality model for each stage, **quantify the data quality of the output** and **propagate per-cell error / uncertainty / provenance** from inputs through every operator, so that a quality budget can be enforced end-to-end.

Variants:
- **Forward propagation (prediction):** Given input quality distribution and per-stage transfer functions, compute output quality (decision: "does output meet SLA $\tau$?").
- **Inverse / attribution:** Given an observed output defect, attribute it back to responsible stage(s)/inputs (a counting/credit-assignment variant).
- **Optimization:** Choose stage configurations (which cleaner, which threshold) to minimize cost subject to an output-quality constraint, or maximize quality under a compute/labeling budget.

The hard part is that operators are *non-linear*, *correlated*, and *quality-altering*: a join can multiply errors; an aggregation can mask or amplify them; a dedup step can both fix and erase.

## 2. Mathematical Foundations

Model each stage as a (possibly stochastic) map $s_i : \mathcal{D} \to \mathcal{D}$ and quality as a vector $q \in [0,1]^m$ over dimensions (accuracy, completeness, consistency, timeliness — Wang–Strong taxonomy). Propagation seeks a **transfer operator** $T_i$ with $q_{i} \approx T_i(q_{i-1})$.

Foundations it rests on:
- **Provenance semirings** (Green–Karvounarakis–Tannen, PODS 2007): annotate tuples with elements of a commutative semiring $K$; relational operators map to $+$ (union/projection) and $\times$ (join). Choosing $K$ as a *probability* or *error* semiring lets uncertainty propagate compositionally — the algebraic backbone for forward propagation.
- **Probabilistic databases:** output is a distribution; lineage formulas give $\Pr[t \in \text{output}]$, but exact evaluation is $\#\mathsf{P}$-hard (Dalvi–Suciu dichotomy).
- **Error propagation calculus:** first-order (delta-method) propagation $\mathrm{Var}(f) \approx \nabla f^\top \Sigma \nabla f$ for numeric stages; fails under strong nonlinearity → Monte-Carlo / measure transport.
- **Information theory:** data-processing inequality $I(X;s_i(Y)) \le I(X;Y)$ bounds how much *signal* survives, giving a lower envelope on recoverable quality.

## 3. State of the Art (SOTA)

There is **no end-to-end propagation theory**; SOTA is fragmented:
- **Provenance/lineage systems** — ProvSQL (Senellart et al., VLDB 2018) computes semiring/probabilistic provenance for SQL.
- **mlinspect** (Grafberger, Stoyanovich et al., 2021–2022) instruments ML preprocessing pipelines (pandas/sklearn) to inspect distribution and bias changes operator-by-operator — the closest practical "propagation" tool.
- **Data Quality frameworks** — Deequ / unit-tests-for-data (Schelter et al., VLDB 2018) and Great Expectations measure quality *at* stages but do not *propagate* a model across them.
- **Cleaning-pipeline optimizers** — AlphaClean, CPClean (certain predictions over cleaning choices, Karlaš et al., 2020) reason about how cleaning affects a *downstream model's* prediction — a special-case inverse/robustness result.

## 4. Upper Bound

- For pipelines whose stages are **safe (hierarchical) queries**, probabilistic provenance — hence forward quality — is computable in **PTIME** (Dalvi–Suciu safe-plan dichotomy).
- General Monte-Carlo propagation gives an $\epsilon$-accurate output-quality estimate with $O(\epsilon^{-2}\log(1/\delta))$ pipeline replays (Hoeffding) — model-agnostic but expensive.
- CPClean shows **certain-prediction checking** over the space of cleanings of $k$ dirty cells is PTIME for nearest-neighbor classifiers.

## 5. Lower Bound

- Exact forward propagation through joins is **$\#\mathsf{P}$-hard** (inherits the probabilistic-database dichotomy; unsafe queries).
- The data-processing inequality is an **information-theoretic impossibility**: no stage can increase recoverable mutual information, so quality lost at stage $i$ cannot be regained downstream without external evidence.
- Optimal stage-configuration selection under a quality constraint is **NP-hard** (knapsack/Set-Cover-style reductions over discrete cleaner choices).
- Exact error attribution (responsibility) for an output defect is **$\mathsf{NP}$-hard** in general (related to causal-responsibility / $\mathsf{coNP}$ results of Meliou et al.).

## 6. The Gap

This is **genuinely open**. We have compositional *exact* propagation only for tractable (hierarchical) query fragments and *approximate* propagation only via expensive replay. Missing: (i) closed-form, composable transfer functions for non-relational stages (imputers, embeddings, LLM extractors); (ii) tight approximation guarantees better than generic Monte-Carlo; (iii) a unified algebra spanning relational + ML operators. Closing it requires marrying provenance semirings with statistical error models and a fine-grained complexity account of which stage compositions stay tractable.

## 7. Current Research (as of June 2026)

- Extending mlinspect-style instrumentation to LLM/embedding stages and end-to-end uncertainty propagation *(frontier — verify)*.
- "Data debugging" via influence functions and provenance to attribute model errors to input records (Stoyanovich, Ilyas, Suciu lineages).
- Probabilistic-circuit (knowledge-compilation) propagation to push the tractable boundary past hierarchical queries *(frontier — verify)*.
- Quality SLAs / "data contracts" in data-mesh architectures with runtime monitors — industry-driven, theory-light.

## 8. Future Work

- A transfer-function calculus unifying relational, statistical, and learned operators.
- Anytime, budgeted propagation with provable error bars cheaper than $\epsilon^{-2}$ replays.
- Inverse propagation: principled root-cause attribution with responsibility guarantees.
- Standard benchmarks where ground-truth output quality is known so propagation models can be validated (see Benchmarking page).

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Dalvi, Suciu. *Efficient Query Evaluation on Probabilistic Databases.* VLDB Journal, 2007. — [DOI](https://doi.org/10.1007/s00778-006-0004-3)
- **[Foundational]** Wang, Strong. *Beyond Accuracy: What Data Quality Means to Data Consumers.* J. of MIS, 1996. — [DOI](https://doi.org/10.1080/07421222.1996.11518099)
- **[SOTA]** Schelter et al. *Automating Large-Scale Data Quality Verification (Deequ).* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3229867)
- **[SOTA]** Grafberger, Groth, Stoyanovich, Schelter. *Data Distribution Debugging in Machine Learning Pipelines (mlinspect).* VLDB Journal, 2022. — [DOI](https://doi.org/10.1007/s00778-021-00726-w)
- **[SOTA]** Karlaš et al. *Nearest Neighbor Classifiers over Incomplete Information: From Certain Answers to Certain Predictions (CPClean).* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2005.05117)

## 10. Worked Example

A two-stage pipeline $P = s_2 \circ s_1$ over a table of 1000 rows.

- $s_1$ = **dedup**: removes exact duplicates. Suppose 5% of rows are erroneous and dedup has accuracy $a_1=0.9$ (fixes 90% of the duplicate-induced errors it touches).
- $s_2$ = **join** with a reference table whose key coverage is 0.8.

Track *completeness* $q\in[0,1]$. Input completeness $q_0 = 0.95$ (5% missing/bad). Model each stage as a multiplicative transfer: $q_1 = q_0 \cdot (1 - (1-a_1)\cdot 0.05) = 0.95\cdot(1-0.005)=0.9453$. The inner join then *drops* rows lacking a key match, so completeness is multiplied by coverage: $q_2 = q_1 \cdot 0.8 = 0.7562$.

So the SLA check "is output completeness $\ge \tau=0.85$?" **fails** — and attribution is immediate: the join ($\times 0.8$) caused the $0.945\to0.756$ drop, far more than dedup. Note the **data-processing inequality** at work: the join cannot recover completeness lost upstream, only erode it further. This illustrates why per-stage transfer functions, not a single end-to-end number, are needed for credit assignment.

---
*Part of the [DBMS Research catalog](../../README.md).*
