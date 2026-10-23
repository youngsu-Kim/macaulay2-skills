# AGENTS.md — working on macaulay2-skills

## What this is

Agent Skills repo for Macaulay2 1.26: one core skill (`skills/macaulay2/`), growing to one sibling skill per M2 package. Companion to [macaulay2-mcp](https://github.com/youngsu-Kim/macaulay2-mcp), but the skill must stay useful for ANY M2 access path (plain CLI, other MCP servers, batch).

## Commands

```sh
python3 tools/mk_skill.py   # regenerate index.tsv / toc.md / packages.md from the
                            # INSTALLED 1.26 docs tree (never scrape the web)
python3 tools/verify.py     # execute every ```m2 block against a real kernel
uv/python3 available as-is; no dependencies beyond stdlib + M2 on PATH.
```

## Hard constraints

1. **Version pin.** Content targets Macaulay2 1.26 (mirrors macaulay2-mcp). Generated artifacts carry provenance headers (version, source path, date); bump by regenerating, then re-verifying — never hand-edit generated files (`index.tsv`, `toc.md`, `packages.md`).
2. **No unverified claims.** Every behavioral statement in any markdown file must be either (a) backed by an ```m2 block that `verify.py` runs (use `-- expect:` / `-- expect-error:` directives for exact output/error text), or (b) a doc-page pointer present in `references/index.tsv`. When unsure of M2's actual behavior, RUN IT FIRST — this repo has already caught a wrong membership claim (`x^5 % I`) and a wrong return-type claim (`installedPackages()` is a List, not a HashTable) via verification.
3. **Blocks are self-contained.** `verify.py` runs each block in a fresh kernel: normal blocks in strict batch (`--stop`), error blocks in piped REPL mode (continues past the error by design — that REPL behavior is itself a documented skill claim). No state may leak between blocks.
4. **SKILL.md stays small** (~150 lines): rules + lookup ladder + pointers. Depth belongs in `references/*.md`. Progressive disclosure is the point.
5. **Error text is content.** Quote M2's error strings verbatim (they are the lookup keys a struggling model has); if an expected string changes, that's a version-pin change, not a cosmetic one — same review discipline as macaulay2-mcp's golden.jsonl.
6. **GPL-3.0-or-later.** Generated files derive from M2's GPL doc tree; keep SPDX headers on scripts. Do not relicense.
7. **Release boundaries need explicit approval, every time** (inherited convention): commit, push, tag each need the user's word for that action.
8. **Messages inform, never direct** — applies to skill prose too: state what an idiom does and its trade-offs; don't issue blind commands to the reader.

## Layout

```
skills/macaulay2/    SKILL.md + references/ (index.tsv toc.md packages.md
                       groebner.md resolutions.md debugging.md)
tools/               mk_skill.py (docs tree -> router artifacts)
                     verify.py   (markdown ```m2 blocks -> kernel)
                     reflow.py   (prose -> one-line paragraphs; --check mode)
```

Per-package skills (wave 2+): `skills/macaulay2-<name>/`, artifacts generated via `mk_skill.py --docs <pkg>/html` extension; same verify loop.

## Style (adopted 2026-10-12)

Hand-written prose is ONE line per paragraph — never wrap manually. `python3 tools/reflow.py --check <files>` enforces it; running it plain reflows in place. The tool never touches ``` fenced blocks (M2 blocks are line-based and verify.py parses their newlines), tables, headings, or blockquotes. Generated artifacts (index.tsv, toc.md, packages.md) and LICENSE (verbatim legal text) are excluded.

## Commit trailer

Every commit message ends with: `Assisted-by: <MODEL> hosted at the National Research Platform (https://nrp.ai)` where `<MODEL>` is the name and version of the model of the session making the commit (e.g. `GLM-5.3-NVFP4`, `Qwen3.8-Flash-Next-FP8`). Verify the running session's model identity before writing it — never reuse a name copied from earlier commits. Historical commits keep the trailer they were made with; corrections are forward-looking only.

## Sources policy (adopted 2026-10-22)

Only publicly available material is incorporated into this repo. Any new source must be added to README's `## Sources` section; unpublished material (raw transcripts, private notes) may be summarized but must be labeled as pending publication.
