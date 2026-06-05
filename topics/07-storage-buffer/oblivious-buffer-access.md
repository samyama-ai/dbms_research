# Encrypted/Oblivious Buffer Access Patterns

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/oblivious-buffer-access` · **Status:** open

## 1. Problem Statement

An adversary observing the **sequence of physical page/frame accesses** in the buffer pool (via shared-memory side channels, cache timing, page-fault traces in an SGX/enclave, or a malicious storage layer) can infer secret query parameters and data distributions even when page *contents* are encrypted. The problem: serve a logical access trace while making the **observable physical access pattern reveal nothing** about the logical trace, with **low overhead** (bandwidth/time blowup as small as possible) and within a bounded buffer.

Formally: a client issues logical accesses $(op_i, addr_i, data_i)$; the buffer/storage substrate produces a physical trace $\mathcal{A}$. **Access-pattern obliviousness** requires that for any two equal-length logical sequences, the induced distributions over $\mathcal{A}$ are **computationally (or statistically) indistinguishable**.

Variants:
- **Full ORAM-style:** hide every access (read & write) of a sequence of equal length.
- **Differentially-private access:** hide *changes* between neighboring traces, allowing bounded leakage for lower overhead.
- **Decision/leakage-quantification:** given a policy, measure mutual information $I(\text{logical};\mathcal{A})$.

## 2. Mathematical Foundations

**Oblivious RAM (ORAM).** The canonical primitive: a compiler turning any RAM program into one whose physical access pattern is independent of inputs. **Goldreich–Ostrovsky** proved a logarithmic-factor lower bound; **Path ORAM** (Stefanov et al., CCS 2013) achieves $O(\log N)$ bandwidth blowup with $O(\log N)\cdot\omega(1)$ client storage. The **Goldreich–Ostrovsky / Larsen–Nielsen** bound shows $\Omega(\log N)$ overhead is **unavoidable** for any online ORAM in the cell-probe model.

**Information-theoretic target.** Obliviousness $\equiv$ the observable trace's distribution is a fixed function of the *length* only: $I(\text{secret}; \mathcal{A} \mid \text{length}) = 0$ (statistical) or negligible (computational).

**Differential privacy relaxation.** A weaker, cheaper target: the access mechanism is $(\epsilon,\delta)$-DP over neighboring logical traces, bounding leakage by $e^\epsilon$ rather than zero — **differentially-oblivious** algorithms (Chan–Chung–Maggs–Shi 2019) beat the $\Omega(\log N)$ wall for some primitives.

**Oblivious data structures.** Buffer pools need oblivious *maps/queues/priority queues* (for the replacement metadata too — eviction-order leaks!), studied as **oblivious data structures** (Wang et al., CCS 2014). The replacement policy itself must be oblivious or it leaks reuse.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **Oblix** (Mishra et al., S&P 2018), **ZeroTrace** (Sasy et al., NDSS 2018) and **Obladi** (Crooks et al., OSDI 2018 — oblivious ACID transactions) bring ORAM into trusted-hardware databases; **Opaque** (Zheng et al., NSDI 2017) provides oblivious Spark operators. **PathORAM** and its recursive/parallel variants are the workhorse. For analytics, **oblivious join/sort/group-by** operators (sorting-network-based) dominate. Buffer-pool-specific obliviousness is mostly subsumed into enclave-side ORAM rather than treated as a distinct replacement problem.

**Theory-SOTA.** $O(\log N)$ ORAM (Path ORAM; OptORAMa, Asharov et al. 2020, achieves optimal $O(\log N)$ *with* $O(1)$ client memory and statistical security). Differential obliviousness (Chan et al. 2019) for sub-logarithmic leakage-bounded primitives.

## 4. Upper Bound

- **General obliviousness:** $O(\log N)$ amortized bandwidth blowup (OptORAMa, Asharov–Komargodski–Lin–Nayak–Peserico–Shi 2020) — optimal, in the balls-in-bins / RAM model.
- **Path ORAM:** $O(\log N)$ bandwidth, $O(\log N)\,\omega(1)$ client storage, $O(\log^2 N/\log\log N)$ for recursive position map.
- **Differentially-oblivious** sort/merge/group-by: $O(\log\log N)$ or $O(1)\cdot$-leakage variants beating full ORAM for those operators (Chan et al.).
- **Oblivious replacement metadata:** doable at $O(\log N)$ per op via oblivious priority queue, but a tight bound for *policy-faithful* oblivious eviction is unsettled.

## 5. Lower Bound

- **Goldreich–Ostrovsky (1996)** and the strengthened **Larsen–Nielsen (CRYPTO 2018)**: any online ORAM has $\Omega(\log N)$ cell-probe overhead — **information-theoretic / cell-probe**, holds even computationally and even for offline in some regimes.
- The bound applies to the buffer-access-hiding problem since hiding buffer accesses is at least as hard as ORAM on the page address space.
- For the **DP relaxation**, lower bounds are weaker — some primitives provably need only $\Omega(\log\log N)$ — but full-trace zero-leakage cannot beat $\Omega(\log N)$.

## 6. The Gap

For the *generic* hiding problem the gap is **closed**: OptORAMa meets the $\Omega(\log N)$ Larsen–Nielsen bound. What is **open** is everything buffer-pool-specific: (i) **policy-aware obliviousness** — can we run ARC/LRU-quality replacement while keeping eviction order oblivious, and at what overhead?; (ii) the **right leakage/overhead trade-off** for buffer pools via differential obliviousness, where the constant in front of $\log N$ and the achievable leakage budget are unsettled; (iii) **side-channel-faithful** models (page-fault, cache-timing, NUMA traffic) under which "oblivious" actually holds — current ORAM models the storage channel, not all enclave side channels. These are genuinely open.

## 7. Current Research (as of June 2026)

- **Differentially-oblivious DB operators** trading provable leakage budgets for big overhead cuts (Cornell, CMU, NUS). *(frontier — verify)*
- **Oblivious buffer/index structures** for confidential-computing DBs (SGX/TDX/SEV-SNP, CXL-attached secure memory). *(frontier — verify)*
- **Hardware-assisted ORAM** and oblivious memory controllers to cut the $\log N$ constant. *(frontier — verify)*
- Leakage-quantification frameworks measuring $I(\text{query};\text{access trace})$ for real engines.

## 8. Future Work

- Replacement policies that are simultaneously *competitive* (hit-ratio) and *oblivious* (eviction order leaks nothing), with proven overhead.
- Tight differential-obliviousness bounds for buffer management (leakage budget vs. blowup).
- Side-channel-complete threat models (page faults + timing + traffic) with end-to-end guarantees.
- Practical sub-$2\times$-overhead oblivious buffering via hardware (secure memory controllers, CXL).

## 9. Key References

- **[Foundational]** Goldreich, Ostrovsky. *Software Protection and Simulation on Oblivious RAMs.* JACM, 1996. — [DOI](https://doi.org/10.1145/233551.233553)
- **[Foundational]** Stefanov, van Dijk, Shi, et al. *Path ORAM: An Extremely Simple Oblivious RAM Protocol.* CCS, 2013. — [DOI](https://doi.org/10.1145/2508859.2516660)
- **[Foundational]** Larsen, Nielsen. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96881-0_18)
- **[SOTA]** Asharov, Komargodski, Lin, Nayak, Peserico, Shi. *OptORAMa: Optimal Oblivious RAM.* EUROCRYPT, 2020. — [DOI](https://doi.org/10.1007/978-3-030-45724-2_14)
- **[SOTA]** Crooks, Burke, Cecchetti, et al. *Obladi: Oblivious Serializable Transactions in the Cloud.* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/crooks)
- **[SOTA]** Chan, Chung, Maggs, Shi. *Foundations of Differentially Oblivious Algorithms.* SODA, 2019. — [DOI](https://doi.org/10.1145/3555984)

## 10. Worked Example

Consider a tiny index with $N=4$ pages stored in an enclave-backed buffer. A query plan issues the logical read sequence $\langle p_3, p_3, p_1\rangle$. A non-oblivious buffer would touch physical frames $\langle 3, \text{(hit)}, 1\rangle$ — the repeat reveals reuse, and the address $3$ leaks the secret key bucket.

Run a toy Path ORAM over a binary tree of $N=4$ leaves (height $\log_2 4 = 2$). Each logical access does: (1) look up the block's current leaf in the position map, (2) read the *entire root-to-leaf path* (3 buckets), (3) remap the block to a fresh random leaf, (4) write the path back. So both reads of $p_3$ fetch *different* random paths, and the access to $p_1$ is indistinguishable from them.

Cost: each logical op costs $3$ bucket transfers vs. $1$ demand fetch — a $\log N$-type blowup, exactly the $\Omega(\log N)$ Larsen–Nielsen wall. Observer sees three length-3 path reads to random leaves: $I(\text{logical};\mathcal{A}\mid\text{length})\approx 0$.

---
*Part of the [DBMS Research catalog](../../README.md).*
