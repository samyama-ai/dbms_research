# Holistic Multi-Constraint Repair

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/holistic-multi-constraint-repair` · **Status:** partially-solved

## 1. Problem Statement

Real datasets violate **multiple heterogeneous constraint types simultaneously** — functional dependencies (FDs), conditional FDs (CFDs), denial constraints (DCs), matching dependencies (MDs), inclusion/foreign-key dependencies, and external master-data rules. Repairing them **constraint-by-constraint** is order-dependent and can loop or oscillate: fixing one constraint reintroduces violations of another. **Holistic repair** asks for a *single joint* repair that resolves all constraints together while minimizing cost and respecting value plausibility.

Variants:
- **Decision:** Is there a joint repair of cost $\le k$ satisfying $\Sigma = \Sigma_{FD}\cup\Sigma_{CFD}\cup\Sigma_{DC}\cup\dots$?
- **Optimization:** Minimum-cost joint repair.
- **Interaction analysis:** Determine when constraints interact (share cells/tuples) and whether the joint problem decomposes.

## 2. Mathematical Foundations

The unifying abstraction is a **conflict hypergraph** $H = (V, E)$ where $V$ is the set of *cells* (not tuples) and each hyperedge is a minimal violation of *any* constraint in $\Sigma$, regardless of type (Chu et al. 2013). A repair is a value assignment to cells that hits/resolves every hyperedge — generalizing **minimum hitting set / weighted vertex cover** to a heterogeneous hyperedge family. Because constraints of different types can touch the same cell, resolving them jointly = solving one global optimization rather than a sequence.

Key formalizations:
- **Cell groups / equivalence classes** of cells forced to share a value (LLUNATIC's *cell groups*), giving a partial order of preference and a lattice of repairs.
- **MAP inference** in a factor graph mixing all constraint types plus statistical priors (HoloClean), making the problem a unified probabilistic optimization.
- **Chase**-based unification: all constraint types compiled into a single set of tuple-generating / equality-generating dependencies with a cost-managed chase.
- Interaction is captured by hyperedge overlap; if the hypergraph is **disconnected**, the problem decomposes per component (a treewidth/component-based FPT handle).

## 3. State of the Art (SOTA)

- **Holistic Data Cleaning** (Chu, Ilyas, Papotti, ICDE 2013): the first to put *all* DC-expressible violations into one conflict hypergraph and repair via a single minimum-vertex-cover-style optimization — the namesake result.
- **LLUNATIC** (Geerts et al., VLDB 2013): a unified chase-based framework handling FDs, CFDs, MDs, editing rules, and master data with a cost manager and cell groups.
- **HoloClean** (Rekatsinas et al., VLDB 2017): joint probabilistic repair across constraints + statistics + external signals; SOTA accuracy on standard benchmarks.
- **BigDansing** (Khayyat et al., SIGMOD 2015): scalable, rule-agnostic detection/repair on distributed engines.
- **Horizon / recent systems** combining holistic repair with learned signals. *(frontier — verify)*

## 4. Upper Bound

- General holistic minimum-cost repair: **factor-$k$ approximation** via hitting-set LP rounding ($k$ = max hyperedge size across all constraint types); polynomial in instance and constraint-set size.
- **FPT** in the conflict-hypergraph treewidth / number of interacting components; embarrassingly parallel across disconnected components.
- Approximate MAP inference (Gibbs/loopy BP, HoloClean) runs in near-linear passes over the violation set; ILP/MaxSAT gives exact answers at moderate scale.

## 5. Lower Bound

- **NP-hard** and **APX-hard** already for two FDs, hence for any superset including heterogeneous constraints (vertex-cover reduction).
- Joint MAP inference is **NP-hard** (embeds weighted MAX-SAT).
- The interaction makes naive **sequential repair non-terminating / Church-Rosser-failing**: without a cost-managed chase, ordering can diverge — an *impossibility* of order-independent constraint-by-constraint repair.

## 6. The Gap

It is **partially solved**: holistic *frameworks* exist and dominate sequential repair empirically, and the bounded-arity approximation is essentially tight against the vertex-cover barrier. What remains open: (i) **provable accuracy** (not just cost) guarantees for joint repair across constraint types; (ii) a characterization of *when* heterogeneous constraints provably interact vs. decompose; (iii) scalable **exact** holistic optimization beyond moderate scale; (iv) principled integration of **soft/statistical** constraints with hard ones in the same guarantee. The cost-vs-truth gap (minimum cost need not equal maximum accuracy) is the central unresolved issue.

## 7. Current Research (as of June 2026)

- **Learned + holistic** pipelines where constraint signals and ML/LLM priors are jointly optimized (Ilyas, Rekatsinas, Papotti, Abedjan groups). *(frontier — verify)*
- **Constraint discovery feeding holistic repair** end-to-end (discover DCs/CFDs, then jointly repair). *(frontier — verify)*
- **Scalable exact solvers** via decomposition and modern MaxSAT/ILP. *(frontier — verify)*
- **Foundation-model-assisted** conflict resolution for value choice within the holistic objective. *(frontier — verify)*

## 8. Future Work

- Accuracy-guaranteed (not only cost-minimal) holistic repair.
- Formal interaction theory: decomposition conditions across constraint families.
- Unified hard+soft constraint optimization with bounds.
- Incremental/streaming holistic repair under evolving constraints.

## 9. Key References

- **[Foundational]** Chu, Ilyas, Papotti. *Holistic Data Cleaning: Putting Violations into Context.* ICDE, 2013.
- **[Foundational]** Fan, Geerts. *Foundations of Data Quality Management.* Morgan & Claypool, 2012.
- **[SOTA]** Geerts, Mecca, Papotti, Santoro. *The LLUNATIC Data-Cleaning Framework.* VLDB, 2013.
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017.
- **[SOTA]** Khayyat et al. *BigDansing: A System for Big Data Cleansing.* SIGMOD, 2015.
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
