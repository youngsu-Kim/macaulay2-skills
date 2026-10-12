#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify every ```m2 code block in the skill markdown against a real kernel.

Each fenced ```m2 block must be SELF-CONTAINED: it is written to a temp .m2
file and run as a fresh batch process, exactly how macaulay2-mcp's
m2_run_script invokes M2:

    M2 -q --no-debug --no-tty --silent [--stop] FILE

Directives (comment lines inside the block, stripped before running):
    -- expect: SUBSTRING          SUBSTRING must appear in stdout
    -- expect-error: SUBSTRING    the run must error AND SUBSTRING must appear
                                  (the erroring statement should be LAST)

Blocks without expect-error must exit 0 with no "error:" line.
Exit code: 0 = all blocks pass, 1 = at least one failure.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BLOCK_RE = re.compile(r"```m2\n(.*?)```", re.S)
EXPECT_RE = re.compile(r"^\s*--\s*expect:\s*(.*)$")
EXPECT_ERR_RE = re.compile(r"^\s*--\s*expect-error:\s*(.*)$")
ERROR_RE = re.compile(r"^\s*error:|\berror:", re.M)


def m2_binary() -> str:
    import os
    b = os.environ.get("M2_BIN", "").strip() or shutil.which("M2") or ""
    if not b:
        sys.exit("error: no M2 binary found (set M2_BIN or put M2 on PATH)")
    return b


def run_block(binary: str, code: str, mode: str) -> tuple[int, str]:
    """mode 'file'  -> batch file + --stop: halts at first error (strict).
       mode 'stdin' -> piped REPL: continues past errors (interactive truth),
                       used for expect-error blocks so later statements and
                       `-- expect:` substrings are still observable."""
    flags = [binary, "-q", "--no-debug", "--no-tty", "--silent"]
    try:
        if mode == "file":
            with tempfile.NamedTemporaryFile("w", suffix=".m2", delete=False) as f:
                f.write(code if code.endswith("\n") else code + "\n")
                path = f.name
            try:
                proc = subprocess.run(flags + ["--stop", path], capture_output=True,
                                      text=True, timeout=180, stdin=subprocess.DEVNULL)
            finally:
                Path(path).unlink(missing_ok=True)
        else:
            proc = subprocess.run(flags, input=code, capture_output=True,
                                  text=True, timeout=180)
        return proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after 180s"


def check(md_files: list[Path], binary: str) -> int:
    passed = failed = 0
    for md in md_files:
        for n, block in enumerate(BLOCK_RE.findall(md.read_text()), 1):
            expects, err_expects, keep = [], [], []
            for line in block.splitlines():
                if m := EXPECT_RE.match(line):
                    expects.append(m.group(1).strip())
                elif m := EXPECT_ERR_RE.match(line):
                    err_expects.append(m.group(1).strip())
                else:
                    keep.append(line)
            code = "\n".join(keep)
            if not code.strip():
                continue
            label = f"{md.name} block#{n}"
            rc, out = run_block(binary, code, "stdin" if err_expects else "file")
            errored = bool(ERROR_RE.search(out)) or rc != 0
            problems = []
            if err_expects:
                if not errored:
                    problems.append("expected an error, run succeeded")
                needles = err_expects + expects
            else:
                if errored:
                    line = next((l for l in out.splitlines() if "error:" in l), "unknown error")
                    problems.append(f"unexpected error: {line.strip()}")
                needles = expects
            for needle in needles:
                if needle and needle not in out:
                    problems.append(f"missing expect: {needle!r}")
            if problems:
                failed += 1
                print(f"FAIL  {label}: " + "; ".join(problems))
                tail = [l for l in out.splitlines() if l.strip()][-6:]
                print("      output tail: " + " ⏎ ".join(tail))
            else:
                passed += 1
                print(f"pass  {label}" + (f"  ({len(expects)} expect)" if expects else ""))
    print(f"\n{passed} passed, {failed} failed across {len(md_files)} file(s)")
    return 1 if failed else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", type=Path, help="markdown files (default: skills/**)")
    args = ap.parse_args()
    files = args.paths or sorted(Path(__file__).resolve().parent.parent.glob("skills/**/*.md"))
    sys.exit(check(files, m2_binary()))


if __name__ == "__main__":
    main()
