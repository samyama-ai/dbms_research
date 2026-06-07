---
id: 01-relational-theory/conditional-fd-theory
title: "Conditional FD Implication Theory"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Conditional FD Implication Theory

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/conditional-fd-theory` · **Status:** partially-solved

## 1. Problem Statement

**Conditional functional dependencies (CFDs)** extend FDs with a pattern tableau that restricts the dependency to *parts* of a relation (e.g., "for tuples with country = UK, zip → street"). They were introduced for data cleaning and inconsistency detection. The theory problems:

- **(Implication / Decision)** Given a set $\Sigma$ of CFDs and a candidate $\sigma$, decide $\Sigma \models \sigma$.
- **(Consistency / Satisfiability)** Decide whether $\Sigma$ is satisfiable by a non-empty instance (unlike FDs, CFD sets can be inconsistent).
- **(Axiomatization)** Provide a sound and complete inference system.
- **(Approximate FDs)** For AFDs/measures ($g_3$ error, reliable FDs), characterize implication and discovery complexity.
- **(Counting/discovery)** Mine a cover of CFDs/AFDs holding (approximately) in a given instance.

## 2. Mathematical Foundations

A CFD over $R$ is $(X \to Y, T_p)$ where $T_p$ is a **pattern tableau**: each row assigns to attributes in $X \cup Y$ either a constant or the wildcard "$\_$". A tuple matches a pattern if it agrees on all constant entries. The CFD holds iff for every pair of tuples matching the same $X$-pattern and agreeing on $X$, they agree on $Y$ (and any constant $Y$-pattern is enforced). Standard FDs are the all-wildcard special case.

Key results (Fan, Geerts, Jia, Kementsietsidis, *TODS* 2008):
- **Satisfiability of CFDs is NP-complete** (constant patterns can conflict), versus trivial for FDs.
- **Implication is coNP-complete** for general CFDs, versus PTIME for FDs.
- A **sound and complete finite axiomatization** exists, generalizing Armstrong's axioms with pattern-merge/inference rules.

For approximate FDs, the $g_3$ measure is
$$
g_3(X\!\to\!Y, r) = 1 - \frac{\max\{|s| : s \subseteq r,\ s \models X\to Y\}}{|r|},
$$
the minimum fraction of tuples to delete to satisfy the FD. Information-theoretic and VC-style bounds govern sampling-based discovery.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fan et al. (*TODS* 2008) settled satisfiability (NP-c), implication (coNP-c), and gave the axiomatization for CFDs; extensions to **conditional inclusion dependencies (CINDs)** followed (Bravo, Fan, Ma). Kenig & Suciu (2020–22) recast approximate/exact implication via entropy, giving **relaxation** results.
- **Systems-SOTA.** Discovery tools: **CTANE / FastCFD** (Fan, Geerts, Li, Xiong, *TKDE* 2011); profilers **Metanome** and **HyFD/CFDDiscovery** (Papenbrock, Naumann). Cleaning systems **HoloClean** (Ré, Rekatsinas) and **NADEEF** use (C)FDs/denial constraints as signals.

## 4. Upper Bound

CFD implication is decidable in **coNP** and satisfiability in **NP** (Fan et al. 2008); both drop to **PTIME** when patterns use a fixed finite domain bound or for "constant-free" CFDs that reduce to FDs. Discovery of a CFD cover is exponential in the worst case (number of patterns), with practical **CTANE** running in time polynomial in instance size and exponential only in the lattice level / attribute count. AFD implication for the $g_3$/reliable-FD measures admits PTIME checking for fixed thresholds. Model: finite-instance semantics with constant patterns over a possibly infinite domain.

## 5. Lower Bound

- **CFD satisfiability is NP-hard** and **implication is coNP-hard** (Fan, Geerts, Jia, Kementsietsidis 2008) — reductions from (non)satisfiability with conflicting constant patterns. This is a sharp jump over FDs, whose implication is linear-time.
- **Discovery** of minimal CFDs/AFDs is at least as hard as FD discovery, which has **exponential** lower bounds in attribute count (the number of minimal FDs can be exponential; Mannila–Räihä), so any complete cover is worst-case exponential-size — an output-sensitivity lower bound.
- For approximate dependencies, exact $g_3$ computation relates to maximum-satisfying-subset problems that are **NP-hard** in some constrained variants.

## 6. The Gap

The **classical decision questions are essentially closed**: tight NP/coNP completeness with a complete axiomatization for CFDs and CINDs. The open frontier is on the **approximate / probabilistic** side: a clean, unified implication theory and axiomatization for AFDs under various error measures ($g_3$, mutual-information, $\tau$), tight sample-complexity bounds for PAC-style discovery, and complexity of *discovering minimal-error* CFDs rather than exact ones. Bridging the entropic-relaxation view (Kenig–Suciu) to a practical proof system is the gap whose closure is sought.

## 7. Current Research (as of June 2026)

- **Entropic / information-theoretic implication** unifying exact, approximate, and conditional dependencies (Kenig, Suciu, Albarghouthi). *(frontier — verify)* Recent work tightens "exact implies approximate" relaxation bounds and extends to differential-privacy-aware dependency reasoning.
- **ML-assisted dependency discovery** and integration with **HoloClean**-style probabilistic cleaning; denial-constraint discovery (Pena, Naumann, *VLDB* 2019+) subsumes many CFDs.
- *(frontier — verify)* Use of CFD/denial-constraint reasoning to validate and repair LLM-extracted or synthetic tabular data is an emerging applied direction.
- Fine-grained complexity of approximate-FD discovery via sampling and sketching.

## 8. Future Work

- Sound/complete axiomatization for approximate FDs under a principled error semantics.
- Tight PAC / VC sample-complexity bounds for (C)FD discovery.
- Scalable incremental CFD discovery under updates and streams.
- Unifying CFDs, CINDs, denial constraints, and AFDs under one entropic implication calculus.

## 9. Key References

- **[Foundational]** W. Fan, F. Geerts, X. Jia, A. Kementsietsidis. *Conditional functional dependencies for capturing data inconsistencies.* ACM TODS, 2008. — [DOI](https://doi.org/10.1145/1366102.1366103)
- **[SOTA]** W. Fan, F. Geerts, J. Li, M. Xiong. *Discovering conditional functional dependencies.* IEEE TKDE, 2011. — [DOI](https://doi.org/10.1109/TKDE.2010.154)
- **[SOTA]** B. Kenig, D. Suciu. *Integrity constraints revisited: from exact to approximate implication.* ICDT / Logical Methods in Computer Science, 2020–2022. — [arXiv](https://arxiv.org/abs/1812.09987)
- **[Survey]** T. Papenbrock, F. Naumann, et al. *Functional dependency discovery: an experimental evaluation of seven algorithms.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2794367.2794377)
- **[SOTA]** T. Rekatsinas, X. Chu, I. F. Ilyas, C. Ré. *HoloClean: holistic data repairs with probabilistic inference.* PVLDB, 2017. — [DOI](https://doi.org/10.14778/3137628.3137631)
- **[Foundational]** H. Mannila, K.-J. Räihä. *Algorithms for inferring functional dependencies from relations.* Data & Knowledge Engineering, 1994. — [DOI](https://doi.org/10.1016/0169-023X(94)90023-X)

## 10. Worked Example

Relation $\mathit{Cust}(\text{CC},\text{zip},\text{city})$ (CC = country code). CFD:
$$\varphi=([\text{CC},\text{zip}]\to[\text{city}],\ T_p),\qquad T_p:\ (\text{CC}=\text{44},\ \text{zip}=\_\ \Vert\ \text{city}=\_).$$

This says: *for UK tuples (CC = 44), zip determines city*; it imposes nothing on other countries. Instance:

| | CC | zip | city |
|--|----|-----|------|
|$t_1$| 44 | EH1 | Edinburgh |
|$t_2$| 44 | EH1 | Glasgow |
|$t_3$| 01 | 10001 | New York |

$t_1,t_2$ both match the pattern (CC = 44) and agree on zip but **disagree on city**, so $\varphi$ is violated — exactly the inconsistency CFDs catch that a plain FD $\text{CC},\text{zip}\to\text{city}$ would also catch, but here scoped to UK only.

$g_3$ error: deleting one of $\{t_1,t_2\}$ restores satisfaction, and that is minimal, so
$$g_3(\varphi)=1-\tfrac{2}{3}=\tfrac{1}{3}.$$

Satisfiability subtlety: adding a constant CFD forcing $\text{city}=\text{London}$ for $\text{zip}=\text{EH1}$ would conflict with the Edinburgh constant — such constant-pattern conflicts are why CFD satisfiability is NP-complete, unlike for FDs.

---
*Part of the [DBMS Research catalog](../../README.md).*
