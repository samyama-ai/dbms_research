# Oblivious Relational Operators at Scale

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/oblivious-relational-operators` · **Status:** open

## 1. Problem Statement
Design relational operators — selection, projection, **join**, **group-by/aggregation**, and **sort** — whose memory access patterns are *data-oblivious*: the sequence of physical addresses (and any timing/volume side channels) touched during execution is independent of the actual data values and of which tuples satisfy predicates. The goal is operators that run on a trusted-but-leaky platform (an enclave such as Intel SGX/TDX, or an untrusted-storage/ORAM setting) with overhead **competitive with plaintext** on large inputs.

Variants:
- **Optimization (primary):** minimize concrete overhead factor over a plaintext baseline for inputs of $n$ tuples, ideally a constant or polylog factor.
- **Decision/feasibility:** does an oblivious algorithm exist for operator $O$ achieving $O(n\,\mathrm{polylog}\,n)$ work *and* $O(1)$ external-memory-pass obliviousness?
- **Counting/output-size:** handle data-dependent output sizes (e.g., join result of size $Z$) without leaking $Z$ — i.e., jointly oblivious *and* volume-hiding.

## 2. Mathematical Foundations
An algorithm $\mathcal{A}$ is **oblivious** if for any two inputs $x_0,x_1$ with $|x_0|=|x_1|$, the access-pattern distributions are computationally (or statistically) indistinguishable: $\mathrm{AccPat}(\mathcal{A},x_0)\approx_c \mathrm{AccPat}(\mathcal{A},x_1)$.

Building blocks: **oblivious sort** via sorting networks — Batcher's bitonic sort gives a data-independent $O(n\log^2 n)$ network; AKS / Goodrich's randomized Shellsort give $O(n\log n)$ but with large constants. **Compaction/distribution** (Goodrich, Order-ISA) yields oblivious tight compaction in $O(n)$. **ORAM** (Goldreich–Ostrovsky) gives a $\Omega(\log n)$ amortized cell-probe lower bound (Larsen–Nielsen, CRYPTO'18) for general oblivious RAM simulation.

Join cost is governed by the **AGM bound** $|Q|\le \prod_e |R_e|^{x_e}$ for a fractional edge cover $x$; an oblivious worst-case-optimal join must pad work to the AGM bound to hide selectivity. Group-by reduces to oblivious sort + linear oblivious aggregation scan; band/equi-joins reduce to oblivious sort-merge with expansion.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** *ObliDB* (Eskandarian–Zaharia, VLDB'19/PVLDB) — oblivious query operators in SGX. *Opaque* (Zheng et al., NSDI'17) — oblivious Spark SQL operators with bitonic-sort-based joins. *Oblix*, *ZeroTrace* for oblivious index/ORAM primitives. *SODA*/*Hermetic* and *Snoopy* (SOSP'21, oblivious storage scaling).
- **Theory-SOTA:** oblivious sort-merge and hash joins matching plaintext up to $O(\log n)$–$O(\log^2 n)$ factors; *Krastnikov–Kerschbaum–Stachowiak* (PVLDB'20) oblivious binary/band joins in $O((n+Z)\log(n+Z))$ without ORAM. Linear oblivious compaction (Asharov et al., "Bucket Oblivious Sort", SOSA'20).

## 4. Upper Bound
For sort-based equi-join and group-by: $O((n+Z)\log(n+Z))$ oblivious work using $O(n\log n)$ oblivious sort + linear oblivious expansion/aggregation, in the **oblivious RAM / sorting-network model** (Krastnikov et al. 2020). General operators via ORAM incur an additional $O(\log n)$–$O(\log^2 n)$ factor. With a sorting network the bound is $O((n+Z)\log^2(n+Z))$ (bitonic), the common systems choice for vectorizability. Worst-case-optimal oblivious multiway joins pad to the AGM bound $\mathrm{AGM}(Q)$, giving $O(\mathrm{AGM}(Q)\cdot \mathrm{polylog})$.

## 5. Lower Bound
- **Cell-probe:** Larsen–Nielsen (CRYPTO'18) prove any online ORAM has $\Omega(\log n)$ amortized overhead; thus operators built on general ORAM cannot beat a $\log n$ factor. For *offline*/non-adaptive oblivious algorithms this barrier does not directly apply, leaving room for $o(\log n)$ amortized in restricted models.
- **Sorting-network depth:** $\Omega(\log n)$ depth (Ajtai–Komlós–Szemerédi) — comparison-based oblivious sort is $\Omega(n\log n)$.
- **Volume:** hiding output size $Z$ forces $\Omega(\mathrm{AGM}(Q))$ padding (information-theoretic) for joins, so a truly value-and-volume-oblivious join cannot be output-sensitive.

## 6. The Gap
For *sort-based* equi-join/group-by the gap is essentially the $\log n$ sort factor vs. linear plaintext hashing — modest and arguably near-closed in the oblivious-sort model. The genuinely **open** gaps: (i) closing the $O(\log^2 n)$ (bitonic, practical) vs. $O(\log n)$ (AKS, impractical-constant) divide with a *concretely fast* $O(n\log n)$ oblivious sort; (ii) oblivious worst-case-optimal *multiway* joins matching plaintext WCOJ on cyclic queries; (iii) whether general operators truly require the ORAM $\log n$ tax or can exploit non-adaptivity.

## 7. Current Research (as of June 2026)
Active threads: (a) hardware-enclave operator libraries riding TDX/SEV-SNP with oblivious primitives and constant-time vectorized compaction; (b) "*differentially oblivious*" relaxations (Chan–Chung–Maggs–Shi, ITCS'19) trading a tiny $\epsilon$-leakage for near-linear cost — now extended to joins and group-by *(frontier — verify)*; (c) GPU-accelerated oblivious sort/compaction to shrink constants. Groups: Stanford (Zaharia/Eskandarian lineage), Waterloo (Kerschbaum), CMU/Cornell (Shi), Berkeley RISE-successors. Concrete oblivious WCOJ remains largely unbuilt *(frontier — verify)*.

## 8. Future Work
- A practical $O(n\log n)$ oblivious sort with small constants to replace bitonic in systems.
- Oblivious worst-case-optimal and Yannakakis-style acyclic join pipelines with bounded padding.
- Principled composition of differential obliviousness across an operator tree with end-to-end leakage budgets.
- Co-design with volume-hiding multimaps so intermediate result sizes are not leaked across pipeline stages.

## 9. Key References
- **[Foundational]** O. Goldreich, R. Ostrovsky. *Software Protection and Simulation on Oblivious RAMs.* J. ACM, 1996.
- **[Foundational]** K. Batcher. *Sorting Networks and Their Applications.* AFIPS, 1968.
- **[SOTA]** S. Eskandarian, M. Zaharia. *ObliDB: Oblivious Query Processing for Secure Databases.* PVLDB 13(2), 2019.
- **[SOTA]** W. Zheng et al. *Opaque: An Oblivious and Encrypted Distributed Analytics Platform.* NSDI, 2017.
- **[SOTA]** S. Krastnikov, F. Kerschbaum, D. Stachowiak. *Efficient Oblivious Database Joins.* PVLDB 13(11), 2020.
- **[SOTA]** K. G. Larsen, J. B. Nielsen. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018.
- **[Survey]** T-H. H. Chan, K-M. Chung, B. Maggs, E. Shi. *Foundations of Differentially Oblivious Algorithms.* ITCS/J. ACM, 2019/2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
