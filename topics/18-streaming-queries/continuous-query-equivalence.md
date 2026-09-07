---
id: 18-streaming-queries/continuous-query-equivalence
title: "Continuous query containment and equivalence"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Continuous query containment and equivalence

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/continuous-query-equivalence` · **Status:** open

## 1. Problem Statement
Two **continuous queries** $Q_1, Q_2$ are **equivalent** if they produce the same output stream on every input stream, and $Q_1$ is **contained** in $Q_2$ ($Q_1 \sqsubseteq Q_2$) if its output is always a sub-stream of $Q_2$'s. Deciding these relations underlies query caching, multi-query sharing, rewriting (e.g. answering a query from a materialized continuous view), and provable optimizer correctness. The problem: characterize the **decidability and complexity** of containment/equivalence for continuous queries that combine relational operators with **windowing** (tumbling/sliding/session), **time/temporal predicates**, **stream-to-relation and relation-to-stream operators** (the CQL Istream/Dstream/Rstream model), and — at the hard end — **recursion** (Datalog-style continuous queries).

Variants: (i) *set/bag semantics* over snapshots; (ii) *order-and-timestamp-sensitive* stream equivalence (outputs must match as timestamped sequences, not just sets); (iii) equivalence *under a window/punctuation discipline*. Status open: classical relational containment is well-charted, but adding time semantics, windows, and recursion to the *streaming* output model yields cases whose decidability/complexity are unsettled.

## 2. Mathematical Foundations
For **conjunctive queries (CQs)**, containment is decidable and **NP-complete** via the existence of a **containment homomorphism** (Chandra–Merlin, 1977); equivalence of CQs reduces to mutual containment / minimization. For queries with **union** (UCQs) containment is still decidable; adding **inequalities** ($<,\le$) keeps it decidable but pushes complexity to $\Pi^p_2$. **Datalog containment** in a CQ is decidable but **2-EXPTIME**; **Datalog–Datalog containment is undecidable** (reduction from the containment of context-free languages / Datalog programs).

The streaming twist: a continuous query is a function from input streams to output streams. Using **CQL semantics** (Arasu–Babu–Widom), a continuous query unfolds to a family of relational snapshots indexed by time; equivalence becomes "agree on every snapshot under every valid arrival." Windows behave like time-parameterized selection; sliding windows interact with **temporal logic** (LTL/MTL) and **timed-automata** equivalence, where language equivalence of timed automata is **undecidable** in general — a source of hardness. **Bag semantics** containment (relevant because streams emit multiplicities) is notoriously open even for CQs (decidability of CQ bag-containment is a long-standing open problem).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Chandra–Merlin homomorphism theorem (CQ containment, NP-complete); van der Meyden and others on containment with order/inequalities; results on **conjunctive query containment over temporal/sequence data**; CQL's formal semantics giving a snapshot-reducibility framework.
- **Systems-SOTA:** continuous multi-query optimizers (NiagaraCQ, TelegraphCQ/CACQ, Flink/Spark logical-plan equalization) detect *syntactic/structural* sharing and equivalence heuristically; differential-dataflow / IVM systems reason about equivalence of incremental plans. No system implements complete semantic containment for windowed/recursive continuous queries.

## 4. Upper Bound
For the **windowed-conjunctive fragment** (CQs with bounded sliding/tumbling windows expressed as time predicates, no recursion), containment is **decidable in $\Pi^p_2$ / NP-hard-and-in-PSPACE** depending on the predicate class, by reducing each snapshot to relational CQ-with-inequalities containment and quantifying over window offsets. For **recursive (Datalog) continuous queries contained in a non-recursive one**, decidability holds with a **2-EXPTIME** upper bound (lifting classical Datalog⊑UCQ results). Equivalence in these decidable fragments inherits the same bounds.

## 5. Lower Bound
CQ containment is **NP-complete** (Chandra–Merlin) — already intractable for the simplest fragment. Adding inequalities makes it **$\Pi^p_2$-hard**. **Datalog⊑Datalog containment is undecidable**, so full recursive continuous-query containment is undecidable. Order/timestamp-sensitive equivalence reduces to **timed-automata language equivalence**, which is **undecidable**, giving an undecidability barrier for the fully timestamp-sensitive streaming model. **Bag-semantics CQ containment** decidability is **open** (long-standing), and since streams carry multiplicities this open problem sits directly under streaming equivalence.

## 6. The Gap
The relational core is mapped (CQ = NP-complete; recursion = undecidable). The genuine **open** gaps are streaming-specific: (a) decidability/complexity of containment under *timestamp- and order-sensitive* stream equivalence (between the decidable snapshot view and the undecidable timed-automata view, the exact boundary is unknown); (b) the inherited **bag-containment** open problem; (c) equivalence *modulo a window/punctuation discipline* (queries equal only on streams respecting given watermark bounds). Closing the gap means precisely delineating which window+temporal+recursion fragments are decidable and at what complexity — and building a complete decision procedure for the largest practical decidable fragment.

## 7. Current Research (as of June 2026)
Active: semantic-equivalence checking for incremental/streaming dataflow plans to validate optimizer rewrites (extending SQL equivalence verifiers like UDP/Cosette/SPES to windowed and incremental queries) *(frontier — verify)*; decidable temporal/streaming Datalog fragments and their containment; equivalence reasoning for differential dataflow. Groups: theory groups working on query containment (Barceló, Pichler, ten Cate), Oxford/RelationalAI (Datalog/IVM), and verification-of-SQL-rewrites groups (Washington — Cheung/Wang lineage).

## 8. Future Work
- Pin down decidability of timestamp/order-sensitive continuous-query equivalence.
- Resolve (or restrict around) bag-semantics containment for streaming multiplicities.
- Containment modulo watermark/punctuation disciplines (assume-correct-arrival reasoning).
- A complete, implemented decision procedure for the maximal practical decidable fragment, wired into a streaming optimizer for safe caching/rewriting.

## 9. Key References
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Foundational]** A. Arasu, S. Babu, J. Widom. *The CQL Continuous Query Language: Semantic Foundations and Query Execution.* VLDB Journal, 2006. — [DOI](https://doi.org/10.1007/s00778-004-0147-z)
- **[Foundational]** Y. Sagiv, M. Yannakakis. *Equivalences among Relational Expressions with the Union and Difference Operators.* JACM, 1980. — [DOI](https://doi.org/10.1145/322217.322221)
- **[Survey]** R. van der Meyden. *The Complexity of Querying Indefinite Data about Linearly Ordered Domains.* JCSS, 1997. — [DOI](https://doi.org/10.1006/jcss.1997.1455)

## 10. Worked Example

**Conjunctive-query containment via homomorphism (Chandra–Merlin).** Over a graph relation $E(x,y)$, consider two CQs asking "which nodes start a path":

$$Q_1(a) \leftarrow E(a,b),\, E(b,c) \qquad\text{(a path of length 2 from }a)$$
$$Q_2(a) \leftarrow E(a,b) \qquad\text{(an edge out of }a)$$

Claim: $Q_1 \sqsubseteq Q_2$. By the Chandra–Merlin theorem, $Q_1 \sqsubseteq Q_2$ iff there is a **containment homomorphism** $h$ from $Q_2$'s body to $Q_1$'s body that fixes the head variable. Map $h: a \mapsto a,\ b \mapsto b$. Then $Q_2$'s atom $E(a,b)$ maps to $E(a,b)$, which appears in $Q_1$'s body — homomorphism found, so $Q_1 \sqsubseteq Q_2$. ✓ (Intuitively, every node with an outgoing length-2 path also has an outgoing edge.)

The converse fails: no homomorphism maps $Q_1$'s two atoms into $Q_2$'s single atom while preserving the chain $a\!\to\!b\!\to\!c$, so $Q_2 \not\sqsubseteq Q_1$ — witnessed by the database $\{E(1,2)\}$, where $Q_2$ returns $\{1\}$ but $Q_1$ returns $\varnothing$.

Finding $h$ is NP-complete (it is essentially a homomorphism/embedding search). **Streaming twist:** add a $5$-second sliding window so each atom carries a timestamp predicate $|t_a - t_b| \le 5$. Containment now must hold on *every snapshot*, and the homomorphism must respect the window/inequality constraints — pushing the problem from NP toward $\Pi^p_2$ and, once order-sensitive timestamps enter, toward the undecidable timed-automata regime.

---
*Part of the [DBMS Research catalog](../../README.md).*
