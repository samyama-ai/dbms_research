# Phantom Prevention Without Predicate Locks

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/phantom-prevention-cost` · **Status:** partially-solved

## 1. Problem Statement
A *phantom* arises when a transaction re-evaluates a predicate (e.g. `WHERE salary > 100k`) and sees a row inserted/deleted by a concurrent transaction, violating serializability even though no individual row was conflictingly accessed. Full **predicate locking** prevents phantoms but is impractical (predicate satisfiability is intractable, and locks don't compose by index). Index **gap/next-key locking** approximates it but locks ranges pessimistically and is index-structure-specific. The problem:

> **Minimize the cost** (lock metadata, blocking, false conflicts, abort rate) of preventing phantoms while guaranteeing serializability, *without* full predicate locks or full index-gap locks.

Variants:
- **Decision variant:** Does a given execution exhibit a phantom under protocol $P$?
- **Optimization variant:** Among phantom-safe protocols, minimize expected concurrency loss (false-conflict rate / lock footprint) for a workload.
- **Lower-bound variant:** What is the minimum tracking information any phantom-safe protocol must maintain?

## 2. Mathematical Foundations
A predicate $\varphi$ defines a (possibly infinite) set of *potential* tuples. Two operations *predicate-conflict* if one writes a tuple $t$ and another reads/predicate-reads with $\varphi(t)$ true. The serialization graph must include **predicate anti-dependencies**: $T_i \xrightarrow{rw} T_j$ if $T_j$ inserts/deletes a tuple matching a predicate $T_i$ read. Phantom-free serializability requires acyclicity of this *augmented* $DSG$.

Predicate locking soundness rests on: $\text{lock}(\varphi_1)$ and $\text{write}(t)$ conflict iff $\varphi_1(t)$ — deciding which is **predicate satisfiability**, NP-hard for general SQL predicates. Practical protocols replace $\varphi$ by a *coarsening* $C(\varphi) \supseteq \{t : \varphi(t)\}$ (e.g. a key range covering the predicate) so that $C$ is cheaply testable; soundness needs $C$ to over-approximate, while *cost* grows with the over-approximation's false-conflict volume. SSI instead tracks *materialized* rw-antidependencies on scanned index pages/ranges (SIREAD locks), trading false conflicts for read-only metadata.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Eswaran et al. (CACM 1976) introduced predicate locks and proved the predicate-satisfiability obstacle. Precision locking and granular/multi-granularity locking (Gray et al.) give sound, cheaper approximations. The augmented serialization-graph theory (Adya/Bernstein-Hadzilacos-Goodman) frames phantom-safety as antidependency-cycle freedom.
- **Systems-SOTA:** **Next-key / gap locking** in InnoDB (and ARIES/KVL key-range locking, Mohan VLDB 1990) is the dominant production technique. **SSI** (Ports–Grittner, VLDB 2012) prevents phantoms via index-range SIREAD locks plus the dangerous-structure test, avoiding blocking entirely. In-memory systems (Silo, Hekaton) use **phantom-avoidance via index-node version validation** — readers record the version of scanned B-tree/Masstree nodes and re-validate at commit, detecting structural changes that imply phantoms.

## 4. Upper Bound
Best practical: **per-scan index-node validation** (Silo, Tu et al. SOSP 2013) — phantom detection at cost $O(\text{nodes scanned})$ in read-set metadata, *no* range locks, no predicate evaluation. SSI gives non-blocking prevention at cost $O(\text{ranges read})$ SIREAD locks plus conflict-flag tracking. Both are sound for serializability; neither requires general predicate satisfiability. These define the current upper-bound cost frontier (linear in scanned structure, no exponential predicate reasoning).

## 5. Lower Bound
A phantom-safe protocol must distinguish "the set matching $\varphi$ was stable" from "an insert/delete changed it," so it must record *enough* about the read predicate's footprint to detect any conflicting future insert. Information-theoretically, this requires $\Omega(|\text{read footprint}|)$ tracking in the worst case (you cannot detect an insertion into a region you recorded nothing about). For *exact* predicate locking, soundness decisions reduce to **predicate satisfiability**, which is NP-hard (Eswaran et al.) and undecidable for sufficiently rich predicate languages — the canonical hardness barrier forcing approximation.

## 6. The Gap
Partially solved: phantoms are *prevented* cheaply in practice via gap locks / node validation / SIREAD. The open gap is *optimality* — these methods generate **false conflicts** (range locks over-cover; node validation aborts on unrelated co-located inserts) and are tied to a specific index. No protocol is known that achieves minimal false-conflict rate for arbitrary predicates with structure-independent, near-tight tracking. Closing it needs predicate-aware coarsenings with provable false-conflict bounds, or a matching lower bound showing the current linear-footprint cost is essentially optimal.

## 7. Current Research (as of June 2026)
Directions: learned/range-summary predicate coarsenings (e.g. using learned indexes / Bloom-style range fingerprints) to shrink false conflicts; phantom-safe validation for LSM and learned-index structures; precision-locking revivals for in-memory engines. *(frontier — verify)* 2025–2026 work integrating predicate-lock approximations with vectorized/columnar scans and with serializable snapshot isolation on cloud-native (disaggregated) storage appears active at SIGMOD/VLDB.

## 8. Future Work
- False-conflict-optimal predicate coarsenings with provable bounds.
- Structure-independent phantom detection (works across B-tree, LSM, learned index).
- Tight lower bounds on tracking metadata for phantom-safety.

## 9. Key References
- **[Foundational]** Eswaran, Gray, Lorie, Traiger. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[Foundational]** Mohan. *ARIES/KVL: A Key-Value Locking Method for Concurrency Control of Multiaction Transactions on B-Tree Indexes.* VLDB, 1990. — [ACM](https://dl.acm.org/doi/10.5555/645916.672135)
- **[SOTA]** Cahill, Röhm, Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD/TODS, 2008/2009. — [ACM](https://dl.acm.org/doi/10.1145/1376616.1376690)
- **[SOTA]** Ports, Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1208.4179)
- **[SOTA]** Tu, Zheng, Kohler, Liskov, Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013.
- **[Foundational]** Bernstein, Hadzilacos, Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)

## 10. Worked Example

Table `Emp(id, salary)` holds rows with salaries $\{90k, 110k, 130k\}$, indexed on `salary`.

- $T_1$: `SELECT COUNT(*) FROM Emp WHERE salary > 100k` → reads 2 rows ($110k, 130k$).
- $T_2$: concurrently `INSERT (id=9, salary=120k)`, then commits.

If $T_1$ re-runs its predicate it now sees 3 rows — a **phantom**. No single existing row was write-conflicted, so item-level locks miss it.

Compare cost of three phantom-safe responses:
- **Predicate lock:** lock $\{salary>100k\}$; admitting $T_2$ requires deciding $120k>100k$ (predicate satisfiability) — sound but general-case NP-hard.
- **Gap/next-key lock:** lock the index gap $(100k, +\infty)$; the insert at $120k$ falls in the locked gap → $T_2$ blocks. Cost $O(\log N)$, but it would also block a harmless insert at $200k$ (false conflict).
- **Silo node-validation:** $T_1$ records the version of the scanned B-tree leaf; $T_2$'s insert bumps that version, so $T_1$ aborts at commit. Cost $O(\text{nodes scanned})$, no range lock — but co-located unrelated inserts also trigger aborts.

Each prevents the phantom; they differ only in false-conflict footprint — the heart of the open optimality gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
