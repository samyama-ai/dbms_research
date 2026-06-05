# Optimizing queries with expensive predicates

> **Topic:** Query Optimization · **ID:** `02-query-optimization/expensive-predicate-ordering` · **Status:** partially-solved

## 1. Problem Statement

Some predicates are not free: a UDF, a regex over a CLOB, an ML inference call, a subquery, or a remote/web-service lookup can cost orders of magnitude more per tuple than a simple comparison. Given a set of predicates $\{p_1,\dots,p_k\}$ each with a **per-tuple cost** $c_i$ and **selectivity** $s_i$, decide the *order* in which to apply them — and, jointly, *where to place* them relative to joins — to minimize total expected work.

- **Decision variant:** is there an ordering/placement with expected cost $\le B$?
- **Optimization variant:** minimize expected evaluation cost over the predicate pipeline (and join tree).
- **Pure-selection sub-problem:** order a single conjunction of independent predicates — this restricted case is exactly solvable in closed form.

"Solving" means treating expensive predicates as first-class plan operators, not as residual filters applied last.

## 2. Mathematical Foundations

For a **conjunction of independent predicates** applied to a stream, applying $p_i$ costs $c_i$ per surviving tuple and passes a fraction $s_i$. The expected cost of order $\pi$ is
$$ \text{Cost}(\pi) = \sum_{j} c_{\pi(j)} \prod_{l < j} s_{\pi(l)}. $$
This is minimized by sorting predicates in increasing order of the **rank** $\dfrac{c_i}{1 - s_i}$ — the classic *rank ordering* / **R*-rule** (Hellerstein–Stonebraker; Krishnamurthy–Boral–Zaniolo for the analogous join/selection ordering). This is a special case of **Smith's rule** for sequencing to minimize weighted completion, and connects to **pipelined set cover / min-sum set cover** when predicates are correlated.

With **correlations** the product no longer factorizes and the problem becomes the *Pipelined Filter Ordering* / *Adaptive Filtering* problem, which is NP-hard in general; conditional plans (decision trees over predicate outcomes) generalize linear orders. **Predicate migration** (Hellerstein) moves expensive predicates up/down a join tree; the join+predicate interleaving makes the joint space combinatorial.

## 3. State of the Art (SOTA)

- **Theory SOTA:** the rank rule is *optimal* for independent predicates. For correlated predicates, **constant-factor approximations** exist for pipelined filter ordering (e.g., 4-approximations via min-sum set cover techniques; Munagala–Babu–Motwani–Widom and follow-ups), and the *adaptive* (instance-by-instance) version admits competitive algorithms.
- **Systems SOTA:** PostgreSQL exposes per-function `COST`; commercial optimizers (Oracle, SQL Server, DB2) cost UDFs and reorder/pull-up predicates. **Predicate migration** (Hellerstein, Postgres/Illustra lineage) is the canonical systems result; modern *ML-in-DB* systems (e.g., model-serving predicates) reorder inference predicates by cost/selectivity and add cascades of cheap proxies.

## 4. Upper Bound

For independent predicates the optimum is found in $O(k \log k)$ by sorting on the rank $c_i/(1-s_i)$ (Krishnamurthy–Boral–Zaniolo; Hellerstein–Stonebraker). For the correlated **pipelined filter ordering** problem, polynomial-time **$O(1)$-approximation** algorithms are known (4-approx for the non-adaptive set-cover formulation), and a $4$-competitive adaptive strategy exists.

## 5. Lower Bound

Ordering correlated predicates to minimize expected cost is **NP-hard** (reduction from min-sum set cover; Munagala et al.), and min-sum set cover is **hard to approximate below factor 4** unless P = NP (Feige–Lovász–Tetali). The *joint* predicate-placement-with-join-ordering problem inherits NP-hardness of join ordering (Ibaraki–Kameda). No SETH/fine-grained separation is the binding constraint here; the wall is classical approximation hardness.

## 6. The Gap

For the **independent** case the problem is *closed* (exact, optimal, near-linear time). For the **correlated** and **join-interleaved** cases there is a residual gap between the $4$-approximation upper bound and the factor-$4$ inapproximability — these nearly meet for min-sum set cover, but the join-aware variant lacks tight bounds. The practical gap is selectivity/cost *estimation*: the rank rule is only as good as its $s_i, c_i$ inputs, which for UDFs and ML predicates are data-dependent and drift. Hence "partially solved."

## 7. Current Research (as of June 2026)

- **Predicate cascades for ML inference**: cheap proxy models gate expensive deep models; cost/accuracy-aware ordering (NoScope-style and successors, Stanford/MIT/UW). *(frontier — verify)*
- Learned cost and selectivity for UDFs/inference predicates, with online correction.
- Adaptive / eddy-style reordering under drifting correlations.
- Tight approximation for joint predicate-placement + join-ordering remains under study (TU Munich, UW, Wisconsin). *(frontier — verify)*

## 8. Future Work

- Closing the approximation gap for join-interleaved expensive predicates.
- Robust ordering under uncertain/learned $(c_i, s_i)$ with guarantees.
- Conditional (branching) plans vs. linear orders: when does branching pay off?
- Cost models for accelerator-resident predicates (GPU/SIMD inference).

## 9. Key References

- **[Foundational]** J. M. Hellerstein, M. Stonebraker. *Predicate Migration: Optimizing Queries with Expensive Predicates.* SIGMOD, 1993. — [DOI](https://doi.org/10.1145/170036.170078)
- **[Foundational]** R. Krishnamurthy, H. Boral, C. Zaniolo. *Optimization of Nonrecursive Queries.* VLDB, 1986. — [DBLP](https://dblp.org/rec/conf/vldb/KrishnamurthyBZ86.html)
- **[SOTA]** K. Munagala, S. Babu, R. Motwani, J. Widom. *The Pipelined Set Cover Problem.* ICDT, 2005. — [DOI](https://doi.org/10.1007/978-3-540-30570-5_6)
- **[SOTA]** U. Feige, L. Lovász, P. Tetali. *Approximating Min Sum Set Cover.* Algorithmica, 2004. — [DOI](https://doi.org/10.1007/s00453-004-1110-5)
- **[SOTA]** D. Kang et al. *NoScope: Optimizing Neural Network Queries over Video at Scale.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1703.02529)
- **[Survey]** S. Chaudhuri. *An Overview of Query Optimization in Relational Systems.* PODS, 1998. — [DOI](https://doi.org/10.1145/275487.275492)

## 10. Worked Example

A stream of $1000$ tuples passes through three independent filters:

| predicate | cost $c_i$ | selectivity $s_i$ | rank $\frac{c_i}{1-s_i}$ |
|-----------|-----------|-------------------|--------------------------|
| $p_1$ (cheap regex) | $1$ | $0.9$ | $1/0.1=10$ |
| $p_2$ (UDF) | $5$ | $0.2$ | $5/0.8=6.25$ |
| $p_3$ (ML inference) | $20$ | $0.5$ | $20/0.5=40$ |

The **rank rule** sorts by increasing rank: $p_2\;(6.25) < p_1\;(10) < p_3\;(40)$. Using $\text{Cost}(\pi)=\sum_j c_{\pi(j)}\prod_{l<j}s_{\pi(l)}$ per tuple, times $1000$:

- Rank order $p_2,p_1,p_3$: $1000\,[\,5 + 0.2(1) + 0.2(0.9)(20)\,] = 1000(5.2+3.6)=8800$.
- Naive "cheapest-first" $p_1,p_2,p_3$: $1000\,[\,1 + 0.9(5) + 0.9(0.2)(20)\,]=1000(5.5+3.6)=9100$.

The rank order wins because $p_2$, despite costing more than $p_1$, is far more selective ($0.2$ vs $0.9$), so it discards tuples before the expensive $p_3$ ever runs. Note cheapest-first is *not* optimal — selectivity, not raw cost, drives the rank.

---
*Part of the [DBMS Research catalog](../../README.md).*
