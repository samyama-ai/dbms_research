# Access Control for Provenance Queries

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/provenance-access-control` · **Status:** open

## 1. Problem Statement

**Data provenance** records *why*, *how*, and *where* a result tuple was derived — its lineage through the operators of a query or workflow. Provenance is essential for debugging, reproducibility, trust, compliance, and explanation. But provenance is *meta-data about the base data*, and it can **leak the very tuples that the base-data access policy forbids**:

- A user authorized to see an *aggregate* (e.g., average salary) but not individual salaries could, via *why-provenance*, recover the contributing tuples.
- *Where-provenance* points at exact source cells; *how-provenance* (provenance polynomials) encodes which combinations of source tuples produced a result — revealing existence, multiplicity, and structure of hidden data.

The problem:

> Design access-control policies and mechanisms that release lineage / explanations **consistent with** the base-data policy — i.e., a user learns nothing from provenance that the base policy denies — while still being **useful** (returning as much true, non-leaking lineage as possible).

Variants: **(Decision)** does releasing provenance $P$ to user $u$ violate base policy $\Pi$? **(Sanitization/Optimization)** compute the maximal sub-provenance releasable without violation. **(Counting/Quantitative)** bound the information about hidden tuples leaked by a provenance answer. There is an inherent **availability vs. confidentiality** tension: an over-redacted explanation is useless; an honest one leaks.

## 2. Mathematical Foundations

The semiring framework (**Green, Karvounarakis, Tannen, PODS 2007**) models provenance as annotations from a commutative semiring $(K,+,\cdot,0,1)$: union/projection use $+$, join uses $\cdot$. The **provenance polynomial** semiring $\mathbb{N}[X]$ is the most informative; specializations give why-provenance ($\mathrm{Why}(\mathcal{P}(X))$), lineage (the set of contributing tuples), and trust/security semirings. A result tuple $t$ carries polynomial $p_t(x_1,\dots,x_n)$ over source-tuple variables $x_i$.

Access control over provenance is an *information-flow* problem on these annotations. Let $\Pi$ partition source tuples into *visible* $V$ and *hidden* $H$. Releasing $p_t$ is *safe* for user $u$ iff the released annotation is **independent of** $\{x_i : i\in H\}$ in the sense that the user's posterior over hidden tuples is unchanged:
$$\forall\,\text{hidden valuations } h,h':\quad \textit{view}_u(p_t)\big|_h = \textit{view}_u(p_t)\big|_{h'}.$$
This is **noninterference** on annotations — a 2-safety hyperproperty. Quantitatively, leakage is $I(H; \textit{view}_u)$, and a $\varepsilon$-safe release bounds it. Provenance redaction = computing a semiring homomorphism $\phi$ collapsing hidden variables (e.g., mapping them to an opaque constant) such that $\phi(p_t)$ is both informative and non-leaking — closely related to **provenance abstraction** and **m-semiring** (difference) subtleties.

## 3. State of the Art (SOTA)

- **Foundational:** the provenance semiring framework (Green–Karvounarakis–Tannen 2007) unified why/how/where (Buneman–Khanna–Tan 2001) provenance and underlies all reasoning. Cheney–Chiticariu–Tan's survey is the standard reference.
- **Access control on provenance:** work on *security views* over provenance graphs and on *provenance redaction/abstraction* — e.g., access-controlled provenance for scientific workflows (PROV graphs), and graph-grouping/abstraction that hides sensitive nodes while preserving structure. Policy-aware provenance for databases (Davidson, Roy, et al.) studies the *module-privacy* problem: hiding a module's behavior in a workflow while exposing the rest, with provable guarantees and **NP-hardness** of optimal hiding.
- **Systems:** ProvSQL (Senellart et al.) computes semiring provenance in PostgreSQL; PERM/GProM (Glavic et al.) compute provenance via query rewriting — practical substrates, but access control over the produced provenance is largely policy-by-construction, not proven non-leaking.

## 4. Upper Bound

For specific, restricted settings, safe-and-useful release is computable. **Module privacy** (Davidson et al.) gives algorithms that, by hiding a minimal set of additional data, guarantee $\Gamma$-privacy (the hidden module's I/O is indistinguishable among $\Gamma$ possibilities) — a constructive upper bound, with *propagation* algorithms in polynomial time for restricted workflow shapes. Where-provenance can be filtered by base-cell ACLs in linear time (drop pointers to hidden cells). For positive (monotone) queries, redacting hidden variables to an opaque token yields a sound, polynomial-time sanitizer; its *utility-optimal* version is the hard part. Differential-privacy-style noised provenance gives quantitative $\varepsilon$-bounds for aggregate lineage.

## 5. Lower Bound

- **Hyperproperty barrier:** non-leakage is **2-safety**, so it cannot be certified by inspecting single provenance answers; general checking is undecidable in the program model.
- **NP-hardness:** optimal *standalone/workflow module privacy* — choosing the minimum extra data to hide so a sensitive module stays $\Gamma$-private — is **NP-hard** (Davidson, Khanna, Roy, et al.), as is utility-maximal sanitization in general.
- **Inference impossibility:** if the *visible* result + schema + integrity constraints functionally determine a hidden tuple, *no* provenance redaction can prevent inference — the leak is via the answer itself, not the provenance (a fundamental limit shared with statistical-database inference control / the *tracker* problem). Thus there exist policies for which **no** useful, non-leaking provenance exists.

## 6. The Gap

We have (a) a complete semantic theory of *what* provenance is (semirings) and (b) point solutions and hardness results for *hiding* it (module privacy, security views). The **open gap**: a *general, declarative* access-control model for provenance that is **provably consistent with the base-data policy** (no formal guarantee currently composes provenance policies with row/column/aggregate policies), is **utility-aware** (returns maximal safe lineage), and is **practical** over how-provenance (polynomials), not just lineage sets. The availability/confidentiality trade-off lacks tight characterizations. Closing it needs: a noninterference-grounded provenance-release semantics, tractable approximations to the NP-hard sanitization, and integration with DP for quantitative aggregate lineage.

## 7. Current Research (as of June 2026)

- Provenance for **explanations** in ML/data systems (why a prediction, why an anomaly) — and the privacy of those explanations, echoing membership-inference attacks via explanations *(frontier — verify)*.
- ProvSQL/GProM-style systems gaining policy-aware provenance filters; semiring provenance over access-controlled views.
- Connections between *intervention-based* explanations (Roy–Suciu "causality/responsibility") and what they leak about hidden tuples.
- Differential privacy for lineage and counting provenance; bounding $I(H;\textit{view})$ for aggregate explanations.
- PROV-graph abstraction/redaction for compliance (GDPR "right to explanation" vs. third-party data) *(frontier — verify)*.
- Groups: Tannen/Davidson/Roy (Penn), Glavic (IIT), Senellart (ENS), Suciu (UW).

## 8. Future Work

- A declarative provenance access-control language proven to refine base-data policies.
- Tractable utility-maximal redaction with approximation guarantees for the NP-hard cases.
- Quantitative (DP-style) bounds for how-provenance and explanation release.
- Handling integrity-constraint-driven inference (when the answer alone leaks).
- Provenance access control for ML/workflow explanations and federated/multi-source lineage.

## 9. Key References

- **[Foundational]** Green, T. J., Karvounarakis, G., Tannen, V. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Buneman, P., Khanna, S., Tan, W.-C. *Why and Where: A Characterization of Data Provenance.* ICDT, 2001. — [DOI](https://doi.org/10.1007/3-540-44503-X_20)
- **[SOTA]** Davidson, S., Khanna, S., Roy, S., et al. *Privacy Issues in Scientific Workflow Provenance / Module Privacy.* VLDB & PODS, 2010–2011. — [arXiv](https://arxiv.org/abs/1005.5543)
- **[SOTA]** Senellart, P., et al. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[Survey]** Cheney, J., Chiticariu, L., Tan, W.-C. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)
- **[SOTA]** Glavic, B., et al. *GProM: A Generic Provenance Middleware.* (TaPP / VLDB), 2014–2017. — [DBLP search](https://dblp.org/search?q=Generic+Provenance+Middleware+Queries+Updates+Transactions+Arab+Glavic)

## 10. Worked Example

Relation **Salary**, each tuple tagged with a provenance variable:

| Emp | Salary | prov |
|-----|--------|------|
| Ann | 100 | $x_1$ |
| Bob | 120 | $x_2$ |
| Cy  | 80  | $x_3$ |

A user may see the aggregate $\text{AVG}(Salary)=100$ but **not** individual rows: policy $\Pi$ hides $\{x_1,x_2,x_3\}$. The query $Q=\;$ "employees earning $>90$" returns $\{Ann, Bob\}$ with **how-provenance** polynomials $p_{Ann}=x_1$, $p_{Bob}=x_2$ in the semiring $\mathbb{N}[X]$.

Releasing $p_{Ann}=x_1$ is **unsafe**: it reveals that Ann's hidden tuple exists and singly caused the result. Formally, $\textit{view}_u(p_{Ann})$ depends on the hidden valuation of $x_1$, violating the noninterference condition $\textit{view}_u(p)|_h = \textit{view}_u(p)|_{h'}$.

A sanitizer applies the homomorphism $\phi$ mapping every hidden $x_i \mapsto \bullet$ (opaque), giving $\phi(p_{Ann})=\bullet$: the user learns "some hidden source contributed" but not which — sound but low-utility. Note that even fully redacting provenance cannot stop inference here: knowing $\text{AVG}=100$, count $=3$, and two visible-via-aggregate facts can still narrow the third salary — the §5 "answer-itself" leak.

---
*Part of the [DBMS Research catalog](../../README.md).*
