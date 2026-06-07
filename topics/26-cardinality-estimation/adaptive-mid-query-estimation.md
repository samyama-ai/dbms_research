---
id: 26-cardinality-estimation/adaptive-mid-query-estimation
title: "Online / Adaptive Re-Estimation During Execution"
topic: 26-cardinality-estimation
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Online / Adaptive Re-Estimation During Execution

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/adaptive-mid-query-estimation` · **Status:** partially-solved
> **Verification note:** The POP paper (Markl, Raman, Simmen, Lohman, Pirahesh, Cilimdzic) appeared at SIGMOD 2004 (DOI 10.1145/1007568.1007642), not VLDB 2004 as stated in §3.

## 1. Problem Statement

Static optimization commits to a plan from a priori estimates that can be badly wrong. **Adaptive query processing** instead observes *actual* cardinalities as operators run and refines estimates and the plan mid-flight. The problem: **use runtime feedback to re-estimate downstream cardinalities and re-optimize the remaining plan, maximizing end-to-end performance while bounding re-optimization overhead and avoiding instability.**

Variants:

- **Mid-query re-optimization (online optimization):** at materialization/pipeline boundaries, compare observed vs estimated cardinalities; if divergence exceeds a threshold, re-optimize the suffix plan.
- **Continuous adaptivity (streaming/operator-level):** route tuples adaptively (eddies), or switch join orders/algorithms during a single pipeline.
- **Feedback persistence (learning):** fold observed cardinalities back into the statistics catalog so future queries benefit (distinct from, but adjacent to, the within-query problem).

It matters because a single severe under-estimate can cause a catastrophic operator (e.g. unbounded nested-loop); reacting at runtime can rescue such plans when static CE cannot.

## 2. Mathematical Foundations

Let observed cardinalities at checkpoints update a belief over remaining-subplan cardinalities $\mathbf c_{rem}$. Re-optimization is **online sequential decision-making**: at each checkpoint choose to continue or re-plan, balancing expected improvement against re-optimization cost and already-sunk work — a stopping/switching problem analyzable via **competitive analysis** (ratio to the offline-optimal plan) and online-learning **regret** (vs the best fixed plan in hindsight).

Foundations:

- **Conditioning on observations:** observed exact cardinalities at boundary $i$ refine downstream estimates by conditioning the joint $\Pr[\mathbf c_{rem}\mid \text{observed}]$; correlated subplans gain the most.
- **Eddies / routing** (Avnur–Hellerstein, SIGMOD 2000): per-tuple operator routing as a multi-armed-bandit-like adaptive policy, with the **lottery scheduling** routing rule.
- **Mid-query re-optimization** (Kabra–DeWitt, SIGMOD 1998): place *statistics-collecting* checkpoints at low-risk materialization points; re-optimize when estimates prove inaccurate — the canonical "partially-solved" technique now in commercial systems.
- **Stability:** re-optimization can oscillate; one wants monotone progress guarantees (no worse than committing), akin to a competitive-ratio guarantee.

## 3. State of the Art (SOTA)

- **Foundational/systems-SOTA:** Kabra–DeWitt mid-query re-optimization (SIGMOD 1998); **POP / progressive optimization** with validity ranges (Markl, Raman, Lohman et al., VLDB 2004) — re-optimize only when runtime cardinality leaves the plan's validity range; **eddies** and SteMs/STAIRs (Hellerstein group). **LEO** (Stillger et al., VLDB 2001) — learning optimizer feeding execution feedback back into the catalog. Adaptive execution ships in production: **Spark SQL Adaptive Query Execution (AQE)**, Oracle adaptive plans, SQL Server interleaved execution / adaptive joins.
- **Learning-SOTA:** runtime-feedback-driven learned optimizers (Bao re-routing via hints; reinforcement-style adaptivity) *(frontier — verify)*; robust/risk-aware re-optimization triggers.
- **Theory-SOTA:** competitive analysis of adaptive operator ordering and online join processing (worst-case-optimal join connections).

## 4. Upper Bound

- **Progressive optimization (POP):** validity-range checks add only $O(1)$ per checkpoint and trigger re-optimization solely when provably outside the range, giving a practical guarantee that adaptivity never fires spuriously and end-to-end cost is no worse than the static plan up to the checkpoint granularity.
- **Online routing:** eddy-style routing achieves bounded regret vs the best fixed routing under bandit assumptions; worst-case-optimal join algorithms (NPRR/LeapFrog-TrieJoin) give AGM-tight runtime $O(\text{AGM bound})$ independent of order, partially obviating order re-optimization.
- Re-optimization overhead is bounded by checkpoint placement (only at materialization boundaries) so it is amortized against work already done.

## 5. Lower Bound

- **Online competitive limits:** without lookahead, any adaptive policy can be forced into a constant-factor (or worse) competitive gap vs the offline-optimal plan on adversarial inputs — adaptivity cannot match clairvoyance.
- **Sunk-cost irreversibility:** once a pipeline has materialized expensive intermediates, no re-optimization recovers the wasted work; the achievable improvement is bounded by remaining work.
- **Decision hardness:** choosing the optimal re-optimization points/suffix plan inherits NP-hardness of join ordering; and detecting a harmful divergence early enough is limited by how much the pipeline must run before the error is observable (information-theoretic delay).

## 6. The Gap

Status is **partially-solved**: the *mechanism* (checkpoints, validity ranges, AQE) is mature and deployed, but the *policy* — when to re-optimize, how to avoid oscillation, how to credit runtime feedback to the right downstream estimates, and how to do this for deep pipelines without cheap materialization boundaries — lacks guarantees. Closing the remaining gap needs competitive/regret-bounded adaptive policies and tighter integration of runtime feedback with learned estimators.

## 7. Current Research (as of June 2026)

- Learned, feedback-driven re-optimization: RL/bandit policies deciding when to switch plans, combined with learned CE updates *(frontier — verify)*.
- Tighter, lower-overhead validity ranges and pipeline-friendly checkpoints for vectorized/columnar engines.
- Coupling within-query feedback with persistent statistics learning (LEO-style) and drift handling.
- Active groups: Berkeley (Hellerstein lineage), IBM/POP-LEO heritage, TUM/MIT learned-optimizer groups, and cloud-engine teams (Spark AQE, Snowflake/Redshift adaptive features) *(frontier — verify)*.

## 8. Future Work

- Adaptive policies with provable competitive ratios against the offline-optimal plan.
- Stability/anti-oscillation guarantees for repeated re-optimization.
- Mid-pipeline adaptivity without expensive materialization barriers.
- Unified runtime-feedback loop feeding both within-query re-optimization and cross-query learned statistics.

## 9. Key References

- **[Foundational]** Kabra, DeWitt. *Efficient Mid-Query Re-Optimization of Sub-Optimal Query Execution Plans.* SIGMOD, 1998. — [DOI](https://doi.org/10.1145/276304.276315)
- **[Foundational]** Avnur, Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335420)
- **[Foundational]** Markl, Raman, Simmen, Lohman, Pirahesh, Cilimdzic. *Robust Query Processing through Progressive Optimization (POP).* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007642)
- **[Foundational]** Stillger, Lohman, Markl, Kandil. *LEO – DB2's LEarning Optimizer.* VLDB, 2001. — [DBLP](https://dblp.org/rec/conf/vldb/StillgerLMK01.html)
- **[Survey]** Deshpande, Ives, Raman. *Adaptive Query Processing.* Foundations and Trends in Databases, 2007. — [DOI](https://doi.org/10.1561/1900000001)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)

## 10. Worked Example

Plan a 3-way join $A \bowtie B \bowtie C$ with $|A|=10^6$, $|B|=10^3$, $|C|=10^6$. The optimizer's estimate for $A \bowtie B$ is $\hat c = 10^4$ rows (assuming low selectivity), so it picks: materialize $A \bowtie B$, then **nested-loop** it against $C$. Cost model expects $\approx 10^4 \times (\text{index probes})$.

A **statistics-collecting checkpoint** sits at the materialization boundary of $A \bowtie B$. At runtime the actual count is observed: $c_{obs} = 8 \times 10^5$ rows — an $80\times$ under-estimate. The q-error is $\max(c_{obs}/\hat c,\ \hat c/c_{obs}) = 8\times10^5 / 10^4 = 80$.

POP's **validity range** for the chosen plan was, say, $[2\times10^3,\ 5\times10^4]$: the nested-loop is optimal only while the intermediate is below $5\times10^4$. Since $8\times10^5 \notin [2\times10^3, 5\times10^4]$, the check fires and the suffix is re-optimized — switching the second join from nested-loop to **hash join**. Re-optimization cost is $O(1)$ per checkpoint (a range test) and is incurred only after $A\bowtie B$ is already materialized, so the wasted work is bounded by that sunk first join, illustrating both the rescue and the §5 sunk-cost limit.

---
*Part of the [DBMS Research catalog](../../README.md).*
