# Statistics Maintenance Under Updates

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/incremental-statistics-maintenance` · **Status:** partially-solved

## 1. Problem Statement

A synopsis $M$ (histogram, distinct-count sketch, sample, learned model) summarizes a relation $R$ to support selectivity estimation. As $R$ undergoes a stream of inserts, deletes, and updates, $M$ drifts from the true data distribution. The problem: **maintain $M$ incrementally** so it stays accurate, while keeping the per-update cost low (ideally $O(1)$ amortized or $O(\text{polylog})$) and the space bounded — avoiding full rescans.

Formally, over an update stream $u_1, u_2, \dots$ each transforming $R_{t-1} \to R_t$, maintain $M_t$ such that for any query $q$, $|\hat{c}_{M_t}(q) - c_{R_t}(q)|$ stays within target error, with update time $\ll |R_t|$.

Variants:
- **Insert-only (cash-register), turnstile (inserts+deletes), sliding-window** streaming models.
- **Decision:** detect *when* a synopsis has drifted enough to warrant a (costly) refresh.
- **Optimization:** schedule refreshes to minimize total cost given an accuracy SLA.

## 2. Mathematical Foundations

Grounded in the **streaming / sketching model**. Linear sketches support turnstile updates natively: **Count-Min** (Cormode–Muthukrishnan) and **AMS/AGMS** sketches are linear, so $M(R \pm e) = M(R) \pm M(e)$ in $O(1)$. **Distinct counting** uses **HyperLogLog** (Flajolet et al.) — mergeable, $O(1)$ update, $O(\varepsilon^{-2})$ space for relative error; deletions need extensions (e.g. counting variants).

Sampling under deletions is the hard case: maintaining a uniform sample of size $k$ under a turnstile stream requires **random pairing / backing-sample** techniques (Gibbons–Matias) or $\ell_p$-samplers; reservoir sampling alone handles inserts only. Quantile/histogram maintenance uses mergeable summaries (**GK**, **t-digest**, **KLL** — Karnin–Lang–Liberty optimal $O(\varepsilon^{-1}\log\log(1/\delta))$). Drift is quantified by divergence (KL, total variation, or q-error degradation) between $M_t$ and the true distribution.

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- **KLL sketch** (Karnin–Lang–Liberty, FOCS 2016): optimal-space mergeable quantile summary, supports streaming maintenance.
- **HyperLogLog / HLL++** for distinct counts; mergeable, used everywhere (Redis, Presto, BigQuery).
- **Linear sketches** (Count-Min, AGMS) for frequency/join-size moments under turnstile updates.

**Systems-SOTA:**
- Commercial **auto-update statistics** with modification-counter thresholds (SQL Server's `AUTO_UPDATE_STATISTICS`, Oracle's automatic stats gathering, PostgreSQL autovacuum/ANALYZE driven by `pg_stat` change counters).
- **Self-maintaining histograms** and incremental wavelet/sketch maintenance.
- **Maintaining learned models** is the weak spot: most learned estimators (Naru, DeepDB) require retraining; recent work explores incremental/online updates *(frontier — verify)*.

## 4. Upper Bound

Linear sketches: $O(1)$ update time, $O(\varepsilon^{-2}\log(1/\delta))$ space for frequency/inner-product (join-size) estimates under turnstile streams. KLL quantiles: $O(\log(1/\varepsilon))$ amortized update, $O(\varepsilon^{-1}\log\log(1/\delta))$ space, fully mergeable. HLL distinct count: $O(1)$ update, relative error $1.04/\sqrt{m}$ with $m$ registers. Bounded-size uniform sample under inserts+deletes: maintainable with $O(1)$ expected work via random pairing while keeping sample size near target. Refresh-scheduling can be cast as a competitive online problem.

## 5. Lower Bound

Distinct counting requires $\Omega(\varepsilon^{-2} + \log n)$ bits (Indyk–Woodruff / Kane–Nelson–Woodruff lower bounds) — HLL-class space is essentially optimal. Quantile summaries require $\Omega(\varepsilon^{-1})$ space (KLL is optimal up to the $\log\log$ factor). Maintaining a uniform sample under arbitrary deletions can force $\Omega(k)$ stored items and, adversarially, sample depletion that needs rescans — there is no turnstile sample with $o(\varepsilon^{-2})$ space and worst-case guarantees for all functionals. Detecting drift to arbitrary accuracy is information-theoretically as hard as estimating the underlying distribution change.

## 6. The Gap

**Partially solved**: for distinct counts, quantiles, frequency moments, and join-size moments, near-optimal incrementally maintainable sketches exist (upper bounds match lower bounds up to logs). The **open** frontier is (1) **uniform sampling under heavy deletion** with tight space *and* worst-case guarantees, and (2) **incremental maintenance of correlated multidimensional and learned synopses** — where current practice still falls back to periodic full retraining/rescan. Closing it needs sublinear-update learned models with accuracy guarantees and principled refresh-scheduling under accuracy SLAs.

## 7. Current Research (as of June 2026)

- **Updatable learned cardinality estimators**: incremental fine-tuning, online density models, and drift-triggered partial retraining *(frontier — verify)*.
- **Differentially private / robust** streaming sketches under adaptive (adversarial) update streams (Ben-Eliezer–Jayaram–Woodruff–Yogev robustness line).
- **Cost-aware refresh policies** balancing maintenance overhead vs. plan-quality loss.
- Mergeable summaries for distributed/partitioned tables (KLL/HLL in cloud warehouses).

## 8. Future Work

- Learned synopses with provable accuracy under $O(\text{polylog})$ per-update cost.
- Tight turnstile sampling that resists deletion-driven depletion.
- Unified drift metrics tied directly to downstream plan-quality regression.
- Adaptive/adversarially-robust maintenance for security-sensitive workloads.

## 9. Key References

- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166v1)
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[Foundational]** Gibbons, Matias. *New Sampling-Based Summary Statistics for Improving Approximate Query Answers.* SIGMOD, 1998. — [DOI](https://doi.org/10.1145/276304.276334)
- **[SOTA]** Ben-Eliezer, Jayaram, Woodruff, Yogev. *A Framework for Adversarially Robust Streaming Algorithms.* PODS, 2020. — [arXiv](https://arxiv.org/abs/2003.14265)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Maintain a Count-Min sketch with $w = 4$ columns and $d = 2$ rows (hash functions $h_1, h_2$) over a frequency stream. Linearity is the key: an insert of key $x$ adds $+1$ to one cell per row; a delete subtracts $1$ — no rescan.

Process inserts of keys with hashes
$$h_1(a)=0,\ h_2(a)=2;\quad h_1(b)=0,\ h_2(b)=1;\quad h_1(c)=3,\ h_2(c)=2.$$
After inserting $a,a,b,c$ the two rows hold
$$\text{row}_1 = [\,3,\,0,\,0,\,1\,],\qquad \text{row}_2 = [\,0,\,1,\,3,\,0\,].$$
(Row 1 col 0 = count of $a$+$b$ = 3; row 2 col 2 = count of $a$+$c$ = 3.)

Query frequency of $a$: $\hat f(a) = \min(\text{row}_1[0], \text{row}_2[2]) = \min(3,3) = 3$ — exact here, but the estimate is $\ge$ the truth because of collisions ($a$ and $b$ collide in row 1). Now **delete** one $a$: subtract $1$ at cols $0$ and $2$ giving $\text{row}_1=[2,0,0,1]$, $\text{row}_2=[0,1,2,0]$, and $\hat f(a)=2$ in $O(d)=O(1)$ work. The error bound $\hat f(x) \le f(x) + \varepsilon\lVert f\rVert_1$ holds with $w = \lceil e/\varepsilon\rceil$, matching the $\Omega(\varepsilon^{-1})$ space floor up to the $1/\varepsilon$ vs $1/\varepsilon^2$ regime for point vs distinct queries.

---
*Part of the [DBMS Research catalog](../../README.md).*
