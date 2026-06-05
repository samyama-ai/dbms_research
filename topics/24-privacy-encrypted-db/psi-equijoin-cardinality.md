# Practical Private Set Intersection Joins

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/psi-equijoin-cardinality` · **Status:** partially-solved

## 1. Problem Statement
Two (or more) mutually distrustful parties hold relations $A$ and $B$ and wish to compute a function over their **equi-join** $A \bowtie_{a=b} B$ — typically the **intersection cardinality** $|A \cap B|$ or an aggregate $\sum_{r \in A\cap B} v(r)$ (e.g., SUM of an associated payload) — *without* revealing the intersecting keys, the non-intersecting elements, or the per-row join witnesses to either party. The canonical industrial instance is **PSI-Sum / private join-and-compute**: measure conversion lift across two datasets keyed on a common identifier while leaking only the final aggregate.

Variants:
- **PSI-cardinality (counting):** output only $|A \cap B|$.
- **PSI-Sum / circuit-PSI (aggregation):** output $f$ over intersecting payloads; reveal nothing about which rows matched.
- **Decision/threshold:** reveal only whether $|A \cap B| \ge \tau$.
- **Unbalanced** ($|A| \gg |B|$) and **multi-key / band** joins as harder generalizations.

The "practical" qualifier demands near-linear communication and concrete throughput on $n \sim 10^8$ records.

## 2. Mathematical Foundations
Security is in the **real/ideal simulation paradigm**: a protocol $\Pi$ securely realizes ideal functionality $\mathcal{F}$ against a semi-honest (or malicious) adversary $\mathcal{A}$ if there exists a simulator $\mathcal{S}$ such that $\mathrm{REAL}_{\Pi,\mathcal{A}}(x,y) \approx_c \mathrm{IDEAL}_{\mathcal{F},\mathcal{S}}(x,y)$. PSI functionalities are defined so the ideal output is *exactly* the cardinality/aggregate, formalizing "reveal nothing else."

Core primitives: **Oblivious Pseudorandom Functions (OPRF)** $F_k(\cdot)$ — the receiver learns $F_k(x_i)$ without learning $k$; the sender learns nothing. Intersection becomes equality of OPRF outputs in a common domain. **Diffie–Hellman PSI** uses the commutative blinding $H(x)^{k_1 k_2}$. Modern fast PSI uses **OT extension** (IKNP/SilentOT) and **Vector-OLE / Oblivious Key-Value Stores (OKVS)** to encode sets in $O(n)$ space. Cardinality/sum add a **secret-sharing or additively-homomorphic layer** (Paillier / threshold ElGamal) so payloads aggregate under encryption. Circuit-PSI feeds shared intersection bits into a generic 2PC (GMW/garbled circuits) evaluating $f$.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Google's **Private Join and Compute** (DH-based OPRF + Paillier, open-sourced 2019) is the deployed reference for PSI-Sum. **Meta/PCI** and the **DPCA / Private Lift** stacks run circuit-PSI at ad scale.
- **Protocol-SOTA:** **KKRT16** (Kolesnikov–Kumaresan–Rosulek–Trieu, CCS'16) OT-based PSI; **Pinkas–Schneider–Tkachenko–Zohner / "SpOT-light"** and **PaXoS/OKVS** lines (EUROCRYPT'19–'20); **Chase–Miao** (CRYPTO'20) lightweight OKVS-PSI; **Rindal–Schoppmann "VOLE-PSI"** (EUROCRYPT'21) — malicious-secure, near-linear; **RS3PSI / circuit-PSI** (Rindal–Schoppmann, Pinkas et al.) for cardinality and arbitrary aggregates.
- **Unbalanced/FHE:** **Chen–Laine–Rindal** (CCS'17/'18) labeled-PSI via leveled FHE for $|B|$ small, $|A|$ huge.

## 4. Upper Bound
VOLE-/OKVS-based PSI achieves $O((|A|+|B|)\lambda)$ communication and $O((|A|+|B|))$ symmetric-crypto work in the **semi-honest and malicious 2PC models** (Rindal–Schoppmann 2021), with concrete rates of tens of millions of items in seconds on a LAN. PSI-cardinality/PSI-Sum add an $O(n)$ additively-homomorphic or shared-aggregation pass; circuit-PSI adds $O(n \cdot |C|)$ for the aggregation circuit $C$ but keeps the *intersection* step near-linear. Labeled FHE-PSI achieves communication sublinear in $|A|$ for the unbalanced regime.

## 5. Lower Bound
- **Communication:** any secure PSI must transmit $\Omega(n)$ bits (the intersection can encode $\Theta(n)$ bits of information); cardinality alone is cheaper in *output* but still $\Omega(n)$ in *protocol* communication for hiding individual membership (Freedman–Nissim–Pinkas reductions).
- **OT lower bound:** OT-based constructions inherit the impossibility of OT from one-way functions alone — PSI with full security requires public-key assumptions or correlated randomness setup (Impagliazzo–Rudich black-box separation).
- **Malicious overhead:** achieving malicious security generically costs a constant factor but cannot be free; selective-failure leakage forces consistency checks.

## 6. The Gap
The *semi-honest, single-key, two-party* case is essentially **solved** — near-linear and concretely fast. Genuinely open: (i) **malicious-secure circuit-PSI** for rich aggregates at the same throughput as semi-honest PSI; (ii) **multiparty** PSI-cardinality scaling beyond ~16 parties; (iii) **multi-key / inequality (band) join** predicates, where reductions to equality blow up communication; (iv) composing PSI-Sum with **differential privacy** on the output so even the aggregate is protected. The gap is "constant-factor and feature-completeness," not asymptotic — hence *partially-solved*.

## 7. Current Research (as of June 2026)
Active lines: OKVS constructions with smaller expansion (Bienstock–Patel–Seo–Yeo, RB-OKVS) pushing concrete rates; **differentially-private PSI-cardinality** to defeat repeated-query inference; GPU/SIMD VOLE-PSI for billion-scale joins *(frontier — verify)*. Groups: Rosulek/Trieu (Oregon State), Rindal (Visa Research), Pinkas/Schneider (Bar-Ilan/TU Darmstadt), Boneh/Corrigan-Gibbs (Stanford/MIT) on the aggregation side, and Google/Meta production teams. Integration of PSI joins into **encrypted query engines** (as a join operator under a leakage budget) is an emerging systems direction *(frontier — verify)*.

## 8. Future Work
- Malicious circuit-PSI at semi-honest throughput; standardized, auditable PSI-Sum libraries.
- Private *band/range* and multi-attribute joins without quadratic blowup.
- DP-composed PSI so iterated measurement does not leak the intersection.
- $k$-party PSI-cardinality with sublinear-in-$k$ round complexity.
- Hardware (TEE + PSI hybrid) acceleration with formal leakage accounting.

## 9. Key References
- **[Foundational]** Freedman, Nissim, Pinkas. *Efficient Private Matching and Set Intersection.* EUROCRYPT, 2004.
- **[Foundational]** Kolesnikov, Kumaresan, Rosulek, Trieu. *Efficient Batched Oblivious PRF with Applications to Private Set Intersection.* CCS, 2016.
- **[SOTA]** Rindal, Schoppmann. *VOLE-PSI: Fast OPRF and Circuit-PSI from Vector-OLE.* EUROCRYPT, 2021.
- **[SOTA]** Chen, Laine, Rindal. *Fast Private Set Intersection from Homomorphic Encryption.* CCS, 2017.
- **[SOTA]** Ion, Kreuter, et al. *On Deploying Secure Computing: Private Intersection-Sum-with-Cardinality.* IEEE EuroS&P, 2020 (Google Private Join and Compute).
- **[Survey]** Pinkas, Schneider, Zohner. *Scalable Private Set Intersection Based on OT Extension.* ACM TOPS, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
