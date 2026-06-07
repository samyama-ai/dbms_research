---
id: 23-database-security/polyinstantiation-consistency
title: "Polyinstantiation Consistency"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Polyinstantiation Consistency

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/polyinstantiation-consistency` · **Status:** open

## 1. Problem Statement

In a **multilevel secure (MLS)** relational database, tuples and even individual attribute values carry security classifications drawn from a lattice (e.g., *Unclassified ⊑ Confidential ⊑ Secret ⊑ Top-Secret*). The **no read-up / no write-down** (Bell–LaPadula) rules forbid information flowing from high to low. This creates a dilemma when a *low* subject inserts a tuple whose primary key already exists in a *high* tuple it cannot see:

- Rejecting the insert **signals** that a high tuple exists → a **covert channel**.
- Allowing it overwrites high data → integrity loss / write-down.

**Polyinstantiation** resolves this by permitting *multiple tuples with the same apparent primary key at different security levels* (or the same key + level with different values). The key is extended with the classification. But this breaks core relational guarantees:

> **Problem:** reconcile polyinstantiation with (a) **entity integrity** and key semantics, (b) **serializable concurrency** across levels, and (c) **referential / functional-dependency integrity**, while provably *closing* the covert channels (signaling, timing) that the mechanism was introduced to avoid.

Variants: (modeling) define a sound update semantics that does not create *spurious* polyinstantiation; (decision) given a schedule, is it serializable without a high→low channel; (consistency) do integrity constraints remain satisfiable across all level-projections of the database.

## 2. Mathematical Foundations

A multilevel relation has scheme $R(A_1,C_1,\dots,A_n,C_n,TC)$ where each data attribute $A_i$ has a classification $C_i$ and $TC$ is the tuple class. The **apparent key** $AK$ plus classifications forms the real key. The database is viewed through **level filters**: for clearance $\ell$, the *view* $R_\ell = \pi_{\le \ell}(R)$ contains only tuples/attributes dominated by $\ell$.

Soundness requires the filter to be a **homomorphism** consistent across levels: lower views must be projections of higher views (the *containment* / *poly-instantiation integrity* properties of Jajodia–Sandhu's SeaView/MLR model). Key properties (Jajodia–Sandhu 1991): entity integrity, *polyinstantiation integrity* ($AK, C_{AK}, C_i \to A_i$, i.e., apparent key + classifications functionally determines each value), and inter-instance integrity.

Concurrency: a schedule over multilevel data must be **secure-serializable** — equivalent to a serial schedule **and** producing no high→low timing dependency. This forbids a high transaction from delaying a low one via shared locks; standard 2PL violates security because lock waits leak. Secure scheduling typically requires **level-ordered** or **multiversion** protocols where low transactions never block on high data:
$$\text{low never waits on high} \;\Rightarrow\; \text{no $\Box$-channel via lock contention.}$$
This is information-flow noninterference applied to the *scheduling* channel, a hyperproperty over schedules.

## 3. State of the Art (SOTA)

- **Models:** **SeaView** (Denning, Lunt, et al., 1987–90) and the **Jajodia–Sandhu MLR model** (1990–91) are canonical; MLR fixed several semantic anomalies (spurious tuples, ambiguous updates) of earlier models. Smith–Winslett "belief-based" semantics gives polyinstantiation a clean interpretation: each level holds *beliefs*, and a low-level tuple at higher levels is read as "what low believes."
- **Concurrency:** secure multiversion timestamp and "single-level transaction" architectures (Trusted Oracle, the "kernelized" vs. "replicated" MLS architectures) where each level is a separate single-level DB and a trusted front-end composes views, structurally avoiding cross-level lock channels.
- **Systems:** historic Trusted Oracle, Sybase Secure SQL Server, Informix-OnLine/Secure; modern incarnations as **label-based row security** (Oracle Label Security, PostgreSQL + SELinux/sepgsql) — but most modern systems *drop* polyinstantiation, accepting either denial-based channels or simply not targeting MLS covert-channel-free operation.

## 4. Upper Bound

The **replicated/kernelized architecture** gives a clean upper bound: run one single-level untrusted DBMS per level, replicate lower data upward, and let a small trusted filter compose views. This achieves provable no-write-down and avoids cross-level lock channels by construction, at the cost of $O(L)$ storage blow-up ($L$ levels) and replication-update complexity. Secure concurrency control via multiversion scheduling adds bounded overhead while guaranteeing low transactions never wait on high. Belief-based update semantics (Smith–Winslett) yields a polynomial-time, anomaly-free update operator. So *correct-and-secure* designs exist; they are expensive and limited to small, static lattices.

## 5. Lower Bound

- **Covert-channel impossibility:** any scheduler in which low transactions can *observe* contention from high transactions has a timing channel of positive capacity; eliminating it provably forces "low ignores high," which can starve or abort high transactions — a fundamental **security/serializability/liveness trilemma** analogous to FLP-style tension. You cannot have classic serializability, full availability, and zero high→low channel simultaneously under shared data.
- **Integrity tension:** enforcing functional dependencies *across* levels reintroduces a channel (a low FD violation can reveal a high value), so MLS systems must weaken cross-level integrity — an inherent loss, not an implementation gap.
- General covert-channel-freedom checking is a **2-safety hyperproperty** (undecidable in the general program model), so no algorithm certifies an arbitrary MLS design as channel-free.

## 6. The Gap

The classical models (MLR, belief-based) *closed* the **single-relation semantic** anomalies. What remains genuinely **open**: a unified theory giving (a) serializable, (b) covert-channel-free, and (c) integrity-preserving operation **simultaneously** for realistic schemas with referential integrity and transactions spanning levels — without paying the full replicated-architecture cost. The trilemma in §5 means *some* property must be relaxed; which relaxations are acceptable, and tight bounds on the resulting residual channel bandwidth, are not settled. Polyinstantiation also remains awkward to compose with modern features (MVCC, snapshot isolation, JSON/temporal data).

## 7. Current Research (as of June 2026)

MLS/polyinstantiation is a comparatively dormant classical area, revived in niches: label-based security in cloud/government data lakes; formal re-examination of belief semantics with modern proof assistants; combining MLS labels with **information-flow type systems** for query languages. Connections to **differential privacy** (treating "denial vs. polyinstantiation" as a privacy-utility choice) and to confidential-computing multilevel separation are emerging *(frontier — verify)*. Sandhu's and Bertino's lineage continues on attribute/label-based generalizations; formal-methods groups study secure transaction scheduling as noninterference.

## 8. Future Work

- A modern MVCC/snapshot-isolation protocol proven secure-serializable with quantified residual channel bandwidth.
- Polyinstantiation semantics for semi-structured/temporal data.
- Mechanized proofs of MLR-style integrity properties and channel-freedom.
- Principled relaxations of the serializability/security/liveness trilemma with tight trade-off curves.
- Reconciling polyinstantiation with referential integrity and triggers.

## 9. Key References

- **[Foundational]** Jajodia, S., Sandhu, R. *Toward a Multilevel Secure Relational Data Model.* SIGMOD, 1991. — [DOI](https://doi.org/10.1145/115790.115796)
- **[Foundational]** Denning, D., Lunt, T., et al. *The SeaView Security Model.* IEEE Trans. Software Engineering, 1990. — [DOI](https://doi.org/10.1109/32.55088)
- **[Foundational]** Smith, K., Winslett, M. *Entity Modeling in the MLS Relational Model* (belief-based semantics). VLDB, 1992. — [DBLP](https://dblp.org/rec/conf/vldb/SmithW92.html)
- **[Foundational]** Bell, D., LaPadula, L. *Secure Computer System: Unified Exposition and Multics Interpretation.* MITRE, 1976. — [DBLP search](https://dblp.org/search?q=Secure+Computer+System+Unified+Exposition+Multics)
- **[Survey]** Atluri, V., Jajodia, S., Bertino, E. *Transaction Processing in Multilevel Secure Databases.* (multilevel concurrency control), 1990s. — [DBLP search](https://dblp.org/search?q=Transaction+Processing+Multilevel+Secure+Databases+Atluri+Jajodia)

## 10. Worked Example

Relation **Mission**$(Name, Objective, TC)$ with apparent key $Name$. Initially a *Secret* user inserts:

| Name | Objective | TC |
|------|-----------|----|
| Bravo | Sabotage bridge | S |

A *Unclassified* (U) user — who, by **no-read-up**, cannot see the S tuple — inserts `('Bravo', 'Deliver mail', U)`.

- **Reject** the insert → the U user infers a hidden 'Bravo' exists: a covert channel of $1$ bit.
- **Polyinstantiate** → store both, with the real key extended by classification $(Name, C_{TC})$:

| Name | Objective | TC |
|------|-----------|----|
| Bravo | Deliver mail | U |
| Bravo | Sabotage bridge | S |

Now the level-filtered views are consistent: $R_U = \pi_{\le U}$ shows only the U row (the cover story), while $R_S$ shows both. **Polyinstantiation integrity** holds because $(Name, C_{TC}) \to Objective$: the pair $(Bravo, U)$ determines "Deliver mail," $(Bravo, S)$ determines "Sabotage bridge." Entity integrity on $Name$ alone is sacrificed — exactly the relational guarantee §1 says polyinstantiation breaks.

---
*Part of the [DBMS Research catalog](../../README.md).*
