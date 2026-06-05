# Revocation Cascade Complexity

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/revocation-cascade-complexity` · **Status:** partially-solved

## 1. Problem Statement

SQL's discretionary access control lets a privilege be granted **WITH GRANT OPTION**, so the grantee may re-grant it. This induces a directed **grant graph** whose nodes are (privilege-holding) authorizations and whose edges record "who granted what to whom, when." **REVOKE CASCADE** must remove not only the named grant but every authorization that *depends* on it and could not survive without it. The problem is to compute the correct post-revocation state — and to do so efficiently **at scale** and **under concurrency**.

Subtleties:
- **Recursive cascade:** revoking a grant may orphan downstream grants, which orphan further grants, transitively.
- **Timestamp / abandonment semantics:** SQL's standard "recursive revocation" deletes grants that lose their justifying chain *as of* the grant times (Griffiths–Wade), versus *non-cascading* (RESTRICT) and *non-recursive* variants.
- **Concurrency:** interleaved grants/revokes can produce different final states depending on serialization; we want a well-defined, ideally serializable, outcome.

Variants: *decision* (does privilege $p$ survive for subject $s$ after a revoke?), *computation* (produce the new grant set), *counting* (how many authorizations cascade), and a *concurrency-correctness* variant (is the schedule equivalent to a serial one?).

## 2. Mathematical Foundations

Model the grant state as a directed graph $G=(V,E)$ where each authorization is a tuple $\langle \text{grantor}, \text{grantee}, \text{priv}, \text{grant-option}, t \rangle$. A node is **valid** iff there is a path from a *source of authority* (the object owner / system) to it. The seminal **Griffiths–Wade** algorithm (TODS 1976) and Fagin's correction (TODS 1978) define **timestamp-based recursive revocation**: an authorization survives a revoke iff it still has a supporting chain in which each granting authorization is *older* than the grant it supports. Removing an edge triggers a reachability recomputation; the cascade set is exactly the nodes that lose all valid supporting paths.

Formally the maintained property is **dynamic reachability from the authority source** in a digraph under edge insertions (grants) and deletions (revokes). Worst-case a single revoke can remove $\Theta(|V|)$ nodes (a chain), and naively recomputing reachability costs $O(|V|+|E|)$ per operation. The timestamp condition makes validity a function of edge labels, turning it into a *constrained* reachability problem. Correctness under concurrency is framed as **serializability** of grant/revoke operations, with the grant graph as shared state.

## 3. State of the Art (SOTA)

**Theory-SOTA.** Griffiths–Wade (1976) and Fagin (1978) fix the semantics; Bertino–Samarati–Jajodia studied **non-cascading revocation** and richer revocation taxonomies (TKDE 1997) — distinguishing *deletion vs. negation*, *cascading vs. non-cascading*, *local vs. global* (the "dominance/grant-dependency" axes). Hagström–Jajodia–Parisi-Presicce–Wijesekera (POLICY 2001) give a comprehensive **revocation framework** with eight revocation schemes on three axes (resilience, propagation, dominance).

**Systems-SOTA.** PostgreSQL, Oracle, SQL Server implement `REVOKE ... CASCADE`/`RESTRICT` per the SQL standard's recursive-revocation semantics, storing grant dependencies in catalog tables (`pg_depend`/`pg_shdepend`). Dynamic-graph-reachability theory (decremental/incremental SSR) supplies the algorithmic backbone but is rarely specialized to grant graphs in production.

## 4. Upper Bound

A single revoke is computable in $O(|V| + |E|)$ by recomputing source-reachability (BFS/DFS) over the timestamp-filtered graph — linear in the affected component. **Decremental single-source reachability** data structures give better *amortized* totals: Italiano-style and more recent decremental SSR achieve roughly $O(|E|)$ *total* over a sequence of deletions on DAGs (amortized near-constant per edge for the reachable-set maintenance), and Bender–Fineman–Gilbert–Tarjan-style structures maintain topological/reachability info under updates. For grant graphs (typically sparse, near-DAG except for mutual grants), per-operation cost is effectively near-linear in the cascade size $|\Delta|$ plus the touched frontier.

## 5. Lower Bound

Maintaining reachability under both insertions and deletions (fully dynamic) faces strong fine-grained barriers: under the **OMv (Online Boolean Matrix-Vector) conjecture**, fully dynamic single-source reachability (and $s$–$t$ reachability) requires **$\Omega(n^{1-o(1)})$ amortized time per update/query** (Henzinger–Krinninger–Nanongkai–Saranurak, STOC 2015) — so no polylog fully-dynamic algorithm exists for the general grant-graph maintenance unless OMv fails. Thus the worst-case cascade truly can cost linear work, and *incremental maintenance avoiding it is conditionally impossible*. Concurrency adds a separate barrier: serializable grant/revoke under contention is subject to standard concurrency-control lower bounds (conflicts on the shared grant graph).

## 6. The Gap

"Partially solved": **semantics are settled** (Griffiths–Wade/Fagin/Hagström et al.) and single-operation cost is linear-time and adequate at modest scale. The open gap is the **scale + concurrency** regime: (i) OMv conditionally forbids sub-linear fully-dynamic maintenance, so very large, churning grant graphs (cloud IAM, multi-tenant SaaS) lack provably cheap incremental revocation; (ii) the *concurrency semantics* of interleaved cascading revokes are under-specified — most engines serialize coarsely (catalog locks), and a principled, high-throughput concurrent revocation protocol with a clean serializable definition is missing; (iii) timestamp-recursive semantics interact subtly with negative authorizations and delegation.

## 7. Current Research (as of June 2026)

Active directions: **graph-based authorization at scale** (Google **Zanzibar**, SpiceDB, OpenFGA) where "revocation" is relation-tuple deletion with consistency tokens (Zookies) — re-raising cascade/consistency under massive concurrency *(frontier — verify)*; applying modern **decremental/dynamic reachability** results to authorization catalogs; and formal concurrency models for grant/revoke (serializable authorization transactions) *(frontier — verify)*. Groups/people: the Zanzibar/Authzed and OpenFGA communities; dynamic-graph-algorithms researchers (Thorup, Saranurak, Nanongkai); database-security lineage of Bertino, Samarati, Jajodia.

## 8. Future Work

- Provably efficient incremental cascade maintenance for sparse grant graphs, or matching OMv-conditional lower bounds tightly.
- A clean serializable (or well-defined snapshot) semantics for concurrent cascading revocation, with a protocol achieving high throughput.
- Unifying timestamp-recursive revocation with negative authorization and delegation algebras.
- Revocation consistency guarantees for globally-distributed authorization systems (CAP-aware).
- Audit-friendly explanations: efficiently answering "why was privilege $p$ revoked for $s$?"

## 9. Key References

- **[Foundational]** Griffiths, P.P., Wade, B.W. *An Authorization Mechanism for a Relational Database System.* ACM TODS, 1976. — [DOI](https://doi.org/10.1145/320473.320482)
- **[Foundational]** Fagin, R. *On an Authorization Mechanism.* ACM TODS, 1978. — [DOI](https://doi.org/10.1145/320263.320288)
- **[Foundational]** Bertino, E., Samarati, P., Jajodia, S. *An Extended Authorization Model for Relational Databases.* IEEE TKDE, 1997. — [DOI](https://doi.org/10.1109/69.567051)
- **[SOTA]** Hagström, Å., Jajodia, S., Parisi-Presicce, F., Wijesekera, D. *Revocations — A Classification.* IEEE CSFW/POLICY, 2001. — [DOI](https://doi.org/10.1109/CSFW.2001.930133)
- **[SOTA]** Henzinger, M., Krinninger, S., Nanongkai, D., Saranurak, T. *Unifying and Strengthening Hardness for Dynamic Problems via the Online Matrix-Vector Multiplication Conjecture.* STOC, 2015. — [DOI](https://doi.org/10.1145/2746539.2746609) · [arXiv](https://arxiv.org/abs/1511.06773)
- **[SOTA]** Pang, R., et al. *Zanzibar: Google's Consistent, Global Authorization System.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/pang)

## 10. Worked Example

Owner $O$ holds `SELECT` on table `T`. Grants (each WITH GRANT OPTION), with timestamps:

| edge | grant | time |
|------|-------|------|
| $O\to A$ | SELECT | $t_1=10$ |
| $A\to B$ | SELECT | $t_2=20$ |
| $A\to C$ | SELECT | $t_3=30$ |
| $B\to C$ | SELECT | $t_4=40$ |
| $C\to D$ | SELECT | $t_5=50$ |

Now $O$ issues `REVOKE SELECT ON T FROM A CASCADE`, deleting edge $O\to A$. Under Griffiths–Wade timestamp-recursive semantics, an authorization survives iff it still has a supporting chain from the source $O$ in which each grant is *older* than the one it supports.

- $A$: lost its only support ($O\to A$) → **revoked**.
- $B$: only support was $A\to B$ (granted by $A$, now invalid) → **revoked**.
- $C$: had two supports — $A\to C$ ($t_3=30$, gone) and $B\to C$ ($t_4=40$, but $B$ is gone) → no valid chain → **revoked**.
- $D$: supported by $C\to D$ ($t_5$), and $C$ is gone → **revoked**.

The entire chain $\{A,B,C,D\}$ cascades — a single revoke removes $\Theta(|V|)$ nodes, exactly the linear worst case. Had $O$ separately granted $C$ at $t=5$, that older independent edge would have *saved* $C$ and $D$, illustrating why validity is a constrained-reachability (not plain reachability) property.

---
*Part of the [DBMS Research catalog](../../README.md).*
