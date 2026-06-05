# Incremental Maintenance of Recursive Views

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/incremental-recursive-views` · **Status:** empirically-open
> **Verification note:** The CIDR 2013 *Differential Dataflow* paper's authors are McSherry, Murray, Isaacs, and Isard (Abadi co-authored the later *Foundations of Differential Dataflow*, FoSSaCS 2015); the reference has been corrected accordingly.

## 1. Problem Statement
Given a recursive view $V$ defined by a Datalog program (or `WITH RECURSIVE` SQL) over base relations, and a stream of updates $\Delta$ (insertions and especially **deletions**) to the base, recompute $V$ **incrementally** — doing work proportional to the change rather than re-evaluating from scratch — while guaranteeing the result equals the from-scratch answer. Insertions to a monotone recursive view are easy (semi-naive continues); **deletions** are the hard case because a deleted base fact may or may not invalidate a derived fact that has *other* supporting derivations.

Variants: (a) *exact* incremental maintenance with correctness guarantees; (b) *bounded* maintenance — when is per-update work independent of database size? (c) maintenance with **aggregation/negation** in the recursion; (d) the descriptive-complexity question: which recursive views are maintainable in $\mathrm{FO}$ / $\mathrm{DynFO}$.

## 2. Mathematical Foundations
Two algorithmic lineages:
- **Counting / DRed (Delete–Rederive).** Gupta–Mumick–Subrahmanian (SIGMOD 1993): on deletion, over-delete everything transitively derivable from deleted facts, then **rederive** facts that still have alternative support. Correct but can over-delete badly. The **counting** algorithm keeps derivation counts and works for **non-recursive** or restricted recursive cases.
- **Provenance / support-based** maintenance: keep enough provenance (absorptive semiring, see the provenance page) to decide survival of a derived fact in $O(1)$ amortized, avoiding rederivation.

Descriptive complexity formalizes "cheap maintenance": a query is in **$\mathrm{DynFO}$** (Patnaik–Immerman 1997) if after each single-tuple update the answer relation is recomputed by a *first-order* formula over auxiliary relations. The landmark result: **(undirected and directed) reachability — i.e., transitive closure — is in $\mathrm{DynFO}$** (Datta, Kulkarni, Mukherjee, Schwentick, Zeume, J. ACM 2018), settling a 20-year open problem. This means the canonical recursive view *is* maintainable with constant-depth (parallel, AC$^0$) update circuits using polynomial auxiliary storage.

**Differential dataflow** (McSherry, Murray, Isard, Abadi, CIDR 2013) gives an operational model: collections indexed by a partial order of (time, iteration) with a difference operator $\delta$; fixpoints are maintained incrementally so that an update triggers work proportional to the changed differences, supporting iteration (recursion) natively.

## 3. State of the Art (SOTA)
Theory-SOTA: TC $\in\mathrm{DynFO}$ (Datta et al., J. ACM 2018) and follow-ups extending $\mathrm{DynFO}$ to richer queries (Datta–Mukherjee–Schwentick–Vortmeier–Zeume); maintaining regular path / Dyck reachability incrementally. Systems-SOTA: **Differential Dataflow / Timely Dataflow** and **Materialize** (streaming SQL incl. recursive views), **DDlog** (incremental Datalog, used in network/program-analysis tooling), **DBToaster** (higher-order delta processing, primarily non-recursive aggregates), **Soufflé** with incremental evaluation, **RecStep**, and the **F-IVM / IVM$^\epsilon$** line (Olteanu, Kara, Nikolic) for factorized incremental aggregation. For pure recursion, differential dataflow is the practical reference implementation.

## 4. Upper Bound
For transitive closure and related queries, $\mathrm{DynFO}$ gives **$\mathrm{AC}^0$ (constant parallel depth)** per update with polynomial auxiliary relations — the strongest "bounded work" upper bound known. Operationally, **differential dataflow** maintains a recursive view with per-update cost proportional to the size of the *output difference* (plus log factors for index maintenance), which is optimal in an output-sensitive sense. DRed with good provenance achieves $O(|\Delta\text{-affected}|)$ amortized work for monotone recursion, and $O(1)$-support-check deletions under absorptive provenance.

## 5. Lower Bound
There is **no general unconditional non-trivial lower bound** matching the upper bounds — this is precisely why the status is *empirically open*. Negative facts: not all recursive views are in $\mathrm{DynFO}$ under *arbitrary* (non-single-tuple) updates; some queries require auxiliary data or fall into $\mathrm{DynFO}$-hardness classes (e.g., problems complete for $\mathrm{DynFO}$ under bounded reductions). The classical notion of a **"bounded" recursive view** (one maintainable with FO/relational-algebra deltas) is **undecidable** to detect in general. Worst-case deletions can force $\Omega(n)$ rederivation for views with $\Theta(1)$-support facts, so output-sensitive bounds can degrade. No SETH/3SUM-style fine-grained conditional lower bound is known to pin the per-update cost of general recursive maintenance.

## 6. The Gap
The gap is between **strong existence results** (TC is in DynFO; differential dataflow works) and the absence of a **complete, practical, worst-case-bounded** algorithm with matching lower bounds for *arbitrary* recursive views with aggregation and negation. We do not know a tight per-update complexity for general Datalog maintenance, nor a decidable characterization of which views admit bounded ($\mathrm{DynFO}$/sublinear) maintenance. Hence empirically open: systems demonstrate good amortized behavior, but guarantees are workload-dependent and worst cases remain bad.

## 7. Current Research (as of June 2026)
Schwentick, Zeume, Vortmeier and collaborators continue mapping the $\mathrm{DynFO}$ landscape (which queries enter $\mathrm{DynFO}$, lower bounds, parallelism). McSherry's and the Materialize team push differential dataflow into production recursive SQL; Olteanu/Kara extend factorized IVM toward recursion and aggregation *(frontier — verify recursive IVM$^\epsilon$ results)*. Active threads: incremental maintenance with **provenance/absorptive semirings** for $O(1)$ deletion checks; maintenance of **recursive aggregate** views (PageRank, shortest paths) with convergence-aware deltas; and integration with GPU/streaming engines *(frontier — verify 2025–2026 differential-Datalog and recursive-SQL-IVM systems)*.

## 8. Future Work
A decidable characterization (or robust sufficient conditions) for boundedly maintainable recursive views; worst-case-optimal and fine-grained-conditional lower bounds for recursive deletion; unified maintenance of recursion + aggregation + negation with correctness proofs; and provenance-driven engines that maintain *and* explain recursive views with provably sublinear per-update work.

## 9. Key References
- **[Foundational]** A. Gupta, I. S. Mumick, V. S. Subrahmanian. *Maintaining Views Incrementally.* SIGMOD 1993 (counting and DRed). — [DOI](https://doi.org/10.1145/170035.170066)
- **[Foundational]** S. Patnaik, N. Immerman. *Dyn-FO: A Parallel, Dynamic Complexity Class.* JCSS / PODS 1994. — [DOI](https://doi.org/10.1145/182591.182614) — [PDF](https://people.cs.umass.edu/~immerman/pub/dynfo.pdf)
- **[SOTA]** S. Datta, R. Kulkarni, A. Mukherjee, T. Schwentick, T. Zeume. *Reachability Is in DynFO.* Journal of the ACM 65(5), 2018 (ICALP 2015). — [arXiv](https://arxiv.org/abs/1502.07467) — [DOI](https://doi.org/10.1145/3212685)
- **[SOTA]** F. McSherry, D. Murray, R. Isaacs, M. Isard. *Differential Dataflow.* CIDR 2013. — [PDF](https://www.microsoft.com/en-us/research/publication/differential-dataflow/)
- **[SOTA]** M. Nikolic, M. Dashti, D. Olteanu. *F-IVM: Factorized Incremental View Maintenance.* SIGMOD 2018 / VLDB Journal. — [arXiv](https://arxiv.org/abs/1703.07484) — [DOI](https://doi.org/10.1145/3183713.3183758)
- **[Survey]** A. Gupta, I. S. Mumick (eds.). *Materialized Views: Techniques, Implementations, and Applications.* MIT Press, 1999. — [MIT Press](https://direct.mit.edu/books/edited-volume/2853/Materialized-ViewsTechniques-Implementations-and)

## 10. Worked Example

Recursive view $\text{TC}(x,y) \leftarrow E(x,y)$ and $\text{TC}(x,y)\leftarrow E(x,z),\text{TC}(z,y)$ over the path graph $E=\{(1,2),(2,3),(3,4)\}$. Semi-naive yields $\text{TC}=\{(1,2),(2,3),(3,4),(1,3),(2,4),(1,4)\}$ — 6 pairs.

Now **delete** base edge $(2,3)$. DRed first *over-deletes* every TC tuple derivable using $(2,3)$: that removes $(2,3),(1,3),(2,4),(1,4)$, leaving only $\{(1,2),(3,4)\}$. The **rederive** phase checks each over-deleted pair against the remaining edges $\{(1,2),(3,4)\}$: none can be rederived (1 no longer reaches 3, 2 no longer reaches 4), so the final view is $\{(1,2),(3,4)\}$ — correct.

The cost lesson: a single base deletion forced re-examination of 4 derived tuples on a 4-node graph, i.e. $\Theta(n)$ rederivation work in the worst case. By contrast $\text{TC}\in\mathrm{DynFO}$ (Datta et al.) maintains the *same* relation with a first-order update formula over polynomial auxiliary relations — constant parallel ($\mathrm{AC}^0$) depth per single-tuple change — which is exactly the gap between practical DRed and the theoretical bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
