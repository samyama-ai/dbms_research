# Multi-tenant query-result and plan sharing

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/multitenant-work-sharing` · **Status:** partially-solved

## 1. Problem Statement
In a shared serverless query service, many tenants issue overlapping work: similar table scans, common subexpressions, repeated joins, and structurally identical plans differing only in literals. **Work sharing** aims to compute a piece of work once and reuse it across concurrent or temporally close queries — scan sharing, materialized intermediate results (the "MQO" / shared-scan family), and cached compiled plans — to cut cost and latency.

The constraints that make the cloud variant hard are *cross-tenant*: (i) **isolation** — shared state must not leak one tenant's data or even the *existence* of their query to another; (ii) **billing fairness** — when one scan serves $k$ tenants, the cost must be attributed without over- or under-charging anyone; (iii) **policy heterogeneity** — tenants differ in row-level security, encryption keys, and freshness/SLO requirements.

Variants:
- **Decision:** given a set of in-flight queries, does a sharing schedule exist meeting all isolation + SLO constraints?
- **Optimization:** minimize total resource-seconds (or carbon, or $\$$) subject to per-tenant tail-latency and isolation constraints.
- **Online:** decide sharing as queries arrive without knowledge of the future.

## 2. Mathematical Foundations
Model queries as DAGs over relational-algebra operators. Common-subexpression sharing is the **Multi-Query Optimization (MQO)** problem: given query plans $Q_1,\dots,Q_n$, choose a global plan minimizing total cost where shared subexpressions are evaluated once. Formally, over an AND-OR DAG of candidate subexpressions with materialization costs $c(v)$ and reuse benefits $b(v)$, MQO is the problem of selecting a minimum-cost subset closed under operator dependencies — equivalent to a **weighted directed Steiner / set-cover** instance, hence NP-hard.

Result-cache reuse rests on **query containment and equivalence**: a cached result for $Q'$ answers $Q$ iff $Q \sqsubseteq Q'$ plus a residual filter; for conjunctive queries containment is NP-complete (Chandra–Merlin) and decided by the **chase / homomorphism** test. Cardinality of shared scans is bounded by the **AGM bound** $|Q| \le \prod_e |R_e|^{x_e}$ for a fractional edge cover $x$.

Isolation can be cast information-theoretically: a sharing mechanism $M$ is *non-leaking* if tenant $A$'s view is statistically (or computationally) independent of tenant $B$'s private inputs, i.e. mutual information $I(\text{view}_A; D_B \mid \text{public}) = 0$, or a differential-privacy-style bound for usage/timing side channels.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** shared-scan engines (QPipe, IBM Blink/BLU, SharedDB, and circular-scan techniques in column stores) realize scan and operator sharing at scale. Snowflake's result cache and **Amazon Redshift's compiled-segment cache / result reuse**, and Microsoft's **Cloud-scale plan caching (Peregrine/QO learning)** are production exemplars. Materialized common subexpressions are scheduled by cost-based MQO in Microsoft SCOPE.
- **Theory-SOTA:** Sellis's MQO framework and Roy–Seshadri–Sudarshan–Bhobe greedy DAG-based MQO remain the canonical optimization results; containment-based result reuse derives from Chandra–Merlin and the **chase** (Aho–Sagiv–Ullman, Maier–Mendelzon–Sagiv).
- **Cross-tenant safety** is the genuinely newer front: secure shared computation borrows from secure multi-party / TEE-backed query processing and oblivious operators.

## 4. Upper Bound
MQO subexpression selection admits an $O(\log n)$-approximation via reduction to weighted set cover / directed Steiner tree (best general directed-Steiner ratio is $O(n^{\epsilon})$, but realistic two-level DAGs give logarithmic guarantees). Greedy DAG selection (Roy et al.) is a constant-competitive heuristic in practice. Scan sharing achieves throughput within a constant factor of optimal under a **single circular scan** model: $n$ concurrent scans served in $O(1)$ passes rather than $n$. Result-cache hit-testing for conjunctive queries is decided in **NP** (homomorphism), polynomial when queries are acyclic or bounded-treewidth (Yannakakis-style).

## 5. Lower Bound
- MQO (optimal common-subexpression selection) is **NP-hard** by reduction from set cover / Steiner tree; the directed Steiner formulation makes a $o(\log n)$ approximation unlikely (set-cover hardness, $(1-o(1))\ln n$ inapproximability under $P\neq NP$).
- Conjunctive-query **containment/equivalence is NP-complete** (Chandra–Merlin), so deciding cache reusability is NP-hard in general.
- **Isolation impossibility:** any deterministic sharing that exposes shared-cache *timing* admits a covert channel; eliminating timing side channels forces worst-case cost (no sharing benefit), a CAP-style tension between *cost-sharing* and *non-interference* — provable in the information-flow model.

## 6. The Gap
The classical *optimization* gap (MQO approximation) is essentially closed up to set-cover constants. The genuinely **open** gap is the *joint* problem: no framework gives provable guarantees that simultaneously (a) bound side-channel leakage (timing/billing), (b) attribute cost fairly (a cooperative-game / Shapley-value question), and (c) stay competitive online. Whether non-trivial cross-tenant sharing benefit is achievable under a strict differential-privacy timing budget is open — current systems trade safety for sharing heuristically.

## 7. Current Research (as of June 2026)
- Learned and **semantic result caches** that reuse subexpression results across tenants using embeddings of plan fragments *(frontier — verify)*.
- **Shapley-based cost attribution** for shared scans/results, connecting MQO to cooperative game theory for billing fairness.
- TEE- and oblivious-operator-backed sharing (work from CMU, Berkeley RISELab successors, Microsoft Research) to give cryptographic isolation while sharing scans.
- Snowflake/Databricks engineering on result-reuse safety under row-level security and key isolation *(frontier — verify)*.

## 8. Future Work
- A formal model unifying MQO cost-optimality with a per-tenant leakage budget.
- Online competitive analysis of shared materialization under adversarial arrivals.
- Truthful, Shapley-fair billing mechanisms that are also strategy-proof against tenants gaming workloads to offload cost.
- Sharing across *encrypted* tenants with provable non-interference.

## 9. Key References
- **[Foundational]** Timos Sellis. *Multiple-Query Optimization.* ACM TODS, 1988.
- **[Foundational]** Prasan Roy, S. Seshadri, S. Sudarshan, Siddhesh Bhobe. *Efficient and Extensible Algorithms for Multi Query Optimization.* SIGMOD, 2000.
- **[Foundational]** Ashok K. Chandra, Philip M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977.
- **[SOTA]** Stavros Harizopoulos, Vladislav Shkapenyuk, Anastassia Ailamaki. *QPipe: A Simultaneously Pipelined Relational Query Engine.* SIGMOD, 2005.
- **[SOTA]** Georgios Giannikis, Gustavo Alonso, Donald Kossmann. *SharedDB: Killing One Thousand Queries with One Stone.* VLDB, 2012.
- **[Survey]** Serge Abiteboul, Richard Hull, Victor Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (chase, containment).

---
*Part of the [DBMS Research catalog](../../README.md).*
