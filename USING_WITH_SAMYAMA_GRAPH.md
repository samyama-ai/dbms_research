# Use this catalog as a knowledge graph (Samyama-Graph)

This repository is a catalog of **1,053 open problems in database systems**, one Markdown
file per problem. But the problems don't stand alone — they cite shared papers, rest on
shared concepts, are worked on by the same researchers, and require overlapping future
work. That structure *is a graph*.

We publish that graph as a portable snapshot you can load into
**[Samyama-Graph](https://github.com/samyama-ai/samyama-graph)** (the open-source,
Apache-2.0 graph-vector database) and query with OpenCypher in a couple of minutes — no
account, no cloud, one binary.

```
1,053 Problems · 35 Topics · 2,954 Papers · 3,939 Researchers · 3,825 future directions
20,019 nodes · 39,393 edges · 12.8 MB snapshot  (iteration `2026-09`)
Researchers are resolved against DBLP: 1,966 carry a dblp_pid / profile-page link + affiliation.
```

> The snapshot is generated from the Markdown in this repo by an extraction pipeline.
> The catalog here is the source of truth; the graph is a derived, queryable view of it.

---

## 1. Get Samyama-Graph running (≈2 min)

```bash
git clone https://github.com/samyama-ai/samyama-graph && cd samyama-graph
cargo build --release
./target/release/samyama          # RESP on :6379, HTTP/REST on :8080
```

Leave it running. Everything below talks to the HTTP API on `:8080`.

> A prebuilt Docker image is on the way ([samyama-graph#6](https://git.samyama.ai/Samyama.ai/samyama-graph/issues/6)) so you'll be able to `docker run` instead of building from source.

## 2. Download the snapshot

```bash
curl -L -o dbms-research.sgsnap \
  https://github.com/samyama-ai/samyama-graph/releases/download/kg-snapshots-v10/dbms-research.sgsnap
```

(`.sgsnap` is Samyama-Graph's portable, gzip'd JSON-Lines snapshot format.)

## 3. Import it

```bash
curl -F file=@dbms-research.sgsnap http://localhost:8080/api/snapshot/import
```

You should see:

```json
{"status":"ok","nodes_imported":18881,"edges_imported":39142,
 "labels":["Algorithm","Bound","ComputationModel","Concept","FutureDirection",
           "Institution","Paper","Person","Problem","System","Topic","Venue"], ...}
```

## 4. Query it

All queries go to `POST /api/query` with a JSON body `{"query": "<cypher>"}`. A tiny helper:

```bash
q() { curl -s -H 'Content-Type: application/json' -d "{\"query\":\"$1\"}" \
        http://localhost:8080/api/query; echo; }
```

(Or use any Redis client on `:6379` with `GRAPH.QUERY`.)

---

## The graph at a glance

**Node labels** — `Problem`, `Topic`, `Paper`, `Person`, `Concept`, `Algorithm`,
`System`, `Bound`, `ComputationModel`, `FutureDirection`, `Venue`, `Institution`.

**Edges (direction matters):**

```
(Problem)-[:IN_TOPIC]->(Topic)
(Problem)-[:CITES]->(Paper)
(Paper)-[:AUTHORED_BY]->(Person)
(Paper)-[:APPEARED_AT]->(Venue)
(Problem)-[:RESTS_ON]->(Concept)
(Problem)-[:HAS_BOUND]->(Bound)-[:IN_MODEL]->(ComputationModel)
(Problem)-[:CLOSING_REQUIRES]->(FutureDirection)
(Problem)-[:STATE_OF_ART]->(Algorithm | System)
(Problem)-[:RELATED_TO]->(Problem)
(Person)-[:ACTIVE_ON]->(Problem)
(Person)-[:AFFILIATED_WITH]->(Institution)
(Concept)-[:GENERALIZES]->(Concept)
```

Key properties: `Problem{title, slug, statement, status}`, `Topic{name, slug}`,
`Paper{title, year, venue, url}`, `Person{name, dblp_pid, dblp_url, orcid, affiliation, aliases}`,
`FutureDirection{text}`.

---

## Example queries (all verified against this snapshot)

### Explore the landscape

How many problems, and which topics are the deepest?

```cypher
MATCH (p:Problem) RETURN count(p) AS problems          // → 1053

MATCH (p:Problem)-[:IN_TOPIC]->(t:Topic)
RETURN t.name AS topic, count(p) AS n ORDER BY n DESC LIMIT 5
```
| topic | n |
|-------|---|
| NoSQL & Key-Value Stores | 31 |
| Temporal Databases | 31 |
| Query Optimization | 31 |
| Query Processing & Execution | 30 |
| Recovery, Logging & Durability | 30 |

### Who works on what (researcher view)

Most prolific researchers in the catalog, and what one of them is active on:

```cypher
MATCH (pap:Paper)-[:AUTHORED_BY]->(per:Person)
RETURN per.name AS author, count(pap) AS papers ORDER BY papers DESC LIMIT 5
```
> Thomas Neumann (51), Samuel Madden (38), Alfons Kemper (36) …
>
> Bare surnames (`Wang`, `Suciu`) also appear near the top. They are surname-only
> mentions lifted from citation text, and they are deliberately **not** merged into a
> full-name node: a surname alone does not identify a person. Resolution under-merges
> rather than risk a false merge — before iteration `2026-09` it did merge them, which
> pinned 63 nodes onto arbitrary DBLP profiles, the systems `Aurora` and `Calvin`
> among them.

```cypher
MATCH (per:Person)-[:ACTIVE_ON]->(p:Problem)
WHERE per.name = "Thomas Neumann"
RETURN p.title LIMIT 10
```
> Instance-optimal join evaluation · Worst-Case-Optimal Distributed Joins ·
> Semijoin Reducers for Cyclic Queries · Unbiased Sampling Over Joins …

Co-authorship — who collaborates with whom:

```cypher
MATCH (a:Person)<-[:AUTHORED_BY]-(:Paper)-[:AUTHORED_BY]->(b:Person)
WHERE a.name = "Thomas Neumann" AND a.name <> b.name
RETURN b.name AS collaborator, count(*) AS papers ORDER BY papers DESC LIMIT 8
```

Jump straight to a researcher's **DBLP profile page** (researchers are resolved to DBLP
PIDs, so name variants collapse to one node — e.g. `A. Ailamaki`/`Ailamaki`/`Anastassia
Ailamaki` → one `Anastasia Ailamaki`):

```cypher
MATCH (per:Person)-[:ACTIVE_ON]->(p:Problem)
WHERE per.dblp_url IS NOT NULL
RETURN per.name, per.dblp_url, per.affiliation, count(p) AS problems
ORDER BY problems DESC LIMIT 10
```

### The people and papers behind a problem

```cypher
MATCH (p:Problem)-[:CITES]->(pap:Paper)
WHERE p.title = "Instance-optimal join evaluation"
RETURN pap.title, pap.year ORDER BY pap.year

MATCH (p:Problem)-[:CITES]->(:Paper)-[:AUTHORED_BY]->(per:Person)
WHERE p.title = "Instance-optimal join evaluation"
RETURN count(DISTINCT per.name) AS people
```

### Most-cited foundational papers

```cypher
MATCH (p:Problem)-[:CITES]->(pap:Paper)
RETURN pap.title AS paper, count(p) AS cited_by ORDER BY cited_by DESC LIMIT 5
```
> *Foundations of Databases* (64) · *Access Path Selection…* (43) ·
> *The I/O Complexity of Sorting…* (38) · *Spanner* (35)

### What it would take to close a problem (future work)

```cypher
MATCH (p:Problem)-[:IN_TOPIC]->(t:Topic),
      (p)-[:CLOSING_REQUIRES]->(fd:FutureDirection)
WHERE t.name CONTAINS "Query Optimization"
RETURN fd.text LIMIT 5

// Find a problem by title, fuzzily:
MATCH (p:Problem) WHERE p.title CONTAINS "Worst-Case-Optimal" RETURN p.title
```

---

## Semantic search (vector) — coming soon

Every `Problem` node carries a 1,024-dim embedding (Bedrock Titan v2) as a `Vector`
property, so "find problems similar to this description" is the natural next query:

```cypher
-- intended usage (4-arg signature: label, property, query_vector, k)
CALL db.index.vector.queryNodes('Problem', 'embedding', [/* 1024 floats */], 5)
YIELD node, score
RETURN node.title, score
```

**This currently returns empty.** Snapshot import stores the embedding vectors but does
not yet populate the HNSW index, so approximate-nearest-neighbour search finds nothing
until that's fixed. Tracked upstream:
[samyama-graph#5](https://git.samyama.ai/Samyama.ai/samyama-graph/issues/5). The graph
traversals above are unaffected. Once the fix lands, semantic "researcher onboarding"
(paste a paragraph of interests → most-similar problems → papers → people → future work)
works end-to-end on the OSS engine.

> **Want natural-language querying?** *"Which researchers work on worst-case-optimal
> joins, and what's left to solve?"* answered in plain English (NL→Cypher), plus richer
> entity resolution and hosted endpoints, are part of **Samyama-Graph Enterprise**.
> Reach out at [samyama.ai](https://samyama.ai).

---

## Good to know (engine notes)

- **Filter with `WHERE`.** It's the reliable way to filter (`WHERE p.title = "..."`,
  `WHERE p.title CONTAINS "..."`).
- **Deduplicating columns:** prefer `count(DISTINCT x)` / `collect(DISTINCT x)`.
  `RETURN DISTINCT <scalar>` does not always collapse duplicate rows in the current OSS
  build.
- **`UNWIND` can't lead a query** in the OSS build — start from a `MATCH`.
- Writes (`CREATE`/`SET`/`MERGE`/`DELETE`) and reads share the same `/api/query`
  endpoint; the server routes them automatically.

---

*Snapshot built from this catalog; see
[samyama-graph releases](https://github.com/samyama-ai/samyama-graph/releases) for the
`.sgsnap` and other prebuilt knowledge graphs.*
