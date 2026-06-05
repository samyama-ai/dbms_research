# Incremental maintenance of graph pattern views

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/incremental-pattern-maintenance` · **Status:** open

## 1. Problem Statement
A graph pattern query $Q$ (a subgraph-isomorphism pattern, a conjunctive query over edges, or an RPQ/UCRPQ) is evaluated once over $G$ to produce an answer view $Q(G)$. The graph then changes by a stream of single-edge updates $\Delta = \pm e$. **Incrementally maintain $Q(G)$** — i.e., produce $Q(G\oplus\Delta)$ or just the *delta* $\Delta Q$ — with **work bounded sublinearly in $|G|$ per update**, ideally with worst-case constant or polylog update time and constant-delay enumeration of the maintained answer.
Variants: (a) **counting** the number of matches; (b) **Boolean** existence; (c) full **enumeration** of matches with bounded delay; (d) maintaining answers to **path/reachability** queries. The optimization target is the per-update update time and the auxiliary-space overhead.

## 2. Mathematical Foundations
The model is **Dynamic Complexity** (Patnaik–Immerman **DynFO**): a query is in DynFO if its answer can be maintained by first-order update formulas after each single edge change. Reachability — long open — was shown to be in **DynFO** by **Datta, Kulkarni, Mukherjee, Schwentick, Zeume (2018)**. Subgraph-counting connects to the **CCQ/AGM** framework: maintaining the count of a join query relates to its **fractional edge cover** $\rho^*(Q)$ and to **fractional hypertree width**. The fine-grained theory uses the **Online Matrix–Vector (OMv) conjecture** and **triangle-detection** hardness to lower-bound dynamic update time. For free-connex acyclic CQs, **constant-delay enumeration with $O(1)$ amortized update** is achievable (Berkholz–Keppeler–Schweikardt, "Answering Conjunctive Queries under Updates," PODS 2017). $q$-hierarchical queries characterize the constant-time-maintainable class.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Berkholz–Keppeler–Schweikardt give a **dichotomy**: a CQ is maintainable with constant update time and constant-delay enumeration **iff** it is *q-hierarchical*; otherwise OMv-hardness kicks in. Reachability/regular-path maintainability sits in DynFO.
- **Systems-SOTA:** **Differential Dataflow / DBSP** (McSherry, Murray, Budiu, Abadi; later Feldera/DBSP, Budiu et al. VLDB 2023) give incremental view maintenance for recursive (Datalog) and relational queries. **Graphflow / TurboFlux / SymBi / RapidFlow** and **IncDelta** maintain subgraph matches; **Cosmos / TC-style** delta engines maintain triangles/cliques.

## 4. Upper Bound
For **q-hierarchical CQs**: $O(1)$ amortized update time, $O(1)$ delay enumeration, linear space (BKS PODS 2017). For **acyclic / free-connex** CQs without the hierarchical property: update time $O(|G|^{1-\epsilon})$ via worst-case-optimal delta joins, with $\rho^*$-bounded materialization. For reachability and fixed RPQs: **DynFO** (polylog parallel update, $\mathrm{AC}^0$ formulas). DBSP gives provably incremental plans for all of relational algebra + recursion with delta cost proportional to change size times query complexity.

## 5. Lower Bound
For non-q-hierarchical CQs (e.g., triangle $Q_\triangle$), maintaining the count or enumerating with constant delay under edge updates requires $\Omega(|G|^{\gamma})$ per update **unless the OMv conjecture fails** (Berkholz–Keppeler–Schweikardt). Triangle detection under updates is OMv-hard; $k$-clique maintenance inherits this. These are **conditional fine-grained** lower bounds in the cell-probe/RAM model. Combinatorially, no amortized $O(1)$ scheme exists for cyclic patterns.

## 6. The Gap
For **CQ counting/enumeration** the boundary is essentially *closed* (q-hierarchical dichotomy under OMv). The genuinely **open** territory: (1) tight bounds for **general cyclic patterns** beyond OMv-conditional — is there an unconditional separation? (2) maintenance of **UCRPQ / recursive path** answers with bounded per-update work (DynFO membership is known for reachability but *enumeration delay* and *space* trade-offs are open); (3) maintenance under **batch** updates with amortization better than replaying deltas; (4) closing the gap between DBSP's incremental cost and information-theoretic minimum work.

## 7. Current Research (as of June 2026)
**Schweikardt, Berkholz, Keppeler** (HU Berlin) on dynamic query classes; **Schwentick, Zeume, Datta** on DynFO for recursive queries; **Budiu, McSherry, Tannen** on DBSP/Feldera; subgraph-IVM systems work (**Özsu, Salihoglu** at Waterloo with Kùzu/Graphflow). *(frontier — verify)* 2025–2026 work pushes **constant-delay maintenance for unions of acyclic CQs**, DynFO maintainability of **conjunctive regular path queries**, and GPU/streaming delta-join engines with skew-aware repartitioning. Feldera and Materialize commercialize incremental graph/recursive views.

## 8. Future Work
- Dichotomies for **path and recursive** query maintenance (DynFO + enumeration delay).
- Unconditional (non-OMv) lower bounds for cyclic-pattern updates.
- Space-optimal auxiliary structures (beyond $\rho^*$ materialization).
- Adaptive maintenance under workload/skew drift; provenance-aware deletions.

## 9. Key References
- **[Foundational]** Patnaik, Immerman. *Dyn-FO: A Parallel, Dynamic Complexity Class.* PODS 1994 / JCSS 1997. — [DOI](https://doi.org/10.1006/jcss.1997.1520)
- **[Foundational]** Datta, Kulkarni, Mukherjee, Schwentick, Zeume. *Reachability is in DynFO.* J. ACM, 2018. — [DOI](https://doi.org/10.1145/3212685)
- **[SOTA]** Berkholz, Keppeler, Schweikardt. *Answering Conjunctive Queries under Updates.* PODS 2017. — [DOI](https://doi.org/10.1145/3034786.3034789)
- **[SOTA]** Budiu, McSherry, Ryzhyk, Tannen. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* VLDB 2023. — [DOI](https://doi.org/10.14778/3587136.3587137)
- **[Foundational]** McSherry, Murray, Isaacs, Isard. *Differential Dataflow.* CIDR 2013. — [PDF](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf)

## 10. Worked Example

**Maintaining a triangle count vs. a hierarchical join.** Let the view be the triangle count $Q_\triangle$ over an edge relation $E$. Start with a 4-cycle $1\!-\!2\!-\!3\!-\!4\!-\!1$: count $=0$. Insert the chord $e=(1,3)$. This single update creates two triangles: $\{1,2,3\}$ and $\{1,3,4\}$. To find the delta we must count common neighbors of $1$ and $3$ — i.e. compute $|N(1)\cap N(3)|=|\{2,4\}|=2$. In the worst case a vertex has $\Theta(|G|)$ neighbors, so this intersection — an Online Matrix–Vector product in disguise — costs $\Omega(|G|^{\gamma})$ per update unless the OMv conjecture fails. Triangle is **not** q-hierarchical, so no $O(1)$ scheme exists (Berkholz–Keppeler–Schweikardt).

Contrast a **q-hierarchical** query, e.g. $Q(x)\!:\!-\,R(x,y),S(x)$. Its atoms' variable sets nest: $\{x\}\subseteq\{x,y\}$. Here inserting one $R$- or $S$-tuple updates the answer and resumes constant-delay enumeration in $O(1)$ amortized time, with linear auxiliary space — landing on the tractable side of the dichotomy.

---
*Part of the [DBMS Research catalog](../../README.md).*
