---
id: 22-provenance-lineage/provenance-access-control
title: "Provenance-Based Access Control"
topic: 22-provenance-lineage
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Provenance-Based Access Control

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-access-control` · **Status:** open

## 1. Problem Statement

Classical access control decides whether a principal may read/write a data item from the item's *current* attributes. **Provenance-based access control (PBAC)** decides access from the item's *lineage*: who produced it, through which transformations, from which sources, and under which prior policies. Examples: "an analyst may see an aggregate only if every source tuple it depends on is cleared for them"; "a derived record inherits the most restrictive label among its inputs"; "a value computed via an untrusted pipeline is quarantined."

The problem is to (a) specify provenance-derived policies precisely, (b) *enforce* them efficiently at query time, and (c) *verify* that enforcement yields sound **information-flow** guarantees — i.e., no principal can infer protected source content through the lineage of permitted answers (no laundering through derivation).

Variants:
- **Decision (enforcement):** Given a query, principal, and provenance policy, is each output tuple authorized?
- **Verification:** Does a labeling/declassification scheme satisfy non-interference / a chosen flow lattice?
- **Optimization:** Minimal-redaction release maximizing utility under the policy.

## 2. Mathematical Foundations

Model lineage as a provenance semiring annotation (Green–Tannen) or as a **provenance graph** $G=(V,E)$ with agent/activity/entity nodes (W3C PROV). Policies are functions over annotations.

Security labels form a **lattice** $(L,\sqsubseteq,\sqcup,\sqcap)$ (Denning). A flow from $a$ to $b$ is legal iff $\ell(a)\sqsubseteq\ell(b)$. PBAC computes a derived label by a semiring/lattice homomorphism:
$$\ell(t) \;=\; \bigsqcup_{s \in \mathrm{lineage}(t)} \ell(s)\quad\text{(join over sources, "high water mark").}$$

Soundness target = **non-interference**: for principal clearance $c$, the projection of outputs visible to $c$ is a function only of inputs with $\ell \sqsubseteq c$. Formally, if $D_1,D_2$ agree on all $\sqsubseteq c$ tuples then $\mathrm{view}_c(Q(D_1))=\mathrm{view}_c(Q(D_2))$. Controlled relaxations use **declassification** (the *what/where/when/who* dimensions of Sabelfeld–Sands). Annotation propagation over positive relational algebra corresponds to the security semiring $(\mathbb{S}, \sqcap, \sqcup)$ studied by Foster–Green–Tannen.

## 3. State of the Art (SOTA)

- **Security-semiring provenance** (Foster, Green, Tannen, ICDT 2008) gives a clean algebra for propagating clearance labels through positive RA, the theory-SOTA for *propagation correctness*.
- **W3C PROV / PROV-DM** plus graph-reachability policy engines drive systems-SOTA; SELinux-style and Pedigree/provenance-aware OS work (PASS, Hi-Fi) enforce flow at the kernel.
- **Cyclon / Trio / Orchestra**-lineage systems support where/why provenance that policies can reference.
- Database-level: **Oracle Label Security / row-level security** approximate PBAC but do *not* track derivation, so they miss laundering.

No production RDBMS enforces full lineage-derived information-flow with a soundness proof; that remains research-grade.

## 4. Upper Bound

For positive relational algebra (SPJU), provenance-annotated evaluation propagates lattice labels with only constant overhead per operator, so label computation is in the same complexity class as evaluation: **$\mathsf{AC}^0$ / LOGSPACE data complexity**, polynomial combined complexity. Policy checking per output tuple is $O(\text{lineage size})$; with semiring factorization the lineage circuit is polynomial in input + output, giving PTIME enforcement. For PROV-graph reachability policies, authorization is graph reachability — NL-complete, near-linear in practice.

## 5. Lower Bound

Verifying that a *declassifying* transformation preserves non-interference is undecidable in general (reduces to program equivalence / the halting problem for arbitrary transformations). For relational policies with negation/difference, deciding whether two databases are indistinguishable to a clearance — the certain-answer style check — is **$\Pi^p_2$/coNP-hard** (tied to certain-answers and view-security hardness). Detecting illegal *inference* channels (an analyst combining permitted aggregates to reconstruct a protected source) inherits **reconstruction lower bounds** (Dinur–Nissim) and is coNP-hard to audit (Miklau–Suciu view-security results: deciding whether a view discloses a query is $\Pi^p_2$-complete / undecidable in extensions).

## 6. The Gap

Propagation over *positive* queries is essentially solved (tight PTIME, sound). The open gap is the **negative/aggregate fragment plus inference channels**: enforcement is tractable but *soundness verification against an inferring adversary* sits between undecidable (general transforms) and coNP/$\Pi^p_2$-hard (relational fragments), with no tight characterization of the maximal decidable, sound, useful policy language. Closing it means finding the largest query+policy fragment with decidable non-interference and matching hardness for everything beyond.

## 7. Current Research (as of June 2026)

- Provenance + information-flow type systems for dataflow/ETL pipelines (groups around Tannen at Penn, Cheney at Edinburgh, Acar) *(frontier — verify)*.
- PROV-based policy engines integrated with row-level security and column masking in cloud warehouses (Snowflake/BigQuery research previews) *(frontier — verify)*.
- Causal-provenance access control: using counterfactual lineage (Salimi, Meliou) to bound inference channels.
- Cryptographic enforcement combining PBAC with verifiable provenance and zero-knowledge label proofs.

## 8. Future Work

- A decidable maximal policy language with proven non-interference.
- Quantitative information-flow bounds on lineage leakage (min-entropy, channel capacity).
- Integration of PBAC with differential privacy for the inference-channel problem.
- Efficient incremental re-authorization as provenance changes.
- Standardized, machine-checkable PROV policy semantics.

## 9. Key References

- **[Foundational]** Denning. *A Lattice Model of Secure Information Flow.* CACM, 1976. — [DOI](https://doi.org/10.1145/360051.360056)
- **[Foundational]** Foster, Green, Tannen. *Annotated XML: Queries and Provenance.* PODS 2008 (security semirings). — [DOI](https://doi.org/10.1145/1376916.1376954) · [DBLP](https://dblp.org/rec/conf/pods/FosterGT08.html)
- **[Foundational]** Sabelfeld, Sands. *Declassification: Dimensions and Principles.* J. Computer Security, 2009. — [DOI](https://doi.org/10.3233/JCS-2009-0352)
- **[SOTA]** Miklau, Suciu. *A Formal Analysis of Information Disclosure in Data Exchange.* SIGMOD 2004 / J. Comput. Syst. Sci., 2007. — [DOI](https://doi.org/10.1145/1007568.1007633)
- **[SOTA]** Moreau et al. *The PROV Data Model (PROV-DM).* W3C Recommendation, 2013. — [W3C](https://www.w3.org/TR/prov-dm/)
- **[Survey]** Cheney, Chiticariu, Tan. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)

## 10. Worked Example

Take a two-level lattice $L = \{\mathsf{public} \sqsubset \mathsf{secret}\}$ and a base relation $\textsf{Sales}(region, amount, \ell)$:

| region | amount | $\ell$ |
|--------|--------|--------|
| North  | 100    | public |
| South  | 200    | secret |

A clearance-public analyst runs $Q = \texttt{SUM(amount)}$. The aggregate's lineage is $\{r_1, r_2\}$, so the high-water-mark label is
$$\ell(\text{SUM}) = \ell(r_1)\sqcup\ell(r_2) = \mathsf{public}\sqcup\mathsf{secret} = \mathsf{secret}.$$
PBAC therefore **denies** the analyst the total $300$ — correctly, because the value depends on a secret tuple.

Contrast with row-level security that only checks the *output* label: it would let the analyst read $300$, never noticing the secret input — a laundering channel. The non-interference test makes this precise: change $r_2$'s amount $200\to 500$ (a secret-only edit). The public projection $\text{view}_{\mathsf{public}}$ must be unchanged. But $\text{SUM}$ jumps $300\to600$, so the unguarded view violates non-interference, while the high-water-mark label that hides SUM from public restores it.

---
*Part of the [DBMS Research catalog](../../README.md).*
