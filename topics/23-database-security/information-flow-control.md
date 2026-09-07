---
id: 23-database-security/information-flow-control
title: "Information Flow Control in DBMS"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Information Flow Control in DBMS

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/information-flow-control` · **Status:** open

## 1. Problem Statement

Access control gates *who may touch* a relation; **Information Flow Control (IFC)** governs *where data may end up* — it tracks labeled data **end-to-end** through query operators, views, triggers, stored procedures, and the surrounding application, and enforces a *non-interference* / declassification policy so that high-sensitivity values do not flow (directly or via implicit channels) to low-sensitivity sinks except through explicitly authorized **declassifiers**. The open problem is **sound, precise, and practical** IFC across the whole DBMS data path — including set-oriented relational operators, transitive flows through triggers/stored logic, and *implicit* flows through control dependencies (e.g., a `WHERE` predicate or a conditional in a procedure that leaks a secret via which rows are returned).

- **Decision variant:** given a query/procedure, a labeling, and a policy lattice, does every execution satisfy non-interference (no illegal flow)?
- **Optimization variant:** maximize accepted (utility-preserving) queries / minimize over-tainting (label creep) while remaining sound.
- **Quantitative variant:** if some leakage is permitted, *bound* it — min-entropy / channel-capacity leakage at most $\ell$ bits.

## 2. Mathematical Foundations

Labels form a **security lattice** $(\mathcal{L}, \sqsubseteq, \sqcup, \sqcap)$ (Denning's lattice model). The gold standard is **non-interference**: for programs $P$ with high/low inputs, $\forall\, s_1,s_2$ agreeing on *low* inputs, $P(s_1)$ and $P(s_2)$ agree on *low* outputs — i.e., high inputs cannot affect low outputs. Formally, with low-equivalence $\approx_L$:

$$ s_1 \approx_L s_2 \implies \llbracket P\rrbracket(s_1) \approx_L \llbracket P\rrbracket(s_2). $$

For databases this must be extended to **set-oriented semantics**: a query is a function over relations, and flows arise both *explicitly* (a high column projected to a low view) and *implicitly* (selection on a high predicate makes the *cardinality/identity* of the output depend on high data). **Declassification** relaxes strict non-interference along controlled dimensions (Sabelfeld–Sands' *what/who/where/when* taxonomy). Quantitative IFC replaces the boolean guarantee with a leakage measure — **min-entropy leakage** $\mathcal{L}(P)=\log_2 \frac{V(\text{posterior})}{V(\text{prior})}$ or channel capacity — bounding how many bits a low observer learns. Enforcement uses **dependency/provenance** analysis: provenance semirings (Green–Karvounarakis–Tannen) and the *how/why/where*-provenance of an output tuple precisely capture which inputs influenced it, giving a principled taint-propagation calculus for relational operators.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Denning's lattice model and the **Decentralized Label Model** (Myers–Liskov) underpin language-level IFC (**Jif/JFlow**). Provenance semirings (Green et al., PODS 2007) give exact data-dependency tracking for positive relational algebra. **SeaView / multilevel-secure (MLS) databases** historically enforced lattice flows with polyinstantiation. Quantitative IFC (Smith; Köpf–Basin) bounds leakage for programs and could lift to queries.
- **Systems-SOTA:** **IFDB** (Schultz–Liskov, EuroSys 2013) adds decentralized IFC to a relational DBMS, propagating labels through queries and the application via *Query by Label*. **Resin / Nemesis**-style web-app taint tracking catches DB-mediated flows. SQL row/column security + Oracle Label Security implement *static* lattice labels but do not track transitive/implicit flows through application logic. **SELinks / Fabric / Jeeves** explore policy-agnostic programming over persistent data.

## 4. Upper Bound

For **positive relational algebra** (SPJU), provenance-based taint propagation is exact and computable in time polynomial in the query plan and data size (semiring evaluation alongside normal execution), giving *sound and precise* explicit-flow tracking in the RAM model. Type-system enforcement (Jif-style) is **sound by construction** and runs at compile time, conservatively rejecting unsafe programs; runtime label propagation (IFDB) adds per-tuple/per-operator label overhead that is constant-factor on top of query execution. Quantitative leakage for restricted (deterministic, loop-bounded) query fragments is computable / boundable via model counting.

## 5. Lower Bound

**Precise** IFC is fundamentally limited: deciding non-interference for general programs (with the procedural logic of triggers/stored procedures) is **undecidable** (reduces to program equivalence / halting); hence any sound, terminating analysis must be *conservative* (over-taint, causing label creep). Even for restricted languages, *precise* implicit-flow analysis with full path-sensitivity is intractable. **Quantitative** leakage estimation is **#P-hard** in general (it reduces to model counting / $\\#\mathrm{SAT}$). Covert and *termination/timing channels* are not closed by standard non-interference and require stronger (timing-sensitive) models — and fully closing termination channels conflicts with completeness (you cannot accept all safe terminating programs while rejecting all leaky ones). These are information-theoretic and computability lower bounds, not merely engineering limits.

## 6. The Gap

Explicit, set-oriented flows over positive relational algebra are essentially **handled** (provenance-exact). The genuinely **open** gap is *end-to-end*: (1) sound tracking through **stored procedures/triggers with control flow** without crippling over-tainting; (2) **implicit flows** via cardinality, ordering, and predicate-dependent results; (3) practical **quantitative bounds** ($\le \ell$ bits) for real query workloads despite #P-hardness; (4) closing **declassification** policies that compose safely across the DB/application boundary. Closing it requires analyses that are sound *and* precise enough to avoid label creep, plus accepted leakage-bound certificates for declassifiers.

## 7. Current Research (as of June 2026)

Active directions: **provenance-driven IFC** that unifies why/how-provenance with declassification policies; **policy-agnostic / faceted execution** (Jeeves, multi-execution) ported to query engines so one query yields per-clearance views without manual filtering; **quantitative IFC for SQL** using approximate model counting to certify leakage budgets; integrating IFC with **differential privacy** as a principled declassifier (DP bounds the leakage of an aggregate sink). *(frontier — verify)* Recent work explores IFC for **data pipelines / ML feature stores** and TEE-backed enforcement so labels survive across enclave boundaries. Groups: MIT PMG (Liskov lineage), Chalmers (Sabelfeld/Sands), Penn (Tannen/provenance), and language-based-security teams.

## 8. Future Work

- Sound + precise IFC through **triggers and stored procedures** with bounded, well-characterized over-tainting.
- Practical **quantitative leakage budgets** for query workloads (scalable approximate model counting).
- Compositional **declassification** that is verified across the DB/application/ML-pipeline boundary.
- Timing/cardinality **side-channel-aware** non-interference for query operators (links to side-channel-free execution).

## 9. Key References

- **[Foundational]** Denning, D.E. *A Lattice Model of Secure Information Flow.* Communications of the ACM, 1976. — [DOI](https://doi.org/10.1145/360051.360056)
- **[Foundational]** Myers, A.C., Liskov, B. *A Decentralized Model for Information Flow Control.* SOSP, 1997. — [DOI](https://doi.org/10.1145/268998.266669)
- **[Foundational]** Goguen, J.A., Meseguer, J. *Security Policies and Security Models.* IEEE S&P, 1982. — [DOI](https://doi.org/10.1109/SP.1982.10014)
- **[SOTA]** Schultz, D., Liskov, B. *IFDB: Decentralized Information Flow Control for Databases.* EuroSys, 2013. — [DBLP](https://dblp.org/rec/conf/eurosys/SchultzL13.html)
- **[SOTA]** Green, T.J., Karvounarakis, G., Tannen, V. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Survey]** Sabelfeld, A., Myers, A.C. *Language-Based Information-Flow Security.* IEEE JSAC, 2003. — [DOI](https://doi.org/10.1109/JSAC.2002.806121)
- **[Survey]** Sabelfeld, A., Sands, D. *Declassification: Dimensions and Principles.* Journal of Computer Security, 2009. — [DOI](https://doi.org/10.3233/JCS-2009-0352)

## 10. Worked Example

Lattice $\{L \sqsubseteq H\}$. Relation $\mathsf{Acct}(\text{id}, \text{balance}^{H})$ — `balance` is High, `id` is Low. A user cleared only to $L$ runs:

```sql
SELECT id FROM Acct WHERE balance > 1000000;
```

No High *value* appears in the output (we project only `id`), so an explicit-flow checker that tracks projected columns sees nothing leak. Yet this is a textbook **implicit flow**: *which* ids appear depends entirely on the High `balance` predicate. Provenance makes it precise — each output tuple's why-provenance includes its `balance` cell, so the result's very *membership* carries a High dependency. Concretely, over two databases $D_1, D_2$ that are low-equivalent (same `id`s) but differ in one balance crossing the \$1M threshold, the query returns different row sets — violating non-interference $\llbracket P\rrbracket(D_1)\approx_L\llbracket P\rrbracket(D_2)$.

Quantitatively, if an attacker uses such a predicate as a binary probe, each query reveals $\le 1$ bit; $k$ adaptive threshold queries binary-search a balance to $\le k$ bits of min-entropy leakage — exactly the budget a declassifier (or DP noise on the count) must bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
