# Privacy-Preserving Record Linkage

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/privacy-preserving-linkage` · **Status:** partially-solved

## 1. Problem Statement

Privacy-Preserving Record Linkage (PPRL) lets two or more parties identify records referring to the same entity **across their datasets without revealing the non-matching records' identifying values** to each other (or to a third party). The challenge is approximate matching (typos, formatting) under cryptographic/statistical privacy, **at scale** (billions of comparisons) and **at accuracy** comparable to clear-text linkage.

Variants:
- **Two-party vs. multi-party** (with or without a semi-trusted linkage unit).
- **Exact vs. approximate (fuzzy)** linkage — the latter is the technically hard case.
- **Security model:** semi-honest (honest-but-curious) vs. malicious adversaries.
- **Output granularity:** reveal only match/non-match labels, or also linked attributes for matched pairs.
- **Decision/optimization:** maximize linkage F1 subject to a formal privacy budget (e.g., $\epsilon$-DP) and a communication/time budget.

## 2. Mathematical Foundations

PPRL composes **approximate string matching** with **secure computation / privacy mechanisms**:

- **Bloom-filter encoding (BFE):** map $q$-grams of a field into a length-$m$ bit array via $k$ hashes; matched records have high **Dice/Jaccard** overlap of bit arrays. This trades a tunable privacy/utility profile but is vulnerable to frequency cryptanalysis.
- **Secure multiparty computation (SMC):** garbled circuits / secret sharing compute similarity without revealing inputs; security relies on standard simulation-based definitions (real/ideal indistinguishability).
- **Private set intersection (PSI):** for exact join keys, oblivious-transfer or homomorphic PSI gives provable security; **fuzzy PSI** extends to thresholded similarity.
- **Differential privacy:** add calibrated noise so released linkage statistics satisfy $\Pr[\mathcal M(D)\in S]\le e^{\epsilon}\Pr[\mathcal M(D')\in S]+\delta$. DP composes (basic/advanced composition, RDP) across queries.

The core tension is information-theoretic: any output correlated with true matches *leaks*, formalized via the **privacy–utility trade-off** and channel capacity arguments.

## 3. State of the Art (SOTA)

- **Bloom-filter PPRL** (Schnell, Bachteler, Reiher, 2009) remains the practical workhorse; hardened variants (salted/record-level BF, BLIP, **tabulation/min-hash + LSH blocking**) address cryptanalysis.
- **Cryptanalysis & defenses:** Christen, Vatsalan, Ranbaduge (2017–2020) demonstrated attacks on BFE and proposed countermeasures — defining the security frontier.
- **SMC/HE-based PPRL** and **fuzzy PSI** (e.g., Chen–Laine–Rindal HE-PSI lineage, 2017–2021; fuzzy/threshold PSI 2021–2024) give cryptographic guarantees at higher cost.
- **DP linkage** combining linkage with $\epsilon$-DP release (2020s).
- Surveys: Vatsalan, Christen, Verykios (Information Systems 2013); Gkoulalas-Divanis et al. (2021).

## 4. Upper Bound

Blocking + BFE achieves near clear-text F1 with **subquadratic** comparison cost: LSH/MinHash blocking gives candidate generation in $O(n^{1+\rho})$, and per-pair Dice comparison is $O(m)$ bits. Cryptographic PPRL via PSI/SMC achieves provable semi-honest security with communication/computation roughly **linear-to-quasilinear in input size** for modern PSI (e.g., OT-extension PSI is $O(n)$ symmetric-key ops; HE-PSI trades computation for low communication). Threshold/fuzzy PSI protocols give security at polynomial overhead. Thus *both* scale and security are individually attainable; the upper-bound frontier is achieving all three (security, scale, fuzzy accuracy) at once.

## 5. Lower Bound

- **Communication complexity:** any secure two-party protocol computing a non-trivial linkage predicate inherits $\Omega(n)$ (often $\Omega(n\log n)$) communication lower bounds from set-intersection/disjointness-style arguments; PSI has matching near-linear bounds.
- **Privacy impossibility:** Dwork–Naor / Dinur–Nissim style results show that answering too many accurate linkage queries enables **reconstruction**, forcing noise — a hard accuracy ceiling under DP. Exact, leak-free, perfectly-accurate fuzzy linkage is information-theoretically impossible: any useful output leaks some bits about non-matches.
- **Cryptanalytic hardness:** efficient (non-SMC) encodings like BFE provably cannot match the security of SMC — frequency information is recoverable in principle (demonstrated attacks).

## 6. The Gap

Status is **partially-solved**: there is a well-characterized **Pareto frontier** among {provable security, scalability, fuzzy accuracy}. Cryptographically-secure protocols (PSI/SMC) are accurate and secure but expensive at billion-record scale; cheap Bloom-filter methods scale and are accurate but offer only heuristic, attackable privacy; DP methods give formal privacy but degrade accuracy. The genuinely open part is a method that is simultaneously **cryptographically secure, billion-scale, and fuzzy-accurate** with formal guarantees — and a clean theory unifying SMC-style and DP-style guarantees for *approximate* matching.

## 7. Current Research (as of June 2026)

- **Fuzzy/threshold PSI** with practical performance and malicious security *(frontier — verify)*.
- **Hardware-enclave (TEE) linkage** (SGX/TDX) as a pragmatic middle ground, with side-channel caveats.
- **DP-blocking** and end-to-end $\epsilon$-DP linkage pipelines; **federated ER**.
- Encoding hardening against ML-based cryptanalysis; graph-based attacks and defenses.
- Groups: Christen, Vatsalan, Ranbaduge (ANU/Deakin), Schnell (Duisburg-Essen), Kuzu/Kantarcioglu (UT Dallas), HE-PSI lineage (Microsoft Research / Visa Research). National statistical agencies drive applied requirements *(frontier — verify)*.

## 8. Future Work

- Provably-secure, scalable fuzzy linkage with malicious-adversary guarantees.
- A unified privacy accounting across cryptographic leakage and statistical (DP) noise.
- Standard adversarial benchmarks for encoding cryptanalysis.
- Multi-party (n>2) scalable PPRL with composable privacy budgets.

## 9. Key References

- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006.
- **[Foundational]** Schnell, Bachteler, Reiher. *Privacy-Preserving Record Linkage Using Bloom Filters.* BMC Medical Informatics and Decision Making, 2009.
- **[Foundational]** Dinur, Nissim. *Revealing Information While Preserving Privacy.* PODS, 2003.
- **[SOTA]** Chen, Laine, Rindal. *Fast Private Set Intersection from Homomorphic Encryption.* ACM CCS, 2017.
- **[SOTA]** Christen, Ranbaduge, Vatsalan, et al. *Pattern-Mining Based Cryptanalysis of Bloom Filters for PPRL.* (PAKDD/IEEE), 2018.
- **[Survey]** Vatsalan, Christen, Verykios. *A Taxonomy of Privacy-Preserving Record Linkage Techniques.* Information Systems, 2013.
- **[Survey]** Gkoulalas-Divanis, Vatsalan, Karapiperis, Kantarcioglu. *Modern Privacy-Preserving Record Linkage Techniques: An Overview.* IEEE TIFS, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
