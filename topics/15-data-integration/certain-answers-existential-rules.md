# Certain Answers Under Existential Rules

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/certain-answers-existential-rules` · **Status:** open

## 1. Problem Statement

Given a source database $D$, a set $\Sigma$ of **existential rules** (tuple-generating dependencies, TGDs) mapping source to target, and a **union of conjunctive queries (UCQ)** $Q$, the *certain answers* are the tuples $\bar{a}$ that hold in **every** model $I \supseteq D$ satisfying $\Sigma$:
$$\mathsf{cert}(Q, D, \Sigma) = \bigcap \{ Q(I) \mid I \models D \cup \Sigma \}.$$
Equivalently, $\mathsf{cert}(Q, D, \Sigma) = Q(\mathsf{chase}(D, \Sigma))$ restricted to constants, when the chase terminates or when $Q$ is preserved under homomorphisms.

The open problem is to obtain **tight data-complexity and combined-complexity boundaries** for the decision problem ("is $\bar{a} \in \mathsf{cert}$?") across the major **decidable** TGD classes — guarded, weakly-acyclic, sticky, frontier-guarded, warded, and their bounded-treewidth-model fragments — where gaps between known upper and lower bounds persist, especially for combined complexity and for the boundaries between fragments.

Variants: (i) **decision** (Boolean CQ certainty); (ii) **counting** (#certain answers, in $\#P$/$\#\cdot$ hierarchies); (iii) **enumeration** (constant/polynomial delay output of certain tuples).

## 2. Mathematical Foundations

A TGD has the form $\forall \bar{x}\,\bar{y}\; \phi(\bar{x},\bar{y}) \rightarrow \exists \bar{z}\; \psi(\bar{x},\bar{z})$. Certain-answer evaluation under TGDs coincides with **Boolean Conjunctive Query Answering (BCQ)** over ontologies and is the central problem of *existential-rule reasoning* (a.k.a. Datalog$^\pm$).

The **chase** is the canonical procedure: it repeatedly fires unsatisfied rules, introducing fresh nulls (labeled nulls) for existential variables, producing a **universal model** $U$ such that $U \to I$ for every model $I$. Then $\mathsf{cert}(Q) = \mathsf{certUnion}$ holds via the homomorphism theorem: $\bar a \in \mathsf{cert}(Q,D,\Sigma) \iff U \models Q(\bar a)$.

Key structural notions: **guardedness** (each rule body has an atom containing all universally quantified variables) yields bounded-treewidth universal models and decidability via alternating tree automata; **chase termination** classes (weak acyclicity) give finite $U$. Complexity hinges on the **treewidth of the chase** and on first-order/MSO definability of the answer set.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Calì, Gottlob, Lukasiewicz, Pieris established the Datalog$^\pm$ landscape: guarded TGDs give 2ExpTime-complete combined / PTime data complexity; sticky and linear TGDs give lower combined complexity (linear is in $\mathrm{AC}^0$ data). Warded Datalog$^\pm$ (Gottlob–Pieris, PODS 2015; the **VADALOG** system, Bellomarini et al., VLDB 2018) is PTime-complete in combined complexity and captures core OWL 2 QL reasoning.
- **Systems-SOTA.** VADALOG (Oxford/Bank of Italy), **GraphDB**, **RDFox** (Oxford) for materialization-based chase; **LLunatic** / **Llunatic** chase engines for data exchange; **PDQ** for query answering with constraints.

## 4. Upper Bound

For **guarded TGDs**: BCQ answering is **2ExpTime-complete** in combined complexity, **ExpTime** in bounded-arity combined, and **PTime-complete** in data complexity. For **linear/sticky** TGDs: data complexity in $\mathrm{AC}^0$ (first-order rewritable), combined in PSpace/ExpTime depending on arity. For **weakly-acyclic** TGDs (terminating chase): data complexity **PTime**, combined **2ExpTime** (chase is exponential). These hold in the standard RAM/Turing model. Frontier-guarded TGDs: combined **2ExpTime**, via tree-automata over bounded-treewidth chase witnesses.

## 5. Lower Bound

BCQ answering under **general TGDs is undecidable** (encodes the halting problem via unrestricted chase). Within decidable classes, matching hardness is known in several but not all cases: guarded is 2ExpTime-hard (Calì et al.); PTime-hardness in data complexity follows from Datalog. For **bounded-arity** fragments and for certain combinations (e.g., guarded + sticky, or frontier-guarded restricted treewidth), exact combined-complexity lower bounds remain **open**. Counting certain answers is $\#P$-hard already for simple TGDs.

## 6. The Gap

The frontier is **genuinely open** in two places: (1) precise **combined-complexity** classifications for several intersections/unions of decidable classes (notably bounded-treewidth-set TGDs and frontier-guarded fragments at fixed arity); (2) the boundary between **first-order rewritable** and **PTime-complete-but-not-FO** fragments — a fine-grained "rewritability vs. recursion" gap. Closing these requires either new automata-theoretic upper bounds matching existing reductions, or new $\Sigma_2^p$/ExpTime-hardness gadgets.

## 7. Current Research (as of June 2026)

Active work: **bounded-treewidth and "well-behaved" chase variants** (oblivious, semi-oblivious, restricted, core chase) and their termination/complexity interplay (Gottlob, Pieris, Marnette, Grau). The VADALOG group pushes **PTime warded** extensions with aggregation and recursion. *(frontier — verify)* Recent work on **combined approximation / "approximate certain answers"** and on parallel/streaming chase for incremental reasoning. *(frontier — verify)* Connections to **existential rules over probabilistic/weighted data** and to neuro-symbolic rule learning are emerging at PODS/ICDT 2025–2026.

## 8. Future Work

- Complete the combined-complexity map for fixed-arity decidable fragments.
- Practical **chase-termination-aware** query planners; cost models for restricted vs. oblivious chase.
- Tractable **enumeration** with bounded delay for guarded/sticky certain answers.
- Robust semantics combining TGDs with **equality-generating dependencies (EGDs)** and negation without losing decidability.

## 9. Key References

- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. (Chase, dependencies, universal models.) — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Foundational]** A. Calì, G. Gottlob, T. Lukasiewicz. *A general Datalog-based framework for tractable query answering over ontologies.* Journal of Web Semantics, 2012. — [DOI](https://doi.org/10.1016/j.websem.2012.03.001)
- **[SOTA]** G. Gottlob, A. Pieris. *Beyond SPARQL under OWL 2 QL entailment regime: Rules to the rescue.* IJCAI, 2015. (Warded Datalog$^\pm$.) — [PDF](https://www.ijcai.org/Proceedings/15/Papers/424.pdf)
- **[SOTA]** L. Bellomarini, E. Sallinger, G. Gottlob. *The VADALOG System: Datalog-based Reasoning for Knowledge Graphs.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3213880.3213888)
- **[Survey]** A. Calì, G. Gottlob, A. Pieris. *Towards more expressive ontology languages: The query answering problem.* Artificial Intelligence, 2012. — [DOI](https://doi.org/10.1016/j.artint.2012.08.002)
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)

## 10. Worked Example

Source $D = \{\mathsf{Emp}(\mathrm{alice})\}$. One TGD (guarded, the body atom $\mathsf{Emp}(x)$ contains $x$):
$$\Sigma:\quad \mathsf{Emp}(x) \rightarrow \exists z\; \mathsf{Manages}(z, x).$$

**Chase.** The trigger $\mathsf{Emp}(\mathrm{alice})$ has no extension, so fire it, introducing a fresh labeled null $n_1$:
$$U = \{\mathsf{Emp}(\mathrm{alice}),\ \mathsf{Manages}(n_1, \mathrm{alice})\}.$$
No further trigger fires (no $\mathsf{Emp}$ fact about a null), so the chase terminates with universal model $U$.

**Query 1:** $Q_1() \leftarrow \exists y\, \mathsf{Manages}(y, \mathrm{alice})$. Evaluating on $U$: $y \mapsto n_1$ satisfies it, so $Q_1$ is **certain** (true). By the homomorphism theorem, since $U \to I$ for every model $I$, every model also has *someone* managing alice.

**Query 2:** $Q_2(y) \leftarrow \mathsf{Manages}(y, \mathrm{alice})$ asking *who*. The only witness is the null $n_1$, and certain answers are restricted to constants — so $\mathsf{cert}(Q_2) = \varnothing$. No specific manager is certain, because different models instantiate $z$ differently. This is exactly why existential nulls block constant-level certainty while preserving Boolean/UCQ certainty.

---
*Part of the [DBMS Research catalog](../../README.md).*
