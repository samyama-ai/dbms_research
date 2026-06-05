# Rank Logic and Capturing PTIME via Linear Algebra

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/rank-logic-ptime` · **Status:** open

## 1. Problem Statement

Fixpoint logic with counting (FPC) fails to capture PTIME because of the **Cai–Fürer–Immerman (CFI)** queries, which are PTIME-decidable but encode a *parity/linear-algebra* obstacle FPC cannot see. **Rank logic** ($\mathrm{FP}{+}\mathrm{rk}$, Dawar–Grohe–Holm–Laubner 2009) augments fixpoint-with-counting by operators that compute the **rank of definable matrices over finite fields** $\mathbb{F}_p$ — exactly the algebraic information FPC lacks. The problem: **does FO/fixpoint logic plus rank operators (or related linear-algebraic operators) capture PTIME** on all finite structures? More broadly, which *algebraic* operator (rank over a fixed prime, rank over all primes, solvability of linear systems over arbitrary finite rings, invertible maps) — if any — yields a logic capturing P?

This is **open** in the strong sense that rank logic as originally defined has been *separated* from P (so it does **not** capture P), and the question is whether a richer algebraic extension does, or whether no such logic exists (Gurevich's conjecture).

## 2. Mathematical Foundations

Rank logic extends IFP+C with, for each prime $p$, a **rank operator** $\mathrm{rk}_p$: given a formula defining a matrix $M \in \mathbb{F}_p^{I \times J}$ indexed by definable index sets, $\mathrm{rk}_p$ returns $\mathrm{rank}_{\mathbb{F}_p}(M)$ as a number usable by counting machinery. Rank generalizes counting (the all-ones/identity patterns recover cardinalities) and **solves systems of linear equations over $\mathbb{F}_p$**, which is exactly the obstruction in CFI constructions.

Two natural variants matter:

- **$\mathrm{FP}{+}\mathrm{rk}_p$ for a single fixed $p$** — uniform rank over one field.
- **Full rank logic with $\mathrm{rk}_p$ for all $p$**, where the prime can itself be defined/quantified. Lichter's separation crucially concerns the **uniform** rank operator quantifying over primes vs. a single fixed prime — the original definition allowed a *fixed-arity* operator whose prime was a parameter, and the separation exploited CFI structures over $\mathbb{Z}/2^k\mathbb{Z}$ (rings, not fields).

Key inclusions: $\mathrm{FPC} \subsetneq \mathrm{FP}{+}\mathrm{rk} \subseteq \mathrm{P}$. Rank logic strictly exceeds FPC (it expresses the CFI query and solvability of $\mathbb{F}_p$-systems). Underlying tools: **Weisfeiler–Leman / pebble games**, **invertible-map equivalences** (the algebraic analog of WL), and **symmetric circuits** with majority/rank gates.

## 3. State of the Art (SOTA)

- **Rank logic strictly contains FPC** and expresses CFI queries, solvability of linear systems over $\mathbb{F}_p$, and many isomorphism problems that defeat counting (Dawar, Grohe, Holm, Laubner 2009; Holm's thesis 2010).
- **Rank logic does NOT capture P:** Moritz Lichter, *Separating rank logic from polynomial time* (LICS 2021; J. ACM 2023), built a PTIME query — a CFI-style construction over $\mathbb{Z}/2^k\mathbb{Z}$ — not definable in rank logic. This is the central SOTA result and closes one route.
- Beyond rank: **linear-algebraic logic / solvability logic** over arbitrary finite rings, and **invertible-map logic (IM)** are studied as stronger candidates; Dawar–Grädel–Pakusa, Grädel–Pakusa, Grohe–Pakusa relate them. None is known to capture P, and Lichter-style ideas threaten them too.

## 4. Upper Bound

By soundness, $\mathrm{FP}{+}\mathrm{rk} \subseteq \mathrm{PTIME}$: rank over $\mathbb{F}_p$ of a polynomial-size definable matrix is computable in PTIME (Gaussian elimination, $O(n^3)$), and the fixpoint converges in $n^{O(1)}$ stages, so every rank-logic query is PTIME. The same holds for solvability/invertible-map logics — all are *contained* in P. The open direction is the **completeness** (capturing) upper bound: no algorithmic argument is known that compiles every PTIME isomorphism-invariant query into rank (or extended-algebraic) operators; the canonization route that works for FPC on excluded-minor classes does not extend to all structures.

## 5. Lower Bound

- **Separation (the decisive lower bound):** rank logic $\subsetneq$ P (Lichter 2021) — there is a PTIME query no rank-logic sentence defines, via CFI graphs over $\mathbb{Z}/2^k\mathbb{Z}$ and an invertible-map / algebraic-pebble lower bound. This rules out rank logic as a capturing logic.
- **FPC $\subsetneq$ P** (Cai–Fürer–Immerman 1992) is inherited and motivates rank in the first place.
- For **stronger algebraic logics**, partial inexpressibility results exist (e.g., limits of $\mathrm{rk}_p$ for a single prime against multi-prime constructions); a general lower bound covering all linear-algebraic/solvability operators is **not** known — that absence is exactly why the overall problem stays open.

## 6. The Gap

The gap is qualitative. Rank logic was the most promising algebraic candidate to capture P; Lichter's separation **closed** the specific question (rank logic does not capture P) but **reopened** the general one: is there *any* algebraic-operator extension of fixpoint+counting that captures P, or does Gurevich's conjecture hold? Between the upper bound (everything algebraic stays inside P) and the lower bound (rank, and FPC, are strictly weaker), the open territory is **solvability/invertible-map logics over arbitrary finite rings** and **choiceless polynomial time** — none proven to capture P, none yet separated. Closing it needs either a new operator with a completeness proof or a uniform lower bound defeating all such operators.

## 7. Current Research (as of June 2026)

- **Post-Lichter linear-algebraic logics:** logics with solvability operators over **all finite rings**, and **invertible-map logic**, aiming to absorb the $\mathbb{Z}/2^k\mathbb{Z}$ obstruction; whether these capture P or are themselves separable is actively studied (Lichter, Dawar, Grädel, Pakusa, Schweitzer) *(frontier — verify)*.
- **CFI constructions over richer algebraic structures** (non-abelian groups, modules) as a uniform lower-bound generator against algebraic logics *(frontier — verify)*.
- **Symmetric circuits with rank/algebraic gates** and their lower bounds (Dawar, Wilsenach).
- Relating rank/algebraic logics to the **Weisfeiler–Leman hierarchy** and to **graph isomorphism** algorithms.
- Groups: TU Darmstadt/Berlin (Lichter, Schweitzer), RWTH Aachen (Grädel, Grohe, Pakusa), Cambridge (Dawar).

## 8. Future Work

- Determine whether **solvability logic over all finite rings** or **invertible-map logic** captures P, or extend Lichter's method to separate them.
- Seek a **canonical algebraic operator** subsuming counting, rank, and solvability with a completeness theorem on broad structure classes.
- Establish a **lower-bound barrier** clarifying whether any effective algebraic logic can capture P (toward or against Gurevich's conjecture).
- Connect these logics to **practical isomorphism/canonical-form** algorithms.

## 9. Key References

- **[Foundational]** A. Dawar, M. Grohe, B. Holm, B. Laubner. *Logics with rank operators.* LICS 2009.
- **[Foundational]** B. Holm. *Descriptive Complexity of Linear Algebra.* PhD thesis, University of Cambridge, 2010.
- **[SOTA]** M. Lichter. *Separating rank logic from polynomial time.* LICS 2021 / J. ACM, 2023.
- **[Foundational]** J.-Y. Cai, M. Fürer, N. Immerman. *An optimal lower bound on the number of variables for graph identification.* Combinatorica, 1992.
- **[SOTA]** A. Dawar, E. Grädel, W. Pakusa. *Approximations of isomorphism and logics with linear-algebraic operators.* ICALP 2019.
- **[Survey]** M. Grohe. *Descriptive Complexity, Canonisation, and Definable Graph Structure Theory.* Cambridge Univ. Press, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
