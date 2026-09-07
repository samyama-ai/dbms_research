---
id: 04-indexing-access-methods/lsm-secondary-indexing
title: "Secondary indexing on LSM-trees"
topic: 04-indexing-access-methods
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Secondary indexing on LSM-trees

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/lsm-secondary-indexing` · **Status:** partially-solved

## 1. Problem Statement
A **log-structured merge (LSM)** store ingests writes as immutable sorted runs and resolves the *latest* value of a primary key by merging across levels. A **secondary index** maps a non-key attribute value $a$ to the set of primary keys $\{k : v_a(k) = a\}$. The core difficulty is that LSM updates are **blind**: a new version of record $k$ is appended without reading its prior version, so the index cannot learn that $k$'s *old* attribute value $a_{\text{old}}$ must be retracted. This yields **stale postings** (false positives) unless extra work is performed.

The problem: **maintain a consistent secondary index over an LSM primary store while minimizing write, read, and space amplification**, and bounding **query-time validation cost**.

- **Optimization variant:** minimize $c_w W + c_r R$ subject to correctness (no false negatives; bounded false positives) and a space bound.
- **Decision variant:** given a budget, does a maintenance scheme exist that keeps index lookups within $f(N)$ I/Os while keeping ingest blind?
- **Counting/aggregate variant:** support index-only `COUNT`/`SUM` with consistent results despite deferred deletes.

*Partially solved:* validation-based (lazy) and synchronous (eager) schemes are well understood and deployed; the optimal point on the consistency/amplification curve is uncharacterized.

## 2. Mathematical Foundations
Model the store as a sequence of timestamped versions; a record is $(k, a, t)$ with monotone timestamps. The **index correctness predicate**: a posting $(a, k)$ is *valid* iff the latest version of $k$ has $v_a(k)=a$. Three implementation families:

- **Eager (synchronous):** on update, read $a_{\text{old}}$ (point lookup, $O(L)$ with $L$ levels) and emit a tombstone $(a_{\text{old}}, k, t, \text{del})$ plus $(a_{\text{new}}, k, t)$. Converts blind writes into read-modify-writes — write amp grows, lookups stay clean.
- **Lazy (validation):** index posts only $(a_{\text{new}}, k, t)$; a query for $a$ retrieves candidate keys then **validates** each against the primary store, discarding $k$ whose current value $\ne a$. Ingest stays blind; query pays $O(|\text{candidates}|)$ primary point-lookups.
- **Hybrid / repair-on-compaction:** background compaction reconciles postings, amortizing cleanup via a *visibility*-timestamp join.

Cost is governed by the LSM $(T, L, B)$ parameters and by the **selectivity** $\sigma$ of the indexed predicate; lazy validation cost scales with the *churn rate* of the indexed attribute, not just $\sigma$.

## 3. State of the Art (SOTA)
- **Systems:** **AsterixDB** pioneered validated (lazy) LSM secondary indexes with primary-key validation; **RocksDB**-based stacks (MyRocks, CockroachDB) use eager maintenance with explicit delete markers; **Cassandra/ScyllaDB** materialized views and **SAI** (Storage-Attached Indexing) give async, eventually-consistent secondary access; **HBase + Phoenix** use coprocessor-maintained indexes.
- **Research:** Luo & Carey's *Efficient Data Ingestion and Query Processing for LSM-Based Storage Systems* (VLDB 2019) formalizes eager vs. validation/lazy maintenance and stateful batched validation; **DELI** (deferred lightweight index cleanup) and primary-key-index-assisted validation reduce per-query cost.

## 4. Upper Bound
With validation, query I/O is $O(\sigma N \cdot C_{\text{point}})$ where $C_{\text{point}}=O(L)$ (or $O(1)$ expected with Monkey-style filters); batched/stateful validation amortizes this toward $O(\sigma N / B + L)$ per query. Eager maintenance bounds query I/O at $O(\sigma N / B + L)$ (clean postings) at the cost of an extra point lookup per update, giving write amp $W_{\text{idx}} = O(L)$ per indexed attribute. These are **I/O-model (DAM) upper bounds within the LSM design family** — systems-SOTA, not proven optimal.

## 5. Lower Bound
No tight unconditional lower bound is known. Constraint: any scheme keeping ingest **blind** must defer reconciliation, so *some* query or background work must touch stale entries — a conservation argument rather than a formal bound. Sorting/dictionary lower bounds (Aggarwal–Vitter $\Omega(\log_{M/B} N/B)$) lower-bound the merge component. The genuinely hard case is **high-churn attributes** under adversarial update interleavings, where lazy validation degrades to per-candidate primary probes; no proven separation establishes that eager is asymptotically forced.

## 6. The Gap
The eager↔lazy spectrum is *engineered* but not *characterized*: no theorem states, for a given $(\sigma, \text{churn}, \text{read/write mix})$, which point on the maintenance-cost/query-cost curve is optimal, nor a matching lower bound. Closing it requires a cost model unifying validation cost, compaction-time repair, and filter allocation into one optimality statement — analogous to what Monkey/Dostoevsky did for primary lookups.

## 7. Current Research (as of June 2026)
- **Compaction-integrated index repair** piggybacking reconciliation on merges to bound staleness with provable freshness windows *(frontier — verify)*.
- **Learned validation skipping**: predicting which candidates are stale to avoid primary probes *(frontier — verify)*.
- Secondary indexing for **key-value-separated** LSMs (WiscKey/BlobDB lineage), where the value log complicates validation.
- Groups: UC Irvine (AsterixDB / Carey, Luo), Harvard DASlab, BU (Athanassoulis), DataStax SAI and CockroachDB teams.

## 8. Future Work
- A Pareto-optimality theorem for LSM secondary-index maintenance across $(\sigma, \text{churn})$.
- Consistent index-only aggregates with bounded deferred-delete error.
- Multi-attribute / composite secondary indexes with shared validation state.

## 9. Key References
- **[Foundational]** P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[SOTA]** C. Luo, M. Carey. *Efficient Data Ingestion and Query Processing for LSM-Based Storage Systems.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1808.08896)
- **[SOTA]** S. Alsubaiee, et al. *Storage Management in AsterixDB.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732951.2732958)
- **[Survey]** C. Luo, M. Carey. *LSM-based Storage Techniques: A Survey.* VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)
- **[SOTA]** S. Dharmasiri, et al. *Storage-Attached Indexing for Apache Cassandra.* (DataStax / industrial track), 2023. — [DBLP search](https://dblp.org/search?q=Storage-Attached%20Indexing%20Apache%20Cassandra)

## 10. Worked Example

A users table is ingested into an LSM store keyed by `user_id`; we want a secondary index on `city`. Record $k{=}7$ is first written as $(7,\text{"Pune"},t_1)$, later updated to $(7,\text{"Goa"},t_2)$ with $t_2>t_1$ — a *blind* write, so the engine never reads the old "Pune".

**Lazy (validation):** the index now holds two postings, $(\text{Pune},7)$ and $(\text{Goa},7)$. A query `city = 'Pune'` returns candidate $\{7\}$, then point-looks-up $k{=}7$ in the primary store, finds current value "Goa" $\ne$ "Pune", and discards it — correct, but it paid $1$ primary probe ($O(L)$ I/O) for a false positive. Ingest stayed cheap.

**Eager (synchronous):** at $t_2$ the engine first reads old value "Pune" (cost $O(L)$), then emits a tombstone $(\text{Pune},7,t_2,\text{del})$ plus $(\text{Goa},7,t_2)$. The query for "Pune" returns clean postings with no validation probe — but every update now costs an extra lookup, raising write amplification.

The open problem: for a given churn rate (here, how often `city` changes) and read/write mix, which point on this spectrum minimizes $c_wW+c_rR$? No theorem yet says.

---
*Part of the [DBMS Research catalog](../../README.md).*
