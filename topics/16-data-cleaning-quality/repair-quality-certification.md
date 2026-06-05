# Repair Quality Certification

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/repair-quality-certification` · **Status:** open

## 1. Problem Statement
Data-cleaning systems produce a **repaired** instance $R'$ from a dirty $R$, but the **unknown ground truth** $R^\*$ is never observed. The problem: **certify—with a formal guarantee—that $R'$ is close to $R^\*$** (e.g., bound $d(R', R^\*)$ or the number of remaining errors), without access to $R^\*$.

Variants:
- **A-posteriori certification:** Given $R'$ and a (sampled) oracle, output a high-confidence upper bound on residual error.
- **A-priori guarantee:** A repair algorithm that *provably* outputs $R'$ within $\epsilon$ of $R^\*$ under stated assumptions.
- **Verification (decision):** Is $\Pr[d(R',R^\*) \le \tau] \ge 1-\delta$?

This is the data-cleaning analogue of program verification: today repairs are evaluated on benchmarks with known truth, but **deployments have no such oracle**, so quality is asserted, not certified.

## 2. Mathematical Foundations
Let $d(\cdot,\cdot)$ be a repair distance (number of differing cells, EMD over tuples). With a small **clean sample** $\mathcal{O}$ from an oracle, residual error can be **estimated** with **statistical-learning** tools: a PAC-style bound gives, for a sample of size $n$, $|\hat{\mathrm{err}} - \mathrm{err}| \le \sqrt{\tfrac{\ln(2/\delta)}{2n}}$ (Hoeffding), so error-rate certification reduces to **sample-complexity** with confidence $1-\delta$. **Conformal prediction** yields distribution-free, finite-sample validity for per-cell repair predictions, producing certified prediction *sets*. When repairs are framed as **minimal repairs** w.r.t. constraints $\Sigma$, one can prove $R'\models\Sigma$ (constraint certification) but **not** $R'\approx R^\*$—satisfying constraints is necessary, not sufficient. Information-theoretically, certification needs the **noise/error process** to be (partially) identifiable; without assumptions on how $R$ was corrupted from $R^\*$, $R^\*$ is unrecoverable and uncertifiable (an adversary can hide errors that satisfy $\Sigma$).

## 3. State of the Art (SOTA)
- **Metrics & error estimation: Metanome / cleaning benchmarks** report precision/recall *only when ground truth is available*; there is no standard *certificate* without it.
- **HoloClean / probabilistic repair** (Rekatsinas et al., VLDB 2017) yields marginal probabilities per repaired cell—calibratable into confidence statements, but uncalibrated by default.
- **Sampling-based quality estimation: Sample-and-Clean / SampleClean** (Wang et al., SIGMOD 2014; Krishnan et al., VLDB 2016 *ActiveClean*) gives statistically bounded estimates of *aggregate-query* error after partial cleaning—closest existing thing to a certificate, but for query answers not the full instance.
- **Continuous data validation: Great Expectations, Deequ** (Schelter et al., VLDB 2018 *Automating Large-Scale Data Quality Verification*): assert and monitor constraints, providing operational (not ground-truth-relative) guarantees.

## 4. Upper Bound
With an oracle that can clean sampled cells, **SampleClean/ActiveClean** provide unbiased, CLT-based confidence intervals on cleaned-aggregate answers in $O(n)$ oracle calls for $n$ samples, achieving certified error of width $O(1/\sqrt{n})$ for aggregate estimands. **Conformal prediction** certifies per-cell repair coverage with finite-sample validity under exchangeability, again at $O(1/\epsilon^2)$ samples for accuracy $\epsilon$. These certify *statistical aggregates / coverage*, not a worst-case bound on the entire repaired instance.

## 5. Lower Bound
Certifying $d(R',R^\*)$ over the **full instance** without distributional assumptions is **information-theoretically impossible**: errors that satisfy all stated constraints are undetectable by any constraint-based or sample-based method below their sampling resolution—an **adversarial-corruption lower bound**. Sample-based certification has the unavoidable $\Omega(1/\epsilon^2)$ **sample complexity** for $\epsilon$-accurate error-rate estimates (matching Hoeffding) and **cannot** certify rare/heavy-tail errors without proportionally many samples. Computing a *minimum-cost* certified repair inherits the **NP-hardness** of minimal repair (Bohannon et al. 2005). Thus exact, assumption-free certification is impossible; only statistical, assumption-bounded certificates exist.

## 6. The Gap
**Genuinely open.** We have (a) constraint-satisfaction certificates ($R'\models\Sigma$) and (b) sample/conformal certificates for *aggregates or coverage*, but **no method certifying closeness of the whole repaired instance to ground truth** under realistic (non-adversarial, identifiable) noise. The gap between "we satisfied the constraints" and "we are close to truth" is unbridged. Closing it requires formal noise/identifiability models under which a poly-sample, poly-time certificate for $d(R',R^\*)\le\tau$ provably holds—plus matching impossibility for the rest.

## 7. Current Research (as of June 2026)
- **Conformal data cleaning:** distribution-free residual-error certificates for repairs and LLM-generated fixes *(frontier — verify)*.
- **LLM-as-judge verification of repairs**, with the open problem of certifying the judge itself (calibration, adversarial robustness) *(frontier — verify)*.
- **Data-quality SLAs / observability** (Monte Carlo, Bigeye–style) pushing toward statistical guarantees in production *(frontier — verify)*.
- Groups: Ihab Ilyas & Theo Rekatsinas (probabilistic repair), Sebastian Schelter (Deequ/data validation), Eugene Wu, Sanjay Krishnan (ActiveClean lineage), Wang-Chiew Tan.

## 8. Future Work
- Noise-model assumptions under which full-instance certification is provably achievable.
- Unifying constraint certificates with statistical coverage into a single repair certificate.
- Certified human/LLM-in-the-loop cleaning with budgeted oracle queries (links to crowd-cleaning-cost).
- Benchmarks that score *certificate validity*, not just repair F1.

## 9. Key References
- **[Foundational]** P. Bohannon, M. Flaster, W. Fan, R. Rastogi. *A Cost-Based Model and Effective Heuristic for Repairing Constraints by Value Modification.* SIGMOD, 2005. — [DOI](https://doi.org/10.1145/1066157.1066175)
- **[SOTA]** J. Wang, S. Krishnan, M. J. Franklin, K. Goldberg, T. Kraska, T. Milo. *A Sample-and-Clean Framework for Fast and Accurate Query Processing on Dirty Data.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610505)
- **[SOTA]** S. Krishnan, J. Wang, E. Wu, M. J. Franklin, K. Goldberg. *ActiveClean: Interactive Data Cleaning for Statistical Modeling.* VLDB, 2016. — [DOI](https://doi.org/10.14778/2994509.2994514)
- **[SOTA]** S. Schelter, D. Lange, P. Schmidt, M. Celikel, F. Biessmann, A. Grafberger. *Automating Large-Scale Data Quality Verification (Deequ).* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3229867)
- **[SOTA]** T. Rekatsinas, X. Chu, I. F. Ilyas, C. Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[Foundational]** V. Vovk, A. Gammerman, G. Shafer. *Algorithmic Learning in a Random World (Conformal Prediction).* Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)

## 10. Worked Example

A repaired table $R'$ has $N = 10{,}000$ cells. We hold an oracle that can clean any sampled cell. Draw $n = 400$ cells uniformly, send them to the oracle, and find that $12$ still differ from truth, so the empirical residual error rate is $\hat{p} = 12/400 = 0.03$.

Hoeffding gives, at confidence $1-\delta = 0.95$ ($\delta = 0.05$):
$$|\hat{p} - p| \le \sqrt{\tfrac{\ln(2/\delta)}{2n}} = \sqrt{\tfrac{\ln 40}{800}} = \sqrt{\tfrac{3.689}{800}} \approx 0.068.$$
So we **certify** $p \le 0.03 + 0.068 = 0.098$ with 95% confidence, i.e. at most $\approx 980$ residual erroneous cells.

The catch (section 5): this certifies an *aggregate* rate. A single critical error hidden in an unsampled cell that satisfies all of $\Sigma$ stays invisible — to halve the $\pm0.068$ width we would need $4\times$ the samples ($n=1600$), the unavoidable $\Omega(1/\epsilon^2)$ cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
