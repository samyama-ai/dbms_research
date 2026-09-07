---
id: 01-relational-theory/embedded-dependency-implication
title: "Implication Problem for Embedded Dependencies"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Implication Problem for Embedded Dependencies

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/embedded-dependency-implication` · **Status:** partially-solved

## 1. Problem Statement

The **implication problem** asks: given a finite set $\Sigma$ of data dependencies and a single dependency $\sigma$, does every database instance satisfying $\Sigma$ also satisfy $\sigma$ (written $\Sigma \models \sigma$)?

"Embedded" dependencies are those that constrain only a *projection* of a relation — the canonical examples being **embedded multivalued dependencies (EMVDs)**, **join dependencies (JDs)**, and **inclusion dependencies (INDs)**. Embeddedness is what makes the problem hard: unlike full functional/multivalued dependencies, no finite complete axiomatization exists.

Two variants must be separated because they *differ*:

- **Unrestricted implication** ($\models_{\mathrm{unr}}$): over all (finite or infinite) instances.
- **Finite implication** ($\models_{\mathrm{fin}}$): over finite instances only.

For embedded dependencies these two relations diverge, and each may have its own (un)decidability status. The problem is **partially solved**: undecidable in full generality, but with sharply characterized decidable and tractable fragments.

## 2. Mathematical Foundations

A general **embedded (implicational) dependency** is a first-order sentence
$$\forall \bar{x}\,\big( \phi(\bar{x}) \rightarrow \exists \bar{z}\, \psi(\bar{x},\bar{z}) \big)$$
covering both **TGDs** ($\psi$ relational) and **EGDs** ($\psi$ an equality). An EMVD $X \twoheadrightarrow Y \,|\, Z$ over $XYZ \subsetneq R$ states that the projection onto $XYZ$ decomposes losslessly; a JD $\bowtie[R_1,\dots,R_k]$ states $R = \pi_{R_1}R \bowtie \cdots \bowtie \pi_{R_k}R$. An IND $R[\bar{A}] \subseteq S[\bar{B}]$ is a non-full TGD.

The decision procedure of record is the **chase**: $\Sigma \models \sigma$ iff chasing the frozen body of $\sigma$ with $\Sigma$ yields the head. Termination of the chase delineates decidability. Key separating phenomena: EMVDs lack a finite, $k$-ary complete axiom system (Parker–Parsaye-Ghomi; Sagiv–Walecka), and IND+FD interaction is undecidable.

## 3. State of the Art (SOTA)

Landmark results: **Chandra–Lewis–Makowsky / Beeri–Vardi (1981)** — implication for general embedded dependencies is **undecidable**. **Casanova–Fagin–Papadimitriou (1984)** — INDs alone are decidable (PSPACE-complete) but FDs+INDs together are **undecidable**, and finite vs. unrestricted implication differ for INDs. **Herrmann (1995)** proved **EMVD implication is undecidable**, resolving a 20-year open question. Tractable islands: FDs are linear (Armstrong axioms), MVDs and acyclic JDs are well-behaved, and *unary* INDs combined with FDs are decidable in polynomial time (Cosmadakis–Kanellakis–Vardi). Modern angle: embedded dependencies are studied via **finite implication ≈ guarded/frontier-guarded TGD** reasoning and via information-theoretic inequalities (Geiger–Pearl, Lee).

## 4. Upper Bound

- **INDs alone:** implication decidable, **PSPACE-complete** (Casanova–Fagin–Papadimitriou). Acyclic IND sets drop to PTIME.
- **FDs:** PTIME (linear) via Armstrong's axioms.
- **Unary INDs + FDs:** PTIME (Cosmadakis–Kanellakis–Vardi).
- **Full TGDs/EGDs (chase terminates):** decidable; combined complexity up to EXPTIME-/2EXPTIME-complete for guarded fragments (Calì–Gottlob–Kifer).
- **Acyclic JDs:** implication tractable via the link to acyclic hypergraphs (Beeri–Fagin–Maier–Yannakakis).

## 5. Lower Bound

- **General embedded dependencies:** implication is **undecidable** (Beeri–Vardi 1981) by Turing-machine simulation in the chase.
- **EMVDs:** **undecidable**, both finite and unrestricted (Herrmann 1995).
- **FDs + INDs:** **undecidable**; finite implication is **co-r.e.-complete**, unrestricted is **r.e.-complete** (Mitchell; Chandra–Vardi).
- **INDs alone:** **PSPACE-hard** lower bound matching the upper bound.

These establish that no finite complete axiomatization (no $k$-ary one) can exist for the embedded classes.

## 6. The Gap

The boundary between decidable and undecidable is, for once, *well-localized*: full dependencies with terminating chase and INDs-alone are decidable; EMVDs, general embedded dependencies, and FD+IND mixtures are undecidable. The remaining gaps are **complexity gaps inside the decidable fragments** (e.g., exact complexity of various guarded/sticky/frontier-guarded TGD classes, and of restricted JD families), and the persistent **finite-vs-unrestricted** divergence, which is fully understood only for some classes. Closing these means tight complexity dichotomies per syntactic fragment rather than a single grand decision procedure.

## 7. Current Research (as of June 2026)

Active directions: (1) sharpening the **guarded / frontier-guarded / sticky / warded** TGD hierarchy that governs decidable implication and query answering (Gottlob, Pieris, Sallinger; Bourhis, Mugnier, Thomazo); (2) **information-theoretic** treatment of dependency implication and the connection between conditional-independence implication and EMVD implication (Kenig, Suciu — entropic/information inequalities); (3) implication over **temporal, probabilistic, and approximate** dependencies; (4) renewed interest from **schema-mapping composition** and **data-integration** correctness *(frontier — verify)*.

## 8. Future Work

- Complete the dichotomy map of decidable TGD/EGD fragments with tight complexity.
- Settle remaining finite-controllability questions for embedded classes.
- Practical implication checkers leveraging modern SAT/SMT and the chase for the decidable islands.
- Bridge the information-theoretic and chase-based views of EMVD/JD implication.

## 9. Key References

- **[Foundational]** C. Beeri, M. Y. Vardi. *The Implication Problem for Data Dependencies.* ICALP, 1981. — [DOI](https://doi.org/10.1007/3-540-10843-2_7)
- **[Foundational]** M. A. Casanova, R. Fagin, C. H. Papadimitriou. *Inclusion Dependencies and Their Interaction with Functional Dependencies.* JCSS, 1984. — [DOI](https://doi.org/10.1016/0022-0000(84)90075-8)
- **[SOTA]** C. Herrmann. *On the Undecidability of Implications Between Embedded Multivalued Dependencies.* Information and Computation, 1995. — [DOI](https://doi.org/10.1006/inco.1995.1148)
- **[Foundational]** S. S. Cosmadakis, P. C. Kanellakis, M. Y. Vardi. *Polynomial-Time Implication Problems for Unary Inclusion Dependencies.* JACM, 1990. — [DOI](https://doi.org/10.1145/78935.78937)
- **[SOTA]** B. Kenig, D. Suciu. *Integrity Constraints Revisited: From Exact to Approximate Implication.* ICDT / LMCS, 2020–2022. — [arXiv](https://arxiv.org/abs/1812.09987)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Ch. 8–10). — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

Consider relation $R(A,B,C)$ and ask whether the two MVDs $A \twoheadrightarrow B$ and $A \twoheadrightarrow C$ imply the JD $\bowtie[AB, AC]$ — i.e., lossless decomposition into $AB$ and $AC$. Because $B$ and $C$ together with $A$ exhaust the attributes, this is a *full* MVD setting, so the chase decides it. Freeze the JD body: tuples $t_1=(a,b_1,c_1)$, $t_2=(a,b_2,c_2)$. Applying $A \twoheadrightarrow B$ to the $A$-group $\{t_1,t_2\}$ generates the swapped tuple $(a,b_1,c_2)$; that tuple is exactly the join witness $\pi_{AB}t_1 \bowtie \pi_{AC}t_2$ the JD demands. The chase halts, the head is satisfied, so $\{A\twoheadrightarrow B,\ A\twoheadrightarrow C\} \models \bowtie[AB,AC]$. Now drop a column — make the MVDs *embedded* over $XYZ \subsetneq R$ in a wider relation. The swap tuples may force fresh values on the hidden attributes, the chase need not terminate, and (Herrmann) no algorithm decides such EMVD implication. The single missing attribute is the entire difference between decidable and undecidable.

---
*Part of the [DBMS Research catalog](../../README.md).*
