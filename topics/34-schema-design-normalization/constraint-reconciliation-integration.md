# Cross-Schema Constraint Reconciliation in Integration

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/constraint-reconciliation-integration` · **Status:** partially-solved

## 1. Problem Statement
Given two (or more) independently designed schemas $\mathcal{S}_1,\mathcal{S}_2$ — each with its own keys, functional dependencies (FDs), inclusion dependencies (INDs), and achieved normal forms — plus a set of correspondences/mappings $M$ between them, **reconcile** their constraints so that the integrated or mediated schema has a consistent, non-contradictory constraint set, and **propagate** constraints across $M$.

- **Decision variant:** Is the union of mapped constraints *satisfiable* (does any instance satisfy all of them)? Equivalently, is the constraint set consistent under the chase?
- **Propagation variant:** Given source constraints and a mapping (e.g., GLAV/tgds), compute the constraints *entailed* on the target schema.
- **Optimization variant:** When constraints conflict, find a minimum-cost repair (drop/relax the fewest constraints, or weaken a key to a "soft" key) restoring consistency while maximizing preserved normalization (BCNF/3NF).

This sits between schema matching (finding $M$) and schema mapping (using $M$): even with $M$ given, deciding which keys/FDs survive and propagate is hard.

## 2. Mathematical Foundations
Constraints are embedded dependencies: FDs and keys are **equality-generating dependencies (egds)**; INDs and referential constraints are **tuple-generating dependencies (tgds)**. Mappings are typically **source-to-target tgds** (GLAV). The canonical reasoning tool is the **chase**: a constraint set $\Sigma$ is consistent iff the chase of a representative instance does not fail (an egd forcing $a=b$ for distinct constants).

Key facts the problem rests on: implication for FDs is **linear-time** (closure / Armstrong axioms); for FDs+INDs together, finite implication is **undecidable** (Chandra–Vardi); IND implication alone is **PSPACE-complete**. Mapping composition of GLAV mappings may require **second-order tgds** to be closed (Fagin–Kolaitis–Popa–Tan), so propagated constraints can exceed first-order expressivity. Certain-answer semantics over the integrated schema is defined via the universal solution produced by the chase.

Constraint *propagation* across a mapping $m: \mathcal{S}_1 \to \mathcal{S}_2$ asks: which FDs/keys on $\mathcal{S}_1$ induce FDs/keys on $\mathcal{S}_2$? This is the "dependency implication problem for views" — decidable and PTIME for projections but undecidable in general for FD+IND view definitions.

## 3. State of the Art (SOTA)
**Theory-SOTA.** The **Clio / ++Spicy** mapping lineage (Fagin, Haas, Hernández, Miller, Popa, Tan) established data exchange with universal solutions and core computation; **mapping composition** and **inversion** (Fagin et al., 2005–2009) give the algebra for chaining and reconciling. **Schema mapping with target egds/tgds** and consistency checking via the chase is the foundational SOTA.

**Systems-SOTA.** **++Spicy** and **Llunatic** (Geerts, Mecca, Papotti, Santoro) handle data-exchange + cleaning with conflicting constraints, computing repairs. **HoloClean** (Ré et al., 2017) reconciles constraints/data probabilistically. Commercial integration (Informatica, Talend) reconciles keys heuristically. Recent constraint-aware integration leans on **denial constraints** discovered jointly (Hydra, DCFinder) to find the surviving constraints empirically.

## 4. Upper Bound
Consistency of a weakly-acyclic set of tgds+egds is decidable and the chase terminates in **polynomial time in the data** (Fagin–Kolaitis–Miller–Popa, 2005), giving PTIME data complexity for certain answers of conjunctive queries. FD-only reconciliation (merge of two FD sets, compute closure, detect a violated key) is **$O(|\Sigma|\cdot n)$**. Minimum-repair under denial constraints is solved via MaxSAT/ILP — exponential worst case but practically tractable on discovered constraint sets.

## 5. Lower Bound
The general reconciliation problem inherits **undecidability** from finite implication of FDs+INDs (Chandra–Vardi, 1985), so no algorithm can decide consistency of an arbitrary mapped FD+IND set. Restricted to INDs, implication (hence reconciliation of referential constraints) is **PSPACE-complete** (Casanova–Fagin–Papadimitriou, 1984). Minimum constraint repair generalizes **minimum vertex cover / weighted MaxSAT** and is **NP-hard and APX-hard**. Chase termination itself is undecidable for unrestricted tgds, so propagation has no general terminating procedure outside acyclicity-style restrictions.

## 6. The Gap
For **decidable fragments** (weakly acyclic tgds, FD-only, bounded INDs) the picture is essentially closed — PTIME data complexity, known combined complexity. The genuine gap is the **practical middle**: real schemas mix FDs and INDs (undecidable in full generality), so systems use sound-but-incomplete reasoning. Partially solved because we have exact algorithms for clean fragments but no complete, terminating method for arbitrary mixed constraints, and repair-quality (which constraint to drop) lacks principled objectives.

## 7. Current Research (as of June 2026)
Active threads: (1) **denial-constraint and approximate-FD discovery** feeding reconciliation, so constraints are mined then merged rather than assumed (HPI, Naumann; Livshits–Kimelfeld on minimal repairs); (2) **LLM-assisted correspondence + constraint suggestion** for entity/attribute matching with explanations *(frontier — verify)*; (3) knowledge-graph / RDF integration where constraints become SHACL shapes that must be reconciled; (4) probabilistic/soft keys (HoloClean lineage) replacing hard reconciliation. Groups: Miller (Northeastern), Kolaitis (UCSC), Mecca–Papotti (++Spicy), Kimelfeld–Livshits (repairs).

## 8. Future Work
- Practical complete reasoning for useful FD+IND fragments narrower than the undecidable full class.
- Principled, cost-aware repair objectives (preserve normalization, minimize information loss).
- Reconciliation under uncertainty (probabilistic mappings + soft constraints) with guarantees.
- Incremental reconciliation as new sources join a data lake.

## 9. Key References
- **[Foundational]** Fagin, R., Kolaitis, P., Miller, R.J., Popa, L. *Data Exchange: Semantics and Query Answering.* ICDT 2003 / TCS, 2005.
- **[Foundational]** Chandra, A., Vardi, M. *The Implication Problem for Functional and Inclusion Dependencies is Undecidable.* SIAM J. Comput., 1985.
- **[Foundational]** Fagin, R., Kolaitis, P., Popa, L., Tan, W.C. *Composing Schema Mappings: Second-Order Dependencies to the Rescue.* PODS 2004 / TODS, 2005.
- **[SOTA]** Geerts, F., Mecca, G., Papotti, P., Santoro, D. *That's All Folks! LLUNATIC Goes Open Source.* PVLDB, 2014.
- **[SOTA]** Rekatsinas, T., Chu, X., Ilyas, I., Ré, C. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* PVLDB, 2017.
- **[Survey]** Doan, A., Halevy, A., Ives, Z. *Principles of Data Integration.* Morgan Kaufmann, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
