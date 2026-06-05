# Forward/Backward Private Dynamic SSE

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/forward-backward-private-sse` · **Status:** partially-solved

## 1. Problem Statement
**Dynamic Searchable Symmetric Encryption (DSSE)** lets a client outsource an encrypted keyword index supporting both **search** and **updates** (add/delete document–keyword pairs). Two privacy properties matter:
- **Forward privacy:** an update (newly added entry) cannot be linked to past searches — defeats file-injection attacks.
- **Backward privacy:** searches do not reveal entries that were added *and then deleted* (with graded levels Type-I/II/III, strongest to weakest).

The problem: build DSSE that is **forward- and (strongly) backward-private** while achieving **low update and search overhead at scale** — ideally $O(1)$ amortized update, search cost proportional to current (non-deleted) result size $a_w$, low client state and few roundtrips, and locality/parallelism friendly to real storage.

Variants: decision (security game), optimization (minimize search/update I/O, roundtrips, client storage), and the trade-off frontier among backward-privacy level vs. cost.

## 2. Mathematical Foundations
Security is leakage-parameterized: a scheme is $\mathcal{L}$-adaptively secure if real view $\approx_c \mathcal{S}(\mathcal{L})$ (Curtmola et al., CCS'06). **Forward privacy** (Stefanov–Papamanthou–Shi, NDSS'14; Bost "$\Sigma o\phi o\varsigma$", CCS'16): update leakage is independent of which keyword is updated. **Backward privacy** formalized by Bost–Minaud–Ohrimenko (CCS'17) into **Type-I** (leak only current matching docs + insertion times), **Type-II** (+ when updates happened), **Type-III** (+ which deletion cancels which insertion).

Primitives: **trapdoor permutations** (Sophos), **constrained/puncturable PRFs**, **symmetric puncturable encryption** (Diana, Janus), and **ORAM** for the strongest hiding. Cost metrics: search $O(a_w)$ vs. $O(n_w)$ (total historical), roundtrips, and **locality** $L$ / read-efficiency $R$ (Cash–Tessaro EUROCRYPT'14 lower bound: a sublinear-storage SSE cannot have $O(1)$ locality and $O(1)$ read-efficiency simultaneously).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** **Sophos/$\Sigma o\phi o\varsigma$** (Bost, CCS'16) forward-private; **Diana / Janus** (Bost–Minaud–Ohrimenko, CCS'17) backward-private (Type-II/III); **Moneta** (Type-I, via TWORAM, costly); **Mitra/Orion/Horus** (Ghareh Chamani et al., CCS'18) practical backward-private with ORAM trade-offs; **Aura**, **SDd / FAST / FASTIO** (Song et al.), **DynHIDX**. **Bestie**/**MUSES** and **OSSE**/**SWiSSSE** add stronger leakage suppression.
- **Systems-SOTA:** **Clusion** library (Brown), **SWiSSSE** (Royal Holloway, end-to-end leakage-suppressed SSE), encrypted-search modules in production document stores.

## 4. Upper Bound
- **Forward-private, $O(1)$ amortized update, $O(a_w)$ search:** achievable (Mitra/Diana lineage) in the symmetric-primitive model with one roundtrip per result block.
- **Backward-private Type-II:** $O(a_w)$ search, $O(\log)$-ish update with puncturable encryption (Janus/Janus++, Diana_del) — near-optimal asymptotically.
- **Backward-private Type-I (strongest):** $O(a_w)$ search but requires ORAM/oblivious-map machinery (Orion/Moneta), paying $O(\log^2 n)$ or multiple roundtrips.
Model: $\mathcal{L}$-adaptive SSE security with PRFs/TDPs (and ORAM for Type-I).

## 5. Lower Bound
- **Locality vs. read-efficiency:** Cash–Tessaro (EUROCRYPT'14) and Asharov–Naor–Segev–Shahaf (STOC'16) prove any SSE with $O(n)$ storage cannot simultaneously have $O(1)$ locality and $O(1)$ read-efficiency; there is an inherent trade-off curve.
- **Backward Type-I via obliviousness:** hiding deleted-entry access inherits the ORAM $\Omega(\log n)$ cell-probe lower bound (Larsen–Nielsen, CRYPTO'18); thus strongest backward privacy cannot beat a $\log n$ factor with current techniques.
- **Leakage-abuse:** Zhang–Katz–Papamanthou (USENIX'16) file-injection attacks show *non*-forward-private schemes are catastrophically broken — motivating the property, and bounding how little can be leaked.

## 6. The Gap
Forward privacy and Type-II/III backward privacy are essentially **solved** with near-optimal $O(a_w)$ search and small update cost — hence "partially solved." The open gaps: (i) **Type-I (strongest) backward privacy without the ORAM $\log^2 n$ / multi-roundtrip tax** — is the ORAM barrier fundamental here? (ii) jointly achieving strong backward privacy *and* good **locality** (the Cash–Tessaro frontier) at scale; (iii) suppressing residual *search-pattern*/query-equality leakage that backward privacy does not cover; (iv) efficient multi-client/verifiable variants.

## 7. Current Research (as of June 2026)
Directions: (a) closing the Type-I cost gap with lighter oblivious maps and lazy deletion *(frontier — verify)*; (b) **leakage-suppressed** SSE (SWiSSSE, query-equality hiding) merging forward/backward privacy with volume/search-pattern hiding *(frontier — verify)*; (c) hardware-enclave-assisted DSSE shifting obliviousness into TEEs; (d) verifiable and multi-writer DSSE; (e) new leakage-abuse attacks targeting backward-private schemes' update-timing leakage. Groups: Brown/MongoDB (Kamara/Moataz), SAP/Waterloo (Bost/Kerschbaum lineage), USC (Ghareh Chamani/Papamanthou), Royal Holloway (Paterson/Minaud), Monash/CSIRO.

## 8. Future Work
- Type-I backward privacy with $O(a_w)$ search and $o(\log^2 n)$ overhead, or a matching lower bound.
- Unified schemes hiding search-pattern + volume + update-timing with provable composition.
- Locality-optimal backward-private constructions reconciling the Cash–Tessaro trade-off.
- Standardized leakage profiles + attack benchmarks for production encrypted search.

## 9. Key References
- **[Foundational]** R. Curtmola, J. Garay, S. Kamara, R. Ostrovsky. *Searchable Symmetric Encryption: Improved Definitions and Efficient Constructions.* CCS, 2006.
- **[Foundational]** R. Bost. *$\Sigma o\phi o\varsigma$: Forward Secure Searchable Encryption.* CCS, 2016.
- **[SOTA]** R. Bost, B. Minaud, O. Ohrimenko. *Forward and Backward Private Searchable Encryption from Constrained Cryptographic Primitives.* CCS, 2017.
- **[SOTA]** J. Ghareh Chamani, D. Papadopoulos, C. Papamanthou, R. Jalili. *New Constructions for Forward and Backward Private Symmetric Searchable Encryption.* CCS, 2018.
- **[Attack]** Y. Zhang, J. Katz, C. Papamanthou. *All Your Queries Are Belong to Us: The Power of File-Injection Attacks on Searchable Encryption.* USENIX Security, 2016.
- **[Lower bound]** D. Cash, S. Tessaro. *The Locality of Searchable Symmetric Encryption.* EUROCRYPT, 2014.
- **[SOTA]** Z. Gui, K. Paterson, S. Patranabis, et al. *SWiSSSE: System-Wide Security for Searchable Symmetric Encryption.* PoPETs, 2024.

---
*Part of the [DBMS Research catalog](../../README.md).*
