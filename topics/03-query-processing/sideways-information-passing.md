# Sideways information passing at execution

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/sideways-information-passing` · **Status:** partially-solved
> **Verification note:** The LIP paper (PVLDB 2017) is by Zhu, Potti, Saurabh, and Patel (Wisconsin), not "Zhu/Ghosh/Krishnamurthy/Ross (Columbia)" as written in §3/§7 — the reference has been corrected accordingly.

## 1. Problem Statement

**Sideways Information Passing (SIP)** propagates constraints learned in one part of a query plan to *prune* work in another part: a hash-join build side yields a set (or Bloom filter, or min/max range, or semijoin set) of join keys that can filter the probe side — or even a sibling scan — before tuples are processed. Datalog's **magic sets** are the logical-optimization ancestor; at *execution* time the question is sharper: *which runtime filters (exact semijoin sets, Bloom filters, range/IN predicates) should be generated, where should they be placed/pushed in the plan, and in what order, so that the work pruned provably exceeds the cost of building and probing the filters?*

Variants: (a) **decision** — will filter $F$ at edge $e$ pay off (prune more than its build+probe cost)?; (b) **optimization** — choose a *set* of filters and placements maximizing pruned work minus overhead under a budget (a coverage problem); (c) **exact vs. approximate** — semijoin (exact, may be large) vs. Bloom (compact, false positives); (d) **cyclic SIP** — passing information around join cycles (bidirectional/iterative) as in Yannakakis-style full reducers and bushy SIP. The "provably prune" requirement distinguishes this from purely heuristic filter pushdown.

## 2. Mathematical Foundations

A **semijoin** $R \ltimes S = \{ r\in R : \exists s\in S,\ r[A]=s[A]\}$; **Yannakakis's algorithm** uses a bottom-up then top-down sweep of semijoins to fully reduce an **acyclic** conjunctive query so that every surviving tuple participates in the output, giving $O((|D|+|\text{out}|)\cdot \text{poly})$ — optimal for $\alpha$-acyclic queries. SIP generalizes this to arbitrary (including cyclic) plans and to *approximate* reducers. Bloom filters give membership with false-positive rate $\approx (1-e^{-kn/m})^k$, optimal at $k=\frac{m}{n}\ln 2$ and $\approx 0.6185^{m/n}$, costing $\approx 1.44\log_2(1/\epsilon)$ bits/key. Choosing a profitable set of filters under build/probe cost is a **submodular maximization / set-cover** problem (diminishing returns in pruning as filters overlap). For cyclic queries, full reduction is impossible by semijoins alone; **GYO / acyclicity** and **fractional hypertree width** characterize when SIP fully reduces vs. only partially prunes.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Yannakakis gives optimal full reduction for acyclic CQs; for cyclic queries, tree decompositions + SIP reduce to width-bounded subproblems. **Systems-SOTA:** Runtime Bloom/semijoin filters are ubiquitous — **Spark dynamic partition pruning & runtime Bloom filters**, **Impala/Presto/Trino runtime filters** (min/max + Bloom pushed from build to probe scan), **Snowflake/BigQuery** join-key pruning, **Oracle Bloom filter pushdown** for partition-wise joins, and **DuckDB/Umbra** zone-map + Bloom pushdown. **LIP (Look-ahead Information Passing)** (Zhu et al., SIGMOD 2017) gives a principled adaptive ordering of Bloom-filter probes in star-schema joins with robustness guarantees. SIP across scans using min/max **zone maps** prunes I/O before tuples materialize.

## 4. Upper Bound

For **acyclic** conjunctive queries, Yannakakis-style SIP achieves $O\big((|D| + |\text{out}|)\cdot |Q|\big)$ time — output-optimal, RAM model. A single Bloom filter of $m$ bits prunes the probe side in $O(1)$ per tuple with controllable false-positive rate; semijoin reducers are exact at $O(|R|+|S|)$ per edge. **LIP** orders the application of $k$ filters to be *competitive with the best fixed order* (an online/experts guarantee) so adaptive SIP never does much worse than optimal filter ordering. Choosing a near-optimal filter *set* under a budget is $(1-1/e)$-approximable via greedy submodular maximization when pruning is submodular.

## 5. Lower Bound

For **cyclic** queries, no sequence of semijoins fully reduces the relations (Yannakakis); the **AGM bound** lower-bounds achievable pruning since output can be as large as $\mathrm{AGM}(Q)$ regardless of filters. Boolean conjunctive-query evaluation hardness and **fine-grained** barriers (triangle/OV/SETH) bound how much *any* pre-filtering can help on adversarial cyclic instances. The set-of-filters selection problem inherits **NP-hardness** from weighted set cover / submodular maximization (so exact optimal placement is hard, matching the greedy $(1-1/e)$ inapproximability of Feige). Bloom filters cannot beat the $\Omega(n\log(1/\epsilon))$ space bound for approximate membership (Carter–Wegman / Pagh–Pagh–Rao), capping how compact a reducer can be.

## 6. The Gap

For **acyclic** SIP the picture is **closed** (Yannakakis optimal; LIP near-optimal filter ordering). The **partially-solved** label reflects the open pieces: (a) jointly optimal **selection + placement + sizing** of a *set* of filters across a bushy/cyclic plan with build/probe overhead is only greedily approximated, with no instance-optimal execution-time algorithm; (b) cyclic SIP's *partial* pruning has no tight cost/benefit characterization; (c) interaction with adaptivity (deciding at runtime whether a filter will pay off) lacks regret guarantees beyond the star-schema LIP case. Closing it means a provable cost model that picks the profitable filter set and placement on general plans.

## 7. Current Research (as of June 2026)

(1) **Adaptive runtime-filter ordering & gating** beyond star schemas — generalizing LIP to bushy and cyclic plans with robustness guarantees. (2) **Cross-operator and cross-scan SIP** using zone maps / min-max + Bloom to prune storage I/O (lakehouse formats: Iceberg/Delta data skipping driven by runtime keys). (3) **Joint SIP + WCOJ** — passing information sideways inside worst-case-optimal join intersections. (4) **Learned filter sizing** (see adaptive-bloom-pushdown). Groups: Ross/Zhu (Columbia, LIP), the Trino/Presto and Spark runtime-filter teams, Suciu/Ngo on Yannakakis-with-filters. *(frontier — verify)* 2025–2026 work reports SIP integrated with Yannakakis-style execution in columnar engines giving provable pruning on acyclic analytics and heuristic gains on cyclic joins.

## 8. Future Work

- A provable cost model for joint filter selection, placement, and sizing on general bushy/cyclic plans.
- Tight cost/benefit theory for *partial* (cyclic) SIP and its interaction with tree decompositions / fhw.
- Robust adaptive gating that turns off unprofitable filters mid-query with regret bounds.
- SIP that prunes at the storage layer (data-skipping) driven by runtime join keys, with I/O-cost guarantees.
- Integration of semijoin/Bloom SIP inside worst-case-optimal and Yannakakis-style execution.

## 9. Key References

- **[Foundational]** Yannakakis. *Algorithms for Acyclic Database Schemes.* VLDB 1981. — [DBLP](https://dblp.org/rec/conf/vldb/Yannakakis81.html)
- **[Foundational]** Bancilhon, Maier, Sagiv, Ullman. *Magic Sets and Other Strange Ways to Implement Logic Programs.* PODS 1986. — [DOI](https://doi.org/10.1145/6012.15399)
- **[Foundational]** Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970. — [DOI](https://doi.org/10.1145/362686.362692)
- **[SOTA]** Zhu, Potti, Saurabh, Patel. *Looking Ahead Makes Query Plans Robust (Look-ahead Information Passing).* PVLDB 10(8), 2017. — [DBLP](https://dblp.org/rec/journals/pvldb/ZhuPSP17.html)
- **[SOTA]** Ives, Taylor. *Sideways Information Passing for Push-Style Query Processing.* ICDE 2008. — [DOI](https://doi.org/10.1109/ICDE.2008.4497486)
- **[Survey]** Pagh, Pagh, Rao. *An Optimal Bloom Filter Replacement.* SODA 2005. — [DBLP](https://dblp.org/rec/conf/soda/PaghPR05.html)

## 10. Worked Example

Star-schema join: fact $F$ has $10^6$ rows; two dimension filters keep
$|D_1|=10$ keys (selectivity $10^{-4}$ on $F.k_1$) and $|D_2|=10^4$ keys (selectivity
$10^{-1}$ on $F.k_2$). Build a Bloom filter from each dimension's surviving keys and probe
$F$ with both before the joins.

**Pruning power.** Filter $f_1$ passes a fraction $\approx 10^{-4}$ of $F$; $f_2$ passes
$\approx 10^{-1}$. Apply the most selective first: after $f_1$, only $\approx 100$ rows
remain; $f_2$ then probes just those $100$, not $10^6$.

**Why order matters (LIP).** Wrong order ($f_2$ then $f_1$) probes $f_2$ on all $10^6$ rows
and leaves $\approx 10^5$ for $f_1$ — about $10^6$ wasted $f_2$ probes. LIP's adaptive
reordering tracks observed pass-rates and converges to the $f_1$-first order, staying
competitive with the best fixed order.

**Cost check.** Each Bloom probe is $O(1)$; at $\epsilon=0.01$ a filter costs
$\approx 1.44\log_2(1/\epsilon)\approx 9.6$ bits/key, so $f_1$ needs $\approx 12$ bytes
total — pruning $\sim10^6$ rows for a few bytes of filter.

---
*Part of the [DBMS Research catalog](../../README.md).*
