# Provenance across multi-model transformations

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/multimodel-provenance` · **Status:** open

## 1. Problem Statement

Multi-model queries **shred** documents into relations, **nest** relations back into documents, traverse **graph** edges, and aggregate — crossing data-model boundaries within a single pipeline. The task is to track, for every output element $o$:

- **why-provenance:** which input data items "witness" $o$ (the source sets justifying its existence);
- **how-provenance:** the algebraic *derivation* of $o$ (which combination of joins/unions/projections produced it, with multiplicities) — the provenance **semiring** polynomial;
- **where-provenance:** from which specific input *location* (document, path, field, edge) each value in $o$ was copied.

The challenge unique to multi-model: provenance must be **defined and composed across heterogeneous operators** — unnest (document→relation), nest/group (relation→document), graph path traversal (transitive closure), and type coercion — for which a single semiring/annotation framework does not yet uniformly account.

Variants:
- **Construction:** compute the provenance annotation of every output.
- **Decision:** is input item $x$ in the why-provenance of output $o$? (membership)
- **Counting / aggregation:** how-provenance over **aggregate** and **recursive** queries (semiring vs. semimodule semantics).
- **Storage/size:** maintain provenance within a polynomial size/overhead bound.

## 2. Mathematical Foundations

- **Provenance semirings (Green–Karvounarakis–Tannen, PODS 2007):** annotate tuples with elements of a commutative semiring $(K, +, \cdot, 0, 1)$; positive relational algebra propagates annotations homomorphically. The free semiring $\mathbb{N}[X]$ (provenance polynomials) is the *most informative*; specializations recover lineage, why-, trust, and probability. **where-provenance** is captured separately (Buneman–Khanna–Tan, ICDT 2001) as it is not semiring-homomorphic.
- **Recursion / graph atoms:** Datalog and transitive closure need provenance over $\omega$-continuous semirings / formal power series and least-fixpoint semantics (Green et al.; provenance for Datalog), giving possibly infinite polynomials that must be represented as systems of equations (provenance *circuits*).
- **Aggregation:** semirings are insufficient; **provenance semimodules** / $K$-relations with aggregation (Amsterdamer–Deutch–Tannen, PODS 2011) handle SUM/COUNT over annotated data.
- **Nesting/unnest:** requires provenance for the **nested relational calculus**; provenance must commute with `nest`/`unnest`, an area only partially formalized.
- **Provenance circuits / semiring of polynomials:** compact DAG representation; size and evaluation relate to arithmetic-circuit complexity and to probabilistic-database $\\#$P-hardness.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** the semiring framework + its extensions to aggregation (semimodules), recursion (continuous semirings/circuits), and where-provenance are the canonical machinery. M-semirings and provenance for difference/negation (Geerts–Poggi; Amsterdamer et al.) extend to full RA.
- **Systems-SOTA:** **ProvSQL** (Senellart et al., VLDB 2018) — provenance + probabilistic computation as a PostgreSQL extension; **Perm/GProM** (Glavic et al.) — provenance via query rewriting across SQL engines; **Smoke** (Psallidas–Wu, SIGMOD 2018) — fast lineage capture. Spark/Titian and Trio (probabilistic). For documents/graph: provenance in Cypher/SPARQL prototypes and JSON lineage in dataflow systems, but **no production multi-model engine offers unified why/how/where across model boundaries**.

## 4. Upper Bound

For **positive relational algebra (+ projection, join, union)**, how-provenance polynomials over $\mathbb{N}[X]$ are computed with **constant overhead per operator** (one semiring op per tuple op), giving total provenance in time $O(|\text{evaluation}|)$ and size linear in the derivation — optimal up to the polynomial's representation. With recursion, provenance circuits of size polynomial in the number of derivation steps suffice (least fixpoint over an $\omega$-continuous semiring). where-provenance is computable in the same pass via location annotations. So for the *positive, finite* multi-model fragment, near-linear-overhead capture is achievable; nest/unnest and aggregation are handled by the semimodule extension at a (still polynomial) overhead.

## 5. Lower Bound

- **Negation/difference:** there is **no** commutative semiring that correctly captures how-provenance for relational *difference* in general; this is an algebraic impossibility (motivating m-semirings, which only partially resolve it).
- **Probabilistic evaluation is #P-hard:** computing the probability of a query answer from its provenance (read-once vs. general) is **#P-hard** for non-hierarchical conjunctive queries (Dalvi–Suciu dichotomy); equivalently, evaluating the provenance polynomial under a probabilistic semiring is intractable in general.
- **Size blow-up:** how-provenance polynomials for queries with self-joins/recursion can be exponential-size if expanded (must stay as circuits); minimizing a provenance circuit is as hard as Boolean-circuit minimization.
- **where-provenance non-functoriality:** where-provenance is not preserved by query equivalence — provably depends on the *syntactic* query, not just its result (Buneman et al.), so no semantics-only algorithm captures it uniformly.

## 6. The Gap

**Open.** The semiring framework cleanly closes the positive RA case, but multi-model pipelines need **uniform** provenance across (a) **nest/unnest** boundaries, (b) **graph recursion**, (c) **aggregation**, and (d) **type coercion/shredding** — each handled by a *separate* extension (semimodules, circuits, m-semirings) with no single account that composes them. Open problems: a provenance algebra closed under all multi-model operators; tractable where-provenance across shredding; bounded-size provenance for recursive cross-model queries; and reconciling negation. Closing it needs a unifying algebraic structure plus matching tractability/intractability dichotomies.

## 7. Current Research (as of June 2026)

- Extending ProvSQL/GProM-style capture to JSON-shredding and graph traversal in one engine *(frontier — verify)*.
- Provenance for nested-relational and document transformations with where-provenance preserved *(frontier — verify)*.
- Provenance circuits as the substrate for explanation/debugging of multi-model ETL (why-not provenance, responsibility).
- Groups: UPenn (Tannen, Davidson), Inria/IPP (Senellart — ProvSQL), IIT (Glavic — GProM), Tel Aviv (Deutch), Edinburgh (Buneman lineage).

## 8. Future Work

- A single provenance semiring/semimodule closed under unnest, nest, recursion, aggregation, and coercion.
- Tractable, compact provenance for recursive graph+document queries.
- Where-provenance robust to model-crossing shredding.
- Provenance-aware optimization (rewrite without losing lineage) across polystores.

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Buneman, Khanna, Tan. *Why and Where: A Characterization of Data Provenance.* ICDT, 2001. — [DOI](https://doi.org/10.1007/3-540-44503-X_20)
- **[Foundational]** Cheney, Chiticariu, Tan. *Provenance in Databases: Why, How, and Where.* FnT Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)
- **[SOTA]** Amsterdamer, Deutch, Tannen. *Provenance for Aggregate Queries.* PODS, 2011. — [DOI](https://doi.org/10.1145/1989284.1989302)
- **[SOTA]** Senellart, Jachiet, Maniu, Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[SOTA]** Arab, Feng, Glavic, et al. *GProM — A Swiss Army Knife for Your Provenance Needs.* IEEE Data Eng. Bulletin, 2018. — [DBLP](https://dblp.org/rec/journals/debu/ArabFGLNZ18.html)
- **[Foundational]** Dalvi, Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* JACM, 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)

## 10. Worked Example

Relation $R$ with provenance-annotated tuples (free semiring $\mathbb{N}[X]$):

| tuple | annotation |
|---|---|
| (Ann, HR) | $x_1$ |
| (Bob, HR) | $x_2$ |
| (Carol, IT)| $x_3$ |

**Query** $Q$: $\pi_{dept}(R)$ — list departments.

Projection *adds* annotations of tuples that collapse to the same output. Output:

- (HR): $x_1 + x_2$
- (IT): $x_3$

The **how-provenance** of (HR) is the polynomial $x_1 + x_2$: it says HR is witnessed by *either* the Ann tuple *or* the Bob tuple (the $+$ encodes alternative use). Its **why-provenance** is $\{x_1, x_2\}$ (the variables appearing).

Now self-join $Q' = \pi_{\emptyset}(R \bowtie_{dept} R)$ to ask "does some department have $\ge 1$ pair?" The HR group contributes $(x_1+x_2)\cdot(x_1+x_2) = x_1^2 + 2x_1x_2 + x_2^2$. The exponent on $x_1^2$ and coefficient $2$ record *multiplicity* — Ann paired with herself, and Ann–Bob counted twice. A plain set-lineage $\{x_1,x_2\}$ loses this; the **semiring polynomial** keeps it, which is precisely why $\mathbb{N}[X]$ is the most informative annotation (Section 2). Crossing into a graph `nest` step is where, per Section 6, no single semiring yet composes cleanly.

---
*Part of the [DBMS Research catalog](../../README.md).*
