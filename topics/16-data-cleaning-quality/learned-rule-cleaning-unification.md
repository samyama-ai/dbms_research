---
id: 16-data-cleaning-quality/learned-rule-cleaning-unification
title: "Learned vs Rule-Based Cleaning Unification"
topic: 16-data-cleaning-quality
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Learned vs Rule-Based Cleaning Unification

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/learned-rule-cleaning-unification` · **Status:** empirically-open

## 1. Problem Statement

Data cleaning has historically split into two paradigms. The **logical/rule-based** paradigm expresses correctness declaratively — functional dependencies (FDs), conditional FDs (CFDs), denial constraints (DCs), matching dependencies, edit rules — and repairs the data to satisfy them at minimum cost. The **statistical/ML** paradigm models the data distribution and flags or imputes values that are improbable under a learned model (e.g., outlier detection, probabilistic imputation, learned error classifiers).

The problem is to design **one principled framework** in which logical constraints and statistical signals are *first-class citizens of the same objective*, such that a repair is jointly optimal with respect to (a) constraint satisfaction and (b) likelihood under a data-generating model — rather than two pipelines stapled together with ad hoc thresholds.

Variants:
- **Decision:** Does there exist an assignment with weighted-logical cost $\le k$ and log-likelihood $\ge \ell$?
- **Optimization:** Find the repair minimizing a combined objective $\lambda \cdot \text{Cost}_{\text{logic}} + (1-\lambda)\cdot \text{Cost}_{\text{stat}}$.
- **Inference/marginal:** Compute the posterior probability that a given cell is erroneous given both rules and the model.

## 2. Mathematical Foundations

Let $D$ be a database instance over schema $R$, and $\Sigma$ a set of integrity constraints. A **repair** $D'$ is an instance with $D' \models \Sigma$; the cost $\Delta(D, D')$ counts cell changes (or weighted edits). Classical minimum-cost repair under FDs/DCs is the optimization core.

Unification is naturally expressed as a **factor graph / Markov logic** model: define a joint distribution
$$P(D') \propto \exp\!\Big( -\sum_{\phi \in \Sigma} w_\phi \cdot v_\phi(D') + \sum_{c}\log p_\theta(c \mid \text{context}) \Big),$$
where $v_\phi$ counts violations of (soft) constraint $\phi$ with learned weight $w_\phi$, and $p_\theta$ is a learned per-cell density. MAP inference over this distribution *is* the unified repair; marginal inference yields calibrated error probabilities. This is precisely the **Markov Logic Network (MLN)** view, and connects cleaning to **statistical relational learning** and to **probabilistic databases** (possible-worlds semantics).

Key tools: weighted MAX-SAT and its LP/SDP relaxations; submodularity (when the violation function is submodular, greedy gives $(1-1/e)$); the **chase** for constraint propagation; and information-theoretic descriptions (MDL — pick the repair that minimizes description length of model + corrections).

## 3. State of the Art (SOTA)

- **HoloClean** (Rekatsinas, Chu, Ilyas, Ré; VLDB 2017) is the canonical unification: it compiles DCs, statistical correlations, and external signals into a single factor graph and performs probabilistic inference, reporting state-of-the-art repair F1 on standard benchmarks.
- **Raha / Baran** (Mahdavi, Abedjan; SIGMOD 2019, VLDB 2020) — configuration-free error *detection* and value-correction that aggregate many weak signals via learned ensembles.
- **HoloDetect** (Heidari, McGrath, Ilyas, Rekatsinas; SIGMOD 2019) learns error-generation models with data augmentation to bridge few labels.
- LLM-assisted cleaning (e.g., **GPT-driven imputation/repair**, 2023–2025) is the current empirical frontier for incorporating world knowledge.

## 4. Upper Bound

For the unified MAP objective, exact inference is intractable in general, but several tractable regimes are known. When constraints are FDs and the statistical term is per-cell, minimum-cost repair admits approximation: the **vertex-cover / LP-rounding** reduction gives a factor-2 approximation for single-FD repair, and constant-factor results extend to bounded constraint interaction. For submodular violation objectives, greedy yields $1 - 1/e$. HoloClean's relaxation runs MAP via Gibbs sampling / quadratic-program relaxation in time polynomial per iteration in the number of cells and candidate values; no global optimality guarantee is claimed.

## 5. Lower Bound

Minimum-cost repair is **NP-hard** already for two FDs and for DCs (reduction from MAX-2SAT / vertex cover; Kolahi & Lakshmanan, ICDT 2009; Bohannon et al., SIGMOD 2005). MAP inference in general MLNs / factor graphs is **NP-hard** and marginal inference is **#P-hard** (counting satisfying worlds). Thus the unified objective inherits both NP-hardness (optimization) and #P-hardness (the probabilistic/counting variant). These are unconditional in the standard model of computation; no fine-grained tightness is established.

## 6. The Gap

The *computational* gap (NP-hard objective vs. polynomial-time heuristic inference) is well understood and arguably "closed" in the sense that hardness is expected. The genuinely **open** gap is **modeling/semantic**: there is no agreed-upon principled way to set the relative weight $\lambda$ (or the $w_\phi$) so that logical and statistical evidence are commensurable, no calibration guarantee that posterior error probabilities are sound, and no characterization of when adding a learned signal can *override* a hard constraint. The empirical gap — generalization across datasets without per-dataset tuning — remains wide.

## 7. Current Research (as of June 2026)

Active directions: (i) LLMs as the statistical prior, with constraints as a verifier/guardrail — *(frontier — verify)* several 2025 systems use retrieval + constraint repair loops; (ii) weak-supervision/data-programming weight learning (Ré group lineage) to set $w_\phi$ from noisy signals; (iii) neuro-symbolic repair where differentiable relaxations of DCs are co-trained with imputation models. Groups: Ilyas/Rekatsinas (Inductiv/Apple, UWaterloo), Ré (Stanford), Abedjan (Leibniz Univ. Hannover/TU Berlin), Chu (Georgia Tech). Calibration and "when to trust the model vs the rule" remain unresolved *(frontier — verify)*.

## 8. Future Work

- A semantics for *soft constraints* with provable calibration of resulting error posteriors.
- Theoretical characterization of when learned priors strictly improve repair accuracy over rules alone (sample complexity bounds).
- Compositional weight-learning that transfers across schemas.
- Unified benchmarks separating modeling error from inference error.

## 9. Key References

- **[Foundational]** Bohannon, Fan, Flaster, Rastogi. *A Cost-Based Model and Effective Heuristic for Repairing Constraints by Value Modification.* SIGMOD, 2005. — [DBLP](https://dblp.org/rec/conf/sigmod/BohannonFFR05.html)
- **[Foundational]** Richardson, Domingos. *Markov Logic Networks.* Machine Learning, 2006. — [DOI](https://doi.org/10.1007/s10994-006-5833-1)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[SOTA]** Heidari, McGrath, Ilyas, Rekatsinas. *HoloDetect: Few-Shot Learning for Error Detection.* SIGMOD, 2019. — [arXiv](https://arxiv.org/abs/1904.02285)
- **[SOTA]** Mahdavi, Abedjan, et al. *Raha: A Configuration-Free Error Detection System.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3324956)
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books / Morgan & Claypool, 2019. — [DOI](https://doi.org/10.1145/3310205)

## 10. Worked Example

Consider `Person(Name, Zip, City)` with FD `Zip → City` and three tuples:

| t | Zip | City |
|---|-----|------|
| 1 | 10001 | New York |
| 2 | 10001 | New York |
| 3 | 10001 | Bostton |

The FD is violated: $t_3$ disagrees on City. A purely rule-based repair could change either *all* three Cities or just $t_3$ — minimum cost (1 edit) picks $t_3$. But *which* value? The rule alone is indifferent between "New York" and "Bostton".

Now add the statistical term: a learned per-cell density gives $p_\theta(\text{City}=\text{New York}\mid \text{Zip}=10001)=0.95$, while "Bostton" has near-zero likelihood (it is not even a dictionary city). The unified objective scores candidate $t_3.\text{City}$:

$$\text{New York}: w_\phi\cdot 0 + (-\log 0.95)\approx 0.05,\qquad \text{Bostton}: w_\phi\cdot 1 + (-\log 10^{-6})\approx w_\phi + 13.8.$$

MAP inference sets $t_3.\text{City}=\text{New York}$, simultaneously satisfying the FD and maximizing likelihood — exactly the joint optimum the framework targets.

---
*Part of the [DBMS Research catalog](../../README.md).*
