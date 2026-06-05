# Source Selection Under Cost and Coverage

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/source-selection-coverage` · **Status:** partially-solved

## 1. Problem Statement

Given a universe of candidate data sources $\mathcal{S} = \{S_1, \dots, S_n\}$, each with an acquisition/integration cost $c(S_i)$ and a (possibly overlapping, possibly conflicting) contribution to answering a workload, choose a subset $T \subseteq \mathcal{S}$ that maximizes **answer coverage/quality** subject to a budget $B$ on total cost. "Quality" combines **coverage** (fraction of true entities/answers obtained), **accuracy** (after truth discovery over conflicting sources), and **freshness**.

Variants to distinguish:

- **Optimization (budgeted):** $\max_{T} g(T)$ s.t. $\sum_{S_i \in T} c(S_i) \le B$, where $g$ is a gain/quality function.
- **Dual (coverage-constrained):** $\min_T \sum c(S_i)$ s.t. $g(T) \ge \tau$.
- **Decision:** does there exist $T$ with cost $\le B$ and gain $\ge \tau$?
- **Marginal/online:** sources discovered or priced over time; decide incrementally.

The hardness lies in **diminishing returns** (sources overlap) and in **non-monotone quality** when adding a low-accuracy source degrades a truth-discovery estimate.

## 2. Mathematical Foundations

When $g$ is **monotone submodular** ($g(A \cup \{x\}) - g(A) \ge g(B \cup \{x\}) - g(B)$ for $A \subseteq B$), the problem is the classic **budgeted submodular maximization**. Pure coverage ($g(T) = |\bigcup_{S_i \in T} S_i|$) is the **maximum coverage** problem — a canonical submodular instance.

Key result (Nemhauser–Wolsey–Fisher 1978): greedy gives a $(1 - 1/e)$ approximation for cardinality constraints; with **knapsack (cost) constraints**, the cost-benefit greedy of Khuller–Moss–Naor and the Sviridenko (2004) partial-enumeration algorithm restore the $(1 - 1/e)$ ratio. For non-monotone submodular $g$, randomized greedy / measured continuous greedy give $\approx 0.385$ (Buchbinder–Feldman).

The truth-discovery layer breaks pure submodularity: Dong–Saha–Srivastava (VLDB 2013) model **marginal gain of a source net of integration cost** and show the "**fewer sources can be better**" phenomenon — quality is non-monotone once accuracy and copying are modeled. Source dependence/copying is captured via Bayesian models (Dong–Berti-Equille–Srivastava).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Budgeted submodular maximization is essentially settled: $(1-1/e)$ in value-oracle model, matching the oracle lower bound (Feige 1998 for set cover/max-coverage).
- **Systems-SOTA.** **Dong–Saha–Srivastava, "Less is More"** (PVLDB 2013) is the reference framework for cost-vs-coverage source selection with truth discovery. **Rekatsinas–Dong–Srivastava** ("SourceSight"/marginalism, SIGMOD 2014/2016) extend to time-varying quality and integration-order. Truth-discovery engines (**SLiMFast**, **HoloClean** lineage) feed the quality estimate.

## 4. Upper Bound

For monotone submodular $g$ with a single knapsack constraint, the best polynomial-time approximation is $(1 - 1/e) \approx 0.632$ (Sviridenko 2004), in the **value-oracle / RAM model**. Greedy alone (no enumeration) gives $\frac{1}{2}(1 - 1/e)$. For coverage with explicit set sizes, an LP-rounding alternative also achieves $1 - 1/e$. Non-monotone budgeted variants: $\approx 0.385$ (Buchbinder–Feldman) in the same oracle model.

## 5. Lower Bound

- **NP-hardness:** maximum coverage and set cover reduce in; the decision variant is **NP-complete**.
- **Inapproximability:** for max-coverage, $(1 - 1/e + \varepsilon)$ is **NP-hard** to achieve (Feige 1998), so the upper bound is tight unless P=NP. In the value-oracle model, beating $1 - 1/e$ requires **exponentially many queries** (Nemhauser–Wolsey lower bound) — an information-theoretic barrier independent of P vs NP.
- For the **non-monotone** truth-discovery objective, no constant-factor guarantee is known and the objective is not even submodular, so the $1-1/e$ frame does not apply.

## 6. The Gap

For the **submodular** abstraction the gap is **closed** ($1-1/e$ upper = lower). The genuinely open part is the **realistic objective**: once accuracy, source copying, and truth-discovery feedback make $g$ non-submodular and non-monotone, no tight approximation is known, and even formulating a well-behaved surrogate that the $1-1/e$ machinery applies to is open. Closing it requires either a structural property (e.g., approximate submodularity / submodularity ratio bounds) of realistic quality functions, or a hardness result showing none exists.

## 7. Current Research (as of June 2026)

Active directions: **learning the quality function** (submodularity-ratio / weak-submodularity bounds à la Das–Kempe transferred to source selection); **online and bandit source selection** where pulling a source reveals its value at a cost (Rekatsinas-style marginalism meets combinatorial bandits). *(frontier — verify)* Recent SIGMOD/VLDB 2024–2025 work integrates **LLM-extracted sources** and web tables, where acquisition cost is extraction/verification cost, and studies coverage of long-tail entities. *(frontier — verify)* Groups: Srivastava/Dong (data integration lineage), Rekatsinas (HoloClean/learning-over-data).

## 8. Future Work

- Tight approximation for non-monotone, copying-aware quality objectives.
- Distributionally-robust selection under uncertain per-source accuracy.
- Joint optimization of source selection *and* schema-mapping/ER cost in one budget.
- Streaming/online algorithms with regret guarantees for live source pricing.

## 9. Key References

- **[Foundational]** G. Nemhauser, L. Wolsey, M. Fisher. *An analysis of approximations for maximizing submodular set functions—I.* Math. Programming, 1978.
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998.
- **[SOTA]** X. L. Dong, B. Saha, D. Srivastava. *Less is More: Selecting Sources Wisely for Integration.* PVLDB, 2013.
- **[SOTA]** T. Rekatsinas, X. L. Dong, D. Srivastava. *Characterizing and Selecting Fresh Data Sources.* SIGMOD, 2014.
- **[SOTA]** M. Sviridenko. *A note on maximizing a submodular set function subject to a knapsack constraint.* Operations Research Letters, 2004.
- **[Survey]** X. L. Dong, D. Srivastava. *Big Data Integration.* Morgan & Claypool (Synthesis Lectures), 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
