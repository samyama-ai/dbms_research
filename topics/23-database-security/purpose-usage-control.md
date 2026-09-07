---
id: 23-database-security/purpose-usage-control
title: "Purpose-Based and Usage Control"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Purpose-Based and Usage Control

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/purpose-usage-control` · **Status:** open

## 1. Problem Statement

Classical access control answers a single question: *may principal $s$ perform action $a$ on object $o$ now?* Purpose-based and usage control (UCON) generalize this along two axes that traditional models cannot express:

- **Purpose limitation** (a core GDPR/HIPAA requirement): a data item collected for purpose $p$ may be used only for purposes *compatible* with $p$. The access decision depends not on the subject's identity alone but on the declared *intended purpose* of the query and the *allowed purpose* annotation of the data.
- **Obligations and continuity (UCON)**: authorization is not a point-in-time predicate. Decisions depend on mutable **attributes**, **conditions** (environment), and **obligations** (actions that must be performed before/during/after, e.g., "log access", "delete within 30 days", "notify data subject"). Rights may be revoked *during* ongoing use.

The decision problem: given a policy, a request, and a system state, decide whether use is permitted **and** whether the induced obligations are *enforceable* downstream — i.e., after data leaves the query result and propagates through copies, derivations, and exports. The hard part is **post-release control**: a DBMS naturally mediates the read, but obligations like "do not re-share" or "use only for billing" must bind to data that has already left the database boundary.

Variants: (decision) policy compliance of a single request; (verification) does a workflow/program satisfy all obligations on all executions; (synthesis) generate enforcement monitors; (counting/optimization) minimize obligation-tracking overhead.

## 2. Mathematical Foundations

UCON$_{ABC}$ (Park & Sandhu) models state as attribute valuations over subjects $S$ and objects $O$. A usage session is a labeled transition system; predicates **A**uthorizations, o**B**ligations, **C**onditions gate transitions `tryaccess → permitaccess → endaccess`, with attribute *mutability* updating state on pre/ongoing/post phases. Continuity is captured as a safety property over infinite traces, naturally expressed in temporal logic (LTL/obligation-LTL).

Purpose limitation is formalized over a **purpose lattice** $(P, \sqsubseteq)$: intended purpose $p_i$ is allowed iff $p_i \sqsubseteq p_a$ for the data's allowed purpose $p_a$, generalized to AIP/PIP (allowed/prohibited) sets. Compliance reduces to lattice membership.

Post-release semantics connect to **information-flow control**: an obligation "data $D$ used only for $p$" is a noninterference-style property — observable behavior in disallowed-purpose executions must be independent of $D$. Decidability hinges on the safety analysis being a reachability problem; for UCON with unbounded creates/mutability it is **undecidable in general** (HRU-style), and tractable only for restricted fragments (finite attribute domains, no creation).

$$\text{Compliant}(req,\sigma) \iff \mathbf{A}(\sigma) \wedge \mathbf{C}(\sigma) \wedge \Box\,\mathbf{B}(\text{trace})$$

## 3. State of the Art (SOTA)

- **Theory:** UCON$_{ABC}$ (Park–Sandhu 2004) is the reference model; safety analysis results (Zhang, Sandhu) delineate decidable fragments. Purpose-based access control for relational data (Byun–Bertino–Li, SACMAT 2005) ties purposes to query rewriting.
- **Systems:** Sticky policies and policy-carrying data (HP Labs, Casassa Mont et al.); **Hippocratic Databases** (Agrawal, Kiernan, Srikant, Xu, VLDB 2002) operationalize purpose via per-column purpose metadata and query-time filtering. Modern lineage-aware systems (e.g., Google's Zanzibar-style relationship ABAC) handle scale but not post-release obligations. Differential-privacy and TEE-based "clean rooms" (data clean rooms, confidential computing) enforce usage by *running computation under a monitor* rather than releasing raw tuples.

## 4. Upper Bound

For finite-attribute UCON without object creation, safety (will a forbidden right ever be granted) is decidable in **PSPACE** via model checking the induced finite transition system; obligation-LTL compliance for a fixed bounded-state policy is decidable in time polynomial in states × exponential in the formula. Query-time purpose enforcement via rewriting is essentially free: it adds a predicate, so it is **linear** in policy size and preserves the base query's complexity. TEE/clean-room enforcement gives sound post-release control at the cost of confining all computation, an upper bound of "as expensive as the confined query."

## 5. Lower Bound

General UCON safety is **undecidable** (reduction from HRU safety / Turing machine simulation via unbounded creation + mutable attributes). Even bounded fragments inherit **PSPACE-hardness** from reachability in succinctly-described transition systems. Post-release "use only for $p$" as enforced noninterference is a **hyperproperty** (relating multiple traces), so it is *not* monitorable by any single-run reference monitor — an information-theoretic impossibility for purely runtime enforcement without confinement or trusted hardware. Sticky-policy schemes thus rely on cryptographic/TEE trust assumptions, not on a sound mediation guarantee.

## 6. The Gap

The decidable/undecidable boundary for UCON is *closed* in the classical safety sense. The genuinely **open** gap is **enforceability of post-release obligations under realistic adversaries**: between (a) query-time mediation (cheap, sound, but only controls the read) and (b) full confinement in a TEE (sound post-release, but kills sharing and is costly). No mechanism cheaply enforces "compatible purpose only" once tuples are exported. Closing it requires either a confinement primitive that is composable across organizations or a formal account of which obligations are *runtime-monitorable* vs. require static/cryptographic enforcement.

## 7. Current Research (as of June 2026)

Active threads: GDPR purpose-compliance checking integrated into query compilers; obligation monitoring via runtime verification (MonPoly, metric first-order temporal logic, Basin et al., ETH Zürich); usage control for ML training data and "machine unlearning" as an obligation; confidential-computing data clean rooms (Snowflake, AWS, Google) operationalizing purpose at scale *(frontier — verify)*. Emerging work connects **information-flow control in databases** (e.g., IFC-typed query languages) with purpose lattices to get static guarantees. Privacy-engineering groups (Bertino at Purdue; Sandhu's group) continue refining attribute-based UCON.

## 8. Future Work

- A composable, cross-organizational confinement primitive for sticky obligations.
- A precise monitorability theory: which UCON obligations are pure safety (runtime-enforceable) vs. hyperproperties (need confinement/crypto).
- Purpose lattices learned from regulation text; automated compatibility reasoning.
- Integrating purpose enforcement with provenance and differential privacy so derived data inherits obligations.
- Quantifying the residual leakage when obligations are only approximately enforced.

## 9. Key References

- **[Foundational]** Park, J., Sandhu, R. *The UCON$_{ABC}$ Usage Control Model.* ACM TISSEC, 2004. — [DOI](https://doi.org/10.1145/984334.984339)
- **[Foundational]** Agrawal, R., Kiernan, J., Srikant, R., Xu, Y. *Hippocratic Databases.* VLDB, 2002. — [DBLP](https://dblp.org/rec/conf/vldb/AgrawalKSX02.html)
- **[SOTA]** Byun, J.-W., Bertino, E., Li, N. *Purpose Based Access Control of Complex Data for Privacy Protection.* SACMAT, 2005. — [DOI](https://doi.org/10.1145/1063979.1063998)
- **[SOTA]** Basin, D., Klaedtke, F., Müller, S., Zălinescu, E. *Monitoring Metric First-Order Temporal Properties.* Journal of the ACM, 2015. — [DOI](https://doi.org/10.1145/2699444)
- **[Survey]** Lazouski, A., Martinelli, F., Mori, P. *Usage Control in Computer Security: A Survey.* Computer Science Review, 2010. — [DOI](https://doi.org/10.1016/j.cosrev.2010.02.002)

## 10. Worked Example

A purpose lattice with $\textit{Marketing} \sqsubseteq \textit{Admin}$ and $\textit{Billing} \sqsubseteq \textit{Admin}$ (Admin is most general; Marketing and Billing are incomparable). Each customer row carries an **allowed purpose** $p_a$:

| Cust | Phone | $p_a$ |
|------|-------|-------|
| Ann | 555-0101 | Billing |
| Bob | 555-0102 | Admin |

**Query-time check (Hippocratic / Byun).** A billing job declares intended purpose $p_i = \textit{Billing}$. The rewrite appends predicate "$p_i \sqsubseteq p_a$": Ann passes ($\textit{Billing}\sqsubseteq\textit{Billing}$), Bob passes ($\textit{Billing}\sqsubseteq\textit{Admin}$). A marketing job ($p_i=\textit{Marketing}$) gets Bob only — Ann's row is filtered because $\textit{Marketing}\not\sqsubseteq\textit{Billing}$ (incomparable). This is the **linear** rewrite of §4: one lattice-membership test per row.

**The post-release gap.** Suppose the billing job exports Ann's phone with obligation "delete within 30 days." The DBMS soundly mediated the *read*, but "$\Box\,\textbf{B}$" — the deletion obligation over the future trace — is a property of code *outside* the database. As §5 notes, "use only for Billing" is a hyperproperty: no single-run monitor on the exported copy can certify it, so enforcement needs confinement (TEE) or crypto, not mediation alone.

---
*Part of the [DBMS Research catalog](../../README.md).*
