# Online Working-Set Estimation for Auto-Sizing

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/working-set-estimation` · **Status:** partially-solved
> **Verification note:** The cited AET title "Fast Miss Ratio Curve Modeling..." is the ACM Trans. Storage 2018 journal version (the original AET appeared as Hu et al., "Kinetic Modeling of Data Eviction in Cache," USENIX ATC 2016), so the "USENIX ATC, 2018" venue label is inexact.

## 1. Problem Statement

Given an online stream of page accesses $r_1, r_2, \dots, r_t$ over a universe of $N$ pages, continuously estimate the **resident working set** — the set (or count) of distinct pages whose retention materially improves the hit ratio — in **sublinear space** $s \ll N$, to drive **elastic buffer allocation** (grow/shrink the pool to track the working set). Concretely, maintain the **miss-ratio curve (MRC)** $f(c) = \Pr[\text{miss} \mid \text{cache size } c]$, or its working-set proxy $W(t,\tau) = |\{p : p \text{ accessed in } (t-\tau, t]\}|$ (Denning's working set), at all sizes from one pass.

Variants:
- **Estimation (counting):** report $|W|$ or the full reuse-distance histogram within $(\epsilon,\delta)$ error.
- **Decision:** "is the working set $> c$?" to trigger a resize.
- **Optimization:** choose the buffer size $c^\*$ minimizing $\text{cost}(c) = f(c)\cdot p_{\text{miss}} + c \cdot p_{\text{mem}}$ (miss penalty vs. memory rent), tracked online under drift.

## 2. Mathematical Foundations

**Reuse / stack distance.** For LRU, the miss ratio at size $c$ equals the fraction of references whose **reuse distance** (number of distinct pages since the last access to the same page) exceeds $c$ (Mattson et al. 1970). The MRC is thus the CDF of the reuse-distance distribution; computing it exactly costs $O(\log N)$ per access with an order-statistics tree, $O(N)$ space.

**Sublinear estimation.** The core subproblem is **distinct-element / $F_0$ estimation** and, more sharply, estimating the **reuse-distance distribution**. $F_0$ admits $(1\pm\epsilon)$ approximation in $O(\epsilon^{-2} + \log N)$ space (Kane–Nelson–Woodruff 2010, optimal). Spatial sampling — keep only references whose hash $h(p) < T$ — yields the **SHARDS** estimator: an unbiased MRC from $O(1)$ tracked keys.

**Concentration.** With a sampling rate $R$, the estimated reuse-distance CDF deviates by $O(1/\sqrt{R\,n})$ (DKW-type bounds), so a fixed budget gives MRC error shrinking with stream length. Counter Stacks use **probabilistic counters (HyperLogLog-style)** over a pyramid of time windows, giving $|W(t,\tau)|$ for all $\tau$ in $O(\text{polylog})$ space per window.

**Drift.** Under nonstationarity, the target is a sliding-window functional; sliding-window $F_0$ has $\Theta(\epsilon^{-2}\log^2 N)$ space lower bounds (Datar–Gionis–Indyk–Motwani).

## 3. State of the Art (SOTA)

**Systems-SOTA.** **SHARDS** (Waldspurger et al., FAST 2015) constructs full MRCs online in $O(1)$ space via hash-based spatial sampling; **Counter Stacks** (Wires et al., OSDI 2014) use HLL sketches over time to produce MRCs for huge traces. **AET** (Hu et al., ATC 2018) estimates miss ratio from average eviction time in $O(1)$-per-access kernel-feasible form. These drive auto-sizing in production caches and self-tuning DBs.

**Theory-SOTA.** Optimal $F_0$ sketches (KNW 2010) and sliding-window distinct counting (DGIM 2002) bound what any estimator can achieve.

## 4. Upper Bound

- **Full MRC online:** SHARDS gives a $(\epsilon)$-accurate MRC in $\tilde O(1)$ space and $O(1)$ amortized time per reference (RAM model, hash-sampling).
- **Working-set size $|W(\tau)|$ for all $\tau$:** Counter Stacks in $O(\text{polylog }N)$ space per window via HLL.
- **Single-size distinct count:** $(1\pm\epsilon)$ in $O(\epsilon^{-2}+\log N)$ bits (KNW), optimal.
- **Sizing decision:** once the MRC is known, the cost-minimizing $c^\*$ is read off in $O(\text{\\#sizes})$.

## 5. Lower Bound

- **$F_0$ estimation** requires $\Omega(\epsilon^{-2}+\log N)$ bits (Indyk–Woodruff; KNW match it) — information-theoretic, streaming model.
- **Sliding-window distinct counting** requires $\Omega(\epsilon^{-2}\log^2 N)$ bits (DGIM lower bound).
- **Exact reuse-distance histogram** needs $\Omega(N)$ space (must distinguish all distinct-page configurations) — communication-complexity argument.
- No sublinear estimator can be correct under **fully adversarial** reorderings without a sampling/independence assumption (adversarially robust streaming gap, Ben-Eliezer et al. 2020).

## 6. The Gap

For the **stationary, single-MRC** problem the gap is essentially **closed**: sublinear estimators match information-theoretic lower bounds. What remains open and gives this a **partially-solved** status: (i) **adversarially-robust** working-set estimation with provable accuracy (current sketches assume oblivious or random streams); (ii) **non-LRU policies** — reuse distance characterizes LRU exactly but MRCs for ARC/LIRS/LFU lack equally tight one-pass estimators; (iii) **regret-bounded online resizing** that converts an estimated, drifting MRC into resize actions with bounded total cost — coupling estimation error to control error is not fully analyzed.

## 7. Current Research (as of June 2026)

- **Disaggregated / CXL memory auto-sizing** using online MRCs to rent pooled memory by the second. *(frontier — verify)*
- **Adversarially-robust sketches** for cache modeling, extending Ben-Eliezer–Jayaram–Woodruff–Yogev robustness to reuse distance. *(frontier — verify)*
- **Learned MRC predictors** that extrapolate cliffs from short prefixes (CMU self-driving DB lineage, VMware Research). *(frontier — verify)*
- Kernel/eBPF integration of AET-style estimators for OS page-cache auto-sizing.

## 8. Future Work

- One-pass, sublinear MRC estimators with provable accuracy for **non-stack** policies (ARC, LIRS, LFU).
- End-to-end **regret bounds** linking MRC-estimation error to resize cost under drift.
- Robust estimators secure against workloads that adapt to the sampler.
- Multi-tier working-set estimation (DRAM + NVM + SSD) producing a joint cost-optimal sizing.

## 9. Key References

- **[Foundational]** Denning. *The Working Set Model for Program Behavior.* CACM, 1968. — [DOI](https://doi.org/10.1145/363095.363141)
- **[Foundational]** Mattson, Gecsei, Slutz, Traiger. *Evaluation Techniques for Storage Hierarchies.* IBM Systems Journal, 1970. — [DOI](https://doi.org/10.1147/sj.92.0078)
- **[SOTA]** Waldspurger, Park, Garthwaite, Ahmad. *Efficient MRC Construction with SHARDS.* FAST, 2015. — [USENIX](https://www.usenix.org/conference/fast15/technical-sessions/presentation/waldspurger)
- **[SOTA]** Wires, Ingram, Drudi, Harvey, Warfield. *Characterizing Storage Workloads with Counter Stacks.* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/wires)
- **[Foundational]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** Hu, Wang, Luo, et al. *Fast Miss Ratio Curve Modeling with Average Eviction Time (AET).* USENIX ATC, 2018. — [DOI](https://doi.org/10.1145/3185751)

## 10. Worked Example

Access stream over $N$ pages: $A,B,C,A,B,D,A$. **Reuse distance** of a reference = number of *distinct* pages seen since that page's previous access (or $\infty$ on first touch).

| ref | $A$ | $B$ | $C$ | $A$ | $B$ | $D$ | $A$ |
|-----|-----|-----|-----|-----|-----|-----|-----|
| rd  | $\infty$ | $\infty$ | $\infty$ | $2$ | $2$ | $\infty$ | $2$ |

For the 2nd $A$: distinct pages since prior $A$ are $\{B,C\}$, so rd $=2$. For the final $A$: distinct since prior $A$ are $\{B,D\}$, rd $=2$.

**MRC for LRU.** Miss ratio at cache size $c$ = fraction of refs with rd $> c$ (Mattson). Of 7 refs, 4 have rd $=\infty$, 3 have rd $=2$:
$$f(1)=\tfrac{7}{7}=1.0,\quad f(2)=\tfrac{4}{7}\approx0.57,\quad f(3)=\tfrac{4}{7}\approx0.57.$$
The MRC flattens past $c=2$ — the reuse working set fits in 2 frames. **SHARDS** would sample only pages whose hash $h(p)<T$ (e.g. keep $\tfrac14$ of keys), build the same histogram from $O(1)$ tracked keys, and rescale — recovering this curve in sublinear space.

---
*Part of the [DBMS Research catalog](../../README.md).*
