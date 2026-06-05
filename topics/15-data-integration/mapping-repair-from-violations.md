# Mapping Repair From Constraint Violations

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/mapping-repair-from-violations` · **Status:** open

## 1. Problem Statement

A schema mapping $M$ (a set of source-to-target dependencies) exchanges data from a source schema $\mathbf{S}$ to a target $\mathbf{T}$. After the chase, the materialized target may **violate target constraints** $\Sigma_T$ (keys, EGDs, denial constraints) or **disagree with user feedback** (labeled tuples that should/should not appear). The **mapping-repair problem** asks for a **minimally revised** mapping $M'$ such that the exchanged data satisfies $\Sigma_T$ and is consistent with feedback, where "minimal" is measured by an edit distance on the mapping (added/removed/weakened dependencies, modified atoms).

Variants:

- **Decision:** does a repair of cost $\le k$ exist?
- **Optimization:** find a minimum-cost repair.
- **Feedback-driven (refinement):** given accept/reject labels on target tuples, revise $M$ to maximize agreement — a learning-flavored objective.
- **Instance-repair vs. mapping-repair:** repair the *data* (classic database repair) versus repair the *mapping* (the generator of all future data). This page is the latter, which is strictly harder because one mapping edit affects unboundedly many instances.

## 2. Mathematical Foundations

A GLAV mapping is a set of TGDs $\forall \mathbf{x}\, (\varphi_\mathbf{S}(\mathbf{x}) \to \exists \mathbf{y}\, \psi_\mathbf{T}(\mathbf{x},\mathbf{y}))$. Semantics is the set of **solutions** $\mathrm{Sol}_M(I)$; the **certain answers** are $\bigcap_{J \in \mathrm{Sol}} q(J)$. Repair is **belief revision** over the logical theory $M \cup \Sigma_T$: a target EGD violated by the chase signals an inconsistency between what $M$ generates and what $\Sigma_T$ demands.

Two formal anchors:

1. **AGM-style minimal change** — repairs should change as little as possible (Alchourrón–Gärdenfors–Makinson), inducing a partial order on candidate $M'$ and a notion of *minimal mutilation*.
2. **The chase as the consistency oracle** — $M'$ is feasible iff the chase of every source instance under $M' \cup \Sigma_T$ terminates without EGD failure; this couples repair to **chase termination** (itself undecidable in general).

Feedback-driven refinement connects to **PAC/ILP learning of GLAV mappings** (ten Cate–Dalmau–Kolaitis): each labeled tuple is a constraint on the hypothesis mapping; the goal is a consistent hypothesis of minimal complexity (Occam/MDL).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Learnability of schema mappings: **ten Cate, Dalmau, Kolaitis** (TODS 2013, *Learning Schema Mappings*) characterize when GAV/GLAV mappings are exactly/PAC learnable from data examples. Gottlob–Senellart (JACM 2010) define mapping **cost / validity / repair** with a complexity census.
- **Systems-SOTA.** Interactive mapping design tools — **Clio** (IBM), **++Spicy / ?Spicy** (Mecca–Papotti–Bonifati), and **Muse** (Alexe–ten Cate–Kolaitis–Tan) — refine mappings from user-chosen data examples. **EIRENE** (Alexe et al.) derives mappings from ground data examples (a repair-by-example primitive). Cleaning systems (**LLunatic**, **HoloClean**) repair instances against EGDs/DCs but stop short of repairing the mapping.

## 4. Upper Bound

For **GAV** mappings (no existentials) over fixed target EGDs, checking whether a bounded-size repair exists is in **NP** (guess the edit, verify on a representative/critical instance), and the optimization is **FPNP**-style. Repair-by-example with a *finite* set of ground examples reduces to consistent-hypothesis search: for GAV, polynomial-size fitting mappings can be computed when one exists (ten Cate–Dalmau–Kolaitis). When the chase is guaranteed to terminate (e.g., weakly acyclic $M' \cup \Sigma_T$), feasibility checking is decidable in **coNP/Π₂ᵖ data-to-combined** ranges depending on the dependency class.

## 5. Lower Bound

- **NP-hardness:** minimum mapping repair embeds minimum-cost database repair under denial constraints, which is **NP-hard** (Lopatenko–Bertossi; Afrati–Kolaitis). Even **deciding existence** of a consistent GLAV mapping fitting a set of examples is **coNP-hard / Π₂ᵖ-hard** for richer classes (ten Cate–Kolaitis–Pichler–Wu).
- **Undecidability:** because target EGDs can make the chase non-terminating, deciding whether an arbitrary GLAV $M'$ even *has* a consistent target for all sources inherits **undecidability** from chase termination (Gogacz–Marcinkowski) and from GLAV mapping-composition/inverse undecidability (Fagin–Kolaitis–Popa–Tan).
- The feedback-maximization variant generalizes agnostic learning, so optimal refinement is hard to approximate in the worst case.

## 6. The Gap

This is **genuinely open**. There is no algorithm that, for full GLAV with arbitrary target EGDs, computes a minimal repair with a guarantee — the problem straddles the undecidability frontier of the chase and the hardness of belief revision. The closed islands are narrow (GAV, terminating chase, finite ground examples). Closing the gap means either (i) identifying the largest mapping/constraint fragment with a decidable, ideally tractable, minimal-repair algorithm, or (ii) proving sharp undecidability/inapproximability boundaries and falling back to principled heuristics with quality certificates.

## 7. Current Research (as of June 2026)

Active threads: **interactive, example-and-feedback-driven** mapping refinement (Kolaitis/ten Cate/Tan lineage), and **fitting algorithms for GAV/GLAV** with succinctness guarantees (ten Cate, Funk, Jung, Lutz on *separability* and *fitting*). *(frontier — verify)* 2024–2025 work brings **LLM-proposed mapping edits** validated against constraint violations, and **active-learning loops** that pick maximally informative example tuples to label. *(frontier — verify)* Cross-pollination with **ontology/KG mapping repair** (DL-Lite mapping repair, Bienvenu–Bourgaux) is a notable frontier.

## 8. Future Work

- A complete complexity classification of minimal mapping repair by (mapping class × target-constraint class × cost metric).
- Repair operators that preserve **certain-answer** semantics, not just constraint satisfaction.
- Anytime repair with approximation/quality certificates under non-terminating chase.
- Unified treatment of instance-repair and mapping-repair (when to fix data vs. generator).

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Composing Schema Mappings: Second-Order Dependencies to the Rescue.* TODS, 2005.
- **[Foundational]** G. Gottlob, P. Senellart. *Schema Mapping Discovery from Data Instances.* JACM, 2010.
- **[SOTA]** B. ten Cate, V. Dalmau, P. Kolaitis. *Learning Schema Mappings.* ACM TODS, 2013.
- **[SOTA]** B. Alexe, B. ten Cate, P. Kolaitis, W.-C. Tan. *Designing and Refining Schema Mappings via Data Examples (Muse / EIRENE).* SIGMOD, 2011.
- **[SOTA]** B. Marnette, G. Mecca, P. Papotti, S. Raunich, D. Santoro. *++Spicy: an Open-Source Tool for Second-Generation Schema Mapping and Data Exchange.* PVLDB, 2011.
- **[Survey]** P. Kolaitis. *Schema Mappings, Data Exchange, and Metadata Management.* PODS keynote/survey, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
