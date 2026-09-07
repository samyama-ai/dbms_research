---
id: 25-query-languages-expressiveness/logic-capturing-ptime
title: "A Logic Capturing PTIME on Unordered Structures"
topic: 25-query-languages-expressiveness
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# A Logic Capturing PTIME on Unordered Structures

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/logic-capturing-ptime` · **Status:** open

## 1. Problem Statement

Is there a logic that captures exactly the polynomial-time (PTIME) computable queries on arbitrary finite structures? A query is a class of finite structures closed under isomorphism (an isomorphism-invariant property); it is in PTIME if some Turing machine, given any reasonable encoding of the input structure, decides membership in time polynomial in the size of the structure. We seek a logic $L$ such that:

- (**Soundness**) every $L$-definable query is computable in PTIME, and
- (**Completeness**) every PTIME query is $L$-definable;

together with the **effectivity** requirement (Gurevich) that $L$ has a decidable/recursively enumerable syntax and an effective semantics. This is *Gurevich's Conjecture*: **no such logic exists**. The decision/structural question is whether the conjecture holds, and equivalently whether $\mathrm{P} = \mathrm{NP}$ or related separations are entangled with it. The problem is open in both directions: no logic capturing PTIME on unordered structures is known, and no proof that none exists is known.

## 2. Mathematical Foundations

The framework is **descriptive complexity** over finite relational structures $\mathfrak{A} = (A, R_1^{\mathfrak{A}}, \dots)$. Key landmarks:

- **Fagin's theorem (1974):** existential second-order logic captures NP: $\mathrm{ESO} = \mathrm{NP}$.
- **Immerman–Vardi theorem (1982/86):** on **ordered** structures, least-fixpoint logic captures PTIME: $\mathrm{FO}{+}\mathrm{LFP} = \mathrm{P}$ (also $\mathrm{P} = \mathrm{FO}{+}\mathrm{IFP}$). Order is essential: a linear order on the universe is available as a built-in relation.

The difficulty is *order-invariance*. Without a built-in order, fixpoint logic cannot even express that a structure has an even number of elements (**parity**). The canonical separators:

- $\mathrm{FO}{+}\mathrm{LFP} \subsetneq \mathrm{P}$ on unordered structures (counting is missing).
- **FPC** (fixpoint logic with counting, Immerman): adds counting quantifiers $\exists^{\geq i}$. FPC captures PTIME on many natural classes but **does not capture PTIME in general** — Cai–Fürer–Immerman (1992) built PTIME-decidable graphs (CFI graphs) distinguished by no FPC sentence, via a connection to the Weisfeiler–Leman algorithm and the $k$-pebble bijective game.

A logic capturing PTIME would yield a recursive enumeration of all PTIME queries with a corresponding effective "P-machine," which is itself a deep, possibly impossible, object. Gurevich noted such a logic existing would imply a "normal form" for PTIME isomorphism-invariant computation.

## 3. State of the Art (SOTA)

No candidate logic is known to capture PTIME on all finite structures. The strongest **positive** results capture PTIME on restricted classes:

- **FP + Counting (FPC)** captures PTIME on graph classes with **excluded minors** (Grohe, 2010, culminating in *Descriptive Complexity, Canonisation, and Definable Graph Structure Theory*, 2017) — including planar graphs and bounded-genus graphs.
- **Choiceless Polynomial Time (CPT)** with counting (Blass–Gurevich–Shelah, 1999) is the leading *candidate* for the general case: a model of computation manipulating hereditarily finite sets symmetrically. CPT can solve the CFI query (Dawar–Richerby–Rossman) and many problems FPC cannot, and no PTIME problem is yet proven outside CPT.

## 4. Upper Bound

By soundness, all candidate logics ($\mathrm{FP}$, $\mathrm{FPC}$, CPT, rank logic) are contained in PTIME — that is the easy inclusion. The *capturing* upper bound (algorithmic side) is the **canonization** route: if a class $\mathcal{C}$ admits a PTIME *canonical form* computable in an order-invariant way, then $\mathrm{FPC}$ (or the relevant logic) captures PTIME on $\mathcal{C}$. Grohe's structure theory gives FPC-canonization for all graph classes with an excluded minor and, more recently, bounded rank-width / clique-width frontiers *(frontier — verify)*. The CPT upper bound for the CFI query is $n^{O(1)}$ via symmetric set computation.

## 5. Lower Bound

The central inexpressibility (lower) bound: **FPC does not capture PTIME** (Cai–Fürer–Immerman 1992) — there are PTIME queries definable by no FPC formula, proven via Weisfeiler–Leman / pebble-game lower bounds. **Rank logic** ($\mathrm{FP}{+}\mathrm{rk}$) was also shown **not** to capture PTIME (Lichter, 2021, *Separating rank logic from polynomial time*, LICS 2021 / J. ACM) — a CFI-style construction over rings $\mathbb{Z}/2^k\mathbb{Z}$ defeats all rank operators. No unconditional lower bound rules out CPT or a future logic. A proof that *no* effective logic captures PTIME (Gurevich's conjecture) would be a meta-lower-bound; none exists.

## 6. The Gap

The gap is foundational, not numerical: we lack either (a) a logic proven to capture all of PTIME, or (b) a proof that none can exist. Every concrete candidate has either been separated (FPC, rank logic) or remains a candidate with neither completeness nor a separation (CPT). Closing it requires either constructing an effective logic with a matching syntax/semantics for PTIME, or proving Gurevich's conjecture — likely demanding new lower-bound machinery beyond pebble games and the symmetric-circuit/Weisfeiler–Leman toolkit.

## 7. Current Research (as of June 2026)

- **Choiceless Polynomial Time** is the active frontier: separating CPT from PTIME, or showing CPT captures PTIME, via symmetric circuits and group-theoretic CFI variants (Dawar, Pakusa, Lichter, Schweitzer). Recent work studies CPT on CFI graphs over non-abelian groups *(frontier — verify)*.
- **Symmetric and circuit lower bounds**: Anderson–Dawar's correspondence between FPC and symmetric circuits drives new inexpressibility results; extensions to counting/linear-algebraic gates are active *(frontier — verify)*.
- **Logics with linear-algebraic operators** beyond rank (e.g., operators over varied rings, "invertible-map" logics) are explored to climb past Lichter's separation (Dawar, Grädel, Pakusa, Lichter, Grohe).
- Groups: Cambridge (Dawar), RWTH Aachen (Grädel, Grohe, Pakusa), TU Darmstadt/Berlin (Schweitzer, Lichter).

## 8. Future Work

- Resolve whether **CPT(+counting)** captures PTIME or is separable.
- Develop a **uniform lower-bound method** for arbitrary symmetric/choiceless models (a "natural proofs"-style barrier or its absence).
- Pin the exact place of **graph isomorphism** and **Weisfeiler–Leman dimension** in this hierarchy.
- Settle whether order-invariance over richer algebraic operators (solvability of linear systems over all finite rings) suffices.

## 9. Key References

- **[Foundational]** Y. Gurevich. *Logic and the challenge of computer science.* In Current Trends in Theoretical Computer Science, 1988. (States the conjecture.) — [DBLP search](https://dblp.org/search?q=Gurevich+Logic+and+the+challenge+of+computer+science)
- **[Foundational]** N. Immerman. *Relational queries computable in polynomial time.* Information and Control, 1986. / M. Vardi, STOC 1982. — [DOI](https://doi.org/10.1016/S0019-9958(86)80029-8) — [DBLP](https://dblp.org/rec/journals/iandc/Immerman86.html)
- **[Foundational]** J.-Y. Cai, M. Fürer, N. Immerman. *An optimal lower bound on the number of variables for graph identification.* Combinatorica, 1992. — [DOI](https://doi.org/10.1007/BF01305232) — [PDF](https://people.cs.umass.edu/~immerman/pub/opt.pdf)
- **[SOTA]** M. Grohe. *Descriptive Complexity, Canonisation, and Definable Graph Structure Theory.* Cambridge University Press, 2017. — [DOI](https://doi.org/10.1017/9781139028868)
- **[SOTA]** M. Lichter. *Separating rank logic from polynomial time.* LICS 2021 (J. ACM 2023). — [arXiv](https://arxiv.org/abs/2104.12999) — [DOI](https://doi.org/10.1145/3572918)
- **[Foundational]** A. Blass, Y. Gurevich, S. Shelah. *Choiceless polynomial time.* Annals of Pure and Applied Logic, 1999. — [DOI](https://doi.org/10.1016/S0168-0072(99)00005-6) — [PDF](https://web.eecs.umich.edu/~gurevich/Opera/120.pdf)
- **[Survey]** A. Dawar. *The nature and power of fixed-point logic with counting.* ACM SIGLOG News, 2015. — [DOI](https://doi.org/10.1145/2728816.2728820)

## 10. Worked Example

Why order matters, in miniature. Consider the query EVEN: "does the input structure have an even number of elements?" Take two bare sets (no relations) $A=\{1,2\}$ and $B=\{1,2,3\}$ — sizes 2 and 3.

EVEN is trivially in PTIME (count the elements). But it is **not** expressible in $\mathrm{FO}{+}\mathrm{LFP}$ on *unordered* structures: a fixpoint formula's truth depends only on the isomorphism type, and with no relations to fix on, the only invariant FO can extract from a bare set is its size *modulo the quantifier rank's reach* — captured exactly by the $k$-pebble Ehrenfeucht–Fraïssé game. For any fixed formula of quantifier rank $k$, Duplicator wins the $k$-pebble game between *any* two sufficiently large sets, so the formula cannot separate even-sized from odd-sized universes.

Add a built-in linear order $1<2<3$ and the obstruction vanishes: "the maximum element is at an even position" is now FO-definable, and Immerman–Vardi gives $\mathrm{FO}{+}\mathrm{LFP}=\mathrm{P}$. This single example — a 2-element vs. 3-element set — is the seed of the whole field: counting/parity is the first thing plain fixpoint logic loses without order, which is why FPC adds counting quantifiers $\exists^{\ge i}$, and why CFI graphs (which defeat even FPC) are needed to push the separation further.

---
*Part of the [DBMS Research catalog](../../README.md).*
