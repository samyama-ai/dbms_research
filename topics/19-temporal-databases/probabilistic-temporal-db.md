---
id: 19-temporal-databases/probabilistic-temporal-db
title: "Probabilistic Temporal Databases"
topic: 19-temporal-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Probabilistic Temporal Databases

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/probabilistic-temporal-db` · **Status:** open
> **Verification note:** The TP-databases paper is by Dekhtyar, Ross & Subrahmanian (*Probabilistic Temporal Databases, I: Algebra*, TODS 2001); the prior "Ozsoyoglu/Ross J." attribution was incorrect and is corrected in §2 and §9.

## 1. Problem Statement
A probabilistic temporal database represents uncertainty in **both** the data values **and** the time at which facts hold. A tuple may exist with probability $p$, and/or its valid-time period may be an *uncertain interval* — endpoints drawn from distributions, or a set of candidate periods with a probability mass. The problem is **tractable query evaluation**: compute (or approximate) the marginal probability that a temporal query answer holds, possibly as a function of time, when the possible-worlds space is the product of value-uncertainty and time-uncertainty.

Variants:
- **Decision / exact:** compute $\Pr[t \in Q(\text{DB})]$ for output tuple $t$ (and over which valid-time it holds).
- **Counting:** this *is* a weighted model counting (#P) problem in general.
- **Approximation:** $(\epsilon,\delta)$-estimates via sampling or anytime bounds.
- **Time-indexed:** return the *probability curve* $p(\tau)=\Pr[\text{fact holds at } \tau]$ rather than a scalar.

The new difficulty over standard probabilistic DBs: temporal operators (sequenced join, coalescing, overlap) correlate value-existence with interval-overlap events, so even "safe" non-temporal queries can become unsafe once time uncertainty couples the variables.

## 2. Mathematical Foundations
A probabilistic database is a distribution over possible worlds; query evaluation is **weighted model counting (WMC)** over the lineage Boolean formula (Suciu–Olteanu–Ré–Koch). For a Boolean query $Q$, $\Pr[Q]=\sum_{W\models Q}\Pr[W]$, computable in PTIME iff the query is **safe** (hierarchical / has an efficient *dissociation* or read-once lineage); otherwise it is **#P-hard** — the **dichotomy theorem** of Dalvi–Suciu for unions of conjunctive queries.

Temporal uncertainty adds a second source of randomness. Endpoints $t_s, t_e$ become random variables; the event "$p\cap q \neq \varnothing$" is a function of four random endpoints, turning interval-overlap into a **continuous (or discretized) convolution** of distributions. Formally the lineage becomes a formula over a mixed set of Boolean (existence) and arithmetic (endpoint-comparison) variables — a *hybrid* WMC / **weighted model integration (WMI)** problem. Indeterminate-time models (Dyreson–Snodgrass *probability mass / credibility distributions* over a period, TODS 1998) and **interval-probabilistic** models (Dekhtyar–Ross–Subrahmanian) give the discrete-time foundation; correlations are captured by *pc-tables* / **provenance semirings over the $\mathbb{B}[X]$ / probability semiring**.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The Dalvi–Suciu **dichotomy** (PTIME vs #P-hard) for UCQs on tuple-independent DBs is the backbone; *dissociation* and *oblivious bounds* (Gatterbauer–Suciu) give principled approximations for hard queries. For time, Dyreson–Snodgrass *valid-time indeterminacy* and Dekhtyar et al.'s *temporal-probabilistic (TP) databases* (TODS 2001) define algebra with probability intervals over periods. Knowledge-compilation (d-DNNF, SDD) reduces WMC when circuits are tractable.

**Systems-SOTA:** MystiQ, Trio (uncertainty + lineage), MayBMS/SPROUT, ProbLog/PSDD-style PP engines, and ProvSQL (probability via provenance circuits) handle value uncertainty; none natively handle *continuous endpoint* uncertainty at scale. Discretized time-uncertainty is handled by sampling in modern PP systems and by interval-probabilistic extensions in research prototypes; lakehouse/CEP engines model only point-in-time confidence, not joint value+time distributions.

## 4. Upper Bound
For **safe** temporal UCQs over discrete time with **tuple-independent** existence and **independent, discretized** endpoint distributions of support size $m$, exact evaluation is **PTIME** (in data) via lineage WMC, with an extra polynomial factor in $m$ for endpoint convolution — RAM model. For general (unsafe) queries, knowledge compilation gives time exponential only in circuit *treewidth/pathwidth*. Approximation: $(\epsilon,\delta)$ Monte-Carlo gives additive-error estimates in $O(\epsilon^{-2}\log\delta^{-1})$ samples; **dissociation/oblivious bounds** give deterministic anytime upper/lower bounds in PTIME. Continuous endpoints: WMI with piecewise-polynomial densities is solvable but #P-hard in general; tractable for hierarchical lineage with log-concave endpoint densities.

## 5. Lower Bound
Even with *certain* time, evaluating non-hierarchical UCQs (e.g. the classic $R(x),S(x,y),T(y)$) is **#P-hard** (Dalvi–Suciu) — counting, not just decision. Adding time-interval uncertainty only enlarges the hard class: queries that are *safe* without time can become **#P-hard** once endpoint randomness correlates the join variables (overlap couples otherwise independent tuples). Continuous WMI is **#P-hard** and, for general densities, lacks any FPRAS unless RP=NP for some fragments. Under exact computation these are the binding obstructions; under approximation, hardness of *relative*-error estimation persists for certain UCQs (no FPRAS unless NP=RP).

## 6. The Gap
For *value-only* uncertainty the gap is essentially **closed** by the Dalvi–Suciu dichotomy. For **joint value + time** uncertainty it is **open**: there is no dichotomy theorem characterizing which temporal queries are PTIME vs #P-hard when endpoints are random, no canonical safe-plan synthesis for sequenced operators, and no settled tractability frontier for continuous-time WMI in this setting. Closing the gap requires lifting the dichotomy to the hybrid Boolean+arithmetic lineage induced by interval algebra, and identifying endpoint-distribution classes (e.g. log-concave, bounded-support) that restore safety.

## 7. Current Research (as of June 2026)
Active: (i) **weighted model integration** advances (Belle, Suciu, Van den Broeck) bringing continuous variables into tractable probabilistic inference — directly relevant to random endpoints; (ii) probabilistic **stream/CEP** with time uncertainty and out-of-order events; (iii) probabilistic temporal **knowledge graphs** (uncertain time-stamped facts) and neuro-symbolic temporal reasoning. *(frontier — verify)* Recent work connects probabilistic-circuit (PSDD/SDD) compilation with temporal interval reasoning to get anytime bounds for joint value-time queries, and explores diffusion/score-based models of endpoint uncertainty feeding WMI back-ends. Groups: Suciu (UW), Van den Broeck/Belle (UCLA/Edinburgh), Ré (Stanford), Theobald (probabilistic temporal KGs).

## 8. Future Work
- A **dichotomy theorem** for temporal UCQs with random intervals (PTIME vs #P-hard).
- Tractable **continuous-time WMI** subclasses (log-concave / bounded-support endpoints).
- Safe-plan synthesis and dissociation bounds specialized to sequenced/overlap operators.
- Scalable systems returning **probability-over-time curves** with anytime guarantees; integration with probabilistic temporal KGs.

## 9. Key References
- **[Foundational]** Dalvi, N., Suciu, D. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* JACM, 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)
- **[Foundational]** Suciu, D., Olteanu, D., Ré, C., Koch, C. *Probabilistic Databases.* Morgan & Claypool, 2011. — [DBLP](https://dblp.org/rec/series/synthesis/2011Suciu.html)
- **[Foundational]** Dyreson, C., Snodgrass, R. *Supporting Valid-Time Indeterminacy.* ACM TODS, 1998. — [DOI](https://doi.org/10.1145/288086.288087)
- **[Foundational]** Dekhtyar, A., Ross, R., Subrahmanian, V. S. *Probabilistic Temporal Databases, I: Algebra.* (TP-databases) ACM TODS, 26(1):41–95, 2001. — [DBLP search](https://dblp.org/search?q=Probabilistic%20Temporal%20Databases%20Algebra%20Dekhtyar%20Subrahmanian)
- **[SOTA]** Gatterbauer, W., Suciu, D. *Dissociation and Propagation for Approximate Lifted Inference.* VLDBJ, 2017. — [DOI](https://doi.org/10.1007/s00778-016-0434-5)
- **[SOTA]** Belle, V., Passerini, A., Van den Broeck, G. *Probabilistic Inference in Hybrid Domains by Weighted Model Integration.* IJCAI, 2015. — [DBLP](https://dblp.org/rec/conf/ijcai/BellePB15.html)

## 10. Worked Example

Two uncertain facts over discrete days. Fact $p$: "machine A busy," exists with prob $0.6$, valid interval $[2,5)$ (certain). Fact $q$: "machine B busy," exists with prob $1.0$, but its start endpoint is random: $s_q\in\{3,4\}$ with $\Pr=(0.5,0.5)$, end $=6$.

**Query:** "Were A and B busy simultaneously?" = does $[2,5)\cap[s_q,6)\neq\varnothing$, weighted by existence.

Overlap event: $[2,5)$ meets $[s_q,6)$ iff $s_q<5$ — true for both $s_q=3$ and $s_q=4$. So conditioned on $p$ existing, overlap holds with probability $1$. Total:

$$\Pr[\text{overlap}] = \Pr[p]\cdot\Pr[q]\cdot \Pr[s_q<5] = 0.6\times 1.0\times 1.0 = 0.6.$$

**Why time couples variables.** Had the endpoints been such that overlap depended on a *join* of two random starts, the lineage formula would mix Boolean existence vars with arithmetic comparison vars ($s_p<e_q \wedge s_q<e_p$) — a hybrid **WMI** instance. A query that is *safe* (read-once) on existence alone can lose read-once-ness once $s_q$ correlates the two facts, tipping it from PTIME toward #P-hard.

---
*Part of the [DBMS Research catalog](../../README.md).*
