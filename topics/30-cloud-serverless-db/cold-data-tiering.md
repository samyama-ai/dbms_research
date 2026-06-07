---
id: 30-cloud-serverless-db/cold-data-tiering
title: "Cold-data tiering with access-cost guarantees"
topic: 30-cloud-serverless-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cold-data tiering with access-cost guarantees

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/cold-data-tiering` · **Status:** partially-solved

## 1. Problem Statement

Cloud storage offers a hierarchy of classes — hot (SSD/standard), warm (infrequent-access), cold (archive, e.g., Glacier) — with a cost tradeoff: colder tiers have lower **storage** $/GB-month but higher **retrieval** $/GB plus latency (and sometimes minimum-residency penalties or early-deletion fees). Given an online stream of object accesses with **unknown, possibly non-stationary** distribution, decide which tier each object lives in (and when to promote/demote) to minimize total expected cost (storage + retrieval + migration), ideally with a provable bound on competitive ratio or on expected retrieval cost.

Variants:
- **Online (competitive):** Tier placement decided online; compare to the offline optimum.
- **Decision:** Given a budget $B$ and access trace, is there a placement keeping expected retrieval cost $\le \tau$?
- **Stochastic:** Accesses i.i.d. or Markovian; minimize expected steady-state cost (closed-form tier thresholds).
- **With residency constraints:** Minimum-storage-duration and early-deletion fees make demotion irreversible-ish (commitment cost).

## 2. Mathematical Foundations

Per-object, the core is a **rent-or-buy / ski-rental** decision: keeping an object hot costs storage rent per unit time; demoting saves rent but risks paying retrieval (buy) on the next access. The classic ski-rental optimum (break-even when accumulated rent equals buy cost) gives the **2-competitive** deterministic and $e/(e-1)\approx1.58$ randomized policy. With migration cost between tiers, the multi-state generalization is a **Metrical Task System (MTS)** / $k$-server-flavored problem on the tier "line" (hot–warm–cold), where moving between tiers incurs migration distance.

Under a known stationary access rate $\lambda$ per object, the optimal tier is a **threshold rule**: object belongs in tier $t$ minimizing $s_t + \lambda\,(r_t + \ell_t \cdot \text{penalty})$ where $s_t$ is storage cost-rate, $r_t$ retrieval cost, $\ell_t$ latency penalty — a simple equimarginal/threshold partition of objects by access frequency (an **LRU/LFU-with-cost** characterization). Caching/eviction theory (competitive paging, **LRU is $k$-competitive**; Belady offline optimal) underpins the hot-tier admission decision; the cost-asymmetric tiers turn it into **weighted caching / file caching**, which has a known $k$-competitive (LANDLORD/Greedy-Dual-Size) algorithm.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** S3 **Intelligent-Tiering** auto-moves objects across access tiers by observed idle time; Azure Blob and GCS offer lifecycle policies and autoclass. DB engines (Snowflake, BigQuery, Vertica) and lakehouses tier partitions to cheaper storage by age/access. **OctopusFS**, **hatS**, and HDFS heterogeneous storage do multi-tier placement. ML-driven tiering predicts object temperature.
- **Theory-SOTA.** Ski-rental and its randomized optimum; weighted/file caching (Young's LANDLORD / Greedy-Dual-Size, $k$-competitive); MTS competitive theory (Borodin–Linial–Saks); **learning-augmented ski-rental** (Purohit–Svitkina–Kumar, NeurIPS 2018) giving consistency/robustness tradeoffs with predictions.

## 4. Upper Bound

Per-object tiering reduces to ski-rental: **2-competitive** deterministic, **$e/(e-1)$-competitive** randomized, against the offline optimum — unconditional. Hot-tier admission/eviction under cost-asymmetric tiers is **$k$-competitive** via Greedy-Dual-Size/LANDLORD (optimal for deterministic online caching). Learning-augmented policies achieve $(1+\epsilon)$-consistency with predictions while retaining $O(1)$ robustness (Purohit et al.). Under known stationary access rates, the threshold rule is **exactly optimal** (closed form). These hold in the online competitive and stochastic models respectively.

## 5. Lower Bound

Deterministic online tiering cannot beat **2-competitive** (ski-rental lower bound); randomized cannot beat **$e/(e-1)$**. Online caching/paging has a deterministic **$k$-competitive** lower bound (and $\Omega(\log k)$ randomized via the coupon-collector / MTS argument), inherited by hot-tier eviction. With migration costs the MTS lower bound is $\Omega(\log n / \log\log n)$-randomized on general metrics. These are tight against their upper bounds. No *better-than-ski-rental* bound is possible without distributional assumptions or predictions — an information-theoretic barrier under adversarial access patterns.

## 6. The Gap

For the **per-object** and **single-cache-tier** abstractions the problem is essentially **solved** — ski-rental and weighted-caching upper/lower bounds meet, hence "partially-solved". The remaining open gaps: (1) the **joint multi-tier, migration-aware, residency-constrained** problem (with early-deletion fees making demotion partly irreversible) lacks a tight competitive characterization — it is an MTS variant whose optimal ratio for the specific hot/warm/cold metric with asymmetric costs is not pinned down; (2) **non-stationary / correlated** access (bursty re-access of "cold" data) defeats threshold rules and stationary analysis; (3) integrating tiering with the **disaggregated-I/O dollar model** and SLA latency guarantees jointly. Closing it needs competitive algorithms for the constrained multi-tier metric and learning-augmented bounds under non-stationarity.

## 7. Current Research (as of June 2026)

Directions: learning-augmented tiering (predict object temperature, plug into ski-rental with robustness guarantees) — actively extended post Purohit et al. *(frontier — verify)*; non-stationary and bandit formulations of tier placement; cost-aware caching theory under cloud pricing (groups around Stanford/MIT systems and the competitive-analysis community, e.g., work building on Greedy-Dual-Size); industrial autoclass/intelligent-tiering whose exact policies are undisclosed but increasingly ML-driven *(frontier — verify)*. Vector/embedding cold storage tiering for RAG corpora is an emerging niche.

## 8. Future Work

- Tight competitive ratio for the hot/warm/cold metric with migration + residency/early-deletion fees.
- Learning-augmented multi-tier policies with consistency/robustness under non-stationarity.
- Joint tiering + remote-I/O pricing + latency-SLA optimization.
- Distributionally robust thresholds under uncertain/correlated access.
- Public traces + pricing benchmarks for reproducible tiering evaluation.

## 9. Key References

- **[Foundational]** D. D. Sleator, R. E. Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** N. E. Young. *On-Line File Caching (Greedy-Dual-Size / LANDLORD).* Algorithmica, 2002. — [DOI](https://doi.org/10.1007/s00453-001-0124-5)
- **[Foundational]** A. Borodin, N. Linial, M. Saks. *An Optimal On-Line Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[SOTA]** M. Purohit, Z. Svitkina, R. Kumar. *Improving Online Algorithms via ML Predictions.* NeurIPS, 2018. — [NeurIPS](https://proceedings.neurips.cc/paper/2018/hash/73a427badebe0e32caa2e1fc7530b7f3-Abstract.html)
- **[Survey]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge University Press, 1998. — [ACM](https://dl.acm.org/doi/book/10.5555/290169)

## 10. Worked Example

Take one object, $1$ GB. Hot tier: storage rent $s_{\text{hot}} = \$0.023$/GB-month, retrieval free. Cold tier: storage $s_{\text{cold}} = \$0.004$/GB-month, but retrieval $r = \$0.09$/GB. Demoting hot→cold is essentially free here. This is **ski-rental**: "renting" = paying the extra hot storage to keep retrieval free; "buying" = demoting and risking a $\$0.09$ retrieval on the next access.

Extra rent for staying hot vs. cold is $0.023 - 0.004 = \$0.019$/GB-month. The break-even is when accumulated extra rent equals the retrieval cost:

$$t^* = \frac{r}{s_{\text{hot}} - s_{\text{cold}}} = \frac{0.09}{0.019} \approx 4.7\ \text{months}.$$

The deterministic $2$-competitive rule: keep the object hot until it has sat idle for $t^* \approx 4.7$ months, then demote. If the next access comes at month $3$ (before $t^*$), we stayed hot and paid only rent — optimal. If no access ever comes, we paid $\approx 4.7$ months of extra rent ($\$0.089$) then demoted, vs. an offline optimum that demotes immediately; the ratio is at most $2$. With a temperature predictor (Purohit et al.), a confident "cold" prediction lets us demote early, pushing the consistency toward $1$ while ski-rental's $t^*$ rule bounds the robustness.

---
*Part of the [DBMS Research catalog](../../README.md).*
