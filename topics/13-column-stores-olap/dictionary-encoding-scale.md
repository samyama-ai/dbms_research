# String/Dictionary Encoding at Scale

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/dictionary-encoding-scale` · **Status:** partially-solved

## 1. Problem Statement

Dictionary encoding replaces variable-length string (or wide categorical) values with fixed-width integer **codes** drawn from a per-column **dictionary** mapping $\text{code} \leftrightarrow \text{value}$. It is the backbone of columnar string storage: it shrinks data, enables bit-packing, and lets predicates and joins run on integers. At scale the hard problems are:

- **Global vs. local dictionaries:** one dictionary per column (global — best compression and cross-block code comparability, but a contended, possibly huge shared structure) vs. one per block/row-group (local — cheap to build and parallel, but codes are incomparable across blocks, hurting joins/aggregations and requiring re-encoding on merge).
- **Order-preserving codes:** assign codes so that $\text{code}(x) < \text{code}(y) \iff x < y$, enabling range predicates and sort/merge directly on codes — but order-preservation conflicts with cheap incremental insertion.
- **Maintenance under updates:** inserting a new value can require code reassignment (re-encoding the whole column) if order-preservation or dense codes must be maintained; the problem is to bound this cost.

Variants: optimization (minimize bits + maintenance cost), decision (does an order-preserving assignment with $\le b$ bits exist after $k$ inserts without re-encoding?), and counting (dictionary cardinality estimation for code-width and join planning).

## 2. Mathematical Foundations

Let a column have $d$ distinct values out of $n$ rows. A dictionary is an injection $D:\mathcal{V}\to\{0,\dots,d-1\}$; codes need $\lceil\log_2 d\rceil$ bits, so the encoded column is $n\lceil\log_2 d\rceil$ bits plus the dictionary $\sum_{v}|v|$. **Order-preserving dictionary encoding (OPDE)** additionally requires $D$ monotone w.r.t. the value order. The maintenance tension is captured by the **list-labeling / order-maintenance** problem: maintaining monotone integer labels for a dynamically inserted ordered set in a tag space of size $\Theta(\text{poly}(d))$ costs $\Theta(\log^2 d)$ amortized relabels per insert (Itai–Konheim–Rodeh; Bender et al.), or $\Theta(\log d)$ with $\Theta(d^{1+\epsilon})$ tag space. With a *dense*/minimal code space, a single insert can force $\Omega(d)$ relabels in the worst case — the source of full re-encoding.

Compression bound: by the **entropy** of the value distribution, an optimal code achieves $\ge nH_0(\text{column})$ bits; dictionary + bit-packing approaches $n\lceil\log_2 d\rceil$, near-optimal only for near-uniform value frequencies. Frequency-aware (Huffman/ANS over codes) closes the gap to $nH_0$. **Shared/global dictionaries** relate to set-union and to *dictionary intersection* for cross-column joins.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Apache **Parquet/ORC** use per-row-group (local) dictionaries with fallback to plain encoding; **Apache Arrow** dictionary arrays with delta dictionaries across batches; **SAP HANA** uses sorted (order-preserving) per-column dictionaries in the main store + an unsorted delta dictionary merged periodically; **Vertica**, **Redshift** (BYTEDICT, ZSTD), **ClickHouse** `LowCardinality`, **DuckDB** dictionary + FSST. **FSST** (Boncz, Neumann, Leis — VLDB 2020) is the SOTA for *substring*-compressible strings, complementary to whole-value dictionaries.
- **Theory-SOTA:** Order-preserving minimal-perfect/monotone hashing and the list-labeling bounds above; **OPMPHF** and Antoshenkov-style order-preserving compression (ALM, 1996) for sorted code assignment.

## 4. Upper Bound

Encoding: $n\lceil\log_2 d\rceil$ bits for fixed-width codes; with frequency-aware entropy coding over codes, $\to nH_0 + o(n)$. Order-preserving maintenance with **order-maintenance / list-labeling**: $O(\log^2 d)$ amortized relabels per insertion in polynomial tag space, $O(1)$ amortized in $n^{1+\epsilon}$ tag space (Bender–Cole–Demaine–Farach-Colton–Zito, ESA 2002). HANA's delta/main amortizes re-encoding: inserts go to an unordered delta in $O(1)$, merged in bulk so per-tuple re-encoding is amortized $O(\log d)$ over a merge cycle. Cardinality estimation for code width: HyperLogLog gives $d$ within relative error $\epsilon$ using $O(\epsilon^{-2}\log\log d)$ bits.

## 5. Lower Bound

Maintaining **dense, order-preserving** codes under insertions has an amortized relabeling lower bound of $\Omega(\log^2 d)$ per insert in linear/polynomial tag space (Bulánek, Koucký, Saks — STOC 2012/2013 prove the $\Omega(\log^2 n)$ list-labeling lower bound), so cheap order-preservation is *provably impossible* without either slack tag space or batched re-encoding. Space: any code achieving exact value recovery needs $\ge \log_2 d$ bits/row by counting; beating $nH_0$ violates Shannon. Cross-block code comparability with local dictionaries is information-theoretically impossible without storing per-block mappings, forcing $\Omega(\text{blocks}\times d_{\text{local}})$ extra metadata or a merge.

## 6. The Gap

**Partially solved.** The 1-D theory is essentially tight (encoding $\approx nH_0$; order-maintenance bounds $\Theta(\log^2 d)$ matched upper/lower). The *systems* gap is open: optimal **global-vs-local** policy under distributed ingest, dictionary sharing across columns/files, and re-encoding-free merges at petabyte scale are heuristic. *Note:* recent work (Bender et al., 2024) gives improved list-labeling beating the classic $\Omega(\log^2 n)$ in some regimes *(frontier — verify)*, which may sharpen OPDE maintenance bounds.

## 7. Current Research (as of June 2026)

- **FSST successors** and learned/per-block string compression integrated with dictionaries in lakehouse formats (Parquet v2 / Arrow) *(frontier — verify)*.
- Distributed **global dictionary** services for open table formats (shared dictionaries across Iceberg/Parquet files) to make codes joinable without re-encoding *(frontier — verify)*.
- Renewed list-labeling theory (Bender, Kuszmaul, et al., 2023–2024) tightening order-maintenance constants/lower bounds, feeding back into OPDE.

## 8. Future Work

- Re-encoding-free dictionary merge protocols at scale with provable amortized bounds.
- Cross-column / federated global dictionaries enabling integer joins across files.
- Tight bounds for order-preserving codes under concurrent distributed ingest.

## 9. Key References

- **[Foundational]** G. Antoshenkov, D. Lomet, J. Murray. *Order Preserving String Compression (ALM).* ICDE, 1996.
- **[Foundational]** M. A. Bender et al. *Two Simplified Algorithms for Maintaining Order in a List.* ESA, 2002.
- **[SOTA]** P. Boncz, T. Neumann, V. Leis. *FSST: Fast Random Access String Compression.* VLDB, 2020.
- **[SOTA]** V. Sikka et al. *Efficient Transaction Processing in SAP HANA Database.* SIGMOD, 2012.
- **[Foundational]** J. Bulánek, M. Koucký, M. Saks. *Tight Lower Bounds for the Online Labeling Problem.* STOC, 2012.
- **[Survey]** D. Abadi et al. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
