# Safety of Propagating Access Rights

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/hru-safety-decidability` · **Status:** open

## 1. Problem Statement

A *protection state* is an access-control configuration: which subjects hold which rights over which objects. A *protection system* specifies commands that transform protection states (granting, revoking, creating subjects/objects). The **safety question** asks: given an initial state and a generic right $r$, can any sequence of commands ever *leak* $r$ into a cell where it was not present — i.e., reach a state in which some subject acquires $r$ over some object it could not previously reach?

The decision problem: *Given a protection system $\langle \mathcal{S}, \mathcal{O}, \mathcal{C}\rangle$, an initial matrix $M_0$, and a right $r$, is the system **safe** for $r$ (no reachable state leaks $r$)?*

The open problem is not whether the general case is decidable (it is not — see §5) but to **characterize the maximal sub-classes of protection systems that remain decidable while retaining enough expressiveness to model real DBMS authorization** (delegation, grant-option propagation, role hierarchies). The frontier sits between the undecidable Harrison–Ruzzo–Ullman (HRU) matrix model and trivially weak monotonic / take–grant systems.

## 2. Mathematical Foundations

The HRU model represents state as an access matrix $M : \mathcal{S} \times \mathcal{O} \to 2^{R}$, where $R$ is a finite set of generic rights. Commands have the form

$$\textbf{command } \alpha(X_1,\dots,X_k)\;\textbf{if } r_1 \in M[X_{s_1},X_{o_1}] \wedge \dots \textbf{ then } op_1; \dots; op_m$$

with primitive operations $op_i \in \{\textsf{enter } r, \textsf{delete } r, \textsf{create subject}, \textsf{create object}, \textsf{destroy }\}$. A command is **mono-operational** if $m=1$.

Key results it rests on:
- **HRU Theorem.** Safety for general HRU is *undecidable* by reduction from the halting problem of a Turing machine encoded in subject/object creation.
- **Mono-operational decidability.** Safety for mono-operational HRU systems is decidable but **NP-complete**.
- **Mono-conditional / monotonic** systems and the **Take–Grant** model admit *linear-time* safety via graph reachability over "can-share"/"can-steal" predicates.
- **Schematic Protection Model (SPM)** and **Typed Access Matrix (TAM)**: safety is decidable for *acyclic, monotonic TAM* but undecidable for general TAM.

The expressiveness/decidability frontier is the object of study: one seeks a class $\mathcal{K}$ with decidable safety such that any RBAC/ABAC delegation policy of practical interest embeds into $\mathcal{K}$.

## 3. State of the Art (SOTA)

- **HRU (1976)** — the original undecidability result and mono-operational NP-completeness.
- **Take–Grant (Lipton–Snyder, 1977)** — linear-time safety for a graph-rewriting model.
- **SPM (Sandhu, 1988)** and **TAM (Sandhu, 1992)** — typed refinements; *ternary monotonic TAM* is decidable, general TAM undecidable.
- **ARBAC97 / administrative RBAC analysis (Sandhu et al.; Li–Tripunitara, 2004–2006)** — safety/reachability for role-administration becomes **PSPACE-complete** under bounded role sets; this is the practical SOTA target model.
- Systems-SOTA: policy analyzers such as **Margrave** (XACML) and SMT-backed ABAC reachability checkers reduce bounded safety to model checking / SAT-modulo-theories.

## 4. Upper Bound

- Mono-operational HRU: safety decidable, **NP** (and NP-complete).
- Take–Grant: **$O(n)$** in graph size.
- Acyclic monotonic TAM: decidable, with complexity depending on type-graph depth.
- Bounded administrative RBAC (ARBAC): user-role reachability is in **PSPACE**; restricted fragments (separate administration, no negative preconditions) drop to **NP** or **P**.

Best general statement: *no algorithm decides safety for all HRU systems*; upper bounds exist only per sub-class.

## 5. Lower Bound

- **General HRU safety is undecidable** (reduction from Turing-machine halting; HRU 1976).
- **Mono-operational safety is NP-hard** (HRU).
- **General TAM safety is undecidable** (Sandhu 1992).
- **ARBAC user-role reachability is PSPACE-complete** (Li–Tripunitara 2006) even with finite role sets — the hardness comes from the exponential reachable-state space.

These establish that any decidable, expressive class must restrict either creation (unbounded object generation drives undecidability) or non-monotonicity (revocation interacting with grant).

## 6. The Gap

Decidability is settled at the two extremes: undecidable for general HRU/TAM, tractable for Take–Grant. The genuinely **open** part is the *middle*: a model that (a) supports bounded creation, delegation with grant-option, role hierarchies, and *some* revocation, while (b) keeping safety decidable with practical (ideally polynomial, or at worst PSPACE) complexity. No characterization theorem currently delimits exactly which combinations of features cross from decidable to undecidable, and which decidable fragments are NP vs PSPACE. Closing it requires a dichotomy-style classification over the feature lattice (creation × monotonicity × typing × hierarchy).

## 7. Current Research (as of June 2026)

- SMT/CHC-based bounded and unbounded reachability for ABAC and attribute-delegation policies; abstraction-refinement to push past bounded safety *(frontier — verify)*.
- Decidability dichotomies for **relationship-based access control (ReBAC)** and graph-policy languages (Google **Zanzibar**-style models), where safety becomes a question over recursive graph queries / Datalog evaluation.
- Connections to **Datalog and the chase**: safety as boundedness/termination of policy-derivation rules, importing decidability results from existential-rule (TGD) reasoning.
- Groups: Ninghui Li and collaborators (Purdue) on RBAC/ABAC analysis; formal-methods teams applying CHC solvers; the ReBAC verification community *(frontier — verify)*.

## 8. Future Work

- A **feature-lattice dichotomy theorem** mapping each protection-system feature combination to decidable/undecidable and to its exact complexity class.
- Decidable fragments closed under composition, so that modular policy components preserve safety.
- Tight safety analysis for industrial ReBAC (Zanzibar-like) with hierarchies and computed usersets.
- Practical: certified policy analyzers whose decidable fragment provably covers a named, documented policy idiom set.

## 9. Key References

- **[Foundational]** Michael A. Harrison, Walter L. Ruzzo, Jeffrey D. Ullman. *Protection in Operating Systems.* Communications of the ACM, 1976.
- **[Foundational]** Richard J. Lipton, Lawrence Snyder. *A Linear Time Algorithm for Deciding Subject Security.* Journal of the ACM, 1977.
- **[Foundational]** Ravi S. Sandhu. *The Typed Access Matrix Model.* IEEE Symposium on Security and Privacy, 1992.
- **[SOTA]** Ninghui Li, Mahesh V. Tripunitara. *Security Analysis in Role-Based Access Control.* ACM Transactions on Information and System Security (TISSEC), 2006.
- **[Foundational]** Ravi S. Sandhu. *The Schematic Protection Model: Its Definition and Analysis for Acyclic Attenuating Schemes.* Journal of the ACM, 1988.
- **[SOTA]** R. Pang et al. *Zanzibar: Google's Consistent, Global Authorization System.* USENIX ATC, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
