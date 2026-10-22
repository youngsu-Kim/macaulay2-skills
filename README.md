# macaulay2-skills

Version-pinned [Agent Skills](https://agentskills.io) for **Macaulay2 1.26** — teach any skill-capable agent (Claude Code, OpenCode, LM Studio, …) the M2 vocabulary and traps, instead of letting every model rediscover them.

**Motivation:** in a benchmark run of the three README examples from [macaulay2-mcp](https://github.com/youngsu-Kim/macaulay2-mcp), a no-thinking model hallucinated a nonexistent `reduceGb`, misread M2's misleading "no method for adjacent objects" error as a spacing problem, and needed ~11 kernel calls to do a ~3-call computation. The fix is not more instructions inside an MCP server — it is portable, machine-verified domain knowledge sitting next to the model.

**Note:** Unlike the [macaulay2-mcp](https://github.com/youngsu-Kim/macaulay2-mcp), this document only contains text. It has less risk compared to the mcp. This repo would use greater help of AI to maintain. Most of the data is collected from the public Macaulay2 page with instructions provided by the author. Skills do not require the mcp, and it may be just helpful for those who need to clean up their M2 package documents, or need some help with their code without training/fine-tuning a large language model. Likewise, the skills can be used by pointing your AI agent to this webpage, without installation. The test run with macaulay2-mcp greatly saved the number of tokens and reduced the number of tool calls.

## Benchmark at a glance

All runs driven by **OpenCode v2.0.26** subagents against the **macaulay2-mcp 0.1.4** server with **Macaulay2 1.26.06** kernels; skill content **v0.0.0** at run time (traps #17–#18 shipped afterward as v0.0.1 — nothing they cover was re-run since). Protocol: the three Introduction-example prompts from the mcp README; metric = `m2_evaluate` calls until all answers verified correct; model specs per [nrp.ai/llms](https://nrp.ai/llms/). Full grids and per-cell transcripts: [FINDINGS.md](FINDINGS.md).

| Model (NRP deployment) | Thinking | No skill | With skill | Ran | Kernel errors | Graded subanswers |
|---|---|---|---|---|---|---|
| NRP Qwen3.8-Flash-Next-FP8 · 180B (6B active) MoE · 1M ctx | off | **22** | **5** | 10-11 | 0 | 3/3 |
| NRP Qwen3.8-27B · 1M ctx | off | **21** | **3**¹ | 10-12 | 0 | 3/3 |
| NRP DeepSeek-V4-Flash-0731 · 304B MoE · 1M ctx | off | — | **3** | 10-12 | 0 | 3/3 (+ 4/4 on unseen Segre task in 5) |
| NRP GLM-5.3-NVFP4 · 753B · 1M ctx | low | — | **3** | 10-12 | 0 | 3/3 |
| NRP Kimi · 1T · 131K ctx | default | — | **4**¹ | 10-12 | 0 | 3/3 (+ 4/4 Segre in 2) |
| NRP GPT OSS · 120B · 131K ctx | low | — | **3** | 10-12 | 0 | 2/3² |
| NRP MiniMax-M2.7 · 230B native FP8 · 205K ctx | default | — | — | 10-12 | — | agent died twice (infra); excluded from stats |

¹ skill auto-discovered from the agent's skill listing — no pointer given. ² the one miss: misread `hilbertPolynomial`'s class-form display → became trap #17. Dates are 2026, Pacific. `—` not re-measured: the no-skill control ran on the two Qwen rows and reproduced almost exactly across a model swap (22 → 21 calls, same failure catalog) — the delta is causal, not anecdotal.

Bottom line: 32/33 graded subanswers with the skill; call budget cut ~4–7×; across four thinking levels on the author family: 3–8 calls, zero kernel errors.

## Install

```sh
npx skills add youngsu-Kim/macaulay2-skills
```

The CLI auto-detects your agents (or use `-a claude-code -a opencode`, `-g` for user-wide). Add `--skill macaulay2` to grab just the core skill.

## What's inside

```
skills/
  macaulay2/
    SKILL.md              # rules + traps + lookup ladder (kept small)
    references/
      index.tsv           # 5,704 rows: symbol -> blurb -> page -> package (prefix-grep ^name)
      toc.md              # 2,016-node thematic outline of the 1.26 core docs
      packages.md         # 299 bundled packages by theme, ⚡ = default-loaded, ⭐ = refereed
      groebner.md         # bases, orders, elimination, membership
      resolutions.md      # res/betti reading, Hilbert series/polynomial
      debugging.md        # error-message taxonomy, no-rollback semantics
tools/
  mk_skill.py             # regenerate router artifacts from the INSTALLED docs
  verify.py               # run every ```m2 block in the skill against a real 1.26 kernel
FINDINGS.md               # the measured record: benchmark grid + doc-gap taxonomy
```

## The two promises this repo makes

1. **Version-pinned by construction.** `index.tsv` / `toc.md` / `packages.md` are generated from doc trees inside your *installed* Macaulay2 1.26 — core **plus the 21 packages M2 loads at startup** — and carry provenance headers. The kernel's own `m2_help` reads the same corpus — skill, docs, and server cannot disagree.
2. **Machine-verified claims.** Every `m2` code block in the skill executes against a real kernel — in CI on every push (GitHub Actions, Macaulay2's official Ubuntu PPA) and locally via `python3 tools/verify.py` — with asserted output (or asserted exact error text). `tools/verify.py` currently runs 38 blocks, all passing. A claim that can't be verified doesn't ship.

```sh
# after an M2 version bump (or doc-tree change):
python3 tools/mk_skill.py     # regenerate the three router artifacts
python3 tools/verify.py       # re-verify every block (needs M2 on PATH)
```

## Honest limits

The claims above are exactly as strong as the evidence:

- **Pinned to one build.** All verified behavior is Macaulay2 1.26.06; the reference provenance is the Homebrew arm64 build (runtime-detected default-loaded set recorded in each artifact header). CI re-verifies the same blocks weekly on Ubuntu's official PPA; for any other build, regenerate (`tools/mk_skill.py`) and re-verify (`tools/verify.py`) before trusting it.

## Roadmap

One sibling skill per package that earns it, generated the same way from each package's own pinned docs (all 299 ship `master.html` + `toc.html`, so the pipeline is identical): `macaulay2-fourti-two`, `macaulay2-primarydecomposition`, … Install individually via `npx skills add youngsu-Kim/macaulay2-skills --skill <name>`.

## License

GPL-3.0-or-later — same as [macaulay2-mcp](https://github.com/youngsu-Kim/macaulay2-mcp) and in the spirit of Macaulay2 itself (GPL v2/v3). Generated artifacts are mechanical transforms of the **official Macaulay2 documentation tree** shipped with the distribution (© Daniel R. Grayson and Michael E. Stillman); the hand-written pages quote that documentation. Copyleft keeps the derivation legally clean while keeping the whole family open.

This program is free software under the [GNU General Public License v3 or later](LICENSE): use it freely, including commercially — but if you distribute it, or a program built on top of it, the same freedoms must travel with your copy.
