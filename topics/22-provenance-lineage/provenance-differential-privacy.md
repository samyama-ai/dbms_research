# Provenance for Differential Privacy

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-differential-privacy` · **Status:** open

## 1. Problem Statement

Provenance explains *why* a tuple appears in an answer, *how* it was derived, and *where* its values came from. Differential privacy (DP) guarantees that an analyst learns essentially nothing about any single individual. These goals are in direct tension: provenance, by design, points back at the source records, so a faithful lineage of a query answer can leak exactly the per-record information DP is meant to hide.

The problem is to design mechanisms that release **useful** lineage and explanations of query answers — enough to support debugging, auditing, trust, and "why/why-not" questions — while provably satisfying $(\varepsilon,\delta)$-DP (or a relaxation such as Rényi/zCDP) on the underlying base data.

Variants:
- **Decision:** Does a given provenance-release mechanism satisfy $(\varepsilon,\delta)$-DP?
- **Optimization:** Maximize utility (explanation fidelity / coverage) subject to a fixed privacy budget $\varepsilon$.
- **Counting/structural:** Release how-provenance (semiring annotations, witness counts) under DP, where the *structure* of the polynomial — not just a numeric answer — is the sensitive object.

## 2. Mathematical Foundations

Let $D \in \mathcal{X}^n$ be a database; $D \sim D'$ are neighbors differing in one tuple. A randomized mechanism $M$ is $(\varepsilon,\delta)$-DP if for all measurable $S$,
$$\Pr[M(D)\in S] \le e^{\varepsilon}\Pr[M(D')\in S] + \delta.$$

How-provenance is captured by **provenance semirings** (Green–Karvounarakis–Tannen): each answer tuple is annotated by an element of a commutative semiring $(K,+,\cdot,0,1)$, e.g. the polynomial semiring $\mathbb{N}[X]$ over source identifiers $X$. The released object is a function $\Phi: \text{Answers}\to K$.

The core difficulty is **sensitivity**: changing one source tuple can change a provenance polynomial discontinuously (a monomial appears/disappears), so the global sensitivity of "release the polynomial" is unbounded. Useful tools:
- **Smooth sensitivity / propose-test-release** for instance-dependent noise on numeric provenance summaries.
- **Lipschitz extensions** and **stability** for graph-shaped lineage.
- **Local sensitivity of semiring valuations** under tropical/counting homomorphisms $h:K\to\mathbb{R}$.
- **Composition** ($\varepsilon$ accumulates across lineage queries; advanced/Rényi composition give tighter bounds).

## 3. State of the Art (SOTA)

There is no general mechanism that releases full how-provenance under DP. Practical work targets *summaries* of lineage:
- **PrivateSQL / APEx / Chorus** (VLDB 2019; SIGMOD 2018–2020) — DP query engines that track sensitivity through relational operators, effectively a numeric provenance of noise, but they do not expose tuple-level lineage.
- **DP explanations / Scorpion-style** outlier explanation under privacy (frontier work) — releases *predicates* explaining aggregates with DP-noised supports.
- **Semiring DP** results bound sensitivity of provenance valuations under specific homomorphisms (counting, probability) and release the scalar, not the polynomial.

Systems-SOTA = sensitivity-tracking DP engines; theory-SOTA = sensitivity bounds for restricted provenance valuations (positive relational algebra without difference).

## 4. Upper Bound

For an aggregate with bounded per-tuple contribution $\Delta$, the Laplace/Gaussian mechanism gives $(\varepsilon,0)$- or $(\varepsilon,\delta)$-DP with additive error $O(\Delta/\varepsilon)$, and this extends to *numeric* provenance summaries (witness counts, derivation counts) whenever the relevant semiring homomorphism is $\Delta$-Lipschitz. For self-join-free conjunctive queries the elastic/residual sensitivity framework (Johnson–Near–Song, VLDB 2018) yields polynomially computable per-query bounds, giving error within polylog factors of smooth-sensitivity-optimal.

## 5. Lower Bound

Releasing exact how-provenance is impossible under any nontrivial DP guarantee: the presence/absence of a monomial in a polynomial reveals a single tuple's existence, an event with privacy loss $+\infty$. More quantitatively, **reconstruction / tracing attacks** (Dinur–Nissim 2003; Bun–Ullman–Vadhan) imply that releasing $\Theta(n)$ low-noise linear lineage statistics permits blatant reconstruction, forcing error $\Omega(\sqrt{n}/\varepsilon)$ on the worst-case explanation set. Queries with joins have global sensitivity that grows with the data (degree), giving an information-theoretic floor that no post-processing can beat.

## 6. The Gap

The gap is wide and structural, not merely constant-factor. We have tight bounds for *scalar* numeric provenance, but the central open question — **a finitely representable, semiring-correct provenance object releasable under DP** — has neither a positive construction nor a clean impossibility characterizing *which* lineage fragments are DP-releasable. Closing it likely requires a new "DP-stable" abstraction of provenance (perhaps coarsened polynomials, or lineage over $k$-anonymous super-tuples) plus matching lower bounds via fingerprinting codes.

## 7. Current Research (as of June 2026)

- DP explanation systems extending Scorpion/Smart-drilldown ideas with budget-aware predicate search *(frontier — verify)*.
- "Provenance-aware sensitivity analysis" connecting Green–Tannen semirings to elastic sensitivity (groups around Tannen at Penn, Near at U. Vermont, Machanavajjhala at Duke).
- Causal-DP overlap: using DP causality (Cuong/Salimi-style causal provenance) to release *why-not* explanations with formal guarantees *(frontier — verify)*.
- Tropical-semiring summaries as DP-friendly lineage sketches.

## 8. Future Work

- A taxonomy of which semirings admit bounded-sensitivity valuations.
- Mechanisms releasing *structure-preserving* coarsened provenance (which sources, not which tuples).
- Interactive lineage under per-analyst budget accounting and Rényi composition.
- Local-DP variants where sources self-report lineage.
- Lower bounds via fingerprinting tailored to provenance polynomials.

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** Dinur, Nissim. *Revealing Information While Preserving Privacy.* PODS 2003. — [DOI](https://doi.org/10.1145/773153.773173)
- **[SOTA]** Johnson, Near, Song. *Towards Practical Differential Privacy for SQL Queries.* VLDB 2018 (elastic sensitivity). — [DOI](https://doi.org/10.14778/3187009.3177733), [arXiv](https://arxiv.org/abs/1706.09479)
- **[SOTA]** Kotsogiannis et al. *PrivateSQL: A Differentially Private SQL Query Engine.* VLDB 2019. — [DOI](https://doi.org/10.14778/3342263.3342274)
- **[Survey]** Bun, Ullman, Vadhan. *Fingerprinting Codes and the Price of Approximate Differential Privacy.* SIAM J. Comput., 2018. — [DOI](https://doi.org/10.1137/15M1033587), [arXiv](https://arxiv.org/abs/1311.3158)

## 10. Worked Example

A hospital table `Patients(id, hasFluPos)` has $n=3$ rows. Query $Q$ counts flu-positive patients: answer $c = 2$. Its how-provenance is the polynomial $\Phi = x_1 + x_3$ (patients 1 and 3 contributed), where each $x_i$ is a source-tuple indeterminate.

**Why raw provenance leaks.** The monomial $x_3$ appears iff patient 3 is flu-positive. Releasing $\Phi$ on neighbor $D'$ (patient 3 removed) gives $\Phi'=x_1$. The two outputs are disjoint events, so $\Pr[M(D)=\Phi]/\Pr[M(D')=\Phi] = \infty$ — privacy loss is unbounded. No noise on the *structure* fixes this; releasing the polynomial is impossible under DP.

**What is releasable: the scalar count.** Apply the counting homomorphism $h:\mathbb{N}[X]\to\mathbb{N}$, $x_i\mapsto 1$, giving $h(\Phi)=c=2$. Per-tuple sensitivity is $\Delta=1$ (one patient flips the count by 1). The Laplace mechanism releases
$$\tilde c = c + \mathrm{Lap}(\Delta/\varepsilon) = 2 + \mathrm{Lap}(1/\varepsilon),$$
which is $(\varepsilon,0)$-DP with expected error $1/\varepsilon$. At $\varepsilon=1$ the noise std is $\sqrt 2\approx 1.41$ — useful for the aggregate, yet the per-patient lineage stays hidden. This is exactly the SOTA boundary: numeric provenance summaries are releasable; the polynomial is not.

---
*Part of the [DBMS Research catalog](../../README.md).*
