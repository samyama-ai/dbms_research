# Tight Chase-Based Containment Algorithms

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/chase-containment-algorithms` · **Status:** solved-but-impractical

## 1. Problem Statement

**Query containment under constraints** asks whether $Q_1 \sqsubseteq_\Sigma Q_2$: on every database satisfying a set $\Sigma$ of dependencies (TGDs/EGDs), every answer of $Q_1$ is an answer of $Q_2$. The **chase** is the canonical decision tool, and **chase & backchase (C&B)** (Deutsch–Popa–Tannen) is the canonical algorithm for **constraint-aware query reformulation/minimization** — rewriting a query using views, indexes, and integrity constraints to find equivalent, cheaper plans.

The theory is *settled* for well-behaved fragments: containment is decidable, the chase characterizes it, and C&B is **complete** for finding all minimal reformulations. The unsolved part is **engineering**: the chase can explode (or fail to terminate), and C&B's search over the "universal plan" is combinatorially huge. The problem is therefore:

> Make chase-and-backchase containment/reformulation **practical at production query-engine scale** — fast enough, with bounded memory, and integrated into a cost-based optimizer — while preserving completeness (or with characterized, controlled incompleteness).

This is an **optimization/systems** problem layered on a *solved* decision problem.

## 2. Mathematical Foundations

A **TGD** is $\forall\bar x\,(\varphi(\bar x)\to\exists\bar y\,\psi(\bar x,\bar y))$; an **EGD** is $\forall\bar x\,(\varphi(\bar x)\to x_i=x_j)$. The **chase** repairs an instance to satisfy $\Sigma$ by firing active triggers, inventing fresh **labeled nulls** for existentials. The chase of $Q_1$'s frozen body, $\mathrm{chase}_\Sigma(Q_1)$, is a **universal model**:

$$Q_1 \sqsubseteq_\Sigma Q_2 \iff \text{there is a homomorphism } Q_2 \to \mathrm{chase}_\Sigma(Q_1).$$

Termination is guaranteed for **weakly acyclic**, **rich/joint-acyclic**, and **stratified** TGD sets; in general the chase may not terminate and containment is **undecidable**. **C&B** chases $Q$ with $\Sigma$ to build a *universal plan* containing every reformulation, then **backchases** (sub-query enumeration + containment checks) to extract minimal equivalent rewritings. Correctness rests on the chase being a universal model and on **homomorphism testing**. Cost interacts with the **AGM bound** and worst-case-optimal join theory when the reformulations are finally evaluated.

## 3. State of the Art (SOTA)

- **Theory-SOTA**: Deutsch, Popa, Tannen, *Chase & Backchase* (PODS 1999; *VLDBJ* "Reformulation of XML Queries and Constraints" 2006). Onet's chase survey; **core chase** (Deutsch–Nash–Remmel 2008) for minimal universal models; Fagin–Kolaitis–Miller–Popa **data-exchange** chase results.
- **Systems-SOTA**: **PEGASUS / Provenance-aware C&B** (Ileana–Cautis–Deutsch–Katsis, SIGMOD 2014) — *Provenance-Directed C&B* prunes the backchase using provenance, the key practicality leap. **ChaseFUN, Llunatic** (Geerts–Mecca–Papotti–Santoro) and **PDQ** (Benedikt et al., *Proof-Driven Query planning*, 2014–2017) are the leading constraint-driven reformulation/planning engines. **ChaseBench** (Benedikt et al., SIGMOD 2017) is the standard benchmark.

## 4. Upper Bound

- For **weakly-acyclic** $\Sigma$, the chase terminates in time **polynomial in the data but exponential in the schema/dependency size**; containment is decidable in **EXPTIME** (combined), data complexity in **PTIME**.
- For **guarded** TGDs, containment/UCQ-answering is **2ExpTime-complete** (combined), **PTIME** (data).
- C&B explores a universal plan whose size is **worst-case exponential** in the number of constraints/views; **provenance-directed backchase** (Ileana et al.) reduces the practically explored space by orders of magnitude but the worst case stands. Model: standard finite-instance, terminating-chase regime.

## 5. Lower Bound

- **General TGD containment is undecidable** (reduction from the implication/word problem); no algorithm exists outside restricted fragments.
- Even where decidable, containment under TGDs is **2ExpTime-hard** (guarded) and **EXPTIME-hard** for weakly-acyclic sets (combined complexity) — inherent, not conditional.
- The universal-plan / backchase search is **NP-hard** even per-reformulation (subquery minimization ≈ CQ minimization, Chandra–Merlin). These are classical hardness results bounding any complete C&B implementation.

## 6. The Gap

The **decision-theoretic gap is closed** for the standard fragments — chase characterizes containment and C&B is complete. What remains is the **theory-to-practice gap**: the algorithms are *correct but exponential*, so the open work is reducing the *typical-case* and *parameterized* cost — provenance pruning, incremental/parallel chase, cost-aware early termination, and tight integration with cardinality estimation — without sacrificing completeness. Hence **solved-but-impractical**: we know how to decide it, we cannot always afford to. Closing the practical gap means parameterized/output-sensitive C&B with guarantees and engine-grade implementations.

## 7. Current Research (as of June 2026)

- **Benedikt, Bourhis, Leblay, ten Cate, Tsamoura**: **PDQ** and proof-driven planning; **interpolation-based** reformulation (Beth definability) as an alternative to brute C&B. *(frontier — verify)*
- **Deutsch, Cautis, Ileana**: scaling provenance-directed C&B; incremental reformulation under evolving constraints.
- **Geerts, Mecca, Papotti, Santoro**: parallel/database-grounded chase engines (**Llunatic**, **ChaseFUN**) and ChaseBench-driven optimization.
- **Pieris, Gottlob, Calautti**: chase termination analysis and bounded fragments enabling reformulation at scale.
- Worst-case-optimal-join evaluation of the chosen reformulations.

## 8. Future Work

- **Output-sensitive / parameterized** C&B with provable practicality on real schemas.
- **Cost-integrated** reformulation: fuse backchase with the optimizer's cost model and cardinality estimator.
- **Incremental & parallel** chase for streaming constraints and large warehouses.
- Bridging **interpolation-based** and **chase-based** reformulation; completeness guarantees with controlled approximation.

## 9. Key References

- **[Foundational]** Deutsch, A., Popa, L., Tannen, V. *Physical Data Independence, Constraints, and Optimization with Universal Plans (Chase & Backchase).* VLDB, 1999.
- **[Foundational]** Fagin, R., Kolaitis, P.G., Miller, R.J., Popa, L. *Data Exchange: Semantics and Query Answering.* ICDT / TCS, 2005.
- **[SOTA]** Ileana, I., Cautis, B., Deutsch, A., Katsis, Y. *Complete Yet Practical Search for Minimal Query Reformulations under Constraints.* SIGMOD, 2014.
- **[SOTA]** Benedikt, M., Leblay, J., Tsamoura, E. *Querying with Access Patterns and Integrity Constraints (PDQ).* PVLDB, 2015.
- **[SOTA]** Benedikt, M., Konstantinidis, G., Mecca, G., et al. *Benchmarking the Chase (ChaseBench).* SIGMOD, 2017.
- **[Survey]** Onet, A. *The Chase Procedure and Its Applications in Data Exchange.* Data Exchange, Integration, and Streams, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
