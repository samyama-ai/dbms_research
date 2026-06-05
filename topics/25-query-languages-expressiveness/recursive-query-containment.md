# Containment of Conjunctive Queries with Recursion

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/recursive-query-containment` · **Status:** partially-solved

## 1. Problem Statement
Given two queries $Q_1$ and $Q_2$ in a recursive query language, decide whether $Q_1 \sqsubseteq Q_2$, i.e., whether $Q_1(D) \subseteq Q_2(D)$ for every database $D$. The decision problem ranges over several language classes:

- **Datalog ⊑ Datalog** (recursive containment, both sides recursive);
- **Datalog ⊑ UCQ** (recursive query contained in a nonrecursive union of conjunctive queries);
- **UCQ ⊑ Datalog**;
- **RPQ / CRPQ / C2RPQ containment** (regular path queries and their conjunctive/two-way extensions over graphs).

Variants include containment **under constraints** (TGDs/EGDs, the chase), **certain-answer** containment over incomplete data, and the optimization variant of computing a minimal equivalent program. The goal is to characterize the exact decidability frontier and tight complexity for each class.

## 2. Mathematical Foundations
A conjunctive query is $Q(\bar x) \leftarrow \bigwedge_i R_i(\bar u_i)$; CQ containment $Q_1 \sqsubseteq Q_2$ holds iff there is a **homomorphism** $h: Q_2 \to Q_1$ (Chandra–Merlin, 1977), making it NP-complete. Datalog programs define least fixpoints of monotone operators $T_P$; their semantics is $\bigcup_n T_P^n(\emptyset)$.

For Datalog ⊑ Datalog, undecidability follows by reduction from the **containment / equivalence of context-free languages** and Turing-machine encodings. The decidable subcase **Datalog ⊑ UCQ** rests on **boundedness** and tree-automata techniques: a recursive query is contained in a nonrecursive one iff finitely many "unfoldings" (expansions) suffice, checkable via two-way alternating tree automata.

RPQs denote $\{(x,y) : x \xrightarrow{w} y,\ w \in L\}$ for a regular language $L$; containment reduces to automata-theoretic constructions on the product of NFAs and is decidable. C2RPQ containment uses canonical-database/automaton arguments and sits in EXPSPACE.

## 3. State of the Art (SOTA)
- **CQ/UCQ:** containment is NP-complete (Chandra–Merlin 1977; Sagiv–Yannakakis 1980).
- **Datalog ⊑ UCQ:** decidable, 2EXPTIME-complete (Chaudhuri–Vardi 1992; Bourhis–Krötzsch–Rudolph and others refined bounds).
- **UCQ ⊑ Datalog:** decidable via boundedness/automata.
- **Datalog ⊑ Datalog:** **undecidable** (Shmueli 1993).
- **RPQ ⊑ RPQ:** PSPACE-complete. **C2RPQ ⊑ C2RPQ:** EXPSPACE-complete (Calvanese–De Giacomo–Lenzerini–Vardi 2000–2003).
- **Monadic Datalog containment** is decidable (2EXPTIME).

## 4. Upper Bound
- CQ/UCQ containment: in NP (guess the homomorphism).
- Datalog ⊑ UCQ: 2EXPTIME via tree automata emptiness.
- C2RPQ containment: EXPSPACE via exponential automata products, tight.
- Monadic Datalog ⊑ Datalog: decidable, 2EXPTIME upper bound (Cosmadakis–Gaifman–Kanellakis–Vardi style automata). Boundedness of monadic Datalog is decidable; boundedness of general Datalog is undecidable.

## 5. Lower Bound
- CQ containment is NP-hard (3-colorability reduction).
- Datalog ⊑ UCQ is 2EXPTIME-hard.
- RPQ containment is PSPACE-hard; C2RPQ is EXPSPACE-hard.
- **Datalog ⊑ Datalog is undecidable** (reduction from CFG/Turing containment), as is general **Datalog boundedness** (Gaifman–Mairson–Sagiv–Vardi 1987).

## 6. The Gap
The frontier is sharp on the **decidability** axis: full Datalog⊑Datalog is undecidable, while Datalog⊑UCQ and monadic-Datalog containment are decidable with tight 2EXPTIME bounds. The genuinely open territory is the **constrained** setting: containment of (frontier-guarded / linear / sticky) Datalog and Datalog$^\pm$ under TGDs, and containment of CRPQs with data-value comparisons or with counting, where decidability boundaries and tight complexity are partly unknown. Closing these requires new automata models that combine recursion, regular navigation, and constraints.

## 7. Current Research (as of June 2026)
Active work targets containment for **navigational + recursive** fragments motivated by GQL/SPARQL property paths, and for **Datalog with aggregation/negation** under well-founded or stable semantics. Groups around Vardi, Calvanese, Barceló, Bourhis, Figueira, and Pieris study CRPQ/UCRPQ containment, the role of the **chase** under existential rules, and **semantic tree-width** characterizations. *(frontier — verify)* Recent results sharpen UCRPQ containment via "tree-likeness" of canonical models and connect determinacy to containment. Practical containment checkers are being revisited for graph-database optimizers.

## 8. Future Work
- Settle decidability/complexity for containment of guarded and frontier-guarded Datalog$^\pm$ under TGDs.
- CRPQ containment with data values, path variables, and counting (GQL features).
- Approximate / "almost-containment" notions and learning-based containment heuristics for optimizers.
- Containment under bag (multiset) semantics, largely open beyond CQs.

## 9. Key References
- **[Foundational]** A. Chandra, P. Merlin. *Optimal implementation of conjunctive queries in relational data bases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Foundational]** S. Chaudhuri, M. Vardi. *On the equivalence of recursive and nonrecursive Datalog programs.* PODS, 1992. — [DOI](https://doi.org/10.1145/137097.137109)
- **[Foundational]** O. Shmueli. *Equivalence of Datalog queries is undecidable.* J. Logic Programming, 1993. — [DOI](https://doi.org/10.1016/0743-1066(93)90040-N)
- **[SOTA]** D. Calvanese, G. De Giacomo, M. Lenzerini, M. Vardi. *Containment of conjunctive regular path queries with inverse.* KR, 2000. — [DBLP](https://dblp.org/rec/conf/kr/CalvaneseGLV00.html)
- **[Survey]** P. Barceló. *Querying graph databases.* PODS, 2013. — [DOI](https://doi.org/10.1145/2463664.2465216)

## 10. Worked Example

CQ containment via the homomorphism test (Chandra–Merlin). Let
$$Q_1(x,z) \leftarrow E(x,y), E(y,z) \qquad Q_2(x,z) \leftarrow E(x,w).$$
$Q_1$ asks for endpoints of a 2-edge path; $Q_2$ asks for any node $x$ with an outgoing edge (projected to $x,z$... here $z$ is free in $Q_1$). To test $Q_1 \sqsubseteq Q_2$ we seek a homomorphism $h: Q_2 \to Q_1$ mapping $Q_2$'s body into $Q_1$'s body and preserving the distinguished variable. Treat $Q_1$'s body as the "frozen" canonical database $D = \{E(x,y), E(y,z)\}$. We need $h$ with $h(x)=x$ and $E(h(x),h(w)) \in D$: take $h(w)=y$, giving $E(x,y) \in D$. ✓ So a homomorphism exists and $Q_1 \sqsubseteq Q_2$.

The reverse fails: mapping $Q_1$ into $Q_2$'s single-edge body would need a length-2 path, which $D'=\{E(x,w)\}$ lacks — so $Q_2 \not\sqsubseteq Q_1$, confirming proper containment. This homomorphism search is the NP-complete core (Section 2); recursion (Datalog $\sqsubseteq$ Datalog) replaces this finite test with unfolding-equivalence, which is undecidable (Shmueli).

---
*Part of the [DBMS Research catalog](../../README.md).*
