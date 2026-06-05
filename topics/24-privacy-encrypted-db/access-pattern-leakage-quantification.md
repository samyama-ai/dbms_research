# Access-Pattern Leakage Quantification

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/access-pattern-leakage-quantification` · **Status:** open
> **Verification note:** The Kornaropoulos–Papamanthou–Tamassia S&P 2020 paper is titled *"The State of the Uniform: Attacks on Encrypted Databases Beyond the Uniform Query Distribution"* (corrected in §9).

## 1. Problem Statement
Given an encrypted-database scheme that reveals *access patterns* (which encrypted records each query touches), plus auxiliary side channels (result **volume**, query **co-occurrence**, **search/insert timing**), build a **general framework** that (i) formally specifies what a sequence of observed access patterns reveals about the underlying data and the issued queries, and (ii) gives **tight, composable bounds** relating an adversary's reconstruction success to the scheme's leakage profile and any auxiliary distribution.

Variants:
- **Reconstruction (counting/optimization):** from observations, recover the plaintext values/order or the query values; measure error or fraction recovered.
- **Decision:** distinguish two databases/query-workloads given their leakage (the indistinguishability/security-game form).
- **Quantitative bound:** upper-bound mutual information / advantage as a function of #queries $q$, domain size $N$, and auxiliary knowledge.

## 2. Mathematical Foundations
Leakage is formalized via a **leakage function** $\mathcal{L}(\mathrm{DB},\mathrm{queries})$; security says there is a simulator $\mathcal{S}$ such that the real view $\approx_c \mathcal{S}(\mathcal{L})$ (Curtmola–Garay–Kamara–Ostrovsky, CCS'06). Attacks lower-bound how much $\mathcal{L}$ leaks.

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
- **[Foundational]** R. Curtmola, J. Garay, S. Kamara, R. Ostrovsky. *Searchable Symmetric Encryption: Improved Definitions and Efficient Constructions.* CCS, 2006. — [DOI](https://doi.org/10.1145/1180405.1180417) · [DBLP](https://dblp.org/rec/conf/ccs/CurtmolaGKO06.html)
- **[Foundational]** G. Kellaris, G. Kollios, K. Nissim, A. O'Neill. *Generic Attacks on Secure Outsourced Databases.* CCS, 2016. — [DOI](https://doi.org/10.1145/2976749.2978386) · [DBLP](https://dblp.org/rec/conf/ccs/KellarisKNO16.html)
- **[SOTA]** M-S. Lacharité, B. Minaud, K. Paterson. *Improved Reconstruction Attacks on Encrypted Data Using Range Query Leakage.* IEEE S&P, 2018. — [DBLP](https://dblp.org/rec/conf/sp/LachariteMP18.html) · [ePrint](https://eprint.iacr.org/2017/701)
- **[SOTA]** P. Grubbs, M-S. Lacharité, B. Minaud, K. Paterson. *Pump up the Volume: Practical Database Reconstruction from Volume Leakage on Range Queries.* CCS, 2018. — [ePrint](https://eprint.iacr.org/2018/965) · [DBLP search](https://dblp.org/search?q=Pump+up+the+Volume+Practical+Database+Reconstruction)
- **[SOTA]** E. M. Kornaropoulos, C. Papamanthou, R. Tamassia. *The State of the Uniform: Attacks on Encrypted Databases Beyond the Uniform Query Distribution.* IEEE S&P, 2020. — [IEEE](https://ieeexplore.ieee.org/document/9152784) · [PDF](https://obj.umiacs.umd.edu/papers_for_stories/Kornaropoulos_paper.pdf)
- **[Survey]** D. Cash, P. Grubbs, J. Perry, T. Ristenpart. *Leakage-Abuse Attacks Against Searchable Encryption.* CCS, 2015. — [DOI](https://doi.org/10.1145/2810103.2813700) · [DBLP](https://dblp.org/rec/conf/ccs/CashGPR15.html)
- **[Survey]** S. Kamara, A. Kati, T. Moataz, T. Schneider, A. Treiber, M. Yonli. *SoK: Cryptanalysis of Encrypted Search with LEAKER — A framework for LEakage AttacK Evaluation on Real-world data.* IEEE EuroS&P, 2022. — [ePrint](https://eprint.iacr.org/2021/1035)

## 10. Worked Example

**Order reconstruction from access-pattern co-occurrence.** Take a domain of $N=4$ values $\{1,2,3,4\}$ with one record per value, stored encrypted. The server cannot read values but sees *which encrypted records each range query touches*. Suppose the adversary observes these access-pattern sets for four range queries:

- $q_a \to \{r_2,r_3\}$, $\quad q_b \to \{r_1,r_2,r_3\}$, $\quad q_c \to \{r_3,r_4\}$, $\quad q_d \to \{r_2,r_3,r_4\}$.

Each range query returns a *contiguous* interval of values, so each observed set must be consecutive in the true order. Treating records as nodes and "appears together in a query" as constraints, the only linear arrangement consistent with all four sets (up to reflection) is $r_1\,r_2\,r_3\,r_4$: $q_a,q_c$ force $r_2,r_3$ and $r_3,r_4$ adjacent; $q_b,q_d$ pin the endpoints. The adversary thus recovers the full value *order* — value$(r_1)<\dots<$value$(r_4)$ — with zero plaintext access. This is exactly the PQ-tree/interval-order recovery of KKNO; for dense data it needs $\Theta(N\log N)$ random range queries to see enough co-occurrences (here $N=4$ took 4 well-chosen queries).

---
*Part of the [DBMS Research catalog](../../README.md).*
