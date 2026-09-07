---
id: 34-schema-design-normalization/vertical-partitioning-optimality
title: "Cost-Optimal Vertical Partitioning"
topic: 34-schema-design-normalization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cost-Optimal Vertical Partitioning

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/vertical-partitioning-optimality` · **Status:** partially-solved

## 1. Problem Statement
Given a relation $R$ with attribute set $A=\{a_1,\dots,a_n\}$, a workload $W$ of queries each accessing a subset of attributes with a frequency, and a cost model $C$, partition $A$ into vertical fragments (column groups) so as to minimize total workload I/O / reconstruction cost. Fragments may be required to be disjoint (a partition) or allowed to overlap (replicated columns).

- **Decision variant:** Does a vertical partition with cost $\le \tau$ exist?
- **Optimization variant:** Minimize $\sum_{q\in W} f_q\,C(q,\Pi)$ over partitions $\Pi$.
- **Counting/enumeration:** number of distinct cost-equivalent partitions (relevant to search-space pruning).

The central tension: grouping co-accessed attributes reduces per-query scan cost, but queries with disjoint access sets impose conflicting preferences, plus **tuple-reconstruction joins** (stitching fragments back) add cost for queries spanning fragments.

## 2. Mathematical Foundations
A partition is a set partition of $A$; the number of candidate partitions is the **Bell number** $B_n$, which grows super-exponentially. Define an **affinity matrix** $M$ where $M_{ij}=\sum_{q:\,a_i,a_j\in q} f_q$ measures co-access. Classic formulations maximize within-fragment affinity (clustering) via the **Bond Energy Algorithm (BEA)** followed by binary partitioning.

In column-store cost models, query cost is
$$C(q,\Pi)=\sum_{F\in\Pi:\,F\cap \text{attrs}(q)\ne\emptyset}\big(\text{scan}(F)\big) + \text{recon}(q,\Pi),$$
where scanning a fragment touched for even one attribute pays for all its columns (in disjoint storage), and reconstruction stitches selected fragments via positional joins. The problem connects to **hypergraph partitioning** (queries = hyperedges over attributes) and to **graph clustering / correlation clustering**, both of which underpin its hardness.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The general cost-driven problem is NP-hard; practical solvers use ILP for small $n$, and graph/affinity heuristics (BEA + binary partitioning of Navathe et al.) for larger instances. Branch-and-bound with affinity-based pruning gives optimal solutions for moderate $n$.
- **Systems-SOTA:** Automated vertical partitioning advisors — **AutoPart** (Papadomanolakis & Ailamaki, SSDBM 2004), **HYRISE** (Grund et al., VLDB 2010) for hybrid OLTP/OLAP layouts, **Hyrise/data-blocks** and column-group selection in commercial column stores (Vertica, SQL Server columnstore). **O2P / one-pass** approaches scale to thousands of attributes with near-optimal results on realistic workloads. Vertica's automatic projection (DBD) design is a strong production exemplar.

This is "partially-solved": excellent heuristics and exact solvers for realistic sizes exist, but provable near-optimality at full scale under realistic (non-linear, recon-aware) cost models is unresolved.

## 4. Upper Bound
For the **disjoint-partition** formulation with additive scan costs and no reconstruction term, the problem is a clustering objective for which BEA-based and graph-cut heuristics run in $O(n^2|W|)$ per iteration with strong empirical results. Exact ILP/branch-and-bound is exponential in $n$ but tractable for $n$ in the low tens. **O2P** achieves a single-pass, scalable algorithm whose solutions are empirically within a few percent of optimal but **without a proven approximation ratio**. No constant-factor approximation is known for the recon-aware objective.

## 5. Lower Bound
Cost-optimal vertical partitioning is **NP-hard** (reduction from set/graph-partitioning–style problems; the hypergraph-partitioning embedding gives APX-hardness for the general weighted objective). With reconstruction joins, minimizing cost generalizes problems related to **min-cut hypergraph partitioning**, which is NP-hard and hard to approximate within any constant under standard assumptions. No fine-grained (SETH/3SUM) conditional lower bound specific to vertical partitioning is established; the hardness is classical NP-hardness plus inapproximability inherited from hypergraph partitioning.

## 6. The Gap
The gap is between (i) NP-hardness / APX-hardness of the general recon-aware objective and (ii) heuristics with strong empirical—but unproven—quality. It is **genuinely open** whether a constant-factor approximation exists for realistic cost models, and whether exact solvers can scale beyond a few dozen attributes. Closing it requires either a provable approximation under structural assumptions on workloads (e.g., bounded query width) or a matching inapproximability result.

## 7. Current Research (as of June 2026)
- Learned/cost-model-driven partitioning that replaces hand-tuned cost formulas with calibrated or learned estimators *(frontier — verify)*.
- Workload-adaptive re-partitioning integrated into self-driving systems (CMU NoisePage / OtterTune lineage) *(frontier — verify)*.
- Joint vertical + horizontal + index design solved together rather than sequentially *(frontier — verify)*.
- Groups: Ailamaki (EPFL), Plattner/Grund (HPI, HYRISE), TUM (Neumann), CMU (Pavlo).

## 8. Future Work
- Approximation algorithms with guarantees for recon-aware cost.
- Scalable exact methods (better B&B / column generation) for hundreds of attributes.
- Unified co-design with indexing, materialized views, and compression-aware costs.
- Online vertical re-layout with bounded migration cost under workload drift.

## 9. Key References
- **[Foundational]** S. Navathe, S. Ceri, G. Wiederhold, J. Dou. *Vertical Partitioning Algorithms for Database Design.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1994.2209)
- **[Foundational]** D. Cornell, P. Yu. *An Effective Approach to Vertical Partitioning for Physical Design of Relational Databases.* IEEE TSE, 1990. — [DOI](https://doi.org/10.1109/32.44388)
- **[SOTA]** S. Papadomanolakis, A. Ailamaki. *AutoPart: Automating Schema Design for Large Scientific Databases.* SSDBM, 2004. — [DOI](https://doi.org/10.1109/SSDM.2004.1311234)
- **[SOTA]** M. Grund, J. Krüger, H. Plattner, A. Zeier, P. Cudre-Mauroux, S. Madden. *HYRISE: A Main Memory Hybrid Storage Engine.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1921071.1921077), [PDF](https://www.vldb.org/pvldb/vol4/p105-grund.pdf)
- **[SOTA]** A. Jindal, J. Dittrich. *Relax and Let the Database Do the Partitioning Online (O2P).* BIRTE/related, 2011. — [DOI](https://doi.org/10.1007/978-3-642-33500-6_5)

## 10. Worked Example

Relation $R$ with attributes $A=\{a_1,a_2,a_3\}$, each column costing 1 unit to scan. Workload of two queries, each $f_q=1$:

- $q_1$ reads $\{a_1,a_2\}$
- $q_2$ reads $\{a_2,a_3\}$

A disjoint fragment is scanned in full if it touches *any* attribute the query needs. Ignore reconstruction for simplicity.

**Candidate partitions** (Bell number $B_3 = 5$):

- $\{a_1a_2a_3\}$ (all-in-one): each query scans the single 3-wide fragment → cost $3+3 = 6$.
- $\{a_1\}\{a_2\}\{a_3\}$ (full split): $q_1$ scans $a_1,a_2$ → 2; $q_2$ scans $a_2,a_3$ → 2; total $= 4$.
- $\{a_1a_2\}\{a_3\}$: $q_1$ scans the $a_1a_2$ fragment → 2; $q_2$ scans $a_1a_2$ (for $a_2$) + $a_3$ → $2+1=3$; total $= 5$.
- $\{a_2a_3\}\{a_1\}$: symmetric → $5$.
- $\{a_1a_3\}\{a_2\}$: $q_1$ scans $a_1a_3$+$a_2$ → 3; $q_2$ scans $a_1a_3$+$a_2$ → 3; total $=6$.

**Optimum:** full split, cost $4$. The shared attribute $a_2$ has conflicting co-access (paired with $a_1$ in $q_1$, $a_3$ in $q_2$), so no grouping helps — isolating it wins. The affinity matrix here has $M_{a_1 a_2}=M_{a_2 a_3}=1$, $M_{a_1 a_3}=0$: a "path" with no clusterable triangle, exactly why BEA finds no profitable merge.

---
*Part of the [DBMS Research catalog](../../README.md).*
