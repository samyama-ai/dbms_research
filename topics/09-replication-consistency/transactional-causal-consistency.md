# Transactional causal consistency at scale

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/transactional-causal-consistency` · **Status:** partially-solved

## 1. Problem Statement
**Transactional Causal Consistency (TCC)**, often called **causal+ with transactions**, is the strongest consistency model achievable while remaining *available* and *convergent* under network partitions (it sits at the "HAT ceiling"). It combines: (a) **causal consistency** — if write $a$ causally precedes write $b$, every replica that sees $b$ has already seen $a$; (b) **convergence** (the "+": concurrent writes are merged deterministically); and (c) **transactions** — a multi-key read sees a *causally consistent snapshot* and a multi-key write is applied *atomically* (all-or-nothing, read-atomic).

The problem: support **multi-key read–write transactions** with TCC across geo-distributed, sharded replicas while keeping (1) **throughput** high (no global serialization), (2) **metadata** small (dependency-tracking overhead must not blow up with the number of partitions/clients), and (3) **visibility latency** low (snapshots should not lag far behind). The central tension is metadata vs. false dependencies vs. snapshot freshness.

Variants: read-only TCC transactions (easier), general read-write TCC transactions (must order concurrent conflicting writes via a merge/arbitration rule), and the *partial-replication* case where no replica holds all shards.

## 2. Mathematical Foundations
Executions are histories with session order $\rightarrow_{so}$ and a write-into / visibility relation; the **causal order** $\rightarrow_{hb}$ is the transitive closure of session order and reads-from. Causal consistency requires $\mathit{vis}$ to be a *transitive, acyclic* superset of $\rightarrow_{hb}$. TCC additionally requires **atomic visibility**: for a transaction $T$, $\mathit{vis}$ either includes all of $T$'s writes or none (Cerone–Bernardi–Gotsman's *read-atomic* axiom, CONCUR 2015). A **causal snapshot** is a downward-closed set in $\rightarrow_{hb}$.

Implementation rests on logical-clock machinery: **version vectors** $V \in \mathbb{N}^k$ (one entry per partition/datacenter) with the dominance order $V \le V'$, **Hybrid Logical Clocks** (Kulkarni et al., 2014) to bound vector size with physical time, and **stable snapshots** computed from a global lower bound $\bigwedge_p \text{clock}(p)$. The metadata-size question is fundamentally: how compactly can a downward-closed causal frontier be encoded? Dependency-vector size lower-bounds (Charron-Bost, 1991: vector clocks of dimension $n$ are *necessary* to characterize causality among $n$ processes) govern the floor.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Cerone, Bernardi, Gotsman, *A Framework for Transactional Consistency Models with Atomic Visibility* (CONCUR 2015) gives the axiomatic placement of TCC; Bailis et al.'s **RAMP** transactions (SIGMOD 2014) achieve read-atomic visibility with bounded metadata and one round of coordination.
- **Systems-SOTA:** **Eiger** (Lloyd et al., NSDI 2013) — causal multi-key reads/writes; **Cure** (Akkoorath et al., ICDCS 2016) and its production form **AntidoteDB** — TCC with CRDTs using one vector-clock entry per datacenter; **Wren** (Spirovska, Didona, Zwaenepoel, DSN 2018) cuts metadata to two scalars via dependency-time + completion-time clocks; **Occult** (Mehdi et al., NSDI 2017) — observable causal consistency with compressed timestamps tolerating stale reads; **PaRiS / partial-replication TCC** (Spirovska et al., 2019).

## 4. Upper Bound
TCC read-only transactions are achievable in **one round** of non-blocking reads with a snapshot vector of size **$O(D)$**, $D$ = number of datacenters (Cure/AntidoteDB), independent of the number of keys or clients. Wren reduces per-message dependency metadata to **$O(1)$ scalars** (two hybrid timestamps) at the cost of slightly staler snapshots. Read-write TCC commits with one coordination round among the touched partitions (2-phase, no global order). Throughput scales horizontally because no inter-shard total order is required.

## 5. Lower Bound
- **Coordination floor:** TCC is *the strongest* model still highly available; anything stronger (e.g. transactional *snapshot isolation* or serializability) provably requires synchronous coordination and sacrifices availability under partition (CAP; Bailis et al. HAT, VLDB 2014). So TCC cannot be strengthened "for free."
- **Metadata floor:** characterizing causality among $n$ origins requires vector clocks of dimension $\Omega(n)$ (Charron-Bost, 1991) — scalar/HLC compressions necessarily introduce *false dependencies* (extra waiting/staleness). There is no encoding that is simultaneously $o(n)$-sized **and** false-dependency-free.

## 6. The Gap
The *model placement* is closed. What remains open is the **metadata–staleness–throughput Pareto frontier**: Cure pays $O(D)$ vectors, Wren/Occult pay $O(1)$ but accept extra staleness or stale-read anomalies, and no result proves a *tight* lower bound on the staleness forced by a given metadata budget. Partial replication and read-write (not read-only) TCC at high contention remain the practically hard, under-characterized regimes.

## 7. Current Research (as of June 2026)
- Constant-metadata TCC with provable staleness bounds (descendants of Wren/Occult) and HLC refinements.
- TCC under **partial replication** and edge/fog topologies (PaRiS line) *(frontier — verify)*.
- Integrating TCC with strong transactions in **mixed-consistency** systems (per-operation consistency choice; RedBlue/Olisipo lineage).
- Formal verification of TCC implementations (Gotsman, Kaki, Sivaramakrishnan groups) *(frontier — verify)*.

## 8. Future Work
- Tight metadata↔staleness lower bounds for TCC snapshots.
- Efficient read-write TCC under high cross-shard contention.
- Composable mixed-consistency transactions with a single proof framework.

## 9. Key References
- **[Foundational]** Lloyd, Freedman, Kaminsky, Andersen. *Stronger Semantics for Low-Latency Geo-Replicated Storage* (Eiger). NSDI, 2013.
- **[Foundational]** Cerone, Bernardi, Gotsman. *A Framework for Transactional Consistency Models with Atomic Visibility.* CONCUR, 2015.
- **[SOTA]** Akkoorath, Tomsic, Bravo, Li, Crain, Bieniusa, Preguiça, Shapiro. *Cure: Strong Semantics Meets High Availability and Low Latency.* ICDCS, 2016.
- **[SOTA]** Spirovska, Didona, Zwaenepoel. *Wren: Nonblocking Reads in a Partitioned Transactional Causally Consistent Data Store.* DSN, 2018.
- **[SOTA]** Mehdi, Littley, Crooks, Alvisi, Bronson, Lloyd. *I Can't Believe It's Not Causal! Scalable Causal Consistency with No Slowdown Cascades* (Occult). NSDI, 2017.
- **[Foundational]** Bailis, Davidson, Fekete, Ghodsi, Hellerstein, Stoica. *Highly Available Transactions.* VLDB, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
