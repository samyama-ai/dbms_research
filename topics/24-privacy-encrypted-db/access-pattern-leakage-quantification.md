# Access-Pattern Leakage Quantification

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/access-pattern-leakage-quantification` · **Status:** open

## 1. Problem Statement
Given an encrypted-database scheme that reveals *access patterns* (which encrypted records each query touches), plus auxiliary side channels (result **volume**, query **co-occurrence**, **search/insert timing**), build a **general framework** that (i) formally specifies what a sequence of observed access patterns reveals about the underlying data and the issued queries, and (ii) gives **tight, composable bounds** relating an adversary's reconstruction success to the scheme's leakage profile and any auxiliary distribution.

Variants:
- **Reconstruction (counting/optimization):** from observations, recover the plaintext values/order or the query values; measure error or fraction recovered.
- **Decision:** distinguish two databases/query-workloads given their leakage (the indistinguishability/security-game form).
- **Quantitative bound:** upper-bound mutual information / advantage as a function of #queries $q$, domain size $N$, and auxiliary knowledge.

## 2. Mathematical Foundations
Leakage is formalized via a **leakage function** $\mathcal{L}(\mathrm{DB},\mathrm{queries})$; security says there is a simulator $\mathcal{S}$ such that the real view $\approx_c \mathcal{S}(\mathcal{L})$ (Curtmola–Garcia–Kamara–Roxana, CCS'06). Attacks lower-bound how much $\mathcal{L}$ leaks.

Range-query reconstruction reduces to combinatorial/geometric recovery: from access-pattern co-occurrence one recovers a **PQ-tree / interval order** of values (Kellaris–Kollios–Nissim–O'Neill, CCS'16) — sample complexity $\Theta(N^2\log N)$ queries, improved to $\Theta(N\log N)$ for dense/uniform variants (Lacharité–Minaud–Paterson, S&P'18; Grubbs et al.). **Volume leakage** alone enables reconstruction (Grubbs–Lacharité–Minaud–Paterson, CCS'18; Kornaropoulos–Papamanthou–Tamassia, "data-recovery via search-pattern", S&P'20). Tools: **VC dimension** / sample complexity for learning the value order, **information theory** ($I(\mathrm{queries};\mathrm{view})$), **statistical distance**, and **differential privacy** as a *defense* metric (Chen–Kamara, etc.). Quantitative information flow (min-entropy leakage, $g$-leakage of Alvim–Chatzikokolakis–Smith) provides an adversary-parameterized measure.

## 3. State of the Art (SOTA)
- **Attack-SOTA:** KKNO (CCS'16) full reconstruction from access patterns; Lacharité–Minaud–Paterson (S&P'18) approximate/scale reconstruction; Grubbs et al. *Pump up the Volume* (CCS'18) volume-only attacks; Kornaropoulos et al. (S&P'19/'20) search-pattern and "state-of-the-uncertainty" attacks generalizing to unknown distributions; Gui–Paterson et al. range attacks.
- **Framework-SOTA:** *LEAKER* (Kamara et al., a leakage-attack evaluation framework) and abstract leakage hierarchies (Cash–Grubbs–Perry–Ristenpart, CCS'15). No single accepted *quantitative calculus* yet covers volume+access+search+timing jointly.

## 4. Upper Bound
For **defenses**, schemes bound leakage: ORAM hides access pattern entirely ($O(\log n)$ overhead, §oblivious-operators); volume-hiding multimaps bound volume leakage; differentially private access patterns bound advantage to $\le e^{\epsilon}$. As a *quantification* upper bound, mutual-information arguments cap reconstruction: with $q$ uniform range queries on domain $N$, order recovery needs $\Omega(N\log N)$ samples, so $<N\log N$ queries information-theoretically bound recovery probability. These are **distribution-conditional** upper bounds, not a universal framework.

## 5. Lower Bound
- **Attack lower bounds (impossibility of hiding):** Access-pattern + auxiliary distribution suffices for $\Theta(N^2\log N)$- (general) or $\Theta(N\log N)$- (uniform) query full reconstruction — i.e., any scheme revealing access pattern *cannot* protect order at scale.
- **No-free-lunch / "leakage is inherent":** Kamara–Moataz–Ohrimenko and follow-ups show structural leakage is necessary for sub-linear search (a search index that is fully leakage-free degrades to ORAM/linear scan).
- **Information-theoretic:** volume sequence has min-entropy lower bounds that any volume-hiding scheme must pad away, giving $\Omega(\text{quadratic})$ naive cost.

## 6. The Gap
There is **no agreed, composable quantitative framework** mapping an arbitrary leakage profile to a tight adversarial-advantage bound under arbitrary auxiliary distributions. Existing results are attack-specific and assume known/uniform priors; bounds for *correlated multi-attribute*, *adaptive*, and *partially-known-distribution* settings are loose or missing. Closing it means a leakage *calculus* with matching attack lower bounds and defense upper bounds per leakage primitive, that composes across a query pipeline.

## 7. Current Research (as of June 2026)
Directions: (a) distribution-agnostic / "*uncertainty-aware*" attacks (Kornaropoulos, Falzon) that drop the known-prior assumption *(frontier — verify)*; (b) leakage-abuse against **multi-attribute** and **join** indexes, and against ML-augmented encrypted search *(frontier — verify)*; (c) DP-style formal leakage accounting and "leakage budgets" composed over workloads; (d) automated leakage-attack tooling (LEAKER lineage). Groups: Royal Holloway (Paterson/Minaud), Brown/MongoDB (Kamara/Moataz), George Mason (Kornaropoulos), Cornell Tech (Ristenpart/Grubbs), UCL.

## 8. Future Work
- A unified information-theoretic / QIF calculus covering access + volume + search-pattern + timing with composition theorems.
- Tight reconstruction bounds under unknown, correlated, and adaptive query priors.
- Principled "leakage budgets" usable by query optimizers to choose plans under a privacy constraint.
- Standardized benchmarks tying leakage profiles to concrete attack success for deployed systems (CryptDB-style, MongoDB Queryable Encryption).

## 9. Key References
- **[Foundational]** R. Curtmola, J. Garay, S. Kamara, R. Ostrovsky. *Searchable Symmetric Encryption: Improved Definitions and Efficient Constructions.* CCS, 2006.
- **[Foundational]** G. Kellaris, G. Kollios, K. Nissim, A. O'Neill. *Generic Attacks on Secure Outsourced Databases.* CCS, 2016.
- **[SOTA]** M-S. Lacharité, B. Minaud, K. Paterson. *Improved Reconstruction Attacks on Encrypted Data Using Range Query Leakage.* IEEE S&P, 2018.
- **[SOTA]** P. Grubbs, M-S. Lacharité, B. Minaud, K. Paterson. *Pump up the Volume: Practical Database Reconstruction from Volume Leakage on Range Queries.* CCS, 2018.
- **[SOTA]** E. M. Kornaropoulos, C. Papamanthou, R. Tamassia. *The State of the Uncertainty: ... Reconstruction Attacks without Knowing the Distribution.* IEEE S&P, 2020.
- **[Survey]** D. Cash, P. Grubbs, J. Perry, T. Ristenpart. *Leakage-Abuse Attacks Against Searchable Encryption.* CCS, 2015.
- **[Survey]** S. Kamara, T. Moataz. *Leakage and the abstraction of structured encryption* (and the LEAKER framework, USENIX Security 2022).

---
*Part of the [DBMS Research catalog](../../README.md).*
