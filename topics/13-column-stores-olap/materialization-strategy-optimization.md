---
id: 13-column-stores-olap/materialization-strategy-optimization
title: "Late vs. Early Materialization Optimization"
topic: 13-column-stores-olap
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Late vs. Early Materialization Optimization

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/materialization-strategy-optimization` · **Status:** open

## 1. Problem Statement

In a column-store plan, each operator can consume/produce either **values** (early materialization — stitch columns into tuples up front) or **positions** (late materialization — carry position lists / selection bitmaps and fetch values only when needed). Decide, **per operator (or per edge) in a query plan**, the materialization timing that minimizes total cost: tuple-reconstruction work plus intermediate-result size plus the cost of accessing columns in (un)favorable orders.

- **Optimization variant:** Given a physical plan DAG, assign each column-access edge a strategy in $\{$early, late$\}$ (and a position-representation: bitmap vs. position list vs. RID-list) to minimize total estimated cost.
- **Decision variant:** Is there a strategy assignment with cost $\le C$?

The choice interacts with selectivity, value width, access locality, encoding (coded vs. decoded), and whether downstream operators can run on compressed/coded data.

## 2. Mathematical Foundations

Let a plan be a DAG with operators $o_1,\dots,o_k$. A **materialization policy** $\pi$ assigns each column reference a fetch point. The cost decomposes as

$$
\mathrm{Cost}(\pi) = \sum_{\text{edges } e} \big[ \underbrace{\sigma_e\, w_e\, a_e}_{\text{value access}} + \underbrace{p_e}_{\text{position carry}} + \underbrace{\rho_e}_{\text{reconstruction/stitch}} \big],
$$

where $\sigma_e$ is selectivity reaching the edge, $w_e$ value width, $a_e$ access cost (sequential vs. random — late access can be random/out-of-order), $p_e$ position-list size, and $\rho_e$ the stitch cost. Late materialization wins when high selectivity drops $\sigma_e$ before paying $w_e a_e$; early wins when access would otherwise be random and selectivity is low.

The combinatorial core resembles **join-order/operator-physical-property optimization**: decisions are non-local because a column fetched late by one operator may need to be re-sorted or re-positioned for another, and **position-order divergence** (operators that reorder positions, e.g., sort, hash) creates reconstruction dependencies. This embeds in the System-R style **physical-property-aware plan search**, which is NP-hard in general.

## 3. State of the Art (SOTA)

- **Foundational:** Abadi, Myers, DeWitt, Madden, *Materialization Strategies in a Column-Oriented DBMS* (ICDE 2007), gave the early/late taxonomy and cost models; showed late materialization usually wins but not always (low selectivity, wide tuples, many predicates).
- **Systems-SOTA:** Vectorwise/Vertica use selection vectors and defer materialization; **DuckDB**, **Velox**, and **Photon** (Databricks, SIGMOD 2022) carry selection vectors through vectorized pipelines, effectively a fixed late-leaning policy with heuristics.
- Most engines use **rule-based heuristics**, not provably optimal per-operator assignment.

## 4. Upper Bound

For **tree-shaped** plans where reconstruction dependencies form a forest, a bottom-up **dynamic program** over the operator tree computes an optimal early/late assignment in $O(k)$ states given calibrated selectivities — analogous to Selinger DP. With $b$ position-representation choices per edge, the DP is $O(k\, b)$. For general DAGs with shared subplans, the exact problem is NP-hard and engines fall back to greedy/cost-threshold heuristics.

## 5. Lower Bound

The general DAG version (shared intermediates, operators that permute positions) is **NP-hard**: it generalizes physical-plan selection with interesting orders, which encodes problems equivalent to optimal join ordering / weighted constraint assignment. No fine-grained conditional bound is established specifically for materialization timing; the hardness is classical NP-hardness inherited from plan optimization with order/property constraints. A separate **information-theoretic** lower bound governs reconstruction itself (see the tuple-reconstruction lower-bounds problem).

## 6. The Gap

**Open.** The tree case is essentially closed (poly DP), but real OLAP plans are DAGs with sorts, hash repartitioning, and shared scans. We lack (a) a provable approximation for the DAG case, and (b) cost models robust to estimation error — wrong selectivity estimates flip the early/late decision. Closing it needs both an approximation guarantee and estimation-error-aware (robust) policies.

## 7. Current Research (as of June 2026)

- **Adaptive / runtime** materialization that switches strategy mid-pipeline as observed selectivity deviates from estimates *(frontier — verify)*.
- Materialization decisions co-optimized with **compressed execution** so coded columns are reconstructed lazily and only when an operator truly needs values.
- Learned cost models feeding the early/late decision in vectorized engines *(frontier — verify)*.
- Groups: MIT (Madden), CWI/TUM vectorized-engine lineage, Databricks (Photon team).

## 8. Future Work

- Approximation algorithms for DAG-shaped materialization with shared subplans.
- Robust/regret-bounded policies under cardinality-estimation uncertainty.
- Unified objective combining materialization, encoding selection, and tuple-reconstruction lower bounds.

## 9. Key References

- **[Foundational]** Abadi, Myers, DeWitt, Madden. *Materialization Strategies in a Column-Oriented DBMS.* ICDE, 2007. — [PDF](http://www.cs.umd.edu/~abadi/papers/abadiicde2007.pdf)
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Behm et al. *Photon: A Fast Query Engine for Lakehouse Systems.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526054)
- **[Foundational]** Stonebraker et al. *C-Store: A Column-oriented DBMS.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/StonebrakerABCCFLLMOORTZ05.html)
- **[Survey]** Abadi, Boncz, Harizopoulos, Idreos, Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Query: `SELECT name WHERE age > 60` over a column-store with $n=10^6$ rows. The `age` column is $4$ B/value; `name` is $w=40$ B/value. Predicate selectivity $\sigma = 0.01$ (10,000 survivors).

**Early materialization** stitches `(age, name)` tuples up front, then filters: it touches all $10^6$ name values $= 40$ MB of `name` access regardless of selectivity.

**Late materialization** scans `age` only, producing a position list of the $10^4$ survivors, then fetches just those `name` values: $10^4 \times 40\,\text{B} = 0.4$ MB — a $100\times$ reduction in `name` bytes, matching $1/\sigma$.

The catch is access pattern: the late fetch is **random** (positions scattered), cost $a_e$ per value. If random access is $\sim 50\times$ slower per byte than sequential, late still wins here ($0.4\,\text{MB}\times 50 = 20$ < $40$ MB sequential). But flip selectivity to $\sigma=0.8$: late fetches $0.8 n$ values randomly $= 32\,\text{MB}\times 50$, far worse than $40$ MB sequential early. This selectivity crossover is exactly why Abadi et al. show late "usually but not always" wins, and why a wrong $\sigma$ estimate flips the decision.

---
*Part of the [DBMS Research catalog](../../README.md).*
