# Termination and Magic-Sets for Existential Rules

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/existential-rules-evaluation` · **Status:** partially-solved

## 1. Problem Statement

*Existential rules* (a.k.a. tuple-generating dependencies, TGDs, or Datalog$^\pm$) are implications $\forall \bar x\,(\varphi(\bar x) \to \exists \bar y\, \psi(\bar x, \bar y))$ that may invent fresh values ("nulls") in the head. They power ontology-mediated query answering (OMQA) over knowledge graphs and incomplete data. Two intertwined problems:

1. **Termination (decision variant):** does the *chase* — the canonical bottom-up procedure that satisfies all rules — terminate on every database (all-instance termination), on a given database, or for a given query? Termination implies a finite universal model and hence decidable, materialization-based answering.
2. **Goal-directed evaluation (optimization variant):** when the chase does *not* terminate or is too large, design **magic-set**-style query rewritings and **goal-directed chase** variants so that only the rule instances *relevant to the query* are fired — combining the efficiency of top-down (SLD-style) reasoning with the completeness of bottom-up chase, while preserving soundness/completeness for *certain answers*.

The status is **partially-solved**: termination is undecidable in general but many sufficient syntactic classes and several decidable cases are known; goal-directed magic-set techniques exist for Datalog and for some Datalog$^\pm$ fragments but are not yet general.

## 2. Mathematical Foundations

Given database $D$ and rule set $\Sigma$, a **homomorphism** $h$ satisfies $\varphi \to \exists \bar y\,\psi$ if every match of $\varphi$ extends to a match of $\psi$. The **chase** repairs violations by adding $\psi$-atoms with fresh nulls for $\bar y$, producing a (possibly infinite) **universal model** $U$: for every model $M$ of $D \cup \Sigma$ there is a homomorphism $U \to M$. Certain answers satisfy
$$\mathrm{cert}(Q, D, \Sigma) = \{\bar a : \bar a \in Q(M)\ \text{for all } M \models D\cup\Sigma\} = Q(U)\big|_{\text{null-free}}.$$

Chase variants — **oblivious**, **semi-oblivious/Skolem**, **restricted (standard)**, **core** — differ in when a rule is "already satisfied" and thus in termination behavior; they form a strict hierarchy of termination.

Decidable / well-behaved classes form lattices: **weak-acyclicity** $\subset$ **joint/super-weak acyclicity** (ensure termination); and orthogonally **guarded**, **frontier-guarded**, **sticky**, **linear**, **warded**, and **shy** TGDs (ensure decidable answering even with non-terminating chase, via bounded-treewidth/forest-model arguments).

## 3. State of the Art (SOTA)

- **Termination criteria:** weak-acyclicity (Fagin–Kolaitis–Miller–Popa 2005), super-weak acyclicity (Marnette 2009), and the **MFA/MSA** (model-faithful/-summarising acyclicity) checks of Cuenca Grau et al. (JAIR 2013), which are the systems-SOTA termination tests.
- **Decidable answering fragments:** Datalog$^\pm$ — guarded (Calì–Gottlob–Lukasiewicz 2009), sticky, linear, and **warded** (the basis of **Vadalog**, VLDB 2018).
- **Goal-directed / magic sets:** classic magic sets for Datalog (Bancilhon–Maier–Sagiv–Ullman 1986); magic-set rewriting for existential rules in **shy** programs / **DLV$^\exists$** and in warded Datalog$^\pm$ (Bellomarini et al.).
- **Systems:** VLog/Rulewerk, RDFox (materialization + restricted chase), Vadalog, GLog/ChaseBench.

## 4. Upper Bound

For all-instance chase termination there is no complete algorithm (see §5), but membership in concrete acyclicity classes is decidable: **MFA/MSA membership is decidable** (and MFA is 2EXPTIME-c-ish in program size in the relevant encoding). For answering: BCQ entailment under **guarded** TGDs is **2EXPTIME-complete** (combined) and EXPTIME for bounded arity; **linear/inclusion-dependency** TGDs give **PSPACE**; **sticky** and **warded** classes give PTIME data complexity, enabling goal-directed magic-set evaluation in polynomial data complexity.

## 5. Lower Bound

- **Chase termination is undecidable.** All-instance termination of the standard chase is undecidable (Deutsch–Nash–Remmel 2008; Gogacz–Marcinkowski 2014 for the core/restricted chase). Even single-instance termination is undecidable.
- **BCQ answering under general TGDs is undecidable** (reduction from the halting problem / unbounded chase).
- Within fragments, matching hardness: guarded-TGD BCQ answering is **2EXPTIME-hard**; the PTIME-data fragments are **P-hard** (inherited from Datalog).

## 6. The Gap

The decidability frontier of termination is essentially mapped, but it is *strictly* below true semantic termination — every sufficient syntactic criterion has terminating programs it rejects, and closing that gap fully is impossible (undecidability). The **practical** gap is the lack of a *general* goal-directed magic-set procedure that is sound and complete for the union of all decidable fragments (guarded $\cup$ sticky $\cup$ warded $\cup$ ...), and that prunes the chase as aggressively as top-down resolution. This is the open, actively-attacked part.

## 7. Current Research (as of June 2026)

- **Restricted-chase termination** characterizations and tighter acyclicity (Karimi–Zhang–You; Krötzsch, Marx, Rudolph). *(frontier — verify)* unified termination criteria spanning chase variants.
- **Existential-rule magic sets at scale** in VLog/Rulewerk and Vadalog, with provenance and incremental maintenance (Dresden group: Krötzsch; Oxford: Cuenca Grau, Horrocks; TU Wien/Bank of Italy: Gottlob, Sallinger).
- **Datalog$^\pm$ for graph/SQL/PGQ reasoning** and combining existential rules with aggregation/negation under stable-model semantics. *(frontier — verify)*

## 8. Future Work

- A complete goal-directed (magic-set) evaluation for warded/frontier-guarded rules.
- Cost-based choice among chase variants and acyclicity-driven materialization.
- Hybrid top-down/bottom-up engines with worst-case-optimal joins inside the chase.

## 9. Key References

- **[Foundational]** Fagin, Kolaitis, Miller, Popa. *Data Exchange: Semantics and Query Answering.* TCS, 2005 (chase, weak acyclicity, universal models).
- **[Foundational]** Bancilhon, Maier, Sagiv, Ullman. *Magic Sets and Other Strange Ways to Implement Logic Programs.* PODS, 1986.
- **[Foundational]** Calì, Gottlob, Lukasiewicz. *A General Datalog-Based Framework for Tractable Query Answering over Ontologies (Datalog$^\pm$).* JWS/PODS, 2009/2012.
- **[SOTA]** Cuenca Grau, Horrocks, Krötzsch, et al. *Acyclicity Notions for Existential Rules and Their Application to Query Answering in Ontologies.* JAIR, 2013.
- **[SOTA]** Bellomarini, Sallinger, Gottlob. *The Vadalog System: Datalog-based Reasoning for Knowledge Graphs.* PVLDB, 2018.
- **[Survey]** Gogacz, Marcinkowski. *All-Instances Termination of Chase is Undecidable.* ICALP, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
