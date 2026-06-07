---
id: 25-query-languages-expressiveness/fixpoint-logic-capture
title: "Choice of Fixpoint Operator for Capturing Classes"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Choice of Fixpoint Operator for Capturing Classes

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/fixpoint-logic-capture` · **Status:** partially-solved
> **Verification note:** In §10 the parenthetical "(8 vertices each split appropriately)" is imprecise about vertex counts; the substantive claim — parity is not expressible in FO+IFP on unordered structures — is correct.

## 1. Problem Statement

First-order logic (FO) over finite structures captures the "static" queries but no recursion. Many operators extend FO with recursion/closure: **least fixpoint (LFP)**, **inflationary fixpoint (IFP)**, **partial fixpoint (PFP)**, **transitive closure (TC)**, **deterministic transitive closure (DTC)**, and counting variants (FPC). The problem: **determine which fixpoint/closure extension of FO captures which complexity class**, separately on **ordered** structures (where a linear order is built in) and **unordered** structures (isomorphism-invariant queries). The decision/structural question is to settle all the capture equalities and separations:

$$\mathrm{FO}{+}\mathrm{DTC} \stackrel{?}{=} \mathrm{L},\quad \mathrm{FO}{+}\mathrm{TC} \stackrel{?}{=} \mathrm{NL},\quad \mathrm{FO}{+}\mathrm{LFP} = \mathrm{FO}{+}\mathrm{IFP} \stackrel{?}{=} \mathrm{P},\quad \mathrm{FO}{+}\mathrm{PFP} \stackrel{?}{=} \mathrm{PSPACE}.$$

It is **partially solved**: all equalities are theorems **on ordered structures**; on **unordered** structures they fail (and capturing the classes is open, intertwined with Gurevich's conjecture and with L vs NL vs P).

## 2. Mathematical Foundations

For a formula $\varphi(R, \bar{x})$ positive in relation variable $R$, the **least fixpoint** operator forms $[\mathrm{lfp}_{R,\bar x}\,\varphi]$, the least $R$ with $R = \{\bar a : \varphi(R,\bar a)\}$ (exists by monotonicity, Knaster–Tarski). **IFP** drops the positivity requirement using the inflationary iteration $R^{i+1} = R^i \cup \{\bar a : \varphi(R^i,\bar a)\}$. **PFP** iterates without inflation and takes the fixpoint if reached (else empty), giving a PSPACE-bounded operator. **TC** forms the reflexive-transitive closure of an FO-definable binary relation; **DTC** of its deterministic part.

Capture theorems (**ordered** finite structures with built-in $\leq, +, \times$):

- **Immerman:** $\mathrm{FO}{+}\mathrm{DTC} = \mathrm{LOGSPACE}$, $\mathrm{FO}{+}\mathrm{TC} = \mathrm{NLOGSPACE}$ (1987–88).
- **Immerman–Vardi:** $\mathrm{FO}{+}\mathrm{LFP} = \mathrm{FO}{+}\mathrm{IFP} = \mathrm{PTIME}$ (1982/86).
- **Abiteboul–Vianu / Vardi:** $\mathrm{FO}{+}\mathrm{PFP} = \mathrm{PSPACE}$ on ordered structures.

Two foundational structural facts: **(Gurevich–Shelah 1986)** LFP = IFP in expressive power on all finite structures; **(Abiteboul–Vianu 1991)** $\mathrm{IFP} = \mathrm{PFP}$ (as logics, without order) **iff** $\mathrm{P} = \mathrm{PSPACE}$ — directly tying a logic question to a complexity separation.

## 3. State of the Art (SOTA)

- On **ordered** structures the picture is **complete and tight**: DTC↔L, TC↔NL, LFP/IFP↔P, PFP↔PSPACE.
- On **unordered** structures, none of these logics captures its class: e.g., $\mathrm{FO}{+}\mathrm{IFP}$ cannot express **parity**, hence $\mathrm{FO}{+}\mathrm{IFP} \subsetneq \mathrm{P}$ (Cai–Fürer–Immerman strengthen this even with counting: **FPC $\subsetneq$ P**).
- **FPC** (IFP + counting quantifiers) is the strongest well-behaved logic: captures P on bounded-treewidth, planar, excluded-minor classes (Grohe 2017) but not in general.
- **Separations among operators without order:** $\mathrm{TC} \subsetneq \mathrm{LFP}$, $\mathrm{DTC} \subsetneq \mathrm{TC}$ are known unconditionally on unordered structures; many were established via Ehrenfeucht–Fraïssé / pebble games.

## 4. Upper Bound

Each capture is an *inclusion both ways*; the algorithmic upper bound is the easy direction: every formula of the logic evaluates within the target class. E.g., an $\mathrm{FO}{+}\mathrm{TC}$ query evaluates in **NLOGSPACE** (guess-and-check reachability over the FO-defined graph of polynomial size); $\mathrm{FO}{+}\mathrm{IFP}$ in **PTIME** (fixpoint reached in $\leq n^k$ stages, each FO-evaluable in PTIME); $\mathrm{FO}{+}\mathrm{PFP}$ in **PSPACE** (iteration uses only polynomial space, $2^{n^{O(1)}}$ steps tracked by a counter). FPC adds counting quantifiers evaluable in PTIME. These upper bounds hold in the standard RAM/Turing model with the structure given by an encoding.

## 5. Lower Bound

- **Completeness/hardness** giving the matching lower bound on ordered structures: $\mathrm{FO}{+}\mathrm{TC}$ expresses an NL-complete problem (directed reachability, $\mathrm{STCON}$); $\mathrm{FO}{+}\mathrm{LFP}$ expresses a P-complete problem; so the logics are as hard as their class.
- **Inexpressibility (separation) lower bounds on unordered structures:** parity is not in $\mathrm{FO}{+}\mathrm{IFP}$; **CFI graphs** are not separated by FPC (Cai–Fürer–Immerman 1992); rank logic $\subsetneq$ P (Lichter 2021). These are unconditional, via pebble games / Weisfeiler–Leman.
- **Conditional bound:** $\mathrm{IFP} = \mathrm{PFP}$ (no order) $\iff \mathrm{P}=\mathrm{PSPACE}$ (Abiteboul–Vianu) — a fine-grained logic↔complexity equivalence.

## 6. The Gap

On **ordered** structures, the gap is **closed**: every listed capture is a theorem. The genuinely open part lives **without order**:

1. Whether *any* logic captures P/NL/L on unordered structures (the L, NL, P capturing problems — open, and the P case is Gurevich's conjecture).
2. The unordered logic separations mirror unresolved complexity separations: $\mathrm{FO}{+}\mathrm{DTC}$ vs $\mathrm{FO}{+}\mathrm{TC}$ relates to L vs NL; $\mathrm{IFP}$ vs $\mathrm{PFP}$ to P vs PSPACE. Closing these would resolve major open problems in complexity, so progress is via *order-free* capturing logics (FPC, rank logic, CPT) rather than direct separation.

## 7. Current Research (as of June 2026)

- **Linear-algebraic fixpoint operators** beyond counting and rank — invertible-map logics, operators for solvability of linear systems over arbitrary finite rings — chasing a capture of P past Lichter's rank-logic separation (Dawar, Grädel, Grohe, Pakusa, Lichter) *(frontier — verify)*.
- **Symmetric-circuit characterizations** of FPC/rank logic to push inexpressibility (Anderson, Dawar; Dawar–Wilsenach) *(frontier — verify)*.
- **Capturing P on further graph classes** (bounded rank-width, bounded clique-width, hereditary classes) by FPC via definable canonization (Grohe, Neuen, Schweitzer).
- Counting/fixpoint logics for **probabilistic/quantitative** query languages and their capture results.

## 8. Future Work

- Find a single fixpoint+algebraic operator capturing P on all structures, or prove none does.
- Settle the **DTC/TC/LFP/PFP** unordered separations independent of (or jointly with) L/NL/P/PSPACE.
- Extend tight capture theorems to **richer logics with aggregation** matching real query languages.

## 9. Key References

- **[Foundational]** N. Immerman. *Languages that capture complexity classes.* SIAM J. Computing, 1987 (DTC↔L, TC↔NL). — [DOI](https://doi.org/10.1137/0216051)
- **[Foundational]** N. Immerman. *Relational queries computable in polynomial time.* Inf. & Control, 1986 / M. Vardi, STOC 1982 (LFP/IFP↔P). — [DOI](https://doi.org/10.1016/S0019-9958(86)80029-8)
- **[Foundational]** S. Abiteboul, V. Vianu. *Generic computation and its complexity.* STOC 1991 (IFP=PFP ⇔ P=PSPACE; PFP↔PSPACE). — [ACM](https://doi.org/10.1145/103418.103444)
- **[Foundational]** Y. Gurevich, S. Shelah. *Fixed-point extensions of first-order logic.* Annals of Pure and Applied Logic, 1986 (LFP = IFP). — [DOI](https://doi.org/10.1016/0168-0072(86)90055-2)
- **[Foundational]** J.-Y. Cai, M. Fürer, N. Immerman. *An optimal lower bound on the number of variables for graph identification.* Combinatorica, 1992. — [DOI](https://doi.org/10.1007/BF01305232)
- **[Survey]** N. Immerman. *Descriptive Complexity.* Springer, 1999. — [DOI](https://doi.org/10.1007/978-1-4612-0539-5)
- **[SOTA]** M. Grohe. *Descriptive Complexity, Canonisation, and Definable Graph Structure Theory.* Cambridge Univ. Press, 2017. — [DOI](https://doi.org/10.1017/9781139028868)

## 10. Worked Example

**Transitive closure via LFP.** Let $E$ be a binary edge relation. Define reachability by the LFP formula
$$T(x,y) \equiv [\mathrm{lfp}_{R,(x,y)}\;\; E(x,y)\;\vee\;\exists z\,(E(x,z)\wedge R(z,y))](x,y).$$
The body is positive in $R$, so iteration is monotone. On the path graph $1\to 2\to 3$:
- $R^0=\varnothing$;
- $R^1=\{(1,2),(2,3)\}$ (the $E$ disjunct);
- $R^2=R^1\cup\{(1,3)\}$ (now $E(1,2)\wedge R^1(2,3)$ fires);
- $R^3=R^2$ — fixpoint reached.

So $T=\{(1,2),(2,3),(1,3)\}$, computed in $\le n$ stages, each FO-evaluable in PTIME — witnessing $\mathrm{FO}{+}\mathrm{LFP}\subseteq\mathrm{P}$.

**Why order matters.** Consider the two unordered structures $A=$ a single 4-cycle and $B=$ two disjoint 2-cycles (8 vertices each split appropriately). With enough vertices these are $\equiv_k$-indistinguishable in $\mathrm{FO}{+}\mathrm{IFP}$ for any fixed iteration that cannot count, so **parity** ("is $|V|$ even?") escapes $\mathrm{FO}{+}\mathrm{IFP}$ — concretely placing it strictly below P on unordered structures, exactly the gap that a built-in linear order $\le$ would erase.

---
*Part of the [DBMS Research catalog](../../README.md).*
