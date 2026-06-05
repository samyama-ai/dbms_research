# Semijoin Reducers for Cyclic Queries

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/cyclic-query-semijoins` · **Status:** open

## 1. Problem Statement
A **full reducer** is a sequence of semijoins that removes every dangling tuple from each relation of a query, so that the reduced instance contains exactly the tuples participating in the final join. For **acyclic** conjunctive queries (CQs), Yannakakis' algorithm gives a full reducer using $O(\text{number of relations})$ semijoins and evaluates the query in time linear in input + output. The open problem: **extend full-reducer theory to cyclic queries** — characterize, construct, and bound the cost of (generalized) semijoin reducers for cyclic CQs via hypertree-style decompositions, ideally with communication-optimal distributed realizations.

Variants:
- **Decision:** does a query admit a full reducer? (For pure semijoins: iff acyclic.)
- **Optimization:** minimize residual intermediate size / communication for a cyclic query under a chosen decomposition.
- **Structural:** which width measure (treewidth, generalized/fractional hypertree width, submodular width) governs the best achievable reduction?

## 2. Mathematical Foundations
A CQ is a hypergraph $H=(V,E)$: vertices = variables, hyperedges = atoms. **Acyclicity** ($\alpha$-acyclicity) is equivalent to having a **join tree**, computable via the GYO ear-removal. A semijoin $R \ltimes S$ keeps tuples of $R$ matching some tuple of $S$.

Width measures generalize tractability:
- **Fractional hypertree width** $\mathrm{fhw}$ via fractional edge covers of bags (Grohe–Marx).
- **Submodular width** $\mathrm{subw} \le \mathrm{fhw}$ (Marx) — the sharp parameter for fixed-parameter tractability of CQ evaluation.

The **AGM bound** $|Q| \le \prod_{e} |R_e|^{x_e}$ for a fractional edge cover $x$ bounds output size. **Worst-case-optimal joins (WCOJ)** meet AGM. For cyclic queries there is *no* pure-semijoin full reducer; instead one materializes bag relations (sub-joins) over a decomposition of width $w$, reducing the problem to an acyclic query over relations of size $\tilde{O}(N^{w})$, then applies Yannakakis. The PANDA algorithm realizes $\mathrm{subw}$ as a runtime exponent.

## 3. State of the Art (SOTA)
- **Theory:** Yannakakis (1981) for acyclic; Generalized/Fractional Hypertree Decompositions (Gottlob–Leone–Scarcello; Grohe–Marx); **PANDA** (Abo Khamis–Ngo–Suciu, PODS 2017) achieving $\mathrm{subw}$; *Worst-Case Optimal Joins* — NPRR / LeapFrog Triejoin / Generic Join (Ngo–Porat–Ré–Rudra; Veldhuizen). For cyclic distributed evaluation, *HyperCube/Shares* (Afrati–Ullman; Beame–Koutris–Suciu) gives one-round optimal load.
- **Systems:** *EmptyHeaded* (Aberger et al., SIGMOD 2017) and *Umbra/LMFAO* integrate WCOJ; *RelationalAI* and *DuckDB* ship Yannakakis-style optimizations; factorized databases (Olteanu–Schleich) exploit decompositions for reduced intermediate size.

## 4. Upper Bound
Best evaluation upper bound for a cyclic CQ $Q$ on input of size $N$: $\tilde{O}(N^{\mathrm{subw}(Q)} + |Q|)$ via PANDA (theory). For distributed one-round MPC, HyperCube achieves per-server load $\tilde{O}(N / p^{1/\psi})$ where $\psi$ is the fractional edge-cover number, optimal among one-round algorithms for skew-free inputs. Once a width-$w$ decomposition is materialized, a generalized full reducer over the decomposition removes all dangling tuples with $O(|\text{tree}|)$ semijoins, after which Yannakakis runs in time linear in the (now decomposed) input plus output.

## 5. Lower Bound
- **Pure semijoins:** a full reducer of pure semijoins exists **iff** the query is acyclic (Bernstein–Goodman; Beeri–Fagin–Maier–Yannakakis) — so cyclic queries provably have *no* pure-semijoin full reducer.
- **Evaluation:** under the *Triangle / 3SUM / hyperclique* and **SETH**-based fine-grained hypotheses, no algorithm evaluates all CQs in time $O(N^{\mathrm{subw}-\epsilon})$; e.g., triangle detection is conjectured to need $N^{\omega/2}$ / $N^{1.5}$-type bounds, ruling out linear-time reducers for cyclic queries.
- **MPC:** one-round lower bounds (Beame–Koutris–Suciu) match HyperCube load for many cyclic queries.

## 6. The Gap
The gap is **structural and genuinely open**: (1) there is no clean combinatorial characterization of "best generalized semijoin reducer" for cyclic queries analogous to GYO; (2) it is open whether $\mathrm{subw}$ is *tight* — no matching fine-grained lower bound is known for all queries, so the exponent could potentially be improved. Whether one can reduce a cyclic query to acyclic with *less* than $N^{\mathrm{subw}}$ materialization, or with communication-optimal multi-round reducers, is open. Closing it requires either a sharper width parameter with matching conditional lower bounds, or new reducer constructions.

## 7. Current Research (as of June 2026)
- Bringing PANDA/$\mathrm{subw}$ from theory into practical query engines with predictable constants *(frontier — verify)*.
- Degree-aware and instance-optimal semijoin reducers that adapt the decomposition to data statistics rather than worst case.
- Distributed (multi-round MPC) generalized full reducers minimizing total communication, not just one-round load.
- Connections to **factorized / FAQ / sum-product** computation and to differential privacy-safe joins.
- Groups: Ngo/Abo Khamis/Suciu (RelationalAI), Ré (Stanford), Olteanu (Zurich), Koutris (Wisconsin), Marx (CISPA).

## 8. Future Work
- A GYO-analogue characterization for cyclic reducers.
- Tight fine-grained lower bounds certifying $\mathrm{subw}$ (or improving it).
- Multi-round communication-optimal reducers for cyclic CQs in MPC.
- Robust reducers under cardinality uncertainty and skew.

## 9. Key References
- **[Foundational]** M. Yannakakis. *Algorithms for Acyclic Database Schemes.* VLDB, 1981.
- **[Foundational]** C. Beeri, R. Fagin, D. Maier, M. Yannakakis. *On the Desirability of Acyclic Database Schemes.* JACM, 1983.
- **[SOTA]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-Case Optimal Join Algorithms.* PODS 2012 / JACM 2018.
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, D. Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* (PANDA). PODS, 2017.
- **[SOTA]** D. Marx. *Tractable Hypergraph Properties for Constraint Satisfaction and Conjunctive Queries.* JACM, 2013. (Submodular width.)
- **[Survey]** D. Olteanu, M. Schleich. *Factorized Databases.* SIGMOD Record, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
