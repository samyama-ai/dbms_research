# Minimum-Cost Repair Under Denial Constraints

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/min-cost-repair-denial-constraints` · **Status:** open

## 1. Problem Statement

Given a relational instance $I$ that violates a set $\Sigma$ of **denial constraints (DCs)** and a cost model $c$ assigning a non-negative cost to each atomic modification (cell update, tuple deletion, tuple insertion), compute a **repair** $I'$ — an instance satisfying $\Sigma$ — that minimizes total cost $c(I, I')$.

Variants:
- **Decision:** Does a repair of cost $\le k$ exist?
- **Optimization:** Find $\arg\min_{I' \models \Sigma} c(I, I')$.
- **Counting:** How many minimum-cost (or distinct) repairs exist?
- By operation: subset/deletion repairs (S-repairs), tuple-update repairs (U-repairs), and cardinality-minimal vs. cost-minimal variants.

A denial constraint has the form $\forall \bar{x}\, \neg(\,R_1(\bar{x}_1) \wedge \cdots \wedge R_m(\bar{x}_m) \wedge \phi(\bar{x})\,)$ where $\phi$ is a conjunction of built-in comparisons ($=, \neq, <, \le$). DCs subsume functional dependencies (FDs), conditional FDs, and many check constraints, making them the canonical expressive target for repair.

## 2. Mathematical Foundations

A DC is **violated** by a set of tuples (a *violating witness*) jointly satisfying the predicate body. The structure of violations is naturally a **hypergraph** $H = (V, E)$: vertices are tuples (or cells), and each minimal violating witness is a hyperedge. A deletion repair corresponds to a **hitting set** / **vertex cover** of $H$; minimum-cost deletion repair is **weighted minimum vertex cover** when DCs are "2-ary" (e.g., FDs induce a conflict *graph*), and weighted minimum hitting set in general.

Key facts:
- For a single FD, the conflict graph is a disjoint union of cliques; minimum deletion repair = remove all-but-one per clique (poly-time).
- For two or more FDs, minimum cardinality S-repair is **NP-hard** (vertex cover reduction).
- Cell-level update repairs interact through *propagation*: changing one cell to satisfy one DC may create violations of another, so the search space is not monotone — captured by a **fixpoint / chase**-like semantics.

LP relaxation and the primal-dual schema give the standard $2$-approximation for the vertex-cover-shaped subproblem; for $k$-ary hyperedges (DCs with $k$ atoms) a factor-$k$ approximation follows from hitting-set LP rounding.

## 3. State of the Art (SOTA)

- **Theory:** Lopatenko & Bertossi (ICDT 2007) established the complexity landscape for cost-minimal repairs w.r.t. DCs and aggregate queries; minimum-cost repair under DCs is **APX-hard** in general and admits constant-factor approximation only for bounded-arity bodies.
- **Systems:** **HoloClean** (Rekatsinas et al., VLDB 2017) casts repair as MAP inference in a factor graph combining DCs, statistical signals, and external data. **Holistic Data Cleaning** (Chu et al., ICDE 2013) introduced joint repair over DCs via a conflict hypergraph and a minimum vertex cover heuristic. **LLUNATIC** (Geerts et al., VLDB 2013) gives a chase-based unified repair engine. **BigDansing** (Khayyat et al., SIGMOD 2015) and **Cleenex** scale DC-based repair to distributed settings.

## 4. Upper Bound

- Deletion (S-)repair minimizing cost: a **factor-$k$ approximation** via hitting-set LP rounding where $k$ is the maximum number of atoms per DC; **factor-2** for FD-only (graph) instances. Runs in polynomial time in $|I|$ and $|\Sigma|$.
- Exact minimum-cost repair: solvable in time exponential in the number of conflicts but **FPT** in the size of the conflict hypergraph's vertex cover / treewidth — e.g., $O(2^k \cdot \mathrm{poly})$ where $k$ is the repair budget (branching on each hyperedge).
- For a **single** FD or a single DC with key-like structure, **exact polynomial-time** algorithms exist.

## 5. Lower Bound

- **NP-hard** and **APX-hard** for $\ge 2$ FDs (reduction from minimum vertex cover / 3-SAT); thus no PTAS unless P = NP.
- Under the **Unique Games Conjecture**, the factor-2 barrier for the underlying vertex-cover subproblem is essentially optimal, so no $(2-\varepsilon)$-approximation is expected for FD-induced instances.
- Counting minimum repairs is **#P-hard**.

## 6. The Gap

For bounded-arity DCs the approximation gap is essentially closed up to the UGC-conditional vertex-cover barrier (factor $k$ vs. hardness of $k-\varepsilon$). The genuinely open frontier is **update-based** minimum-cost repair with *value choice*: because updates propagate non-monotonically across heterogeneous DCs, no constant-factor approximation with a fixed cost model is known, and even membership in APX for the general cell-update version is open. Tightening the FPT dependence (treewidth vs. budget) and obtaining instance-optimal exact solvers remain open.

## 7. Current Research (as of June 2026)

- **ILP / MaxSAT-based exact repair** at moderate scale, exploiting modern solvers and conflict-hypergraph decomposition *(frontier — verify)*.
- **Learning cost models** (and DC weights) from user feedback and LLM priors to make the "minimum-cost" objective semantically meaningful (groups around Ihab Ilyas, Theodoros Rekatsinas, Paolo Papotti). *(frontier — verify)*
- **Differentiable / probabilistic repair** extending HoloClean with foundation-model value suggestions. *(frontier — verify)*

## 8. Future Work

- Constant-factor approximation (or APX-hardness proof) for cell-level update repairs under interacting DCs.
- Cost models with provable guarantees that align minimum-cost with ground-truth accuracy.
- Repair under DCs + cardinality/aggregate constraints jointly.
- Privacy- and provenance-aware minimum-cost repair.

## 9. Key References

- **[Foundational]** Arenas, Bertossi, Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303983)
- **[Foundational]** Lopatenko, Bertossi. *Complexity of Consistent Query Answering in Databases under Cardinality-Based and Incremental Repair Semantics.* ICDT, 2007. — [DOI](https://doi.org/10.1007/11965893_13)
- **[SOTA]** Chu, Ilyas, Papotti. *Holistic Data Cleaning: Putting Violations into Context.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544847)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[SOTA]** Geerts, Mecca, Papotti, Santoro. *The LLUNATIC Data-Cleaning Framework.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536360.2536363)
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books / Morgan & Claypool, 2019. — [DOI](https://doi.org/10.1145/3310205)

## 10. Worked Example

Relation `Emp(Name, Salary, Mgr, MgrSalary)` with one DC: no employee earns more than their manager,
$$\forall x\, \neg(\text{Emp}(x) \wedge x.\text{Salary} > x.\text{MgrSalary}).$$

| t | Name | Salary | MgrSalary |
|---|------|--------|-----------|
| 1 | Ann  | 90 | 80 |
| 2 | Bob  | 70 | 80 |
| 3 | Cy   | 95 | 80 |

Tuples $t_1$ and $t_3$ each violate the DC (90 > 80, 95 > 80); $t_2$ is fine. Each minimal violating witness is a single tuple, so the conflict hypergraph has two singleton hyperedges $\{t_1\}, \{t_3\}$. A **deletion** S-repair must hit every hyperedge: minimum hitting set $= \{t_1, t_3\}$, cost 2 deletions.

A **cell-update** repair is cheaper: lower each offender's Salary to 80 (or raise MgrSalary). Two cell edits at cost 1 each — but note the propagation hazard: raising $t_1$'s MgrSalary to 95 to "fix" it would be a non-monotone choice if a second DC bounded total payroll. With singleton edges, LP rounding gives the factor-$k=1$ (exact) cover here, matching the poly-time single-DC regime in section 4.

---
*Part of the [DBMS Research catalog](../../README.md).*
