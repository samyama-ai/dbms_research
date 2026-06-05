# Aggregation and Arithmetic in Logical Query Languages

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/aggregation-logic-semantics` · **Status:** open
> **Verification note:** Hella–Libkin–Nurmonen–Wong, *Logics with Aggregate Operators*, appeared in the Journal of the ACM 48(4), 2001 (not the Journal of Symbolic Logic); reference corrected.

## 1. Problem Statement
SQL and practical query languages compute over *interpreted* numeric domains: `GROUP BY`, `SUM`, `AVG`, `COUNT`, window functions, and arithmetic ($+,\times,\le$). Classical finite model theory studies *uninterpreted* relational structures, so it does not directly explain what such languages can and cannot express. The problem: build a **clean expressiveness theory** for logics with grouping/aggregation/arithmetic — define the right logic $\mathcal{L}_{\mathrm{aggr}}$, settle its expressive power, prove **capture results** (which logic = which complexity class on which structures), and obtain **inexpressibility** tools (locality/games) that survive interpreted operations.

Variants: (a) *expressiveness* — does aggregation add power beyond FO+counting? (b) *capture* — which aggregate logic captures PTIME / TC$^0$ / uniform-AC$^0$ with counting? (c) *bounded* vs *unbounded* numeric domains, and the role of order on the numeric sort.

## 2. Mathematical Foundations
The accepted model is a **two-sorted structure**: a finite *domain sort* (the database) and a *numeric sort* $\mathbb{N}$ or $\mathbb{Q}$ with interpreted $+,\times,<$. Aggregate logic adds **aggregate quantifiers** $\mathrm{aggr}_{\bar y}\,\theta(\bar x,\bar y)$ that map the set of $\bar y$ satisfying $\theta$ to a numeric value (Hella–Libkin–Nurmonen–Wong, *Logics with aggregate operators*, 2001). A canonical formalization is $\mathrm{FO}(\mathbf{Cnt})$ / $\mathrm{FO}(\mathbf{Aggr})$ where counting terms $\\#\bar y.\,\theta$ are first-class.

Key fact: relational algebra **with aggregation** $(\mathrm{ALG}_{\mathrm{aggr}})$ and $\mathrm{FO}(\mathbf{Aggr})$ over the natural-number sort with $+,\times$ have **equivalent** expressive power (Libkin). A central structural theorem is that aggregate logics remain **Gaifman-/Hanf-local** under suitable restrictions, *provided* the numeric sort cannot encode a linear order on the domain. Formally, with $\sigma$-restricted aggregation one proves: if $N_r(\bar a)\cong N_r(\bar b)$ then $q(\bar a)=q(\bar b)$, even when $q$ returns numeric values. This yields:
$$\text{connectivity, transitive closure} \notin \mathrm{FO}(\mathbf{Aggr},+,\times)\ \text{(unordered)}.$$
The subtlety: with an order on the domain, aggregation can simulate counting up to $n$ and locality breaks, so capture results (e.g., for TC$^0$ via $\mathrm{FO}(+,\times,\mathrm{Cnt})$) require ordered models.

## 3. State of the Art (SOTA)
The Hella–Libkin–Nurmonen–Wong framework (JACM 2001) plus Libkin's locality-for-aggregates (LICS/J. ACM line) is the theory-SOTA: aggregate operators do **not** help express recursive/global properties over unordered databases. On the **capture** side, $\mathrm{FO}$ with counting and arithmetic captures uniform $\mathrm{TC}^0$ over ordered structures (Barrington–Immerman–Straubing lineage). Systems-SOTA diverges: real SQL semantics (3-valued logic, NULLs, bag semantics, duplicate-sensitive aggregates) is only partially covered; Guagliardo–Libkin (2017) gave a rigorous bag/NULL semantics, but a complete expressiveness theory matching deployed SQL — including window functions and `WITH RECURSIVE` + aggregation — remains **open**.

## 4. Upper Bound
Over **ordered** structures, $\mathrm{FO}(\mathbf{Aggr},+,\times,<)$ sits inside (uniform) $\mathrm{TC}^0 \subseteq \mathrm{NC}^1 \subseteq \mathrm{LOGSPACE}$, so all such queries are evaluable in $O(\log n)$-depth bounded-fan-in-with-majority circuits and in $\mathrm{AC}^0[\mathrm{maj}]$. Concretely, every grouping/aggregation query is computable in $O(n\log n)$ to $O(n^{\omega})$ time depending on joins, and the *aggregation itself* is data-parallel and constant-depth. This is the best general upper bound: aggregation adds counting power but stays within threshold circuits over ordered data.

## 5. Lower Bound
Inexpressibility (the lower bound on *power*): over unordered structures, aggregation + arithmetic still cannot express any non-local property — parity-of-reachability, connectivity, even-cardinality of a definable set in the *domain* (as opposed to the numeric sort), via the locality theorem of §2. On the **complexity** side, separating $\mathrm{FO}(\mathbf{Aggr})$-capture-of-$\mathrm{TC}^0$ from $\mathrm{NC}^1$ is tied to the $\mathrm{TC}^0\stackrel{?}{=}\mathrm{NC}^1$ open problem — a genuine circuit lower-bound barrier.

## 6. The Gap
Two gaps. (1) **Theory vs deployed SQL**: existing clean results assume set semantics, total values, and idealized numeric sorts; deployed SQL is bag-semantic with NULLs, window frames, and recursive+aggregate interaction — no complete expressiveness/capture theorem covers all of it. (2) **Capture sharpness**: pinning the exact circuit class of arithmetic-FO collides with open circuit lower bounds ($\mathrm{TC}^0$ vs $\mathrm{NC}^1$ vs $\mathrm{P}$). Hence **open**.

## 7. Current Research (as of June 2026)
Libkin and collaborators (Geerts, Guagliardo, Toruńczyk) continue rigorous SQL semantics including nulls, bags, and approximate query answering. There is active work on **expressiveness of recursive SQL with aggregation** (`WITH RECURSIVE` interacting with `SUM`/`COUNT`) and its relation to Datalog-with-aggregation lattice semantics *(frontier — verify alignment with the 2024–2026 recursive-SQL standardization and DuckDB/Umbra implementations)*. Separately, the **GQL/SQL-PGQ** graph-query standards (2024) have reignited expressiveness questions for path + aggregation queries *(frontier — verify which aggregate constructs the 2024 ISO standards fixed)*.

## 8. Future Work
A complete locality theory for bag semantics and window functions; capture results for the recursive+aggregate fragment that mirror the lattice/semantics work in Datalog; tools for proving inexpressibility in presence of approximate/numeric operators; and reconciling the two-sorted logical model with property-graph aggregate queries.

## 9. Key References
- **[Foundational]** L. Hella, L. Libkin, J. Nurmonen, L. Wong. *Logics with Aggregate Operators.* Journal of the ACM 48(4), 2001. — [DOI](https://doi.org/10.1145/502090.502100)
- **[Foundational]** L. Libkin. *Expressive Power of SQL.* Theoretical Computer Science 296(3), 2003. — [DOI](https://doi.org/10.1016/S0304-3975(02)00736-3)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[SOTA]** P. Guagliardo, L. Libkin. *A Formal Semantics of SQL Queries, Its Validation, and Applications.* VLDB / PVLDB 11(1), 2017. — [DOI](https://doi.org/10.14778/3151113.3151116)
- **[Foundational]** N. Immerman. *Descriptive Complexity.* Springer, 1999 (FO+counting and TC$^0$ capture). — [DOI](https://doi.org/10.1007/978-1-4612-0539-5)

## 10. Worked Example

Consider one relation $\mathrm{Sales}(\text{store}, \text{amount})$ over the two-sorted model (store is a domain element; amount lives on the numeric sort):

| store | amount |
|-------|--------|
| A | 10 |
| A | 30 |
| B | 50 |

The SQL query `SELECT store, SUM(amount) FROM Sales GROUP BY store` is the aggregate term $q(s) = \mathrm{sum}_{a}\,\{a : \mathrm{Sales}(s,a)\}$, giving $q(A)=40,\ q(B)=50$.

**Why locality blocks reachability.** Now take a graph relation $E$ on the *domain* sort and ask "are $u,v$ connected?". A query in $\mathrm{FO}(\mathbf{Aggr},+,\times)$ has some locality radius $r$ (independent of $n$). Take two cycles of length $2r{+}2$: in $C_1$ pick antipodal $u,v$ (connected); in $C_2$ pick $u',v'$ from two *separate* copies (disconnected). The radius-$r$ neighborhoods $N_r(u,v)\cong N_r(u',v')$ are isomorphic disjoint paths, so any aggregate the logic computes returns identical numeric values on both — it cannot separate "connected" from "disconnected". Hence $\text{connectivity}\notin\mathrm{FO}(\mathbf{Aggr},+,\times)$ over unordered structures, even though summation/counting on the numeric sort is unrestricted.

---
*Part of the [DBMS Research catalog](../../README.md).*
