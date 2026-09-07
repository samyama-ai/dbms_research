---
id: 28-vector-similarity-search/private-similarity-search
title: "Privacy-preserving similarity search"
topic: 28-vector-similarity-search
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Privacy-preserving similarity search

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/private-similarity-search` · **Status:** partially-solved

## 1. Problem Statement

A client holds a query vector $q$; a server holds a vector database $P \subseteq \mathbb{R}^d$. The goal is to compute the (approximate) top-$k$ nearest neighbors of $q$ in $P$ such that the server learns nothing about $q$ and the client learns nothing about $P$ beyond the answer (and an explicitly quantified **leakage profile**). Trust models: **fully homomorphic encryption (FHE)** over an encrypted database; **secure multiparty computation (MPC)** / secret-sharing across non-colluding servers; **private information retrieval (PIR)** for the retrieval step; and **trusted execution environments (TEE)** as a hardware-assisted relaxation. Variants: **single-server** vs **two/three-party**; **exact** vs **approximate**; **query-private only** vs **fully oblivious** (access patterns hidden). The central tension is the trilemma of **(a) quantified leakage**, **(b) practical query latency**, and **(c) high recall at scale** — current schemes achieve at most two.

## 2. Mathematical Foundations

Security is defined by **simulation-based** indistinguishability against a leakage function $\mathcal L$: a protocol is secure if a simulator given only $\mathcal L(P,q)$ produces a view computationally indistinguishable from the real one. Building blocks: **CKKS/BFV FHE** for approximate arithmetic on ciphertexts (inner products and squared $\ell_2$ distances are degree-2, hence FHE-friendly before comparison); **garbled circuits / GMW** for the argmin/top-$k$ comparison stage; **PIR** with $\mathrm{polylog}$ or sublinear communication for oblivious fetch; and **oblivious RAM (ORAM)** / oblivious data structures to hide *access patterns*, which otherwise leak through index traversal. Leakage is quantified along axes: **search-pattern**, **access-pattern**, **volume**, and **distance/rank leakage**; leakage-abuse attacks (Islam–Kuzu–Kantarcioglu; Kellaris et al.) show even "small" volume/access leakage can be catastrophic, motivating fully oblivious designs. Differential privacy can additionally bound *distance/rank* leakage by noising scores.

## 3. State of the Art (SOTA)

- **FHE ANN:** CKKS-based encrypted similarity search computing inner products homomorphically, with clustering (IVF) to bound the comparison set; latencies are seconds-to-minutes per query at moderate $n$.
- **MPC / secret-shared:** Two/three-party secure ANN (e.g. **SANNS**, Chen et al., USENIX Security 2020) combines linear scan / clustering with garbled-circuit top-$k$; **Cheetah / CrypTFlow-style** primitives accelerate the linear-algebra phase.
- **PIR-based:** Recent sublinear-communication PIR (SimplePIR/DoublePIR, 2023; followups) makes *oblivious retrieval* of cluster contents practical, composed with a small secure top-$k$.
- **Systems/TEE:** SGX/TDX-resident vector search with ORAM-protected access for deployable (weaker-trust) privacy.

## 4. Upper Bound

For two-server secret-shared exact ANN, SANNS achieves sublinear *online* work via clustering plus oblivious top-$k$ with rigorous simulation security and leakage limited to public parameters ($n$, $d$, $k$, cluster count) — query latency on the order of seconds for $n \sim 10^6$. FHE single-server inner-product search runs in $\tilde O(n d)$ ciphertext ops with no access-pattern leakage (whole encrypted DB processed) but high constants. PIR-composed retrieval gives $\mathrm{polylog}(n)$ communication for the fetch stage. These are the practical upper bounds; all degrade with high recall + large $n$ simultaneously.

## 5. Lower Bound

**Single-server, no-leakage** retrieval inherits the **PIR communication lower bound**: any single-server information-theoretic PIR requires $\Omega(n)$ communication (Chor–Goldreich–Kushilevitz–Sudan), so sublinear single-server schemes must be *computational* (lattice/LWE-based) and still incur $\Omega(n)$ *server computation* per query (the server must touch every record, else access pattern leaks). Hiding access patterns via ORAM imposes an $\Omega(\log n)$ overhead lower bound per access (Larsen–Nielsen, CRYPTO 2018). Leakage-abuse results (Kellaris–Kollios–Nissim–O'Neill, CCS 2016) show that schemes leaking volume/access patterns are *provably reconstructable*, a lower bound on acceptable leakage rather than on cost. FHE comparison (argmin) is inherently expensive: non-arithmetic operations need bootstrapping or bit-decomposition, a practical floor.

## 6. The Gap

**Partially solved**: for $n$ up to $\sim 10^6$–$10^7$ and modest recall, secure ANN runs in seconds with clean leakage profiles — adequate for some deployments. The gap is **scale × recall × leakage**: no scheme gives billion-scale, high-recall ANN at interactive latency with *zero* access-pattern leakage. Single-server schemes pay $\Omega(n)$ server work; fully oblivious schemes pay ORAM's $\Omega(\log n)$ multiplicative overhead per access on top of graph traversal; FHE pays bootstrapping. Closing the gap needs either index structures whose access pattern is *intrinsically* query-independent (oblivious by design) or hardware/crypto co-design lowering FHE comparison cost by orders of magnitude.

## 7. Current Research (as of June 2026)

- PIR-composed ANN: combining fast LWE-PIR with lightweight secure top-$k$ to push communication sublinear *(frontier — verify)*.
- Oblivious graph indices: HNSW/IVF variants with query-independent access patterns, avoiding generic ORAM overhead.
- DP-relaxed leakage: bounded, *quantified* distance/access leakage traded for large speedups, with formal $(\varepsilon,\delta)$ guarantees.
- TEE + ORAM hybrids for deployable privacy (Microsoft, academic enclaves).
- Groups: Boneh/Corrigan-Gibbs (PIR), the SANNS/crypto-ANN line, and applied-FHE teams (Zama, Duality).

## 8. Future Work

- Intrinsically oblivious ANN indices that avoid generic ORAM blowup.
- Billion-scale secure ANN at sub-second latency with full leakage quantification.
- Tight tradeoff curves between quantified leakage and performance.
- Standardized leakage taxonomies and benchmarks for private vector search.

## 9. Key References

- **[Foundational]** Chor, B., Goldreich, O., Kushilevitz, E., Sudan, M. *Private Information Retrieval.* JACM / FOCS, 1995/1998. — [DOI](https://doi.org/10.1145/293347.293350)
- **[SOTA]** Chen, H., Chillotti, I., Dong, Y., Poburinnaya, O., Razenshteyn, I., Riazi, M. S. *SANNS: Scaling Up Secure Approximate k-Nearest Neighbors Search.* USENIX Security, 2020. — [arXiv](https://arxiv.org/abs/1904.02033)
- **[SOTA]** Henzinger, A., Hong, M., Corrigan-Gibbs, H., Meiklejohn, S., Vaikuntanathan, V. *One Server for the Price of Two: Simple and Fast Single-Server PIR (SimplePIR).* USENIX Security, 2023. — [ePrint](https://eprint.iacr.org/2022/949)
- **[Lower bound]** Larsen, K. G., Nielsen, J. B. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96881-0_18)
- **[Lower bound]** Kellaris, G., Kollios, G., Nissim, K., O'Neill, A. *Generic Attacks on Secure Outsourced Databases.* CCS, 2016. — [DOI](https://doi.org/10.1145/2976749.2978386)

## 10. Worked Example

Consider the **single-server $\Omega(n)$ computation** lower bound concretely. The server holds $n=4$ encrypted records and the client wants record index $2$. Suppose the server, to save work, only touched records $\{2,3\}$ and skipped $\{1,4\}$. Over many queries the server observes *which* records it accessed; here it learns the answer lies in $\{2,3\}$ — the access pattern leaked $1$ bit about the query, violating obliviousness. To leak nothing, the server's computation must be a function of *all* $4$ ciphertexts on *every* query, i.e. $\Omega(n)$ work.

Now the FHE distance step (CKKS): client encrypts $q=(1,0)$; server holds $x=(0.6,0.8)$. The squared $\ell_2$ distance $\lVert q-x\rVert^2 = (1-0.6)^2+(0-0.8)^2 = 0.16+0.64 = 0.80$ is degree-2 in the ciphertext, computable *without bootstrapping*. But the subsequent argmin/top-$k$ comparison is non-arithmetic and needs bit-decomposition or bootstrapping — the practical cost floor of section 5. So the cheap part (distances) and the expensive part (ranking) sit on opposite sides of the FHE difficulty boundary.

---
*Part of the [DBMS Research catalog](../../README.md).*
