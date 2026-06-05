# DBMS Research: 1000+ Open & Hard Problems

A structured catalog of **1000+ problems in the database management systems (DBMS) space**,
organized by topic. Each problem is a standalone Markdown file documenting:

- **Problem statement** — a precise, formal description.
- **Mathematical foundations** — the underlying model, notation, definitions, and key theorems.
- **State of the art (SOTA)** — current best-known algorithms, systems, and results.
- **Upper bound** — best-known algorithmic / complexity upper bound.
- **Lower bound** — best-known hardness / lower bound, and the open gap between the two.
- **Current research (as of June 2026)** — active directions and the groups pursuing them.
- **Future work** — open directions stated by researchers in the area.
- **Key references** — canonical and recent literature, linked where possible.

## How this is organized

```
topics/
  <NN-topic-slug>/
    README.md              # topic overview + index of its problems
    <problem-slug>.md      # one file per problem
```

The master index of all topics is in [`TAXONOMY.md`](./TAXONOMY.md).
Every problem file follows the schema in [`TEMPLATE.md`](./TEMPLATE.md).

## ⚠️ Provenance & honesty note

This catalog is generated primarily from **established domain knowledge** (canonical
PODS / SIGMOD / VLDB / ICDE / CIDR results and textbook theory). Citations to
**foundational** work (Codd, Selinger, Stonebraker, Gray, Abiteboul–Hull–Vianu, etc.)
are reliable. Claims about the **2025–2026 research frontier** are made to the best of
current knowledge but may **lag the true frontier** (knowledge horizon ≈ January 2026);
such claims are flagged inline with *(frontier — verify)*. Complexity bounds reflect
the best results the author is confident about; where a bound is folklore or contested
it is marked as such. **Do not cite this repository as a primary source** — follow the
linked references.

## Topics

See [`TAXONOMY.md`](./TAXONOMY.md) for the full list (35 topics, ~30 problems each).

## License

Content released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Contributions and corrections welcome via issues/PRs.
