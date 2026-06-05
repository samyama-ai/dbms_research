# Aggregation Control Lower Bounds

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/aggregation-control-bounds` · **Status:** open
> **Verification note:** The STOC 2014 fingerprinting-codes paper is by Bun, Ullman, and Vadhan (not Steinke); author corrected in §9.

## 1. Problem Statement

A statistical database answers **aggregate queries** (SUM, COUNT, AVG over selected subsets) but is meant to protect *individual* records. The **aggregation / tracker problem**: an adversary issues a sequence of permitted aggregate queries and combines the answers — via a **tracker** (a pair of queries whose difference isolates a single record) or a system of linear equations — to **reconstruct** protected individual values.

The problem: establish **tight bounds on the maximum number of aggregate queries** that can be answered before reconstruction of a protected individual value becomes possible (or, with noise, before privacy is destroyed). Equivalently, characterize the **query-set size / overlap threshold** below which the database is provably safe and above which it is provably broken.

Variants:
- **Exact (noiseless) reconstruction:** decision/counting — given a query workload, can the answers determine some individual bit? How few queries suffice?
- **Approximate reconstruction under noise:** how much noise per query is *necessary* to prevent reconstruction of a constant fraction of records given $m$ queries over $n$ records?
- **Optimization:** the maximal answerable query budget as a function of noise magnitude and $n$.

This is **open** in the sense that, while the noisy-reconstruction frontier is sharply understood (Dinur–Nissim and successors), *tight* per-workload combinatorial bounds for structured aggregate queries and for the noiseless tracker setting are not fully closed.

## 2. Mathematical Foundations

Model the database as a secret vector $x \in \{0,1\}^n$. A query is a subset $q \subseteq [n]$ with true answer $a_q = \sum_{i \in q} x_i$. The system returns $\tilde a_q = a_q + e_q$ with perturbation $|e_q| \le E$. Reconstruction asks to recover $x' $ agreeing with $x$ on $(1-o(1))n$ coordinates.

- **Linear algebra / trackers (Denning–Schlörer).** With unrestricted query selection, two overlapping aggregates yield $a_{q} - a_{q\setminus\{i\}} = x_i$ — a tracker isolates one record. Query-set-overlap controls limit $|q|$ and overlap to block this.
- **Dinur–Nissim reconstruction theorem (2003).** If a curator answers $m = O(n)$ random subset-sum queries each with noise $E = o(\sqrt{n})$, an adversary using **linear programming** reconstructs $x$ up to $o(n)$ errors. Hence to resist reconstruction one **must** add noise $\Omega(\sqrt{n})$ — the foundational lower bound that launched differential privacy.
- **Fingerprinting codes (Bun–Ullman–Steinke; Dwork et al.).** Lower bounds on the number of statistical queries answerable with per-query error $\alpha$ before privacy collapses: roughly $\tilde O(n^2/\,?)$-type tradeoffs; tight $\Theta$ results for adaptive workloads.
- **Differential privacy** quantifies the safe budget: answering $m$ counting queries to error $\alpha$ requires privacy loss scaling like $\sqrt{m}\log(1/\delta)/(\alpha n)$ (advanced composition / matrix mechanism).

## 3. State of the Art (SOTA)

- **Dinur–Nissim (PODS 2003):** the reconstruction lower bound; $\Omega(\sqrt n)$ noise is necessary against $O(n)$ queries — essentially tight for random workloads.
- **Dwork–McSherry–Nissim–Smith (TCC 2006):** differential privacy and the Laplace/Gaussian mechanisms, giving matching upper bounds on safe query budgets.
- **Hardt–Rothblum private multiplicative weights** and the **matrix mechanism (Li–Miklau)**: near-optimal answering of large linear-query workloads, characterizing how many correlated aggregates can be released.
- **Bun–Ullman–Steinke fingerprinting lower bounds (STOC 2014+):** tight $\Theta(\cdot)$ bounds on adaptive statistical-query budgets.
- Systems-SOTA: query auditors and DP engines (Google/Apple DP, **OpenDP**, **PINQ/Flex**, US Census **TopDown**) implement budget accounting motivated by these bounds.

## 4. Upper Bound

- **Matrix mechanism / private multiplicative weights:** answer $m$ linear queries over $n$ records with error scaling as $\tilde O(\sqrt{m}/(\varepsilon n))$ (or polylogarithmic in the universe via PMW), tight against the reconstruction lower bound for many workloads.
- Noiseless query-set control (overlap/size restrictions) safely answers up to a combinatorially bounded number of queries determined by the workload's incidence structure.
- Gaussian mechanism + advanced composition gives the standard safe-budget upper bound under $(\varepsilon,\delta)$-DP.

## 5. Lower Bound

- **Dinur–Nissim:** $\Omega(\sqrt n)$ per-query noise is *necessary*; with $o(\sqrt n)$ noise, $O(n)$ queries enable near-full reconstruction (information-theoretic + LP attack).
- **Fingerprinting-code lower bounds (Bun–Ullman–Steinke):** no mechanism can answer more than $\tilde O(n^2)$ adaptively-chosen statistical queries (with constant accuracy) without privacy failure — tight against the SQ upper bound.
- **Tracker existence (Denning):** in unrestricted statistical databases a tracker almost always exists, so query-set-size control alone cannot guarantee safety beyond small budgets.

## 6. The Gap

The **noisy random-workload frontier is essentially closed** (Dinur–Nissim lower bound meets DP upper bounds; fingerprinting bounds are tight up to logs). The genuinely **open** parts: (1) *tight, per-workload* bounds for **structured** aggregate queries (range/marginal queries, OLAP cubes) where the worst-case bounds are loose — the exact query budget for a given workload geometry is unknown; (2) the **noiseless exact-reconstruction** combinatorial threshold for restricted query languages (with size/overlap controls) lacks matching upper and lower constructions; (3) bounds under **realistic adversary knowledge** (auxiliary data, partial schema) rather than worst-case. Closing these requires workload-aware lower bounds matching mechanism-specific upper bounds.

## 7. Current Research (as of June 2026)

- **Reconstruction attacks on real releases** (e.g., the US Census 2020 reconstruction debate) sharpening practical thresholds and per-workload bounds *(frontier — verify)*.
- Tight error bounds for **marginal / range query workloads** via the matrix mechanism and discrete Gaussian, pushing toward instance-optimal budgets *(frontier — verify)*.
- **Concentrated / zero-concentrated DP** accounting refining safe-budget constants for large adaptive workloads.
- Lineage of Dwork, Nissim, Ullman, Steinke, Miklau remains central; Census/OpenDP engineering community active.

## 8. Future Work

- Instance-optimal (workload-aware) reconstruction lower bounds matching mechanism error.
- Tight noiseless thresholds for query languages with size/overlap auditing.
- Lower bounds incorporating adversarial auxiliary information realistically.
- Bridging combinatorial tracker theory with modern DP fingerprinting bounds into a single tight framework.

## 9. Key References

- **[Foundational]** Irit Dinur, Kobbi Nissim. *Revealing Information While Preserving Privacy.* PODS, 2003. — [DOI](https://doi.org/10.1145/773153.773173)
- **[Foundational]** Cynthia Dwork, Frank McSherry, Kobbi Nissim, Adam Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[SOTA]** Mark Bun, Jonathan Ullman, Salil Vadhan. *Fingerprinting Codes and the Price of Approximate Differential Privacy.* STOC, 2014. — [DOI](https://doi.org/10.1145/2591796.2591877)
- **[SOTA]** Chao Li, Gerome Miklau, Michael Hay, Andrew McGregor, Vibhor Rastogi. *The Matrix Mechanism: Optimizing Linear Counting Queries Under Differential Privacy.* VLDB Journal, 2015. — [DOI](https://doi.org/10.1007/s00778-015-0398-x)
- **[Foundational]** Dorothy E. Denning, Peter J. Denning, Mayer D. Schwartz. *The Tracker: A Threat to Statistical Database Security.* ACM TODS, 1979. — [DOI](https://doi.org/10.1145/320064.320069)
- **[Survey]** Cynthia Dwork, Aaron Roth. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in Theoretical Computer Science, 2014. — [DOI](https://doi.org/10.1561/0400000042)

## 10. Worked Example

**A tracker in action.** Secret bits $x=(x_1,\dots,x_5)\in\{0,1\}^5$ (say a "has-condition" flag). The policy forbids any COUNT over a set of fewer than 2 records, to hide individuals. The adversary wants $x_3$.

Pick two *allowed* (size $\ge 2$) queries that differ by exactly record 3:
$$q_1=\{2,3,4\},\quad q_2=\{2,4\}.$$
Both have size $\ge 2$, so both are answered. The system returns $a_{q_1}=x_2+x_3+x_4$ and $a_{q_2}=x_2+x_4$. The adversary computes
$$a_{q_1}-a_{q_2}=x_3,$$
isolating the forbidden individual bit despite the size-threshold guard. The pair $(q_1,q_2)$ is a **tracker**: query-set-size control alone fails.

**Why noise is forced (Dinur–Nissim).** If instead each answer carries noise $|e_q|\le E$, then $a_{q_1}-a_{q_2}=x_3+e_{q_1}-e_{q_2}$, an error up to $2E$. Over $m=O(n)$ random queries an LP attack still reconstructs $x$ up to $o(n)$ errors whenever $E=o(\sqrt n)$ — so safety requires noise $\Omega(\sqrt n)$, here $\Omega(\sqrt 5)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
