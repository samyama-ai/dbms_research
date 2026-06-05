# Cross-model join algorithms and bounds

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/cross-model-join-algorithms` · **Status:** open

## 1. Problem Statement

A multi-model query joins data whose join keys live in *different data models* simultaneously:

- a **graph** edge relation $E(s, t)$ (path/reachability semantics),
- a **document** field extracted as $D(\mathrm{id}, p \!\to\! v)$ (nested, multi-valued, schemaless),
- a **relational** column $R(\mathrm{id}, A)$.

Example: "users (relational) whose `address.city` (document) matches a city node within 2 hops (graph) of a hub." The query is a conjunctive query (CQ) over heterogeneous predicates whose join keys are bound across models.

Variants:
- **Optimization:** compute the join result with minimum total time/IO.
- **Worst-case-optimal (WCO) decision/enumeration:** match the AGM/fractional-cover bound for the CQ when some atoms are *graph-recursive* or *array-multivalued* (not classical finite relations).
- **Counting:** $\#$-answers, which is #P-hard in general for CQs with projection.

The novelty over classical join theory: graph atoms encode *transitive closure* (infinite-arity-like), document atoms encode *array unnesting* (one id → many tuples), and relational atoms are standard — and an optimal plan must interleave all three.

## 2. Mathematical Foundations

Write the query as a CQ $Q(\bar z) \,{:}{-}\, A_1, \dots, A_m$. For finite relational atoms the **AGM bound** (Atserias–Grohe–Marx) caps the output:
$$|Q| \le \prod_{i} |A_i|^{x_i}, \quad \text{for any fractional edge cover } x \text{ of the hypergraph } H(Q).$$
**Worst-case-optimal join** algorithms (NPRR / Generic Join, Ngo–Porat–Ré–Rudra; LeapFrog TrieJoin, Veldhuizen) meet this bound in time $\tilde O(\mathrm{AGM}(Q))$.

Cross-model wrinkles:
- **Graph atoms** = regular path queries (RPQs); their answer relation is the transitive closure, whose size is itself bounded by reachability and computed via semi-naïve Datalog / matrix products. AGM does not directly bound recursive atoms; one needs *evaluation under fixpoint* and the PG-Datalog framework.
- **Array/document atoms** correspond to *bag* unnesting; the relevant bound is the AGM bound with multiplicities, and degree-bounded refinements (the **PANDA**/entropic bounds of Khamis–Ngo–Suciu) tighten estimates using functional dependencies that hold per-path.
- **Information-theoretic / polymatroid bounds:** the tightest known output bounds come from Shannon-inequality LP relaxations (entropic cone), giving the degree-aware bound that subsumes AGM.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Generic Join + PANDA give WCO and degree-aware bounds for relational CQs; FAQ/AJAR (Khamis–Ngo–Rudra) unify joins with aggregation. Free-join (Wang–Willsey–Suciu, SIGMOD 2023) generalizes WCO and binary plans.
- **Graph-side:** worst-case-optimal RPQ/graph-pattern evaluation (Hogan et al.; the Ring/CDRW index of Arroyuelo et al., 2021–2024) gives WCO basic graph patterns in compact space.
- **Systems-SOTA:** RelationalAI / EmptyHeaded / Umbra-style WCO engines; ArangoDB, OrientDB, and Microsoft Cosmos DB execute cross-model joins but with classical binary join plans (no WCO guarantee across models). Apache AGE / DuckDB-PGQ add graph atoms over relational engines.

## 4. Upper Bound

For the *finite, non-recursive* fragment (graph atoms pre-materialized to edge relations, arrays unnested to bags), Generic Join evaluates the cross-model CQ in $\tilde O(\mathrm{AGM}(Q) + |\text{input}| + |\text{output}|)$ — **worst-case optimal**, in the RAM model with trie/hash indices. With degree constraints (per-path FDs, bounded vertex degree), PANDA achieves the smaller polymatroid bound. For RPQ atoms, evaluation is $\tilde O(|E| \cdot |\text{output}|)$ via semi-naïve fixpoint composed with the WCO join. No single algorithm is known to be optimal when fixpoint and join are *interleaved* (closing graph atoms lazily inside the join).

## 5. Lower Bound

- **Conditional (fine-grained):** Boolean conjunctive triangle-style queries are as hard as detecting triangles; under the 3SUM / APSP / combinatorial-BMM hypotheses, no truly subquadratic algorithm exists for the corresponding 2-path/triangle cross-model joins (Williams; Abboud–Williams).
- **Counting:** $\#$CQ with projection is **#P-hard** (folklore from #P-completeness of $\#$-clique); even approximate counting of cross-model join answers is hard for self-join-free graph patterns under standard assumptions.
- **AGM tightness:** the AGM bound is tight (Atserias–Grohe–Marx), so any join algorithm reading the whole output must take $\Omega(\mathrm{AGM}(Q))$ — establishing optimality of WCO for the finite fragment but leaving the *recursive/lazy-graph* case open.

## 6. The Gap

For the **finite, fully-materialized** fragment the gap is essentially **closed** (Generic Join/PANDA meet AGM/polymatroid bounds). It is **genuinely open** for: (1) interleaving RPQ fixpoint with WCO join so graph atoms are explored *on demand* with a matching bound; (2) WCO enumeration with array/multiplicity semantics and per-path FDs combined; (3) output bounds that account for transitive-closure atoms (AGM ignores recursion). Closing it needs a unified bound over the entropic cone *plus* fixpoint, and an algorithm meeting it.

## 7. Current Research (as of June 2026)

- Free-join and factorized-execution extensions to graph + document atoms (Suciu, Olteanu groups).
- Compact WCO graph indices (Ring family) being combined with relational columns *(frontier — verify)*.
- Degree-aware (PANDA) optimizers shipping ideas into DuckDB-PGQ / Umbra / RelationalAI *(frontier — verify)*.
- Groups: UW (Suciu, Ré-lineage), Oxford (Olteanu), Chile/IMFD (Arroyuelo, Hogan, Navarro), TUM (Neumann).

## 8. Future Work

- Unified cost/output model spanning recursion, multiplicity, and FDs.
- Lazy graph-atom expansion inside WCO joins with optimality proof.
- Fine-grained lower bounds tailored to mixed graph+document+relational patterns.
- Adaptive plans switching between WCO and binary joins per sub-pattern.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 / SICOMP, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018. — [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017. — [DOI](https://doi.org/10.1145/3034786.3056105)
- **[SOTA]** Wang, Willsey, Suciu. *Free Join: Unifying Worst-Case Optimal and Traditional Joins.* SIGMOD, 2023. — [arXiv](https://arxiv.org/abs/2301.10841)
- **[SOTA]** Arroyuelo, Hogan, Navarro, et al. *Worst-case Optimal Graph Joins in Almost No Space (The Ring).* SIGMOD, 2021. — [DBLP](https://dblp.org/rec/conf/sigmod/ArroyueloHNRRS21.html)
- **[Foundational]** Abboud, Williams. *Popular Conjectures Imply Strong Lower Bounds for Dynamic Problems.* FOCS, 2014. — [DOI](https://doi.org/10.1109/FOCS.2014.53)

## 10. Worked Example

Take the triangle-shaped cross-model CQ
$$Q(a,b,c) \,{:}{-}\, R(a,b),\ D(b,c),\ E(c,a),$$
where $R$ is a relational join column, $D$ a document array-unnest atom, and $E$ a graph edge relation, each of size $|R|=|D|=|E|=N$.

**AGM bound.** The query hypergraph is a 3-cycle; its minimum fractional edge cover assigns $x_i = \tfrac12$ to each atom (each variable $a,b,c$ is covered: e.g. $a$ by $R,E$ giving $\tfrac12+\tfrac12=1$). So
$$|Q| \le |R|^{1/2}|D|^{1/2}|E|^{1/2} = N^{3/2}.$$

**Why binary plans lose.** Any pairwise plan, say $(R \bowtie D)\bowtie E$, can produce an intermediate $R\bowtie D$ of size $\Theta(N^2)$ on adversarial data (one heavy value of $b$), then filter most of it away — total work $\Theta(N^2) \gg N^{3/2}$. A worst-case-optimal join (Generic Join / LeapFrog TrieJoin) instead intersects all three atoms variable-by-variable and runs in $\tilde O(N^{3/2})$, matching AGM.

**Cross-model wrinkle.** If $E$ is actually a 2-hop *reachability* atom (graph transitive closure) rather than a materialized edge set, AGM no longer bounds the output directly, the fixpoint can inflate $|E|$ to $\Theta(N^2)$ edges, and interleaving that expansion lazily inside the WCO join with a matching bound is exactly the open part of section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
