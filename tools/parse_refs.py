#!/usr/bin/env python3
"""Parse §9 reference lines out of every catalogue problem file.

Emits one JSON object per reference on stdout (JSONL) so downstream verifiers
(DBLP dump, Crossref, arXiv) can consume it without re-parsing markdown.
"""
import re, glob, json, sys, os

REF_RE = re.compile(
    r'^- \*\*\[(?P<tag>[^\]]+)\]\*\*\s+'      # [Foundational] / [SOTA] / ...
    r'(?P<rest>.*)$'
)
# A literal asterisk inside a title is escaped in the markdown (`R\*-tree`,
# `Q\*cert`) so it does not close the emphasis. The closing delimiter is
# therefore an asterisk NOT preceded by a backslash; matching any asterisk
# truncates those titles to `The R\` and reports real papers as missing.
TITLE_RE = re.compile(r'\*(?P<title>(?:[^*]|(?<=\\)\*)+?)\.?(?<!\\)\*')
# Elsevier DOIs embed parentheses (10.1016/S0049-237X(08)72018-4), so a
# non-greedy [^)]+ truncates the URL and the DOI 404s. Allow one level of
# nesting inside the link target.
LINK_RE = re.compile(r'\[(?P<kind>[^\]]+)\]\((?P<url>(?:[^()]|\([^()]*\))+)\)')
YEAR_RE = re.compile(r'\b(19|20|21)\d{2}\b')


def parse_line(line):
    m = REF_RE.match(line)
    if not m:
        return None
    rest = m.group('rest')
    tm = TITLE_RE.search(rest)
    if not tm:
        return None
    # Undo the markdown escape so downstream sees the real title: DBLP has
    # `The R*-tree`, not `The R\*-tree`.
    title = tm.group('title').strip().replace('\\*', '*')
    authors = rest[:tm.start()].strip().rstrip('.').strip()
    tail = rest[tm.end():]
    # venue/year sit between the title and the first link (or end of line)
    cut = tail.find(' — ')
    venue_year = (tail[:cut] if cut >= 0 else tail).strip().strip('.').strip()
    links = [{'kind': k, 'url': u} for k, u in LINK_RE.findall(tail)]
    years = YEAR_RE.findall(venue_year)
    ym = list(YEAR_RE.finditer(venue_year))
    year = int(ym[-1].group(0)) if ym else None
    venue = YEAR_RE.sub('', venue_year).strip(' ,.').strip() if ym else venue_year
    return {
        'tag': m.group('tag'), 'authors': authors, 'title': title,
        'venue': venue, 'year': year, 'venue_year_raw': venue_year,
        'links': links,
    }


def refs_for_file(path):
    text = open(path, encoding='utf-8').read()
    m = re.search(r'^## 9\.[^\n]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    if not m:
        return
    # references may wrap across source lines; re-join continuations first
    joined = []
    for line in m.group(1).split('\n'):
        line = line.rstrip()
        if line.startswith('- '):
            joined.append(line)
        elif line.strip() and joined:
            joined[-1] += ' ' + line.strip()
    for i, line in enumerate(joined):
        rec = parse_line(line)
        if rec is None:
            yield {'file': path, 'idx': i, 'parse_error': True, 'raw': line.rstrip()}
        else:
            rec.update({'file': path, 'idx': i, 'parse_error': False})
            yield rec


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'topics'
    files = [f for f in sorted(glob.glob(os.path.join(root, '*', '*.md')))
             if not f.endswith('README.md')]
    n = bad = 0
    for f in files:
        for rec in refs_for_file(f):
            n += 1
            bad += rec['parse_error']
            print(json.dumps(rec, ensure_ascii=False))
    print(f'# {n} references, {bad} unparsed, {len(files)} files', file=sys.stderr)


if __name__ == '__main__':
    main()
