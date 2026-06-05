# Index Selection Complexity & Approximability

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/index-selection-complexity` · **Status:** partially-solved

## 1. Problem Statement
Given a workload $W = \{(q_1, f_1), \dots, (q_m, f_m)\}$ of queries with frequencies, a set of *candidate* indexes $\mathcal{I}$, a per-index storage cost $s : \mathcal{I} \to \mathbb{R}_{\ge 0}$, and a storage budget $B$, the **Index Selection Problem (ISP)** asks for a configuration $S \subseteq \mathcal{I}$ with $\sum_{i \in S} s(i) \le B$ maximizing the workload *benefit* $\mathrm{ben}(S) = \sum_j f_j \cdot \big(c_\emptyset(q_j) - c_S(q_j)\big)$, where $c_S(q)$ is the optimizer's estimated cost of $q$ under configuration $S$.

Variants:
- **Decision:** Is there $S$ with cost $\le B$ and benefit $\ge t$? (NP-complete.)
- **Optimization:** Maximize benefit subject to $B$ (the practical form).
- **Min-cost:** Minimize total (run + build + storage) cost achieving a benefit target.
- **Counting:** Number of maximal feasible configurations (relevant to search-space sizing).

The central open question is the *tight* approximation ratio achievable in polynomial time, not merely the long-known NP-hardness.

## 2. Mathematical Foundations
The cost function $c_S$ is not arbitrary: in the *atomic* / non-interacting model, each query is served by its single best applicable index, so $\mathrm{ben}$ becomes a coverage-style function. Under the standard assumption that an index only ever *reduces* a query's cost and benefits are taken as the best single index per query, $\mathrm{ben}(\cdot)$ is **monotone submodular**: for $A \subseteq B$ and $i \notin B$, $\mathrm{ben}(A \cup \{i\}) - \mathrm{ben}(A) \ge \mathrm{ben}(B \cup \{i\}) - \mathrm{ben}(B)$. This places ISP within the framework of submodular maximization under a **knapsack constraint**.

Key results imported:
- Nemhauser–Wolsey–Fisher: greedy gives $(1 - 1/e)$ for cardinality-constrained monotone submodular max.
- Sviridenko (2004): $(1 - 1/e)$ for a single **knapsack** constraint via partial enumeration + greedy.
- Feige (1998): $(1 - 1/e)$ is optimal for Max-$k$-Cover unless $\mathrm{P}=\mathrm{NP}$, transferring inapproximability to the coverage special case.

Interaction breaks submodularity: when an index-intersection plan or covering index makes two indexes jointly worth more than the sum of parts, $\mathrm{ben}$ is no longer submodular (see *index-interaction-modeling*).

## 3. State of the Art (SOTA)
**Theory-SOTA:** Treating the non-interacting case as monotone submodular knapsack maximization yields a $(1-1/e)$-approximation (Sviridenko 2004; Khuller–Moss–Naor 1999 for the budgeted variant). Feige's $(1-1/e)$ hardness lower bound matches it for the coverage core.

**Systems-SOTA:** None of the deployed tools — Microsoft AutoAdmin/Database Tuning Advisor (Chaudhuri–Narasayya, VLDB 1997+), DB2 Design Advisor, Oracle SQL Access Advisor — pursue provable ratios; they use *candidate generation + cost-based greedy + enumeration with seeding*, calling the optimizer in "what-if" mode. Learned approaches (DTA's relaxation-based search; reinforcement-learning index advisors) optimize empirically without guarantees.

## 4. Upper Bound
Polynomial-time $(1 - 1/e) \approx 0.632$ approximation for the **non-interacting, monotone-submodular** model with a single knapsack (storage) budget, via Sviridenko's partial-enumeration greedy. For pure cardinality budgets (count of indexes), plain greedy already gives $(1-1/e)$ with $O(|\mathcal{I}| \cdot m)$ what-if calls. With $d$ linear budget constraints (storage + build-time), continuous-greedy + rounding gives $(1 - 1/e - \varepsilon)$.

## 5. Lower Bound
ISP is **NP-hard** (reduction from Knapsack / Set Cover; established in the early tuning-advisor literature). For the coverage core, **Feige's theorem** gives a $(1 - 1/e + \varepsilon)$ inapproximability under $\mathrm{P} \ne \mathrm{NP}$, so no PTAS exists for the submodular formulation. Once *index interactions* are admitted, the benefit can encode general (non-submodular) set functions, pushing the problem toward Max-Coverage-with-pairwise-bonuses / Dense-$k$-Subgraph regimes whose best ratios are polynomially bad, and conjecturally no constant-factor approximation exists.

## 6. The Gap
For the **non-interacting** model the gap is essentially **closed**: $(1-1/e)$ upper meets Feige's $(1-1/e)$ lower. The genuinely **open** gap is the *interacting* model: between the trivial constant-factor results that require submodularity and the (suspected, unproven) super-constant inapproximability of the general interaction-aware problem. Closing it requires either a structural characterization of "how non-submodular" real optimizer cost functions can be, or a hardness reduction calibrated to that structure.

## 7. Current Research (as of June 2026)
- Bridging learned cost models with approximation theory: when a learned $\hat{c}_S$ is $\epsilon$-accurate, can greedy's ratio be preserved? *(frontier — verify)*
- Parameterized/FPT analyses by number of relations or by *interaction degree* of the workload.
- Microsoft Gray Systems Lab and the DTA lineage continue empirical work; academic groups (CWI, TU Darmstadt, the "DB-BERT"/learned-advisor community) probe RL advisors against optimal small instances. Theoretical tightening of interaction-aware bounds is pursued in the submodular-optimization community (Buchbinder, Feldman). *(frontier — verify)*

## 8. Future Work
- A dichotomy theorem: which classes of optimizer cost functions admit constant-factor approximation.
- Instance-optimal / beyond-worst-case bounds exploiting low effective dimension of real workloads.
- Robust approximation under cost-estimate error (distributionally robust ISP).
- Hardness of the *interacting* problem under fine-grained or PCP-based assumptions.

## 9. Key References
- **[Foundational]** S. Chaudhuri, V. Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server.* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN97.html)
- **[Foundational]** G. L. Nemhauser, L. A. Wolsey, M. L. Fisher. *An analysis of approximations for maximizing submodular set functions—I.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)
- **[SOTA]** M. Sviridenko. *A note on maximizing a submodular set function subject to a knapsack constraint.* Operations Research Letters, 2004. — [DOI](https://doi.org/10.1016/S0167-6377(03)00062-2)
- **[SOTA]** S. Chaudhuri, V. Narasayya. *Anytime Algorithm of Database Tuning Advisor for Microsoft SQL Server.* (DTA), Microsoft, 2020. — [Microsoft Research](https://www.microsoft.com/en-us/research/publication/anytime-algorithm-of-database-tuning-advisor-for-microsoft-sql-server/)
- **[Survey]** S. Chaudhuri, V. Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN07.html)

## 10. Worked Example

**Greedy index selection under a cardinality budget.** Workload of 4 queries, each frequency $1$. Candidate indexes $\mathcal I=\{i_1,i_2,i_3\}$; each index, if chosen, serves a set of queries (saving $10$ per served query). Budget: pick $k=2$ indexes.

| index | queries served | benefit alone |
|---|---|---|
| $i_1$ | $\{q_1,q_2,q_3\}$ | $30$ |
| $i_2$ | $\{q_3,q_4\}$ | $20$ |
| $i_3$ | $\{q_4\}$ | $10$ |

This is monotone submodular (best-single-index-per-query coverage). **Greedy:** round 1 picks $i_1$ (benefit $30$, the max). Round 2 — marginal gains given $\{i_1\}$: $i_2$ adds only $q_4$ (since $q_3$ already covered) $=10$; $i_3$ adds $q_4 = 10$. Pick $i_2$. Result $\{i_1,i_2\}$ covers $\{q_1,q_2,q_3,q_4\}$, benefit $40$ = OPT here.

The guarantee: greedy is never worse than $(1-1/e)\approx 0.632$ of OPT. The worst case is tight — Feige's theorem shows no poly-time algorithm beats $(1-1/e)$ for the coverage core unless $\mathrm{P}=\mathrm{NP}$, so upper and lower bounds meet for this non-interacting model. The cost paid is $O(|\mathcal I|\cdot m) = O(3\times 4)=12$ "what-if" optimizer calls.

---
*Part of the [DBMS Research catalog](../../README.md).*
