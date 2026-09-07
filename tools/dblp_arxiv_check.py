#!/usr/bin/env python3
"""Verify cited arXiv ids against the DBLP dump instead of the arXiv API.

The arXiv API rate-limits hard and was returning 429/503 for the whole of this
run. DBLP indexes preprints under keys of the form journals/corr/abs-2308-16862,
so the same question -- does this arXiv id belong to the paper cited? -- can be
answered offline from the dump we already have.

  python3 tools/dblp_arxiv_check.py --refs refs.jsonl \
      --dump <path>/dblp-<date>.xml.gz --out arxiv_dblp.json
"""
import argparse, gzip, html, json, re, sys, time

CORR_RE = re.compile(r'key="journals/corr/abs-(\d{4})-(\d{4,5})"')
OLD_CORR_RE = re.compile(r'key="journals/corr/([a-z-]+)-?(\d{7})"')
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.S)
YEAR_RE = re.compile(r'<year[^>]*>(\d{4})</year>')
TAG_RE = re.compile(r'<[^>]+>')
ART_RE = re.compile(r'<article\b[^>]*>(.*?)</article>', re.S)
ARX_URL_RE = re.compile(r'arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})')


def clean(t):
    return ' '.join(TAG_RE.sub('', html.unescape(t)).split()).rstrip('.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', required=True)
    ap.add_argument('--dump', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    wanted = {}
    for r in map(json.loads, open(args.refs, encoding='utf-8')):
        if r['parse_error']:
            continue
        for l in r['links']:
            m = ARX_URL_RE.search(l['url'])
            if m:
                wanted.setdefault(m.group(1), []).append(r)
    print(f'{len(wanted)} unique cited arXiv ids', file=sys.stderr)

    found = {}
    n = 0
    t0 = time.time()
    buf = ''
    CHUNK = 1 << 22
    with gzip.open(args.dump, 'rt', encoding='utf-8', errors='replace') as fh:
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            buf += chunk
            last = 0
            for m in ART_RE.finditer(buf):
                last = m.end()
                rec = m.group(0)
                km = CORR_RE.search(rec)
                if km:
                    aid = f'{km.group(1)}.{km.group(2)}'
                else:
                    km = OLD_CORR_RE.search(rec)
                    if not km:
                        continue
                    aid = f'{km.group(1)}/{km.group(2)}'
                n += 1
                if aid in wanted and aid not in found:
                    tm = TITLE_RE.search(m.group(1))
                    ym = YEAR_RE.search(m.group(1))
                    found[aid] = {'title': clean(tm.group(1)) if tm else '',
                                  'year': int(ym.group(1)) if ym else None}
            buf = buf[last:]

    print(f'done: {n} corr records, {len(found)}/{len(wanted)} cited ids found, '
          f'{time.time()-t0:.0f}s', file=sys.stderr)
    json.dump({'found': found,
               'not_in_dblp': sorted(set(wanted) - set(found))},
              open(args.out, 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
