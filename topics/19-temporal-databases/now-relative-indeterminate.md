# Now-Relative & Indeterminate Time

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/now-relative-indeterminate` · **Status:** open

## 1. Problem Statement

Temporal databases must represent and query facts whose endpoints are not fixed constants. Two intertwined sources of variability arise:

- **Now-relative time:** a tuple's valid- or transaction-time endpoint is the moving variable `NOW` (also `UC`, `until changed`, `forever`). A row "valid `[2020-01-01, NOW)`" denotes a growing interval whose right endpoint advances with the clock. The stored value is a *binding pattern*, not a constant, so the relation's extent is time-of-evaluation dependent.
- **Indeterminate time:** an endpoint is known only to lie in a set (e.g. "started sometime between 9:00 and 10:00") with optional probability mass over that set.

The problems: (i) give a denotational **semantics** under which selection, join, coalescing, and aggregation are well-defined and closed; (ii) answer queries correctly when `NOW` and indeterminate endpoints interact (e.g. overlap join between a now-relative interval and an indeterminate one); (iii) build **indexes** that answer interval-stabbing/overlap queries whose query point or data endpoints are themselves variables. Variants: *decision* (does fact $f$ definitely/possibly hold at $t$?), *optimization* (best plan over now-relative predicates), *counting/probabilistic* (expected number of qualifying tuples under an endpoint distribution).

## 2. Mathematical Foundations

Model a temporal database over a discrete time domain $\mathbb{T}=\{0,1,\dots,t_{\max}\}$ with a distinguished moving point $\textsf{now}(t)=t$. A now-relative interval is a *parametric* interval $I(t)=[a,\min(b,t))$ or $[a,t)$; its semantics is the function $t\mapsto I(t)$ from evaluation time to a ground interval (Clifford–Dyreson–Snodgrass–Jensen–Umeslawski, *VLDB J. 1997*).

Indeterminacy is captured by a *probabilistic temporal element*: each endpoint $e$ carries a mass function $p_e:\mathbb{T}\to[0,1]$, $\sum p_e=1$, and a *plausibility* threshold (Dyreson–Snodgrass, *ACM TODS 1998*). A fact holds at $t$ with probability $\Pr[a\le t < b]=\big(\sum_{x\le t}p_a(x)\big)\big(\sum_{y>t}p_b(y)\big)$ under endpoint independence; correlation requires a joint mass over $\mathbb{T}^2$.

Two semantic regimes coexist: **certain answers** (true for every binding of `NOW`/endpoints) and **possible answers** (some binding). Certain-answer computation over now-relative data reduces to evaluation over *conditional tables* (Imieliński–Lipski), placing it in the incomplete-information framework where naive evaluation can be incorrect. For indexing, the relevant geometric object is a point/segment whose coordinate is a *line* $x=t$ (the now-diagonal) in the 2D endpoint plane, so stabbing becomes a query against moving objects.

## 3. State of the Art (SOTA)

- **Semantics:** The Clifford et al. *VLDB Journal* (1997) treatment of `NOW` and the Dyreson–Snodgrass indeterminacy model (*TODS* 1998) remain the canonical references; both are folded into the consensus glossary (Jensen–Dyreson et al., 1998).
- **Systems:** SQL:2011 application-time/system-time periods deliberately exclude a moving `NOW` symbol; engines emulate it with `9999-12-31` sentinels or with `MAXVALUE` open ranges (MariaDB, DB2, Oracle Flashback, SQL Server temporal tables). Probabilistic/indeterminate time has **no production engine support**; research prototypes (TimeDB, TSQL2 prototypes, MayBMS-style probabilistic DBs for the indeterminacy slice) are the SOTA.
- **Indexing:** GiST/SP-GiST range and `tstzrange` GiST in PostgreSQL handle open-ended ranges via $+\infty$ sentinels; no index natively reasons about a moving diagonal or endpoint distributions.

## 4. Upper Bound

Evaluating a relational-algebra query with now-relative endpoints under the *possible*-answer semantics is in **PTIME data complexity**: substitute the sentinel $t_{\max}$ (or symbolic $\textsf{now}$) and evaluate, with overlap predicates rewritten to $\min(b,\textsf{now})$ — linear in input per operator. For *indeterminate* probabilistic queries, exact answer computation is **#P** in general (inherited from probabilistic databases) but admits PTIME when the query is *safe* (hierarchical) and endpoints are independent. Stabbing a now-relative interval set at a fixed historical $t<\textsf{now}$ is $O(\log n + k)$ via an interval tree, since the diagonal does not yet bite; queries *at or after* the diagonal need the moving-point reduction.

## 5. Lower Bound

Exact probability of a Boolean conjunctive query over independent indeterminate endpoints is **#P-hard** (Dalvi–Suciu dichotomy: any unsafe query is hard), so no PTIME exact algorithm exists unless FP = #P. Certain-answer evaluation over conditional tables (the natural home of unbound `NOW`) is **coNP-hard** for unions of conjunctive queries (Abiteboul–Hull–Vianu incomplete-information results). For indexing, answering overlap queries against $n$ moving (now-diagonal) intervals inherits the kinetic/parametric-search lower bounds: any structure handling arbitrary endpoint distributions must, in the comparison model, pay $\Omega(\log n)$ per stab plus output.

## 6. The Gap

For **semantics**, the gap is largely *definitional/adoption*, not complexity: a consensus exists in the literature but the SQL standard and engines collapse `NOW` to a sentinel, losing the correct moving semantics (e.g. sentinel rows wrongly compare equal across facts). For **indeterminacy**, the gap is the classic safe/unsafe #P chasm — closed in the dichotomy sense but practically open: no system delivers approximate (FPRAS / Monte-Carlo) indeterminate temporal querying at scale. For **indexing**, there is *no* established index whose query/update cost is tight for the moving-diagonal + distributional regime; the gap between the $O(\log n)$ static-interval ideal and what moving/probabilistic endpoints actually cost is genuinely open.

## 7. Current Research (as of June 2026)

- Re-examination of SQL:2011/SQL:2023 period semantics and proposals to standardize an explicit moving `NOW`, driven by bitemporal adoption in MariaDB/DB2 *(frontier — verify)*.
- Probabilistic temporal querying riding on the probabilistic-database / FPRAS revival (Suciu, Van den Broeck and collaborators) and on lifted/weighted model counting for safe fragments.
- Learned and kinetic interval indexes (groups around interval/temporal indexing in PostgreSQL and academic kinetic-data-structure lines) being evaluated for high-velocity expiring data — directly relevant to now-relative right endpoints *(frontier — verify)*.

## 8. Future Work

- A closed-form, *closed* algebra in which `NOW` and indeterminate endpoints compose (coalescing, aggregation, outer joins) with provable certain/possible-answer correctness.
- Index structures with worst-case $O(\log n)$ stabbing under endpoint distributions and $O(\log n)$ amortized advance of the now-diagonal, plus an I/O-optimal external variant.
- FPRAS-based query processors for indeterminate time with practical error/latency guarantees, integrated with cost-based optimization over moving predicates.

## 9. Key References

- **[Foundational]** J. Clifford, C. Dyreson, T. Isakowitz, C. S. Jensen, R. T. Snodgrass. *On the Semantics of "NOW" in Databases.* ACM Transactions on Database Systems / VLDB Journal, 1997.
- **[Foundational]** C. E. Dyreson, R. T. Snodgrass. *Supporting Valid-Time Indeterminacy.* ACM Transactions on Database Systems, 23(1), 1998.
- **[Foundational]** C. S. Jensen, C. E. Dyreson et al. (eds.). *The Consensus Glossary of Temporal Database Concepts.* In Temporal Databases: Research and Practice, LNCS 1399, 1998.
- **[SOTA]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* Journal of the ACM, 2012.
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (incomplete information, conditional tables).
- **[Survey]** M. H. Böhlen, A. Dignös, J. Gamper, C. S. Jensen. *Temporal Data Management — An Overview.* eBISS lectures, Springer, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
