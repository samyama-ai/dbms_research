---
id: 16-data-cleaning-quality/error-detection-no-ground-truth
title: "Error Detection Without Ground Truth"
topic: 16-data-cleaning-quality
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Error Detection Without Ground Truth

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/error-detection-no-ground-truth` · **Status:** empirically-open
> **Verification note:** In §10 the stated pairwise agreements (0.82/0.78/0.74) and the recovered accuracies (0.90/0.85/0.80) are not mutually consistent under the given formula — those accuracies imply agreements 0.78/0.74/0.71, and the stated agreements imply accuracies ≈0.93/0.87/0.82; the numbers are illustrative.

## 1. Problem Statement

Given a dirty relation $r$ with **no labeled clean instance** and no oracle, flag the set of erroneous *cells* (or tuples) $E \subseteq \text{cells}(r)$. Errors are heterogeneous: typos, formatting/unit inconsistencies, integrity-constraint violations, outliers, missing values disguised as defaults, and semantic violations (a city in the wrong country). 

Formally, let $r = r^\* \oplus N$ where $r^\*$ is the unknown clean instance and $N$ a noise process. We must estimate $E = \{c : r[c] \neq r^\*[c]\}$ maximizing F1 against the (unobserved) true $E$.
- **Decision:** is cell $c$ an error?
- **Optimization:** maximize expected F1 / minimize Bayes risk under an unknown noise model.
- **Ranking:** order cells by error probability for human review under a budget $B$.

The defining difficulty: without ground truth, precision/recall cannot be measured during operation, and different error *types* require different detectors (rule-based, statistical, ML, knowledge-base), which must be combined without supervision.

## 2. Mathematical Foundations

Each detector $d_i$ defines a signal $s_i(c) \in [0,1]$. Unsupervised aggregation is the problem of combining weak labelers without labels — formalized by **Dawid–Skene** latent-confusion-matrix models and **crowd/weak-supervision** theory (Snorkel's generative model): estimate detector accuracies from agreement structure via the method of moments on the second/third-order agreement tensors, identifiable when detectors are conditionally independent given the true label and accuracies exceed $1/2$.

Statistical error/outlier detection rests on **density estimation** and concentration: a cell is anomalous if its conditional likelihood $p(r[c]\mid \text{context})$ is low. Integrity-violation detection grounds in **constraint satisfaction**: given DCs/FDs $\Sigma$, a *minimal* set of cells whose change satisfies $\Sigma$ is a minimum vertex cover of the *conflict hypergraph* — **NP-hard** (vertex cover). Information theory bounds detectability: if noise entropy approaches signal entropy, the channel is non-identifiable and **no** detector beats the prior (an info-theoretic impossibility). VC/Rademacher bounds govern how confidently per-type detectors generalize from self-supervised pretext tasks.

## 3. State of the Art (SOTA)

- **HoloDetect** (Heidari, McGrath, Ilyas, Rekatsinas, *SIGMOD 2019*) — few-shot/weakly-supervised error detection with data augmentation to learn noise channels.
- **Raha** (Mahdavi et al., *SIGMOD 2019*) — configuration-free detection that runs a *portfolio* of base detectors and clusters their outputs, requiring only a tiny interactive label budget; the systems-SOTA for low-supervision detection.
- **Picket** (Liu et al., *VLDB 2020*) — self-supervised, learns to flag corrupted tuples for ML pipelines via a transformer reconstruction loss.
- **ED2 / activeclean / metadata-driven** lines for active-learning-minimal detection.
- **Garf, RECODE, LLM-based detectors (2023–2025)** — using foundation models / GPT-class reasoning over cell context as zero-/few-shot detectors *(frontier — verify)*.
- Classic baselines: dBoost (statistical), KATARA (knowledge-base + crowd), NADEEF (rule engine).

## 4. Upper Bound

No algorithm-independent upper bound on F1 exists, because the achievable error is governed by the (unknown) noise model. Under the conditional-independence weak-supervision model, detector accuracies and the true-label posterior are estimable in **polynomial time** via tensor decomposition with sample complexity $O(\epsilon^{-2})$ for $\epsilon$-accurate accuracy estimates. For constraint-based detection, computing a minimal repair-cover is a $2$-approximation in poly-time (vertex-cover LP rounding). Self-supervised reconstruction detectors run in $O(|r|\cdot \text{model})$ inference time, linear in cells.

## 5. Lower Bound

- **Info-theoretic impossibility:** when the noise distribution overlaps the clean conditional distribution (non-identifiable channel), expected F1 is upper-bounded by the Bayes detector on priors alone — no detector can exceed it (a no-free-lunch / channel-capacity bound).
- **NP-hardness:** minimum-cardinality error set consistent with FDs/DCs is NP-hard (vertex cover / hitting set), and **inapproximable** below the vertex-cover threshold under UGC.
- **Weak-supervision identifiability:** if detectors are correlated in unknown ways (violating conditional independence), the latent accuracies are **not identifiable** — a structural lower bound on label-free aggregation.

## 6. The Gap

This is **empirically open**: there is no theory predicting achievable precision/recall for a given dataset and detector portfolio, and no certificate that a chosen flagged set is near-optimal. The gap between (a) what minimal supervision provably buys (identifiability under independence) and (b) what real heterogeneous detectors achieve is unquantified. Closing it requires either a measurable proxy for detection quality without labels, or provable detectability conditions tied to dataset statistics. Currently SOTA systems are compared only on benchmark datasets with synthetic-or-curated ground truth — which itself biases conclusions.

## 7. Current Research (as of June 2026)

- LLM-as-detector with retrieval-augmented context and self-consistency voting; calibration of LLM error probabilities *(frontier — verify)*.
- Theory connecting weak-supervision aggregation guarantees to the data-cleaning setting where detectors are correlated by shared constraints.
- Benchmarks beyond curated datasets (e.g., realistic injected-error suites, REIN benchmark) and label-free evaluation metrics.
- Active groups: Rekatsinas (Wisconsin→ETH/Apple), Ilyas/Chu (Waterloo), Abedjan (Hannover, Raha/REIN), Stoyanovich (NYU, responsible data).

## 8. Future Work

- Label-free quality estimators (proxy F1) with guarantees.
- Detectors robust to *adversarial / systematic* (non-random) corruption.
- Unified type-agnostic detection that provably composes per-type detectors.
- Detection that propagates calibrated uncertainty downstream to repair and to ML training.

## 9. Key References

- **[SOTA]** Heidari, McGrath, Ilyas, Rekatsinas. *HoloDetect: Few-Shot Learning for Error Detection.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319888)
- **[SOTA]** Mahdavi et al. *Raha: A Configuration-Free Error Detection System.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3324956)
- **[SOTA]** Liu, Han, et al. *Picket: Guarding Against Corrupted Data in Tabular Data during Learning and Inference.* VLDB Journal, 2020/2022. — [DOI](https://doi.org/10.1007/s00778-021-00699-w)
- **[Foundational]** Dawid, Skene. *Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm.* Applied Statistics, 1979. — [DOI](https://doi.org/10.2307/2346806)
- **[Foundational]** Ratner, Bach, Ehrenberg, Fries, Wu, Ré. *Snorkel: Rapid Training Data Creation with Weak Supervision.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3157794.3157797)
- **[Survey]** Abedjan, Chu, Deng, Fernandez, Ilyas, Ouzzani, Papotti, Stonebraker, Tang. *Detecting Data Errors: Where Are We and What Needs to Be Done?* PVLDB, 2016. — [DOI](https://doi.org/10.14778/2994509.2994518)

## 10. Worked Example

One dirty cell, three independent unsupervised detectors $d_1,d_2,d_3$ voting on whether a cell is an error. We have no labels, but Dawid–Skene/Snorkel can estimate accuracies from *agreement structure*. Over many cells the pairwise agreement rates are: $\Pr[d_1{=}d_2]=0.82$, $\Pr[d_1{=}d_3]=0.78$, $\Pr[d_2{=}d_3]=0.74$.

Assume conditional independence given the true label and accuracy $a_i=\Pr[d_i\text{ correct}]$. For two-class balanced labels, agreement $\Pr[d_i{=}d_j]=a_i a_j+(1{-}a_i)(1{-}a_j)=2a_ia_j-a_i-a_j+1$. Solving the three equations (method of moments) gives, e.g., $a_1\approx0.90,\ a_2\approx0.85,\ a_3\approx0.80$ — recovered with **no ground truth**.

Now a cell where $d_1=\text{error}, d_2=\text{error}, d_3=\text{clean}$. The log-odds posterior is $\log\frac{0.90}{0.10}+\log\frac{0.85}{0.15}-\log\frac{0.80}{0.20}\approx 2.20+1.73-1.39=2.54>0$, so the weighted vote flags it as an error. Note the impossibility caveat: if the noise channel made all three detectors agree-by-correlation, the independence assumption breaks and $a_i$ become non-identifiable.

---
*Part of the [DBMS Research catalog](../../README.md).*
