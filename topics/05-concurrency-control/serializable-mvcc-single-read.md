# Serializable MVCC With One Version Read

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/serializable-mvcc-single-read` · **Status:** open

## 1. Problem Statement
Multi-version concurrency control (MVCC) lets readers see a consistent snapshot without blocking writers. Plain snapshot-isolation (SI) is *not* serializable (write skew). The question:

> Does there exist an MVCC protocol that guarantees **serializability** while each read operation inspects **at most one version** of the accessed item, and incurs **no additional validation cost** beyond ordinary snapshot reads?

Variants:
- **Decision variant:** Given a workload class, decide whether a single-version-read serializable schedule exists for every history.
- **Optimization variant:** Among serializable single-version-read protocols, minimize aborts / version-tracking metadata / validation work.
- **Impossibility variant:** Prove that serializability + single-version-read + zero validation overhead are *mutually unsatisfiable* in the worst case.

"One version read" means the reader resolves a key to exactly one physical version (typical MVCC index lookup) and never scans a version chain or re-reads to validate. "No extra validation cost" excludes commit-time read-set re-checks, SSI antidependency bookkeeping, or predicate revalidation.

## 2. Mathematical Foundations
A multiversion history maps each read $r_i[x_j]$ to a specific writer version $x_j$. A *version order* $\ll$ totally orders versions of each item. The **Multiversion Serialization Graph** $MVSG(H, \ll)$ has edges from version order, reads-from, and induced anti-dependencies; $H$ is *one-copy serializable* iff some $\ll$ makes $MVSG$ acyclic (Bernstein–Hadzilacos–Goodman).

SI corresponds to a *fixed* snapshot timestamp $start(T_i)$ choosing the latest version $\ll commit(T_j)$. The non-serializability of SI is captured by Fekete's dangerous structure: two consecutive rw-antidependency edges in a cycle. SSI removes such cycles but needs per-transaction tracking of in/out conflict flags — i.e. *validation cost*. The open problem asks whether one can pick $\ll$ and snapshot rules so $MVSG$ is provably acyclic *by construction*, without runtime tracking, while reads stay single-version.

Theoretical lever: the class of histories where single-version reads suffice relates to **chopping** and to the existence of a *commit order = serialization order* witness computable from timestamps alone.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Serializable SI (Cabrera/Fekete/Liarokapis/O'Neil/O'Neil/Shasha, TODS 2009) achieves serializability with single-version reads but *adds* antidependency tracking and may abort spuriously. Write-Snapshot Isolation (Yabandeh–Gómez Ferro, EuroSys 2012) serializes by checking write-write/read-write conflicts at commit — single-version reads, but commit-time validation.
- **Systems-SOTA:** PostgreSQL SSI (Ports–Grittner, VLDB 2012) is the production realization, paying SIREAD-lock bookkeeping overhead. Hekaton/Silo-style MVCC (Larson et al., VLDB 2011; Tu et al., SOSP 2013) use commit-time validation. *Cicada* (Lim–Kaminsky–Andersen, SIGMOD 2017) and *TicToc* (Yu et al., SIGMOD 2016) reduce, but do not eliminate, validation.

## 4. Upper Bound
Best achievable today: serializability with single-version reads and validation **proportional to read-set size** (SSI / write-SI). No protocol attains serializability + single-version read + $O(1)$ amortized validation overhead in the general case. Commit-timestamp-ordering MVCC (e.g. BOHM, Faleiro–Abadi VLDB 2015) achieves single-version reads via deterministic pre-computed version visibility, shifting cost to a serial **sequencing** phase — an upper bound only under deterministic/partitioned execution.

## 5. Lower Bound
No unconditional lower bound forbidding the combination is published, but partial impossibilities exist: under SI snapshots, serializability provably *requires* detecting the dangerous antidependency structure (Fekete et al.), implying some validation when the snapshot rule is fixed to "latest committed." Relatedly, robustness checking — deciding whether a workload is *guaranteed* serializable under SI — is tractable for some classes but the general avoidance of validation reduces to detecting future anti-dependencies, an inherently *online* (competitive) problem with no zero-overhead strategy. This is the suspected genuine impossibility.

## 6. The Gap
Open and likely fundamental: every known serializable MVCC either re-reads/validates or pre-sequences (sacrificing generality/latency). Whether a *general-purpose*, online, single-version-read MVCC can be serializable with truly zero added validation is unresolved. Closing it needs either a constructive protocol or an impossibility proof (e.g. an adversarial-history / competitive lower bound showing validation work $\Omega(\text{conflict degree})$ is unavoidable).

## 7. Current Research (as of June 2026)
Directions: deterministic/Calvin-style sequencing to make version visibility precomputable; learned/ predictive validation that skips checks for provably-safe transactions; hardware-assisted timestamp ordering. *(frontier — verify)* Recent VLDB/SIGMOD 2025–2026 work on "validation-free" serializable MVCC under restricted (monotonic, append-mostly, or partitioned) workloads, and on certifying serializability via static analysis of stored procedures, appears active.

## 8. Future Work
- A precise dichotomy: workload classes admitting zero-validation single-version serializable MVCC vs. those provably requiring validation.
- Hybrid protocols escalating from single-version to validated mode only on detected conflict.
- Formal competitive analysis of validation overhead.

## 9. Key References
- **[Foundational]** Bernstein, Hadzilacos, Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[Foundational]** Cahill, Röhm, Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD/TODS, 2008/2009.
- **[SOTA]** Ports, Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012.
- **[SOTA]** Yabandeh, Gómez Ferro. *A Critique of Snapshot Isolation (Write-Snapshot Isolation).* EuroSys, 2012.
- **[SOTA]** Faleiro, Abadi. *Rethinking Serializable Multiversion Concurrency Control (BOHM).* VLDB, 2015.
- **[SOTA]** Tu, Zheng, Kohler, Liskov, Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
