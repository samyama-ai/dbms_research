---
id: 17-approximate-query-processing/interactive-latency-scheduling
title: "Interactive Latency-Accuracy Scheduling"
topic: 17-approximate-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Interactive Latency-Accuracy Scheduling

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/interactive-latency-scheduling` · **Status:** empirically-open

## 1. Problem Statement
An interactive dashboard issues a *set* of queries $Q_1,\dots,Q_k$ (one per chart) that must all render within a hard latency budget $T$ (e.g. 500 ms for "interactive" feel). Each query can be answered *progressively* — an online-aggregation engine produces a stream of refining estimates with shrinking confidence intervals. The scheduling problem: allocate the shared resource (CPU/IO/sample budget, possibly a single scan) across the $k$ progressive computations so that, at deadline $T$, every chart has an answer with a *useful* error bound, and aggregate utility (or worst-case error) is optimized.

Formally this is an **online resource-allocation / scheduling** problem: at each time slice decide which query receives the next unit of work, given that each query's error decays at a query- and data-dependent rate $\varepsilon_i(t)$. Variants: **min–max** (minimize the worst chart's error at $T$), **utility-max** (maximize $\sum_i u_i(\varepsilon_i(T))$ under fairness), and the **deadline-decision** variant (is there a schedule meeting per-chart error SLAs within $T$?). It is "empirically-open": good heuristics ship in systems, but no schedule with proven competitive guarantees against the offline optimum across realistic, correlated, convergence-curves exists.

## 2. Mathematical Foundations
Model each query's progressive error as a decreasing function $\varepsilon_i(b_i)$ of allocated budget $b_i$ (samples processed). For sampling-based aggregates, CI half-width $\varepsilon_i(b_i)=c_i/\sqrt{b_i}$ (CLT/Hoeffding), so error is **convex decreasing** in budget — marginal-value scheduling is governed by the derivative $-\tfrac{d\varepsilon_i}{db_i}\propto c_i b_i^{-3/2}$. Under a total budget $B=\sum b_i$ fixed at deadline, min-sum-error has a closed-form *water-filling*/Lagrangian solution: equalize marginal error reduction across queries, $b_i\propto c_i^{2/3}$.

The difficulty is that $c_i$ (data skew, selectivity) is **unknown a priori** and revealed only as the query runs — an online/bandit setting. The min–max objective is a *makespan-like* problem; utility-max with concave $u_i$ is a **submodular-/convex-budget** allocation. Shared scans add coupling: if queries can ride a common sequential scan, the schedule must also decide scan order (a set-cover-flavored coupling). Competitive analysis compares the online schedule's error to the clairvoyant optimum that knows all $c_i$ and convergence curves; multi-armed-bandit regret ($\sqrt{kT}$-type) bounds the cost of learning $c_i$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Water-filling / Lagrangian allocation is optimal *offline* for convex error curves; online versions reduce to budgeted bandits with sublinear regret, but tight competitive ratios for the coupled-scan, deadline-constrained, min–max version are not established.
- **Systems-SOTA:** `Online Aggregation` (Hellerstein–Haas–Wang, SIGMOD 1997) and `CONTROL`/`DBO` pioneered ripple-join progressive refinement; `G-OLA` (SIGMOD 2015) generalizes online aggregation to nested queries; `IDEA`/`Pangloss` and `DICE`/`Foresight`-style interactive cube systems and `Sample+Seek` (SIGMOD 2016) target sub-second dashboards. `Tableau`/`PowerBI`-class tools use precomputed extracts; `AQP++`, `VerdictDB` (SIGMOD 2018) layer sample-based answers under BI tools with CIs.

## 4. Upper Bound
Offline, convex error curves with fixed total budget: the water-filling allocation is **optimal** and computable in $O(k\log k)$. Online with unknown $c_i$ under a bandit oracle: budgeted-bandit policies achieve $\tilde O(\sqrt{kB})$ regret versus the best fixed allocation, giving near-optimal min-sum error as $B\to\infty$. Shared-scan progressive engines deliver per-query CIs of width $O(1/\sqrt{b_i})$ in the **RAM + sequential-scan** model. No published policy gives a constant competitive ratio for the min–max, deadline-coupled objective.

## 5. Lower Bound
The coupled problem inherits online-scheduling impossibilities. Min–max completion under unknown processing rates is at least as hard as **online makespan minimization**, which admits no better than a $\approx 1.88$ competitive ratio for identical machines and worse under uncertainty; deadline feasibility with unknown convergence rates is hard in the *clairvoyance* sense (no online algorithm matches the offline optimum). Learning each $c_i$ incurs an unavoidable $\Omega(\sqrt{kB})$ bandit-regret information-theoretic lower bound. These are online-competitive and statistical lower bounds, not NP-hardness — the offline problem itself is poly-time.

## 6. The Gap
The gap is between strong *offline/asymptotic* optimality (water-filling, vanishing bandit regret) and the absence of any *finite-horizon, hard-deadline, min–max* guarantee that also models shared scans and correlated query convergence. It is genuinely open whether a single online policy can be simultaneously (near-)optimal for min–max error, respect a sub-second deadline, and exploit scan-sharing. Closing it needs a competitive-ratio result for this coupled model — currently only heuristics with empirical wins exist, hence *empirically-open*.

## 7. Current Research (as of June 2026)
Active threads: learned cost/convergence predictors to warm-start $c_i$; reinforcement-learning schedulers for progressive workloads; "approximate materialized view" caches shared across dashboard queries; integrating VerdictDB-style error propagation with per-widget SLAs. *(frontier — verify)* Several 2025 interactive-analytics prototypes claim sub-second multi-query scheduling with learned convergence models, but report empirical latency/error rather than competitive guarantees.

## 8. Future Work
- A competitive-ratio theory for deadline-bounded, min–max progressive scheduling with scan-sharing.
- Robust online estimation of per-query convergence under correlated/skewed data.
- Co-design of synopsis caches and schedulers so dashboard panels share work optimally.

## 9. Key References
- **[Foundational]** Hellerstein, J., Haas, P., Wang, H. *Online Aggregation.* SIGMOD, 1997. — [DOI](https://doi.org/10.1145/253262.253291)
- **[SOTA]** Zeng, K., Agarwal, S., Dave, A., Armbrust, M., Stoica, I. *G-OLA: Generalized Online Aggregation for Interactive Analysis.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2735381)
- **[SOTA]** Park, Y., Mozafari, B., Sorenson, J., Wang, J. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[SOTA]** Ding, B., Huang, S., Chaudhuri, S., Chakrabarti, K., Wang, C. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD, 2016. — [DBLP](https://dblp.org/rec/conf/sigmod/DingHCC016.html)
- **[Survey]** Chaudhuri, S., Ding, B., Kandula, S. *Approximate Query Processing: No Silver Bullet.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056097)

## 10. Worked Example

A dashboard renders $k=2$ charts under deadline $T$, total sample budget $B=10{,}000$. Progressive CI half-widths are $\varepsilon_i(b_i)=c_i/\sqrt{b_i}$ with data-dependent constants $c_1=1$ (low-skew chart) and $c_2=2$ (high-skew chart).

**Naive equal split** $b_1=b_2=5000$:
$\varepsilon_1=1/\sqrt{5000}\approx 0.0141$, $\varepsilon_2=2/\sqrt{5000}\approx 0.0283$. Sum $\approx 0.0424$, max $=0.0283$.

**Min-sum water-filling** allocates $b_i\propto c_i^{2/3}$. With $c_1^{2/3}=1$, $c_2^{2/3}=2^{2/3}\approx 1.587$, the shares are $b_1=10000\cdot\frac{1}{2.587}\approx 3866$, $b_2\approx 6134$. Then $\varepsilon_1\approx 0.0161$, $\varepsilon_2=2/\sqrt{6134}\approx 0.0255$, sum $\approx 0.0416$ — below the equal split, confirming the Lagrangian optimum.

**Min–max** instead equalizes errors: set $c_1/\sqrt{b_1}=c_2/\sqrt{b_2}$, i.e. $b_2/b_1=(c_2/c_1)^2=4$, giving $b_1=2000$, $b_2=8000$ and $\varepsilon_1=\varepsilon_2=2/\sqrt{8000}\approx 0.0224$ — a smaller worst-case error than either above. The online catch: $c_2$ is unknown until chart 2's stream reveals its skew, so a scheduler must *learn* $c_i$ on the fly, paying the $\Omega(\sqrt{kB})$ bandit regret of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
