# Provenance for Dataflow & ML Pipelines

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/dataflow-ml-pipeline-provenance` · **Status:** partially-solved

## 1. Problem Statement
Modern analytics and ML pipelines compose **opaque operators** — user-defined functions (UDFs), dataframe transformations (pandas/Spark), feature engineering, model `fit`/`transform`, train/test splits — that relational provenance cannot see through: a UDF is a black box, so the semiring algebra that explains $\sigma/\pi/\bowtie$ does not apply. The problem: **capture fine-grained, queryable lineage across UDFs, dataframes, and ML operators**, answering questions like *which training rows influenced this prediction*, *which input cells flowed into this feature*, and *replay/why* over a heterogeneous DAG, despite operator opacity.

Variants: **(coarse DAG)** artifact/operator-level lineage (which dataset version → which model). **(fine-grained data)** row/cell-level input→output mapping through each operator. **(influence/why for ML)** attributing a model output to training examples (a different, statistical notion of "provenance"). **(decision/optimization)** capture target precision under overhead and opacity constraints.

## 2. Mathematical Foundations
Relational provenance ($\mathbb{N}[X]$ semiring, Green et al.) is exact for positive RA but **undefined for arbitrary UDFs**, which can read any subset of input cells. Three formal handles exist: **(1)** treat each UDF as a relation with *declared* or *inferred* dependency footprint — provenance becomes the Cartesian dependency $f(\text{in}) \mapsto$ (rows it touched), recovering a coarse semiring annotation; **(2)** **program analysis / dynamic taint tracking** to derive per-cell data-flow through UDF code (dependency provenance, Cheney–Ahmed–Acar), giving an over-approximation that is sound (no missed dependency) but may be imprecise; **(3)** for ML attribution, provenance becomes **influence functions** $\mathcal{I}(z_{\text{train}}, z_{\text{test}}) \approx -\nabla_\theta L(z_{\text{test}})^\top H_\theta^{-1} \nabla_\theta L(z_{\text{train}})$ (Koh–Liang) or **Data Shapley / TracIn** — a *statistical* lineage distinct from logical witnesses. Dataframe algebra (relational-ish, with order/index) admits a hybrid: known operators get exact provenance, opaque ones get taint- or footprint-based over-approximation. Soundness/precision form a lattice: exact ⊑ taint ⊑ whole-input.

## 3. State of the Art (SOTA)
- **Pipeline / dataframe lineage:** **mlinspect** (Grafberger, Schelter et al., 2021) instruments scikit-learn/pandas pipelines to extract a dataflow DAG with annotated provenance for fairness/data-distribution inspection. **Vamsa** (Microsoft, KDD 2020) statically tracks column provenance in ML scripts. **Lima**, **Nodebook**, and notebook-lineage tools track cell/artifact dependencies. **Pandas/Modin lineage** via Smoke-style or wrapper instrumentation.
- **Platform lineage:** **OpenLineage** + **Marquez**, **DataHub**, **Apache Atlas**, **MLflow**, **Spline** capture *coarse* artifact/operator lineage across pipelines (industry SOTA, table/job granularity).
- **ML attribution:** **Influence functions** (Koh–Liang, ICML 2017), **TracIn** (Pruthi et al., NeurIPS 2020), **Data Shapley** (Ghorbani–Zou, ICML 2019) provide training-data → prediction provenance.

## 4. Upper Bound
For pipelines whose operators are a known library (pandas/sklearn ops with declared semantics), **mlinspect**-style instrumentation captures row-level lineage with overhead within a small constant factor by wrapping each operator and propagating row identifiers — exact where operators are relational, footprint-approximate for UDFs. Static column-provenance (Vamsa) is computed in time linear in the program AST. Dynamic taint tracking yields cell-level dependency provenance at a constant-factor (sometimes higher) runtime cost, sound by construction. ML influence approximations compute per-test attribution in $O(\text{params})$ per training point via Hessian-vector products (no explicit $H^{-1}$).

## 5. Lower Bound
For **arbitrary** UDFs, exact fine-grained provenance is **undecidable / uncomputable** in general: determining the precise input-cell footprint of an arbitrary program reduces to deciding which inputs a Turing-complete function actually reads (a non-trivial semantic property → Rice's theorem). Hence any general scheme must over-approximate (taint) or under-approximate (sampling), with no sound-and-complete-and-efficient option. For ML attribution, influence functions are **provably non-robust**: exact leave-one-out retraining is the ground truth but costs $\Theta(n)$ retrains; the convex approximation has unbounded error for non-convex deep models (empirical and theoretical fragility results, Basu et al., 2021). Thus precise ML provenance has a **statistical lower bound** — no cheap estimator matches retraining in the non-convex regime.

## 6. The Gap
**Partially solved:** coarse artifact lineage (OpenLineage/Marquez/MLflow) is mature and deployed; library-operator row lineage (mlinspect/Vamsa) works for known operators. The **gap** is: (1) precise fine-grained lineage *through arbitrary UDFs* — fundamentally over-approximate, with no agreed precision/overhead Pareto point; (2) unifying *logical* lineage (witness rows) with *statistical* influence (which training points mattered) into one queryable model; (3) cell-level provenance through tensor/dataframe reshapes. Closing requires sound approximations with measured precision and a query language spanning both notions.

## 7. Current Research (as of June 2026)
- Extending **mlinspect**-style capture to deep-learning/feature-store pipelines and to fairness/debugging queries (Schelter, Grafberger groups) *(frontier — verify)*.
- Integrating **OpenLineage** fine-grained (column/row) facets with engine-native lineage (Spark, dbt) — standardizing cross-system lineage *(frontier — verify)*.
- Scalable, more faithful **training-data attribution** (TRAK, datamodels) bridging influence and provenance for large models *(frontier — verify)*.
- Taint-tracking + LLM-assisted UDF dependency inference to tighten the UDF over-approximation *(frontier — verify)*.

## 8. Future Work
A sound approximate UDF-provenance framework with a tunable precision/overhead knob and measured guarantees. A unified query model over logical and statistical lineage. Cell-level provenance through tensor reshapes and embeddings. Standardized fine-grained lineage facets in OpenLineage. Benchmarks for ML-pipeline provenance quality.

## 9. Key References
- **[SOTA]** Stefan Grafberger, Shubha Guha, Julia Stoyanovich, Sebastian Schelter. *mlinspect: Inspecting ML Pipelines for Provenance and Data Distribution Issues.* SIGMOD (demo) / EDBT, 2021. — [DOI](https://doi.org/10.1145/3448016.3452759)
- **[SOTA]** Mohammad Hossein Namaki, et al. *Vamsa: Automated Provenance Tracking in Data Science Scripts.* KDD, 2020. — [arXiv](https://arxiv.org/abs/2001.01861) · [DOI](https://doi.org/10.1145/3394486.3403205)
- **[SOTA]** Pang Wei Koh, Percy Liang. *Understanding Black-box Predictions via Influence Functions.* ICML, 2017. — [arXiv](https://arxiv.org/abs/1703.04730) · [PMLR](https://proceedings.mlr.press/v70/koh17a.html)
- **[Foundational]** James Cheney, Amal Ahmed, Umut Acar. *Provenance as Dependency Analysis.* Mathematical Structures in Computer Science, 2011. — [arXiv](https://arxiv.org/abs/0708.2173) · [DOI](https://doi.org/10.1017/S0960129511000211)
- **[Foundational]** Todd Green, Grigoris Karvounarakis, Val Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** Garima Pruthi, Frederick Liu, Satyen Kale, Mukund Sundararajan. *Estimating Training Data Influence by Tracing Gradient Descent (TracIn).* NeurIPS, 2020. — [arXiv](https://arxiv.org/abs/2002.08484)
- **[Survey]** Boris Glavic. *Data Provenance.* Foundations and Trends in Databases, 2021. — [DOI](https://doi.org/10.1561/1900000068)

## 10. Worked Example

A 3-step sklearn/pandas pipeline on a tiny table `People(age, city, label)` with 4 rows:

```
df2 = df.dropna()                       # known relational op
df3 = OneHotEncoder().fit_transform(    # known library op
          df2[['city']])
score = my_udf(df3)                     # opaque UDF
```

**Known ops (exact, semiring-style).** `dropna` drops the row with a missing `age`, so output rows $\{2,3,4\}$ carry annotations $\{r_2,r_3,r_4\}$ — a clean $\mathbb{N}[X]$ image. One-hot of `city` $\in\{$NYC,LA$\}$ maps each surviving row to itself, so row lineage is preserved exactly: output cell `is_NYC` for row 3 has provenance $r_3$.

**Opaque UDF (over-approximation).** `my_udf` is a black box. Static/footprint inference can only conclude it *may* read all of `df3`, so each output of `my_udf` gets the whole-input lineage $\{r_2,r_3,r_4\}$ — sound (no missed dependency) but imprecise. Dynamic taint tracking might tighten this to, say, only the `is_NYC` column.

**Why a lower bound bites.** Deciding the *exact* cell footprint of an arbitrary `my_udf` reduces to "which inputs does this Turing-complete function actually read" — a non-trivial semantic property, undecidable by Rice's theorem. Hence the inevitable retreat to taint (over-approx) or sampling (under-approx); there is no sound-complete-efficient option for arbitrary UDFs.

---
*Part of the [DBMS Research catalog](../../README.md).*
