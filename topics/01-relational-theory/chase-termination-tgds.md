---
id: 01-relational-theory/chase-termination-tgds
title: "Chase Termination for Arbitrary TGDs"
topic: 01-relational-theory
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Chase Termination for Arbitrary TGDs

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/chase-termination-tgds` · **Status:** open

## 1. Problem Statement
Given a finite set $\Sigma$ of tuple-generating dependencies (TGDs), decide whether the chase procedure terminates. Several precise decision variants must be distinguished:

- **All-instances termination (CT$_\forall$):** does every chase sequence terminate on *every* database instance?
- **Some-sequence variant (CT$_\exists$):** does *some* fair chase sequence terminate on every instance?
- **Instance-specific termination:** given $\Sigma$ *and* a fixed instance $I$, does the chase terminate?

These split further by chase variant: the **oblivious** (naive) chase, the **semi-oblivious** (restricted-to-frontier) chase, the **standard/restricted** chase (fire only when the head is not already satisfied), and the **core** chase. Termination of one variant does not imply termination of another, so each induces a distinct decision problem.

## 2. Mathematical Foundations
A TGD has the form $\forall \bar{x}\,\bar{y}\; \big(\varphi(\bar{x},\bar{y}) \rightarrow \exists \bar{z}\; \psi(\bar{x},\bar{z})\big)$, where $\varphi,\psi$ are conjunctions of relational atoms. A **chase step** finds a homomorphism $h:\varphi \to I$ with no extension satisfying $\psi$ (for the restricted chase) and adds $h'(\psi)$, introducing fresh labelled nulls for $\bar{z}$.

The chase computes a **universal model**: if it terminates with result $J$, then for every model $M$ of $\Sigma$ extending $I$ there is a homomorphism $J \to M$. This is the semantic backbone of data exchange and certain-answer computation:
$$\text{cert}(Q, I, \Sigma) = \bigcap_{M \models \Sigma,\, M \supseteq I} Q(M) = Q(\text{chase}_\Sigma(I))_{\downarrow}.$$

Non-termination arises from cyclic existential propagation; analysis rests on **dependency graphs** and **position graphs** tracking how nulls flow into positions across rule firings.

## 3. State of the Art (SOTA)
The general problem is **undecidable** for all standard chase variants (Deutsch–Nash–Remmel 2008; Gogacz–Marcinkowski for the all-instances case). Research therefore targets **sufficient sound conditions** that guarantee termination, organized as a hierarchy of increasing power:

- **Weak acyclicity** (Fagin–Kolaitis–Miller–Popa 2005) — the foundational, polynomial-time-checkable condition.
- **Stratification / safety / super-weak acyclicity** (Deutsch–Nash–Remmel; Meier; Marnette 2009).
- **Acyclic graph of rule dependencies (aGRD)** and the **MFA/MSA** (model-faithful / model-summarizing acyclicity) criteria (Cuenca Grau–Horrocks–Krötzsch–Kupke–Magka–Motik–Wang, 2013), which are among the most general checkable conditions, used in RDFox.

## 4. Upper Bound
When a recognized acyclicity condition holds, the chase terminates and the universal model has size polynomial in $|I|$ for fixed $\Sigma$: $O(|I|^{w})$ where $w$ depends on the dependency width. Weak acyclicity, safety, and super-weak acyclicity are all **PTIME-decidable** as properties of $\Sigma$ (data-independent checks on the position/dependency graph). MFA recognition is decidable but **2EXPTIME**-complete in general. Within these classes, certain-answer evaluation for conjunctive queries is in PTIME (data complexity).

## 5. Lower Bound
The core obstruction is **undecidability**: CT$_\forall$ for the standard chase is undecidable (reduction from Turing-machine halting / word problems); the oblivious and semi-oblivious all-instances variants are also undecidable (Gogacz, Marcinkowski, Pieris and others). Hence no algorithm can decide termination for arbitrary $\Sigma$, and every checkable criterion is necessarily incomplete. Recognizing the most expressive practical class (MFA) is **2EXPTIME-hard**.

## 6. The Gap
The gap is not between matching bounds but between **undecidability** and an ever-growing tower of *sufficient* conditions, none complete. The open question is how far decidable sufficient classes can be pushed and whether a *natural maximal* decidable class exists for restricted-chase termination. For specific subclasses (e.g. single-head TGDs, guarded/sticky fragments) sharper characterizations remain only partially settled.

## 7. Current Research (as of June 2026)
Active work characterizes **restricted (standard) chase** termination, which is subtler than the oblivious case because firing order matters; recent results give decidability for single-head and linear fragments *(frontier — verify)*. Groups around Marcinkowski, Pieris, Gottlob, Krötzsch, and the existential-rules / OBDA community continue refining acyclicity hierarchies and connecting them to **bounded treewidth of the chase**. Combinations with EGDs and equality constraints, and termination *modulo* a query, are active *(frontier — verify)*.

## 8. Future Work
- Tight characterizations of restricted-chase termination for guarded and frontier-guarded TGDs.
- Parameterized and instance-aware termination guarantees.
- Practical "as-general-as-possible" decidable criteria with low recognition cost for reasoners (RDFox, VLog, LLunatic).
- Unified theory linking chase termination, finite controllability, and certain-answer decidability.

## 9. Key References
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* TCS / ICDT, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** A. Deutsch, A. Nash, J. Remmel. *The Chase Revisited.* PODS, 2008. — [ACM](https://dl.acm.org/doi/10.1145/1376916.1376938)
- **[SOTA]** B. Marnette. *Generalized Schema-Mappings: From Termination to Tractability.* PODS, 2009. — [ACM](https://dl.acm.org/doi/10.1145/1559795.1559799)
- **[SOTA]** B. Cuenca Grau, I. Horrocks, M. Krötzsch, C. Kupke, D. Magka, B. Motik, Z. Wang. *Acyclicity Notions for Existential Rules and Their Application to Query Answering in Ontologies.* JAIR, 2013. — [arXiv](https://arxiv.org/abs/1406.4110)
- **[SOTA]** T. Gogacz, J. Marcinkowski. *All-Instances Termination of Chase is Undecidable.* ICALP, 2014. — [DOI](https://doi.org/10.1007/978-3-662-43951-7_25)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Ch. 8–10, chase and dependencies). — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

A single TGD whose chase never terminates, and where restricted vs. oblivious differ. Relation $E(\text{x},\text{y})$, dependency
$$\tau:\ E(x,y)\to\exists z\,E(y,z).$$

**Oblivious chase** on $D=\{E(a,b)\}$ ignores whether the head is already satisfied and fires on *every* trigger:
- $E(a,b)\Rightarrow E(b,n_1)$
- $E(b,n_1)\Rightarrow E(n_1,n_2)$
- $E(n_1,n_2)\Rightarrow E(n_2,n_3)\ \dots$

an infinite chain — non-terminating.

**Restricted (standard) chase** fires only if no extension already satisfies the head. Same start: each new atom $E(n_{i-1},n_i)$ still has *no* outgoing edge from $n_i$, so the head $\exists z\,E(n_i,z)$ is unsatisfied and the chase still runs forever. So here both diverge.

Now add the seed $D'=\{E(a,a)\}$. Restricted chase: trigger on $E(a,a)$ asks for $\exists z\,E(a,z)$ — already witnessed by $z=a$. No fresh fact is added; restricted chase **terminates immediately**, while the oblivious chase still loops. This separation is exactly why each variant induces a distinct, separately undecidable termination problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
