# End-to-End Privacy Budget Accounting for Workloads

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/privacy-budget-accounting-workloads` · **Status:** partially-solved
> **Verification note:** Gopi–Lee–Wutschitz (NeurIPS 2021) is titled "Numerical Composition of Differential Privacy"; the "Connect-the-Dots" name refers to a distinct later accountant (Doroshenko et al., PoPETs 2022), so the parenthetical in §3 and §9 conflates two papers.

## 1. Problem Statement

A DP database serves an **evolving, adaptive workload**: analysts issue a stream of SQL queries $Q_1,Q_2,\dots$, each consuming part of a fixed global budget $\varepsilon_{\mathrm{tot}}$ (or $\rho_{\mathrm{tot}}$ in zCDP), where later queries are chosen based on earlier noisy answers (adaptivity) and queries may be **correlated** (overlapping predicates, shared joins, repeated columns). The problem: **account the total privacy loss as tightly as possible** so the system can answer the maximum number / accuracy of queries before exhausting the budget, while remaining sound under adaptivity and correlation.

Variants:
- **Composition-accounting (counting/optimization):** compute the smallest provable $\varepsilon_{\mathrm{tot}}$ for a given sequence of mechanisms.
- **Budget-allocation under a cap (online/optimization):** decide per-query $\varepsilon_i$ to maximize utility subject to $\sum$ bound, possibly online.
- **Correlation-aware accounting:** exploit that correlated queries leak *less jointly* than worst-case composition assumes — largely open.

## 2. Mathematical Foundations

Composition theorems bound cumulative loss. **Basic composition:** $\varepsilon_{\mathrm{tot}}=\sum_i\varepsilon_i$. **Advanced composition** (Dwork–Rothblum–Vadhan): $\tilde{O}(\sqrt{k}\,\varepsilon)$ for $k$ mechanisms. **Rényi DP / zCDP** (Mironov; Bun–Steinke) compose additively: $\rho_{\mathrm{tot}}=\sum_i\rho_i$, with conversion $\rho$-zCDP $\Rightarrow (\rho+2\sqrt{\rho\ln(1/\delta)},\delta)$-DP. The **optimal** composition is characterized by the **privacy loss distribution (PLD)** / dominating pairs (Sommer–Meiser–Mohammadi; Koskela et al.), computed numerically via FFT — the *moments/PLD accountant* gives the tightest known $(\varepsilon,\delta)$ for arbitrary heterogeneous adaptive sequences. **Fully adaptive composition** with *budget chosen on the fly* requires **privacy filters and odometers** (Rogers–Roth–Ullman–Vadhan), which match advanced composition up to constants while allowing data-dependent stopping. Correlation is *not* exploited by these: composition is worst-case over adaptive adversaries.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** PLD/FFT accountants (Koskela–Jälkö–Honkela, AISTATS 2020; Gopi–Lee–Wutschitz, NeurIPS 2021) give numerically tight composition. Fully-adaptive **filters/odometers** (Whitehouse–Ramdas–Rogers–Wu, NeurIPS 2022) close the constant-factor gap to the non-adaptive optimum.
- **Systems-SOTA:** **PrivateSQL/Tumult Analytics/OpenDP** track per-query spend with zCDP accountants. **Cohere / Sage / privacy budget schedulers** (Luo, Lécuyer et al.) manage budgets across many pipelines as a *resource-allocation* problem; **DPella** and **PINQ/wPINQ** (McSherry) pioneered language-level budget tracking.

## 4. Upper Bound

For a *fixed, non-adaptive* sequence the PLD accountant computes the optimal $(\varepsilon,\delta)$ to arbitrary numerical precision in near-linear time per composition (FFT). For *fully adaptive* budgeting, privacy filters guarantee $\varepsilon_{\mathrm{tot}}$ within a small constant of advanced composition while letting per-query $\varepsilon_i$ depend on observed outputs — this is the strongest general **upper-bound (positive) result**, hence the "partially-solved" status: the accounting layer is essentially solved for independent mechanisms.

## 5. Lower Bound

The advanced-composition $\Omega(\sqrt{k}\,\varepsilon)$ growth is **tight** — Kairouz–Oh–Viswanath gave the exact optimal composition for homogeneous mechanisms, and no accountant can do asymptotically better against an adaptive adversary (information-theoretic, via hypothesis-testing / $f$-DP trade-off curves, Dong–Roth–Su). For **correlated** queries, there is no general tight lower bound *exploiting* correlation: worst-case composition is provably loose on specific correlated workloads, but a matching general accounting scheme is missing. Online budget allocation inherits competitive-ratio lower bounds from adversarial resource allocation.

## 6. The Gap

**Independent-mechanism accounting is closed** (PLD optimal; filters near-optimal). The **open gap** is **correlation-aware** accounting: when $Q_i$ overlap heavily, true joint leakage can be far below $\sum$-style bounds, yet we lack a sound, general, tight accountant that certifies this — current practice over-charges. Also open: tight *online* allocation maximizing workload utility under the cap. Closing it needs joint-leakage characterization (e.g., via $f$-DP trade-off composition that detects shared randomness/overlap) with provable optimality.

## 7. Current Research (as of June 2026)

- $f$-DP / Gaussian-DP unified accounting and its tight composition for SQL pipelines (Dong–Roth–Su line) *(frontier — verify)*.
- Correlation- and overlap-aware accounting that treats repeated columns as a single measurement (PrivateSQL "sensitivity views" extended to budget reuse) *(frontier — verify)*.
- Budget-scheduling systems (Cohere, Turbo/Sage successors) treating $\varepsilon$ as a multi-tenant resource with fairness *(frontier — verify)*.

## 8. Future Work

- Provably tight correlation-aware composition for overlapping joins/predicates.
- Optimal online budget allocation with utility guarantees.
- Accountants integrated into query optimizers (see `dp-query-plan-optimization`).
- Long-running "forever" odometers with sublinear budget growth for benign workloads.

## 9. Key References

- **[Foundational]** Dwork, Rothblum, Vadhan. *Boosting and Differential Privacy (Advanced Composition).* FOCS, 2010. — [DOI](https://doi.org/10.1109/FOCS.2010.12)
- **[Foundational]** Kairouz, Oh, Viswanath. *The Composition Theorem for Differential Privacy.* ICML, 2015. — [PMLR](https://proceedings.mlr.press/v37/kairouz15.html) — [arXiv](https://arxiv.org/abs/1311.0776)
- **[Foundational]** Bun, Steinke. *Concentrated Differential Privacy: Simplifications, Extensions, and Lower Bounds.* TCC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53641-4_24) — [arXiv](https://arxiv.org/abs/1605.02065)
- **[SOTA]** Rogers, Roth, Ullman, Vadhan. *Privacy Odometers and Filters: Pay-as-you-Go Composition.* NeurIPS, 2016. — [arXiv](https://arxiv.org/abs/1605.08294)
- **[SOTA]** Gopi, Lee, Wutschitz. *Numerical Composition of Differential Privacy.* NeurIPS, 2021. — [arXiv](https://arxiv.org/abs/2106.02848)
- **[SOTA]** Dong, Roth, Su. *Gaussian Differential Privacy.* J. Royal Statistical Society B, 2022. — [DOI](https://doi.org/10.1111/rssb.12454)
- **[Survey]** McSherry. *Privacy Integrated Queries (PINQ).* SIGMOD, 2009. — [DOI](https://doi.org/10.1145/1559845.1559850)

## 10. Worked Example

A DP dataset has total budget $\varepsilon_{\text{tot}} = 1.0$ at $\delta = 10^{-6}$. An analyst issues $k = 100$ identical Laplace-mechanism count queries, each $\varepsilon_0$-DP. How small must $\varepsilon_0$ be?

**Basic composition** charges linearly: $k\varepsilon_0 \le 1 \Rightarrow \varepsilon_0 \le 0.01$. So at most 100 queries at $\varepsilon_0 = 0.01$ each.

**Advanced composition** (Dwork–Rothblum–Vadhan) gives, for $k$ mechanisms,
$$\varepsilon_{\text{tot}} \le \sqrt{2k\ln(1/\delta)}\,\varepsilon_0 + k\varepsilon_0(e^{\varepsilon_0}-1).$$
With $k=100,\ \delta=10^{-6}$: $\ln(1/\delta)\approx13.8$, so $\sqrt{2\cdot100\cdot13.8}\approx52.6$. Ignoring the tiny second term, $52.6\,\varepsilon_0 \le 1 \Rightarrow \varepsilon_0 \le 0.019$ — nearly **double** the per-query budget of basic composition, because privacy loss grows like $\sqrt{k}$, not $k$.

**Tighter still:** the PLD/numerical accountant (Gopi–Lee–Wutschitz) computes the exact $(\varepsilon,\delta)$ curve, typically permitting $\varepsilon_0$ a further $\sim$10–30% larger.

**The open gap:** if the 100 queries are *correlated* (e.g., COUNT on heavily overlapping predicates), true joint leakage can be far below this $\sqrt{k}$ bound, yet no sound general accountant certifies the saving — so the system still over-charges and stops early.

---
*Part of the [DBMS Research catalog](../../README.md).*
