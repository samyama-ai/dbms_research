# Query rewriting between document and relational

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/document-relational-rewriting` · **Status:** partially-solved

## 1. Problem Statement
Given a logical dataset that admits two physical designs — a **normalized relational** schema $R$ and an **embedded document** design $D$ (nested/denormalized) — translate queries provably correctly across them so that a query written against one design returns identical results when evaluated against the other.

- **Decision variant:** given queries $q_R$ over $R$ and $q_D$ over $D$ and a mapping $\mathcal{M}$ between designs, decide *equivalence* $q_R \equiv_{\mathcal{M}} q_D$.
- **Synthesis/optimization variant:** given $q_D$ and $\mathcal{M}$, *synthesize* a relational $q_R$ (and conversely) that is certain-answer correct and cost-minimal.
- **Bidirectional/round-trip variant:** maintain a lens so that updates on one side propagate correctly (view-update problem).

Correctness must hold under the document model's quirks: embedded arrays, optional/missing fields, ordering, and duplicate semantics.

## 2. Mathematical Foundations
Both designs are instances of **schema mappings**: source-to-target tuple-generating dependencies (s-t tgds) and equality-generating dependencies (egds). The semantics of translation is **data exchange** and **certain answers**: $\mathrm{cert}(q,I,\mathcal{M})=\bigcap\{q(J): J \models \mathcal{M}(I)\}$, computed via the **chase**. Nesting is modeled by **nested relational algebra (NRA)** with $\mathsf{nest}/\mathsf{unnest}$ and the complex-value calculus (Abiteboul–Hull–Vianu). Query equivalence under constraints is decidable for conjunctive queries via the **chase & backchase** and homomorphism characterization, but undecidable in general first-order/recursive fragments (Trakhtenbrot). Bidirectional correctness uses **lens** laws (GetPut/PutGet, Foster et al.). Cost-optimal rewriting connects to the **AGM bound** for join output size, since denormalization changes the join graph.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** chase-based rewriting and certain-answer query answering (Fagin–Kolaitis–Miller–Popa, *Data Exchange*, 2005; *Composing Schema Mappings*, 2004); **C&B** optimization with integrity constraints (Deutsch–Popa–Tannen). Nested-to-flat normalization via NRA conservativity (Wong; Van den Bussche).
- **Systems-SOTA:** **Apache Calcite** (relational⇄document adapters), MongoDB BI Connector / Atlas SQL, PostgreSQL `jsonb` with `json_table`/SQL:2016 `JSON_TABLE`, Couchbase **N1QL** (SQL++), and **AsterixDB/SQL++** (Ong, Papakonstantinou, Vernoux) which gives a clean algebra unifying SQL and JSON. DuckDB and Snowflake compile JSON-path navigation into relational unnest plans.

## 4. Upper Bound
For **conjunctive queries (CQs)** under weakly-acyclic tgds + egds, the chase terminates in polynomial time in the data and the certain answers are computable; equivalence/containment of CQs under such constraints is decidable. With a terminating chase, rewriting synthesis is in **EXPTIME** in query size but PTIME data complexity. SQL++ shows nested↔flat rewriting is *complete* for its algebra: every nested query has an equivalent flattened plan and vice versa (conservativity of NRA over flat inputs). Lens-based round-tripping is correct by construction for the tree-update fragment.

## 5. Lower Bound
- CQ containment is **NP-complete** (Chandra–Merlin); under arbitrary tgds, certain-answer evaluation and chase termination become **undecidable** (Deutsch–Nash–Remmel).
- Equivalence of queries over nested/complex values with arithmetic or arbitrary FO is **undecidable** (Trakhtenbrot).
- View-update determinacy is undecidable in general; even deciding whether a relational query is rewritable using views is $\Pi_2^p$/undecidable depending on the language (Nash–Segoufin–Vianu).

## 6. The Gap
"Partially solved": the **CQ + weakly-acyclic-constraint** core is closed and implemented (AsterixDB, Calcite). The open frontier is *cost-aware, full-SQL++* bidirectional rewriting that handles arrays with order, three-valued logic for missing fields, and aggregation/window functions while preserving certain-answer semantics — plus automatic, verified update propagation (lenses) beyond toy fragments. The gap is between decidable-but-restricted fragments and the messy full language used in practice.

## 7. Current Research (as of June 2026)
Verified query compilers and equivalence checkers (e.g., **Cosette**-style SMT/relational-equivalence provers, Chu–Cheung–Suciu) are being extended to nested/JSON semantics; SQL++ semantics work continues at UC San Diego (Papakonstantinou) and via the SQL:2023 JSON features. *(frontier — verify: claims of fully verified, order-preserving JSON_TABLE round-trip lenses in a shipping engine.)* Active: mapping inference between document and relational designs using LLM-assisted but formally checked synthesis.

## 8. Future Work
- Decidable rewriting fragments covering ordered arrays + aggregation.
- Certified compilers (proof-carrying rewrites) for SQL++ ⇄ SQL.
- Cost models making denormalization vs normalization choices AGM-aware.
- Practical bidirectional lenses for document updates with conflict semantics.

## 9. Key References
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* TCS / ICDT, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [full text](http://webdam.inria.fr/Alice/)
- **[Foundational]** A. Chandra, P. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[SOTA]** K. Ong, Y. Papakonstantinou, R. Vernoux. *The SQL++ Query Language: Configurable, Unifying and Semi-structured.* arXiv:1405.3631, 2014. — [arXiv](https://arxiv.org/abs/1405.3631)
- **[SOTA]** A. Deutsch, L. Popa, V. Tannen. *Query Reformulation with Constraints.* SIGMOD Record, 2006. — [DOI](https://doi.org/10.1145/1147376.1147377)
- **[Foundational]** J. N. Foster et al. *Combinators for Bidirectional Tree Transformations (Lenses).* ACM TOPLAS, 2007. — [DOI](https://doi.org/10.1145/1232420.1232424)

## 10. Worked Example

Two physical designs of the same data. **Relational (normalized):**

`Users(uid, name)` = $\{(1,\text{Ann}), (2,\text{Bob})\}$
`Orders(oid, uid, item)` = $\{(10,1,\text{pen}), (11,1,\text{ink}), (12,2,\text{mug})\}$

**Document (embedded):**
```json
{ "uid":1, "name":"Ann", "orders":[{"item":"pen"},{"item":"ink"}] }
{ "uid":2, "name":"Bob", "orders":[{"item":"mug"}] }
```

The schema mapping $\mathcal{M}$ is the s-t tgd
$$\textsf{Users}(u,n) \wedge \textsf{Orders}(o,u,i) \;\to\; \exists\,\textsf{doc}:\ \textsf{doc}.uid{=}u \wedge \textsf{doc}.name{=}n \wedge i \in \textsf{doc}.orders.item.$$

**Rewriting a query.** Document query $q_D$: "items of user 1" = `$.orders[*].item where uid=1`, returning $\{\text{pen},\text{ink}\}$. Its certified relational rewrite is the CQ
$$q_R(i) \,{:}{-}\, \textsf{Users}(1,n),\ \textsf{Orders}(o,1,i),$$
which also yields $\{\text{pen},\text{ink}\}$ — the *unnest* in $q_D$ becomes a *join* in $q_R$. The chase of the relational instance through $\mathcal{M}$ produces exactly the two documents above, and certain-answer correctness means both queries agree on every model of $\mathcal{M}$.

**Where it breaks (the gap).** If a third user has *no* orders, the embedded `orders:[]` vs. a missing relational row forces three-valued reasoning, and array *order* (pen before ink) is not preserved by the unordered tgd — exactly the order/missing-field cases section 6 flags as open.

---
*Part of the [DBMS Research catalog](../../README.md).*
