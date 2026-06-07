---
id: 23-database-security/dynamic-sod-enforcement
title: "Dynamic Separation of Duty Enforcement"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Dynamic Separation of Duty Enforcement

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/dynamic-sod-enforcement` · **Status:** open

## 1. Problem Statement

**Separation of Duty (SoD)** forbids any single principal from completing a sensitive *business task* by performing a forbidden combination of steps (e.g., the same clerk both *creates* and *approves* a payment). **Dynamic SoD (DSoD)** makes the constraint *history-dependent*: whether a user may execute step $s$ on object $o$ depends on which steps that user (or her role-conflict class) already executed on $o$ in the current workflow instance. The enforcement problem is to admit or reject each incoming transaction step so that **no execution history ever violates** any DSoD constraint, while running under **concurrent, interleaved transactions** without simply serializing all conflicting access.

- **Decision variant:** given a set of DSoD constraints, a partial execution history, and a requested step, is granting it *safe* (no reachable history violates a constraint)?
- **Optimization variant:** maximize concurrency / throughput (minimize aborts or lock-hold time) subject to never admitting an unsafe interleaving.
- **Counting variant:** count the number of distinct conflict-free user-to-step assignments that complete a workflow (relevant to *satisfiability*: does a valid assignment exist at all?).

## 2. Mathematical Foundations

Model a workflow as steps $S=\{s_1,\dots,s_k\}$ with a *step authorization relation* $A \subseteq U \times S$ and a set of **entailment constraints**. A DSoD constraint is a pair $(c, \rho)$ requiring that no $c$ of the steps in a *scope* $\rho \subseteq S$ are all performed by users drawn from a single conflicting set. The classic **Workflow Satisfiability Problem (WSP)** asks whether a plan $\pi: S \to U$ exists with $\pi(s)\in A(s)$ for all $s$ and all SoD/binding constraints satisfied.

WSP is **NP-hard** in general (Wang–Li, TISSEC 2010) but **fixed-parameter tractable** in $k$ (the number of steps): for *user-independent* constraints it is solvable in $O^*(2^{k\log k})$ via the pattern-backtracking / Crampton–Gutin–Karapetyan FPT algorithms. Under concurrency the relevant object is the **reachable-state graph** of interleavings; a schedule is safe iff every prefix maps to a WSP-satisfiable residual. This couples access control with **conflict serializability** $\Rightarrow$ the enforcement monitor must reason about commutativity of grant/deny decisions, not just data conflicts.

$$ \text{Safe}(h, s, u) \iff \forall\, h' \text{ reachable from } h\cdot(s,u):\ h' \models \bigwedge (c_i,\rho_i). $$

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Crampton, Gutin, Karapetyan, Watrigant — FPT algorithms for WSP with user-independent and *class-independent* constraints ($O^*(2^{k\log k})$); ILP/SAT and pattern-based solvers (Karapetyan et al.) handle thousands of users for $k \le 50$. Basin, Burri, Karjoth (*Obstruction-free SoD*) characterize when an enforcement monitor can guarantee completion ("resiliency") rather than deadlock.
- **Systems-SOTA:** RBAC/ABAC engines (XACML PDPs, Oracle Label Security, PostgreSQL row-level security) enforce *static* SoD natively but treat DSoD as application logic. Workflow engines (Camunda, jBPM) implement history checks per-instance, typically by pessimistically locking the case. No mainstream DBMS provides serializable DSoD as a first-class transactional guarantee.

## 4. Upper Bound

Per-step admission decision: solving the residual WSP is **FPT in $k$**, $O^*(2^{k\log k})$ time, in the standard RAM model — practical because $k$ (steps per workflow) is small even when $|U|$ is large. Under concurrency, an *obstruction-free* monitor (Basin–Burri–Karjoth) admits steps in time polynomial in history length per request while preserving the invariant, at the cost of possibly aborting in-flight cases. With **commutativity analysis**, conflicting steps need only be serialized pairwise, giving throughput close to multi-version concurrency control on the non-conflicting majority.

## 5. Lower Bound

WSP is **NP-complete** even for simple SoD constraints (reduction from Graph $k$-Colorability / Exact Cover), so admission that always preserves *future satisfiability* is NP-hard in $k+|U|$ unless restricted. Adding serializable concurrency makes the *safe-schedule existence* problem at least as hard as **conflict-serializability testing combined with WSP**; deciding serializability of a general schedule is itself NP-complete (View-Serializability, Papadimitriou). No FPT result is known when constraints are *not* user-independent — those are W[1]-hard, a conditional lower bound under FPT $\neq$ W[1].

## 6. The Gap

For *user-independent* DSoD the **static** decision problem is essentially settled ($\Theta^*(2^{k\log k})$ matching W[1]-hardness for the general case). The genuinely **open** gap is the *concurrent* version: there is no known algorithm that achieves serializable DSoD enforcement with provably *minimal* added serialization (only conflicting steps), nor a lower bound proving extra blocking is unavoidable. Closing it requires either a concurrency-control protocol whose abort/lock set is provably optimal for a given constraint set, or an impossibility result tying DSoD enforcement to a stronger isolation level than the data conflicts alone demand.

## 7. Current Research (as of June 2026)

Active threads: (1) **resiliency-aware WSP** — enforcing DSoD when users may become unavailable (Crampton, Gutin, Watrigant); (2) integrating DSoD into **serializable transactions** via commutativity/escrow so admission decisions commute with data operations; (3) **policy-as-data** approaches that push history checks into the query optimizer using triggers and materialized conflict views. *(frontier — verify)* Recent work explores ABAC-style DSoD with continuous/risk-adaptive constraints and FPT solvers parameterized jointly by steps and constraint treewidth. Groups: ETH Zürich (Basin), Royal Holloway / Leicester (Crampton, Gutin), and several workflow-security teams in the policy/ABAC community.

## 8. Future Work

- A concurrency-control protocol that serializes *only* genuinely conflicting DSoD steps with a proven optimality/competitiveness guarantee.
- Incremental / streaming WSP under transaction aborts and rollbacks (re-satisfiability after partial undo).
- DSoD over **distributed / sharded** databases where history is not centrally observable.
- Risk-adaptive ("break-glass") DSoD with quantified residual-risk bounds rather than hard deny.

## 9. Key References

- **[Foundational]** Sandhu, R. *Transaction Control Expressions for Separation of Duties.* ACSAC, 1988. — [IEEE](https://ieeexplore.ieee.org/document/113349)
- **[Foundational]** Wang, Q., Li, N. *Satisfiability and Resiliency in Workflow Authorization Systems.* ACM TISSEC, 2010. — [DOI](https://doi.org/10.1145/1880022.1880034)
- **[SOTA]** Crampton, J., Gutin, G., Yeo, A. *On the Parameterized Complexity and Kernelization of the Workflow Satisfiability Problem.* ACM TISSEC, 2013. — [DOI](https://doi.org/10.1145/2487222.2487226)
- **[SOTA]** Karapetyan, D., Gagarin, A., Gutin, G. *Pattern Backtracking Algorithm for the Workflow Satisfiability Problem with User-Independent Constraints.* J. Heuristics / FAW, 2015. — [arXiv](https://arxiv.org/abs/1412.7834)
- **[SOTA]** Basin, D., Burri, S.J., Karjoth, G. *Obstruction-Free Authorization Enforcement: Aligning Security and Business Objectives.* Journal of Computer Security, 2014. — [DOI](https://doi.org/10.3233/JCS-140500)
- **[Survey]** Crampton, J., Gutin, G., Karapetyan, D., Watrigant, R. *The Bi-Objective Workflow Satisfiability Problem and Workflow Resiliency.* Journal of Computer Security, 2017. — [arXiv](https://arxiv.org/abs/1512.07019)

## 10. Worked Example

A payment workflow has $k=3$ steps: $s_1$ *create*, $s_2$ *approve*, $s_3$ *pay*. Users $U=\{a,b,c\}$, authorization $A$: $a$ may do $s_1,s_2$; $b$ may do $s_2,s_3$; $c$ may do $s_3$. Two DSoD constraints: $(s_1,s_2)$ different users, and $(s_2,s_3)$ different users.

Enumerate satisfiable plans $\pi:S\to U$. $\pi(s_1)=a$ (only option). For $s_2$: must differ from $a$, and be authorized for $s_2$, so $\pi(s_2)=b$. For $s_3$: must differ from $b$, authorized for $s_3$, so $\pi(s_3)=c$. Exactly **one** valid plan: $(a,b,c)$. The instance is satisfiable but tightly so.

Now a *dynamic* admission trace. Step $s_1$ arrives from $a$ — grant (history $h=\{(s_1,a)\}$). Step $s_3$ arrives from $b$ — granting yields residual where $s_2$ must avoid both its $(s_1,s_2)$ partner $a$ and its $(s_2,s_3)$ partner $b$; but the only $s_2$-authorized users are $a,b$ — residual WSP **unsatisfiable**, so the monitor must **deny** $s_3$-by-$b$ to stay safe, even though no constraint is yet literally violated. This is the lookahead the FPT residual-satisfiability check performs at each step, $O^*(2^{k\log k})$ with $k=3$ trivial here.

---
*Part of the [DBMS Research catalog](../../README.md).*
