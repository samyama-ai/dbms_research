#!/usr/bin/env python3
"""
Backfill provenance frontmatter onto every problem file (iteration-1 setup for the
periodic Refresh Runbook — see dbms_cloud/wiki/refresh-runbook.md).

Adds a YAML frontmatter block so future iterations are diffable (survived / new / stale):

    ---
    id: NN-topic-slug/problem-slug      # stable identity across iterations
    title: "..."
    topic: NN-topic-slug
    status: open|partially-solved|empirically-open|solved-but-impractical
    first_added: 2026-06
    last_reviewed: 2026-06
    last_substantive_update: 2026-06
    stale_since: ""
    provenance: synthesized
    ---

Parses title (H1) + status (the `**Status:**` blockquote) from each file. Idempotent:
skips files that already begin with a `---` frontmatter block. The human-readable
blockquote line is left untouched.

  python3 tools/add_provenance.py            # dry-run (report)
  python3 tools/add_provenance.py --apply
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITER = "2026-06"
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([a-z][a-z-]*)")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = sorted(p for p in (ROOT/"topics").glob("*/*.md") if p.name != "README.md")
    done = skipped = noparse = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            skipped += 1; continue
        topic = f.parent.name
        pid = f"{topic}/{f.stem}"
        h1 = H1_RE.search(text)
        st = STATUS_RE.search(text)
        if not h1 or not st:
            noparse += 1
            print(f"  !! cannot parse title/status: {f.relative_to(ROOT)}")
            continue
        fm = (
            "---\n"
            f"id: {pid}\n"
            f"title: {json.dumps(h1.group(1))}\n"
            f"topic: {topic}\n"
            f"status: {st.group(1)}\n"
            f"first_added: {ITER}\n"
            f"last_reviewed: {ITER}\n"
            f"last_substantive_update: {ITER}\n"
            f'stale_since: ""\n'
            f"provenance: synthesized\n"
            "---\n\n"
        )
        if args.apply:
            f.write_text(fm + text, encoding="utf-8")
        done += 1

    print(f"\nfiles={len(files)} {'wrote' if args.apply else 'would write'}={done} "
          f"already_had_frontmatter={skipped} unparseable={noparse}")
    if not args.apply:
        print("(dry-run) re-run with --apply to write frontmatter.")

if __name__ == "__main__":
    main()
