---
id: 23-database-security/verified-reference-monitor
title: "Verified Reference Monitors for DBMS"
topic: 23-database-security
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Verified Reference Monitors for DBMS

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/verified-reference-monitor` · **Status:** partially-solved
> **Verification note:** The canonical Cedar OOPSLA 2024 paper (DOI 10.1145/3649835) is "Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization" by Cutler et al. (AWS); §9 corrected.

## 1. Problem Statement

A **reference monitor** is the component that mediates every access to protected objects. The Anderson (1972) criteria require it to be: **complete** (it cannot be bypassed — *total mediation*), **tamperproof**, and **verifiable** (small enough to be subjected to analysis proving correctness). The problem here is the *verifiable* clause taken to its strongest form for a real DBMS:

> Produce a **machine-checked proof** that a production authorization layer (a) fully mediates all data access paths, and (b) the decisions it computes are *exactly* those entailed by a declarative policy specification — i.e., the implementation **refines** the policy with no over- or under-permission.

Sub-problems / variants:
- **(Mediation)** Prove every read/write path — including index scans, query rewriting, materialized views, replication, prepared statements, and side paths like error messages and EXPLAIN — passes through the monitor. This is a whole-program *non-bypassability* property.
- **(Soundness)** Prove the monitor's allow set $\subseteq$ policy's allow set (no privilege escalation).
- **(Completeness)** Prove policy's allow set $\subseteq$ monitor's allow set (no spurious denial / availability).
- **(Policy correctness)** Separately, prove the *policy* itself satisfies higher-level goals (e.g., noninterference between security levels).

"Partially solved": full formal verification exists for *small kernels and microhypervisors* and for *standalone policy engines*, but not yet end-to-end for a full-featured relational engine with an optimizer.

## 2. Mathematical Foundations

Let the system be a state machine $M=(\Sigma,\delta)$ with states $\sigma$ and transitions labeled by requests. A policy is a predicate $\mathrm{Pol}\subseteq \text{Req}\times\Sigma$. The monitored system $M_{\mathrm{mon}}$ permits a request iff $\mathrm{Pol}$ holds. Correctness is a **refinement**: there is a simulation relation $R$ such that $M_{\mathrm{mon}} \preceq_R \mathrm{Spec}_{\mathrm{Pol}}$.

Total mediation is the safety property: $\forall$ execution traces, every access event is immediately preceded by a granting decision event — a property over the trace alphabet, provable by an *inductive invariant* on the program's control-flow.

The gold standard for the policy side is **noninterference** (Goguen–Meseguer 1982): partition principals into levels; high-level inputs must not affect low-level observations. Formally, with purge function $\textit{purge}_\ell$,
$$\forall \tau:\quad \textit{obs}_\ell(\textit{run}(\tau)) = \textit{obs}_\ell(\textit{run}(\textit{purge}_\ell(\tau))).$$
Noninterference is a **2-safety hyperproperty**, verified by self-composition or relational program logics. Proofs are discharged in **Coq/Rocq, Isabelle/HOL, or F\***, often via translation validation or a verified compiler (CompCert-style) to extend guarantees to machine code.

## 3. State of the Art (SOTA)

- **Kernels/monitors:** **seL4** (Klein et al., SOSP 2009) — first OS kernel with machine-checked functional correctness *and* proofs of integrity/confidentiality (noninterference) down to binary. This is the canonical "verified reference monitor" exemplar, though for an OS, not a DBMS.
- **Information-flow DB:** **IFDB / SeaView**-lineage multilevel DBs; **Jacqueline / Jeeves** (Yang, Yessenov, Solar-Lezama; Austin–Flanagan) — faceted execution that enforces policies by construction. **Ur/Web** and **LWeb** (Parker, Vazou, Hicks, POPL 2019) give *mechanized* proofs of noninterference for a database-backed web language (Liquid Haskell).
- **Systems:** SQL row-level security (PostgreSQL RLS, SQL Server) and Oracle VPD are *unverified* production monitors. Cedar (AWS, 2023) is an ABAC policy language with a **formally verified** (Lean/Dafny) evaluator and analyzer — verified policy engine, not full DB mediation.

## 4. Upper Bound

Feasibility upper bound: seL4 shows that *full functional correctness + noninterference of a ~10 kLOC monitor* is achievable, at a historically reported cost of roughly 20–30 person-years (now lower with better tooling). For a *policy evaluator in isolation* (Cedar/LWeb), mechanized soundness + completeness is now routine and reusable. Total mediation for a fixed, small access path is provable by a control-flow invariant in time linear in the program. The "upper bound" is therefore *engineering-bounded*: proof effort scales super-linearly with the trusted computing base (TCB) size, which is why work pushes to shrink the mediated surface.

## 5. Lower Bound

There is no complexity *lower bound* obstacle to the proof existing — the obstruction is fundamental scope. Two hard limits:
1. **TCB minimality vs. expressiveness:** a full optimizer/executor is enormous; verifying it wholesale is the lower-bound difficulty (proof cost grows with TCB). Hence verification targets a *small* monitor with all data paths funneled through it — but proving that funneling (non-bypassability) for an optimizer that can rewrite queries is itself undecidable in general (it reduces to program equivalence).
2. **Hyperproperty limit:** confidentiality (noninterference) is **2-safety**, not 1-safety, so it cannot be enforced or fully checked by observing single runs; declassification (necessary in practice) breaks pure noninterference and requires weaker, policy-specific definitions (delimited release, gradual release) whose verification is open per policy.

## 6. The Gap

What's proven: small verified monitors (seL4) and verified policy engines (Cedar, LWeb). What's missing: an **end-to-end machine-checked proof for a full SQL engine with a cost-based optimizer**, including covert paths (timing, EXPLAIN, error oracles) — i.e., closing the gap between a verified *decision* and verified *total mediation across every execution path of a real DBMS*. The gap is genuinely open and is primarily about (a) shrinking/structuring the DB TCB so the optimizer is outside the security-critical path, and (b) verifying non-bypassability through query rewriting. Closing it likely needs a verified "security kernel for data access" that the optimizer must call, plus a noninterference proof robust to declassification.

## 7. Current Research (as of June 2026)

- AWS **Cedar** team extending verified analysis (policy validation, "is this policy a tightening?") with Lean proofs; integration toward verified data-plane enforcement *(frontier — verify)*.
- **seL4 Foundation** and Proofcraft generalizing verified-monitor techniques; verified microkernels hosting DB engines so mediation lives in a tiny verified layer.
- Liquid-Haskell / F\* groups (Hicks at Maryland; Swamy at Microsoft Research) on mechanized IFC for data-backed apps.
- Verified query compilers (DBCert, HoTTSQL/$\mathrm{U}$-semiring SQL equivalence by Chu, Cheung, Suciu) supplying the *equivalence* machinery needed to prove rewrites preserve mediation.

## 8. Future Work

- A verified, minimal "data access kernel" with the optimizer proven to only narrow, never widen, access.
- Mechanized declassification policies (delimited release) for SQL views and aggregates.
- Proofs covering side channels (timing/EXPLAIN/error) as part of the monitored interface.
- Scaling proof automation so verifying a production engine is person-months, not person-decades.

## 9. Key References

- **[Foundational]** Anderson, J. P. *Computer Security Technology Planning Study* (reference monitor concept). USAF, 1972. — [PDF](https://csrc.nist.gov/files/pubs/conference/1998/10/08/proceedings-of-the-21st-nissc-1998/final/docs/early-cs-papers/ande72a.pdf)
- **[Foundational]** Goguen, J., Meseguer, J. *Security Policies and Security Models* (noninterference). IEEE S&P, 1982. — [DOI](https://doi.org/10.1109/SP.1982.10014)
- **[SOTA]** Klein, G., et al. *seL4: Formal Verification of an OS Kernel.* SOSP, 2009. — [DOI](https://doi.org/10.1145/1629575.1629596)
- **[SOTA]** Parker, J., Vazou, N., Hicks, M. *LWeb: Information Flow Security for Multi-Tier Web Applications.* POPL, 2019. — [DOI](https://doi.org/10.1145/3290388)
- **[SOTA]** Cutler, J., et al. (AWS). *Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization.* OOPSLA, 2024. — [DOI](https://doi.org/10.1145/3649835)
- **[Survey]** Sabelfeld, A., Myers, A. *Language-Based Information-Flow Security.* IEEE JSAC, 2003. — [DOI](https://doi.org/10.1109/JSAC.2002.806121)

## 10. Worked Example

**Total mediation as a trace invariant.** Model the engine as a state machine over events $\{\textit{decide}(r), \textit{access}(o)\}$. The policy is $\mathrm{Pol}=\{(\text{read}, \texttt{tbl.salary}, \text{role}=\texttt{HR})\}$. The safety property is: every $\textit{access}(o)$ event is immediately preceded by a $\textit{decide}(r)$ that granted $o$.

Trace $\tau_1 = \langle \textit{decide}(\texttt{read salary, HR})^{\checkmark},\ \textit{access}(\texttt{salary})\rangle$ satisfies it. The inductive invariant "the last event before any access is a matching grant" holds, proved by induction over $\tau$.

**Optimizer bypass.** Now the cost optimizer rewrites `SELECT salary FROM emp WHERE id=5` using an *index-only scan* on `idx_salary`, emitting $\textit{access}(\texttt{idx\_salary})$ with **no** preceding $\textit{decide}$ — a side path. Trace $\tau_2 = \langle \textit{access}(\texttt{idx\_salary})\rangle$ *violates* the invariant: the index leaf carries the same secret column yet bypasses mediation.

This is exactly the non-bypassability gap of section 6: proving no rewrite emits an unmediated access reduces to optimizer/query equivalence, undecidable in general — so funneling *all* access paths (including indexes, EXPLAIN, error oracles) through the verified monitor is the open challenge.

---
*Part of the [DBMS Research catalog](../../README.md).*
