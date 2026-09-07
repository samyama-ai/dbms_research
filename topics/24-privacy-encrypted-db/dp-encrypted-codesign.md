---
id: 24-privacy-encrypted-db/dp-encrypted-codesign
title: "DP-Encrypted Co-Design Against Leakage"
topic: 24-privacy-encrypted-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# DP-Encrypted Co-Design Against Leakage

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/dp-encrypted-codesign` · **Status:** open

## 1. Problem Statement

Encrypted databases (searchable encryption, ORAM-backed stores, encrypted indexes) hide *data values* but leak structural side channels: **access patterns** (which physical locations are touched), **volume** (how many records match), and **search/co-occurrence patterns**. A line of attacks (IKK, Cash et al., Kellaris–Kollios–Nissim–O'Neill, LMP volume attacks) reconstructs plaintext from exactly these leakage profiles. Pure obliviousness (full ORAM) removes the leakage but at logarithmic-to-linear overhead per access. The problem is to **co-design** encryption with **differential privacy** so that the *leakage itself* — the distribution over access/volume patterns observed by the server — is $(\varepsilon,\delta)$-differentially private with respect to the underlying database, at sub-oblivious cost.

Variants:
- **Decision:** given a scheme and a leakage function $\mathcal{L}$, decide whether $\mathcal{L}$ is $(\varepsilon,\delta)$-DP over neighboring databases/queries.
- **Optimization:** minimize bandwidth/storage/round overhead subject to a target $(\varepsilon,\delta)$ leakage budget.
- **Counting:** characterize the minimum number of "dummy" accesses/records needed to achieve a given $\varepsilon$.

## 2. Mathematical Foundations

Model the server's view as a randomized leakage transcript $\mathcal{L}(\mathrm{DB}, q_1,\dots,q_t)$. **Differentially private leakage** requires that for neighboring databases $D \sim D'$ (or neighboring query sequences),
$$\Pr[\mathcal{L}(D,\vec q)\in S]\le e^{\varepsilon}\Pr[\mathcal{L}(D',\vec q)\in S]+\delta,$$
for all measurable $S$. This composes over a stream of $t$ queries by advanced composition / zCDP, so a per-query budget $\varepsilon_0$ yields $\varepsilon\approx \varepsilon_0\sqrt{2t\ln(1/\delta')}$. Achieving it typically perturbs **volume** (padding match counts via a discrete Laplace/geometric mechanism, which must be one-sided/truncated since you cannot return fewer real records) and **access patterns** (injecting dummy accesses or using a differentially private ORAM relaxation). Key tension: DP needs noise calibrated to *sensitivity* (here, how much one record changes the touched-location multiset), while functionality requires every real match still be returned — so the noise is **additive padding** with a one-sided geometric distribution, and the privacy/overhead trade-off is governed by that distribution's tail.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Mazloom & Gordon (*Secure Computation with Differentially Private Access Patterns*, CCS 2018) give a framework making access patterns DP via a perturbation layer over an encrypted/secure-computation store, with formal $(\varepsilon,\delta)$ guarantees and overhead analysis. Patel, Persiano, Yeo, Yung (CCS 2019) give **volume-hiding** encrypted multimaps with DP-style padding.
- **Systems-SOTA:** **Shrinkwrap** (Bater et al., VLDB 2019) applies DP to intermediate-result *cardinalities* in oblivious query processing, padding result sizes to a DP-noised bound rather than worst case. **SEAL** (Demertzis et al., USENIX Security 2020) tunably trades leakage for efficiency via adjustable padding and ORAM locality.

## 4. Upper Bound

Shrinkwrap-style DP padding reduces oblivious-operator output from the worst-case bound to (true size + $O(\frac{1}{\varepsilon}\log\frac{1}{\delta})$) expected dummy tuples per operator, a large practical saving over full obliviousness while $(\varepsilon,\delta)$-DP. DP volume-hiding multimaps (Patel et al.) achieve query time linear in true response size plus DP padding, with $O(1)$ amortized overhead beyond the padding term, in the RAM/encrypted-multimap model. DP-ORAM relaxations achieve $o(\log n)$ per-access overhead where strict ORAM requires $\Omega(\log n)$, by tolerating $(\varepsilon,\delta)$ leakage.

## 5. Lower Bound

Strict (zero-leakage) ORAM has a **$\Omega(\log n)$ per-access bandwidth lower bound** (Larsen–Nielsen, CRYPTO 2018) in the cell-probe model — this is the cost DP-leakage co-design aims to beat by relaxing to $\varepsilon>0$. For the privacy side, any scheme returning all true matches must leak volume up to its additive noise, and one-sided DP noise has an information-theoretic floor on the dummy count needed for a target $\varepsilon$ (the geometric mechanism is optimal among one-sided integer mechanisms, Ghosh–Roughgarden–Sundararajan). Reconstruction-attack lower bounds (KKNO, CCS 2016) show that with $\varepsilon$ too large, $O(N\log N)$ uniform queries suffice to fully reconstruct.

## 6. The Gap

The gap is **genuinely open** and multi-dimensional. (1) The $\Omega(\log n)$ ORAM bound is for $\varepsilon=0$; the exact Pareto frontier of *bandwidth vs. $(\varepsilon,\delta)$* across the full leakage range is not tight. (2) Composition over long query streams blows the budget up by $\sqrt t$, but no scheme matches a proven optimal per-query/total trade-off under continual observation. (3) Correlated leakage (volume × access × search pattern *jointly*) lacks a unified sensitivity/DP analysis — most results treat one channel. Closing it needs a model that simultaneously bounds all channels under adaptive, long-horizon queries with a matching lower bound.

## 7. Current Research (as of June 2026)

- Unifying volume-, access-, and search-pattern leakage under a single DP accountant with a numerical PLD-style composition for encrypted streams *(frontier — verify)*.
- DP-relaxed Oblivious RAM / oblivious data structures proving $o(\log n)$ amortized cost at fixed $\varepsilon$ *(frontier — verify)*.
- Groups: Paterson/Minaud/Lacharité (leakage cryptanalysis & defenses), Kamara–Moataz (structured encryption), the EPFL/Demertzis line (SEAL/locality), and the oblivious-query-processing group around Rogers/Bater/Kantarcioglu (Shrinkwrap lineage).

## 8. Future Work

- Tight bandwidth–privacy Pareto curves for DP-leakage indexes across the full $\varepsilon$ range.
- DP leakage under *update* workloads (forward/backward privacy composed with DP).
- Provable end-to-end guarantees for joint multi-channel leakage in a real encrypted SQL engine.
- Reconstruction-attack resistance proofs as a *function of* the DP budget actually spent.

## 9. Key References

- **[Foundational]** Kellaris, Kollios, Nissim, O'Neill. *Generic Attacks on Secure Outsourced Databases.* CCS, 2016. — [DOI](https://doi.org/10.1145/2976749.2978386) · [DBLP](https://dblp.org/rec/conf/ccs/KellarisKNO16.html)
- **[Foundational]** Larsen, Nielsen. *Yes, There is an Oblivious RAM Lower Bound!* CRYPTO, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96881-0_18) · [DBLP](https://dblp.org/rec/conf/crypto/LarsenN18.html) · [ePrint](https://eprint.iacr.org/2018/423)
- **[SOTA]** Mazloom, Gordon. *Secure Computation with Differentially Private Access Patterns.* CCS, 2018. — [DOI](https://doi.org/10.1145/3243734.3243851) · [ePrint](https://eprint.iacr.org/2017/1016)
- **[SOTA]** Bater, He, Ehrich, Machanavajjhala, Rogers. *Shrinkwrap: Efficient SQL Query Processing in Differentially Private Data Federations.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3291264.3291274) · [PDF](http://www.vldb.org/pvldb/vol12/p307-bater.pdf) · [arXiv](https://arxiv.org/abs/1810.01816)
- **[SOTA]** Patel, Persiano, Yeo, Yung. *Mitigating Leakage in Secure Cloud-Hosted Data Structures: Volume-Hiding for Multi-Maps via Hashing.* CCS, 2019. — [DOI](https://doi.org/10.1145/3319535.3354213) · [DBLP](https://dblp.org/rec/conf/ccs/PatelPYY19.html) · [ePrint](https://eprint.iacr.org/2019/1292)
- **[SOTA]** Demertzis, Papadopoulos, Papamanthou, Shintre. *SEAL: Attack Mitigation for Encrypted Databases via Adjustable Leakage.* USENIX Security, 2020. — [USENIX](https://www.usenix.org/conference/usenixsecurity20/presentation/demertzis) · [ePrint](https://eprint.iacr.org/2019/811)

## 10. Worked Example

**One-sided geometric volume padding.** An encrypted multimap maps a keyword to its matching record IDs; the server learns the *volume* (count) returned. Keyword "diabetes" truly matches $v=12$ records; on a neighboring database with one patient removed it would match $v'=11$. To make the released volume $(\varepsilon,0)$-DP we must pad — we can only *add* dummy records, never drop real ones — so we draw padding from a one-sided geometric distribution with parameter $\alpha=e^{-\varepsilon}$: $\Pr[\text{pad}=k]=(1-\alpha)\alpha^{k}$, $k\ge 0$, and release $\tilde v = v+\text{pad}$.

Take $\varepsilon=\ln 2$, so $\alpha=\tfrac12$. The DP guarantee needs $\Pr[\tilde v = m \mid v=12]\le e^{\varepsilon}\Pr[\tilde v=m\mid v'=11]$ for all $m$; since shifting the floor up by one only rescales the geometric tail by $\alpha^{-1}=2=e^{\varepsilon}$, the bound holds exactly. Expected dummy cost is $\mathbb{E}[\text{pad}]=\frac{\alpha}{1-\alpha}=1$ extra record per query — versus full obliviousness, which would pad every query to the worst-case bound (e.g. $N$). The privacy/overhead knob is $\varepsilon$: halving $\alpha$ (raising $\varepsilon$) cuts expected padding but loosens the multiplicative leakage bound $e^{\varepsilon}$.

---
*Part of the [DBMS Research catalog](../../README.md).*
