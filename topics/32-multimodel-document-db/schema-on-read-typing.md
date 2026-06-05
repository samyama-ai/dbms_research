# Type systems for schema-on-read access

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/schema-on-read-typing` · **Status:** open

## 1. Problem Statement
Design a *sound gradual type discipline* for queries over schema-on-read document stores: data is stored without a write-time schema, yet queries make structural assumptions (a field exists, has a given type, an array is non-empty). The system should statically catch type errors — missing fields, type confusion, unsafe coercions — *without* forcing the user to declare or enforce a write-time schema, and degrade gracefully where structure is genuinely unknown.

- **Type-checking (decision) variant:** given a query and an *inferred or partial* schema, is the query type-safe (no run-time type error on conforming data)?
- **Inference variant:** infer the most general schema under which a query is safe (a *principal type*), and the result type of the query.
- **Soundness variant:** guarantee that well-typed queries do not "go wrong" at run time — the classic *type soundness* property — under a precise dynamic semantics that allows `null`/missing.

The crux is *gradual* typing: parts of the data are statically known (from samples or annotations), parts are `dynamic`, and the discipline must mediate the boundary with run-time casts that are sound but not over-conservative.

## 2. Mathematical Foundations
The setting is **gradual typing** (Siek–Taha) over a type language for semistructured values: record types with *optional* and *open* fields, union types (for heterogeneous fields), array/collection types, and a top type `dynamic`/`?`. Key apparatus:
- **Subtyping** with width/depth/optionality and unions; the *consistency* relation $\sim$ of gradual typing (reflexive, symmetric, not transitive) replaces equality at the dynamic boundary.
- **Type soundness** via progress + preservation, or the modern *gradual guarantee* (Siek–Vitousek–Cimini–Boyland): adding type information never changes a passing program's behavior except to fail earlier.
- **Schema inference** as type *reconstruction* — related to **regular tree types** / tree automata for JSON Schema (a JSON Schema is essentially a tree-automaton predicate), and to *semantic subtyping* (Castagna, Frisch) for $\mathrm{XDuce}$/$\mathrm{CDuce}$ where types are sets of values and subtyping is set inclusion (decided via emptiness of tree automata).
- **Null/3-valued logic** semantics for SQL/JSON `NULL`-vs-missing, requiring a careful dynamic semantics.

## 3. State of the Art (SOTA)
- **Foundational typed semistructured languages:** XDuce and CDuce gave *regular-tree* type systems with semantic subtyping for XML; JSON analogues exist (e.g., type systems for JSONPath/JSONiq, and *Elm/TypeScript*-style structural typing of JSON in app code).
- **Schema inference systems:** automatic JSON Schema / structural-type extraction (e.g., Baazizi–Colazzo–Ghelli–Sartiani, *Counting Types for Massive JSON Datasets*, 2017, and follow-ups producing union/optional-aware schemas) is the systems-SOTA for the *inference* side.
- **Gradual typing theory:** Siek–Taha and the gradual-guarantee line are mature for $\lambda$-calculi but *not* specialized to query languages with collections, `UNWIND`, and 3-valued `NULL`. No published, fully-sound gradual type system for a real document query language (SQL/JSON, MongoDB pipeline) exists.

## 4. Upper Bound
For the *typed-tree* fragment, semantic subtyping (XDuce/CDuce) gives **decidable** type-checking and subtyping via tree-automata emptiness (EXPTIME in the worst case, practical via on-the-fly algorithms). Schema inference over JSON with union/optional types runs in near-linear passes producing a sound *over-approximating* schema (Baazizi et al.). Gradual-typing soundness (the gradual guarantee) is established for core calculi, giving a template upper bound for *correctness* (not complexity) — but it has not been carried through to a query language with the full operator set.

## 5. Lower Bound
Subtyping/type-checking for regular-tree types is at least **EXPTIME-hard** (inherited from tree-automaton inclusion/CDuce semantic subtyping). With arithmetic predicates or value-dependent types (e.g., "field present iff discriminator = X"), exact type-checking becomes **undecidable** (Diophantine/Datalog-style encodings). Sound static typing therefore *cannot* be both exact and complete over expressive document predicates — any decidable system must over-approximate, and the *gradual guarantee* imposes additional structural constraints that further limit precision. These are the fundamental barriers; a precise lower bound for a *gradual* document type discipline is itself open.

## 6. The Gap
We have (i) sound regular-tree typing without gradualness (CDuce), (ii) sound gradual typing without collections/queries (Siek–Taha line), and (iii) sound schema *inference* without a query-level soundness theorem. **No system combines all three**: a gradual discipline, over real collection/query operators, with a proven soundness/gradual-guarantee theorem and tractable checking. Closing the gap means defining the dynamic semantics (including `null`/missing/heterogeneity), proving the gradual guarantee, and bounding checking complexity — genuinely open.

## 7. Current Research (as of June 2026)
Active strands: typed JSON Schema validation and inference (Pezoa/Reutter/Suciu/Vrgoč lineage on JSON Schema semantics and complexity); semantic-subtyping extensions to JSON (Castagna et al.); *(frontier — verify)* gradual/structural typing for dataframe and document query APIs (pandas/Spark/MongoDB) and LLM-assisted schema inference are being explored in 2025–2026 but lack soundness proofs. Work on *static analysis* of MongoDB/SQL-JSON queries to flag missing-field errors is emerging in industry tooling.

## 8. Future Work
A sound gradual type system for a full document query language with the gradual guarantee; precise treatment of 3-valued `NULL`/missing; principal-type inference from data samples with statistical confidence; complexity-tractable checking via automata + abstraction; integration with schema-evolution so types track multiple coexisting versions.

## 9. Key References
- **[Foundational]** Siek, Taha. *Gradual Typing for Functional Languages.* Scheme and Functional Programming Workshop, 2006. — [PDF](http://scheme2006.cs.uchicago.edu/13-siek.pdf)
- **[Foundational]** Hosoya, Pierce. *XDuce: A Statically Typed XML Processing Language.* ACM TOIT, 2003. — [DOI](https://doi.org/10.1145/767193.767195)
- **[Foundational]** Frisch, Castagna, Benzaken. *Semantic Subtyping (CDuce).* JACM, 2008. — [DOI](https://doi.org/10.1145/1391289.1391293)
- **[SOTA]** Baazizi, Colazzo, Ghelli, Sartiani. *Counting Types for Massive JSON Datasets.* DBPL, 2017. — [DOI](https://doi.org/10.1145/3122831.3122837)
- **[SOTA]** Pezoa, Reutter, Suarez, Ugarte, Vrgoč. *Foundations of JSON Schema.* WWW, 2016. — [DOI](https://doi.org/10.1145/2872427.2883029) · [DBLP](https://dblp.org/rec/conf/www/PezoaRSUV16.html)
- **[Survey]** Siek, Vitousek, Cimini, Boyland. *Refined Criteria for Gradual Typing (the Gradual Guarantee).* SNAPL, 2015. — [DOI](https://doi.org/10.4230/LIPIcs.SNAPL.2015.274)

## 10. Worked Example

Consider a collection sampled from two documents:

```
{ "user": "ann", "age": 30 }
{ "user": "bob", "age": "31" }   // age stored as string!
```

Inference produces the structural type $\{\,\texttt{user}:\texttt{String},\ \texttt{age}:(\texttt{Int}\mid\texttt{String})\,\}$ — `age` is a *union* because the sample is heterogeneous. Now type-check the query `SELECT age + 1`.

- The `+` operator demands `Int`. Against the inferred type, the operand has type $\texttt{Int}\mid\texttt{String}$. Subtyping requires $(\texttt{Int}\mid\texttt{String})\le\texttt{Int}$, which fails (the `String` arm is not covered) — so a purely static check **rejects** the query, correctly flagging `"31" + 1`.

Under *gradual* typing, suppose `age` were instead annotated `dynamic` (`?`). Consistency gives $? \sim \texttt{Int}$, so the check **passes statically** but inserts a run-time cast $\langle\texttt{Int}\rangle$ at the `+` site. On `ann` the cast succeeds; on `bob` it raises a cast error — failing *earlier and with blame*, exactly as the gradual guarantee promises, rather than silently coercing. This shows the union (sound rejection) vs. dynamic (deferred, blamed check) trade-off at the boundary.

---
*Part of the [DBMS Research catalog](../../README.md).*
