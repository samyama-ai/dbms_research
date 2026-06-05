# Finite vs. Unrestricted Implication

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/finite-vs-unrestricted-implication` · **Status:** partially-solved
> **Verification note:** The §10 worked example is garbled — the canonical FD+IND separation uses FD $A\to B$ with IND $R[A]\subseteq R[B]$ (forcing $R[B]\subseteq R[A]$ only on finite models, via $A\mapsto B$ injective on $\pi_A R$), and a valid infinite counterexample is tuples $(n{+}1,n)$; as written, the stated $B\to A$ "injectivity" step and the $(n,n{+}1)$ instance do not satisfy the premise IND.

## 1. Problem Statement

Logical implication of database dependencies can be evaluated over two model classes:

- **Unrestricted implication** $\Sigma \models \sigma$: every model (finite *or* infinite) of $\Sigma$ satisfies $\sigma$.
- **Finite implication** $\Sigma \models_{\mathrm{fin}} \sigma$: every *finite* model of $\Sigma$ satisfies $\sigma$.

The problems:

- **(Coincidence / Finite controllability)** For which dependency classes do the two notions coincide ($\models\ =\ \models_{\mathrm{fin}}$)? A class is **finitely controllable** when they do.
- **(Decision)** For classes where they differ, decide finite implication separately; characterize its complexity.
- **(Axiomatization)** When does finite implication admit a sound and complete *recursive* axiomatization (it always is r.e. for unrestricted, but finite implication can be non-r.e.)?

This is foundational: the chase and Armstrong axioms reason about unrestricted implication, but real databases are finite.

## 2. Mathematical Foundations

For **full dependencies** (FDs, full tgds, JDs, MVDs) the two notions coincide — the chase terminates and gives a finite counterexample, so finite controllability holds. The divergence appears with **existential** constraints:

- **Inclusion dependencies (INDs)** alone: $\models = \models_{\mathrm{fin}}$ (finitely controllable) and implication is **PSPACE-complete** (Casanova, Fagin, Papadimitriou 1984).
- **FDs + INDs**: finite and unrestricted implication **differ**, and finite implication is **undecidable** (Chandra & Vardi 1985; Mitchell). Unrestricted implication for FD+IND is also undecidable.

A key theorem (Rosati; Bárány–Gottlob–Otto): **guarded tgds / guarded fragments are finitely controllable**. For unrestricted implication, completeness theorems give an r.e. proof system; finite implication may be **co-r.e.** but not r.e., hence non-axiomatizable by a recursive system.

$$
\Sigma \models_{\mathrm{fin}} \sigma \quad\Longleftarrow\quad \Sigma \models \sigma, \qquad \text{equality} \iff \text{finite controllability.}
$$

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Casanova–Fagin–Papadimitriou (1984) for INDs; Chandra–Vardi (1985) for FD+IND undecidability and non-coincidence. **Rosati** (2006/2011) and **Bárány, Gottlob, Otto** (*LICS* 2010, *LMCS*) established **finite controllability of the guarded fragment** and guarded tgds, a major modern result. Pratt-Hartmann and Otto developed finite-model-theory tools (resolution, finite controllability of fragments with counting).
- **Datalog$^\pm$** classes (guarded, weakly-guarded, sticky) inherit finite controllability results, making certain-answer query answering robust over finite databases (Calì, Gottlob, Pieris).

## 4. Upper Bound

- **INDs alone:** finite/unrestricted implication coincide and are decidable in **PSPACE** (CFP 1984).
- **Guarded tgds / guarded fragment:** finitely controllable; query answering / implication is decidable, with combined complexity up to **2EXPTIME** (guarded Datalog$^\pm$; Calì–Gottlob–Kifer) and data complexity in **PTIME**.
- **Full dependencies:** decidable via the chase (finite = unrestricted), complexity from PTIME (FDs) up to EXPTIME (full tgds).

Model: classical first-order semantics, finite vs. arbitrary structures.

## 5. Lower Bound

- **FD + IND finite implication is undecidable** (Chandra & Vardi 1985) — and *distinct* from unrestricted implication, which is also undecidable; finite implication is **co-r.e.-complete** (not r.e.), so **no recursive complete axiomatization exists** for it. This is the canonical impossibility separating the two notions.
- **IND implication is PSPACE-hard** (CFP 1984).
- Embedded multivalued dependencies (EMVDs): finite and unrestricted implication **differ** and finite implication of EMVDs is **undecidable** (Herrmann), a classic separation.

## 6. The Gap

For **full dependencies, INDs, and guarded fragments**, the question is *closed*: coincidence (or its precise failure) and complexity are known. The genuinely **open / partially-solved** territory is the **fine boundary of finite controllability** for intermediate constraint languages — e.g., exactly which extensions of guardedness (frontier-guarded, sticky, with transitivity or counting) remain finitely controllable, and tight complexity of finite implication in those classes. The non-axiomatizability of finite implication for FD+IND is settled negatively; what remains is mapping where decidability is regained.

## 7. Current Research (as of June 2026)

- **Finite controllability with additional features**: transitive relations, counting quantifiers, and the **finite-model property** for description-logic / ontology fragments (Pratt-Hartmann, Gogacz, Ibáñez-García, Murlak). *(frontier — verify)* Recent results extend finite controllability to fragments combining guardedness with limited functionality/keys.
- **Finite open-world query answering** in **existential rules / Datalog$^\pm$** under finiteness assumptions (Amendola, Leone, Manna; Bourhis, Leclère, Mugnier, Thomazo).
- *(frontier — verify)* Connections to **finite-model reasoning for knowledge graphs and SHACL/ontology validation**, where finiteness of the data matters for certain answers.
- Finite controllability under bag semantics and with arithmetic remains largely open.

## 8. Future Work

- Sharp characterization of finite controllability across the Datalog$^\pm$ / guarded landscape.
- Decidable fragments combining keys/functionality with inclusion dependencies.
- Tight complexity of finite implication for frontier-guarded and sticky rules.
- Finite-model reasoning tools usable in ontology-based data access systems.

## 9. Key References

- **[Foundational]** M. A. Casanova, R. Fagin, C. H. Papadimitriou. *Inclusion dependencies and their interaction with functional dependencies.* JCSS, 1984. — [DOI](https://doi.org/10.1016/0022-0000(84)90075-8)
- **[Foundational]** A. K. Chandra, M. Y. Vardi. *The implication problem for functional and inclusion dependencies is undecidable.* SIAM J. Computing, 1985. — [DOI](https://doi.org/10.1137/0214049)
- **[SOTA]** V. Bárány, G. Gottlob, M. Otto. *Querying the guarded fragment.* LICS, 2010 / Logical Methods in Computer Science, 2014. — [arXiv](https://arxiv.org/abs/1309.5822)
- **[SOTA]** R. Rosati. *On the finite controllability of conjunctive query answering in databases under open-world assumption.* JCSS, 2011. — [DOI](https://doi.org/10.1016/j.jcss.2010.04.011)
- **[Foundational]** A. Calì, G. Gottlob, M. Kifer. *Taming the infinite chase (Datalog±).* JAIR, 2013. — [arXiv](https://arxiv.org/abs/1212.3357)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

A classic separation. Take one relation $R(A,B)$ with the FD $B \to A$ and the IND $R[A] \subseteq R[B]$. Claim: every *finite* model satisfies the extra IND $R[B] \subseteq R[A]$, but some *infinite* model does not.

Reason finitely: the IND $R[A]\subseteq R[B]$ gives an injection $\pi_A R \hookrightarrow \pi_B R$ (injectivity from $B\to A$: distinct $B$-values map to distinct $A$-values, so $|\pi_B R| \le |\pi_A R|$, while the IND gives $|\pi_A R| \le |\pi_B R|$). Hence $|\pi_A R| = |\pi_B R|$, and on a *finite* set an injection that is "into" must be *onto*, forcing $R[B] \subseteq R[A]$.

Infinite counterexample: let $A,B$ range over $\mathbb{N}$ with tuples $(n, n+1)$ for all $n \ge 0$. Then $\pi_A R = \mathbb{N}$, $\pi_B R = \{1,2,\dots\}$, so $R[A]\subseteq R[B]$ holds, $B\to A$ holds, yet $0 \in \pi_B$? No — $0 \notin \pi_B R$ while $0 \in \pi_A R$, so $R[B]\subseteq R[A]$ *fails*. Thus $\Sigma \models_{\mathrm{fin}} \sigma$ but $\Sigma \not\models \sigma$: the two notions genuinely diverge for FD+IND.

---
*Part of the [DBMS Research catalog](../../README.md).*
