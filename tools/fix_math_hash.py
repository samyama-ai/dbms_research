#!/usr/bin/env python3
"""Escape unescaped '#' that occurs INSIDE math mode ($...$ / $$...$$) so KaTeX
(GitHub math) stops throwing "can't use macro parameter character # in math mode".

STRICTLY SURGICAL:
- Only '#' inside math delimiters is changed (-> '\\#').
- Markdown headings (##), prose '#P-hard', inline code `#P`, and fenced code
  blocks (``` / ~~~) are left untouched.
- Already-escaped '\\#' is never double-escaped.

Usage:
  fix_math_hash.py --dry-run   # report changes, write nothing
  fix_math_hash.py --apply     # apply in place
"""
import sys, os, re

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "topics")

def transform(text):
    """Return (new_text, n_escapes). Walks the file with a small state machine."""
    out = []
    n = 0
    i = 0
    L = len(text)
    in_math = False
    delim = None          # '$' or '$$'
    fence = None          # None, or the fence string '```'/'~~~' currently open
    at_line_start = True

    while i < L:
        c = text[i]

        # --- fenced code block handling (line-oriented) ---
        if at_line_start and not in_math:
            # look at the rest of the line
            j = text.find('\n', i)
            line = text[i:(j if j != -1 else L)]
            stripped = line.lstrip()
            if stripped.startswith('```') or stripped.startswith('~~~'):
                marker = stripped[:3]
                if fence is None:
                    fence = marker
                elif stripped.startswith(fence):
                    fence = None
                out.append(line)
                i = j if j != -1 else L
                at_line_start = (j != -1)
                if j != -1:
                    out.append('\n'); i += 1
                continue
            if fence is not None:
                # inside a fenced code block: copy line verbatim
                out.append(line)
                i = j if j != -1 else L
                at_line_start = (j != -1)
                if j != -1:
                    out.append('\n'); i += 1
                continue

        if fence is not None:
            out.append(c); i += 1; at_line_start = (c == '\n'); continue

        # --- inline code span (backtick run) outside math ---
        if not in_math and c == '`':
            m = re.match(r'`+', text[i:])
            ticks = m.group(0)
            close = text.find(ticks, i + len(ticks))
            if close == -1:
                out.append(text[i:]); i = L; break
            end = close + len(ticks)
            out.append(text[i:end]); i = end; at_line_start = False
            continue

        # --- enter math ---
        if not in_math and c == '$':
            if text[i:i+2] == '$$':
                in_math = True; delim = '$$'; out.append('$$'); i += 2
            else:
                in_math = True; delim = '$'; out.append('$'); i += 1
            at_line_start = False
            continue

        # --- inside math ---
        if in_math:
            # inline ($...$) math NEVER spans lines -> close at newline (desync guard)
            if c == '\n':
                if delim == '$':
                    in_math = False; delim = None
                out.append('\n'); i += 1; at_line_start = True; continue
            # a markdown heading can't be inside display math -> desync; bail to text
            if at_line_start and re.match(r'#{1,6}\s', text[i:i+8] or ''):
                in_math = False; delim = None
                # do NOT consume; fall through to ordinary-text handling below
            else:
                # GitHub math needs '\\#' (double backslash): markdown strips one '\'
                # so MathJax receives '\#' and renders a literal '#'. Normalize bare
                # '#', broken '\#', and already-correct '\\#' all to exactly '\\#'.
                if text[i:i+3] == r'\\#':            # already correct -> leave (idempotent)
                    out.append(r'\\#'); i += 3; at_line_start = False; continue
                if text[i:i+2] == r'\#':             # broken single backslash -> fix
                    out.append(r'\\#'); n += 1; i += 2; at_line_start = False; continue
                if c == '\\':                        # other escape pair: copy verbatim
                    out.append(text[i:i+2]); i += 2; at_line_start = False; continue
                if c == '$':
                    if delim == '$$' and text[i:i+2] == '$$':
                        in_math = False; delim = None; out.append('$$'); i += 2
                    elif delim == '$':
                        in_math = False; delim = None; out.append('$'); i += 1
                    else:
                        out.append(c); i += 1
                    at_line_start = False; continue
                if c == '#':                         # bare hash -> '\\#'
                    out.append(r'\\#'); n += 1; i += 1; at_line_start = False; continue
                out.append(c); i += 1; at_line_start = False; continue

        # --- ordinary text ---
        out.append(c)
        at_line_start = (c == '\n')
        i += 1

    return ''.join(out), n

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--dry-run'
    apply = (mode == '--apply')
    total_files = 0; total_changed = 0; total_esc = 0
    for dirpath, _, files in os.walk(ROOT):
        for fn in sorted(files):
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dirpath, fn)
            total_files += 1
            with open(p, encoding='utf-8') as f:
                src = f.read()
            new, n = transform(src)
            if n == 0:
                continue
            total_changed += 1; total_esc += n
            rel = os.path.relpath(p, os.path.dirname(ROOT))
            print(f"{rel}: {n} '#'->'\\#' in math")
            # show changed lines for review
            for so, sn in zip(src.splitlines(), new.splitlines()):
                if so != sn:
                    print(f"    -  {so.strip()[:140]}")
                    print(f"    +  {sn.strip()[:140]}")
            if apply:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(new)
    print(f"\n{'APPLIED' if apply else 'DRY-RUN'}: {total_changed}/{total_files} files, {total_esc} escapes total")

if __name__ == '__main__':
    main()
