---
id: 16-data-cleaning-quality/update-repairs-value-choice
title: "Update-Based Repairs with Value Imputation"
topic: 16-data-cleaning-quality
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Update-Based Repairs with Value Imputation

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/update-repairs-value-choice` · **Status:** open

## 1. Problem Statement

Given an instance $I$, constraints $\Sigma$ (FDs, CFDs, denial constraints, matching dependencies), restore consistency by **updating individual cell values** — not deleting tuples — while choosing **plausible replacement values**. The objective combines two terms:

$$\min_{I' \models \Sigma}\quad \underbrace{\lambda \cdot d_{\text{edit}}(I, I')}_{\text{minimal change}} \;+\; \underbrace{(1-\lambda)\cdot \ell_{\text{impute}}(I')}_{\text{value plausibility}},$$

where $d_{\text{edit}}$ counts changed cells and $\ell_{\text{impute}}$ scores how plausible the chosen new values are (likelihood under a data distribution / external master data / learned model).

Variants:
- **Decision:** Is there a U-repair with $\le k$ cell changes satisfying $\Sigma$?
- **Optimization:** Minimize the joint objective (a MAP/MRF inference problem).
- **Imputation sub-problem:** Given the *set of cells to change* is fixed, choose values — itself a prediction problem.
- **Domain models:** finite/categorical domains vs. infinite/continuous (fresh value/labeled-null choices, à la the chase).

## 2. Mathematical Foundations

U-repair semantics (Wijsen 2005) treats updates as the atomic operation. The interaction structure is again a **conflict hypergraph**, but updates *propagate*: changing a cell to satisfy one constraint may violate another, so the feasible region is non-convex and the optimum is a **fixpoint**. Formally the joint objective is a **MAP inference** in a factor graph / Markov Random Field whose factors encode (i) hard constraints from $\Sigma$ and (ii) soft factors from the imputation model — i.e., a **probabilistic graphical model** view (HoloClean). 

For value choice in infinite domains, repairs may introduce **labeled nulls** and are formalized via the **chase**; minimality is measured against a homomorphism order. Statistical foundations: imputation as estimating $P(\text{cell value}\mid \text{context})$, with guarantees framed via VC-dimension / sample-complexity of the value predictor and information-theoretic limits on recoverability (you cannot impute information absent from the data + side channels). Submodularity of certain coverage objectives yields greedy guarantees in restricted cases.

## 3. State of the Art (SOTA)

- **HoloClean** (Rekatsinas et al., VLDB 2017): unifies integrity constraints, quantitative statistics, and external dictionaries into a probabilistic model; performs value imputation jointly with repair — the canonical SOTA system.
- **LLUNATIC** (Geerts et al., VLDB 2013): chase-based U-repairs with cost-managed value choices and preference among "cell groups."
- **ERACER** (Mayfield et al., SIGMOD 2010): relational dependency networks for joint imputation and cleaning.
- **Baran / RAHA / Daisy and recent LLM-imputers** (Mahdavi, Abedjan and others; 2019–2024) learn value corrections from few labels.
- **LLM-based imputation** (e.g., foundation-model "fill-in" for missing/erroneous cells), 2023–2025. *(frontier — verify)*

## 4. Upper Bound

- Exact minimum-cell-change U-repair: **FPT** in the repair budget $k$ via bounded branching over violations ($O(b^k\,\mathrm{poly})$ with bounded body width $b$); MAP inference solved approximately via Gibbs sampling / loopy BP (HoloClean) in near-linear passes over conflicts.
- For a single FD over a finite domain, optimal value-choice U-repair is poly-time (assign each equivalence class its plurality / minimum-cost value).
- ILP/MaxSAT formulations give exact solutions at moderate scale.

## 5. Lower Bound

- Minimum-cardinality U-repair is **NP-hard** for $\ge 2$ FDs and for denial constraints (reduction from vertex cover / MAX-SAT), and **APX-hard**.
- MAP inference in the induced MRF is **NP-hard** in general (it embeds weighted MAX-SAT).
- **Information-theoretic** limit: when the true value is not determined by any constraint or correlated attribute, no algorithm can recover it better than the data prior — a hard accuracy ceiling independent of compute.
- Even *verifying* a claimed value-optimal repair can be $\mathsf{coNP}$-hard via the CQA connection.

## 6. The Gap

For finite domains and bounded-arity constraints the *combinatorial* side is well understood (NP/APX-hard with FPT and ILP solvers). The open gap is **value choice with guarantees**: no algorithm provably achieves a constant-factor trade-off between edit distance and imputation accuracy under interacting constraints, and there is no matching lower bound characterizing the best achievable accuracy/edit Pareto frontier. The continuous-domain and labeled-null version lacks even a clean optimality definition. Closing it needs a unified objective with provable approximation and an information-theoretic characterization of imputability.

## 7. Current Research (as of June 2026)

- **LLM- and foundation-model-driven imputation** integrated with constraint repair, with calibration/abstention to bound hallucinated values (Abedjan, Papotti, Ilyas groups). *(frontier — verify)*
- **Differentiable repair** end-to-end optimized for downstream task loss. *(frontier — verify)*
- **Weak-supervision / few-label** correction (Baran-style) extended with self-supervised value models. *(frontier — verify)*
- Theoretical work on **sample complexity** of imputation under dependencies. *(frontier — verify)*

## 8. Future Work

- Approximation algorithms with provable edit/accuracy trade-offs for interacting constraints.
- Information-theoretic limits of value recoverability given a constraint set + side data.
- Trustworthy LLM imputation with verifiable plausibility and provenance.
- Continuous-domain U-repairs with a principled minimality order.

## 9. Key References

- **[Foundational]** Wijsen. *Database Repairing Using Updates.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1093382.1093385)
- **[Foundational]** Bohannon, Fan, Flaster, Rastogi. *A Cost-Based Model and Effective Heuristic for Repairing Constraints by Value Modification.* SIGMOD, 2005. — [DOI](https://doi.org/10.1145/1066157.1066175)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[SOTA]** Geerts, Mecca, Papotti, Santoro. *The LLUNATIC Data-Cleaning Framework.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536360.2536363)
- **[SOTA]** Mahdavi, Abedjan, et al. *Raha / Baran: Configuration-Free and Few-Shot Error Detection & Correction.* SIGMOD, 2019 / VLDB, 2020. — [Raha DOI](https://doi.org/10.1145/3299869.3324956)
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books, 2019. — [DOI](https://doi.org/10.1145/3310205)

## 10. Worked Example

Table $I$ with two FDs $\Sigma=\{\textsf{Zip}\to\textsf{City},\ \textsf{City}\to\textsf{State}\}$:

| id | Zip   | City      | State |
|----|-------|-----------|-------|
| 1  | 02139 | Cambridge | MA    |
| 2  | 02139 | Cambridge | MA    |
| 3  | 02139 | Boston    | NY    |

Tuple 3 conflicts on both FDs: its `City` disagrees with $t_1,t_2$ under $\textsf{Zip}\to\textsf{City}$, and `Boston→NY` disagrees with the (correct) `Boston→MA` mapping.

**Objective.** With $\lambda=0.5$, edit cost $d_{\text{edit}}$ = number of changed cells, and $\ell_{\text{impute}}$ = negative log-likelihood of chosen values under a master-data dictionary that asserts $P(\text{City}=\text{Cambridge}\mid \text{Zip}=02139)=0.95$ and $P(\text{State}=\text{MA}\mid\text{City}=\text{Cambridge})=1$.

**Option A — change `City`:** $t_3.\textsf{City}\to\text{Cambridge}$. Then $\textsf{City}\to\textsf{State}$ forces $t_3.\textsf{State}\to\text{MA}$ too (propagation!). Cost: 2 cell edits, but both values are high-likelihood. Joint cost $\approx 0.5\cdot 2 + 0.5\cdot(-\log 0.95 - \log 1)=1.0+0.026=1.026$.

**Option B — change `Zip`:** edit $t_3.\textsf{Zip}$ to some value mapping to Boston/NY — but no dictionary support, so $\ell_{\text{impute}}$ is large.

Option A wins. Note the **fixpoint** behavior of section 2: repairing one cell to satisfy FD$_1$ triggered a second repair to keep FD$_2$ satisfied. With a single FD this would be poly-time (plurality vote); the two interacting FDs are what make minimum-cardinality U-repair NP-hard.

---
*Part of the [DBMS Research catalog](../../README.md).*
