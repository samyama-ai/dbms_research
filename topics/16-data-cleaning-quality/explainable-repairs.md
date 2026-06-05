# Explainable Repairs

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/explainable-repairs` · **Status:** open

## 1. Problem Statement

When a cleaning system changes a value (or flags an error), it should produce a **human-interpretable explanation** of *why* the original was deemed wrong and *why* the chosen correction is justified — an explanation a domain expert can audit, accept, reject, or generalize. The problem is to define, compute, and evaluate such explanations for repairs that arise from a mixture of logical constraints, statistical models, and external/LLM evidence.

Variants:
- **Why-error (attribution):** which constraints / which other tuples / which model features made cell $c$ suspect?
- **Why-this-value (justification):** why correction $v$ over alternatives — provenance + counterfactual.
- **Minimal-cause / counterfactual:** the smallest set of facts whose change would flip the repair decision.
- **Global vs. local:** explain one repair vs. summarize a whole repair batch as rules.
- **Optimization:** find the **minimum-size / minimum-cost** explanation meeting a fidelity threshold.

## 2. Mathematical Foundations

Explanations rest on several formal substrates:

- **Data provenance:** why-, how-, and where-provenance (Buneman; Green–Karvounarakis–Tannen **provenance semirings**) trace a repair to the source tuples and rule firings that produced it. The how-provenance polynomial *is* a faithful explanation of derivation.
- **Minimal hitting sets / MUSes:** the set of violated constraints justifying that a cell must change corresponds to a **minimal unsatisfiable subset**; minimum explanations are minimum hitting sets — NP-hard.
- **Counterfactuals & responsibility:** causality à la Halpern–Pearl; the **responsibility** of a fact $f$ for outcome $o$ is $1/(1+|\Gamma|)$ for the smallest contingency set $\Gamma$. Computing responsibility is intractable in general.
- **Feature attribution:** for the statistical component, **Shapley values** (SHAP) attribute the error score to features; exact Shapley is $\#$P-hard but has DB-specific tractable cases.
- **MDL / Occam:** prefer the explanation minimizing description length, formalizing "simplest faithful reason."

Quality is a trade-off between **fidelity** (does the explanation actually entail the repair?) and **interpretability** (size/complexity).

## 3. State of the Art (SOTA)

- **Provenance-based explanations** for queries and updates are mature (ProvSQL, Perm/GProM — Glavic et al.), and provide the backbone for explaining rule-driven repairs.
- **Explaining query answers / outliers:** Wu–Madden *Scorpion* (VLDB 2013), Roy–Suciu *A Formal Approach to Finding Explanations for Database Queries* (SIGMOD 2014) — predicate-based explanations; **Cape** (Miao et al.) for counterbalancing explanations.
- **Repair explanation specifically** is nascent: HoloClean exposes factor-graph marginals (probabilistic "reasons"); interactive systems surface violated DCs.
- **LLM-generated natural-language explanations** of detected errors and proposed fixes are the 2023–2025 empirical frontier — fluent but **fidelity-unverified**.
Because no accepted formal definition + computation + evaluation triad exists for *repair* explanations, status is **open**.

## 4. Upper Bound

For rule-driven repairs, how-provenance gives an *exact* explanation computable in time polynomial in the derivation size; predicate-based explanation search (Scorpion/Roy–Suciu style) is exponential in predicate space but admits polynomial-time approximations with submodular coverage objectives ($1-1/e$ greedy). Minimum-MUS / minimum hitting-set explanations have **$O(\log n)$-approximation** via greedy set cover. Shapley-based attribution for the statistical part has polynomial-time exact algorithms in restricted (e.g., tractable-circuit / read-once) settings, and Monte-Carlo $(\epsilon,\delta)$-approximation otherwise.

## 5. Lower Bound

- **Minimum-size explanations are NP-hard** (minimum hitting set / minimum MUS) and **$(1-o(1))\ln n$-inapproximable** under $\mathsf P\ne\mathsf{NP}$.
- **Responsibility/causality** computation is NP-hard (and complete for higher classes in general queries; Halpern–Pearl actual-cause checking is $\mathrm D^P$/$\Sigma_2^p$-hard depending on formulation).
- **Exact Shapley-value attribution is $\#$P-hard** in general (Deng–Papadimitriou), inherited by feature-attribution explanations.
- **Information-theoretic:** there is an irreducible fidelity–interpretability trade-off — any explanation strictly smaller than the true minimal cause must lose fidelity; no free lunch.

## 6. The Gap

The gap is **fundamental and open on two axes**. (1) *Definitional:* there is no consensus formal definition of a "good repair explanation" that spans logical, statistical, and LLM-derived repairs — provenance explains rules, Shapley explains models, but no unified, composable semantics exists. (2) *Computational vs. usable:* minimum faithful explanations are NP-/#P-hard and log-inapproximable, while LLM explanations are cheap and fluent but lack any fidelity guarantee. Closing it requires both a unifying formal semantics and approximation algorithms with *certified fidelity* — plus human-grounded evaluation that current benchmarks lack.

## 7. Current Research (as of June 2026)

- **Certified / faithful LLM explanations:** pairing LLM-generated natural-language rationales with a provenance or constraint *checker* that verifies entailment *(frontier — verify)*.
- **Counterfactual repair explanations** ("change these k cells and the repair would differ") with responsibility scores.
- **Provenance-for-ML-cleaning:** extending semiring provenance through statistical imputation steps.
- **Interactive explanation** to drive human-in-the-loop repair acceptance and rule generalization.
- Groups: Glavic (Illinois Tech) on provenance, Roy (Duke) and Suciu (UW) on query/explanation theory, Ilyas/Rekatsinas lineage on repair systems, Meliou (UMass) on causality/responsibility in databases. Evaluation methodology is unsettled *(frontier — verify)*.

## 8. Future Work

- A unified, composable semantics of repair explanations across logic + statistics + LLMs.
- Approximation algorithms with certified fidelity bounds.
- Human-subject evaluation protocols and benchmarks for explanation quality.
- Provenance that survives probabilistic/neural imputation steps.

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS, 2007.
- **[Foundational]** Halpern, Pearl. *Causes and Explanations: A Structural-Model Approach.* British J. Philosophy of Science, 2005.
- **[Foundational]** Meliou, Gatterbauer, Moore, Suciu. *The Complexity of Causality and Responsibility for Query Answers and Non-Answers.* VLDB, 2010.
- **[SOTA]** Wu, Madden. *Scorpion: Explaining Away Outliers in Aggregate Queries.* VLDB, 2013.
- **[SOTA]** Roy, Suciu. *A Formal Approach to Finding Explanations for Database Queries.* SIGMOD, 2014.
- **[SOTA]** Lundberg, Lee. *A Unified Approach to Interpreting Model Predictions (SHAP).* NeurIPS, 2017.
- **[Survey]** Glavic. *Data Provenance: Origins, Applications, Algorithms, and Models.* Foundations and Trends in Databases, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
