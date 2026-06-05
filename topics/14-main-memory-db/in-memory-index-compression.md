# Compression for In-Memory Indexes

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/in-memory-index-compression` · **Status:** open

## 1. Problem Statement
In an IMDB, the index (B+-tree, ART, hash, learned model) can consume as much DRAM as the base data — sometimes more. DRAM is the scarce, costly resource. **The problem:** compress the in-memory index so that it occupies space close to the information-theoretic minimum, **while preserving $O(\log n)$ (or near-$O(1)$) random point lookups, range scans, and in-place updates at main-memory speed** — i.e., without paying decompression cost on every probe and without losing dynamism.

This is harder than data compression because indexes are *navigational*: every access dereferences pointers and compares keys, so a compression scheme must support **operations directly on the compressed form** (or with negligible local decode). Static succinct structures often achieve great space but lose update support; dynamic indexes resist compression.

Variants: *(space-optimization)* minimize bits subject to a query-time bound; *(static vs. dynamic)* succinct/immutable vs. updatable; *(point vs. range)* membership-only (filters) vs. ordered range support; *(decision)* given a space budget $S$, does a structure answering rank/select/predecessor in $t$ time exist?

## 2. Mathematical Foundations
For $n$ keys from a universe $[u]$, the information-theoretic lower bound on storing the set is $\mathcal{B}(n,u)=\lceil\log_2\binom{u}{n}\rceil \approx n\log_2(u/n)+O(n)$ bits. **Succinct** data structures use $\mathcal{B}+o(\mathcal{B})$ bits while answering **rank/select/predecessor** in $O(1)$ or $O(\log\log u)$ time — the theoretical backbone (wavelet trees, FM-index, succinct tries / Patricia, the **van Emde Boas** layout). Filters relax to approximate membership with a false-positive rate $\varepsilon$, where the lower bound is $n\log_2(1/\varepsilon)$ bits (achieved by quotient/cuckoo filters; classic Bloom uses $\approx1.44\,n\log_2(1/\varepsilon)$).

**Learned indexes** reframe the index as a regression model: store a function $\hat F$ approximating the CDF, with error bound $\epsilon$ so a lookup does a local $O(\log\epsilon)$ search; space is the model size, often $\ll$ a B-tree when keys are smooth. Compressibility is then governed by the *Kolmogorov-style* complexity of the key distribution, not just $n\log u$. The central tension: $o(\mathcal{B})$ redundancy and constant-time navigation are compatible *statically* (Pătrașcu, Belazzougui-Navarro), but **dynamic** succinct predecessor structures incur a proven update/query overhead.

## 3. State of the Art (SOTA)
- **Succinct Range Filter — SuRF** (Zhang, Lim, Andersen, Kaminsky, Keeton, Pavlo — SIGMOD 2018): a fast succinct trie (FST) giving approximate range filtering at a few bits/key; landmark for compressed in-memory ordered indexing.
- **ART / Adaptive Radix Tree** (Leis, Kemper, Neumann — ICDE 2013): adaptive node sizes give strong space efficiency with full dynamism; the practical in-memory index baseline.
- **Learned indexes** — **RMI** (Kraska, Beutel, Chi, Dean, Polyzotis — SIGMOD 2018), **PGM-index** (Ferragina, Vinciguerra — VLDB 2020, with worst-case bounds), **ALEX** (Ding et al., SIGMOD 2020, updatable). PGM gives provable space-time tradeoffs; ALEX restores updates.
- **Hybrid Index / Dual-stage** (Zhang et al., SIGMOD 2016): compact a cold static stage beneath a dynamic stage — the canonical "compress the cold part" recipe.

## 4. Upper Bound
- **Static, ordered:** succinct tries / SuRF and the **PGM-index** achieve near-information-optimal space; PGM gives $O(\log n)$ lookups with provably $O(m)$ space for $m$ piecewise-linear segments, often $\ll n$.
- **Approximate membership:** quotient/cuckoo/**ribbon filters** reach within $\approx1.0$–$1.08\times$ the $n\log_2(1/\varepsilon)$ optimum with $O(1)$ probes.
- **Dynamic, exact, ordered:** ALEX and Hybrid-Index give compressed structures with amortized $O(\log n)$ updates and lookups, but with constant-factor space overhead above the static optima. Best known combines a succinct cold tier with a small dynamic hot tier.

## 5. Lower Bound
- **Information-theoretic:** any membership structure needs $\ge\mathcal{B}(n,u)$ bits exactly, or $\ge n\log_2(1/\varepsilon)$ bits for FP-rate $\varepsilon$ (filters are *optimal up to constants* — a hard floor).
- **Cell-probe:** the **predecessor problem** has tight cell-probe lower bounds (Pătrașcu–Thorup, STOC 2006/2007): with space $S$ and word size $w$, query time is $\Omega(\log_w u / \log(S\,w/n))$-style — you *cannot* have both linear space and $o(\log\log u)$ predecessor in general. This bounds how fast a near-succinct ordered index can be.
- **Dynamism:** dynamic succinct ordered dictionaries face an update–query product lower bound (a $\Omega(\log n / \log\log n)$-type barrier), so full dynamism + succinctness + fast queries cannot all be free.

## 6. The Gap
Static and approximate cases are essentially *closed* (filters and PGM/SuRF hit the bounds up to constants). The **open** core is the **dynamic, exact, ordered** index: there is a real gap between the cell-probe/dynamic lower bounds and any practical structure that is simultaneously near-succinct, updatable in-place, and fast on real (non-smooth, skewed, string) keys. Learned indexes shrink space dramatically on smooth data but lack worst-case guarantees on adversarial distributions; reconciling distribution-adaptive compression with worst-case predecessor bounds is the unresolved question. Closing it needs either a dynamic succinct predecessor structure matching the cell-probe bound in practice, or a proof that the constant-factor overhead is inherent for updatable indexes.

## 7. Current Research (as of June 2026)
- **Updatable learned indexes** with worst-case guarantees and string-key support; hybridizing PGM bounds with ALEX-style gapped arrays *(frontier — verify)*.
- **Compressed indexes for vectors/embeddings** and for tiered DRAM–CXL memory, where compression trades against remote-access latency *(frontier — verify)*.
- **Ribbon/quotient filter** refinements approaching the $n\log(1/\varepsilon)$ floor with SIMD probing *(frontier — verify)*.
- Groups: CMU DB Group (Pavlo), MIT (Kraska/Madden), Univ. of Pisa (Ferragina/Vinciguerra), TUM (Leis/Neumann).

## 8. Future Work
- A dynamic, near-succinct, distribution-robust ordered index closing the cell-probe gap in practice.
- Compression-aware concurrency: keeping succinct structures latch-free/updatable.
- Theoretical worst-case bounds for learned indexes on arbitrary key distributions.
- Co-design with hardware (SIMD/decompression accelerators, CXL).

## 9. Key References
- **[SOTA]** H. Zhang, H. Lim, D. Andersen, M. Kaminsky, K. Keeton, A. Pavlo. *SuRF: Practical Range Query Filtering with Fast Succinct Tries.* SIGMOD, 2018. — [DBLP](https://dblp.org/rec/conf/sigmod/ZhangLLAKKP18.html)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-index: a fully-dynamic compressed learned index with provable worst-case bounds.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[Foundational]** T. Kraska, A. Beutel, E. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[Foundational]** M. Pătrașcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043)
- **[Foundational]** V. Leis, A. Kemper, T. Neumann. *The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544812)
- **[Survey]** G. Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016. — [DOI](https://doi.org/10.5555/3092586)

## 10. Worked Example

Index $n = 10^6$ keys drawn from a $u = 2^{32}$ universe.

**Information-theoretic floor.** Storing the *set* exactly needs
$\mathcal{B}(n,u) = \lceil\log_2\binom{u}{n}\rceil \approx n\log_2(u/n) = 10^6\times\log_2(2^{32}/10^6) \approx 10^6\times 12 = 12\text{ Mbit} \approx 1.5\text{ MB}.$

**B+-tree baseline.** With 8 B keys + 8 B child pointers and ~50% fill, a B+-tree easily consumes $\ge 20$–$30$ MB — over $15\times$ the floor.

**Approximate filter.** If we only need membership at false-positive rate $\varepsilon = 1\%$, the floor drops to $n\log_2(1/\varepsilon) = 10^6\times\log_2(100) \approx 6.64\text{ Mbit} = 830\text{ KB}$. A classic Bloom filter pays the $1.44\times$ penalty ($\approx 1.2$ MB); a quotient/ribbon filter reaches $\approx 1.0$–$1.08\times$ ($\approx 0.9$ MB) — essentially the floor.

**Learned (PGM) angle.** If the keys are near-uniform, a piecewise-linear model with $m \ll n$ segments (say $m = 1000$, each a slope+intercept = 16 B) stores in $\approx 16$ KB and answers a lookup with one $O(\log m)$ model probe plus a local $O(\log\varepsilon)$ search — illustrating how distribution structure beats the generic $n\log_2(u/n)$ bound while keeping $O(\log n)$ queries.

---
*Part of the [DBMS Research catalog](../../README.md).*
