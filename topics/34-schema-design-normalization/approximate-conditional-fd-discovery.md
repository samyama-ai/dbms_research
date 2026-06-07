---
id: 34-schema-design-normalization/approximate-conditional-fd-discovery
title: "Robust Approximate and Conditional FD Discovery"
topic: 34-schema-design-normalization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Robust Approximate and Conditional FD Discovery

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/approximate-conditional-fd-discovery` · **Status:** partially-solved

## 1. Problem Statement

Real data is dirty: exact FDs rarely hold because of typos, missing values, and outliers. Two relaxations make dependency discovery robust:

- **Approximate FDs (AFDs):** $X \to A$ that hold on *most* of the data — i.e., a small fraction of tuples must be removed for the FD to hold exactly. Quantified by an error measure such as $g_3$ (minimum fraction of tuples to delete).
- **Conditional FDs (CFDs):** FDs that hold only on a **subset** selected by a pattern tableau, e.g., $[\text{country}=\text{UK}] : \text{zip} \to \text{city}$. CFDs were introduced for data cleaning and capture context-dependent semantics.

Problems:
- **Discovery:** mine all AFDs / CFDs above a support/confidence threshold that are **statistically meaningful** (not artifacts of small samples) and **noise-robust**.
- **Ranking:** order discovered dependencies by significance, controlling false discoveries.

## 2. Mathematical Foundations

The **$g_3$ error** of $X\to A$ on $r$ is $g_3 = 1 - \frac{\max\{|s| : s\subseteq r,\ s \models X\to A\}}{|r|}$, computable from PLIs as a minimum-vertex-removal over conflict structure. An AFD holds at threshold $\varepsilon$ iff $g_3 \le \varepsilon$. Approximate-FD validity is **not upward-closed** the way exact FDs are, complicating lattice pruning; one uses monotonicity of error under attribute addition for partial pruning.

For **CFDs**, a dependency is a pair $(X\to A,\ T_p)$ where $T_p$ is a pattern tableau of constant/wildcard rows; *support* = fraction of tuples matching $T_p$, *confidence* = fraction among those satisfying the FD. Discovery is search over (FD, pattern) pairs — a larger lattice than plain FDs.

Statistical robustness draws on **hypothesis testing / mutual information** and **VC-dimension / sample-complexity** arguments: with $m$ rows, an estimated dependency strength concentrates around its true value with error $O(\sqrt{(\text{VC}\log m)/m})$, enabling FDR-controlled selection.

## 3. State of the Art (SOTA)

- **AFD discovery:** TANE supports approximate variants via $g_3$; **Pyro** (Kruse & Naumann, PVLDB 2018) gives efficient hybrid approximate-and-exact discovery; XYStar and sampling-based estimators speed validation.
- **CFD discovery:** **CTANE / FastCFD** (Fan, Geerts, Li, Xiong, *Discovering Conditional Functional Dependencies*, ICDE 2009 / TKDE 2011) are the canonical algorithms; CFDMiner for constant CFDs.
- **Statistical/robust angle:** information-theoretic AFD measures (reliable fraction of information, **RFI**) by Mandros, Boley, Vreeken (KDD 2017) give bias-corrected, comparable dependency scores; **pyROSITA**/significance-aware mining and FDR control are recent directions.
- **Systems-SOTA:** integrated into cleaning systems (HoloClean-style, Metanome platform).

## 4. Upper Bound

- AFD discovery with $g_3$: same lattice/PLI machinery as exact FD discovery, **exponential in $n$** worst case, near-linear in $m$ for validation; Pyro is the practical upper bound.
- CFD discovery: search space is FD-lattice × pattern-tableau space, **larger** than FD discovery; CTANE/FastCFD are exponential in $n$ and pattern complexity but practical for bounded thresholds.
- Bias-corrected information measures (RFI) are computable in polynomial time per candidate, with sample-complexity bounds for reliability.

## 5. Lower Bound

- AFD/CFD discovery inherits the **exponential output** lower bound of exact FD discovery (powerset lattice; minimal-transversal hardness).
- Computing $g_3$ exactly relates to maximum-consistent-subset problems; for some richer dependency relaxations the optimal-repair version is **NP-hard**. Selecting a *minimum* set of meaningful CFDs (cover) is NP-hard via set-cover reductions.
- **Statistical lower bound:** distinguishing a true weak dependency from noise requires $\Omega(1/\Delta^2)$ samples for effect size $\Delta$ (standard estimation lower bound), bounding how robust discovery can be on limited data.

## 6. The Gap

Algorithms exist and are practical, but the **statistical-significance / multiple-testing** foundations are unsettled: thresholds ($\varepsilon$, support, confidence) are usually chosen heuristically, with no agreed framework guaranteeing controlled false-discovery rates across the exponential candidate set. The gap between *fast enumeration* and *statistically principled, noise-robust selection at scale* is open. Closing it needs unified estimation + multiple-testing theory matched to efficient enumeration.

## 7. Current Research (as of June 2026)

- **Significance-aware** dependency mining with FDR control over huge candidate sets *(frontier — verify)*.
- Robust dependencies under **missing values and uncertain data**, and on **data lakes / heterogeneous sources**.
- LLM- and embedding-assisted CFD pattern discovery for semantic context *(frontier — verify)*.
- Active: Vreeken/Boley (information-theoretic dependencies), Naumann/HPI (scalable profiling), Fan (CFDs and cleaning).

## 8. Future Work

- A principled, scalable FDR-controlled AFD/CFD discovery framework.
- Tight sample-complexity bounds tying VC-dimension of dependency classes to discovery reliability.
- End-to-end integration with repair/cleaning that closes the loop discovery → repair → re-discovery.

## 9. Key References

- **[Foundational]** W. Fan, F. Geerts, J. Li, M. Xiong. *Discovering Conditional Functional Dependencies.* IEEE TKDE, 2011 (ICDE 2009). — [DOI](https://doi.org/10.1109/TKDE.2010.154)
- **[SOTA]** S. Kruse, F. Naumann. *Efficient Discovery of Approximate Dependencies (Pyro).* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3192965.3192968)
- **[SOTA]** P. Mandros, M. Boley, J. Vreeken. *Discovering Reliable Approximate Functional Dependencies.* ACM SIGKDD, 2017. — [DOI](https://doi.org/10.1145/3097983.3098062), [arXiv](https://arxiv.org/abs/1705.09391)
- **[Foundational]** Y. Huhtala, J. Kärkkäinen, P. Porkka, H. Toivonen. *TANE: Discovering Functional and Approximate Dependencies.* The Computer Journal, 1999. — [DOI](https://doi.org/10.1093/comjnl/42.2.100), [DBLP](https://dblp.org/rec/journals/cj/HuhtalaKPT99.html)
- **[Survey]** Z. Abedjan, L. Golab, F. Naumann. *Profiling Relational Data: A Survey.* The VLDB Journal, 2015. — [DOI](https://doi.org/10.1007/s00778-015-0389-y)

## 10. Worked Example

Consider a 5-tuple relation `Customer(zip, city, country)`:

| # | zip | city | country |
|---|------|-----------|---------|
| 1 | E1 | London | UK |
| 2 | E1 | London | UK |
| 3 | E1 | Reading | UK |
| 4 | 10001| New York | US |
| 5 | 10001| New York | US |

**AFD via $g_3$.** Test $\text{zip} \to \text{city}$. The partition by `zip` is $\{\{1,2,3\},\{4,5\}\}$. The first block disagrees on `city` (London vs Reading), so the largest consistent subset keeps either the two London rows or the one Reading row from that block — keep $\{1,2\}$, drop tuple 3 — plus both of $\{4,5\}$. Maximal consistent subset size $=4$, so $g_3 = 1 - \frac{4}{5} = 0.2$. At threshold $\varepsilon = 0.25$ the AFD $\text{zip}\to\text{city}$ holds approximately.

**CFD.** The tableau row $[\text{country}=\text{UK}]:\ \text{zip}\to\text{city}$ has support $=\frac{3}{5}$ (tuples 1–3 match `UK`) but confidence $=\frac{2}{3}$ (tuple 3 violates). Restricting further to $[\text{country}=\text{US}]$ gives support $\frac{2}{5}$, confidence $1.0$ — an exact context-specific CFD that plain FD discovery would miss because the global FD fails.

---
*Part of the [DBMS Research catalog](../../README.md).*
