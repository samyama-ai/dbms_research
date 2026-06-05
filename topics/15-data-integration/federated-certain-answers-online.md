# Federated Query Certain Answers Online

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/federated-certain-answers-online` · **Status:** open

## 1. Problem Statement

In a federated/mediator setting, a query $q$ is posed over a global schema while data lives in autonomous remote sources reachable only through **restricted access interfaces**. Each source relation exposes **access patterns** (binding patterns): some attributes must be *bound* (given as input) before the source returns matching tuples — e.g., a web API that requires a `zip` to return `stores(zip, name, …)`. Sources also impose **latency, rate limits, and partial availability**.

The problem: **return the *certain answers* of $q$** — tuples guaranteed true in *every* consistent global database — **online**, i.e., streaming results as sources respond, under access-pattern and latency constraints, rather than returning a best-effort/approximate answer.

Variants to distinguish:

- **Decision (membership):** is tuple $\bar{t}$ a certain answer reachable under the access patterns?
- **Feasibility (executability):** does an **executable plan** exist that respects all binding patterns and computes $\mathrm{certain}(q)$ (or a maximal sound subset)?
- **Optimization:** among executable plans, minimize total latency / number of source calls / makespan.
- **Online/anytime:** maximize the (monotone) set of *certified* certain answers emitted by deadline $\Delta$, ideally with a soundness guarantee at every prefix.

The tension: certain-answer semantics (a $\forall$-over-models, hence often **coNP**-flavored notion) collides with access restrictions that make some answers **unreachable** at all, and with an online requirement that demands *sound* incremental output.

## 2. Mathematical Foundations

Sources expose relations with **binding patterns** $R^{\text{bf…}}$ (b = must-bind, f = free). A conjunctive query is **executable** iff its atoms admit an ordering where every bound position is supplied by a prior atom or a constant — captured by Rajaraman–Sagiv–Ullman's *answerable/executable* rewriting and the notion of the **reachable portion** of a source (the recursive closure of values you can feed back, a **Datalog** least-fixpoint).

Two semantic anchors:

1. **Certain answers under incomplete information.** With OWA, $\mathrm{certain}(q,\mathcal{D}) = \bigcap_{D \models \Sigma} q(D)$. For CQs over GLAV this is computable from a universal solution, but adding access limitations and source incompleteness shifts the model toward **naive tables / conditional tables** (Imieliński–Lipski) and the **closed-world vs open-world** distinction of Libkin.

2. **Access-pattern reachability.** The set of obtainable tuples is the fixpoint of a Datalog program over the binding graph; *maximally contained* executable plans (Duschka–Genesereth, Florescu–Levy–Manolescu–Suciu) give the best *recursive* rewriting under LAV. Soundness of an online prefix requires each emitted tuple be **certified** — provably in $q(D)$ for all $D$ — i.e., a *monotone* lower bound that never retracts.

The online/latency layer is naturally modeled as **competitive analysis** (ratio to an offline optimum that knows all source latencies) or as **multi-armed bandit / scheduling** over source calls. CAP/FLP-style impossibilities bound what is certifiable when a source is unreachable.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Answering queries over sources with binding patterns: **Rajaraman–Sagiv–Ullman** (PODS 1995), **Duschka–Genesereth** (recursive plans), **Florescu–Levy–Manolescu–Suciu** (binding-pattern query optimization, VLDB 1999). **Deutsch–Ludäscher–Nash** (*Rewriting queries using views with access patterns*, ICDT 2007 / TCS) gave decidability and minimal executable reformulations. **Benedikt–Leblay–ten Cate–Tsamoura**, *Generating Plans from Proofs* (the **PDQ** framework, 2016 book) unifies access patterns, integrity constraints, and cost into a proof-theoretic plan search.
- **Systems-SOTA.** **PDQ** (Oxford) generates and costs access-respecting plans. Mediator/wrapper systems — **Garlic**, **TSIMMIS**, **Information Manifold**, and modern federation engines (**Trino/Presto**, **Teiid**, **Ontop** for OBDA, **Apache Calcite** adapters) — execute federated plans but generally deliver **best-effort** answers, not certified certain answers. SPARQL federation (**SERVICE**, FedX, Comunica) faces the same gap.

## 4. Upper Bound

- **CQ over LAV with access patterns, no constraints:** a **maximally-contained recursive (Datalog) plan** exists and is computable; executing it yields the **reachable certain answers** — data complexity **PTime** (fixpoint), combined complexity up to **EXPTIME** for the rewriting. Holds in the **RAM/Datalog evaluation** model.
- **With integrity constraints (TGDs/EGDs):** PDQ-style proof search yields an executable plan when one exists; decidability requires a **terminating chase** (e.g., weakly-acyclic/guarded), giving decidable but high (EXPTIME/2EXPTIME-combined) bounds.
- **Online competitive ratio:** no nontrivial constant-competitive algorithm is known for general source-latency adversaries; greedy "fire all currently-executable calls" is the practical upper bound. Anytime emission of a *monotone certified* subset is achievable but without a proven ratio.

## 5. Lower Bound

- **Undecidability / non-finite-controllability:** with **binding patterns + recursion or with target TGDs**, deciding whether a *finite* executable plan computes the certain answers is **undecidable** in general (reduces to chase/Datalog containment); the reachable certain-answer set may require **unbounded recursion** (Li–Chang; Nash–Ludäscher).
- **coNP-hardness of certainty:** computing certain answers becomes **coNP-hard in data** as soon as queries use inequalities/negation or sources are mutually inconsistent (Abiteboul–Duschka), independent of access limits.
- **Impossibility under failure:** if a needed source is **unreachable/slow**, no algorithm can *certify* the affected certain answers within the deadline — an **FLP/CAP-style impossibility** in the asynchronous, partial-failure model: you cannot have certified-completeness, availability, and bounded latency simultaneously when a binding-required source is partitioned.
- **Communication-complexity** lower bounds limit how few source round-trips can verify a join's certain answers across sources.

## 6. The Gap

This is **genuinely open**. The static-plan theory (PDQ, access-pattern rewriting) is mature, but the **online, latency-bounded, *certified* certain-answer** problem has no algorithm with guarantees: (i) there is no competitive-ratio result for scheduling access-restricted source calls under adversarial latency; (ii) reconciling **monotone certified output** (never retract) with the **coNP/$\forall$-models** nature of certainty under inconsistency is unsolved; (iii) the executable-plan-existence question is undecidable with recursion/constraints, so even the offline target can be ill-defined. Closing the gap means (a) carving decidable fragments where certified online certain answering admits a competitive algorithm, and (b) matching impossibility results (FLP/CAP-style) delimiting what no online algorithm can certify under partition.

## 7. Current Research (as of June 2026)

Active directions: extending **PDQ** with cost/latency-aware and **anytime** plan execution (Benedikt, ten Cate, Tsamoura); **certain answers over inconsistent federations** via consistent query answering meeting access limits (Bertossi, Bienvenu–Bourgaux). *(frontier — verify)* 2024–2025 work targets **streaming/anytime certain answers** with soundness-at-every-prefix and **bandit-style source scheduling** under rate limits, and revisits **SPARQL federation** for *complete* (not best-effort) results with provenance certificates. *(frontier — verify)* OBDA federation (Ontop, Calvanese/Xiao group) is pushing access-pattern-aware rewriting over live SQL/SPARQL endpoints. Groups: Benedikt/ten Cate (PDQ), Calvanese/Xiao (OBDA), Bienvenu–Bourgaux (inconsistency-tolerant), Libkin/Hernich (semantics of certainty).

## 8. Future Work

- A **competitive-ratio** theory for online, access-restricted source scheduling under latency adversaries.
- **Certified anytime** algorithms: monotone sound prefixes with quantified completeness over time.
- Sharp **CAP/FLP-style impossibility** boundaries for certified federated certainty under partition.
- Unifying **consistent query answering** (inconsistent sources) with **access patterns** and **provenance** certificates.
- Decidable fragments (guarded/linear constraints + finite binding closure) with practical optimal plans.

## 9. Key References

- **[Foundational]** A. Rajaraman, Y. Sagiv, J. D. Ullman. *Answering Queries Using Templates with Binding Patterns.* PODS, 1995. — [DOI](https://doi.org/10.1145/212433.220198)
- **[Foundational]** O. Duschka, M. Genesereth, A. Levy. *Recursive Query Plans for Data Integration.* J. Logic Programming, 2000. — [DOI](https://doi.org/10.1016/S0743-1066(99)00025-4)
- **[Foundational]** M. Lenzerini. *Data Integration: A Theoretical Perspective.* PODS, 2002. — [DOI](https://doi.org/10.1145/543613.543644)
- **[SOTA]** A. Deutsch, B. Ludäscher, A. Nash. *Rewriting Queries Using Views with Access Patterns under Integrity Constraints.* Theoretical Computer Science, 2007. — [DOI](https://doi.org/10.1016/j.tcs.2006.11.008)
- **[SOTA]** M. Benedikt, J. Leblay, B. ten Cate, E. Tsamoura. *Generating Plans from Proofs: The Interpolation-based Approach to Query Reformulation (PDQ).* Morgan & Claypool, 2016. — [DOI](https://doi.org/10.2200/S00703ED1V01Y201602DTM043)
- **[Survey]** L. Bertossi. *Database Repairing and Consistent Query Answering.* Morgan & Claypool (Synthesis Lectures), 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)

## 10. Worked Example

Two sources with binding patterns:
- $\text{Store}^{\text{bf}}(\underline{zip}, name)$ — must bind $zip$, returns store names in that zip.
- $\text{Nearby}^{\text{bf}}(\underline{zip}, zip')$ — must bind $zip$, returns adjacent zips.

Query: *names of all stores reachable from zip 10001.* As a CQ:
$$q(name) \leftarrow \text{Reach}(z),\ \text{Store}(z,name),\quad \text{Reach}(10001),\ \text{Reach}(z')\!\leftarrow\!\text{Reach}(z),\text{Nearby}(z,z').$$

**Executability check.** Every bound position is fed by a constant or a prior atom: $10001$ seeds $\text{Reach}$; each $\text{Nearby}$ call binds its $zip$ from a known $\text{Reach}$ value; each $\text{Store}$ call binds $zip$ likewise. So the plan is executable — it is a **Datalog least-fixpoint** over the binding graph.

**Online/reachability trace.** Call $\text{Nearby}(10001)\to\{10002\}$; call $\text{Nearby}(10002)\to\{10001,10003\}$ (10001 already seen); call $\text{Nearby}(10003)\to\{\}$. Fixpoint reached: $\text{Reach}=\{10001,10002,10003\}$. Emitting $\text{Store}$ results as each call returns gives a **monotone certified prefix**. But if the $\text{Nearby}(10002)$ API is rate-limited/partitioned, no algorithm can certify whether $10003$'s stores belong to the answer before the deadline — the FLP/CAP-style impossibility of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
