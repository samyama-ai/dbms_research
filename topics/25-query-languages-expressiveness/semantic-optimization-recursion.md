# Semantic Query Optimization with Recursion

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/semantic-optimization-recursion` · **Status:** open

## 1. Problem Statement

*Semantic query optimization* (SQO) rewrites a query using the database's integrity constraints (keys, foreign keys, functional dependencies, inclusion dependencies, denial constraints, general tuple- and equality-generating dependencies) to produce a semantically equivalent query that is cheaper to evaluate. For non-recursive conjunctive queries this is well understood; the open problem is **SQO in the presence of recursion** — i.e., for Datalog and Datalog with negation/aggregation — where the goal is to *provably and automatically* rewrite or prune recursive programs given a constraint set $\Sigma$.

Variants:
- **Decision variant:** given recursive query $Q$, constraints $\Sigma$, and candidate rewrite $Q'$, is $Q \equiv_\Sigma Q'$ (equivalent on all databases satisfying $\Sigma$)?
- **Optimization variant:** find the cost-minimal $Q'$ with $Q \equiv_\Sigma Q'$ under a cost model.
- **Pruning variant:** identify rules/atoms that fire no useful tuples on any $\Sigma$-model, and remove them or add constraint-derived selections/joins that bound the recursion (e.g. proving a transitive-closure recursion is actually acyclic, or bounded, under $\Sigma$).

## 2. Mathematical Foundations

A Datalog program $P$ defines a monotone operator $T_P$ whose least fixpoint $\mathrm{lfp}(T_P)$ is the answer. Constraints are dependencies: a TGD has the form $\forall \bar x\,(\varphi(\bar x) \to \exists \bar y\, \psi(\bar x,\bar y))$; an EGD enforces equalities. Semantic equivalence is $Q \equiv_\Sigma Q' \iff \forall D \models \Sigma:\ Q(D)=Q'(D)$.

The core tool is the **chase**: $\mathrm{chase}_\Sigma(Q)$ repairs the canonical (frozen) instance of $Q$ to satisfy $\Sigma$. For CQs, $Q \sqsubseteq_\Sigma Q'$ iff there is a homomorphism $\mathrm{chase}_\Sigma(Q') \to \mathrm{chase}_\Sigma(Q)$ — the *chase-and-backchase* characterization. Recursion breaks the finiteness this relies on: $Q$ is itself a fixpoint, so containment $P \sqsubseteq_\Sigma P'$ of Datalog programs is **undecidable** in general (already $\Sigma = \emptyset$ Datalog containment is undecidable, Shmueli 1993). The research target is identifying decidable fragments and sound (if incomplete) rewrite rules where $\mathrm{chase}_\Sigma$ over a recursive program terminates or admits a *bounded* representation.

Key notions: **boundedness** (does $P$ collapse to a non-recursive UCQ?), **uniform equivalence**, and constraint-induced **acyclicity** of the dependency/precedence graph.

## 3. State of the Art (SOTA)

- **Chase & Backchase** (Deutsch, Popa, Tannen, PODS 1999; the *Chase & Backchase* algorithm) — complete SQO for CQs/UCQs under embedded dependencies; the foundation everyone extends.
- **Boundedness:** undecidable for general Datalog (Gaifman–Mairson–Sagiv–Vardi 1987/1993) but decidable for monadic and for linear Datalog — these results bound when recursion is removable.
- Constraint-aware Datalog reasoning in **Vadalog** (Bellomarini, Gottlob, Sallinger, VLDB 2018) and **LogicBlox** integrate dependencies operationally.
- **Magic-set + constraint pushing** in modern systems (Soufflé, RecStep) is the systems-SOTA but is heuristic, not "provable" SQO.

## 4. Upper Bound

For SQO over **non-recursive** CQ/UCQ under weakly-acyclic TGDs+EGDs, chase termination is guaranteed and chase-and-backchase gives a complete (doubly-exponential in the worst case) algorithm. For recursive programs, the best general guarantee is restricted to **bounded** or **guarded/sticky** Datalog$^\pm$ fragments where query answering under TGDs is decidable: 2EXPTIME-complete for guarded TGDs (Calì–Gottlob–Kifer), EXPTIME for linear/inclusion-dependency cases. These give a constructive (worst-case exponential) rewrite-and-prune procedure within those fragments.

## 5. Lower Bound

- **Datalog equivalence/containment is undecidable** (Shmueli 1987/1993) — so unrestricted recursive SQO is undecidable.
- **Boundedness is undecidable** for general Datalog (GMSV).
- Query answering under general TGDs is undecidable (the chase need not terminate); even checking chase termination for a *fixed* instance is undecidable (Deutsch–Nash–Remmel 2008).
- Within decidable fragments, hardness is high: guarded-TGD answering is **2EXPTIME-hard** (Calì–Gottlob–Kifer 2013).

## 6. The Gap

The gap is **qualitative, not just quantitative**: in the unrestricted case there is a hard undecidability barrier, so no algorithm can be both sound and complete. The genuinely open problem is to carve out the *largest practically useful fragment* of recursive queries + constraint classes for which provable, automatic SQO (especially recursion-pruning and acyclicity detection) is decidable and tractable — and to give sound-but-incomplete rewrite systems with cost-model guarantees outside it. This is open.

## 7. Current Research (as of June 2026)

- Constraint-aware reasoning at scale in the **Vadalog/Warded Datalog$^\pm$** line (Gottlob, Sallinger, Bellomarini) — extending termination and rewriting guarantees to richer ontological constraints. *(frontier — verify)* recent work on cost-based selection among provably-equivalent chase-rewrites.
- **Provenance-guided pruning** of recursive programs and incremental/differential Datalog SQO (groups around Soufflé and around DDlog/Differential Dataflow).
- Decidable SQO for **recursive queries over knowledge graphs** under existential rules (*(frontier — verify)* — integration with PG-Keys / SQL/PGQ recursive path constraints).

## 8. Future Work

- Tight characterization of recursion-removability ("semantic boundedness") under common SQL constraint sets.
- Cost-aware chase-and-backchase that ranks equivalent rewrites by an actual optimizer cost model.
- Integrating SQO with worst-case-optimal join recursion and with SQL/PGQ recursive path queries.

## 9. Key References

- **[Foundational]** Deutsch, Popa, Tannen. *Physical Data Independence, Constraints, and Optimization with Universal Plans.* VLDB, 1999 (Chase & Backchase). — [DBLP](https://dblp.org/rec/conf/vldb/DeutschPT99.html)
- **[Foundational]** Gaifman, Mairson, Sagiv, Vardi. *Undecidable Optimization Problems for Database Logic Programs.* JACM, 1993. — [DOI](https://doi.org/10.1145/174130.174142)
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (chase, Datalog, dependencies). — [book](http://webdam.inria.fr/Alice/)
- **[SOTA]** Calì, Gottlob, Kifer. *Taming the Infinite Chase: Query Answering under Expressive Relational Constraints.* JAIR, 2013. — [DOI](https://doi.org/10.1613/jair.3873)
- **[SOTA]** Bellomarini, Gottlob, Sallinger. *The Vadalog System: Datalog-based Reasoning for Knowledge Graphs.* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3213880.3213888)
- **[Survey]** Deutsch, Nash, Remmel. *The Chase Revisited.* PODS, 2008. — [DOI](https://doi.org/10.1145/1376916.1376938)

## 10. Worked Example

Consider the transitive-closure program $P$ over an edge relation $\mathsf{E}$:

$$
\mathsf{tc}(x,y) \leftarrow \mathsf{E}(x,y) \qquad
\mathsf{tc}(x,y) \leftarrow \mathsf{E}(x,z),\,\mathsf{tc}(z,y)
$$

and the query $Q$: $\mathsf{ans}(x,y)\leftarrow \mathsf{tc}(x,y)$. Naively, $\mathrm{lfp}(T_P)$ may iterate up to $n-1$ times on an $n$-node graph.

Now add the constraint $\Sigma$: a denial constraint asserting $\mathsf{E}$ is **acyclic and of depth $\le 1$** — operationally, "every edge target is a sink," i.e. $\mathsf{E}(x,z)\wedge \mathsf{E}(z,y)\to \bot$. Under any $D\models\Sigma$, the recursive rule's body $\mathsf{E}(x,z),\mathsf{tc}(z,y)$ can only fire via $\mathsf{tc}(z,y)=\mathsf{E}(z,y)$ at the base, and then $\mathsf{E}(x,z),\mathsf{E}(z,y)$ is unsatisfiable. So the recursive rule contributes nothing.

**Pruning result:** $P \equiv_\Sigma P'$ where $P'$ is the non-recursive $\mathsf{tc}(x,y)\leftarrow\mathsf{E}(x,y)$. We have *semantically removed recursion* — $P$ is bounded under $\Sigma$ even though it is unbounded with $\Sigma=\emptyset$. Evaluation drops from up to $n-1$ semi-naïve rounds to a single scan, $O(|\mathsf{E}|)$.

The catch the topic flags: deciding such removability for *arbitrary* $\Sigma$ is undecidable (boundedness is undecidable, GMSV), so only restricted constraint classes admit an automatic prover.

---
*Part of the [DBMS Research catalog](../../README.md).*
