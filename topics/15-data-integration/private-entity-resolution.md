---
id: 15-data-integration/private-entity-resolution
title: "Entity Resolution Under Differential Privacy"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Entity Resolution Under Differential Privacy

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/private-entity-resolution` · **Status:** open

## 1. Problem Statement

Two (or more) parties hold record sets $A$ and $B$ describing overlapping real-world entities (e.g., patients, customers). **Privacy-preserving record linkage (PPRL)** / **private entity resolution (ER)** computes the matching $M \subseteq A \times B$ — or an aggregate over it — **without revealing non-matching records' attributes** to the other party or to an analyst. The problem here is to perform linkage under a **formal differential-privacy (DP)** guarantee on the *released output* (the match set, a join, or a downstream statistic), while **bounding the loss in linkage accuracy** (precision/recall or F-measure) caused by the privacy noise.

Formally: design a (possibly multiparty / secure-computation) mechanism $\mathcal{A}$ such that (1) $\mathcal{A}$ is $(\varepsilon, \delta)$-DP with respect to neighboring inputs (one record added/removed/changed), and (2) the expected linkage error $\mathbb{E}[\,F_1(\hat M) - F_1(M^\star)\,]$ is bounded by a function of $\varepsilon, \delta$, the blocking quality, and the matcher's margin.

Variants: **decision/output** (release the match set under DP), **counting** (release $|M|$ or a private *join size* / private SQL aggregate over the linked relation), **secure-computation** flavor (MPC for correctness + DP for output leakage), and the **accuracy–privacy tradeoff** optimization (minimize error at fixed $\varepsilon$).

## 2. Mathematical Foundations

**Differential privacy** (Dwork–McSherry–Nissim–Smith, TCC 2006): $\mathcal{A}$ is $\varepsilon$-DP if for neighboring $D \sim D'$ and all $S$, $\Pr[\mathcal{A}(D) \in S] \le e^{\varepsilon}\Pr[\mathcal{A}(D') \in S]$. The Laplace/Gaussian mechanisms calibrate noise to **global sensitivity** $\Delta f$. ER's difficulty: the output (a *set of pairs*) has **high sensitivity** — one record can join many others, so naive matchings have unbounded sensitivity. This forces **Lipschitz extensions / restricted sensitivity** (Blocki–Blum–Datta–Sheffet) and **stability-based** releases, or **truncation** of degree (bounded-degree joins).

ER itself is a **clustering over the transitive closure** of a learned/declared similarity $\mathrm{sim}(a,b)$; correctness is measured against a Fellegi–Sunter probabilistic model. Combining with DP invokes **private set intersection (PSI)** and **secure multiparty computation** for the *computation* leakage and DP for the *output* leakage — two distinct guarantees that must be composed (sequential/advanced composition; Rényi-DP accounting). **Private join-size estimation** rests on results that DP join queries have sensitivity governed by maximum row multiplicity / **truncation** (Kotsogiannis et al.; Dong–Yi on DP for joins).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** **Restricted/Lipschitz-sensitivity** frameworks for graph- and join-like outputs (Blocki et al., ITCS 2013; Kasiviswanathan et al.). **DP for SQL joins** with truncation and residual sensitivity (Dong, Fang, Yi, PODS/SIGMOD 2021–2022) bounds private *join-size* error — the closest rigorous handle on linked-relation analytics.
- **Systems-SOTA.** PPRL via **Bloom-filter encodings** (Schnell–Bachteler–Reiher) and **secure MPC linkage** are deployed in health/census settings, but these protect *computation* leakage, not output DP. Systems giving end-to-end **DP-on-output** linkage are largely prototypes; private record-linkage with DP guarantees remains pre-deployment.

## 4. Upper Bound

For **private join/linked-aggregate queries**, truncation-based mechanisms achieve error $\tilde{O}(\Delta_{\mathrm{trunc}}/\varepsilon)$ where $\Delta_{\mathrm{trunc}}$ is the (chosen) maximum join degree — near-optimal for self-join-free joins (Dong–Yi). For **releasing a private matching** as a graph object, Lipschitz-extension mechanisms give utility scaling with the restricted sensitivity, polynomial-time for bounded-degree matchings. PSI + DP composition yields an $(\varepsilon,\delta)$ end-to-end protocol with communication polynomial in $|A|+|B|$. Model: $(\varepsilon,\delta)$-DP, computational DP under MPC, RAM/communication complexity.

## 5. Lower Bound

DP imposes an **information-theoretic accuracy floor**: releasing degree-sensitive join outputs incurs error $\Omega(1/\varepsilon)$ per high-degree entity, and for general (many-to-many) joins the error is **unbounded without truncation** — a genuine impossibility, since one record's removal can change the match set by $\Theta(n)$ pairs (sensitivity $\Theta(n)$). Lower bounds via **packing/fingerprinting** arguments (Bun–Ullman–Vadhan) show $\Omega(\sqrt{d}/\varepsilon)$-type error for releasing many correlated linkage statistics. In the MPC setting, **PSI lower bounds** give $\Omega(n)$ communication. Model: information-theoretic DP lower bounds, communication complexity, fingerprinting codes.

## 6. The Gap

**Genuinely open.** The relational structure of ER (many-to-many, transitive-closure clustering) gives the released object inherently **high sensitivity**, so strong DP either (a) requires aggressive truncation that *discards true matches* (recall loss) or (b) admits only aggregate releases, not the match set itself. There is **no tight theory of the privacy–accuracy frontier for the matching object** — only for join-size aggregates. The gap between the $\Theta(n)$ worst-case sensitivity and the much smaller *typical-case* sensitivity (under blocking, bounded duplication) is unquantified, and instance-/smooth-sensitivity or per-entity DP that exploits it is undeveloped. Closing it needs an accuracy–privacy dichotomy parameterized by blocking degree and match margin.

## 7. Current Research (as of June 2026)

Active directions: **per-entity / individualized DP** and **smooth sensitivity** for linkage exploiting realistic bounded duplication; combining **MPC + output-DP** with tight Rényi accounting. *(frontier — verify)* **Label-DP and propose-test-release** matchers that release confident matches and suppress ambiguous ones to bound sensitivity. *(frontier — verify)* DP-aware **blocking** that itself satisfies DP, and private linkage feeding **DP synthetic data** for downstream analytics. Groups: Machanavajjhala (Duke), Dwork (Harvard), Yi/Dong (HKUST), Kasiviswanathan, Vilhuber/Abowd (census/LEHD lineage), Christen (ANU, PPRL).

## 8. Future Work

- A tight **privacy–accuracy frontier** for releasing the matching object, not just aggregates.
- **Instance-optimal** mechanisms using smooth/per-entity sensitivity under blocking.
- End-to-end **MPC + output-DP** systems with audited composition for health/census linkage.
- Private ER feeding **DP synthetic linked datasets** with provable utility for joins.

## 9. Key References

- **[Foundational]** C. Dwork, F. McSherry, K. Nissim, A. Smith. *Calibrating noise to sensitivity in private data analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** C. Dwork, A. Roth. *The algorithmic foundations of differential privacy.* Found. & Trends in TCS, 2014. — [DOI](https://doi.org/10.1561/0400000042)
- **[SOTA]** W. Dong, K. Yi. *Residual sensitivity for differentially private multi-way joins.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452813)
- **[SOTA]** J. Blocki, A. Blum, A. Datta, O. Sheffet. *Differentially private data analysis of social networks via restricted sensitivity.* ITCS, 2013. — [arXiv](https://arxiv.org/abs/1208.4586)
- **[Survey]** P. Christen, T. Ranbaduge, R. Schnell. *Linking Sensitive Data: Methods and Techniques for Privacy-Preserving Record Linkage.* Springer, 2020. — [DOI](https://doi.org/10.1007/978-3-030-59706-1)
- **[Foundational]** I. Fellegi, A. Sunter. *A theory for record linkage.* Journal of the American Statistical Association, 1969. — [DOI](https://doi.org/10.1080/01621459.1969.10501049)

## 10. Worked Example

Party A has $A=\{a_1,\dots,a_5\}$; party B has one "hub" record $b_1$ that, under the similarity threshold, matches **all** of A (e.g. a generic placeholder name). The true match set is $M=\{(a_i,b_1)\}_{i=1}^5$, so $|M|=5$.

**Sensitivity blowup.** Remove $b_1$ (one neighboring change): the released match set drops from 5 pairs to 0. So the global sensitivity of "number of matched pairs" is $\Delta f = 5$, and in general one record can change the count by $\Theta(n)$. To be $\varepsilon$-DP, the Laplace mechanism must add noise $\mathrm{Lap}(\Delta f/\varepsilon)$; at $\varepsilon=1$ that is $\mathrm{Lap}(5)$ — std. dev. $5\sqrt{2}\approx 7.07$, swamping the true count of 5.

**Truncation fix.** Cap each B-record's degree at $\tau=1$. Now $\Delta f = 1$, noise is $\mathrm{Lap}(1)$, but four of the five true matches are *discarded* — recall falls to $1/5$. This is the Section-6 frontier in miniature: strong DP forces either unbounded noise ($\Omega(n/\varepsilon)$) or aggressive truncation that destroys recall.

---
*Part of the [DBMS Research catalog](../../README.md).*
