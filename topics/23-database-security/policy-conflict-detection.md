# Policy Conflict Detection at Scale

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/policy-conflict-detection` · **Status:** partially-solved

## 1. Problem Statement

Large access-control deployments accumulate thousands to millions of rules in **ABAC** (attribute-based) or **RBAC** (role-based with hierarchies and constraints) policies. Over time these develop anomalies:

- **Redundancy:** a rule whose effect is already implied by others (removable without changing semantics);
- **Conflict:** two rules that, for some request, prescribe opposite decisions (permit vs. deny) — requiring a resolution strategy and signaling author intent errors;
- **Unreachable / shadowed rules:** rules that can never be the deciding rule for any request, given ordering and earlier-matching rules.

The problem is to **detect all three efficiently** over realistic policies featuring attribute conditions, role hierarchies, separation-of-duty (SoD) and cardinality constraints, and combining algorithms (first-applicable, deny-overrides, etc.).

Variants:
- **Decision variant:** is rule $r$ redundant / unreachable, or do rules $r_i, r_j$ conflict (∃ a request matched oppositely)?
- **Enumeration variant:** list all conflicting/redundant/shadowed rules.
- **Optimization variant:** compute a minimum-size equivalent policy (policy minimization).

## 2. Mathematical Foundations

Represent a policy as a function $\pi: \mathcal{R} \to \{\text{permit},\text{deny},\bot\}$ over the request space $\mathcal{R} = A_1\times\cdots\times A_k$ (cross product of attribute domains). Each rule $r$ has a **condition** $\varphi_r$ (a Boolean/arithmetic predicate over attributes) and an effect; the rule's footprint is the region $\llbracket\varphi_r\rrbracket \subseteq \mathcal{R}$.

- **Conflict** between $r_i,r_j$ (opposite effects): $\llbracket\varphi_{r_i}\rrbracket \cap \llbracket\varphi_{r_j}\rrbracket \neq \emptyset$ — a **predicate satisfiability** (SMT) query.
- **Unreachable/shadowed** under first-applicable order: $\llbracket\varphi_{r}\rrbracket \subseteq \bigcup_{j<r}\llbracket\varphi_{j}\rrbracket$ — a **predicate-coverage / UNSAT** check.
- **Redundant:** removing $r$ leaves $\pi$ unchanged on all requests — equivalence of two policies, i.e. $\pi \equiv \pi\setminus r$.

These reduce to **Boolean/first-order satisfiability and validity**; with numeric/range attributes they become **SMT over linear arithmetic** or **geometric region (hyperrectangle) overlap** — connecting to computational geometry (Klee's measure, rectangle intersection) and to **BDD/decision-diagram** representations of the decision function. RBAC adds a **partial order** (role hierarchy, transitive role inheritance) and **constraints** (SoD = mutual exclusion), turning some questions into reachability/closure over a DAG and SoD-consistency into a **set-cover / hypergraph** condition (the classic RBAC role-engineering and "safety" connection).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **XACML policy analysis** via formal logic — **Margrave** (Fisler, Krishnamurthi, Meyerovich, Tschantz, ICSE 2005) compiles policies to **MTBDDs** and answers change-impact, conflict, and coverage queries; **SMT-based ABAC analysis** (encoding conditions in Z3) for numeric attributes; **EXAM** (Lin et al.) for policy similarity/conflict across XACML. RBAC anomaly detection draws on **role mining / role engineering** formalisms (Vaidya et al.) and constraint-consistency checking.
- **Systems-SOTA:** Cloud IAM analyzers — **AWS IAM Access Analyzer** (backed by **Zelkova**, an SMT-based reasoning engine, Backes et al., CAV 2019) proves policy properties at scale; **Google IAM Policy Troubleshooter**; **Open Policy Agent (Rego)** with linters; firewall/ACL analyzers (**Firmato**, **FIREMAN**, Yuan et al., S&P 2006) detect shadowing/redundancy/correlation in rule sets. Network-policy verifiers (**Veriflow**, **Header Space Analysis**) solve the geometric overlap version at line rate.

## 4. Upper Bound

Pairwise conflict/shadow detection is **$O(n^2)$ SMT/SAT queries** for $n$ rules; each query is the cost of deciding the condition logic (polynomial for pure Boolean tabular conditions via BDD operations; NP-/SMT-cost for arithmetic). **MTBDD/BDD** encodings (Margrave, Zelkova) answer conflict and coverage in time polynomial in the **diagram size**, which is small for structured real policies though worst-case exponential. Geometric (hyperrectangle) overlap detection runs in $O(n\log^{d-1} n + K)$ for $d$ attributes and $K$ overlaps via interval/segment-tree sweeps. Cloud analyzers (Zelkova) decide many real properties in **sub-second** by bounding logic to decidable, finite-domain fragments.

## 5. Lower Bound

The general decision problems are **NP-hard / coNP-hard**: conflict detection = predicate **SAT** (NP-complete for Boolean conditions), shadow/coverage = **TAUTOLOGY/UNSAT** (coNP-complete), and **minimum-equivalent-policy** is **$\Sigma_2^p$ / NP-hard** (related to minimum-DNF and Boolean-function minimization, which is $\Sigma_2^p$-complete). With arithmetic attributes the satisfiability is **NEXP/undecidable** for sufficiently rich theories (nonlinear), and SMT-decidable but worst-case exponential for linear arithmetic. BDD/MTBDD sizes are **exponential in the worst case** (variable-ordering sensitivity). RBAC **safety** in the general HRU sense is **undecidable**; constrained models (ARBAC) make administrative reachability **PSPACE-complete**.

## 6. The Gap

**Partially solved:** for bounded, finite-domain, BDD-friendly policies, conflict/shadow/redundancy detection is *practically* solved (Margrave, Zelkova run at production scale). The gap is **scalability with expressiveness**: as policies gain rich arithmetic attributes, deep role hierarchies, and SoD/cardinality constraints, the underlying SAT/SMT/BDD machinery hits the worst-case exponential wall, and **exact policy minimization** ($\Sigma_2^p$) remains intractable. What is open: detection that stays **near-linear at million-rule scale** for the full ABAC condition language with constraints, plus practical minimum-equivalent-policy synthesis. Closing it needs structure-exploiting (modular/incremental) reasoning and tight parameterized-complexity characterizations of which policy features are the cost drivers.

## 7. Current Research (as of June 2026)

Active: **incremental / change-impact analysis** (re-verify only the affected diagram region on each edit, as in Zelkova-style CI gates); **abstraction-refinement and modular decomposition** of large ABAC sets; **policy mining + anomaly detection** that flags likely-erroneous conflicts using statistical/ML signals over access logs; parameterized-complexity studies isolating tractable ABAC fragments. *(frontier — verify)* 2025–2026 work applies **LLMs to explain and cluster policy conflicts** and to translate natural-language intent into checkable invariants, and pushes **SMT-portfolio + GPU-accelerated BDD** backends for million-rule cloud IAM. Groups: AWS Automated Reasoning (Backes, Cook), Brown/PLT (Krishnamurthi/Fisler lineage), Purdue (Vaidya) on role mining.

## 8. Future Work

- Near-linear, incremental conflict/shadow detection at $10^6$+ rules with full ABAC arithmetic.
- Practical (heuristic with quality bounds) minimum-equivalent-policy synthesis.
- Parameterized-complexity map: which features (hierarchy depth, SoD, arithmetic arity) drive hardness.
- Conflict *explanation* and automated repair suggestions tied to author intent.

## 9. Key References

- **[Foundational]** Sandhu, R., Coyne, E., Feinstein, H., Youman, C. *Role-Based Access Control Models.* IEEE Computer, 1996. — [DOI](https://doi.org/10.1109/2.485845)
- **[Foundational]** Fisler, K., Krishnamurthi, S., Meyerovich, L.A., Tschantz, M.C. *Verification and Change-Impact Analysis of Access-Control Policies.* ICSE, 2005. — [DOI](https://doi.org/10.1145/1062455.1062502)
- **[SOTA]** Backes, J., Bolignano, P., Cook, B., et al. *Semantic-Based Automated Reasoning for AWS Access Policies Using SMT (Zelkova).* FMCAD/CAV, 2018–2019. — [DOI](https://doi.org/10.23919/FMCAD.2018.8602994)
- **[SOTA]** Yuan, L., Mai, J., Su, Z., Chen, H., Chuah, C.-N., Mohapatra, P. *FIREMAN: A Toolkit for FIREwall Modeling and ANalysis.* IEEE S&P, 2006. — [DOI](https://doi.org/10.1109/SP.2006.16)
- **[Survey]** Hu, V.C., et al. *Guide to Attribute Based Access Control (ABAC) Definition and Considerations.* NIST SP 800-162, 2014. — [DOI](https://doi.org/10.6028/NIST.SP.800-162)

## 10. Worked Example

Take an ABAC policy over attributes $age\in[0,100]$ and $dept\in\{HR, ENG\}$, evaluated **first-applicable** (top rule wins):

- $r_1$: **permit** if $age \ge 18 \wedge dept = HR$
- $r_2$: **deny**  if $age \ge 21$
- $r_3$: **permit** if $age \ge 18$

**Conflict ($r_1$ vs $r_2$).** Are the footprints' overlap nonempty with opposite effects? Solve $age\ge 18 \wedge dept=HR \wedge age\ge 21$. The SMT solver returns $age=21, dept=HR$ — a witness, so $r_1$ and $r_2$ **conflict**; first-applicable resolves it to *permit*, but the author may not have intended that.

**Shadowing ($r_3$).** Is $\llbracket r_3\rrbracket \subseteq \llbracket r_1\rrbracket \cup \llbracket r_2\rrbracket$? Check UNSAT of $age\ge18 \wedge \neg(age\ge18\wedge dept{=}HR) \wedge \neg(age\ge21)$. Witness $age=19, dept=ENG$ exists, so $r_3$ is **reachable** (not shadowed): a 19-year-old ENG user is decided by $r_3$.

With $n=3$ rules this took $\binom{3}{2}=3$ pairwise overlap queries plus one coverage query — illustrating the $O(n^2)$ SMT-query upper bound of §4.

---
*Part of the [DBMS Research catalog](../../README.md).*
