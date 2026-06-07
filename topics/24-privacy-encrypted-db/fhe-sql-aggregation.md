---
id: 24-privacy-encrypted-db/fhe-sql-aggregation
title: "Homomorphic SQL Aggregation at Practical Cost"
topic: 24-privacy-encrypted-db
status: solved-but-impractical
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Homomorphic SQL Aggregation at Practical Cost

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/fhe-sql-aggregation` · **Status:** solved-but-impractical

## 1. Problem Statement
Evaluate SQL **filter + aggregate** queries — `SELECT SUM/COUNT/AVG/MIN/MAX(expr) WHERE predicate GROUP BY g` — directly on **fully homomorphically encrypted (FHE)** data held by an untrusted server, so the server learns *nothing* (not even access patterns or result size, in the strongest setting) and the client decrypts only the final aggregate. Correctness and full semantic security are *known to be achievable* by Gentry's FHE; the open problem is **cost**: getting the overhead low enough for interactive analytic workloads ($\sim$seconds on millions of rows), not the hours-to-days of naïve FHE.

Variants:
- **Counting:** encrypted `COUNT(*) WHERE p` — homomorphic predicate then sum of selection bits.
- **Linear aggregation:** `SUM`/`AVG` — homomorphic dot-product, FHE's best case.
- **Comparison-heavy:** `MIN`/`MAX`/`GROUP BY`/`TOP-K` — require homomorphic comparison and sorting, the expensive case.
- **Result-hiding vs. result-size-revealing** (whether output cardinality leaks).

## 2. Mathematical Foundations
An FHE scheme provides $\mathrm{Enc}, \mathrm{Dec}, \mathrm{Eval}$ with $\mathrm{Dec}(\mathrm{Eval}(f, \mathrm{Enc}(x))) = f(x)$ and **IND-CPA** security; **Gentry (STOC'09)** showed bootstrapping yields *fully* homomorphic evaluation of any circuit. Security rests on **(Ring-)Learning With Errors (RLWE)**: distinguishing $(a, a\cdot s + e)$ from uniform is hard, with $e$ a small Gaussian noise term. Each homomorphic op grows the noise; **bootstrapping** refreshes ciphertexts at high cost.

Scheme families: **BGV/BFV** (exact integer/modular arithmetic, SIMD "batching" via CRT packing of thousands of slots), **CKKS** (approximate real arithmetic, ideal for averages/analytics), **TFHE/FHEW** (fast programmable bootstrapping, good for comparisons/non-linear functions). SQL aggregation maps to: predicate $\to$ encrypted boolean circuit (cheap in TFHE), selection-and-sum $\to$ batched multiply-add (cheap in BGV/CKKS with packing), $\mathrm{MIN/MAX}/\mathrm{sort} \to$ depth-$O(\log n)$ comparison networks (expensive, bootstrap-heavy). Multiplicative depth $d$ and noise budget govern whether bootstrapping is needed; **AGM-style** padding is needed if output size must be hidden.

## 3. State of the Art (SOTA)
- **Theory/scheme-SOTA:** **CKKS** (Cheon–Kim–Kim–Song, ASIACRYPT'17) for approximate analytics; **BGV** (Brakerski–Gentry–Vaikuntanathan, ITCS'12); **TFHE** (Chillotti et al., 2016–20) programmable bootstrapping. Libraries: **Microsoft SEAL, OpenFHE, HEAAN, Concrete (Zama), HElib, Lattigo**.
- **Systems-SOTA:** **CryptDB** (SOSP'11, additively-homomorphic Paillier for SUM only — not FHE); **HEDA / SHE-based analytics**; **Symmetria, Arx**; **Zama's Concrete-ML / fhEVM** and **TenSEAL** for encrypted compute pipelines; FHE-accelerated SQL prototypes over CKKS/BFV. **HE-friendly query compilers** (e.g., **EVA**, MSR) auto-schedule packing and rescaling.

## 4. Upper Bound
For linear aggregates (`SUM`/`COUNT`/`AVG`) with batched BGV/CKKS, amortized cost is **polylogarithmic per slot** with thousands of records packed per ciphertext — concretely sub-second for SUM over $10^6$ rows on a single packed evaluation, in the **RLWE/IND-CPA model**. Predicate evaluation adds depth proportional to the predicate's boolean complexity. The full leveled-FHE cost is $\mathrm{poly}(\lambda, d)$ for a depth-$d$ circuit; bootstrapping is $\tilde{O}(\lambda)$ amortized per refresh. Hardware FHE accelerators report 1–3 orders of magnitude speedups, moving comparison-heavy queries toward practicality *(frontier — verify)*. So the upper bound exists and is *correct and fully secure* — the constant is the problem.

## 5. Lower Bound
- **No sublinear server work:** any FHE query touching all encrypted rows is $\Omega(n)$ in server work (the server cannot skip ciphertexts without leaking which it skipped); access-pattern hiding forbids indexing, so a fully oblivious encrypted aggregate is inherently a **linear scan**.
- **Ciphertext expansion:** RLWE ciphertexts are $\Omega(\lambda)$ larger than plaintext; the multiplicative overhead over plaintext arithmetic is bounded below by the noise-growth/bootstrapping cost — there is no known FHE with $o(\lambda)$ per-op overhead.
- **Hardness basis:** security reduces to worst-case lattice problems (GapSVP/SIVP) via RLWE; breaking it would refute lattice hardness assumptions. No information-theoretic FHE is possible (would imply impossible-rate private information retrieval bounds).

## 6. The Gap
The gap is **purely the constant/overhead factor**, not feasibility — hence *solved-but-impractical*. We can compute any aggregate with full security; we cannot (yet) do comparison/sort-heavy analytics at interactive latency without hardware. Closing it requires: better packing/scheduling so SQL maps to few high-throughput SIMD operations; cheaper programmable bootstrapping for comparisons; and FHE accelerators (ASIC/GPU) bringing the $10^4$–$10^6\times$ slowdown down to $10$–$100\times$. For *linear* aggregation the gap is already small; for `MIN`/`MAX`/`GROUP BY`/joins it remains large.

## 7. Current Research (as of June 2026)
Directions: **FHE hardware accelerators** (DARPA DPRIVE program; designs like **CraterLake, BTS, ARK, SHARP**) targeting $\ge 10^4\times$ speedups *(frontier — verify)*; **transciphering** (symmetric-cipher-to-FHE conversion, e.g., **Pasta/HERA/Rasta**) to cut ciphertext upload cost; HE-aware query compilers that auto-batch and minimize multiplicative depth; **hybrid FHE+TEE** offload for the comparison-heavy operators. Groups: Cheon (Seoul Nat'l / CryptoLab), Vaikuntanathan (MIT), Chillotti/Zama, Halevi/Shoup (HElib), Microsoft Research Cryptography (SEAL/EVA), Polyakov (OpenFHE, Duality).

## 8. Future Work
- Practical encrypted `GROUP BY`/`JOIN`/`TOP-K`, not just scalar aggregates.
- Standardized FHE-SQL semantics and a cost-based HE query optimizer.
- Co-design of accelerators with database operators (FHE-native columnar layout).
- Reducing client-side bootstrapping/key-management burden for analytic clients.
- Composable FHE + DP so the decrypted aggregate is also privacy-protected.

## 9. Key References
- **[Foundational]** Gentry. *Fully Homomorphic Encryption Using Ideal Lattices.* STOC, 2009. — [DOI](https://doi.org/10.1145/1536414.1536440)
- **[Foundational]** Brakerski, Gentry, Vaikuntanathan. *(Leveled) Fully Homomorphic Encryption without Bootstrapping.* ITCS, 2012. — [DOI](https://doi.org/10.1145/2090236.2090262)
- **[SOTA]** Cheon, Kim, Kim, Song. *Homomorphic Encryption for Arithmetic of Approximate Numbers (CKKS).* ASIACRYPT, 2017. — [DOI](https://doi.org/10.1007/978-3-319-70694-8_15)
- **[SOTA]** Chillotti, Gama, Georgieva, Izabachène. *TFHE: Fast Fully Homomorphic Encryption over the Torus.* Journal of Cryptology, 2020. — [DOI](https://doi.org/10.1007/s00145-019-09319-x)
- **[SOTA]** Dathathri, Kostova, Saarikivi, et al. *EVA: An Encrypted Vector Arithmetic Language and Compiler for Efficient Homomorphic Computation.* PLDI, 2020. — [DOI](https://doi.org/10.1145/3385412.3386023)
- **[Survey]** Acar, Aksu, Uluagac, Conti. *A Survey on Homomorphic Encryption Schemes: Theory and Implementation.* ACM Computing Surveys, 2018. — [DOI](https://doi.org/10.1145/3214303)

## 10. Worked Example

Evaluate `SELECT COUNT(*) FROM T WHERE status = 1` over $n=4096$ encrypted rows using CKKS/BGV **SIMD packing**. One ciphertext packs $N=4096$ slots, so the whole `status` column lives in a single ciphertext $\mathbf{c}_{\text{status}}=\mathrm{Enc}(s_0,\dots,s_{4095})$.

The predicate `status = 1` here is just the bit itself, so `COUNT` = sum of the slots. Steps:
1. Multiply nothing (predicate is the value) — $0$ multiplicative depth for this case; an equality test against a constant $k$ would add depth $\lceil\log_2 p\rceil$ for a degree-$(p-1)$ comparison polynomial.
2. **Slot-sum** via $\log_2 N = 12$ rotate-and-add steps: rotate by $1,2,4,\dots,2048$, adding each time, so slot $0$ ends holding $\sum_i s_i$.

Cost: $12$ homomorphic rotations + $12$ additions on one ciphertext — sub-second, with multiplicative depth $\approx 0$, so **no bootstrapping**. Contrast `MIN(salary)`: an oblivious comparison network over $4096$ packed values needs depth $\Theta(\log n)=12$ *comparisons*, each a bootstrap-heavy programmable-bootstrap in TFHE — orders of magnitude slower. This is exactly the linear-aggregate-cheap / comparison-expensive split that makes the problem *solved-but-impractical*.

---
*Part of the [DBMS Research catalog](../../README.md).*
