# Provable Bounds for Snapshot Encrypted DBs

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/snapshot-attack-bounds` · **Status:** open

## 1. Problem Statement
A **snapshot adversary** obtains a single dump of an encrypted database at one moment — the at-rest ciphertexts, indices, and metadata — but does *not* observe queries, access patterns, or update traffic (that is the persistent/access-pattern adversary). For columns protected by **property-preserving encryption (PPE)** — deterministic (DET, reveals equality) or order-preserving/order-revealing (OPE/ORE, reveals order) — characterize **tight bounds on how much plaintext an optimal snapshot adversary can reconstruct**, given auxiliary distributional knowledge.

Variants:
- **Counting/reconstruction:** how many cell values can be recovered exactly (or to within a bucket) as a function of $n$, domain size $N$, and column entropy?
- **Decision:** can the adversary recover *any* value above chance given auxiliary data $\mathcal{Z}$?
- **Approximate reconstruction:** error bound on inferred values (e.g., $\pm \epsilon N$).
- **Optimization (adversary side):** the best-possible attack; **(defender side):** the minimum leakage encryption achieving a target bound.

## 2. Mathematical Foundations
Model a column as a multiset $X = (x_1,\dots,x_n)$ over domain $[N]$ drawn from distribution $\mathcal{D}$. PPE reveals a relation: DET reveals the **equality partition** (a coloring); OPE/ORE reveals the **total order** (the rank vector) and, for "ideal" OPE, frequency too. The snapshot adversary sees $\phi(X)$ for leakage function $\phi$ plus auxiliary $\mathcal{Z}$ (a public reference distribution or an auxiliary dataset).

Reconstruction is **statistical inference**: the adversary computes the posterior $\Pr[X = x \mid \phi(X), \mathcal{Z}]$ and outputs the MAP assignment. For DET columns this is a **frequency-matching / assignment problem** — optimally a min-cost bipartite matching between observed equality classes (by frequency) and reference values (**Naveed–Kamara–Wright frequency analysis**, CCS'15). For ORE columns it is sorting + frequency matching. Tight bounds invoke: **distribution distance** ($\ell_1$/Kolmogorov between empirical and auxiliary), **VC-dimension/sample-complexity** style arguments for how much $\mathcal{Z}$ is needed, and **information-theoretic** mutual information $I(X; \phi(X), \mathcal{Z})$ upper-bounding recoverable bits. A clean general theorem — "snapshot leakage $\phi$ + auxiliary $\mathcal{Z}$ $\Rightarrow$ at most $g(\phi,\mathcal{Z},\mathcal{D})$ cells recoverable w.h.p." — is **not known**.

## 3. State of the Art (SOTA)
- **Attack-SOTA:** **Naveed–Kamara–Wright** (CCS'15) — frequency analysis and $\ell_p$-optimization snapshot attacks recovering most values in DET/OPE-encrypted medical columns; **Grubbs–Sekniqi–Bindschaedler–Naveed–Ristenpart** (S&P'17) — leakage-abuse and "binomial" attacks on OPE/ORE; **Durak–DuBuisson–Cash** (CCS'16) — inference from order leakage on 2-D/correlated data; **Bindschaedler et al.** snapshot attacks on encrypted columns.
- **Defense-SOTA:** **frequency-smoothing / frequency-hiding OPE** (Kerschbaum, CCS'15); **Lewi–Wu left/right ORE** (CCS'16) limiting order leakage to nearby elements; **Arx**, **CryptDB onion** demotion away from DET/OPE. These reduce leakage but lack *tight* reconstruction bounds.

## 4. Upper Bound
On the **defender** side, an upper bound on adversary success is what we want and largely lack. Known: with frequency-hiding OPE (Kerschbaum'15), the order leakage is randomized so exact-value recovery probability is bounded by the smoothing parameter — a *scheme-specific* bound, not general. Information-theoretically, no adversary recovers more than $I(X;\phi(X),\mathcal{Z})/H(\mathcal{D})$ fraction of entropy — an upper bound, but loose and rarely instantiated tightly. For DET on a *uniform high-entropy* column, equality leakage alone yields near-zero exact reconstruction without auxiliary frequency data — a positive (defender) bound in the **information-theoretic model**.

## 5. Lower Bound
On the **attack** (adversary-power) side: Naveed–Kamara–Wright (CCS'15) empirically recover a *constant fraction* (often $>50\%$) of cells in low-entropy DET/OPE columns with public auxiliary data — a strong reconstruction *lower bound* (the leakage *is* at least this harmful). Order leakage from OPE/ORE permits **full-order reconstruction**, and with dense domains, **$\epsilon$-approximate value recovery** for $\Theta(n)$ cells (Grubbs et al., S&P'17; sorting + density attacks). For correlated/2-D data, Durak et al. show order leakage compounds across columns. These are concrete/empirical lower bounds; matching *provable, distribution-parameterized* lower bounds (e.g., "for entropy-$H$ columns the adversary recovers $\ge c(H)\cdot n$") are **not established in general**.

## 6. The Gap
Genuinely **open**: there is a chasm between strong *empirical attacks* (lots of recovery) and weak, loose *information-theoretic upper bounds*. We have neither (i) a tight, distribution-parameterized formula for snapshot reconstruction as a function of $(\phi, \mathcal{D}, \mathcal{Z}, n, N)$, nor (ii) encryption schemes with *proven* reconstruction bounds matching an attacker's best case. Closing it requires a reconstruction-theory framework — analogous to the access-pattern reconstruction theory of Kellaris et al. but for the *snapshot/at-rest* setting — that pins the optimal adversary's success and yields schemes provably at that frontier.

## 7. Current Research (as of June 2026)
Directions: **reconstruction-theoretic snapshot bounds** parameterized by auxiliary-distribution distance and column entropy; **frequency-smoothing schemes with proven bounds** rather than heuristic smoothing; analysis of **ORE/OPE under correlated multi-column** snapshots; quantifying snapshot leakage of newer **encrypted-search / structured-encryption** indices at rest. Practical relevance is high given deployments like **MongoDB Queryable Encryption** and **CipherStash** that must argue about snapshot security *(frontier — verify)*. Groups: Kamara/Moataz (Brown/MongoDB), Cash (Chicago), Ristenpart/Grubbs (Cornell Tech/Colorado), Kerschbaum (Waterloo), Naveed (UIUC).

## 8. Future Work
- A tight, general snapshot-reconstruction theorem and matching schemes.
- Lower bounds for adversaries with *partial* or *noisy* auxiliary data.
- Multi-column / correlated-leakage snapshot bounds (joins of leaky columns).
- Composability: snapshot leakage of full encrypted indices, not single columns.
- Connecting snapshot bounds to differential-privacy-style guarantees for at-rest data.

## 9. Key References
- **[Foundational]** Naveed, Kamara, Wright. *Inference Attacks on Property-Preserving Encrypted Databases.* CCS, 2015.
- **[SOTA]** Grubbs, Sekniqi, Bindschaedler, Naveed, Ristenpart. *Leakage-Abuse Attacks against Order-Revealing Encryption.* IEEE S&P, 2017.
- **[SOTA]** Kerschbaum. *Frequency-Hiding Order-Preserving Encryption.* CCS, 2015.
- **[SOTA]** Lewi, Wu. *Order-Revealing Encryption: New Constructions, Applications, and Lower Bounds.* CCS, 2016.
- **[SOTA]** Durak, DuBuisson, Cash. *What Else is Revealed by Order-Revealing Encryption?* CCS, 2016.
- **[Survey]** Fuller, Varia, Hamlin, et al. *SoK: Cryptographically Protected Database Search.* IEEE S&P, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
