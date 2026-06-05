# Serializability certification overhead bounds

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/serializability-certification-overhead` · **Status:** open

## 1. Problem Statement

**Optimistic concurrency control (OCC)** executes a transaction speculatively and, at commit,
runs a **validation / certification** step that decides whether committing it preserves
serializability (no cycle in the conflict graph among concurrent committed transactions). In a
*distributed* SQL system, this certification spans shards and must aggregate read/write sets and
timestamps. The problem is to establish **lower bounds** on the unavoidable cost of this
certification — in messages, latency rounds, metadata size, and per-record work — as a function
of transaction footprint, concurrency, and the consistency target.

- **Lower-bound (decision) variant:** what is the minimum information any protocol must exchange
  / store to *decide* that a candidate schedule is serializable?
- **Optimization variant:** minimize certification cost (e.g., validation comparisons, read-set
  shipping, coordination rounds) at a fixed abort rate and isolation level.
- **Counting/structure variant:** how does cost scale with the size of the conflict graph and the
  number of concurrent transactions a committing txn must check against?

## 2. Mathematical Foundations

Serializability $=$ acyclicity of the **conflict-serialization graph** $\mathit{CSG}$
(Eswaran–Gray–Lorie–Traiger 1976; Papadimitriou 1979 shows testing serializability of an
arbitrary schedule is **NP-complete** in general, while *conflict*-serializability is
polynomial via cycle detection). Certifying a committing txn $T$ requires checking, for its read
set $R(T)$ and write set $W(T)$, that no concurrently committed $T'$ induces a back-edge — the
**backward/forward validation** of Kung–Robinson (1981). The information needed is essentially
$T$'s footprint plus the **overlapping** footprints of concurrent txns.

In the distributed setting this becomes a **communication-complexity** problem: shards holding
disjoint pieces of $R(T)\cup W(T)$ must jointly compute whether a conflict edge exists, i.e.,
evaluate a predicate (set-disjointness-like) over distributed sets. **Set-disjointness** has
communication complexity $\Omega(n)$ (Kalyanasundaram–Schnitger; Razborov), suggesting an
intrinsic floor when validation must compare large read sets across nodes. Deterministic and
**timestamp-ordering** approaches replace certification with pre-assigned order (no graph test),
shifting cost from validation to ordering.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Papadimitriou (1979) — *the* complexity baseline for serializability testing.
  Communication-complexity lower bounds (set-disjointness) are the canonical tool but have **not**
  been sharply applied to distributed transaction certification; the field lacks a tight,
  problem-specific lower bound.
- **Systems SOTA:** **Silo** (SOSP 2013) shows near-zero-overhead OCC on a single machine via
  epoch-based validation avoiding shared-memory contention. **FaRM**, **Sundial** (read-write
  conflict avoidance via *logical leases*), and **TicToc** (data-driven timestamps, SIGMOD 2016)
  reduce certification cost and abort rate. Distributed OCC in **Percolator/TiDB** validates via
  per-key write intents + a timestamp oracle. **Spanner** uses pessimistic 2PL + 2PC, sidestepping
  certification. Deterministic systems (**Calvin/Aria**) replace it with pre-agreed order.

## 4. Upper Bound

Backward validation against $C$ concurrently committed transactions with footprint size $f$ costs
$O(C\cdot f)$ comparisons; with sorted read/write sets or interval/index structures it drops to
$O(f \log f)$ per txn plus conflict lookups. **TicToc/Sundial** make it effectively $O(f)$ amortized
by attaching logical timestamps/leases to records, deciding commit-ts feasibility locally and only
shipping $O(f)$ metadata. Distributed certification adds $O(k)$ coordination messages for $k$ shards
(folded into the 2PC prepare phase), so the *extra* cost over commit is $O(f + k)$ metadata/messages
per txn in the best engineered systems. These are the best constructive upper bounds; whether they
are optimal is open.

## 5. Lower Bound

- **Detection hardness:** general serializability testing is **NP-complete** (Papadimitriou 1979),
  though the *conflict-serializable* restriction used in practice is poly-time, so the binding
  bounds are communication/space, not NP-hardness.
- **Communication floor:** deciding whether two transactions on different shards conflict on their
  read/write sets reduces to **set-disjointness**, giving $\Omega(f)$ bits of communication in the
  worst case to certify against a single peer — and $\Omega(C\cdot f)$ against $C$ peers without
  shared structure. This is a genuine lower bound but is **loose**: real validation reuses indexes,
  timestamps, and leases, and no tight bound captures how much that structure can save.
- **Coordination floor:** strict serializability needs at least one cross-shard round to fix commit
  order (PACELC/CAP latency cost), so $\ge 1$ message delay per distributed certification.

## 6. The Gap

There is a wide, **genuinely open** gap. Upper bounds (TicToc/Sundial/Silo, $\approx O(f)$ amortized
metadata + $O(k)$ messages) are excellent in practice, but there is **no matching lower bound** that
proves certification *must* cost this much, nor one that rules out a cheaper protocol. The
set-disjointness reduction gives only a coarse $\Omega(f)$-per-peer floor and ignores the leverage of
indexes, timestamps, and approximate (false-positive-tolerant) conflict tests. The central open
question — *is there an unconditional, structure-aware lower bound on distributed serializability
certification matching the best OCC implementations?* — is unresolved.

## 7. Current Research (as of June 2026)

- **Approximate / probabilistic certification** (Bloom-filter-style conflict summaries) trading a
  controlled abort/false-positive rate for sub-linear metadata *(frontier — verify)*.
- Sharper **communication-complexity** models of distributed validation that account for shared
  index structure, narrowing the loose set-disjointness bound *(frontier — verify)*.
- **Lease/timestamp-based** designs (descendants of Sundial/TicToc) pushing validation cost toward
  the conjectured floor; learned conflict prediction to skip validation on low-risk txns.
- Deterministic execution as an *avoidance* strategy, reframing the question as "ordering cost vs.
  certification cost."
Groups: MIT (Madden/Yu), Yale (Abadi), CMU (Pavlo), Microsoft Research.

## 8. Future Work

- An unconditional lower bound on certification metadata/communication that matches engineered OCC.
- A formal cost model unifying validation comparisons, message rounds, and abort rate as a single
  Pareto surface.
- Tight bounds for *approximate* serializability certification under a target abort budget.
- Reductions establishing whether sub-linear certification implies breaking known hard problems.

## 9. Key References

- **[Foundational]** Papadimitriou, C. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** Kung, H.T., Robinson, J. *On Optimistic Methods for Concurrency Control.* ACM TODS, 1981. — [DOI](https://doi.org/10.1145/319566.319567)
- **[Foundational]** Eswaran, K., Gray, J., Lorie, R., Traiger, I. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976. — [DOI](https://doi.org/10.1145/360363.360369)
- **[SOTA]** Tu, S., Zheng, W., Kohler, E., Liskov, B., Madden, S. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** Yu, X., Xia, Y., Pavlo, A., Sanchez, D., Rudolph, L., Devadas, S. *Sundial: Harmonizing Concurrency Control and Caching.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3231751.3231763)
- **[Foundational]** Kalyanasundaram, B., Schnitger, G. *The Probabilistic Communication Complexity of Set Intersection.* SIAM J. Discrete Math, 1992. — [DOI](https://doi.org/10.1137/0405044)

## 10. Worked Example

OCC validation trace. Transaction $T$ reads $R(T)=\{a,b\}$ at versions $\langle a_3, b_1\rangle$ and writes $W(T)=\{b\}$. Between $T$'s start and commit, two transactions committed: $T'_1$ wrote $\{a\}$ (bumping $a$ to $a_4$), $T'_2$ wrote $\{c\}$.

Backward validation checks each committed $T'_i$ overlapping $T$'s read set:
- $T'_1$: $W(T'_1)\cap R(T)=\{a\}\neq\varnothing$, and $T$ read $a_3$ while $T'_1$ produced $a_4$ — a **stale read**. Conflict edge $T'_1 \to T$ would close a cycle; $T$ **aborts**.
- $T'_2$: $W(T'_2)\cap R(T)=\varnothing$ — no conflict, skip.

Cost: comparing against $C=2$ committed txns with footprint $f=2$ is $O(C\cdot f)=4$ naive comparisons; with sorted/indexed read sets it drops to $O(f\log f)$.

Distributed twist: if $a$ lives on shard $X$ and $b$ on shard $Y$, deciding the $\{a\}$ overlap reduces to **set-disjointness** across $X,Y$, forcing $\Omega(f)$ bits of communication per peer — the lower-bound floor that no engineered OCC has been proven to beat tightly.

---
*Part of the [DBMS Research catalog](../../README.md).*
