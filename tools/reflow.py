#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reflow markdown prose to ONE line per paragraph — the repo's source style.

Rule adopted 2026-10-12: hand-written prose is never wrapped manually, so
edits never require re-wrapping. The formatter collapses wrapped paragraphs
and leaves everything structural exactly as-is:

  - inside ``` fenced blocks: UNTOUCHED (M2 code blocks are line-based and
    tools/verify.py parses their newlines)
  - tables (lines starting with '|'), headings, blockquotes ('>' lines),
  - list items: each item is collapsed to one line, nesting indent preserved
  - explicit hard breaks (line ending with two spaces) are preserved
  - blank lines kept

Usage: python3 tools/reflow.py FILE [FILE ...]        # reflow in place
       python3 tools/reflow.py --check FILE ...       # exit 1 if changes needed
"""

from __future__ import annotations

import re
import sys

LIST_RE = re.compile(r"^(\s*)([-*+]\s+|\d+\.\s+)(.*)$")
FENCE_RE = re.compile(r"^\s*```")


def reflow_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    para: list[str] = []          # buffer of text parts for the current paragraph
    para_indent = ""

    def flush():
        nonlocal para, para_indent
        if para:
            out.append(para_indent + " ".join(p.strip() for p in para).strip())
            para = []
            para_indent = ""

    in_fence = False
    for raw in lines:
        line = raw.rstrip("\n")
        if FENCE_RE.match(line):
            flush()
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        stripped = line.strip()
        if not stripped:
            flush()
            out.append(line)
            continue
        if stripped.startswith(("|", ">", "#")):
            flush()
            out.append(line)
            continue
        m = LIST_RE.match(line)
        if m:
            flush()
            para = [m.group(2) + m.group(3)]
            para_indent = m.group(1)
            # a list item that opens a fenced block already got handled above
            continue
        # plain prose: join, honoring hard breaks (two trailing spaces)
        para.append(stripped)
        if raw.endswith("  \n") or line.endswith("  "):
            para[-1] = stripped + "  "   # keep the hard break marker
            flush()

    flush()
    return out


def main() -> int:
    args = sys.argv[1:]
    check = False
    if args and args[0] == "--check":
        check, args = True, args[1:]
    if not args:
        print(__doc__)
        return 2
    status = 0
    for path in args:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        out = "\n".join(reflow_lines(src.splitlines()))
        if not out.endswith("\n"):
            out += "\n"
        if out != src:
            if check:
                print(f"needs reflow: {path}")
                status = 1
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)
                print(f"reflowed: {path}")
        elif check:
            print(f"ok: {path}")
    return status


if __name__ == "__main__":
    sys.exit(main())
