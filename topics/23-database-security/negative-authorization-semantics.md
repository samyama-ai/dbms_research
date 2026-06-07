---
id: 23-database-security/negative-authorization-semantics
title: "Negative and Default-Deny Authorization"
topic: 23-database-security
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Negative and Default-Deny Authorization

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/negative-authorization-semantics` · **Status:** partially-solved

## 1. Problem Statement

Classical discretionary access control grants positive authorizations only, with an implicit **default-deny** (closed-world) base. Real policies, however, want **negative authorizations** ("deny user $u$ access to $R$ even though her role grants it") to express exceptions concisely. Mixing positive and negative grants over a *propagation structure* (role/group hierarchies, object hierarchies) creates **conflicts**: a subject may inherit a grant along one path and a deny along another.

The problem: define authorization semantics that are (i) **well-defined** — every (subject, object, action) request has a deterministic decision; (ii) **conflict-free** — a stated resolution policy removes all ambiguity; (iii) **monotone/predictable under change** — propagation, *overriding* (a more specific authorization beats a more general one), and **revocation** behave intuitively and compose. Decision variants: *access decision* (given a policy, is request $r$ permitted?), *consistency* (is the policy conflict-free / non-contradictory?), and *safety* (can a sequence of grants/revokes ever leak a permission to an unintended subject?).

## 2. Mathematical Foundations

A policy is a set of signed authorizations $\langle s, o, a, \pm \rangle$ over subjects $s$, objects $o$, actions $a$. Subjects and objects sit in partial orders (hierarchies) $(\mathcal{S}, \preceq_S)$, $(\mathcal{O}, \preceq_O)$ along which authorizations propagate. The foundational framework is the **Flexible Authorization Framework (FAF)** of Jajodia–Samarati–Sapino–Subrahmanian (TODS 2001), which encodes propagation, conflict resolution, and decision as a **locally stratified logic program** whose unique **stable model** assigns a decision to every request — guaranteeing well-definedness.

Key resolution principles, formalized as rule strata: **denials-take-precedence** (negative beats positive on conflict), **most-specific-overrides** (use $\preceq$ to prefer the closest authorization; ties may remain), **most-specific-along-a-path**, and **explicit priorities**. Overriding is non-monotone: adding a specific deny *removes* an inherited allow, so the semantics cannot be a simple least fixed point — stratification (or well-founded/stable-model semantics) is essential. Completeness is enforced by a **default decision** (closed = deny). Decidability of the access decision follows from finiteness and stratification; the *consistency* check is whether the program has a (unique) total stable model.

## 3. State of the Art (SOTA)

**Theory-SOTA.** FAF (Jajodia et al., TODS 2001) is the canonical logic-programming semantics; Bertino–Samarati–Jajodia studied **revocation** semantics (recursive, cascading, non-cascading) and negative-authorization propagation (TKDE 1997). The **propagation algebra** and "strong/weak" authorizations of Bertino et al. predate FAF. ANSI **RBAC** (Ferraiolo–Kuhn–Sandhu) standardizes role hierarchies but deliberately omits negative permissions to avoid conflicts.

**Systems-SOTA.** **XACML** (OASIS) operationalizes Permit/Deny with explicit **combining algorithms** (deny-overrides, permit-overrides, first-applicable, only-one-applicable) and a default-deny base — essentially FAF's conflict resolution as configurable combiners. SQL's `GRANT`/`REVOKE` is positive-only with default-deny; **RLS predicates** (PostgreSQL, with `PERMISSIVE`/`RESTRICTIVE` policies combined by OR/AND) realize a limited positive+restrictive algebra. Cloud IAM (AWS) uses *explicit-deny-always-wins* over allow.

## 4. Upper Bound

For a stratified FAF policy over finite hierarchies, the access decision is computable in **polynomial time** in the policy and hierarchy size (the stable model of a stratified Datalog¬ program is computed bottom-up by strata in PTIME). XACML evaluation with standard combining algorithms is likewise polynomial per request. Materializing the full authorization relation (closure under propagation + override) is polynomial; incremental maintenance under a single grant/revoke is near-linear in affected sub-hierarchy.

## 5. Lower Bound

Unrestricted negative authorization with arbitrary recursive rules can express **non-stratified** logic programs, where a unique semantics is *not guaranteed* and deciding the existence of a (consistent) total stable model is **NP-hard** (coNP-hard for skeptical entailment). The **safety problem** — can a sequence of grant operations leak a right to an unintended subject — is **undecidable** in the general HRU access-matrix model (Harrison–Ruzzo–Ullman, 1976) and PSPACE-hard in monotone restrictions; negative authorizations and revocation do not improve this. Thus completeness/consistency in the *general* model is intractable or undecidable; tractability is bought by stratification restrictions.

## 6. The Gap

"Partially solved": within stratified/FAF-style or XACML-combiner policies the semantics are **well-defined, conflict-free, and PTIME-decidable** — a genuine solution for that fragment. The residual gap: (i) *most-specific-overrides* still leaves **incomparable-path ties** that need ad-hoc tie-breakers, and different systems (XACML vs IAM vs RLS) pick *different* defaults, so policies are not portable; (ii) interaction of negative grants with **delegation/GRANT-option and cascading revocation** lacks a single agreed algebra; (iii) the general (non-stratified, dynamic) case inherits HRU-undecidability. Closing it means a canonical, portable conflict-resolution algebra with verified equivalences across enforcement engines.

## 7. Current Research (as of June 2026)

Active work: **formal verification of policy combiners** and equivalence of XACML/IAM/RLS evaluation semantics; **ABAC and ReBAC** (relationship-based, e.g. Google **Zanzibar**/SpiceDB) where negative/exclusion semantics are re-examined at planetary scale *(frontier — verify)*; SMT- and Datalog-based **policy analyzers** (e.g. AWS *Zelkova*/IAM analyzer using SMT to prove deny-coverage) extended to negative-authorization reasoning *(frontier — verify)*; and conflict-detection tooling for default-deny RLS policy sets. Groups/people: Sandhu, Sandhu's WSPM successors; the Zanzibar/Authzed (SpiceDB) and OpenFGA communities; AWS automated-reasoning (Backes, Cook) for IAM.

## 8. Future Work

- A portable, formally specified conflict-resolution algebra unifying XACML/IAM/RLS combiners.
- Decidable safety analysis for negative-authorization + delegation in realistic fragments.
- Conflict and "dead policy" detection for large RLS/ABAC rule sets.
- Compositional semantics for negative grants under cascading revocation (links to the revocation-cascade problem).
- Default-deny correctness proofs for ReBAC graph-rewrite systems at scale.

## 9. Key References

- **[Foundational]** Jajodia, S., Samarati, P., Sapino, M.L., Subrahmanian, V.S. *Flexible Support for Multiple Access Control Policies.* ACM TODS, 2001. — [DOI](https://doi.org/10.1145/383891.383894)
- **[Foundational]** Harrison, M.A., Ruzzo, W.L., Ullman, J.D. *Protection in Operating Systems.* CACM, 1976. — [DOI](https://doi.org/10.1145/360303.360333)
- **[Foundational]** Bertino, E., Samarati, P., Jajodia, S. *An Extended Authorization Model for Relational Databases.* IEEE TKDE, 1997. — [DOI](https://doi.org/10.1109/69.567051)
- **[SOTA]** OASIS. *eXtensible Access Control Markup Language (XACML) Version 3.0.* OASIS Standard, 2013. — [OASIS](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)
- **[Foundational]** Sandhu, R., Coyne, E., Feinstein, H., Youman, C. *Role-Based Access Control Models.* IEEE Computer, 1996. — [DOI](https://doi.org/10.1109/2.485845)
- **[SOTA]** Pang, R., Caceres, R., Burrows, M., et al. *Zanzibar: Google's Consistent, Global Authorization System.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/pang)

## 10. Worked Example

**A conflict resolved by most-specific-overrides + denials-take-precedence.** Role hierarchy $\text{Intern} \preceq_S \text{Employee}$ (Employee is more general; Intern inherits its grants). Object hierarchy: table $\mathsf{Payroll}$ with column $\mathsf{Payroll.salary}$, and $\mathsf{Payroll.salary} \preceq_O \mathsf{Payroll}$.

Policy (signed authorizations):
- $a_1 = \langle \text{Employee}, \mathsf{Payroll}, \text{read}, +\rangle$ — employees may read Payroll.
- $a_2 = \langle \text{Intern}, \mathsf{Payroll.salary}, \text{read}, -\rangle$ — interns are denied the salary column.

Query: *may user Carol (an Intern) read $\mathsf{Payroll.salary}$?*

Two authorizations propagate to (Carol, salary): via $a_1$, an **allow** inherited down both hierarchies (Intern $\preceq$ Employee, salary $\preceq$ Payroll); via $a_2$, a **deny** stated directly. **Most-specific-overrides** compares them: $a_2$ targets the more specific subject *and* object, so it wins → **deny**. (Even on an incomparable tie, **denials-take-precedence** yields deny.)

As a stratified Datalog¬ program, stratum 0 derives the propagated allow; stratum 1's $\textsf{deny}$ rule fires and *blocks* the allow via negation-as-failure, so the unique stable model assigns $\textsf{decision}(\text{Carol},\mathsf{Payroll.salary},\text{read}) = \text{deny}$ — computed bottom-up in PTIME.

---
*Part of the [DBMS Research catalog](../../README.md).*
