# Testing Learned Database Components

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/testing-learned-components` · **Status:** open

## 1. Problem Statement
Learned components — learned indexes (RMI/ALEX/PGM), learned cardinality estimators (Naru, MSCN), and learned/steering optimizers (Bao, Balsa) — replace algorithmically-specified subroutines with models trained on data and/or workloads. Testing them is harder than testing classical code because correctness is **statistical and contract-relative**, not a fixed input→output map. The problem: develop **oracles** (decision procedures for "is this output acceptable?") and **adversarial workloads** that expose correctness and robustness failures.

Variants:
- **Hard-correctness (decision):** does the component preserve an invariant it *must* never violate? (A learned index must still return the correct record set; a learned optimizer must produce a *valid* plan computing the right answer.) These admit exact oracles.
- **Soft-quality (optimization):** estimates/plans may be wrong but must stay within a tolerance and degrade gracefully under shift.
- **Robustness (counting/search):** find inputs (data + query) on which the model's error or latency exceeds a threshold — a search over a high-dimensional adversarial space.

## 2. Mathematical Foundations
A learned component is a function $f_\theta: \mathcal{X}\to\mathcal{Y}$ with $\theta$ fit on sample $S$. Two correctness notions:
1. **Hard invariants** $I(x, f_\theta(x))$ that hold for *all* $x$ regardless of $\theta$ — e.g., a learned index's predicted position $\hat{p}$ must satisfy correctness *after* the mandatory local search/error-bounded correction, so $I$: "returned set $= \sigma_{\text{key}=k}(R)$." Here testing reduces to **metamorphic** and **differential** testing against a reference structure.
2. **Soft contracts** measured by a loss; robustness is an $\ell_p$-ball guarantee: $\forall x'\!:\|x'-x\|\le\epsilon \Rightarrow |f_\theta(x')-f_\theta(x)|\le L\epsilon$ (Lipschitz/certified-robustness framing).

Adversarial input search is $\max_{x\in\mathcal{D}} \mathcal{L}(f_\theta(x), y^*(x))$, generally non-convex; gradient access (white-box) reduces it to PGD-style attacks, while black-box engines need search (coverage-guided fuzzing, MCMC over query/data space). Metamorphic relations $f(T(x)) \mathrel{R} f(x)$ (e.g., adding a contradictory predicate must not *increase* estimated cardinality) supply oracles without ground truth.

## 3. State of the Art (SOTA)
- **Differential testing** of estimators/optimizers against a trusted engine and against exact `COUNT(*)`; **SQLancer**-style logic testing (TLP, NoREC, PQS; Rigger & Su, OSDI/ESEC-FSE 2020) finds *result* bugs and is being repurposed to flag optimizer-driven wrong answers in learned-plan engines.
- **Metamorphic testing** for cardinality monotonicity (e.g., MUTANT / Cynthia-style query mutation).
- **Robustness studies:** Negi et al. and the "Are We Ready for Learned CE?" line stress learned estimators under shift; learned-index work (ALEX, Updatable PGM) reports adversarial-key and adversarial-update degradation.
- **Learned-optimizer guardrails:** Bao's "do no harm" hint-selection and fallback-to-default are a *systems* answer to robustness, effectively an online oracle.

## 4. Upper Bound
For hard invariants, exact oracles exist and testing is cheap: a learned index can be **wrapped** so its output is verified by the mandatory error-bounded local search, making the *served* answer always correct in $O(\log \text{err})$ extra work (PGM/RMI guarantees). For soft contracts, **certified robustness** (randomized smoothing, interval-bound propagation) gives provable $\ell_2$/$\ell_\infty$ tolerance certificates of radius $r$ with confidence $1-\alpha$ in time polynomial in model size — an upper bound on the *guaranteed* safe region, though typically loose.

## 5. Lower Bound
Robustness verification of even ReLU networks is **NP-hard** (Katz et al., Reluplex/CAV 2017), so exact "is this estimator within tolerance on all inputs in region $X$?" is intractable in the worst case. Finding a worst-case adversarial input is at least as hard. Information-theoretically, no finite test set certifies generalization under arbitrary distribution shift (no-free-lunch / PAC sample-complexity lower bounds), so **soft-quality testing cannot be complete** — only the hard-invariant fragment is decidably testable.

## 6. The Gap
Open. The hard-invariant fragment is solved (wrap + differential test), but there is **no scalable, sound-and-complete oracle for soft quality and robustness**: exact verification is NP-hard, and empirical testing cannot certify shift-robustness. The gap between cheap-but-unsound fuzzing and expensive-but-incomplete formal verification is wide and genuinely open. Closing it needs either tractable abstractions specialized to DB models, or accepted *runtime* guards turning soft contracts into hard ones.

## 7. Current Research (as of June 2026)
- Coverage-guided, **schema-aware fuzzers** that co-mutate data and queries to maximize estimator/optimizer error (overlaps with adversarial-cardinality-workloads) *(frontier — verify)*.
- **Runtime safety wrappers** / selective prediction: serve the learned answer only inside a certified region, else fall back — turning testing into deployment-time monitoring.
- Verification of small DB models via abstract interpretation; metamorphic-relation mining from SQL semantics *(frontier — verify)*.
- Groups: Rigger (NUS, SQLancer), Binnig/Kraska (learned components), Kemper/Neumann ecosystem, and the neural-verification community (Katz, Barrett).

## 8. Future Work
- A taxonomy of *enforceable* hard invariants for every learned component so correctness is always wrappable.
- Sound abstract domains tailored to monotone/piecewise-linear DB models for tractable robustness certificates.
- Online drift detectors with formal false-negative bounds.
- Standard adversarial-robustness benchmark suites for learned indexes/estimators/optimizers.

## 9. Key References
- **[Foundational]** Kraska, Beutel, Chi, Dean, Polyzotis. *The Case for Learned Index Structures.* SIGMOD 2018.
- **[SOTA]** Rigger, Su. *Testing Database Engines via Pivoted Query Synthesis (PQS) / NoREC / TLP.* OSDI & ESEC/FSE 2020.
- **[Foundational]** Katz, Barrett, Dill, Julian, Kochenderfer. *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks.* CAV 2017.
- **[SOTA]** Marcus, Negi, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021.
- **[Survey]** Wang, Yang, et al. *Are We Ready for Learned Cardinality Estimation?* VLDB 2021.
- **[Foundational]** Ferragina, Vinciguerra. *The PGM-index: error-bounded learned index.* VLDB 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
