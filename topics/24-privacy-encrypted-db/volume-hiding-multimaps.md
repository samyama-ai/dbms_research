# Volume-Hiding Encrypted Multi-Maps

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/volume-hiding-multimaps` · **Status:** partially-solved

## 1. Problem Statement
An **encrypted multi-map (EMM)** maps labels (keys) to tuples of values; querying a label returns its value list. EMMs underlie searchable encryption and encrypted **join indexes**. A naive EMM leaks each label's **response volume** $|v_\ell|$, which is enough to reconstruct data (volume-leakage attacks). The problem: construct **volume-hiding** EMMs — the access pattern/volume revealed per query is independent of the true $|v_\ell|$ — with **sub-quadratic storage** (better than padding every label to the max volume $\to O(N\cdot \ell_{\max})$) and low query overhead, and extend this to join/multi-attribute indexes.

Variants:
- **Decision/security:** indistinguishability under a volume-hiding leakage profile.
- **Optimization:** minimize storage $S$ and per-query cost while bounding leakage; trade exact vs. *differentially-private* volume hiding.
- **Counting:** support correct aggregation/COUNT without revealing $|v_\ell|$.

## 2. Mathematical Foundations
Let total volume $N=\sum_\ell |v_\ell|$ over $m$ labels, $\ell_{\max}=\max_\ell|v_\ell|$. **Full padding** gives storage $m\cdot\ell_{\max}$ — up to $\Theta(mN)$, quadratic. Volume-hiding security: $\mathcal{L}_{\text{query}}(\ell)$ independent of $|v_\ell|$.

Key constructions: **dprfMM / VLH / AVLH** (Kamara–Moataz, EUROCRYPT'19) — fully volume-hiding via a pseudorandom transform, and *Advanced VLH* trading a small false-negative rate for linear $O(N)$ storage. **dprfMM** achieves exact hiding with $O(N)$ storage but $O(\ell_{\max})$ query. **XorMM** / **Pancake** (Grubbs–Khandelwal–Lacharité et al., USENIX'20) use frequency-smoothing to a uniform access distribution. **Differentially private volume-hiding** (Patel–Persiano–Yeo–Yung, CCS'19) pads with DP noise to $O(N + m\cdot\mathrm{polylog})$, bounding leakage to $(\epsilon,\delta)$ instead of zero. Lower-bound tooling: cuckoo-hashing load bounds, balls-into-bins concentration, and the information-theoretic cost of hiding a histogram.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Kamara–Moataz **VLH/AVLH** (EUROCRYPT'19); Patel et al. **DP volume-hiding** with near-linear storage (CCS'19); **XorMM** with $O(N)$ storage and $O(1)$-ish amortized query (Bossuat–Bost–Fouque... / Wang–Chow lineage). Recent constructions push to *optimal* $O(N)$ storage + $O(\ell_{\max})$ communication or DP-relaxed near-linear both.
- **Systems-SOTA:** MongoDB **Queryable Encryption** (structured-encryption-based, Kamara–Moataz design) ships EMM-style indexes; encrypted-join indexes appear in research prototypes (SEAL/PiBase lineage). Practical fully-volume-hiding *joins* remain prototype-level.

## 4. Upper Bound
- **Exact volume-hiding:** $O(N)$ storage with $O(\ell_{\max})$ query (dprfMM, Kamara–Moataz EUROCRYPT'19); AVLH reaches $O(N)$ storage at the cost of a tunable false-negative probability.
- **DP volume-hiding:** $O(N + m\log(1/\delta)/\epsilon)$ storage (Patel et al. CCS'19), sub-quadratic and near-linear, hiding to $(\epsilon,\delta)$.
- These hold in the **structured-encryption / leakage-parameterized** model with semantic-secure symmetric primitives + PRFs. For **joins**, composing two volume-hiding EMMs bounds intermediate volume but current constructions pay AGM-bound padding for correctness.

## 5. Lower Bound
- **Exact hiding storage:** any *exactly* volume-hiding EMM that answers correctly must, in the worst case (one heavy label), reserve $\Omega(\ell_{\max})$ per query-able label — giving an $\Omega(m\,\ell_{\max})$ barrier for naive layouts; hashing-based schemes beat this only by reusing slots, bounded by cuckoo load factors.
- **Information-theoretic:** hiding the volume histogram exactly requires padding total work to a value-independent envelope; for joins, hiding result volume forces $\Omega(\mathrm{AGM})$ padding (information-theoretic), precluding output-sensitive cost.
- DP relaxation provably escapes the exact-hiding storage barrier (this is *why* the problem is "partially solved").

## 6. The Gap
For *single-attribute* EMMs the gap is largely closed under DP relaxation (near-linear storage, $(\epsilon,\delta)$ leakage). **Genuinely open:** (i) exact volume-hiding with simultaneously $O(N)$ storage *and* $O(1)$ amortized query and no false negatives; (ii) **volume-hiding join indexes** with sub-quadratic storage that hide *intermediate* result volumes across a pipeline without AGM-bound blowup; (iii) multi-attribute/conjunctive volume-hiding without leakage cross-products.

## 7. Current Research (as of June 2026)
Active: (a) DP-volume-hiding tightened with better noise distributions and tighter composition for workloads *(frontier — verify)*; (b) volume-hiding **conjunctive and join** indexes (extending OXT/SEAL with volume-smoothing) *(frontier — verify)*; (c) frequency-smoothing (Pancake-style) merged with ORAM-lite for KV stores in production encrypted databases; (d) attacks specifically targeting *residual* volume leakage in DP schemes. Groups: Brown/MongoDB (Kamara–Moataz), Google (Patel–Yeo–Persiano), Cornell Tech (Grubbs/Ristenpart), Royal Holloway (Minaud).

## 8. Future Work
- Provably optimal exact volume-hiding (close storage/query trade-off) or a matching lower bound.
- End-to-end volume-hiding **encrypted joins** with bounded padding and pipeline composition (ties to oblivious-operators page).
- Tighter DP accounting across multi-query workloads; adaptive adversaries.
- Hardware-accelerated volume-hiding KV layers for OLTP-scale encrypted stores.

## 9. Key References
- **[Foundational]** S. Kamara, T. Moataz, O. Ohrimenko. *Structured Encryption and Leakage Suppression.* CRYPTO, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96884-1_12) · [ePrint](https://eprint.iacr.org/2018/551)
- **[SOTA]** S. Kamara, T. Moataz. *Computationally Volume-Hiding Structured Encryption.* EUROCRYPT, 2019. — [DOI](https://doi.org/10.1007/978-3-030-17656-3_7)
- **[SOTA]** S. Patel, G. Persiano, K. Yeo, M. Yung. *Mitigating Leakage in Secure Cloud-Hosted Data Structures: Volume-Hiding for Multi-Maps via Hashing.* CCS, 2019. — [DOI](https://doi.org/10.1145/3319535.3354213) · [DBLP](https://dblp.org/rec/conf/ccs/PatelPYY19.html)
- **[SOTA]** P. Grubbs, A. Khandelwal, M-S. Lacharité, et al. *Pancake: Frequency Smoothing for Encrypted Data Stores.* USENIX Security, 2020. — [USENIX](https://www.usenix.org/conference/usenixsecurity20/presentation/grubbs) · [ePrint](https://eprint.iacr.org/2020/1501)
- **[Attack]** P. Grubbs, M-S. Lacharité, B. Minaud, K. Paterson. *Pump up the Volume: Practical Database Reconstruction from Volume Leakage.* CCS, 2018. — [DOI](https://doi.org/10.1145/3243734.3243864) · [ePrint](https://eprint.iacr.org/2018/965)
- **[Survey]** S. Kamara, T. Moataz, et al. *SoK / Structured Encryption surveys* and the MongoDB Queryable Encryption design notes, 2022–2023. *(unverified)*

## 10. Worked Example

**Full padding vs. volume hiding on a 3-label EMM.** A multi-map has $m=3$ labels with value lists:

$$|v_{\text{A}}|=2,\quad |v_{\text{B}}|=1,\quad |v_{\text{C}}|=5,\qquad N=\sum_\ell|v_\ell|=8,\;\ell_{\max}=5.$$

A naive EMM returns 2, 1, 5 results respectively — the per-query **volume directly reveals which label was queried** (only C returns 5). This is the leakage Pump-up-the-Volume exploits.

**Full padding** pads every label to $\ell_{\max}=5$, so all queries return 5 (volume-independent). Storage $= m\cdot\ell_{\max}=3\times5=15$ vs. the true $N=8$ — nearly $2\times$ blowup here, and $\Theta(m\,\ell_{\max})$ (quadratic) in the worst case when one heavy label dominates.

**dprfMM (Kamara–Moataz '19):** lays all 8 values into a hash-indexed array of size $O(N)$ and answers each query by fetching a fixed $\ell_{\max}=5$ pseudorandom slots — exact hiding at $O(N)$ storage, $O(\ell_{\max})$ query.

**DP volume-hiding (Patel et al. '19):** instead of padding to the max, add noise drawn so each reported volume is $|v_\ell|+\text{Lap}$ truncated — e.g. report $5,4,6$ — giving $O(N+m\log(1/\delta)/\epsilon)$ storage and $(\epsilon,\delta)$-leakage rather than zero. For $m=3$ this is near-linear, escaping the $\Omega(m\,\ell_{\max})$ exact-hiding barrier — which is why the single-attribute case is "partially solved."

---
*Part of the [DBMS Research catalog](../../README.md).*
