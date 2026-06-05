# Provenance for Full Relational Algebra

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-difference-negation` · **Status:** partially-solved

## 1. Problem Statement
The semiring framework (Green–Karvounarakis–Tannen 2007) elegantly handles **positive** relational algebra, but $\mathrm{RA}^+$ excludes set **difference** ($R - S$), and by extension relational **negation** and the universal/division operators. The obstacle is structural: a commutative semiring has no inverse for $+$, so "tuple $t$ is in $R$ but *not* in $S$" has no canonical algebraic counterpart. Naively adding subtraction breaks the homomorphism property — different but semantically-equivalent query plans yield different annotations, and instantiation to particular semirings (probabilities, bag counts) becomes ill-defined.

The problem is to define a provenance model for **full relational algebra (with difference and negation)** that is (a) *sound* — annotations are invariant under semantically equivalent rewrites; (b) *commutes with homomorphisms* so it still specializes to bags, sets, probabilities, access control; (c) *informative* — it records *why a tuple is absent* (negative provenance) not just present. Variants: an algebraic-structure variant (which structure replaces the semiring?), a complexity variant (cost of evaluating negative provenance), and an applications variant (how-provenance for deletion propagation and view maintenance under difference).

## 2. Mathematical Foundations
Two main algebraic responses exist. (1) **Semirings with monus** ($m$-semirings): equip $K$ with a partial "truncated subtraction" $a \ominus b$ satisfying Geerts–Poggi's axioms ($a \ominus b$ is the least $c$ with $b + c \ge a$ under the natural order $a \le b \iff \exists c.\, a+c=b$). This works only when $K$ is *naturally ordered*; $\mathbb{N}$ becomes $a \ominus b = \max(a-b,0)$, and the free $m$-semiring is built from polynomials over a monus. (2) **Provenance for full FO via dual-indeterminate semirings**: Grädel–Tannen's *transformed* semirings use *two* sets of indeterminates — positive ($p$) and negative ($\bar p$) — with an involution, so negation swaps roles; this yields well-defined provenance for *all* of first-order logic, interpreting $\forall/\exists$ as $\prod/\sum$ and $\neg$ via the dual. The key technical demand is **idempotence/absorption** conditions ensuring soundness under the laws of FO (double negation, distributivity).

Formally, soundness means: if $Q \equiv Q'$ as RA expressions then $\text{Prov}(Q) = \text{Prov}(Q')$ in the chosen structure. For monus this fails for some equivalences (monus is not fully compatible with all RA identities), which is the crux of "partially solved."

## 3. State of the Art (SOTA)
Geerts–Poggi, *On Database Query Languages for K-Relations* (J. Applied Logic, 2010) introduced $m$-semirings and characterized when difference is well-behaved. Amsterdamer–Deutch–Tannen (PODS 2011) extended provenance with monus and exposed its limits. The most complete *full-FO* treatment is Grädel–Tannen's semiring provenance for first-order model checking (2017+) and Dannert–Grädel–Naaf–Tannen, *Semiring Provenance for Fixed-Point Logic* (CSL 2021), which handle negation via *dual-indeterminate, absorptive, $\omega$-continuous* semirings. Systems-SOTA: GProM (Arab–Glavic et al.) computes provenance for queries with difference using a *Perm/sufficient-witness* rewriting; ProvSQL supports $m$-semirings for the monotone fragment and approximates negation.

## 4. Upper Bound
For RA-with-difference under $m$-semirings, provenance is computed by a single annotated pass over the query plan: data complexity stays PTIME ($\mathrm{AC}^0$ for fixed queries), with each $\ominus$ a constant-time semiring op. For full-FO dual-indeterminate provenance, computing the provenance value of a fixed FO sentence over a structure of size $n$ is in PTIME data complexity; the provenance *polynomial* can have exponential size in the number of variables/quantifier alternations, but evaluation under a concrete absorptive semiring stays polynomial.

## 5. Lower Bound
Soundness has an inherent *impossibility flavor*: no commutative semiring without additional structure can support a difference operator that commutes with all homomorphisms (this is essentially algebraic — $+$ has no inverse). For full FO, deciding equivalence of provenance expressions is at least as hard as FO equivalence (undecidable in general). For negative why-provenance, identifying minimal *causes* of a tuple's absence is **coNP-hard** / connects to abductive reasoning and to the $\Sigma_2^p$ minimal-diagnosis problems. View-update/deletion-propagation under difference is NP-hard (Buneman–Khanna–Tan side-effect-free deletion).

## 6. The Gap
We have *two* sound models for restricted regimes (naturally-ordered $m$-semirings; absorptive dual-indeterminate semirings for FO), but **no single structure that is simultaneously sound for all RA-with-difference, fully homomorphism-commuting, and specializing correctly to ordinary bag counts and probabilities**. The $m$-semiring approach sacrifices some RA equivalences; the FO approach requires absorption that collapses multiplicities (losing bag semantics). Closing the gap means either an impossibility theorem showing no such universal structure exists, or a new algebraic object that reconciles monus with multiplicity tracking.

## 7. Current Research (as of June 2026)
Grädel's Aachen group and Tannen (Penn) are extending dual-indeterminate provenance from FO to fixed-point and modal logics. *(frontier — verify)* recent work explores provenance for **SQL's three-valued NULL logic** and for negation in Datalog$^\neg$ under stable/well-founded semantics, where negative provenance must respect non-monotone fixpoints. Glavic's group (IIT) pushes practical negative provenance (the "why-not"/missing-answer line, Chapman–Jagadish, Herschel) into systems. Active question: a clean compositional account of *why-not* that coincides with the algebraic negative provenance.

## 8. Future Work
Open directions: a universal sound structure or its impossibility; reconciling monus with aggregation; provenance for SQL NULLs; scalable negative/why-not provenance with ranked minimal explanations; and integrating negation-provenance into incremental view maintenance and data repair.

## 9. Key References
- **[Foundational]** F. Geerts, A. Poggi. *On Database Query Languages for K-Relations.* J. Applied Logic, 2010.
- **[Foundational]** Y. Amsterdamer, D. Deutch, V. Tannen. *Provenance for Aggregate Queries.* PODS, 2011.
- **[SOTA]** K. Dannert, E. Grädel, M. Naaf, V. Tannen. *Semiring Provenance for Fixed-Point Logic.* CSL, 2021.
- **[SOTA]** B. Glavic, R. J. Miller, et al. *Reexamining Some Holy Grails of Data Provenance.* TaPP, 2013.
- **[Survey]** A. Chapman, H. V. Jagadish. *Why Not? (Explaining Missing Answers).* SIGMOD, 2009.

---
*Part of the [DBMS Research catalog](../../README.md).*
