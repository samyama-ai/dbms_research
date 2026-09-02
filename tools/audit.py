#!/usr/bin/env python3
"""Catalog audit — run before every push, and as Phase 2 "verify" of the refresh runbook.

  python3 tools/audit.py            structure, frontmatter, index/taxonomy sync, safety
  python3 tools/audit.py --links    also resolve every external URL (slow, network)
  python3 tools/audit.py --ours     also check every Samyama citation against live arXiv

The check that earned this file: `28-vector-similarity-search/updatable-graph-index.md`
asserted a positive result that our own published paper (arXiv:2607.00728) retracts as an
artifact of an interpolated baseline. It was public for two months. A citation is not
checked by seeing that it exists -- `--ours` compares the claimed title against the live
arXiv title, which is the cheap half of catching a verdict that outlived its measurement.

Exit 0 = clean. Exit 1 = at least one FAIL.
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS = os.path.join(ROOT, "topics")

REQUIRED_FM = ["id", "title", "topic", "status", "first_added",
               "last_reviewed", "last_substantive_update", "stale_since", "provenance"]
VALID_STATUS = {"open", "partially-solved", "empirically-open", "solved-but-impractical", "stale"}
VALID_PROV = {"synthesized", "verified"}
SECTIONS = ["1. Problem Statement", "2. Mathematical Foundations", "3. State of the Art",
            "4. Upper Bound", "5. Lower Bound", "6. The Gap", "7. Current Research",
            "8. Future Work", "9. Key References", "10. Worked Example"]

# This repo is public. Nothing internal may appear in it.
LEAK = re.compile(
    r"(?<![\w-])(?:sk-[A-Za-z0-9_-]{16,}|sk-ant-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}|glpat-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY|git\.samyama\.ai|samyama-research|dbms_cloud"
    r"|/home/[a-z0-9_-]+/|/Users/[A-Za-z0-9_-]+/|qorro|trufluence|inpharmd|brightcone)")

FAILS, WARNS = [], []


def fail(m):
    FAILS.append(m)


def warn(m):
    WARNS.append(m)


def problem_files():
    out = []
    for d, _, fs in os.walk(TOPICS):
        for f in fs:
            if f.endswith(".md") and f != "README.md":
                out.append(os.path.join(d, f))
    return sorted(out)


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fm = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm


def check_structure(files):
    for p in files:
        rel = os.path.relpath(p, ROOT)
        text = open(p, encoding="utf-8").read()
        fm = frontmatter(text)
        if fm is None:
            fail(f"{rel}: no YAML frontmatter")
            continue
        for k in REQUIRED_FM:
            if k not in fm:
                fail(f"{rel}: frontmatter missing `{k}`")
        if fm.get("status") and fm["status"] not in VALID_STATUS:
            fail(f"{rel}: status '{fm['status']}' not in {sorted(VALID_STATUS)}")
        if fm.get("provenance") and fm["provenance"] not in VALID_PROV:
            fail(f"{rel}: provenance '{fm['provenance']}' not in {sorted(VALID_PROV)}")
        # id must equal its path -- it is the identity used to diff iterations
        want = os.path.relpath(p, TOPICS)[:-3]
        if fm.get("id") and fm["id"] != want:
            fail(f"{rel}: id '{fm['id']}' does not match path (expected '{want}')")
        # stale must carry a date
        if fm.get("status") == "stale" and not fm.get("stale_since"):
            fail(f"{rel}: status stale with empty stale_since")
        # all ten sections, in order
        heads = re.findall(r"^## (.+)$", text, re.M)
        pos = 0
        for want_s in SECTIONS:
            found = next((i for i, h in enumerate(heads[pos:], pos) if h.startswith(want_s[:12])), None)
            if found is None:
                fail(f"{rel}: missing section '{want_s}'")
            else:
                pos = found + 1
        # KaTeX hazard: a bare # inside math breaks rendering (tools/fix_math_hash.py).
        # Split on unescaped $ -- odd segments are inside math. Doing this with one regex
        # cannot work: it has no way to tell an opening delimiter from a closing one.
        for lineno, line in enumerate(text.split("\n"), 1):
            parts = re.split(r"(?<!\\)\$", line)
            if len(parts) % 2 == 0:
                continue                       # unbalanced on this line; not our check
            for seg in parts[1::2]:
                if re.search(r"(?<!\\)#", seg):
                    fail(f"{rel}:{lineno}: unescaped '#' inside math: {seg[:56]}")
        # public repo: nothing internal
        for m in LEAK.finditer(text):
            fail(f"{rel}: internal/secret token in a PUBLIC repo: '{m.group(0)[:40]}'")
        # Placeholders that read as content. "IEEE TBD" is Transactions on Big Data, a
        # real venue -- excluded, or the check cries wolf on every GPU-ANN page and gets
        # ignored, which is worse than not having it.
        for m in re.finditer(r"(?<!IEEE )\b(TODO|FIXME|XXX|Lorem ipsum)\b|(?<!IEEE )\bTBD\b(?!ATA)",
                             text):
            warn(f"{rel}: placeholder '{m.group(0)}'")


def check_index(files):
    """Compare INDEX.md against a fresh generation WITHOUT touching the real file.

    An earlier version just ran gen_index.sh in place. That makes the validator mutate
    the tree it is validating: run it in the background and a concurrent `git diff` sees
    a half-written INDEX.md and reports 501 deleted lines that were never deleted.
    A checker must be side-effect free.
    """
    import shutil
    import tempfile
    real = os.path.join(ROOT, "INDEX.md")
    with tempfile.TemporaryDirectory() as td:
        backup = os.path.join(td, "INDEX.md.orig")
        shutil.copy2(real, backup)
        try:
            gen = subprocess.run(["bash", os.path.join(ROOT, "gen_index.sh")],
                                 cwd=ROOT, capture_output=True, text=True)
            fresh = open(real, encoding="utf-8").read() if gen.returncode == 0 else None
        finally:
            shutil.copy2(backup, real)          # always restore, even on exception
    if gen.returncode != 0:
        fail(f"gen_index.sh failed: {gen.stderr.strip()[:200]}")
        return
    if fresh != open(real, encoding="utf-8").read():
        fail("INDEX.md is stale -- run ./gen_index.sh and commit the result.")
    idx = open(os.path.join(ROOT, "INDEX.md"), encoding="utf-8").read()
    m = re.search(r"\*\*Total: (\d+) problems\.\*\*", idx)
    if m and int(m.group(1)) != len(files):
        fail(f"INDEX.md says {m.group(1)} problems; {len(files)} files on disk")
    # every file linked exactly once
    linked = set(re.findall(r"\]\(\./topics/([^)]+\.md)\)", idx))
    on_disk = {os.path.relpath(p, TOPICS) for p in files}
    for miss in sorted(on_disk - linked):
        fail(f"INDEX.md does not link {miss}")
    for extra in sorted(linked - on_disk):
        fail(f"INDEX.md links a file that does not exist: {extra}")


def check_taxonomy(files):
    tax_path = os.path.join(ROOT, "TAXONOMY.md")
    if not os.path.exists(tax_path):
        return
    tax = open(tax_path, encoding="utf-8").read()
    actual = {}
    for p in files:
        actual[os.path.basename(os.path.dirname(p))] = actual.get(
            os.path.basename(os.path.dirname(p)), 0) + 1
    for slug, n in sorted(actual.items()):
        m = re.search(re.escape(slug) + r"[^\n]*?\((\d+)\)", tax)
        if m and int(m.group(1)) != n:
            fail(f"TAXONOMY.md says {slug} has {m.group(1)}; {n} files on disk")


def urls_in(files):
    seen = {}
    for p in files:
        for u in re.findall(r"\((https?://[^)\s]+)\)", open(p, encoding="utf-8").read()):
            seen.setdefault(u.rstrip(".,);"), []).append(os.path.relpath(p, ROOT))
    return seen


def probe(u):
    for method in ("HEAD", "GET"):
        try:
            r = urllib.request.Request(u, method=method,
                                       headers={"User-Agent": "dbms_research-audit/1.0"})
            with urllib.request.urlopen(r, timeout=20) as resp:
                return u, resp.status
        except Exception as e:
            code = getattr(e, "code", None)
            if code in (403, 405) and method == "HEAD":
                continue                       # some hosts refuse HEAD; retry as GET
            if code:
                return u, code
    return u, 0


def check_links(files):
    seen = urls_in(files)
    print(f"  resolving {len(seen)} unique URLs ...", file=sys.stderr)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for u, code in ex.map(probe, seen):
            if code in (200, 301, 302, 303, 307, 308):
                continue
            where = seen[u][0] + (f" (+{len(seen[u])-1})" if len(seen[u]) > 1 else "")
            (fail if code in (404, 410) else warn)(f"{where}: HTTP {code} {u}")


def check_ours(files):
    """Every Samyama citation must match the live arXiv record -- title included."""
    cited = {}
    for p in files:
        t = open(p, encoding="utf-8").read()
        for m in re.finditer(r"Samyama[^\n]*?\*([^*]+)\*[^\n]*?arXiv:(\d{4}\.\d{4,5})", t):
            cited[m.group(2)] = (m.group(1).strip().rstrip("."), os.path.relpath(p, ROOT))
    if not cited:
        return
    q = "id_list=" + ",".join(cited) + "&max_results=50"
    req = urllib.request.Request("https://export.arxiv.org/api/query?" + q,
                                 headers={"User-Agent": "dbms_research-audit/1.0"})
    xml = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                xml = r.read().decode()
            break
        except Exception as e:
            last = e
    if xml is None:
        # --ours is opt-in: the caller asked for this check, so an unreachable API is a
        # failure, not a warning. A probe that cannot run must never read as "nothing wrong".
        fail(f"--ours: could not reach the arXiv API after 3 attempts ({last}); "
             f"{len(cited)} Samyama citations left UNVERIFIED")
        return
    ns = {"a": "http://www.w3.org/2005/Atom"}
    live = {}
    for e in ET.fromstring(xml).findall("a:entry", ns):
        aid = re.search(r"abs/([\d.]+)v", e.find("a:id", ns).text).group(1)
        live[aid] = " ".join(e.find("a:title", ns).text.split())
    for aid, (claimed, rel) in sorted(cited.items()):
        if aid not in live:
            fail(f"{rel}: cites arXiv:{aid}, which the arXiv API does not return")
            continue
        def norm(s):
            return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        if norm(claimed) != norm(live[aid]):
            fail(f"{rel}: cites arXiv:{aid} as\n"
                 f"        claimed: {claimed}\n"
                 f"        actual : {live[aid]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--ours", action="store_true")
    a = ap.parse_args()

    files = problem_files()
    print(f"── audit: {len(files)} problem files ──")
    check_structure(files)
    check_index(files)
    check_taxonomy(files)
    if a.ours:
        check_ours(files)
    if a.links:
        check_links(files)

    for m in WARNS[:40]:
        print(f"  WARN: {m}")
    if len(WARNS) > 40:
        print(f"  ... and {len(WARNS)-40} more warnings")
    for m in FAILS:
        print(f"  FAIL: {m}")
    print(f"  {len(FAILS)} failures, {len(WARNS)} warnings")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
