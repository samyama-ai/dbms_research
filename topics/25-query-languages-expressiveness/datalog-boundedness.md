# Datalog Boundedness and Predicate Boundedness

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/datalog-boundedness` · **Status:** partially-solved

## 1. Problem Statement

A Datalog program is **bounded** if its least-fixpoint evaluation reaches a fixpoint after a constant number of iterations $k$ independent of the input database — equivalently, the recursive program is logically equivalent to a *non-recursive* Datalog program (a union of conjunctive queries, hence an $\mathrm{FO}$ query). The **boundedness problem** asks: given a Datalog program $P$ (and optionally a designated intensional predicate), decide whether $P$ is bounded. Variants:

- **Program boundedness** vs. **predicate boundedness** (boundedness of one intensional relation).
- **Uniform boundedness** (bounded over all databases) vs. boundedness relative to a class.
- By **program shape**: linear, single-rule (sirups), monadic (single recursive IDB of arity 1), guarded, frontier-guarded.

The decision variant is primary; the optimization side is "find the smallest $k$" (the *stage/closure ordinal*). The problem is **partially solved**: undecidable in general, decidable for important subclasses, with tight complexity for several.

## 2. Mathematical Foundations

A Datalog program $P$ over EDB schema $\sigma$ and IDB schema computes the least fixpoint $T_P^\infty$ of the immediate-consequence operator $T_P$, which is monotone, so $T_P^\infty = \bigcup_{i} T_P^i(\emptyset)$. Define the **stage** $\mathrm{stage}_P(D) = \min\{ i : T_P^i(D) = T_P^{i+1}(D)\}$. Then

$$P \text{ bounded} \iff \exists k\, \forall D : T_P^k(D) = T_P^{k+1}(D).$$

Boundedness is equivalent to the existence of an equivalent **non-recursive** (FO) program, by Naughton/Gaifman–Mairson–Sagiv–Vardi. Tools: the **expansion-tree / proof-tree** characterization (a fact is derivable iff some finite proof tree exists; boundedness means proof-tree depth is bounded), **containment of CQs** (homomorphism / the chase), and **automata over trees** for linear/monadic programs. The relationship $\mathrm{boundedness} \Rightarrow \mathrm{FO}\text{-definability}$ holds; the converse (FO-definable $\Rightarrow$ bounded) is *not* generally true but holds for important fragments.

## 3. State of the Art (SOTA)

- **General Datalog:** boundedness is **undecidable** (Gaifman, Mairson, Sagiv, Vardi, *Undecidable optimization problems for database logic programs*, JACM 1993).
- **Linear Datalog:** undecidable in general (same line of work), but decidable for several restrictions.
- **Monadic Datalog** (all IDBs arity $\leq 1$): boundedness is **decidable**, **2EXPTIME-complete** (Cosmadakis, Gaifman, Kanellakis, Vardi, STOC 1988; complexity refined by Benedikt et al.).
- **Single-rule programs (sirups):** decidability results for restricted forms (Vardi; Hillebrand–Kanellakis–Mairson–Vardi).
- **Guarded / frontier-guarded Datalog:** boundedness is **decidable** (Barceló, Berkholz, Murlak, Bourhis, Benedikt, ten Cate, Vanden Boom). For **(frontier-)guarded** Datalog, decidable in 2EXPTIME, tied to MSO over trees of bounded treewidth.

## 4. Upper Bound

Best-known *decidability* upper bounds for tractable-syntax fragments:

- **Monadic:** $2\mathrm{EXPTIME}$ (tree-automata emptiness on bounded-arity proof trees).
- **Frontier-guarded Datalog:** $2\mathrm{EXPTIME}$ via reduction to satisfiability/emptiness of automata on trees, exploiting bounded-treewidth model property (ten Cate–Segoufin; Barceló–Bourhis–Vanden Boom).
- When bounded, the equivalent non-recursive program can be exponential in $P$; the smallest $k$ can be exponential. For ordered/linear cases, sharper bounds exist.

## 5. Lower Bound

- **Undecidability** for general Datalog and for linear Datalog (Gaifman–Mairson–Sagiv–Vardi 1993) — by reduction from Turing-machine/Post correspondence-style encodings; this is the strongest possible negative bound.
- **2EXPTIME-hardness** for monadic and for frontier-guarded boundedness (matching the upper bound) — Benedikt, ten Cate, Colcombet, Vanden Boom, *The complexity of boundedness for guarded logics*, LICS 2015.
- For specific simple sirups, boundedness can already be NP-hard / PSPACE-hard depending on encoding.

## 6. The Gap

For the *general* problem the gap is closed in the strongest sense: **undecidable**, so no algorithm exists. The research gap is the *frontier of decidability* — precisely characterizing which syntactic restrictions (guardedness, linearity, arity bounds, sirup shape) flip boundedness from undecidable to decidable, and the exact complexity within decidable fragments. Several monadic/guarded cases are **tight** (2EXPTIME-complete). Open spots remain for intermediate classes (e.g., certain non-monadic linear or limited-recursion programs) where neither a decision procedure nor an undecidability proof is known.

## 7. Current Research (as of June 2026)

- **Boundedness of guarded and existential rules (tuple-generating dependencies / Datalog$^\pm$):** extending boundedness analysis to ontology-mediated query answering; deciding when a set of existential rules is bounded/FO-rewritable (Bourgaux, Leclère, Mugnier, Thomazo; Benedikt, Bourhis, Boom) *(frontier — verify)*.
- **Reverse boundedness and "stage" optimization** for incremental and streaming Datalog engines.
- **Boundedness vs. FO-rewritability** distinctions in the ontology/OBDA setting; links to the **bounded-derivation-depth property (BDDP)** (Cali, Gottlob, Pieris).
- Groups: Oxford (Benedikt, Kostylev), LIGM/Montpellier (Mugnier, Leclère), Edinburgh, IMDEA (Barceló), Warsaw (Murlak, Bourhis).

## 8. Future Work

- Close the decidability frontier for **non-monadic linear** and **bounded-arity** programs.
- Unify **boundedness, FO-rewritability, and BDDP** under existential rules with a single decidable criterion where possible.
- Practical **boundedness detection** as a query optimization: detect partial/predicate boundedness to unfold recursion in real Datalog systems (Soufflé, LogicBlox-style).
- Parameterized complexity of boundedness by treewidth/arity.

## 9. Key References

- **[Foundational]** H. Gaifman, H. Mairson, Y. Sagiv, M. Vardi. *Undecidable optimization problems for database logic programs.* JACM, 1993.
- **[Foundational]** S. Cosmadakis, H. Gaifman, P. Kanellakis, M. Vardi. *Decidable optimization problems for database logic programs.* STOC 1988.
- **[SOTA]** M. Benedikt, B. ten Cate, T. Colcombet, M. Vanden Boom. *The complexity of boundedness for guarded logics.* LICS 2015.
- **[SOTA]** P. Barceló, D. Figueira, M. Romero, et al. work on guarded/frontier-guarded Datalog boundedness (LICS/ICDT).
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Ch. on Datalog optimization and boundedness).

---
*Part of the [DBMS Research catalog](../../README.md).*
