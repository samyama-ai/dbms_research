# Optimal Semijoin Reduction Programs

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/optimal-semijoin-programs` · **Status:** open

## 1. Problem Statement
Given a (possibly cyclic) conjunctive query $Q$ over relations distributed across sites, compute a **sequence of semijoin operations** that removes all dangling tuples (tuples not contributing to any answer) while **minimizing total communication** before the final assembly/join phase. A semijoin $R \ltimes S$ ships only the projection of $S$'s join attributes, so it is far cheaper than shipping full relations — but choosing *which* semijoins, in *what order*, to reach a **fully reduced** instance is an optimization problem.

Variants:
- **Decision:** Does a full reducer of cost $\le B$ exist? For **acyclic** $Q$ a full reducer of linear length always exists (GYO); for **cyclic** $Q$ no semijoin-only full reducer exists in general.
- **Optimization (cost):** Minimize bytes/messages of the reduction program (the classic *semijoin program* problem, NP-hard in general).
- **Cyclic case:** Find the cheapest reducer that maximally reduces, possibly augmented with bounded "generalized" (e.g., 2-way) semijoins or partial materialization.

## 2. Mathematical Foundations
A query is **acyclic** iff its hypergraph has a **GYO** (Graham–Yu–Ozsoyoglu) elimination order, equivalently a **join tree**. For acyclic $Q$, **Yannakakis' algorithm** (1981) gives a full reducer via two semijoin sweeps over the join tree (bottom-up then top-down), with total intermediate size $O(N + |Q|)$. For cyclic $Q$, no semijoin program is a full reducer; reduction is limited to a *fractional/elimination-width* core, with residual handled by joins. Cost models count message bytes; the optimization is related to **query graph** orderings and is provably **NP-hard** (Bernstein–Goodman; the general semijoin-program minimization problem). The chase and **acyclicity hierarchy** ($\alpha$-, $\beta$-, $\gamma$-acyclicity) underpin which queries are reducible.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Yannakakis (VLDB 1981) — optimal for acyclic queries. Bernstein–Goodman (1981) — semijoin programs and full reducers; minimizing cost is NP-hard. Recent work uses **GHDs / fractional hypertree decompositions** (Gottlob, Grohe, Marx) to reduce cyclic queries to acyclic ones first, then Yannakakis-reduce.
- **Systems-SOTA:** **Bloom-filter / sideways information passing (SIP)** semijoins in Spark, Presto/Trino dynamic filtering, and **bushy SIP** in commercial MPP. These approximate semijoin reduction with sketches rather than computing optimal programs.

## 4. Upper Bound
Acyclic $Q$: $O(N)$-communication full reducer in $O(\text{depth of join tree})$ rounds (Yannakakis). Cyclic $Q$: after a width-$w$ decomposition, reduce in $\tilde O(N^{w})$ communication where $w$ = fractional hypertree-width, then assemble. Greedy / heuristic semijoin ordering yields good constant-factor reductions in practice but no general optimality guarantee.

## 5. Lower Bound
Minimizing the cost of a semijoin program (full reducer for reducible queries) is **NP-hard** (Bernstein–Goodman 1981; later sharpened). Communication lower bounds: any full reducer must ship $\Omega(N)$ in the worst case even for acyclic queries; for cyclic queries, semijoin-only reduction provably **cannot** eliminate all dangling tuples (information-theoretic argument on the query hypergraph). Approximating the optimal program within certain factors is open / conjectured hard.

## 6. The Gap
For **acyclic** queries the *reduction* is optimally solved (Yannakakis), but choosing the **cheapest schedule** under real cost models (network heterogeneity, statistics uncertainty) is **NP-hard and open** in approximability. For **cyclic** queries there is no clean notion of an "optimal" semijoin program at all — the gap is between heuristic SIP and a principled cost-minimal reducer. This is **open**: we lack both tight approximation algorithms and matching hardness for the cost-minimization variant.

## 7. Current Research (as of June 2026)
Work on **Yannakakis-style optimization inside modern engines** (e.g., "free join" and predicate transfer / Bloom-reducer scheduling) is active *(frontier — verify)*. Groups: Suciu/Wang (UW) on predicate transfer optimality; Gottlob/Pichler on decomposition-driven reduction; industry teams adding cost-based dynamic-filter ordering. Learned cardinality estimates to order semijoins are being studied *(frontier — verify)*.

## 8. Future Work
- Approximation algorithms (with guarantees) for cost-minimal semijoin schedules under realistic network/cardinality models.
- A clean optimality theory for cyclic-query reducers combining decompositions and generalized semijoins.
- Robust ordering under uncertain statistics (online / adaptive reducers).

## 9. Key References
- **[Foundational]** Yannakakis. *Algorithms for Acyclic Database Schemes.* VLDB, 1981.
- **[Foundational]** Bernstein, Goodman. *Power of Natural Semijoins.* SIAM J. Computing, 1981.
- **[Foundational]** Beeri, Fagin, Maier, Yannakakis. *On the Desirability of Acyclic Database Schemes.* JACM, 1983.
- **[SOTA]** Gottlob, Greco, Scarcello. *Treewidth and Hypertree Width* (in *Tractability*, Cambridge), 2014.
- **[SOTA]** Yang, Wang, Suciu et al. *Predicate Transfer / Robust Predicate Pushdown.* (CIDR/VLDB), 2024.

---
*Part of the [DBMS Research catalog](../../README.md).*
