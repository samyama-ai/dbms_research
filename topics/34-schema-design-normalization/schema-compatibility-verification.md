# Backward and Forward Schema Compatibility Verification

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/schema-compatibility-verification` · **Status:** open

## 1. Problem Statement
Given a schema change $\mathcal{S} \to \mathcal{S}'$ (relational DDL, or an evolving Avro/Protobuf/JSON-Schema), **statically verify compatibility** so that the change does not break existing or future consumers/producers and stored data.

- **Backward compatibility (decision):** Can code/readers written for $\mathcal{S}'$ still correctly process data/messages produced under $\mathcal{S}$? (New reader, old data.)
- **Forward compatibility (decision):** Can code/readers written for $\mathcal{S}$ still process data produced under $\mathcal{S}'$? (Old reader, new data.)
- **Full / transitive compatibility:** Both, and across an entire version history.
- **Application-code variant:** Beyond data — does existing SQL/ORM/application code remain well-typed and semantically equivalent (same results) against $\mathcal{S}'$? This requires reasoning about *queries*, not just *data shapes*.

The hard part is that "compatibility" spans three artifacts at once: **persisted data**, **wire/serialization contracts**, and **application query code** — and the strongest variant asks for *semantic* (result-preserving) equivalence, not just type-safety.

## 2. Mathematical Foundations
Schema-level compatibility is a **subtyping/refinement** relation: $\mathcal{S}' $ is backward-compatible with $\mathcal{S}$ iff the set of valid documents of $\mathcal{S}$ is contained in (or coercible into) the readable set of $\mathcal{S}'$ — a **schema containment** $\mathsf{Lang}(\mathcal{S}) \subseteq \mathsf{Lang}(\mathcal{S}')$. For tree/JSON schemas this is **language inclusion of unranked tree automata / regular tree grammars**, and for XML-schema (DTD/XSD) inclusion is **EXPTIME-complete**. JSON Schema with references/recursion can express constraints whose **satisfiability is undecidable** in the full draft, decidable for restricted profiles.

Application-code compatibility is **query equivalence under a schema mapping**: letting $V$ be the migration mapping, code is preserved iff $q \equiv \rho_V(q)$ on all valid instances — **query equivalence**, which is **undecidable for relational algebra/SQL** in general and **NP-complete for conjunctive queries** (Chandra–Merlin homomorphism theorem). Type-level (not semantic) checking reduces to a **type-inference / well-typedness** judgment $\Gamma \vdash q : \tau$ under $\mathcal{S}'$. Forward compatibility additionally quantifies over *unknown future* producers, naturally an **abstract-interpretation / refinement-type** over-approximation.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **Confluent Schema Registry** enforces Avro/Protobuf/JSON-Schema BACKWARD/FORWARD/FULL (+transitive) compatibility via concrete structural rules (Avro resolution rules; Protobuf field-number invariants) — the dominant deployed checker, but rule-based and data-only. **Buf** does breaking-change detection for Protobuf. Database **migration linters** (Squawk, **sqlc** type-checking, Liquibase/Flyway validation, GitHub's online-migration safety checks) flag unsafe DDL. **SQL equivalence provers** — **Cosette** (Chu et al., 2017) and **UDP/SQLSolver** — verify query equivalence and could certify code preservation, but are not yet integrated into schema-change gates.

**Theory-SOTA.** Tree-automata inclusion algorithms (Hosoya–Pierce, *XDuce/regular expression types*) underpin schema subtyping; conjunctive-query containment (Chandra–Merlin) underpins code equivalence. No deployed tool certifies *semantic* application compatibility — hence **open**.

## 4. Upper Bound
Structural backward/forward checks for Avro-style schemas are **linear/polynomial** in schema size (field-wise rules). Tree-automata language **inclusion** for regular tree grammars (DTD class) is decidable in **EXPTIME** (PTIME for deterministic/local fragments). **Conjunctive-query** equivalence/containment is **NP-complete** and decidable via homomorphism search; bounded SQL fragments are handled by SMT-backed provers (Cosette) in practice on real queries. So restricted, well-behaved fragments admit complete decision procedures within these bounds.

## 5. Lower Bound
Full **SQL/relational-algebra query equivalence is undecidable** (reduction from FOL validity / via difference operators), so *semantic* application-code compatibility cannot be decided in general. **XSD/DTD inclusion is EXPTIME-complete**, and full **JSON Schema satisfiability is undecidable** (Pezoa et al. / Bourhis et al. characterize the decidable boundary). Even conjunctive-query containment is **NP-hard**. Thus the strongest variant is provably out of reach in full generality; only fragments are tractable.

## 6. The Gap
The gap is between today's **data-shape-only, rule-based** checkers (sound for serialization, silent about query semantics) and the **semantic** guarantee users actually want ("my application still returns the same answers"). The latter is undecidable in full generality but *decidable on real fragments* (conjunctive/UCQ, bounded SQL) — so the open problem is **engineering and theoretical**: define the largest practically-relevant fragment, give a complete + scalable checker, and integrate it as a migration gate. It is **open**: no system today verifies application-semantic forward/backward compatibility end-to-end.

## 7. Current Research (as of June 2026)
- Integrating SQL **equivalence provers** (Cosette/SQLSolver lineage) into CI schema-change gates to certify code preservation *(frontier — verify)*.
- **Refinement-typed** JSON/Protobuf evolution with decidable compatibility profiles; formal semantics for JSON Schema drafts.
- **LLM + verifier** loops that propose a migration and a machine-checkable compatibility proof obligation *(frontier — verify)*.
- Compatibility analysis for **data contracts** and lakehouse table formats (Iceberg/Delta schema-evolution rules) with column-level lineage.

## 8. Future Work
- A characterized maximal decidable fragment for *semantic* backward/forward compatibility, with a complete checker.
- Compositional compatibility across long version histories (transitive guarantees without re-checking all pairs).
- Joint reasoning over data + wire format + application queries in one verifier.
- Counterexample-producing checkers (the breaking query/datum) for developer ergonomics.

## 9. Key References
- **[Foundational]** Chandra, A., Merlin, P. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** Hosoya, H., Pierce, B. *XDuce: A Statically Typed XML Processing Language (regular expression types / tree-automata subtyping).* ACM TOIT, 2003. — [DOI](https://doi.org/10.1145/767193.767195)
- **[SOTA]** Chu, S., Weitz, K., Cheung, A., Suciu, D. *Cosette: An Automated Prover for SQL.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/ChuWWC17.html)
- **[SOTA]** Pezoa, F., Reutter, J., Suarez, F., Ugarte, M., Vrgoč, D. *Foundations of JSON Schema.* WWW, 2016. — [DOI](https://doi.org/10.1145/2872427.2883029)
- **[Survey]** Confluent. *Schema Registry: Schema Evolution and Compatibility* (documentation), 2017–. — [docs](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- **[Foundational]** Martens, W., Neven, F., Schwentick, T. *Complexity of Decision Problems for XML Schemas and Inclusion.* ACM TODS, 2006. — [DBLP search](https://dblp.org/search?q=Martens+Neven+Schwentick+XML+schema+complexity) *(unverified)*

## 10. Worked Example

Take an Avro record evolving $\mathcal{S} \to \mathcal{S}'$:

```
S:   record User { string name; int age; }
S':  record User { string name; int age; string email = "n/a"; }
```

**Backward compatibility** (new reader $\mathcal{S}'$, old data written under $\mathcal{S}$): old data has no `email` field. The new reader supplies the default `"n/a"`, so it reads old data correctly — **backward-compatible**. Avro's rule: adding a field with a default is backward-safe.

**Forward compatibility** (old reader $\mathcal{S}$, new data written under $\mathcal{S}'$): new data carries an `email` the old reader does not know; the resolution rule drops unknown fields — so the old reader still parses it — **forward-compatible**. Adding a field with a default is therefore **FULL**-compatible.

Contrast a *removal*: dropping `age` would break a backward reader expecting `age` unless `age` also had a default. This is a pure data-shape check (linear in fields). It says nothing about query semantics: a view `SELECT name FROM User WHERE age > 18` is unaffected by adding `email`, but the *semantic* variant — does some query $q$ return the same answers under $\mathcal{S}'$? — reduces to conjunctive-query equivalence (NP-complete via Chandra–Merlin), and to undecidable full SQL equivalence in general, which the rule-based checker cannot certify.

---
*Part of the [DBMS Research catalog](../../README.md).*
