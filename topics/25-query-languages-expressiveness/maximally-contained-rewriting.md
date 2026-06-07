---
id: 25-query-languages-expressiveness/maximally-contained-rewriting
title: "Maximally Contained Rewritings Using Views"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Maximally Contained Rewritings Using Views

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/maximally-contained-rewriting` · **Status:** partially-solved

## 1. Problem Statement
Under the **open-world assumption (OWA)** — views are sound but possibly incomplete — an *equivalent* rewriting rarely exists. Instead we seek a **maximally contained rewriting (MCR)** of query $Q$ using views $\mathcal{V}$ in a target language $\mathcal{L}'$: a query $R \in \mathcal{L}'$ such that (i) $R$ uses only the view symbols, (ii) $R \sqsubseteq Q$ for all databases consistent with the views, and (iii) $R$ is maximal — every other contained $\mathcal{L}'$-rewriting is contained in $R$. The MCR computes exactly the **certain answers** when $\mathcal{L}'$ is expressive enough.

Variants: (a) target $\mathcal{L}' =$ UCQ (classical), Datalog (recursive), or FO; (b) presence of **integrity constraints** (functional dependencies, TGDs, description-logic TBoxes); (c) **bag** vs set semantics; (d) cost-based selection among contained rewritings. The decision side asks whether the MCR is finite/expressible; the optimization side asks for the best executable plan.

## 2. Mathematical Foundations
A rewriting $R$ is **contained** in $Q$ iff its expansion (replacing view atoms by their definitions) is contained in $Q$ — checked by **homomorphism** for CQs. The MCR equals the union of all **maximally contained CQ rewritings**, and over OWA it computes **certain answers**: $\mathsf{certain}_Q(\mathcal{V}(D)) = \bigcap \{ Q(D') : \mathcal{V}(D') \supseteq \mathcal{V}(D)\}$.

For **recursive** targets, when views are recursive or constraints induce recursion (e.g., DL-Lite, Datalog$^\pm$), the MCR is a **Datalog program** even when no finite UCQ MCR exists. The **inverse-rules** algorithm constructs logic rules $V_i \to \exists\,\text{body}$ and reasons by the **chase**; **MiniCon** prunes by tracking which query atoms a view can cover (MiniCon Descriptions). Under LAV/GLAV mappings, certain-answer computation reduces to evaluating the rewriting over the canonical (chased) instance.

## 3. State of the Art (SOTA)
- **Bucket** (Levy et al., 1996), **inverse-rules** (Duschka–Genesereth, 1997), and **MiniCon** (Pottinger–Halevy, 2001) are the canonical UCQ-MCR algorithms; MiniCon is the practical baseline.
- **Recursive MCR:** inverse-rules yields a Datalog MCR for CQ views with recursion/constraints; for **DL-Lite** ontologies, **PerfectRef** and the **Combined Approach** give FO/UCQ rewritings (Calvanese et al., Lutz et al.).
- **Datalog$^\pm$ / existential rules:** MCR via **piece-unification** and the chase (Gottlob, Leone, Pieris, König–Leclère–Mugnier–Thomazo).
- Systems: ontology-based data access (OBDA) engines such as **Ontop** compile MCRs to SQL.

## 4. Upper Bound
- UCQ-MCR for CQ views/CQ query: computable; the MCR is a UCQ of size singly-exponential in the query, each disjunct of size bounded by $|Q|$. MiniCon achieves this with strong pruning.
- With **DL-Lite** TBoxes: FO-rewritability holds; PerfectRef terminates with a UCQ rewriting (worst-case exponential).
- With **guarded/sticky/linear** existential rules: the chase is finite-controllable or the MCR is a (possibly non-UCQ) Datalog program; FO-rewritability holds for first-order-rewritable classes.

## 5. Lower Bound
- Even for CQ views, the UCQ-MCR can be **exponential** in $|Q|$ (number of disjuncts), and deciding membership of a tuple in certain answers is **coNP-hard in data complexity** for CQ views under OWA (Abiteboul–Duschka 1998).
- For Datalog views or full TGDs, **certain answering is undecidable**; FO-rewritability fails and even a finite Datalog MCR may not exist.
- DL with role inclusions / $\mathcal{ELHI}$: certain answering is **PTIME-complete** in data complexity (no FO rewriting), beyond DL-Lite.

## 6. The Gap
For UCQ views, the problem is largely **solved** (algorithms + matching bounds). The open frontier is the **recursive/constrained** regime: characterizing exactly when a **finite Datalog MCR** exists, when it collapses to FO, and tight data/combined complexity for rich existential-rule classes. Bag-semantics MCRs and **cost-optimal** rewriting selection (which contained rewriting to run) remain underexplored, as does MCR under **bounded incompleteness** (partially-closed worlds).

## 7. Current Research (as of June 2026)
OBDA and **knowledge-graph** querying drive renewed interest: MCR over property-graph/RDF views, MCR with **SHACL/ontology** constraints, and rewriting to scalable SQL/Spark. Groups: Calvanese, Lenzerini, Xiao (Ontop); Mugnier, Leclère, Thomazo (existential rules); Pieris, Gottlob (Datalog$^\pm$); Konstantinidis, Ambite (MCR systems). *(frontier — verify)* Recent work studies MCR under **partially-closed** (mixed OWA/CWA) databases and "**bounded-rewriting**" for graph queries, plus learned/cost-aware rewriting selection inside modern optimizers.

## 8. Future Work
- Sharp characterization of finite Datalog-MCR existence under existential rules.
- MCR for **CRPQ/UCRPQ** graph views and GQL constraints.
- Cost-based and adaptive MCR integrated with cardinality estimation.
- MCR under partially-closed worlds and access-pattern (binding-pattern) limitations.

## 9. Key References
- **[Foundational]** A. Levy, A. Mendelzon, Y. Sagiv, D. Srivastava. *Answering queries using views.* PODS, 1995. — [DOI](https://doi.org/10.1145/212433.220198)
- **[Foundational]** O. Duschka, M. Genesereth. *Answering recursive queries using views.* PODS, 1997. — [DOI](https://doi.org/10.1145/263661.263674)
- **[SOTA]** R. Pottinger, A. Halevy. *MiniCon: A scalable algorithm for answering queries using views.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100048)
- **[Foundational]** S. Abiteboul, O. Duschka. *Complexity of answering queries using materialized views.* PODS, 1998. — [DOI](https://doi.org/10.1145/275487.275516)
- **[SOTA]** D. Calvanese, G. De Giacomo, D. Lembo, M. Lenzerini, R. Rosati. *Tractable reasoning and efficient query answering in description logics: The DL-Lite family.* J. Automated Reasoning, 2007. — [DOI](https://doi.org/10.1007/s10817-007-9078-x)
- **[Survey]** A. Halevy. *Answering queries using views: A survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)

## 10. Worked Example

Query (find advisor–department pairs reachable via co-authorship):
$$Q(a,d) \leftarrow \text{Advises}(a,s),\ \text{Works}(s,d).$$
Two sound-but-incomplete views:
$$V_1(x,y)\leftarrow \text{Advises}(x,y), \qquad V_2(u,w)\leftarrow \text{Works}(u,w).$$

**MiniCon Descriptions (MCDs):** $V_1$ can cover the atom $\text{Advises}(a,s)$, mapping head var $x\mapsto a$ and exposing $s$ (a join var) through $y$; $V_2$ can cover $\text{Works}(s,d)$, mapping $u\mapsto s,\ w\mapsto d$. Neither view alone covers a query atom containing the join variable $s$ in a way the other cannot complete, so MiniCon combines the two MCDs. The maximally contained rewriting is
$$R(a,d)\leftarrow V_1(a,s),\ V_2(s,d).$$

**Why "maximally contained," not "equivalent":** under OWA the views may be incomplete, so $R$ returns only the *certain* answers — pairs guaranteed by what the views expose. If a real advising edge $(a',s')$ exists but is absent from $V_1$, $R$ misses $(a',d')$; that is sound (every tuple $R$ returns is a true $Q$-answer) but not complete. No CQ rewriting over $\{V_1,V_2\}$ can do better, which is exactly the maximality MiniCon guarantees. Adding a third view $V_3(x,w)\leftarrow\text{Advises}(x,s),\text{Works}(s,w)$ would yield a *second*, redundant MCD, and the MCR becomes the union $R \cup \{R'(a,d)\leftarrow V_3(a,d)\}$.

---
*Part of the [DBMS Research catalog](../../README.md).*
