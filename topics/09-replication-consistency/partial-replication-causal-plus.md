# Genuine partial replication with causal+ consistency

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/partial-replication-causal-plus` · **Status:** open

## 1. Problem Statement

Under **full replication**, every replica stores every key, so causal consistency can be enforced by tracking dependencies over all keys/replicas. Under **partial replication**, each replica $r$ stores only a subset of keys $K_r \subsetneq K$ (chosen for capacity, locality, or regulatory reasons). The goal is **genuine** partial replication: a replica should do work — store data, exchange metadata, and stall waiting for dependencies — **only for the keys it actually hosts**, never for keys it does not. The research problem is to provide **causal+ consistency** (causal consistency plus convergent conflict resolution / progress) in this setting.

Formally: design a replication protocol that guarantees, for every read at replica $r$ of key $k \in K_r$, that all causal predecessors *of $k$'s returned version that are themselves keys in $K_r$* are visible — without $r$ ever (a) storing versions of keys $\notin K_r$, (b) receiving/processing metadata describing updates to keys $\notin K_r$, or (c) blocking on the propagation of keys it does not host.

- **Decision variant:** given a placement $\{K_r\}$ and a target metadata budget, does a *genuine* causal+ protocol exist?
- **Optimization variant:** minimize metadata size / visibility latency subject to genuineness.
- **Impossibility variant:** prove that genuineness is incompatible with $o(\cdot)$ metadata or with bounded visibility latency.

Status is **open**: most "partial replication" systems either fall back to full metadata, route through full-replica nodes, or sacrifice genuineness; a protocol that is provably genuine *and* efficient is not known.

## 2. Mathematical Foundations

Executions are a partial order $(\mathcal{O}, \to)$ under Lamport happens-before. **Causal+** (Lloyd et al., COPS) = causal consistency + **convergent conflict handling** (concurrent writes to the same key resolve identically everywhere, e.g., last-writer-wins or a CRDT merge). The enforcement primitive is **deliverability**: an update $u$ to key $k$ is deliverable at $r$ once all of $u$'s causal predecessors *that $r$ tracks* are applied.

Full causality among $N$ peers needs vector clocks of dimension $\geq N$ (Charron-Bost, 1991): no smaller clock characterizes $\to$ exactly. The partial-replication twist: $r$ should track dependencies only over the **transitive causal cut restricted to $K_r$**. This is a **projected partial order** — the induced suborder on operations touching $K_r$. The difficulty: a chain $w(a) \to w(b) \to w(c)$ with $a,c \in K_r$ but $b \notin K_r$ creates a **hidden transitive dependency** $w(a) \to w(c)$ that $r$ must respect *without* observing $w(b)$. Capturing such "shortcut" dependencies cheaply links to **transitive-closure / reachability labeling** of DAGs (worst case $\Theta(n)$-bit labels for general DAGs; polylog for restricted classes) and to **communication complexity** of distributed reachability.

A "genuine partial replication" criterion (in the spirit of genuine atomic multicast, Guerraoui–Schiper) requires that only replicas storing keys in an update's read/write set take steps for that update — formalizable as a non-interference condition on the protocol's transition system.

## 3. State of the Art (SOTA)

- **Systems SOTA:** COPS / Eiger (Lloyd et al., SOSP'11 / NSDI'13) give causal+ but assume each datacenter is a *full* replica (partial replication only *across* DCs, full *within*). GentleRain (Du et al., SoCC'14) and Cure (Akkoorath et al., ICDCS'16) compress metadata (one scalar / one entry per DC) but are not genuine under intra-DC partial replication — a scalar clock forces tracking of unrelated keys (false dependencies). Saturn (Bravo et al., EuroSys'17) routes metadata through a serialization tree, decoupling label size from data, and is among the closest to scalable partial-replication causal+. **PaRiS** (Spirovska, Didona, Zwaenepoel, ICDCS'19) explicitly targets partial replication with a *Universal Stable Time* and dependency vectors. **Wren** and **Okapi** (same group) handle partial geo-replication with bounded metadata. EunomiaKV / Eiger-PORT and **Eiger-PS** address performance-optimal transactional causal consistency.
- **Theory SOTA:** the metadata vs. visibility-latency tradeoff is studied (Bravo, Bailis et al.) but no tight genuineness lower bound exists. Genuine *atomic multicast* (Guerraoui–Schiper; Coelho–Pedone) gives the analogous genuineness formalism in the consensus setting.

## 4. Upper Bound

Best-known *genuine-ish* protocols use **dependency vectors with one entry per datacenter** ($O(\#DC)$ metadata, PaRiS/Cure) plus a stabilization scalar, achieving causal+ under partial replication with visibility latency bounded by a stabilization round; PaRiS is genuine in that a client interacts only with replicas hosting its data items, paying $O(\#DC)$ rather than $O(K)$ or $O(N)$. Saturn achieves **$O(1)$-sized labels** by paying visibility latency proportional to the metadata-tree depth. For restricted dependency-DAG classes (bounded tree-width / bounded fan-in causal graphs), reachability-labeling results suggest sublinear exact labels are possible, but this has not been turned into a deployed genuine protocol. All upper bounds buy small metadata with either false dependencies or extra visibility latency.

## 5. Lower Bound

Unconditional: exact causality tracking across $N$ peers requires $\Omega(N)$-entry clocks (Charron-Bost). Reachability/adjacency labeling of general DAGs needs $\Omega(n)$-bit labels in the worst case, lower-bounding any scheme that encodes hidden transitive dependencies exactly. **CAP** (Gilbert–Lynch) does not forbid causal consistency under partition (causal+ *is* achievable while available — it is the strongest always-available model, per Mahajan–Alvisi–Dahlin's "Consistency, Availability, and Convergence" and Attiya et al.'s observable-causal-consistency optimality), so the barrier is **metadata/latency**, not availability. The precise open lower bound: whether *genuine* partial replication (zero work for un-hosted keys) is compatible with $o(N)$ — or even $o(\#DC)$ — metadata and bounded visibility latency. Communication-complexity arguments hint at a three-way tradeoff (metadata bits × false-dependency rate × visibility latency) but a matching bound is unproven.

## 6. The Gap

The gap is between practical genuine-ish protocols at $O(\#DC)$ metadata (PaRiS/Cure) or $O(1)$ labels with latency cost (Saturn), and the absence of any **tight lower bound** establishing that genuineness *forces* this cost. It is genuinely open whether a protocol can be simultaneously (i) genuine (no work for un-hosted keys), (ii) $o(\#DC)$ metadata, and (iii) bounded visibility latency without false dependencies. Closing it requires either a labeling-scheme / communication-complexity lower bound for genuine deliverability, or a protocol beating $O(\#DC)$ while remaining genuine and convergent.

## 7. Current Research (as of June 2026)

Active directions: dependency-tracking that exploits causal-graph structure (bounded fan-in, locality) to shrink metadata *(frontier — verify)*; probabilistic / Bloom-clock dependencies with quantified false-staleness for partial replication *(frontier — verify)*; transactional causal+ under partial replication optimized for read latency (Eiger-PORT/PaRiS lineage). The formal framing as a *genuineness lower bound* (borrowing from genuine atomic multicast) is being revisited *(frontier — verify)*. Groups: EPFL (Zwaenepoel, Didona, Spirovska), INESC-TEC / U. Minho (Baquero, Almeida, Bravo), Sorbonne/IMDEA (Shapiro, Gotsman), and UT Austin (Alvisi lineage on observable causal consistency).

## 8. Future Work

- Prove a tight metadata–latency–false-dependency tradeoff for *genuine* partial-replication causal+.
- Characterize dependency-graph classes (bounded tree-width / fan-in) admitting sublinear exact genuine labels.
- Genuine transactional causal+ (atomic multi-key reads) with optimal read latency under partial replication.
- Combine Bloom/interval clocks with provable convergence and quantified anomaly rates in the genuine setting.

## 9. Key References

- **[Foundational]** B. Charron-Bost. *Concerning the size of logical clocks in distributed systems.* Information Processing Letters, 1991.
- **[Foundational]** W. Lloyd, M. Freedman, M. Kaminsky, D. Andersen. *Don't settle for eventual: scalable causal consistency for wide-area storage with COPS.* SOSP, 2011.
- **[Foundational]** P. Mahajan, L. Alvisi, M. Dahlin. *Consistency, availability, and convergence.* Tech. report TR-11-22, UT Austin, 2011.
- **[SOTA]** D. Akkoorath, A. Tomsic, M. Bravo, Z. Li, T. Crain, A. Bieniusa, N. Preguiça, M. Shapiro. *Cure: strong semantics meets high availability and low latency.* ICDCS, 2016.
- **[SOTA]** K. Spirovska, D. Didona, W. Zwaenepoel. *Paris: causally consistent transactions with non-blocking reads and partial replication.* ICDCS, 2019.
- **[SOTA]** M. Bravo, L. Rodrigues, P. Van Roy. *Saturn: a distributed metadata service for causal consistency.* EuroSys, 2017.
- **[Foundational]** R. Guerraoui, A. Schiper. *Genuine atomic multicast in asynchronous distributed systems.* Theoretical Computer Science, 2001.

---
*Part of the [DBMS Research catalog](../../README.md).*
