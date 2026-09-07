---
id: 07-storage-buffer/nvm-buffer-placement
title: "NVM-Aware Buffer Management and Page Placement"
topic: 07-storage-buffer
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# NVM-Aware Buffer Management and Page Placement

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/nvm-buffer-placement` · **Status:** empirically-open

## 1. Problem Statement
Byte-addressable persistent memory (PMEM/NVM, e.g. Intel Optane DC PMM, and emerging CXL-attached persistent tiers) sits between DRAM and SSD in latency, capacity, and persistence. It offers DRAM-like random access but with **asymmetric read/write cost** (writes are ~2–4× slower and consume limited endurance) and supports persistence without a flush-to-block-device step. The problem: given a three-tier hierarchy (DRAM buffer · NVM tier · SSD/disk), decide for each page **(a)** which tier it resides in, **(b)** when to migrate it, and **(c)** whether NVM is used as a *cache* (volatile-style buffer extension) or as the *primary persistent store* (so writes can be persisted in place, shrinking the write-ahead log path).

Variants:
- **Decision:** Given a fixed access trace and tier capacities, does a placement exist whose total cost (read + asymmetric write + migration) is below budget $B$? (This is NP-hard in general — it generalizes weighted offline caching with non-uniform fetch/eviction costs.)
- **Optimization (offline):** Minimize total weighted cost over the trace.
- **Online:** Decide placement/migration with no future knowledge; measure competitive ratio against the offline optimum.

## 2. Mathematical Foundations
Model the hierarchy as tiers $T_0$ (DRAM, size $k_0$), $T_1$ (NVM, size $k_1$), $T_2$ (disk, unbounded). Each access to page $p$ at time $t$ is a read or write. Define per-tier costs: read cost $r_i$, write cost $w_i$ with $w_1 > r_1$ (asymmetry), and migration cost $m_{i\to j}$. The objective is

$$\min \sum_{t} \big( c_{\text{access}}(p_t, \text{tier}(p_t,t)) \big) + \sum_{\text{migrations}} m_{i\to j}.$$

This is **weighted caching with two cache levels and asymmetric read/write costs**. Single-level weighted caching is the classic $k$-server-style paging problem: LRU is $k$-competitive and no deterministic online algorithm beats $k$; randomized $O(\log k)$ is achievable (Bansal–Buchbinder–Naor primal–dual). The NVM twist adds **write-asymmetry**, modeled in the *asymmetric read/write external-memory (ARW)* model of Blelloch et al., where writes cost $\omega \gg 1$ and reads cost 1; sorting and many primitives have revised $\Theta$ bounds under this asymmetry. Endurance adds a budget constraint $\sum \mathbb{1}[\text{write to cell}] \le E$, turning it into a constrained online problem.

## 3. State of the Art (SOTA)
- **Systems:** *FOEDUS* (Kimura, SIGMOD 2015) — dual in-memory + NVM page design. *SOFORT* / *Peloton-NVM* hybrid SCM-DRAM engines (Oukid et al., DaMoN 2014–17). *Spitfire* (Zhou, Arulraj et al., SIGMOD 2021) — a learned three-tier (DRAM-NVM-SSD) buffer manager using probabilistic admission/migration. *PACMAN*, *Viper* (Benson et al., VLDB 2021) — NVM-optimized KV layout.
- **Theory:** ARW-model algorithms (Blelloch, Fineman, Gibbons, Gu, Shun, 2018) give write-efficient sorting/search; two-level weighted caching competitive results derive from the BBN primal–dual framework.
- Hardware caveat: Intel discontinued Optane (2022); the frontier has shifted to **CXL-attached memory** tiers, which reopens placement questions with different latency/coherence assumptions.

## 4. Upper Bound
Offline optimum is poly-time computable as min-cost flow only in restricted (single-tier, uniform-cost) cases; the general two-tier asymmetric problem is solved exactly only by ILP/DP exponential in tiers. Online: the BBN primal–dual gives an $O(\log k)$-competitive randomized algorithm for weighted caching, which transfers to a single NVM-cache tier; for two coupled tiers the best rigorous bound is $O(\log(k_0+k_1))$ via reduction, but constants degrade with the asymmetry ratio $\omega$. Systems-SOTA (Spitfire) reports near-optimal cost empirically via tuned admission probabilities but offers **no competitive guarantee**.

## 5. Lower Bound
The offline two-tier weighted placement decision problem is **NP-hard** (reduction from weighted offline caching / partition with non-uniform costs). Online deterministic algorithms cannot beat $k$-competitiveness (standard adversary argument for paging), and randomized lower bound is $\Omega(\log k)$. Under endurance constraints, no online algorithm can bound write-amplification within a constant of OPT without future knowledge (adversary forces premature migrations). The ARW model gives matching $\Omega(\omega \cdot n/B \log_{\omega M/B} n)$-type write lower bounds for comparison sorting.

## 6. The Gap
For the *single* NVM-cache tier the $\Theta(\log k)$ randomized bound is essentially tight. The genuine open gap is the **coupled multi-tier asymmetric online problem with endurance**: no algorithm is known with a competitive ratio that is tight in both $\omega$ (asymmetry) and the tier ratio. Empirically, learned/adaptive placement (Spitfire) dominates static heuristics, but we lack a tight characterization of how far adaptive policies sit from OPT on real traces. Closing it requires either a competitive algorithm parameterized by $\omega$ or a matching lower bound that incorporates write-asymmetry into the caching adversary.

## 7. Current Research (as of June 2026)
- Re-targeting NVM placement results to **CXL memory tiering** (Type-3 devices), where persistence may be optional but the asymmetric/latency-tier structure persists *(frontier — verify)*.
- Learned and RL-based migration controllers extending Spitfire's probabilistic admission *(frontier — verify)*.
- Endurance-aware wear-leveling integrated with buffer replacement rather than handled below the FS.
- Groups: CMU Database Group (Pavlo, Arulraj), TUM (Neumann/Leis on storage hierarchies), HPI (Plattner/Oukid lineage), MIT/CMU on CXL pooling.

## 8. Future Work
- A competitive analysis that jointly captures write-asymmetry, migration cost, and endurance.
- Hybrid use of NVM as *both* log and buffer (in-place persist to shorten WAL critical path) with provable recovery cost.
- Co-design with CXL coherence semantics and far-memory pooling across nodes.
- Benchmarks that separate placement quality from raw device latency, so policies generalize across NVM/CXL/future media.

## 9. Key References
- **[Foundational]** Blelloch, Fineman, Gibbons, Gu, Shun. *Sorting with Asymmetric Read and Write Costs.* SPAA, 2015 (journal 2018). — [arXiv](https://arxiv.org/abs/1603.03505)
- **[Foundational]** Bansal, Buchbinder, Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[SOTA]** Zhou, Arulraj, Pavlo, Cohen. *Spitfire: A Three-Tier Buffer Manager for Volatile and Non-Volatile Memory.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452819)
- **[SOTA]** Kimura. *FOEDUS: OLTP Engine for a Thousand Cores and NVRAM.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2746480)
- **[SOTA]** Benson, Makait, Rabl. *Viper: An Efficient Hybrid PMem-DRAM Key-Value Store.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3461535.3461543)
- **[Survey]** Oukid, Lehner et al. *Data Management on Non-Volatile Memory: A Perspective.* (DaMoN / tutorial line), 2017. — [DOI](https://doi.org/10.1007/s13222-018-0301-1)

## 10. Worked Example

DRAM ($T_0$, 1 frame), NVM ($T_1$, 1 frame), disk ($T_2$, unbounded). Costs per op: DRAM read/write $=1/1$; NVM read $r_1=2$, write $w_1=8$ (asymmetry $\omega=4$); disk read $=20$; migration DRAM↔NVM $=3$. Access trace on a single hot page $p$: **R, W, R, W, W** (read-heavy then write-heavy).

**Policy A — keep $p$ in NVM** (no DRAM copy): cost $=r_1+w_1+r_1+w_1+w_1 = 2+8+2+8+8 = 28$.

**Policy B — promote $p$ to DRAM after first read** (pay one migration, then serve from DRAM, write back once at end): $r_1$ (first read from NVM, 2) $+\,3$ (migrate to DRAM) $+\,1+1+1+1$ (DRAM R/W/W/W) $+\,8$ (one write-back to NVM at eviction) $= 2+3+4+8 = 17$.

Policy B wins ($17 < 28$) because DRAM absorbs the **expensive NVM writes** ($w_1=8$ each): paying a fixed migration of 3 avoids three 8-cost writes. The crossover depends on $\omega$ — if NVM writes were cheap ($w_1=r_1=2$), Policy A would cost $10$ and migration wouldn't pay off. This write-asymmetry is exactly what classical $k$-competitive paging ignores.

---
*Part of the [DBMS Research catalog](../../README.md).*
