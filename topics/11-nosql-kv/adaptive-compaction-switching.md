# Adaptive Compaction Policy Switching

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/adaptive-compaction-switching` · **Status:** empirically-open

## 1. Problem Statement

An LSM-tree's compaction *policy* — **leveled** (one sorted run per level, low read/space amplification, high write amplification), **tiered** (many runs per level, low write amplification, high read/space amplification), or a **hybrid** interpolation (e.g. lazy-leveling, fluid LSM) — is normally fixed at configuration time. Real workloads **drift**: a write-heavy ingest burst favors tiering, while a subsequent read-heavy serving phase favors leveling. **Adaptive compaction policy switching** asks: detect workload drift online and *transition the on-disk layout* from one policy to another **safely** — without an unbounded compaction stall, without violating read-latency SLOs during the transition, and without thrashing (oscillating policies under noisy signals).

Variants:
- **Decision:** given current layout, target policy, and a transition budget (IO/CPU per unit time), does a transition plan exist that reaches the target layout while keeping read amplification $\le \beta$ and write-stall $\le \tau$ throughout?
- **Optimization (offline):** given a known future workload trace, choose the *switching schedule* (which policy, when, via which intermediate layouts) minimizing total weighted cost $w_W\!\cdot\!WA + w_R\!\cdot\!RA + w_S\!\cdot\!SA$ plus a **switching cost** charged for layout reorganization.
- **Online/competitive:** the trace is revealed incrementally; minimize competitive ratio against the best offline policy *with* switching costs (a metrical-task-system / ski-rental flavor).

The hard, realistic regime is online switching under bounded background budget with hysteresis to suppress thrashing.

## 2. Mathematical Foundations

Let $N$ entries, buffer size $B$, size ratio $T$, levels $L=\lceil\log_T(N/B)\rceil$. The fluid-LSM parameterization $(T,K,Z)$ — runs per level, runs at the largest level, merge greediness — places leveling ($K{=}Z{=}1$) and tiering ($K{=}Z{=}T{-}1$) as endpoints of a continuum (Dostoevsky). A *policy* is thus a point $\pi\in\Pi$ in this design space; **switching** is a trajectory $\pi(t)$ through $\Pi$.

Switching has a **reorganization cost**: converting tiered runs at a level into a single leveled run is a full merge of that level, $\Theta(N_i/B)$ I/Os for level $i$ of size $N_i$, dominated by the largest levels — so an eager full re-layout costs $\Theta(N/B)$ I/Os, the same order as one round of external-memory sorting ($\Omega((N/B)\log_{M/B}(N/B))$, Aggarwal–Vitter, bounds the cumulative work).

The online problem is naturally a **metrical task system / ski-rental** instance: pay incremental cost to stay in policy $\pi$ under the current workload, or pay a one-time switching cost to move. With two policies and symmetric switch cost $C$, the classic ski-rental $e/(e{-}1)$-competitive (randomized) and $2$-competitive (deterministic) bounds apply to *when* to switch; the layout-transition planning is the additional, LSM-specific layer.

$$ \min_{\pi(\cdot)} \int_0^Tig(w_W WA(\pi,t)+w_R RA(\pi,t)+w_S SA(\pi,t)ig)\,dt \;+\; \sum_{\text{switches}} C\,(\pi_{k}\!\to\!\pi_{k+1}) \quad \text{s.t. budget } \rho,\; RA\le\beta. $$

The RUM conjecture (Athanassoulis et al., EDBT 2016) bounds the per-policy Pareto surface; switching navigates *between* surfaces but cannot escape the frontier.

## 3. State of the Art (SOTA)

**Systems-SOTA:** RocksDB supports changing compaction style but a leveled↔universal switch in practice requires a costly manual reorganization and is treated as offline. Cassandra allows `ALTER TABLE` to change `compaction` strategy, triggering a background re-compaction with no transition-cost guarantees. **Dostoevsky / Fluid LSM** (Dayan & Idreos, SIGMOD 2018) makes the *space* of policies continuous and navigable; **Endure** (Huynh et al., VLDB 2022) tunes robustly under workload *uncertainty* but picks a static-robust point rather than switching online. Learned/RL compaction pickers (Idreos group; *Spooky*, Dayan et al. 2022, for partial compaction) are the systems frontier for *adaptivity*.

**Theory-SOTA:** no tight competitive analysis exists for the LSM policy-switching problem with reorganization cost; the closest formal handle is ski-rental / MTS, applied only to the *timing* of a switch, not the layout-transition plan.

## 4. Upper Bound

For the *timing* sub-problem (two policies, switch cost $C$), deterministic $2$-competitive and randomized $e/(e{-}1)$-competitive bounds hold in the online (adversarial) model via ski-rental. For the *transition plan*, the best-known guarantee is the trivial eager re-layout at $\Theta(N/B)$ I/Os, or **incremental/lazy** switching that amortizes reorganization into ordinary compaction (so new SSTables adopt the target policy while old ones age out) — empirically bounded stall but **no proven competitive ratio** for the full $WA\times RA\times SA$ objective with budget $\rho$. No constant-competitive algorithm against an adaptive adversary is known for the joint problem.

## 5. Lower Bound

Deterministic ski-rental gives a matching $2$-competitive lower bound for the symmetric two-policy *timing* problem (adversarial online model). Reorganization work is lower-bounded by external-memory sorting: $\Omega((N/B)\log_{M/B}(N/B))$ I/Os (Aggarwal–Vitter, 1988) to re-sort a tiered level into a leveled run, so any policy reaching a fully-leveled layout from a fully-tiered one pays $\Omega(N/B)$ I/Os — a hard floor on switch cost. The RUM conjecture supplies an informal impossibility on simultaneously optimizing Read/Update/Memory, bounding what any reachable policy can deliver. No unconditional lower bound is known for the *online weighted-cost-plus-switching* objective under a compaction budget.

## 6. The Gap

The timing sub-problem is essentially closed (tight ski-rental bounds). The **joint** problem — *when* to switch **and** *how* to plan the layout transition under a bounded background budget while honoring read-latency SLOs and suppressing thrashing — is genuinely open: there is no algorithm with a competitive ratio matching a lower bound for the full three-amplification objective with switching cost. The status is *empirically-open* — incremental/lazy switching works well in practice but lacks worst-case guarantees, and no impossibility theorem rules them out. Closing the gap needs either a constant-competitive joint scheduler with a matching lower bound, or a hardness proof in the MTS/online model.

## 7. Current Research (as of June 2026)

Active directions: RL/learned policies that detect drift and re-tune online (Idreos group, Harvard DASlab), extending Endure-style robust tuning toward *online* re-selection rather than one-shot robust points *(frontier — verify)*; **hysteresis / change-point detection** on workload signals (read/write ratio, range-vs-point mix) to gate switches and prevent oscillation; **partial / sub-range switching** that applies different policies to different key ranges based on per-range access skew *(frontier — verify)*; and disaggregated/cloud-native LSM where compaction (and thus reorganization) is offloaded to elastic remote compute, changing the switch-cost calculus (RocksDB-Cloud, Neon-style storage separation) *(frontier — verify)*. Benchmarking continues via Endure/K-V-bench-style harnesses with explicitly drifting traces.

## 8. Future Work

- A provably constant-competitive online policy-switching scheduler accounting for reorganization cost (or an impossibility proof in the MTS model).
- Formal change-point/hysteresis models with bounded thrashing under noisy workload signals.
- Per-key-range adaptive policies with a unified cost model spanning ranges.
- Switch-cost models on disaggregated storage where reorganization IO is elastic and metered.
- Joint online optimization of policy *and* Bloom-filter/cache memory under one budget.

## 9. Key References

- **[Foundational]** Patrick O'Neil, Edward Cheng, Dieter Gawlick, Elizabeth O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[SOTA]** Niv Dayan, Stratos Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Andy Huynh, Harshal Chaudhari, Evimaria Terzi, Manos Athanassoulis. *Endure: A Robust Tuning Paradigm for LSM Trees under Workload Uncertainty.* VLDB 2022. — [arXiv](https://arxiv.org/abs/2110.13801)
- **[Foundational]** Manos Athanassoulis, Michael S. Kester, Lukas M. Maas, Radu Stoica, Stratos Idreos, Anastasia Ailamaki, Mark Callaghan. *Designing Access Methods: The RUM Conjecture.* EDBT 2016. — [PDF](https://openproceedings.org/2016/conf/edbt/paper-12.pdf)
- **[Foundational]** Anna R. Karlin, Mark S. Manasse, Lyle A. McGeoch, Susan Owicki. *Competitive Randomized Algorithms for Nonuniform Problems (ski-rental / MTS).* Algorithmica, 1994. — [DOI](https://doi.org/10.1007/BF01189993)
- **[Foundational]** Alok Aggarwal, Jeffrey Scott Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)

## 10. Worked Example

A store runs **tiered** during a write-heavy ingest, then the workload flips read-heavy, making **leveled** preferable. Staying tiered costs an extra $r = 4$ units/s of read amplification; the one-time switch (full merge to leveled) costs $C = 30$ units. This is exactly **ski-rental**: "rent" (stay tiered, pay $r$/s) vs. "buy" (switch, pay $C$ once).

The deterministic 2-competitive rule: switch once accumulated extra cost reaches $C$, i.e. at $t^\* = C/r = 30/4 = 7.5$s. If the read-heavy phase actually lasts only $5$s, the optimal offline choice was *never switch* (cost $5\times4 = 20 < 30$); our rule also never reaches $7.5$s, so it pays $20$ — optimal here. If the phase lasts forever, offline buys immediately ($30$); our rule pays $7.5\times4 = 30$ renting, then $30$ to buy $= 60 = 2\times30$, hitting the 2-competitive bound exactly.

Separately, the *transition* itself is not free: re-sorting a tiered level of size $N_i$ into one leveled run costs $\Theta(N_i/B)$ I/Os, dominated by the largest level — the $\Omega(N/B)$ floor (Aggarwal–Vitter).

---
*Part of the [DBMS Research catalog](../../README.md).*
