---
id: 15-data-integration/chase-termination-decidability
title: "Chase Termination Decidability Gap"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Chase Termination Decidability Gap

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/chase-termination-decidability` · **Status:** open

## 1. Problem Statement

The **chase** is the workhorse of data exchange and dependency reasoning: given an instance $D$ and a set $\Sigma$ of TGDs/EGDs, it repeatedly enforces unsatisfied dependencies by adding facts (introducing fresh nulls for existentials), producing a universal solution. The **chase-termination problem** asks whether this process halts.

Several distinct decision problems must be separated:

- **CT$_{\forall}$ (all-instances):** does the chase terminate for **every** input instance $D$?
- **CT$_{\exists}$ / data-dependent:** does it terminate for a **given** instance $D$?
- per **chase variant**: *oblivious*, *semi-oblivious (Skolem)*, *restricted (standard)*, *core* chase — each with possibly different termination behavior.

The open problem: **close the gap** between known *sufficient* acyclicity conditions (which guarantee termination) and the exact **(semi-)decidability frontier** — i.e., characterize precisely which $(\Sigma)$ or $(\Sigma, D)$ pairs admit a terminating chase, and determine the exact complexity/decidability status of each variant.

## 2. Mathematical Foundations

A TGD fires when a homomorphism from its body into the instance has no extension to its head. The **oblivious** chase fires on every trigger; the **restricted** chase fires only when the head is not already (homomorphically) satisfied; the **core** chase computes the core after each round.

Sufficient termination conditions form a hierarchy of **acyclicity** notions analyzing the *dependency graph* of how nulls propagate:
$$\text{weak acyclicity} \subsetneq \text{safety} \subsetneq \text{super-weak acyclicity} \subsetneq \text{(model-faithful / acyclic GRD)} \dots$$
**Weak acyclicity** (Fagin–Kolaitis–Miller–Popa) forbids cycles through "existential" positions in the position dependency graph, guaranteeing a **polynomial-size** chase. Richer notions (**inductive restriction, super-weak acyclicity** of Marnette; **MFA/MSA** — model-faithful/model-summarizing acyclicity of Grau et al.) capture strictly more terminating sets but are all merely **sufficient**, never exact.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Marnette (PODS 2009) introduced super-weak acyclicity and Skolem (semi-oblivious) chase analysis. **Grahne–Onet** and **Gogacz–Marcinkowski** delivered the deepest undecidability results: Gogacz & Marcinkowski (LICS 2014) proved **all-instance termination of the chase is undecidable**. Grau et al. (JAIR 2013) systematized MFA/MSA. Calautti–Gottlob–Pieris studied data-dependent termination.
- **Systems-SOTA.** **RDFox** uses MFA-style checks for safe materialization; **LLunatic** (Geerts–Mecca–Papotti–Santoro) implements core/restricted chase for data exchange and cleaning; **Graal**, **VLog/Rulewerk** (TU Dresden) implement the restricted/Skolem chase with acyclicity front-ends.

## 4. Upper Bound

When a sufficient acyclicity condition holds (weakly acyclic, safe, super-weakly acyclic, MFA), the chase terminates and produces a universal solution of **polynomial size in data** (combined: exponential). Checking weak acyclicity itself is **PTime**; checking MFA/MSA is decidable but can be **2ExpTime**. For the **semi-oblivious / Skolem** chase, *all-instance* termination is **decidable** for restricted classes (e.g., single-head, or guarded) and reducible to monadic emptiness in those cases.

## 5. Lower Bound

The general results are **negative**:

- **CT$_{\forall}$ for the restricted (standard) chase is undecidable** (Gogacz–Marcinkowski, LICS 2014; Grahne–Onet).
- All-instance termination of the **oblivious** and **semi-oblivious** chase is also undecidable in general (reductions from the halting/Turing-machine tiling problems via TGD encodings).
- Even **data-dependent** termination (given $D$) is undecidable in general.

These rely on encoding Turing-machine computations in null-propagation, making the frontier inherently $\Pi^0_1$/$\Sigma^0_1$ in the arithmetical hierarchy rather than within PTime/NP.

## 6. The Gap

The gap is **genuinely open and partly provably unbridgeable**: a *complete* decidable characterization of restricted-chase termination cannot exist (undecidability). The real research question is therefore **where exactly** the decidable/undecidable boundary lies for **structured fragments** (guarded, sticky, single-head, linear) and **which chase variant** is easiest. Notably, restricted vs. semi-oblivious termination differ (one may halt while the other diverges), and the precise relationship — and the exact arithmetical-hierarchy level of each CT problem per fragment — is incompletely mapped.

## 7. Current Research (as of June 2026)

Active threads: **fairness and order-dependence** of the restricted chase (does a *fair* strategy terminating imply *all* strategies terminate?) — partial answers by Grahne–Onet and by Gogacz–Marcinkowski–Pieris. *(frontier — verify)* Recent ICDT/PODS 2025 work refines **bounded-derivation-depth** and **"chase-step counting"** semi-decision procedures, and explores **restricted-chase termination for guarded and frontier-guarded TGDs** as a decidable island. *(frontier — verify)* The VLog/Rulewerk and RDFox teams pursue *runtime* termination guards and incremental rematerialization.

## 8. Future Work

- Exact decidability classification per chase variant for guarded/sticky/linear fragments.
- Resolve the **fairness conjecture** for the restricted chase fully.
- Practical *anytime* chase with provable progress and early non-termination detection.
- Unifying TGD+EGD termination (EGDs can both accelerate and break termination).

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005. (Weak acyclicity.) — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** B. Marnette. *Generalized schema-mappings: from termination to tractability.* PODS, 2009. (Super-weak acyclicity, Skolem chase.) — [DOI](https://doi.org/10.1145/1559795.1559799)
- **[SOTA]** T. Gogacz, J. Marcinkowski. *All-Instances Termination of Chase is Undecidable.* ICALP/LICS, 2014. — [DOI](https://doi.org/10.1007/978-3-662-43951-7_25)
- **[SOTA]** B. C. Grau, I. Horrocks, M. Krötzsch, C. Kupke, D. Magka, B. Motik, Z. Wang. *Acyclicity Notions for Existential Rules and Their Application to Query Answering in Ontologies.* JAIR, 2013. (MFA/MSA.) — [arXiv](https://arxiv.org/abs/1406.4110)
- **[SOTA]** F. Geerts, G. Mecca, P. Papotti, D. Santoro. *That's All Folks! LLUNATIC Goes Open Source.* VLDB, 2014. (Chase engine.) — [DOI](https://doi.org/10.14778/2733004.2733031)
- **[Survey]** M. Calautti, G. Gottlob, A. Pieris. *Chase Termination for Guarded Existential Rules.* PODS, 2015. — [DOI](https://doi.org/10.1145/2745754.2745773)

## 10. Worked Example

A single TGD that creates an infinite oblivious chase but a terminating *restricted* chase, showing the variants diverge.
$$\Sigma:\quad P(x,y) \rightarrow \exists z\; P(y,z).$$
Start from $D = \{P(a,b)\}$.

**Oblivious chase** fires on *every* trigger regardless of satisfaction:
$$P(a,b) \Rightarrow P(b,n_1) \Rightarrow P(n_1,n_2) \Rightarrow P(n_2,n_3) \Rightarrow \dots$$
Each new fact $P(\cdot, n_i)$ is itself a fresh trigger, so the chase **never halts** — an infinite chain.

**Restricted (standard) chase** fires only if the head is not *already* satisfiable. After producing $P(b,n_1)$, when the trigger $P(b,n_1)$ asks for some $z$ with $P(n_1,z)$, no such fact exists yet, so it fires once more producing $P(n_1,n_2)$ — this particular $\Sigma$ still diverges, but a small change ($P(x,y)\rightarrow \exists z\,P(z,x)$ with a reflexive seed) makes the restricted chase halt while oblivious loops.

**Position dependency graph:** the existential position $P[2]$ feeds the universal position $P[1]$ of the same rule via the join on $y$ — a cycle *through an existential position*, so the set is **not weakly acyclic**, correctly predicting possible non-termination.

---
*Part of the [DBMS Research catalog](../../README.md).*
