# Cardinality Constraints in the Chase

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/cardinality-constraints-chase` · **Status:** open

## 1. Problem Statement

The **chase** is the universal engine of dependency reasoning, query answering under constraints, and data exchange. It handles **equality-generating dependencies (EGDs)** and **tuple-generating dependencies (TGDs)**. The open problem is to **soundly and completely incorporate numeric cardinality and counting constraints** — e.g. "each customer has at most 5 accounts," "each order has between 1 and 10 items," "attribute $A$ takes at most $k$ distinct values" — into chase-based reasoning.

Variants:
- **Decision:** Given a schema with TGDs/EGDs *plus* cardinality constraints (CCs), is query answering / certain-answer computation decidable?
- **Construction:** Does a (finite) universal model respecting CCs exist, and can the chase build it?
- **Counting/optimization:** Compute the minimum/maximum cardinality of a query answer consistent with the constraints (a counting/ILP-flavored problem).

This is **open**: cardinality constraints interact with TGD-generated witnesses in ways that classical chase termination theory does not cover.

## 2. Mathematical Foundations

A **cardinality constraint** generalizes keys and participation constraints. In ER/UML terms, $\mathrm{card}(R, A) = (\min, \max)$ bounds how many tuples relate to each entity. Formally a CC may be written as a counting quantifier:
$$\forall x\ \big| \{ y : R(x,y) \} \big| \le k.$$

The chase fires a TGD $\forall \bar x\,(\phi(\bar x) \to \exists \bar y\,\psi(\bar x,\bar y))$ by adding witness tuples (often **labeled nulls**). EGDs equate values; if two constants are forced equal the chase **fails**. **Cardinality constraints add a third action**: counting can force fresh witnesses to *coalesce* (upper bounds) or *demand* new ones (lower bounds), blending TGD and EGD behavior and introducing arithmetic.

Key theory it rests on:
- **Chase termination** classes: weak acyclicity, stratification, super-weak acyclicity.
- **AGM / fractional edge cover bound** for output cardinality of joins (Atserias–Grohe–Marx): a *cardinality* bound on query results,
$$|Q| \le \prod_e |R_e|^{x_e},\quad x \text{ a fractional edge cover}.$$
- Counting quantifiers connect to **Presburger arithmetic** and **integer linear programming**, the natural decidable/undecidable boundary for the arithmetic part.

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- Cardinality constraints in conceptual modeling are well studied (Lenzerini–Nobili; Thalheim) for **consistency** of ER cardinalities via linear inequalities — but *not* integrated with the chase.
- **Existential rules with number restrictions** appear in description logics (e.g., $\mathcal{SHIQ}$, role number restrictions) where reasoning is decidable but EXPTIME/NEXPTIME-hard; this is the closest principled integration of counting with TGD-like rules.
- Chase-based query answering under TGDs/EGDs: Datalog$^\pm$ (Calì–Gottlob–Lukasiewicz) gives decidable guarded/sticky fragments, **without** numeric CCs.

**Systems-SOTA:**
- **Cardinality estimation** in optimizers uses statistics, sketches, and worst-case bounds (AGM, **degree/LP bounds**), but this is *estimation*, not reasoning.
- **Worst-case-optimal join** engines (LogicBlox, Umbra) and **pessimistic cardinality estimators** (Cai–Balazinska–Suciu, 2019) operationalize cardinality *bounds* but not constraint *implication*.

## 4. Upper Bound

- For TGDs/EGDs without CCs, on **weakly-acyclic** sets the chase terminates and certain answers are computable in PTIME data complexity; combined complexity EXPTIME.
- Adding **bounded** integer CCs encodable in **Presburger arithmetic** keeps reasoning decidable but raises complexity to at least NEXPTIME-style bounds, mirroring qualified number restrictions in expressive DLs.
- Consistency of pure cardinality constraints (no TGDs) is solvable by **linear/integer programming**, giving PSPACE/NP-style upper bounds depending on encoding.

## 5. Lower Bound

- General TGD+EGD query answering is already **undecidable** (the chase need not terminate); CCs cannot make it easier.
- Counting/number restrictions push hardness: number-restricted existential rules are **2EXPTIME-hard** in expressive fragments, and CC-consistency with cyclic schemas embeds **ILP feasibility (NP-hard)**.
- Cardinality bounds interacting with key (EGD) propagation can encode **subset-sum / ILP**, yielding NP-hardness even in restricted, terminating cases.
- Lower bounds inherit FD+IND **undecidability** when CCs simulate inclusion-style witnessing.

## 6. The Gap

This is genuinely **open**. There is no canonical "chase with counting" with proven soundness, completeness, and a termination theory analogous to weak acyclicity. The gap separates: (a) decidable, well-understood CC-consistency *without* generating rules, and (b) undecidable TGD/EGD reasoning *with* unbounded generation — with the interesting middle (bounded CCs + guarded TGDs) only partially mapped. Closing it requires a chase variant whose counting actions have a termination criterion and a matching complexity classification, likely via Presburger-guarded fragments.

## 7. Current Research (as of June 2026)

- **Cardinality estimation meets constraints:** pessimistic/bound-based estimators (Suciu group; degree-sequence and LP bounds) increasingly fold in declared keys and FDs to tighten bounds *(frontier — verify)*.
- **Existential rules + arithmetic / aggregation:** extending Datalog$^\pm$ and Vadalog with counting and numeric reasoning (Gottlob, Pieris, and collaborators) *(frontier — verify)*.
- **Information-theoretic cardinality bounds** beyond AGM (Khamis–Ngo–Suciu, entropy/Shannon-inequality LPs) provide the most principled current handle on counting in joins.
- Probabilistic/numeric constraints in the chase for data cleaning and repair.

## 8. Future Work

- A formal **chase-with-cardinality** calculus with a termination theory.
- Decidable fragments combining **guarded TGDs + Presburger-bounded CCs**.
- Tight complexity (and dichotomies) for CC-augmented query answering.
- Bridging reasoning-grade CC implication with practical **cardinality estimation** so optimizers exploit declared constraints provably.

## 9. Key References

- **[Foundational]** Lenzerini, M., Nobili, P. *On the Satisfiability of Dependency Constraints in Entity-Relationship Schemata.* Information Systems, 1990. — [DBLP](https://dblp.org/db/journals/is/is15.html)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Comput. / FOCS, 2008/2013. — [DOI](https://doi.org/10.1137/110859440)
- **[SOTA]** Abo Khamis, M., Ngo, H., Suciu, D. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS, 2017. — [arXiv](https://arxiv.org/abs/1612.02503)
- **[SOTA]** Cai, W., Balazinska, M., Suciu, D. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[Survey]** Calì, A., Gottlob, G., Lukasiewicz, T. *A General Datalog-based Framework for Tractable Query Answering over Ontologies (Datalog±).* J. Web Semantics, 2012. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1570826812000388)

## 10. Worked Example

Schema: $\mathrm{Customer}(c)$, $\mathrm{Account}(c,a)$. A TGD demands every customer own an account:
$$\mathrm{Customer}(c)\;\to\;\exists a\,\mathrm{Account}(c,a),$$
and a cardinality constraint caps accounts per customer: $\big|\{a:\mathrm{Account}(c,a)\}\big|\le 2$.

**Chase trace.** Start $D=\{\mathrm{Customer}(c_1)\}$. The TGD fires, adding $\mathrm{Account}(c_1,\nu_1)$ with a fresh null $\nu_1$. The CC is satisfied ($1\le2$). Done — universal model has 1 account tuple. Now suppose a second EGD-like rule re-fires the TGD twice (say via two source rows), yielding $\mathrm{Account}(c_1,\nu_1),\mathrm{Account}(c_1,\nu_2),\mathrm{Account}(c_1,\nu_3)$: three nulls, violating $\le2$. The **counting action** must coalesce two nulls (e.g. $\nu_3:=\nu_1$), an EGD-like equate driven by *arithmetic*, not by an explicit equality dependency.

**AGM cross-check.** A join $\mathrm{Customer}\bowtie\mathrm{Account}$ on $c$ with $|\mathrm{Account}|=N$ and the degree cap $2$ has output $\le 2\cdot|\mathrm{Customer}|$ — far below the unconstrained AGM bound $\prod_e|R_e|^{x_e}$. Capturing such coalescing with a *termination guarantee* is exactly the open gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
