---
id: 30-cloud-serverless-db/serverless-shuffle
title: "Serverless OLAP shuffle without warm workers"
topic: 30-cloud-serverless-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Serverless OLAP shuffle without warm workers

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/serverless-shuffle` · **Status:** partially-solved

## 1. Problem Statement

Analytical query plans use **shuffle** (repartition exchange): the output of $m$ map/producer tasks is redistributed to $r$ reduce/consumer tasks by a hash/range function on the shuffle key. In a serverless setting the workers are **ephemeral functions** (AWS Lambda, GCP Cloud Functions, Azure Functions) that are *short-lived*, *non-addressable* (no stable inbound IP/port, behind NAT), *cannot accept incoming connections*, and *cannot communicate peer-to-peer*. The problem: realize an all-to-all exchange of $O(D)$ bytes of intermediate data among such workers, when the only durable, addressable substrate is **remote storage** (S3, blob store) or an external **shuffle service**.

Variants:
- **Optimization:** minimize wall-clock shuffle latency and/or dollar cost ($=$ object-store request cost + storage-seconds + function-seconds) for a given $(m,r,D)$.
- **Decision:** given a budget and deadline, does a feasible exchange schedule exist over the storage substrate's IOPS/throughput limits?
- **Skew-robust:** same, when key frequencies are heavy-tailed (a few partitions dominate $D$).

## 2. Mathematical Foundations

The data-movement cost of dense shuffle is captured by the **MPC (Massively Parallel Computation) / MapReduce** model: with $p$ workers and load $L$ per worker, a single round of all-to-all on $D$ data needs $\Theta(D)$ aggregate communication; the relevant complexity measures are **rounds** and per-worker **load**. For joins, the optimal one-round load is governed by the **AGM bound** and its MPC realization (Koutris–Suciu, the *HyperCube/Shares* algorithm), giving per-worker load $\tilde O(|R|/p^{1/\rho^\*})$ where $\rho^\*$ is the fractional edge cover of the join query — this dictates how finely shuffle can be partitioned.

The serverless constraint adds an **indirection penalty**: each byte traverses storage twice (write then read), so naive cost is $2D$ object-store bytes plus $\Theta(m\cdot r)$ object *operations* (each producer writes one object per consumer), which blows up the per-request cost term. Reducing the $m\times r$ object count is a combinatorial design problem (multi-level merge / coalescing), analogous to **external multiway merge** with branching factor bounded by per-function memory and the I/O-complexity model $\Theta\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ (Aggarwal–Vitter).

## 3. State of the Art (SOTA)

**Systems-SOTA.** *PyWren* (Jonas et al., SoCC 2017) showed general computation on Lambda with S3 as the exchange medium. *Locus* (Pu, Venkataraman, Stoica; NSDI 2019) is the key result: it models the *cost/performance* of storage media and *mixes* slow-cheap (S3) with fast-expensive (in-memory Redis/ElastiCache) storage to hit a chosen point on the cost–latency curve, making serverless shuffle competitive with clusters for moderate data. *Starling* (Perron et al., SIGMOD 2020) builds a full serverless OLAP query engine, with a multi-stage shuffle and straggler mitigation, achieving good price/performance on TPC-H. *Lambada* (Müller, Marroquín, Alonso; SIGMOD 2020) designs an exchange operator with a two-level shuffle to cut the $m\times r$ object explosion. Cloud-native external **shuffle services** (e.g., disaggregated shuffle in Spark-on-Kubernetes, Google *Dataflow Shuffle*, Apache *Celeborn*) are the warm-server analog.

**Theory-SOTA.** MPC round/load lower bounds (Beame–Koutris–Suciu) and HyperCube optimal-load joins frame the achievable exchange efficiency.

## 4. Upper Bound

With an external storage substrate, a single-round all-to-all is achievable at aggregate cost $\Theta(D)$ bytes but $\Theta(m r)$ object operations; **two-level / hierarchical shuffle** (Lambada, Starling) reduces operation count to $\Theta\!\big((m+r)\sqrt{mr}\big)$-style or $\Theta(p\log p)$ via a fan-in tree, trading rounds for request cost. Locus gives a *cost-parameterized* upper bound: for a target latency, the minimal dollar cost is obtained by an LP over the (fast,slow) storage mix, provably on the achievable frontier of its model. For joins, HyperCube gives per-worker load $\tilde O(|D|/p^{1/\rho^\*})$ in one round. These are upper bounds in the **MPC + external-memory + cloud-pricing** composite model.

## 5. Lower Bound

In the MPC model, **one-round** computation of certain queries (e.g., connectivity, some joins) requires per-worker load $\Omega(D/p)$ and, for connectivity-like problems, $\Omega(\log p)$ rounds are conjectured/required under the *1-vs-2-cycle* hardness assumption (Beame–Koutris–Suciu; Roughgarden–Vassilvitskii–Wang). For skewed joins, the AGM/fractional-cover bound is a hard floor on communication. The serverless indirection imposes an unavoidable $\geq 2D$ storage-byte traffic and a request-count floor of $\Omega(p)$ objects for any all-to-all, since each of $p$ workers must emit at least one durable artifact. CAP/FLP are not the binding constraints here; the binding limits are **communication-complexity / I/O-complexity** ones plus the substrate's IOPS ceiling.

## 6. The Gap

This is **partially solved**: serverless shuffle works and is cost-competitive for small-to-moderate $D$, but degrades at large scale because the $\Theta(mr)$ request cost and storage round-trips dominate, and warm-cluster shuffle still wins on large, latency-sensitive jobs. The open gap is a *tight* characterization of the minimal cost–latency frontier as a function of $(m,r,D,\text{skew})$ and the substrate's price/throughput, and whether the storage-indirection $2\times$ traffic and $\Omega(p)$ request floor can be beaten by a serverless-native exchange primitive (e.g., a thin relay or storage-side aggregation). Hardware/service trends (S3 Express One Zone low-latency, function-attached fast caches) keep moving the frontier rather than closing the theory.

## 7. Current Research (as of June 2026)

Directions: **storage-side aggregation / pushdown** (combiners executed inside the object store or a thin shuffle relay) to cut request count; low-latency object tiers (*S3 Express One Zone*, single-digit-ms) reshaping Locus-style mixing *(frontier — verify)*; and integrating serverless shuffle into managed lakehouse engines. Groups/people: Alonso's group (ETH Zürich — Lambada, serverless data processing), Stoica/RISELab→Sky Computing lineage (Locus, Ray-on-serverless), Perron/Madden (MIT — Starling), and the Spark/Celeborn disaggregated-shuffle community. A frontier claim: *fast single-AZ object tiers narrow the warm-vs-cold shuffle gap enough that ephemeral workers match dedicated shuffle services for mid-size OLAP* *(frontier — verify)*.

## 8. Future Work

- A serverless-native exchange primitive with provable sub-$2D$ traffic (in-network/in-storage aggregation).
- Skew-adaptive shuffle with formal load guarantees under heavy-tailed keys.
- Joint optimization of degree-of-parallelism, storage tier, and function memory (links to function-right-sizing) on one cost–latency objective.
- Tight MPC-style lower bounds that *include* the cloud pricing model, not just communication volume.

## 9. Key References

- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* JACM / PODS, 2017 (PODS 2013). — [DOI](https://doi.org/10.1145/3125644), [arXiv](https://arxiv.org/abs/1306.5972)
- **[SOTA]** E. Jonas et al. *Occupy the Cloud: Distributed Computing for the 99% (PyWren).* SoCC, 2017. — [DOI](https://doi.org/10.1145/3127479.3128601), [arXiv](https://arxiv.org/abs/1702.04024)
- **[SOTA]** Q. Pu, S. Venkataraman, I. Stoica. *Shuffling, Fast and Slow: Scalable Analytics on Serverless Infrastructure (Locus).* NSDI, 2019. — [DBLP](https://dblp.org/rec/conf/nsdi/PuVS19.html)
- **[SOTA]** M. Perron, R. Castro Fernandez, D. DeWitt, S. Madden. *Starling: A Scalable Query Engine on Cloud Functions.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380609)
- **[SOTA]** I. Müller, R. Marroquín, G. Alonso. *Lambada: Interactive Data Analytics on Cold Data Using Serverless Cloud Infrastructure.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389758), [arXiv](https://arxiv.org/abs/1912.00937)

## 10. Worked Example

Shuffle $D = 10$ GB among $m = 1000$ producer and $r = 1000$ consumer Lambdas via S3, repartitioned by a hash on the shuffle key. **Naive one-level shuffle:** each producer writes one object per consumer, so the object count is $m\times r = 10^6$ PUTs, then $r$ consumers issue up to $m\times r = 10^6$ GETs. At S3 pricing $\$5\times10^{-6}$ per PUT and $\$4\times10^{-7}$ per GET:

$$\$_{\text{req}} \approx 10^6(5\!\times\!10^{-6}) + 10^6(4\!\times\!10^{-7}) \approx \$5.0 + \$0.4 = \$5.4,$$

while byte cost is only $2D = 20$ GB of traffic (write + read). The request term dominates and grows as $\Theta(mr)$.

**Two-level shuffle** (Lambada/Starling) inserts an intermediate aggregation tier of $g = \sqrt{mr} = 1000$ groups: producers write $m\cdot\sqrt{r}$ objects to the tier, which coalesces to $\sqrt{m}\cdot r$ — total $\Theta((m+r)\sqrt{mr}) \approx 2000\times1000 = 2\times10^6$? No: the fan-in tree cuts distinct objects to $\Theta(p\log p)$ with $p=1000$: $\approx 1000\times10 = 10^4$ objects, a $100\times$ reduction, bringing request cost to $\approx \$0.05$ at the price of one extra round (latency). This is the rounds-vs-request-cost trade §4 describes; the $\geq 2D$ byte floor and $\Omega(p)$ object floor remain.

---
*Part of the [DBMS Research catalog](../../README.md).*
