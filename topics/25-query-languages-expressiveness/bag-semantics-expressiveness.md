# Bag (Multiset) Semantics Expressiveness and Equivalence

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/bag-semantics-expressiveness` · **Status:** open

## 1. Problem Statement
Real SQL is **bag-semantics**: tables are multisets, `SELECT` without `DISTINCT` keeps duplicates, and operators track multiplicities. The theory of query languages, however, was largely built under **set semantics**. This problem asks for a full **expressiveness theory under bag semantics** and, crucially, decision procedures for **bag-equivalence** ($q_1 \equiv_b q_2$: same multiplicity for every output tuple on every database) and **bag-containment** ($q_1 \sqsubseteq_b q_2$: multiplicity of $q_1$ $\le$ that of $q_2$ pointwise).

Variants:
- **Equivalence:** decide $q_1 \equiv_b q_2$ for conjunctive queries (CQ), CQ with comparisons, unions (UCQ), and with aggregation.
- **Containment:** decide $q_1 \sqsubseteq_b q_2$ — notoriously harder than equivalence.
- **Expressiveness/separation:** does bag semantics increase or decrease distinguishing power vs. set semantics; what is the bag analogue of genericity, of FO vs. relational algebra?

## 2. Mathematical Foundations
A bag instance assigns each tuple a multiplicity in $\mathbb{N}$; CQ evaluation under bags counts the number of satisfying homomorphisms (so a CQ's output multiplicity of tuple $\bar a$ is $|\{h : h \text{ a homomorphism from body to } D,\ h(\text{head})=\bar a\}|$). This is exactly **#CQ / counting answers**, linking bag semantics to **counting complexity** and the **provenance semiring** $\mathbb{N}[X]$ (the free commutative semiring), the universal semiring whose homomorphisms specialize to set, bag, security, and probability semantics (Green–Karvounarakis–Tannen).

Key facts:
- **Bag equivalence of CQs** is decidable and characterized by **isomorphism**: two CQs are bag-equivalent iff they are isomorphic (Chaudhuri–Vardi), in sharp contrast to set equivalence (homomorphic equivalence / folding).
- **Bag containment of CQs** is the famous hard case — equivalent to a question about polynomial inequalities / counting homomorphisms; its decidability has been **open for over three decades**.
- Genericity and locality arguments transfer only partially; counting collapses some set-semantics equivalences and refines others.

$$q_1 \equiv_{\mathrm{set}} q_2 \iff q_1 \stackrel{\text{hom}}{\equiv} q_2, \qquad q_1 \equiv_{\mathrm{bag}} q_2 \iff q_1 \cong q_2 \text{ (isomorphic)}.$$

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Chaudhuri–Vardi (PODS 1993) settled **bag equivalence of CQs = isomorphism** and posed bag containment. Cohen, Nutt, Sagiv and others extended to **bag-set** semantics, UCQs, and queries with aggregation/grouping (Cohen–Nutt–Sagiv, "Deciding equivalences among aggregate queries," JACM 2007). Connections to provenance semirings (Green et al.) and to **#-hardness** of counting answers (Pichler–Skritek; Dell–Roth–Wellnitz on counting homomorphisms / answers fine-grained complexity).
- **Systems-SOTA:** Automated **SQL equivalence checkers**—**Cosette** (Chu et al., CIDR 2017) using $K$-relations/U-semiring and bounded provers, **SQLSolver**, **WeTune**, **SPES**—decide or refute bag-equivalence of real SQL queries (with three-valued logic, NULLs, aggregation) up to bounds, and are used for rewrite-rule verification and query-optimizer testing.

## 4. Upper Bound
**Bag equivalence of CQs** is decidable via the isomorphism characterization, hence in **GI-/NP** (graph-isomorphism-bounded; polynomial for bounded arity in many cases). For UCQs and bag-set, equivalence reduces to systems of multiplicity equations and remains decidable (Cohen et al.). Provenance-semiring methods give a *uniform* upper bound: equivalence over the free semiring $\mathbb{N}[X]$ implies equivalence under all semirings, and U-semiring normalization (Cosette/SPES) yields a sound (and in bounded fragments complete) decision procedure. Counting CQ answers is in **FP** for bounded-treewidth / fractional-hypertree-width queries (worst-case-optimal counting).

## 5. Lower Bound
**Bag containment of CQs is not known to be decidable** — it is the central open hardness frontier; it is known to be undecidable for CQs with comparisons (Ioannidis–Ramakrishnan; Jayram–Kolaitis–Vee showed undecidability of bag-containment for *conjunctive queries with inequalities*) and at least **$\Pi^p_2$-hard / coNP-hard** lower bounds apply to broad fragments. Counting homomorphisms/answers is **#P-hard** in general and, under fine-grained hypotheses, requires time $n^{\Omega(\text{tw})}$ (Dell–Roth–Wellnitz; #W[1]-hardness for unbounded treewidth), giving conditional lower bounds on bag evaluation itself.

## 6. The Gap
The signature open gap is the **decidability of bag-containment for pure conjunctive queries** — open since Chaudhuri–Vardi (1993). Equivalence is fully understood (isomorphism); containment is not, and the boundary between decidable equivalence and (un)decidable containment, and how aggregation/UCQ/comparisons shift it, is only partially mapped. A second gap: a clean **expressiveness/separation theory** (a Codd-style completeness theorem) for bag-relational algebra is still missing.

## 7. Current Research (as of June 2026)
- **U-semiring / $K$-relation provers** for full SQL (NULLs, three-valued logic, aggregation, sorting) — pushing completeness boundaries of Cosette/SPES/SQLSolver and integrating them into optimizer rule verification *(frontier — completeness scope for aggregation+NULLs is evolving; verify)*.
- Fine-grained complexity of **counting query answers** (Dell–Roth–Wellnitz; Focke–Roth) sharpening bag-evaluation lower bounds.
- Renewed attacks on **bag-containment decidability** via Hilbert's-Tenth / polynomial-identity-testing connections.

## 8. Future Work
- Resolve (un)decidability of CQ bag-containment.
- A genericity/locality and BP-completeness theory native to bag semantics.
- Provably complete, scalable equivalence checkers for the full SQL bag fragment, including window functions and recursion.

## 9. Key References
- **[Foundational]** S. Chaudhuri, M. Vardi. *Optimization of Real Conjunctive Queries.* PODS, 1993 (bag equivalence = isomorphism; containment open). — [DOI](https://doi.org/10.1145/153850.153856)
- **[Foundational]** T. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** T. S. Jayram, P. Kolaitis, E. Vee. *The Containment Problem for Real Conjunctive Queries with Inequalities.* PODS, 2006. — [DOI](https://doi.org/10.1145/1142351.1142363)
- **[Foundational]** S. Cohen, W. Nutt, Y. Sagiv. *Deciding Equivalences Among Conjunctive Aggregate Queries.* JACM, 2007. — [DOI](https://doi.org/10.1145/1219092.1219093)
- **[SOTA]** S. Chu, C. Wang, K. Weitz, A. Cheung. *Cosette: An Automated Prover for SQL.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/ChuWWC17.html)
- **[SOTA]** H. Dell, M. Roth, P. Wellnitz. *Counting Answers to Existential Questions.* ICALP, 2019. — [arXiv](https://arxiv.org/abs/1902.04960) · [DOI](https://doi.org/10.4230/LIPIcs.ICALP.2019.113)

## 10. Worked Example

**Set-equivalent but bag-different.** Let $R(x,y)$ be the edge relation $\{(1,2),(2,3),(2,4)\}$. Consider two CQs returning the first column:
$$q_1(x) \leftarrow R(x,y), \qquad q_2(x) \leftarrow R(x,y), R(x,z).$$
Under **set** semantics they are equivalent (both fold to $q_1$ by homomorphism: $z$ maps onto $y$), so $q_1\equiv_{\text{set}}q_2$.

Under **bag** semantics, multiplicity = number of homomorphisms. For $x=2$, query $q_1$ has $2$ witnesses ($y\in\{3,4\}$); $q_2$ has $2\times 2 = 4$ witnesses (independent choices of $y,z$). So the output bags differ ($2$ vs $4$ for tuple $2$), hence $q_1\not\equiv_{\text{bag}}q_2$.

**Chaudhuri–Vardi in action.** The bodies of $q_1$ and $q_2$ are *not isomorphic* (one atom vs two atoms over different variable sets), which by the theorem $q_1\equiv_{\text{bag}}q_2 \iff q_1\cong q_2$ immediately certifies bag-inequivalence — no database search needed. This is exactly why bag equivalence is "easy" (isomorphism) while bag *containment* $q_1\sqsubseteq_b q_2$ (here $2\le 4$ pointwise — does it always hold?) stays the long-open hard frontier.

---
*Part of the [DBMS Research catalog](../../README.md).*
