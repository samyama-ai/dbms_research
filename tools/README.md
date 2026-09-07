# tools — catalogue checks

`audit.py` is the gate: run it before every push. The rest are the reference-verification
pipeline it reports on, added in iteration `2026-09`.

## Why a reference pipeline

A citation is not checked by seeing that its link is alive. The failure that matters is a
**live identifier attached to a different paper** — and it is invisible to any link checker.
Two real examples from the catalogue, both public since 2026-06:

| file | cited | the DOI actually resolved to |
|---|---|---|
| `32-multimodel-document-db/jsonpath-containment` | Containment and Equivalence for a Fragment of XPath | *JACM editors-in-chief* |
| `34-schema-design-normalization/temporal-normal-forms` | An Information-Theoretic Approach to Normal Forms | *Sequent and hypersequent calculi for abelian and Łukasiewicz logics* |

## The passes

```
parse_refs.py          section 9 -> one JSON record per reference (title, venue, year, links)
verify_refs.py         resolves every DOI (Crossref, then DataCite) and arXiv id, and
                       compares the RESOLVED title to the CITED title
dblp_title_check.py    exact-title existence check against the DBLP bulk dump (offline)
dblp_fuzzy_match.py    second pass for titles the catalogue shortens ("ARIES", "FITing-Tree")
dblp_arxiv_check.py    arXiv ids via DBLP's journals/corr records, when the arXiv API throttles
dblp_doi_suggest.py    for a flagged reference, reads DBLP's own <ee> to suggest the right DOI
```

Typical run (the dump lives outside this repo):

```sh
python3 tools/parse_refs.py > refs.jsonl
python3 tools/dblp_title_check.py --refs refs.jsonl --dump <path>/dblp-<date>.xml.gz \
    --out dblp_titles.json
python3 tools/dblp_fuzzy_match.py --titles dblp_titles.json --dump <path>/dblp-<date>.xml.gz \
    --out dblp_fuzzy.json
python3 tools/verify_refs.py --refs refs.jsonl --cache res_doi.jsonl   --kind doi   --workers 1
python3 tools/verify_refs.py --refs refs.jsonl --cache res_arxiv.jsonl --kind arxiv --batch 25
```

## Things that cost a false result once, so they are encoded here

- **Half of DBLP is invisible to a line-based scanner.** `dblp.xml` packs
  `</incollection><incollection ...>` onto one line: 4.4M of 8.7M publication records do not
  start a line. Scan a carry-over buffer with a record regex, never `for line in fh`.
- **Elsevier DOIs contain parentheses** (`10.1016/S0049-237X(08)72018-4`). A markdown link
  regex of `\(([^)]+)\)` truncates them, and all 49 such DOIs then 404.
- **A 404 from Crossref is not a dead DOI.** LIPIcs/Dagstuhl (`10.4230/*`) register with
  DataCite. Asking one registry only reported 23 dead DOIs; 17 of them were alive.
- **Crossref titles carry markup and truncate at the subtitle** — `O<scp>rpheus</scp>DB`,
  and `Calvin` for *Calvin: Fast Distributed Transactions…*. Compare by containment against
  the shorter title, plus a punctuation-free squash, not by equality or Jaccard.
- **Crossref 429s under concurrency** (13 of 24 requests at 6 workers, none sequentially).
  Use one worker.
- **`ThreadPoolExecutor.map` yields in submission order**, so one slow identifier stalls
  every write behind it and a killed sweep loses them. Use `as_completed` and flush per line.
- **The catalogue shortens titles**, and *Encyclopedia of Database Systems* has thousands of
  one-word entries. Score a fuzzy match symmetrically (`/max`), or "Adaptive." matches
  everything.

Each of these turned a clean run into a wrong number before it was fixed. An exact-title
check alone called 905 references missing; after removing the false-positive classes above,
21 titles had no plausible record and none of them was a fabrication.
