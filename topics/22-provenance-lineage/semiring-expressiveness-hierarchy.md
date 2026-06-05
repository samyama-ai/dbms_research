# Semiring Expressiveness Hierarchy

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/semiring-expressiveness-hierarchy` · **Status:** open

## 1. Problem Statement
Green, Karvounarakis, and Tannen (PODS 2007) showed that annotating tuples with elements of a commutative semiring $(K, +, \cdot, 0, 1)$ and propagating those annotations through positive relational algebra ($\mathrm{RA}^+$) uniformly captures many provenance and data models: set semantics ($\mathbb{B}$), bag/multiplicity semantics ($\mathbb{N}$), probabilistic event tables, access-control lattices, the tropical/cost semiring, and others. The **free** object in this picture is the semiring of provenance polynomials $\mathbb{N}[X]$ over indeterminates $X$ (one per source tuple): every other instantiation is the image of $\mathbb{N}[X]$ under a unique semiring homomorphism.

The open problem is to **characterize exactly the expressiveness hierarchy** induced by this homomorphism picture. Concretely: (a) Given two provenance questions $Q_1, Q_2$ (each a property of the polynomial annotating an answer), when can $Q_1$ be answered from the value of $Q_2$ — i.e., when does a homomorphism collapse distinctions that one question needs but another does not? (b) Produce a *complete lattice/poset* of provenance semirings ordered by "refines" (factors through a surjective homomorphism), with crisp separating examples at every covering edge. (c) Decide, for a given finite semiring or variety, which $\mathrm{RA}^+$-definable provenance queries it can and cannot distinguish. Variants: a *decision* form (can $K_1$ answer everything $K_2$ can?), a *counting* form (how many polynomials collapse), and a *definability* form (axiomatize the collapse).

## 2. Mathematical Foundations
Annotated relations are functions $R: \mathrm{Tup} \to K$ with finite support. $\mathrm{RA}^+$ operators map to semiring operations: union/projection use $+$ (alternative derivations), join/selection use $\cdot$ (joint use). The fundamental theorem: for any commutative semiring $K$ and valuation $\nu: X \to K$, evaluation of $Q$ in $K$ equals $\hat\nu(\text{Prov}_{\mathbb{N}[X]}(Q))$, where $\hat\nu$ is the induced homomorphism. Thus $\mathbb{N}[X]$ is **free** on $X$ in the category of commutative semirings, and the expressiveness order is the lattice of congruences on $\mathbb{N}[X]$ that are *uniform* (respect $\mathrm{RA}^+$).

Key landmarks already known: $\mathbb{B}$ (which-provenance) is the most lossy; $\mathrm{PosBool}(X)$ (positive Boolean, = why-provenance via minimal witnesses) sits above it; the dual-poly $\mathrm{Trio}(X)$ (lineage with duplicate-insensitive coefficients) and Sorp/security semirings form intermediate strata; $\mathbb{N}[X]$ (how-provenance) is the top. Formally these relate by homomorphisms $\mathbb{N}[X] \twoheadrightarrow \mathrm{Trio}(X) \twoheadrightarrow \mathrm{PosBool}(X) \twoheadrightarrow \mathbb{B}$. The hard part is the *interior*: $m$-semirings, $\omega$-continuous semirings (for recursion), and semirings with monus.

## 3. State of the Art (SOTA)
Theory-SOTA is the original Green–Karvounarakis–Tannen framework plus Green's "Containment of Conjunctive Queries on Annotated Relations" (ICDT 2009, *Theory of Computing Systems* 2011), which settles when query containment over $K$-relations holds and shows it depends sharply on the semiring (e.g., containment over $\mathbb{N}$ vs. over $\mathbb{B}$ differ). Amsterdamer–Deutch–Tannen extended the picture to aggregates; Geerts–Poggi characterized which semirings are "positive" enough. The most complete map to date is in the survey chapter by Green and Tannen, *The Semiring Framework for Database Provenance* (PODS 2017 tutorial / *Foundations and Trends* style summary). Systems-SOTA: Orchestra, ProvSQL (Senellart et al., VLDB 2018), and GProM (Arab et al.) implement specific semirings but do not expose the hierarchy itself.

## 4. Upper Bound
For *finite* commutative semirings, deciding whether $K_1$'s provenance refines $K_2$'s on a fixed query reduces to checking a finite set of polynomial identities; this is decidable, in PSPACE via congruence-closure over the term algebra. For conjunctive queries, evaluating provenance in $\mathbb{N}[X]$ is in the same data complexity as evaluation (PTIME, $\mathrm{AC}^0$ for fixed CQ), and any homomorphic image is computed in linear time in the polynomial size. Containment over $K$ for CQs is decidable (Green 2011), NP-complete in query size for many semirings.

## 5. Lower Bound
CQ containment over $K$-relations is **NP-hard** in query size (it generalizes classical CQ containment / homomorphism, which is NP-complete). For bag semantics ($\mathbb{N}$), CQ *equivalence* is graph-isomorphism-complete and containment's decidability was a long-standing open question (still not fully resolved in general). Separating two semirings in the hierarchy requires exhibiting queries whose polynomials collapse under one homomorphism but not the other; lower bounds on the *size* of such separating witnesses are not known and there is no proven general method, which is part of why the full hierarchy is open. Information-theoretically, $\mathbb{B}$ loses $\Omega(\log)$ bits per distinct monomial relative to $\mathbb{N}[X]$.

## 6. The Gap
The endpoints and a handful of named strata are understood, but the **interior lattice is genuinely open**: there is no complete classification of which uniform congruences on $\mathbb{N}[X]$ are realizable, no general separating-witness theorem, and the bag-semantics containment question that underpins comparing $\mathbb{N}$-relations remains undecided in full generality. Closing the gap would require either a decidability result (or undecidability proof) for $\mathbb{N}$-containment and a structural theorem classifying provenance-preserving homomorphisms.

## 7. Current Research (as of June 2026)
Tannen's group (Penn) and the ProvSQL group (Senellart, Inria/ENS) continue mapping semirings useful for security and probability. Work on *semiring provenance for logic* (Grädel–Tannen, "Semiring Provenance for First-Order Model Checking") has pushed the framework into model theory and reopened expressiveness questions via games and absorptive/$\omega$-continuous semirings. Active threads: (i) provenance semirings for fixed-point logics and their congruence lattices; (ii) *(frontier — verify)* claimed partial classifications of finite commutative-semiring varieties by provenance-distinguishability; (iii) connections to weighted automata expressiveness. Grädel, Tannen, Dannert, and Naaf are central names.

## 8. Future Work
Articulated directions: a Galois-connection-style "which provenance question ↔ which semiring quotient" duality; a decidability resolution for $\mathbb{N}$-containment; an effective procedure that, given a provenance question expressed in a logic, returns the *coarsest* sufficient semiring; and lifting the hierarchy to recursive/aggregate settings where $\omega$-continuity and monus interact.

## 9. Key References
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007.
- **[Foundational]** T. J. Green. *Containment of Conjunctive Queries on Annotated Relations.* ICDT 2009 / Theory of Computing Systems, 2011.
- **[Survey]** T. J. Green, V. Tannen. *The Semiring Framework for Database Provenance.* PODS (tutorial), 2017.
- **[SOTA]** E. Grädel, V. Tannen. *Semiring Provenance for First-Order Model Checking.* arXiv:1712.01980, 2017.
- **[SOTA]** P. Senellart, L. Jachiet, S. Maniu, Y. Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
