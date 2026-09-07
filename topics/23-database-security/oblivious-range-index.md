---
id: 23-database-security/oblivious-range-index
title: "Oblivious Range and Index Queries"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Oblivious Range and Index Queries

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/oblivious-range-index` · **Status:** open

## 1. Problem Statement

A client outsources a table of $N$ records to an untrusted server and issues **range queries** (`a ≤ key ≤ b`) or **index lookups** through a B-tree. The server, even while honestly serving requests, observes the **access pattern** — which physical blocks are touched, in what order, and how often. We want a data structure that answers range/index queries while making this observable transaction trace *computationally indistinguishable* across any two query sequences of equal length and equal result size. The open question is whether one can do this with **sublinear (ideally $O(\text{polylog } N + r)$)** server work per query, where $r$ is the result size, **without** the $\Omega(\log^2 N)$ or worse per-access blowup that generic ORAM imposes on each of the $r$ traversed nodes.

- **Decision variant:** does there exist an oblivious range index with $o(\log^2 N)$ amortized overhead per returned record under standard cryptographic assumptions?
- **Optimization variant:** minimize bandwidth/server-compute overhead subject to a fixed obliviousness (indistinguishability) guarantee and client storage $O(\text{polylog } N)$.
- **Counting variant:** oblivious range-*count* (return $r$ only) without revealing which keys fall in $[a,b]$.

## 2. Mathematical Foundations

Let a logical access sequence be $\vec{x} = (x_1,\dots,x_m)$ over operations. A scheme with transcript $\mathsf{T}(\vec{x})$ is **oblivious** if for all $\vec{x},\vec{y}$ with $|\vec{x}|=|\vec{y}|$ (and matching result cardinalities), $\mathsf{T}(\vec{x}) \stackrel{c}{\approx} \mathsf{T}(\vec{y})$.

The baseline is **Oblivious RAM (ORAM)**: Goldreich–Ostrovsky proved a $\Omega(\log N)$ amortized lower bound on bandwidth for ORAM in the "balls-in-bins" model; Larsen–Nielsen (CRYPTO 2018) raised this to $\Omega(\log N)$ unconditionally in the cell-probe model for *any* online ORAM. Path ORAM achieves $O(\log^2 N)$ (or $O(\log N)$ with large blocks).

Naively wrapping a B-tree of height $h = O(\log_B N)$ in ORAM costs $O(h \cdot \text{ORAM}(N))$ per pointer-chase, and range queries that touch $r$ leaves pay this per leaf — the **"pointer-chasing tax."** The structural difficulty is that B-tree navigation is *sequential and data-dependent*: each node read determines the next, so locality cannot be hidden cheaply. Formally this resembles an oblivious version of the **predecessor problem**, linking to cell-probe bounds (Pătraşcu–Thorup) on predecessor search.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Oblivious data structures (Wang, Nayak, Liu, Shi et al., CCS 2014) give $O(\log^2 N)$ per operation for maps/trees by exploiting bounded "access locality" of pointer-based structures. **OPRAM** and **OptORAMa** (Asharov et al., EUROCRYPT 2020) achieve asymptotically optimal $O(\log N)$ ORAM, improving the underlying primitive but not removing the per-node multiplier for range traversal.
- **Systems-SOTA:** **Oblix** (Mishra et al., S&P 2018) builds an oblivious sorted multimap (doubly-oblivious index) atop Intel SGX with ORAM; **ObliDB** (Eskandarian–Zaharia, PVLDB 2019) gives oblivious relational operators including range scans inside enclaves. **Snoopy** (SOSP 2021) scales oblivious key-value storage. These rely on trusted hardware to cut constants, not to beat the asymptotic bound.

## 4. Upper Bound

Best general upper bound: $O(\log^2 N)$ amortized server bandwidth per *point* operation (oblivious map/AVL via Path ORAM), and $O(r \log^2 N + \log^2 N)$ for a range returning $r$ records, in the **client-server bandwidth model** under standard ORAM assumptions (PRFs / one-way functions). With enclave-resident position maps and block sizes $\Omega(\log^2 N)$, this drops to $O(\log N)$ per node — still $O(r\log N)$ for the range — in the **trusted-hardware model**.

## 5. Lower Bound

Larsen–Nielsen (CRYPTO 2018): any online ORAM (hence any oblivious index reducible to it) has $\Omega(\log N)$ amortized cell-probe overhead, *unconditionally*. Jacob–Larsen–Nielsen (2019) extend $\Omega(\log N)$ lower bounds to oblivious **stacks, queues, and search trees**, showing the logarithmic tax is intrinsic to oblivious pointer-following, not an artifact of generic ORAM. No lower bound, however, forces the *multiplicative* $\log^2$ or the per-leaf cost for *batched* range output — leaving room above $\Omega(\log N + r)$.

## 6. The Gap

The point-query gap is essentially **closed** at $\Theta(\log N)$ (Larsen–Nielsen lower bound matched by OptORAMa-based structures, modulo block size). The genuinely **open** gap is for **range** queries: lower bound $\Omega(\log N + r)$ vs. upper bound $O(r\log N)$ (hardware) / $O(r\log^2 N)$ (bandwidth). Closing it means either (a) an oblivious B-tree whose $r$ returned leaves share traversal work so total cost is $O(\log N + r \cdot \text{polyloglog})$, or (b) a lower bound proving the per-leaf logarithmic factor is unavoidable for range output.

## 7. Current Research (as of June 2026)

Active directions: **locality-preserving oblivious structures** that batch the $r$ leaves into a single ORAM-eviction pass; **differentially-oblivious** range indexes (Chan–Chung–Maggs–Shi) that trade a small access-pattern $\epsilon$-leakage for near-linear-in-$r$ cost — a relaxation gaining traction as a principled middle ground. Enclave teams (Berkeley RISELab descendants, EPFL DEDIS) push doubly-oblivious B+-trees with vectorized oblivious comparators. *(frontier — verify)* Several 2025 preprints claim oblivious range scans approaching $O(\log N + r)$ under differential obliviousness rather than full indistinguishability.

## 8. Future Work

- Tight lower bound for *batched* oblivious range output (does $r\log$ collapse to $r$?).
- Oblivious **secondary indexes** and multi-dimensional (oblivious R-tree / kd-tree) range search.
- Composability of oblivious indexes under concurrent multi-client access without serializing the position map.
- Quantitative bridge between differential obliviousness and full obliviousness for ranges.

## 9. Key References

- **[Foundational]** Goldreich, O., Ostrovsky, R. *Software Protection and Simulation on Oblivious RAMs.* JACM, 1996. — [DOI](https://doi.org/10.1145/233551.233553)
- **[Foundational]** Stefanov, E., van Dijk, M., Shi, E., et al. *Path ORAM: An Extremely Simple Oblivious RAM Protocol.* CCS, 2013. — [DOI](https://doi.org/10.1145/2508859.2516660)
- **[SOTA]** Wang, X.S., Nayak, K., Liu, C., Shi, E., et al. *Oblivious Data Structures.* CCS, 2014. — [DOI](https://doi.org/10.1145/2660267.2660314)
- **[SOTA]** Larsen, K.G., Nielsen, J.B. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96881-0_18)
- **[SOTA]** Asharov, G., Komargodski, I., Lin, W.-K., Nayak, K., Peserico, E., Shi, E. *OptORAMa: Optimal Oblivious RAM.* EUROCRYPT, 2020. — [DOI](https://doi.org/10.1007/978-3-030-45724-2_14)
- **[SOTA]** Eskandarian, S., Zaharia, M. *ObliDB: Oblivious Query Processing for Secure Databases.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364331)

## 10. Worked Example

**The pointer-chasing tax on a range query.** Outsource $N = 2^{20}$ records keyed $1\ldots N$ in a B-tree with branching $B=16$, so height $h=\log_{16} 2^{20} = 5$. A range query $20{,}000 \le \text{key} \le 20{,}049$ returns $r=50$ records spanning, say, $3$ adjacent leaves.

*Non-oblivious cost:* one root-to-leaf descent ($5$ node reads) plus a leaf scan — $\approx 5 + 3 = 8$ block accesses; the server learns nothing extra because it sees nothing hidden, but it *does* see exactly which blocks.

*Wrapped in Path ORAM* (per-access cost $O(\log^2 N) = (\log 2^{20})^2 = 400$ block transfers): every one of the $h=5$ pointer-chases is a separate oblivious access, and each of the $3$ leaves is fetched obliviously too:

$$\text{cost} \approx (h + r_{\text{leaves}})\cdot O(\log^2 N) = (5+3)\cdot 400 = 3200 \text{ block transfers.}$$

So obliviousness inflates $8 \to 3200$, a $400\times$ blowup — the per-node $\log^2 N$ multiplier. The Larsen–Nielsen $\Omega(\log N)=\Omega(20)$ lower bound says *some* logarithmic tax per access is unavoidable, but it does **not** justify the full $r\cdot\log^2 N$: the open question is whether the $50$ returned records can share one $O(\log N)$ traversal, collapsing the cost toward $O(\log N + r)\approx 20 + 50 = 70$.

---
*Part of the [DBMS Research catalog](../../README.md).*
