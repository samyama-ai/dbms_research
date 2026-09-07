#!/usr/bin/env python3
"""Check every cited reference title against the DBLP bulk dump — offline.

DBLP indexes essentially all of computer science, so a catalogue reference whose
title has no DBLP record is a fabrication signal. This is the only oracle that
covers all 6,134 references: DOI/arXiv links cover 2,251 of them, and neither is
rate-free. Known false-negative classes (books, standards, non-CS journals, HAL
tech reports) are reported separately rather than counted as failures.

  python3 tools/dblp_title_check.py --refs refs.jsonl \
      --dump <path>/dblp-<date>.xml.gz --out dblp_titles.json
"""
import argparse, gzip, html, json, re, sys, time
from collections import defaultdict

REC_TYPES = ('article', 'inproceedings', 'incollection', 'book',
             'phdthesis', 'mastersthesis', 'proceedings')
OPEN_RE = re.compile(r'<(%s)\s' % '|'.join(REC_TYPES))
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.S)
YEAR_RE = re.compile(r'<year[^>]*>(\d{4})</year>')
AUTHOR_RE = re.compile(r'<author[^>]*>(.*?)</author>', re.S)
KEY_RE = re.compile(r'key="([^"]+)"')
TAG_RE = re.compile(r'<[^>]+>')


def norm_title(t):
    t = html.unescape(t)
    t = TAG_RE.sub('', t)
    t = t.lower().replace('’', "'").replace('–', '-').replace('—', '-')
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return ' '.join(t.split())



PAREN_RE = re.compile(r'\s*\([^()]*\)\s*$')


def title_variants(t):
    """Normalized forms a cited title may take in DBLP."""
    out = []
    for cand in (t, PAREN_RE.sub('', t), re.sub(r'\([^()]*\)', ' ', t)):
        n = norm_title(cand)
        if n and n not in out:
            out.append(n)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', required=True)
    ap.add_argument('--dump', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    refs = [r for r in map(json.loads, open(args.refs, encoding='utf-8'))
            if not r['parse_error']]
    # The catalogue appends a system nickname to many titles -- "There Is More
    # Consensus in Egalitarian Parliaments (EPaxos)" -- which DBLP does not carry.
    # Matching only the literal title reports those as missing papers. Index each
    # cited title under every variant, so a nickname is not read as a fabrication.
    wanted = defaultdict(list)      # normalized title variant -> cited records
    for r in refs:
        for v in title_variants(r['title']):
            wanted[v].append(r)
    n_titles = len({norm_title(r['title']) for r in refs})
    print(f'{len(refs)} references, {n_titles} unique titles, '
          f'{len(wanted)} match variants', file=sys.stderr)

    found = {}
    n_rec = 0
    t0 = time.time()
    # NOT line-based: dblp.xml packs "</incollection><incollection ...>" onto one
    # line, so a scanner that only matches an open tag at line start silently
    # drops about half the corpus. Scan a carry-over buffer with a record regex.
    REC_RE = re.compile(r'<(%s)\b[^>]*>(.*?)</\1>' % '|'.join(REC_TYPES), re.S)
    CHUNK = 1 << 22
    buf = ''
    with gzip.open(args.dump, 'rt', encoding='utf-8', errors='replace') as fh:
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            buf += chunk
            last = 0
            for m in REC_RE.finditer(buf):
                last = m.end()
                n_rec += 1
                kind, body = m.group(1), m.group(2)
                tm = TITLE_RE.search(body)
                if not tm:
                    continue
                nt = norm_title(tm.group(1))
                if nt in wanted and nt not in found:
                    ym = YEAR_RE.search(body)
                    km = KEY_RE.search(m.group(0))
                    found[nt] = {
                        'key': km.group(1) if km else '',
                        'type': kind,
                        'year': int(ym.group(1)) if ym else None,
                        'authors': [html.unescape(TAG_RE.sub('', a)).strip()
                                    for a in AUTHOR_RE.findall(body)][:12],
                    }
            buf = buf[last:]
            if n_rec and n_rec // 1000000 != (n_rec - 1) // 1000000:
                print(f'  {n_rec/1e6:.0f}M records, {len(found)}/{len(wanted)} '
                      f'titles matched, {time.time()-t0:.0f}s', file=sys.stderr)

    print(f'done: {n_rec} records, {len(found)}/{len(wanted)} titles matched, '
          f'{time.time()-t0:.0f}s', file=sys.stderr)
    unmatched = []
    hit = 0
    for r in refs:
        vs = title_variants(r['title'])
        if any(v in found for v in vs):
            hit += 1
        else:
            unmatched.append({'file': r['file'], 'title': r['title'],
                              'year': r['year'], 'venue': r['venue']})
    print(f'references with a DBLP record: {hit}/{len(refs)}', file=sys.stderr)
    json.dump({'matched': found, 'unmatched': unmatched},
              open(args.out, 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
